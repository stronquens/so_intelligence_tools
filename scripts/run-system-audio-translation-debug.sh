#!/usr/bin/env bash
set -u

LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/so_intelligence_tools"
LOG_FILE="$LOG_DIR/system_audio_shortcut.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI="$PROJECT_DIR/.venv/bin/so-intelligence-tools"

mkdir -p "$LOG_DIR"

cd "$PROJECT_DIR"

BINDING="$(
  awk -F= '/^GNOME_SYSTEM_AUDIO_TRANSLATION_BINDING=/{print $2; exit}' "$PROJECT_DIR/.env" 2>/dev/null
)"

{
  printf '\n[%s] gnome-shortcut-wrapper invoked\n' "$(date -Is)"
  printf 'project_dir=%s\n' "$PROJECT_DIR"
  printf 'cli=%s\n' "$CLI"
  printf 'pwd=%s\n' "$(pwd)"
  printf 'XDG_SESSION_TYPE=%s\n' "${XDG_SESSION_TYPE:-}"
  printf 'WAYLAND_DISPLAY=%s\n' "${WAYLAND_DISPLAY:-}"
  printf 'DISPLAY=%s\n' "${DISPLAY:-}"
  printf 'binding=%s\n' "${BINDING:-}"
} >> "$LOG_FILE" 2>&1

if [[ ! -x "$CLI" ]]; then
  {
    printf '[%s] ERROR cli-not-executable\n' "$(date -Is)"
    ls -l "$PROJECT_DIR/.venv/bin" 2>&1 | sed -n '1,80p'
  } >> "$LOG_FILE" 2>&1
  exit 1
fi

"$CLI" run-system-audio-translation-toggle >> "$LOG_FILE" 2>&1
STATUS=$?

{
  printf '[%s] gnome-shortcut-wrapper exit_status=%s\n' "$(date -Is)" "$STATUS"
} >> "$LOG_FILE" 2>&1

exit "$STATUS"
