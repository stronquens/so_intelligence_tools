# Delta Spec

## ADDED Requirements

### Requirement: Arquitectura modular por puertos y composición
La primera implementación de `python-tool-runners` SHALL organizarse como una capa modular basada en composición, puertos explícitos y adapters reemplazables.

#### Scenario: La lógica de aplicación no conoce el sistema operativo concreto
- **WHEN** un caso de uso de herramienta necesite leer o escribir contexto del sistema
- **THEN** SHALL depender de puertos abstractos en lugar de invocar utilidades Linux directamente

#### Scenario: El proyecto necesita portar la misma herramienta a otro sistema
- **WHEN** una capability futura deba funcionar en otro sistema operativo
- **THEN** la lógica de aplicación SHALL poder reutilizarse sustituyendo adapters sin reescribir el caso de uso principal

### Requirement: Cliente Python reusable para la API local
La primera implementación SHALL incluir un cliente Python tipado y reusable para consumir `local-inference-api`.

#### Scenario: Una herramienta batch necesita una respuesta textual
- **WHEN** un caso de uso solicite inferencia textual
- **THEN** SHALL hacerlo a través de un cliente Python interno y no mediante llamadas HTTP dispersas

#### Scenario: El backend local falla
- **WHEN** el cliente Python no pueda completar la petición a la API local
- **THEN** SHALL traducir ese fallo a errores semánticos reutilizables por la capa de aplicación

### Requirement: Primera iteración limitada a flujos batch de texto e imagen
La primera implementación de la capability SHALL cubrir solo flujos batch de texto e imagen.

#### Scenario: El equipo implementa el bootstrap de runners
- **WHEN** se ejecute esta primera iteración
- **THEN** SHALL incluir soporte reusable para texto e imagen
- **AND** SHALL dejar audio y streaming fuera del alcance de implementación

### Requirement: Entry points finos y reutilización del núcleo
La primera implementación SHALL exponer entrypoints ligeros que solo compongan dependencias y disparen casos de uso reutilizables.

#### Scenario: Un comando CLI activa una herramienta batch
- **WHEN** una persona ejecute un entrypoint del runner
- **THEN** la lógica principal SHALL vivir en un caso de uso reusable y no dentro del script de arranque

### Requirement: Validación automatizada de la capa runner
La primera implementación SHALL incluir tests automatizados para cliente, casos de uso y manejo de errores dentro del alcance batch.

#### Scenario: El equipo modifica la capa runner
- **WHEN** una persona ejecute la validación automatizada del proyecto
- **THEN** SHALL poder verificar el contrato interno de la capability sin depender exclusivamente del sistema operativo real o del backend real
