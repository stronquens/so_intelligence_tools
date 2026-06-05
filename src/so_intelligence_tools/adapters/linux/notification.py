from __future__ import annotations

import shutil
import subprocess

from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class LinuxNotificationAdapter:
    def __init__(self, settings: ToolRunnerSettings) -> None:
        self._settings = settings

    def notify(self, *, title: str, body: str, level: str = "info") -> None:
        binary = self._settings.linux_notify_send_binary
        if not shutil.which(binary):
            return
        urgency = {
            "error": "critical",
            "warning": "normal",
            "success": "low",
            "info": "low",
        }.get(level, "low")
        subprocess.run([binary, "-u", urgency, title, body], check=False)
