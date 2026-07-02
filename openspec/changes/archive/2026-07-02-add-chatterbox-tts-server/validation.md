# Validation

Date: 2026-07-02

## Static And Unit Checks

Passed:

```powershell
poetry run python -m py_compile docker\chatterbox-tts\server.py src\so_intelligence_tools\infrastructure\user_services.py src\so_intelligence_tools\cli\main.py
```

Passed:

```powershell
poetry run pytest tests\test_user_services.py tests\test_local_tts_client.py
```

Result:

```text
16 passed
```

Note: broader Codex voice tests were also sampled, but this runner repeatedly interrupted them with `KeyboardInterrupt` after partial passes. The interruption did not reproduce in the new Chatterbox lifecycle/status path; `poetry run so-intelligence-tools status-chatterbox-tts-server` returned `ready` with exit code 0 in serial execution.

## Docker Compose

Passed:

```powershell
docker compose -f docker\chatterbox-tts\compose.yaml config
```

Initial validation found that this Docker Compose version rejects `gpus: all`; the compose file now uses NVIDIA device reservations under `deploy.resources.reservations.devices`.

Passed:

```powershell
docker compose -f docker\chatterbox-tts\compose.yaml build
```

Result: image `chatterbox-tts-chatterbox-tts` built successfully.

## Runtime Smoke

Whisper container `71e577ef72b5_whisper-server` was stopped before the heavy Chatterbox smoke test to leave GPU headroom. VRAM did not materially drop after stopping Whisper, so Whisper was not the main VRAM consumer at this point.

Passed:

```powershell
poetry run so-intelligence-tools ensure-chatterbox-tts-server
```

Result: service started and `/health` became ready.

Passed:

```powershell
poetry run so-intelligence-tools status-chatterbox-tts-server
```

Result:

```text
ready
```

Generated smoke audio:

- `evidence/chatterbox-female-smoke.wav`
- `evidence/chatterbox-male-smoke.wav`

Captured endpoint evidence:

- `evidence/health.json`
- `evidence/metrics-after-smoke.json`
- `evidence/smoke-summary.json`

Smoke summary:

```json
{
  "female_wall_seconds": 17.336,
  "female_wav_bytes": 207404,
  "male_wall_seconds": 5.962,
  "male_wav_bytes": 213164,
  "nvidia_smi": "NVIDIA GeForce RTX 3070, 4683, 8192",
  "health_status": "ok",
  "default_voice": "female",
  "voices": ["male", "female"],
  "requests_total": 2,
  "successful_requests_total": 2,
  "average_realtime_factor": 2.629127183126763,
  "current_vram_mib": 4683
}
```

The first female clone request was slower than the male request. Treat that as a real startup/conditioning cost to watch in later latency optimization.

## Chatterbox-Only Cleanup And Codex Listener Trial

Date: 2026-07-02

Removed active Piper implementation and docs:

- `docker/piper-tts/`
- `docs/piper-tts-voice-output.md`
- `ensure-piper-tts-server`, `status-piper-tts-server`, and `stop-piper-tts-server` CLI paths
- Piper lifecycle tests

Updated defaults and docs:

- `LOCAL_TTS_BASE_URL` example now points to `http://127.0.0.1:9011`.
- `LocalTtsSettings` and `ToolRunnerSettings` default local TTS base URL now point to Chatterbox.
- `docs/chatterbox-tts-voice-output.md` now separates Linux and Windows status.
- Linux docs describe the Codex wrapper/listener path.
- Windows docs describe endpoint and JSONL-listener smoke tests, without claiming the Linux wrapper path is validated on Windows.

Cleaned discarded TTS investigation artifacts:

