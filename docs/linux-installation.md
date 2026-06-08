# Instalacion Linux

## Objetivo

Dejar `so_intelligence_tools` operativo en un equipo Linux con el menor numero posible de pasos manuales.

## Flujo recomendado

### Opcion corta

```bash
make install-system-deps
poetry install
poetry run so-intelligence-tools install-linux-desktop-integration
```

### Opcion de bootstrap

```bash
make bootstrap-linux
```

Este flujo:

- instala dependencias de sistema para Ubuntu/Debian
- instala Ollama si no esta presente
- instala dependencias Python en `.venv`
- registra el atajo nativo de GNOME
- deja un servicio `systemd --user` preparado para arrancar la API local al iniciar sesion

## Dependencias de sistema

El instalador `scripts/install-linux-deps.sh` instala:

- `curl`
- `libnotify-bin`
- `wl-clipboard`
- `wtype`
- `xclip`
- `xdotool`
- `ydotool`
- `ydotoold`

## Ollama

Si Ollama no esta instalado, el script usa el instalador oficial.

Despues de instalarlo, descarga el modelo inicial validado:

```bash
ollama pull gemma4:e2b-it-qat
```

El backend mantiene el modelo cargado con `OLLAMA_KEEP_ALIVE=10m`. Para flujos interactivos como `selected-text-correction`, las peticiones con `reasoning_mode=off|low` fuerzan `think: false` en Ollama para obtener texto final inmediato.

## Sesion recomendada

En Ubuntu 22.04 con GNOME, la sesion mas fiable para `selected-text-correction` es:

- `Ubuntu on Xorg`

Puedes verificarla con:

```bash
echo $XDG_SESSION_TYPE
```

Debe devolver:

```bash
x11
```

En esta sesion `X11`, la implementacion estable usa:

- lectura del texto seleccionado desde la seleccion primaria `PRIMARY`
- pegado del texto corregido desde el portapapeles

## Servicio de usuario

El comando:

```bash
poetry run so-intelligence-tools install-linux-desktop-integration
```

crea este servicio:

- `~/.config/systemd/user/so-intelligence-tools-api.service`

Y lo habilita para `default.target`.

Si ya tienes un `uvicorn` manual ocupando `127.0.0.1:8000`, el instalador no intenta arrancar el servicio en ese momento para evitar conflicto, pero lo deja habilitado para el siguiente login.

## Desarrollo vs uso diario

### Desarrollo

Usa:

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8000
```

### Uso diario

Usa el servicio de usuario y no levantes `uvicorn` manualmente a la vez.

## Comandos utiles

Arrancar servicio manualmente:

```bash
systemctl --user start so-intelligence-tools-api.service
```

Ver estado:

```bash
systemctl --user status so-intelligence-tools-api.service
```

Parar servicio:

```bash
systemctl --user stop so-intelligence-tools-api.service
```
