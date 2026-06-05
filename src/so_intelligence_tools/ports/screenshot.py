from __future__ import annotations

from typing import Protocol


class ScreenshotPort(Protocol):
    def capture_region(self) -> bytes: ...
