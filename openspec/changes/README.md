# Changes

Los cambios activos viven aquí con una carpeta por iniciativa:

```text
openspec/changes/<change-name>/
```

Artifacts habituales:

- `proposal.md`
- `design.md`
- `tasks.md`
- `specs/.../spec.md` para delta specs cuando haga falta
- `validation.md`
- `evidence/`
- `research/`

Cuando un change termine, muévelo a `openspec/changes/archive/<change-name>/`. El nombre se conserva sin prefijos de fecha: Git ya mantiene la cronología y la ruta estable evita duplicados. Si el destino existe, detén el archivado y compara ambos changes; no sobrescribas archivos ni añadas una fecha para esquivar la colisión.
