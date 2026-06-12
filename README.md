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

## Vision

El proyecto busca ofrecer herramientas de IA que se sientan nativas dentro del flujo diario del sistema operativo. La arquitectura parte de una API de inferencia local al sistema, sobre la que se apoyan herramientas Python activadas por atajos de teclado, overlays y automatizaciones sobre selección de texto, capturas y portapapeles. Ese backend puede ejecutarse sobre un runtime local como Ollama o actuar como pasarela a un proveedor remoto OpenAI-compatible como LiteLLM Proxy.

## Entorno Python

El proyecto debe usar Python gestionado con Poetry. El entorno virtual debe vivir dentro del propio repositorio en `.venv/`, de modo que cualquier dependencia o herramienta instalada para el proyecto quede aislada del sistema.

## Instalacion en Linux

La forma recomendada de dejar la primera versión integrada en tu escritorio Linux es instalar:

- un servicio `systemd --user` para arrancar `local-inference-api` al iniciar sesión en `127.0.0.1:8010`
- atajos nativos de GNOME para corrección de texto y traducción de audio
- un autostart de sesión que refresca `org.gnome.SettingsDaemon.MediaKeys.target` y reaplica los atajos tras login

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

Eso deja el backend activo tras reiniciar, registra los atajos de GNOME sobre wrappers de diagnóstico del proyecto y crea:

- `~/.config/systemd/user/so-intelligence-tools-api.service`
- `~/.config/autostart/so-intelligence-tools-desktop-health.desktop`

Atajos actuales recomendados:

| Herramienta | Atajo |
| --- | --- |
| Corrección de texto seleccionado | `Ctrl + Alt + C` |
| Traducción del audio del sistema | `Ctrl + Alt + Y` |
| Traducción de tu voz con micrófono virtual | `Ctrl + Alt + U` |

El puerto de escritorio por defecto es `8010` para evitar conflictos con otros proyectos locales que usen `8000`.

Documentacion ampliada:

- [Instalacion Linux](docs/linux-installation.md)
- [Problemas y soluciones Linux](docs/linux-problems-and-solutions.md)

## Backend local-inference-api

La primera implementación del backend se ejecuta como un servicio FastAPI y hoy soporta dos proveedores:

- `ollama`: runtime local, con `gemma4:e2b-it-qat` como modelo recomendado actual para portátiles sin GPU dedicada
- `litellm_proxy`: proveedor remoto OpenAI-compatible vía API key

En peticiones interactivas de baja latencia, el backend fuerza `think: false` cuando `reasoning_mode` es `off` o `low`. Con Gemma 4 QAT en Ollama esto evita respuestas centradas en thinking o salidas finales vacías cuando la herramienta necesita texto utilizable de inmediato.

El proveedor activo se controla desde `.env` con `INFERENCE_PROVIDER`.

Ejemplo para `ollama`:

```env
LOCAL_INFERENCE_API_HOST=127.0.0.1
LOCAL_INFERENCE_API_PORT=8010
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
INFERENCE_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4:e2b-it-qat
OLLAMA_TIMEOUT_SECONDS=180
OLLAMA_KEEP_ALIVE=10m
```

Ejemplo para `litellm_proxy`:

```env
LOCAL_INFERENCE_API_HOST=127.0.0.1
LOCAL_INFERENCE_API_PORT=8010
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
INFERENCE_PROVIDER=litellm_proxy
LITELLM_PROXY_URL=https://litellm-proxy.core.sciling.com
LITELLM_VIRTUAL_KEY=...
LITELLM_MODEL=eu/tensorix/deepseek/deepseek-v4-flash
OLLAMA_TIMEOUT_SECONDS=180
```

Arranque local esperado:

