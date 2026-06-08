from __future__ import annotations

from typing import Protocol


class ClipboardPort(Protocol):
    def get_text(self) -> str | None: ...

    def set_text(self, text: str) -> None: ...
