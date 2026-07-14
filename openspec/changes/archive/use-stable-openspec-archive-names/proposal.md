## Why

Los changes archivados mezclan nombres estables con directorios prefijados por fecha. La fecha en la ruta fragmenta la convención, dificulta las referencias duraderas y permite que un mismo change termine archivado varias veces bajo nombres distintos.

## What Changes

- Adoptar `openspec/changes/archive/<change-name>/` como ruta canónica, sin fecha.
- Migrar los archivos existentes con fecha conservando íntegramente sus artifacts y evidencia.
- Detectar colisiones por nombre antes de archivar o migrar; consolidar solo duplicados reales y no mezclar changes históricos distintos.
- Actualizar el workflow local de archivado y la documentación que contiene rutas fechadas.

## Capabilities

### New Capabilities

- `openspec-change-lifecycle`: Convenciones de identidad, archivado, colisiones y conservación de changes OpenSpec.

### Modified Capabilities

Ninguna.

## Impact

Afecta a las rutas bajo `openspec/changes/archive/`, al skill local `openspec-archive-change`, a la guía del repositorio y a referencias documentales hacia artifacts archivados. No cambia el comportamiento de producto ni las APIs de ejecución.
