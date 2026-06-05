from __future__ import annotations

from typing import Protocol


class ClipboardPort(Protocol):
    def set_text(self, text: str) -> None: ...
