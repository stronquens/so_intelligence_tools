from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import socket
import threading
import time

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.domain.models import (
    LivePartialUpdate,
    LiveSessionState,
    SystemAudioSessionMode,
    TranscriptBlock,
)
from so_intelligence_tools.system_audio_translation.audio_capture import LinuxParecAudioCapture
from so_intelligence_tools.system_audio_translation.provider import ChunkedAudioTranslationProvider


@dataclass(slots=True)
class PcmSegmentAccumulator:
    sample_rate_hz: int
    segment_seconds: float
    overlap_seconds: float
    _buffer: bytearray = field(default_factory=bytearray)

    def add_chunk(self, chunk: bytes) -> list[bytes]:
        self._buffer.extend(chunk)
        segment_bytes = int(self.sample_rate_hz * self.segment_seconds * 2)
        overlap_bytes = int(self.sample_rate_hz * self.overlap_seconds * 2)
        ready: list[bytes] = []
        while len(self._buffer) >= segment_bytes:
            ready.append(bytes(self._buffer[:segment_bytes]))
            self._buffer = bytearray(self._buffer[segment_bytes - overlap_bytes :])
        return ready

    def reset(self) -> None:
        self._buffer.clear()


@dataclass(slots=True)
class TranscriptSessionLogger:
    logs_dir: Path
    _events: list[dict[str, object]] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()

    def record_event(self, event_type: str, **payload: object) -> None:
        event = {
            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
            "type": event_type,
            **payload,
        }
        with self._lock:
            self._events.append(event)

    def write_session(self, blocks: list[TranscriptBlock]) -> Path | None:
        with self._lock:
            events_snapshot = list(self._events)
        if not blocks and not events_snapshot:
            return None
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.logs_dir / f"system-audio-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        lines: list[str] = []
        if events_snapshot:
            lines.append("# Session Events")
            lines.extend(
                json.dumps(event, ensure_ascii=False, sort_keys=True)
                for event in events_snapshot
            )
        if blocks:
            if lines:
                lines.append("")
            lines.append("# Final Blocks")
            lines.extend(block.to_log_line() for block in blocks)
        file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.reset()
        return file_path


