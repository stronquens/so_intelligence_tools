# Purpose

Definir una herramienta que corrija texto seleccionado en cualquier aplicación usando un LLM local y sustituya el contenido original por la versión corregida.

## Requirements

### Requirement: Corrección sobre texto previamente seleccionado
El sistema SHALL operar sobre texto que ya esté seleccionado por el usuario dentro de una aplicación cualquiera.

#### Scenario: Hay texto seleccionado
- **WHEN** el usuario selecciona texto en una aplicación y activa el atajo de corrección
- **THEN** la herramienta SHALL leer el texto seleccionado como entrada de la operación

#### Scenario: No hay texto seleccionado
- **WHEN** el usuario activa el atajo de corrección sin texto seleccionado
- **THEN** el sistema SHALL mostrar una notificación indicando que no hay texto seleccionado

### Requirement: Sustitución directa del texto por la versión corregida
El sistema SHALL reemplazar el contenido seleccionado por la versión corregida sin obligar al usuario a pegar manualmente un resultado intermedio.

#### Scenario: La corrección se completa correctamente
- **WHEN** la herramienta recibe una respuesta válida del backend de inferencia
- **THEN** el texto original seleccionado SHALL ser sustituido por el texto corregido en la misma aplicación

#### Scenario: El entorno impide la sustitución automática
- **WHEN** la herramienta recibe una respuesta válida pero el entorno del escritorio no permite completar la inserción automática
- **THEN** el sistema SHALL dejar el texto corregido en el portapapeles y notificar al usuario para que pueda pegarlo manualmente

### Requirement: Preservación del idioma original
El sistema SHALL mantener el idioma original del texto de entrada durante la corrección ortográfica y de estilo básico.

#### Scenario: Texto en español
- **WHEN** el usuario corrige un texto escrito en español
- **THEN** la salida SHALL mantenerse en español y corregir solo ortografía, gramática o errores menores

#### Scenario: Texto en otro idioma
- **WHEN** el usuario corrige un texto escrito en otro idioma soportado por el modelo
- **THEN** la salida SHALL mantenerse en ese idioma en lugar de traducirse

### Requirement: Conservación de intención y alcance mínimo
El sistema SHALL corregir el texto sin reescribirlo de forma innecesaria ni alterar su intención principal.

#### Scenario: Texto con errores simples
- **WHEN** el texto contiene faltas ortográficas o pequeños errores de puntuación
- **THEN** la herramienta SHALL priorizar una corrección mínima sobre una reescritura extensa

### Requirement: Compatibilidad operativa con Linux real
La herramienta SHALL adaptarse al entorno Linux disponible y documentar su camino operativo recomendado.

#### Scenario: Sesión X11 disponible
- **WHEN** el sistema se ejecute en una sesión Linux `X11`
- **THEN** la herramienta SHALL usar ese entorno como camino recomendado para la sustitución automática completa

#### Scenario: Sustitución automática en X11
- **WHEN** el sistema se ejecute en una sesión Linux `X11`
- **THEN** la herramienta MAY leer la selección activa desde la selección primaria `PRIMARY`
- **AND** MAY realizar la inserción final usando el portapapeles como mecanismo de pegado estable

#### Scenario: Sesión Wayland con limitaciones de inyección
- **WHEN** el sistema se ejecute en Wayland y la automatización de teclado no sea totalmente fiable
- **THEN** la herramienta SHALL mantener la corrección del texto como capability usable aunque deba degradar a portapapeles
