from __future__ import annotations

from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.voice_translation_virtual_microphone.pipeline import (
    VoiceTranslationVirtualMicrophonePipeline,
)
from so_intelligence_tools.system_audio_translation.session import TranscriptSessionLogger


class FakeVirtualMicrophone:
    monitor_source_name = "so_ai_test.monitor"
    virtual_source_name = "so_ai_test"

    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


class FakePassthrough:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.volumes: list[float] = []
        self.volume = 0.0

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def set_volume(self, volume: float) -> None:
        self.volume = volume
        self.volumes.append(volume)


class FakeTranslationController:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


class FakeDebugRecorder:
    recording_path = "/tmp/final-output.wav"

    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> str:
        self.started = True
        return self.recording_path

    def stop(self) -> str:
        self.stopped = True
        return self.recording_path


def test_tool_runner_settings_use_safe_voice_translation_defaults():
    settings = ToolRunnerSettings(_env_file=None)

    assert settings.voice_translation_passthrough_volume == 1.0
    assert settings.voice_translation_ducked_passthrough_volume == 0.03
    assert settings.voice_translation_max_ducked_passthrough_volume == 0.12
    assert settings.voice_translation_output_volume == 0.75


def test_pipeline_ducks_passthrough_while_translation_is_active():
    virtual_microphone = FakeVirtualMicrophone()
    passthrough = FakePassthrough()
    translation_controller = FakeTranslationController()
    pipeline = VoiceTranslationVirtualMicrophonePipeline(
        virtual_microphone=virtual_microphone,  # type: ignore[arg-type]
        passthrough=passthrough,  # type: ignore[arg-type]
        translation_controller_factory=lambda _virtual_microphone: translation_controller,  # type: ignore[arg-type]
        passthrough_volume=1.0,
        ducked_passthrough_volume=0.2,
        max_ducked_passthrough_volume=0.5,
    )

    pipeline.start()
    pipeline.start_translation()
    pipeline.stop_translation()
    pipeline.stop()

    assert virtual_microphone.started is True
    assert translation_controller.started is True
    assert translation_controller.stopped is True
    assert passthrough.volumes == [1.0, 0.2, 1.0, 1.0]
    assert passthrough.stopped is True
    assert virtual_microphone.stopped is True


def test_pipeline_caps_unsafe_ducked_passthrough_volume(tmp_path):
    virtual_microphone = FakeVirtualMicrophone()
    passthrough = FakePassthrough()
    translation_controller = FakeTranslationController()
    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    pipeline = VoiceTranslationVirtualMicrophonePipeline(
        virtual_microphone=virtual_microphone,  # type: ignore[arg-type]
        passthrough=passthrough,  # type: ignore[arg-type]
        translation_controller_factory=lambda _virtual_microphone: translation_controller,  # type: ignore[arg-type]
        ducked_passthrough_volume=0.6,
        max_ducked_passthrough_volume=0.12,
        session_logger=logger,
    )

    pipeline.start_translation()
    pipeline.stop()

    assert passthrough.volumes[0:2] == [1.0, 0.12]
    assert pipeline.last_log_path is not None
    content = pipeline.last_log_path.read_text(encoding="utf-8")
    assert '"requested_ducked_passthrough_volume": 0.6' in content
    assert '"applied_ducked_passthrough_volume": 0.12' in content


def test_pipeline_writes_detailed_session_log(tmp_path):
    virtual_microphone = FakeVirtualMicrophone()
    passthrough = FakePassthrough()
    translation_controller = FakeTranslationController()
    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    pipeline = VoiceTranslationVirtualMicrophonePipeline(
        virtual_microphone=virtual_microphone,  # type: ignore[arg-type]
        passthrough=passthrough,  # type: ignore[arg-type]
        translation_controller_factory=lambda _virtual_microphone: translation_controller,  # type: ignore[arg-type]
        session_logger=logger,
    )

    pipeline.start()
    pipeline._record_passthrough_audio(1, 3840, 1.0)
    pipeline.start_translation()
    pipeline.stop()

    assert pipeline.last_log_path is not None
    content = pipeline.last_log_path.read_text(encoding="utf-8")
    assert '"type": "voice_pipeline_started"' in content
    assert '"type": "passthrough_audio_forwarded"' in content
    assert '"type": "voice_translation_started"' in content
    assert '"type": "voice_pipeline_stopped"' in content


def test_pipeline_records_final_virtual_microphone_output_in_debug_mode(tmp_path):
    virtual_microphone = FakeVirtualMicrophone()
    passthrough = FakePassthrough()
    debug_recorder = FakeDebugRecorder()
    logger = TranscriptSessionLogger(logs_dir=tmp_path)
    pipeline = VoiceTranslationVirtualMicrophonePipeline(
        virtual_microphone=virtual_microphone,  # type: ignore[arg-type]
        passthrough=passthrough,  # type: ignore[arg-type]
        translation_controller_factory=lambda _virtual_microphone: FakeTranslationController(),  # type: ignore[arg-type]
        session_logger=logger,
        debug_recorder=debug_recorder,  # type: ignore[arg-type]
    )

    pipeline.start()
    pipeline.stop()

    assert debug_recorder.started is True
    assert debug_recorder.stopped is True
    assert pipeline.last_log_path is not None
    content = pipeline.last_log_path.read_text(encoding="utf-8")
    assert '"type": "debug_recording_started"' in content
    assert '"type": "debug_recording_stopped"' in content
    assert "/tmp/final-output.wav" in content