class SystemAudioTranslationController:
    def __init__(
        self,
        *,
        capture: LinuxParecAudioCapture,
        provider: ChunkedAudioTranslationProvider,
        session_logger: TranscriptSessionLogger,
        source_language: str,
        target_language: str,
        sample_rate_hz: int,
        segment_seconds: float,
        overlap_seconds: float,
        pending_segment_limit: int,
        reconnect_backoff_seconds: float,
        session_mode: SystemAudioSessionMode = "translate_es",
    ) -> None:
        self.capture = capture
        self.provider = provider
        self.session_logger = session_logger
        self.source_language = source_language
        self.target_language = target_language
        self.sample_rate_hz = sample_rate_hz
        self.pending_segment_limit = pending_segment_limit
        self.reconnect_backoff_seconds = reconnect_backoff_seconds
        self.session_mode = session_mode
        self.state: LiveSessionState = "inactive"
        self.history: list[TranscriptBlock] = []
        self.last_log_path: Path | None = None

        self._accumulator = PcmSegmentAccumulator(
            sample_rate_hz=sample_rate_hz,
            segment_seconds=segment_seconds,
            overlap_seconds=overlap_seconds,
        )
        self._pending_segments: deque[bytes] = deque(maxlen=pending_segment_limit)
        self._condition = threading.Condition()
        self._stop_event = threading.Event()
        self._worker_thread: threading.Thread | None = None
        self._last_translated_text: str | None = None
        self._on_state_changed: Callable[[LiveSessionState, str], None] | None = None
        self._on_block_ready: Callable[[TranscriptBlock], None] | None = None
        self._on_partial_text_changed: Callable[[LivePartialUpdate], None] | None = None

    def bind_callbacks(
        self,
        *,
        on_state_changed: Callable[[LiveSessionState, str], None],
        on_block_ready: Callable[[TranscriptBlock], None],
        on_partial_text_changed: Callable[[LivePartialUpdate], None] | None = None,
    ) -> None:
        self._on_state_changed = on_state_changed
        self._on_block_ready = on_block_ready
        self._on_partial_text_changed = on_partial_text_changed

    def start(self) -> None:
        if self.state not in {"inactive", "error"}:
            return
        self._stop_event.clear()
        self.history.clear()
        self._pending_segments.clear()
        self._accumulator.reset()
        self._set_state("starting", "Iniciando captura de audio del sistema…")
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="system-audio-translation-worker",
        )
        self._worker_thread.start()
        self.capture.start(self._on_audio_chunk)
        self._set_state("active", "Escuchando y traduciendo…")

    def pause(self) -> None:
        if self.state not in {"active", "reconnecting"}:
            return
        self.capture.stop()
        self._set_state("paused", "Sesión en pausa.")

    def resume(self) -> None:
        if self.state != "paused":
            return
        self.capture.start(self._on_audio_chunk)
        self._set_state("active", "Escuchando y traduciendo…")

    def reset(self) -> None:
        if self.state == "paused":
            self.resume()
            return
        if self.state in {"error", "reconnecting"}:
            self._set_state("active", "Reintentando conexión…")
            with self._condition:
                self._condition.notify_all()

    def stop(self) -> None:
        if self.state == "inactive":
            return
        self._set_state("stopping", "Deteniendo sesión…")
        self.capture.stop()
        self._stop_event.set()
        with self._condition:
            self._condition.notify_all()
        thread = self._worker_thread
        if thread is not None:
            thread.join(timeout=3.0)
        self._worker_thread = None
        self.last_log_path = self.session_logger.write_session(self.history)
        self._set_state("inactive", "Sesión detenida.")

    def _on_audio_chunk(self, chunk: bytes) -> None:
        if self.state not in {"active", "reconnecting"}:
            return
        ready_segments = self._accumulator.add_chunk(chunk)
        if not ready_segments:
            return
        with self._condition:
            for segment in ready_segments:
                self._pending_segments.append(segment)
            self._condition.notify_all()

    def _worker_loop(self) -> None:
        while not self._stop_event.is_set():
            segment = self._next_segment()
            if segment is None:
                continue
            try:
                original, translated = self.provider.transcribe_and_translate(
                    pcm_bytes=segment,
                    sample_rate_hz=self.sample_rate_hz,
                    source_language=self.source_language,
                    target_language=self.target_language,
                )
            except Exception as exc:
                self._set_state("reconnecting", f"Reconectando backend remoto… {exc}")
                with self._condition:
                    self._pending_segments.appendleft(segment)
                time.sleep(self.reconnect_backoff_seconds)
                continue

            if not translated.strip():
                continue
            if translated == self._last_translated_text:
                continue

            self._last_translated_text = translated
            block = TranscriptBlock(
                timestamp=datetime.now(),
                translated_text=translated,
                original_text=original or None,
            )
            self.history.append(block)
            self._set_state("active", "Escuchando y traduciendo…")
            if self._on_partial_text_changed is not None:
                self._on_partial_text_changed(LivePartialUpdate(kind="original", text=""))
                self._on_partial_text_changed(LivePartialUpdate(kind="translation", text=""))
            if self._on_block_ready is not None:
                self._on_block_ready(block)

    def _next_segment(self) -> bytes | None:
        with self._condition:
            while not self._pending_segments and not self._stop_event.is_set():
                self._condition.wait(timeout=0.5)
            if self._stop_event.is_set():
                return None
            return self._pending_segments.popleft()

    def _set_state(self, state: LiveSessionState, message: str) -> None:
        self.state = state
        if self._on_state_changed is not None:
            self._on_state_changed(state, message)


class ToggleSocketServer:
    def __init__(self, socket_path: Path, on_toggle: Callable[[], None]) -> None:
        self.socket_path = socket_path
        self.on_toggle = on_toggle
        self._thread: threading.Thread | None = None
        self._server_socket: socket.socket | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except OSError as exc:
                raise ToolRunnerConfigurationError(
                    "No se pudo limpiar el socket de control de la traducción de audio."
                ) from exc
        self._server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._server_socket.bind(str(self.socket_path))
        self._server_socket.listen(1)
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._serve_loop,
            daemon=True,
            name="system-audio-toggle-socket",
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._server_socket is not None:
            self._server_socket.close()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self._server_socket = None
        self._thread = None
        self.socket_path.unlink(missing_ok=True)

    def _serve_loop(self) -> None:
        server = self._server_socket
        if server is None:
            return
        while not self._stop_event.is_set():
            try:
                connection, _ = server.accept()
            except OSError:
                break
            with connection:
                payload = connection.recv(64).decode("utf-8", errors="ignore").strip()
                if payload == "toggle":
                    self.on_toggle()


def send_toggle_command(socket_path: Path) -> bool:
    if not socket_path.exists():
        return False
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(0.75)
            client.connect(str(socket_path))
            client.sendall(b"toggle")
        return True
    except OSError:
        socket_path.unlink(missing_ok=True)
        return False
