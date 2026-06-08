from __future__ import annotations

import os
import shutil
import subprocess

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError


class LinuxClipboardAdapter:
    def get_primary_text(self) -> str | None:
        if self._is_wayland_session():
            if not shutil.which("wl-paste"):
                raise UnsupportedEnvironmentError(
                    "En Wayland se requiere `wl-paste` para leer la selección primaria. "
                    "Instala el paquete `wl-clipboard`."
                )
            result = subprocess.run(
                ["wl-paste", "--primary", "--no-newline"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout if result.returncode == 0 else None

        if shutil.which("xclip"):
            result = subprocess.run(
                ["xclip", "-selection", "primary", "-o"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout if result.returncode == 0 else None
        return None

    def get_text(self) -> str | None:
        if self._is_wayland_session():
            if not shutil.which("wl-paste"):
                raise UnsupportedEnvironmentError(
                    "En Wayland se requiere `wl-paste` para leer el portapapeles. "
                    "Instala el paquete `wl-clipboard`."
                )
            result = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout if result.returncode == 0 else None

        if shutil.which("xclip"):
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout if result.returncode == 0 else None
        if shutil.which("xsel"):
            result = subprocess.run(
                ["xsel", "--clipboard", "--output"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout if result.returncode == 0 else None
        raise UnsupportedEnvironmentError(
            "No hay una utilidad de lectura de portapapeles compatible disponible en Linux."
        )

    def set_text(self, text: str) -> None:
        if self._is_wayland_session():
            if not shutil.which("wl-copy"):
                raise UnsupportedEnvironmentError(
                    "En Wayland se requiere `wl-copy` para escribir en el portapapeles. "
                    "Instala el paquete `wl-clipboard`."
                )
            subprocess.run(["wl-copy"], input=text, text=True, check=True)
            return

        if shutil.which("xclip"):
            subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
            return
        if shutil.which("xsel"):
            subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
            return
        raise UnsupportedEnvironmentError(
            "No hay una utilidad de portapapeles compatible disponible en Linux."
        )

    @staticmethod
    def _is_wayland_session() -> bool:
        return os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
