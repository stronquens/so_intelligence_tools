from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, Protocol


StreamingAsrEventKind = Literal["partial", "final", "state", "error"]


@dataclass(slots=True)
class StreamingAsrEvent:
    kind: StreamingAsrEventKind
    text: str = ""
    message: str | None = None


class StreamingAsrSession(Protocol):
    def accept_audio(self, pcm_s16le: bytes) -> Iterable[StreamingAsrEvent]: ...

    def finish(self) -> Iterable[StreamingAsrEvent]: ...

    def close(self) -> None: ...


class StreamingAsrTranscriber(Protocol):
    def check_ready(self) -> None: ...

    def start_session(self) -> StreamingAsrSession: ...
