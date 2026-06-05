## 1. Contrato y alcance

- [x] 1.1 Confirmar en la delta spec que la primera iteración cubre solo texto e imagen en modo batch
- [x] 1.2 Cerrar el contrato inicial de endpoints, payloads y respuestas del API local
- [x] 1.3 Definir el contrato de `reasoning_mode` y su mapeo inicial a perfiles rápido e inteligente
- [x] 1.4 Cerrar la compatibilidad OpenAI del formato de respuesta y el uso de `multipart/form-data` para inputs de archivo

## 2. Servicio base

- [x] 2.1 Crear el scaffold del servicio `local-inference-api`
- [x] 2.2 Inicializar Poetry y asegurar `.venv` dentro del proyecto
- [x] 2.3 Implementar endpoint de healthcheck
- [x] 2.4 Implementar endpoint separado de estado operativo
- [x] 2.5 Implementar capa adaptadora para Ollama aislada del contrato HTTP

## 3. Inferencia batch

- [x] 3.1 Implementar endpoint textual de generación o respuesta
- [x] 3.2 Implementar endpoint de extracción de texto desde imagen
- [x] 3.3 Implementar la resolución interna de `reasoning_mode` dentro del adaptador
- [x] 3.4 Gestionar errores básicos del runtime local y respuestas inválidas

## 4. Despliegue

- [x] 4.1 Añadir configuración `docker compose` para levantar el API local y el runtime local
- [x] 4.2 Permitir encender y apagar la infraestructura de inferencia de forma controlada
- [x] 4.3 Añadir `.env` con las variables de entorno mínimas del stack
- [x] 4.4 Documentar pasos mínimos de arranque, parada y sustitución de modelo

## 5. Validación

- [x] 5.1 Validar `GET /health`
- [x] 5.2 Validar una petición textual real contra el modelo local
- [x] 5.3 Validar una petición con imagen real contra el modelo local
- [x] 5.4 Validar al menos un modo rápido y un modo inteligente
- [x] 5.5 Validar el ciclo de arranque y parada de los contenedores
- [x] 5.6 Validar el formato de respuesta OpenAI-compatible dentro del alcance soportado
- [x] 5.7 Registrar resultados y límites conocidos en `validation.md`
- [x] 5.8 Añadir tests automatizados en Python para cubrir endpoints, errores básicos y lógica interna crítica
