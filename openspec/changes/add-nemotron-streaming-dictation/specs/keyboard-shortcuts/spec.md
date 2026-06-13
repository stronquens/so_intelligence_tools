## ADDED Requirements

### Requirement: Atajo global para dictado streaming
El sistema SHALL registrar `Ctrl + Alt + Space` como atajo global inicial para iniciar y detener el dictado streaming sin interferir con el resto de herramientas.

#### Scenario: Dictado mientras se mantiene el atajo
- **WHEN** el usuario mantenga pulsado el atajo de dictado streaming
- **THEN** el sistema SHALL iniciar captura de micrófono y transcripción streaming
- **AND** SHALL detener y finalizar la sesión cuando el usuario libere el atajo

#### Scenario: Liberación del atajo
- **WHEN** el usuario libere `Ctrl + Alt + Space`
- **THEN** el sistema SHALL emitir una señal de fin de dictado a la herramienta
- **AND** la herramienta SHALL detener captura, transcripción e inserción incremental salvo el cierre final pendiente

#### Scenario: Diagnóstico del atajo
- **WHEN** el atajo sea invocado por GNOME o por el backend de teclado configurado
- **THEN** el sistema SHALL registrar evidencia temprana de inicio y fin de pulsación para diagnosticar fallos de captura

#### Scenario: Atajo por defecto
- **WHEN** se instale la integración de escritorio inicial
- **THEN** el dictado streaming SHALL quedar asociado por defecto a `Ctrl + Alt + Space`

#### Scenario: Persistencia tras reinicio
- **WHEN** el usuario reinicie el equipo e inicie sesión de nuevo
- **THEN** el atajo `Ctrl + Alt + Space` SHALL seguir disponible o reaplicarse automáticamente por la integración de escritorio
