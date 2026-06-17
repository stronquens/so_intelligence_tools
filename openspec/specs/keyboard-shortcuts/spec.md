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

#### Scenario: Windows text automation without shortcut registration
- **WHEN** a Windows runtime is introduced for text-focused tools
- **THEN** it SHALL NOT imply that Windows global shortcut registration is complete
- **AND** Windows shortcut installation SHALL remain a separate capability until explicitly designed.

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

### Requirement: Windows selected text correction shortcut listener
The system SHALL provide an initial Windows global shortcut listener for selected text correction.

#### Scenario: The listener runs on Windows
- **WHEN** the shortcut listener is started on Windows
- **THEN** it SHALL register a Windows-compatible global shortcut for selected text correction
- **AND** it SHALL execute the selected-text correction action through the platform-aware runtime.

#### Scenario: The user presses the Windows correction shortcut
- **WHEN** the listener is running
- **AND** the user presses the configured selected-text correction shortcut
- **THEN** the system SHALL run only the selected text correction action.
- **AND** repeated hotkey events inside the configured cooldown window SHALL be ignored.

#### Scenario: The user presses the Windows correction shortcut without selected text
- **WHEN** the listener is running
- **AND** focus is in a text input that supports normal Windows text shortcuts
- **AND** no text is selected
- **AND** the user presses the configured selected-text correction shortcut
- **THEN** the system SHALL attempt `Ctrl+A` followed by copy before reporting missing selected text.

### Requirement: Windows shortcut listener startup entry
The system SHALL provide a user-level Windows startup entry for the selected text correction shortcut listener.

#### Scenario: The user installs Windows shortcut startup
- **WHEN** the user runs the Windows shortcut startup installer
- **THEN** the system SHALL create a Startup folder launcher that launches the shortcut listener from the project virtual environment
- **AND** the launcher SHALL run without leaving a visible terminal window open
- **AND** the launcher SHALL write process output to a diagnostic log file
- **AND** the installer SHALL NOT require administrator privileges.

#### Scenario: The user starts a new Windows session
- **WHEN** the Startup entry exists
- **THEN** Windows SHALL be able to start the shortcut listener after user login.

### Requirement: Windows press-and-hold dictation shortcut
The system SHALL provide a Windows global press-and-hold shortcut for local dictation.

#### Scenario: Dictation shortcut press
- **WHEN** the Windows dictation listener is running
- **AND** the user presses the configured dictation shortcut
- **THEN** the system SHALL start only the dictation action
- **AND** it SHALL ignore repeated press events while dictation is already active.

#### Scenario: Dictation shortcut release
- **WHEN** dictation is active from the Windows dictation shortcut
- **AND** the user releases the shortcut
- **THEN** the system SHALL stop only the active dictation action.

#### Scenario: Dictation shortcut avoids native Windows dictation
- **WHEN** Windows dictation shortcuts are configured by default
- **THEN** the system SHALL use `Ctrl+Space` for project dictation
- **AND** this SHALL be allowed because the conflicting Codex integrated dictation shortcut has been disabled on the current Windows machine.

### Requirement: Windows dictation startup entry
The system SHALL provide a user-level Windows Startup entry for the dictation shortcut listener.

#### Scenario: User installs Windows dictation startup
- **WHEN** the user runs the Windows dictation startup installer
- **THEN** the system SHALL create a hidden Startup launcher for the dictation listener
- **AND** the installer SHALL NOT require administrator privileges.

#### Scenario: User starts a new Windows session
- **WHEN** the Startup entry exists
- **THEN** Windows SHALL be able to start the dictation listener after user login.

### Requirement: Shortcut map introspection
The system SHALL provide a way to inspect the effective keyboard shortcuts by platform.

#### Scenario: User lists all shortcuts
- **WHEN** the user runs the shortcut map command without filters
- **THEN** the system SHALL show supported Linux, Windows and desktop-overlay shortcut entries
- **AND** each entry SHALL include the feature, platform, configured shortcut, configuration source and activation mechanism.

#### Scenario: User filters shortcuts by platform
- **WHEN** the user requests a specific platform shortcut map
- **THEN** the system SHALL show only entries for that platform.

#### Scenario: Windows overlay shortcut is listed
- **WHEN** the user requests the Windows shortcut map
- **THEN** the system SHALL include the main overlay launcher shortcut
- **AND** it SHALL identify `Ctrl + Alt + A` as the Windows shortcut that opens or toggles the overlay.

#### Scenario: Shortcut is visual but not globally registered
- **WHEN** a shortcut belongs to desktop overlay settings rather than an OS listener
- **THEN** the system SHALL identify it separately from active OS-level shortcuts.

### Requirement: User-facing shortcut documentation
The repository SHALL keep user-facing shortcut documentation aligned with the implemented operating-system and desktop shortcut behavior.

#### Scenario: Documentation describes active shortcuts
- **WHEN** a shortcut becomes operational or changes ownership between features
- **THEN** README, AGENTS and relevant `docs/` pages SHALL identify the active key combination, platform, feature and configuration source.

