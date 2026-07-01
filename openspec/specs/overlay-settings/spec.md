# Purpose

Definir la experiencia de ajustes accesible desde el overlay para configurar atajos de teclado y otras preferencias del sistema de herramientas.

## Requirements

### Requirement: Acceso a configuracion desde el overlay principal
El sistema SHALL permitir abrir ajustes directamente desde la interfaz principal del overlay.

#### Scenario: El usuario quiere cambiar una preferencia
- **WHEN** el usuario abre el overlay y pulsa el acceso de ajustes
- **THEN** el sistema SHALL mostrar una ventana independiente de configuracion
- **AND** la ventana principal del overlay SHALL permanecer abierta

### Requirement: Gestion de atajos por herramienta
El sistema SHALL permitir configurar el atajo global asociado a cada herramienta que lo soporte.

#### Scenario: Cambio de atajo
- **WHEN** el usuario reasigna la combinacion de teclas de una herramienta
- **THEN** el sistema SHALL persistir el nuevo atajo y usarlo en futuras ejecuciones

#### Scenario: Conflicto entre atajos
- **WHEN** el usuario intenta asignar una combinacion que ya esta en uso por otra herramienta del proyecto
- **THEN** el sistema SHALL avisar del conflicto o guiar al usuario para resolverlo

### Requirement: Extensibilidad de preferencias
La interfaz de ajustes SHALL admitir nuevas preferencias funcionales a medida que aparezcan mas herramientas.

#### Scenario: Se anade una nueva opcion configurable
- **WHEN** una capability futura introduce parametros adicionales
- **THEN** el sistema SHALL poder exponerlos en la misma area de ajustes sin redisenar por completo la experiencia

### Requirement: Persistencia de configuracion
El sistema SHALL conservar los ajustes del usuario entre sesiones.

#### Scenario: Reinicio de la aplicacion o del sistema
- **WHEN** el usuario vuelve a abrir el sistema de herramientas tras cerrarlo
- **THEN** sus ajustes previos SHALL seguir disponibles

### Requirement: Dictation shortcut default migration
The desktop settings layer SHALL migrate known legacy push-to-talk dictation defaults to the current project default.

#### Scenario: Legacy dictation shortcut is loaded
- **WHEN** persisted desktop settings contain a known legacy dictation shortcut such as `Ctrl + Space`, `Ctrl + Shift + D`, or `Ctrl + Alt + Space`
- **THEN** the desktop settings layer SHALL replace it with `Ctrl + Shift + Space`.
