from __future__ import annotations

from so_intelligence_tools.domain.models import SystemAudioSessionMode


SYSTEM_AUDIO_MODE_LABELS: dict[SystemAudioSessionMode, str] = {
    "translate_es_chunked": "Traducir a espanol (chunked)",
    "translate_es_openai_realtime": "Traducir a espanol (OpenAI realtime)",
}

_LEGACY_MODE_ALIASES: dict[str, SystemAudioSessionMode] = {
    "translate_es": "translate_es_chunked",
}


def normalize_system_audio_mode(mode: str | None) -> SystemAudioSessionMode:
    if mode is None:
        return "translate_es_chunked"
    normalized = mode.strip()
    if normalized in SYSTEM_AUDIO_MODE_LABELS:
        return normalized  # type: ignore[return-value]
    if normalized in _LEGACY_MODE_ALIASES:
        return _LEGACY_MODE_ALIASES[normalized]
    return "translate_es_chunked"
