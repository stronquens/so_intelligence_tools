from __future__ import annotations

import json
import queue
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from so_intelligence_tools.local_tts.client import LocalTtsClient
from so_intelligence_tools.local_tts.codex_events import clean_visible_text, chunk_text


DEFAULT_CODEX_SESSIONS_DIR = Path.home() / ".codex" / "sessions"
VISIBLE_PHASES = {"commentary", "final", "final_answer"}


@dataclass(slots=True)
class CodexDesktopVisibleMessage:
    text: str
    timestamp: datetime | None = None
    phase: str | None = None


@dataclass(slots=True)
class CodexDesktopSpeechSegment:
    text: str
    event_timestamp: datetime | None = None
    phase: str | None = None
    kind: str = "message"
    priority_clear: bool = False


def parse_visible_text_from_codex_session_line(line: str) -> str | None:
    message = parse_visible_message_from_codex_session_line(line)
    return message.text if message else None


def parse_visible_message_from_codex_session_line(
    line: str,
) -> CodexDesktopVisibleMessage | None:
    try:
        payload = json.loads(line.strip().lstrip("\ufeff"))
    except json.JSONDecodeError:
        return None
    if payload.get("type") != "event_msg":
        return None
    event = payload.get("payload")
    if not isinstance(event, dict):
        return None
    if event.get("type") != "agent_message":
        return None
    phase = str(event.get("phase") or "")
    if phase and phase not in VISIBLE_PHASES:
        return None
    message = event.get("message")
    if not isinstance(message, str) or not message.strip():
        return None
    return CodexDesktopVisibleMessage(
        text=message,
        timestamp=_parse_codex_timestamp(payload.get("timestamp")),
        phase=phase or None,
    )


def parse_lifecycle_segment_from_codex_session_line(
    line: str,
) -> CodexDesktopSpeechSegment | None:
    try:
        payload = json.loads(line.strip().lstrip("\ufeff"))
    except json.JSONDecodeError:
        return None
    if payload.get("type") != "event_msg":
        return None
    event = payload.get("payload")
    if not isinstance(event, dict):
        return None
    event_type = str(event.get("type") or "")
    timestamp = _parse_codex_timestamp(payload.get("timestamp"))
    if event_type == "task_started":
        return CodexDesktopSpeechSegment(
            text="Inicio de tarea.",
            event_timestamp=timestamp,
            phase="task_started",
            kind="task_started",
            priority_clear=True,
        )
    if event_type == "task_complete":
        return CodexDesktopSpeechSegment(
            text="Fin de tarea.",
            event_timestamp=timestamp,
            phase="task_complete",
            kind="task_complete",
            priority_clear=True,
        )
    if event_type in {"task_failed", "task_error"}:
        return CodexDesktopSpeechSegment(
            text="Fin de tarea con error.",
            event_timestamp=timestamp,
            phase=event_type,
            kind="task_failed",
            priority_clear=True,
        )
    return None


def parse_action_segment_from_codex_session_line(
    line: str,
) -> CodexDesktopSpeechSegment | None:
    try:
        payload = json.loads(line.strip().lstrip("\ufeff"))
    except json.JSONDecodeError:
        return None
    timestamp = _parse_codex_timestamp(payload.get("timestamp"))
    top_type = payload.get("type")
    event = payload.get("payload")
    if not isinstance(event, dict):
        return None

    if top_type == "response_item":
        item_type = str(event.get("type") or "")
        if item_type == "function_call":
            name = _safe_label(event.get("name") or event.get("tool_name"))
            return CodexDesktopSpeechSegment(
                text=_function_call_started_text(name),
                event_timestamp=timestamp,
                phase="action",
                kind="tool_started",
            )
        if item_type == "function_call_output":
            return CodexDesktopSpeechSegment(
                text="Herramienta terminada.",
                event_timestamp=timestamp,
                phase="action",
                kind="tool_completed",
            )

    if top_type != "event_msg":
        return None

    event_type = str(event.get("type") or "")
    if event_type == "patch_apply_begin":
        return CodexDesktopSpeechSegment(
            text="Preparando cambios de archivos.",
            event_timestamp=timestamp,
            phase="action",
            kind="tool_started",
        )
    if event_type == "patch_apply_end":
        return CodexDesktopSpeechSegment(
            text="Cambios de archivos registrados.",
            event_timestamp=timestamp,
            phase="action",
            kind="tool_completed",
        )
    if event_type == "web_search_begin":
        return CodexDesktopSpeechSegment(
            text="Buscando en la web.",
            event_timestamp=timestamp,
            phase="action",
            kind="tool_started",
        )
    if event_type == "web_search_end":
        return CodexDesktopSpeechSegment(
            text="Busqueda web completada.",
            event_timestamp=timestamp,
            phase="action",
            kind="tool_completed",
        )
    return None


