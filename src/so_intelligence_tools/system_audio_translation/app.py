from __future__ import annotations

from pathlib import Path
from typing import Protocol

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.domain.models import SystemAudioSessionMode
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings, get_tool_runner_settings
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient
from so_intelligence_tools.system_audio_translation.audio_capture import LinuxParecAudioCapture
from so_intelligence_tools.system_audio_translation.modes import normalize_system_audio_mode
from so_intelligence_tools.system_audio_translation.openai_realtime import (
    OpenAIRealtimeTranslationController,
)
from so_intelligence_tools.system_audio_translation.provider import ChunkedAudioTranslationProvider
from so_intelligence_tools.system_audio_translation.session import (
    SystemAudioTranslationController,
    ToggleSocketServer,
    TranscriptSessionLogger,
    send_toggle_command,
)
from so_intelligence_tools.system_audio_translation.window import SystemAudioTranslationWindow
from so_intelligence_tools.voice_translation_virtual_microphone.app import (
    build_voice_translation_pipeline,
)
from so_intelligence_tools.voice_translation_virtual_microphone.pipeline import (
    VoiceTranslationVirtualMicrophonePipeline,
)


class SessionController(Protocol):
    state: str

    def bind_callbacks(self, *, on_state_changed, on_block_ready, on_partial_text_changed=None) -> None: ...
    def start(self) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def reset(self) -> None: ...
    def stop(self) -> None: ...


class ModeAwareSystemAudioTranslationApp:
    def __init__(self, settings: ToolRunnerSettings) -> None:
        self.settings = settings
        self.mode: SystemAudioSessionMode = normalize_system_audio_mode(
            settings.system_audio_translation_mode
        )
        self.window = SystemAudioTranslationWindow(
            title=settings.system_audio_translation_window_title,
            initial_mode=self.mode,
            on_pause=self.pause,
            on_resume=self.resume,
            on_reset=self.reset,
            on_close=self.stop,
            on_mode_changed=self.change_mode,
            on_voice_translation_toggle=self.toggle_voice_translation,
        )
        self._socket_path = Path(settings.system_audio_translation_control_socket_path).expanduser()
        self._toggle_server = ToggleSocketServer(
            socket_path=self._socket_path,
            on_toggle=lambda: (self.stop(), self.window.close_from_controller()),
        )
        self._controller: SessionController | None = None
        self._voice_translation_pipeline: VoiceTranslationVirtualMicrophonePipeline | None = None

    def run(self) -> str:
        self._toggle_server.start()
        try:
            self.start_voice_passthrough()
            self._start_mode(self.mode)
            self.window.run()
        finally:
            self.stop()
            self._toggle_server.stop()
        return "System audio translation session finished."

    def pause(self) -> None:
        if self._controller is not None:
            self._controller.pause()

    def resume(self) -> None:
        if self._controller is not None:
            self._controller.resume()

    def reset(self) -> None:
        if self._controller is not None:
            self._controller.reset()

    def stop(self) -> None:
        self.stop_voice_passthrough()
        controller = self._controller
        if controller is not None:
            controller.stop()
            self._controller = None

    def toggle_voice_translation(self) -> None:
        pipeline = self._voice_translation_pipeline
        if pipeline is None or not pipeline.translation_active:
            self.start_voice_translation()
            return
        self.stop_voice_translation()

    def start_voice_passthrough(self) -> None:
        if self._voice_translation_pipeline is not None:
            return
        try:
            pipeline = build_voice_translation_pipeline(self.settings)
            pipeline.start()
        except Exception as exc:
            self.window.set_voice_translation_state(
                False,
                f"Micrófono virtual: error - {exc}",
            )
            return
        self._voice_translation_pipeline = pipeline
        self.window.set_voice_translation_state(
            False,
            (
                "Micrófono virtual activo en passthrough: selecciona "
                f"{pipeline.virtual_source_name} como micrófono"
            ),
        )

    def start_voice_translation(self) -> None:
        self.start_voice_passthrough()
        pipeline = self._voice_translation_pipeline
        if pipeline is None:
            return
        try:
            pipeline.start_translation()
        except Exception as exc:
            self.window.set_voice_translation_state(
                False,
                f"Micrófono traducido: error - {exc}",
            )
            return
        self.window.set_voice_translation_state(
            True,
            (
                "Traducción activa: voz original bajada y voz inglesa superpuesta en "
                f"{pipeline.virtual_source_name}"
            ),
        )

    def stop_voice_translation(self) -> None:
        pipeline = self._voice_translation_pipeline
        if pipeline is not None:
            pipeline.stop_translation()
            self.window.set_voice_translation_state(
                False,
                (
                    "Micrófono virtual activo en passthrough: selecciona "
                    f"{pipeline.virtual_source_name} como micrófono"
                ),
            )

    def stop_voice_passthrough(self) -> None:
        pipeline = self._voice_translation_pipeline
        if pipeline is not None:
            pipeline.stop()
            self._voice_translation_pipeline = None
        self.window.set_voice_translation_state(False, "Micrófono virtual: apagado")

    def change_mode(self, mode: SystemAudioSessionMode) -> None:
        canonical = normalize_system_audio_mode(mode)
        if canonical == self.mode:
            return
        previous = self._controller
        if previous is not None:
            previous.stop()
        self.mode = canonical
        self.window.set_mode(canonical)
        self.window.set_partial_text("")
        self._start_mode(canonical)

    def _start_mode(self, mode: SystemAudioSessionMode) -> None:
        controller = build_session_controller(self.settings, mode)
        controller.bind_callbacks(
            on_state_changed=self.window.set_state,
            on_block_ready=self.window.add_block,
            on_partial_text_changed=self.window.set_partial_text,
        )
        self._controller = controller
        controller.start()


