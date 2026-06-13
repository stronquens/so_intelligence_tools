#!/usr/bin/env bash
set -u

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ok() { printf "${GREEN}[OK]${NC}    %s\n" "$1"; }
warn() { printf "${YELLOW}[WARN]${NC}  %s\n" "$1"; }
fail() { printf "${RED}[FAIL]${NC}  %s\n" "$1"; }

EXIT_CODE=0

echo "-- 1. Repository files --------------------------------"

for file in AGENTS.md pyproject.toml poetry.toml Makefile openspec/config.yaml; do
  if [ -f "$file" ]; then
    ok "Found $file"
  else
    fail "Missing $file"
    EXIT_CODE=1
  fi
done

echo ""
echo "-- 2. Toolchain ---------------------------------------"

if command -v poetry >/dev/null 2>&1; then
  ok "poetry -> $(poetry --version)"
else
  fail "poetry is not installed or not on PATH"
  EXIT_CODE=1
fi

if command -v openspec >/dev/null 2>&1; then
  ok "openspec -> $(openspec --version 2>/dev/null || echo available)"
else
  warn "openspec is not installed or not on PATH"
fi

echo ""
echo "-- 3. Python environment ------------------------------"

if [ -d ".venv" ]; then
  ok "Local .venv exists"
else
  warn "Local .venv does not exist yet; run 'poetry install'"
fi

if command -v poetry >/dev/null 2>&1; then
  if poetry check >/dev/null 2>&1; then
    ok "poetry check"
  else
    fail "poetry check failed"
    EXIT_CODE=1
  fi
fi

echo ""
echo "-- 4. Validation --------------------------------------"

if command -v poetry >/dev/null 2>&1; then
  if poetry run ruff check src tests scripts; then
    ok "ruff check src tests scripts"
  else
    fail "ruff check failed"
    EXIT_CODE=1
  fi

  if poetry run pytest; then
    ok "pytest"
  else
    fail "pytest failed"
    EXIT_CODE=1
  fi
fi

if command -v openspec >/dev/null 2>&1; then
  if openspec validate --all --strict; then
    ok "openspec validate --all --strict"
  else
    fail "openspec validation failed"
    EXIT_CODE=1
  fi
fi

echo ""
echo "-- 5. Summary -----------------------------------------"

if [ "$EXIT_CODE" -eq 0 ]; then
  ok "Workspace preflight passed"
else
  fail "Workspace preflight found issues"
fi

exit "$EXIT_CODE"
