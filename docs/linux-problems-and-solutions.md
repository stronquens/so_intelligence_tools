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

## Recomendacion actual

Para Ubuntu 22.04 con GNOME:

- usar `Ubuntu on Xorg` para la experiencia mas estable
- usar Wayland con fallback a portapapeles solo como compatibilidad parcial
