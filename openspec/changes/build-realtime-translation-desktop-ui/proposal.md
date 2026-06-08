# Proposal

Implementar una primera interfaz de escritorio Electron + Vue.js para la capability `realtime-translation-desktop-ui`.

Esta fase se centra en validar la direccion visual avanzada para la traduccion en tiempo real sin eliminar ni reemplazar la ventana actual de `system-audio-transcription`. La UI vive en `desktop/`, usa datos mock para poder iterar rapido sobre layout y estados, y prepara el contrato de comandos/eventos para conectarse despues al controlador Python.

## Scope

- Crear una app Electron + Vue separada de la capa Python actual.
- Reproducir la interfaz objetivo enviada por el usuario: topbar, sidebar, panel de transcript/traduccion agrupado y controles inferiores.
- Definir tipos TypeScript para el contrato `UiEvent` y `UiCommand`.
- Exponer un bridge Electron seguro desde preload hacia el proceso principal.
- Validar render frontend, comandos basicos y build.

## Out Of Scope

- Reemplazar la ventana `tkinter` actual.
- Capturar audio desde Electron.
- Hablar directamente con OpenAI, LiteLLM, Ollama u otros proveedores desde la UI.
- Conectar todavia el bridge Electron al controlador Python real.
