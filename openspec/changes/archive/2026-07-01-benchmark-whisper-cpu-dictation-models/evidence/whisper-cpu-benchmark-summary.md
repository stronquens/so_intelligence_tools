# Whisper CPU Model Benchmark

Sample: `/home/sciling/.cache/so_intelligence_tools/voice_translation_debug_audio/voice-translation-final-output-20260610-155636.wav`
Reference mode: large-v3-turbo pseudo-reference

| Model | Status | Startup s | Transcription s | Audio s | RTF | WER/distance |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| large-v3-turbo | ok |  | 7.14 | 12.00 | 0.60 |  |
| base | ok | 18.36 | 2.70 | 12.00 | 0.22 | 0.788 / 26 |
| small | ok | 12.37 | 2.26 | 12.00 | 0.19 | 0.697 / 23 |
| medium | ok | 28.36 | 5.59 | 12.00 | 0.47 | 0.303 / 10 |

## Transcripts

### large-v3-turbo (ok)

Ahora estoy hablando normal y ahora estoy hablando normal. Ok, ahora estoy hablando normal y ahora debería empezar a cambiar y voy a hablar en otra lengua. He bajado un poco de audio.

### base (ok)

Ok, ahora vamos a hablar normalmente y ahora vamos a empezar a cambiar y no estoy hablando de la otra lengua.

### small (ok)

Ok, ahora estoy hablando normalmente y ahora debería estar cambiando y estaré hablando en la otra lengua. Me han bajado el audio un poco más.

### medium (ok)

Ahora estoy hablando normal y ahora... Ok, ahora estoy hablando normal y ahora se debe empezar a cambiar y voy a hablar en la otra lengua. He bajado el audio un poco más.