class CodexDesktopSessionTailer:
    def __init__(
        self,
        sessions_dir: Path | None = None,
        *,
        start_at_end: bool = True,
    ) -> None:
        self._sessions_dir = sessions_dir or DEFAULT_CODEX_SESSIONS_DIR
        self._start_at_end = start_at_end
        self._offsets: dict[Path, int] = {}

    def read_new_lines(self) -> list[str]:
        lines: list[str] = []
        for path in self._session_files():
            offset = self._offset_for(path)
            try:
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    handle.seek(offset)
                    lines.extend(handle.readlines())
                    self._offsets[path] = handle.tell()
            except OSError:
                continue
        self._forget_deleted_files()
        return lines

    def _session_files(self) -> list[Path]:
        if not self._sessions_dir.exists():
            return []
        try:
            return sorted(
                self._sessions_dir.rglob("*.jsonl"),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )[:25]
        except OSError:
            return []

    def _offset_for(self, path: Path) -> int:
        if path in self._offsets:
            return self._offsets[path]
        if not self._start_at_end:
            self._offsets[path] = 0
            return 0
        try:
            offset = path.stat().st_size
        except OSError:
            offset = 0
        self._offsets[path] = offset
        return offset

    def _forget_deleted_files(self) -> None:
        for path in list(self._offsets):
            if not path.exists():
                self._offsets.pop(path, None)


def visible_segments_from_session_lines(
    lines: Iterable[str],
    *,
    speech_detail: str = "standard",
    max_segment_chars: int = 500,
) -> list[str]:
    segments: list[str] = []
    for line in lines:
        text = parse_visible_text_from_codex_session_line(line)
        if not text:
            continue
        cleaned = clean_visible_text(
            text,
            code_block_mode="drop" if speech_detail == "no-code" else None,
            shorten_urls=speech_detail != "full",
        )
        if cleaned:
            segments.extend(chunk_text(cleaned, max_chars=max_segment_chars))
    return segments


def visible_speech_segments_from_session_lines(
    lines: Iterable[str],
    *,
    speech_detail: str = "standard",
    max_segment_chars: int = 500,
) -> list[CodexDesktopSpeechSegment]:
    segments: list[CodexDesktopSpeechSegment] = []
    detail = speech_detail.strip().lower()
    for line in lines:
        if detail in {"standard", "no-code", "full"}:
            completion_segments = _completion_segments_from_session_line(
                line,
                speech_detail=speech_detail,
                max_segment_chars=max_segment_chars,
            )
            if completion_segments:
                segments.extend(completion_segments)
                continue

        lifecycle = parse_lifecycle_segment_from_codex_session_line(line)
        if lifecycle is not None:
            segments.append(lifecycle)
            continue

        if detail != "minimal":
            action = parse_action_segment_from_codex_session_line(line)
            if action is not None:
                segments.append(action)
                continue

        if detail == "actions":
            continue
        if detail == "minimal":
            continue
        message = parse_visible_message_from_codex_session_line(line)
        if not message:
            continue
        cleaned = clean_visible_text(
            message.text,
            code_block_mode="drop" if speech_detail == "no-code" else None,
            shorten_urls=speech_detail != "full",
        )
        if cleaned:
            segments.extend(
                CodexDesktopSpeechSegment(
                    text=segment,
                    event_timestamp=message.timestamp,
                    phase=message.phase,
                    kind="message",
                )
                for segment in chunk_text(cleaned, max_chars=max_segment_chars)
            )
    return segments


def run_codex_desktop_session_listener(
    *,
    client: LocalTtsClient,
    sessions_dir: Path | None = None,
    poll_interval_seconds: float = 0.5,
    speech_detail: str = "standard",
    max_segment_chars: int = 500,
    start_at_end: bool = True,
    idle_timeout_seconds: float | None = None,
) -> int:
    tailer = CodexDesktopSessionTailer(
        sessions_dir=sessions_dir,
        start_at_end=start_at_end,
    )
    playback = CodexDesktopTimedSpeechPlaybackQueue(client)
    playback.start()
    deadline = (
        time.monotonic() + idle_timeout_seconds
        if idle_timeout_seconds is not None
        else None
    )
    try:
        while True:
            lines = tailer.read_new_lines()
            for segment in visible_speech_segments_from_session_lines(
                lines,
                speech_detail=speech_detail,
                max_segment_chars=max_segment_chars,
            ):
                if segment.priority_clear:
                    playback.clear(cancel_current=True)
                playback.enqueue(segment)
            if deadline is not None and time.monotonic() >= deadline:
                return 0
            time.sleep(max(0.05, poll_interval_seconds))
    except KeyboardInterrupt:
        return 0
    finally:
        playback.stop()


