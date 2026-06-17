# Purpose

Definir una herramienta de dictado push-to-talk que grabe audio mientras se mantiene pulsada una combinación de teclas, lo transcriba en local y escriba el texto donde esté el cursor.
## Requirements
### Requirement: Windows local push-to-talk dictation
The system SHALL provide local push-to-talk dictation on Windows using the configured local ASR runtime.

#### Scenario: User holds the Windows dictation shortcut
- **WHEN** the Windows dictation listener is running
- **AND** the user holds `Ctrl + Space`
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

