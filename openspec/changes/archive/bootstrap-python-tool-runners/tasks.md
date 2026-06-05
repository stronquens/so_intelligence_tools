## 1. Contrato y arquitectura

- [x] 1.1 Confirmar en la delta spec que la primera iteración cubre solo runners batch de texto e imagen
- [x] 1.2 Definir la estructura inicial de carpetas para la capa runner
- [x] 1.3 Definir puertos mínimos y modelo de errores del dominio
- [x] 1.4 Definir la estrategia de inyección de dependencias por composición y factories

## 2. Cliente de inferencia

- [x] 2.1 Implementar un cliente Python tipado para `local-inference-api`
- [x] 2.2 Gestionar timeouts, errores de conexión y parsing de respuestas
- [x] 2.3 Aislar configuración y defaults del cliente en settings reutilizables

## 3. Puertos y adapters

- [x] 3.1 Crear interfaces base para selección, inserción, portapapeles, notificaciones y captura
- [x] 3.2 Implementar adapters Linux iniciales o stubs controlados para los puertos batch
- [x] 3.3 Crear fakes o adapters de testing para pruebas automatizadas

## 4. Casos de uso y entrypoints

- [x] 4.1 Implementar un caso de uso reusable para corrección textual
- [x] 4.2 Implementar un caso de uso reusable para extracción de texto desde imagen
- [x] 4.3 Crear entrypoints CLI finos para validar ambos flujos
- [x] 4.4 Asegurar feedback claro ante errores operativos frecuentes

## 5. Validación

- [x] 5.1 Añadir tests automatizados del cliente de inferencia
- [x] 5.2 Añadir tests automatizados de casos de uso con adapters falsos
- [x] 5.3 Validar al menos un flujo batch textual de extremo a extremo dentro del alcance del change
- [x] 5.4 Registrar evidencia y límites conocidos en `validation.md`
