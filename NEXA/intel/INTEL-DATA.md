# NEXA Intel — Data & Knowledge Architecture

Created 260712. Status: **design document (N0)**. Schemas here are the contract for
N1–N3 deliverables; change them here first, then regenerate data.

## 0. Delivery format (constraint C3: file:// safe)

All machine data ships as `.js` files in `NEXA/intel/data/`, loaded by `<script src>`:

```js
// NEXA/intel/data/site-citymarket.js
window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.sites = window.NEXA_INTEL.sites || {};
window.NEXA_INTEL.sites["citymarket-la"] = { dossier: {...}, timeline: {...}, scenarios: [...] };
```

Each `.js` data file has a human-readable MD companion (same basename) holding the
cited prose report. The MD is the citable research artifact; the JS is the UI feed.

## 1. Confidence tagging (constraint C5 — applies to every fact)

```js
{ value: <any>, source: "short citation", url: "…", accessed: "YYMMDD",
  confidence: "verified" | "reported" | "estimated" }
```

- **verified** — primary source seen (official plan, ordinance, ZIMAS record, archival map)
- **reported** — secondary source (press, developer marketing) not independently confirmed
- **estimated** — our judgment; must say what it was based on

A fact with no source is written as `{ value: null, confidence: "unknown" }` — never guessed.

## 2. SITE-DOSSIER schema (M1)

```js
dossier = {
  meta:     { name, address, apn: [], areaSqm, accessedRange },
  physical: { parcelGeometry, siteArea, existingFootprint, existingGFA, far, heightLimit, easements },
  urban:    { streetHierarchy, transitStops: [], walkability, bikeNetwork, parkingSupply },
  environmental: { solarOrientation, windNotes, noiseSources: [], topography, floodRisk, heatIsland },
  context:  { adjacentUses: [], publicSpace: [], culturalDistricts: [], institutions: [] },
  regulation: { zoning, communityPlan, overlayZones: [], far, height, setbacks, parkingReq,
                historicStatus, affordableHousingBonuses, pendingRezoning },
  market:   { population, income, age, employmentBase, housingDemand, officeVacancy,
              retailDemand, tourism, creativeIndustry },
  climate:  { heatProjection, floodProjection, waterEnergyNotes, transitInvestment, resilienceOpportunities }
}
```
Every leaf is a confidence-tagged fact object (§1). A section left `null` is honest;
a section filled without sources is a defect.

## 3. SITE-TIMELINE schema (M2 — Temporal Knowledge Graph)

```js
timeline = {
  nodes: [{
    id, kind: "program"|"building"|"regulation"|"transit"|"economy"|"society"|"climate",
    label,                        // e.g. "Wholesale produce market"
    tStart, tEnd,                 // year (int); tEnd null = ongoing; future = projection
    epoch: "past"|"present"|"future",
    facts: [ <confidence-tagged> ]
  }],
  edges: [{
    from, to,                     // node ids
    relation: "succeeded_by" | "caused" | "enabled" | "constrained" | "coexisted",
    note
  }]
}
```

Rules: every node ≥1 source (future nodes cite the plan/policy that projects them);
`succeeded_by` chains must be temporally consistent (`from.tEnd ≤ to.tStart + 5y` overlap
tolerance); the site's program succession chain is the spine, other kinds attach via
`caused`/`enabled`/`constrained`.

## 4. PROGRAM-TRANSITION-DB schema (M3, site-independent)

```js
transitions = [{
  from: "warehouse", to: "housing",         // ProgramFormat-aligned type vocabulary
  likelihood: "high"|"medium"|"low",         // ESTIMATE — tier, not a percentage
  basis,                                     // one sentence: why this tier
  preconditions: { structure, span, floorHeight, core, mep, zoningClass, other },
  blockers: [],
  examples: [{ project, city, yearFrom, yearTo, source, url }]  // ≥1 required
}]
```

Design decisions: (a) likelihood is a **tier with a stated basis**, not a fake percentage —
we have no transition-frequency dataset (C5); (b) the type vocabulary is the union of
ProgramFormat categories + common urban types (warehouse, factory, parking, mall, church…)
with an explicit mapping table to ProgramFormat categories at the top of the file.

## 5. SCENARIO CARD schema (M4 output)

```js
scenarios = [{
  id, name,                        // e.g. "B — Entertainment District"
  horizon,                         // target year
  likelihoodNote,                  // qualitative + basis; never a bare number
  drivers: [ <node ids from timeline + dossier refs> ],
  risks: [],
  strategy: [],                    // design-strategy directives (modular, expandable, …)
  programMix: [{ type, share }],   // shares sum to 1
  programFormatDraft: "…",         // full ProgramFormat text, program-auditor-validated
  generation: { promptFile, inputsHash, date }   // reproducibility record
}]
```

## 6. Pilot site: The City Market of Los Angeles (Fashion District, DTLA)

Everything below is a **research seed for N1** — facts marked `reported` until N1
verifies them against primary sources. Known outline: founded ~1909 as a wholesale
produce market (immigrant merchant shareholders); produce operations declined late
20th c.; partial adaptive reuse as "City Market South" creative office/retail (~2010s);
a multi-phase mixed-use master plan (office/residential/hotel/retail/education) has been
in entitlement since the 2010s; site sits inside the DTLA 2040 community plan area.
This succession (market → decline → creative reuse → planned mixed-use) is exactly the
program-evolution story the platform studies.

Source inventory for N1:

| Domain | Sources |
|---|---|
| Parcel / zoning | ZIMAS, LA City Planning (DTLA 2040 adopted plan + zoning code), LADBS records |
| Historic maps / buildings | Sanborn maps (LAPL), LA Conservancy, Water & Power Associates, USC/LAPL photo archives |
| Entitlements | LA City Planning case files (EIR for City Market redevelopment), council files |
| Demographics / market | Census/ACS, SCAG growth forecast, DTLA market reports (press-tier) |
| Transit | Metro plans (existing A/E lines proximity, future projects), LADOT |
| Press timeline | LA Times archive, Urbanize LA, The Real Deal (all `reported` tier) |

## 7. File layout

```
NEXA/intel/
  INTEL-ARCHITECTURE.md   INTEL-DATA.md   INTEL-ROADMAP.md      (design docs, N0)
  data/
    site-citymarket.js    site-citymarket.md                    (N1)
    transitions.js        transitions.md                        (N2)
    scenarios-citymarket.js  scenarios-citymarket.md            (N3, M4 output)
  prompts/                                                       (N3, archived M4 prompts)
  timeline.html                                                  (N4, optional)
```
