# Validation

## Summary

Validated on Linux on 2026-07-14. Automatic backend selection resolves Piper,
the shared client uses port `9010`, Whisper and Piper are prepared by the Linux
voice-runtime service, and no Chatterbox container is started. Windows automatic
selection and explicit backend overrides are covered by unit tests; the existing
Windows Chatterbox implementation remains present and its Compose definition is
valid.

The user also confirmed that Piper voice output on this Linux host continues to
sound correct.

## Automated validation

- `poetry run pytest -q`: 227 tests passed. One third-party Starlette/httpx
  deprecation warning remains and is unrelated to this change.
- Focused backend, service, TTS client and Codex voice tests: 53 tests passed;
  the updated backend/service subset subsequently passed 26 tests.
- `poetry run ruff check` for all changed Python files: passed.
- `poetry run ruff format --check` for all changed Python files: 7 files already
  formatted.
- `poetry run python -m compileall -q src tests`: passed.
- `docker compose config -q` passed for `docker/piper-tts`,
  `docker/chatterbox-tts`, and `docker/whisper-server`.
- `openspec validate support-platform-specific-tts-runtimes --strict`: valid.
- `poetry run so-intelligence-tools --help`: passed and exposes the generic
  runtime commands plus Piper- and Chatterbox-specific diagnostics.

Repository-wide `ruff format --check .` still reports pre-existing formatting
debt in 75 unrelated files. Those files were intentionally not rewritten as
part of this platform integration; all Python files changed by this change pass
the formatter check.

## Runtime evidence

- `DOCKER_CONTEXT=default poetry run so-intelligence-tools
  ensure-linux-voice-runtimes` completed successfully and ensured both the
  faster-whisper environment and Piper environment.
- `poetry run so-intelligence-tools install-linux-voice-runtimes-service`
  installed, enabled, and started
  `so-intelligence-tools-voice-runtimes.service`.
- `systemctl --user status so-intelligence-tools-voice-runtimes.service`
  reported `active (exited)` with `status=0/SUCCESS`; its journal confirms
  faster-whisper followed by Piper.
- `GET http://127.0.0.1:9010/health` returned `status=ok`, sample rate `22050`,
  and the `default`, `female`, and `male` voice aliases.
- The default Docker daemon had no running `chatterbox-tts` container after the
  Linux startup validation.

## Requirement mapping

- Platform-aware selection and endpoint defaults: unit tests cover Linux,
  Windows, explicit values, invalid values, and explicit URL overrides.
- Piper service lifecycle and API: Compose validation, CLI checks, live health,
  and the user's audible output acceptance cover readiness and speech use.
- Linux login startup: the installed user service completed successfully and
  selected Whisper plus Piper without starting Chatterbox.
- Explicit Chatterbox and `none` modes: service-routing unit tests verify that
  only the selected runtime is called while Whisper remains independent.
- Whisper authentication repair and dictation ordering: user-service tests and
  generated service assertions cover the empty-key environment repair and
  dependency ordering.

## Residual risks

- Windows backend resolution is unit-tested but was not smoke-tested on a
  Windows host in this Linux validation session. The previously validated
  Windows Chatterbox files and commands were retained.
- Chatterbox Compose syntax was validated on Linux, but its GPU container was
  deliberately not started because this host is configured to use Piper and
  must not allocate Chatterbox automatically.
- The default Docker daemon contains an older healthy Piper container whose
  replacement can fail with a daemon-level `permission denied`. Startup now
  reuses an already-ready runtime before asking Compose to recreate it, and the
  installed login service completed successfully with that behavior.
