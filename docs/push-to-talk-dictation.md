# Push-To-Talk Dictation

Status: Experimental.

Push-to-talk dictation records while you hold a shortcut, transcribes Spanish speech locally with Nemotron ASR ONNX CPU, and inserts the resulting text into the focused text field.

## Shortcut Behavior

Default:

```text
Ctrl + Alt + Space
```

The tool records while the keys are held. When you release the shortcut, recording stops and final transcription/insertion completes.

## Runtime

Current runtime:

```env
PUSH_TO_TALK_DICTATION_RUNTIME=onnx_cpu
PUSH_TO_TALK_DICTATION_MODEL_REPO=onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4
PUSH_TO_TALK_DICTATION_LANGUAGE=es-ES
```

Validate runtime setup:

```bash
poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
```

Run the service manually:

```bash
poetry run so-intelligence-tools run-push-to-talk-dictation-service
```

Installed service:

```bash
systemctl --user status so-intelligence-tools-push-to-talk-dictation.service
```

## Known Issues

This feature is promising but not stable yet. Current known issues:

- The first words can be lost because the model/session may take a moment to warm up.
- Text can appear out of order during insertion.
- Inserted text can sometimes be replaced or partially deleted before the session continues.
- The listener is currently oriented toward Linux/X11.

These issues are tracked in the active OpenSpec change for Nemotron streaming dictation.

## Practical Advice

- Start speaking a brief moment after pressing the shortcut.
- Use it only in low-risk text fields until insertion stabilization is complete.
- Keep an eye on the focused field after release.

