from __future__ import annotations

import httpx

from so_intelligence_tools.domain.errors import InferenceUnavailableError
from so_intelligence_tools.domain.models import ReasoningMode, TextGenerationResult
from so_intelligence_tools.infrastructure.config import ToolRunnerSettings


class LocalInferenceClient:
    def __init__(
        self,
        settings: ToolRunnerSettings,
        *,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._transport = transport

    def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        reasoning_mode: ReasoningMode = "off",
        max_output_tokens: int = 256,
        temperature: float = 0.0,
    ) -> TextGenerationResult:
        payload = {
            "prompt": prompt,
            "system_prompt": system_prompt,
            "reasoning_mode": reasoning_mode,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        data = self._post_json("/v1/text/generate", json=payload)
        return self._parse_chat_completion(data)

    def extract_text_from_image(
        self,
        *,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str | None = None,
        reasoning_mode: ReasoningMode = "off",
        max_output_tokens: int = 256,
        temperature: float = 0.0,
    ) -> TextGenerationResult:
        files = {"image": ("capture.png", image_bytes, "image/png")}
        data = {
            "prompt": prompt,
            "reasoning_mode": reasoning_mode,
            "max_output_tokens": str(max_output_tokens),
            "temperature": str(temperature),
        }
        if system_prompt:
            data["system_prompt"] = system_prompt

        response = self._post_multipart("/v1/image/extract-text", data=data, files=files)
        return self._parse_chat_completion(response)

    def _post_json(self, path: str, *, json: dict) -> dict:
        try:
            with httpx.Client(
                base_url=self._settings.local_inference_api_base_url,
                timeout=self._settings.local_inference_api_timeout_seconds,
                transport=self._transport,
            ) as client:
                response = client.post(path, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            detail = self._extract_error_detail(exc.response)
            raise InferenceUnavailableError(detail) from exc
        except httpx.HTTPError as exc:
            raise InferenceUnavailableError(
                "No se pudo contactar con la API local de inferencia."
            ) from exc

    def _post_multipart(self, path: str, *, data: dict, files: dict) -> dict:
        try:
            with httpx.Client(
                base_url=self._settings.local_inference_api_base_url,
                timeout=self._settings.local_inference_api_timeout_seconds,
                transport=self._transport,
            ) as client:
                response = client.post(path, data=data, files=files)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            detail = self._extract_error_detail(exc.response)
            raise InferenceUnavailableError(detail) from exc
        except httpx.HTTPError as exc:
            raise InferenceUnavailableError(
                "No se pudo contactar con la API local de inferencia."
            ) from exc

    @staticmethod
    def _extract_error_detail(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or "La API local devolvió un error."
        return payload.get("detail") or response.text or "La API local devolvió un error."

    @staticmethod
    def _parse_chat_completion(payload: dict) -> TextGenerationResult:
        try:
            content = payload["choices"][0]["message"]["content"]
            usage = payload.get("usage", {})
        except (KeyError, IndexError, TypeError) as exc:
            raise InferenceUnavailableError(
                "La API local devolvió una respuesta inválida o inesperada."
            ) from exc

        return TextGenerationResult(
            content=content,
            model=payload.get("model", "unknown"),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            reasoning_mode_requested=payload.get("reasoning_mode_requested", "off"),
            reasoning_strategy_applied=payload.get("reasoning_strategy_applied", "thinking:off"),
        )
