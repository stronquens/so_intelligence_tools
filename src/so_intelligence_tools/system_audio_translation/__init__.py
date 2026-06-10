from __future__ import annotations

from typing import Any


def run_system_audio_translation_toggle(*args: Any, **kwargs: Any) -> str:
    from so_intelligence_tools.system_audio_translation.app import (
        run_system_audio_translation_toggle as _run,
    )

    return _run(*args, **kwargs)

__all__ = ["run_system_audio_translation_toggle"]
