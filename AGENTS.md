# AGENTS

## Purpose

Este repositorio define y desarrolla una suite de herramientas de IA local integradas con el sistema operativo, con foco inicial en Linux y una arquitectura preparada para portarse a otros sistemas.

## Product Direction

- El motor de inferencia servirÃ¡ peticiones mediante una API local al sistema y podrÃ¡ apoyarse en runtimes locales o remotos.
- La primera aproximaciÃ³n contempla Gemma 4 corriendo con Ollama y soporte opcional a LiteLLM Proxy como proveedor OpenAI-compatible remoto.
- El despliegue de la API debe poder encapsularse en Docker.
- Las herramientas de usuario vivirÃ¡n como scripts o servicios Python que consumen la API local.
- El stack Python del repo debe gestionarse con Poetry y un entorno `.venv` dentro del propio proyecto.
- El stack Node/Electron del frontend debe instalar dependencias en `desktop/node_modules/` desde `desktop/`, usando la `.npmrc` local del paquete.
- La interacciÃ³n principal del usuario serÃ¡ mediante atajos globales de teclado, overlays y automatizaciones del portapapeles o del texto seleccionado.

## Working Agreement

1. Antes de implementar, crea o selecciona un change en `openspec/changes/`.
2. Define el alcance en `proposal.md`.
3. Describe la soluciÃ³n en `design.md`.
4. Captura requisitos nuevos o cambios de comportamiento en delta specs dentro del change.
5. DescompÃ³n el trabajo en `tasks.md`.
6. Implementa solo cuando el change estÃ© listo.
7. Registra validaciÃ³n y evidencia dentro del mismo change antes de archivarlo.

## Repository Layout

- `.codex/skills/`: skills locales disponibles para Codex en este repo.
- `pyproject.toml`: configuraciÃ³n base del proyecto Python gestionado con Poetry.
- `poetry.toml`: fuerza el entorno virtual `.venv` dentro del repo.
- `Makefile`: comandos operativos de bootstrap para Linux.
- `scripts/`: utilidades de integraciÃ³n y bootstrap del sistema operativo.
- `docs/`: documentaciÃ³n operativa, instalaciÃ³n y troubleshooting.
- `openspec/config.yaml`: configuraciÃ³n base del workflow spec-driven.
- `openspec/capabilities-index.md`: Ã­ndice priorizado de capabilities y metadatos.
- `openspec/changes/`: cambios activos y archivados.
- `openspec/specs/`: fuente de verdad de capacidades consolidadas.

## Current Capability Map

Los nombres de capability deben describir la funciÃ³n y mantenerse estables en el tiempo. La prioridad y los metadatos operativos viven en `openspec/capabilities-index.md`.

- `local-inference-api`: servicio de inferencia multimodal detrÃ¡s de una API, con proveedor intercambiable local o remoto.
- `python-tool-runners`: runners Python que orquestan herramientas, contexto del sistema e inferencia.
- `keyboard-shortcuts`: capa de integraciÃ³n con atajos globales del sistema.
- `tools-overlay`: overlay lanzador con botones de herramientas y entrada conversacional.
- `overlay-launcher-desktop-ui`: implementaciÃ³n Electron/Vue del overlay principal, settings y launcher de herramientas.
- `overlay-settings`: configuraciÃ³n de atajos de teclado y preferencias desde la UI del overlay.
- `selected-text-correction`: correcciÃ³n de texto seleccionado en cualquier aplicaciÃ³n.
- `screenshot-text-extraction`: captura parcial de pantalla y extracciÃ³n exacta de texto al portapapeles.
- `push-to-talk-dictation`: grabaciÃ³n mientras se mantiene un atajo, transcripciÃ³n local e inserciÃ³n automÃ¡tica de texto.
- `overlay-agent-chat`: barra de texto conversacional en el overlay con acceso a herramientas del sistema.
- `system-audio-transcription`: captura de audio del sistema, transcripciÃ³n o traducciÃ³n en vivo y visualizaciÃ³n en una ventana propia.
- `voice-translation-virtual-microphone`: micrÃ³fono virtual compatible con apps de videollamada que hace passthrough o traducciÃ³n de voz en streaming.

