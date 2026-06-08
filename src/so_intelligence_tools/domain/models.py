from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


ReasoningMode = Literal["off", "low", "medium", "high"]
NotificationLevel = Literal["info", "warning", "error", "success"]
LiveSessionState = Literal[
    "inactive",
    "starting",
    "active",
    "paused",
    "reconnecting",
    "error",
    "stopping",
]
SystemAudioSessionMode = Literal[
    "translate_es_chunked",
    "translate_es_openai_realtime",
]
LivePartialKind = Literal["original", "translation"]


@dataclass(slots=True)
class TextGenerationResult:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_mode_requested: ReasoningMode = "off"
    reasoning_strategy_applied: str = "thinking:off"


@dataclass(slots=True)
class NotificationMessage:
    title: str
    body: str
    level: NotificationLevel = "info"


@dataclass(slots=True)
class TranscriptBlock:
    timestamp: datetime
    translated_text: str
    original_text: str | None = None
    speaker_label: str | None = None

    def to_log_line(self) -> str:
        stamp = self.timestamp.isoformat(timespec="seconds")
        speaker = f"[{self.speaker_label}] " if self.speaker_label else ""
        original = f" | original={self.original_text}" if self.original_text else ""
        return f"{stamp} {speaker}{self.translated_text}{original}"


@dataclass(slots=True)
class LivePartialUpdate:
    kind: LivePartialKind
    text: str
