from __future__ import annotations

from local_inference_api.config import Settings
from local_inference_api.ollama_adapter import OllamaAdapter
from local_inference_api.remote_openai_adapter import RemoteOpenAICompatibleAdapter
from local_inference_api.runtime_protocol import RuntimeAdapter


def build_runtime_adapter(settings: Settings) -> RuntimeAdapter:
    if settings.inference_provider == "litellm_proxy":
        return RemoteOpenAICompatibleAdapter(settings)
    return OllamaAdapter(settings)
