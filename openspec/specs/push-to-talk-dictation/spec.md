# Purpose

Definir una herramienta de dictado push-to-talk que grabe audio mientras se mantiene pulsada una combinación de teclas, lo transcriba en local y escriba el texto donde esté el cursor.

## Requirements

### Requirement: Activación mediante combinación de teclas mantenida
El sistema SHALL iniciar el flujo de dictado cuando el usuario pulse una combinación global concreta y mantenerlo activo mientras dicha combinación siga pulsada.

#### Scenario: Inicio de la pulsación
- **WHEN** el usuario pulsa la combinación asignada al dictado
- **THEN** la herramienta SHALL comenzar a grabar audio de inmediato

#### Scenario: Fin de la pulsación
- **WHEN** el usuario deja de pulsar la combinación asignada
- **THEN** la herramienta SHALL detener la grabación y continuar automáticamente con la transcripción

### Requirement: Overlay temporal de estado de grabación
El sistema SHALL mostrar un pequeño overlay visual mientras el dictado esté grabando para indicar claramente que el audio está siendo capturado.

#### Scenario: Grabación en curso
- **WHEN** el flujo de dictado está grabando audio
- **THEN** el sistema SHALL mostrar un overlay discreto con estado de grabación

#### Scenario: Grabación finalizada
- **WHEN** la grabación termina
- **THEN** el overlay SHALL desaparecer sin requerir interacción adicional del usuario

### Requirement: Transcripción automática en local al terminar la grabación
El sistema SHALL enviar automáticamente el audio capturado al modelo local al finalizar la pulsación, sin pasos intermedios manuales.

#### Scenario: Audio capturado correctamente
- **WHEN** el usuario suelta la combinación y existe audio válido
- **THEN** la herramienta SHALL enviar ese audio al backend local para obtener la transcripción

### Requirement: Inserción automática del texto en el foco actual
El sistema SHALL insertar la transcripción resultante directamente en el punto donde el usuario tenga el cursor activo.

#### Scenario: Hay un campo editable con foco
- **WHEN** la transcripción se completa correctamente
- **THEN** el sistema SHALL escribir el texto resultante en la ubicación actual del cursor

### Requirement: Limpieza de audio efímero
El sistema SHALL minimizar la persistencia del audio grabado y eliminar cualquier artefacto temporal al finalizar el flujo.

#### Scenario: Procesamiento completamente en memoria
- **WHEN** la implementación pueda evitar escribir el audio a disco
- **THEN** la herramienta SHALL mantener la grabación solo en memoria

#### Scenario: Archivo temporal inevitable
- **WHEN** la implementación necesite usar un archivo temporal para interoperar con librerías o herramientas del sistema
- **THEN** dicho archivo SHALL eliminarse automáticamente en cuanto termine la transcripción

### Requirement: Feedback claro ante fallos o grabación vacía
El sistema SHALL evitar comportamientos silenciosos cuando no haya audio útil o cuando la transcripción no pueda completarse.

#### Scenario: No se capturó audio utilizable
- **WHEN** el usuario dispara el flujo pero no queda audio válido para transcribir
- **THEN** el sistema SHALL mostrar una notificación o feedback equivalente indicando que no se pudo generar texto

#### Scenario: El backend local falla
- **WHEN** la grabación termina pero el backend local no devuelve una transcripción válida
- **THEN** el sistema SHALL informar del fallo y no insertar texto parcial o corrupto
