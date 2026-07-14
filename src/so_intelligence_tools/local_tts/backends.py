from __future__ import annotations

import sys


LOCAL_TTS_BACKENDS = {"auto", "piper", "chatterbox", "none"}
LOCAL_TTS_DEFAULT_URLS = {
    "piper": "http://127.0.0.1:9010",
    "chatterbox": "http://127.0.0.1:9011",
}


def resolve_local_tts_backend(
    configured_backend: str = "auto",
    *,
    platform_name: str | None = None,
) -> str:
    backend = configured_backend.strip().lower()
    if backend not in LOCAL_TTS_BACKENDS:
        choices = ", ".join(sorted(LOCAL_TTS_BACKENDS))
        raise ValueError(
            f"Unsupported local TTS backend {backend!r}; choose {choices}."
        )
    if backend != "auto":
        return backend

    platform_value = (platform_name or sys.platform).lower()
    if platform_value.startswith("linux"):
        return "piper"
    if platform_value.startswith("win"):
        return "chatterbox"
    return "none"


def resolve_local_tts_base_url(
    configured_backend: str = "auto",
    *,
    explicit_base_url: str | None = None,
    platform_name: str | None = None,
) -> str | None:
    if explicit_base_url and explicit_base_url.strip():
        return explicit_base_url.strip().rstrip("/")
    backend = resolve_local_tts_backend(
        configured_backend,
        platform_name=platform_name,
    )
    return LOCAL_TTS_DEFAULT_URLS.get(backend)
