# Purpose

Definir un agente conversacional accesible desde el overlay que pueda responder preguntas y usar herramientas del sistema para completar tareas.

## Requirements

### Requirement: Barra de entrada conversacional en el overlay
El sistema SHALL incluir dentro del overlay una barra horizontal de texto para enviar consultas o instrucciones al agente.

#### Scenario: El usuario formula una petición
- **WHEN** el usuario escribe una consulta en la barra y la envía
- **THEN** el sistema SHALL iniciar una interacción con el agente

### Requirement: Respuesta útil a preguntas generales y operativas
El agente SHALL poder responder consultas del usuario tanto sobre información general como sobre recursos disponibles en el sistema.

#### Scenario: Consulta general
- **WHEN** el usuario hace una pregunta sin necesitar acciones sobre el sistema
- **THEN** el agente SHALL devolver una respuesta textual adecuada dentro de la experiencia definida

### Requirement: Acceso a herramientas del sistema
El agente SHALL disponer de herramientas del sistema para ejecutar acciones o búsquedas cuando la consulta lo requiera.

#### Scenario: La consulta requiere una herramienta
- **WHEN** el usuario pide una acción o búsqueda que depende de datos locales del sistema
- **THEN** el agente SHALL poder invocar la herramienta adecuada antes de responder

### Requirement: Búsqueda de archivos y contenido en archivos
El agente SHALL poder buscar archivos del sistema y localizar contenido dentro de ellos para responder consultas o ayudar al usuario.

#### Scenario: Búsqueda por nombre o ubicación
- **WHEN** el usuario pide encontrar un archivo o carpeta
- **THEN** el agente SHALL poder buscar recursos del sistema de archivos y presentar los resultados relevantes

#### Scenario: Búsqueda dentro del contenido
- **WHEN** el usuario pide encontrar información contenida dentro de archivos
- **THEN** el agente SHALL poder buscar texto o contenido estructurado dentro de archivos accesibles

### Requirement: Integración con otras herramientas del proyecto
El agente SHALL poder reutilizar herramientas ya existentes del sistema cuando eso ayude a cumplir una solicitud.

#### Scenario: Una consulta deriva en una acción del proyecto
- **WHEN** el usuario pide algo que puede resolverse con otra capability del sistema
- **THEN** el agente SHALL poder lanzar o coordinar esa capability según las reglas del producto

### Requirement: Transparencia operativa mínima
La experiencia SHALL dejar claro cuándo el agente está procesando, buscando o esperando resultados de herramientas.

#### Scenario: La respuesta requiere trabajo intermedio
- **WHEN** el agente necesita ejecutar búsquedas o herramientas antes de contestar
- **THEN** la interfaz SHALL reflejar un estado de trabajo para que el usuario entienda que la petición sigue en curso