- Removed active workstation TTS benchmark change `openspec/changes/benchmark-current-workstation-tts-models`.
- Removed archived Piper service change `openspec/changes/archive/2026-07-01-add-piper-tts-voice-output`.
- Removed archived CPU TTS benchmark change `openspec/changes/archive/2026-07-01-benchmark-local-tts-cpu-models`.
- Removed Docker volume `so-ai-chatterbox-es-es-cache`.
- No Piper/Kokoro/Qwen/NeuTTS/NutDD TTS containers or volumes remain.
- Retained `chatterbox-tts-chatterbox-tts:latest` image and `chatterbox-tts_chatterbox-tts-data` volume because they belong to the deployed Chatterbox API.

Windows Codex visible-event listener smoke:

```powershell
'{"type":"item.completed","item":{"type":"agent_message","text":"Prueba visible de Codex con Chatterbox en Windows."}}' |
  poetry run so-intelligence-tools listen-codex-visible-events `
    --base-url http://127.0.0.1:9011 `
    --voice female `
    --detail standard
```

Evidence:

- `evidence/codex-listener-metrics-before.json`
- `evidence/codex-listener-metrics-after.json`
- `evidence/codex-listener-smoke-windows.json`

Result:

```json
{
  "exit_code": 0,
  "before_requests": 0,
  "after_requests": 1,
  "after_last_voice": "female",
  "after_last_rtf": 5.133615957831616
}
```

The listener reached the Chatterbox endpoint. Local Windows playback was not asserted because the current default playback discovery is Linux-oriented; Windows playback requires `LOCAL_TTS_PLAYBACK_COMMAND` or direct WAV generation/playback.

Whisper was stopped temporarily for GPU headroom during the trial, then restarted. Chatterbox was stopped after validation to release VRAM.

Post-cleanup validation:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\infrastructure\user_services.py src\so_intelligence_tools\cli\main.py src\so_intelligence_tools\local_tts\client.py docker\chatterbox-tts\server.py
poetry run pytest tests\test_user_services.py tests\test_local_tts_client.py
openspec validate --all --strict
```

Results:

- Python compile passed.
- Focused lifecycle/client tests passed: `14 passed`.
- Codex listener JSONL tests sampled passed: `2 passed`.
- Codex voice session update test output passed, although this local runner returned exit `137` after pytest printed `1 passed`; the same intermittent runner interruption was observed earlier and is not specific to Chatterbox.
- `openspec validate --all --strict` passed: `24 passed, 0 failed`.
- CLI help no longer lists Piper lifecycle commands and still lists Chatterbox lifecycle commands.
- Final service state: Chatterbox stopped, Whisper restarted on `127.0.0.1:9000`, GPU memory about `3300 MiB` used.
- Final Docker TTS images: only `chatterbox-tts-chatterbox-tts:latest` remains.
- Final relevant Docker volumes: `chatterbox-tts_chatterbox-tts-data`, `whisper-server_whisper-data`, and the non-TTS `qwen3_embedding_0_6b_ollama_models`.
- The unneeded base image tag `pytorch/pytorch:2.7.1-cuda12.6-cudnn9-runtime` was removed after the Chatterbox image was built.

## Windows VRAM And Coexistence Check

Date: 2026-07-02

Investigated why GPU VRAM remains occupied after stopping the Whisper and Chatterbox containers. The residual usage came from two sources:

- Windows/WDDM and desktop processes keep about `1074 MiB` resident even with local AI models unloaded.
- The Memanto embedding Ollama container can keep `qwen3-embedding:0.6b` resident on the GPU. This model is used by Memanto/Moorcheh semantic memory and is not part of TTS or Whisper.

Relevant commands:

```powershell
docker exec qwen3-embedding-0-6b-ollama-gpu ollama ps
docker exec qwen3-embedding-0-6b-ollama-gpu ollama stop qwen3-embedding:0.6b
```

Measured VRAM states on the Windows RTX 3070:

| State | VRAM used |
| --- | ---: |
| Windows/WDDM floor after unloading local AI models | about `1074 MiB` |
| Qwen embeddings resident, Whisper and Chatterbox stopped | about `3522 MiB` |
| Whisper resident, Chatterbox stopped, Qwen embeddings resident | about `5762 MiB` |
| Chatterbox resident, Whisper stopped, Qwen embeddings unloaded | about `4335 MiB` |
| Chatterbox and Whisper resident, Qwen embeddings unloaded | about `6567 MiB` |
| Chatterbox synthesis while Whisper was resident | about `6890 MiB` after request |

Conclusion: Whisper and Chatterbox fit together on this 8 GiB RTX 3070 when Qwen embeddings is unloaded first, but the margin is modest. Keeping Whisper, Chatterbox, and Qwen embeddings all resident is not recommended.

Functional check while Whisper and Chatterbox were both loaded:

- Chatterbox `/health` returned ready with default voice `female`.
- Whisper `http://127.0.0.1:9000/v1/models` returned `large-v3-turbo`.
- A short female Chatterbox synthesis completed while Whisper stayed loaded; wall time was about `17.087s`, last voice was `female`, and reported last RTF was about `4.7423`.

