from __future__ import annotations

import socket
import subprocess
from pathlib import Path

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError


class LocalApiUserServiceInstaller:
    def __init__(
        self,
        *,
        project_dir: Path | None = None,
        service_dir: Path | None = None,
        autostart_dir: Path | None = None,
        user_systemctl_bin: str = "systemctl",
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        self._project_dir = (project_dir or Path.cwd()).resolve()
        self._service_dir = (service_dir or Path.home() / ".config" / "systemd" / "user").resolve()
        self._autostart_dir = (autostart_dir or Path.home() / ".config" / "autostart").resolve()
        self._user_systemctl_bin = user_systemctl_bin
        self._host = host
        self._port = port

    @property
    def service_name(self) -> str:
        return "so-intelligence-tools-api.service"

    @property
    def dictation_service_name(self) -> str:
        return "so-intelligence-tools-push-to-talk-dictation.service"

    @property
    def service_path(self) -> Path:
        return self._service_dir / self.service_name

    @property
    def dictation_service_path(self) -> Path:
        return self._service_dir / self.dictation_service_name

    @property
    def autostart_path(self) -> Path:
        return self._autostart_dir / "so-intelligence-tools-desktop-health.desktop"

    def install_api_service(self, *, enable_now: bool = True) -> tuple[Path, bool]:
        venv_uvicorn = self._project_dir / ".venv" / "bin" / "uvicorn"
        if not venv_uvicorn.exists():
            raise ToolRunnerConfigurationError(
                "No se encontró `.venv/bin/uvicorn`. Ejecuta `poetry install` antes de instalar el servicio."
            )

        self._service_dir.mkdir(parents=True, exist_ok=True)
        self.service_path.write_text(self._build_service_contents(), encoding="utf-8")

        self._run_systemctl(["--user", "daemon-reload"])
        start_now = enable_now and not self._is_port_in_use(self._host, self._port)
        if start_now:
            self._run_systemctl(["--user", "enable", "--now", self.service_name])
        else:
            self._run_systemctl(["--user", "enable", self.service_name])
        return self.service_path, start_now

    def install_push_to_talk_dictation_service(self, *, enable_now: bool = True) -> tuple[Path, bool]:
        cli = self._project_dir / ".venv" / "bin" / "so-intelligence-tools"
        if not cli.exists():
            raise ToolRunnerConfigurationError(
                "No se encontró `.venv/bin/so-intelligence-tools`. Ejecuta `poetry install` antes de instalar el servicio."
            )

        self._service_dir.mkdir(parents=True, exist_ok=True)
        self.dictation_service_path.write_text(
            self._build_dictation_service_contents(),
            encoding="utf-8",
        )

        self._run_systemctl(["--user", "daemon-reload"])
        if enable_now:
            self._run_systemctl(["--user", "enable", "--now", self.dictation_service_name])
        else:
            self._run_systemctl(["--user", "enable", self.dictation_service_name])
        return self.dictation_service_path, enable_now

    def install_desktop_health_autostart(self) -> Path:
        script_path = self._project_dir / "scripts" / "ensure-linux-desktop-integration.sh"
        if not script_path.exists():
            raise ToolRunnerConfigurationError(
                "No se encontró el script de autostart de integración Linux."
            )
        self._autostart_dir.mkdir(parents=True, exist_ok=True)
        self.autostart_path.write_text(
            "\n".join(
                [
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=so_intelligence_tools desktop health",
                    "Comment=Ensures so_intelligence_tools API and GNOME shortcuts are ready after login",
                    f"Exec={script_path}",
                    "Terminal=false",
                    "X-GNOME-Autostart-enabled=true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return self.autostart_path

    def _build_service_contents(self) -> str:
        project_dir = self._project_dir
        uvicorn_bin = project_dir / ".venv" / "bin" / "uvicorn"
        return "\n".join(
            [
                "[Unit]",
                "Description=so_intelligence_tools local inference API",
                "After=network.target",
                "Wants=network.target",
                "",
                "[Service]",
                "Type=simple",
                f"WorkingDirectory={project_dir}",
                (
                    f"ExecStart={uvicorn_bin} --app-dir {project_dir / 'src'} "
                    f"local_inference_api.main:app --host {self._host} --port {self._port}"
                ),
                "Restart=on-failure",
                "RestartSec=2",
                "",
                "[Install]",
                "WantedBy=default.target",
                "",
            ]
        )

    def _build_dictation_service_contents(self) -> str:
        project_dir = self._project_dir
        cli = project_dir / ".venv" / "bin" / "so-intelligence-tools"
        return "\n".join(
            [
                "[Unit]",
                "Description=so_intelligence_tools push-to-talk dictation listener",
                "After=graphical-session.target",
                "Wants=graphical-session.target",
                "",
                "[Service]",
                "Type=simple",
                f"WorkingDirectory={project_dir}",
                f"ExecStart={cli} run-push-to-talk-dictation-service",
                "Restart=on-failure",
                "RestartSec=2",
                "",
                "[Install]",
                "WantedBy=default.target",
                "",
            ]
        )

    def _run_systemctl(self, args: list[str]) -> None:
        result = subprocess.run(
            [self._user_systemctl_bin, *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ToolRunnerConfigurationError(
                "No se pudo instalar o activar el servicio de usuario. "
                f"Detalle: {(result.stderr or result.stdout).strip()}"
            )

    @staticmethod
    def _is_port_in_use(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((host, port)) == 0
