from __future__ import annotations

import subprocess

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class LinuxCommandTextSelectionAdapter:
    def __init__(self, settings: ToolRunnerSettings) -> None:
        self._settings = settings

    def get_selected_text(self) -> str | None:
        command = self._settings.linux_read_selection_command
        if not command:
            raise ToolRunnerConfigurationError(
                "No hay comando configurado para leer texto seleccionado en Linux."
            )

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ToolRunnerConfigurationError(
                "El comando de lectura de selección devolvió error en Linux."
            )
        selected_text = result.stdout.strip()
        return selected_text or None
