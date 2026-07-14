# Migration Status

This change was completed and validated against the former Linux Piper TTS
runtime. The current `main` branch replaced Piper with the GPU-backed Chatterbox
runtime in commit `ab5fa75`.

The preserved implementation is therefore intentionally kept on the
`wip/migrate-linux-voice-runtime-to-chatterbox` branch and must not be merged as
is. Before integration it needs to:

- replace `ensure_piper_tts_server()` and Piper paths with the current
  Chatterbox lifecycle;
- update the user service, CLI output, tests and documentation to name the
  actual retained runtimes;
- decide whether Chatterbox should start automatically at login given its GPU
  memory cost;
- rerun focused tests, OpenSpec validation and a real login/startup smoke test.
