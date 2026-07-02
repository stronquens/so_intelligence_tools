# Chatterbox Latency Spikes

Date: 2026-07-02

Goal: compare the current PyTorch Chatterbox es-ES service against two speed-up paths:

- PyTorch optimized/faster fork path.
- ONNX Runtime path.

The reference latency problem was the Codex Desktop monitor metric where visible-message-to-playback-start took `20.849s`, with `20.763s` spent in synthesis.

## Current PyTorch Service

Evidence:

- `current-pytorch-http-cfg-and-chunking.json`
- `current-pytorch-direct-bf16-spike.json`

Best medium-text result in the current runtime was `cfg_weight=0.25`:

| Path | Text chars | Synthesis | Audio | RTF | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| HTTP, cfg `0.35` | 178 | `37.43s` | `9.04s` | `4.14` | Outlier/slow. |
| HTTP, cfg `0.25` | 178 | `12.64s` | `9.00s` | `1.40` | Best HTTP setting tested. |
| Direct Python, cfg `0.25` | 178 | `11.42s` | `8.96s` | `1.27` | Best direct setting tested. |

Chunking was the biggest user-facing win:

| Text | Mode | First audio latency |
| --- | --- | ---: |
| 288 chars | full request | `56.92s` |
| same text split into chunks | first chunk | `5.56s` |

Naive `bf16` on the current PyTorch runtime is not drop-in: it failed with a dtype mismatch in the T3 conditioning path (`Float` speaker embedding vs `BFloat16` weights).

## Fast/Faster Fork Path

Evidence:

- `fast-fork-runtime-spike.json`

The `rsxdalv/chatterbox` faster branch was not drop-in compatible with the current multilingual es-ES loader. Startup failed before synthesis:

```text
AttributeError("'LlamaConfig' object has no attribute 'rope_theta'")
```

Conclusion: this path may still be promising, but it needs adapter work against the es-ES multilingual config before it can be measured as a service candidate.

## ONNX Runtime Path

Evidence:

- `onnx-runtime-spike.json`
- `onnx_medium_measured_exag_0.5.wav`
- `onnx_medium_measured_exag_0.7.wav`

Source checked: Hugging Face model card for `onnx-community/chatterbox-multilingual-ONNX`, which documents ONNX Runtime usage, `language_id`, `target_voice_path`, CUDA provider support, and multilingual Chatterbox support.

Measured with `onnxruntime-gpu==1.22.0` because `onnxruntime-gpu==1.22.1` was not available for this Python environment.

| Exaggeration | Text chars | Synthesis | Audio | RTF | VRAM | Stop token |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `0.5` | 132 | `15.60s` | `15.34s` | `1.02` | `5739 MiB` | no |
| `0.7` | 132 | `15.74s` | `15.34s` | `1.03` | `5732 MiB` | no |

ONNX used `CUDAExecutionProvider` for all four sessions and loaded about `5505 MiB` VRAM. It reached good realtime factor, but this simple script did not emit the stop token before `max_new_tokens`, so latency stayed around 15-16 seconds and audio duration was too long for the prompt.

Conclusion: ONNX is not clearly better than the current PyTorch service for Codex yet. It may become useful if the generation loop is tuned to stop earlier or stream tokens/audio, but this first local spike does not beat current PyTorch plus chunking.

## Whisper + TTS Coexistence

User preference: if VRAM is tight, unload/pause Memanto Qwen embeddings before pausing Whisper.

After unloading `qwen3-embedding:0.6b`, Whisper and Chatterbox ran together:

| State | VRAM |
| --- | ---: |
| Whisper + Chatterbox ready, Qwen unloaded | `4237 MiB` |
| Short Chatterbox synthesis while Whisper stayed active | `4826 MiB` after request |

Coexistence smoke:

- Output: `coexistence_whisper_tts_cfg_0.25.wav`
- Wall time: `11.028s`
- Chatterbox synthesis: `10.836s`
- Audio: `5.20s`
- RTF: `2.084`

Conclusion: Whisper and Chatterbox fit together on the RTX 3070 when the Qwen embedding model is not resident in GPU memory. Keeping all three resident is still not recommended.

## Recommendation

For the current Codex/OpenClaw path, the best practical next step is not ONNX or the faster fork. It is:

1. Split visible assistant output into smaller speech chunks.
2. Start playback as soon as the first chunk is ready.
3. Trial `cfg_weight=0.25` for the selected female voice and listen for quality loss before making it the default.

This is the path that can realistically reduce perceived latency from about 20 seconds toward the 5-12 second range on this machine without replacing the deployed service.
