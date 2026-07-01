# Faster-Whisper Docker Server

Status: CPU-capable by default; NVIDIA GPU supported through an optional compose override.

`so_intelligence_tools` can use a warm faster-whisper Docker server as the preferred local ASR backend for Spanish push-to-talk dictation. The server exposes an OpenAI-compatible endpoint at `/v1/audio/transcriptions`, and the dictation tool talks to it through `PUSH_TO_TALK_DICTATION_RUNTIME=faster_whisper_http`.

## Runtime Profiles

Use the CPU profile when the machine has no NVIDIA GPU. This is the default repository setup and the current Linux workstation profile.

Use the CUDA profile only on machines with a working NVIDIA driver and NVIDIA Container Toolkit. This has been used for the validated Windows GPU dictation route.

| Profile | Files | Device | Compute type | Notes |
| --- | --- | --- | --- | --- |
| CPU default | `compose.yaml` + `.env.example` | `cpu` | `int8` | Best for machines without GPU; higher latency but simpler and portable. |
| NVIDIA CUDA | `compose.yaml` + `compose.cuda.yaml` + `.env.cuda.example` | `cuda` | `float16` | Best latency when Docker can access an NVIDIA GPU. |

## Start The Server On CPU

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

CPU configuration:

```env
WHISPER_MODEL=large-v3-turbo
WHISPER_LANGUAGE=es
WHISPER_PORT=9000
WHISPER_IMAGE=hwdsl2/whisper-server:latest
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
WHISPER_BEAM=1
WHISPER_STARTUP_TIMEOUT_SECONDS=300
```

The default compose file uses:

- image: `${WHISPER_IMAGE:-hwdsl2/whisper-server:latest}`
- host binding: `127.0.0.1:9000`
- model cache volume: `whisper-data:/var/lib/whisper`
- restart policy: `unless-stopped`

## Start The Server On NVIDIA GPU

```bash
cd docker/whisper-server
cp .env.cuda.example .env
docker compose -f compose.yaml -f compose.cuda.yaml up -d
```

CUDA configuration:

```env
WHISPER_MODEL=large-v3-turbo
WHISPER_LANGUAGE=es
WHISPER_PORT=9000
WHISPER_IMAGE=hwdsl2/whisper-server:cuda
WHISPER_DEVICE=cuda
WHISPER_COMPUTE_TYPE=float16
WHISPER_BEAM=1
WHISPER_STARTUP_TIMEOUT_SECONDS=300
```

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

For CPU inference, expect higher latency than CUDA. Keep the server warm and use a smaller or quantized model if latency is too high. First start can take several minutes because the model may need to download from Hugging Face and load into memory; `WHISPER_STARTUP_TIMEOUT_SECONDS` controls how long the Linux installer waits before starting the dictation listener.

For GPU acceleration, the target machine needs Docker, an NVIDIA driver, and working NVIDIA GPU access from Docker. If GPU support is unavailable, do not use `compose.cuda.yaml`.

On the current Windows GPU test machine, this backend produced the best Spanish dictation quality observed so far for rare words.

On the current CPU-only Linux workstation, the July 1, 2026 model spike compared `large-v3-turbo`, `base`, `small`, and `medium` with temporary benchmark containers and volumes. The result kept `large-v3-turbo` as the default because the faster smaller models degraded Spanish quality too much. See [Linux Whisper CPU Benchmark](whisper-cpu-benchmark-linux.md).
