#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import shlex
import shutil
import signal
import subprocess
import sys
import threading
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from so_intelligence_tools.local_tts.codex_voice_control import (  # noqa: E402
    CodexVoiceSession,
    register_session,
    unregister_session,
    update_session,
)


def main() -> int:
    real_codex = resolve_real_codex()
    argv = [str(real_codex), *sys.argv[1:]]
    if "app-server" not in sys.argv[1:]:
        os.execv(str(real_codex), argv)
    session = register_session(pid=os.getpid(), cwd=os.getcwd(), args=sys.argv[1:])

    child = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        text=True,
        bufsize=1,
        env={**os.environ, "SO_AI_CODEX_TTS_WRAPPED": "1"},
    )
    assert child.stdin is not None
    assert child.stdout is not None

    tts: subprocess.Popen[str] | None = None
    tts_key: tuple[str, str, str | None] | None = None

    stdin_thread = threading.Thread(
        target=pipe_stdin_to_child,
        args=(child, session.session_id),
        daemon=True,
    )
    stdin_thread.start()

    try:
        for line in child.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            current_session = update_session(session.session_id, last_event=True)
            if current_session is None:
                current_session = session
            if not current_session.enabled:
                tts = stop_tts_listener(tts)
                tts_key = None
                continue
            next_key = (
                current_session.detail,
                current_session.voice,
                current_session.base_url,
            )
            if tts_key != next_key or tts is None or tts.poll() is not None:
                tts = stop_tts_listener(tts)
                tts = start_tts_listener(current_session)
                tts_key = next_key
            write_line_to_tts(tts, line)
        return child.wait()
    finally:
        unregister_session(session.session_id)
        tts = stop_tts_listener(tts)
        terminate_process(child)


def resolve_real_codex() -> Path:
    configured = os.getenv("SO_AI_CODEX_REAL_CLI")
    if configured:
        return Path(configured).expanduser().resolve()

    extension_candidates = sorted(
        Path.home().glob(".vscode/extensions/openai.chatgpt-*/bin/linux-x86_64/codex"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if extension_candidates:
        return extension_candidates[0].resolve()

    path_candidate = shutil.which("codex")
    if path_candidate:
        resolved = Path(path_candidate).resolve()
        if resolved != Path(__file__).resolve():
            return resolved

    raise SystemExit(
        "No real Codex CLI found. Set SO_AI_CODEX_REAL_CLI to the bundled codex binary."
    )


def start_tts_listener(session: CodexVoiceSession) -> subprocess.Popen[str] | None:
    if os.getenv("SO_AI_CODEX_TTS_DISABLED") == "1":
        return None
    command_env = os.getenv("SO_AI_CODEX_TTS_LISTENER")
    if command_env:
        command = shlex.split(command_env)
    else:
        local_cli = REPO_ROOT / ".venv" / "bin" / "so-intelligence-tools"
        if local_cli.exists():
            command = [str(local_cli), "listen-codex-visible-events"]
        else:
            command = ["poetry", "run", "so-intelligence-tools", "listen-codex-visible-events"]
    command = [
        *command,
        "--detail",
        session.detail,
        "--voice",
        session.voice,
    ]
    if session.base_url:
        command.extend(["--base-url", session.base_url])

    try:
        return subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
    except OSError:
        return None


def stop_tts_listener(tts: subprocess.Popen[str] | None) -> subprocess.Popen[str] | None:
    if tts is None:
        return None
    if tts.poll() is None:
        try:
            tts.stdin.close() if tts.stdin is not None else None
        except (BrokenPipeError, OSError):
            pass
        terminate_process(tts)
    return None


def write_line_to_tts(tts: subprocess.Popen[str] | None, line: str) -> None:
    if tts is None or tts.stdin is None or tts.poll() is not None:
        return
    try:
        tts.stdin.write(line)
        tts.stdin.flush()
    except (BrokenPipeError, OSError):
        return


def pipe_stdin_to_child(child: subprocess.Popen[str], session_id: str) -> None:
    assert child.stdin is not None
    try:
        for line in sys.stdin:
            cwd = extract_cwd_from_json_line(line)
            if cwd:
                update_session(session_id, cwd=cwd)
            child.stdin.write(line)
            child.stdin.flush()
    except (BrokenPipeError, OSError):
        return
    finally:
        try:
            child.stdin.close()
        except OSError:
            pass


def extract_cwd_from_json_line(line: str) -> str | None:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return None
    value = find_key(payload, "cwd")
    return value if isinstance(value, str) and value else None


def find_key(value: object, key: str) -> object | None:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for nested in value.values():
            found = find_key(nested, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = find_key(nested, key)
            if found is not None:
                return found
    return None


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=2)
    except Exception:
        process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
