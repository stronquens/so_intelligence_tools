# Validation

## Connected and responsive implementation (2026-07-14)

The Electron translator is now connected to the real Python
`system-audio-transcription` controller through JSON Lines. Linux
`Ctrl+Alt+Y` opens or toggles that window, while the prior Tkinter UI remains a
manual fallback.

### Automated

- `poetry run pytest -q`: 237 passed; one unrelated third-party
  Starlette/httpx deprecation warning.
- `npm --prefix desktop run test`: 26 passed.
- `npm --prefix desktop run build`: Vite and Electron TypeScript build passed.
- `bash -n scripts/run-system-audio-translation-debug.sh`: passed.
- `openspec validate build-realtime-translation-desktop-ui --strict`: valid.
- Changed Python files pass Ruff and compilation checks.

### Functional smoke

- The GNOME wrapper launched one 1440 x 820 Electron translator window and one
  `run-system-audio-translation-desktop-bridge` Python child.
- A live OpenAI realtime session displayed real original/Spanish block pairs and
  a streaming partial in the single timeline.
- Pause changed the backend and all visible status surfaces to `Paused`, stopped
  waveform motion and preserved completed history; resume is covered by the
  same backend command path and frontend contract tests.
- Invoking the wrapper again toggled the translator closed. Electron waited for
  cooperative Python shutdown and applied a bounded forced stop when necessary;
  no Electron/Python child or control socket remained afterward.
- Production sessions start without mock transcript data. The browser-only
  render remains explicitly labelled `Preview`.
- Responsive visual QA ran through `npm run translator:mock`, which explicitly
  prevents Electron from starting the paid Python/provider bridge. The mock
  window was resized from 1440 x 820 to its supported 900 x 600 minimum.
  Header, language/model selectors, paired transcript and all five bottom
  actions remained available; the sidebar uses an explicit scrollbar when its
  content exceeds the available height.
- Changing language configuration is covered end to end at the JSONL and app
  layers. The controller is stopped and rebuilt with the new pair while Vue
  retains prior blocks.

### Visual evidence

- [Connected empty/live state](evidence/connected-electron-session.png)
- [Connected paused state with real history](evidence/connected-electron-paused.png)
- [Reference versus connected comparison](evidence/reference-vs-connected.png)
- [Responsive audit and findings](evidence/responsive-audit/audit.md)
- [Refined 1440 x 820](evidence/responsive-audit/03-refined-1440x820.png)
- [Refined 900 x 600](evidence/responsive-audit/04-refined-900x600.png)
- [Synchronized paused state at 900 x 600](evidence/responsive-audit/05-refined-900x600-paused.png)
- [Original mock fidelity audit](evidence/fidelity-audit/audit.md)
- [Implementation before fidelity correction](evidence/fidelity-audit/02-current-before.png)
- [Corrected 1680 x 946 mock render](evidence/fidelity-audit/04-current-after.png)
- [Corrected 900 x 600 mock render](evidence/fidelity-audit/05-current-after-900x600.png)
- [Original reference versus corrected implementation](evidence/fidelity-audit/06-reference-vs-after.png)
- [Selector, PCM meter and virtual microphone audit](evidence/language-selector-fix/audit.md)
- [Final model popover and meter](evidence/language-selector-fix/08-final-model-and-meter-1680x946.png)
- [Final window-control hover](evidence/language-selector-fix/09-final-window-hover.png)
- [Full language menu at 900 x 600](evidence/language-selector-fix/10-final-language-menu-900x600.png)
- The responsive audit records the before/after review with no remaining
  blocking visual finding. All durable QA material now lives inside the change.

### Requirement mapping

- Python ownership and renderer isolation: `desktop_bridge.py`, preload IPC and
  Electron process tests/build demonstrate that capture/providers remain in
  Python and only typed events/commands cross the bridge.
- Grouped visualization: frontend tests cover buffered blocks, live partials,
  aligned columns, persisted density and retained history through reconnection;
  live evidence shows real pairs.
- Controls: tests cover pause pending/confirmation, optimistic mode and language
  changes, stale backend events, translated-microphone pending state, density
  and native close/minimize/maximize;
  the live pause and shortcut toggle were manually exercised.
