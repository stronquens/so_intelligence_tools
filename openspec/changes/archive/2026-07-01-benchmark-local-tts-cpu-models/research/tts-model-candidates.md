# Local TTS CPU Candidate Research

Date: 2026-07-01

Scope: Spanish local TTS on a CPU-only Linux workstation, eventually served behind a Dockerized local text-to-speech API.

## Summary Ranking For This Machine

| Rank | Candidate | CPU expectation | Spanish support | Control / cloning | First-pass decision |
| ---: | --- | --- | --- | --- | --- |
| 1 | Piper Spanish voices | Very likely fast on CPU | Spanish voices available, including Spain Spanish | Low control, voice-per-model | Benchmark first as speed baseline. |
| 2 | Kokoro 82M / Kokoro ONNX | Very likely fast on CPU | Multilingual, but Spanish quality must be checked | Voice selection/blending depending runtime | Benchmark first as small neural quality/speed candidate. |
| 3 | NeuTTS Nano Spanish | Designed for CPU/on-device | Spanish-only model exists | Instant voice cloning with reference audio | Benchmark first; promising if install/runtime is not heavy. |
| 4 | Chatterbox Multilingual V3 / Spanish packs | CPU possible in API, but likely slower | Multilingual `es` plus `es-es` and `es-mx-latam` packs | Voice cloning, CFG/exaggeration style controls | Feasibility probe after small models. |
| 5 | Qwen3-TTS 0.6B / 1.7B | Official path appears GPU-oriented | Spanish supported | Natural-language instruction control, voice clone/design | Research strongly; CPU probe only with tight cleanup/time limits or a CPU/GGUF runtime. |

## Candidate Notes

### Chatterbox Multilingual V3

Primary sources:

- GitHub: https://github.com/resemble-ai/chatterbox
- Hugging Face: https://huggingface.co/ResembleAI/chatterbox

Findings:

- Chatterbox is a Resemble AI open-source TTS family.
- Multilingual V3 keeps a 0.5B model size and targets improved speaker similarity, fewer hallucinations, and more natural multilingual speech.
- The general multilingual model supports Spanish via `language_id="es"`.
- Dedicated language packs include Spain Spanish (`es-es`) and Latam Spanish (`es-mx-latam`).
- Install path is `pip install chatterbox-tts`; source install notes mention Python 3.11 and Debian 11 testing.
- Runtime examples allow `device = "cuda"  # or "cpu" / "mps"`, so a CPU feasibility test is legitimate, but not guaranteed to be fast.

Expected role:

- Quality/control candidate, especially for voice cloning and expressive generation.
- Probably not the first production default on CPU unless benchmark latency is acceptable.

### Qwen3-TTS 0.6B / 1.7B

Primary sources:

- GitHub: https://github.com/QwenLM/Qwen3-TTS
- Hugging Face 1.7B Base: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base
- Hugging Face 0.6B CustomVoice: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice

Findings:

- Qwen3-TTS supports Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, and Italian.
- Released variants include 1.7B VoiceDesign, 1.7B CustomVoice, 1.7B Base, 0.6B CustomVoice, and 0.6B Base.
- It supports streaming generation and natural-language control of tone, speaking rate, emotion, prosody, timbre, and voice design/clone workflows.
- Model cards report end-to-end synthesis latency "as low as 97ms" for optimized streaming generation.
- Official examples load models with `device_map="cuda:0"`, `torch.bfloat16`, and `flash_attention_2`; docs recommend FlashAttention 2 to reduce GPU memory.
- Official environment setup recommends a fresh Python 3.12 environment.

Expected role:

- Most interesting for natural-language control, but highest CPU risk.
- For this CPU-only machine, test `0.6B` before `1.7B`.
- If official CPU is impractical, consider a separate community CPU/GGUF probe, but keep that result clearly labeled as not the official runtime.

### Piper

Primary sources:

- GitHub: https://github.com/rhasspy/piper
- Current development note/source: https://github.com/OHF-Voice/piper1-gpl
- Voices: https://huggingface.co/rhasspy/piper-voices
- Samples: https://rhasspy.github.io/piper-samples/

Findings:

- Piper is a fast, local neural TTS system.
- Official voice repository contains ONNX voices and lists 35 languages.
- Spanish samples are available, including Spanish Argentina and Spanish Spain.
- Spain Spanish voices in the Piper voice tree include options such as `carlfm`, `davefx`, `mls_10246`, `mls_9972`, and `sharvard` at different quality levels.

Expected role:

- CPU speed baseline and likely first "it works now" local TTS backend.
- Lower expressive/control ceiling than Qwen/Chatterbox/NeuTTS.

### Kokoro 82M / Kokoro ONNX

Primary sources:

- Model card: https://huggingface.co/hexgrad/Kokoro-82M
- ONNX model: https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX

Findings:

- Kokoro is an 82M-parameter open-weight TTS model.
- The model card emphasizes small size, speed, and Apache-licensed weights.
- ONNX community release provides quantization choices including `q8`, `q4`, and other dtypes through JavaScript/Python usage.
- Python usage depends on Kokoro's pipeline and G2P tooling; ONNX usage may be cleaner for Docker CPU benchmarking.

Expected role:

- Strong speed/quality candidate for CPU.
- Need Spanish-specific listening test because official examples often highlight English voices and general multilingual support.

### NeuTTS Nano Spanish

Primary sources:

- GitHub: https://github.com/neuphonic/neutts
- Spanish model: https://huggingface.co/neuphonic/neutts-nano-spanish
- Multilingual collection: https://huggingface.co/collections/neuphonic/neutts-nano-multilingual-collection

Findings:

- NeuTTS Nano Spanish is a Spanish-only TTS model in the NeuTTS Nano multilingual collection.
- The model card describes it as on-device, CPU-friendly, and optimized for real-time generation on laptop-class CPUs.
- It supports instant voice cloning from a few seconds of reference audio.
- The multilingual collection describes Nano as 0.2B and CPU real-time.
- GGUF quantizations are available for efficient on-device deployment.
- For non-English backbones, the GitHub docs recommend same-language reference audio for best performance.

Expected role:

- Very promising CPU candidate if the runtime can be made reproducible in Docker.
- Test with a Spanish reference clip and transcript, not only default/example voice.

## Proposed Benchmark Order

1. Piper Spanish Spain voice (`es_ES-davefx-medium` or `es_ES-sharvard-medium`) as speed baseline.
2. Kokoro ONNX quantized (`q8` first, optionally `q4`) for small neural model performance.
3. NeuTTS Nano Spanish Q4/Q8 GGUF or Python runtime, depending on reproducibility.
4. Chatterbox Multilingual V3 `es` and, if feasible, Spain Spanish language pack.
5. Qwen3-TTS 0.6B CustomVoice/Base feasibility probe; only attempt 1.7B if 0.6B is remotely usable on CPU.

## Benchmark Prompts

Short prompt:

```text
Hola, estoy probando una voz local en español para integrarla con mis herramientas del sistema operativo.
```

Medium prompt:

```text
Cuando suelte el atajo, quiero que el sistema responda con una voz clara, natural y rápida. La pronunciación en español de España me importa bastante.
```

Expressive prompt:

```text
Vale, esto ya empieza a sonar mejor. Dilo con un tono tranquilo, cercano y un poco entusiasmado, como si explicaras algo útil a un compañero.
```

## Metrics

- `startup_seconds`: time until runtime is ready.
- `synthesis_seconds`: wall time to generate output audio from text.
- `audio_duration_seconds`: generated WAV duration.
- `realtime_factor`: `synthesis_seconds / audio_duration_seconds`.
- `disk_bytes_downloaded`: approximate candidate cache size when measurable.
- `cpu_feasible`: yes/no with reason.
- Subjective notes: Spanish pronunciation, naturalness, prosody, artifacts, voice control, and stability.
