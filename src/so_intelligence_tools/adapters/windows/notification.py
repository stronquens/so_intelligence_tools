from __future__ import annotations

import ctypes
import sys


class WindowsNotificationAdapter:
    def notify(self, *, title: str, body: str, level: str = "info") -> None:
        if sys.platform != "win32":
            return
        icon = {
            "error": 0x00000010,
            "warning": 0x00000030,
            "success": 0x00000040,
            "info": 0x00000040,
        }.get(level, 0x00000040)
        try:
            ctypes.windll.user32.MessageBeep(icon)
        except Exception:
            return
