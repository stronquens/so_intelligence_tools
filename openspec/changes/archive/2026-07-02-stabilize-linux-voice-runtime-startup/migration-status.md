# Migration Status

This change was completed and validated against the Linux Piper TTS runtime.
Commit `ab5fa75` later introduced the Windows/GPU Chatterbox runtime and briefly
treated that backend as a global replacement.

The implementation was reconciled by
`support-platform-specific-tts-runtimes`: Linux automatic selection retains
Piper, Windows automatic selection retains Chatterbox, and the shared client
selects the matching endpoint. The original WIP branch remains historical and
must not be merged independently because its useful changes are already
integrated through that platform-aware change.

Linux login startup does not allocate Chatterbox unless it is explicitly
selected.
