# Delta Spec

## ADDED Requirements

### Requirement: Servicio de inferencia accesible por API
El sistema SHALL exponer un servicio accesible por API local al sistema para recibir peticiones de inferencia desde las herramientas cliente del sistema operativo.

#### Scenario: Puerto local configurable
- **WHEN** otro proceso local ya use el puerto por defecto del backend
- **THEN** el servicio SHALL poder moverse a otro puerto local mediante configuración
- **AND** las herramientas cliente SHALL poder apuntar a la nueva base URL sin cambios de código
