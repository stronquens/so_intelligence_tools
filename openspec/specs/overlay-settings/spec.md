# Purpose

Definir la experiencia de ajustes accesible desde el overlay para configurar atajos de teclado y otras preferencias del sistema de herramientas.

## Requirements

### Requirement: Acceso a configuración desde el overlay principal
El sistema SHALL permitir abrir ajustes directamente desde la interfaz principal del overlay.

#### Scenario: El usuario quiere cambiar una preferencia
- **WHEN** el usuario abre el overlay y pulsa el acceso de ajustes
- **THEN** el sistema SHALL mostrar una vista o panel de configuración

### Requirement: Gestión de atajos por herramienta
El sistema SHALL permitir configurar el atajo global asociado a cada herramienta que lo soporte.

#### Scenario: Cambio de atajo
- **WHEN** el usuario reasigna la combinación de teclas de una herramienta
- **THEN** el sistema SHALL persistir el nuevo atajo y usarlo en futuras ejecuciones

#### Scenario: Conflicto entre atajos
- **WHEN** el usuario intenta asignar una combinación que ya está en uso por otra herramienta del proyecto
- **THEN** el sistema SHALL avisar del conflicto o guiar al usuario para resolverlo

### Requirement: Extensibilidad de preferencias
La interfaz de ajustes SHALL admitir nuevas preferencias funcionales a medida que aparezcan más herramientas.

#### Scenario: Se añade una nueva opción configurable
- **WHEN** una capability futura introduce parámetros adicionales
- **THEN** el sistema SHALL poder exponerlos en la misma área de ajustes sin rediseñar por completo la experiencia

### Requirement: Persistencia de configuración
El sistema SHALL conservar los ajustes del usuario entre sesiones.

#### Scenario: Reinicio de la aplicación o del sistema
- **WHEN** el usuario vuelve a abrir el sistema de herramientas tras cerrarlo
- **THEN** sus ajustes previos SHALL seguir disponibles
