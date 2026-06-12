# Purpose

Definir una herramienta que exponga un micrófono virtual compatible con aplicaciones de videollamada y que pueda traducir la voz del usuario en tiempo real por streaming.
## Requirements
### Requirement: Activación y desactivación explícitas
El sistema SHALL permitir activar o desactivar la herramienta mediante un comando, atajo o control equivalente del sistema.

#### Scenario: La herramienta se enciende
- **WHEN** el usuario activa la herramienta
- **THEN** el sistema SHALL iniciar el pipeline de audio correspondiente y mostrar un estado visible de que está disponible

#### Scenario: La herramienta se apaga
- **WHEN** el usuario desactiva la herramienta
- **THEN** el sistema SHALL detener el pipeline y retirar el estado visible o marcarlo como inactivo

### Requirement: Indicador persistente de estado en el sistema
La herramienta SHALL mostrar un indicador representativo en la notificación persistente o toolbar del sistema mientras esté habilitada o disponible.

#### Scenario: Herramienta activa
- **WHEN** la funcionalidad está encendida
- **THEN** el usuario SHALL poder identificar en el sistema que el micrófono virtual especial está activo

### Requirement: Micrófono virtual seleccionable por aplicaciones externas
El sistema SHALL exponer una entrada de audio virtual explícita que pueda elegirse como micrófono en aplicaciones como Zoom, Slack, Meet u otras similares. El nombre que se muestra al usuario SHALL corresponder a una fuente de entrada seleccionable y no al monitor de un altavoz virtual.

#### Scenario: Selección desde una app de videollamada
- **WHEN** una aplicación enumera los micrófonos disponibles del sistema
- **THEN** el micrófono virtual SHALL aparecer como una opción utilizable
- **AND** el usuario SHALL poder seleccionarlo como entrada de micrófono sin cambiar su altavoz de salida

#### Scenario: Slack enumera entradas y salidas por separado
- **WHEN** Slack u otra aplicación muestre listas separadas de micrófono y altavoz
- **THEN** `so_ai_translated_mic` SHALL aparecer en la lista de micrófonos
- **AND** el usuario SHALL mantener su altavoz normal para escuchar la llamada

### Requirement: Modo passthrough cuando no hay traducción activa
El micrófono virtual SHALL poder reenviar la voz del usuario sin transformarla cuando la herramienta no esté traduciendo.

#### Scenario: Herramienta disponible sin traducción activa
- **WHEN** la funcionalidad está encendida pero no está aplicando traducción
- **THEN** el micrófono virtual SHALL transmitir la voz original del usuario de forma normal

### Requirement: Traducción de voz en tiempo real por streaming
El sistema SHALL poder reemplazar la voz original por una versión hablada en otro idioma, generada en tiempo real a partir del contenido capturado del micrófono físico.

#### Scenario: Traducción activa
- **WHEN** el usuario habla por su micrófono físico y la traducción está activada
- **THEN** el sistema SHALL enviar el audio por streaming y publicar por el micrófono virtual una salida traducida en el idioma de destino

### Requirement: Uso de API externa de traducción en tiempo real
Esta capability SHALL utilizar una API de traducción en tiempo real por streaming en lugar del backend local del proyecto.

#### Scenario: Pipeline de traducción
- **WHEN** la herramienta necesita traducir y sintetizar la voz del usuario
- **THEN** el flujo SHALL apoyarse en la API de traducción en tiempo real de OpenAI o equivalente configurado

### Requirement: Compatibilidad transversal con apps de comunicación
La herramienta SHALL comportarse como una integración de sistema y no como una integración específica por aplicación.

#### Scenario: Cambio entre distintas apps
- **WHEN** el usuario cambia entre Zoom, Meet, Slack u otra app compatible
- **THEN** la funcionalidad SHALL seguir operando mientras la aplicación permita seleccionar el micrófono virtual

### Requirement: Latencia apta para conversación
El sistema SHALL priorizar un flujo de streaming con latencia suficientemente baja para no romper una conversación en vivo.

#### Scenario: Conversación bidireccional
- **WHEN** el usuario participa en una llamada y usa la traducción
- **THEN** la demora introducida SHALL mantenerse dentro de un rango razonable para uso conversacional

### Requirement: Degradación segura ante fallo
El sistema SHALL manejar fallos del servicio externo, del micrófono físico o del dispositivo virtual sin generar estados ambiguos para el usuario.

#### Scenario: Falla la API externa
- **WHEN** el servicio de traducción en streaming deja de responder o entrega resultados inválidos
- **THEN** el sistema SHALL informar del problema y detener la salida traducida o volver al passthrough según la estrategia definida

#### Scenario: El micrófono virtual no puede publicarse
- **WHEN** el entorno no permite crear o mantener el dispositivo virtual
- **THEN** el sistema SHALL mostrar un error claro y no simular que la herramienta está funcionando correctamente

### Requirement: Implementación inicial Linux PulseAudio
La primera implementación SHALL soportar Linux mediante herramientas compatibles con PulseAudio, creando un sink interno para mezcla y una fuente de entrada virtual remapeada para aplicaciones externas.

#### Scenario: Dependencias de audio disponibles
- **WHEN** `pactl`, `parec` y `pacat` estén disponibles
- **THEN** la herramienta SHALL crear el sink interno, crear la fuente virtual de micrófono, capturar el micrófono físico y escribir audio traducido en el sink interno
- **AND** la fuente virtual SHALL publicar la mezcla final como entrada de micrófono seleccionable

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
- **AND** SHALL mostrar en la ventana el nombre de la fuente de micrófono virtual que debe seleccionarse en aplicaciones externas

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

### Requirement: Niveles seguros de mezcla de voz traducida
El sistema SHALL usar valores por defecto conservadores para que la voz original en passthrough no compita con la voz traducida durante una llamada.

#### Scenario: Traducción activa con valores por defecto
- **WHEN** el usuario active la traducción de voz sin ajustar volúmenes avanzados
- **THEN** el passthrough original SHALL quedar muy reducido
- **AND** la salida traducida SHALL mantener headroom para reducir clipping

#### Scenario: Ducking configurado accidentalmente alto
- **WHEN** el entorno configure un volumen ducked superior al techo de seguridad
- **THEN** el pipeline SHALL usar el techo de seguridad durante traducción
- **AND** SHALL registrar el valor solicitado y el valor aplicado

### Requirement: Protección básica contra clipping de salida
El sistema SHALL limitar la salida PCM traducida antes de escribirla al micrófono virtual para evitar muestras fuera de rango o saturación por ganancia.

#### Scenario: Audio traducido con ganancia alta
- **WHEN** el proveedor realtime entregue PCM y el volumen de salida lo amplifique
- **THEN** el sistema SHALL limitar las muestras a un techo seguro antes de escribirlas

### Requirement: Rechazo de fuentes de captura peligrosas
El sistema SHALL rechazar fuentes físicas que sean monitores de salida o dispositivos virtuales propios del proyecto.

#### Scenario: Fuente configurada como monitor de salida
- **WHEN** `VOICE_TRANSLATION_PHYSICAL_SOURCE` termine en `.monitor`
- **THEN** la herramienta SHALL fallar con un mensaje claro antes de iniciar captura

#### Scenario: Fuente configurada como micro virtual propio
- **WHEN** `VOICE_TRANSLATION_PHYSICAL_SOURCE` apunte a `so_ai_translated_mic` o su sink interno
- **THEN** la herramienta SHALL fallar con un mensaje claro para evitar realimentación
