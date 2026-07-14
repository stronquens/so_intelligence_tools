from __future__ import annotations

from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.system_audio_translation import app as system_audio_app


class FakeWindow:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.voice_states: list[tuple[bool, str]] = []
        self.voice_outputs: list[tuple[int, int]] = []

    def set_voice_translation_state(
        self, active: bool, message: str, state: str | None = None
    ) -> None:
        _ = state
        self.voice_states.append((active, message))

    def set_voice_translation_output(self, chunks: int, byte_count: int) -> None:
        self.voice_outputs.append((chunks, byte_count))

    def set_audio_level(self, level: float, source: str = "system") -> None:
        _ = (level, source)

    def close_from_controller(self) -> None:
        return None

    def set_mode(self, mode):  # noqa: ANN001
        return None

    def set_partial_text(self, update):  # noqa: ANN001
        return None

    def set_state(self, state, message):  # noqa: ANN001
        self.state = (state, message)

    def add_block(self, block):  # noqa: ANN001
        return None

    def set_session_config(self, source_language, target_language, languages):  # noqa: ANN001
        self.session_config = (source_language, target_language, languages)

    def run(self) -> None:
        return None


class FakeVoiceTranslationPipeline:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.translation_started = False
        self.translation_stopped = False
        self.monitor_source_name = "so_ai_test.monitor"
        self.virtual_source_name = "so_ai_test"
        self.on_audio_level = None
        self.on_translation_state = None
        self.on_translation_output = None

    def start(self) -> None:
        self.started = True

    @property
    def translation_active(self) -> bool:
        return self.translation_started and not self.translation_stopped

    def start_translation(self) -> None:
        self.translation_started = True
        self.translation_stopped = False
        if self.on_translation_state is not None:
            self.on_translation_state("active", "Traduciendo tu voz en tiempo real…")

    def stop_translation(self) -> None:
        self.translation_stopped = True

    def stop(self) -> None:
        self.stopped = True


class FakeSessionController:
    state = "inactive"

    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def bind_callbacks(self, **callbacks) -> None:
        self.callbacks = callbacks

    def start(self) -> None:
        self.started = True

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def reset(self) -> None:
        return None

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
        "Micrófono virtual activo en passthrough: selecciona so_ai_test como micrófono",
    )

    app.toggle_voice_translation()
    assert fake_pipeline.translation_started is True
    assert app.window.voice_states[-1] == (
        True,
        "Traduciendo tu voz en tiempo real… Selecciona so_ai_test como micrófono en la videollamada.",
    )
    assert fake_pipeline.on_translation_output is not None
    fake_pipeline.on_translation_output(25, 96000)
    assert app.window.voice_outputs == [(25, 96000)]

    app.toggle_voice_translation()
    assert fake_pipeline.translation_stopped is True
    assert app.window.voice_states[-1] == (
        False,
        "Micrófono virtual activo en passthrough: selecciona so_ai_test como micrófono",
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


def test_system_audio_app_restarts_controller_with_selected_languages(monkeypatch):
    controllers: list[FakeSessionController] = []
    calls: list[tuple[str, str]] = []

    def build_controller(settings, mode, *, source_language, target_language):  # noqa: ANN001
        _ = (settings, mode)
        calls.append((source_language, target_language))
        controller = FakeSessionController()
        controllers.append(controller)
        return controller

    monkeypatch.setattr(system_audio_app, "SystemAudioTranslationWindow", FakeWindow)
    monkeypatch.setattr(system_audio_app, "build_session_controller", build_controller)
    app = system_audio_app.ModeAwareSystemAudioTranslationApp(
        ToolRunnerSettings(_env_file=None)
    )

    app._start_mode(app.mode)
    app.change_languages("en", "fr")

    assert calls == [("auto", "es"), ("en", "fr")]
    assert controllers[0].stopped is True
    assert controllers[1].started is True
    assert app.window.session_config[:2] == ("en", "fr")
