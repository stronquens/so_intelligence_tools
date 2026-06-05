# Purpose

Definir un overlay del sistema que exponga de forma rápida las herramientas de IA disponibles para escritura y productividad.

## Requirements

### Requirement: Overlay invocable por atajo de teclado
El sistema SHALL mostrar un overlay de herramientas cuando el usuario pulse una combinación global definida.

#### Scenario: Apertura del overlay
- **WHEN** el usuario pulsa el atajo asignado al menú de herramientas
- **THEN** el sistema SHALL mostrar un overlay visible con las acciones disponibles

### Requirement: Catálogo inicial de acciones de escritura
El sistema SHALL ofrecer en el overlay un conjunto inicial de herramientas inspiradas en flujos de writing tools, como resumir, profesionalizar, reescribir o volver el tono más friendly.

#### Scenario: El overlay muestra acciones disponibles
- **WHEN** el overlay aparece en pantalla
- **THEN** el usuario SHALL poder ver varias acciones de IA identificables mediante botones o controles equivalentes

#### Scenario: Selección de una acción
- **WHEN** el usuario activa una de las acciones del overlay
- **THEN** el sistema SHALL lanzar el flujo asociado a esa herramienta concreta

### Requirement: Acceso a ajustes desde el overlay
El sistema SHALL ofrecer dentro del overlay una entrada visible a ajustes para configurar atajos de teclado y otras preferencias de las herramientas.

#### Scenario: Apertura de ajustes
- **WHEN** el usuario pulsa el botón o acceso de ajustes dentro del overlay
- **THEN** el sistema SHALL mostrar una interfaz para modificar configuraciones disponibles

#### Scenario: Reasignación de atajos
- **WHEN** el usuario cambia el atajo asociado a una herramienta desde ajustes
- **THEN** el sistema SHALL guardar y aplicar la nueva combinación de teclado a esa herramienta

### Requirement: Entrada conversacional embebida
El sistema SHALL incluir en el overlay una barra horizontal de texto para interactuar con un agente mediante lenguaje natural.

#### Scenario: El usuario escribe una consulta
- **WHEN** el overlay está abierto y el usuario escribe en la barra de entrada
- **THEN** el sistema SHALL enviar la consulta al agente conversacional asociado

#### Scenario: El agente responde dentro del overlay o flujo asociado
- **WHEN** el agente genera una respuesta o necesita lanzar una acción
- **THEN** el sistema SHALL mostrar la respuesta y ejecutar las herramientas necesarias según el diseño definido

### Requirement: Extensibilidad del catálogo
El sistema SHALL permitir añadir nuevas herramientas al overlay sin rediseñar toda la interfaz de lanzamiento.

#### Scenario: Se incorpora una nueva herramienta
- **WHEN** el proyecto añada una nueva capacidad compatible con el overlay
- **THEN** esta SHALL poder registrarse en el menú como una acción adicional

### Requirement: Integración con herramientas que actúan sobre contexto del usuario
El overlay SHALL poder disparar acciones basadas en selección de texto, portapapeles o captura de pantalla según la herramienta elegida.

#### Scenario: Una herramienta depende del texto seleccionado
- **WHEN** el usuario elige una acción del overlay que opera sobre texto seleccionado
- **THEN** el sistema SHALL reutilizar o solicitar el contexto necesario para ejecutar esa acción

#### Scenario: Una herramienta abre una ventana operativa persistente
- **WHEN** el usuario elige una acción del overlay que requiere una interfaz activa, como transcripción en tiempo real
- **THEN** el sistema SHALL abrir la ventana o superficie dedicada de esa herramienta
