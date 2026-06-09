from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from so_intelligence_tools.adapters.testing.fakes import (
    CollectingNotificationAdapter,
    FileScreenshotAdapter,
    InlineTextSelectionAdapter,
    MemoryClipboardAdapter,
    MemoryTextInsertionAdapter,
)
from so_intelligence_tools.domain.errors import ToolRunnerError
from so_intelligence_tools.application.actions.selected_text_correction import (
    run_selected_text_correction,
)
from so_intelligence_tools.application.use_cases.correct_selected_text import (
    correct_selected_text,
)
from so_intelligence_tools.application.use_cases.extract_text_from_image import (
    extract_text_from_image,
)
from so_intelligence_tools.infrastructure.config import get_tool_runner_settings
from so_intelligence_tools.infrastructure.gnome_shortcuts import GnomeShortcutManager
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient
from so_intelligence_tools.infrastructure.logging import configure_logging
from so_intelligence_tools.infrastructure.runtime import build_linux_runtime
from so_intelligence_tools.infrastructure.shortcut_actions import (
    build_default_shortcut_registry,
)
from so_intelligence_tools.infrastructure.shortcut_listener import LinuxShortcutListener
from so_intelligence_tools.infrastructure.user_services import (
    LocalApiUserServiceInstaller,
)
from so_intelligence_tools.system_audio_translation import (
    run_system_audio_translation_toggle,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="so-intelligence-tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    correct_parser = subparsers.add_parser("correct-text")
    correct_parser.add_argument("--text", required=True)
    correct_parser.add_argument("--reasoning-mode", default="off")

    image_parser = subparsers.add_parser("extract-image-text")
    image_parser.add_argument("--image-path", required=True)
    image_parser.add_argument("--reasoning-mode", default="off")

    selected_parser = subparsers.add_parser("run-selected-text-correction")
    selected_parser.add_argument("--debug", action="store_true")
    selected_parser.add_argument("--debug-log-path", default=None)
    subparsers.add_parser("run-system-audio-translation-toggle")
    subparsers.add_parser("listen-shortcuts")
    install_parser = subparsers.add_parser("install-gnome-selected-text-shortcut")
    install_parser.add_argument("--binding", default=None)
    install_parser.add_argument("--debug", action="store_true")
    translation_shortcut_parser = subparsers.add_parser(
        "install-gnome-system-audio-translation-shortcut"
    )
    translation_shortcut_parser.add_argument("--binding", default=None)
    desktop_parser = subparsers.add_parser("install-linux-desktop-integration")
    desktop_parser.add_argument("--binding", default=None)
    desktop_parser.add_argument("--debug-shortcut", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_tool_runner_settings()
    inference_client = LocalInferenceClient(settings)
    notifications = CollectingNotificationAdapter()

    try:
        if args.command == "correct-text":
            selection = InlineTextSelectionAdapter(args.text)
            insertion = MemoryTextInsertionAdapter()
            result = correct_selected_text(
                inference=inference_client,
                text_selection=selection,
                text_insertion=insertion,
                notifications=notifications,
                reasoning_mode=args.reasoning_mode,
            )
            print(result)
            return 0

        if args.command == "extract-image-text":
            screenshot = FileScreenshotAdapter(args.image_path)
            clipboard = MemoryClipboardAdapter()
            result = extract_text_from_image(
                inference=inference_client,
                screenshot=screenshot,
                clipboard=clipboard,
                notifications=notifications,
                reasoning_mode=args.reasoning_mode,
            )
            print(result)
            return 0

        if args.command == "run-selected-text-correction":
            time.sleep(settings.shortcut_action_start_delay_seconds)
            runtime = build_linux_runtime(settings)
            debug_log_path = None
            if args.debug:
                debug_log_path = Path(
                    args.debug_log_path
                    or "~/.cache/so_intelligence_tools/selected_text_correction.log"
                ).expanduser()
            result = run_selected_text_correction(runtime, debug_log_path=debug_log_path)
            print(result)
            return 0

        if args.command == "run-system-audio-translation-toggle":
            result = run_system_audio_translation_toggle(settings)
            print(result)
            return 0

        if args.command == "listen-shortcuts":
            runtime = build_linux_runtime(settings)
            registry = build_default_shortcut_registry(runtime)
            listener = LinuxShortcutListener(
                shortcut_to_action={
                    settings.selected_text_correction_shortcut: "selected-text-correction"
                },
                registry=registry,
            )
            listener.run_forever()
            return 0

        if args.command == "install-gnome-selected-text-shortcut":
            manager = GnomeShortcutManager(project_dir=Path.cwd())
            binding = args.binding or settings.gnome_selected_text_correction_binding
            command = manager.install_selected_text_correction_shortcut(
                binding=binding,
                debug=args.debug,
            )
            print(f"Shortcut installed: {binding}")
            print(f"Command: {command}")
            return 0

        if args.command == "install-gnome-system-audio-translation-shortcut":
            manager = GnomeShortcutManager(project_dir=Path.cwd())
            binding = args.binding or settings.gnome_system_audio_translation_binding
            command = manager.install_system_audio_translation_shortcut(binding=binding)
            print(f"Shortcut installed: {binding}")
            print(f"Command: {command}")
            return 0

        if args.command == "install-linux-desktop-integration":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            service_path, service_started_now = installer.install_api_service(enable_now=True)
            autostart_path = installer.install_desktop_health_autostart()
            manager = GnomeShortcutManager(project_dir=Path.cwd())
            binding = args.binding or settings.gnome_selected_text_correction_binding
            shortcut_command = manager.install_selected_text_correction_shortcut(
                binding=binding,
                debug=args.debug_shortcut,
            )
            audio_shortcut_command = manager.install_system_audio_translation_shortcut(
                binding=settings.gnome_system_audio_translation_binding,
            )
            print(f"User service installed: {service_path}")
            print(f"Desktop health autostart installed: {autostart_path}")
            print(
                "User service state: "
                + (
                    "enabled and started now"
                    if service_started_now
                    else (
                        "enabled for next login because port "
                        f"{settings.local_inference_api_port} is already in use"
                    )
                )
            )
            print(f"Shortcut installed: {binding}")
            print(f"Shortcut command: {shortcut_command}")
            print(
                "System audio shortcut installed: "
                f"{settings.gnome_system_audio_translation_binding}"
            )
            print(f"System audio shortcut command: {audio_shortcut_command}")
            return 0
    except ToolRunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.error("Unsupported command")
    return 2
