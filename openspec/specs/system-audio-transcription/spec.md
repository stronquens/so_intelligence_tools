# Purpose

Definir una herramienta que capture el audio que suena en el sistema operativo, lo traduzca al español en tiempo real y muestre el resultado en una ventana dedicada con control por atajo global y por controles propios de la ventana.

## Requirements

### Requirement: Inicio desde una herramienta del overlay
El sistema SHALL permitir lanzar la herramienta de transcripción o traducción en tiempo real desde el overlay de herramientas del sistema.

#### Scenario: Selección de la herramienta desde el overlay
- **WHEN** el usuario pulsa el botón correspondiente dentro del overlay
- **THEN** el sistema SHALL abrir una ventana de aplicación dedicada a esa herramienta

### Requirement: Ventana dedicada con control explícito de sesión
La herramienta SHALL mostrar una ventana propia, normal del sistema, redimensionable y no fijada siempre por encima, desde la que el usuario pueda pausar, reanudar, reiniciar y detener la sesión.

#### Scenario: La ventana se abre
- **WHEN** la herramienta es lanzada
- **THEN** el usuario SHALL ver una interfaz con un control claro para pausar o reanudar la captura
- **AND** la ventana SHALL comportarse como una ventana normal del sistema

#### Scenario: El usuario pausa la sesión
- **WHEN** el usuario pausa la captura desde la ventana
- **THEN** el sistema SHALL detener la captura y el consumo del proveedor en vivo sin cerrar necesariamente la ventana

#### Scenario: El usuario reanuda la sesión
- **WHEN** el usuario reanuda la captura desde la ventana
- **THEN** el sistema SHALL volver a activar la captura y el procesamiento en vivo reutilizando la misma ventana

#### Scenario: El usuario reinicia tras un error
- **WHEN** la herramienta está en estado de error y el usuario pulsa el botón de reinicio
- **THEN** el sistema SHALL reintentar la conexión sin perder el historial visible de la sesión actual

#### Scenario: El usuario cierra la ventana
- **WHEN** el usuario cierra manualmente la ventana
- **THEN** el sistema SHALL detener la captura y el procesamiento en vivo
- **AND** SHALL finalizar la sesión activa para dejar de consumir recursos remotos o locales

### Requirement: Atajo global con semántica toggle
La herramienta SHALL poder iniciarse y detenerse reutilizando el mismo atajo global de teclado.

#### Scenario: Primer pulso del atajo
- **WHEN** el usuario pulsa el atajo configurado mientras la herramienta está inactiva
- **THEN** el sistema SHALL abrir la ventana dedicada
- **AND** SHALL comenzar a capturar el audio de salida del sistema
- **AND** SHALL comenzar a traducir en vivo al idioma destino configurado

#### Scenario: Segundo pulso del mismo atajo
- **WHEN** el usuario pulsa el mismo atajo mientras la herramienta está activa
- **THEN** el sistema SHALL detener la captura
- **AND** SHALL detener el procesamiento en vivo
- **AND** SHALL cerrar la ventana dedicada

#### Scenario: Atajo inicial configurable en el futuro
- **WHEN** la primera versión de la herramienta se entregue con un atajo por defecto
- **THEN** la arquitectura SHALL dejar preparada la reasignación futura del atajo desde ajustes del sistema o de la aplicación

### Requirement: Captura de audio de salida del sistema
El sistema SHALL recoger el audio que está sonando por el sistema operativo en ese momento, independientemente de la aplicación que lo reproduzca.

#### Scenario: Audio procedente de una videollamada o reproductor
- **WHEN** una aplicación como Meet, Zoom, Slack u otra emite voz por los altavoces del sistema
- **THEN** la herramienta SHALL poder usar ese audio como entrada de la transcripción

#### Scenario: Independencia respecto de la aplicación origen
- **WHEN** la fuente de audio cambia entre distintas aplicaciones
- **THEN** la herramienta SHALL seguir operando sobre el audio del sistema sin requerir integración específica por aplicación

#### Scenario: No hay audio utilizable en ese momento
- **WHEN** la herramienta está activa pero no llega voz útil desde los altavoces
- **THEN** el sistema SHALL permanecer en espera sin cerrar la sesión automáticamente

### Requirement: Transcripción en streaming con baja latencia percibida
El sistema SHALL mostrar resultados parciales o actualizaciones frecuentes en la ventana con la menor latencia razonable para que la lectura resulte útil en vivo, equilibrando latencia y calidad.

#### Scenario: Habla continua en inglés
- **WHEN** el sistema está capturando una conversación en el idioma inicialmente soportado
- **THEN** la interfaz SHALL actualizar el texto visible de forma progresiva mientras llega el audio

#### Scenario: Buffer de recuperación tras fallo temporal
- **WHEN** la conexión con el backend o proveedor se interrumpe de forma temporal mientras la captura sigue activa
- **THEN** el sistema SHALL intentar conservar una ventana efímera de audio o contexto suficiente para traducir el contenido perdido al reconectarse
- **AND** SHALL reanudar la publicación en la ventana sin perder el historial ya mostrado

### Requirement: Traducción inicial al español con idioma destino configurable
La primera iteración SHALL priorizar la traducción en vivo al español del audio hablado en inglés, dejando la arquitectura preparada para cambiar el idioma destino más adelante.

#### Scenario: Audio en inglés
- **WHEN** el sistema captura una conversación o contenido hablado en inglés
- **THEN** la ventana SHALL mostrar el resultado traducido al español de forma progresiva

#### Scenario: Idioma destino configurable internamente
- **WHEN** la implementación necesite soportar más idiomas de salida en iteraciones futuras
- **THEN** la configuración SHALL poder cambiar el idioma destino sin rediseñar la herramienta

