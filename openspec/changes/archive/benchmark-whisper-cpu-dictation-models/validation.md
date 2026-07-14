# Validation

## Benchmark Command

```bash
poetry run python openspec/changes/benchmark-whisper-cpu-dictation-models/benchmark_whisper_cpu_models.py \
  --sample /home/sciling/.cache/so_intelligence_tools/voice_translation_debug_audio/voice-translation-final-output-20260610-155636.wav \
  --models base small medium \
  --max-seconds 12 \
  --timeout-seconds 1200 \
  --transcription-timeout-seconds 240
```

## Evidence

- Raw results: `evidence/whisper-cpu-benchmark-results.json`
- Summary: `evidence/whisper-cpu-benchmark-summary.md`
- Operational documentation: `docs/whisper-cpu-benchmark-linux.md`
- Linked from: `docs/push-to-talk-dictation.md`, `docs/whisper-docker.md`, and `docs/README.md`

| Model | Transcription s | Audio s | RTF | Pseudo WER vs large-v3-turbo | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| `large-v3-turbo` | 7.14 | 12.00 | 0.60 | n/a | Current warm production baseline. |
| `base` | 2.70 | 12.00 | 0.22 | 0.788 | Too much content loss for quality-first Spanish dictation. |
| `small` | 2.26 | 12.00 | 0.19 | 0.697 | Fastest candidate, but loses/rewords too much content. |
| `medium` | 5.59 | 12.00 | 0.47 | 0.303 | Best candidate among smaller models, but only saves about 1.6 s on this sample and still changes wording. |

## Cleanup Checks

```bash
docker ps -a --filter name=so-ai-whisper-bench --format '{{.Names}}'
docker volume ls --filter name=so-ai-whisper-bench --format '{{.Name}}'
curl -fsS http://127.0.0.1:9000/v1/models
```

Both Docker cleanup commands returned no rows after the benchmark. The production server still reported `large-v3-turbo` at `http://127.0.0.1:9000/v1/models`.

## Caveats

- The sample is a real Spanish audio clip from local debug audio, but no human reference transcript was available.
- Quality metrics are pseudo-reference evidence against the current `large-v3-turbo` output, so they are useful for regression screening but not a final ASR quality score.
- Candidate startup time includes temporary model download/load and is not the post-release dictation latency users feel once a model is warm.

## Recommendation

Do not change the default from `large-v3-turbo` based on this spike. `medium` is the only plausible lower-latency candidate, but the measured saving is modest and the transcript is visibly weaker. `small` and `base` are fast enough to reduce lag, but they lose too much Spanish content for a quality-first workflow.
