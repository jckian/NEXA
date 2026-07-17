# M4 generation record — scenarios-citymarket.js (260712)

Reproducibility record per INTEL-DATA.md §5. This documents how the four scenario cards
were produced, so the run can be repeated or challenged.

## Inputs

| File | MD5 at generation |
|---|---|
| `NEXA/intel/data/site-citymarket.js` | `0A9B1F37757EED0ED54E77AC4B8ABD0A` |
| `NEXA/intel/data/transitions.js` | `23280A41C595ACCC438EDA77E2C1F185` |

Executor: main Claude Code session (Fable 5), offline — no runtime API (constraint C3).

## Method

1. Read the SITE-TIMELINE spine: produce market (1909–2009) → creative reuse (2014–2024)
   → entitled mixed-use build-out (2026–2049 est.). The forecast question is what fills
   the third node and what happens if it slips.
2. From the timeline's present-epoch driver nodes (office vacancy `e-dtla-office-vacancy`,
   population growth `e-dtla-population-growth`, transit `t-future-southeast-gateway`,
   regulation `r-2024-revised-agreement` / `r-2023-dtla2040`), enumerate the program
   directions the PROGRAM-TRANSITION-DB supports from the site's current programs
   (wholesale-market/warehouse stock, creative office): housing, education, food/event,
   continued creative reuse.
3. One scenario per direction; each `drivers` array cites timeline node ids; each
   `likelihoodNote` states its basis in one sentence; risks include the transition DB's
   gating preconditions (operator, institutional anchor, capital).
4. Scenario A is deliberately the entitled program itself — the null hypothesis a
   forecast must include. Scenario D is the stall case (analogous to the original
   proposal's "population decline" scenario, grounded here in the observed 2018→2024
   entitlement saga instead of demographics).
5. `programFormatDraft`s are study-scale slices (~6,000–10,000 m² GFA) written in the
   handoff-test's verified vocabulary and area/{w,h} pairs, 3 cores + 1 circulation strip
   per level (ProgramFormat core rule: ≥3 fire stairs). They instantiate the mix at
   platform scale; they are not the master plan.

## Validation applied before shipping

- Mechanical draft check (node script, session 260712): grammar per line, category ∈
  {public, private, circulation}, ≥3 fire-stair cores per level, |w·h − area|/area ≤ 10%.
- End-to-end: draft applied through program-input.html → shortfloor massing render
  (headless-Edge screenshot), see 260712 session log.

## Regeneration rule

If either input file's hash changes (dossier/timeline update, new transitions), rerun
this method and bump the `generation.date`; do not hand-edit scenario cards in place.
