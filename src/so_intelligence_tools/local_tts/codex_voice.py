from __future__ import annotations

import sys
import json
import queue
import threading
from collections.abc import Iterable
from typing import TextIO

from so_intelligence_tools.local_tts.client import LocalTtsClient
from so_intelligence_tools.local_tts.codex_events import (
    CodexVisibleEventExtractor,
    normalize_speech_detail,
)


def speak_text(client: LocalTtsClient, text: str) -> str:
    result = client.speak(text)
    return result.status


def run_codex_visible_event_listener(
    *,
    lines: Iterable[str] | TextIO | None = None,
    client: LocalTtsClient,
    include_progress: bool = False,
    speech_detail: str = "standard",
    max_segment_chars: int = 500,
) -> int:
    source = lines if lines is not None else sys.stdin
    speech_detail = normalize_speech_detail(speech_detail)
    extractor = CodexVisibleEventExtractor(
        include_progress=include_progress,
        speech_detail=speech_detail,
        max_segment_chars=max_segment_chars,
    )
    playback = SpeechPlaybackQueue(client)
    playback.start()
    for line in source:
        segments = extractor.feed_line(line)
        if _is_turn_completion_line(line) and include_progress:
            completion_segments = [
                segment for segment in segments if segment.startswith("Fin de tarea")
            ]
            if completion_segments:
                playback.clear()
                for segment in completion_segments:
                    playback.enqueue(segment)
                continue
        for segment in segments:
            playback.enqueue(segment)
    for segment in extractor.flush():
        playback.enqueue(segment)
    playback.stop()
    return 0


class SpeechPlaybackQueue:
    def __init__(self, client: LocalTtsClient) -> None:
        self._client = client
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def enqueue(self, text: str) -> None:
        self._queue.put(text)

    def clear(self) -> None:
        while True:
            try:
                item = self._queue.get_nowait()
            except queue.Empty:
                return
            if item is None:
                self._queue.put(None)
                return

    def stop(self) -> None:
        self._queue.put(None)
        self._thread.join()

    def _run(self) -> None:
        while True:
            text = self._queue.get()
            if text is None:
                return
            self._client.speak(text)


def _is_turn_completion_line(line: str) -> bool:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return False
    method = str(payload.get("method") or "")
    event_type = str(payload.get("type") or "")
    return method in {"turn/completed", "turn/failed"} or event_type in {
        "turn.completed",
        "turn.failed",
    }
