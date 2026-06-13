## Context

`push-to-talk-dictation` ya existe como capability, pero su spec actual describe una grabación efímera que se transcribe al finalizar la pulsación. El objetivo nuevo es que el campo enfocado reciba texto dictado en lenguaje natural con poca fricción, apto para escribir prompts e instrucciones sin tocar el teclado.

Según documentación oficial/comunitaria de NVIDIA en Hugging Face, `nvidia/nemotron-3.5-asr-streaming-0.6b` es un ASR streaming multilingüe de 600M parámetros, soporta 40 language-locales incluyendo español, puntuación y capitalización, y requiere NeMo 26.06+ para ejecución local. La ficha inglesa previa de Nemotron ASR describe arquitectura Cache-Aware FastConformer-RNNT y chunks configurables de 80ms, 160ms, 560ms y 1120ms; el modelo 3.5 extiende esa línea a multilingüe.

Fuentes verificadas:

- https://huggingface.co/blog/nvidia/fine-tuning-nemotron-35-asr
- https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b
- https://build.nvidia.com/explore/speech
- https://huggingface.co/onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4

## Goals / Non-Goals

**Goals:**

- Dictado local en español con baja latencia usando Nemotron 3.5 ASR Streaming 0.6B si la spike confirma runtime viable; en esta máquina, la ruta viable es ONNX INT4 en CPU.
- Inserción de segmentos finales/estables en el campo de texto enfocado mientras el usuario mantiene el atajo.
- Manejo de parciales y finales para evitar duplicados, texto corrupto o parpadeo excesivo.
- Overlay discreto de estado: escuchando, transcribiendo, insertando, error.
- Configuración por entorno para modelo, idioma, fuente de micrófono, chunks y atajo `Ctrl+Alt+Space`.
- Spike técnica para decidir entre Ollama y Docker/NVIDIA NIM/NeMo como runtime local operable desde Docker Desktop.
- Instalación persistente en Linux para que el dictado esté disponible después de reiniciar e iniciar sesión.

**Non-Goals:**

- Control completo del IDE por voz en esta primera iteración.
- Comandos hablados de formato o símbolos de código; el texto se insertará literalmente como lenguaje natural.
- Corrección semántica con LLM o refactor automático.
- Soporte inicial garantizado para macOS/Windows.
- Ejecución remota por defecto; la ruta principal debe ser local.

## Decisions

- Reutilizar la capability `push-to-talk-dictation` en lugar de crear una nueva: el comportamiento es una evolución natural del dictado push-to-talk ya priorizado.
- Crear un puerto `StreamingAsrTranscriber` en la capa de aplicación, con eventos `partial`, `final`, `error` y `state`.
- Hacer una spike antes del adapter definitivo: comprobar si Ollama puede servir este modelo ASR con audio streaming. Si no puede, priorizar una ruta local alternativa y documentarla.
- Resultado de la spike: Ollama no queda seleccionado para esta primera implementación. Docker/NVIDIA Speech NIM o NeMo sigue siendo una ruta GPU futura, pero esta máquina no expone actualmente `nvidia-smi`, `/dev/nvidia*` ni runtime NVIDIA en Docker.
- Resultado de la spike ONNX/CPU: `onnx-community/nemotron-3.5-asr-streaming-0.6b-onnx-int4` carga con `onnxruntime-genai` en CPU, usa `StreamingProcessor`, `lang_id=2` para `es-ES`, y transcribe el audio de prueba de 44.65 s en 29.47 s (`RTF=0.66`). Esta será la primera ruta de adapter.
- Mantener press-and-hold como interacción inicial con `Ctrl+Alt+Space`: key-down empieza a capturar y transcribir; key-up detiene inmediatamente la captura, cierra/finaliza el stream ASR y solo permite insertar el cierre final pendiente. No habrá modo toggle en esta fase.
- Integrar la instalación con `install-linux-desktop-integration`: registrar el atajo GNOME, wrapper de diagnóstico y cualquier servicio `systemd --user` necesario para que el runtime o listener esté disponible en cada login. La sesión de dictado solo captura audio mientras el atajo está pulsado; lo persistente es la integración/listener/runtime preparado, no una grabación activa.
- Insertar texto solo cuando haya hipótesis estable o final. Los parciales se pueden mostrar en overlay; la inserción incremental debe preferir segmentos finalizados para evitar ediciones destructivas en campos externos.
- Tratar el contenido dictado como texto literal de lenguaje natural. Frases como "nueva línea" o "tab" no tendrán significado especial en esta primera fase.
- Observación de uso real del 2026-06-13: la ruta ONNX CPU ya responde al atajo y transcribe parcialmente, pero no queda aceptada como experiencia final. Al mantener `Ctrl+Alt+Space`, tarda un par de segundos en empezar a emitir texto, se pierden palabras iniciales, y la inserción incremental puede dejar texto desordenado o borrar/reemplazar texto ya escrito. El siguiente pase debe centrarse en buffering previo, estabilización de segmentos y una estrategia de inserción no destructiva.

## Risks / Trade-offs

- [Runtime pesado o GPU no disponible] -> Detectar precondiciones al arrancar y mostrar feedback claro; documentar fallback futuro a otro ASR local.
- [Ollama no soporta ASR streaming para Nemotron] -> Registrar la conclusión de la spike y usar Docker/NVIDIA NIM/NeMo como runtime local.
- [GPU/NVIDIA runtime no disponible en el equipo] -> Mantener listener/shortcut instalables, pero degradar a estado "runtime unavailable" hasta que exista GPU/runtime compatible o se añada un ASR local alternativo.
- [ONNX CPU demasiado lento en otro equipo] -> Medir RTF en preflight o primera ejecución y permitir degradar a "runtime too slow" o backend alternativo.
- [Parciales inestables] -> Mostrar parciales en overlay y solo insertar texto estable/final salvo que el usuario active inserción agresiva.
- [Inserción incremental desordenada o destructiva] -> No escribir tokens sueltos directamente en el campo externo; acumular una hipótesis de sesión, reconciliar finales con timestamps/offsets cuando el runtime lo permita, y confirmar bloques estables de forma append-only o con edición controlada en un buffer propio.
- [Pérdida de palabras iniciales] -> Añadir pre-roll de audio al key-down, inicializar/calentar el runtime antes de abrir la ventana de dictado y medir latencia hasta primer token.
- [Inserción en Wayland] -> Reutilizar degradación existente: si no se puede escribir directamente, copiar al portapapeles o notificar.
- [Modelo todavía reciente] -> Encapsular la integración en un adapter pequeño para poder ajustar NeMo/NIM sin tocar la UX.
- [Atajo perdido tras reinicio] -> Reutilizar el autostart/healthcheck de escritorio para reaplicar atajos y registrar evidencia temprana en logs.
