# Validation

Date: 2026-07-01.
Host: local Linux workstation, CPU-only.

## Commands Run

```bash
poetry run openspec validate benchmark-local-tts-cpu-models --strict
poetry run python openspec/changes/benchmark-local-tts-cpu-models/benchmark_tts_cpu_models.py --candidates piper kokoro neutts-probe chatterbox-probe qwen-probe --probe-timeout-seconds 180
curl -fsS http://127.0.0.1:9000/v1/models
poetry run python -m py_compile openspec/changes/benchmark-local-tts-cpu-models/score_tts_outputs_with_whisper.py
poetry run python openspec/changes/benchmark-local-tts-cpu-models/score_tts_outputs_with_whisper.py
python -m venv /tmp/so-ai-tts-neutts-*/venv && pip install "neutts[onnx]" soundfile
python -m venv /tmp/so-ai-tts-chatterbox-*/venv && pip install chatterbox-tts soundfile
python -m venv /tmp/so-ai-tts-qwen-*/venv && pip install qwen-tts soundfile
find /tmp -maxdepth 1 \( -name 'so-ai-tts-*' -o -name 'tts-*probe*' \) -print
docker ps -a --filter name=so-ai-tts-bench --format '{{.Names}}'
docker volume ls --filter name=so-ai-tts-bench --format '{{.Name}}'
rm -f evidence/audio/kokoro_onnx__*.wav evidence/audio/neutts_nano_spanish__*.wav evidence/audio/qwen3_tts_0_6b_customvoice__*.wav evidence/audio/chatterbox_multilingual__*.wav
jq '.results |= map(select(.candidate == "piper"))' evidence/tts-cpu-benchmark-results.json
jq '.results |= map(select(.candidate == "piper"))' evidence/tts-asr-quality-results.json
docker ps -a --format '{{.ID}} {{.Image}} {{.Names}} {{.Status}}' | rg -i 'tts|piper|kokoro|qwen|chatter|neutts|so-ai'
docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}' | rg -i 'tts|piper|kokoro|qwen|chatter|neutts|so-ai'
docker volume ls --format '{{.Name}}' | rg -i 'tts|piper|kokoro|qwen|chatter|neutts|so-ai'
```

## Evidence

- Raw benchmark results: `evidence/tts-cpu-benchmark-results.json`.
- Timing summary: `evidence/tts-cpu-benchmark-summary.md`.
- ASR quality proxy results: `evidence/tts-asr-quality-results.json`.
- ASR quality proxy summary: `evidence/tts-asr-quality-summary.md`.
- Human comparison table: `evidence/tts-cpu-comparison.md`.
- Retained audio samples: `evidence/audio/piper__*.wav`.

## Results

Piper completed successfully for two Spanish voices and three Spanish prompts. Mean synthesis time was 1.51 seconds for 7.42 seconds of generated audio, with mean realtime factor 0.21.

Kokoro ONNX completed successfully for two voices and three Spanish prompts. Mean synthesis time was 3.13 seconds for 7.60 seconds of generated audio, with mean realtime factor 0.42.

NeuTTS Nano Spanish completed successfully with the official `mateo` Spanish reference sample. Mean synthesis time was 27.20 seconds for 8.63 seconds of generated audio, with mean realtime factor 3.16.

Qwen3-TTS 0.6B CustomVoice completed successfully through the `qwen-tts` CPU fallback without `flash-attn`. Mean synthesis time was 52.27 seconds for 10.02 seconds of generated audio, with mean realtime factor 5.24. Ryan was tested for the three common prompts and Aiden was tested as a second voice on a shorter prompt.

Chatterbox Multilingual completed successfully through `chatterbox-tts` 0.1.7 on CPU. Mean synthesis time was 47.95 seconds for 7.17 seconds of generated audio, with mean realtime factor 6.74. The PyPI API supports `language_id`, `exaggeration`, and `cfg_weight`; the current README's `t3_model="v3"` argument was not accepted by the installed 0.1.7 package.

Whisper ASR quality proxy stayed broadly similar for the intelligible candidates: Piper mean WER 7.3%, Kokoro ONNX mean WER 6.7%, NeuTTS Nano Spanish mean WER 6.7%, Qwen3-TTS 0.6B CustomVoice mean WER 6.8%, and Chatterbox Multilingual mean WER 10.1%. This measures intelligibility only and does not replace subjective listening for naturalness, emotion, or speaker preference.

## Cleanup

No `/tmp/so-ai-tts-*` or `/tmp/tts-*probe*` directories remained after cleanup. The Chatterbox probe initially created `~/.pkuseg`; that directory was removed after rerunning with `HOME` redirected to a temporary benchmark root. No Docker containers or volumes were created by the benchmark. The only retained artifacts are the benchmark evidence files and generated WAV samples inside this OpenSpec change.

After the user listened to the generated samples and selected Piper as the practical default, retained evidence was pruned to Piper only. Removed artifacts:

- Kokoro ONNX generated WAV files.
- NeuTTS Nano Spanish generated WAV files and per-run metrics.
- Qwen3-TTS generated WAV files and per-run metrics.
- Chatterbox generated WAV files and per-run metrics.

The aggregate benchmark and ASR JSON files were filtered to Piper rows only so retained summaries do not point to removed audio. Docker inspection found no TTS benchmark containers, images, or volumes to remove. The global Hugging Face cache did not contain the TTS model repos from the spike; large existing non-TTS caches such as Nemotron, embeddings, and CLIP were left untouched. A pre-existing `/home/sciling/.lmstudio/hub/models/qwen` directory was also left untouched because it was outside this benchmark and not created by these tests.

## Recommendation

Use Piper as the first Docker TTS baseline for this machine because it is fastest, simple, and already good enough for an initial CPU-only local service. Keep Kokoro ONNX as the quality challenger: it is roughly twice as slow in this run but still below realtime and may sound more natural depending on listening preference. NeuTTS Nano Spanish is the best of the larger CPU-only tests for Spanish focus, but it is still about 3x slower than realtime. Defer Qwen3-TTS and Chatterbox for this CPU-only machine unless natural-language control or expressive cloning is more important than latency.
