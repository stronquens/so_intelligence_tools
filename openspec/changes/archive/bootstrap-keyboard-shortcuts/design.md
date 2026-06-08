## Context

Esta iteración conecta por primera vez una capability de activación (`keyboard-shortcuts`) con una capability visible para usuario (`selected-text-correction`).

El objetivo no es diseñar aún un sistema universal de hotkeys para todos los escritorios Linux, sino validar una ruta operativa útil y mantenible.

## Decisions

Usar un listener Python de atajos globales con `pynput`.
Motivo: permite una primera implementación razonablemente pequeña e integrada con el stack Python actual.
Trade-off: su fiabilidad es claramente mejor en X11 que en Wayland.

Modelar los atajos como un registry de acciones.
Motivo: un atajo debe mapear a una capability o acción concreta, no a lógica ad hoc mezclada dentro del listener.

Resolver la selección y el reemplazo de texto en Linux mediante portapapeles + automatización del foco.
Motivo: es la forma más generalista de interoperar con aplicaciones de terceros sin integraciones específicas por app.

Mantener el primer alcance Linux-first y X11-oriented.
Motivo: es mejor una implementación honesta y usable en un entorno bien definido que una promesa ambigua de compatibilidad total.

## Proposed Architecture

Piezas nuevas:

- `ShortcutActionRegistry`
- `LinuxShortcutListener`
- `run_selected_text_correction()` como acción reusable
- adapters Linux de selección e inserción basados en portapapeles y herramientas del escritorio

Flujo:

1. el listener registra `<ctrl>+<space>` u otro atajo configurable
2. al activarse, consulta el registry
3. el registry ejecuta la acción `selected-text-correction`
4. la acción compone runtime Linux + caso de uso ya existente
5. si falta selección o backend, se muestra notificación

## Linux Integration Recommendation

Para esta iteración:

- shortcut global: `pynput`
- copiar selección: `xdotool key --clearmodifiers ctrl+c`
- pegar reemplazo: `xdotool key --clearmodifiers ctrl+v`
- leer/restaurar portapapeles: `xclip`, `xsel` o `wl-copy`/`wl-paste` según disponibilidad

Límite explícito:

- la ruta de shortcut global queda validada para Linux X11
- Wayland puede requerir un adapter distinto o una estrategia distinta en otra iteración
