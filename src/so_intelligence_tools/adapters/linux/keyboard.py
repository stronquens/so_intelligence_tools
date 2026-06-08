from __future__ import annotations

import os
import shutil
import subprocess
import time

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError


class LinuxKeyboardAutomationAdapter:
    def __init__(self, *, copy_delay_seconds: float = 0.15, paste_delay_seconds: float = 0.1) -> None:
        self._copy_delay_seconds = copy_delay_seconds
        self._paste_delay_seconds = paste_delay_seconds

    def trigger_copy_selection(self) -> None:
        if self._is_wayland_session():
            if shutil.which("ydotool"):
                self._run_ydotool_key(["29:1", "46:1", "46:0", "29:0"])
                time.sleep(self._copy_delay_seconds)
                return
            if not shutil.which("wtype"):
                raise UnsupportedEnvironmentError(
                    "En GNOME Wayland se requiere `ydotool` y `ydotoold` para simular copiar la selección."
                )
            self._run_wtype(["-M", "ctrl", "c", "-m", "ctrl"])
            time.sleep(self._copy_delay_seconds)
            return

        if not shutil.which("xdotool"):
            raise UnsupportedEnvironmentError(
                "No hay soporte de automatización de teclado compatible; se requiere xdotool."
            )
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+c"], check=True)
        time.sleep(self._copy_delay_seconds)

    def trigger_paste(self) -> None:
        if self._is_wayland_session():
            if shutil.which("ydotool"):
                self._run_ydotool_key(["29:1", "47:1", "47:0", "29:0"])
                time.sleep(self._paste_delay_seconds)
                return
            if not shutil.which("wtype"):
                raise UnsupportedEnvironmentError(
                    "En GNOME Wayland se requiere `ydotool` y `ydotoold` para simular pegado de texto."
                )
            self._run_wtype(["-M", "ctrl", "v", "-m", "ctrl"])
            time.sleep(self._paste_delay_seconds)
            return

        if not shutil.which("xdotool"):
            raise UnsupportedEnvironmentError(
                "No hay soporte de automatización de teclado compatible; se requiere xdotool."
            )
        subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+v"], check=True)
        time.sleep(self._paste_delay_seconds)

    def type_text(self, text: str) -> None:
        if self._is_wayland_session():
            if shutil.which("ydotool"):
                self._run_ydotool_type(text)
                time.sleep(self._paste_delay_seconds)
                return
            if not shutil.which("wtype"):
                raise UnsupportedEnvironmentError(
                    "En GNOME Wayland se requiere `ydotool` y `ydotoold` para escribir texto sobre la selección activa."
                )
            self._run_wtype([text])
            time.sleep(self._paste_delay_seconds)
            return

        if not shutil.which("xdotool"):
            raise UnsupportedEnvironmentError(
                "No hay soporte de automatización de teclado compatible; se requiere xdotool."
            )
        subprocess.run(["xdotool", "type", "--clearmodifiers", "--delay", "0", text], check=True)
        time.sleep(self._paste_delay_seconds)

    @staticmethod
    def _is_wayland_session() -> bool:
        return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"

    @staticmethod
    def _run_wtype(args: list[str]) -> None:
        result = subprocess.run(
            ["wtype", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise UnsupportedEnvironmentError(
                "GNOME Wayland no permite automatización con `wtype` en este equipo. "
                "Instala y habilita `ydotool` + `ydotoold` para simular entrada a nivel del sistema."
                + (f" Detalle: {detail}" if detail else "")
            )

    @staticmethod
    def _run_ydotool_key(keys: list[str]) -> None:
        result = subprocess.run(
            ["ydotool", "key", *keys],
            env=LinuxKeyboardAutomationAdapter._ydotool_env(),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise UnsupportedEnvironmentError(
                "No se pudo usar `ydotool` para simular teclas. "
                "Comprueba que `ydotoold` está instalado y arrancado."
                + (f" Detalle: {detail}" if detail else "")
            )

    @staticmethod
    def _run_ydotool_type(text: str) -> None:
        result = subprocess.run(
            ["ydotool", "type", text],
            env=LinuxKeyboardAutomationAdapter._ydotool_env(),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise UnsupportedEnvironmentError(
                "No se pudo usar `ydotool` para escribir texto. "
                "Comprueba que `ydotoold` está instalado y arrancado."
                + (f" Detalle: {detail}" if detail else "")
            )

    @staticmethod
    def _ydotool_env() -> dict[str, str]:
        env = dict(os.environ)
        configured_socket = env.get("YDOTOOL_SOCKET")
        if configured_socket and os.path.exists(configured_socket):
            return env
        if os.path.exists("/tmp/.ydotool_socket"):
            env["YDOTOOL_SOCKET"] = "/tmp/.ydotool_socket"
        return env
