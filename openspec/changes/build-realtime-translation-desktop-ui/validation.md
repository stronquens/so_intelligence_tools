# Validation

## Automated

- `npm --prefix desktop run test`
- `npm --prefix desktop run build`
- `poetry run pytest -q`

## Visual

- `npx playwright screenshot --viewport-size=1680,946 http://127.0.0.1:5173 .tmp/realtime-translator-ui-v3.png`
- Screenshot reviewed against the user-provided reference.

## Notes

- The UI is currently validated with mock transcript data and a mock Electron command bridge.
- The current production translation flow remains the Python/Tkinter UI from `system-audio-transcription`.
- The next implementation step is the real Python <-> Electron bridge.
