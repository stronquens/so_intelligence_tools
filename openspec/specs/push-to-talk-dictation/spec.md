# Purpose

Definir una herramienta de dictado push-to-talk que grabe audio mientras se mantiene pulsada una combinación de teclas, lo transcriba en local y escriba el texto donde esté el cursor.
## Requirements
### Requirement: Windows local push-to-talk dictation
The system SHALL provide local push-to-talk dictation on Windows using the configured local ASR runtime.

#### Scenario: User holds the Windows dictation shortcut
- **WHEN** the Windows dictation listener is running
- **AND** the user holds `Ctrl + Shift + Space`
- **THEN** the system SHALL start capturing microphone audio
- **AND** it SHALL stream or buffer captured audio chunks for the configured local ASR transcriber.

#### Scenario: User releases the Windows dictation shortcut
- **WHEN** the Windows dictation listener is capturing microphone audio
- **AND** the user releases any key in the configured dictation shortcut
- **THEN** the system SHALL stop microphone capture after the configured post-roll
- **AND** it SHALL finalize the ASR session.

#### Scenario: Faster-whisper HTTP runtime is selected
- **WHEN** `PUSH_TO_TALK_DICTATION_RUNTIME` is `faster_whisper_http`
- **THEN** the system SHALL send captured dictation audio to the configured OpenAI-compatible `/v1/audio/transcriptions` endpoint
- **AND** it SHALL insert the final transcript after the user releases the shortcut.

### Requirement: Windows dictation runtime warm-up
The Windows dictation listener SHALL check the configured local ASR runtime before waiting for dictation shortcuts.

#### Scenario: Dictation listener starts successfully
- **WHEN** the Windows dictation listener starts
- **THEN** it SHALL check that the configured ASR runtime is available
- **AND** it SHALL load or contact the runtime so the first dictation session does not pay avoidable startup cost.

#### Scenario: Dictation runtime is unavailable
- **WHEN** the configured ASR runtime or model cannot be loaded or contacted
- **THEN** the listener SHALL fail with diagnostic output
- **AND** it SHALL NOT stay running in a broken ready state.

### Requirement: Windows microphone capture
The system SHALL capture Windows microphone audio in the PCM format expected by the local ASR transcriber.

#### Scenario: Default microphone capture
- **WHEN** dictation capture starts without a configured microphone source
- **THEN** the system SHALL use the default Windows input device
- **AND** it SHALL produce mono 16 kHz signed 16-bit PCM chunks.

#### Scenario: Configured microphone source
- **WHEN** a Windows microphone source is configured
- **THEN** the system SHALL attempt to capture from that configured source
- **AND** it SHALL report a clear error if the source is unavailable.

### Requirement: Activación mediante combinación de teclas mantenida
El sistema SHALL iniciar el flujo de dictado cuando el usuario pulse una combinación global concreta y mantenerlo activo mientras dicha combinación siga pulsada.

#### Scenario: Inicio de la pulsación
- **WHEN** el usuario pulsa la combinación asignada al dictado
- **THEN** la herramienta SHALL comenzar a grabar audio de inmediato

#### Scenario: Fin de la pulsación
- **WHEN** el usuario deja de pulsar la combinación asignada
- **THEN** la herramienta SHALL detener la grabación y continuar automáticamente con la transcripción

### Requirement: Overlay temporal de estado de grabación
El sistema SHALL mostrar un pequeño overlay visual mientras el dictado esté grabando para indicar claramente que el audio está siendo capturado.

#### Scenario: Grabación en curso
- **WHEN** el flujo de dictado está grabando audio
- **THEN** el sistema SHALL mostrar un overlay discreto con estado de grabación

#### Scenario: Grabación finalizada
- **WHEN** la grabación termina
- **THEN** el overlay SHALL desaparecer sin requerir interacción adicional del usuario

### Requirement: Transcripción automática en local al terminar la grabación
El sistema SHALL enviar automáticamente el audio capturado al modelo local al finalizar la pulsación, sin pasos intermedios manuales.

#### Scenario: Audio capturado correctamente
- **WHEN** el usuario suelta la combinación y existe audio válido
- **THEN** la herramienta SHALL enviar ese audio al backend local para obtener la transcripción

### Requirement: Inserción automática del texto en el foco actual
El sistema SHALL insertar la transcripción resultante directamente en el punto donde el usuario tenga el cursor activo.

#### Scenario: Hay un campo editable con foco
- **WHEN** la transcripción se completa correctamente
- **THEN** el sistema SHALL escribir el texto resultante en la ubicación actual del cursor

### Requirement: Limpieza de audio efímero
El sistema SHALL minimizar la persistencia del audio grabado y eliminar cualquier artefacto temporal al finalizar el flujo.

