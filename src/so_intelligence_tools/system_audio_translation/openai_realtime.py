from __future__ import annotations

import asyncio
import base64
from collections import OrderedDict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import threading

from openai import AsyncOpenAI

from so_intelligence_tools.domain.errors import StreamingSessionError
from so_intelligence_tools.domain.models import LivePartialUpdate, LiveSessionState, TranscriptBlock
from so_intelligence_tools.system_audio_translation.audio_capture import LinuxParecAudioCapture
from so_intelligence_tools.system_audio_translation.session import TranscriptSessionLogger


@dataclass(slots=True)
class _RealtimeTurn:
    input_item_id: str
    original_partial: str = ""
    original_final: str = ""
    translation_partial: str = ""
    translation_final: str = ""
    response_id: str | None = None

    @property
    def best_original_text(self) -> str:
        return _pick_most_complete_text(self.original_final, self.original_partial)

    @property
    def is_ready(self) -> bool:
        return bool(self.translation_final.strip() and self.best_original_text.strip())


@dataclass(slots=True)
class OpenAIRealtimeTranslationController:
    capture: LinuxParecAudioCapture
    session_logger: TranscriptSessionLogger
    api_key: str
    model: str
    source_language: str
    target_language: str
    reconnect_backoff_seconds: float
    max_pending_audio_chunks: int = 128
    base_url: str | None = None
    silence_duration_ms: int = 280
    prefix_padding_ms: int = 180
    vad_threshold: float = 0.4
    turn_detection_type: str = "server_vad"
    semantic_vad_eagerness: str = "medium"
    interrupt_response: bool = False
    max_output_tokens: int = 1024
    translate_completed_transcripts: bool = False
    text_translation_model: str = "gpt-4o-mini"
    state: LiveSessionState = field(init=False, default="inactive")
    history: list[TranscriptBlock] = field(init=False, default_factory=list)
    last_log_path: Path | None = field(init=False, default=None)
    _pending_audio: deque[bytes] = field(init=False)
    _condition: threading.Condition = field(init=False)
    _stop_event: threading.Event = field(init=False)
    _reconnect_request: threading.Event = field(init=False)
    _worker_thread: threading.Thread | None = field(init=False, default=None)
    _last_translated_text: str | None = field(init=False, default=None)
    _on_state_changed: Callable[[LiveSessionState, str], None] | None = field(
        init=False,
        default=None,
    )
    _on_block_ready: Callable[[TranscriptBlock], None] | None = field(
        init=False,
        default=None,
    )
    _on_partial_text_changed: Callable[[LivePartialUpdate], None] | None = field(
        init=False,
        default=None,
    )
    _last_logged_original_partial: str = field(init=False, default="")
    _last_logged_translation_partial: str = field(init=False, default="")

    def __post_init__(self) -> None:
        self._pending_audio: deque[bytes] = deque(maxlen=self.max_pending_audio_chunks)
        self._condition = threading.Condition()
        self._stop_event = threading.Event()
        self._reconnect_request = threading.Event()

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
        self._reconnect_request.clear()
        self.history.clear()
        self._pending_audio.clear()
        self.session_logger.reset()
        self.session_logger.record_event(
            "session_started",
            mode="openai_realtime",
            model=self.model,
            turn_detection_type=self.turn_detection_type,
            silence_duration_ms=self.silence_duration_ms,
            prefix_padding_ms=self.prefix_padding_ms,
            vad_threshold=self.vad_threshold,
            translate_completed_transcripts=self.translate_completed_transcripts,
        )
        self._set_state("starting", "Iniciando traduccion OpenAI realtime…")
        self._worker_thread = threading.Thread(
            target=self._worker_main,
            daemon=True,
            name="openai-realtime-translation-worker",
        )
        self._worker_thread.start()
        self.capture.start(self._on_audio_chunk)
        self._set_state("active", "Escuchando y traduciendo… (OpenAI realtime)")

    def pause(self) -> None:
        if self.state not in {"active", "reconnecting"}:
            return
        self.capture.stop()
        with self._condition:
            self._pending_audio.clear()
        self._set_state("paused", "Sesion en pausa.")

    def resume(self) -> None:
        if self.state != "paused":
            return
        self.capture.start(self._on_audio_chunk)
        self._set_state("active", "Escuchando y traduciendo… (OpenAI realtime)")

    def reset(self) -> None:
        if self.state == "paused":
            self.resume()
            return
        if self.state in {"active", "error", "reconnecting"}:
            self._reconnect_request.set()
            with self._condition:
                self._pending_audio.clear()
            if self._on_partial_text_changed is not None:
                self._clear_partials()
            self._set_state("reconnecting", "Reiniciando sesion realtime…")

    def stop(self) -> None:
        if self.state == "inactive":
            return
        self._set_state("stopping", "Deteniendo sesion…")
        self.capture.stop()
        self._stop_event.set()
        self._reconnect_request.set()
        with self._condition:
            self._condition.notify_all()
        thread = self._worker_thread
        if thread is not None:
            thread.join(timeout=4.0)
        self._worker_thread = None
        self.last_log_path = self.session_logger.write_session(self.history)
        self._set_state("inactive", "Sesion detenida.")

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
                if control_result == "reconnect":
                    self._set_state("reconnecting", "Reiniciando sesion realtime…")
                    await asyncio.sleep(0.1)
                    continue
            except Exception as exc:  # pragma: no cover - covered via callback-facing behavior
                if self._stop_event.is_set():
                    break
                self._set_state("reconnecting", f"Reconectando OpenAI realtime… {exc}")
                await asyncio.sleep(self.reconnect_backoff_seconds)

    async def _run_connection(self) -> str:
        client_kwargs: dict[str, str] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url.rstrip("/")
        client = AsyncOpenAI(**client_kwargs)
        async with client.realtime.connect(
            model=self.model,
        ) as connection:
            await connection.send(
                self._build_session_update_payload()
            )
            self._set_state("active", "Escuchando y traduciendo… (OpenAI realtime)")
            sender = asyncio.create_task(self._sender_loop(connection))
            receiver = asyncio.create_task(self._receiver_loop(connection))
            controller = asyncio.create_task(self._control_loop())
            done, pending = await asyncio.wait(
                {sender, receiver, controller},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for task in done:
                exc = task.exception()
                if exc is not None:
                    raise exc
            return controller.result() if controller in done else "reconnect"

    async def _sender_loop(self, connection: object) -> None:
        while not self._stop_event.is_set() and not self._reconnect_request.is_set():
            chunk = await asyncio.to_thread(self._next_audio_chunk_blocking)
            if not chunk:
                continue
            encoded = base64.b64encode(chunk).decode("ascii")
            await connection.send({"type": "input_audio_buffer.append", "audio": encoded})

    async def _receiver_loop(self, connection: object) -> None:
        turns: OrderedDict[str, _RealtimeTurn] = OrderedDict()
        response_to_input_item: dict[str, str] = {}
        unassigned_input_items: deque[str] = deque()
        published_input_items: set[str] = set()
        pending_transcript = ""
        async for event in connection:
            event_type = getattr(event, "type", "")
            if event_type == "input_audio_buffer.committed":
                input_item_id = getattr(event, "item_id", "") or ""
                if input_item_id:
                    _ensure_turn(turns, input_item_id)
                    unassigned_input_items.append(input_item_id)
                    self.session_logger.record_event(
                        "input_committed",
                        input_item_id=input_item_id,
                    )
            elif event_type == "response.created":
                response_id = _extract_response_id(event)
                input_item_id = _assign_response_to_next_turn(
                    turns,
                    unassigned_input_items,
                    response_to_input_item,
                    response_id,
                )
                if input_item_id and response_id:
                    turns[input_item_id].response_id = response_id
                    self.session_logger.record_event(
                        "response_created",
                        input_item_id=input_item_id,
                        response_id=response_id,
                    )
            elif event_type == "response.output_text.delta":
                if self.translate_completed_transcripts:
                    continue
                turn = _turn_for_response_event(
                    turns,
                    unassigned_input_items,
                    response_to_input_item,
                    event,
                )
                turn.translation_partial += getattr(event, "delta", "") or ""
                if self._on_partial_text_changed is not None:
                    self._on_partial_text_changed(
                        LivePartialUpdate(
                            kind="translation",
                            text=turn.translation_partial,
                        )
                    )
                self._log_partial_if_needed(
                    kind="translation",
                    text=turn.translation_partial,
                )
            elif event_type == "response.output_text.done":
                if self.translate_completed_transcripts:
                    continue
                final_text = getattr(event, "text", "").strip()
                if not final_text or final_text == self._last_translated_text:
                    continue
                self._last_translated_text = final_text
                turn = _turn_for_response_event(
                    turns,
                    unassigned_input_items,
                    response_to_input_item,
                    event,
                )
                turn.translation_final = final_text
                self.session_logger.record_event(
                    "translation_final",
                    input_item_id=turn.input_item_id,
                    response_id=turn.response_id,
                    text=final_text,
                )
                self._publish_ready_turns(turns, published_input_items)
                self._set_state("active", "Escuchando y traduciendo… (OpenAI realtime)")
            elif event_type == "conversation.item.input_audio_transcription.delta":
                input_item_id = getattr(event, "item_id", "") or ""
                if input_item_id in published_input_items:
                    continue
                delta = getattr(event, "delta", "") or ""
                turn = _ensure_turn(turns, input_item_id)
                turn.original_partial += delta
                if turn.original_partial.strip() and self._on_partial_text_changed is not None:
                    self._on_partial_text_changed(
                        LivePartialUpdate(kind="original", text=turn.original_partial)
                    )
                self._log_partial_if_needed(
                    kind="original",
                    text=turn.original_partial,
                )
            elif event_type == "conversation.item.input_audio_transcription.completed":
                input_item_id = getattr(event, "item_id", "") or ""
                if input_item_id in published_input_items:
                    continue
                transcript = _clean_transcript_text(getattr(event, "transcript", ""))
                if transcript:
                    self.session_logger.record_event(
                        "transcription_final",
                        input_item_id=input_item_id,
                        text=transcript,
                    )
                    if self.translate_completed_transcripts:
                        previous_pending = bool(pending_transcript.strip())
                        pending_transcript = _join_transcript_segments(
                            pending_transcript,
                            transcript,
                        )
                        if self._on_partial_text_changed is not None:
                            self._on_partial_text_changed(
                                LivePartialUpdate(
                                    kind="original",
                                    text=pending_transcript,
                                )
                            )
                        if not _should_flush_transcript(
                            pending_transcript,
                            latest_segment=transcript,
                            previous_pending=previous_pending,
                        ):
                            continue
                        translated_text = await self._translate_text(pending_transcript)
                        if translated_text:
                            self._publish_translated_transcript_block(
                                original_text=pending_transcript,
                                translated_text=translated_text,
                            )
                        pending_transcript = ""
                        continue
                    turn = _ensure_turn(turns, input_item_id)
                    turn.original_final = _pick_most_complete_text(
                        turn.original_final,
                        transcript,
                    )
                    turn.original_partial = _pick_most_complete_text(
                        turn.original_partial,
                        transcript,
                    )
                    if self._on_partial_text_changed is not None:
                        self._on_partial_text_changed(
                            LivePartialUpdate(kind="original", text=turn.original_partial)
                        )
                    self._publish_ready_turns(turns, published_input_items)
            elif event_type == "input_audio_buffer.speech_started":
                self.session_logger.record_event("speech_started")
                self._set_state("active", "Voz detectada…")
            elif event_type == "input_audio_buffer.speech_stopped":
                self.session_logger.record_event("speech_stopped")
                self._set_state("active", "Procesando traduccion…")
            elif event_type == "error":
                detail = _extract_realtime_error_message(event)
                raise StreamingSessionError(detail)
        if self.translate_completed_transcripts and pending_transcript.strip():
            translated_text = await self._translate_text(pending_transcript)
            if translated_text:
                self._publish_translated_transcript_block(
                    original_text=pending_transcript,
                    translated_text=translated_text,
                )
        if not self.translate_completed_transcripts:
            self._flush_residual_turns(turns, published_input_items)

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

    def _set_state(self, state: LiveSessionState, message: str) -> None:
        self.state = state
        self.session_logger.record_event(
            "state_changed",
            state=state,
            message=message,
        )
        if self._on_state_changed is not None:
            self._on_state_changed(state, message)

    def _clear_partials(self) -> None:
        if self._on_partial_text_changed is None:
            return
        self._on_partial_text_changed(LivePartialUpdate(kind="original", text=""))
        self._on_partial_text_changed(LivePartialUpdate(kind="translation", text=""))

    def _publish_translated_transcript_block(
        self,
        *,
        original_text: str,
        translated_text: str,
    ) -> None:
        block = TranscriptBlock(
            timestamp=datetime.now(),
            translated_text=translated_text,
            original_text=original_text,
        )
        self.history.append(block)
        self.session_logger.record_event(
            "block_published",
            original_text=original_text,
            translated_text=translated_text,
            source="completed_transcript_translation",
        )
        if self._on_partial_text_changed is not None:
            self._clear_partials()
        if self._on_block_ready is not None:
            self._on_block_ready(block)

    async def _translate_text(self, text: str) -> str:
        client_kwargs: dict[str, str] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url.rstrip("/")
        client = AsyncOpenAI(**client_kwargs)
        response = await client.chat.completions.create(
            model=self.text_translation_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Translate English transcript fragments to natural Spanish subtitles. "
                        "Preserve the meaning, resolve obvious fragment boundaries, and output "
                        "only Spanish without labels or explanations."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""

    def _publish_ready_turns(
        self,
        turns: OrderedDict[str, _RealtimeTurn],
        published_input_items: set[str],
    ) -> None:
        while turns:
            input_item_id, turn = next(iter(turns.items()))
            if not turn.is_ready:
                return
            block = TranscriptBlock(
                timestamp=datetime.now(),
                translated_text=turn.translation_final,
                original_text=turn.best_original_text,
            )
            self.history.append(block)
            self.session_logger.record_event(
                "block_published",
                input_item_id=input_item_id,
                original_text=turn.best_original_text,
                translated_text=turn.translation_final,
                source="realtime_turn",
            )
            turns.popitem(last=False)
            published_input_items.add(input_item_id)
            if self._on_partial_text_changed is not None:
                self._clear_partials()
            if self._on_block_ready is not None:
                self._on_block_ready(block)

    def _flush_residual_turns(
        self,
        turns: OrderedDict[str, _RealtimeTurn],
        published_input_items: set[str],
    ) -> None:
        while turns:
            input_item_id, turn = turns.popitem(last=False)
            fallback_translation = turn.translation_final or turn.translation_partial
            fallback_original = turn.best_original_text
            if not fallback_original.strip() or not fallback_translation.strip():
                continue
            block = TranscriptBlock(
                timestamp=datetime.now(),
                translated_text=fallback_translation.strip(),
                original_text=fallback_original.strip(),
            )
            self.history.append(block)
            self.session_logger.record_event(
                "residual_block_published",
                input_item_id=input_item_id,
                original_text=fallback_original.strip(),
                translated_text=fallback_translation.strip(),
            )
            published_input_items.add(input_item_id)
            if self._on_block_ready is not None:
                self._on_block_ready(block)
        if self._on_partial_text_changed is not None:
            self._clear_partials()

    def _log_partial_if_needed(self, *, kind: str, text: str) -> None:
        clean = text.strip()
        if not clean:
            return
        if kind == "original":
            previous = self._last_logged_original_partial
        else:
            previous = self._last_logged_translation_partial
        if clean == previous:
            return
        # Log only meaningful growth to keep files readable during long sessions.
        if previous and clean.startswith(previous) and (len(clean) - len(previous)) < 12:
            return
        self.session_logger.record_event(
            "partial_update",
            kind=kind,
            text=clean,
        )
        if kind == "original":
            self._last_logged_original_partial = clean
        else:
            self._last_logged_translation_partial = clean

    def _build_realtime_instructions(self) -> str:
        return (
            "You are a real-time subtitle translator for system audio. "
            "Output concise Spanish subtitles only. If the speaker is already speaking Spanish, "
            "transcribe it naturally in Spanish instead of suppressing it. If the speaker is "
            "speaking another language, translate it to Spanish. Do not explain, do not prefix "
            "labels, and do not include the original language."
        )

    def _build_transcription_config(self) -> dict[str, str]:
        config = {
            "model": "gpt-realtime-whisper",
            "delay": "minimal",
        }
        if self.source_language and self.source_language.lower() != "auto":
            config["language"] = self.source_language
        return config

    def _build_session_update_payload(self) -> dict[str, object]:
        return {
            "type": "session.update",
            "session": {
                "type": "realtime",
                "instructions": self._build_realtime_instructions(),
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcm", "rate": 24000},
                        "turn_detection": self._build_turn_detection_config(),
                        "transcription": self._build_transcription_config(),
                    }
                },
                "output_modalities": ["text"],
                "max_output_tokens": self.max_output_tokens,
            },
        }

    def _build_turn_detection_config(self) -> dict[str, object]:
        if self.turn_detection_type == "semantic_vad":
            return {
                "type": "semantic_vad",
                "eagerness": self.semantic_vad_eagerness,
                "create_response": not self.translate_completed_transcripts,
                "interrupt_response": self.interrupt_response,
            }
        return {
            "type": "server_vad",
            "create_response": not self.translate_completed_transcripts,
            "interrupt_response": self.interrupt_response,
            "prefix_padding_ms": self.prefix_padding_ms,
            "silence_duration_ms": self.silence_duration_ms,
            "threshold": self.vad_threshold,
        }


