# so_intelligence_tools

Base de trabajo para una suite de herramientas de IA local integradas con el sistema operativo.

## Incluye

- Estructura `openspec/` para cambios, specs y archivo histórico.
- Índice de capabilities priorizadas con metadatos en `openspec/capabilities-index.md`.
- Skills locales de OpenSpec copiadas desde la referencia `Awai`.
- Skills de sistema de Codex copiadas a `.codex/skills/`.
- Bootstrap de proyecto Python con Poetry y `.venv` local dentro del repo.
- Guía operativa en `AGENTS.md`.
- Specs semilla para las capacidades principales del producto.

## Visión

El proyecto busca ofrecer herramientas de IA que se sientan nativas dentro del flujo diario del sistema operativo. La arquitectura parte de un modelo multimodal local servido por API, sobre el que se apoyan herramientas Python activadas por atajos de teclado, overlays y automatizaciones sobre selección de texto, capturas y portapapeles.

## Entorno Python

El proyecto debe usar Python gestionado con Poetry. El entorno virtual debe vivir dentro del propio repositorio en `.venv/`, de modo que cualquier dependencia o herramienta instalada para el proyecto quede aislada del sistema.

## Backend local-inference-api

La primera implementación del backend se ejecuta como un servicio FastAPI y usa Ollama como runtime local. El modelo inicial validado para portátiles sin GPU dedicada es `hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL`.

Arranque local esperado:

```bash
poetry install
poetry run uvicorn --app-dir src local_inference_api.main:app --reload
```

Validación automática:

```bash
poetry run pytest
```

## Docker

La primera versión del stack Docker usa dos servicios:

- `ollama`: runtime local del modelo
- `api`: backend FastAPI que consume Ollama

El runtime `ollama` no publica puerto al host por defecto. La comunicación ocurre dentro de la red interna de Docker y así evitamos conflictos con una instalación local de Ollama ya corriendo en `127.0.0.1:11434`.
La imagen queda fijada a `ollama/ollama:0.30.5` porque Gemma 4 no funcionó correctamente con un runtime más antiguo.

Arranque del stack:

```bash
docker compose up -d --build
```

Preparación del modelo dentro del runtime contenedorizado:

```bash
docker compose exec ollama ollama pull hf.co/unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL
```

Comprobación rápida:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/status
```

Parada del stack:

```bash
docker compose down
```

Si se quiere liberar también el volumen de modelos descargados:

```bash
docker compose down -v
```

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
pyproject.toml
poetry.toml
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
