# Linux Whisper CPU Benchmark

Status: historical benchmark evidence for CPU-only Spanish dictation on this workstation.

This note preserves the July 1, 2026 CPU spike that compared the current warm `large-v3-turbo` faster-whisper Docker server against smaller Whisper model families. It is meant to answer the future question: "Can we reduce post-release dictation latency without losing much Spanish quality?"

## Machine And Runtime

Machine used for this benchmark:

- Host: `dollo-slimbook-executive`
- OS/kernel: Ubuntu Linux, kernel `6.8.0-124-generic`
- CPU: 12th Gen Intel Core i7-12700H
- Logical CPUs: 20
- RAM: 62 GiB
- GPU/CUDA: not used; benchmark was CPU-only

Production runtime during the benchmark:

```env
WHISPER_MODEL=large-v3-turbo
WHISPER_LANGUAGE=es
WHISPER_PORT=9000
WHISPER_IMAGE=hwdsl2/whisper-server:latest
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
WHISPER_BEAM=1
```

The production Docker server stayed warm at `http://127.0.0.1:9000`. Candidate models ran in temporary Docker containers on separate localhost ports with temporary Docker volumes. Those containers and volumes were removed after each candidate so benchmark model weights were not retained.

## Method

Benchmark script:

```bash
poetry run python openspec/changes/archive/2026-07-01-benchmark-whisper-cpu-dictation-models/benchmark_whisper_cpu_models.py \
  --sample /home/sciling/.cache/so_intelligence_tools/voice_translation_debug_audio/voice-translation-final-output-20260610-155636.wav \
  --models base small medium \
  --max-seconds 12 \
  --timeout-seconds 1200 \
  --transcription-timeout-seconds 240
```

Sample:

- Local WAV debug audio: `/home/sciling/.cache/so_intelligence_tools/voice_translation_debug_audio/voice-translation-final-output-20260610-155636.wav`
- Evaluated slice: 12.00 seconds
- Language: Spanish
- Human reference transcript: unavailable

Because no human reference transcript was available, quality was measured as word-level distance against the current `large-v3-turbo` output. Treat these quality numbers as regression screening, not as final ASR WER.

## Results

| Model | Status | Startup s | Transcription s | Audio s | RTF | Pseudo WER vs `large-v3-turbo` | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `large-v3-turbo` | ok | n/a | 7.14 | 12.00 | 0.60 | n/a | Keep as current quality baseline. |
| `base` | ok | 18.36 | 2.70 | 12.00 | 0.22 | 0.788 | Too much Spanish content loss. |
| `small` | ok | 12.37 | 2.26 | 12.00 | 0.19 | 0.697 | Fast, but too much rewording/loss. |
| `medium` | ok | 28.36 | 5.59 | 12.00 | 0.47 | 0.303 | Best smaller candidate, but modest latency win and visibly weaker text. |

Startup time includes temporary container startup, model download/cache fill, and readiness for that candidate. It is not the normal post-release latency once a model is already warm. The user-visible latency comparison is primarily `Transcription s` and `RTF`.

## Transcripts

`large-v3-turbo`:

```text
Ahora estoy hablando normal y ahora estoy hablando normal. Ok, ahora estoy hablando normal y ahora deberia empezar a cambiar y voy a hablar en otra lengua. He bajado un poco de audio.
```

`base`:

```text
Ok, ahora vamos a hablar normalmente y ahora vamos a empezar a cambiar y no estoy hablando de la otra lengua.
```

`small`:

```text
Ok, ahora estoy hablando normalmente y ahora deberia estar cambiando y estare hablando en la otra lengua. Me han bajado el audio un poco mas.
```

`medium`:

```text
Ahora estoy hablando normal y ahora... Ok, ahora estoy hablando normal y ahora se debe empezar a cambiar y voy a hablar en la otra lengua. He bajado el audio un poco mas.
```

## Cleanup Evidence

After the benchmark:

```bash
docker ps -a --filter name=so-ai-whisper-bench --format '{{.Names}}'
docker volume ls --filter name=so-ai-whisper-bench --format '{{.Name}}'
curl -fsS http://127.0.0.1:9000/v1/models
```

The temporary container and volume checks returned no rows. The production server still reported `large-v3-turbo`.

## Recommendation

Keep `large-v3-turbo` as the default on this CPU-only Linux workstation for now.

`small` and `base` are fast enough to reduce the post-release wait, but they lose too much Spanish content for quality-first dictation. `medium` is the only plausible lower-latency candidate, but on this sample it saved only about 1.6 seconds versus `large-v3-turbo` and still degraded the transcript. If this question comes up again, rerun the benchmark with two or three real dictated Spanish samples plus human reference transcripts before changing the default.

Durable spike evidence lives under `openspec/changes/archive/2026-07-01-benchmark-whisper-cpu-dictation-models/`.
