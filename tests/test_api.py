from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi.testclient import TestClient

from local_inference_api.config import Settings
from local_inference_api.main import app
from local_inference_api.ollama_adapter import OllamaRuntimeError


@dataclass
class FakeGenerateResult:
    model: str = "test-model"
    response: str = "respuesta"
    prompt_eval_count: int = 10
    eval_count: int = 5
    done_reason: str = "stop"
    reasoning_strategy_applied: str = "thinking:off"


class FakeAdapter:
    def __init__(
        self,
        *,
        status_result: dict[str, Any] | None = None,
        status_error: Exception | None = None,
        text_result: FakeGenerateResult | None = None,
        text_error: Exception | None = None,
        image_result: FakeGenerateResult | None = None,
        image_error: Exception | None = None,
    ) -> None:
        self.status_result = status_result
        self.status_error = status_error
        self.text_result = text_result or FakeGenerateResult()
        self.text_error = text_error
        self.image_result = image_result or FakeGenerateResult(response="texto extraido")
        self.image_error = image_error
        self.last_text_request: dict[str, Any] | None = None
        self.last_image_request: dict[str, Any] | None = None

    async def status(self) -> dict[str, Any]:
        if self.status_error:
            raise self.status_error
        return self.status_result or {
            "ollama_version": "0.30.5",
            "configured_model": "test-model",
            "configured_model_available": True,
        }

    async def generate_text(self, **kwargs: Any) -> FakeGenerateResult:
        self.last_text_request = kwargs
        if self.text_error:
            raise self.text_error
        return self.text_result

    async def extract_text_from_image(self, **kwargs: Any) -> FakeGenerateResult:
        self.last_image_request = kwargs
        if self.image_error:
            raise self.image_error
        return self.image_result


def make_settings() -> Settings:
    return Settings(
        ollama_model="gemma4:e2b-it-qat",
        ollama_base_url="http://ollama.test:11434",
    )


def test_health_endpoint_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "local-inference-api"}


def test_status_endpoint_reports_ready_runtime(monkeypatch):
    fake_adapter = FakeAdapter(
        status_result={
            "ollama_version": "0.30.5",
            "configured_model": "gemma4:e2b-it-qat",
            "configured_model_available": True,
        }
    )
    monkeypatch.setattr("local_inference_api.main.get_settings", make_settings)

    with TestClient(app) as client:
        client.app.state.runtime = fake_adapter
        response = client.get("/status")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["ollama_reachable"] is True
    assert body["configured_model_available"] is True
    assert body["configured_model"] == "gemma4:e2b-it-qat"


def test_status_endpoint_reports_degraded_when_runtime_is_unreachable(monkeypatch):
    fake_adapter = FakeAdapter(
        status_error=OllamaRuntimeError("No se puede contactar con Ollama.")
    )
    monkeypatch.setattr("local_inference_api.main.get_settings", make_settings)

    with TestClient(app) as client:
        client.app.state.runtime = fake_adapter
        response = client.get("/status")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "degraded"
    assert body["ollama_reachable"] is False
    assert body["message"] == "No se puede contactar con Ollama."


def test_text_generation_returns_openai_compatible_envelope(monkeypatch):
    fake_adapter = FakeAdapter(
        text_result=FakeGenerateResult(
            model="test-model",
            response="Linux es un sistema operativo.",
            prompt_eval_count=12,
            eval_count=7,
            done_reason="stop",
            reasoning_strategy_applied="thinking:on",
        )
    )
    monkeypatch.setattr("local_inference_api.main.get_settings", make_settings)

    payload = {
        "prompt": "Explica Linux en una frase",
        "system_prompt": "Responde en español",
        "reasoning_mode": "high",
        "max_output_tokens": 120,
        "temperature": 0.2,
    }

    with TestClient(app) as client:
        client.app.state.runtime = fake_adapter
        response = client.post("/v1/text/generate", json=payload)

    body = response.json()
    assert response.status_code == 200
    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["content"] == "Linux es un sistema operativo."
    assert body["usage"] == {
        "prompt_tokens": 12,
        "completion_tokens": 7,
        "total_tokens": 19,
    }
    assert body["reasoning_mode_requested"] == "high"
    assert body["reasoning_strategy_applied"] == "thinking:on"
    assert fake_adapter.last_text_request == payload


def test_text_generation_returns_503_when_runtime_fails(monkeypatch):
    fake_adapter = FakeAdapter(
        text_error=OllamaRuntimeError("Levanta el runtime local antes de enviar peticiones.")
    )
    monkeypatch.setattr("local_inference_api.main.get_settings", make_settings)

    with TestClient(app) as client:
        client.app.state.runtime = fake_adapter
        response = client.post("/v1/text/generate", json={"prompt": "hola"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Levanta el runtime local antes de enviar peticiones."


def test_image_extraction_reads_uploaded_file_and_returns_openai_envelope(monkeypatch):
    fake_adapter = FakeAdapter(
        image_result=FakeGenerateResult(
            model="test-model",
            response="Test 123",
            prompt_eval_count=8,
            eval_count=3,
            reasoning_strategy_applied="thinking:off",
        )
    )
    monkeypatch.setattr("local_inference_api.main.get_settings", make_settings)

    with TestClient(app) as client:
        client.app.state.runtime = fake_adapter
        response = client.post(
            "/v1/image/extract-text",
            data={
                "prompt": "Extrae el texto",
                "reasoning_mode": "off",
                "max_output_tokens": "64",
                "temperature": "0.0",
            },
            files={"image": ("sample.png", b"fake-image-bytes", "image/png")},
        )

    body = response.json()
    assert response.status_code == 200
    assert body["choices"][0]["message"]["content"] == "Test 123"
    assert body["reasoning_mode_requested"] == "off"
    assert fake_adapter.last_image_request is not None
    assert fake_adapter.last_image_request["image_bytes"] == b"fake-image-bytes"
    assert fake_adapter.last_image_request["prompt"] == "Extrae el texto"
    assert fake_adapter.last_image_request["max_output_tokens"] == 64
    assert fake_adapter.last_image_request["temperature"] == 0.0
