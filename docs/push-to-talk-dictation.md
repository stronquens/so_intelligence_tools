# Push-To-Talk Dictation

Status: Working on Windows with faster-whisper HTTP; Linux bootstrap starts the same Docker backend.

Push-to-talk dictation records while you hold a shortcut, transcribes Spanish speech locally through an OpenAI-compatible faster-whisper HTTP server, and inserts the resulting text into the focused text field.

## Shortcut Behavior

Linux/default:

```text
Ctrl + Alt + Space
```

Windows default:

```text
Ctrl + Space
```

On Windows, recognized text is inserted after you release the shortcut. The listener still captures while the shortcut is held, but it avoids writing into the focused app while modifier keys are still down.

To reduce clipped words, capture begins before the ASR stream is ready and the early audio is replayed into the stream. After releasing the shortcut, capture continues briefly according to `PUSH_TO_TALK_DICTATION_POST_ROLL_SECONDS`.

The tool records while the keys are held. When you release the shortcut, recording stops and final transcription/insertion completes.

On Windows, run the listener manually with:

```powershell
poetry run so-intelligence-tools listen-dictation-shortcut
```

Install the hidden user-level Startup launcher with:

```powershell
poetry run so-intelligence-tools install-windows-dictation-startup
```

## Runtime

Faster-whisper HTTP runtime:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_BASE_URL=http://127.0.0.1:9000
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_MODEL=whisper-1
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
```

This feature does not use Ollama for ASR. The supported route expects a warm Docker/server process that exposes `/v1/audio/transcriptions`. See [Faster-Whisper Docker Server](whisper-docker.md) for the reproducible container setup.

Validate runtime setup:

```bash
poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
```

Run the service manually:

```bash
poetry run so-intelligence-tools run-push-to-talk-dictation-service
```

Installed service:

```bash
systemctl --user status so-intelligence-tools-push-to-talk-dictation.service
```

## Current Validation

Windows push-to-talk dictation is validated with `faster_whisper_http` against a warm Docker faster-whisper server using `large-v3-turbo` on CUDA. User testing confirmed the dictation quality is good for Spanish dictation, including uncommon words.

Known limitations:

- Windows inserts dictated text after the shortcut is released, not live character by character.
- Insertion into third-party fields can still vary by application focus and privilege level.
- Linux uses the same faster-whisper Docker backend during desktop bootstrap; end-to-end desktop validation is still pending.

## Practical Advice

- Keep the faster-whisper Docker server running warm for best latency.
- Use `Ctrl + Space` on Windows and `Ctrl + Alt + Space` on Linux unless changed in `.env`.
- If Whisper is unavailable, start the Docker faster-whisper server before using dictation.

