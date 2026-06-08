from __future__ import annotations

import os
import subprocess

from so_intelligence_tools.adapters.linux.clipboard import LinuxClipboardAdapter
from so_intelligence_tools.adapters.linux.keyboard import LinuxKeyboardAutomationAdapter
from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class LinuxCommandTextInsertionAdapter:
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

    def replace_selected_text(self, text: str) -> None:
        command = self._settings.linux_replace_selection_command
        if command:
            result = subprocess.run(
                command,
                shell=True,
                input=text,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise ToolRunnerConfigurationError(
                    "El comando de reemplazo de texto devolvió error en Linux."
                )
            return

        if self._is_wayland_session():
            self._clipboard.set_text(text)
            self._keyboard.trigger_paste()
            return

        self._clipboard.set_text(text)
        self._keyboard.trigger_paste()

    @staticmethod
    def _is_wayland_session() -> bool:
        return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
