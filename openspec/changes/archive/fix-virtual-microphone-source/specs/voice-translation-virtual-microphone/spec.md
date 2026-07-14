## MODIFIED Requirements

### Requirement: Micrófono virtual seleccionable por aplicaciones externas
El sistema SHALL exponer una entrada de audio virtual explícita que pueda elegirse como micrófono en aplicaciones como Zoom, Slack, Meet u otras similares. El nombre que se muestra al usuario SHALL corresponder a una fuente de entrada seleccionable y no al monitor de un altavoz virtual.

#### Scenario: Selección desde una app de videollamada
- **WHEN** una aplicación enumera los micrófonos disponibles del sistema
- **THEN** el micrófono virtual SHALL aparecer como una opción utilizable
- **AND** el usuario SHALL poder seleccionarlo como entrada de micrófono sin cambiar su altavoz de salida

#### Scenario: Slack enumera entradas y salidas por separado
- **WHEN** Slack u otra aplicación muestre listas separadas de micrófono y altavoz
- **THEN** `so_ai_translated_mic` SHALL aparecer en la lista de micrófonos
- **AND** el usuario SHALL keep su altavoz normal para escuchar la llamada

### Requirement: Implementación inicial Linux PulseAudio
La primera implementación SHALL soportar Linux mediante herramientas compatibles con PulseAudio, creando un sink interno para mezcla y una fuente de entrada virtual remapeada para aplicaciones externas.

#### Scenario: Dependencias de audio disponibles
- **WHEN** `pactl`, `parec` y `pacat` estén disponibles
- **THEN** la herramienta SHALL crear el sink interno, crear la fuente virtual de micrófono, capturar el micrófono físico y escribir audio traducido en el sink interno
- **AND** la fuente virtual SHALL publicar la mezcla final como entrada de micrófono seleccionable

#### Scenario: Dependencias de audio ausentes
- **WHEN** falte una dependencia requerida
- **THEN** la herramienta SHALL fallar con un mensaje claro y sin dejar módulos de audio huérfanos

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
