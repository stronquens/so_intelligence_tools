# Linux Whisper Dictation

Status: Preferred current Linux route; validated locally on CPU with known post-release latency.

This is the recommended Linux path for push-to-talk dictation. It records while the shortcut is held, sends the captured audio to a warm faster-whisper HTTP server, and inserts the final Spanish transcription after release.

## Why Use This Option

- Better Spanish dictation quality in current tests than smaller CPU Whisper candidates.
- Simpler insertion model: insert final text after release instead of live partial text.
- Same backend shape on Windows and Linux.
- Local/on-prem when the Docker server runs on your machine.

## Shortcut

Default Linux shortcut:

```text
Ctrl + Shift + Space
```

The listener records while the shortcut is held. After release, the session keeps a short post-roll buffer and then inserts the recognized text.

If an existing listener was started before changing the shortcut, restart it:

```bash
systemctl --user restart so-intelligence-tools-push-to-talk-dictation.service
```

`faster_whisper_http` keeps the Docker server warm, but it still sends each captured utterance for transcription after release rather than streaming final text live while you speak.

The runner serializes sessions. If you press the shortcut again while the previous release is still transcribing or inserting text, the new press is ignored so old audio cannot be mixed into the next dictation.

## Runtime Configuration

Project `.env`:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http
PUSH_TO_TALK_DICTATION_SHORTCUT=<ctrl>+<shift>+<space>
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_BASE_URL=http://127.0.0.1:9000
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_MODEL=whisper-1
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_TIMEOUT_SECONDS=30
PUSH_TO_TALK_DICTATION_SAMPLE_RATE_HZ=16000
PUSH_TO_TALK_DICTATION_CHUNK_MS=560
PUSH_TO_TALK_DICTATION_POST_ROLL_SECONDS=0.35
PUSH_TO_TALK_DICTATION_INSERTION_STRATEGY=final_segments
PUSH_TO_TALK_DICTATION_MICROPHONE_SOURCE=
```

Docker Whisper `.env` on a CPU-only machine:

```env
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
WHISPER_STARTUP_TIMEOUT_SECONDS=300
```

## Start The Whisper Server

The Linux bootstrap now ensures the Docker backend during desktop setup:

```bash
poetry run so-intelligence-tools install-linux-desktop-integration
```

You can also start only the Whisper server:

```bash
poetry run so-intelligence-tools ensure-whisper-docker-server
```

Manual Docker route:

```bash
cd docker/whisper-server
cp .env.example .env
docker compose up -d
```

See [Faster-Whisper Docker Server](whisper-docker.md) for CPU and GPU profiles. On a CPU-only machine, keep the default `.env.example` values: `WHISPER_DEVICE=cpu` and `WHISPER_COMPUTE_TYPE=int8`.

## Model Choice On This Linux Workstation

Current CPU default:

```env
WHISPER_MODEL=large-v3-turbo
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
WHISPER_BEAM=1
```

A local CPU benchmark on July 1, 2026 compared `large-v3-turbo`, `base`, `small`, and `medium` on a 12-second Spanish sample. `large-v3-turbo` transcribed in 7.14s. `small` and `base` were much faster but lost too much content; `medium` transcribed in 5.59s but still degraded wording and saved only about 1.6s. Keep `large-v3-turbo` as the default unless a future benchmark with human reference transcripts proves a better tradeoff. See [Linux Whisper CPU Benchmark](whisper-cpu-benchmark-linux.md).

## Verify

```bash
curl http://127.0.0.1:9000/v1/models
poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
```

Run the listener manually:

```bash
poetry run so-intelligence-tools listen-dictation-shortcut
```

Or check the installed Linux user service:

```bash
systemctl --user status so-intelligence-tools-push-to-talk-dictation.service
```

## Switching From Nemotron To Whisper

1. Set `PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http`.
2. Start the faster-whisper Docker server.
3. Restart the dictation listener/service.

```bash
systemctl --user restart so-intelligence-tools-push-to-talk-dictation.service
```

## Known Linux Notes

- Linux has local validation for the CPU Docker backend, shortcut behavior, service readiness, `Ctrl + Space` conflict cleanup, and CPU model benchmark evidence.
- Windows is validated separately with its own Startup launcher and adapter path; do not use Windows commands as Linux service commands.
- CPU-only machines are supported by the default compose profile and should expect higher latency than CUDA machines.
- CUDA machines can use `compose.cuda.yaml` plus `.env.cuda.example`.
- If `Ctrl + Space` still opens a desktop search/input UI, restart the Linux dictation service and check IBus/GNOME/Ulauncher bindings; the listener cannot reliably prevent every shell-level shortcut.
