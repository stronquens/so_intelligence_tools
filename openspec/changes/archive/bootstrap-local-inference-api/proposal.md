## Why

La primera capability del proyecto es el cimiento de casi todo lo demás. Sin un servicio local de inferencia bien definido y fácil de levantar, el resto de herramientas del sistema quedan bloqueadas o forzadas a trabajar contra prototipos inestables.

Esta primera iteración debe convertir la idea de "modelo local detrás de una API" en una base concreta: un servicio HTTP local, desplegable con Docker, con integración real con Ollama y con una superficie mínima útil para texto e imagen.

## What Changes

- Crear la primera iteración del servicio `local-inference-api`.
- Definir una API HTTP local simple y estable para peticiones de texto e imagen, con respuestas OpenAI-compatible dentro del alcance soportado.
- Integrar el servicio con Ollama como runtime de modelo local.
- Introducir un control de perfil de razonamiento para distinguir entre modo rápido y modo más inteligente.
- Preparar despliegue con Docker Compose y `.env` para facilitar instalación y aislamiento.
- Preparar la base Python del backend con Poetry y `.venv` local dentro del repo.
- Fijar `Gemma 4 E2B Unsloth UD-Q4_K_XL` como runtime inicial validado para CPU-only.
- Dejar el runtime local desplegado de forma que pueda encenderse, apagarse o sustituirse fácilmente.
- Acotar la primera iteración a tareas no streaming.

## Capabilities

### New Capabilities

### Modified Capabilities

- `local-inference-api`: pasa de spec base a una primera iteración implementable, centrada en inferencia batch para texto e imagen sobre una API local.
  Además, introduce un contrato inicial para elegir entre respuestas rápidas y respuestas con más deliberación.

## Impact

- Código nuevo esperado:
  - servicio backend del API local
  - cliente interno para Ollama
  - bootstrap de proyecto Python con Poetry
  - configuración Docker Compose para API y runtimes locales
  - archivo `.env` para configuración mínima
- Spec afectada:
  - `openspec/specs/local-inference-api/spec.md`
- Documentación afectada:
  - guía de arranque local
  - guía de encendido, apagado y sustitución de contenedores
  - variables de entorno mínimas
- No incluye aún:
  - audio streaming
  - traducción en tiempo real
  - routing avanzado entre varios modelos
