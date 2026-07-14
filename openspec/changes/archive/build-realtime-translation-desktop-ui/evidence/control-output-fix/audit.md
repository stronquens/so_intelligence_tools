# Window controls, pending icons and translated output audit

Date: 2026-07-14

## Scope

Regression review after the user reported a remaining white halo around the
traffic-light controls, rotating button backgrounds during pending actions and
no visible indication of translated-voice output.

## Provider-safe method

- Electron screenshots used `SO_AI_TRANSLATOR_MOCK=1`; the Python bridge and
  paid provider were not started.
- The pending-state screenshot used a browser-injected local bridge whose
  command promise deliberately remained pending. It did not contact Python or
  any external service.
- Vue tests and the production Electron build were rerun after the changes.

## Results

- Hovered red window control computed styles: transparent background, no button
  shadow and no button filter. The only shadow belongs to the 17 px `.dot-mark`.
- The translated-output strip remains visible when off, connecting and active;
  the active mock state is green and contains its routing message.
- Python now publishes confirmed translated chunk and byte totals. The Electron
  parser accepts both these output events and the previously omitted real
  `audio_level` events instead of silently discarding them.
- Pending microphone state uses a static `.control-icon-surface` and a separate
  `.pending-control-icon`. Computed animation names were respectively `none`
  and `spin`; the surface transform remained `none`.
- The same component structure is used by the large pause/resume button and is
  covered by the frontend regression.

## Evidence

- [Window-control hover and inactive output](01-window-hover-and-output.png)
- [Active translated output](02-active-output-strip.png)
- [Static surface with inner pending spinner](03-microphone-pending-spinner.png)
- [Confirmed translated chunks and bytes](04-confirmed-translated-output.png)

## Automated validation

- Targeted provider-free Python regressions: 23 tests passed.
- Full Python suite: 237 tests passed.
- `npm test -- --run`: 26 tests passed.
- `npm run build`: Vite build and Electron TypeScript compilation passed.
