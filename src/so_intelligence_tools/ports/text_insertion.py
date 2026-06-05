from __future__ import annotations

from typing import Protocol


class TextInsertionPort(Protocol):
    def replace_selected_text(self, text: str) -> None: ...