class CodexDesktopTimedSpeechPlaybackQueue:
    def __init__(self, client: LocalTtsClient) -> None:
        self._client = client
        self._synthesis_queue: queue.Queue[_QueuedSpeechSegment | None] = queue.Queue()
        self._playback_queue: queue.Queue[_SynthesizedSpeechSegment | None] = queue.Queue(
            maxsize=2
        )
        self._synthesis_thread = threading.Thread(
            target=self._run_synthesis,
            daemon=True,
        )
        self._playback_thread = threading.Thread(
            target=self._run_playback,
            daemon=True,
        )
        self._lock = threading.Lock()
        self._generation = 0
        self._action_generation = 0
        self._current_playback_kind: str | None = None

    def start(self) -> None:
        self._synthesis_thread.start()
        self._playback_thread.start()

    def enqueue(self, segment: CodexDesktopSpeechSegment) -> None:
        if _segment_replaces_pending_actions(segment):
            self.drop_pending_actions(cancel_current=True)
        with self._lock:
            generation = self._generation
            action_generation = self._action_generation
        self._synthesis_queue.put(
            _QueuedSpeechSegment(segment, generation, action_generation)
        )

    def clear(self, *, cancel_current: bool = False) -> None:
        with self._lock:
            self._generation += 1
        _drain_queue_preserving_stop(self._synthesis_queue)
        _drain_queue_preserving_stop(self._playback_queue)
        if cancel_current and hasattr(self._client, "stop_playback"):
            self._client.stop_playback()

    def drop_pending_actions(self, *, cancel_current: bool = False) -> None:
        with self._lock:
            self._action_generation += 1
            current_playback_kind = self._current_playback_kind
        _drain_matching_items_preserving_stop(
            self._synthesis_queue,
            _queued_item_is_action,
        )
        _drain_matching_items_preserving_stop(
            self._playback_queue,
            _synthesized_item_is_action,
        )
        if (
            cancel_current
            and _kind_is_action(current_playback_kind)
            and hasattr(self._client, "stop_playback")
        ):
            self._client.stop_playback()

    def stop(self) -> None:
        self._synthesis_queue.put(None)
        self._synthesis_thread.join()
        self._playback_thread.join()

    def _run_synthesis(self) -> None:
        while True:
            item = self._synthesis_queue.get()
            if item is None:
                self._playback_queue.put(None)
                return
            segment = item.segment
            generation = item.generation
            action_generation = item.action_generation
            queue_started_at = datetime.now(UTC)
            if hasattr(self._client, "synthesize") and hasattr(self._client, "play_audio"):
                synthesized = self._synthesize_if_current(
                    segment,
                    generation,
                    action_generation,
                    queue_started_at,
                )
                if synthesized is not None:
                    self._playback_queue.put(synthesized)
            elif hasattr(self._client, "speak_timed"):
                result = self._client.speak_timed(segment.text)
                _emit_latency_metric(segment, queue_started_at, result)
            else:
                spoken = self._client.speak(segment.text)
                result = _untimed_result(spoken)
                _emit_latency_metric(segment, queue_started_at, result)

    def _run_playback(self) -> None:
        while True:
            item = self._playback_queue.get()
            if item is None:
                return
            if not self._is_current_generation(item.generation):
                result = _desktop_timed_result(
                    spoken=False,
                    status="superseded",
                    synthesis_started_at=item.synthesis_started_at,
                    synthesis_finished_at=item.synthesis_finished_at,
                    synthesis_seconds=item.synthesis_seconds,
                )
                _emit_latency_metric(item.segment, item.queue_started_at, result)
                continue
            if not self._is_current_action_generation(
                item.segment,
                item.action_generation,
            ):
                result = _desktop_timed_result(
                    spoken=False,
                    status="superseded_action",
                    synthesis_started_at=item.synthesis_started_at,
                    synthesis_finished_at=item.synthesis_finished_at,
                    synthesis_seconds=item.synthesis_seconds,
                )
                _emit_latency_metric(item.segment, item.queue_started_at, result)
                continue
            playback_started_at = datetime.now(UTC)
            playback_started_perf = time.perf_counter()
            with self._lock:
                self._current_playback_kind = item.segment.kind
            try:
                played = self._client.play_audio(item.audio)
            finally:
                with self._lock:
                    if self._current_playback_kind == item.segment.kind:
                        self._current_playback_kind = None
                playback_finished_at = datetime.now(UTC)
                playback_seconds = time.perf_counter() - playback_started_perf
            result = _desktop_timed_result(
                spoken=played,
                status="spoken" if played else "playback_unavailable",
                synthesis_started_at=item.synthesis_started_at,
                synthesis_finished_at=item.synthesis_finished_at,
                playback_started_at=playback_started_at,
                playback_finished_at=playback_finished_at,
                synthesis_seconds=item.synthesis_seconds,
                playback_seconds=playback_seconds,
            )
            _emit_latency_metric(item.segment, item.queue_started_at, result)

    def _synthesize_if_current(
        self,
        segment: CodexDesktopSpeechSegment,
        generation: int,
        action_generation: int,
        queue_started_at: datetime,
    ) -> "_SynthesizedSpeechSegment | None":
        synthesis_started_at = datetime.now(UTC)
        synthesis_started_perf = time.perf_counter()
        audio = self._client.synthesize(segment.text)
        synthesis_finished_at = datetime.now(UTC)
        synthesis_seconds = time.perf_counter() - synthesis_started_perf
        if not audio:
            result = _desktop_timed_result(
                spoken=False,
                status="disabled",
                synthesis_started_at=synthesis_started_at,
                synthesis_finished_at=synthesis_finished_at,
                synthesis_seconds=synthesis_seconds,
            )
            _emit_latency_metric(segment, queue_started_at, result)
            return None
        if not self._is_current_generation(generation):
            result = _desktop_timed_result(
                spoken=False,
                status="superseded",
                synthesis_started_at=synthesis_started_at,
                synthesis_finished_at=synthesis_finished_at,
                synthesis_seconds=synthesis_seconds,
            )
            _emit_latency_metric(segment, queue_started_at, result)
            return None
        if not self._is_current_action_generation(segment, action_generation):
            result = _desktop_timed_result(
                spoken=False,
                status="superseded_action",
                synthesis_started_at=synthesis_started_at,
                synthesis_finished_at=synthesis_finished_at,
                synthesis_seconds=synthesis_seconds,
            )
            _emit_latency_metric(segment, queue_started_at, result)
            return None
        return _SynthesizedSpeechSegment(
            segment=segment,
            generation=generation,
            action_generation=action_generation,
            queue_started_at=queue_started_at,
            audio=audio,
            synthesis_started_at=synthesis_started_at,
            synthesis_finished_at=synthesis_finished_at,
            synthesis_seconds=synthesis_seconds,
        )

    def _is_current_generation(self, generation: int) -> bool:
        with self._lock:
            return generation == self._generation

    def _is_current_action_generation(
        self,
        segment: CodexDesktopSpeechSegment,
        action_generation: int,
    ) -> bool:
        if not _kind_is_action(segment.kind):
            return True
        with self._lock:
            return action_generation == self._action_generation