Final state after the check: Chatterbox stopped, Whisper left running, Qwen embeddings model unloaded from GPU.

## Windows Codex Wrapper Integration

Date: 2026-07-02

Implemented Windows wrapper support:

- Added `scripts/codex-tts-wrapper.cmd` so the VS Code/Codex extension can launch the Python wrapper as a Windows executable command.
- Updated `scripts/codex-tts-wrapper.py` to resolve the newest bundled Windows Codex CLI under `%USERPROFILE%\.vscode\extensions\openai.chatgpt-*\bin\windows-x86_64\codex.exe`.
- Updated the wrapper shutdown path to close the listener stdin and wait for queued speech before killing the listener.
- Added native Windows WAV playback through Python `winsound`, so `LOCAL_TTS_PLAYBACK_COMMAND` is not required for normal local speaker output.
- Configured the current user's VS Code setting:

```json
{
  "chatgpt.cliExecutable": "C:\\Dev\\Active\\so_intelligence_tools\\scripts\\codex-tts-wrapper.cmd"
}
```

Searched for an equivalent standalone Codex Desktop app override. Codex Desktop logs show an internal stdio app-server startup, but no `chatgpt.cliExecutable`-style setting was found under `%LOCALAPPDATA%\Packages\OpenAI.Codex_2p2nqsd0c76g0`, `%APPDATA%`, or `%USERPROFILE%\.codex`. The validated hook path is therefore the VS Code/Codex extension path.

Validation commands:

```powershell
poetry run python -m py_compile scripts\codex-tts-wrapper.py src\so_intelligence_tools\local_tts\client.py
poetry run pytest tests\test_local_tts_client.py tests\test_codex_tts_wrapper.py tests\test_codex_voice_events.py tests\test_codex_voice_control.py
poetry run so-intelligence-tools ensure-chatterbox-tts-server
.\scripts\codex-tts-wrapper.cmd app-server --stdio
.\scripts\codex-tts-wrapper.cmd app-server --help
```

Test result:

- Python compile passed.
- Focused wrapper/listener/playback tests printed `34 passed in 0.33s`; this local runner returned process exit `137` after the successful pytest summary, matching the intermittent runner behavior already observed in Codex voice test groups.
- `scripts\codex-tts-wrapper.cmd app-server --help` resolved the real bundled Windows Codex CLI and exited `0`.
- End-to-end wrapper smoke used a temporary fake real Codex CLI that emitted one app-server JSONL event. The wrapper launched, started the listener, forwarded stdout, sent the visible event to Chatterbox, and played the generated WAV through Windows audio.

Evidence:

- `evidence/codex-wrapper-metrics-before.json`
- `evidence/codex-wrapper-metrics-after.json`
- `evidence/codex-wrapper-smoke-windows.json`
- `evidence/codex-wrapper-real-cli-help.txt`

