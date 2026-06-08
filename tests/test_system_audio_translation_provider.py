from __future__ import annotations

import httpx

from so_intelligence_tools.domain.models import TextGenerationResult
from so_intelligence_tools.system_audio_translation.provider import (
    ChunkedAudioTranslationProvider,
    pcm16_to_wav_bytes,
)


class FakeInferenceClient:
    def generate_text(self, **kwargs) -> TextGenerationResult:
        prompt = kwargs["prompt"]
        transcript = prompt.split("\n\n", 1)[1]
        return TextGenerationResult(content=f"ES:{transcript}", model="fake-text")


def test_pcm16_to_wav_bytes_creates_valid_riff_header():
    wav_bytes = pcm16_to_wav_bytes(pcm_bytes=b"\x00\x00\x01\x00", sample_rate_hz=16000)

    assert wav_bytes[:4] == b"RIFF"
    assert b"WAVE" in wav_bytes[:16]


def test_chunked_audio_translation_provider_transcribes_and_translates():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/audio/transcriptions"
        return httpx.Response(200, json={"text": "hello world"})

    provider = ChunkedAudioTranslationProvider(
        transcription_base_url="http://proxy",
        transcription_api_key="secret",
        transcription_model="whisper-1",
        inference_client=FakeInferenceClient(),
        transport=httpx.MockTransport(handler),
    )

    original, translated = provider.transcribe_and_translate(
        pcm_bytes=b"\x00\x00" * 160,
        sample_rate_hz=16000,
        source_language="en",
        target_language="es",
    )

    assert original == "hello world"
    assert translated == "ES:hello world"
