## Context

El repositorio contiene archivos OpenSpec creados bajo dos convenciones: nombres estables y nombres `YYYY-MM-DD-<change-name>`. El skill local genera la segunda forma, mientras que varias entradas antiguas ya usan la primera. Las rutas archivadas también se citan desde documentación operativa.

## Goals / Non-Goals

**Goals:**

- Dar a cada change una identidad de ruta estable antes y después del archivado.
- Conservar artifacts, validaciones y evidencia durante la migración.
- Impedir que una colisión se resuelva sobrescribiendo o creando otra copia fechada.
- Corregir referencias y documentar la convención.

**Non-Goals:**

- Fusionar changes distintos solo porque afecten a la misma capability.
- Reescribir el contenido histórico de proposals, designs o validaciones.
- Alterar el formato de las specs de producto.

## Decisions

1. El destino canónico será `archive/<change-name>`. La identidad funcional del change ya está expresada por su nombre; la fecha pertenece al historial de Git y no debe formar parte de la clave de ruta.
2. La migración retirará únicamente un prefijo inicial con forma `YYYY-MM-DD-`. Antes de mover se comprobará que todos los destinos sean únicos y estén libres.
3. Ante una colisión futura, el archivado se detendrá para comparar ambos árboles. Solo se consolidarán si representan el mismo change y sus archivos pueden combinarse sin pérdida; de lo contrario se exigirá un nombre funcional distinto.
4. Se conservarán changes históricos diferentes aunque compartan capability. Una capability puede evolucionar mediante varios changes y fusionarlos reduciría la trazabilidad.

## Risks / Trade-offs

- [Referencias rotas a rutas antiguas] → Buscar y actualizar todas las referencias versionadas, y validar que no quede ningún directorio ni enlace con prefijo de fecha.
- [Pérdida por colisión] → Calcular el mapa completo origen/destino antes de efectuar movimientos y abortar si existe cualquier duplicado.
- [El CLI oficial puede seguir proponiendo fechas] → Mantener la política explícita en el skill local y en la guía del repositorio; el repositorio prevalece sobre el valor por defecto del CLI.

## Migration Plan

1. Inventariar los directorios fechados y comprobar destinos.
2. Renombrarlos mecánicamente sin modificar su contenido.
3. Actualizar el skill, la guía y las referencias documentales.
4. Validar estructura, specs, enlaces y diff de Git.
5. Archivar este mismo change sin fecha, confirmando la nueva convención.

El rollback consiste en revertir el commit, lo que restaura todas las rutas anteriores mediante Git.

## Open Questions

Ninguna.
