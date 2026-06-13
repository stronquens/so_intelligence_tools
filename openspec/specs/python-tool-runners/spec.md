# Purpose

Definir el comportamiento esperado de los scripts o servicios Python que orquestan las herramientas cliente del sistema.

## Requirements

### Requirement: Herramientas cliente desacopladas del backend concreto
El sistema SHALL implementar herramientas cliente en Python que consuman la API local sin depender directamente del runtime interno del modelo ni del proveedor efectivo de inferencia.

#### Scenario: Una herramienta invoca la API
- **WHEN** una herramienta Python necesita ejecutar una tarea de IA
- **THEN** esta SHALL comunicarse con la API local mediante una interfaz definida y no mediante llamadas acopladas al proceso del modelo o al proveedor remoto

### Requirement: Tooling Python aislado dentro del proyecto
El sistema SHALL gestionar dependencias y comandos Python mediante Poetry usando un entorno `.venv` dentro del propio repositorio.

#### Scenario: Instalación de dependencias del proyecto
- **WHEN** una persona necesite instalar o actualizar dependencias Python del proyecto
- **THEN** SHALL hacerlo mediante Poetry
- **AND** el entorno virtual SHALL crearse dentro de `.venv/` en la raíz del repositorio

### Requirement: Orquestación de acciones de sistema y de inferencia
Las herramientas Python SHALL encargarse de unir el contexto del sistema operativo con la llamada al backend de IA.

#### Scenario: Flujo con selección de texto
- **WHEN** una herramienta necesita leer texto seleccionado, invocar inferencia y reemplazar el resultado
- **THEN** la capa Python SHALL coordinar esas etapas como un flujo único

#### Scenario: Flujo con captura de pantalla
- **WHEN** una herramienta necesita capturar una imagen, enviarla al backend y escribir en el portapapeles
- **THEN** la capa Python SHALL coordinar esos pasos de principio a fin

#### Scenario: Flujo con grabación de audio temporal
- **WHEN** una herramienta necesita empezar a grabar al pulsar un atajo, detener la grabación al soltarlo, transcribir el audio e insertar el texto resultante
- **THEN** la capa Python SHALL coordinar esas etapas como un único flujo transitorio

#### Scenario: Flujo con audio del sistema en vivo
- **WHEN** una herramienta necesita capturar audio de salida del sistema, enviarlo de forma continua al backend y refrescar una interfaz con resultados parciales
- **THEN** la capa Python SHALL coordinar captura, streaming, actualización de UI y parada controlada del flujo

#### Scenario: Flujo con micrófono virtual y traducción en tiempo real
- **WHEN** una herramienta necesita capturar el micrófono físico, enviar audio por streaming a un servicio externo y publicar el audio resultante en un micrófono virtual
- **THEN** la capa Python SHALL coordinar entrada, estado, streaming y salida en tiempo real como un pipeline continuo

### Requirement: Gestión explícita de errores operativos
Las herramientas Python SHALL detectar y comunicar errores operativos frecuentes como fallo de API local, ausencia de contexto o cancelación del usuario.

#### Scenario: El backend local no responde
- **WHEN** una herramienta no puede obtener respuesta de la API local
- **THEN** el flujo SHALL terminar con feedback claro para el usuario en lugar de fallar silenciosamente

### Requirement: Windows adapters for text-focused runner flows
The system SHALL provide an initial Windows adapter layer for text-focused Python tool runners without changing the shared application use cases.

#### Scenario: A text tool runs on Windows
- **WHEN** the selected text correction runner is invoked on Windows
- **THEN** the system SHALL compose Windows adapters for clipboard, keyboard automation, selected text, text insertion and notifications
- **AND** the correction use case SHALL remain independent of the concrete operating system.

#### Scenario: Windows selected text is read through a clipboard roundtrip
- **WHEN** a Windows text adapter needs to read selected text from the focused application
- **THEN** it SHALL preserve the existing clipboard when possible
- **AND** it SHALL send a copy shortcut to request the current selection
- **AND** it SHALL return no selection if the clipboard does not change to useful text.

#### Scenario: Windows corrected text is inserted into the focused application
- **WHEN** a Windows text adapter needs to replace selected text
- **THEN** it SHALL write the replacement text to the clipboard
- **AND** it SHALL send a paste shortcut to the focused application.

### Requirement: Platform-aware runtime composition
The system SHALL centralize operating-system runtime selection instead of hardcoding Linux in text-focused entrypoints.

#### Scenario: The runtime is built automatically
- **WHEN** a text-focused runner builds its desktop runtime without an explicit platform
- **THEN** the system SHALL choose a Windows runtime on Windows
- **AND** it SHALL choose the existing Linux runtime on Linux.

#### Scenario: A platform is unsupported
- **WHEN** runtime composition is requested for an unsupported platform
- **THEN** the system SHALL fail with clear unsupported-environment feedback.