```bash
poetry install
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010 --reload
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

Nota: Docker sigue publicando `8000:8000` por diseño. La instalación de escritorio usa `8010` para convivir mejor con otros backends locales.

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

- `local-inference-api`: API multimodal con proveedor intercambiable entre runtime local y backend remoto OpenAI-compatible.
- `python-tool-runners`: scripts y servicios Python para orquestar flujos.
- `keyboard-shortcuts`: integración global mediante combinaciones de teclado.
- `tools-overlay`: overlay del sistema con acciones de escritura asistida.
- `overlay-settings`: ajustes del overlay para reasignar atajos y gestionar preferencias.
- `selected-text-correction`: corrección ortográfica del texto seleccionado preservando el idioma original.
- `screenshot-text-extraction`: extracción exacta de texto desde una región capturada de pantalla.
- `push-to-talk-dictation`: dictado push-to-talk con transcripción local e inserción automática.
- `overlay-agent-chat`: barra conversacional para hablar con un agente con herramientas del sistema.
- `system-audio-transcription`: traducción en vivo del audio que suena en el sistema, con ventana dedicada, modo inicial fijo de traducción al español y espacio para futuros modos seleccionables.
- `realtime-translation-desktop-ui`: interfaz Electron/Vue alternativa para visualizar la traducción en vivo con una experiencia visual avanzada.
- `voice-translation-virtual-microphone`: micrófono virtual para traducir tu voz en tiempo real usando API remota.

## Probar micrófono virtual con passthrough y traducción de tu voz

La primera fase de `voice-translation-virtual-microphone` crea un micrófono virtual Linux usando PulseAudio. Al abrir la app de traducción, ese micrófono virtual queda disponible en modo passthrough y retransmite tu Logitech como un micrófono normal. Al activar la traducción, baja la voz original y superpone la voz traducida al inglés.

```text
Logitech C922 -> passthrough -> so_ai_translated_mic
Logitech C922 -> OpenAI Realtime Translate -> voz inglesa superpuesta -> so_ai_translated_mic
```

Configura `OPENAI_API_KEY` en `.env`. Por defecto se asume que hablas en castellano y quieres que las aplicaciones reciban audio hablado en inglés:

```env
VOICE_TRANSLATION_SOURCE_LANGUAGE=Spanish
VOICE_TRANSLATION_TARGET_LANGUAGE=English
VOICE_TRANSLATION_OPENAI_MODEL=gpt-realtime-translate
VOICE_TRANSLATION_VOICE=marin
VOICE_TRANSLATION_PHYSICAL_SOURCE=alsa_input.usb-046d_C922_Pro_Stream_Webcam_719B22BF-02.analog-stereo
VOICE_TRANSLATION_PASSTHROUGH_VOLUME=1.0
VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03
VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME=0.12
VOICE_TRANSLATION_OUTPUT_VOLUME=0.75
VOICE_TRANSLATION_DEBUG_RECORDING_ENABLED=false
VOICE_TRANSLATION_DEBUG_RECORDINGS_DIR=~/.cache/so_intelligence_tools/voice_translation_debug_audio
GNOME_VOICE_TRANSLATION_BINDING=<Primary><Alt>u
```

Durante la traducción, el volumen ducked se limita por defecto a `0.12` aunque el entorno pida más. Esto evita que la voz original en castellano compita con la voz inglesa y sature la mezcla.

Lanzar manualmente:

```bash
poetry run so-intelligence-tools run-voice-translation-virtual-mic-toggle
```

Tambien se puede activar desde la ventana actual de traduccion del audio del sistema. Abre la app:

```bash
poetry run so-intelligence-tools run-system-audio-translation-toggle
```

La ventana crea el micrófono virtual y lo deja en passthrough. Selecciona `so_ai_translated_mic` como micrófono en Zoom, Meet o Slack, y deja tu altavoz normal como salida para escuchar la llamada. Pulsa `Activar mi voz traducida` para bajar tu voz original y superponer la traducción inglesa. Al pulsarlo de nuevo vuelve el passthrough normal; al cerrar la ventana se limpia el dispositivo virtual.

Para depurar lo que realmente reciben las aplicaciones externas, activa temporalmente:

```env
VOICE_TRANSLATION_DEBUG_RECORDING_ENABLED=true
```

Con ese modo se graba un WAV por sesión desde el monitor del micrófono virtual, incluyendo passthrough, ducking y audio traducido. Los archivos quedan en `~/.cache/so_intelligence_tools/voice_translation_debug_audio/` y el log de sesión incluye eventos `debug_recording_started` y `debug_recording_stopped` con la ruta exacta del WAV.

Cuando esté activo, selecciona como micrófono en Zoom, Meet, Slack o una grabadora de audio la fuente:

```text
so_ai_translated_mic
```

Ejecutar el mismo comando una segunda vez detiene la sesión, cierra la conexión realtime, para la captura del micrófono físico y descarga el módulo virtual de PulseAudio.

Instalar el atajo GNOME:

```bash
poetry run so-intelligence-tools install-gnome-voice-translation-shortcut
```

Atajo por defecto:

```text
Ctrl + Alt + U
```

Notas de esta fase:

- usa `gpt-realtime-translate`, no un pipeline Whisper + traducción + TTS
- mantiene una conexión remota abierta mientras esté activa, así que detén la sesión cuando no la uses para cortar consumo
- el micrófono virtual se implementa como `module-null-sink`; algunas apps pueden necesitar reabrir ajustes de audio para refrescar la lista de micros
- los logs se escriben en `~/.cache/so_intelligence_tools/voice_translation_logs/`
- la UI/tray persistente queda para una iteración posterior

## Probar atajo de corrección en Linux

La integración real de `keyboard-shortcuts` + `selected-text-correction` ya se puede probar en Linux.

En GNOME, el camino soportado es instalar un atajo nativo del sistema:

```bash
poetry install
poetry run so-intelligence-tools install-gnome-selected-text-shortcut --debug
```

Eso registra `Ctrl + Alt + C` como atajo para ejecutar la corrección del texto seleccionado usando un wrapper de diagnóstico del proyecto.

Para probarlo:

1. Arranca el backend local:

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010
```

2. Abre una aplicación cualquiera donde puedas escribir texto.
3. Escribe y selecciona un texto con errores.
4. Pulsa `Ctrl + Alt + C`.

