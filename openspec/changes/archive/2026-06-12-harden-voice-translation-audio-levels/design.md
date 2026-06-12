## Context

El pipeline actual mezcla passthrough físico y salida traducida como streams separados hacia el sink interno del micrófono virtual. Si el passthrough ducked queda alto, la voz original en castellano sigue presente bajo la voz inglesa. Si además se sube la salida traducida o el micro físico recoge altavoces, los participantes escuchan doble voz, eco y saturación.

## Goals / Non-Goals

**Goals:**

- Hacer que la configuración por defecto sea apta para llamadas reales.
- Evitar que un valor de ducking accidentalmente alto arruine la mezcla durante traducción.
- Aplicar un limitador simple a la salida PCM traducida para evitar clipping por ganancia.
- Fallar pronto si la fuente física configurada parece ser un monitor o el propio micro virtual.

**Non-Goals:**

- Implementar un mezclador DSP central con limitador final de suma.
- Resolver acústicamente el uso de altavoces abiertos; se seguirá recomendando usar auriculares.
- Cambiar el proveedor realtime o la latencia de red/modelo.

## Decisions

- Mantener `VOICE_TRANSLATION_PASSTHROUGH_VOLUME=1.0` para que el micro virtual sea útil en passthrough.
- Usar `VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03` para que la voz original quede casi inaudible durante traducción, pero aún pueda dar algo de presencia si el usuario lo desea.
- Usar `VOICE_TRANSLATION_OUTPUT_VOLUME=0.75` para dejar headroom a la salida inglesa.
- Introducir `VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME=0.12` como techo de seguridad. Si el entorno configura más, el pipeline usa el techo y lo registra.
- Añadir `limit_pcm_s16le` para limitar muestras PCM por debajo de full scale antes de escribir audio traducido. Esto no sustituye un limitador final de mezcla, pero reduce clipping por salida traducida demasiado alta.
- Validar fuentes físicas en `LinuxMicrophoneAudioCapture.start`, rechazando nombres que terminen en `.monitor` o coincidan con prefijos virtuales del proyecto.

## Risks / Trade-offs

- El inglés puede sonar más bajo en algunas llamadas -> subir `VOICE_TRANSLATION_OUTPUT_VOLUME` hasta `0.85` o `1.0`, manteniendo el ducking bajo.
- El limitador por stream no ve la suma final de passthrough + traducción -> el nuevo ducking bajo reduce el riesgo de suma.
- El cap de ducking limita configuraciones avanzadas -> queda configurable por entorno con `VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME`.