def _extract_realtime_error_message(event: object) -> str:
    error = getattr(event, "error", None)
    if error is None:
        return "La sesion OpenAI realtime devolvio un error."
    message = getattr(error, "message", None)
    if isinstance(message, str) and message.strip():
        return message
    return str(error)


def _ensure_turn(
    turns: OrderedDict[str, _RealtimeTurn],
    input_item_id: str,
) -> _RealtimeTurn:
    if not input_item_id:
        input_item_id = "__synthetic_current_turn__"
    turn = turns.get(input_item_id)
    if turn is None:
        turn = _RealtimeTurn(input_item_id=input_item_id)
        turns[input_item_id] = turn
    return turn


def _assign_response_to_next_turn(
    turns: OrderedDict[str, _RealtimeTurn],
    unassigned_input_items: deque[str],
    response_to_input_item: dict[str, str],
    response_id: str,
) -> str:
    if not response_id:
        return ""
    if response_id in response_to_input_item:
        return response_to_input_item[response_id]
    if unassigned_input_items:
        input_item_id = unassigned_input_items.popleft()
    elif turns:
        input_item_id = next(reversed(turns))
    else:
        input_item_id = "__synthetic_current_turn__"
    _ensure_turn(turns, input_item_id)
    response_to_input_item[response_id] = input_item_id
    return input_item_id


