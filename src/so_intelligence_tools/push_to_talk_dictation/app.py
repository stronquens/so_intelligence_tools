from __future__ import annotations

import sys
import os
from pathlib import Path

from so_intelligence_tools.adapters.linux.keyboard import LinuxKeyboardAutomationAdapter
from so_intelligence_tools.adapters.linux.text_insertion import LinuxCommandTextInsertionAdapter
from so_intelligence_tools.adapters.windows.keyboard import WindowsKeyboardAutomationAdapter
from so_intelligence_tools.adapters.windows.text_insertion import WindowsCommandTextInsertionAdapter
from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.infrastructure.press_and_hold_listener import PressAndHoldShortcutListener
from so_intelligence_tools.infrastructure.runtime import build_linux_runtime, build_windows_runtime
from so_intelligence_tools.ports.streaming_asr import StreamingAsrTranscriber
from so_intelligence_tools.push_to_talk_dictation.audio import (
    LinuxParecMicrophoneCapture,
    WindowsSoundDeviceMicrophoneCapture,
)
from so_intelligence_tools.push_to_talk_dictation.faster_whisper_http import (
    FasterWhisperHttpSettings,
    FasterWhisperHttpTranscriber,
)
from so_intelligence_tools.push_to_talk_dictation.session import (
    PressAndHoldDictationRunner,
    StreamingDictationController,
)


class LinuxDictationTextInsertionAdapter:
    def __init__(
        self,
        *,
        keyboard: LinuxKeyboardAutomationAdapter,
        fallback: LinuxCommandTextInsertionAdapter,
    ) -> None:
        self._keyboard = keyboard
        self._fallback = fallback

    def replace_selected_text(self, text: str) -> None:
        try:
            self._keyboard.type_text(text)
        except Exception:
            self._fallback.replace_selected_text(text)


class WindowsDictationTextInsertionAdapter:
    def __init__(
        self,
        *,
        keyboard: WindowsKeyboardAutomationAdapter,
        fallback: WindowsCommandTextInsertionAdapter,
    ) -> None:
        self._keyboard = keyboard
        self._fallback = fallback

    def replace_selected_text(self, text: str) -> None:
        try:
            self._keyboard.type_text(text)
        except Exception:
            self._fallback.replace_selected_text(text)


def build_push_to_talk_transcriber(settings: ToolRunnerSettings) -> StreamingAsrTranscriber:
    runtime = settings.push_to_talk_dictation_runtime.lower()
    if runtime in {"faster_whisper_http", "whisper_http"}:
        return FasterWhisperHttpTranscriber(
            FasterWhisperHttpSettings(
                base_url=settings.push_to_talk_dictation_faster_whisper_base_url,
                model=settings.push_to_talk_dictation_faster_whisper_model,
                language=settings.push_to_talk_dictation_language,
                sample_rate_hz=settings.push_to_talk_dictation_sample_rate_hz,
                timeout_seconds=(
                    settings.push_to_talk_dictation_faster_whisper_timeout_seconds
                ),
                prompt=settings.push_to_talk_dictation_faster_whisper_prompt,
            )
        )
    raise ToolRunnerConfigurationError(
        "Runtime de dictado no soportado en esta version: "
        f"{settings.push_to_talk_dictation_runtime}"
    )


def build_push_to_talk_runner(
    settings: ToolRunnerSettings,
    *,
    platform_name: str | None = None,
) -> PressAndHoldDictationRunner:
    detected_platform = platform_name or sys.platform
    if detected_platform == "win32":
        return build_windows_push_to_talk_runner(settings)
    return build_linux_push_to_talk_runner(settings)


def build_linux_push_to_talk_runner(settings: ToolRunnerSettings) -> PressAndHoldDictationRunner:
    runtime = build_linux_runtime(settings)
    transcriber = build_push_to_talk_transcriber(settings)
    fallback_insertion = LinuxCommandTextInsertionAdapter(
        settings,
        clipboard=runtime.clipboard,
        keyboard=runtime.keyboard,
    )
    text_insertion = LinuxDictationTextInsertionAdapter(
        keyboard=runtime.keyboard,
        fallback=fallback_insertion,
    )
    controller = StreamingDictationController(
        transcriber=transcriber,
        text_insertion=text_insertion,
        notifications=runtime.notifications,
        insertion_strategy=settings.push_to_talk_dictation_insertion_strategy,
    )

    def capture_factory(callback):
        return LinuxParecMicrophoneCapture(
            sample_rate_hz=settings.push_to_talk_dictation_sample_rate_hz,
            chunk_ms=settings.push_to_talk_dictation_chunk_ms,
            source_name=settings.push_to_talk_dictation_microphone_source,
            callback=callback,
        )

    return PressAndHoldDictationRunner(
        controller=controller,
        audio_capture_factory=capture_factory,
        post_roll_seconds=settings.push_to_talk_dictation_post_roll_seconds,
    )


def build_windows_push_to_talk_runner(settings: ToolRunnerSettings) -> PressAndHoldDictationRunner:
    runtime = build_windows_runtime(settings)
    transcriber = build_push_to_talk_transcriber(settings)
    keyboard = WindowsKeyboardAutomationAdapter()
    text_insertion = WindowsCommandTextInsertionAdapter(
        clipboard=runtime.clipboard,
        keyboard=keyboard,
    )
    controller = StreamingDictationController(
        transcriber=transcriber,
        text_insertion=text_insertion,
        notifications=runtime.notifications,
        insertion_strategy="final_on_release",
    )

    def capture_factory(callback):
        return WindowsSoundDeviceMicrophoneCapture(
            sample_rate_hz=settings.push_to_talk_dictation_sample_rate_hz,
            chunk_ms=settings.push_to_talk_dictation_chunk_ms,
            source_name=settings.push_to_talk_dictation_microphone_source,
            callback=callback,
        )

    return PressAndHoldDictationRunner(
        controller=controller,
        audio_capture_factory=capture_factory,
        post_roll_seconds=settings.push_to_talk_dictation_post_roll_seconds,
    )


def run_push_to_talk_dictation_service(
    settings: ToolRunnerSettings,
    *,
    platform_name: str | None = None,
) -> str:
    detected_platform = platform_name or sys.platform
    runner = build_push_to_talk_runner(settings, platform_name=detected_platform)
    runner.warm_up()
    listener = PressAndHoldShortcutListener(
        shortcut=_dictation_shortcut_for_platform(settings, detected_platform),
        on_press=runner.press,
        on_release=runner.release,
        event_log_path=_dictation_event_log_path(detected_platform),
    )
    listener.run_forever()
    return "Push-to-talk dictation service stopped"


def run_push_to_talk_dictation_once(settings: ToolRunnerSettings) -> str:
    transcriber = build_push_to_talk_transcriber(settings)
    transcriber.check_ready()
    return "Push-to-talk dictation runtime ready"


def _dictation_shortcut_for_platform(
    settings: ToolRunnerSettings,
    platform_name: str,
) -> str:
    if platform_name == "win32":
        return settings.windows_push_to_talk_dictation_shortcut
    return settings.push_to_talk_dictation_shortcut


def _dictation_event_log_path(platform_name: str) -> Path:
    if platform_name == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        root = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return root / "so_intelligence_tools" / "logs" / "so-intelligence-tools-dictation-events.log"
    return (
        Path("~/.cache/so_intelligence_tools/so-intelligence-tools-dictation-events.log")
        .expanduser()
    )
