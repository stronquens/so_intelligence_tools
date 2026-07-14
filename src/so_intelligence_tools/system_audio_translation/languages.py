from __future__ import annotations

from typing import Final


SUPPORTED_SYSTEM_AUDIO_LANGUAGES: Final[dict[str, str]] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ca": "Catalan",
    "gl": "Galician",
    "eu": "Basque",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "uk": "Ukrainian",
    "ar": "Arabic",
    "hi": "Hindi",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
}


def language_catalog() -> list[dict[str, str]]:
    return [
        {"code": code, "label": label}
        for code, label in SUPPORTED_SYSTEM_AUDIO_LANGUAGES.items()
    ]


def validate_language_pair(source_language: str, target_language: str) -> None:
    if source_language != "auto" and source_language not in SUPPORTED_SYSTEM_AUDIO_LANGUAGES:
        raise ValueError(f"Idioma de origen no soportado: {source_language}")
    if target_language not in SUPPORTED_SYSTEM_AUDIO_LANGUAGES:
        raise ValueError(f"Idioma de destino no soportado: {target_language}")


def language_name(code: str) -> str:
    return SUPPORTED_SYSTEM_AUDIO_LANGUAGES.get(code, code)
