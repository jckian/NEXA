# NEXA Intel — Implementation Roadmap

Created 260712. Status: N0 done (the three design docs). Phases below are additive to
the platform — nothing existing is removed or replaced (constraint C6); `VORO/` is never
touched (C4); no runtime API until the whole system is built (C3).

## N1 — Pilot site dossier + timeline · City Market of Los Angeles

One-shot WebSearch research task(s) producing `data/site-citymarket.js` + `.md`
(SITE-DOSSIER + SITE-TIMELINE per INTEL-DATA §2–§3), human-reviewed.

**Done when:** every timeline node has ≥1 source; dossier sections either filled with
tagged facts or explicitly `null/unknown`; the program-succession spine (market →
decline → creative reuse → planned mixed-use → 2050 projection) is continuous;
MD companion reads as a citable site report.

## N2 — Program Transition Database

Author `data/transitions.js` + `.md` per INTEL-DATA §4. Start from the pilot site's own
transitions, add the platform's case-study lineages (TPAC site history, 53W53/MoMA
block), then the canonical adaptive-reuse pairs (warehouse/office/mall/parking → …).

**Done when:** ≥15 `from` types covering every ProgramFormat category in platform use;
every transition has ≥1 cited built example; every likelihood tier states its basis;
the vocabulary→ProgramFormat mapping table is complete.

## N3 — Forecast generation + platform integration

1. M4 run: scenario cards for City Market (3–5), each with a ProgramFormat draft —
   drafts authored via program-planner, validated by program-auditor; prompt + inputs
   archived in `prompts/` (reproducibility record per INTEL-DATA §5).
2. `program-input.html`: add a **Site Forecast** entry — loads
   `NEXA/intel/data/*.js` via `<script src>`, renders scenario cards, one click applies
   a card's draft into the existing wizard flow → localStorage → shortfloor.
   Manual input path unchanged.

**Done when:** program-auditor passes every draft; headless-Edge screenshots verify
(a) scenario cards render in the wizard, (b) applying a card lands in shortfloor with a
correct massing (same pipeline as TEST/_handoff-test.html); manual path regression-checked.

## N4 (optional) — Timeline visualization

`NEXA/intel/timeline.html`: single-file page, 1900→2050 axis from the SITE-TIMELINE
data, scenario branching at the present. Presentation artifact; screenshot-verified.

## G — Site Scout (added + built 260713, user-approved scope G1–G3)

`NEXA/intel/site-scout.html` — address → geocode → map (Leaflet/OSM) → LA County parcel
candidates (click-to-select) → LA City zoning + overlays → Overpass surroundings metrics →
downloadable dossier-skeleton `site-<slug>.js` (all fields `reported` tier, timeline empty
pending N1). Coverage: any US address geocodes + OSM analysis; parcel/zoning panels are
LA-only. Endpoints probed + documented in the 260713 session log. **LA county/city layers
need an http origin — use the local server; `file://` degrades to zoning + OSM only.**
The C3 amendment covering this lives in INTEL-ARCHITECTURE §2.

## Deferred — API socket (post-N4, user decision 260712)

Runtime generation (wizard → API → scenario JSON, same schema as offline). Revisit only
after N1–N3 are stable. Design rule from INTEL-ARCHITECTURE §6 already guarantees the
schemas are socket-ready; no N1–N4 work may depend on the socket existing.

## Risk register

- **Source thinness on early history (pre-1950):** acceptable — mark nodes `reported`,
  narrow `tStart/tEnd` ranges later. Do not block N1 on archival perfection.
- **Fake precision creep:** the moment a likelihood becomes a bare percentage or an
  unsourced fact enters a `.js` file, C5 is violated — program-auditor-style review
  (numbers and line numbers, no adjectives) applies to data files too.
- **Wizard regression:** N3 touches `program-input.html`; back it up to `BACKUP/`
  first per project convention, verify the manual path after.
