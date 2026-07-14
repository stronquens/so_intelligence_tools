from __future__ import annotations

from datetime import datetime
from io import StringIO
import json

from so_intelligence_tools.domain.models import LivePartialUpdate, TranscriptBlock
from so_intelligence_tools.system_audio_translation.desktop_bridge import (
    DesktopTranslationBridgeWindow,
)


def _events(output: StringIO) -> list[dict[str, object]]:
    return [json.loads(line) for line in output.getvalue().splitlines()]


def _build_window(
    *,
    input_text: str = "",
    output: StringIO | None = None,
    calls: list[object] | None = None,
) -> DesktopTranslationBridgeWindow:
    recorded_calls = calls if calls is not None else []
    return DesktopTranslationBridgeWindow(
        title="Translator",
        initial_mode="translate_es_openai_realtime",
        on_pause=lambda: recorded_calls.append("pause"),
        on_resume=lambda: recorded_calls.append("resume"),
        on_reset=lambda: recorded_calls.append("reset"),
        on_close=lambda: recorded_calls.append("stop"),
        on_mode_changed=lambda mode: recorded_calls.append(("mode", mode)),
        on_voice_translation_toggle=lambda: recorded_calls.append("voice"),
        on_languages_changed=lambda source, target: recorded_calls.append(
            ("languages", source, target)
        ),
        input_stream=StringIO(input_text),
        output_stream=output or StringIO(),
    )


def test_desktop_bridge_serializes_session_content() -> None:
    output = StringIO()
    window = _build_window(output=output)

    window.set_state("active", "Escuchando")
    window.set_partial_text(LivePartialUpdate(kind="original", text="Hello"))
    window.set_partial_text(LivePartialUpdate(kind="translation", text="Hola"))
    window.add_block(
        TranscriptBlock(
            timestamp=datetime(2026, 7, 14, 12, 34, 56),
            original_text="Good morning",
            translated_text="Buenos dias",
            speaker_label="A",
        )
    )
    window.set_mode("translate_es_openai_realtime")
    window.set_voice_translation_state(True, "Microfono traducido activo")
    window.set_voice_translation_output(25, 96000)
    window.set_audio_level(0.25, "microphone")
    window.set_session_config(
        "auto",
        "es",
        [{"code": "en", "label": "English"}, {"code": "es", "label": "Spanish"}],
    )

    events = _events(output)
    assert events[0] == {
        "type": "session_state",
        "state": "active",
        "message": "Escuchando",
    }
    assert events[1:3] == [
        {"type": "partial", "kind": "original", "text": "Hello"},
        {"type": "partial", "kind": "translation", "text": "Hola"},
    ]
    assert events[3] == {
        "type": "block",
        "id": "2026-07-14T12:34:56-1",
        "sourceText": "Good morning",
        "translatedText": "Buenos dias",
        "timestamp": "12:34:56",
        "speakerLabel": "A",
    }
    assert events[4:] == [
        {"type": "mode", "mode": "translate_es_openai_realtime"},
        {
            "type": "voice_translation_state",
            "active": True,
            "message": "Microfono traducido activo",
        },
        {
            "type": "voice_translation_output",
            "chunks": 25,
            "bytes": 96000,
        },
        {
            "type": "audio_level",
            "source": "microphone",
            "level": 0.25,
        },
        {
            "type": "session_config",
            "sourceLanguage": "auto",
            "targetLanguage": "es",
            "languages": [
                {"code": "en", "label": "English"},
                {"code": "es", "label": "Spanish"},
            ],
        },
    ]


def test_desktop_bridge_dispatches_supported_commands_and_stops_on_eof() -> None:
    calls: list[object] = []
    commands = "\n".join(
        [
            '{"type":"pause"}',
            '{"type":"resume"}',
            '{"type":"reset"}',
            '{"type":"toggle_voice_translation"}',
            '{"type":"change_mode","mode":"translate_es_chunked"}',
            '{"type":"change_languages","sourceLanguage":"en","targetLanguage":"fr"}',
        ]
    )
    window = _build_window(input_text=f"{commands}\n", calls=calls)

    window.run()

    assert calls == [
        "pause",
        "resume",
        "reset",
        "voice",
        ("mode", "translate_es_chunked"),
        ("languages", "en", "fr"),
        "stop",
    ]


def test_desktop_bridge_reports_invalid_json_and_commands() -> None:
    output = StringIO()
    window = _build_window(
        input_text='not-json\n{"type":"change_mode","mode":"unknown"}\n',
        output=output,
    )

    window.run()

    errors = [event for event in _events(output) if event["type"] == "error"]
    assert len(errors) == 2
    assert "JSON" in str(errors[0]["message"])
    assert "Modo" in str(errors[1]["message"])
