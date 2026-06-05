from __future__ import annotations

from typing import Protocol


class TextSelectionPort(Protocol):
    def get_selected_text(self) -> str | None: ...
