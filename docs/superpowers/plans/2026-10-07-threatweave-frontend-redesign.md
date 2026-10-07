# ThreatWeave frontend redesign implementation plan

## Goal

Implement the approved Evidence Workbench system in `design.md` across the
existing investigation, replay, and suppression views. Keep typed API contracts,
incident facts, evidence links, and current actions intact. Do not modify backend
behavior or delete existing files.

## Work sequence

1. **Protect current work.** Review the existing working-tree diffs and current
   UI composition before editing. Read the relevant installed Next.js 16
   guidance. Preserve pre-existing frontend and backend changes.
2. **Set the visual foundation.** Implement the approved paper/charcoal/copper
   tokens, type, focus treatment, responsive base rules, and reduced-motion
   behavior in the existing global stylesheet. Rework the application shell,
   navigation, context header, and loading/offline states.
3. **Rebuild investigation hierarchy.** Recompose the existing investigation
   screen around case identity, verified metadata, attack stages, and event
   chronology. Keep risk factors, response actions, entity graph, and copilot
   accessible without giving them equal visual weight.
4. **Restyle other work areas.** Apply the same system to dataset replay,
   suppression audit, graph controls, and the evidence drawer. Keep existing
   scenario selection, analysis, refresh, filters, and event selection wired to
   the same state and API functions.
5. **Polish responsive behavior.** Verify desktop, tablet, and narrow layouts;
   remove decorative motion and retain short functional feedback only. Preserve
   keyboard access, labels, focus, and text-based severity/status cues.
6. **Verify the working product.** Run the frontend lint/build checks, start the
   backend and frontend, exercise the seeded attack and benign replay paths, and
   run the available Playwright smoke flow. Inspect browser console and network
   failures; fix issues caused by the redesign before reporting completion.

## Expected files

- Create/update: `frontend/app/globals.css`, `frontend/app/layout.tsx`,
  `frontend/app/page.tsx`, and the existing view components under
  `frontend/components/` that are actually mounted by those views.
- Do not delete files, change API/data contracts, or alter backend code.
- Preserve unrelated working-tree changes and keep edits limited to the UI.

## Completion checks

- All three views render from the real API data without invented values.
- Clicking a stage/event still selects its real evidence and opens the raw and
  normalized event detail.
- Graph filtering/selection, risk components, approved actions, dataset replay,
  suppression reasons, case switching, and refresh still work.
- Layouts remain usable at narrow widths; reduced-motion preference is honored.
- Lint/build and end-to-end browser checks complete without new console or
  network errors.
