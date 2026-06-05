from __future__ import annotations

import subprocess

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class LinuxCommandTextInsertionAdapter:
    def __init__(self, settings: ToolRunnerSettings) -> None:
        self._settings = settings

    def replace_selected_text(self, text: str) -> None:
        command = self._settings.linux_replace_selection_command
        if not command:
            raise ToolRunnerConfigurationError(
                "No hay comando configurado para reemplazar texto seleccionado en Linux."
            )
        result = subprocess.run(
            command,
            shell=True,
            input=text,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ToolRunnerConfigurationError(
                "El comando de reemplazo de texto devolvió error en Linux."
            )
