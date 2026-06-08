#!/usr/bin/env bash
set -euo pipefail

SOCKET="/tmp/.ydotool_socket"

if ! command -v ydotool >/dev/null 2>&1 || ! command -v ydotoold >/dev/null 2>&1; then
  printf 'ydotool/ydotoold no están instalados. Ejecuta: sudo apt-get install -y ydotool ydotoold\n' >&2
  exit 1
fi

if pgrep -x ydotoold >/dev/null 2>&1; then
  printf 'Parando ydotoold anterior para recrear el socket con permisos correctos.\n'
  sudo pkill -x ydotoold || true
  sleep 0.2
fi

sudo rm -f "$SOCKET"
printf 'Arrancando ydotoold. Esta versión de Ubuntu usa el socket fijo %s\n' "$SOCKET"
sudo -b ydotoold

for _ in $(seq 1 20); do
  [[ -S "$SOCKET" ]] && break
  sleep 0.1
done

if [[ ! -S "$SOCKET" ]]; then
  printf 'No se creó el socket de ydotoold en %s\n' "$SOCKET" >&2
  exit 1
fi

sudo chown "$(id -u):$(id -g)" "$SOCKET"
sudo chmod 660 "$SOCKET"

printf 'ydotoold listo en %s\n' "$SOCKET"
printf 'El atajo usará este socket automáticamente.\n'
