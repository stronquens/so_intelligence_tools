# Runtime Spike: Nemotron 3.5 ASR Streaming

## Objective

Compare whether the first implementation should run Nemotron 3.5 ASR Streaming through Ollama, or through a Dockerized NVIDIA runtime such as NIM/NeMo.

## External Findings

- NVIDIA describes `nvidia/nemotron-3.5-asr-streaming-0.6b` as a 600M parameter multilingual streaming ASR model with 40 language-locales, punctuation/capitalization, and NeMo 26.06+ support.
- The previous English Nemotron ASR streaming model documents a Cache-Aware FastConformer-RNNT streaming architecture with configurable chunks of 80ms, 160ms, 560ms, and 1120ms.
- NVIDIA NeMo release notes describe Nemotron 3.5 ASR Streaming 0.6B as controllable latency, roughly 80ms to 1s, and GPU-oriented.
- NVIDIA Speech NIM exposes ASR through streaming/offline APIs, including a realtime WebSocket path, which matches the application's desired adapter shape.
- I did not find an official Ollama path for Nemotron ASR audio streaming. Local Ollama also does not know the expected model name.

Sources:

- https://huggingface.co/blog/nvidia/fine-tuning-nemotron-35-asr
- https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b
- https://github.com/NVIDIA-NeMo/NeMo
- https://docs.nvidia.com/nim/speech/latest/asr/customization/customization.html
- https://build.nvidia.com/explore/speech

## Local Environment Probe

Commands run on 2026-06-12:

```text
$ ollama --version
ollama version is 0.30.5

$ ollama list
NAME                 ID              SIZE      MODIFIED
gemma4:e2b-it-qat    8ccf136fdd52    4.3 GB    4 days ago

$ ollama show nvidia/nemotron-3.5-asr-streaming-0.6b
Error: model 'nvidia/nemotron-3.5-asr-streaming-0.6b:latest' not found

$ docker --version
Docker version 29.5.3, build d1c06ef

$ docker compose version
Docker Compose version v2.35.1-desktop.1

$ docker info --format 'OSType={{.OSType}} Architecture={{.Architecture}} Runtimes={{json .Runtimes}}'
OSType=linux Architecture=x86_64 Runtimes={"io.containerd.runc.v2":...,"runc":...}

$ nvidia-smi
command not found

$ ls /dev/nvidia*
no NVIDIA devices found

$ python --version
Python 3.11.8

$ poetry run python --version
Python 3.11.8
```

## ONNX CPU Follow-up

After the initial GPU/NIM spike, we tested a CPU path with `onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4`.

Additional sources:

- https://huggingface.co/onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4
- https://onnxruntime.ai/docs/genai/api/python.html
- https://github.com/microsoft/onnxruntime-genai/blob/main/docs/RuntimeOptions.md

Local setup:

```text
$ poetry add --group dev onnxruntime-genai huggingface-hub soundfile numpy
onnxruntime-genai 0.14.1
onnxruntime 1.26.0
huggingface-hub 1.19.0
soundfile 0.14.0
numpy 2.4.6
```

Model footprint:

```text
Repository: onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4
Downloaded size: ~756.6 MB
Files: encoder.onnx(.data), decoder.onnx(.data), joint.onnx(.data), tokenizer, Silero VAD and config files
```

Load test:

```text
cuda False openvino True
loaded 0.74 s
model type: nemotron_speech
device: CPU
```

The generic `MultiModalProcessor` API does not support this model type:

```text
RuntimeError: MultiModalProcessor cannot be created. nemotron_speech is not a registered multi-modal model type.
```

The working path is the Nemotron speech streaming path:

- `model.create_streaming_processor()`
- `og.Tokenizer(model)`
- `og.Generator(model, params)`
- `generator.set_runtime_option("lang_id", "2")` for `es-ES`
- `processor.process(audio_chunk)` with 16 kHz mono float32 chunks
- `processor.flush()` at the end of the push-to-talk session

Performance test with `/home/sciling/Descargas/WhatsApp Ptt 2026-06-12 at 12.56.20.ogg`:

```text
Input: OGG/Opus, mono, 48 kHz, 44.654 s
Resample: local float32 mono 16 kHz
Chunk: 8960 samples, 560 ms
Provider: CPUExecutionProvider
Model load: 0.70 s
Transcription elapsed: 29.47 s
RTF: 0.66
```

Output:

```text
Vale, cuando quieras activado he cambiado al micro virtual General switching on the live transcription I'm going to start talking and you speak to every now and then to check the delay from when you speak until it comes through the speakers or whatever and we'll test a few things too
```

A shorter 12 s slice transcribed in 9.76 s, RTF 0.81.

OpenVINO was not selected:

```text
RuntimeError: OpenVINOExecutionProvider execution provider is not supported in this build.
```

Even though `onnxruntime_genai.is_openvino_available()` returned `True`, the installed wheel did not support appending `OpenVINOExecutionProvider`.

## Conclusion

Ollama is not the selected runtime path for the first Nemotron dictation implementation. It is present locally and works for the existing Gemma setup, but there is no verified official audio-streaming ASR path for Nemotron 3.5 ASR through Ollama, and the expected model name is not available to this Ollama installation.

The preferred implementation path for this machine is now the ONNX INT4 CPU runtime behind `StreamingAsrTranscriber`. It runs locally, loads quickly, avoids the missing NVIDIA GPU/runtime blocker, and transcribes faster than real time on the available test audio.

NVIDIA Speech NIM/NeMo should remain the higher-performance GPU path for future setups with a compatible NVIDIA runtime. The app should still keep dependency checks explicit because CPU performance may vary by machine.

## Implementation Implications

- Keep Ollama out of the critical path for this feature unless a later verified ASR audio-streaming Ollama runtime appears.
- Add an ONNX CPU adapter skeleton first, with clear preflight checks for `onnxruntime-genai`, model files, audio sample rate conversion and language id support.
- Keep Docker/NVIDIA NIM/NeMo as an optional accelerated backend for future machines with GPU runtime support.
- Keep the adapter boundary small: the dictation UX should depend only on `StreamingAsrTranscriber` events, not on NIM/NeMo-specific client details.
- Do not install NeMo directly into the project Poetry environment in this phase. The current project Python is 3.11.8, while NVIDIA NeMo Speech requirements point to newer Python/PyTorch/GPU assumptions; containerizing isolates that stack.
- Provide a clear "runtime unavailable" overlay/notification when neither the ONNX CPU runtime nor an accelerated backend is available.
