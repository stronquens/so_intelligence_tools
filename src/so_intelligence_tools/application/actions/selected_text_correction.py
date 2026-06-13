from __future__ import annotations

from pathlib import Path

from so_intelligence_tools.application.use_cases.correct_selected_text import (
    correct_selected_text,
)
from so_intelligence_tools.infrastructure.runtime import ToolRuntime


def run_selected_text_correction(runtime: ToolRuntime, *, debug_log_path: Path | None = None) -> str:
    return correct_selected_text(
        inference=runtime.inference_client,
        text_selection=runtime.text_selection,
        text_insertion=runtime.text_insertion,
        notifications=runtime.notifications,
        debug_log_path=debug_log_path,
        fallback_clipboard=runtime.clipboard,
    )
