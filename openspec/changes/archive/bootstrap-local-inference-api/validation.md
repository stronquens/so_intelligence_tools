## Local Spike: Ollama + Gemma 4 E2B on CPU-only Laptop

Date: 2026-06-05

### Environment

- Host: Linux laptop without dedicated GPU
- RAM observed by Ollama: 62.5 GiB total
- Available RAM observed by Ollama during startup: 53.7 GiB
- Compute mode used by Ollama: CPU-only
- Ollama version before update: 0.21.0
- Ollama version after update: 0.30.5

### Important Runtime Finding

The first attempt with `ollama 0.21.0` failed to run Gemma 4 GGUF models from Unsloth.

Observed error:

`unknown model architecture: 'gemma4'`

Conclusion:

- Gemma 4 benchmarking on this project requires a newer Ollama runtime.
- Updating to `0.30.5` resolved the architecture-loading blocker.

The same compatibility constraint also affected the Docker stack:

- an initial container run using a too-old Ollama image surfaced runtime version `0.13.0`
- the model could be downloaded inside the volume, but requests failed when loading it
- pinning the compose service to `ollama/ollama:0.30.5` aligned container behavior with the validated host runtime

### Models Evaluated

1. `hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL`
2. `hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q8_K_XL`

### Method

- API used: `POST /api/generate` on Ollama
- Mode: non-streaming
- Temperature: `0`
- `num_predict`: `96`
- Keep-alive: `10m`
- Prompt set:
  - short factual reply in Spanish
  - rewrite in Spanish
  - light reasoning list in Spanish

### Results

#### Q4: `UD-Q4_K_XL`

- Ollama model size shown by `ollama list`: `4.2 GB`
- Cold first response wall time: `6.079 s`
- Cold load time: `4.296 s`
- Average wall time across 3 prompts: `6.201 s`
- Average prompt throughput: `86.99 tok/s`
- Average generation throughput: `17.55 tok/s`

Detailed runs:

- Short response:
  - wall: `6.079 s`
  - load: `4.296 s`
  - prompt eval: `0.335 s`
  - generation eval: `1.442 s`
  - generation speed: `17.34 tok/s`

- Rewrite:
  - wall: `6.272 s`
  - load: `0.425 s`
  - generation eval: `5.384 s`
  - generation speed: `17.83 tok/s`

- Light reasoning:
  - wall: `6.252 s`
  - load: `0.391 s`
  - generation eval: `5.489 s`
  - generation speed: `17.49 tok/s`

#### Q8: `UD-Q8_K_XL`

- Ollama model size shown by `ollama list`: `6.3 GB`
- Runtime footprint shown by `ollama ps`: `6.6 GB`
- Cold first response wall time: `6.994 s`
- Cold load time: `4.895 s`
- Average wall time across 3 prompts: `8.136 s`
- Average prompt throughput: `71.59 tok/s`
- Average generation throughput: `12.48 tok/s`

Detailed runs:

- Short response:
  - wall: `6.994 s`
  - load: `4.895 s`
  - prompt eval: `0.473 s`
  - generation eval: `1.621 s`
  - generation speed: `12.96 tok/s`

- Rewrite:
  - wall: `8.642 s`
  - load: `0.386 s`
  - generation eval: `7.772 s`
  - generation speed: `12.35 tok/s`

- Light reasoning:
  - wall: `8.771 s`
  - load: `0.392 s`
  - generation eval: `7.916 s`
  - generation speed: `12.13 tok/s`

### Comparison Summary

- `Q4` is about `40%` faster than `Q8` for generation on this CPU-only machine.
- `Q4` reduces average wall time by about `1.9 s` versus `Q8`.
- `Q4` uses materially less memory and disk than `Q8`.
- `Q8` did not show a decisive enough quality improvement in these short tests to justify the latency penalty for the default local experience.

### Recommendation For This Project

For a Linux laptop without dedicated GPU:

- default `instant` profile: `Gemma 4 E2B Unsloth UD-Q4_K_XL`
- optional slower profile to explore later: `Gemma 4 E2B Unsloth UD-Q8_K_XL`

