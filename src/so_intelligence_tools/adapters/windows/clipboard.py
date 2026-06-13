from __future__ import annotations

import ctypes
from ctypes import wintypes
import sys
import time

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError


CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002
_WIN32_CLIPBOARD_CONFIGURED = False


class WindowsClipboardAdapter:
    def get_text(self) -> str | None:
        self._ensure_windows()
        if not _open_clipboard_with_retry():
            raise UnsupportedEnvironmentError("No se pudo abrir el portapapeles de Windows.")
        try:
            handle = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return None
            pointer = ctypes.windll.kernel32.GlobalLock(handle)
            if not pointer:
                return None
            try:
                text = ctypes.wstring_at(pointer)
            finally:
                ctypes.windll.kernel32.GlobalUnlock(handle)
            return text or None
        finally:
            ctypes.windll.user32.CloseClipboard()

    def set_text(self, text: str) -> None:
        self._ensure_windows()
        if not _open_clipboard_with_retry():
            raise UnsupportedEnvironmentError("No se pudo abrir el portapapeles de Windows.")
        try:
            ctypes.windll.user32.EmptyClipboard()
            data = text + "\0"
            size = len(data) * ctypes.sizeof(wintypes.WCHAR)
            handle = ctypes.windll.kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
            if not handle:
                raise UnsupportedEnvironmentError("No se pudo reservar memoria para el portapapeles.")
            pointer = ctypes.windll.kernel32.GlobalLock(handle)
            if not pointer:
                ctypes.windll.kernel32.GlobalFree(handle)
                raise UnsupportedEnvironmentError("No se pudo escribir en el portapapeles.")
            try:
                ctypes.memmove(pointer, ctypes.create_unicode_buffer(data), size)
            finally:
                ctypes.windll.kernel32.GlobalUnlock(handle)
            if not ctypes.windll.user32.SetClipboardData(CF_UNICODETEXT, handle):
                ctypes.windll.kernel32.GlobalFree(handle)
                raise UnsupportedEnvironmentError("Windows rechazó el contenido del portapapeles.")
        finally:
            ctypes.windll.user32.CloseClipboard()

    def clear_text(self) -> None:
        self._ensure_windows()
        if not _open_clipboard_with_retry():
            raise UnsupportedEnvironmentError("No se pudo abrir el portapapeles de Windows.")
        try:
            ctypes.windll.user32.EmptyClipboard()
        finally:
            ctypes.windll.user32.CloseClipboard()

    @staticmethod
    def _ensure_windows() -> None:
        if sys.platform != "win32":
            raise UnsupportedEnvironmentError("Este adapter de portapapeles solo funciona en Windows.")
        _configure_win32_clipboard_api()


def _open_clipboard_with_retry(*, attempts: int = 10, delay_seconds: float = 0.03) -> bool:
    _configure_win32_clipboard_api()
    for _ in range(attempts):
        if ctypes.windll.user32.OpenClipboard(None):
            return True
        time.sleep(delay_seconds)
    return False


def _configure_win32_clipboard_api() -> None:
    global _WIN32_CLIPBOARD_CONFIGURED
    if _WIN32_CLIPBOARD_CONFIGURED or sys.platform != "win32":
        return

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    user32.CloseClipboard.argtypes = []
    user32.CloseClipboard.restype = wintypes.BOOL
    user32.EmptyClipboard.argtypes = []
    user32.EmptyClipboard.restype = wintypes.BOOL
    user32.GetClipboardData.argtypes = [wintypes.UINT]
    user32.GetClipboardData.restype = wintypes.HANDLE
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE

    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HANDLE
    kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
    kernel32.GlobalUnlock.restype = wintypes.BOOL
    kernel32.GlobalFree.argtypes = [wintypes.HANDLE]
    kernel32.GlobalFree.restype = wintypes.HANDLE

    _WIN32_CLIPBOARD_CONFIGURED = True
