# Purpose

Definir una herramienta que capture el audio que suena en el sistema operativo, lo transcriba o traduzca en tiempo real y muestre el resultado en una ventana dedicada.

## Requirements

### Requirement: Inicio desde una herramienta del overlay
El sistema SHALL permitir lanzar la herramienta de transcripción o traducción en tiempo real desde el overlay de herramientas del sistema.

#### Scenario: Selección de la herramienta desde el overlay
- **WHEN** el usuario pulsa el botón correspondiente dentro del overlay
- **THEN** el sistema SHALL abrir una ventana de aplicación dedicada a esa herramienta

### Requirement: Ventana dedicada con control explícito de captura
La herramienta SHALL mostrar una ventana propia desde la que el usuario pueda iniciar o detener la captura de audio del sistema.

#### Scenario: La ventana se abre
- **WHEN** la herramienta es lanzada
- **THEN** el usuario SHALL ver una interfaz con un control claro para encender o apagar la captura

#### Scenario: El usuario apaga la captura
- **WHEN** el usuario desactiva la captura desde la ventana
- **THEN** el sistema SHALL detener el procesamiento en vivo sin cerrar necesariamente la ventana

### Requirement: Captura de audio de salida del sistema
El sistema SHALL recoger el audio que está sonando por el sistema operativo en ese momento, independientemente de la aplicación que lo reproduzca.

#### Scenario: Audio procedente de una videollamada o reproductor
- **WHEN** una aplicación como Meet, Zoom, Slack u otra emite voz por los altavoces del sistema
- **THEN** la herramienta SHALL poder usar ese audio como entrada de la transcripción

#### Scenario: Independencia respecto de la aplicación origen
- **WHEN** la fuente de audio cambia entre distintas aplicaciones
- **THEN** la herramienta SHALL seguir operando sobre el audio del sistema sin requerir integración específica por aplicación

### Requirement: Transcripción en streaming con baja latencia percibida
El sistema SHALL mostrar resultados parciales o actualizaciones frecuentes en la ventana con la menor latencia razonable para que la lectura resulte útil en vivo.

#### Scenario: Habla continua en inglés
- **WHEN** el sistema está capturando una conversación en el idioma inicialmente soportado
- **THEN** la interfaz SHALL actualizar el texto visible de forma progresiva mientras llega el audio

### Requirement: Modo de transcripción y modo de traducción
La herramienta SHALL poder ofrecer al menos un modo de transcripción directa y un modo de traducción a otro idioma de salida.

#### Scenario: Modo transcripción
- **WHEN** el usuario usa la herramienta en modo transcripción
- **THEN** el sistema SHALL mostrar el contenido reconocido en el mismo idioma hablado cuando sea posible

#### Scenario: Modo traducción inicial desde inglés
- **WHEN** el usuario usa la herramienta en modo traducción sobre audio hablado en inglés
- **THEN** el sistema SHALL mostrar el resultado traducido al idioma de salida configurado

### Requirement: Soporte incremental de idiomas
El sistema SHALL permitir empezar por inglés como primer idioma soportado y dejar abierta la ampliación posterior a más idiomas.

#### Scenario: Primera iteración limitada de idiomas
- **WHEN** se construye la primera versión de esta herramienta
- **THEN** el alcance SHALL poder limitarse a inglés sin bloquear la arquitectura para idiomas futuros

### Requirement: Interfaz legible para seguimiento en directo
La ventana SHALL priorizar la legibilidad del texto en vivo y el estado operativo de la captura.

#### Scenario: Captura activa
- **WHEN** la herramienta está escuchando el audio del sistema
- **THEN** la interfaz SHALL indicar visualmente que la captura está activa y mostrar el texto actualizado

#### Scenario: No hay audio útil o la captura está detenida
- **WHEN** no se recibe voz o la herramienta está detenida
- **THEN** la interfaz SHALL reflejar ese estado sin mostrar resultados engañosos como si hubiera transcripción en curso

### Requirement: Gestión clara de errores y permisos
El sistema SHALL comunicar problemas de permisos, ausencia de dispositivo compatible o fallo del backend de forma comprensible para el usuario.

#### Scenario: El sistema no permite capturar la salida de audio
- **WHEN** la herramienta no puede engancharse al audio del sistema en el entorno actual
- **THEN** la interfaz SHALL informar del problema en lugar de permanecer aparentemente activa sin resultados

#### Scenario: El backend local falla durante el streaming
- **WHEN** el backend deja de devolver actualizaciones válidas
- **THEN** la herramienta SHALL mostrar el error y detener o degradar el flujo de forma controlada
