## Why

El micrófono virtual de traducción de voz se implementó como un `module-null-sink` y se documentó que el usuario debía seleccionar su monitor source (`so_ai_translated_mic.monitor`) como micrófono. En Slack y otras apps eso se comporta como salida/altavoz o no aparece como entrada utilizable, por lo que las personas de la llamada no reciben la voz traducida.

## What Changes

- Publicar una fuente de entrada PulseAudio/PipeWire real para que las aplicaciones externas la enumeren como micrófono.
- Mantener un sink interno para mezclar passthrough, ducking y audio traducido, pero dejar de usar su monitor como nombre que debe seleccionar el usuario.
- Actualizar mensajes, logs, documentación y tests para indicar que el micrófono seleccionable es `so_ai_translated_mic`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `voice-translation-virtual-microphone`: el dispositivo seleccionable por apps externas debe ser una fuente de entrada virtual explícita, no el monitor source del sink interno.

## Impact

- Código PulseAudio de `voice_translation_virtual_microphone`.
- Mensajes de la ventana de traducción de audio del sistema que indican qué micrófono elegir.
- Documentación Linux/README y tests unitarios de audio/pipeline.
- No cambia el contrato remoto con OpenAI ni el pipeline de captura del micrófono físico.
