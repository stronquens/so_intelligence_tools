# Validation

## Checks

### OpenSpec change validation

```bash
poetry run openspec validate document-linux-windows-dictation-session-updates --strict
```

Result:

```text
Change 'document-linux-windows-dictation-session-updates' is valid
```

### OpenSpec full validation

```bash
poetry run openspec validate --all --strict
```

Result before archiving:

```text
21 passed, 0 failed
```

### Markdown relative links

```bash
python3 - <<'PY'
from pathlib import Path
import re
files = [Path('README.md'), *Path('docs').glob('*.md')]
missing = []
for path in files:
    text = path.read_text(encoding='utf-8')
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', text):
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
```

Result:

```text
Checked 24 markdown files; all relative links exist.
```

## Summary

- Linux setup docs now describe `Ctrl + Shift + Space`, the warm faster-whisper Docker backend, CPU profile expectations, old `Ctrl + Space` cleanup, and the Linux CPU model benchmark.
- Shared dictation docs now separate Linux and Windows validation state.
- Windows docs remain focused on Windows Startup launchers, Windows shortcut variables, and Windows microphone/runtime notes.
- The public documentation spec now requires platform-specific operational state when Linux and Windows behavior differs.

## Residual Caveats

- This is a documentation-only change; no runtime behavior was changed.
- Linux GUI focus/insertion behavior can still vary by desktop session and target application, so docs describe local validation scope rather than claiming universal GUI behavior.
