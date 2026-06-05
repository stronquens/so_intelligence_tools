from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    local_inference_api_host: str = "127.0.0.1"
    local_inference_api_port: int = 8000
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL"
    ollama_timeout_seconds: int = 180
    ollama_keep_alive: str = "10m"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
