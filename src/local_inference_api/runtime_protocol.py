from __future__ import annotations

from typing import Any, Protocol

from local_inference_api.models import OllamaGenerateResult, ReasoningMode


class RuntimeAdapter(Protocol):
    async def status(self) -> dict[str, Any]: ...

    async def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str | None,
        reasoning_mode: ReasoningMode,
        max_output_tokens: int,
        temperature: float,
    ) -> OllamaGenerateResult: ...

    async def extract_text_from_image(
        self,
        *,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str | None,
        reasoning_mode: ReasoningMode,
        max_output_tokens: int,
        temperature: float,
    ) -> OllamaGenerateResult: ...
