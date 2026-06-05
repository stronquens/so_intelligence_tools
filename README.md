# so_intelligence_tools

Base de trabajo para una suite de herramientas de IA local integradas con el sistema operativo.

## Incluye

- Estructura `openspec/` para cambios, specs y archivo histórico.
- Índice de capabilities priorizadas con metadatos en `openspec/capabilities-index.md`.
- Skills locales de OpenSpec copiadas desde la referencia `Awai`.
- Skills de sistema de Codex copiadas a `.codex/skills/`.
- Guía operativa en `AGENTS.md`.
- Specs semilla para las capacidades principales del producto.

## Visión

El proyecto busca ofrecer herramientas de IA que se sientan nativas dentro del flujo diario del sistema operativo. La arquitectura parte de un modelo multimodal local servido por API, sobre el que se apoyan herramientas Python activadas por atajos de teclado, overlays y automatizaciones sobre selección de texto, capturas y portapapeles.

## Capacidades iniciales

Los nombres de las capabilities priorizan claridad y estabilidad. La prioridad y el resto de metadatos viven en `openspec/capabilities-index.md`.

- `local-inference-api`: API local multimodal sobre Ollama y Docker.
- `python-tool-runners`: scripts y servicios Python para orquestar flujos.
- `keyboard-shortcuts`: integración global mediante combinaciones de teclado.
- `tools-overlay`: overlay del sistema con acciones de escritura asistida.
- `overlay-settings`: ajustes del overlay para reasignar atajos y gestionar preferencias.
- `selected-text-correction`: corrección ortográfica del texto seleccionado preservando el idioma original.
- `screenshot-text-extraction`: extracción exacta de texto desde una región capturada de pantalla.
- `push-to-talk-dictation`: dictado push-to-talk con transcripción local e inserción automática.
- `overlay-agent-chat`: barra conversacional para hablar con un agente con herramientas del sistema.
- `system-audio-transcription`: transcripción o traducción en vivo del audio que suena en el sistema.
- `voice-translation-virtual-microphone`: micrófono virtual para traducir tu voz en tiempo real usando API remota.

## Estructura

```text
.codex/skills/
openspec/
  config.yaml
  changes/
    archive/
  specs/
AGENTS.md
README.md
```

## Flujo recomendado

1. Crear un change nuevo.
2. Escribir `proposal.md`, `design.md` y `tasks.md`.
3. Añadir delta specs si el cambio altera comportamiento.
4. Implementar.
5. Validar y guardar evidencia.
6. Sincronizar specs y archivar.

## Primer siguiente paso

Crear el primer change sobre una de las capabilities ya definidas en `openspec/specs/`.
