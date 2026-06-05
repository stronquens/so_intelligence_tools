## Context

La spec viva de `python-tool-runners` es deliberadamente amplia. Antes de construir tools visibles del sistema necesitamos una base de aplicación que:

- no se acople al runtime interno del modelo
- no incruste dependencias Linux por todo el código
- no obligue a reescribir el manejo de errores, configuración y logging para cada herramienta

La primera iteración de esta capability debe comportarse como un bootstrap arquitectónico, no como una colección de scripts finales.

## Goals / Non-Goals

**Goals**

- crear una base reusable para futuras tools del sistema
- desacoplar la lógica de aplicación del backend y del sistema operativo
- permitir que Linux sea el primer target sin cerrarnos a otros sistemas
- dejar una experiencia de ejecución simple mediante CLIs finos
- dar soporte directo a flujos batch de texto e imagen

**Non-Goals**

- resolver ya toda la complejidad de integración real con cada app del escritorio
- soportar audio, streaming o procesos persistentes
- diseñar un framework interno excesivamente abstracto

## Decisions

Usar arquitectura por composición en lugar de herencia profunda.
Motivo: los flujos del proyecto combinan IO, llamadas HTTP y acciones del sistema operativo. En este terreno, la composición con interfaces pequeñas permite sustituir adapters con menos rigidez que una jerarquía de clases base.
Alternativas consideradas: sistema centrado en herencia. Se descarta como enfoque principal porque aumenta el acoplamiento y complica la evolución entre sistemas operativos.

Dividir la capa runner en `application`, `ports`, `adapters`, `infrastructure` y `cli`.
Motivo: hace explícita la frontera entre lógica de negocio, contratos y detalles del entorno.
Alternativas consideradas: scripts planos o una sola carpeta de utilidades. Se descartan porque mezclarían demasiadas responsabilidades.

Crear un `InferenceClient` tipado como dependencia reusable.
Motivo: la capability 1 ya expone un backend estable; ahora hace falta una capa cliente que oculte payloads, parsing y errores.
Alternativas consideradas: hacer `httpx` directo desde cada herramienta. Se descarta porque duplicaría contrato y manejo de errores.

Modelar el acceso al sistema operativo con puertos explícitos.
Motivo: operaciones como leer selección, insertar texto o lanzar notificaciones son dependencias externas y deben poder sustituirse.
Alternativas consideradas: llamar utilidades Linux directamente desde los casos de uso. Se descarta porque rompería la portabilidad y la testabilidad.

Introducir entrypoints CLI finos para validación y automatización.
Motivo: permiten probar los casos de uso sin esperar a tener atajos globales u overlay.
Alternativas consideradas: arrancar directamente con un daemon o integraciones permanentes. Se descartan por prematuras.

Limitar la primera iteración a flujos batch de texto e imagen.
Motivo: prepara las siguientes capabilities priorizadas sin introducir desde ya complejidad de audio o streaming.
Alternativas consideradas: incluir audio por anticipado. Se descarta para mantener el bootstrap pequeño y verificable.

## Proposed Architecture

Estructura objetivo inicial:

```text
src/so_intelligence_tools/
  application/
    use_cases/
  domain/
  ports/
  adapters/
    linux/
    testing/
  infrastructure/
    config.py
    logging.py
    inference_client.py
  cli/
```

Notas:

- `application/use_cases/` contendrá flujos como `correct_selected_text` o `extract_text_from_image`
- `ports/` definirá interfaces mínimas y estables
- `adapters/linux/` contendrá implementaciones Linux iniciales
- `adapters/testing/` contendrá fakes útiles para tests
- `infrastructure/inference_client.py` centralizará acceso al API local
- `cli/` solo cableará dependencias y disparará casos de uso

## Ports Recommendation

Puertos mínimos para esta iteración:

- `InferencePort`
- `TextSelectionPort`
- `TextInsertionPort`
- `ClipboardPort`
- `NotificationPort`
- `ScreenshotPort`

Cada puerto debe ser pequeño y centrarse en una responsabilidad observable.

Ejemplo de principio de diseño:

- `TextSelectionPort` lee selección actual o informa ausencia de selección
- `TextInsertionPort` reemplaza o inserta texto en el foco actual
- `NotificationPort` muestra feedback visible al usuario

## Dependency Injection Recommendation

Sí, debe existir inyección de dependencias configurable, pero simple.

Recomendación concreta:

- evitar un contenedor DI complejo
- usar factories o ensambladores explícitos
- decidir adapters por configuración o detección del entorno

Ejemplo:

- `build_linux_runtime()` devuelve un objeto de composición con:
  - cliente de inferencia real
  - adapters Linux reales
  - logger
  - settings

Esto da portabilidad sin introducir demasiado framework interno.

## Error Model Recommendation

Definir errores del dominio o de aplicación claros:

- `NoSelectionError`
- `InferenceUnavailableError`
- `UserCancelledError`
- `UnsupportedEnvironmentError`
- `ToolRunnerConfigurationError`

Los casos de uso no deben decidir cómo se muestran todos los errores; solo deben emitir fallos semánticos claros. El entrypoint CLI o la herramienta superior decidirá si se notifica, loguea o reintenta.

## Linux Integration Recommendation

Para la primera iteración:

- permitir adapters Linux reales cuando el mecanismo sea razonablemente simple y confiable
- usar stubs o implementación controlada cuando una integración real aún no esté cerrada

La meta de este change no es resolver ya toda la automatización del escritorio, sino fijar el esqueleto correcto.

## Validation Strategy

La validación debería mezclar:

- tests unitarios del cliente de inferencia
- tests de casos de uso con adapters falsos
- smoke tests CLI básicos donde tenga sentido

La mayor parte del valor de esta capability está en que el contrato interno sea estable y testeable, no en hacer demos manuales frágiles.

## Open Questions Resolved

`python-tool-runners` debe incluir tanto orquestación como acceso al sistema operativo, pero separados por puertos.

La primera iteración debe producir infraestructura reusable antes que herramientas finales visibles.

La capability debe diseñarse pensando primero en `selected-text-correction`, porque es el primer flujo con mejor relación valor/complejidad.
