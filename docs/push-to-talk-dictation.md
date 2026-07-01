# Push-To-Talk Dictation

Status: Whisper is the preferred current route; Nemotron streaming is preserved as a Linux backup/experimental route.

Push-to-talk dictation records while you hold a shortcut, transcribes Spanish speech locally, and inserts the resulting text into the focused text field.

## Backend Options

| Backend | Runtime | Linux status | Windows status | Behavior | Best for |
| --- | --- | --- | --- | --- | --- |
| [Whisper / faster-whisper HTTP](linux-whisper-dictation.md) | `faster_whisper_http` | Preferred current route; CPU Docker profile validated locally | Validated with Windows listener and warm Docker server | Inserts final text after release | Daily dictation quality and reliability |
| [Nemotron ONNX CPU streaming](nemotron-dictation-backup.md) | `onnx_cpu` | Retired Linux prototype, restorable from Git history | Not active | Experimental realtime streaming insertion | Realtime ASR experiments and rollback |

Current recommendation: use Whisper/faster-whisper for daily work. Keep Nemotron documented as a recoverable Linux realtime streaming option.

## Shortcut Behavior

Linux default:

```text
Ctrl + Shift + Space
```

Windows default:

```text
Ctrl + Shift + Space
```

On Linux and Windows, recognized text is inserted after you release the shortcut. The listener still captures while the shortcut is held, but it avoids writing into the focused app while modifier keys are still down.

To reduce clipped words, capture begins before the ASR stream is ready and the early audio is replayed into the stream. After releasing the shortcut, capture continues briefly according to `PUSH_TO_TALK_DICTATION_POST_ROLL_SECONDS`.

The tool records while the keys are held. When you release the shortcut, recording stops and final transcription/insertion completes.

On Linux, the installed user service is:

```bash
systemctl --user status so-intelligence-tools-push-to-talk-dictation.service
```

On Windows, run the listener manually with:

```powershell
poetry run so-intelligence-tools listen-dictation-shortcut
```

Install the hidden user-level Startup launcher with:

```powershell
poetry run so-intelligence-tools install-windows-dictation-startup
```

## Runtime

Current Whisper runtime:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_BASE_URL=http://127.0.0.1:9000
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_MODEL=whisper-1
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
```

This feature does not use Ollama for ASR. The supported Whisper route expects a warm Docker/server process that exposes `/v1/audio/transcriptions`. See [Linux Whisper Dictation](linux-whisper-dictation.md) and [Faster-Whisper Docker Server](whisper-docker.md) for the reproducible setup.

The previous Linux Nemotron ONNX CPU realtime prototype is documented in [Linux Nemotron Streaming Dictation](nemotron-dictation-backup.md).

## Warm Runtime And Latency

The installer keeps the faster-whisper Docker server warm with `docker compose up -d`, waits for `/v1/models`, and the dictation listener checks readiness before it starts listening for shortcuts. That avoids the cold model startup on the first dictation.

The current `faster_whisper_http` path is still buffered-on-release: it records while the shortcut is held, then sends the captured utterance to `/v1/audio/transcriptions` after release. Long utterances or CPU-only Whisper profiles can still feel laggy even though the server is already warm.

The runner serializes dictation sessions. If you press the shortcut again while the previous recording is still finalizing transcription or insertion, the new press is ignored instead of mixing old audio/text into the next dictation.

On the current CPU-only Linux workstation, a July 1, 2026 benchmark kept `large-v3-turbo` as the recommended default. `base` and `small` were faster but lost too much Spanish content; `medium` was the only plausible smaller candidate but saved only about 1.6 seconds on a 12-second sample while still degrading the transcript. See [Linux Whisper CPU Benchmark](whisper-cpu-benchmark-linux.md).

If the system still reacts to `Ctrl + Space`, restart the dictation listener so it picks up the current `Ctrl + Shift + Space` default:

```bash
systemctl --user restart so-intelligence-tools-push-to-talk-dictation.service
```

The installer also removes known old `Ctrl + Space` IBus/GNOME input-source bindings when present, but global keyboard listeners cannot reliably `preventDefault` every desktop-shell shortcut.

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

| Platform | Validation state |
| --- | --- |
| Linux | Local CPU route validated with warm Docker `large-v3-turbo`, `Ctrl + Shift + Space`, session serialization, best-effort old `Ctrl + Space` cleanup, and a CPU model benchmark. Full GUI focus behavior can still vary by desktop session/app. |
| Windows | Validated with `faster_whisper_http` against a warm Docker faster-whisper server using `large-v3-turbo` on CUDA. User testing confirmed good Spanish dictation quality, including uncommon words. |

Known limitations:

- Linux and Windows insert dictated text after the shortcut is released, not live character by character.
- Insertion into third-party fields can still vary by application focus and privilege level.
- Linux CPU-only transcription can feel laggy after release; the server is warm, but the utterance is still transcribed after recording stops.
- Nemotron streaming is not currently active in the runtime tree; use its backup guide before attempting to restore it.

## Practical Advice

- Keep the faster-whisper Docker server running warm for best latency.
- Use `Ctrl + Shift + Space` on Linux and Windows unless changed in `.env`.
- If Whisper is unavailable, start the Docker faster-whisper server before using dictation.
