# Faster-Whisper Docker Server

Status: Working on Windows with NVIDIA GPU; used by the Linux desktop bootstrap as the supported dictation backend.

`so_intelligence_tools` can use a warm faster-whisper Docker server as the preferred local ASR backend for Spanish push-to-talk dictation. The server exposes an OpenAI-compatible endpoint at `/v1/audio/transcriptions`, and the dictation tool talks to it through `PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http`.

## Start The Server

Windows:

```powershell
cd C:\Dev\Active\so_intelligence_tools\docker\whisper-server
copy .env.example .env
docker compose up -d
```

Linux:

```bash
cd /path/to/so_intelligence_tools/docker/whisper-server
cp .env.example .env
docker compose up -d
```

## Current Working Configuration

```env
WHISPER_MODEL=large-v3-turbo
WHISPER_LANGUAGE=es
WHISPER_PORT=9000
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
WHISPER_BEAM=1
```

The compose file uses:

- image: `hwdsl2/whisper-server:cuda`
- host binding: `127.0.0.1:9000`
- model cache volume: `whisper-data:/var/lib/whisper`
- restart policy: `unless-stopped`
- NVIDIA GPU reservation: one GPU

## Verify

```bash
curl http://127.0.0.1:9000/v1/models
```

Expected response includes the active faster-whisper model, for example `large-v3-turbo`.

## Configure Dictation

In the project `.env`:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_BASE_URL=http://127.0.0.1:9000
PUSH_TO_TALK_DICTATION_FASTER_WHISPER_MODEL=whisper-1
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
```

Then verify the runner:

```bash
poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
```

## Porting Notes

For GPU acceleration, the target machine needs Docker, an NVIDIA driver, and working NVIDIA GPU access from Docker. If GPU support is unavailable, this exact CUDA compose file will not start correctly; use a CPU-capable Whisper image/configuration instead and expect higher latency.

On the current Windows machine, this backend produced the best Spanish dictation quality observed so far for rare words and is the daily dictation backend while the container is running.
