from __future__ import annotations

import os
import subprocess
import time
import uuid

from so_intelligence_tools.adapters.linux.clipboard import LinuxClipboardAdapter
from so_intelligence_tools.adapters.linux.keyboard import LinuxKeyboardAutomationAdapter
from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class LinuxCommandTextSelectionAdapter:
    def __init__(
        self,
        settings: ToolRunnerSettings,
        *,
        clipboard: LinuxClipboardAdapter | None = None,
        keyboard: LinuxKeyboardAutomationAdapter | None = None,
    ) -> None:
        self._settings = settings
        self._clipboard = clipboard or LinuxClipboardAdapter()
        self._keyboard = keyboard or LinuxKeyboardAutomationAdapter()

    def get_selected_text(self) -> str | None:
        command = self._settings.linux_read_selection_command
        if command:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise ToolRunnerConfigurationError(
                    "El comando de lectura de selección devolvió error en Linux."
                )
            selected_text = result.stdout.strip()
            return selected_text or None

        previous_clipboard = self._clipboard.get_text()
        if self._is_wayland_session() and hasattr(self._clipboard, "get_primary_text"):
            selected_text = (self._clipboard.get_primary_text() or "").strip()
            if selected_text:
                return selected_text

        sentinel = f"__so_intelligence_tools_selection_probe__:{uuid.uuid4()}"
        try:
            self._clipboard.set_text(sentinel)
            self._keyboard.trigger_copy_selection()
            selected_text = ""
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                selected_text = (self._clipboard.get_text() or "").strip()
                if selected_text and selected_text != sentinel:
                    break
                time.sleep(0.05)
        finally:
            if previous_clipboard is not None:
                self._clipboard.set_text(previous_clipboard)

        if not selected_text or selected_text == sentinel:
            return None

        return selected_text or None

    @staticmethod
    def _is_wayland_session() -> bool:
        return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
