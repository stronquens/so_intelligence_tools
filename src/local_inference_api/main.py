from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from local_inference_api.config import get_settings
from local_inference_api.models import (
    HealthResponse,
    ReasoningMode,
    RuntimeStatusResponse,
    TextGenerateRequest,
    build_chat_completion,
)
from local_inference_api.ollama_adapter import OllamaRuntimeError
from local_inference_api.runtime_factory import build_runtime_adapter
from local_inference_api.runtime_protocol import RuntimeAdapter


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.runtime = build_runtime_adapter(settings)
    yield


app = FastAPI(
    title="local-inference-api",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="local-inference-api")


@app.get("/status", response_model=RuntimeStatusResponse)
async def status() -> RuntimeStatusResponse:
    settings = get_settings()
    adapter: RuntimeAdapter = app.state.runtime
    try:
        runtime = await adapter.status()
    except OllamaRuntimeError as exc:
        return RuntimeStatusResponse(
            status="degraded",
            service="local-inference-api",
            ollama_reachable=False,
            configured_model=settings.litellm_model or settings.ollama_model,
            configured_model_available=False,
            reasoning_mode_strategy="off|low -> fast path, medium|high -> more deliberative path",
            message=str(exc),
        )

    available = runtime["configured_model_available"]
    message = (
        "El proveedor de inferencia está disponible y el modelo configurado está listo."
        if available
        else "El proveedor responde, pero el modelo configurado no aparece disponible."
    )
    return RuntimeStatusResponse(
        status="ok" if available else "degraded",
        service="local-inference-api",
        ollama_reachable=True,
        ollama_version=runtime["ollama_version"],
        configured_model=runtime["configured_model"],
        configured_model_available=available,
        reasoning_mode_strategy="off|low -> fast path, medium|high -> more deliberative path",
        message=message,
    )


@app.post("/v1/text/generate")
async def generate_text(request: TextGenerateRequest):
    adapter: RuntimeAdapter = app.state.runtime
    try:
        result = await adapter.generate_text(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            reasoning_mode=request.reasoning_mode,
            max_output_tokens=request.max_output_tokens,
            temperature=request.temperature,
        )
    except OllamaRuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return build_chat_completion(
        model=result.model,
        content=result.response,
        prompt_tokens=result.prompt_eval_count,
        completion_tokens=result.eval_count,
        finish_reason=result.done_reason,
        reasoning_mode_requested=request.reasoning_mode,
        reasoning_strategy_applied=result.reasoning_strategy_applied,
    )


@app.post("/v1/image/extract-text")
async def extract_text_from_image(
    image: UploadFile = File(...),
    prompt: str = Form(
        default="Extrae exactamente el texto visible en la imagen. No añadas explicación ni texto adicional."
    ),
    system_prompt: str | None = Form(default=None),
    reasoning_mode: ReasoningMode = Form(default="off"),
    max_output_tokens: int = Form(default=256),
    temperature: float = Form(default=0.0),
):
    adapter: RuntimeAdapter = app.state.runtime
    try:
        image_bytes = await image.read()
        result = await adapter.extract_text_from_image(
            image_bytes=image_bytes,
            prompt=prompt,
            system_prompt=system_prompt,
            reasoning_mode=reasoning_mode,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
    except OllamaRuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return build_chat_completion(
        model=result.model,
        content=result.response,
        prompt_tokens=result.prompt_eval_count,
        completion_tokens=result.eval_count,
        finish_reason=result.done_reason,
        reasoning_mode_requested=reasoning_mode,
        reasoning_strategy_applied=result.reasoning_strategy_applied,
    )
