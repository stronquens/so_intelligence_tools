from __future__ import annotations

import time
import uuid

from so_intelligence_tools.adapters.windows.clipboard import WindowsClipboardAdapter
from so_intelligence_tools.adapters.windows.keyboard import WindowsKeyboardAutomationAdapter


class WindowsCommandTextSelectionAdapter:
    def __init__(
        self,
        *,
        clipboard: WindowsClipboardAdapter | None = None,
        keyboard: WindowsKeyboardAutomationAdapter | None = None,
    ) -> None:
        self._clipboard = clipboard or WindowsClipboardAdapter()
        self._keyboard = keyboard or WindowsKeyboardAutomationAdapter()

    def get_selected_text(self) -> str | None:
        selected_text = self._copy_selected_text(
            select_all_first=False,
            timeout_seconds=0.4,
            copy_attempts=1,
        )
        if selected_text:
            return selected_text
        return self._copy_selected_text(
            select_all_first=True,
            timeout_seconds=0.8,
            copy_attempts=3,
        )

    def _copy_selected_text(
        self,
        *,
        select_all_first: bool,
        timeout_seconds: float,
        copy_attempts: int,
    ) -> str | None:
        previous_clipboard = self._clipboard.get_text()
        sentinel = f"__so_intelligence_tools_selection_probe__:{uuid.uuid4()}"
        selected_text = ""
        try:
            self._clipboard.set_text(sentinel)
            if select_all_first:
                self._keyboard.trigger_select_all()
            for _ in range(copy_attempts):
                self._keyboard.trigger_copy_selection()
                selected_text = self._wait_for_clipboard_text(
                    sentinel=sentinel,
                    timeout_seconds=timeout_seconds,
                )
                if selected_text:
                    break
                time.sleep(0.1)
        finally:
            if previous_clipboard is not None:
                self._clipboard.set_text(previous_clipboard)
            elif hasattr(self._clipboard, "clear_text"):
                self._clipboard.clear_text()

        return selected_text

    def _wait_for_clipboard_text(self, *, sentinel: str, timeout_seconds: float) -> str | None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            selected_text = (self._clipboard.get_text() or "").strip()
            if selected_text and selected_text != sentinel:
                return selected_text
            time.sleep(0.05)
        return None
