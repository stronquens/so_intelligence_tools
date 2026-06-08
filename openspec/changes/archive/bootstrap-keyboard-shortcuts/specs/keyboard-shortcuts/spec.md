# Delta Spec

## ADDED Requirements

### Requirement: Asociación explícita entre atajo y capability
La primera implementación SHALL permitir asociar un atajo global a una capability concreta del sistema.

#### Scenario: Atajo para corrección de texto seleccionado
- **WHEN** el usuario active el atajo configurado para corrección de texto
- **THEN** el sistema SHALL disparar la capability `selected-text-correction`

### Requirement: Primera ruta operativa Linux-first para texto seleccionado
La primera implementación SHALL ofrecer una ruta operativa en Linux para capturar el atajo y ejecutar una corrección real sobre texto seleccionado.

#### Scenario: Shortcut global dispara corrección real
- **WHEN** el listener global detecte el atajo registrado
- **THEN** el sistema SHALL intentar leer la selección actual, pedir la corrección al backend local y reemplazar el texto en foco

### Requirement: Registro reusable de acciones por shortcut
La primera implementación SHALL modelar el mapeo entre atajos y acciones como una capa reusable y testeable.

#### Scenario: Se registra una acción nueva
- **WHEN** una capability futura necesite un nuevo atajo
- **THEN** el sistema SHALL poder asociarla a una acción reusable sin modificar el listener base

### Requirement: Limitaciones operativas explícitas para Linux
La primera implementación SHALL documentar de forma explícita las limitaciones del mecanismo de shortcut y automatización del escritorio.

#### Scenario: El entorno no soporta la integración prevista
- **WHEN** el entorno Linux no permita capturar el atajo global o automatizar el foco como se espera
- **THEN** el sistema SHALL fallar con feedback claro y no de forma silenciosa
