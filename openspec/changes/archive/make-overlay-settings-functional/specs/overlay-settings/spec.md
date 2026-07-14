## MODIFIED Requirements

### Requirement: Gestión de atajos por herramienta
El sistema SHALL permitir configurar el atajo global asociado a cada herramienta que lo soporte.

#### Scenario: Cambio de atajo
- **WHEN** el usuario reasigna la combinación de teclas de una herramienta desde el panel de ajustes
- **THEN** el sistema SHALL persistir el nuevo atajo
- **AND** la interfaz SHALL volver a mostrar el valor guardado al reabrir ajustes

#### Scenario: Conflicto entre atajos
- **WHEN** el usuario intenta guardar una combinación que ya está en uso por otra herramienta del proyecto
- **THEN** el sistema SHALL avisar del conflicto
- **AND** SHALL avoid persisting the conflicting assignment.

### Requirement: Persistencia de configuración
El sistema SHALL conservar los ajustes del usuario entre sesiones.

#### Scenario: Reinicio de la aplicación o del sistema
- **WHEN** el usuario vuelve a abrir el sistema de herramientas tras cerrarlo
- **THEN** sus ajustes previos SHALL seguir disponibles

#### Scenario: Settings file is missing or malformed
- **WHEN** the desktop app cannot read a valid settings file
- **THEN** it SHALL fall back to default settings
- **AND** it SHALL keep the settings panel usable.
