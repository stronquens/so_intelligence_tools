# Purpose

Definir una interfaz de escritorio Electron + Vue.js para visualizar y controlar la traduccion en tiempo real del audio del sistema, reutilizando como backend funcional la capability `system-audio-transcription`.

Esta capability es una mejora visual futura. No reemplaza automaticamente la ventana actual ni modifica la captura de audio, el proveedor realtime, los logs, los shortcuts o el ciclo de vida del controlador Python hasta que un change posterior lo valide.

## Requirements

### Requirement: Dependencia funcional sobre system-audio-transcription
La interfaz SHALL actuar como capa visual sobre la capability `system-audio-transcription`, sin duplicar su responsabilidad de captura, streaming, proveedores, logs o shortcuts.

#### Scenario: El backend Python controla la sesion
- **WHEN** la interfaz Electron/Vue se abre
- **THEN** SHALL consumir estado, parciales y bloques finales emitidos por el controlador Python
- **AND** SHALL enviar comandos de usuario al controlador Python
- **AND** SHALL evitar hablar directamente con OpenAI, LiteLLM, Ollama o cualquier proveedor de modelo

#### Scenario: La UI avanzada no esta disponible
- **WHEN** Electron/Vue no esta instalado, no arranca o no esta validado todavia
- **THEN** el sistema SHALL poder seguir evolucionando la ventana actual de `system-audio-transcription` sin bloquear el cierre de esa capability

### Requirement: Aplicacion Electron + Vue.js
La interfaz SHALL estar implementada como aplicacion de escritorio con Electron y Vue.js.

#### Scenario: Arranque de la aplicacion
- **WHEN** el usuario lance la UI avanzada desde el flujo de traduccion en tiempo real
- **THEN** el sistema SHALL abrir una ventana de escritorio Electron
- **AND** el render principal SHALL estar implementado con Vue.js

#### Scenario: Convivencia con la ventana actual
- **WHEN** se implemente la primera version de esta capability
- **THEN** la UI Electron/Vue SHALL poder convivir como alternativa seleccionable
- **AND** SHALL evitar eliminar la ventana `tkinter` hasta que la nueva UI quede validada manualmente

### Requirement: Layout principal moderno
La UI SHALL presentar una experiencia visual moderna, limpia y orientada a una app de traduccion en vivo.

#### Scenario: Barra superior
- **WHEN** la ventana esta abierta
- **THEN** SHALL mostrar una barra superior con el titulo `Real-Time Translator`
- **AND** SHALL mostrar un indicador `Live` con punto verde cuando la sesion este activa
- **AND** SHALL mostrar un boton de ajustes aunque pueda estar mockeado en esta fase

#### Scenario: Sidebar lateral
- **WHEN** la ventana esta abierta
- **THEN** SHALL mostrar una sidebar con estado de streaming, temporizador de sesion, visualizador de audio, idiomas, selector de modelo y estado de conexion

#### Scenario: Barra inferior
- **WHEN** la ventana esta abierta
- **THEN** SHALL mostrar controles de `Microphone`, `Speaker`, `Pause/Resume`, `Swap` y `Stop`
- **AND** `Pause/Resume` y `Stop` SHALL enviar comandos funcionales al controlador Python
- **AND** los controles mockeados SHALL verse presentes pero no deberan prometer funcionalidad real si todavia no la tienen

### Requirement: Visualizacion agrupada EN/ES
La UI SHALL agrupar cada transcripcion original con su traduccion asociada para que la correspondencia sea inmediata.

#### Scenario: Bloque finalizado
- **WHEN** el backend emite un bloque final con texto original y traduccion
- **THEN** la UI SHALL mostrar una burbuja azul `EN` con el texto original
- **AND** SHALL mostrar justo debajo una burbuja verde `ES` con la traduccion
- **AND** ambas burbujas SHALL compartir el mismo contenedor logico

#### Scenario: Evitar scrolls independientes
- **WHEN** hay multiples segmentos acumulados
- **THEN** la UI SHALL usar un unico flujo principal de scroll para los pares EN/ES
- **AND** SHALL evitar que original y traduccion se desalineen por vivir en paneles desplazables independientes

#### Scenario: Segmento en progreso
- **WHEN** el backend emite texto parcial original o traduccion parcial
- **THEN** la UI SHALL mostrar el segmento actual como bloque en progreso
- **AND** SHALL poder mostrar puntos animados o indicador equivalente mientras se completa

### Requirement: Contrato de eventos con Python
La UI SHALL comunicarse con el backend Python mediante un contrato estable de eventos y comandos.

#### Scenario: Eventos desde Python hacia la UI
- **WHEN** el backend Python cambia de estado o produce contenido
- **THEN** SHALL emitir eventos compatibles con este contrato minimo:

```ts
type UiEvent =
  | { type: "session_state"; state: string; message: string }
  | { type: "partial"; kind: "original" | "translation"; text: string }
  | { type: "block"; id: string; sourceText?: string; translatedText: string; timestamp: string; speakerLabel?: string }
  | { type: "mode"; mode: "translate_es_openai_realtime" | "translate_es_chunked" }
  | { type: "error"; message: string };
```

#### Scenario: Comandos desde la UI hacia Python
- **WHEN** el usuario interactua con controles funcionales
- **THEN** la UI SHALL enviar comandos compatibles con este contrato minimo:

```ts
type UiCommand =
  | { type: "pause" }
  | { type: "resume" }
  | { type: "reset" }
  | { type: "stop" }
  | { type: "change_mode"; mode: "translate_es_openai_realtime" | "translate_es_chunked" };
```

#### Scenario: Transporte no congelado en spec base
- **WHEN** se implemente el primer change de esta capability
- **THEN** el change SHALL elegir y documentar el transporte concreto, como JSON Lines por proceso hijo o socket local
- **AND** la spec base SHALL exigir estabilidad del contrato, no una tecnologia de transporte especifica antes de validarla

### Requirement: Selector de modelo visual
La UI SHALL mostrar un selector de modelo o backend de transcripcion integrado en la sidebar.

#### Scenario: Opciones visibles
- **WHEN** el usuario abre el selector
- **THEN** SHALL poder ver opciones como `Whisper Tiny (Local)`, `Whisper Large v3 (Local)`, `OpenAI Realtime API` y `Deepgram API`
- **AND** SHALL distinguir visualmente modelos locales y APIs remotas
- **AND** SHALL marcar el modo activo

#### Scenario: Opciones mockeadas
- **WHEN** una opcion todavia no este conectada al backend real
- **THEN** la UI MAY mostrarla como mockeada, deshabilitada o no funcional en esta fase
- **AND** SHALL mantener funcional el modo principal conectado a `system-audio-transcription`

### Requirement: Estados visuales de conexion y streaming
La UI SHALL reflejar de forma clara el estado operativo de la sesion.

#### Scenario: Sesion activa
- **WHEN** el backend este en estado activo
- **THEN** SHALL mostrar estado `STREAMING` y `Live`
- **AND** SHALL actualizar el temporizador de sesion

#### Scenario: Reconectando o error
- **WHEN** el backend emite estado de reconexion o error
- **THEN** SHALL mostrar un estado visible como `Reconnecting`, `Poor network` o `Disconnected`
- **AND** SHALL conservar el historial ya mostrado cuando sea posible

### Requirement: Funcionalidad parcial aceptada
La primera version de la UI SHALL permitir elementos visuales no funcionales mientras la parte principal de visualizacion y control este conectada.

#### Scenario: Elementos mockeados
- **WHEN** la UI muestre ajustes, swap de idiomas, microfono, modelos alternativos o señal avanzada de red
- **THEN** esos elementos MAY estar mockeados o fijos en esta fase
- **AND** SHALL evitar bloquear la validacion de la UI principal por funcionalidades secundarias

#### Scenario: Controles funcionales minimos
- **WHEN** el usuario pulse pausa, reanudar o detener
- **THEN** esos controles SHALL comunicarse con el controlador Python real
- **AND** SHALL afectar a la sesion activa de traduccion

### Requirement: No bloquear cierre de capability actual
La nueva capability SHALL poder planificarse e implementarse despues de cerrar la capability actual de traduccion de audio.

#### Scenario: system-audio-transcription aun requiere ajustes
- **WHEN** queden pendientes mejoras de rendimiento, latencia o fiabilidad en `system-audio-transcription`
- **THEN** esta capability SHALL permanecer como trabajo futuro
- **AND** SHALL evitar introducir cambios que distraigan o impidan cerrar la base funcional actual

### Requirement: Validacion de la UI y del contrato
La implementacion futura SHALL validar por separado el contrato Python/UI, el render frontend y la integracion con el flujo real.

#### Scenario: Validacion del contrato Python
- **WHEN** se implemente el serializador de eventos hacia la UI
- **THEN** SHALL existir cobertura de tests Python para eventos `session_state`, `partial`, `block`, `mode` y `error`
- **AND** SHALL existir cobertura para comandos `pause`, `resume`, `reset`, `stop` y `change_mode`

#### Scenario: Validacion frontend
- **WHEN** se implemente la interfaz Electron/Vue
- **THEN** SHALL existir cobertura frontend para renderizar pares agrupados EN/ES
- **AND** SHALL validar segmentos parciales, bloques finales, errores y estado de sesion
- **AND** el build `npm --prefix desktop run build` SHALL completarse correctamente

#### Scenario: Smoke test manual
- **WHEN** la UI avanzada este disponible
- **THEN** SHALL poder abrirse con datos mock para revisar layout y estados visuales
- **AND** SHALL poder abrirse conectada al flujo real de `system-audio-transcription`
