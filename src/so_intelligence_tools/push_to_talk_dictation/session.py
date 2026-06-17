from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock
import time

from so_intelligence_tools.domain.models import NotificationLevel
from so_intelligence_tools.ports.notification import NotificationPort
from so_intelligence_tools.ports.streaming_asr import StreamingAsrEvent, StreamingAsrTranscriber
from so_intelligence_tools.ports.text_insertion import TextInsertionPort


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DictationSessionResult:
    inserted_text: str = ""
    final_segments: list[str] = field(default_factory=list)


class StreamingDictationController:
    def __init__(
        self,
        *,
        transcriber: StreamingAsrTranscriber,
        text_insertion: TextInsertionPort,
        notifications: NotificationPort | None = None,
        insertion_strategy: str = "final_segments",
    ) -> None:
        self._transcriber = transcriber
        self._text_insertion = text_insertion
        self._notifications = notifications
        self._insertion_strategy = insertion_strategy
        self._lock = Lock()
        self._session = None
        self._result = DictationSessionResult()
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    @property
    def result(self) -> DictationSessionResult:
        return self._result

    def warm_up(self) -> None:
        self._transcriber.check_ready()

    def start(self) -> None:
        with self._lock:
            if self._active:
                return
            self._transcriber.check_ready()
            self._session = self._transcriber.start_session()
            self._result = DictationSessionResult()
            self._active = True
            self._notify(
                title="Dictado activo",
                body="Escuchando mientras mantienes el atajo.",
                level="info",
            )

    def accept_audio(self, pcm_s16le: bytes) -> None:
        with self._lock:
            if not self._active or self._session is None:
                return
            events = list(self._session.accept_audio(pcm_s16le))
        self._handle_events(events)

    def stop(self) -> DictationSessionResult:
        with self._lock:
            if not self._active or self._session is None:
                return self._result
            session = self._session
            self._active = False
            self._session = None

        try:
            self._handle_events(list(session.finish()))
        finally:
            session.close()
        self._insert_buffered_result()
        self._notify(
            title="Dictado finalizado",
            body=self._result.inserted_text.strip() or "No se reconoció texto.",
            level="success" if self._result.inserted_text.strip() else "warning",
        )
        return self._result

    def abort(self) -> None:
        with self._lock:
            session = self._session
            self._session = None
            self._active = False
        if session is not None:
            session.close()

    def _handle_events(self, events: list[StreamingAsrEvent]) -> None:
        for event in events:
            if event.kind == "final":
                self._insert_final_segment(event.text)
            elif event.kind == "error":
                self._notify(
                    title="Error de dictado",
                    body=event.message or event.text or "El runtime ASR devolvió un error.",
                    level="error",
                )
            elif event.kind == "state":
                logger.info("Dictation ASR state: %s", event.message or event.text)
            elif event.kind == "partial":
                logger.debug("Dictation partial: %s", event.text)

    def _insert_final_segment(self, text: str) -> None:
        segment = self._stable_delta(text)
        if not segment:
            return
        self._result.final_segments.append(segment)
        self._result.inserted_text += segment
        if self._insertion_strategy == "final_segments":
            self._text_insertion.replace_selected_text(segment)

    def _insert_buffered_result(self) -> None:
        if self._insertion_strategy != "final_on_release":
            return
        text = self._result.inserted_text
        if text:
            self._text_insertion.replace_selected_text(text)

    def _stable_delta(self, text: str) -> str:
        if not text:
            return ""
        inserted = self._result.inserted_text
        if inserted and text.startswith(inserted):
            return text[len(inserted) :]
        if text == inserted:
            return ""
        return text

    def _notify(self, *, title: str, body: str, level: NotificationLevel) -> None:
        if self._notifications is not None:
            self._notifications.notify(title=title, body=body, level=level)


class PressAndHoldDictationRunner:
    def __init__(
        self,
        *,
        controller: StreamingDictationController,
        audio_capture_factory: Callable[[Callable[[bytes], None]], object],
        post_roll_seconds: float = 0.0,
    ) -> None:
        self._controller = controller
        self._audio_capture_factory = audio_capture_factory
        self._post_roll_seconds = post_roll_seconds
        self._capture = None

    def press(self) -> None:
        if self._controller.active:
            return
        pending_audio: list[bytes] = []
        pending_audio_lock = Lock()

        def accept_or_buffer(pcm_s16le: bytes) -> None:
            if self._controller.active:
                self._controller.accept_audio(pcm_s16le)
                return
            with pending_audio_lock:
                pending_audio.append(pcm_s16le)

        capture = self._audio_capture_factory(accept_or_buffer)
        start = getattr(capture, "start")
        try:
            start()
            self._controller.start()
        except Exception:
            stop = getattr(capture, "stop")
            stop()
            self._controller.abort()
            raise
        self._capture = capture
        with pending_audio_lock:
            buffered_audio = list(pending_audio)
            pending_audio.clear()
        for chunk in buffered_audio:
            self._controller.accept_audio(chunk)

    def release(self) -> DictationSessionResult:
        capture = self._capture
        self._capture = None
        if capture is not None:
            if self._post_roll_seconds > 0:
                time.sleep(self._post_roll_seconds)
            stop = getattr(capture, "stop")
            stop()
        return self._controller.stop()

    def abort(self) -> None:
        capture = self._capture
        self._capture = None
        if capture is not None:
            stop = getattr(capture, "stop")
            stop()
        self._controller.abort()

    def warm_up(self) -> None:
        self._controller.warm_up()
