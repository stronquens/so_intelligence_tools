# Piper TTS Voice Output

Status: working Linux implementation path for CPU-only voice output.

Piper is the selected local TTS backend after the July 1, 2026 Linux CPU benchmark. The goal is to keep a small Docker service warm while voice output is wanted. Stopping the container disables speech without affecting normal text output.

This page documents the Linux-validated setup. The HTTP API and Docker runtime are portable in principle, but the playback command discovery and Codex/VS Code wrapper have only been validated on this Linux workstation.

## Start Or Stop Voice Output

If the global `so-ai` command is installed, the examples below can be run from any project:

```bash
so-ai status-piper-tts-server
```

`so-ai` is a persistent shortcut to this repository's Poetry-managed CLI:

```text
~/.local/bin/so-ai -> /home/sciling/Escritorio/so_intelligence_tools/.venv/bin/so-intelligence-tools
```

Create or refresh it with:

```bash
mkdir -p ~/.local/bin
ln -sfn /home/sciling/Escritorio/so_intelligence_tools/.venv/bin/so-intelligence-tools ~/.local/bin/so-ai
```

Use `so-ai` for per-window voice controls when the VS Code terminal is opened in another project. Use `poetry run so-intelligence-tools` only when the terminal is inside this repo.

Start the warm Piper service:

```bash
so-ai ensure-piper-tts-server
```

Check whether speech is enabled:

```bash
so-ai status-piper-tts-server
```

Stop speech:

```bash
so-ai stop-piper-tts-server
```

When the Piper container is stopped, clients treat voice output as disabled and continue silently.

## Smoke Test

```bash
so-ai speak-text --text "Hola, esto es una prueba de voz local con Piper."
```

The command sends text to `http://127.0.0.1:9010/v1/audio/speech`, plays the returned WAV through `paplay`, `pw-play`, or `aplay`, and deletes its temporary WAV after playback.

## Voice Configuration

The default Docker profile uses the fastest retained Spanish Piper voice from the benchmark:

```env
PIPER_TTS_MODEL_REPO=rhasspy/piper-voices
PIPER_TTS_MODEL_FILE=es/es_ES/davefx/medium/es_ES-davefx-medium.onnx
PIPER_TTS_CONFIG_FILE=es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json
PIPER_TTS_PORT=9010
```

These values live in `docker/piper-tts/.env`. The installer copies `docker/piper-tts/.env.example` only if `.env` does not already exist.

The same container can also preload more voices with `PIPER_TTS_VOICES_JSON`. On this Linux workstation the validated aliases are:

| Alias | Voice file | Notes |
| --- | --- | --- |
| `default` | `es/es_ES/davefx/medium/es_ES-davefx-medium.onnx` | Retained default and fastest benchmarked Spanish voice. |
| `male` | `es/es_ES/davefx/medium/es_ES-davefx-medium.onnx` | Explicit male alias for per-window selection. |
| `female` | `es/es_AR/daniela/high/es_AR-daniela-high.onnx` | Smoke-tested Spanish female alias. |

## Codex Visible Event Voice

Codex lifecycle hooks are useful for turn-level automation, but they do not expose a documented streaming hook for every visible assistant message. For live reading, use the documented JSONL event streams:

- `codex exec --json` emits event lines such as `item.completed` with `agent_message` text.
- `codex app-server` emits notifications such as `item/agentMessage/delta` and `item/completed`; this is the protocol used by rich clients such as the VS Code extension.

To read the visible Codex CLI cycle aloud from a piped JSONL stream:

```bash
codex exec --json "resume el estado del repo" \
  | so-ai listen-codex-visible-events
```

Do not run `listen-codex-visible-events` by itself to change a VS Code window setting. It is a listener and waits for newline-delimited JSON on stdin.

By default, the listener reads the visible cycle, not only the final answer:

- assistant text deltas as they complete readable sentences;
- visible assistant messages from JSONL `agent_message` items;
- tool and command lifecycle states such as "using tool", "executing command", and "command finished";
- visible status/progress items, plan updates, web-search status, and file-change status.

Tool and command payloads are not read aloud. The listener announces lifecycle state only, so it does not speak raw command text, tool arguments, command output, prompts, logs, or private internals.

To reduce speech to final visible assistant messages only:

```bash
codex exec --json "resume el estado del repo" \
  | so-ai listen-codex-visible-events --final-only
```

For the Codex IDE extension, the integration point is the same event shape: a stable hook or adapter in the extension should forward visible app-server notifications to:

```bash
so-ai listen-codex-visible-events
```

The listener accepts newline-delimited JSON on stdin. It reads visible assistant messages and app-server assistant deltas, chunks them into readable segments, and sends them to the Piper service.

Speech detail is configurable with `CODEX_VOICE_DETAIL` in the repo `.env`, per piped listener command with `--detail`, or per active VS Code/Codex window with `codex-voice-detail`:

```bash
CODEX_VOICE_DETAIL=actions
```

```bash
codex exec --json "resume el estado del repo" \
  | so-ai listen-codex-visible-events --detail actions
```

To change the active VS Code/Codex window, use:

```bash
so-ai codex-voice-detail actions
so-ai codex-voice-detail minimal
```

Available detail modes:

| Mode | Spoken content |
| --- | --- |
| `minimal` | Task start and task end only. |
| `actions` | `minimal` plus tool/function/command lifecycle. |
| `standard` | `actions` plus visible assistant text; code blocks are announced, URLs are shortened. |
| `no-code` | Like `standard`, but code blocks are removed instead of announced. |
| `full` | Reads visible assistant text with code block contents preserved and URLs left unshortened. |

The default is `actions`, which speaks task start/end plus tool/function/command lifecycle, without reading full assistant messages.