Log de diagnóstico:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/selected_text_correction.log
```

## Probar traducción en vivo del audio del sistema

La primera fase de `system-audio-transcription` ya tiene una implementación Linux-first dentro del proyecto:

- ventana normal del sistema
- captura del audio de salida por monitor source
- selector de modo dentro de la ventana
- panel en vivo con original y traducción lado a lado
- historial agrupado donde cada bloque muestra original y traducción juntos
- modo `OpenAI realtime` para baja latencia
- modo `chunked` de fallback con transcripción remota por bloques
- toggle del mismo comando para abrir o cerrar la herramienta

Configura primero el bloque de variables `SYSTEM_AUDIO_TRANSLATION_*` en `.env`.

Modos disponibles:

- `translate_es_openai_realtime`: usa `OpenAI realtime` y es el camino recomendado para menor latencia
- `translate_es_chunked`: mantiene el pipeline anterior `whisper-1 + traducción de texto`

Con `OPENAI_API_KEY` configurada, el proyecto puede abrir la ventana directamente en `translate_es_openai_realtime`. Desde el desplegable de la propia ventana puedes cambiar de modo sin cerrar la herramienta.

Lanzar manualmente:

```bash
poetry run so-intelligence-tools run-system-audio-translation-toggle
```

Si el comando se ejecuta una segunda vez mientras la ventana está activa, la sesión se cierra.

Instalar el atajo GNOME para esta tool:

```bash
poetry run so-intelligence-tools install-gnome-system-audio-translation-shortcut
```

Atajo por defecto:

```text
Ctrl + Alt + Y
```

Notas de esta fase:

- la salida principal muestra solo la traducción al español
- en modo realtime, la parte superior muestra original y traducción en paralelo, y el historial las agrupa en un mismo bloque para que la correspondencia visual sea más clara
- la ventana tiene un desplegable de modo para alternar entre `OpenAI realtime` y el fallback `chunked`
- el modo realtime usa idioma de entrada `auto` por defecto: si el audio ya está en español, intenta transcribirlo en español en vez de ocultarlo
- el modo realtime mantiene una conexión abierta mientras la sesión está activa; pausa o cierra la ventana para cortar consumo remoto
- el historial se guarda al cerrar en `~/.cache/so_intelligence_tools/system_audio_logs/`
- el wrapper del atajo escribe en `~/.cache/so_intelligence_tools/system_audio_shortcut.log`
- la diarización de speakers todavía no está implementada; queda como mejora posterior
- `OpenAI realtime` necesita `OPENAI_API_KEY` o `SYSTEM_AUDIO_TRANSLATION_OPENAI_REALTIME_API_KEY`
- la integración directa con OpenAI ya quedó validada con `session.created` y `session.updated` usando la API GA de Realtime
- la ruta `chunked` sigue reutilizando LiteLLM Proxy para transcripción y traducción

## Probar la nueva UI Electron/Vue

La capability `realtime-translation-desktop-ui` vive en `desktop/` y es una interfaz visual separada. No reemplaza todavía la ventana actual de traducción en tiempo real ni captura audio por su cuenta.

Instalar dependencias frontend:

```bash
npm --prefix desktop install
```

Arrancar en modo desarrollo web:

```bash
npm --prefix desktop run dev -- --port 5173
```

Abrir como ventana Electron usando el servidor de desarrollo:

```bash
SO_AI_DESKTOP_DEV_SERVER_URL=http://127.0.0.1:5173 npm --prefix desktop run electron:dev
```

Validar la UI:

```bash
npm --prefix desktop run test
npm --prefix desktop run build
```

Estado actual:

- renderiza una interfaz moderna tipo desktop app con topbar, sidebar, timeline EN/ES agrupado y controles inferiores
- usa datos mock para validar la experiencia visual sin tocar el pipeline realtime actual
- expone tipos `UiEvent` y `UiCommand` como contrato futuro con Python
- el bridge Electron actual acepta comandos desde Vue, pero todavía no controla la sesión Python real
- la ventana `tkinter` de `system-audio-transcription` sigue siendo la implementación funcional de producción

Notas:

- En X11, esta primera versión Linux lee la selección desde `PRIMARY` y reemplaza el texto pegando el resultado corregido desde el portapapeles.
- En Ubuntu 22.04 con GNOME, la forma más fiable de probar esta capability es iniciar sesión con `Ubuntu on Xorg` desde la pantalla de login. Este equipo ya tiene esa sesión instalada.
- Si los atajos de GNOME no hacen nada, comprueba que el servicio de atajos de GNOME está activo:

```bash
systemctl --user status org.gnome.SettingsDaemon.MediaKeys.service
```

- Para repararlo sin reiniciar sesión:

```bash
systemctl --user restart org.gnome.SettingsDaemon.MediaKeys.target
```

- El autostart `so-intelligence-tools-desktop-health.desktop` ejecuta esa reparación al iniciar sesión y escribe en:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/desktop_health.log
```

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
