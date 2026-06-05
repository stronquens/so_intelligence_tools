from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from so_intelligence_tools.domain.errors import UnsupportedEnvironmentError, UserCancelledError


class LinuxScreenshotAdapter:
    def capture_region(self) -> bytes:
        if shutil.which("grim") and shutil.which("slurp"):
            return self._capture_with_grim()
        if shutil.which("gnome-screenshot"):
            return self._capture_with_gnome_screenshot()
        raise UnsupportedEnvironmentError(
            "No hay una herramienta de captura parcial soportada en este entorno Linux."
        )

    def _capture_with_grim(self) -> bytes:
        region = subprocess.run(
            ["slurp"],
            capture_output=True,
            text=True,
            check=False,
        )
        selected_region = region.stdout.strip()
        if region.returncode != 0 or not selected_region:
            raise UserCancelledError("La captura fue cancelada por el usuario.")

        capture = subprocess.run(
            ["grim", "-g", selected_region, "-"],
            capture_output=True,
            check=False,
        )
        if capture.returncode != 0 or not capture.stdout:
            raise UserCancelledError("No se pudo capturar la región seleccionada.")
        return capture.stdout

    def _capture_with_gnome_screenshot(self) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            capture = subprocess.run(
                ["gnome-screenshot", "-a", "-f", str(tmp_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if capture.returncode != 0 or not tmp_path.exists() or tmp_path.stat().st_size == 0:
                raise UserCancelledError("La captura fue cancelada o no generó imagen válida.")
            return tmp_path.read_bytes()
        finally:
            tmp_path.unlink(missing_ok=True)
