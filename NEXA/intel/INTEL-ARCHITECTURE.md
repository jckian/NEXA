# NEXA Intel — System Architecture

Created 260712. Status: **design document (N0)** — nothing in this file is implemented yet.
Companion docs: `INTEL-DATA.md` (schemas + sources), `INTEL-ROADMAP.md` (phases N1–N4).

## 1. What this layer is

An **upstream intelligence layer** for the NEXA platform that answers two questions
about a site before any program is authored:

1. **What does this site need now?** (current-demand program recommendation)
2. **What will it likely need in the future?** (program evolution forecast, scenario-based)

Its final output is always a **ProgramFormat draft** (`{type}/{area m2}/{level}/{category}/{w,h}`),
so it plugs into the existing pipeline instead of creating a parallel one:

```
M1 SITE-DOSSIER ─┐
M2 SITE-TIMELINE ─┼─► M4 FORECAST (scenario cards + ProgramFormat drafts)
M3 TRANSITION-DB ─┘            │
                               ▼
              M5 UI: program-input.html "Site Forecast" entry
                               │  (localStorage handoff — existing)
                               ▼
                  program-massing-shortfloor.html (existing, untouched)
```

## 2. Standing constraints (inherited + new, do not violate)

| # | Constraint | Origin |
|---|---|---|
| C1 | The deterministic layout kernel is never touched. LLM output stops at ProgramFormat text. | NEXA-EXECUTION-PLAN §4 (standing architectural constraint) |
| C2 | No orchestrator agent. The "agents" of the original 12-agent proposal are implemented as **documents with schemas**, produced by one-shot research tasks. | NEXA-EXECUTION-PLAN §5 (blueprint decision #1) |
| C3 | **Offline-first for LLM work.** No LLM runtime API calls until the whole system is built; then an API socket may be added (user decision 260712). **Amended 260713 (user-approved):** public GIS endpoints (Census/Nominatim geocoders, LA GeoHub zoning, LA County parcels, city overlays, Overpass/OSM) are allowed — but only inside the Site Scout tool (`site-scout.html`); the forecast data layer stays offline `.js` files. Data ships as `.js` script files because `file://` pages cannot `fetch()` sidecars. | User 260712, amended 260713 |
| C4 | "The platform" = the root pair `program-input.html` + `program-massing-shortfloor.html` (NEXA). **`VORO/` is frozen — never modified by this work.** | User 260712 |
| C5 | Every quantitative claim in the data layer carries a source + confidence tag. Transition "probabilities" are **estimates** and must be labeled as such. | Project honesty ethos (260707 HANDOFF pattern) |
| C6 | Existing platform features are additive-only: the Site Forecast entry is a new path in the wizard, never a replacement of manual program input. | User 260712 ("原本做的都要有") |

## 3. Modules

### M1 — SITE-DOSSIER (per site)
Curated structured snapshot of one site's **present**: physical, urban, environmental,
context, regulation, market/demographic, climate/infrastructure. Produced by a one-shot
WebSearch research task, human-reviewed. Covers the original proposal's agents
2 (Site Intelligence), 4 (Regulation), 5 (Market & Demographic), 6 (Climate & Infrastructure).

### M2 — SITE-TIMELINE (per site) — the Temporal Knowledge Graph
Timestamped nodes (program, building, regulation, transit, economy, society, climate)
from earliest record to planning horizon (~2050), with typed edges (succession, cause,
constraint). This is the research core. Covers agent 3 (Urban Evolution) and the
"Temporal Knowledge Graph" concept. MVP = one site, one timeline; the multi-site graph
is a later generalization.

### M3 — PROGRAM-TRANSITION-DB (global, site-independent)
Database of observed program-to-program transitions (warehouse→loft→housing…), each with
preconditions (structure span, floor height, zoning class), cited built examples, and an
**estimated** likelihood tier. Type vocabulary aligned with ProgramFormat categories.
Covers agents 7 (Program Evolution) and 8 (Building Adaptability).

### M4 — FORECAST (per site, regenerated when M1–M3 change)
The only LLM step. A Claude Code session reads M1+M2+M3 and writes 3–5 **scenario cards**
(drivers, risks, horizon, program mix) each carrying a ProgramFormat draft validated by
`program-auditor`. Covers agents 9 (Scenario Planning) and 10 (Design Strategy).
Runs offline (C3); the prompt + inputs are archived alongside the output for reproducibility.

### M5 — UI integration
- `program-input.html`: a "Site Forecast" entry that loads scenario data (`<script src>`
  from `NEXA/intel/data/`), shows scenario cards, and applies a card's ProgramFormat draft
  through the existing flow into shortfloor.
- Optional standalone timeline page (`NEXA/intel/timeline.html`): 1900→2050 axis with
  scenario branching, for research presentation.

Agents 11 (Spatial Generation) and 12 (Evaluation) of the original proposal are the
**existing platform** (shortfloor + code-check panel + program-auditor). Agent 1 (Intent)
is the wizard's existing input step, extended with target-year / priority fields.

## 4. Traceability — original 12-agent proposal → this architecture

| Proposal agent | Here |
|---|---|
| 1 Intent | M5 (wizard fields) |
| 2 Site Intelligence | M1 |
| 3 Urban Evolution ⭐ | M2 |
| 4 Regulation | M1 (`regulation` section) |
| 5 Market & Demographic | M1 (`market` section) |
| 6 Climate & Infrastructure | M1 (`climate` section) |
| 7 Program Evolution ⭐ | M3 |
| 8 Building Adaptability | M3 (`preconditions`) |
| 9 Scenario Planning ⭐ | M4 |
| 10 Design Strategy | M4 (`strategy` field per scenario) |
| 11 Spatial Generation | existing shortfloor — untouched |
| 12 Evaluation | existing code-check + program-auditor |

## 5. Task ownership

| Work | Executor |
|---|---|
| M1/M2 research (per site, one-shot) | general-purpose agent + WebSearch, human-reviewed citations |
| M3 authoring | main session (research-heavy, judgment-heavy) |
| M4 ProgramFormat drafts | program-planner |
| M4 draft validation | program-auditor (mechanical) |
| M5 UI edits | main session; visual-verifier screenshots |

## 6. Upgrade path (deferred, designed-for)

Each module's schema doubles as a future agent's I/O contract. When the API socket is
added (post-N4, per C3): M4 becomes a runtime call (wizard → API → scenario JSON of the
same schema); M1/M2 refresh becomes a scheduled research agent. Nothing in N1–N4 may
assume this exists; nothing may block it either — hence "same schema offline and online"
is the design rule.
