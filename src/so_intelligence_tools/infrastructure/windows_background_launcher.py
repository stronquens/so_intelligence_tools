from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="windows-background-launcher")
    subparsers = parser.add_subparsers(dest="command", required=True)

    api_parser = subparsers.add_parser("api")
    api_parser.add_argument("--host", default="127.0.0.1")
    api_parser.add_argument("--port", type=int, default=8010)

    subparsers.add_parser("shortcuts")
    subparsers.add_parser("dictation")

    args = parser.parse_args(argv)
    project_dir = Path.cwd()
    python = Path(sys.executable).with_name("python.exe")
    if args.command == "api":
        command = [
            str(python),
            "-m",
            "uvicorn",
            "--app-dir",
            "src",
            "local_inference_api.main:app",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ]
        log_name = "so-intelligence-tools-api.log"
    elif args.command == "shortcuts":
        command = [str(python), "-m", "so_intelligence_tools", "listen-shortcuts"]
        log_name = "so-intelligence-tools-shortcuts.log"
    else:
        command = [str(python), "-m", "so_intelligence_tools", "listen-dictation-shortcut"]
        log_name = "so-intelligence-tools-dictation.log"

    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    with (log_dir / log_name).open("a", encoding="utf-8") as log_file:
        subprocess.Popen(
            command,
            cwd=project_dir,
            stdin=subprocess.DEVNULL,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW,
            close_fds=True,
        )
    return 0


def _log_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "so_intelligence_tools" / "logs"
    return Path.home() / "AppData" / "Local" / "so_intelligence_tools" / "logs"


if __name__ == "__main__":
    raise SystemExit(main())
