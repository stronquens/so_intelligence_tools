# Delta Spec

## ADDED Requirements

### Requirement: Activación y parada mediante el mismo atajo global
La herramienta SHALL poder iniciarse y detenerse reutilizando el mismo atajo global de teclado.

#### Scenario: Primer pulso del atajo
- **WHEN** el usuario pulsa el atajo configurado mientras la herramienta está inactiva
- **THEN** el sistema SHALL abrir la ventana dedicada
- **AND** SHALL comenzar a capturar el audio de salida del sistema
- **AND** SHALL comenzar a transcribir o traducir en vivo

#### Scenario: Segundo pulso del mismo atajo
- **WHEN** el usuario pulsa el mismo atajo mientras la herramienta está activa
- **THEN** el sistema SHALL detener la captura
- **AND** SHALL detener el procesamiento en vivo
- **AND** SHALL cerrar la ventana dedicada

### Requirement: Controles de pausa y reintento desde la ventana
La primera iteración SHALL incluir controles visibles para pausar, reanudar y reintentar la sesión desde la propia ventana.

#### Scenario: El usuario pausa
- **WHEN** el usuario pausa la herramienta desde la ventana
- **THEN** el sistema SHALL dejar de capturar y dejar de consumir proveedor mientras conserva el historial visible

#### Scenario: El usuario pulsa reset tras un error
- **WHEN** la herramienta está en estado de error y el usuario pulsa reset
- **THEN** el sistema SHALL reintentar la conexión sin perder el historial ya mostrado

### Requirement: Traducción inicial al español
La primera iteración SHALL priorizar la traducción en vivo al español del audio que entra por los altavoces del sistema.

#### Scenario: Audio en inglés
- **WHEN** el sistema captura una conversación o contenido hablado en inglés
- **THEN** la ventana SHALL mostrar el resultado traducido al español de forma progresiva

### Requirement: Historial con marcas temporales y speaker best effort
La herramienta SHALL acumular los segmentos traducidos en una vista con scroll, incluyendo marcas temporales y separación de speakers cuando sea posible sin bloquear la funcionalidad principal.

#### Scenario: La sesión acumula varios segmentos
- **WHEN** la traducción lleva varios fragmentos ya emitidos
- **THEN** la ventana SHALL conservarlos en una vista desplazable

#### Scenario: El pipeline permite identificar speakers
- **WHEN** el backend puede separar voces con coste aceptable
- **THEN** la interfaz SHALL etiquetar los bloques con identificadores aproximados como `[voz 1]`
