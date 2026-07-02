# Capabilities Index

Este índice ordena las capabilities por prioridad de ejecución recomendada y añade metadatos operativos que no conviene meter dentro del nombre de la spec.

| Priority | Capability | Realtime | Modality | Model | Summary |
| --- | --- | --- | --- | --- | --- |
| 1 | `local-inference-api` | No | `multimodal` | `local/remote` | Servicio de inferencia expuesto por API para el resto del sistema, con soporte para Ollama local o proveedores remotos OpenAI-compatible como LiteLLM Proxy. |
| 2 | `python-tool-runners` | No | `system` | `none` | Capa Python que conecta eventos del sistema, contexto de usuario y llamadas a herramientas o modelos. |
| 3 | `keyboard-shortcuts` | No | `system` | `none` | Registro y gestión de atajos globales para disparar herramientas desde cualquier aplicación, con soporte Linux y listener inicial Windows para corrección de texto. |
| 4 | `tools-overlay` | No | `multimodal` | `none` | Overlay principal del sistema con accesos rápidos a herramientas y entrada unificada. |
| 5 | `overlay-settings` | No | `system` | `none` | Ajustes del overlay para atajos, preferencias y configuración futura. |
| 6 | `selected-text-correction` | No | `text` | `local/remote` | Corrección de texto seleccionado preservando idioma y reemplazando el contenido original, con adapters Linux y Windows para flujos de texto. |
| 7 | `screenshot-text-extraction` | No | `image` | `local` | Captura de una región de pantalla y extracción exacta de texto al portapapeles. |
| 8 | `push-to-talk-dictation` | Si | `audio` | `local/on-prem` | Dictado temporal mientras se mantiene un atajo y escritura directa donde está el cursor, validado en Windows con faster-whisper HTTP. |
| 9 | `local-tts-api` | No | `audio` | `local` | Servicio HTTP local para texto a voz con backend Chatterbox es-ES, health, metricas y seleccion parametrica de voz. |
| 10 | `local-tts-voice-output` | No | `audio/system` | `local` | Servicio Chatterbox Docker y puente de voz para leer eventos visibles de Codex, con endpoint comun para OpenClaw. |
| 11 | `overlay-agent-chat` | No | `text` | `local` | Agente conversacional dentro del overlay con acceso a herramientas y búsqueda en archivos. |
| 12 | `system-audio-transcription` | Si | `audio` | `local/remote` | Traducción en vivo del audio de salida del sistema en una ventana dedicada, con primera iteración validada sobre proveedor remoto y apertura futura a rutas locales. |
| 13 | `overlay-launcher-desktop-ui` | No | `system-ui` | `none` | Implementación Electron/Vue del overlay principal con superficie translúcida, catálogo de herramientas y ventanas independientes para ajustes y traductor. |
| 14 | `realtime-translation-desktop-ui` | Si | `audio/system-ui` | `none` | Interfaz Electron/Vue futura para visualizar y controlar la traducción en vivo del audio del sistema sin reemplazar todavía la capa funcional Python. |
| 15 | `voice-translation-virtual-microphone` | Si | `audio` | `remote` | Micrófono virtual para traducir la voz del usuario en tiempo real con streaming remoto. |
