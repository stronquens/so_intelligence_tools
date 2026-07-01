# Purpose

Preservar documentacion tecnica suficiente para entender, comparar o restaurar runtimes de dictado retirados sin convertirlos en el camino por defecto.

## Requirements

### Requirement: Retired Dictation Runtime Backup
The documentation SHALL preserve enough information to inspect or restore the previous Nemotron ONNX CPU dictation prototype without making it the default runtime.

#### Scenario: Developer wants to revisit Nemotron
- **WHEN** a developer reads the push-to-talk dictation docs
- **THEN** they can find a linked backup guide with the source commit, relevant files, runtime variables, known limitations, and restore commands.

### Requirement: Dictation Backend Selector
The documentation SHALL present Whisper/faster-whisper and Nemotron streaming as separate Linux dictation backend options with clear status and switching guidance.

#### Scenario: Developer chooses a Linux dictation backend
- **WHEN** a developer opens the push-to-talk dictation docs
- **THEN** they can compare Whisper and Nemotron by runtime name, Linux status, behavior, and best-fit use case.

### Requirement: Whisper Remains Current Path
The documentation SHALL keep faster-whisper HTTP as the current supported dictation route while labeling Nemotron as a retired prototype.

#### Scenario: User chooses a dictation backend
- **WHEN** a user reads the dictation documentation
- **THEN** faster-whisper is presented as the current path and Nemotron is presented as rollback/reference material.
