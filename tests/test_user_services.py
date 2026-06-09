from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.user_services import (
    LocalApiUserServiceInstaller,
)


def test_install_api_service_writes_unit_and_enables(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    service_dir = tmp_path / "systemd-user"
    (project_dir / ".venv" / "bin").mkdir(parents=True)
    (project_dir / "src").mkdir(parents=True)
    (project_dir / ".env").write_text("LOCAL_INFERENCE_API_PORT=8000\n", encoding="utf-8")
    (project_dir / ".venv" / "bin" / "uvicorn").write_text("", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(LocalApiUserServiceInstaller, "_is_port_in_use", staticmethod(lambda *_: False))
    installer = LocalApiUserServiceInstaller(
        project_dir=project_dir,
        service_dir=service_dir,
        user_systemctl_bin="systemctl",
        host="127.0.0.1",
        port=8010,
    )

    service_path, started_now = installer.install_api_service(enable_now=True)

    assert started_now is True
    assert service_path.exists()
    service_text = service_path.read_text(encoding="utf-8")
    assert "Description=so_intelligence_tools local inference API" in service_text
    assert f"WorkingDirectory={project_dir}" in service_text
    assert "EnvironmentFile=" not in service_text
    assert "local_inference_api.main:app --host 127.0.0.1 --port 8010" in service_text
    assert calls == [
        ["systemctl", "--user", "daemon-reload"],
        ["systemctl", "--user", "enable", "--now", "so-intelligence-tools-api.service"],
    ]


def test_install_api_service_requires_project_venv(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    installer = LocalApiUserServiceInstaller(project_dir=project_dir, service_dir=tmp_path / "user")

    with pytest.raises(ToolRunnerConfigurationError, match="poetry install"):
        installer.install_api_service()


def test_install_api_service_enables_without_start_when_port_is_busy(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    service_dir = tmp_path / "systemd-user"
    (project_dir / ".venv" / "bin").mkdir(parents=True)
    (project_dir / "src").mkdir(parents=True)
    (project_dir / ".env").write_text("LOCAL_INFERENCE_API_PORT=8000\n", encoding="utf-8")
    (project_dir / ".venv" / "bin" / "uvicorn").write_text("", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    monkeypatch.setattr(LocalApiUserServiceInstaller, "_is_port_in_use", staticmethod(lambda *_: True))
    installer = LocalApiUserServiceInstaller(
        project_dir=project_dir,
        service_dir=service_dir,
        user_systemctl_bin="systemctl",
    )

    service_path, started_now = installer.install_api_service(enable_now=True)

    assert service_path.exists()
    assert started_now is False
    assert calls == [
        ["systemctl", "--user", "daemon-reload"],
        ["systemctl", "--user", "enable", "so-intelligence-tools-api.service"],
    ]


def test_install_desktop_health_autostart_writes_desktop_entry(tmp_path):
    project_dir = tmp_path / "project"
    autostart_dir = tmp_path / "autostart"
    (project_dir / "scripts").mkdir(parents=True)
    script_path = project_dir / "scripts" / "ensure-linux-desktop-integration.sh"
    script_path.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    installer = LocalApiUserServiceInstaller(
        project_dir=project_dir,
        autostart_dir=autostart_dir,
    )

    autostart_path = installer.install_desktop_health_autostart()

    assert autostart_path == autostart_dir / "so-intelligence-tools-desktop-health.desktop"
    desktop_entry = autostart_path.read_text(encoding="utf-8")
    assert "Type=Application" in desktop_entry
    assert f"Exec={script_path}" in desktop_entry
    assert "X-GNOME-Autostart-enabled=true" in desktop_entry
