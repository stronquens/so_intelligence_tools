## MODIFIED Requirements

### Requirement: Aplicacion Electron + Vue.js
La interfaz SHALL estar implementada como aplicacion de escritorio con Electron y Vue.js.

#### Scenario: Arranque de la aplicacion con datos mock
- **WHEN** el usuario lance la app Electron/Vue durante esta fase inicial
- **THEN** el sistema SHALL abrir una ventana de escritorio o render web de desarrollo con Vue.js
- **AND** SHALL poder mostrar datos mock de transcripcion/traduccion sin requerir una sesion real activa

#### Scenario: Convivencia con la ventana actual
- **WHEN** se implemente la primera version de esta capability
- **THEN** la UI Electron/Vue SHALL convivir como alternativa separada
- **AND** SHALL evitar eliminar la ventana `tkinter` hasta que la conexion real con Python quede validada

### Requirement: Contrato de eventos con Python
La UI SHALL comunicarse con el backend Python mediante un contrato estable de eventos y comandos.

#### Scenario: Bridge inicial mockeado
- **WHEN** la UI Electron/Vue se use antes de conectar el controlador Python real
- **THEN** SHALL exponer tipos `UiEvent` y `UiCommand` compatibles con la spec base
- **AND** SHALL permitir enviar comandos desde Vue al proceso principal de Electron mediante preload seguro
- **AND** MAY responder con un bridge mock mientras el transporte real este pendiente

### Requirement: Validacion de la UI y del contrato
La implementacion futura SHALL validar por separado el contrato Python/UI, el render frontend y la integracion con el flujo real.

#### Scenario: Validacion visual inicial
- **WHEN** la interfaz Electron/Vue este disponible con datos mock
- **THEN** SHALL poder capturarse una screenshot local para revisar layout, sidebar, burbujas EN/ES y controles
- **AND** SHALL completar tests frontend y build de escritorio sin errores
