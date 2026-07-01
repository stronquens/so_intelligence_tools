## Validation

Date: 2026-06-17

### Commands

```bash
poetry run pytest tests/test_user_services.py tests/test_shortcut_map.py tests/test_push_to_talk_dictation_session.py tests/test_faster_whisper_http.py -q
poetry run ruff check src/so_intelligence_tools/infrastructure/user_services.py src/so_intelligence_tools/infrastructure/config.py tests/test_user_services.py tests/test_shortcut_map.py
openspec validate switch-linux-dictation-to-whisper-ctrl-space --strict
python3 - <<'PY'
from pathlib import Path
import re
files = [Path('README.md'), *Path('docs').glob('*.md')]
missing = []
for path in files:
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        target = match.group(1)
        if '://' in target or target.startswith('#') or target.startswith('mailto:'):
            continue
        clean = target.split('#', 1)[0]
        if clean and not (path.parent / clean).resolve().exists():
            missing.append((str(path), target))
if missing:
    for p, t in missing:
        print(f'MISSING {p} -> {t}')
    raise SystemExit(1)
print(f'Checked {len(files)} markdown files; all relative links exist.')
PY
poetry run so-intelligence-tools install-push-to-talk-dictation-service
docker ps --filter name=whisper-server --format '{{.Names}} {{.Image}} {{.Status}} {{.Ports}}'
gsettings get org.freedesktop.ibus.general.hotkey trigger
gsettings get org.freedesktop.ibus.general.hotkey triggers
curl -s http://127.0.0.1:9000/v1/models
poetry run so-intelligence-tools check-push-to-talk-dictation-runtime
systemctl --user is-active so-intelligence-tools-push-to-talk-dictation.service
```

### Results

- Targeted pytest suite passed: 20 tests.
- Ruff passed for changed Python files and tests.
- OpenSpec validation passed.
- Documentation link check passed across `README.md` plus 22 docs files.
- `install-push-to-talk-dictation-service` created `docker/whisper-server/.env`, started the CPU Whisper container, cleared the IBus `Control+space` trigger, and restarted the dictation service.
- Docker is running `whisper-server hwdsl2/whisper-server:latest` on `127.0.0.1:9000->9000/tcp`.
- `docker/whisper-server/.env` uses `WHISPER_DEVICE=cpu` and `WHISPER_COMPUTE_TYPE=int8`.
- IBus `trigger` no longer contains `Control+space`; `triggers` remains `['<Super>space']`.
- `/v1/models` returns `large-v3-turbo`.
- `check-push-to-talk-dictation-runtime` returns `Push-to-talk dictation runtime ready`.
- `so-intelligence-tools-push-to-talk-dictation.service` is active.
