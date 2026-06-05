from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


ReasoningMode = Literal["off", "low", "medium", "high"]


class TextGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    system_prompt: str | None = None
    reasoning_mode: ReasoningMode = "off"
    max_output_tokens: int = Field(default=256, ge=1, le=4096)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: Literal["local-inference-api"]


class RuntimeStatusResponse(BaseModel):
    status: Literal["ok", "degraded"]
    service: Literal["local-inference-api"]
    ollama_reachable: bool
    ollama_version: str | None = None
    configured_model: str
    configured_model_available: bool
    reasoning_mode_strategy: str
    message: str


class ChatMessage(BaseModel):
    role: Literal["assistant"]
    content: str


class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage
    reasoning_mode_requested: ReasoningMode
    reasoning_strategy_applied: str


class OllamaGenerateResult(BaseModel):
    model: str
    response: str
    prompt_eval_count: int = 0
    eval_count: int = 0
    total_duration: int = 0
    load_duration: int = 0
    prompt_eval_duration: int = 0
    eval_duration: int = 0
    done_reason: str = "stop"
    reasoning_strategy_applied: str


def build_chat_completion(
    *,
    model: str,
    content: str,
    prompt_tokens: int,
    completion_tokens: int,
    finish_reason: str,
    reasoning_mode_requested: ReasoningMode,
    reasoning_strategy_applied: str,
) -> ChatCompletionResponse:
    created = int(datetime.now(tz=timezone.utc).timestamp())
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid4().hex}",
        created=created,
        model=model,
        choices=[
            Choice(
                index=0,
                message=ChatMessage(role="assistant", content=content),
                finish_reason=finish_reason,
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
        reasoning_mode_requested=reasoning_mode_requested,
        reasoning_strategy_applied=reasoning_strategy_applied,
    )
