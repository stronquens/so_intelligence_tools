from __future__ import annotations

from so_intelligence_tools.adapters.linux.keyboard import LinuxKeyboardAutomationAdapter
from so_intelligence_tools.adapters.linux.text_insertion import LinuxCommandTextInsertionAdapter
from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.infrastructure.press_and_hold_listener import PressAndHoldShortcutListener
from so_intelligence_tools.infrastructure.runtime import build_linux_runtime
from so_intelligence_tools.push_to_talk_dictation.audio import LinuxParecMicrophoneCapture
from so_intelligence_tools.push_to_talk_dictation.onnx_cpu import (
    OnnxCpuNemotronSettings,
    OnnxCpuNemotronTranscriber,
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


def build_push_to_talk_transcriber(settings: ToolRunnerSettings) -> OnnxCpuNemotronTranscriber:
    runtime = settings.push_to_talk_dictation_runtime.lower()
    if runtime != "onnx_cpu":
        raise ToolRunnerConfigurationError(
            f"Runtime de dictado no soportado en esta versión: {settings.push_to_talk_dictation_runtime}"
        )
    return OnnxCpuNemotronTranscriber(
        OnnxCpuNemotronSettings(
            model_repo=settings.push_to_talk_dictation_model_repo,
            model_path=settings.push_to_talk_dictation_model_path,
            language=settings.push_to_talk_dictation_language,
            sample_rate_hz=settings.push_to_talk_dictation_sample_rate_hz,
            chunk_samples=settings.push_to_talk_dictation_chunk_samples,
            use_vad=settings.push_to_talk_dictation_use_vad,
        )
    )


def build_push_to_talk_runner(settings: ToolRunnerSettings) -> PressAndHoldDictationRunner:
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
    )


def run_push_to_talk_dictation_service(settings: ToolRunnerSettings) -> str:
    runner = build_push_to_talk_runner(settings)
    listener = PressAndHoldShortcutListener(
        shortcut=settings.push_to_talk_dictation_shortcut,
        on_press=runner.press,
        on_release=runner.release,
    )
    listener.run_forever()
    return "Push-to-talk dictation service stopped"


def run_push_to_talk_dictation_once(settings: ToolRunnerSettings) -> str:
    transcriber = build_push_to_talk_transcriber(settings)
    transcriber.check_ready()
    return "Push-to-talk dictation runtime ready"
