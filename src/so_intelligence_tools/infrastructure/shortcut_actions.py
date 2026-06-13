from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from so_intelligence_tools.application.actions.selected_text_correction import (
    run_selected_text_correction,
)
from so_intelligence_tools.infrastructure.runtime import ToolRuntime


ShortcutAction = Callable[[], str | None]


class ShortcutActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, ShortcutAction] = {}

    def register(self, action_name: str, action: ShortcutAction) -> None:
        self._actions[action_name] = action

    def execute(self, action_name: str) -> str | None:
        action = self._actions[action_name]
        return action()

    def has_action(self, action_name: str) -> bool:
        return action_name in self._actions


def build_default_shortcut_registry(
    runtime: ToolRuntime,
    *,
    debug_log_path: Path | None = None,
) -> ShortcutActionRegistry:
    registry = ShortcutActionRegistry()
    registry.register(
        "selected-text-correction",
        lambda: run_selected_text_correction(runtime, debug_log_path=debug_log_path),
    )
    return registry
