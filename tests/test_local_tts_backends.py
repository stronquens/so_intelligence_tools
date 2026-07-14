from __future__ import annotations

import pytest

from so_intelligence_tools.local_tts.backends import (
    resolve_local_tts_backend,
    resolve_local_tts_base_url,
)


@pytest.mark.parametrize(
    ("platform_name", "expected"),
    [("linux", "piper"), ("linux2", "piper"), ("win32", "chatterbox")],
)
def test_auto_backend_uses_platform_default(platform_name: str, expected: str):
    assert resolve_local_tts_backend("auto", platform_name=platform_name) == expected


@pytest.mark.parametrize("backend", ["piper", "chatterbox", "none"])
def test_explicit_backend_overrides_platform(backend: str):
    assert resolve_local_tts_backend(backend, platform_name="linux") == backend
    assert resolve_local_tts_backend(backend, platform_name="win32") == backend


def test_unknown_platform_disables_auto_backend():
    assert resolve_local_tts_backend("auto", platform_name="darwin") == "none"


def test_invalid_backend_is_rejected():
    with pytest.raises(ValueError, match="Unsupported local TTS backend"):
        resolve_local_tts_backend("unknown", platform_name="linux")


def test_backend_default_urls_follow_resolved_platform():
    assert (
        resolve_local_tts_base_url("auto", platform_name="linux")
        == "http://127.0.0.1:9010"
    )
    assert (
        resolve_local_tts_base_url("auto", platform_name="win32")
        == "http://127.0.0.1:9011"
    )


def test_explicit_base_url_wins_over_backend_default():
    assert (
        resolve_local_tts_base_url(
            "piper",
            explicit_base_url="http://tts.example:9999/",
            platform_name="linux",
        )
        == "http://tts.example:9999"
    )
