# Local TTS CPU Comparison

Run date: 2026-07-01.
Host profile: local Linux workstation, CPU-only, Python 3.11.8, 62 GiB RAM.
Selection outcome: Piper is the retained TTS candidate.
Retained audio evidence: 6 Piper WAV files, 1.9 MiB total.

Non-Piper generated WAVs and per-run metric files were removed after listening and selection so the repository does not keep discarded model artifacts. The research notes still document why Kokoro, NeuTTS, Qwen3-TTS, and Chatterbox were rejected for this CPU-only path.

## Retained Candidate

| Candidate | Local result | Mean synth time | Mean RTF | ASR WER proxy | Voices retained | Control tested | Audio examples | Recommendation |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- |
| Piper | Completed | 1.51 s | 0.21 | 7.3% mean, 12.0% max | es_ES-davefx-medium, es_ES-sharvard-medium | Different voices only; no explicit emotion API in this runner | [neutral](audio/piper__es_ES-davefx-medium__neutral.wav), [clear](audio/piper__es_ES-davefx-medium__clear.wav), [expressive](audio/piper__es_ES-davefx-medium__expressive.wav), [second voice](audio/piper__es_ES-sharvard-medium__expressive.wav) | Use as the first Docker baseline for CPU latency. |

## Discarded Candidates

| Candidate | Decision | Reason |
| --- | --- | --- |
| Kokoro ONNX | Removed from retained artifacts | Good intelligibility but slower than Piper; not selected as the first CPU Docker baseline. |
| NeuTTS Nano Spanish | Removed from retained artifacts | Spanish quality was promising, but CPU synthesis was about 3x slower than realtime. |
| Qwen3-TTS 0.6B CustomVoice | Removed from retained artifacts | Interesting natural-language control, but CPU synthesis was about 5x slower than realtime. |
| Chatterbox Multilingual | Removed from retained artifacts | Expressive controls worked, but it was the slowest measured candidate on CPU. |

## Detailed Piper Timing

| Candidate | Voice | Prompt | Synth s | Audio s | RTF | Audio |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Piper | es_ES-davefx-medium | neutral | 1.50 | 5.58 | 0.27 | [wav](audio/piper__es_ES-davefx-medium__neutral.wav) |
| Piper | es_ES-davefx-medium | clear | 1.59 | 8.08 | 0.20 | [wav](audio/piper__es_ES-davefx-medium__clear.wav) |
| Piper | es_ES-davefx-medium | expressive | 1.55 | 7.78 | 0.20 | [wav](audio/piper__es_ES-davefx-medium__expressive.wav) |
| Piper | es_ES-sharvard-medium | neutral | 1.41 | 6.08 | 0.23 | [wav](audio/piper__es_ES-sharvard-medium__neutral.wav) |
| Piper | es_ES-sharvard-medium | clear | 1.50 | 8.68 | 0.17 | [wav](audio/piper__es_ES-sharvard-medium__clear.wav) |
| Piper | es_ES-sharvard-medium | expressive | 1.49 | 8.34 | 0.18 | [wav](audio/piper__es_ES-sharvard-medium__expressive.wav) |

## Quality Proxy

The quality number is Whisper ASR word error rate against the original text. It is only a proxy for intelligibility; it does not measure naturalness, emotion, speaker preference, or whether the voice feels pleasant for daily use.

| Candidate | Mean WER | Max WER | Notes |
| --- | ---: | ---: | --- |
| Piper | 7.3% | 12.0% | Neutral prompts transcribed perfectly after normalization; the repeated error was around `Espana` being heard as `hispana`. |

## Prompt Set

- `neutral`: Hola, estoy probando una voz local en espanol para integrarla con mis herramientas del sistema operativo.
- `clear`: Cuando suelte el atajo, quiero que el sistema responda con una voz clara, natural y rapida. La pronunciacion en espanol de Espana me importa bastante.
- `expressive`: Vale, esto ya empieza a sonar mejor. Dilo con un tono tranquilo, cercano y un poco entusiasmado, como si explicaras algo util a un companero.

## Reproduce

```bash
poetry run python openspec/changes/benchmark-local-tts-cpu-models/benchmark_tts_cpu_models.py --candidates piper
poetry run python openspec/changes/benchmark-local-tts-cpu-models/score_tts_outputs_with_whisper.py
```
