from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from so_intelligence_tools.local_tts.codex_events import normalize_speech_detail


STATE_DIR_ENV = "SO_AI_CODEX_TTS_STATE_DIR"
DEFAULT_STATE_DIR = "~/.cache/so_intelligence_tools/codex_voice_sessions"
DEFAULT_DETAIL = "actions"
DEFAULT_VOICE = "default"


@dataclass(slots=True)
class CodexVoiceSession:
    session_id: str
    pid: int
    enabled: bool
    cwd: str
    args: list[str]
    started_at: float
    updated_at: float
    detail: str = DEFAULT_DETAIL
    voice: str = DEFAULT_VOICE
    base_url: str | None = None
    last_event_at: float | None = None


def state_dir() -> Path:
    return Path(os.getenv(STATE_DIR_ENV, DEFAULT_STATE_DIR)).expanduser()


def register_session(
    *,
    pid: int,
    cwd: str,
    args: list[str],
    detail: str | None = None,
    voice: str | None = None,
    base_url: str | None = None,
) -> CodexVoiceSession:
    now = time.time()
    session = CodexVoiceSession(
        session_id=f"{pid}-{uuid.uuid4().hex[:8]}",
        pid=pid,
        enabled=True,
        cwd=str(Path(cwd).expanduser()),
        args=args,
        detail=normalize_speech_detail(detail or os.getenv("CODEX_VOICE_DETAIL", DEFAULT_DETAIL)),
        voice=voice or os.getenv("CODEX_VOICE_PROFILE", DEFAULT_VOICE),
        base_url=base_url or os.getenv("CODEX_VOICE_BASE_URL"),
        started_at=now,
        updated_at=now,
    )
    _write_session(session)
    return session


def update_session(
    session_id: str,
    *,
    cwd: str | None = None,
    last_event: bool = False,
) -> CodexVoiceSession | None:
    session = read_session(session_id)
    if session is None:
        return None
    now = time.time()
    if cwd:
        session.cwd = str(Path(cwd).expanduser())
    if last_event:
        session.last_event_at = now
    session.updated_at = now
    _write_session(session)
    return session


def read_session(session_id: str) -> CodexVoiceSession | None:
    path = _session_path(session_id)
    if not path.exists():
        return None
    try:
        return _session_from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def list_sessions(*, include_stale: bool = False) -> list[CodexVoiceSession]:
    directory = state_dir()
    if not directory.exists():
        return []
    sessions: list[CodexVoiceSession] = []
    for path in sorted(directory.glob("*.json")):
        try:
            session = _session_from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
        if include_stale or _pid_alive(session.pid):
            sessions.append(session)
        else:
            path.unlink(missing_ok=True)
    return sorted(sessions, key=lambda item: item.updated_at, reverse=True)


def set_sessions_enabled(
    *,
    enabled: bool,
    pid: int | None = None,
    cwd: str | None = None,
    all_sessions: bool = False,
) -> list[CodexVoiceSession]:
    selected = select_sessions(pid=pid, cwd=cwd, all_sessions=all_sessions)
    updated: list[CodexVoiceSession] = []
    now = time.time()
    for session in selected:
        session.enabled = enabled
        session.updated_at = now
        _write_session(session)
        updated.append(session)
    return updated


def set_sessions_detail(
    *,
    detail: str,
    pid: int | None = None,
    cwd: str | None = None,
    all_sessions: bool = False,
) -> list[CodexVoiceSession]:
    selected = select_sessions(pid=pid, cwd=cwd, all_sessions=all_sessions)
    updated: list[CodexVoiceSession] = []
    now = time.time()
    for session in selected:
        session.detail = normalize_speech_detail(detail)
        session.updated_at = now
        _write_session(session)
        updated.append(session)
    return updated


def set_sessions_voice(
    *,
    voice: str,
    base_url: str | None = None,
    pid: int | None = None,
    cwd: str | None = None,
    all_sessions: bool = False,
) -> list[CodexVoiceSession]:
    selected = select_sessions(pid=pid, cwd=cwd, all_sessions=all_sessions)
    updated: list[CodexVoiceSession] = []
    now = time.time()
    for session in selected:
        session.voice = voice
        session.base_url = base_url or _base_url_for_voice(voice)
        session.updated_at = now
        _write_session(session)
        updated.append(session)
    return updated


