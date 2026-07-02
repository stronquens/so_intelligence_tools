from __future__ import annotations

import ast
import json
import socket
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
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

        self.ensure_whisper_server()
        self.release_linux_ctrl_space_conflicts()
        self._service_dir.mkdir(parents=True, exist_ok=True)
        self.dictation_service_path.write_text(
            self._build_dictation_service_contents(),
            encoding="utf-8",
        )

        self._run_systemctl(["--user", "daemon-reload"])
        if enable_now:
            self._run_systemctl(["--user", "enable", self.dictation_service_name])
            self._run_systemctl(["--user", "restart", self.dictation_service_name])
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

    def ensure_whisper_server(self) -> Path:
        compose_dir = self._project_dir / "docker" / "whisper-server"
        compose_file = compose_dir / "compose.yaml"
        env_file = compose_dir / ".env"
        env_example = compose_dir / ".env.example"
        if not compose_file.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `docker/whisper-server/compose.yaml`."
            )
        if not env_file.exists():
            if not env_example.exists():
                raise ToolRunnerConfigurationError(
                    "No se encontro `docker/whisper-server/.env.example`."
                )
            env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
        self._run_docker_compose(compose_dir, ["up", "-d"])
        self._wait_for_whisper_server(env_file)
        return env_file

    def ensure_chatterbox_tts_server(self) -> Path:
        compose_dir = self._project_dir / "docker" / "chatterbox-tts"
        compose_file = compose_dir / "compose.yaml"
        env_file = compose_dir / ".env"
        env_example = compose_dir / ".env.example"
        if not compose_file.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `docker/chatterbox-tts/compose.yaml`."
            )
        if not env_file.exists():
            if not env_example.exists():
                raise ToolRunnerConfigurationError(
                    "No se encontro `docker/chatterbox-tts/.env.example`."
                )
            env_file.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
        self._run_docker_compose(compose_dir, ["up", "-d", "--build"])
        self._wait_for_chatterbox_tts_server(env_file)
        return env_file

    def stop_chatterbox_tts_server(self) -> None:
        compose_dir = self._project_dir / "docker" / "chatterbox-tts"
        compose_file = compose_dir / "compose.yaml"
        if not compose_file.exists():
            raise ToolRunnerConfigurationError(
                "No se encontro `docker/chatterbox-tts/compose.yaml`."
            )
        self._run_docker_compose(compose_dir, ["down"])

    def chatterbox_tts_server_ready(self) -> bool:
        env_file = self._project_dir / "docker" / "chatterbox-tts" / ".env"
        if not env_file.exists():
            return False
        env_values = self._read_simple_env(env_file)
        port = env_values.get("CHATTERBOX_TTS_PORT", "9011")
        try:
            with urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as response:
                return 200 <= response.status < 300
        except (HTTPError, URLError, TimeoutError, OSError):
            return False

    def release_linux_ctrl_space_conflicts(self) -> None:
        ctrl_space_values = {
            "control+space",
            "<control>space",
            "<ctrl>space",
            "ctrl+space",
        }
        self._remove_gsettings_array_values(
            schema="org.freedesktop.ibus.general.hotkey",
            key="trigger",
            blocked_values=ctrl_space_values,
        )
        self._remove_gsettings_array_values(
            schema="org.freedesktop.ibus.general.hotkey",
            key="triggers",
            blocked_values=ctrl_space_values,
        )
        self._remove_gsettings_array_values(
            schema="org.gnome.desktop.wm.keybindings",
            key="switch-input-source",
            blocked_values=ctrl_space_values,
        )
        self._remove_gsettings_array_values(
            schema="org.gnome.desktop.wm.keybindings",
            key="switch-input-source-backward",
            blocked_values=ctrl_space_values,
        )
        self._clear_ulauncher_ctrl_space_hotkey(
            Path.home() / ".config" / "ulauncher" / "settings.json"
        )

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

    def _run_docker_compose(self, compose_dir: Path, args: list[str]) -> None:
        result = subprocess.run(
            ["docker", "compose", *args],
            cwd=compose_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise ToolRunnerConfigurationError(
                "No se pudo ejecutar Docker Compose para el servicio local. "
                f"Detalle: {(result.stderr or result.stdout).strip()}"
            )

    def _wait_for_whisper_server(self, env_file: Path) -> None:
        env_values = self._read_simple_env(env_file)
        port = env_values.get("WHISPER_PORT", "9000")
        timeout_seconds = float(env_values.get("WHISPER_STARTUP_TIMEOUT_SECONDS", "300"))
        deadline = time.monotonic() + timeout_seconds
        url = f"http://127.0.0.1:{port}/v1/models"
        last_error = ""
        while time.monotonic() < deadline:
            try:
                with urlopen(url, timeout=2) as response:
                    if 200 <= response.status < 300:
                        return
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                last_error = str(exc)
            time.sleep(2)
        raise ToolRunnerConfigurationError(
            "El servidor faster-whisper no estuvo listo a tiempo. "
            f"URL: {url}. Ultimo error: {last_error or 'sin respuesta'}"
        )

    def _wait_for_chatterbox_tts_server(self, env_file: Path) -> None:
        env_values = self._read_simple_env(env_file)
        port = env_values.get("CHATTERBOX_TTS_PORT", "9011")
        timeout_seconds = float(
            env_values.get("CHATTERBOX_TTS_STARTUP_TIMEOUT_SECONDS", "600")
        )
        deadline = time.monotonic() + timeout_seconds
        url = f"http://127.0.0.1:{port}/health"
        last_error = ""
        while time.monotonic() < deadline:
            try:
                with urlopen(url, timeout=2) as response:
                    if 200 <= response.status < 300:
                        return
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                last_error = str(exc)
            time.sleep(2)
        raise ToolRunnerConfigurationError(
            "El servidor Chatterbox TTS no estuvo listo a tiempo. "
            f"URL: {url}. Ultimo error: {last_error or 'sin respuesta'}"
        )

    @staticmethod
    def _read_simple_env(env_file: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in env_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
        return values

    def _remove_gsettings_array_values(
        self,
        *,
        schema: str,
        key: str,
        blocked_values: set[str],
    ) -> None:
        current = self._run_gsettings(["get", schema, key])
        if current is None:
            return
        values = self._parse_gsettings_string_array(current)
        if values is None:
            return
        filtered = [
            value
            for value in values
            if self._normalize_hotkey(value) not in blocked_values
        ]
        if filtered == values:
            return
        serialized = "[" + ", ".join(repr(value) for value in filtered) + "]"
        self._run_gsettings(["set", schema, key, serialized])

    @staticmethod
    def _parse_gsettings_string_array(raw: str) -> list[str] | None:
        raw = raw.strip()
        if raw == "@as []":
            return []
        try:
            parsed = ast.literal_eval(raw)
        except (SyntaxError, ValueError):
            return None
        if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
            return None
        return parsed

    @staticmethod
    def _normalize_hotkey(value: str) -> str:
        return value.lower().replace(" ", "").replace("_l", "").replace("_r", "")

    @staticmethod
    def _run_gsettings(args: list[str]) -> str | None:
        result = subprocess.run(
            ["gsettings", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()

    @staticmethod
    def _clear_ulauncher_ctrl_space_hotkey(settings_path: Path) -> bool:
        if not settings_path.exists():
            return False
        try:
            payload = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        if not isinstance(payload, dict):
            return False
        current = payload.get("hotkey-show-app")
        if not isinstance(current, str):
            return False
        if LocalApiUserServiceInstaller._normalize_hotkey(current) not in {
            "control+space",
            "<control>space",
            "<primary>space",
            "<ctrl>space",
            "ctrl+space",
        }:
            return False
        payload["hotkey-show-app"] = ""
        settings_path.write_text(
            json.dumps(payload, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return True

    @staticmethod
    def _is_port_in_use(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex((host, port)) == 0
