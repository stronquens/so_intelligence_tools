## ADDED Requirements

### Requirement: Niveles seguros de mezcla de voz traducida
El sistema SHALL usar valores por defecto conservadores para que la voz original en passthrough no compita con la voz traducida durante una llamada.

#### Scenario: Traducción activa con valores por defecto
- **WHEN** el usuario active la traducción de voz sin ajustar volúmenes avanzados
- **THEN** el passthrough original SHALL quedar muy reducido
- **AND** la salida traducida SHALL mantener headroom para reducir clipping

#### Scenario: Ducking configurado accidentalmente alto
- **WHEN** el entorno configure un volumen ducked superior al techo de seguridad
- **THEN** el pipeline SHALL usar el techo de seguridad durante traducción
- **AND** SHALL registrar el valor solicitado y el valor aplicado

### Requirement: Protección básica contra clipping de salida
El sistema SHALL limitar la salida PCM traducida antes de escribirla al micrófono virtual para evitar muestras fuera de rango o saturación por ganancia.

#### Scenario: Audio traducido con ganancia alta
- **WHEN** el proveedor realtime entregue PCM y el volumen de salida lo amplifique
- **THEN** el sistema SHALL limitar las muestras a un techo seguro antes de escribirlas

### Requirement: Rechazo de fuentes de captura peligrosas
El sistema SHALL rechazar fuentes físicas que sean monitores de salida o dispositivos virtuales propios del proyecto.

#### Scenario: Fuente configurada como monitor de salida
- **WHEN** `VOICE_TRANSLATION_PHYSICAL_SOURCE` termine en `.monitor`
- **THEN** la herramienta SHALL fallar con un mensaje claro antes de iniciar captura

#### Scenario: Fuente configurada como micro virtual propio
- **WHEN** `VOICE_TRANSLATION_PHYSICAL_SOURCE` apunte a `so_ai_translated_mic` o su sink interno
- **THEN** la herramienta SHALL fallar con un mensaje claro para evitar realimentación
