## Context

La traduccion de audio ya funciona en Python: captura audio del sistema,
mantiene la sesion realtime, publica parciales y bloques finales, guarda logs y
responde a pausa, reanudacion, cambio de modo y parada. La ventana Tkinter actual
expone ese comportamiento, pero su acabado visual es limitado.

`desktop/` contiene una interfaz Electron/Vue visualmente aprobada y un bridge
preload seguro, aunque el transcript y los comandos siguen mockeados. Linux abre
la app funcional con `Ctrl+Alt+Y` mediante
`scripts/run-system-audio-translation-debug.sh`. El cambio debe sustituir solo
esa superficie de lanzamiento, sin mover captura ni credenciales al renderer.

## Goals / Non-Goals

**Goals:**

- Usar la interfaz Electron como superficie real de `Ctrl+Alt+Y` en Linux.
- Mantener Python como dueño unico de captura, proveedor, ciclo de vida y logs.
- Entregar eventos reales a Vue y comandos validados de vuelta a Python.
- Preservar la agrupacion estable de original/traduccion y el historial ya
  recibido durante reconexiones.
- Añadir movimiento discreto y estados claros sin perjudicar la lectura.
- Mantener pares original/traduccion alineados horizontalmente y legibles al
  redimensionar, con una alternativa apilada solo cuando no caben dos columnas.
- Hacer configurables idiomas y densidad desde controles que no puedan quedar
  cortados por el contenedor lateral.
- Conservar Tkinter como fallback invocable manualmente durante la migracion.

**Non-Goals:**

- Capturar audio o llamar a proveedores desde Electron.
- Exponer secretos en IPC o en el renderer.
- Implementar opciones visuales de proveedores que el backend no soporta.
- Cambiar el algoritmo de segmentacion, VAD o traduccion.

## Decisions

### Proceso Python hijo con JSON Lines

Electron iniciara un comando CLI dedicado y mantendra un proceso Python por
ventana de traductor. Python escribira un `UiEvent` JSON por linea en `stdout` y
Electron escribira un `UiCommand` JSON por linea en `stdin`.

Se elige este transporte porque el ciclo de vida queda asociado a la ventana,
no necesita abrir puertos ni gestionar autenticacion local, permite separar
`stderr` para diagnostico y mantiene `contextIsolation`. Un socket Unix
bidireccional permitiria reconexion independiente, pero añade descubrimiento,
limpieza y protocolo innecesarios para una sola ventana local.

`stdout` queda reservado de forma estricta para `UiEvent`. Los mensajes humanos
del controlador se escriben en `stderr` y en el log estructurado. Como defensa
adicional, Electron registra y descarta una linea no JSON sin transformar un
fallo de diagnostico aislado en un error fatal de la sesion visible.

### Adaptador de ventana sin duplicar el controlador

`ModeAwareSystemAudioTranslationApp` recibira una factoria de ventana. La
factoria existente seguira creando Tkinter y la nueva creara un adaptador
headless que serializa callbacks y despacha comandos. Captura, modos, proveedor,
historial y log permanecen sin cambios.

### Electron controla buffering y ciclo de vida

El proceso principal validara comandos, parseara stdout por lineas, almacenara
un buffer corto hasta que Vue anuncie que esta listo y enviara eventos solo a la
ventana del traductor. Al cerrar o alternar la ventana, Electron solicitara una
parada limpia y aplicara terminacion acotada solo si Python no sale.

### El atajo abre Electron; Tkinter queda como fallback

El wrapper GNOME lanzara Electron con `--translator`. La instancia unica
interpretara ese argumento para abrir, enfocar u ocultar la ventana correcta.
El comando Python existente de ventana Tkinter se mantiene para diagnostico y
rollback; un fallo de Electron se registra de forma accionable.

### Estado real con mock explicito solo en navegador

Vue arrancara vacio cuando exista el bridge Electron y se suscribira antes de
mostrar contenido. Los datos mock solo apareceran al abrir el render de
desarrollo sin bridge. Pausa, modo, conexion, parciales, bloques y microfono
traducido procederan de eventos reales.

La QA visual de Electron usara `SO_AI_TRANSLATOR_MOCK=1`. En ese modo el proceso
principal no inicia el bridge Python aunque el preload exista, evitando consumo
accidental de una API de pago durante capturas, resize o ajustes visuales.

### Movimiento orientado a legibilidad

Se conservara el lenguaje visual del mock. Los nuevos pares entraran con una
transicion corta, el bloque parcial respirara suavemente, el indicador de audio
se pausara cuando la sesion no este activa y los cambios de estado usaran color
y texto ademas de animacion. `prefers-reduced-motion` desactivara movimiento no
esencial.

### Configuracion publicada por Python

El bridge publicara un evento `session_config` con idioma de origen, destino y
catalogo soportado. Vue no mantendra una lista independiente. Un comando
`change_languages` validado actualizara la configuracion efectiva, reconstruira
el controlador del modo activo y conservara en Vue los bloques ya recibidos.

El prompt realtime dejara de asumir español y usara el destino efectivo. La
opcion `auto` se ofrece solo para el origen; los destinos requieren un codigo
concreto del catalogo.

### Controles y menus no recortables

Cerrar, minimizar y maximizar siguen viajando por el preload aislado, pero su
objetivo interactivo sera mayor que el punto visual y mostrara hover, pulsacion
y foco. Los selectores de idioma y modelo usan popovers teletransportados para
no quedar limitados por el `overflow` del sidebar.

La marca visible roja, amarilla o verde conservara los 17 px del mock dentro de
un boton transparente de 34 px. De este modo aumenta el objetivo sin cambiar la
apariencia aprobada.

