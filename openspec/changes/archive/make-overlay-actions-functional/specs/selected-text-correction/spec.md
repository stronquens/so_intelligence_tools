## ADDED Requirements

### Requirement: Corrección invocable desde el overlay
La corrección de texto seleccionado SHALL poder ejecutarse desde la tarjeta `Corregir texto` del overlay además de los atajos y comandos existentes.

#### Scenario: El usuario pulsa Corregir texto en el overlay
- **WHEN** el overlay está visible
- **AND** el usuario pulsa la tarjeta `Corregir texto`
- **THEN** Electron SHALL ocultar el overlay antes de ejecutar la corrección
- **AND** SHALL invocar el runner existente de corrección de texto seleccionado.

#### Scenario: La corrección devuelve feedback al overlay
- **WHEN** la acción de corrección termina
- **THEN** Electron SHALL devolver al renderer un resultado estructurado de éxito o fallo
- **AND** el overlay SHALL mostrar un mensaje de estado comprensible para el usuario.