def _emit_latency_metric(
    segment: CodexDesktopSpeechSegment,
    queue_started_at: datetime,
    result,
) -> None:
    payload = {
        "event": "codex_desktop_tts_latency",
        "phase": segment.phase,
        "kind": segment.kind,
        "status": getattr(result, "status", None),
        "spoken": getattr(result, "spoken", None),
        "text_chars": len(segment.text),
        "message_timestamp": _iso_or_none(segment.event_timestamp),
        "queue_started_at": queue_started_at.isoformat(),
        "synthesis_started_at": _iso_or_none(
            getattr(result, "synthesis_started_at", None)
        ),
        "synthesis_finished_at": _iso_or_none(
            getattr(result, "synthesis_finished_at", None)
        ),
        "playback_started_at": _iso_or_none(getattr(result, "playback_started_at", None)),
        "playback_finished_at": _iso_or_none(
            getattr(result, "playback_finished_at", None)
        ),
        "message_to_queue_seconds": _seconds_between(
            segment.event_timestamp,
            queue_started_at,
        ),
        "message_to_playback_start_seconds": _seconds_between(
            segment.event_timestamp,
            getattr(result, "playback_started_at", None),
        ),
        "queue_to_playback_start_seconds": _seconds_between(
            queue_started_at,
            getattr(result, "playback_started_at", None),
        ),
        "synthesis_seconds": getattr(result, "synthesis_seconds", None),
        "playback_seconds": getattr(result, "playback_seconds", None),
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)


