from __future__ import annotations

from pathlib import Path
import signal
import threading

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings, get_tool_runner_settings
from so_intelligence_tools.system_audio_translation.session import (
    ToggleSocketServer,
    TranscriptSessionLogger,
    send_toggle_command,
)
from so_intelligence_tools.voice_translation_virtual_microphone.audio import (
    LinuxMicrophoneAudioCapture,
    MicrophonePassthroughToVirtualMicrophone,
    PulseAudioMonitorWavRecorder,
    PulseAudioPcmPlayback,
    PulseAudioVirtualMicrophone,
)
from so_intelligence_tools.voice_translation_virtual_microphone.openai_realtime import (
    OpenAIRealtimeVoiceTranslationController,
)
from so_intelligence_tools.voice_translation_virtual_microphone.pipeline import (
    VoiceTranslationVirtualMicrophonePipeline,
)


def run_voice_translation_virtual_microphone_toggle(
    settings: ToolRunnerSettings | None = None,
) -> str:
    runtime_settings = settings or get_tool_runner_settings()
    socket_path = Path(runtime_settings.voice_translation_control_socket_path).expanduser()
    if send_toggle_command(socket_path):
        return "Voice translation virtual microphone toggle signal sent."

    app = VoiceTranslationVirtualMicrophoneApp(runtime_settings)
    return app.run()


class VoiceTranslationVirtualMicrophoneApp:
    def __init__(self, settings: ToolRunnerSettings) -> None:
        self.settings = settings
        self._stop_event = threading.Event()
        self._socket_path = Path(settings.voice_translation_control_socket_path).expanduser()
        self._toggle_server = ToggleSocketServer(
            socket_path=self._socket_path,
            on_toggle=self.stop,
        )
        self._pipeline = build_voice_translation_pipeline(settings)

    def run(self) -> str:
        previous_sigint = signal.getsignal(signal.SIGINT)
        previous_sigterm = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        self._toggle_server.start()
        try:
            self._pipeline.start()
            self._pipeline.start_translation()
            self._stop_event.wait()
        finally:
            self._pipeline.stop()
            self._toggle_server.stop()
            signal.signal(signal.SIGINT, previous_sigint)
            signal.signal(signal.SIGTERM, previous_sigterm)
        return "Voice translation virtual microphone session finished."

    def stop(self) -> None:
        self._stop_event.set()

    def _handle_signal(self, *_args: object) -> None:
        self.stop()


def build_voice_translation_controller(
    settings: ToolRunnerSettings,
    *,
    virtual_microphone: PulseAudioVirtualMicrophone | None = None,
    owns_virtual_microphone: bool = True,
    session_logger: TranscriptSessionLogger | None = None,
    write_session_log_on_stop: bool = True,
) -> OpenAIRealtimeVoiceTranslationController:
    api_key = settings.voice_translation_openai_api_key or settings.openai_api_key
    if not api_key:
        raise ToolRunnerConfigurationError(
            "Falta configurar `OPENAI_API_KEY` o `VOICE_TRANSLATION_OPENAI_API_KEY`."
        )
    sample_rate_hz = settings.voice_translation_sample_rate_hz
    output_virtual_microphone = virtual_microphone or PulseAudioVirtualMicrophone(
        sink_name=settings.voice_translation_virtual_sink_name,
        sample_rate_hz=sample_rate_hz,
    )
    return OpenAIRealtimeVoiceTranslationController(
        capture=LinuxMicrophoneAudioCapture(
            sample_rate_hz=sample_rate_hz,
            chunk_ms=settings.voice_translation_chunk_ms,
            source=settings.voice_translation_physical_source,
        ),
        virtual_microphone=output_virtual_microphone,
        session_logger=session_logger
        or TranscriptSessionLogger(
            logs_dir=Path(settings.voice_translation_logs_dir).expanduser()
        ),
        api_key=api_key,
        base_url=settings.voice_translation_openai_base_url or settings.openai_base_url,
        model=settings.voice_translation_openai_model,
        source_language=settings.voice_translation_source_language,
        target_language=settings.voice_translation_target_language,
        voice=settings.voice_translation_voice,
        reconnect_backoff_seconds=settings.voice_translation_reconnect_backoff_seconds,
        max_pending_audio_chunks=settings.voice_translation_pending_audio_chunks,
        silence_duration_ms=settings.voice_translation_silence_duration_ms,
        prefix_padding_ms=settings.voice_translation_prefix_padding_ms,
        vad_threshold=settings.voice_translation_vad_threshold,
        output_volume=settings.voice_translation_output_volume,
        owns_virtual_microphone=owns_virtual_microphone,
        write_session_log_on_stop=write_session_log_on_stop,
    )


def build_voice_translation_pipeline(
    settings: ToolRunnerSettings,
) -> VoiceTranslationVirtualMicrophonePipeline:
    sample_rate_hz = settings.voice_translation_sample_rate_hz
    session_logger = TranscriptSessionLogger(
        logs_dir=Path(settings.voice_translation_logs_dir).expanduser()
    )
    virtual_microphone = PulseAudioVirtualMicrophone(
        sink_name=settings.voice_translation_virtual_sink_name,
        sample_rate_hz=sample_rate_hz,
    )
    passthrough = MicrophonePassthroughToVirtualMicrophone(
        capture=LinuxMicrophoneAudioCapture(
            sample_rate_hz=sample_rate_hz,
            chunk_ms=settings.voice_translation_chunk_ms,
            source=settings.voice_translation_physical_source,
        ),
        playback=PulseAudioPcmPlayback(
            sink_name=virtual_microphone.playback_sink_name,
            sample_rate_hz=sample_rate_hz,
        ),
        volume=settings.voice_translation_passthrough_volume,
    )
    debug_recorder = None
    if settings.voice_translation_debug_recording_enabled:
        debug_recorder = PulseAudioMonitorWavRecorder(
            monitor_source_name=virtual_microphone.monitor_source_name,
            sample_rate_hz=sample_rate_hz,
            recordings_dir=Path(settings.voice_translation_debug_recordings_dir).expanduser(),
        )
    return VoiceTranslationVirtualMicrophonePipeline(
        virtual_microphone=virtual_microphone,
        passthrough=passthrough,
        translation_controller_factory=lambda shared_virtual_microphone: build_voice_translation_controller(
            settings,
            virtual_microphone=shared_virtual_microphone,
            owns_virtual_microphone=False,
            session_logger=session_logger,
            write_session_log_on_stop=False,
        ),
        passthrough_volume=settings.voice_translation_passthrough_volume,
        ducked_passthrough_volume=settings.voice_translation_ducked_passthrough_volume,
        max_ducked_passthrough_volume=(
            settings.voice_translation_max_ducked_passthrough_volume
        ),
        session_logger=session_logger,
        debug_recorder=debug_recorder,
    )
