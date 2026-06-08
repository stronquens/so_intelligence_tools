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

## Instalacion en Linux

La forma recomendada de dejar la primera versión integrada en tu escritorio Linux es instalar:

- un servicio `systemd --user` para arrancar `local-inference-api` al iniciar sesión
- el atajo nativo de GNOME para lanzar la corrección de texto seleccionado

### Instalacion rapida

```bash
make install-system-deps
poetry install
poetry run so-intelligence-tools install-linux-desktop-integration
ollama pull gemma4:e2b-it-qat
```

### Bootstrap en un solo target

```bash
make bootstrap-linux
ollama pull gemma4:e2b-it-qat
```

El target de bootstrap instala dependencias de sistema, instala dependencias Python y registra la integracion de escritorio.

Con el entorno ya preparado con `poetry install`, el comando de integración es:

```bash
poetry run so-intelligence-tools install-linux-desktop-integration
```

Eso deja el backend activo tras reiniciar y reaplica el atajo de GNOME sobre el ejecutable del `.venv` del proyecto.

Documentacion ampliada:

- [Instalacion Linux](docs/linux-installation.md)
- [Problemas y soluciones Linux](docs/linux-problems-and-solutions.md)

## Backend local-inference-api

La primera implementación del backend se ejecuta como un servicio FastAPI y usa Ollama como runtime local. El modelo recomendado actualmente para portátiles sin GPU dedicada es `gemma4:e2b-it-qat`, que mejora la relación calidad/tamaño frente al quant anterior.

En peticiones interactivas de baja latencia, el backend fuerza `think: false` cuando `reasoning_mode` es `off` o `low`. Con Gemma 4 QAT en Ollama esto evita respuestas centradas en thinking o salidas finales vacías cuando la herramienta necesita texto utilizable de inmediato.

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
docker compose exec ollama ollama pull gemma4:e2b-it-qat
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

## Probar atajo de corrección en Linux

La primera integración real de `keyboard-shortcuts` + `selected-text-correction` ya se puede probar en Linux.

En GNOME Wayland, el camino soportado es instalar un atajo nativo del sistema:

```bash
poetry install
poetry run so-intelligence-tools install-gnome-selected-text-shortcut
```

Eso registra `Ctrl+Espacio` como atajo para ejecutar la corrección del texto seleccionado usando el ejecutable del `.venv` del proyecto.

Para probarlo:

1. Arranca el backend local:

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8000
```

2. Abre una aplicación cualquiera donde puedas escribir texto.
3. Escribe y selecciona un texto con errores.
4. Pulsa `Ctrl+Espacio`.

Notas:

- En X11, esta primera versión Linux lee la selección desde `PRIMARY` y reemplaza el texto pegando el resultado corregido desde el portapapeles.
- En Ubuntu 22.04 con GNOME, la forma más fiable de probar esta capability es iniciar sesión con `Ubuntu on Xorg` desde la pantalla de login. Este equipo ya tiene esa sesión instalada.
- En GNOME Wayland, para que la corrección de texto seleccionado funcione de verdad, instala estas utilidades del sistema:

```bash
sudo apt-get update
sudo apt-get install -y wl-clipboard ydotool ydotoold
scripts/start-wayland-keyboard-backend.sh
```

- `wl-clipboard` aporta `wl-copy` y `wl-paste` para el portapapeles Wayland.
- `ydotool` y `ydotoold` permiten simular entrada de teclado en GNOME Wayland, donde `xdotool` y `wtype` no son fiables.
- En Ubuntu 22.04, `ydotoold` usa `/tmp/.ydotool_socket`; el script del proyecto lo reinicia y ajusta permisos para el usuario actual.
- El listener Python `listen-shortcuts` sigue siendo útil para X11, pero en Wayland se rechaza explícitamente y debe usarse el atajo nativo de GNOME.

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
