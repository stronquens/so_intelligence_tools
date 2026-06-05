from __future__ import annotations

import httpx
import pytest

from so_intelligence_tools.domain.errors import InferenceUnavailableError
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings
from so_intelligence_tools.infrastructure.inference_client import LocalInferenceClient


def make_settings() -> ToolRunnerSettings:
    return ToolRunnerSettings(
        local_inference_api_base_url="http://testserver",
        local_inference_api_timeout_seconds=5,
    )


def test_generate_text_parses_openai_compatible_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/text/generate"
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"content": "texto corregido"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 7},
                "reasoning_mode_requested": "off",
                "reasoning_strategy_applied": "thinking:off",
            },
        )

    client = LocalInferenceClient(
        make_settings(),
        transport=httpx.MockTransport(handler),
    )
    result = client.generate_text(prompt="hola")

    assert result.content == "texto corregido"
    assert result.model == "test-model"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 7


def test_extract_text_from_image_parses_response():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/image/extract-text"
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"content": "Test 123"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 2},
                "reasoning_mode_requested": "off",
                "reasoning_strategy_applied": "thinking:off",
            },
        )

    client = LocalInferenceClient(
        make_settings(),
        transport=httpx.MockTransport(handler),
    )
    result = client.extract_text_from_image(image_bytes=b"fake", prompt="ocr")

    assert result.content == "Test 123"


def test_client_raises_domain_error_on_http_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "backend caido"})

    client = LocalInferenceClient(
        make_settings(),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(InferenceUnavailableError, match="backend caido"):
        client.generate_text(prompt="hola")


def test_client_raises_domain_error_on_invalid_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": True})

    client = LocalInferenceClient(
        make_settings(),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(InferenceUnavailableError, match="respuesta inválida"):
        client.generate_text(prompt="hola")
