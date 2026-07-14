## Context

`ToolRunnerSettings` ya contiene la mayor parte de atajos operativos: GNOME, Windows, dictado y acciones de audio. La UI Electron tiene su propio `desktop-settings.json`; algunos valores son visuales o futuros y no necesariamente estan conectados a listeners globales reales.

## Decisions

- Crear un modulo Python pequeno `infrastructure/shortcut_map.py` que devuelva entradas estructuradas con feature, plataforma, shortcut efectivo, variable de entorno, mecanismo y estado.
- Anadir `so-intelligence-tools show-shortcuts` para imprimir una tabla legible.
- Mostrar por defecto todas las plataformas soportadas y permitir `--platform linux|windows|desktop`.
- No introducir un nuevo archivo de settings como fuente de verdad en esta iteracion. Usar `.env` evita duplicacion y encaja con la configuracion existente.
- Documentar los settings del overlay como "UI/desktop settings" separados de los atajos OS registrados.

## Risks / Trade-offs

- Algunos atajos Electron aun no ejecutan herramientas reales. El mapa debe marcarlos como `ui-setting` o `planned`, no como activos.
- Los valores efectivos dependen de procesos ya arrancados: cambiar `.env` no reconfigura listeners activos hasta reiniciarlos.
- GNOME usa sintaxis tipo `<Primary><Alt>c`; los listeners Python usan sintaxis tipo `<ctrl>+<alt>+d`. El mapa debe mostrar la sintaxis real esperada por cada mecanismo.
