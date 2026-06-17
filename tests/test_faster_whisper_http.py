from __future__ import annotations

import httpx
import pytest

from so_intelligence_tools.domain.errors import ToolRunnerConfigurationError
from so_intelligence_tools.push_to_talk_dictation.faster_whisper_http import (
    FasterWhisperHttpSettings,
    FasterWhisperHttpTranscriber,
    _api_language,
)


def test_faster_whisper_http_transcribes_buffered_pcm_as_wav():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": "large-v3-turbo"}]})
        body = request.read()
        assert request.url.path == "/v1/audio/transcriptions"
        assert b"Content-Type: audio/wav" in body
        assert b"RIFF" in body
        assert b'name="language"' in body
        assert b"\r\nes\r\n" in body
        return httpx.Response(200, json={"text": "paralelepipedo correcto"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    transcriber = FasterWhisperHttpTranscriber(
        FasterWhisperHttpSettings(base_url="http://whisper.local", language="es-ES"),
        http_client=client,
    )

    transcriber.check_ready()
    session = transcriber.start_session()
    assert session.accept_audio((1).to_bytes(2, "little", signed=True)) == []
    events = list(session.finish())

    assert [request.url.path for request in requests] == [
        "/v1/models",
        "/v1/audio/transcriptions",
    ]
    assert len(events) == 1
    assert events[0].kind == "final"
    assert events[0].text == "paralelepipedo correcto"


def test_faster_whisper_http_ready_failure_is_configuration_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    transcriber = FasterWhisperHttpTranscriber(
        FasterWhisperHttpSettings(base_url="http://whisper.local"),
        http_client=client,
    )

    with pytest.raises(ToolRunnerConfigurationError):
        transcriber.check_ready()


def test_api_language_uses_primary_subtag():
    assert _api_language("es-ES") == "es"
    assert _api_language(" auto ") == "auto"
