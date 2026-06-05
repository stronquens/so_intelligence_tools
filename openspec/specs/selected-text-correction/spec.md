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
