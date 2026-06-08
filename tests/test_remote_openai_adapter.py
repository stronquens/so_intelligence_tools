from __future__ import annotations

import asyncio

import httpx

from local_inference_api.config import Settings
from local_inference_api.remote_openai_adapter import RemoteOpenAICompatibleAdapter


def make_adapter() -> RemoteOpenAICompatibleAdapter:
    return RemoteOpenAICompatibleAdapter(
        Settings(
            inference_provider="litellm_proxy",
            litellm_proxy_url="https://proxy.test",
            litellm_virtual_key="sk-test",
            litellm_model="provider/model",
            ollama_timeout_seconds=30,
        )
    )


def test_remote_generate_result_maps_openai_chat_completion_shape():
    adapter = make_adapter()

    result = adapter._build_generate_result(
        {
            "model": "provider/model",
            "choices": [
                {
                    "message": {"content": "texto corregido"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 4},
        },
        "off",
    )

    assert result.model == "provider/model"
    assert result.response == "texto corregido"
    assert result.prompt_eval_count == 10
    assert result.eval_count == 4
    assert result.reasoning_strategy_applied == "thinking:off"


def test_remote_status_marks_configured_model_available(monkeypatch):
    adapter = make_adapter()

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            request = httpx.Request("GET", "https://proxy.test/v1/models")
            return httpx.Response(
                200,
                request=request,
                json={"data": [{"id": "provider/model"}, {"id": "another/model"}]},
            )

    monkeypatch.setattr(
        "local_inference_api.remote_openai_adapter.httpx.AsyncClient",
        FakeAsyncClient,
    )

    status = asyncio.run(adapter.status())

    assert status["configured_model"] == "provider/model"
    assert status["configured_model_available"] is True
