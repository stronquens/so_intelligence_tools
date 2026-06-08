# AGENTS

## Purpose

Este repositorio define y desarrolla una suite de herramientas de IA local integradas con el sistema operativo, con foco inicial en Linux y una arquitectura preparada para portarse a otros sistemas.

## Product Direction

- El motor de inferencia será local, multimodal y servirá peticiones mediante una API.
- La primera aproximación contempla Gemma 4 corriendo con Ollama.
- El despliegue de la API debe poder encapsularse en Docker.
- Las herramientas de usuario vivirán como scripts o servicios Python que consumen la API local.
- El stack Python del repo debe gestionarse con Poetry y un entorno `.venv` dentro del propio proyecto.
- La interacción principal del usuario será mediante atajos globales de teclado, overlays y automatizaciones del portapapeles o del texto seleccionado.

## Working Agreement

1. Antes de implementar, crea o selecciona un change en `openspec/changes/`.
2. Define el alcance en `proposal.md`.
3. Describe la solución en `design.md`.
4. Captura requisitos nuevos o cambios de comportamiento en delta specs dentro del change.
5. Descompón el trabajo en `tasks.md`.
6. Implementa solo cuando el change esté listo.
7. Registra validación y evidencia dentro del mismo change antes de archivarlo.

## Repository Layout

- `.codex/skills/`: skills locales disponibles para Codex en este repo.
- `pyproject.toml`: configuración base del proyecto Python gestionado con Poetry.
- `poetry.toml`: fuerza el entorno virtual `.venv` dentro del repo.
- `Makefile`: comandos operativos de bootstrap para Linux.
- `scripts/`: utilidades de integración y bootstrap del sistema operativo.
- `docs/`: documentación operativa, instalación y troubleshooting.
- `openspec/config.yaml`: configuración base del workflow spec-driven.
- `openspec/capabilities-index.md`: índice priorizado de capabilities y metadatos.
- `openspec/changes/`: cambios activos y archivados.
- `openspec/specs/`: fuente de verdad de capacidades consolidadas.

## Current Capability Map

Los nombres de capability deben describir la función y mantenerse estables en el tiempo. La prioridad y los metadatos operativos viven en `openspec/capabilities-index.md`.

- `local-inference-api`: servicio local de inferencia multimodal detrás de una API.
- `python-tool-runners`: runners Python que orquestan herramientas, contexto del sistema e inferencia.
- `keyboard-shortcuts`: capa de integración con atajos globales del sistema.
- `tools-overlay`: overlay lanzador con botones de herramientas y entrada conversacional.
- `overlay-settings`: configuración de atajos de teclado y preferencias desde la UI del overlay.
- `selected-text-correction`: corrección de texto seleccionado en cualquier aplicación.
- `screenshot-text-extraction`: captura parcial de pantalla y extracción exacta de texto al portapapeles.
- `push-to-talk-dictation`: grabación mientras se mantiene un atajo, transcripción local e inserción automática de texto.
- `overlay-agent-chat`: barra de texto conversacional en el overlay con acceso a herramientas del sistema.
- `system-audio-transcription`: captura de audio del sistema, transcripción o traducción en vivo y visualización en una ventana propia.
- `voice-translation-virtual-microphone`: micrófono virtual compatible con apps de videollamada que hace passthrough o traducción de voz en streaming.

## Recommended Skills

- `openspec-propose`: crear un change completo.
- `openspec-explore`: pensar requisitos y enfoque sin implementar.
- `openspec-apply-change`: ejecutar tareas del change.
- `openspec-validate-change`: validar y guardar evidencia.
- `openspec-sync-specs`: sincronizar delta specs a specs vivas.
- `openspec-archive-change`: archivar un change terminado.

## Change Lifecycle

1. Explorar o definir la necesidad.
2. Crear `openspec/changes/<change-name>/`.
3. Redactar artifacts hasta quedar listos para implementar.
4. Implementar y marcar tareas completadas.
5. Validar con evidencia.
6. Sincronizar specs si corresponde.
7. Archivar en `openspec/changes/archive/`.

## Notes

- Si el repo todavía no tiene código de producto, se puede empezar creando una capability desde el primer change.
- No guardes evidencia de validación solo en conversación; déjala dentro del change.
- Linux es el target inicial, pero las decisiones de diseño deben intentar aislar dependencias específicas del sistema operativo.
- No instales dependencias Python a nivel global para este proyecto. Usa siempre Poetry dentro del `.venv` local del repo.
- Para dependencias del sistema operativo, usa los scripts del repo o los targets de `make` antes de crear instrucciones manuales nuevas.
