from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    local_inference_api_host: str = "127.0.0.1"
    local_inference_api_port: int = 8000
    inference_provider: Literal["ollama", "litellm_proxy"] = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma4-e2b-longctx:latest"
    ollama_timeout_seconds: int = 180
    ollama_keep_alive: str = "10m"
    ollama_warmup_on_startup: bool = False
    litellm_proxy_url: str | None = None
    litellm_virtual_key: str | None = None
    litellm_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
