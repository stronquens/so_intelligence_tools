## Validation

Date: 2026-06-13

### Commands

```bash
openspec validate expand-public-english-docs --strict
rg -n "Instalacion|Instalación|Objetivo|Opcion|Configuracion|Atajo|Correccion|Traduccion|Microfono|Problemas|Soluciones|Sintoma|Causa|Solucion|Comprobacion|Herramienta|Dependencias|sesion|validacion|documentacion|contrasena|clave" docs -S
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
        if not clean:
            continue
        resolved = (path.parent / clean).resolve()
        if not resolved.exists():
            missing.append((str(path), target))
if missing:
    for item in missing:
        print(f'MISSING {item[0]} -> {item[1]}')
    raise SystemExit(1)
print(f'Checked {len(files)} markdown files; all relative links exist.')
PY
```

### Results

- `openspec validate expand-public-english-docs --strict` passed.
- The Spanish legacy-heading/content scan returned no matches.
- The relative-link check covered `README.md` plus 16 docs files and found no missing local targets.
