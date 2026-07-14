## Context

La implementación actual crea un `module-null-sink` con nombre `so_ai_translated_mic` y escribe audio con `pacat` en ese sink. PulseAudio expone automáticamente `so_ai_translated_mic.monitor`, pero ese monitor es un artefacto de salida. Algunas aplicaciones lo ocultan, lo presentan como altavoz o no lo aceptan como micrófono normal.

## Goals / Non-Goals

**Goals:**

- Exponer un dispositivo de entrada seleccionable por Slack/Zoom/Meet con nombre estable `so_ai_translated_mic`.
- Seguir escribiendo la mezcla final en un sink interno, para no reestructurar passthrough ni salida traducida.
- Descargar todos los módulos PulseAudio creados al cerrar la sesión.
- Mantener compatibilidad con los tests existentes de mezcla y debug recording.

**Non-Goals:**

- Cambiar el proveedor realtime o la lógica de traducción.
- Añadir una UI de selección de dispositivos.
- Implementar una ruta nativa distinta para PipeWire fuera de la compatibilidad PulseAudio.

## Decisions

- Crear dos módulos: `module-null-sink` para la mezcla interna y `module-remap-source` para publicar una fuente de entrada virtual basada en el monitor del sink interno.
- Usar `VOICE_TRANSLATION_VIRTUAL_SINK_NAME` como nombre de la fuente seleccionable por el usuario, y derivar el sink interno como `<name>_sink`.
- Mantener una propiedad `monitor_source_name` como compatibilidad interna para debug recording, pero introducir `virtual_source_name` como nombre que se muestra al usuario.
- Actualizar passthrough y reproducción traducida para escribir en el sink interno, no en la fuente de entrada.

## Risks / Trade-offs

- Algunas instalaciones antiguas de PulseAudio podrían no tener `module-remap-source` disponible -> fallar con un error claro y descargar el sink si la segunda carga falla.
- El sink interno puede seguir apareciendo como salida del sistema -> nombrarlo como interno para reducir confusión, y documentar que el usuario debe elegir la fuente de entrada `so_ai_translated_mic`.
- Cambiar el nombre interno del sink puede afectar configuraciones avanzadas que esperaban escribir directamente en `VOICE_TRANSLATION_VIRTUAL_SINK_NAME` -> la variable conserva el nombre público del micrófono, que es el comportamiento correcto para el usuario final.
