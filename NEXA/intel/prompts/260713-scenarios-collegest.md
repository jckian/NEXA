# M4 generation record — scenarios-collegest.js (260713)

Reproducibility record per INTEL-DATA.md §5.

## Inputs

| File | MD5 at generation |
|---|---|
| `NEXA/intel/data/site-collegest.js` | `EAC3F9DF07B6977AF0C3749BE31466CD` |
| `NEXA/intel/data/transitions.js` | `23280A41C595ACCC438EDA77E2C1F185` |

Executor: main Claude Code session (Fable 5), offline — no runtime API (constraint C3).

## Evidence caveat (must travel with these scenarios)

The N1 research run for this site was **terminated mid-stream by an API outage**. ZIMAS,
the project case file, the Central City North plan page and the TOC guidelines were never
queried. Consequently **`site-collegest.js` contains no `verified`-tier facts**: zoning
string, FAR, height district, lot area and TOC tier are all `unknown`.

These scenarios are therefore **programmatic hypotheses about a station-adjacent parking
lot, not capacity studies**. The `programFormatDraft` GFAs (1,706–8,649 m²) are
platform-scale study slices sized to exercise the massing model; none is a zoning yield.
Anyone citing them must carry this caveat. Resolving the zoning is the highest-value next
research action for this site.

## Method

1. Read the spine: Old Chinatown (1880s–1933) → New Chinatown / Central Plaza (1938–) …
   [record changes from district to parcel resolution] … surface parking lot (present) →
   2023 creative-office proposal (in environmental review).
2. Identify the site's defining tension from the present-epoch driver nodes: a speculative
   ~225,000 sf office bet (`p-2023-office-proposal`, `e-2023-riboli-chinatown-bet`) on a
   parcel adjacent to the Metro A Line Chinatown station (`t-2003-chinatown-station`),
   into a ~22% office-vacancy market (`e-dtla-office-softness`), needing a General Plan
   Amendment + zone change (`r-2023-entitlement`), in a district with active
   anti-displacement organizing (`s-displacement-pressure`).
3. One scenario per resolution of that tension, each grounded in a transition-DB row:
   - **D (2029)** stall → the lot persists with interim market/event use. The null
     hypothesis; the entitlement burden and office market both argue for it.
   - **A (2030)** the proposal is entitled and built (office).
   - **B (2034)** office→housing (transition DB: *high* tier), corroborated on this very
     block by College Station (725 units approved across the street, 2018).
   - **C (2038)** community anchor — affordable housing + market hall + cultural program;
     driven by the district's politics rather than a private pro forma, hence the longest
     horizon and the operator/subsidy gate the transition DB flags for market→food-hall.
4. Every `drivers` entry is a real timeline node id (mechanically checked).
5. Drafts use the platform's verified vocabulary and area/{w,h} pairs; 3 fire-stair cores
   + circulation per level.

## Validation applied before shipping

Node script (session 260713), both sites at once: JS loads, no dangling/duplicate node
ids, every node sourced, succession chains temporally consistent, every scenario driver
resolves to a timeline node, ProgramFormat grammar per line, category ∈ {public, private,
circulation}, ≥3 fire-stair cores per level, |w·h − area|/area ≤ 10%, mix shares sum to 1,
level contiguity — **ALL PASS**.

## Regeneration rule

If either input hash changes — in particular when the zoning is finally verified — rerun
this method rather than hand-editing the cards, and revisit scenario A's plausibility
first: it is the one the zoning question bears on most directly.
