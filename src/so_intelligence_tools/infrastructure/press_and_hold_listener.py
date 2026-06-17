from __future__ import annotations

import logging
import os
from collections.abc import Callable
from pathlib import Path
from threading import Lock, Timer
import time

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
        event_log_path: Path | None = None,
    ) -> None:
        self._required_keys = _parse_shortcut(shortcut)
        self._on_press = on_press
        self._on_release = on_release
        self._event_log_path = event_log_path
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
        self._log_event(
            "started "
            f"required={','.join(sorted(self._required_keys))} "
            f"pid={os.getpid()}"
        )

    def join(self) -> None:
        if self._listener is None:
            raise RuntimeError("Press-and-hold listener has not been started.")
        self._listener.join()

    def run_forever(self) -> None:
        self.start()
        self.join()

    def _handle_key_press(self, key) -> None:
        normalized = _normalize_key(key)
        with self._lock:
            self._pressed_keys.add(normalized)
            self._log_event(
                "press "
                f"key={normalized} "
                f"pressed={','.join(sorted(self._pressed_keys))}"
            )
            release_timer = self._release_timer
            self._release_timer = None
            if release_timer is not None:
                release_timer.cancel()
            if self._active or not self._required_keys.issubset(self._pressed_keys):
                return
            self._active = True
        try:
            self._log_event("shortcut-starting")
            self._on_press()
            logger.info("Press-and-hold shortcut started")
            self._log_event("shortcut-started")
        except ToolRunnerError as exc:
            with self._lock:
                self._active = False
            logger.warning("Press-and-hold shortcut failed to start: %s", exc)
            self._log_event(f"shortcut-start-failed error={exc}")
        except Exception as exc:
            with self._lock:
                self._active = False
            logger.exception("Press-and-hold shortcut crashed on start: %s", exc)
            self._log_event(f"shortcut-start-crashed error={exc!r}")

    def _handle_key_release(self, key) -> None:
        normalized = _normalize_key(key)
        with self._lock:
            self._pressed_keys.discard(normalized)
            self._log_event(
                "release "
                f"key={normalized} "
                f"pressed={','.join(sorted(self._pressed_keys))}"
            )
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
            self._log_event("shortcut-releasing")
            self._on_release()
            logger.info("Press-and-hold shortcut released")
            self._log_event("shortcut-released")
        except ToolRunnerError as exc:
            logger.warning("Press-and-hold shortcut failed to stop cleanly: %s", exc)
            self._log_event(f"shortcut-release-failed error={exc}")
        except Exception as exc:
            logger.exception("Press-and-hold shortcut crashed on release: %s", exc)
            self._log_event(f"shortcut-release-crashed error={exc!r}")

    def _log_event(self, message: str) -> None:
        if self._event_log_path is None:
            return
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._event_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._event_log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")


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
        if len(char) == 1 and 1 <= ord(char) <= 26:
            return chr(ord(char) + 96)
        return str(char).lower()
    virtual_key = getattr(key, "vk", None)
    if isinstance(virtual_key, int):
        if ord("A") <= virtual_key <= ord("Z"):
            return chr(virtual_key).lower()
        if ord("0") <= virtual_key <= ord("9"):
            return chr(virtual_key)
    name = getattr(key, "name", None)
    return str(name or key).lower().replace("key.", "")