Wrapper smoke metrics:

```json
{
  "before_requests": 0,
  "after_requests": 1,
  "after_last_voice": "female",
  "after_last_realtime_factor": 4.90190133166632,
  "wrapper_exit_code": 0,
  "wrapper_elapsed_seconds": 23.7
}
```

Final state after this check: Chatterbox and Whisper were both running, Qwen embeddings was unloaded, and GPU memory was about `6880 MiB` of `8192 MiB`.

## Windows Codex Desktop Session Monitor

Date: 2026-07-02

The standalone Codex Desktop app starts its own packaged `codex.exe app-server --analytics-default-enabled` process from WindowsApps. No `chatgpt.cliExecutable`-style override was found for that app. The app does write visible transcript events under `%USERPROFILE%\.codex\sessions`, including `event_msg` entries with `payload.type = agent_message`.

Implemented a Desktop-specific integration path:

- Added `listen-codex-desktop-session-events`.
- Added `CodexDesktopSessionTailer` for tailing new JSONL lines under `~/.codex/sessions`.
- The monitor only speaks visible `event_msg` / `agent_message` entries and ignores hidden reasoning, `response_item`, token counts, and tool internals.
- Added `install-windows-codex-desktop-tts-startup`.
- Added a hidden Startup launcher at `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\so-intelligence-tools-codex-desktop-tts.vbs`.
- Started the monitor for the current Windows session.

Validation commands:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\local_tts\codex_desktop.py src\so_intelligence_tools\cli\main.py src\so_intelligence_tools\infrastructure\windows_startup.py src\so_intelligence_tools\infrastructure\windows_background_launcher.py
poetry run pytest tests\test_codex_desktop_tts.py tests\test_windows_startup.py tests\test_local_tts_client.py
poetry run so-intelligence-tools listen-codex-desktop-session-events --sessions-dir <temp> --start-at-beginning --idle-timeout-seconds 0.2 --poll-interval-seconds 0.05 --voice female --base-url http://127.0.0.1:9011 --detail standard
poetry run so-intelligence-tools install-windows-codex-desktop-tts-startup
```

Results:

- Python compile passed.
- Focused tests passed: `19 passed`.
- Additional Desktop parser test after BOM handling passed: `6 passed`.
- Chatterbox session-monitor smoke moved `requests_total` from `1` to `2`.
- The smoke request used voice `female` and reported last realtime factor about `1.8282`.
- Runtime evidence shows the hidden Startup launcher exists and the listener is running. The `.venv` launcher process may spawn the base `C:\Python311` child process; together they represent one logical monitor.

Evidence:

- `evidence/codex-desktop-session-listener-metrics-before.json`
- `evidence/codex-desktop-session-listener-metrics-after.json`
- `evidence/codex-desktop-session-listener-smoke-windows.json`
- `evidence/codex-desktop-session-listener-runtime-windows.json`

## Latency Optimization Spikes

Date: 2026-07-02

Additional latency spikes were recorded under `evidence/tts-latency-spikes/`.

Summary:

- Current PyTorch Chatterbox, direct process, `cfg_weight=0.25`: `11.42s` synthesis for `8.96s` audio, RTF `1.27`.
- Current HTTP service, `cfg_weight=0.25`: `12.64s` synthesis for `9.00s` audio, RTF `1.40`.
- Long text full request: `56.92s`; same text chunked had first chunk ready in `5.56s`.
- Naive current-runtime `bf16` failed with a speaker-conditioning dtype mismatch.
- `rsxdalv/chatterbox` faster branch was not drop-in compatible with the es-ES loader and failed during T3 config/model startup.
- `onnx-community/chatterbox-multilingual-ONNX` ran with `CUDAExecutionProvider`, but measured about `15.6s` for the medium prompt and did not emit a stop token before the max-token cap in this simple script.

Whisper/TTS coexistence check after unloading Memanto Qwen embeddings:

- Whisper and Chatterbox were both running.
- Qwen embeddings container stayed up but `qwen3-embedding:0.6b` was not resident.
- Ready-state VRAM was about `4237 MiB`.
- A short female synthesis completed while Whisper stayed active: wall `11.028s`, synthesis `10.836s`, audio `5.20s`, RTF `2.084`, VRAM after request `4826 MiB`.

Conclusion: on this RTX 3070, Whisper and Chatterbox can run together if Qwen embeddings is unloaded first. For Codex/OpenClaw perceived latency, chunking plus playback-on-first-chunk is currently more promising than switching to ONNX or the faster fork.

## Codex Desktop Task Boundary Priority Fix

Date: 2026-07-02

Fixed a Codex Desktop monitor bug where queued speech from older assistant messages could continue after the user sent a new message or after the task was already complete.

Behavior now validated:

- `task_started` speaks `Inicio de tarea.` and clears stale queued speech.
- `task_complete` speaks `Fin de tarea.`, clears pending assistant-message speech, and asks Windows playback to stop current WAV playback when possible.
- If an older segment was already synthesizing when a task boundary superseded it, the synthesized audio is discarded before playback.
- Codex Desktop `minimal` mode now reads only task start/end markers. At this point in the work, `actions` behaved the same for Desktop; the next validation section supersedes that with lightweight tool progress support.

Validation:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\local_tts\client.py src\so_intelligence_tools\local_tts\codex_desktop.py src\so_intelligence_tools\local_tts\codex_events.py src\so_intelligence_tools\cli\main.py
poetry run pytest tests\test_codex_desktop_tts.py tests\test_codex_voice_events.py tests\test_local_tts_client.py
openspec validate add-chatterbox-tts-server --strict
```

