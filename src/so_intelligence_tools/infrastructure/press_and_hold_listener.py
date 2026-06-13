from __future__ import annotations

import logging
import os
from collections.abc import Callable
from threading import Lock, Timer

from pynput import keyboard

from so_intelligence_tools.domain.errors import ToolRunnerError, UnsupportedEnvironmentError


logger = logging.getLogger(__name__)


class PressAndHoldShortcutListener:
    def __init__(
        self,
        *,
        shortcut: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        self._required_keys = _parse_shortcut(shortcut)
        self._on_press = on_press
        self._on_release = on_release
        self._pressed_keys: set[str] = set()
        self._active = False
        self._listener: keyboard.Listener | None = None
        self._release_timer: Timer | None = None
        self._lock = Lock()

    def start(self) -> None:
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type == "wayland":
            raise UnsupportedEnvironmentError(
                "El listener press-and-hold de dictado requiere X11 en esta primera versión."
            )
        self._listener = keyboard.Listener(
            on_press=self._handle_key_press,
            on_release=self._handle_key_release,
        )
        self._listener.start()

    def join(self) -> None:
        if self._listener is None:
            raise RuntimeError("Press-and-hold listener has not been started.")
        self._listener.join()

    def run_forever(self) -> None:
        self.start()
        self.join()

    def _handle_key_press(self, key) -> None:
        with self._lock:
            self._pressed_keys.add(_normalize_key(key))
            release_timer = self._release_timer
            self._release_timer = None
            if release_timer is not None:
                release_timer.cancel()
            if self._active or not self._required_keys.issubset(self._pressed_keys):
                return
            self._active = True
        try:
            self._on_press()
            logger.info("Press-and-hold shortcut started")
        except ToolRunnerError as exc:
            with self._lock:
                self._active = False
            logger.warning("Press-and-hold shortcut failed to start: %s", exc)

    def _handle_key_release(self, key) -> None:
        normalized = _normalize_key(key)
        with self._lock:
            self._pressed_keys.discard(normalized)
            if not self._active or normalized not in self._required_keys:
                return
            release_timer = self._release_timer
            if release_timer is not None:
                release_timer.cancel()
            self._release_timer = Timer(0.12, self._finish_release_if_still_released)
            self._release_timer.daemon = True
            self._release_timer.start()

    def _finish_release_if_still_released(self) -> None:
        with self._lock:
            self._release_timer = None
            if not self._active or self._required_keys.issubset(self._pressed_keys):
                return
            self._active = False
        try:
            self._on_release()
            logger.info("Press-and-hold shortcut released")
        except ToolRunnerError as exc:
            logger.warning("Press-and-hold shortcut failed to stop cleanly: %s", exc)


def _parse_shortcut(shortcut: str) -> set[str]:
    cleaned = (
        shortcut.lower()
        .replace("><", ">+<")
        .replace(">space", ">+space")
        .replace("<primary>", "ctrl")
        .replace("<control>", "ctrl")
        .replace("<ctrl>", "ctrl")
        .replace("<alt>", "alt")
        .replace("<space>", "space")
        .replace(" ", "")
    )
    parts = {part for part in cleaned.split("+") if part}
    if not parts:
        raise UnsupportedEnvironmentError("El atajo de dictado push-to-talk está vacío.")
    return parts


def _normalize_key(key) -> str:
    if key in {keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
        return "ctrl"
    if key in {keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr}:
        return "alt"
    if key == keyboard.Key.space:
        return "space"
    char = getattr(key, "char", None)
    if char:
        return str(char).lower()
    name = getattr(key, "name", None)
    return str(name or key).lower().replace("key.", "")