def _turn_for_response_event(
    turns: OrderedDict[str, _RealtimeTurn],
    unassigned_input_items: deque[str],
    response_to_input_item: dict[str, str],
    event: object,
) -> _RealtimeTurn:
    response_id = getattr(event, "response_id", "") or ""
    input_item_id = _assign_response_to_next_turn(
        turns,
        unassigned_input_items,
        response_to_input_item,
        response_id,
    )
    return _ensure_turn(turns, input_item_id)


def _extract_response_id(event: object) -> str:
    response_id = getattr(event, "response_id", "") or ""
    if response_id:
        return response_id
    response = getattr(event, "response", None)
    if response is None:
        return ""
    return getattr(response, "id", "") or ""


def _pick_most_complete_text(first: str, second: str) -> str:
    first = first.strip()
    second = second.strip()
    if len(second) > len(first):
        return second
    return first


def _join_transcript_segments(current: str, latest: str) -> str:
    current = _clean_transcript_text(current)
    latest = _clean_transcript_text(latest)
    if not current:
        return latest
    if not latest:
        return current
    if latest in current:
        return current
    if current.endswith(("-", "—")):
        return f"{current}{latest}"
    if current.endswith((".", "?", "!")) and latest.startswith((".", "?", "!")):
        latest = latest.lstrip(".?!").lstrip()
    return f"{current} {latest}"


def _clean_transcript_text(text: str) -> str:
    clean = " ".join(text.strip().split())
    while ".." in clean:
        clean = clean.replace("..", ".")
    return clean


def _should_flush_transcript(
    transcript: str,
    *,
    latest_segment: str,
    previous_pending: bool,
) -> bool:
    clean = transcript.strip()
    latest_words = latest_segment.split()
    total_words = clean.split()
    if not clean:
        return False
    if clean.endswith((".", "?", "!", "¿", "¡")):
        return True
    if previous_pending and len(latest_words) <= 6 and len(total_words) >= 10:
        return True
    return len(total_words) >= 28
