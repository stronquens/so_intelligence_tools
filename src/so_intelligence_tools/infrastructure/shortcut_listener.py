from __future__ import annotations

import logging
import os
from pathlib import Path
import sys
import time
import ctypes
from ctypes import wintypes

from pynput import keyboard

from so_intelligence_tools.domain.errors import ToolRunnerError, UnsupportedEnvironmentError
from so_intelligence_tools.infrastructure.shortcut_actions import ShortcutActionRegistry


logger = logging.getLogger(__name__)

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


class BaseShortcutListener:
    def __init__(
        self,
        *,
        shortcut_to_action: dict[str, str],
        registry: ShortcutActionRegistry,
        action_delay_seconds: float = 0.0,
        action_cooldown_seconds: float = 0.0,
        event_log_path: Path | None = None,
    ) -> None:
        self._shortcut_to_action = shortcut_to_action
        self._registry = registry
        self._action_delay_seconds = action_delay_seconds
        self._action_cooldown_seconds = action_cooldown_seconds
        self._event_log_path = event_log_path
        self._listener: keyboard.GlobalHotKeys | None = None
        self._running_actions: set[str] = set()
        self._last_finished_at: dict[str, float] = {}

    def start(self) -> None:
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
            now = time.monotonic()
            if action_name in self._running_actions:
                self._log_event(f"ignored action={action_name} reason=already-running")
                return
            last_finished_at = self._last_finished_at.get(action_name)
            if (
                last_finished_at is not None
                and now - last_finished_at < self._action_cooldown_seconds
            ):
                self._log_event(f"ignored action={action_name} reason=cooldown")
                return

            self._running_actions.add(action_name)
            try:
                self._log_event(f"triggered action={action_name}")
                if self._action_delay_seconds > 0:
                    time.sleep(self._action_delay_seconds)
                self._registry.execute(action_name)
                logger.info("Shortcut action executed: %s", action_name)
                self._log_event(f"completed action={action_name}")
            except ToolRunnerError as exc:
                logger.warning("Shortcut action failed: %s", exc)
                self._log_event(f"failed action={action_name} error={exc}")
            except Exception as exc:
                logger.exception("Shortcut action crashed: %s", exc)
                self._log_event(f"crashed action={action_name} error={exc!r}")
            finally:
                self._running_actions.discard(action_name)
                self._last_finished_at[action_name] = time.monotonic()

        return handler

    def _log_event(self, message: str) -> None:
        if self._event_log_path is None:
            return
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._event_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self._event_log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")


class LinuxShortcutListener(BaseShortcutListener):
    def start(self) -> None:
        session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        if session_type == "wayland":
            raise UnsupportedEnvironmentError(
                "La primera implementacion de atajos globales esta orientada a Linux X11; "
                "Wayland requiere un adapter especifico."
            )
        super().start()