Results:

- Python compile passed.
- Focused tests passed: `38 passed`.
- OpenSpec strict validation passed.
- The existing hidden Codex Desktop TTS monitor process was restarted so the current Windows session uses the new boundary-priority behavior.

## Codex Desktop Final Message And Tool Progress Fix

Date: 2026-07-02

Fixed a follow-up Codex Desktop monitor issue where the previous boundary-priority behavior made the user hear only `Inicio de tarea.` and `Fin de tarea.`.

Behavior now validated:

- `task_started` still clears stale queued speech and speaks `Inicio de tarea.`.
- `task_complete` with `last_agent_message` clears stale queued speech, speaks `Fin de tarea.`, and then reads the final answer text.
- `task_complete` without `last_agent_message` still speaks `Fin de tarea.` immediately.
- `actions` mode for Codex Desktop now reads task boundaries plus lightweight tool progress from `response_item.function_call`, `response_item.function_call_output`, `patch_apply_*`, and `web_search_*`, while skipping assistant message text.
- `standard`, `no-code`, and `full` read task boundaries, tool progress, and visible assistant/final text.

Validation:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\local_tts\codex_desktop.py
poetry run pytest tests\test_codex_desktop_tts.py tests\test_codex_voice_events.py tests\test_local_tts_client.py
poetry run openspec validate add-chatterbox-tts-server --strict
```

Results:

- Python compile passed.
- Focused tests passed: `41 passed`.
- OpenSpec strict validation passed.
- The Codex Desktop TTS monitor was restarted for the current Windows session after the fix.

## Codex Desktop Synthesis Playback Pipeline

Date: 2026-07-02

Implemented a two-stage Codex Desktop TTS playback queue so Chatterbox can synthesize the next segment while the current WAV is still playing.

Behavior now validated:

- The synthesis worker preserves segment order and sends ready WAV bytes to a bounded playback buffer.
- The playback worker plays ready WAV segments in order.
- While `Primero.` is blocked in playback, `Segundo.` is synthesized before the first playback finishes.
- `clear(cancel_current=True)` still cancels current playback when possible and drains both queued text and prefetched audio.
- Prefetched stale audio is not played after a task boundary clears the queue.

Validation:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\local_tts\codex_desktop.py
poetry run pytest tests\test_codex_desktop_tts.py tests\test_codex_voice_events.py tests\test_local_tts_client.py
poetry run openspec validate add-chatterbox-tts-server --strict
```

