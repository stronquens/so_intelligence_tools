## MODIFIED Requirements

### Requirement: Aplicacion Electron + Vue.js
La interfaz SHALL estar implementada como aplicacion de escritorio con Electron y Vue.js.

#### Scenario: Arranque funcional desde el atajo Linux
- **WHEN** el usuario pulse `Ctrl+Alt+Y` en Linux
- **THEN** el sistema SHALL abrir o alternar la ventana Electron/Vue del traductor
- **AND** SHALL iniciar una sesion Python real sin abrir simultaneamente la ventana Tkinter

#### Scenario: Render aislado de desarrollo
- **WHEN** el render Vue se abra sin el bridge Electron
- **THEN** SHALL poder mostrar datos mock para revisar layout y estados
- **AND** SHALL identificar ese estado como una previsualizacion no conectada

#### Scenario: Convivencia con la ventana actual
- **WHEN** la UI Electron se convierta en la superficie predeterminada del atajo
- **THEN** la ventana `tkinter` SHALL permanecer disponible como fallback manual
- **AND** ambas superficies SHALL reutilizar el mismo controlador Python

### Requirement: Contrato de eventos con Python
La UI SHALL comunicarse con el backend Python mediante un contrato estable de eventos y comandos.

#### Scenario: Bridge conectado al controlador real
- **WHEN** la ventana Electron inicia una sesion
- **THEN** SHALL recibir eventos JSON Lines de un proceso Python hijo
- **AND** SHALL enviar comandos validados al mismo proceso mediante preload seguro
- **AND** SHALL mantener captura, proveedores y credenciales fuera del renderer

#### Scenario: Eventos tempranos
- **WHEN** Python emite estado antes de que Vue termine de montarse
- **THEN** Electron SHALL conservar esos eventos en un buffer acotado
- **AND** SHALL entregarlos cuando el renderer anuncie que esta listo

#### Scenario: Diagnóstico fuera del canal de eventos
- **WHEN** el backend informa estados operativos o escribe diagnóstico
- **THEN** `stdout` SHALL contener exclusivamente eventos JSON Lines válidos
- **AND** el texto de diagnóstico SHALL escribirse en `stderr` o en el log de sesión
- **AND** Electron SHALL descartar y registrar una línea no JSON sin convertir la sesión activa en error

### Requirement: Movimiento y estados profesionales
La UI SHALL usar animaciones discretas y estados operativos claros para mejorar la comprension sin reducir la legibilidad.

#### Scenario: Llega un bloque o parcial
- **WHEN** llega un bloque final o cambia el segmento en progreso
- **THEN** la UI SHALL actualizar el mismo flujo agrupado sin parpadeos ni saltos de columnas
- **AND** MAY animar brevemente la entrada o el indicador de progreso

#### Scenario: Pausa, reconexion o error
- **WHEN** la sesion cambia a pausa, reconexion o error
- **THEN** la UI SHALL reflejarlo mediante texto, color y disponibilidad de controles
- **AND** SHALL conservar los bloques completados ya visibles

#### Scenario: Movimiento reducido
- **WHEN** el sistema solicita `prefers-reduced-motion`
- **THEN** la UI SHALL desactivar las animaciones no esenciales

### Requirement: Validacion de la UI y del contrato
La implementacion futura SHALL validar por separado el contrato Python/UI, el render frontend y la integracion con el flujo real.

#### Scenario: Validacion visual inicial
- **WHEN** la interfaz Electron/Vue este disponible con datos mock
- **THEN** SHALL poder capturarse una screenshot local para revisar layout, sidebar, burbujas EN/ES y controles
- **AND** SHALL completar tests frontend y build de escritorio sin errores

#### Scenario: Smoke test funcional
- **WHEN** se valide la integracion final en Linux
- **THEN** `Ctrl+Alt+Y` SHALL abrir la ventana Electron conectada
- **AND** una sesion real SHALL poder publicar estado, parciales o bloques y responder a pausa, reanudacion y parada

### Requirement: Controles de ventana accesibles
La ventana SHALL permitir cerrar, minimizar y maximizar o restaurar mediante controles visibles, animados y faciles de accionar.

#### Scenario: Accion de ventana
- **WHEN** el usuario active uno de los tres controles de ventana
- **THEN** Electron SHALL ejecutar la accion nativa correspondiente
- **AND** el control SHALL ofrecer un objetivo de puntero y foco mayor que su marca visual

#### Scenario: Hover fiel al control circular
- **WHEN** el puntero pase sobre cerrar, minimizar o maximizar
- **THEN** el fondo del objetivo interactivo SHALL permanecer transparente
- **AND** la sombra SHALL quedar ceñida a la marca circular visible
- **AND** la apariencia nativa del botón SHALL NOT dibujar un halo alrededor del objetivo

### Requirement: Idiomas configurables desde la sesion
La UI SHALL construir sus selectores desde el catalogo de idiomas que publica el backend y aplicar cambios reales a la sesion.

#### Scenario: Cambio de idioma
- **WHEN** el usuario seleccione otro origen o destino soportado
- **THEN** Vue SHALL enviar un comando validado con ambos codigos
- **AND** Python SHALL reiniciar el controlador activo con esos idiomas
- **AND** la UI SHALL conservar el historial ya mostrado

#### Scenario: Catalogo y deteccion automatica
- **WHEN** el backend publique la configuracion de sesion
- **THEN** la UI SHALL mostrar solo opciones declaradas por ese catalogo
- **AND** SHALL ofrecer deteccion automatica unicamente como idioma de origen

