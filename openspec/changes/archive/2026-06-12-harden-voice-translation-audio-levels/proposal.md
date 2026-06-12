## Why

La prueba real mostró que un `VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME` demasiado alto deja pasar mucha voz original en castellano y se suma a la voz inglesa traducida. Esa mezcla puede saturar, sonar acoplada y devolver a los demás participantes de la llamada con retardo si el micrófono físico captura audio de salida.

## What Changes

- Bajar los valores por defecto de traducción de voz a una mezcla más segura: passthrough normal `1.0`, passthrough durante traducción `0.03`, salida traducida `0.75`.
- Actualizar la `.env` local y `.env.example` para usar esos valores seguros.
- Añadir un techo de seguridad al passthrough ducked para impedir configuraciones accidentales como `0.60` durante traducción.
- Añadir limitador PCM simple antes de escribir la salida traducida al micrófono virtual.
- Rechazar fuentes físicas peligrosas (`.monitor` o el propio dispositivo virtual) para reducir retornos de llamada.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `voice-translation-virtual-microphone`: endurece niveles de mezcla, evita clipping básico y protege contra fuentes de captura que pueden reinyectar audio de la llamada.

## Impact

- Configuración de `ToolRunnerSettings`.
- Pipeline de micrófono virtual y controlador realtime.
- Helpers de audio PCM y validación de fuentes PulseAudio.
- Tests unitarios y documentación operativa.
