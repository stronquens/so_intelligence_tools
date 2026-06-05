from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ReasoningMode = Literal["off", "low", "medium", "high"]
NotificationLevel = Literal["info", "warning", "error", "success"]


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