## Current Operational Status

- Windows tiene workflows utiles validados para correccion de texto seleccionado, overlay principal y dictado push-to-talk.
- Atajos Windows actuales: `Ctrl + Alt + A` abre o alterna el overlay principal, `Ctrl + Alt + C` corrige texto seleccionado, `Ctrl + Shift + Space` activa dictado push-to-talk mientras se mantiene pulsado.
- `Ctrl + Shift + Space` se usa para el dictado de `so_intelligence_tools` para evitar colisiones con el buscador o metodo de entrada del sistema operativo asociado a `Ctrl + Space`.
- El dictado usa `faster_whisper_http` contra un servidor Docker warm en `http://127.0.0.1:9000`; no debe tratarse ningun runtime ASR anterior como fallback activo.
- El TTS local retenido usa `docker/chatterbox-tts` en `http://127.0.0.1:9011`; Piper/Kokoro/Qwen/NeuTTS y runners de benchmark TTS no deben tratarse como backends activos.
- Windows tiene TTS experimental validado con Chatterbox es-ES en Docker Desktop, voz `female` por defecto basada en `cv_female_es_ref_01 / warm`, voz `male` disponible, endpoints `/health`, `/metrics` y `/v1/audio/speech`.
- La integracion TTS de Codex Desktop en Windows usa un monitor de sesiones en `%USERPROFILE%\.codex\sessions`; lee inicio/fin de tarea, progreso ligero de tools y mensajes visibles/finales. En `task_complete` debe decir `Fin de tarea.` y despues leer el mensaje final si existe.
- La cola TTS de Codex Desktop sintetiza el siguiente segmento mientras reproduce el WAV actual, descarta progreso blando repetido como `Ejecutando comando.` cuando llega un mensaje visible, y limpia audio viejo al empezar o terminar tarea.
- Whisper y Chatterbox caben juntos en la RTX 3070 de 8 GiB si el modelo `qwen3-embedding:0.6b` de Memanto esta descargado de VRAM; no se recomienda mantener residentes Whisper, Chatterbox y Qwen embeddings a la vez.
- En Linux, `install-linux-desktop-integration` y `install-push-to-talk-dictation-service` deben preparar `docker/whisper-server` con `docker compose up -d` antes de habilitar el listener de dictado.
- El overlay Electron/Vue guarda settings en `desktop-settings.json`; esos settings visuales no implican por si solos que todos los atajos esten registrados a nivel del sistema operativo.
- Para consultar el mapa efectivo de atajos, usa `poetry run so-intelligence-tools show-shortcuts` con `--platform linux`, `--platform windows` o `--platform desktop`.
- Las notas operativas detalladas viven en `docs/windows-support.md`, `docs/chatterbox-tts-voice-output.md`, `docs/keyboard-shortcuts.md`, `docs/push-to-talk-dictation.md`, `docs/whisper-docker.md` y `docs/desktop-ui.md`.

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

- Si el repo todavÃ­a no tiene cÃ³digo de producto, se puede empezar creando una capability desde el primer change.
- No guardes evidencia de validaciÃ³n solo en conversaciÃ³n; dÃ©jala dentro del change.
- Linux es el target inicial, pero las decisiones de diseÃ±o deben intentar aislar dependencias especÃ­ficas del sistema operativo.
- No instales dependencias Python a nivel global para este proyecto. Usa siempre Poetry dentro del `.venv` local del repo.
- No instales dependencias Node/Electron a nivel global para este proyecto. Ejecuta `npm install` dentro de `desktop/` y conserva `node_modules/` como artefacto local ignorado por git.
- Para dependencias del sistema operativo, usa los scripts del repo o los targets de `make` antes de crear instrucciones manuales nuevas.