When a turn completes in full-cycle modes, pending queued speech is cleared and "Fin de tarea" is spoken next. Speech already playing may finish first, but old queued paragraphs are skipped.

Markdown is normalized for speech:

- Fenced code blocks are announced by language, for example "Bloque de código bash omitido", instead of reading their contents aloud.
- Raw URLs are summarized as "URL ..." with only the final path segment, such as `app-server.md`, instead of reading the full URL.
- Markdown links keep their label and add the shortened URL tail.
- Newlines outside code fences are treated as readable boundaries, so lists, headings, and short status lines do not wait for a final period before speaking.
- In full-cycle mode, turn completion is announced with "Fin de tarea".

### VS Code Codex Extension

The installed OpenAI Codex extension uses the Codex CLI app-server. Until the extension exposes a dedicated voice-output hook, use the local wrapper that proxies the bundled Codex CLI and tees app-server events to the TTS listener:

```json
{
  "chatgpt.cliExecutable": "/home/sciling/Escritorio/so_intelligence_tools/scripts/codex-tts-wrapper.py"
}
```

Add that setting in VS Code User Settings JSON, then run **Developer: Reload Window**. The setting is marked by the extension as development-only, so remove it to return to the stock bundled CLI.

Before opening a Codex thread, make sure Piper is running:

```bash
so-ai ensure-piper-tts-server
```

To disable speech without changing VS Code settings:

```bash
so-ai stop-piper-tts-server
```

### Per-Window Voice Toggle

Stopping Piper disables speech everywhere. To mute only one VS Code/Codex window, leave Piper running and toggle the wrapper session for that window.

From the integrated terminal in the VS Code window you want to control:

```bash
so-ai codex-voice-toggle
```

The default target is the most recent active Codex voice session for the current working directory. This makes it suitable for separate VS Code windows opened on different projects.

Useful commands:

```bash
so-ai codex-voice-sessions
so-ai codex-voice-off
so-ai codex-voice-on
so-ai codex-voice-detail minimal
so-ai codex-voice-detail actions
so-ai codex-voice-detail full
so-ai codex-voice-voice male
so-ai codex-voice-voice female
so-ai codex-voice-off --all
so-ai codex-voice-on --pid 12345
```

These commands target the most recent active Codex voice session for the current working directory by default, which is usually the current VS Code window when run from its integrated terminal. Speech that is already playing may finish.

### Piper Voice Selection

The Piper container can load one or more voices. The legacy single-voice settings in `docker/piper-tts/.env` still define the default voice:

```env
PIPER_TTS_MODEL_REPO=rhasspy/piper-voices
PIPER_TTS_MODEL_FILE=es/es_ES/davefx/medium/es_ES-davefx-medium.onnx
PIPER_TTS_CONFIG_FILE=es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json
```

For multiple voices in the same container, add `PIPER_TTS_VOICES_JSON` with aliases such as `male` and `female`:

```env
PIPER_TTS_VOICES_JSON={"default":{"model_file":"es/es_ES/davefx/medium/es_ES-davefx-medium.onnx","config_file":"es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"},"male":{"model_file":"es/es_ES/davefx/medium/es_ES-davefx-medium.onnx","config_file":"es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"},"female":{"model_file":"es/es_AR/daniela/high/es_AR-daniela-high.onnx","config_file":"es/es_AR/daniela/high/es_AR-daniela-high.onnx.json"}}
```

Then restart:

```bash
so-ai ensure-piper-tts-server
so-ai speak-text --voice male --text "Prueba de voz masculina."
so-ai speak-text --voice female --text "Prueba de voz femenina."
```

Verify the loaded aliases:

```bash
curl http://127.0.0.1:9010/health
```

The selected voice can then be changed per VS Code window:

```bash
so-ai codex-voice-voice male
so-ai codex-voice-voice female
```

The retained default is the benchmarked Spanish `davefx/medium` voice. The female `daniela/high` alias is available for manual selection, but it is not the default because the CPU benchmark and daily-use selection favored `davefx/medium`.

The listening detail mode is independent from the Piper voice. Use `CODEX_VOICE_DETAIL` or `--detail` for content verbosity, and `docker/piper-tts/.env` for the synthesized voice.

## Windows Status

The Piper HTTP service shape should be portable, but this integration is not validated on Windows yet.

Windows-specific work still needed before documenting it as supported:

- choose a playback backend instead of Linux `paplay`, `pw-play`, or `aplay`;
- validate Docker Desktop networking and volume/cache behavior for Piper voices;
- validate the VS Code Codex `chatgpt.cliExecutable` wrapper path and process lifecycle on Windows;
- decide where per-window session state should live under `%LOCALAPPDATA%`.

Existing Windows dictation support is separate and remains documented in [Windows Support](windows-support.md). Do not assume the Linux Piper voice wrapper is a supported Windows workflow until those items are validated.

## Privacy Boundary

The listener never speaks hidden reasoning item types, private chain-of-thought, tool internals, prompts, command text, command output, or tool payloads. It only speaks visible assistant text and safe visible lifecycle summaries from supported event shapes.

By default it also strips code blocks and long inline code before speech, so it does not read long logs or code aloud.

## Troubleshooting

If nothing is spoken:

```bash
so-ai status-piper-tts-server
curl http://127.0.0.1:9010/health
```

If the status is `disabled`, start the server with:

```bash
so-ai ensure-piper-tts-server
```

If the service is ready but playback is silent, verify at least one playback command is available:

```bash
which paplay || which pw-play || which aplay
```

If the Codex IDE extension cannot forward app-server events, use the CLI JSONL fallback until a stable extension hook is available.