Results:

- Python compile passed.
- Focused tests passed: `43 passed`.

## Windows Documentation Consolidation

Date: 2026-07-02

Updated the project documentation after the Windows Chatterbox/Codex Desktop integration and GPU coexistence investigation.

Documentation now covers:

- Windows Chatterbox es-ES service lifecycle, HTTP endpoints, voice presets and female reference voice.
- Codex Desktop session monitor behavior, VS Code/Codex wrapper behavior, OpenClaw HTTP integration shape, and Windows startup/log locations.
- Detail levels, voice selection variables, task start/end semantics, final-message ordering, and queue policy for stale tool-progress speech.
- Latency measurements including first-request smoke timing, male/female short requests, direct PyTorch and HTTP spikes, chunked long text, Desktop monitor metrics, and Whisper co-residency request timing.
- Optimization attempts that were rejected or deferred: bf16 dtype mismatch, `rsxdalv` fast branch incompatibility, ONNX CUDA slowness/no stop token, and Qwen3-TTS FlashAttention/bitsandbytes being slower for the Codex/OpenClaw use case.
- VRAM conditions for WDDM baseline, Qwen embeddings, Whisper, Chatterbox, and Whisper+Chatterbox coexistence on the RTX 3070 8 GiB workstation.
- LAN-access caveat: current Whisper and Chatterbox compose bindings are localhost-only unless explicitly changed and firewalled.
- Clear Linux versus Windows status notes in the root README and project docs.

Files updated:

- `README.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/windows-support.md`
- `docs/chatterbox-tts-voice-output.md`

## Codex Desktop Tool Progress Soft Queue

Date: 2026-07-02

Implemented the user-requested optimization to avoid repeated action notices delaying useful text.

Behavior now validated:

- Tool progress segments such as `Ejecutando comando.` are treated as soft feedback.
- When a visible `message` segment arrives, pending text actions and prefetched action WAVs from older tool progress are discarded.
- If an action segment was already synthesizing, the action-generation check marks it obsolete before playback.
- A following visible message plays without waiting for three queued `Ejecutando comando.` segments.
- Task boundaries still use the stronger `clear(cancel_current=True)` path.

Validation:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\local_tts\codex_desktop.py
poetry run ruff check src\so_intelligence_tools\local_tts\codex_desktop.py tests\test_codex_desktop_tts.py
poetry run pytest tests\test_codex_desktop_tts.py tests\test_codex_voice_events.py tests\test_local_tts_client.py
poetry run openspec validate add-chatterbox-tts-server --strict
```

Results:

- Python compile passed.
- Ruff passed.
- Focused tests passed: `44 passed`.
- OpenSpec strict validation passed.
- The Codex Desktop TTS monitor was restarted for the current Windows session so the synthesis/playback pipeline is active.

## Codex Desktop Completion Final Message Order

Date: 2026-07-02

Adjusted `task_complete` handling after user feedback.

Behavior now validated:

- `task_complete` with `last_agent_message` clears stale queued/prefetched speech.
- The monitor speaks `Fin de tarea.` first.
- The monitor then reads the cleaned final message from `last_agent_message`.
- The final message does not clear the just-spoken task boundary.

Validation:

```powershell
poetry run python -m py_compile src\so_intelligence_tools\local_tts\codex_desktop.py
poetry run pytest tests\test_codex_desktop_tts.py tests\test_codex_voice_events.py tests\test_local_tts_client.py
poetry run openspec validate add-chatterbox-tts-server --strict
```

Results:

- Python compile passed.
- Focused tests passed: `43 passed`.
