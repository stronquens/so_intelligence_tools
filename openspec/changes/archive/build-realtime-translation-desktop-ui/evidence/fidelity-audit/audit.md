# Original mock fidelity audit — 2026-07-14

## Verdict

The first responsive pass preserved functionality but drifted too far from the
approved 1680 x 946 mock. The correction restores the original wide-layout
proportions and visual markers while retaining only the explicitly requested
horizontal transcript, density control, functional selectors and responsive
behavior.

## Steps

1. **Original reference — healthy contract.**
   `desktop/.tmp/realtime-translator-ui-v3.png` establishes 17 px traffic-light
   marks, a 356 px sidebar, language flags, 76 px titlebar, 124 px bottom bar,
   plain `Source → Target` route and the approved typography and spacing.
2. **Implementation before correction — needs correction.**
   `02-current-before.png` shows oversized visible window controls, a 310 px
   sidebar, language codes instead of flags, boxed language headings and
   compacted desktop proportions not required by responsive behavior.
3. **Reference versus before — confirms drift.**
   `03-reference-vs-before.png` ties those differences to the same 1680 x 946
   viewport rather than to window resizing.
4. **Corrected implementation at 1680 x 946 — healthy.**
   `04-current-after.png` restores the original markers, sidebar, real flag
   assets, status copy, route treatment, model selector proportions, bottom
   controls and spacing. The clickable area of each window control remains
   larger than its visible 17 px mark.
5. **Corrected implementation at 900 x 600 — healthy with scrolling.**
   `05-current-after-900x600.png` keeps both requested transcript columns,
   flags, all bottom actions and an independently scrollable sidebar.
6. **Reference versus corrected implementation — healthy intentional delta.**
   `06-reference-vs-after.png` shows that the remaining large visual difference
   is the requested horizontal original/translation layout. Density and native
   selects are the other intentional functional additions.

## Accessibility and evidence limits

- Window buttons retain descriptive labels and visible focus treatment while
  their hit area is larger than the visible mark.
- Language selectors use decorative real flag assets plus accessible text
  labels; meaning does not depend on the flag alone.
- Screenshot review cannot prove screen-reader announcements or full keyboard
  order. Existing component tests cover command dispatch, not assistive
  technology behavior.
- Every implementation screenshot in this audit was captured through
  `npm run translator:mock`; no paid provider bridge was running.
