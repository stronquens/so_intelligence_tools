# Proposal

## Summary

Crear la base reusable de `python-tool-runners` como capa de aplicación Python que conecte:

- casos de uso del producto
- API local de inferencia
- adapters del sistema operativo
- entrypoints CLI finos

La primera iteración se centrará en flujos batch de texto e imagen, con foco principal en preparar el terreno para `selected-text-correction` y `screenshot-text-extraction`.

## Why

Tras cerrar `local-inference-api`, el siguiente cuello de botella del proyecto no es el modelo sino la falta de una capa Python reusable para:

- invocar el backend local con un contrato estable
- coordinar operaciones del sistema operativo sin acoplar toda la lógica a Linux
- compartir manejo de errores, configuración y logging entre herramientas futuras

Si saltamos directamente a herramientas visibles sin esta base, el código tenderá a fragmentarse en scripts ad hoc difíciles de portar, probar y mantener.

## Scope

### In scope

- crear el armazón de `python-tool-runners` dentro de `src/`
- definir arquitectura por composición con puertos y adapters
- implementar un cliente Python tipado para `local-inference-api`
- implementar puertos base del sistema:
  - selección de texto
  - inserción de texto
  - portapapeles
  - notificaciones
  - captura de imagen
- crear adapters Linux iniciales o stubs controlados para esos puertos
- crear casos de uso batch reutilizables para:
  - corrección textual
  - extracción de texto desde imagen
- exponer al menos entrypoints CLI básicos para validar los flujos
- añadir tests automatizados sobre cliente, casos de uso y adapters simulados

### Out of scope

- audio batch o streaming
- procesos residentes o daemons persistentes
- registro de atajos globales
- overlay gráfico
- micrófono virtual
- integración completa con todas las apps Linux reales

## Expected Outcome

Al final del change deberá existir una base Python que permita implementar herramientas visibles sin rehacer la arquitectura en cada capability.

En concreto, el repositorio deberá ganar:

- un cliente de inferencia estable y reusable
- una capa de puertos del sistema operativo
- una primera implementación Linux para capacidades batch simples
- casos de uso listos para ser consumidos por capabilities superiores
- tests suficientes para validar el contrato de la capa runner sin depender siempre del sistema real

## Risks

- elegir demasiadas abstracciones demasiado pronto
- introducir adapters Linux demasiado frágiles si se intentan resolver todos los casos reales ya
- mezclar lógica de dominio, CLI y sistema operativo en una sola capa

## Mitigations

- limitar la primera iteración a texto e imagen batch
- usar composición e interfaces pequeñas en vez de jerarquías profundas de herencia
- tratar Linux real como adapter inicial, no como centro del dominio
