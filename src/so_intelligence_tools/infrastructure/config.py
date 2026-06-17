from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ToolRunnerSettings(BaseSettings):
    local_inference_api_host: str = "127.0.0.1"
    local_inference_api_port: int = 8010
    local_inference_api_base_url: str = "http://127.0.0.1:8010"
    local_inference_api_timeout_seconds: int = 30
    default_text_reasoning_mode: str = "off"
    default_image_reasoning_mode: str = "off"
    linux_read_selection_command: str | None = None
    linux_replace_selection_command: str | None = None
    linux_notify_send_binary: str = "notify-send"
    selected_text_correction_shortcut: str = "<ctrl>+<space>"
    windows_selected_text_correction_shortcut: str = "<ctrl>+<alt>+c"
    shortcut_listener_platform: str = "linux-x11"
    gnome_selected_text_correction_binding: str = "<Primary><Alt>c"
    shortcut_action_start_delay_seconds: float = 0.35
    shortcut_action_cooldown_seconds: float = 2.0
    push_to_talk_dictation_shortcut: str = "<ctrl>+<alt>+<space>"
    windows_push_to_talk_dictation_shortcut: str = "<ctrl>+<space>"
    push_to_talk_dictation_runtime: str = "faster_whisper_http"
    push_to_talk_dictation_language: str = "es-ES"
    push_to_talk_dictation_faster_whisper_base_url: str = "http://127.0.0.1:9000"
    push_to_talk_dictation_faster_whisper_model: str = "whisper-1"
    push_to_talk_dictation_faster_whisper_timeout_seconds: float = 30.0
    push_to_talk_dictation_faster_whisper_prompt: str | None = None
    push_to_talk_dictation_microphone_source: str | None = None
    push_to_talk_dictation_sample_rate_hz: int = 16000
    push_to_talk_dictation_chunk_ms: int = 560
    push_to_talk_dictation_insertion_strategy: str = "final_segments"
    push_to_talk_dictation_post_roll_seconds: float = 0.35
    gnome_system_audio_translation_binding: str = "<Primary><Alt>y"
    system_audio_translation_source_language: str = "auto"
    system_audio_translation_target_language: str = "es"
    system_audio_translation_mode: str = "translate_es_chunked"
    system_audio_translation_transcription_base_url: str | None = None
    system_audio_translation_transcription_api_key: str | None = None
    system_audio_translation_transcription_model: str = "whisper-1"
    system_audio_translation_sample_rate_hz: int = 16000
    system_audio_translation_chunk_ms: int = 250
    system_audio_translation_segment_seconds: float = 2.5
    system_audio_translation_overlap_seconds: float = 0.5
    system_audio_translation_pending_segment_limit: int = 16
    system_audio_translation_control_socket_path: str = (
        "~/.cache/so_intelligence_tools/system_audio_translation.sock"
    )
    system_audio_translation_logs_dir: str = "~/.cache/so_intelligence_tools/system_audio_logs"
    system_audio_translation_reconnect_backoff_seconds: float = 2.0
    system_audio_translation_window_title: str = "System Audio Translation"
    system_audio_translation_openai_realtime_api_key: str | None = None
    system_audio_translation_openai_realtime_base_url: str | None = None
    system_audio_translation_openai_realtime_model: str = "gpt-realtime"
    system_audio_translation_openai_realtime_sample_rate_hz: int = 24000
    system_audio_translation_openai_realtime_chunk_ms: int = 80
    system_audio_translation_openai_realtime_silence_duration_ms: int = 280
    system_audio_translation_openai_realtime_prefix_padding_ms: int = 180
    system_audio_translation_openai_realtime_vad_threshold: float = 0.4
    system_audio_translation_openai_realtime_turn_detection_type: str = "server_vad"
    system_audio_translation_openai_realtime_semantic_vad_eagerness: str = "medium"
    system_audio_translation_openai_realtime_interrupt_response: bool = False
    system_audio_translation_openai_realtime_max_output_tokens: int = 1024
    system_audio_translation_openai_realtime_translate_completed_transcripts: bool = False
    system_audio_translation_openai_realtime_text_translation_model: str = "gpt-4o-mini"
    gnome_voice_translation_binding: str = "<Primary><Alt>u"
    voice_translation_source_language: str = "Spanish"
    voice_translation_target_language: str = "English"
    voice_translation_openai_api_key: str | None = None
    voice_translation_openai_base_url: str | None = None
    voice_translation_openai_model: str = "gpt-realtime-translate"
    voice_translation_voice: str = "marin"
    voice_translation_sample_rate_hz: int = 24000
    voice_translation_chunk_ms: int = 80
    voice_translation_silence_duration_ms: int = 260
    voice_translation_prefix_padding_ms: int = 160
    voice_translation_vad_threshold: float = 0.4
    voice_translation_reconnect_backoff_seconds: float = 2.0
    voice_translation_pending_audio_chunks: int = 64
    voice_translation_physical_source: str | None = None
    voice_translation_passthrough_volume: float = 1.0
    voice_translation_ducked_passthrough_volume: float = 0.03
    voice_translation_max_ducked_passthrough_volume: float = 0.12
    voice_translation_output_volume: float = 0.75
    voice_translation_virtual_sink_name: str = "so_ai_translated_mic"
    voice_translation_control_socket_path: str = (
        "~/.cache/so_intelligence_tools/voice_translation_virtual_microphone.sock"
    )
    voice_translation_logs_dir: str = "~/.cache/so_intelligence_tools/voice_translation_logs"
    voice_translation_debug_recording_enabled: bool = False
    voice_translation_debug_recordings_dir: str = (
        "~/.cache/so_intelligence_tools/voice_translation_debug_audio"
    )
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    litellm_proxy_url: str | None = None
    litellm_virtual_key: str | None = None
    litellm_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_tool_runner_settings() -> ToolRunnerSettings:
    return ToolRunnerSettings()
