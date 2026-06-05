from __future__ import annotations

from typing import Protocol

from so_intelligence_tools.domain.models import ReasoningMode, TextGenerationResult


class InferencePort(Protocol):
    def generate_text(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        reasoning_mode: ReasoningMode = "off",
        max_output_tokens: int = 256,
        temperature: float = 0.0,
    ) -> TextGenerationResult: ...

    def extract_text_from_image(
        self,
        *,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str | None = None,
        reasoning_mode: ReasoningMode = "off",
        max_output_tokens: int = 256,
        temperature: float = 0.0,
    ) -> TextGenerationResult: ...
