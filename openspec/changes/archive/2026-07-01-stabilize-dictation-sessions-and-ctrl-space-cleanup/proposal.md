## Why

Push-to-talk dictation can feel laggy because the current faster-whisper HTTP path keeps the server warm but transcribes the buffered utterance only after release. If a new shortcut press happens while the previous release is still finalizing, sessions can overlap and old audio/text can be inserted during a later dictation.

## What Changes

- Serialize dictation runner press/release operations so a new dictation cannot start while the previous recording is still finishing transcription and insertion.
- Keep the existing warm Docker/server model behavior, but document that faster-whisper HTTP is buffered-on-release rather than true streaming.
- Expand Linux cleanup for known `Ctrl + Space` conflicts as best-effort desktop hygiene, including Ulauncher when it owns `Ctrl + Space`.
- Add tests that reproduce and prevent overlapping runner sessions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `push-to-talk-dictation`: dictation sessions must not overlap or leak results between consecutive recordings.
- `keyboard-shortcuts`: Linux shortcut cleanup treats old `Ctrl + Space` bindings as a best-effort cleanup path, not as event suppression.

## Impact

- Push-to-talk dictation runner locking and tests.
- Linux user service shortcut-conflict cleanup tests and Ulauncher settings cleanup.
- Dictation documentation and validation notes.
