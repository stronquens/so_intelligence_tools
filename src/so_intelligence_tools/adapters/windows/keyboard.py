from __future__ import annotations

import ctypes
from ctypes import wintypes
import sys
import time

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError


INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_CONTROL = 0x11
VK_A = 0x41
VK_C = 0x43
VK_V = 0x56
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
_WIN32_KEYBOARD_CONFIGURED = False


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUTUNION)]


class WindowsKeyboardAutomationAdapter:
    def __init__(self, *, copy_delay_seconds: float = 0.15, paste_delay_seconds: float = 0.1) -> None:
        self._copy_delay_seconds = copy_delay_seconds
        self._paste_delay_seconds = paste_delay_seconds

    def trigger_copy_selection(self) -> None:
        self._ensure_windows()
        self._send_shortcut(VK_C)
        time.sleep(self._copy_delay_seconds)

    def trigger_select_all(self) -> None:
        self._ensure_windows()
        self._send_shortcut(VK_A)
        time.sleep(self._copy_delay_seconds)

    def trigger_paste(self) -> None:
        self._ensure_windows()
        self._send_shortcut(VK_V)
        time.sleep(self._paste_delay_seconds)

    def type_text(self, text: str) -> None:
        self._ensure_windows()
        if not text:
            return
        inputs: list[INPUT] = []
        for char in text:
            codepoint = ord(char)
            if codepoint > 0xFFFF:
                raise UnsupportedEnvironmentError(
                    "La escritura directa de caracteres suplementarios aun no esta soportada en Windows."
                )
            inputs.append(_unicode_input(codepoint, key_up=False))
            inputs.append(_unicode_input(codepoint, key_up=True))
        _send_inputs(inputs)
        time.sleep(self._paste_delay_seconds)

    @staticmethod
    def _send_shortcut(key_code: int) -> None:
        _send_inputs(
            [
                _virtual_key_input(VK_CONTROL, key_up=False),
                _virtual_key_input(key_code, key_up=False),
                _virtual_key_input(key_code, key_up=True),
                _virtual_key_input(VK_CONTROL, key_up=True),
            ]
        )

    @staticmethod
    def _ensure_windows() -> None:
        if sys.platform != "win32":
            raise UnsupportedEnvironmentError("Este adapter de teclado solo funciona en Windows.")
        _configure_win32_keyboard_api()


def _virtual_key_input(key_code: int, *, key_up: bool) -> INPUT:
    flags = KEYEVENTF_KEYUP if key_up else 0
    return INPUT(
        type=INPUT_KEYBOARD,
        union=INPUTUNION(ki=KEYBDINPUT(key_code, 0, flags, 0, 0)),
    )


def _unicode_input(codepoint: int, *, key_up: bool) -> INPUT:
    flags = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if key_up else 0)
    return INPUT(
        type=INPUT_KEYBOARD,
        union=INPUTUNION(ki=KEYBDINPUT(0, codepoint, flags, 0, 0)),
    )


def _send_inputs(inputs: list[INPUT]) -> None:
    _configure_win32_keyboard_api()
    array_type = INPUT * len(inputs)
    sent = ctypes.windll.user32.SendInput(len(inputs), array_type(*inputs), ctypes.sizeof(INPUT))
    if sent != len(inputs):
        error_code = ctypes.windll.kernel32.GetLastError()
        raise UnsupportedEnvironmentError(
            "Windows no acepto la simulacion de teclado solicitada. "
            f"Codigo de error Win32: {error_code}."
        )


def _configure_win32_keyboard_api() -> None:
    global _WIN32_KEYBOARD_CONFIGURED
    if _WIN32_KEYBOARD_CONFIGURED or sys.platform != "win32":
        return
    ctypes.windll.user32.SendInput.argtypes = [
        wintypes.UINT,
        ctypes.POINTER(INPUT),
        ctypes.c_int,
    ]
    ctypes.windll.user32.SendInput.restype = wintypes.UINT
    ctypes.windll.kernel32.GetLastError.argtypes = []
    ctypes.windll.kernel32.GetLastError.restype = wintypes.DWORD
    _WIN32_KEYBOARD_CONFIGURED = True