def toggle_sessions(
    *,
    pid: int | None = None,
    cwd: str | None = None,
    all_sessions: bool = False,
) -> list[CodexVoiceSession]:
    selected = select_sessions(pid=pid, cwd=cwd, all_sessions=all_sessions)
    updated: list[CodexVoiceSession] = []
    now = time.time()
    for session in selected:
        session.enabled = not session.enabled
        session.updated_at = now
        _write_session(session)
        updated.append(session)
    return updated


def select_sessions(
    *,
    pid: int | None = None,
    cwd: str | None = None,
    all_sessions: bool = False,
) -> list[CodexVoiceSession]:
    sessions = list_sessions()
    if pid is not None:
        return [session for session in sessions if session.pid == pid]
    if all_sessions:
        return sessions
    selected_cwd = Path(cwd or Path.cwd()).expanduser()
    cwd_matches = [
        session for session in sessions if _same_path(Path(session.cwd), selected_cwd)
    ]
    if cwd_matches:
        return cwd_matches[:1]
    return sessions[:1]


def is_session_enabled(session_id: str) -> bool:
    session = read_session(session_id)
    return bool(session.enabled) if session else False


def unregister_session(session_id: str) -> None:
    _session_path(session_id).unlink(missing_ok=True)


def format_sessions(sessions: list[CodexVoiceSession]) -> str:
    if not sessions:
        return "No active Codex voice sessions."
    lines = ["PID\tON\tDETAIL\tVOICE\tBASE_URL\tUPDATED\tCWD"]
    now = time.time()
    for session in sessions:
        age = int(now - session.updated_at)
        enabled = "on" if session.enabled else "off"
        base_url = session.base_url or "-"
        lines.append(
            f"{session.pid}\t{enabled}\t{session.detail}\t{session.voice}\t"
            f"{base_url}\t{age}s ago\t{session.cwd}"
        )
    return "\n".join(lines)


def _write_session(session: CodexVoiceSession) -> None:
    directory = state_dir()
    directory.mkdir(parents=True, exist_ok=True)
    _session_path(session.session_id).write_text(
        json.dumps(_session_to_dict(session), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _session_path(session_id: str) -> Path:
    return state_dir() / f"{session_id}.json"


def _session_to_dict(session: CodexVoiceSession) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "pid": session.pid,
        "enabled": session.enabled,
        "cwd": session.cwd,
        "args": session.args,
        "detail": session.detail,
        "voice": session.voice,
        "base_url": session.base_url,
        "started_at": session.started_at,
        "updated_at": session.updated_at,
        "last_event_at": session.last_event_at,
    }


def _session_from_dict(payload: dict[str, Any]) -> CodexVoiceSession:
    return CodexVoiceSession(
        session_id=str(payload["session_id"]),
        pid=int(payload["pid"]),
        enabled=bool(payload.get("enabled", True)),
        cwd=str(payload.get("cwd") or ""),
        args=[str(arg) for arg in payload.get("args", [])],
        detail=normalize_speech_detail(str(payload.get("detail") or DEFAULT_DETAIL)),
        voice=str(payload.get("voice") or DEFAULT_VOICE),
        base_url=(
            str(payload["base_url"])
            if payload.get("base_url") not in {None, ""}
            else None
        ),
        started_at=float(payload.get("started_at", 0)),
        updated_at=float(payload.get("updated_at", 0)),
        last_event_at=(
            float(payload["last_event_at"])
            if payload.get("last_event_at") is not None
            else None
        ),
    )


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return left.expanduser().absolute() == right.expanduser().absolute()


def _base_url_for_voice(voice: str) -> str | None:
    normalized = voice.strip().lower()
    if normalized in {"default", "male", "hombre"}:
        return os.getenv("CODEX_VOICE_MALE_BASE_URL") or os.getenv("CODEX_VOICE_BASE_URL")
    if normalized in {"female", "mujer"}:
        return os.getenv("CODEX_VOICE_FEMALE_BASE_URL")
    return os.getenv(f"CODEX_VOICE_{normalized.upper()}_BASE_URL")
