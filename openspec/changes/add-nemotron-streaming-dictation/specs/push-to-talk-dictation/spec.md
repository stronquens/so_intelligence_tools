## MODIFIED Requirements

### Requirement: Transcripción automática en local al terminar la grabación
El sistema SHALL transcribir audio localmente usando un runtime ASR configurado. Para la ruta streaming, el sistema SHALL capturar audio y transcribir solo mientras el usuario mantenga pulsada la combinación de teclas, y SHALL finalizar el stream al soltar la pulsación.

#### Scenario: Audio capturado correctamente
- **WHEN** el usuario suelta la combinación y existe audio válido
- **THEN** la herramienta SHALL detener inmediatamente la captura de micrófono
- **AND** SHALL finalizar el stream ASR local
- **AND** SHALL confirmar la transcripción final pendiente

#### Scenario: Transcripción streaming durante el habla
- **WHEN** el usuario mantiene pulsada la combinación asignada y habla en español
- **THEN** la herramienta SHALL enviar chunks de audio al runtime local de ASR mientras se capturan
- **AND** SHALL recibir eventos parciales o finales sin esperar al fin de toda la grabación

#### Scenario: La pulsación se libera
- **WHEN** el usuario deja de pulsar la combinación asignada
- **THEN** la herramienta SHALL dejar de enviar audio nuevo al runtime ASR
- **AND** SHALL cerrar o finalizar la sesión de transcripción
- **AND** SHALL NOT seguir escuchando ni transcribiendo en segundo plano

### Requirement: Inserción automática del texto en el foco actual
El sistema SHALL insertar la transcripción resultante directamente en el punto donde el usuario tenga el cursor activo. En modo streaming, la herramienta SHALL insertar segmentos estables o finales de forma incremental, evitando duplicar texto ya insertado.

#### Scenario: Hay un campo editable con foco
- **WHEN** la transcripción se completa correctamente
- **THEN** el sistema SHALL escribir el texto resultante en la ubicación actual del cursor

#### Scenario: Inserción incremental durante dictado
- **WHEN** el runtime ASR entregue un segmento final mientras el usuario sigue pulsando el atajo
- **THEN** la herramienta SHALL insertar ese segmento en el campo enfocado sin esperar al final de la sesión completa
- **AND** SHALL mantener un cursor de progreso para no repetir segmentos previos

#### Scenario: Parcial inestable
- **WHEN** el runtime ASR entregue una hipótesis parcial no final
- **THEN** la herramienta SHALL poder mostrarla en el overlay
- **AND** SHALL NOT insertar texto destructivo en el campo externo salvo que el usuario active un modo explícito de parciales agresivos

## ADDED Requirements

### Requirement: Runtime local Nemotron 3.5 ASR
La primera ruta streaming SHALL usar un runtime local compatible con `nvidia/nemotron-3.5-asr-streaming-0.6b` para transcribir español con baja latencia.

#### Scenario: Runtime disponible
- **WHEN** el usuario active el dictado streaming y el runtime local esté preparado
- **THEN** la herramienta SHALL cargar o conectar con Nemotron 3.5 ASR Streaming 0.6B
- **AND** SHALL configurar español como idioma esperado cuando el runtime lo permita

#### Scenario: Runtime ausente o incompatible
- **WHEN** el usuario active el dictado streaming y falte el runtime local, el modelo o una dependencia crítica
- **THEN** la herramienta SHALL mostrar feedback claro
- **AND** SHALL NOT capturar audio indefinidamente ni insertar texto vacío

#### Scenario: Runtime ONNX CPU disponible
- **WHEN** el usuario active el dictado streaming en un equipo sin GPU NVIDIA compatible
- **AND** `onnxruntime-genai` y el modelo ONNX INT4 estén disponibles
- **THEN** la herramienta SHALL usar la ruta ONNX CPU para transcribir audio localmente
- **AND** SHALL configurar `es-ES` mediante el identificador de idioma soportado por el runtime

### Requirement: Dictado literal para prompts en lenguaje natural
El sistema SHALL ofrecer un modo de dictado apto para escribir prompts e instrucciones en lenguaje natural en campos de editor, chat o IDE sin tocar el teclado.

#### Scenario: Inserción literal
- **WHEN** el usuario dicte una frase normal en español
- **THEN** la herramienta SHALL insertar las palabras reconocidas como texto literal
- **AND** SHALL NOT convertir frases habladas en comandos de formato o símbolos de código en esta primera fase

### Requirement: Configuración de dictado streaming
La herramienta SHALL permitir configurar por entorno el modelo ASR, idioma, fuente de micrófono, tamaño de chunk, atajo y estrategia de inserción.

#### Scenario: Configuración por defecto en español
- **WHEN** el usuario no configure idioma explícitamente
- **THEN** la herramienta SHALL asumir español para el dictado local inicial

#### Scenario: Ajuste de latencia
- **WHEN** el usuario configure el tamaño de chunk o contexto del runtime ASR
- **THEN** la herramienta SHALL aplicar esos valores en la siguiente sesión cuando el runtime los soporte

### Requirement: Instalación persistente de escritorio
La herramienta SHALL integrarse con la instalación Linux del proyecto para que el dictado esté disponible después de reiniciar el equipo e iniciar sesión.

#### Scenario: Inicio de sesión tras reinicio
- **WHEN** el usuario reinicie el PC e inicie sesión en Linux
- **THEN** el atajo de dictado streaming SHALL estar registrado o reaplicarse automáticamente
- **AND** los servicios o wrappers necesarios SHALL estar disponibles sin lanzar comandos manuales

#### Scenario: Dictado no activo hasta pulsación
- **WHEN** el sistema arranque y el usuario aún no haya pulsado el atajo
- **THEN** la integración SHALL estar preparada
- **AND** la herramienta SHALL NOT capturar audio hasta que el usuario mantenga pulsado el atajo

### Requirement: Spike de runtime local ASR
El sistema SHALL evaluar la vía de ejecución local de Nemotron 3.5 ASR antes de fijar el adapter definitivo.

#### Scenario: Ollama soporta el caso de uso
- **WHEN** la spike confirme que Ollama puede servir `nvidia/nemotron-3.5-asr-streaming-0.6b` con entrada de audio y latencia apta
- **THEN** la implementación SHALL preferir una ruta operativa similar a la usada por Gemma 4

#### Scenario: Ollama no soporta el caso de uso
- **WHEN** la spike confirme que Ollama no soporta el modelo o el modo ASR streaming requerido
- **THEN** la implementación SHALL definir una ruta local alternativa con ONNX CPU o Docker/NVIDIA NIM/NeMo según el hardware disponible