#### Scenario: Seleccion pendiente de confirmacion
- **WHEN** el usuario cambie un idioma soportado
- **THEN** el selector SHALL reflejar inmediatamente la nueva eleccion sin rebotar al valor anterior
- **AND** SHALL conservarla mientras espera la configuracion confirmada por Python
- **AND** SHALL restaurar la ultima configuracion confirmada si el comando falla

#### Scenario: Identidad visual del catalogo completo
- **WHEN** el usuario abra cualquiera de los selectores de idioma
- **THEN** cada idioma publicado SHALL mostrar su nombre y una bandera o icono explicito
- **AND** el menu SHALL mostrarse fuera del recorte del sidebar y seguir siendo utilizable con teclado

### Requirement: Conversacion densa y alineada
La UI SHALL mostrar original y traduccion como columnas correspondientes para aumentar la cantidad de contexto visible.

#### Scenario: Ventana con espacio horizontal
- **WHEN** haya anchura suficiente
- **THEN** cada turno SHALL renderizar original a la izquierda y traduccion a la derecha en la misma fila
- **AND** las cabeceras SHALL identificar los idiomas efectivos

#### Scenario: Preferencia de densidad
- **WHEN** el usuario cambie entre densidad compacta y comoda
- **THEN** SHALL ajustarse espaciado y tipografia sin ocultar texto
- **AND** la preferencia SHALL persistir para la siguiente apertura

### Requirement: Layout responsive sin contenido perdido
La ventana SHALL mantener contenido y acciones disponibles al cambiar anchura o altura.

#### Scenario: Ventana estrecha o baja
- **WHEN** el usuario redimensione la ventana dentro de sus limites permitidos
- **THEN** sidebar, cabecera, transcript y controles SHALL reajustarse sin desaparecer
- **AND** los selectores abiertos SHALL permanecer utilizables sin quedar recortados
- **AND** las columnas MAY apilarse cuando ya no exista anchura legible

### Requirement: Estado de pausa sincronizado
El chip de estado, el lateral y el control principal SHALL derivar de una unica maquina de estados de sesion.

#### Scenario: Pausa o reanudacion pendiente
- **WHEN** el usuario solicite pausar o reanudar
- **THEN** la UI SHALL mostrar el estado transitorio correspondiente
- **AND** SHALL evitar solicitudes duplicadas hasta recibir confirmacion del backend

### Requirement: Medidor de audio real
El medidor SHALL representar amplitud PCM capturada y no una secuencia decorativa fija.

#### Scenario: Audio del sistema activo
- **WHEN** el controlador reciba chunks del monitor de salida
- **THEN** SHALL publicar niveles normalizados y acotados hacia Electron
- **AND** las barras SHALL responder a esos niveles y decaer al silencio si dejan de llegar

#### Scenario: Voz traducida activa
- **WHEN** el micrófono traducido esté activo
- **THEN** el medidor SHALL priorizar el nivel del micrófono físico
- **AND** SHALL identificar visualmente que está mostrando entrada de micrófono

### Requirement: Micrófono traducido estable
El botón de micrófono SHALL controlar la ruta física → traducción realtime → micrófono virtual seleccionable por una videollamada.

#### Scenario: Endpoint virtual existente
- **WHEN** `so_ai_translated_mic` ya exista por una ejecución anterior
- **THEN** la canalización SHALL reutilizar el sink y la fuente exactos
- **AND** SHALL evitar publicar un endpoint alternativo con sufijo

#### Scenario: Estado pendiente del botón
- **WHEN** el usuario active o desactive la traducción de voz
- **THEN** la UI SHALL bloquear solicitudes duplicadas hasta recibir confirmación
- **AND** SHALL exponer el mensaje operativo que indica qué micrófono seleccionar

#### Scenario: Salida traducida visible
- **WHEN** la traducción de voz esté apagada, conectando, activa o deteniéndose
- **THEN** la interfaz SHALL mostrar de forma persistente el estado de la salida traducida
- **AND** SHALL mostrar visiblemente el mensaje del backend que identifica el micrófono virtual
- **AND** cuando se escriba audio traducido SHALL mostrar contadores confirmados por Python

#### Scenario: Spinner sobre superficie estable
- **WHEN** el botón grande de micrófono o pausa espere confirmación
- **THEN** SHALL girar únicamente el indicador de carga
- **AND** el recuadro o círculo que contiene el indicador SHALL permanecer inmóvil

#### Scenario: Parada confirmada del traductor de voz
- **WHEN** el usuario desactive la traducción de voz
- **THEN** el controlador SHALL cerrar o cancelar de forma acotada las tareas realtime
- **AND** SHALL publicar el estado inactivo solo después de que el worker haya terminado

### Requirement: Fidelidad visual al mock aprobado
La interfaz SHALL conservar el lenguaje y las proporciones del mock original salvo en los cambios funcionales expresamente solicitados.

#### Scenario: Ventana amplia
- **WHEN** la ventana disponga del viewport de referencia
- **THEN** controles de ventana, sidebar, banderas, cabecera y barra inferior SHALL mantener apariencia y proporciones equivalentes al mock
- **AND** la zona de clic de un control MAY ser mayor que su marca visible

#### Scenario: Excepciones funcionales
- **WHEN** se comparen mock e implementacion
- **THEN** las diferencias intencionadas SHALL limitarse al transcript horizontal, densidad configurable, selectores funcionales y comportamiento responsive

#### Scenario: Selector de modelo
- **WHEN** el usuario abra el modelo de transcripción
- **THEN** SHALL conservar el tratamiento visual de botón y menú del mock
- **AND** SHALL listar únicamente modos realmente soportados por el backend
