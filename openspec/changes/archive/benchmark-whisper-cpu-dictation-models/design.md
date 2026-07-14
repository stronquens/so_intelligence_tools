## Context

The active Docker server is `hwdsl2/whisper-server:latest` on `127.0.0.1:9000` with `WHISPER_MODEL=large-v3-turbo`, `WHISPER_DEVICE=cpu`, `WHISPER_COMPUTE_TYPE=int8`, and `WHISPER_BEAM=1`. The model is warm, but the current HTTP API performs final transcription after the user releases the shortcut.

## Goals / Non-Goals

**Goals:**

- Compare CPU latency and transcript quality across selected Whisper model variants.
- Keep the current running Docker service and its model volume intact.
- Remove temporary benchmark containers and volumes even if a benchmark fails.

**Non-Goals:**

- Change the product default model in this spike.
- Keep downloaded benchmark model weights after the spike.
- Treat synthetic or non-dictation audio as final quality evidence.

## Decisions

- Use the current server as the baseline for `large-v3-turbo` instead of redownloading it in a temporary volume.
- Start each candidate model in a separate temporary container on a separate localhost port with a temporary Docker volume.
- Remove each temporary container and volume after measuring that candidate.
- Store scripts and result summaries under the change directory as durable evidence.
- If no human reference transcript is available, compute quality as candidate-vs-baseline edit distance and label it as pseudo-reference evidence.

## Risks / Trade-offs

- Candidate startup includes model download time; transcription latency should be reported separately from startup/download.
- A pseudo-reference can miss cases where the baseline is wrong. A final model choice should use real Spanish dictation samples with expected transcripts.
- Some candidate model names may not be supported by the Docker image; failed candidates should be recorded without leaving containers or volumes.
