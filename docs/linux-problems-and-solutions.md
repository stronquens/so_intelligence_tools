# Problemas y Soluciones en Linux

## Contexto

Este documento resume los problemas reales encontrados al integrar `selected-text-correction` con Linux y las soluciones aplicadas en el proyecto.

## 1. En Wayland se insertaba solo una `v`

### Sintoma

Al pulsar el atajo, el texto seleccionado se reemplazaba por una `v` o hacia un pequeno parpadeo sin pegar el resultado.

### Causa

La primera implementacion usaba `xdotool` para simular `Ctrl+V`. En GNOME Wayland eso no es fiable.

### Solucion aplicada

- separar comportamiento `x11` y `wayland`
- dejar de usar `xdotool` como camino principal en Wayland
- anadir rutas especificas para `wl-clipboard`, `wtype` y `ydotool`

## 2. `wtype` no funcionaba en GNOME Wayland

### Sintoma

El log mostraba:

```text
Compositor does not support the virtual keyboard protocol
```

### Causa

El compositor GNOME 42 del equipo no expone el protocolo virtual keyboard requerido por `wtype`.

### Solucion aplicada

- anadir fallback a `ydotool` y `ydotoold`
- registrar esta limitacion en la documentacion y en la validacion del change

## 3. `ydotool` usaba un socket incorrecto

### Sintoma

El wrapper arrancaba con:

```text
YDOTOOL_SOCKET=/run/user/<uid>/.ydotool_socket
```

pero en Ubuntu 22.04 el daemon empaquetado trabajaba con:

```text
/tmp/.ydotool_socket
```

### Causa

El entorno heredado del atajo y la version empaquetada de `ydotoold` no coincidian.

### Solucion aplicada

- forzar `YDOTOOL_SOCKET=/tmp/.ydotool_socket` en el wrapper
- forzar el mismo socket en el adapter Python si detecta uno heredado que no existe

## 4. `ydotoold` levantaba el socket con permisos de `root`

### Sintoma

`ydotool` no podia usar el backend aunque el daemon parecia arrancado.

### Causa

El socket quedaba con permisos no utilizables para el usuario actual.

### Solucion aplicada

- crear `scripts/start-wayland-keyboard-backend.sh`
- reiniciar `ydotoold`
- recrear el socket
- ajustar propietario y permisos para el usuario actual

## 5. La captura de seleccion podia reutilizar portapapeles viejo

### Sintoma

Parecia que el sistema corregia y volvia a insertar el mismo texto o un texto antiguo.

### Causa

Si el copy fallaba, el flujo podia leer contenido stale del portapapeles.

### Solucion aplicada

- usar un `sentinel` temporal en el portapapeles
- si tras el copy el contenido sigue siendo el `sentinel`, tratarlo como seleccion invalida

## 6. El LLM funcionaba, pero el reemplazo final fallaba

### Sintoma

El log mostraba texto capturado y texto corregido correctamente, pero el texto no se sustituia en pantalla.

### Causa

La parte fallida ya no era inferencia sino inyeccion de teclado o pegado.

### Solucion aplicada

- anadir log de debug con:
  - texto seleccionado
  - texto corregido
  - estado del healthcheck
- anadir fallback a portapapeles cuando la insercion automatica falla

## 7. Tras cambiar a X11 seguia usando `wl-copy`

### Sintoma

Despues de reiniciar en `x11`, el flujo fallaba intentando conectarse a Wayland.

### Causa

La deteccion elegia `wl-copy` y `wl-paste` solo por estar instalados, aunque la sesion ya no era Wayland.

### Solucion aplicada

- hacer que `LinuxClipboardAdapter` priorice `xclip` en `x11`
- mantener `wl-copy` y `wl-paste` solo para sesiones `wayland`

## 8. El servicio `systemd --user` chocaba con `uvicorn` manual

### Sintoma

El servicio de usuario entraba en restart loop con error de puerto ocupado.

### Causa

El backend ya estaba levantado manualmente en `127.0.0.1:8000`.

### Solucion aplicada

- mejorar el instalador para detectar si el puerto `8000` ya esta ocupado
- si lo esta, habilitar el servicio para el siguiente login sin arrancarlo en ese momento
- mover la instalacion de escritorio diaria a `127.0.0.1:8010` para evitar colisiones con otros proyectos locales
- mantener Docker en `8000` porque `docker-compose.yml` publica ese puerto explicitamente

## 9. Gemma 4 QAT podia devolver thinking en vez de texto final

### Sintoma

