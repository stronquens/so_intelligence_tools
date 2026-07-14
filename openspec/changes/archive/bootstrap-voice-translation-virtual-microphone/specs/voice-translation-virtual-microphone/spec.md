## ADDED Requirements

### Requirement: Implementación inicial Linux PulseAudio
La primera implementación SHALL soportar Linux mediante herramientas compatibles con PulseAudio.

#### Scenario: Dependencias de audio disponibles
- **WHEN** `pactl`, `parec` y `pacat` estén disponibles
- **THEN** la herramienta SHALL poder crear el dispositivo virtual, capturar el micrófono físico y escribir audio traducido en el sink virtual

#### Scenario: Dependencias de audio ausentes
- **WHEN** falte una dependencia requerida
- **THEN** la herramienta SHALL fallar con un mensaje claro y sin dejar módulos de audio huérfanos

### Requirement: Traducción speech-to-speech remota
La primera implementación SHALL enviar audio del micrófono físico a un proveedor remoto realtime y SHALL usar audio generado por el proveedor como salida del micrófono virtual.

#### Scenario: Sesión realtime activa
- **WHEN** el usuario habla castellano por el micrófono físico
- **THEN** el sistema SHALL enviar chunks PCM por streaming al proveedor remoto
- **AND** SHALL escribir chunks PCM traducidos al sink virtual según vayan llegando

### Requirement: Configuración por entorno
La herramienta SHALL poder configurarse por variables de entorno sin modificar código.

#### Scenario: Configuración por defecto
- **WHEN** el usuario configure `OPENAI_API_KEY`
- **THEN** la herramienta SHALL poder usar OpenAI Realtime Translate con castellano como idioma origen e inglés como idioma destino

#### Scenario: Configuración avanzada
- **WHEN** el usuario configure modelo, idioma origen, idioma destino, fuente física, nombre de sink virtual o atajo
- **THEN** la herramienta SHALL respetar esos valores en la sesión siguiente

### Requirement: Toggle por comando y atajo
La herramienta SHALL poder iniciarse y detenerse desde un comando idempotente, apto para enlazarse a un atajo del sistema.

#### Scenario: Primera pulsación del atajo
- **WHEN** no exista una sesión activa
- **THEN** el comando SHALL iniciar una nueva sesión de traducción de voz

#### Scenario: Segunda pulsación del atajo
- **WHEN** exista una sesión activa
- **THEN** el comando SHALL solicitar parada y limpiar el pipeline

### Requirement: Logs de sesión
La herramienta SHALL registrar eventos relevantes de cada sesión sin guardar secretos.

#### Scenario: Cierre de sesión
- **WHEN** la sesión termine
- **THEN** el sistema SHALL escribir un log con modelo, idiomas, dispositivo virtual, eventos de estado y errores relevantes

### Requirement: Control desde la ventana de traducción en tiempo real
La herramienta SHALL poder activarse desde la aplicación existente de traducción en tiempo real sin reemplazar su pipeline de audio del sistema.

#### Scenario: Activación desde la ventana
- **WHEN** la ventana de traducción de audio del sistema esté abierta
- **AND** el usuario pulse el botón para activar su voz traducida
- **THEN** el sistema SHALL iniciar el micrófono virtual traducido en paralelo
- **AND** SHALL mostrar en la ventana el nombre del micrófono virtual que debe seleccionarse en aplicaciones externas

#### Scenario: Desactivación desde la ventana
- **WHEN** el micrófono virtual traducido esté activo desde la ventana
- **AND** el usuario pulse el mismo botón de nuevo o cierre la ventana
- **THEN** el sistema SHALL detener la traducción de voz y limpiar el dispositivo virtual

### Requirement: Passthrough permanente mientras la ventana está abierta
La ventana de traducción SHALL mantener disponible un micrófono virtual en modo passthrough mientras esté abierta.

#### Scenario: Ventana abierta sin traducción de voz activa
- **WHEN** la ventana de traducción se abra correctamente
- **THEN** el sistema SHALL crear el micrófono virtual
- **AND** SHALL reenviar el audio del micrófono físico configurado hacia el micrófono virtual sin traducción
- **AND** SHALL informar al usuario qué fuente virtual debe seleccionar en aplicaciones externas

#### Scenario: Activación de traducción de voz con ducking
- **WHEN** el usuario active la traducción de su voz
- **THEN** el sistema SHALL reducir el volumen del passthrough original
- **AND** SHALL superponer la salida traducida en el mismo micrófono virtual con volumen configurable

#### Scenario: Desactivación de traducción de voz
- **WHEN** el usuario desactive la traducción de su voz
- **THEN** el sistema SHALL detener el consumo remoto
- **AND** SHALL restaurar el volumen normal del passthrough original

### Requirement: Grabación debug opcional del micro virtual final
La herramienta SHALL poder grabar el audio final del micrófono virtual en un archivo WAV solo cuando el usuario active explícitamente el modo debug por entorno.

#### Scenario: Debug recording activado
- **WHEN** `VOICE_TRANSLATION_DEBUG_RECORDING_ENABLED` esté activado
- **AND** el pipeline del micrófono virtual se inicie correctamente
- **THEN** el sistema SHALL grabar el monitor del sink virtual en un archivo WAV por sesión
- **AND** el WAV SHALL incluir la mezcla final que recibirían aplicaciones externas, incluyendo passthrough, ducking y traducción superpuesta
- **AND** el log de sesión SHALL registrar la ruta del archivo generado

#### Scenario: Debug recording desactivado
- **WHEN** `VOICE_TRANSLATION_DEBUG_RECORDING_ENABLED` no esté activado
- **THEN** el sistema SHALL no guardar audio WAV de la sesión
