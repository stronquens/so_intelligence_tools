# Responsive translator audit — 2026-07-14

## Verdict

The initial connected UI worked at its intended 1440 x 820 size, but fixed
sidebar, transcript and control dimensions made the minimum window feel cropped
and showed too little history. The refined implementation keeps every core
action reachable, aligns each original with its translation, and uses native
selectors so their popup is not clipped by a scrolling container.

## Steps

1. **Initial connected view at 1440 x 820 — needs improvement.**
   `01-current-1440x820.png` shows a clear active/paused hierarchy, but each
   language is stacked vertically and the 18 px body text plus 28 px row gaps
   limits conversation density. The three 17 px window controls are visually
   and physically difficult to target.
2. **Initial connected view at 1080 x 680 — poor.**
   `02-current-1080x680.png` shows the sidebar cut before its connection card,
   a large fixed bottom control area, and a custom model menu living inside the
   scrolling sidebar where an open menu can be clipped.
3. **Refined mock view at 1440 x 820 — healthy.**
   `03-refined-1440x820.png` shows representative mock turns with original and
   translation aligned horizontally. Source, target, model and density are
   visible controls; window targets are materially larger. Compact density was
   also exercised with the longer functional history before switching visual QA
   to the provider-safe mock launcher.
4. **Refined mock view at 900 x 600 — healthy with intentional scrolling.**
   `04-refined-900x600.png` preserves both transcript columns and all bottom
   actions. The sidebar scrolls independently instead of cutting content, and
   native selects remain operable outside its clipping boundary.
5. **Paused state at 900 x 600 — healthy.**
   `05-refined-900x600-paused.png` shows `Paused` in the header and sidebar and
   `Resume` in the primary action, while retaining the completed conversation.

## Highest-impact changes

- Use a shared session state plus an explicit pending command to prevent
  contradictory `Live`, `Paused`, `Pause` and `Resume` combinations.
- Publish the effective language catalog and selection from Python rather than
  duplicating it in Vue.
- Keep two columns whenever they remain readable, falling back to stacked rows
  below the supported desktop width.
- Default to compact density and preserve a comfortable alternative.

## Accessibility risks and limits

- Visible focus rings, labelled native selects and larger window controls are
  present. Keyboard operation is covered structurally but was not tested with a
  screen reader in this audit.
- Screenshots cannot establish full contrast compliance, focus order or spoken
  announcements. These remain manual accessibility checks for a future pass.