### Requirement: Modo de sesión extensible
La herramienta SHALL dejar preparada una noción de modo de sesión para permitir futuras variantes de procesamiento y presentación sin rediseñar la captura, la ventana ni el atajo.

#### Scenario: Primera iteración con modo por defecto
- **WHEN** se construye la primera versión de la herramienta
- **THEN** la ventana SHALL abrir con un modo por defecto de traducción al español

#### Scenario: Selector de modo visible
- **WHEN** la ventana está abierta
- **THEN** la interfaz SHALL incorporar un desplegable u otro selector equivalente para cambiar entre modos soportados sin rediseñar la captura ni el atajo

#### Scenario: Alternancia entre proveedores o pipelines
- **WHEN** el usuario cambia de modo desde el selector
- **THEN** la herramienta SHALL poder reiniciar la sesión interna con el pipeline correspondiente, como `OpenAI realtime` o un fallback por chunks

### Requirement: Interfaz legible con historial acumulado
La ventana SHALL priorizar la legibilidad del texto en vivo, el estado operativo de la captura y un historial acumulado con scroll.

#### Scenario: Captura activa
- **WHEN** la herramienta está escuchando el audio del sistema
- **THEN** la interfaz SHALL indicar visualmente que la captura está activa y mostrar el texto actualizado

#### Scenario: No hay audio útil o la captura está detenida
- **WHEN** no se recibe voz o la herramienta está detenida
- **THEN** la interfaz SHALL reflejar ese estado sin mostrar resultados engañosos como si hubiera transcripción en curso

#### Scenario: Historial acumulado
- **WHEN** la sesión lleva varios segmentos de traducción acumulados
- **THEN** la ventana SHALL conservarlos en una vista desplazable
- **AND** SHALL permitir que el usuario suba para leer contenido anterior y vuelva abajo para seguir la traducción en vivo

#### Scenario: Formato del historial
- **WHEN** se muestra un nuevo segmento traducido en la ventana
- **THEN** la interfaz SHALL presentarlo como bloque con marca temporal y, cuando sea posible, una etiqueta de speaker como `[voz 1]`

#### Scenario: Texto original y traducción agrupados visualmente
- **WHEN** el proveedor emite transcripción original además de la traducción
- **THEN** la ventana SHALL poder mostrar ambas vistas al mismo tiempo
- **AND** SHALL agrupar visualmente cada bloque de original y traducción dentro del mismo historial para que la correspondencia sea fácil de seguir

### Requirement: Identificación de speakers como best effort
La herramienta SHALL intentar distinguir voces distintas cuando el proveedor o pipeline lo permita, sin bloquear la funcionalidad principal si esa capacidad no está disponible.

#### Scenario: El proveedor permite diarización aproximada
- **WHEN** el backend puede separar voces o hablantes con latencia aceptable
- **THEN** la interfaz SHALL etiquetar los bloques con identificadores aproximados como `[voz 1]` y `[voz 2]`

#### Scenario: No hay diarización disponible
- **WHEN** el pipeline no puede separar speakers de forma fiable sin degradar demasiado la experiencia
- **THEN** la herramienta SHALL seguir mostrando la traducción sin bloquear la sesión por esa ausencia

### Requirement: Persistencia diferida por sesión
La herramienta SHALL escribir el historial textual de cada sesión en un archivo independiente al finalizar, evitando persistencia continua que penalice la latencia.

#### Scenario: La sesión termina por cierre o atajo toggle
- **WHEN** el usuario cierra la ventana o vuelve a pulsar el atajo para detener la herramienta
- **THEN** el sistema SHALL guardar el historial textual de esa sesión en un archivo de log independiente

#### Scenario: El audio no se guarda a disco
- **WHEN** la herramienta está capturando o termina una sesión
- **THEN** el sistema SHALL evitar persistir el audio capturado en disco salvo que una futura capacidad lo requiera explícitamente

### Requirement: Gestión clara de errores y permisos
El sistema SHALL comunicar problemas de permisos, ausencia de dispositivo compatible o fallo del backend de forma comprensible para el usuario, manteniendo el historial visible cuando sea posible.

#### Scenario: El sistema no permite capturar la salida de audio
- **WHEN** la herramienta no puede engancharse al audio del sistema en el entorno actual
- **THEN** la interfaz SHALL informar del problema en lugar de permanecer aparentemente activa sin resultados

#### Scenario: El backend local falla durante el streaming
- **WHEN** el backend deja de devolver actualizaciones válidas
- **THEN** la herramienta SHALL mostrar el error y degradar el flujo de forma controlada
- **AND** SHALL permitir reintentar desde la propia ventana

#### Scenario: Reconexión tras fallo temporal
- **WHEN** el backend o proveedor vuelve a estar disponible tras un corte breve
- **THEN** la herramienta SHALL poder reanudar la traducción sin borrar el historial ya visible

### Requirement: Proveedor remoto validado en la primera iteración
La primera versión validada de esta herramienta SHALL permitir una implementación remota optimizada para streaming, sin cerrar la puerta a rutas locales experimentales más adelante.

#### Scenario: Primera versión oficial
- **WHEN** se construye la primera implementación de referencia
- **THEN** el proveedor remoto SHALL poder ser la vía principal validada para ofrecer mejor equilibrio entre latencia y calidad

#### Scenario: Ruta local futura
- **WHEN** se investiguen proveedores o modelos locales adecuados para este caso de uso
- **THEN** la arquitectura SHALL poder enchufarlos sin romper la semántica de la herramienta
