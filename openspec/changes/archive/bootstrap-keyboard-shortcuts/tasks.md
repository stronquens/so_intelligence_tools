## 1. Contrato y alcance

- [x] 1.1 Confirmar en la delta spec que la primera iteración conecta un atajo con `selected-text-correction`
- [x] 1.2 Definir el registro de acciones y el contrato del listener
- [x] 1.3 Documentar el alcance Linux-first y las limitaciones operativas de X11/Wayland

## 2. Implementación

- [x] 2.1 Añadir soporte de shortcut global en la capa Python
- [x] 2.2 Implementar un registry de acciones por capability
- [x] 2.3 Implementar la acción que dispara la corrección de texto seleccionado
- [x] 2.4 Mejorar los adapters Linux de selección e inserción para funcionar con el escritorio real
- [x] 2.5 Exponer un entrypoint CLI o servicio para escuchar atajos

## 3. Validación

- [x] 3.1 Añadir tests automatizados del registry y del listener
- [x] 3.2 Añadir tests automatizados de los adapters Linux aislando comandos externos
- [x] 3.3 Validar al menos el flujo de corrección textual disparado por shortcut o por acción equivalente dentro del alcance soportado
- [x] 3.4 Registrar evidencia y límites conocidos en `validation.md`