- Professional states: screenshots cover active and paused states; frontend
  tests cover reconnecting history; CSS includes reduced-motion overrides.
- Audio meter: Python tests cover PCM normalization and bridge serialization;
  Vue tests cover source selection and bar updates. A provider-free live audio
  smoke read 4,800 PCM bytes from the exact `so_ai_translated_mic` source.
- Translated microphone: current local routing proves physical capture,
  passthrough and the public source without provider use. Existing 2026-06-12
  realtime logs prove `realtime_connected` and translated
  `output_audio_written` events on that same endpoint.

### Residual risks

- Dynamic audio-device selection remains intentionally out of scope.
- The published desktop catalog is deliberately finite. The underlying models
  may understand additional languages, but they are not selectable until added
  and validated in `languages.py`.
- Windows system-audio capture is still not implemented, so the connected
  translator backend smoke test is Linux-only. Existing Windows overlay behavior
  remains unchanged.
- The host logs a non-fatal Snap/GLIBCXX GIO module warning when Electron starts;
  it did not prevent window rendering, streaming or shutdown.
- Visual captures must use `npm run translator:mock`. Starting the normal
  shortcut is reserved for explicit functional checks because it can consume a
  paid provider API.

### Fidelity correction after user review

The user reported that the first responsive pass changed more than requested,
specifically the traffic-light controls and missing language flags. A fresh
1680 x 946 comparison against `desktop/.tmp/realtime-translator-ui-v3.png`
confirmed the drift. The corrected build restores 17 px visible window marks
inside larger hit targets, the 356 px desktop sidebar, real flag assets, the
plain language route, original status copy and wide-layout control proportions.
The horizontal transcript, density control, functional popovers and responsive
breakpoints remain as intentional requirements.

### Live voice regression correction

The user's 13:24 functional session exposed two coupled lifecycle defects. The
provider connected and produced English transcript/audio output, but a Spanish
controller status was printed to the JSONL-only stdout stream. Electron parsed
that line as an event and surfaced the reported `Unexpected token 'T'` error.
The same log showed `inactive` before the realtime receiver timed out, with
audio activity continuing afterward.

Validation after correction is fully provider-free:

- A Python regression calls the same voice state path and asserts that stdout
  remains empty while the human-readable status is sent to stderr.
- A bounded-drain test verifies cancellation of a receiver that never returns.
- A stuck-worker test verifies that `inactive` is not published while the worker
  remains alive.
- Electron now discards an isolated non-JSON stdout line as a diagnostic; the
  Electron TypeScript build passes.
- The complete suite passes with 237 Python and 26 Vue tests, strict OpenSpec
  validation, Ruff, Python compilation, shell syntax and `git diff --check`.

The payload and event handling were also checked against the current official
OpenAI Realtime translation guide. It matches the documented dedicated
WebSocket endpoint, target-language configuration, continuous 24 kHz PCM16
input, output deltas and graceful `session.close` drain. No payload change was
needed and no additional paid session was opened.

- [Live regression log analysis and provider-free evidence](evidence/voice-translation-live-regression/analysis.md)

### Window halo, pending spinner and output visibility correction

The final visual regression pass removed inherited hover properties from the
window-control button itself. Computed Electron styles now report no background,
shadow or filter on the hovered target; only the colored mark renders a shadow.

Large pending controls now wrap the loader in a static visual surface. A
provider-free pending-state probe reports `animation-name: none` on the surface
and `animation-name: spin` on the inner loader. The translated-microphone backend
message is no longer tooltip-only: a persistent strip above the controls shows
off, connecting, active, stopping and error states plus the routing message.

- [Control and translated-output visual audit](evidence/control-output-fix/audit.md)
- Frontend validation: 26 tests and production Electron build passed.

The same review found that `audio_level` existed in Python and Vue but was
missing from Electron's `UiEvent` parser, so real production levels were being
discarded. Electron now accepts that event. Python additionally publishes
`voice_translation_output` from confirmed writes to the virtual microphone;
the visible output strip reports cumulative chunks and bytes. Provider-free
controller, pipeline, app, JSONL and Vue regressions cover this route.

The full Python suite passes with 237 tests. Ruff passes on all changed files;
the repository-wide Ruff command still reports one pre-existing unused `Path`
import in `tests/test_codex_voice_control.py`, outside this change.
