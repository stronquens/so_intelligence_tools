# Proposal

## Title

Harden Linux desktop shortcuts and startup integration

## Why

Los atajos GNOME dejaron de funcionar de forma intermitente por una combinacion de problemas reales:

- `org.gnome.SettingsDaemon.MediaKeys.service` podia quedar inactivo.
- Otro proyecto local podia ocupar `127.0.0.1:8000`.
- GNOME ejecutaba shortcuts desde `$HOME`, por lo que la CLI no cargaba `.env` del proyecto.
- `systemd EnvironmentFile=.env` no era seguro con valores de atajos como `<Primary><Alt>c`.

## Scope

- Mover la API diaria de escritorio a `127.0.0.1:8010`.
- Hacer host/puerto configurables para el servicio de usuario.
- Registrar atajos recomendados `Ctrl + Alt + C` y `Ctrl + Alt + Y`.
- Usar wrappers de diagnostico para los shortcuts GNOME.
- Crear un autostart de salud para refrescar `MediaKeys` y reaplicar atajos tras login.
- Actualizar documentacion y specs vivas.

## Out Of Scope

- Sustituir GNOME custom shortcuts por un daemon propio.
- Implementar una UI de ajustes para cambiar atajos.
- Soportar oficialmente otros escritorios Linux en esta iteracion.
