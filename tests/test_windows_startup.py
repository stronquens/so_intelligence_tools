from __future__ import annotations

from pathlib import Path

import pytest

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure import windows_background_launcher
from so_intelligence_tools.infrastructure.windows_startup import (
    WindowsApiStartupInstaller,
    WindowsDictationStartupInstaller,
    WindowsShortcutStartupInstaller,
)


def test_windows_shortcut_startup_installer_writes_launcher(tmp_path: Path):
    project_dir = tmp_path / "project"
    scripts_dir = project_dir / ".venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    python = scripts_dir / "python.exe"
    python.write_text("", encoding="utf-8")
    pythonw = scripts_dir / "pythonw.exe"
    pythonw.write_text("", encoding="utf-8")
    startup_dir = tmp_path / "Startup"
    legacy_launcher = startup_dir / "so-intelligence-tools-shortcuts.cmd"
    startup_dir.mkdir()
    legacy_launcher.write_text("old", encoding="utf-8")
    installer = WindowsShortcutStartupInstaller(
        project_dir=project_dir,
        startup_dir=startup_dir,
    )

    launcher_path = installer.install()

    assert launcher_path == startup_dir / "so-intelligence-tools-shortcuts.vbs"
    assert not legacy_launcher.exists()
    content = launcher_path.read_text(encoding="utf-8")
    assert "WScript.Shell" in content
    assert f'projectDir = "{project_dir.resolve()}"' in content
    assert f'executable = "{pythonw.resolve()}"' in content
    assert (
        'arguments = "-m so_intelligence_tools.infrastructure.windows_background_launcher '
        'shortcuts"'
    ) in content
    assert "shell.Run command, 0, False" in content


def test_windows_shortcut_startup_installer_requires_project_venv(tmp_path: Path):
    installer = WindowsShortcutStartupInstaller(
        project_dir=tmp_path / "project",
        startup_dir=tmp_path / "Startup",
    )

    with pytest.raises(ToolRunnerConfigurationError, match="poetry install"):
        installer.install()


def test_windows_dictation_startup_installer_writes_launcher(tmp_path: Path):
    project_dir = tmp_path / "project"
    scripts_dir = project_dir / ".venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    python = scripts_dir / "python.exe"
    python.write_text("", encoding="utf-8")
    pythonw = scripts_dir / "pythonw.exe"
    pythonw.write_text("", encoding="utf-8")
    startup_dir = tmp_path / "Startup"
    legacy_launcher = startup_dir / "so-intelligence-tools-dictation.cmd"
    startup_dir.mkdir()
    legacy_launcher.write_text("old", encoding="utf-8")
    installer = WindowsDictationStartupInstaller(
        project_dir=project_dir,
        startup_dir=startup_dir,
    )

    launcher_path = installer.install()

    assert launcher_path == startup_dir / "so-intelligence-tools-dictation.vbs"
    assert not legacy_launcher.exists()
    content = launcher_path.read_text(encoding="utf-8")
    assert "WScript.Shell" in content
    assert f'projectDir = "{project_dir.resolve()}"' in content
    assert f'executable = "{pythonw.resolve()}"' in content
    assert (
        'arguments = "-m so_intelligence_tools.infrastructure.windows_background_launcher '
        'dictation"'
    ) in content
    assert "shell.Run command, 0, False" in content


def test_windows_api_startup_installer_writes_launcher(tmp_path: Path):
    project_dir = tmp_path / "project"
    scripts_dir = project_dir / ".venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    python = scripts_dir / "python.exe"
    python.write_text("", encoding="utf-8")
    pythonw = scripts_dir / "pythonw.exe"
    pythonw.write_text("", encoding="utf-8")
    startup_dir = tmp_path / "Startup"
    legacy_launcher = startup_dir / "so-intelligence-tools-api.cmd"
    startup_dir.mkdir()
    legacy_launcher.write_text("old", encoding="utf-8")
    installer = WindowsApiStartupInstaller(
        project_dir=project_dir,
        startup_dir=startup_dir,
        host="127.0.0.1",
        port=8010,
    )

    launcher_path = installer.install()

    assert launcher_path == startup_dir / "so-intelligence-tools-api.vbs"
    assert not legacy_launcher.exists()
    content = launcher_path.read_text(encoding="utf-8")
    assert "WScript.Shell" in content
    assert f'projectDir = "{project_dir.resolve()}"' in content
    assert f'executable = "{pythonw.resolve()}"' in content
    assert (
        'arguments = "-m so_intelligence_tools.infrastructure.windows_background_launcher '
        'api '
        '--host 127.0.0.1 --port 8010"'
    ) in content
    assert "shell.Run command, 0, False" in content


def test_windows_api_startup_installer_requires_project_venv(tmp_path: Path):
    installer = WindowsApiStartupInstaller(
        project_dir=tmp_path / "project",
        startup_dir=tmp_path / "Startup",
    )

    with pytest.raises(ToolRunnerConfigurationError, match="poetry install"):
        installer.install()


@pytest.mark.parametrize(
    ("argv", "expected_args", "expected_log"),
    [
        (
            ["api", "--host", "127.0.0.1", "--port", "8010"],
            [
                "-m",
                "uvicorn",
                "--app-dir",
                "src",
                "local_inference_api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8010",
            ],
            "so-intelligence-tools-api.log",
        ),
        (
            ["shortcuts"],
            ["-m", "so_intelligence_tools", "listen-shortcuts"],
            "so-intelligence-tools-shortcuts.log",
        ),
        (
            ["dictation"],
            ["-m", "so_intelligence_tools", "listen-dictation-shortcut"],
            "so-intelligence-tools-dictation.log",
        ),
    ],
)
def test_windows_background_launcher_starts_process_hidden(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    expected_args: list[str],
    expected_log: str,
):
    local_app_data = tmp_path / "local"
    pythonw = tmp_path / ".venv" / "Scripts" / "pythonw.exe"
    pythonw.parent.mkdir(parents=True)
    pythonw.write_text("", encoding="utf-8")
    calls = []

    def fake_popen(command, **kwargs):
        calls.append((command, kwargs))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setattr(windows_background_launcher.sys, "executable", str(pythonw))
    monkeypatch.setattr(windows_background_launcher.subprocess, "Popen", fake_popen)

    assert windows_background_launcher.main(argv) == 0

    command, kwargs = calls[0]
    assert command == [str(pythonw.with_name("python.exe")), *expected_args]
    assert kwargs["cwd"] == tmp_path
    assert kwargs["creationflags"] == windows_background_launcher.CREATE_NO_WINDOW
    assert (
        local_app_data / "so_intelligence_tools" / "logs" / expected_log
    ).exists()