class WindowsShortcutListener(BaseShortcutListener):
    def __init__(
        self,
        *,
        shortcut_to_action: dict[str, str],
        registry: ShortcutActionRegistry,
        action_delay_seconds: float = 0.0,
        action_cooldown_seconds: float = 0.0,
        event_log_path: Path | None = None,
    ) -> None:
        super().__init__(
            shortcut_to_action=shortcut_to_action,
            registry=registry,
            action_delay_seconds=action_delay_seconds,
            action_cooldown_seconds=action_cooldown_seconds,
            event_log_path=event_log_path,
        )
        self._hotkey_to_action: dict[int, str] = {}

    def start(self) -> None:
        if sys.platform != "win32":
            raise UnsupportedEnvironmentError(
                "El listener nativo de atajos Windows solo funciona en Windows."
            )
        for hotkey_id, (shortcut, action_name) in enumerate(
            self._shortcut_to_action.items(),
            start=1,
        ):
            modifiers, virtual_key = _parse_windows_hotkey(shortcut)
            if not ctypes.windll.user32.RegisterHotKey(None, hotkey_id, modifiers, virtual_key):
                error_code = ctypes.get_last_error()
                raise UnsupportedEnvironmentError(
                    "No se pudo registrar el atajo global de Windows "
                    f"{shortcut}. Codigo de error Win32: {error_code}."
                )
            self._hotkey_to_action[hotkey_id] = action_name
            self._log_event(f"registered shortcut={shortcut} action={action_name}")

    def join(self) -> None:
        if not self._hotkey_to_action:
            raise RuntimeError("Shortcut listener has not been started.")
        message = MSG()
        try:
            while True:
                result = ctypes.windll.user32.GetMessageW(ctypes.byref(message), None, 0, 0)
                if result == -1:
                    error_code = ctypes.get_last_error()
                    raise UnsupportedEnvironmentError(
                        f"El listener de atajos Windows fallo leyendo mensajes: {error_code}."
                    )
                if result == 0:
                    return
                if message.message == WM_HOTKEY:
                    action_name = self._hotkey_to_action.get(int(message.wParam))
                    if action_name is not None:
                        self._build_handler(action_name)()
        finally:
            self._unregister_hotkeys()

    def _unregister_hotkeys(self) -> None:
        for hotkey_id in list(self._hotkey_to_action):
            ctypes.windll.user32.UnregisterHotKey(None, hotkey_id)
        self._hotkey_to_action.clear()


def build_shortcut_listener(
    *,
    shortcut_to_action: dict[str, str],
    registry: ShortcutActionRegistry,
    action_delay_seconds: float = 0.0,
    action_cooldown_seconds: float = 0.0,
    event_log_path: Path | None = None,
    platform_name: str | None = None,
) -> BaseShortcutListener:
    detected_platform = platform_name or sys.platform
    if detected_platform.startswith("linux"):
        return LinuxShortcutListener(
            shortcut_to_action=shortcut_to_action,
            registry=registry,
            action_delay_seconds=action_delay_seconds,
            action_cooldown_seconds=action_cooldown_seconds,
            event_log_path=event_log_path,
        )
    if detected_platform == "win32":
        return WindowsShortcutListener(
            shortcut_to_action=shortcut_to_action,
            registry=registry,
            action_delay_seconds=action_delay_seconds,
            action_cooldown_seconds=action_cooldown_seconds,
            event_log_path=event_log_path,
        )
    raise UnsupportedEnvironmentError(
        f"No hay listener de atajos soportado para la plataforma: {detected_platform}"
    )


def _parse_windows_hotkey(shortcut: str) -> tuple[int, int]:
    parts = _split_shortcut(shortcut)
    modifiers = 0
    key: str | None = None
    for part in parts:
        if part in {"ctrl", "control", "primary"}:
            modifiers |= MOD_CONTROL
        elif part == "alt":
            modifiers |= MOD_ALT
        elif part == "shift":
            modifiers |= MOD_SHIFT
        elif part in {"cmd", "super", "win", "windows"}:
            modifiers |= MOD_WIN
        elif key is None:
            key = part
        else:
            raise UnsupportedEnvironmentError(f"Atajo Windows no soportado: {shortcut}")
    if key is None:
        raise UnsupportedEnvironmentError(f"Atajo Windows sin tecla principal: {shortcut}")
    return modifiers, _windows_virtual_key_for(key)


def _split_shortcut(shortcut: str) -> list[str]:
    cleaned = (
        shortcut.lower()
        .replace("><", ">+<")
        .replace(">space", ">+space")
        .replace("<", "")
        .replace(">", "")
        .replace(" ", "")
    )
    return [part for part in cleaned.split("+") if part]


def _windows_virtual_key_for(key: str) -> int:
    if len(key) == 1 and key.isalpha():
        return ord(key.upper())
    if len(key) == 1 and key.isdigit():
        return ord(key)
    if key == "space":
        return 0x20
    if key.startswith("f") and key[1:].isdigit():
        number = int(key[1:])
        if 1 <= number <= 24:
            return 0x70 + number - 1
    raise UnsupportedEnvironmentError(f"Tecla principal Windows no soportada: {key}")
