from __future__ import annotations

import asyncio
import base64
from collections import deque
from dataclasses import dataclass, field
import json
from pathlib import Path
import threading
from urllib.parse import urlencode

import websockets

from so_intelligence_tools.domain.errors import StreamingSessionError
from so_intelligence_tools.system_audio_translation.session import TranscriptSessionLogger
from so_intelligence_tools.voice_translation_virtual_microphone.audio import (
    LinuxMicrophoneAudioCapture,
    PulseAudioVirtualMicrophone,
    scale_pcm_s16le,
)


@dataclass(slots=True)
class OpenAIRealtimeVoiceTranslationController:
    capture: LinuxMicrophoneAudioCapture
    virtual_microphone: PulseAudioVirtualMicrophone
    session_logger: TranscriptSessionLogger
    api_key: str
    model: str
    source_language: str
    target_language: str
    voice: str
    reconnect_backoff_seconds: float
    base_url: str | None = None
    max_pending_audio_chunks: int = 128
    silence_duration_ms: int = 260
    prefix_padding_ms: int = 160
    vad_threshold: float = 0.4
    close_drain_timeout_seconds: float = 8.0
    output_volume: float = 1.25
    owns_virtual_microphone: bool = True
    write_session_log_on_stop: bool = True
    state: str = field(init=False, default="inactive")
    last_log_path: Path | None = field(init=False, default=None)
    _pending_audio: deque[bytes] = field(init=False)
    _condition: threading.Condition = field(init=False)
    _stop_event: threading.Event = field(init=False)
    _reconnect_request: threading.Event = field(init=False)
    _worker_thread: threading.Thread | None = field(init=False, default=None)
    _output_audio_chunks: int = field(init=False, default=0)
    _output_audio_bytes: int = field(init=False, default=0)
    _seen_event_types: set[str] = field(init=False, default_factory=set)

    def __post_init__(self) -> None:
        self._pending_audio = deque(maxlen=self.max_pending_audio_chunks)
        self._condition = threading.Condition()
        self._stop_event = threading.Event()
        self._reconnect_request = threading.Event()

    def start(self) -> None:
        if self.state not in {"inactive", "error"}:
            return
        self.session_logger.reset()
        self._pending_audio.clear()
        self._stop_event.clear()
        self._reconnect_request.clear()
        self.session_logger.record_event(
            "session_started",
            model=self.model,
            source_language=self.source_language,
            target_language=self.target_language,
            voice=self.voice,
            virtual_microphone=self.virtual_microphone.monitor_source_name,
            physical_source=self.capture.source or "default",
            sample_rate_hz=self.capture.sample_rate_hz,
            chunk_ms=self.capture.chunk_ms,
        )
        self._set_state("starting", "Creando micrófono virtual…")
        if self.owns_virtual_microphone:
            self.virtual_microphone.start()
        self._set_state(
            "starting",
            f"Micrófono virtual listo: {self.virtual_microphone.monitor_source_name}",
        )
        self._worker_thread = threading.Thread(
            target=self._worker_main,
            daemon=True,
            name="voice-translation-realtime-worker",
        )
        self._worker_thread.start()
        self.capture.start(self._on_audio_chunk)
        self._set_state("active", "Traduciendo tu voz en tiempo real…")

    def stop(self) -> None:
        if self.state == "inactive":
            return
        self._set_state("stopping", "Deteniendo traducción de voz…")
        self.capture.stop()
        self._stop_event.set()
        self._reconnect_request.set()
        with self._condition:
            self._condition.notify_all()
        thread = self._worker_thread
        if thread is not None:
            thread.join(timeout=4.0)
        self._worker_thread = None
        if self.owns_virtual_microphone:
            self.virtual_microphone.stop()
        if self.write_session_log_on_stop:
            self.last_log_path = self.session_logger.write_session([])
        self._set_state("inactive", "Traducción de voz detenida.")

    def _on_audio_chunk(self, chunk: bytes) -> None:
        if self.state not in {"active", "reconnecting"}:
            return
        with self._condition:
            self._pending_audio.append(chunk)
            self._condition.notify_all()

    def _worker_main(self) -> None:
        asyncio.run(self._async_worker_loop())

    async def _async_worker_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                control_result = await self._run_connection()
                if control_result == "stop":
                    break
                self._set_state("reconnecting", "Reiniciando sesión realtime…")
                await asyncio.sleep(0.1)
            except Exception as exc:  # pragma: no cover - surfaced through logs/manual runs
                if self._stop_event.is_set():
                    break
                self.session_logger.record_event("connection_error", message=str(exc))
                self._set_state("reconnecting", f"Reconectando OpenAI realtime… {exc}")
                await asyncio.sleep(self.reconnect_backoff_seconds)

    async def _run_connection(self) -> str:
        async with websockets.connect(
            self._build_translation_websocket_url(),
            additional_headers={
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Safety-Identifier": "so-intelligence-tools-local-user",
            },
            max_size=None,
        ) as connection:
            await connection.send(json.dumps(self._build_session_update_payload()))
            self.session_logger.record_event("realtime_connected", model=self.model)
            self._set_state("active", "Traduciendo tu voz en tiempo real…")
            sender = asyncio.create_task(self._sender_loop(connection))
            receiver = asyncio.create_task(self._receiver_loop(connection))
            controller = asyncio.create_task(self._control_loop())
            done, pending = await asyncio.wait(
                {sender, receiver, controller},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in done:
                exc = task.exception()
                if exc is not None:
                    raise exc

            if self._stop_event.is_set():
                await self._stop_translation_connection(
                    connection=connection,
                    sender=sender,
                    receiver=receiver,
                )
                return "stop"

            if controller in done:
                control_result = controller.result()
                if control_result == "stop":
                    await self._stop_translation_connection(
                        connection=connection,
                        sender=sender,
                        receiver=receiver,
                    )
                    return "stop"
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)
                return control_result

            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            return "reconnect"

    async def _sender_loop(self, connection: object) -> None:
        while not self._stop_event.is_set() and not self._reconnect_request.is_set():
            chunk = await asyncio.to_thread(self._next_audio_chunk_blocking)
            if not chunk:
                continue
            encoded = base64.b64encode(chunk).decode("ascii")
            await connection.send(
                json.dumps(
                    {
                        "type": "session.input_audio_buffer.append",
                        "audio": encoded,
                    }
                )
            )

    async def _receiver_loop(self, connection: object) -> None:
        async for raw_event in connection:
            event = _coerce_realtime_event(raw_event)
            event_type = _event_get(event, "type")
            self._record_event_type(event_type)
            if event_type in {
                "session.output_audio.delta",
                "response.output_audio.delta",
                "response.audio.delta",
            }:
                audio = _decode_audio_delta(event)
                if audio:
                    output_audio = scale_pcm_s16le(audio, self.output_volume)
                    await asyncio.to_thread(self.virtual_microphone.write, output_audio)
                    self._record_output_audio_chunk(len(audio))
            elif event_type in {
                "session.output_transcript.delta",
                "session.input_transcript.delta",
                "response.output_audio_transcript.delta",
                "response.audio_transcript.delta",
                "response.output_text.delta",
            }:
                delta = _event_get(event, "delta")
                if delta.strip():
                    self.session_logger.record_event("translated_text_delta", text=delta)
            elif event_type == "response.done":
                self.session_logger.record_event("response_done")
                self._record_response_done(event)
            elif event_type == "session.closed":
                self.session_logger.record_event("session_closed")
                break
            elif event_type == "input_audio_buffer.speech_started":
                self.session_logger.record_event("speech_started")
            elif event_type in {
                "input_audio_buffer.speech_stopped",
                "session.input_audio_buffer.speech_stopped",
            }:
                self.session_logger.record_event("speech_stopped")
            elif event_type == "error":
                raise StreamingSessionError(_extract_realtime_error_message(event))

    async def _control_loop(self) -> str:
        while True:
            if self._stop_event.is_set():
                return "stop"
            if self._reconnect_request.is_set():
                self._reconnect_request.clear()
                return "reconnect"
            await asyncio.sleep(0.05)

    def _next_audio_chunk_blocking(self) -> bytes | None:
        with self._condition:
            while not self._pending_audio and not self._stop_event.is_set() and not self._reconnect_request.is_set():
                self._condition.wait(timeout=0.5)
            if self._stop_event.is_set() or self._reconnect_request.is_set():
                return None
            return self._pending_audio.popleft()

    def _set_state(self, state: str, message: str) -> None:
        self.state = state
        self.session_logger.record_event("state_changed", state=state, message=message)
        print(message, flush=True)

    def _build_session_update_payload(self) -> dict[str, object]:
        return {
            "type": "session.update",
            "session": {
                "audio": {
                    "output": {
                        "language": _normalize_translation_language(self.target_language),
                    },
                },
            },
        }

    def _build_translation_websocket_url(self) -> str:
        base = (self.base_url or "https://api.openai.com/v1").rstrip("/")
        if base.startswith("https://"):
            base = "wss://" + base.removeprefix("https://")
        elif base.startswith("http://"):
            base = "ws://" + base.removeprefix("http://")
        return f"{base}/realtime/translations?{urlencode({'model': self.model})}"

    def _record_output_audio_chunk(self, byte_count: int) -> None:
        self._output_audio_chunks += 1
        self._output_audio_bytes += byte_count
        if self._output_audio_chunks == 1 or self._output_audio_chunks % 25 == 0:
            self.session_logger.record_event(
                "output_audio_written",
                chunks=self._output_audio_chunks,
                bytes=self._output_audio_bytes,
                virtual_microphone=self.virtual_microphone.monitor_source_name,
            )

    def _record_event_type(self, event_type: str) -> None:
        if not event_type or event_type in self._seen_event_types:
            return
        self._seen_event_types.add(event_type)
        self.session_logger.record_event(
            "realtime_event_seen",
            realtime_event_type=event_type,
        )

    def _record_response_done(self, event: object) -> None:
        response = _event_get(event, "response")
        if response is None:
            return
        status = _event_get(response, "status")
        status_details = _event_get(response, "status_details")
        output = _event_get(response, "output")
        output_types: list[str] = []
        if isinstance(output, list):
            for item in output:
                item_type = getattr(item, "type", None)
                if isinstance(item_type, str):
                    output_types.append(item_type)
        self.session_logger.record_event(
            "response_done_detail",
            status=status,
            status_details=str(status_details) if status_details is not None else None,
            output_types=output_types,
        )

    async def _stop_translation_connection(
        self,
        *,
        connection: object,
        sender: asyncio.Task[None],
        receiver: asyncio.Task[None],
    ) -> None:
        sender.cancel()
        await asyncio.gather(sender, return_exceptions=True)
        await self._close_translation_session(connection)
        try:
            await asyncio.wait_for(receiver, timeout=self.close_drain_timeout_seconds)
        except TimeoutError:
            self.session_logger.record_event(
                "session_close_timeout",
                timeout_seconds=self.close_drain_timeout_seconds,
            )
            receiver.cancel()
            await asyncio.gather(receiver, return_exceptions=True)

    async def _close_translation_session(self, connection: object) -> None:
        try:
            await connection.send(json.dumps({"type": "session.close"}))
            self.session_logger.record_event("session_close_sent")
        except Exception:
            return


def _decode_audio_delta(event: object) -> bytes:
    delta = _event_get(event, "delta")
    if delta is None:
        delta = _event_get(event, "audio")
    if not isinstance(delta, str) or not delta:
        return b""
    return base64.b64decode(delta)


def _extract_realtime_error_message(event: object) -> str:
    error = _event_get(event, "error")
    if error is None:
        return "La sesión OpenAI realtime devolvió un error."
    message = _event_get(error, "message")
    if isinstance(message, str) and message.strip():
        return message
    return str(error)


def _coerce_realtime_event(raw_event: object) -> object:
    if isinstance(raw_event, str):
        return json.loads(raw_event)
    if isinstance(raw_event, bytes):
        return json.loads(raw_event.decode("utf-8"))
    return raw_event


def _event_get(event: object, key: str) -> object:
    if isinstance(event, dict):
        return event.get(key)
    return getattr(event, key, None)


def _normalize_translation_language(language: str) -> str:
    normalized = language.strip().lower()
    aliases = {
        "english": "en",
        "en-us": "en",
        "en-gb": "en",
        "spanish": "es",
        "español": "es",
        "espanol": "es",
    }
    return aliases.get(normalized, normalized or "en")
