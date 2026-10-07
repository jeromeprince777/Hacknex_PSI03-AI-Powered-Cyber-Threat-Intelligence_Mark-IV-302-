# Design — ThreatWeave

Locked visual system for the ThreatWeave analyst application. Investigation,
dataset replay, and suppression views share these tokens and interaction rules.
Keep the existing typed API contracts and evidence relationships intact.

## System
- Genre · modern-minimal, forensic
- Macrostructure · Evidence Workbench
- Theme · custom (warm paper, charcoal ink, restrained copper)
- Axes · warm off-white / compact technical sans / copper signal accent

## App structure
- Use a slim, fixed top masthead for the wordmark, the three existing work areas,
  engine health, and sync. Put case selection beside the case heading.
- Investigation opens on the case story: identity and verified metadata first,
  attack stages and chronological evidence as the primary work surface.
- On wide screens, keep timeline and stage evidence in the main column; place
  risk components and approved actions in a narrower adjacent column. Put the
  entity graph below the primary evidence so it supports rather than competes.
- Replay uses a compact scenario index beside the selected dataset and run
  result. Suppression uses a readable audit table with reason and event links.
- Avoid equal-weight KPI tiles, decorative charts, fake sample values, glowing
  effects, and claims that cannot be verified from the active data.
- At narrow widths, navigation wraps or collapses accessibly and all work areas
  become a single column without hiding event IDs or actions.

## Tokens
`frontend/app/globals.css` is the runtime source of truth.

```css
:root {
  --color-paper:      oklch(97% 0.008 82);
  --color-paper-2:    oklch(100% 0 0);
  --color-paper-3:    oklch(94% 0.009 82);
  --color-ink:        oklch(19% 0.012 240);
  --color-ink-2:      oklch(34% 0.012 240);
  --color-muted:      oklch(51% 0.012 240);
  --color-rule:       oklch(87% 0.012 82);
  --color-accent:     oklch(53% 0.12 43);
  --color-accent-ink: oklch(99% 0.004 82);
  --color-focus:      oklch(53% 0.12 43);
  --color-high:       oklch(49% 0.16 26);
  --color-medium:     oklch(55% 0.12 67);
  --color-low:        oklch(48% 0.08 158);

  --font-display: "Geist", ui-sans-serif, system-ui, sans-serif;
  --font-body:    "Geist", ui-sans-serif, system-ui, sans-serif;
  --font-mono:    "Geist Mono", ui-monospace, monospace;
  --space-3xs: 0.25rem; --space-2xs: 0.5rem; --space-xs: 0.75rem;
  --space-sm: 1rem; --space-md: 1.5rem; --space-lg: 2rem;
  --space-xl: 3rem; --space-2xl: 4.5rem;
  --text-xs: 0.75rem; --text-sm: 0.875rem; --text-md: 1rem;
  --text-lg: 1.25rem; --text-xl: 1.625rem;
  --radius-card: 6px; --radius-pill: 999px; --radius-input: 5px;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --dur-fast: 140ms; --dur-base: 180ms;
}
```

## Type and data
- Use Geist for interface text and Geist Mono for event IDs, timestamps,
  addresses, rule identifiers, and score components.
- Keep headings functional and modest. Use tabular numerals for aligned values.
- Keep full event identifiers available; truncate only with a visible way to inspect.
- Severity and health always use text labels as well as color.

## Controls and states
- Primary action · solid charcoal or copper only when it signals the principal
  action; compact rectangular control with clear verb-first text.
- Secondary action · paper surface, visible border, same control geometry.
- Use square corners or a restrained 5–6px radius for work surfaces. Reserve
  pills for small status labels only.
- Empty, loading, offline, and error states explain the actual next step. Never
  substitute fabricated counts or incident details.

## Motion
- No scroll reveals, parallax, animated counters, pulsing status lights, or
  decorative graph motion.
- Use short opacity/color transitions for focus, selection, and evidence drawer
  open/close only. Respect `prefers-reduced-motion` with near-instant changes.

## Responsive and accessibility
- Keep keyboard focus visible, hit targets usable, and text contrast strong on
  paper and status surfaces.
- Preserve keyboard operation and accessible names on nav, graph controls,
  evidence selection, replay, and drawer dismissal.
- Do not use color as the only signal. Keep tables horizontally contained and
  allow dense metadata to wrap at mobile widths.
