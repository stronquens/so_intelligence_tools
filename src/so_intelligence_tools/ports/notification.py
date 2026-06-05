from __future__ import annotations

from typing import Protocol

from so_intelligence_tools.domain.models import NotificationLevel


class NotificationPort(Protocol):
    def notify(self, *, title: str, body: str, level: NotificationLevel = "info") -> None: ...
