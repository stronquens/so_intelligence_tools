from __future__ import annotations

import base64
from typing import Any

import httpx

from local_inference_api.config import Settings
from local_inference_api.models import OllamaGenerateResult, ReasoningMode
from local_inference_api.ollama_adapter import OllamaRuntimeError


class RemoteOpenAICompatibleAdapter:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        if not settings.litellm_proxy_url or not settings.litellm_virtual_key or not settings.litellm_model:
            raise OllamaRuntimeError(
                "Falta configurar `LITELLM_PROXY_URL`, `LITELLM_VIRTUAL_KEY` o `LITELLM_MODEL` para usar el proveedor remoto."
            )

    async def status(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self._settings.litellm_proxy_url.rstrip('/')}/v1/models",
                    headers=self._headers(),
                )
                response.raise_for_status()
                models = response.json().get("data", [])
        except httpx.HTTPError as exc:
            raise OllamaRuntimeError(
                "No se puede contactar con LiteLLM Proxy. Revisa la conectividad o la API key."
            ) from exc

        available_models = {item.get("id") for item in models}
        configured_model = self._settings.litellm_model
        return {
            "ollama_version": None,
            "configured_model": configured_model,
            "configured_model_available": configured_model in available_models,
        }

    async def warmup(self) -> dict[str, Any]:
        return {
            "model": self._settings.litellm_model,
            "load_duration": 0,
            "total_duration": 0,
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
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self._settings.litellm_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        data = await self._post_chat(payload)
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
        image_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        )
        payload = {
            "model": self._settings.litellm_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
        }
        data = await self._post_chat(payload)
        return self._build_generate_result(data, reasoning_mode)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.litellm_virtual_key}",
            "Content-Type": "application/json",
        }

    async def _post_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=self._settings.ollama_timeout_seconds) as client:
                response = await client.post(
                    f"{self._settings.litellm_proxy_url.rstrip('/')}/v1/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as exc:
            raise OllamaRuntimeError(
                "No se puede contactar con LiteLLM Proxy. Revisa la conectividad o la API key."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise OllamaRuntimeError(
                f"LiteLLM Proxy devolvió un error al procesar la petición. Detalle: {detail}"
            ) from exc
        except httpx.HTTPError as exc:
            raise OllamaRuntimeError(
                "La petición a LiteLLM Proxy falló por un error de red o timeout."
            ) from exc

    @staticmethod
    def _build_generate_result(
        data: dict[str, Any], reasoning_mode: ReasoningMode
    ) -> OllamaGenerateResult:
        choices = data.get("choices") or []
        first_choice = choices[0] if choices else {}
        message = first_choice.get("message") or {}
        usage = data.get("usage") or {}
        strategy = "thinking:on" if reasoning_mode in {"medium", "high"} else "thinking:off"
        return OllamaGenerateResult(
            model=data.get("model", "remote-openai-compatible"),
            response=message.get("content", "") or "",
            prompt_eval_count=usage.get("prompt_tokens", 0),
            eval_count=usage.get("completion_tokens", 0),
            done_reason=first_choice.get("finish_reason", "stop"),
            reasoning_strategy_applied=strategy,
        )
