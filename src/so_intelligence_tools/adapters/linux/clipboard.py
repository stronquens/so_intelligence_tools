from __future__ import annotations

import shutil
import subprocess

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError


class LinuxClipboardAdapter:
    def set_text(self, text: str) -> None:
        if shutil.which("wl-copy"):
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
