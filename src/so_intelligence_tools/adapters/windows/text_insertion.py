from __future__ import annotations

from so_intelligence_tools.adapters.windows.clipboard import WindowsClipboardAdapter
from so_intelligence_tools.adapters.windows.keyboard import WindowsKeyboardAutomationAdapter


class WindowsCommandTextInsertionAdapter:
    def __init__(
        self,
        *,
        clipboard: WindowsClipboardAdapter | None = None,
        keyboard: WindowsKeyboardAutomationAdapter | None = None,
    ) -> None:
        self._clipboard = clipboard or WindowsClipboardAdapter()
        self._keyboard = keyboard or WindowsKeyboardAutomationAdapter()

    def replace_selected_text(self, text: str) -> None:
        self._clipboard.set_text(text)
        self._keyboard.trigger_paste()