def run_system_audio_translation_toggle(
    settings: ToolRunnerSettings | None = None,
) -> str:
    runtime_settings = settings or get_tool_runner_settings()
    socket_path = Path(runtime_settings.system_audio_translation_control_socket_path).expanduser()
    if send_toggle_command(socket_path):
        return "System audio translation toggle signal sent."

    app = ModeAwareSystemAudioTranslationApp(runtime_settings)
    return app.run()


def build_session_controller(
    settings: ToolRunnerSettings,
    mode: SystemAudioSessionMode,
) -> SessionController:
    if mode == "translate_es_openai_realtime":
        api_key = (
            settings.system_audio_translation_openai_realtime_api_key
            or settings.openai_api_key
        )
        if not api_key:
            raise ToolRunnerConfigurationError(
                "Falta configurar `OPENAI_API_KEY` o `SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_API_KEY`."
            )
        return OpenAIRealtimeTranslationController(
            capture=LinuxParecAudioCapture(
                sample_rate_hz=settings.system_audio_translation_openai_realtime_sample_rate_hz,
                chunk_ms=settings.system_audio_translation_openai_realtime_chunk_ms,
            ),
            session_logger=TranscriptSessionLogger(
                logs_dir=Path(settings.system_audio_translation_logs_dir).expanduser()
            ),
            api_key=api_key,
            base_url=settings.system_audio_translation_openai_realtime_base_url
            or settings.openai_base_url,
            model=settings.system_audio_translation_openai_realtime_model,
            source_language=settings.system_audio_translation_source_language,
            target_language=settings.system_audio_translation_target_language,
            reconnect_backoff_seconds=settings.system_audio_translation_reconnect_backoff_seconds,
            max_pending_audio_chunks=settings.system_audio_translation_pending_segment_limit,
            silence_duration_ms=settings.system_audio_translation_openai_realtime_silence_duration_ms,
            prefix_padding_ms=settings.system_audio_translation_openai_realtime_prefix_padding_ms,
            vad_threshold=settings.system_audio_translation_openai_realtime_vad_threshold,
            turn_detection_type=settings.system_audio_translation_openai_realtime_turn_detection_type,
            semantic_vad_eagerness=settings.system_audio_translation_openai_realtime_semantic_vad_eagerness,
            interrupt_response=settings.system_audio_translation_openai_realtime_interrupt_response,
            max_output_tokens=settings.system_audio_translation_openai_realtime_max_output_tokens,
            translate_completed_transcripts=(
                settings.system_audio_translation_openai_realtime_translate_completed_transcripts
            ),
            text_translation_model=(
                settings.system_audio_translation_openai_realtime_text_translation_model
            ),
        )

    transcription_base_url = (
        settings.system_audio_translation_transcription_base_url or settings.litellm_proxy_url
    )
    transcription_api_key = (
        settings.system_audio_translation_transcription_api_key or settings.litellm_virtual_key
    )
    if not transcription_base_url or not transcription_api_key:
        raise ToolRunnerConfigurationError(
            "Falta configurar el backend remoto de transcripcion de audio. Revisa `.env`."
        )

    translation_base_url = settings.litellm_proxy_url
    translation_api_key = settings.litellm_virtual_key
    translation_model = None
    if translation_base_url and translation_api_key:
        translation_model = _require_translation_model(settings)

    return SystemAudioTranslationController(
        capture=LinuxParecAudioCapture(
            sample_rate_hz=settings.system_audio_translation_sample_rate_hz,
            chunk_ms=settings.system_audio_translation_chunk_ms,
        ),
        provider=ChunkedAudioTranslationProvider(
            transcription_base_url=transcription_base_url,
            transcription_api_key=transcription_api_key,
            transcription_model=settings.system_audio_translation_transcription_model,
            inference_client=LocalInferenceClient(settings),
            translation_base_url=translation_base_url,
            translation_api_key=translation_api_key,
            translation_model=translation_model,
            timeout_seconds=max(settings.local_inference_api_timeout_seconds, 60),
        ),
        session_logger=TranscriptSessionLogger(
            logs_dir=Path(settings.system_audio_translation_logs_dir).expanduser()
        ),
        source_language=settings.system_audio_translation_source_language,
        target_language=settings.system_audio_translation_target_language,
        sample_rate_hz=settings.system_audio_translation_sample_rate_hz,
        segment_seconds=settings.system_audio_translation_segment_seconds,
        overlap_seconds=settings.system_audio_translation_overlap_seconds,
        pending_segment_limit=settings.system_audio_translation_pending_segment_limit,
        reconnect_backoff_seconds=settings.system_audio_translation_reconnect_backoff_seconds,
        session_mode=mode,
    )


def _require_translation_model(settings: ToolRunnerSettings) -> str:
    model = getattr(settings, "litellm_model", None)
    if not model:
        raise ToolRunnerConfigurationError(
            "Falta `LITELLM_MODEL` para traducir texto directamente desde el backend remoto."
        )
    return model
