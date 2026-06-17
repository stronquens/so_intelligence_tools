## Why

The public README lists product highlights but does not make it obvious which capabilities are usable with local/on-prem infrastructure, which require provider APIs, and which can support both. This matters for users evaluating privacy, cost, and deployment constraints.

## What Changes

- Add a runtime/deployment-readiness column to the README Highlights table.
- Use concise labels for local/on-prem, API-backed, both, and planned capabilities.
- Keep the existing feature status column unchanged.

## Capabilities

### New Capabilities

- `repository-presentation-runtime-readiness`: Public repository presentation communicates each highlighted feature's local/on-prem versus API readiness.

### Modified Capabilities

None.

## Impact

- Affects `README.md` and this OpenSpec change only.
- No runtime behavior, dependencies, or product code changes.
