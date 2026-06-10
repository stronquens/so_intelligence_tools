#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo --preserve-env=PATH,INSTALL_OLLAMA,SKIP_OLLAMA "$0" "$@"
fi

if ! command -v apt-get >/dev/null 2>&1; then
  printf 'Este instalador por ahora soporta sistemas basados en apt (Ubuntu/Debian).\n' >&2
  exit 1
fi

INSTALL_OLLAMA="${INSTALL_OLLAMA:-1}"
SKIP_OLLAMA="${SKIP_OLLAMA:-0}"

printf 'Actualizando indice de paquetes...\n'
apt-get update

printf 'Instalando dependencias de escritorio Linux...\n'
apt-get install -y \
  curl \
  libnotify-bin \
  pulseaudio-utils \
  wl-clipboard \
  wtype \
  xclip \
  xdotool \
  ydotool \
  ydotoold

if [[ "$SKIP_OLLAMA" == "1" ]]; then
  printf 'Saltando instalacion de Ollama por configuracion.\n'
  exit 0
fi

if command -v ollama >/dev/null 2>&1; then
  printf 'Ollama ya esta instalado.\n'
  exit 0
fi

if [[ "$INSTALL_OLLAMA" == "1" ]]; then
  printf 'Instalando Ollama con el instalador oficial...\n'
  curl -fsSL https://ollama.com/install.sh | sh
else
  printf 'Ollama no esta instalado. Ejecuta luego:\n'
  printf '  curl -fsSL https://ollama.com/install.sh | sh\n'
fi
