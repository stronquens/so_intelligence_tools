from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolRunnerSettings(BaseSettings):
    local_inference_api_base_url: str = "http://127.0.0.1:8000"
    local_inference_api_timeout_seconds: int = 30
    default_text_reasoning_mode: str = "off"
    default_image_reasoning_mode: str = "off"
    linux_read_selection_command: str | None = None
    linux_replace_selection_command: str | None = None
    linux_notify_send_binary: str = "notify-send"
    selected_text_correction_shortcut: str = "<ctrl>+<space>"
    shortcut_listener_platform: str = "linux-x11"
    gnome_selected_text_correction_binding: str = "<Primary>space"
    shortcut_action_start_delay_seconds: float = 0.35

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_tool_runner_settings() -> ToolRunnerSettings:
    return ToolRunnerSettings()
