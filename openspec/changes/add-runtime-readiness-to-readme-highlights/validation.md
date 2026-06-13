## Validation

Date: 2026-06-13

### Commands

```bash
openspec validate add-runtime-readiness-to-readme-highlights --strict
awk '/^## Highlights/{flag=1; next} /^## Desktop UI/{flag=0} flag && /^\|/ { n=gsub(/\|/,"&"); print n-1 ":" $0 }' README.md
```

### Results

- `openspec validate add-runtime-readiness-to-readme-highlights --strict` passed.
- The Highlights table header, separator, and all capability rows have 4 columns.
