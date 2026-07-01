# Local TTS CPU Benchmark

This retained evidence has been pruned after model selection. Piper is the selected candidate; non-Piper generated WAV files and per-run metric files were removed so the repository does not keep discarded model artifacts.

## Results

| Candidate | Voice | Prompt | Status | Setup s | Synth s | Audio s | RTF | Output | Notes |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| piper | es_ES-davefx-medium | neutral | ok | 22.31 | 1.50 | 5.58 | 0.27 | evidence/audio/piper__es_ES-davefx-medium__neutral.wav | Piper has no explicit emotion control; emotion is only represented by prompt wording. |
| piper | es_ES-davefx-medium | clear | ok | 22.31 | 1.59 | 8.08 | 0.20 | evidence/audio/piper__es_ES-davefx-medium__clear.wav | Piper has no explicit emotion control; emotion is only represented by prompt wording. |
| piper | es_ES-davefx-medium | expressive | ok | 22.31 | 1.55 | 7.78 | 0.20 | evidence/audio/piper__es_ES-davefx-medium__expressive.wav | Piper has no explicit emotion control; emotion is only represented by prompt wording. |
| piper | es_ES-sharvard-medium | neutral | ok | 22.31 | 1.41 | 6.08 | 0.23 | evidence/audio/piper__es_ES-sharvard-medium__neutral.wav | Piper has no explicit emotion control; emotion is only represented by prompt wording. |
| piper | es_ES-sharvard-medium | clear | ok | 22.31 | 1.50 | 8.68 | 0.17 | evidence/audio/piper__es_ES-sharvard-medium__clear.wav | Piper has no explicit emotion control; emotion is only represented by prompt wording. |
| piper | es_ES-sharvard-medium | expressive | ok | 22.31 | 1.49 | 8.34 | 0.18 | evidence/audio/piper__es_ES-sharvard-medium__expressive.wav | Piper has no explicit emotion control; emotion is only represented by prompt wording. |

## Prompts

### neutral

Hola, estoy probando una voz local en espanol para integrarla con mis herramientas del sistema operativo.

### clear

Cuando suelte el atajo, quiero que el sistema responda con una voz clara, natural y rapida. La pronunciacion en espanol de Espana me importa bastante.

### expressive

Vale, esto ya empieza a sonar mejor. Dilo con un tono tranquilo, cercano y un poco entusiasmado, como si explicaras algo util a un companero.

## Reproduce

Run `poetry run python openspec/changes/benchmark-local-tts-cpu-models/benchmark_tts_cpu_models.py --candidates piper`.