Current recommendation:

- start implementation and API validation with `Q4`
- keep `Q8` only as an optional comparison target, not as the default runtime

### Design Implications

- The first local profile should be optimized for CPU-only operation.
- Quantized small multimodal models are more appropriate than larger or less aggressively quantized variants for the initial UX.
- The `reasoning_mode` contract should not assume that a slower quantization automatically gives a good "smart" profile on laptops without dedicated GPU.
- A second profile may still be useful later, but should probably be a separately validated runtime rather than the default path.

## API Validation After Implementation

The first implementation was validated locally against the updated Ollama runtime and the validated `Q4` model.

### Validated Endpoints

- `GET /health`
- `GET /status`
- `POST /v1/text/generate`
- `POST /v1/image/extract-text`

### Observed Results

#### Health endpoint

- Returned `200 OK`
- Response:
  - `{"status":"ok","service":"local-inference-api"}`

#### Status endpoint

- Returned `200 OK`
- Confirmed:
  - Ollama reachable
  - Ollama version `0.30.5`
  - configured model available
  - current reasoning mapping message for Gemma 4

#### Text generation endpoint

- Returned `200 OK`
- Test prompt:
  - short Spanish explanation of Linux
- Returned OpenAI-compatible response envelope with:
  - `id`
  - `object=chat.completion`
  - `model`
  - `choices`
  - `usage`
  - `reasoning_mode_requested`
  - `reasoning_strategy_applied`

#### Image extraction endpoint

- Returned `200 OK`
- Test image:
  - generated PNG containing the text `Test 123`
- Response content:
  - `Test 123`

### Current Known Limits

- The first implementation uses Gemma 4 thinking as a binary internal mapping:
  - `off|low` -> thinking off
  - `medium|high` -> thinking on
- The first implementation exposes OpenAI-compatible response envelopes, but not the full OpenAI API surface.
- The current Docker validation covers startup, model pull, runtime status, one real text request and clean shutdown.

## Automated Validation

The change also includes automated Python tests so validation does not depend only on manual runs against Ollama.

### Covered Areas

- `GET /health`
- `GET /status`
- `POST /v1/text/generate`
- `POST /v1/image/extract-text`
- OpenAI-compatible response envelope shape
- Basic runtime error translation to HTTP `503`
- Internal reasoning mapping for Gemma 4
- Error mapping inside the Ollama adapter

### Test Strategy

- API tests isolate the HTTP contract by replacing the runtime adapter with fakes.
- Adapter tests cover prompt shaping and runtime error normalization without requiring a live Ollama process.
- Manual validation against the real local model remains important for performance and multimodal behavior, but automated tests now cover the stable contract and core control flow.

### Executed Automated Validation

- Command:
  - `poetry run pytest`
- Result:
  - `11 passed`
- Notes:
  - The suite currently emits one dependency warning from `fastapi.testclient` through Starlette about future `httpx2` expectations.
  - The warning does not affect the behavior validated in this iteration.

## Docker Validation

The Docker deployment was also exercised during this change.

### Observed Results

- `docker compose up -d --build`
  - succeeded after removing the unnecessary host port mapping for the `ollama` container
- `curl http://127.0.0.1:8000/health`
  - returned `200 OK`
- `curl http://127.0.0.1:8000/status`
  - first returned `degraded` while the containerized model was not yet downloaded
- `docker compose exec ollama ollama pull hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL`
  - completed successfully inside the Docker volume
- `curl http://127.0.0.1:8000/status`
  - later returned `ok` with `ollama_version=0.30.5` and the configured model available
- `curl -X POST http://127.0.0.1:8000/v1/text/generate ...`
  - returned `200 OK` with an OpenAI-compatible response envelope from the containerized stack
- `docker compose down`
  - completed successfully

### Important Docker Findings

- Publishing `11434` from the `ollama` container caused a conflict when a host Ollama service was already running.
- Keeping `ollama` internal to the Docker network is the safer default for this project.
- A container runtime older than `0.30.5` is not acceptable for Gemma 4 support, so the compose image is pinned explicitly.
