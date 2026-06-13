# Configuration

Configuration is read from `.env` through Pydantic settings. Copy the example file first:

```bash
cp .env.example .env
```

Never commit real secrets. See [Security And Secrets](security-and-secrets.md).

## Local API

```env
LOCAL_INFERENCE_API_HOST=127.0.0.1
LOCAL_INFERENCE_API_PORT=8010
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
LOCAL_INFERENCE_API_TIMEOUT_SECONDS=30
```

The desktop tools use `LOCAL_INFERENCE_API_BASE_URL`. The user service uses host and port.

## Inference Provider

### Ollama

```env
INFERENCE_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4:e2b-it-qat
OLLAMA_TIMEOUT_SECONDS=180
OLLAMA_KEEP_ALIVE=10m
```

### OpenAI-Compatible Proxy

```env
INFERENCE_PROVIDER=litellm_proxy
LITELLM_PROXY_URL=https://your-litellm-proxy.example.com
LITELLM_VIRTUAL_KEY=...
LITELLM_MODEL=your/model
```

## Desktop Shortcuts

```env
GNOME_SELECTED_TEXT_CORRECTION_BINDING=<Primary><Alt>c
PUSH_TO_TALK_DICTATION_SHORTCUT=<ctrl>+<alt>+<space>
GNOME_SYSTEM_AUDIO_TRANSLATION_BINDING=<Primary><Alt>y
GNOME_VOICE_TRANSLATION_BINDING=<Primary><Alt>u
```

GNOME custom shortcuts launch wrapper scripts or CLI commands from the repository root so `.env` is loaded correctly.

## System Audio Translation

```env
OPENAI_API_KEY=
SYSTEM_AUDIO_TRANSLATION_MODE=translate_es_openai_realtime
SYSTEM_AUDIO_TRANSLATION_SOURCE_LANGUAGE=auto
SYSTEM_AUDIO_TRANSLATION_TARGET_LANGUAGE=es
SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_MODEL=gpt-realtime
```

The current realtime mode depends on a provider API key. Chunked modes are still useful for development and fallback testing.

## Voice Translation Virtual Microphone

```env
VOICE_TRANSLATION_SOURCE_LANGUAGE=Spanish
VOICE_TRANSLATION_TARGET_LANGUAGE=English
VOICE_TRANSLATION_OPENAI_MODEL=gpt-realtime-translate
VOICE_TRANSLATION_VOICE=marin
VOICE_TRANSLATION_PHYSICAL_SOURCE=
VOICE_TRANSLATION_PASSTHROUGH_VOLUME=1.0
VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03
VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME=0.12
VOICE_TRANSLATION_OUTPUT_VOLUME=0.75
VOICE_TRANSLATION_VIRTUAL_SINK_NAME=so_ai_translated_mic
```

Use `VOICE_TRANSLATION_PHYSICAL_SOURCE` only when you need to force a specific real microphone. Do not set it to a `.monitor` source or to the virtual microphone itself.

## Push-To-Talk Dictation

```env
PUSH_TO_TALK_DICTATION_RUNTIME=onnx_cpu
PUSH_TO_TALK_DICTATION_MODEL_REPO=onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
PUSH_TO_TALK_DICTATION_SAMPLE_RATE_HZ=16000
PUSH_TO_TALK_DICTATION_CHUNK_MS=560
PUSH_TO_TALK_DICTATION_INSERTION_STRATEGY=final_segments
```

This feature is experimental. See [Push-To-Talk Dictation](push-to-talk-dictation.md).

