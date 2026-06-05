# Purpose

Definir cómo las herramientas de IA se activan mediante combinaciones de teclado a nivel de sistema operativo.

## Requirements

### Requirement: Atajos globales para lanzar herramientas
El sistema SHALL permitir que herramientas de IA concretas se ejecuten mediante atajos globales de teclado.

#### Scenario: El usuario invoca una herramienta desde cualquier aplicación
- **WHEN** el usuario pulsa una combinación de teclado registrada por el sistema
- **THEN** la herramienta asociada SHALL ejecutarse aunque el foco esté en una aplicación de terceros

#### Scenario: La acción se limita a la herramienta correspondiente
- **WHEN** se activa un atajo global
- **THEN** el sistema SHALL lanzar solo la acción asociada a ese atajo

#### Scenario: Atajo mantenido para una acción temporal
- **WHEN** una herramienta requiere mantener una combinación de teclas pulsada durante una interacción temporal
- **THEN** el sistema SHALL distinguir entre inicio de pulsación y liberación para controlar el ciclo de vida de esa acción

### Requirement: Integración inicial orientada a Linux
El sistema SHALL priorizar una integración operativa en Linux sin cerrar la puerta a adaptadores para otros sistemas operativos.

#### Scenario: Primera implementación de atajos
- **WHEN** se construya la primera capa de integración con el sistema
- **THEN** esta SHALL funcionar en Linux como plataforma inicial soportada

#### Scenario: Portabilidad futura
- **WHEN** sea necesario soportar otro sistema operativo
- **THEN** la lógica de negocio de las herramientas SHALL permanecer separada del mecanismo específico de captura de atajos

### Requirement: Feedback cuando una acción no pueda ejecutarse
El sistema SHALL informar al usuario cuando un atajo se active pero no existan las precondiciones necesarias para completar la herramienta.

#### Scenario: Falta una precondición
- **WHEN** el usuario dispara una herramienta sin contexto suficiente, como texto seleccionado o una captura válida
- **THEN** el sistema SHALL mostrar una notificación o feedback equivalente indicando que la acción no pudo completarse
