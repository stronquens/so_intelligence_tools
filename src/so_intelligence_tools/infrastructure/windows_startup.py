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
        return "so-intelligence-tools-shortcuts.vbs"

    @property
    def legacy_launcher_name(self) -> str:
        return "so-intelligence-tools-shortcuts.cmd"

    @property
    def launcher_path(self) -> Path:
        return self._startup_dir / self.launcher_name

    def install(self) -> Path:
        python = self._project_dir / ".venv" / "Scripts" / "python.exe"
        pythonw = self._project_dir / ".venv" / "Scripts" / "pythonw.exe"
        if not python.exists() or not pythonw.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `.venv\\Scripts\\python.exe` ni `.venv\\Scripts\\pythonw.exe`. "
                "Ejecuta `poetry install` antes de instalar el listener de atajos Windows."
            )

        self._startup_dir.mkdir(parents=True, exist_ok=True)
        self._remove_legacy_launcher()
        self.launcher_path.write_text(
            _build_hidden_vbs_launcher(
                project_dir=self._project_dir,
                executable=pythonw,
                arguments=(
                    "-m so_intelligence_tools.infrastructure.windows_background_launcher "
                    "shortcuts"
                ),
            ),
            encoding="utf-8",
        )
        return self.launcher_path

    def _remove_legacy_launcher(self) -> None:
        legacy_path = self._startup_dir / self.legacy_launcher_name
        if legacy_path.exists():
            legacy_path.unlink()

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


class WindowsDictationStartupInstaller(WindowsShortcutStartupInstaller):
    @property
    def launcher_name(self) -> str:
        return "so-intelligence-tools-dictation.vbs"

    @property
    def legacy_launcher_name(self) -> str:
        return "so-intelligence-tools-dictation.cmd"

    def install(self) -> Path:
        python = self._project_dir / ".venv" / "Scripts" / "python.exe"
        pythonw = self._project_dir / ".venv" / "Scripts" / "pythonw.exe"
        if not python.exists() or not pythonw.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `.venv\\Scripts\\python.exe` ni `.venv\\Scripts\\pythonw.exe`. "
                "Ejecuta `poetry install` antes de instalar el listener de dictado Windows."
            )

        self._startup_dir.mkdir(parents=True, exist_ok=True)
        self._remove_legacy_launcher()
        self.launcher_path.write_text(
            _build_hidden_vbs_launcher(
                project_dir=self._project_dir,
                executable=pythonw,
                arguments=(
                    "-m so_intelligence_tools.infrastructure.windows_background_launcher "
                    "dictation"
                ),
            ),
            encoding="utf-8",
        )
        return self.launcher_path


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
        return "so-intelligence-tools-api.vbs"

    @property
    def legacy_launcher_name(self) -> str:
        return "so-intelligence-tools-api.cmd"

    @property
    def launcher_path(self) -> Path:
        return self._startup_dir / self.launcher_name

    def install(self) -> Path:
        python = self._project_dir / ".venv" / "Scripts" / "python.exe"
        pythonw = self._project_dir / ".venv" / "Scripts" / "pythonw.exe"
        if not python.exists() or not pythonw.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `.venv\\Scripts\\python.exe` ni `.venv\\Scripts\\pythonw.exe`. "
                "Ejecuta `poetry install` antes de instalar la API local en Startup."
            )

        self._startup_dir.mkdir(parents=True, exist_ok=True)
        self._remove_legacy_launcher()
        self.launcher_path.write_text(
            self._build_launcher_contents(pythonw),
            encoding="utf-8",
        )
        return self.launcher_path

    def _build_launcher_contents(self, executable: Path) -> str:
        return _build_hidden_vbs_launcher(
            project_dir=self._project_dir,
            executable=executable,
            arguments=(
                "-m so_intelligence_tools.infrastructure.windows_background_launcher "
                "api "
                f"--host {self._host} --port {self._port}"
            ),
        )

    def _remove_legacy_launcher(self) -> None:
        legacy_path = self._startup_dir / self.legacy_launcher_name
        if legacy_path.exists():
            legacy_path.unlink()


def _build_hidden_vbs_launcher(
    *,
    project_dir: Path,
    executable: Path,
    arguments: str,
) -> str:
    project_dir_value = _vbs_string(str(project_dir))
    executable_value = _vbs_string(str(executable))
    arguments_value = _vbs_string(arguments)
    return "\n".join(
        [
            'Set shell = CreateObject("WScript.Shell")',
            f"projectDir = {project_dir_value}",
            f"executable = {executable_value}",
            f"arguments = {arguments_value}",
            "shell.CurrentDirectory = projectDir",
            'command = Chr(34) & executable & Chr(34) & " " & arguments',
            "shell.Run command, 0, False",
            "",
        ]
    )


def _vbs_string(value: str) -> str:
    escaped = value.replace('"', '""')
    return f'"{escaped}"'
