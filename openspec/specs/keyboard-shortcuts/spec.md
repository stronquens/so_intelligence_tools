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

#### Scenario: Atajo toggle para una herramienta persistente
- **WHEN** una herramienta persistente necesita abrir, mantener y cerrar una sesión con el mismo atajo
- **THEN** el sistema SHALL permitir que la misma combinación inicie o detenga esa herramienta según su estado actual

#### Scenario: Atajo inicial sin colisión evidente
- **WHEN** se asigne un atajo por defecto a una nueva herramienta persistente
- **THEN** el sistema SHALL preferir una combinación con bajo riesgo de conflicto con accesos comunes del escritorio o de aplicaciones frecuentes

### Requirement: Integración inicial orientada a Linux
El sistema SHALL priorizar una integración operativa en Linux sin cerrar la puerta a adaptadores para otros sistemas operativos.

#### Scenario: Primera implementación de atajos
- **WHEN** se construya la primera capa de integración con el sistema
- **THEN** esta SHALL funcionar en Linux como plataforma inicial soportada

#### Scenario: Entorno Linux recomendado para automatización completa
- **WHEN** la primera integración necesite automatización fiable de copiar y pegar sobre aplicaciones de terceros
- **THEN** el sistema SHALL considerar `X11` como el entorno Linux recomendado para esa primera iteración

#### Scenario: Portabilidad futura
- **WHEN** sea necesario soportar otro sistema operativo
- **THEN** la lógica de negocio de las herramientas SHALL permanecer separada del mecanismo específico de captura de atajos

### Requirement: Feedback cuando una acción no pueda ejecutarse
El sistema SHALL informar al usuario cuando un atajo se active pero no existan las precondiciones necesarias para completar la herramienta.

#### Scenario: Falta una precondición
- **WHEN** el usuario dispara una herramienta sin contexto suficiente, como texto seleccionado o una captura válida
- **THEN** el sistema SHALL mostrar una notificación o feedback equivalente indicando que la acción no pudo completarse

#### Scenario: El entorno no permite la automatización completa
- **WHEN** el usuario dispara una herramienta en un entorno Linux donde la automatización de teclado o pegado no sea completamente fiable
- **THEN** el sistema SHALL degradar con feedback claro y conservar el resultado por un canal alternativo cuando sea posible

### Requirement: Atajos persistentes y diagnosticables en GNOME
El sistema SHALL registrar los atajos GNOME de forma persistente y ofrecer diagnóstico suficiente para distinguir fallos de captura del atajo, fallos de configuración y fallos de la herramienta.

#### Scenario: Inicio de sesión en GNOME
- **WHEN** el usuario inicia sesión en el escritorio
- **THEN** el sistema SHALL poder revalidar o reaplicar los atajos configurados
- **AND** SHALL poder refrescar el servicio de GNOME responsable de ejecutar atajos personalizados cuando sea necesario

#### Scenario: Un atajo no parece hacer nada
- **WHEN** el usuario pulsa un atajo registrado y no observa efecto visible
- **THEN** el sistema SHALL escribir evidencia temprana en logs de wrapper cuando GNOME haya invocado el comando
- **AND** SHALL permitir distinguir si el fallo ocurrió antes de entrar en Python, al cargar configuración o durante la herramienta