#### Scenario: Procesamiento completamente en memoria
- **WHEN** la implementación pueda evitar escribir el audio a disco
- **THEN** la herramienta SHALL mantener la grabación solo en memoria

#### Scenario: Archivo temporal inevitable
- **WHEN** la implementación necesite usar un archivo temporal para interoperar con librerías o herramientas del sistema
- **THEN** dicho archivo SHALL eliminarse automáticamente en cuanto termine la transcripción

### Requirement: Feedback claro ante fallos o grabación vacía
El sistema SHALL evitar comportamientos silenciosos cuando no haya audio útil o cuando la transcripción no pueda completarse.

#### Scenario: No se capturó audio utilizable
- **WHEN** el usuario dispara el flujo pero no queda audio válido para transcribir
- **THEN** el sistema SHALL mostrar una notificación o feedback equivalente indicando que no se pudo generar texto

#### Scenario: El backend local falla
- **WHEN** la grabación termina pero el backend local no devuelve una transcripción válida
- **THEN** el sistema SHALL informar del fallo y no insertar texto parcial o corrupto

### Requirement: Linux Whisper backend bootstrap
The system SHALL prepare the faster-whisper Docker backend when installing Linux push-to-talk dictation integration.

#### Scenario: Linux desktop integration installs dictation
- **WHEN** the user runs the Linux desktop integration installer
- **THEN** the system SHALL ensure `docker/whisper-server/.env` exists
- **AND** the system SHALL run the faster-whisper Docker Compose service before enabling the dictation listener service.

#### Scenario: User installs only the dictation service
- **WHEN** the user runs the standalone push-to-talk dictation service installer
- **THEN** the system SHALL ensure the faster-whisper Docker backend is started before enabling the service.

### Requirement: Linux push-to-talk dictation shortcut and runtime
The system SHALL provide a Linux push-to-talk dictation listener that records while the configured shortcut is held and inserts recognized Spanish text into the focused field after release.

#### Scenario: Linux default shortcut starts dictation
- **WHEN** the Linux desktop integration is installed with default settings
- **THEN** the push-to-talk dictation listener SHALL use `Ctrl + Shift + Space`.

#### Scenario: Whisper runtime is checked before listening
- **WHEN** the Linux dictation service is installed
- **THEN** the faster-whisper Docker server SHALL be ensured before the listener is enabled.

#### Scenario: Legacy native Ubuntu shortcut conflict is cleared
- **WHEN** the Linux desktop integration is installed on a system exposing old `Ctrl + Space` input-source hotkeys
- **THEN** the installer SHALL clear those conflicting hotkeys as best-effort cleanup for users who previously had dictation on `Ctrl + Space`.

### Requirement: Dictation shortcut includes Shift support
The press-and-hold dictation listener SHALL support shortcuts that include the `Shift` modifier.

#### Scenario: User holds Ctrl Shift Space
- **WHEN** the dictation listener is configured with `Ctrl + Shift + Space`
- **AND** the user holds Ctrl, Shift, and Space together
- **THEN** the system SHALL start dictation capture.

### Requirement: Dictation sessions do not overlap
The push-to-talk dictation runner SHALL prevent a new dictation session from starting while a previous session is still finalizing transcription or text insertion.

#### Scenario: User presses again while previous release is finalizing
- **WHEN** a dictation release is still finalizing
- **AND** the user presses the dictation shortcut again
- **THEN** the runner SHALL NOT start a second capture
- **AND** text from the previous recording SHALL NOT be inserted into the new recording's result state.

### Requirement: Faster-whisper HTTP warm runtime semantics
The system SHALL keep the faster-whisper HTTP runtime warm before listening, while treating each dictation as a buffered transcription finalized after release.

#### Scenario: Dictation listener starts
- **WHEN** the dictation listener starts
- **THEN** it SHALL check the faster-whisper HTTP server readiness before accepting shortcut input.

#### Scenario: User releases the dictation shortcut
- **WHEN** the user releases the dictation shortcut
- **THEN** the runner SHALL stop capture after post-roll
- **AND** it SHALL send the captured utterance for final transcription.

### Requirement: CPU model benchmark evidence
The project SHALL evaluate CPU dictation model changes with measured latency and quality evidence before changing the default model.

#### Scenario: Benchmark runs candidate models
- **WHEN** a CPU dictation model benchmark is run
- **THEN** it SHALL record model name, startup readiness time, transcription time, audio duration, realtime factor, and transcript text.

#### Scenario: Benchmark avoids persistent model cache pollution
- **WHEN** candidate models are benchmarked in Docker
- **THEN** temporary benchmark containers and volumes SHALL be removed after each candidate
- **AND** the existing production `whisper-server` container and volume SHALL remain unchanged.

#### Scenario: Reference transcript is unavailable
- **WHEN** no human reference transcript is provided
- **THEN** the benchmark SHALL label quality metrics against the current large model as pseudo-reference evidence.
