from __future__ import annotations

import logging
import os

from pynput import keyboard

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError
from so_intelligence_tools.domain.errors import ToolRunnerError
from so_intelligence_tools.infrastructure.shortcut_actions import ShortcutActionRegistry


logger = logging.getLogger(__name__)


class LinuxShortcutListener:
    def __init__(
        self,
        *,
        shortcut_to_action: dict[str, str],
        registry: ShortcutActionRegistry,
    ) -> None:
        self._shortcut_to_action = shortcut_to_action
        self._registry = registry
        self._listener: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type == "wayland":
            raise UnsupportedEnvironmentError(
                "La primera implementación de atajos globales está orientada a Linux X11; Wayland requiere un adapter específico."
            )
        callbacks = {
            shortcut: self._build_handler(action_name)
            for shortcut, action_name in self._shortcut_to_action.items()
        }
        self._listener = keyboard.GlobalHotKeys(callbacks)
        self._listener.start()

    def join(self) -> None:
        if self._listener is None:
            raise RuntimeError("Shortcut listener has not been started.")
        self._listener.join()

    def run_forever(self) -> None:
        self.start()
        self.join()

    def _build_handler(self, action_name: str):
        def handler() -> None:
            try:
                self._registry.execute(action_name)
                logger.info("Shortcut action executed: %s", action_name)
            except ToolRunnerError as exc:
                logger.warning("Shortcut action failed: %s", exc)

        return handler
