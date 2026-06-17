## 1. Repository Cleanup

- [x] 1.1 Remove archived experimental dictation runtime directories that referenced retired implementation paths.
- [x] 1.2 Verify repository-wide search no longer finds retired runtime identifiers.

## 2. Linux Whisper Bootstrap

- [x] 2.1 Add a CLI command to start `docker/whisper-server` through Docker Compose.
- [x] 2.2 Wire the same startup path into Linux desktop integration and dictation service installation.
- [x] 2.3 Update Linux setup and Whisper docs.

## 3. Validation

- [x] 3.1 Run focused user-service, dictation and shortcut tests.
- [x] 3.2 Run lint and OpenSpec validation.
- [x] 3.3 Verify repository-wide search remains clean before archiving.
