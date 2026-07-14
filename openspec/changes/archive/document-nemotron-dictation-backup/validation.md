## Validation

Date: 2026-06-17

### Commands

```bash
openspec validate document-nemotron-dictation-backup --strict
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
for p in docs/push-to-talk-dictation.md openspec/changes/add-nemotron-streaming-dictation/design.md openspec/changes/add-nemotron-streaming-dictation/validation.md openspec/specs/push-to-talk-dictation/spec.md src/so_intelligence_tools/push_to_talk_dictation/onnx_cpu.py; do git cat-file -e "e448d56:$p" && echo "OK e448d56:$p"; done
```

### Results

- `openspec validate document-nemotron-dictation-backup --strict` passed.
- Documentation link check covered `README.md` plus 22 docs files and found no missing relative links.
- Historical references in commit `e448d56` were confirmed for the old docs, OpenSpec change, live spec, and `onnx_cpu.py` implementation.
- The push-to-talk dictation docs now present Linux Whisper and Linux Nemotron streaming as separate backend options with clear runtime labels.
