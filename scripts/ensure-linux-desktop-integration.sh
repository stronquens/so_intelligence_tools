#!/usr/bin/env bash
set -u

LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/so_intelligence_tools"
LOG_FILE="$LOG_DIR/desktop_health.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CLI="$PROJECT_DIR/.venv/bin/so-intelligence-tools"

mkdir -p "$LOG_DIR"
cd "$PROJECT_DIR"

{
  printf '\n[%s] desktop-health invoked\n' "$(date -Is)"
  printf 'project_dir=%s\n' "$PROJECT_DIR"
  printf 'cli=%s\n' "$CLI"
  printf 'XDG_SESSION_TYPE=%s\n' "${XDG_SESSION_TYPE:-}"
  printf 'DISPLAY=%s\n' "${DISPLAY:-}"
} >> "$LOG_FILE" 2>&1

sleep 3

{
  printf '[%s] starting-api-service\n' "$(date -Is)"
  systemctl --user start so-intelligence-tools-api.service || true
  printf '[%s] refreshing-gnome-media-keys\n' "$(date -Is)"
  systemctl --user restart org.gnome.SettingsDaemon.MediaKeys.target || true
} >> "$LOG_FILE" 2>&1

if [[ ! -x "$CLI" ]]; then
  {
    printf '[%s] ERROR cli-not-executable\n' "$(date -Is)"
    ls -l "$PROJECT_DIR/.venv/bin" 2>&1 | sed -n '1,80p'
  } >> "$LOG_FILE" 2>&1
  exit 1
fi

{
  printf '[%s] reinstalling-shortcuts\n' "$(date -Is)"
  "$CLI" install-gnome-selected-text-shortcut --debug
  "$CLI" install-gnome-system-audio-translation-shortcut
  "$CLI" install-gnome-voice-translation-shortcut
  "$CLI" install-push-to-talk-dictation-service
  printf '[%s] desktop-health completed\n' "$(date -Is)"
} >> "$LOG_FILE" 2>&1
