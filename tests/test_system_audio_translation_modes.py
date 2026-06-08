from __future__ import annotations

from so_intelligence_tools.system_audio_translation.modes import (
    normalize_system_audio_mode,
)


def test_normalize_system_audio_mode_maps_legacy_value():
    assert normalize_system_audio_mode("translate_es") == "translate_es_chunked"


def test_normalize_system_audio_mode_keeps_realtime_value():
    assert (
        normalize_system_audio_mode("translate_es_openai_realtime")
        == "translate_es_openai_realtime"
    )


def test_normalize_system_audio_mode_falls_back_to_chunked():
    assert normalize_system_audio_mode("unknown-mode") == "translate_es_chunked"
