from __future__ import annotations

import os
from pathlib import Path

from so_intelligence_tools.local_tts.codex_voice_control import (
    format_sessions,
    list_sessions,
    register_session,
    select_sessions,
    set_sessions_enabled,
    set_sessions_detail,
    set_sessions_voice,
    toggle_sessions,
)


def test_register_and_list_sessions(monkeypatch, tmp_path):
    monkeypatch.setenv("SO_AI_CODEX_TTS_STATE_DIR", str(tmp_path / "state"))

    session = register_session(pid=os.getpid(), cwd=str(tmp_path), args=["app-server"])

    sessions = list_sessions()

    assert [item.session_id for item in sessions] == [session.session_id]
    assert sessions[0].enabled is True
    assert sessions[0].detail == "actions"
    assert sessions[0].voice == "default"
    assert "on" in format_sessions(sessions)
    assert "actions" in format_sessions(sessions)


def test_toggle_defaults_to_current_cwd(monkeypatch, tmp_path):
    state_dir = tmp_path / "state"
    cwd_a = tmp_path / "a"
    cwd_b = tmp_path / "b"
    cwd_a.mkdir()
    cwd_b.mkdir()
    monkeypatch.setenv("SO_AI_CODEX_TTS_STATE_DIR", str(state_dir))
    register_session(pid=os.getpid(), cwd=str(cwd_a), args=["app-server"])
    session_b = register_session(pid=os.getpid(), cwd=str(cwd_b), args=["app-server"])
    monkeypatch.chdir(cwd_b)

    updated = toggle_sessions()

    assert [session.session_id for session in updated] == [session_b.session_id]
    assert updated[0].enabled is False


def test_set_enabled_can_target_all_sessions(monkeypatch, tmp_path):
    monkeypatch.setenv("SO_AI_CODEX_TTS_STATE_DIR", str(tmp_path / "state"))
    register_session(pid=os.getpid(), cwd=str(tmp_path / "a"), args=["app-server"])
    register_session(pid=os.getpid(), cwd=str(tmp_path / "b"), args=["app-server"])

    updated = set_sessions_enabled(enabled=False, all_sessions=True)

    assert len(updated) == 2
    assert all(not session.enabled for session in updated)


def test_select_sessions_can_target_pid(monkeypatch, tmp_path):
    monkeypatch.setenv("SO_AI_CODEX_TTS_STATE_DIR", str(tmp_path / "state"))
    session = register_session(pid=os.getpid(), cwd=str(tmp_path), args=["app-server"])

    selected = select_sessions(pid=os.getpid())

    assert [item.session_id for item in selected] == [session.session_id]


def test_set_detail_updates_selected_session(monkeypatch, tmp_path):
    monkeypatch.setenv("SO_AI_CODEX_TTS_STATE_DIR", str(tmp_path / "state"))
    register_session(pid=os.getpid(), cwd=str(tmp_path), args=["app-server"])

    updated = set_sessions_detail(detail="minimal")

    assert len(updated) == 1
    assert updated[0].detail == "minimal"


def test_set_voice_updates_selected_session(monkeypatch, tmp_path):
    monkeypatch.setenv("SO_AI_CODEX_TTS_STATE_DIR", str(tmp_path / "state"))
    register_session(pid=os.getpid(), cwd=str(tmp_path), args=["app-server"])

    updated = set_sessions_voice(voice="female")

    assert len(updated) == 1
    assert updated[0].voice == "female"
