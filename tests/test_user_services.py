from __future__ import annotations

import subprocess
import json

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


def test_install_push_to_talk_dictation_service_writes_unit(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    service_dir = tmp_path / "systemd-user"
    (project_dir / ".venv" / "bin").mkdir(parents=True)
    (project_dir / ".venv" / "bin" / "so-intelligence-tools").write_text("", encoding="utf-8")
    whisper_dir = project_dir / "docker" / "whisper-server"
    whisper_dir.mkdir(parents=True)
    (whisper_dir / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
    (whisper_dir / ".env.example").write_text("WHISPER_MODEL=large-v3-turbo\n", encoding="utf-8")

    calls: list[tuple[list[str], str | None]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        cwd = kwargs.get("cwd")
        calls.append((command, str(cwd) if cwd is not None else None))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    installer = LocalApiUserServiceInstaller(
        project_dir=project_dir,
        service_dir=service_dir,
        user_systemctl_bin="systemctl",
    )
    monkeypatch.setattr(installer, "_wait_for_whisper_server", lambda _env_file: None)

    service_path, started_now = installer.install_push_to_talk_dictation_service(
        enable_now=True
    )

    assert started_now is True
    assert service_path == service_dir / "so-intelligence-tools-push-to-talk-dictation.service"
    assert (whisper_dir / ".env").read_text(encoding="utf-8") == "WHISPER_MODEL=large-v3-turbo\n"
    service_text = service_path.read_text(encoding="utf-8")
    assert "push-to-talk dictation listener" in service_text
    assert f"WorkingDirectory={project_dir}" in service_text
    assert "run-push-to-talk-dictation-service" in service_text
    assert calls == [
        (["docker", "compose", "up", "-d"], str(whisper_dir)),
        (["gsettings", "get", "org.freedesktop.ibus.general.hotkey", "trigger"], None),
        (["gsettings", "get", "org.freedesktop.ibus.general.hotkey", "triggers"], None),
        (["gsettings", "get", "org.gnome.desktop.wm.keybindings", "switch-input-source"], None),
        (
            [
                "gsettings",
                "get",
                "org.gnome.desktop.wm.keybindings",
                "switch-input-source-backward",
            ],
            None,
        ),
        (["systemctl", "--user", "daemon-reload"], None),
        (
            [
                "systemctl",
                "--user",
                "enable",
                "so-intelligence-tools-push-to-talk-dictation.service",
            ],
            None,
        ),
        (
            [
                "systemctl",
                "--user",
                "restart",
                "so-intelligence-tools-push-to-talk-dictation.service",
            ],
            None,
        ),
    ]


def test_ensure_whisper_server_requires_compose_file(tmp_path):
    installer = LocalApiUserServiceInstaller(project_dir=tmp_path / "project")

    with pytest.raises(ToolRunnerConfigurationError, match="whisper-server"):
        installer.ensure_whisper_server()


def test_ensure_chatterbox_tts_server_copies_env_and_starts_compose(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    chatterbox_dir = project_dir / "docker" / "chatterbox-tts"
    chatterbox_dir.mkdir(parents=True)
    (chatterbox_dir / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
    (chatterbox_dir / ".env.example").write_text(
        "CHATTERBOX_TTS_PORT=9011\n",
        encoding="utf-8",
    )
    calls: list[tuple[list[str], str | None]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        cwd = kwargs.get("cwd")
        calls.append((command, str(cwd) if cwd is not None else None))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    installer = LocalApiUserServiceInstaller(project_dir=project_dir)
    monkeypatch.setattr(installer, "_wait_for_chatterbox_tts_server", lambda _env_file: None)

    env_path = installer.ensure_chatterbox_tts_server()

    assert env_path == chatterbox_dir / ".env"
    assert env_path.read_text(encoding="utf-8") == "CHATTERBOX_TTS_PORT=9011\n"
    assert calls == [(["docker", "compose", "up", "-d", "--build"], str(chatterbox_dir))]


def test_stop_chatterbox_tts_server_runs_compose_down(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    chatterbox_dir = project_dir / "docker" / "chatterbox-tts"
    chatterbox_dir.mkdir(parents=True)
    (chatterbox_dir / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
    calls: list[tuple[list[str], str | None]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        cwd = kwargs.get("cwd")
        calls.append((command, str(cwd) if cwd is not None else None))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    installer = LocalApiUserServiceInstaller(project_dir=project_dir)

    installer.stop_chatterbox_tts_server()

    assert calls == [(["docker", "compose", "down"], str(chatterbox_dir))]


def test_read_simple_env_parses_whisper_startup_settings(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "# comment",
                "WHISPER_PORT=9000",
                "WHISPER_STARTUP_TIMEOUT_SECONDS='120'",
                "",
            ]
        ),
        encoding="utf-8",
    )

    values = LocalApiUserServiceInstaller._read_simple_env(env_file)

    assert values["WHISPER_PORT"] == "9000"
    assert values["WHISPER_STARTUP_TIMEOUT_SECONDS"] == "120"


def test_release_linux_ctrl_space_conflicts_removes_ibus_trigger(tmp_path, monkeypatch):
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command == ["gsettings", "get", "org.freedesktop.ibus.general.hotkey", "trigger"]:
            return subprocess.CompletedProcess(
                command,
                0,
                "['Control+space', 'Zenkaku_Hankaku', 'Alt+Release+Alt_R']\n",
                "",
            )
        if command == ["gsettings", "get", "org.freedesktop.ibus.general.hotkey", "triggers"]:
            return subprocess.CompletedProcess(command, 0, "['<Super>space']\n", "")
        if command == ["gsettings", "get", "org.gnome.desktop.wm.keybindings", "switch-input-source"]:
            return subprocess.CompletedProcess(command, 0, "['<Control>space', '<Super>space']\n", "")
        if command == [
            "gsettings",
            "get",
            "org.gnome.desktop.wm.keybindings",
            "switch-input-source-backward",
        ]:
            return subprocess.CompletedProcess(command, 0, "['<Shift><Super>space']\n", "")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("subprocess.run", fake_run)
    installer = LocalApiUserServiceInstaller(project_dir=tmp_path / "project")

    installer.release_linux_ctrl_space_conflicts()

    assert [
        "gsettings",
        "set",
        "org.freedesktop.ibus.general.hotkey",
        "trigger",
        "['Zenkaku_Hankaku', 'Alt+Release+Alt_R']",
    ] in calls
    assert [
        "gsettings",
        "set",
        "org.freedesktop.ibus.general.hotkey",
        "triggers",
        "['<Super>space']",
    ] not in calls
    assert [
        "gsettings",
        "set",
        "org.gnome.desktop.wm.keybindings",
        "switch-input-source",
        "['<Super>space']",
    ] in calls


def test_clear_ulauncher_ctrl_space_hotkey(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps(
            {
                "hotkey-show-app": "<Primary>space",
                "theme-name": "light",
            }
        ),
        encoding="utf-8",
    )

    changed = LocalApiUserServiceInstaller._clear_ulauncher_ctrl_space_hotkey(
        settings_path
    )

    assert changed is True
    assert json.loads(settings_path.read_text(encoding="utf-8")) == {
        "hotkey-show-app": "",
        "theme-name": "light",
    }