El boton exterior neutraliza `appearance`, fondo, borde, filtro y sombra nativos
en todos sus estados. Solo `.dot-mark` recibe color y sombra; el foco de teclado
se dibuja sobre esa marca y no como un disco blanco alrededor del objetivo.

Los idiomas usan un selector propio accesible teletransportado al `body`. El
boton conserva el aspecto del mock, mientras el menu flotante queda fuera del
`overflow` del sidebar y puede mostrar la bandera real de cada opcion. Clic
exterior, `Escape`, foco y botones nativos cubren el cierre y la navegacion por
teclado. El modelo usa el mismo patrón de popover teletransportado que los
idiomas para reproducir el menú del mock, con icono y check por opción, pero
solo expone los dos modos que Python admite realmente.

El renderer aplica los cambios de idioma de forma optimista y conserva aparte
la ultima pareja confirmada por Python. Un `session_config` coincidente confirma
la seleccion; una configuracion anterior no puede hacerla rebotar mientras el
cambio esta pendiente, y un error restaura los valores confirmados.

### Fidelidad al mock aprobado

En ventanas amplias se restauraran las proporciones del mock: sidebar de 356
px, titlebar de 76 px, controles inferiores de 124 px, banderas reales en los
selectores de idioma y resumen de ruta `Source → Target` sin cajas añadidas. Los
breakpoints podran compactar esas medidas solo cuando el espacio lo exija.

El nuevo transcript horizontal y el selector de densidad son excepciones
funcionales solicitadas. El resto de componentes debe conservar tipografia,
bordes, radios, iconos y espaciado del mock original.

### Transcript en columnas con densidad persistente

Cada turno sera una fila con hora, celda original y celda traducida. Las
cabeceras de idioma comparten exactamente la misma reticula para mantener la
correspondencia visual. En anchuras reducidas la fila se apila de forma
explicita; no se encoge el texto hasta hacerlo ilegible.

La densidad (`compact` o `comfortable`) se guarda en `localStorage`. Compacta
sera el valor inicial para reducir padding, tipografia y separacion sin ocultar
contenido ni recortar controles.

### Transiciones de comandos de sesion

Al pulsar pausa o reanudar, la UI mostrara `Pausing…` o `Resuming…` y bloqueara
solo ese control hasta recibir el siguiente `session_state`. El chip superior,
el lateral y el boton principal derivaran del mismo estado mas este comando
pendiente, evitando combinaciones visuales contradictorias.

Los controles grandes separan la superficie visual estatica del icono interior.
Durante una espera rota solo el icono `LoaderCircle`; el fondo blanco o azul no
participa en la transformacion. El mensaje de estado del micrófono traducido se
muestra además en una franja persistente entre la conversación y los controles,
en vez de existir únicamente como tooltip.

### Niveles PCM y procedencia del medidor

Los controladores calculan RMS normalizado sobre cada chunk `s16le` y limitan la
publicación a una frecuencia apta para UI. El bridge añade `audio_level` con
procedencia `system` o `microphone`. Vue mantiene una ventana temporal de
niveles, aplica una curva visual y decae a cero cuando el flujo calla; no usa
alturas ni animaciones periódicas en producción. El mock genera niveles
sintéticos únicamente bajo su etiqueta `Preview`.

Cuando la voz traducida está activa se visualiza el micrófono físico; en otro
caso se visualiza el monitor de audio del sistema. Así el usuario sabe qué flujo
está observando sin mezclar dos capturas concurrentes.

### Endpoint de micrófono virtual estable

Antes de crear módulos, el adaptador PulseAudio consulta si el sink interno y
la fuente pública exactos ya existen. Si ambos existen, los reutiliza y abre la
reproducción sobre el sink estable, sin crear variantes `.2`; solo descarga los
módulos que creó en la sesión actual. Una fuente sin su sink maestro se trata
como estado inconsistente y produce un error accionable.

## Risks / Trade-offs

- [El proceso Python termina inesperadamente] → Electron conserva el historial,
  muestra el error y permite reiniciar la sesion sin recargar la ventana.
- [Eventos llegan antes de montar Vue] → el proceso principal mantiene un
  buffer acotado y lo entrega tras `translator-ready`.
- [Una linea de diagnostico contamina stdout] → el bridge reserva stdout para
  JSONL y redirige diagnostico a stderr/log.
- [Cierre bloqueado por captura o red] → parada cooperativa seguida de timeout y
  cancelacion explicita de sender/receiver; el estado inactivo se publica solo
  despues de terminar el worker y Electron conserva la terminacion acotada del hijo.
- [El atajo encuentra otra instancia Electron] → el bloqueo de instancia unica
  enruta `--translator` a la ventana existente.
- [Animaciones dificultan leer mensajes cortos] → no se autoeliminan bloques,
  las transiciones son breves y se respeta movimiento reducido.
- [Cambio de idioma durante audio activo] → se detiene el controlador anterior,
  se publican estados de reconexion y se inicia uno nuevo; el historial del
  renderer se conserva.
- [Ventana demasiado estrecha o baja] → reticulas fluidas, sidebar desplazable,
  controles compactos y breakpoint apilado mantienen todas las acciones.

## Migration Plan

1. Añadir y probar el adaptador JSONL Python manteniendo Tkinter por defecto.
2. Conectar preload, proceso principal y Vue con buffering de eventos.
3. Cambiar el wrapper de `Ctrl+Alt+Y` para abrir Electron con `--translator`.
4. Reinstalar el atajo GNOME y ejecutar tests/build.
5. Probar una sesion real, pausa/reanudacion/parada e historial.
6. Si falla el smoke test, restaurar temporalmente el wrapper al comando Tkinter
   sin revertir el controlador ni los logs.

## Open Questions

- La seleccion dinamica del dispositivo de audio queda para un change posterior.
