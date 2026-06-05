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
El sistema SHALL exponer una entrada de audio virtual que pueda elegirse como micrófono en aplicaciones como Zoom, Slack, Meet u otras similares.

#### Scenario: Selección desde una app de videollamada
- **WHEN** una aplicación enumera los micrófonos disponibles del sistema
- **THEN** el micrófono virtual SHALL aparecer como una opción utilizable

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
