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
- registra los atajos nativos de GNOME
- deja un servicio `systemd --user` preparado para arrancar la API local al iniciar sesion
- crea un autostart de GNOME para refrescar `MediaKeys` y reaplicar atajos tras login

El servicio puede arrancar con proveedor local `ollama` o con proveedor remoto `litellm_proxy`, segun el `.env` activo.

## Dependencias de sistema

El instalador `scripts/install-linux-deps.sh` instala:

- `curl`
- `libnotify-bin`
- `pulseaudio-utils`
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

## LiteLLM Proxy

Si vas a usar un proveedor remoto OpenAI-compatible, configura estas variables en `.env`:

```env
INFERENCE_PROVIDER=litellm_proxy
LITELLM_PROXY_URL=...
LITELLM_VIRTUAL_KEY=...
LITELLM_MODEL=eu/tensorix/deepseek/deepseek-v4-flash
OLLAMA_TIMEOUT_SECONDS=180
```

En la validacion actual del proyecto, `eu/tensorix/deepseek/deepseek-v4-flash` ha respondido correctamente a traves del proxy y ha dado una latencia comparable o mejor que la configuracion local para la correccion de texto seleccionado.

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

## Configuracion recomendada actual

Para uso diario en escritorio, el proyecto usa `8010` en vez de `8000` para evitar conflictos con otros backends locales.

Variables recomendadas:

```env
LOCAL_INFERENCE_API_HOST=127.0.0.1
LOCAL_INFERENCE_API_PORT=8010
LOCAL_INFERENCE_API_BASE_URL=http://127.0.0.1:8010
GNOME_SELECTED_TEXT_CORRECTION_BINDING=<Primary><Alt>c
GNOME_SYSTEM_AUDIO_TRANSLATION_BINDING=<Primary><Alt>y
GNOME_VOICE_TRANSLATION_BINDING=<Primary><Alt>u
```

Atajos actuales:

| Herramienta | Atajo |
| --- | --- |
| Correccion de texto seleccionado | `Ctrl + Alt + C` |
| Traduccion del audio del sistema | `Ctrl + Alt + Y` |
| Traduccion de tu voz con microfono virtual | `Ctrl + Alt + U` |

## Servicio de usuario

El comando:

```bash
poetry run so-intelligence-tools install-linux-desktop-integration
```

crea este servicio:

- `~/.config/systemd/user/so-intelligence-tools-api.service`

Y lo habilita para `default.target`.

El servicio queda apuntando al puerto configurado en `.env`, actualmente `127.0.0.1:8010`.

Si ya tienes un proceso ocupando ese puerto, el instalador no intenta arrancar el servicio en ese momento para evitar conflicto, pero lo deja habilitado para el siguiente login.

El unit no usa `EnvironmentFile=.env` deliberadamente. `systemd` no acepta bien algunos valores de `.env` con caracteres de atajos como `<Primary><Alt>c`; en su lugar, el proceso Python lee `.env` desde el `WorkingDirectory`.

## Autostart de salud de escritorio

El mismo comando crea:

- `~/.config/autostart/so-intelligence-tools-desktop-health.desktop`

Este autostart ejecuta:

- `scripts/ensure-linux-desktop-integration.sh`

Al iniciar sesion, el script:

- arranca `so-intelligence-tools-api.service` si no esta activo
- refresca `org.gnome.SettingsDaemon.MediaKeys.target`
- reinstala los atajos de GNOME usando wrappers de diagnostico

Log:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/desktop_health.log
```

## Wrappers de atajos

Los atajos de GNOME no ejecutan directamente la CLI, sino wrappers dentro del repo:

- `scripts/run-selected-text-correction-debug.sh`
- `scripts/run-system-audio-translation-debug.sh`

La traduccion de voz usa de momento el comando directo de la CLI y no un wrapper de diagnostico dedicado.

Esto permite:

- ejecutar desde el directorio correcto del proyecto
- cargar `.env` correctamente a traves de Pydantic
- escribir logs antes de entrar en Python
- diagnosticar si GNOME invoco o no el atajo

Logs:

```bash
tail -n 120 ~/.cache/so_intelligence_tools/selected_text_correction.log
tail -n 120 ~/.cache/so_intelligence_tools/system_audio_shortcut.log
tail -n 120 ~/.cache/so_intelligence_tools/voice_translation_logs/*.log
```

## Microfono virtual con traduccion de voz

Para probar la traduccion de tu voz en castellano hacia audio hablado en ingles:

```bash
poetry run so-intelligence-tools run-voice-translation-virtual-mic-toggle
```

Tambien puedes abrir la app de traduccion del audio del sistema y usar el boton `Activar mi voz traducida`:

```bash
poetry run so-intelligence-tools run-system-audio-translation-toggle
```

Ese boton arranca y detiene el microfono virtual sin cerrar la traduccion de altavoces.

La herramienta crea una fuente de entrada virtual de PulseAudio llamada:

```text
so_ai_translated_mic
```

Selecciona esa fuente como microfono en la aplicacion de llamada y deja tu altavoz normal como salida. Para detener la sesion, ejecuta el mismo comando otra vez o pulsa `Ctrl+C` en el terminal que mantiene viva la sesion.

Variables principales:

```env
OPENAI_API_KEY=...
VOICE_TRANSLATION_SOURCE_LANGUAGE=Spanish
VOICE_TRANSLATION_TARGET_LANGUAGE=English
VOICE_TRANSLATION_OPENAI_MODEL=gpt-realtime-translate
VOICE_TRANSLATION_VOICE=marin
VOICE_TRANSLATION_PHYSICAL_SOURCE=alsa_input.usb-046d_C922_Pro_Stream_Webcam_719B22BF-02.analog-stereo
VOICE_TRANSLATION_PASSTHROUGH_VOLUME=1.0
VOICE_TRANSLATION_DUCKED_PASSTHROUGH_VOLUME=0.03
VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME=0.12
VOICE_TRANSLATION_OUTPUT_VOLUME=0.75
VOICE_TRANSLATION_VIRTUAL_SINK_NAME=so_ai_translated_mic
```

Aunque la variable conserva el nombre `VIRTUAL_SINK` por compatibilidad, este valor es el nombre del microfono que debes seleccionar. El sink interno de mezcla se deriva automaticamente.
El volumen ducked queda limitado por `VOICE_TRANSLATION_MAX_DUCKED_PASSTHROUGH_VOLUME` para evitar que la voz original se cuele demasiado alta durante la traduccion.

Instalar atajo:

```bash
poetry run so-intelligence-tools install-gnome-voice-translation-shortcut
```

## Desarrollo vs uso diario

### Desarrollo

Usa:

```bash
poetry run uvicorn --app-dir src local_inference_api.main:app --host 127.0.0.1 --port 8010
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
systemctl --user status org.gnome.SettingsDaemon.MediaKeys.service
curl http://127.0.0.1:8010/health
```

Parar servicio:

```bash
systemctl --user stop so-intelligence-tools-api.service
```

Reparar atajos GNOME sin reiniciar:

```bash
systemctl --user restart org.gnome.SettingsDaemon.MediaKeys.target
poetry run so-intelligence-tools install-linux-desktop-integration --debug-shortcut
```
