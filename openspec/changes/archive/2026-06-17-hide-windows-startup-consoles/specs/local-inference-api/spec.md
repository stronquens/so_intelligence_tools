## MODIFIED Requirements

### Requirement: Despliegue portable mediante contenedores
El sistema SHALL poder desplegar el servicio de inferencia dentro de Docker para facilitar instalacion, aislamiento y portabilidad.

#### Scenario: Despliegue inicial en Linux
- **WHEN** el proyecto se instala en un entorno Linux soportado
- **THEN** el backend SHALL poder levantarse mediante una configuracion basada en Docker

#### Scenario: Preparacion para otros sistemas
- **WHEN** se quiera portar el proyecto a otro sistema operativo
- **THEN** la arquitectura SHALL mantener la capa de inferencia aislada detras de la misma interfaz de API

#### Scenario: El usuario quiere liberar recursos del sistema
- **WHEN** el usuario decide apagar temporalmente la infraestructura local de inferencia
- **THEN** el despliegue SHALL permitir detener los contenedores asociados para liberar recursos del equipo

#### Scenario: Windows user startup
- **WHEN** the project is installed on Windows
- **THEN** the local inference API SHALL provide a user-level Startup launcher installer
- **AND** the launcher SHALL start the API from the project virtual environment without requiring administrator privileges
- **AND** the launcher SHALL run without leaving a visible terminal window open
- **AND** the launcher SHALL write process output to a diagnostic log file.

#### Scenario: El equipo quiere probar otro modelo local
- **WHEN** el proyecto necesite sustituir el modelo local validado por otro nuevo
- **THEN** la arquitectura SHALL permitir cambiar el runtime o perfil de modelo con el menor impacto posible sobre la interfaz publica del API