def _parse_codex_timestamp(value) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _completion_segments_from_session_line(
    line: str,
    *,
    speech_detail: str,
    max_segment_chars: int,
) -> list[CodexDesktopSpeechSegment]:
    try:
        payload = json.loads(line.strip().lstrip("\ufeff"))
    except json.JSONDecodeError:
        return []
    if payload.get("type") != "event_msg":
        return []
    event = payload.get("payload")
    if not isinstance(event, dict):
        return []
    event_type = str(event.get("type") or "")
    if event_type not in {"task_complete", "task_failed", "task_error"}:
        return []

    timestamp = _parse_codex_timestamp(payload.get("timestamp"))
    message = event.get("last_agent_message")
    segments: list[CodexDesktopSpeechSegment] = [
        CodexDesktopSpeechSegment(
            text=(
                "Fin de tarea con error."
                if event_type in {"task_failed", "task_error"}
                else "Fin de tarea."
            ),
            event_timestamp=timestamp,
            phase=event_type,
            kind="task_failed"
            if event_type in {"task_failed", "task_error"}
            else "task_complete",
            priority_clear=True,
        )
    ]
    if isinstance(message, str) and message.strip():
        cleaned = clean_visible_text(
            message,
            code_block_mode="drop" if speech_detail == "no-code" else None,
            shorten_urls=speech_detail != "full",
        )
        for text in chunk_text(cleaned, max_chars=max_segment_chars):
            segments.append(
                CodexDesktopSpeechSegment(
                    text=text,
                    event_timestamp=timestamp,
                    phase="final_answer",
                    kind="message",
                )
            )
    return segments


def _function_call_started_text(name: str) -> str:
    if not name:
        return "Usando herramienta."
    lowered = name.lower()
    if "shell_command" in lowered or "exec_command" in lowered:
        return "Ejecutando comando."
    if "apply_patch" in lowered:
        return "Preparando cambios de archivos."
    if "web" in lowered and "search" in lowered:
        return "Buscando en la web."
    return f"Usando herramienta {name}."


def _safe_label(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    allowed = []
    for char in value:
        if char.isalnum() or char in "_.:-":
            allowed.append(char)
        elif char.isspace():
            allowed.append(" ")
    return " ".join("".join(allowed).split())[:60].strip()


def _seconds_between(start: datetime | None, end: datetime | None) -> float | None:
    if start is None or end is None:
        return None
    return max(0.0, (end - start).total_seconds())


def _iso_or_none(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _untimed_result(result):
    return result


@dataclass(slots=True)
class _QueuedSpeechSegment:
    segment: CodexDesktopSpeechSegment
    generation: int
    action_generation: int


@dataclass(slots=True)
class _SynthesizedSpeechSegment:
    segment: CodexDesktopSpeechSegment
    generation: int
    action_generation: int
    queue_started_at: datetime
    audio: bytes
    synthesis_started_at: datetime
    synthesis_finished_at: datetime
    synthesis_seconds: float


@dataclass(slots=True)
class _DesktopTimedResult:
    spoken: bool
    status: str
    synthesis_started_at: datetime | None = None
    synthesis_finished_at: datetime | None = None
    playback_started_at: datetime | None = None
    playback_finished_at: datetime | None = None
    synthesis_seconds: float | None = None
    playback_seconds: float | None = None


def _desktop_timed_result(**kwargs) -> _DesktopTimedResult:
    return _DesktopTimedResult(**kwargs)


def _drain_queue_preserving_stop(target_queue: queue.Queue) -> None:
    while True:
        try:
            item = target_queue.get_nowait()
        except queue.Empty:
            break
        if item is None:
            target_queue.put(None)
            break


def _drain_matching_items_preserving_stop(target_queue: queue.Queue, predicate) -> None:
    retained = []
    stop_seen = False
    while True:
        try:
            item = target_queue.get_nowait()
        except queue.Empty:
            break
        if item is None:
            stop_seen = True
            continue
        if not predicate(item):
            retained.append(item)
    for item in retained:
        target_queue.put(item)
    if stop_seen:
        target_queue.put(None)


def _segment_replaces_pending_actions(segment: CodexDesktopSpeechSegment) -> bool:
    return segment.kind == "message"


def _kind_is_action(kind: str | None) -> bool:
    return kind in {"tool_started", "tool_completed"}


def _queued_item_is_action(item: _QueuedSpeechSegment) -> bool:
    return _kind_is_action(item.segment.kind)


def _synthesized_item_is_action(item: _SynthesizedSpeechSegment) -> bool:
    return _kind_is_action(item.segment.kind)
