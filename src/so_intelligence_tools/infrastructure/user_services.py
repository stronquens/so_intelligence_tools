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
        user_systemctl_bin: str = "systemctl",
    ) -> None:
        self._project_dir = (project_dir or Path.cwd()).resolve()
        self._service_dir = (service_dir or Path.home() / ".config" / "systemd" / "user").resolve()
        self._user_systemctl_bin = user_systemctl_bin

    @property
    def service_name(self) -> str:
        return "so-intelligence-tools-api.service"

    @property
    def service_path(self) -> Path:
        return self._service_dir / self.service_name

    def install_api_service(self, *, enable_now: bool = True) -> tuple[Path, bool]:
        venv_uvicorn = self._project_dir / ".venv" / "bin" / "uvicorn"
        if not venv_uvicorn.exists():
            raise ToolRunnerConfigurationError(
                "No se encontró `.venv/bin/uvicorn`. Ejecuta `poetry install` antes de instalar el servicio."
            )

        self._service_dir.mkdir(parents=True, exist_ok=True)
        self.service_path.write_text(self._build_service_contents(), encoding="utf-8")

        self._run_systemctl(["--user", "daemon-reload"])
        start_now = enable_now and not self._is_port_in_use("127.0.0.1", 8000)
        if start_now:
            self._run_systemctl(["--user", "enable", "--now", self.service_name])
        else:
            self._run_systemctl(["--user", "enable", self.service_name])
        return self.service_path, start_now

    def _build_service_contents(self) -> str:
        project_dir = self._project_dir
        env_file = project_dir / ".env"
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
                f"EnvironmentFile={env_file}",
                (
                    f"ExecStart={uvicorn_bin} --app-dir {project_dir / 'src'} "
                    "local_inference_api.main:app --host 127.0.0.1 --port 8000"
                ),
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
