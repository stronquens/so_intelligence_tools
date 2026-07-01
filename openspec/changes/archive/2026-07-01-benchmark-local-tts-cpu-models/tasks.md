## 1. Research

- [x] 1.1 Collect primary-source notes for Chatterbox, Qwen3-TTS, Piper, Kokoro ONNX, and NeuTTS Nano Spanish.
- [x] 1.2 Rank candidates by CPU feasibility, Spanish support, quality/control promise, and integration risk.

## 2. Benchmark Design

- [x] 2.1 Define a common Spanish prompt set and optional reference-voice sample strategy.
- [x] 2.2 Design isolated Docker/cache cleanup rules for model downloads.
- [x] 2.3 Define metrics and output artifact schema for TTS benchmark runs.

## 3. Implementation Spike

- [x] 3.1 Add benchmark scripts or candidate runners under this change.
- [x] 3.2 Run first-pass CPU benchmarks for feasible small candidates.
- [x] 3.3 Attempt feasibility probes for Chatterbox and Qwen3-TTS without retaining downloaded weights.

## 4. Validation

- [x] 4.1 Save raw benchmark results and generated samples under this change.
- [x] 4.2 Verify no temporary benchmark containers, volumes, or model caches remain.
- [x] 4.3 Record findings, caveats, and recommendation in `validation.md`.

## 5. Missing Model Benchmark Extension

- [x] 5.1 Add isolated runners for NeuTTS Nano Spanish, Chatterbox, and Qwen3-TTS where practical.
- [x] 5.2 Run CPU synthesis or bounded feasibility attempts for the remaining candidates.
- [x] 5.3 Update comparison tables, ASR quality proxy, cleanup evidence, and recommendation.

## 6. Post-Selection Cleanup

- [x] 6.1 Remove non-Piper generated WAV samples and per-run metric files after Piper selection.
- [x] 6.2 Prune retained benchmark and ASR result JSON to Piper rows only.
- [x] 6.3 Verify no non-Piper TTS Docker artifacts, temporary caches, or benchmark model directories remain.
- [x] 6.4 Update retained summaries and validation notes to document the cleanup.
