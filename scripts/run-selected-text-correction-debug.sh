#!/usr/bin/env bash
set -u

LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/so_intelligence_tools"
LOG_FILE="$LOG_DIR/selected_text_correction.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI="$PROJECT_DIR/.venv/bin/so-intelligence-tools"
export YDOTOOL_SOCKET="/tmp/.ydotool_socket"

mkdir -p "$LOG_DIR"

{
  printf '\n[%s] gnome-shortcut-wrapper invoked\n' "$(date -Is)"
  printf 'project_dir=%s\n' "$PROJECT_DIR"
  printf 'cli=%s\n' "$CLI"
  printf 'pwd=%s\n' "$(pwd)"
  printf 'XDG_SESSION_TYPE=%s\n' "${XDG_SESSION_TYPE:-}"
  printf 'WAYLAND_DISPLAY=%s\n' "${WAYLAND_DISPLAY:-}"
  printf 'DISPLAY=%s\n' "${DISPLAY:-}"
  printf 'YDOTOOL_SOCKET=%s\n' "${YDOTOOL_SOCKET:-}"
  printf 'api_health='
  curl -fsS --max-time 2 http://127.0.0.1:8000/health 2>&1 || true
  printf '\n'
} >> "$LOG_FILE" 2>&1

if [[ ! -x "$CLI" ]]; then
  {
    printf '[%s] ERROR cli-not-executable\n' "$(date -Is)"
    ls -l "$PROJECT_DIR/.venv/bin" 2>&1 | sed -n '1,80p'
  } >> "$LOG_FILE" 2>&1
  exit 1
fi

"$CLI" run-selected-text-correction --debug >> "$LOG_FILE" 2>&1
STATUS=$?

{
  printf '[%s] gnome-shortcut-wrapper exit_status=%s\n' "$(date -Is)" "$STATUS"
} >> "$LOG_FILE" 2>&1

exit "$STATUS"
