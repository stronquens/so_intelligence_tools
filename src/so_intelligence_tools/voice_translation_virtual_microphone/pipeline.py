from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from so_intelligence_tools.voice_translation_virtual_microphone.audio import (
    MicrophonePassthroughToVirtualMicrophone,
    PulseAudioMonitorWavRecorder,
    PulseAudioVirtualMicrophone,
)
from so_intelligence_tools.voice_translation_virtual_microphone.openai_realtime import (
    OpenAIRealtimeVoiceTranslationController,
)
from so_intelligence_tools.system_audio_translation.session import TranscriptSessionLogger


@dataclass(slots=True)
class VoiceTranslationVirtualMicrophonePipeline:
    virtual_microphone: PulseAudioVirtualMicrophone
    passthrough: MicrophonePassthroughToVirtualMicrophone
    translation_controller_factory: Callable[
        [PulseAudioVirtualMicrophone],
        OpenAIRealtimeVoiceTranslationController,
    ]
    passthrough_volume: float = 1.0
    ducked_passthrough_volume: float = 0.03
    max_ducked_passthrough_volume: float = 0.12
    session_logger: TranscriptSessionLogger | None = None
    debug_recorder: PulseAudioMonitorWavRecorder | None = None
    _translation_controller: OpenAIRealtimeVoiceTranslationController | None = field(
        init=False,
        default=None,
    )
    _started: bool = field(init=False, default=False)
    _last_logged_passthrough_chunk: int = field(init=False, default=0)
    last_log_path: Path | None = field(init=False, default=None)

    @property
    def monitor_source_name(self) -> str:
        return self.virtual_microphone.monitor_source_name

    @property
    def virtual_source_name(self) -> str:
        return self.virtual_microphone.virtual_source_name

    @property
    def translation_active(self) -> bool:
        return self._translation_controller is not None

    def start(self) -> None:
        if self._started:
            return
        self._record_event(
            "voice_pipeline_starting",
            virtual_source=self.virtual_source_name,
            monitor_source=self.monitor_source_name,
            passthrough_volume=self.passthrough_volume,
            ducked_passthrough_volume=self.ducked_passthrough_volume,
            max_ducked_passthrough_volume=self.max_ducked_passthrough_volume,
        )
        self.virtual_microphone.start()
        if self.debug_recorder is not None:
            recording_path = self.debug_recorder.start()
            self._record_event(
                "debug_recording_started",
                recording_path=str(recording_path),
                virtual_source=self.virtual_source_name,
                monitor_source=self.monitor_source_name,
            )
        self.passthrough.on_audio_forwarded = self._record_passthrough_audio
        self.passthrough.set_volume(self.passthrough_volume)
        self.passthrough.start()
        self._record_event(
            "voice_pipeline_started",
            virtual_source=self.virtual_source_name,
            monitor_source=self.monitor_source_name,
        )
        self._started = True

    def start_translation(self) -> None:
        if self._translation_controller is not None:
            return
        self.start()
        controller = self.translation_controller_factory(self.virtual_microphone)
        applied_ducked_volume = self._safe_ducked_passthrough_volume()
        self._record_event(
            "voice_translation_starting",
            previous_passthrough_volume=self.passthrough.volume,
            requested_ducked_passthrough_volume=self.ducked_passthrough_volume,
            applied_ducked_passthrough_volume=applied_ducked_volume,
            max_ducked_passthrough_volume=self.max_ducked_passthrough_volume,
        )
        self.passthrough.set_volume(applied_ducked_volume)
        try:
            controller.start()
        except Exception:
            self.passthrough.set_volume(self.passthrough_volume)
            self._record_event(
                "voice_translation_start_failed",
                restored_passthrough_volume=self.passthrough_volume,
            )
            raise
        self._translation_controller = controller
        self._record_event(
            "voice_translation_started",
            passthrough_volume=applied_ducked_volume,
            requested_ducked_passthrough_volume=self.ducked_passthrough_volume,
        )

    def stop_translation(self) -> None:
        controller = self._translation_controller
        if controller is not None:
            self._record_event("voice_translation_stopping")
            controller.stop()
            self._translation_controller = None
        self.passthrough.set_volume(self.passthrough_volume)
        self._record_event(
            "voice_translation_stopped",
            passthrough_volume=self.passthrough_volume,
        )

    def stop(self) -> None:
        self._record_event("voice_pipeline_stopping")
        self.stop_translation()
        self.passthrough.stop()
        if self.debug_recorder is not None:
            recording_path = self.debug_recorder.stop()
            self._record_event(
                "debug_recording_stopped",
                recording_path=str(recording_path) if recording_path is not None else None,
                virtual_source=self.virtual_source_name,
                monitor_source=self.monitor_source_name,
            )
        self.virtual_microphone.stop()
        self._record_event("voice_pipeline_stopped")
        self._started = False
        if self.session_logger is not None:
            self.last_log_path = self.session_logger.write_session([])

    def _record_event(self, event_type: str, **payload: object) -> None:
        if self.session_logger is not None:
            self.session_logger.record_event(event_type, **payload)

    def _safe_ducked_passthrough_volume(self) -> float:
        return min(
            max(self.ducked_passthrough_volume, 0.0),
            max(self.max_ducked_passthrough_volume, 0.0),
        )

    def _record_passthrough_audio(
        self,
        chunks: int,
        bytes_forwarded: int,
        volume: float,
    ) -> None:
        if chunks == 1 or chunks - self._last_logged_passthrough_chunk >= 50:
            self._last_logged_passthrough_chunk = chunks
            self._record_event(
                "passthrough_audio_forwarded",
                chunks=chunks,
                bytes=bytes_forwarded,
                volume=volume,
                virtual_source=self.virtual_source_name,
                monitor_source=self.monitor_source_name,
            )
