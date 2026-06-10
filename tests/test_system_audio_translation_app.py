from __future__ import annotations

from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.system_audio_translation import app as system_audio_app


class FakeWindow:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.voice_states: list[tuple[bool, str]] = []

    def set_voice_translation_state(self, active: bool, message: str) -> None:
        self.voice_states.append((active, message))

    def close_from_controller(self) -> None:
        return None

    def set_mode(self, mode):  # noqa: ANN001
        return None

    def set_partial_text(self, update):  # noqa: ANN001
        return None

    def run(self) -> None:
        return None


class FakeVoiceTranslationPipeline:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.translation_started = False
        self.translation_stopped = False
        self.monitor_source_name = "so_ai_test.monitor"

    def start(self) -> None:
        self.started = True

    @property
    def translation_active(self) -> bool:
        return self.translation_started and not self.translation_stopped

    def start_translation(self) -> None:
        self.translation_started = True
        self.translation_stopped = False

    def stop_translation(self) -> None:
        self.translation_stopped = True

    def stop(self) -> None:
        self.stopped = True


def test_system_audio_app_toggles_voice_translation_button(monkeypatch):
    fake_pipeline = FakeVoiceTranslationPipeline()

    monkeypatch.setattr(system_audio_app, "SystemAudioTranslationWindow", FakeWindow)
    monkeypatch.setattr(
        system_audio_app,
        "build_voice_translation_pipeline",
        lambda settings: fake_pipeline,
    )

    app = system_audio_app.ModeAwareSystemAudioTranslationApp(
        ToolRunnerSettings(_env_file=None)
    )

    app.start_voice_passthrough()
    assert fake_pipeline.started is True
    assert app.window.voice_states[-1] == (
        False,
        "Micrófono virtual activo en passthrough: selecciona so_ai_test.monitor como micrófono",
    )

    app.toggle_voice_translation()
    assert fake_pipeline.translation_started is True
    assert app.window.voice_states[-1] == (
        True,
        "Traducción activa: voz original bajada y voz inglesa superpuesta en so_ai_test.monitor",
    )

    app.toggle_voice_translation()
    assert fake_pipeline.translation_stopped is True
    assert app.window.voice_states[-1] == (
        False,
        "Micrófono virtual activo en passthrough: selecciona so_ai_test.monitor como micrófono",
    )


def test_system_audio_app_stops_voice_translation_on_close(monkeypatch):
    fake_pipeline = FakeVoiceTranslationPipeline()

    monkeypatch.setattr(system_audio_app, "SystemAudioTranslationWindow", FakeWindow)
    monkeypatch.setattr(
        system_audio_app,
        "build_voice_translation_pipeline",
        lambda settings: fake_pipeline,
    )

    app = system_audio_app.ModeAwareSystemAudioTranslationApp(
        ToolRunnerSettings(_env_file=None)
    )
    app.start_voice_passthrough()
    app.toggle_voice_translation()

    app.stop()

    assert fake_pipeline.stopped is True
    assert app.window.voice_states[-1] == (False, "Micrófono virtual: apagado")