La API recibia la peticion y Ollama mostraba actividad, pero la herramienta podia terminar sin texto util para insertar.

### Causa

Con `gemma4:e2b-it-qat`, Ollama puede entrar en modo thinking si no se le marca lo contrario de forma explicita en peticiones instantaneas.

### Solucion aplicada

- mantener `reasoning_mode` como contrato publico
- enviar `think: false` cuando `reasoning_mode` es `off` o `low`
- enviar `think: true` cuando `reasoning_mode` es `medium` o `high`
- mantener `OLLAMA_KEEP_ALIVE=10m` para que el modelo siga caliente entre atajos

## 10. Restaurar el portapapeles demasiado pronto rompia el pegado en X11

### Sintoma

El texto seleccionado desaparecia, la inferencia se completaba, pero el resultado no llegaba a verse pegado.

### Causa

La aplicacion activa podia recibir `Ctrl+V` antes de haber consumido realmente el contenido nuevo del portapapeles si este se restauraba inmediatamente.

### Solucion aplicada

- en `X11`, dejar el texto corregido en el portapapeles despues del pegado
- leer la seleccion desde `PRIMARY`
- usar el portapapeles como via estable de reemplazo

## 11. Otro proyecto ocupaba `127.0.0.1:8000`

### Sintoma

`Ctrl + Alt + C` capturaba texto pero no completaba la correccion. La llamada a `/v1/text/generate` devolvia `404`.

### Causa

El puerto `8000` estaba ocupado por otro backend local de otro proyecto. `/health` respondia, pero no era `local-inference-api` de `so_intelligence_tools`.

### Solucion aplicada

- configurar el backend de escritorio en `127.0.0.1:8010`
- configurar `LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010`
- hacer que el instalador `systemd --user` use `LOCAL_INFERENCE_API_HOST` y `LOCAL_INFERENCE_API_PORT`
- actualizar wrappers y documentacion para usar `8010`

Comprobacion:

```bash
ss -ltnp '( sport = :8000 or sport = :8010 )'
curl http://127.0.0.1:8010/status
```

## 12. GNOME dejo de ejecutar todos los atajos

### Sintoma

Al pulsar fisicamente los atajos no ocurria nada y los logs de wrappers no crecian.

### Causa

El proceso `gsd-media-keys` estaba muerto. Ese proceso pertenece a `org.gnome.SettingsDaemon.MediaKeys.service` y es quien ejecuta los custom shortcuts de GNOME.

### Solucion aplicada

- reiniciar el target correcto:

```bash
systemctl --user restart org.gnome.SettingsDaemon.MediaKeys.target
```

- anadir autostart de salud:

```text
~/.config/autostart/so-intelligence-tools-desktop-health.desktop
```

- el autostart ejecuta `scripts/ensure-linux-desktop-integration.sh`, que refresca `MediaKeys` y reinstala los atajos tras login

Comprobacion:

```bash
systemctl --user status org.gnome.SettingsDaemon.MediaKeys.service
tail -n 120 ~/.cache/so_intelligence_tools/desktop_health.log
```

## 13. Los wrappers se ejecutaban desde `$HOME` y no cargaban `.env`

### Sintoma

El atajo de audio si invocaba el wrapper, pero el comando caia al modo `chunked` y mostraba:

```text
Falta configurar el backend remoto de transcripcion de audio. Revisa `.env`.
```

### Causa

GNOME ejecuta los custom shortcuts con `pwd=/home/sciling`. Como Pydantic lee `.env` desde el directorio actual, la CLI arrancaba con defaults en vez de la configuracion del proyecto.

### Solucion aplicada

- los wrappers hacen `cd "$PROJECT_DIR"` antes de ejecutar la CLI
- los wrappers escriben logs inmediatos para confirmar si GNOME invoco el atajo
- se evito `source .env` en bash porque valores como `<Primary><Alt>c` no son shell-valid sin comillas

Logs:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/selected_text_correction.log
tail -n 120 ~/.cache/so_intelligence_tools/system_audio_shortcut.log
```

## Recomendacion actual

Para Ubuntu 22.04 con GNOME:

- usar `Ubuntu on Xorg` para la experiencia mas estable
- usar Wayland con fallback a portapapeles solo como compatibilidad parcial
- usar `Ctrl + Alt + C` para correccion de texto seleccionado
- usar `Ctrl + Alt + Y` para traduccion de audio del sistema
- mantener la API de escritorio en `127.0.0.1:8010`
- si los atajos dejan de responder, reiniciar `org.gnome.SettingsDaemon.MediaKeys.target`
