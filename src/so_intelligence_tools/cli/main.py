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
from so_intelligence_tools.infrastructure.runtime import build_runtime
from so_intelligence_tools.infrastructure.shortcut_map import (
    ShortcutPlatform,
    build_shortcut_map,
    filter_shortcut_map,
    format_shortcut_map,
)
from so_intelligence_tools.infrastructure.shortcut_actions import (
    build_default_shortcut_registry,
)
from so_intelligence_tools.infrastructure.shortcut_listener import build_shortcut_listener
from so_intelligence_tools.infrastructure.user_services import (
    LocalApiUserServiceInstaller,
)
from so_intelligence_tools.local_tts.client import LocalTtsClient, LocalTtsSettings
from so_intelligence_tools.local_tts.codex_voice import (
    run_codex_visible_event_listener,
    speak_text,
)
from so_intelligence_tools.local_tts.codex_voice_control import (
    format_sessions,
    list_sessions,
    set_sessions_detail,
    set_sessions_enabled,
    set_sessions_voice,
    toggle_sessions,
)
from so_intelligence_tools.infrastructure.windows_startup import (
    WindowsApiStartupInstaller,
    WindowsDictationStartupInstaller,
    WindowsShortcutStartupInstaller,
)
from so_intelligence_tools.push_to_talk_dictation import (
    run_push_to_talk_dictation_once,
    run_push_to_talk_dictation_service,
)
from so_intelligence_tools.system_audio_translation import (
    run_system_audio_translation_toggle,
)
from so_intelligence_tools.voice_translation_virtual_microphone import (
    run_voice_translation_virtual_microphone_toggle,
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
    subparsers.add_parser("run-voice-translation-virtual-mic-toggle")
    subparsers.add_parser("run-push-to-talk-dictation-service")
    subparsers.add_parser("check-push-to-talk-dictation-runtime")
    subparsers.add_parser("listen-dictation-shortcut")
    subparsers.add_parser("listen-shortcuts")
    subparsers.add_parser("install-windows-dictation-startup")
    subparsers.add_parser("install-windows-shortcut-listener-startup")
    subparsers.add_parser("install-windows-api-startup")
    shortcut_map_parser = subparsers.add_parser("show-shortcuts")
    shortcut_map_parser.add_argument(
        "--platform",
        choices=["linux", "windows", "desktop"],
        default=None,
        help="Filter shortcuts by platform.",
    )
    install_parser = subparsers.add_parser("install-gnome-selected-text-shortcut")
    install_parser.add_argument("--binding", default=None)
    install_parser.add_argument("--debug", action="store_true")
    translation_shortcut_parser = subparsers.add_parser(
        "install-gnome-system-audio-translation-shortcut"
    )
    translation_shortcut_parser.add_argument("--binding", default=None)
    voice_shortcut_parser = subparsers.add_parser(
        "install-gnome-voice-translation-shortcut"
    )
    voice_shortcut_parser.add_argument("--binding", default=None)
    subparsers.add_parser("install-push-to-talk-dictation-service")
    subparsers.add_parser("ensure-whisper-docker-server")
    subparsers.add_parser("ensure-piper-tts-server")
    subparsers.add_parser("stop-piper-tts-server")
    subparsers.add_parser("status-piper-tts-server")
    speak_parser = subparsers.add_parser("speak-text")
    speak_parser.add_argument("--text", default=None)
    speak_parser.add_argument("--base-url", default=None)
    speak_parser.add_argument("--voice", default=None)
    codex_voice_parser = subparsers.add_parser("listen-codex-visible-events")
    codex_voice_parser.add_argument("--base-url", default=None)
    codex_voice_parser.add_argument("--voice", default=None)
    codex_voice_parser.add_argument("--include-progress", action="store_true")
    codex_voice_parser.add_argument("--final-only", action="store_true")
    codex_voice_parser.add_argument(
        "--detail",
        choices=["minimal", "actions", "standard", "no-code", "full"],
        default=None,
    )
    codex_voice_parser.add_argument("--max-segment-chars", type=int, default=None)
    subparsers.add_parser("codex-voice-sessions")
    codex_voice_on_parser = subparsers.add_parser("codex-voice-on")
    _add_codex_voice_target_args(codex_voice_on_parser)
    codex_voice_off_parser = subparsers.add_parser("codex-voice-off")
    _add_codex_voice_target_args(codex_voice_off_parser)
    codex_voice_toggle_parser = subparsers.add_parser("codex-voice-toggle")
    _add_codex_voice_target_args(codex_voice_toggle_parser)
    codex_voice_detail_parser = subparsers.add_parser("codex-voice-detail")
    codex_voice_detail_parser.add_argument(
        "detail",
        choices=["minimal", "actions", "standard", "no-code", "full"],
    )
    _add_codex_voice_target_args(codex_voice_detail_parser)
    codex_voice_voice_parser = subparsers.add_parser("codex-voice-voice")
    codex_voice_voice_parser.add_argument("voice")
    codex_voice_voice_parser.add_argument("--base-url", default=None)
    _add_codex_voice_target_args(codex_voice_voice_parser)
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

        if args.command == "show-shortcuts":
            platform: ShortcutPlatform | None = args.platform
            entries = filter_shortcut_map(build_shortcut_map(settings), platform)
            print(format_shortcut_map(entries))
            return 0

        if args.command == "run-selected-text-correction":
            time.sleep(settings.shortcut_action_start_delay_seconds)
            runtime = build_runtime(settings)
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

        if args.command == "run-voice-translation-virtual-mic-toggle":
            result = run_voice_translation_virtual_microphone_toggle(settings)
            print(result)
            return 0

        if args.command in {
            "run-push-to-talk-dictation-service",
            "listen-dictation-shortcut",
        }:
            result = run_push_to_talk_dictation_service(settings)
            print(result)
            return 0

        if args.command == "check-push-to-talk-dictation-runtime":
            result = run_push_to_talk_dictation_once(settings)
            print(result)
            return 0

        if args.command == "listen-shortcuts":
            runtime = build_runtime(settings)
            debug_log_path = Path(
                "~/.cache/so_intelligence_tools/selected_text_correction.log"
            ).expanduser()
            registry = build_default_shortcut_registry(
                runtime,
                debug_log_path=debug_log_path,
            )
            listener = build_shortcut_listener(
                shortcut_to_action={
                    _selected_text_correction_shortcut_for_platform(settings): (
                        "selected-text-correction"
                    )
                },
                registry=registry,
                action_delay_seconds=settings.shortcut_action_start_delay_seconds,
                action_cooldown_seconds=settings.shortcut_action_cooldown_seconds,
                event_log_path=Path(
                    "~/.cache/so_intelligence_tools/shortcut_listener.log"
                ).expanduser(),
            )
            listener.run_forever()
            return 0

        if args.command == "install-windows-shortcut-listener-startup":
            installer = WindowsShortcutStartupInstaller(project_dir=Path.cwd())
            launcher_path = installer.install()
            print(f"Windows shortcut listener startup installed: {launcher_path}")
            print(
                "Start it now with: poetry run so-intelligence-tools listen-shortcuts "
                "or sign out and back in."
            )
            return 0

        if args.command == "install-windows-dictation-startup":
            installer = WindowsDictationStartupInstaller(project_dir=Path.cwd())
            launcher_path = installer.install()
            print(f"Windows dictation startup installed: {launcher_path}")
            print(
                "Start it now with: poetry run so-intelligence-tools "
                "listen-dictation-shortcut or sign out and back in."
            )
            return 0

        if args.command == "install-windows-api-startup":
            installer = WindowsApiStartupInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            launcher_path = installer.install()
            print(f"Windows local API startup installed: {launcher_path}")
            print(
                "Start it now with: poetry run uvicorn --app-dir src "
                "local_inference_api.main:app --host "
                f"{settings.local_inference_api_host} --port "
                f"{settings.local_inference_api_port} or sign out and back in."
            )
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

        if args.command == "install-gnome-voice-translation-shortcut":
            manager = GnomeShortcutManager(project_dir=Path.cwd())
            binding = args.binding or settings.gnome_voice_translation_binding
            command = manager.install_voice_translation_shortcut(binding=binding)
            print(f"Shortcut installed: {binding}")
            print(f"Command: {command}")
            return 0

        if args.command == "install-push-to-talk-dictation-service":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            service_path, started_now = installer.install_push_to_talk_dictation_service(
                enable_now=True
            )
            print(
                "Faster-whisper Docker server ensured: "
                f"{Path.cwd() / 'docker' / 'whisper-server' / '.env'}"
            )
            print(f"Push-to-talk dictation service installed: {service_path}")
            print(
                "Push-to-talk dictation service state: "
                + ("enabled and started now" if started_now else "enabled for next login")
            )
            return 0

        if args.command == "ensure-whisper-docker-server":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            whisper_env_path = installer.ensure_whisper_server()
            print(f"Faster-whisper Docker server ensured: {whisper_env_path}")
            return 0

        if args.command == "ensure-piper-tts-server":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            piper_env_path = installer.ensure_piper_tts_server()
            print(f"Piper TTS Docker server ensured: {piper_env_path}")
            return 0

        if args.command == "stop-piper-tts-server":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            installer.stop_piper_tts_server()
            print("Piper TTS Docker server stopped. Voice output is disabled.")
            return 0

        if args.command == "status-piper-tts-server":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            ready = installer.piper_tts_server_ready()
            print("ready" if ready else "disabled")
            return 0

        if args.command == "speak-text":
            text = args.text if args.text is not None else sys.stdin.read()
            client = _build_local_tts_client(
                settings,
                base_url=args.base_url,
                voice=args.voice,
            )
            print(speak_text(client, text))
            return 0

        if args.command == "listen-codex-visible-events":
            client = _build_local_tts_client(
                settings,
                base_url=args.base_url,
                voice=args.voice,
            )
            return run_codex_visible_event_listener(
                client=client,
                include_progress=(
                    False
                    if args.final_only
                    else args.include_progress or settings.codex_voice_include_progress
                ),
                speech_detail=args.detail or settings.codex_voice_detail,
                max_segment_chars=(
                    args.max_segment_chars or settings.codex_voice_max_segment_chars
                ),
            )

        if args.command == "codex-voice-sessions":
            print(format_sessions(list_sessions()))
            return 0

        if args.command == "codex-voice-on":
            sessions = set_sessions_enabled(
                enabled=True,
                pid=args.pid,
                all_sessions=args.all,
            )
            print(_format_codex_voice_update("enabled", sessions))
            return 0

        if args.command == "codex-voice-off":
            sessions = set_sessions_enabled(
                enabled=False,
                pid=args.pid,
                all_sessions=args.all,
            )
            print(_format_codex_voice_update("disabled", sessions))
            return 0

        if args.command == "codex-voice-toggle":
            sessions = toggle_sessions(pid=args.pid, all_sessions=args.all)
            print(_format_codex_voice_update("toggled", sessions))
            return 0

        if args.command == "codex-voice-detail":
            sessions = set_sessions_detail(
                detail=args.detail,
                pid=args.pid,
                all_sessions=args.all,
            )
            print(_format_codex_voice_update(f"detail set to {args.detail}", sessions))
            return 0

        if args.command == "codex-voice-voice":
            sessions = set_sessions_voice(
                voice=args.voice,
                base_url=args.base_url,
                pid=args.pid,
                all_sessions=args.all,
            )
            print(_format_codex_voice_update(f"voice set to {args.voice}", sessions))
            return 0

        if args.command == "install-linux-desktop-integration":
            installer = LocalApiUserServiceInstaller(
                project_dir=Path.cwd(),
                host=settings.local_inference_api_host,
                port=settings.local_inference_api_port,
            )
            service_path, service_started_now = installer.install_api_service(enable_now=True)
            dictation_service_path, dictation_service_started_now = (
                installer.install_push_to_talk_dictation_service(enable_now=True)
            )
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
            voice_shortcut_command = manager.install_voice_translation_shortcut(
                binding=settings.gnome_voice_translation_binding,
            )
            print(f"User service installed: {service_path}")
            print(
                "Faster-whisper Docker server ensured: "
                f"{Path.cwd() / 'docker' / 'whisper-server' / '.env'}"
            )
            print(f"Push-to-talk dictation service installed: {dictation_service_path}")
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
            print(
                "Voice translation shortcut installed: "
                f"{settings.gnome_voice_translation_binding}"
            )
            print(f"Voice translation shortcut command: {voice_shortcut_command}")
            print(
                "Push-to-talk dictation service state: "
                + (
                    "enabled and started now"
                    if dictation_service_started_now
                    else "enabled for next login"
                )
            )
            return 0
    except ToolRunnerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.error("Unsupported command")
    return 2


def _selected_text_correction_shortcut_for_platform(settings) -> str:
    if sys.platform == "win32":
        return settings.windows_selected_text_correction_shortcut
    return settings.selected_text_correction_shortcut


def _add_codex_voice_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--all", action="store_true")


def _format_codex_voice_update(action: str, sessions) -> str:
    if not sessions:
        return "No matching active Codex voice session."
    return f"Codex voice {action}:\n{format_sessions(sessions)}"


def _build_local_tts_client(
    settings,
    *,
    base_url: str | None = None,
    voice: str | None = None,
) -> LocalTtsClient:
    return LocalTtsClient(
        LocalTtsSettings(
            base_url=base_url or settings.local_tts_base_url,
            timeout_seconds=settings.local_tts_timeout_seconds,
            playback_command=settings.local_tts_playback_command,
            voice=voice or "default",
        )
    )
