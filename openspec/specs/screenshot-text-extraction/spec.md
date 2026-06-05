# Purpose

Definir una herramienta que permita capturar una región de pantalla, extraer exactamente el texto visible y copiar el resultado al portapapeles del sistema.

## Requirements

### Requirement: Inicio de captura desde una herramienta del sistema
El sistema SHALL permitir lanzar un flujo de captura parcial de pantalla desde una acción accesible para el usuario, como el overlay de herramientas.

#### Scenario: Selección de la herramienta de extracción
- **WHEN** el usuario activa la herramienta de extracción de texto desde el overlay o mecanismo equivalente
- **THEN** el sistema SHALL entrar en un modo de captura de región

### Requirement: Selección manual de una región rectangular
El sistema SHALL permitir al usuario marcar con el ratón un área rectangular de la pantalla como entrada de la extracción.

#### Scenario: El usuario arrastra para seleccionar una región
- **WHEN** el sistema está en modo de captura
- **THEN** el usuario SHALL poder seleccionar visualmente un rectángulo con el cursor

### Requirement: Envío automático de la captura al backend local
El sistema SHALL enviar automáticamente la región capturada al servicio local de inferencia sin pasos manuales adicionales.

#### Scenario: La captura finaliza
- **WHEN** el usuario confirma una selección válida
- **THEN** la imagen resultante SHALL enviarse a la API local para su procesamiento

### Requirement: Extracción textual exacta sin texto adicional
El sistema SHALL devolver únicamente el contenido textual detectado en la imagen, sin explicaciones, prólogos ni comentarios añadidos.

#### Scenario: La imagen contiene texto legible
- **WHEN** el backend procesa una captura con texto visible
- **THEN** la salida SHALL contener solo el texto extraído con la mayor fidelidad posible

#### Scenario: La respuesta se prepara para pegado directo
- **WHEN** la extracción se completa
- **THEN** la herramienta SHALL evitar añadir etiquetas, encabezados o frases como introducción al contenido

### Requirement: Copia automática al portapapeles
El sistema SHALL copiar el texto extraído al portapapeles del sistema para poder pegarlo inmediatamente en cualquier contexto.

#### Scenario: Extracción completada
- **WHEN** el backend devuelve el texto extraído
- **THEN** el sistema SHALL copiar ese contenido al portapapeles del usuario
