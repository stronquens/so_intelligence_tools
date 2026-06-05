from __future__ import annotations

import base64
from typing import Any

import httpx

from local_inference_api.config import Settings
from local_inference_api.models import OllamaGenerateResult, ReasoningMode


class OllamaRuntimeError(RuntimeError):
    """Raised when the Ollama runtime cannot satisfy a request."""


class OllamaAdapter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self._settings.ollama_base_url}/api/version")
            response.raise_for_status()
            return response.json()

    async def status(self) -> dict[str, Any]:
        try:
            version = await self.health()
            async with httpx.AsyncClient(timeout=10.0) as client:
                tags_response = await client.get(f"{self._settings.ollama_base_url}/api/tags")
                tags_response.raise_for_status()
                tags = tags_response.json().get("models", [])
        except httpx.HTTPError as exc:
            raise OllamaRuntimeError(
                "No se puede contactar con Ollama. Arranca o revisa el runtime local antes de usar la API."
            ) from exc

        available_models = {item.get("name") for item in tags}
        return {
            "ollama_version": version.get("version"),
            "configured_model": self._settings.ollama_model,
            "configured_model_available": self._settings.ollama_model in available_models,
        }

    async def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str | None,
        reasoning_mode: ReasoningMode,
        max_output_tokens: int,
        temperature: float,
    ) -> OllamaGenerateResult:
        payload = {
            "model": self._settings.ollama_model,
            "prompt": prompt,
            "system": self._build_system_prompt(system_prompt, reasoning_mode),
            "stream": False,
            "keep_alive": self._settings.ollama_keep_alive,
            "options": {
                "temperature": temperature,
                "num_predict": max_output_tokens,
            },
        }
        data = await self._post_generate(payload)
        return self._build_generate_result(data, reasoning_mode)

    async def extract_text_from_image(
        self,
        *,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str | None,
        reasoning_mode: ReasoningMode,
        max_output_tokens: int,
        temperature: float,
    ) -> OllamaGenerateResult:
        payload = {
            "model": self._settings.ollama_model,
            "prompt": prompt,
            "system": self._build_system_prompt(system_prompt, reasoning_mode),
            "images": [base64.b64encode(image_bytes).decode("utf-8")],
            "stream": False,
            "keep_alive": self._settings.ollama_keep_alive,
            "options": {
                "temperature": temperature,
                "num_predict": max_output_tokens,
            },
        }
        data = await self._post_generate(payload)
        return self._build_generate_result(data, reasoning_mode)

    def _build_system_prompt(
        self, system_prompt: str | None, reasoning_mode: ReasoningMode
    ) -> str | None:
        base = (system_prompt or "").strip()
        if reasoning_mode in {"medium", "high"}:
            return f"<|think|>\n{base}" if base else "<|think|>"
        return base or None

    async def _post_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._settings.ollama_timeout_seconds) as client:
                response = await client.post(
                    f"{self._settings.ollama_base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as exc:
            raise OllamaRuntimeError(
                "No se puede contactar con Ollama. Levanta el runtime local antes de enviar peticiones."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise OllamaRuntimeError(
                f"Ollama devolvió un error al procesar la petición. Detalle: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaRuntimeError(
                "La petición a Ollama falló por un error de red o timeout."
            ) from exc

    def _build_generate_result(
        self, data: dict[str, Any], reasoning_mode: ReasoningMode
    ) -> OllamaGenerateResult:
        strategy = "thinking:on" if reasoning_mode in {"medium", "high"} else "thinking:off"
        return OllamaGenerateResult(
            model=data.get("model", self._settings.ollama_model),
            response=data.get("response", ""),
            prompt_eval_count=data.get("prompt_eval_count", 0),
            eval_count=data.get("eval_count", 0),
            total_duration=data.get("total_duration", 0),
            load_duration=data.get("load_duration", 0),
            prompt_eval_duration=data.get("prompt_eval_duration", 0),
            eval_duration=data.get("eval_duration", 0),
            done_reason=data.get("done_reason", "stop"),
            reasoning_strategy_applied=strategy,
        )
