from __future__ import annotations

import asyncio

import httpx

from local_inference_api.config import Settings
from local_inference_api.ollama_adapter import OllamaAdapter, OllamaRuntimeError


def make_adapter() -> OllamaAdapter:
    return OllamaAdapter(
        Settings(
            ollama_base_url="http://ollama.test:11434",
            ollama_model="hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL",
            ollama_keep_alive="10m",
            ollama_timeout_seconds=30,
        )
    )


def test_build_system_prompt_keeps_thinking_off_for_off_and_low():
    adapter = make_adapter()

    assert adapter._build_system_prompt(None, "off") is None
    assert adapter._build_system_prompt("Responde en español", "low") == "Responde en español"


def test_build_system_prompt_enables_thinking_for_medium_and_high():
    adapter = make_adapter()

    assert adapter._build_system_prompt(None, "medium") == "<|think|>"
    assert (
        adapter._build_system_prompt("Responde en español", "high")
        == "<|think|>\nResponde en español"
    )


def test_build_generate_result_maps_reasoning_mode_to_strategy():
    adapter = make_adapter()

    result = adapter._build_generate_result(
        {
            "model": "test-model",
            "response": "respuesta",
            "prompt_eval_count": 4,
            "eval_count": 2,
            "done_reason": "stop",
        },
        "medium",
    )

    assert result.model == "test-model"
    assert result.response == "respuesta"
    assert result.prompt_eval_count == 4
    assert result.eval_count == 2
    assert result.reasoning_strategy_applied == "thinking:on"


def test_post_generate_maps_connection_errors_to_runtime_error(monkeypatch):
    adapter = make_adapter()

    class FailingAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.ConnectError("connect failed")

    monkeypatch.setattr("local_inference_api.ollama_adapter.httpx.AsyncClient", FailingAsyncClient)

    try:
        asyncio.run(adapter._post_generate({"model": "x"}))
    except OllamaRuntimeError as exc:
        assert "Levanta el runtime local" in str(exc)
    else:
        raise AssertionError("Expected OllamaRuntimeError")


def test_post_generate_maps_status_errors_to_runtime_error(monkeypatch):
    adapter = make_adapter()
    request = httpx.Request("POST", "http://ollama.test/api/generate")
    response = httpx.Response(500, request=request, text="internal error")

    class ErrorResponseAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            raise httpx.HTTPStatusError("boom", request=request, response=response)

    monkeypatch.setattr(
        "local_inference_api.ollama_adapter.httpx.AsyncClient", ErrorResponseAsyncClient
    )

    try:
        asyncio.run(adapter._post_generate({"model": "x"}))
    except OllamaRuntimeError as exc:
        assert "internal error" in str(exc)
    else:
        raise AssertionError("Expected OllamaRuntimeError")
