from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from so_intelligence_tools.local_tts.codex_voice_control import CodexVoiceSession


WRAPPER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex-tts-wrapper.py"


def load_wrapper_module():
    spec = importlib.util.spec_from_file_location("codex_tts_wrapper", WRAPPER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_real_codex_finds_latest_windows_extension(monkeypatch, tmp_path):
    wrapper = load_wrapper_module()
    old_cli = (
        tmp_path
        / ".vscode"
        / "extensions"
        / "openai.chatgpt-26.1-win32-x64"
        / "bin"
        / "windows-x86_64"
        / "codex.exe"
    )
    new_cli = (
        tmp_path
        / ".vscode"
        / "extensions"
        / "openai.chatgpt-26.2-win32-x64"
        / "bin"
        / "windows-x86_64"
        / "codex.exe"
    )
    old_cli.parent.mkdir(parents=True)
    new_cli.parent.mkdir(parents=True)
    old_cli.write_text("", encoding="utf-8")
    new_cli.write_text("", encoding="utf-8")
    os.utime(old_cli, (1000, 1000))
    os.utime(new_cli, (2000, 2000))

    monkeypatch.setattr(wrapper.sys, "platform", "win32")
    monkeypatch.setattr(wrapper.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(wrapper.shutil, "which", lambda command: None)

    assert wrapper.resolve_real_codex() == new_cli.resolve()


def test_build_tts_listener_command_uses_windows_venv_script(monkeypatch, tmp_path):
    wrapper = load_wrapper_module()
    local_cli = tmp_path / ".venv" / "Scripts" / "so-intelligence-tools.exe"
    local_cli.parent.mkdir(parents=True)
    local_cli.write_text("", encoding="utf-8")
    session = CodexVoiceSession(
        session_id="session",
        pid=123,
        enabled=True,
        cwd=str(tmp_path),
        args=["app-server"],
        started_at=1,
        updated_at=1,
        detail="actions",
        voice="female",
        base_url="http://127.0.0.1:9011",
    )

    monkeypatch.setattr(wrapper, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(wrapper.os, "name", "nt")

    assert wrapper.build_tts_listener_command(session) == [
        str(local_cli),
        "listen-codex-visible-events",
        "--detail",
        "actions",
        "--voice",
        "female",
        "--base-url",
        "http://127.0.0.1:9011",
    ]
