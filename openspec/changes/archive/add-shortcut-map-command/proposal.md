## Why

Los atajos del proyecto han crecido por varias rutas: variables `.env`, defaults Python, instaladores GNOME, listeners Windows y settings del overlay Electron. Esto hace dificil saber que combinacion levanta cada funcionalidad en cada sistema operativo.

## What Changes

- Anadir un mapa central de atajos operativos que lea `ToolRunnerSettings`.
- Exponer un comando CLI para listar los atajos efectivos por plataforma.
- Documentar que variables `.env` controlan cada atajo y que diferencias existen entre Linux/GNOME, Windows y los settings visuales del overlay.
- Mantener `.env` como mecanismo de configuracion operativa para los listeners Python existentes.

## Capabilities

### Modified Capabilities

- `keyboard-shortcuts`: anade introspeccion documentada de atajos por plataforma.
- `overlay-settings`: aclara la diferencia entre atajos visibles/configurables en el overlay y atajos registrados por el sistema operativo.

## Impact

- Afecta CLI Python, documentacion y specs.
- No cambia combinaciones por defecto ni instala nuevos atajos.
- No hace live reload de listeners ya arrancados; si se cambia `.env`, los procesos de listeners deben reiniciarse.
