# Specs

En esta carpeta viven las specs consolidadas del proyecto.

Cada capability debería tener su propia carpeta con un nombre estable centrado en la función:

```text
openspec/specs/<capability-name>/spec.md
```

Ejemplos:

- `openspec/specs/local-inference-api/spec.md`
- `openspec/specs/selected-text-correction/spec.md`
- `openspec/specs/voice-translation-virtual-microphone/spec.md`

La prioridad, si es `batch` o `realtime`, la modalidad y si usa modelo `local`, `remote` o `none` se documentan en `openspec/capabilities-index.md`.

Usa los changes en `openspec/changes/` para proponer modificaciones antes de actualizar estas specs base.
