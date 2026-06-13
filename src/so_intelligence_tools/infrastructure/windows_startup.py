from __future__ import annotations

import os
from pathlib import Path

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError


class WindowsShortcutStartupInstaller:
    def __init__(
        self,
        *,
        project_dir: Path | None = None,
        startup_dir: Path | None = None,
    ) -> None:
        self._project_dir = (project_dir or Path.cwd()).resolve()
        self._startup_dir = (startup_dir or self._default_startup_dir()).resolve()

    @property
    def launcher_name(self) -> str:
        return "so-intelligence-tools-shortcuts.cmd"

    @property
    def launcher_path(self) -> Path:
        return self._startup_dir / self.launcher_name

    def install(self) -> Path:
        python = self._project_dir / ".venv" / "Scripts" / "python.exe"
        pythonw = self._project_dir / ".venv" / "Scripts" / "pythonw.exe"
        executable = python if python.exists() else pythonw
        if not executable.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `.venv\\Scripts\\python.exe` ni `.venv\\Scripts\\pythonw.exe`. "
                "Ejecuta `poetry install` antes de instalar el listener de atajos Windows."
            )

        self._startup_dir.mkdir(parents=True, exist_ok=True)
        self.launcher_path.write_text(
            self._build_launcher_contents(executable),
            encoding="utf-8",
        )
        return self.launcher_path

    def _build_launcher_contents(self, executable: Path) -> str:
        return "\n".join(
            [
                "@echo off",
                f'cd /d "{self._project_dir}"',
                (
                    'start "so_intelligence_tools shortcuts" /min '
                    f'"{executable}" -m so_intelligence_tools listen-shortcuts'
                ),
                "",
            ]
        )

    @staticmethod
    def _default_startup_dir() -> Path:
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise ToolRunnerConfigurationError("No se encontro APPDATA para ubicar Startup.")
        return (
            Path(appdata)
            / "Microsoft"
            / "Windows"
            / "Start Menu"
            / "Programs"
            / "Startup"
        )


class WindowsApiStartupInstaller:
    def __init__(
        self,
        *,
        project_dir: Path | None = None,
        startup_dir: Path | None = None,
        host: str = "127.0.0.1",
        port: int = 8010,
    ) -> None:
        self._project_dir = (project_dir or Path.cwd()).resolve()
        self._startup_dir = (
            startup_dir or WindowsShortcutStartupInstaller._default_startup_dir()
        ).resolve()
        self._host = host
        self._port = port

    @property
    def launcher_name(self) -> str:
        return "so-intelligence-tools-api.cmd"

    @property
    def launcher_path(self) -> Path:
        return self._startup_dir / self.launcher_name

    def install(self) -> Path:
        python = self._project_dir / ".venv" / "Scripts" / "python.exe"
        if not python.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `.venv\\Scripts\\python.exe`. "
                "Ejecuta `poetry install` antes de instalar la API local en Startup."
            )

        self._startup_dir.mkdir(parents=True, exist_ok=True)
        self.launcher_path.write_text(
            self._build_launcher_contents(python),
            encoding="utf-8",
        )
        return self.launcher_path

    def _build_launcher_contents(self, executable: Path) -> str:
        return "\n".join(
            [
                "@echo off",
                f'cd /d "{self._project_dir}"',
                (
                    'start "so_intelligence_tools api" /min '
                    f'"{executable}" -m uvicorn --app-dir src '
                    "local_inference_api.main:app "
                    f"--host {self._host} --port {self._port}"
                ),
                "",
            ]
        )
