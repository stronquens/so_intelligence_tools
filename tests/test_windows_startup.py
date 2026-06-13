from __future__ import annotations

from pathlib import Path

import pytest

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.windows_startup import (
    WindowsApiStartupInstaller,
    WindowsShortcutStartupInstaller,
)


def test_windows_shortcut_startup_installer_writes_launcher(tmp_path: Path):
    project_dir = tmp_path / "project"
    scripts_dir = project_dir / ".venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    python = scripts_dir / "python.exe"
    python.write_text("", encoding="utf-8")
    startup_dir = tmp_path / "Startup"
    installer = WindowsShortcutStartupInstaller(
        project_dir=project_dir,
        startup_dir=startup_dir,
    )

    launcher_path = installer.install()

    assert launcher_path == startup_dir / "so-intelligence-tools-shortcuts.cmd"
    content = launcher_path.read_text(encoding="utf-8")
    assert f'cd /d "{project_dir.resolve()}"' in content
    assert f'"{python.resolve()}" -m so_intelligence_tools listen-shortcuts' in content


def test_windows_shortcut_startup_installer_requires_project_venv(tmp_path: Path):
    installer = WindowsShortcutStartupInstaller(
        project_dir=tmp_path / "project",
        startup_dir=tmp_path / "Startup",
    )

    with pytest.raises(ToolRunnerConfigurationError, match="poetry install"):
        installer.install()


def test_windows_api_startup_installer_writes_launcher(tmp_path: Path):
    project_dir = tmp_path / "project"
    scripts_dir = project_dir / ".venv" / "Scripts"
    scripts_dir.mkdir(parents=True)
    python = scripts_dir / "python.exe"
    python.write_text("", encoding="utf-8")
    startup_dir = tmp_path / "Startup"
    installer = WindowsApiStartupInstaller(
        project_dir=project_dir,
        startup_dir=startup_dir,
        host="127.0.0.1",
        port=8010,
    )

    launcher_path = installer.install()

    assert launcher_path == startup_dir / "so-intelligence-tools-api.cmd"
    content = launcher_path.read_text(encoding="utf-8")
    assert f'cd /d "{project_dir.resolve()}"' in content
    assert (
        f'"{python.resolve()}" -m uvicorn --app-dir src '
        "local_inference_api.main:app --host 127.0.0.1 --port 8010"
    ) in content


def test_windows_api_startup_installer_requires_project_venv(tmp_path: Path):
    installer = WindowsApiStartupInstaller(
        project_dir=tmp_path / "project",
        startup_dir=tmp_path / "Startup",
    )

    with pytest.raises(ToolRunnerConfigurationError, match="poetry install"):
        installer.install()
