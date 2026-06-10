from __future__ import annotations

from typing import Any


def run_voice_translation_virtual_microphone_toggle(*args: Any, **kwargs: Any) -> str:
    from so_intelligence_tools.voice_translation_virtual_microphone.app import (
        run_voice_translation_virtual_microphone_toggle as _run,
    )

    return _run(*args, **kwargs)

__all__ = ["run_voice_translation_virtual_microphone_toggle"]
