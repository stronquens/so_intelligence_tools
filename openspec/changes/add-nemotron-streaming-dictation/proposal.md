## Why

El dictado actual de `push-to-talk-dictation` está definido como grabar mientras se mantiene un atajo y transcribir al soltar. Para vibecoding y escritura fluida en campos de texto necesitamos dictar prompts en lenguaje natural directamente en el campo enfocado, con latencia baja y sin depender de servicios remotos.

NVIDIA ha publicado `nvidia/nemotron-3.5-asr-streaming-0.6b`, un modelo ASR streaming multilingüe de 600M parámetros con soporte para español, puntuación/capitalización y chunks de baja latencia configurables. Esto encaja con una primera ruta local de dictado interactivo.

## What Changes

- Ampliar `push-to-talk-dictation` de transcripción post-grabación a una primera fase de dictado streaming con inserción de segmentos finales/estables.
- Usar Nemotron 3.5 ASR Streaming 0.6B como runtime local preferido para español si la spike confirma una vía viable.
- Evaluar en una spike si Nemotron puede servirse vía Ollama; si no, definir ruta Docker/NVIDIA NIM/NeMo para poder encenderlo y apagarlo desde Docker Desktop.
- Definir captura de micrófono, streaming ASR, estabilización de parciales y escritura directa en el foco actual.
- Fijar el atajo inicial como `Ctrl + Alt + Space`.
- Mantener el dictado como texto literal en lenguaje natural, sin comandos especiales de formato en esta primera fase.
- Instalar la integración de escritorio de forma persistente para que el dictado esté disponible tras reiniciar el PC e iniciar sesión.
- Mantener fallback claro cuando no exista runtime local compatible o no haya campo editable con foco.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `push-to-talk-dictation`: pasa a cubrir dictado streaming local de baja latencia con inserción incremental en el campo enfocado.
- `keyboard-shortcuts`: añade requisitos para un atajo global de dictado mantenido, con diagnóstico de inicio/fin y bajo riesgo de colisión.

## Impact

- Nuevos adaptadores Python para captura de micrófono y streaming ASR local.
- Spike de runtime local: Ollama si soporta la ruta ASR necesaria, o contenedor Docker/NVIDIA NIM/NeMo compatible para `nvidia/nemotron-3.5-asr-streaming-0.6b`.
- Escritura incremental sobre el foco actual usando los adaptadores Linux existentes de inserción de texto.
- Configuración de entorno para modelo, idioma, fuente de micrófono, atajo y estrategia de inserción.
- Instalación persistente de atajo/servicio de usuario en Linux, integrada con el bootstrap de escritorio existente.
- Tests unitarios con fakes para streaming, parciales/finales y acciones de teclado.
