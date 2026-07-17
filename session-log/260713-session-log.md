# 260713 Session Log

## ⚡ SESSION HANDOVER — what is DONE vs NOT DONE (written at session end, low usage)

**Done and verified this session (details in the sections below):**
back-navigation on all input stages (arrow buttons, wizard + review) · skip-link removed ·
second site 130-college-st (dossier/timeline/4 scenarios) · multi-site forecast panel with
tabs + `?site=` hook · lane-chart history (coexisting programs on separate rows, arrows only
on documented succession) · fc-sub paragraph removed · **Site Scout G1–G3 complete**
(`NEXA/intel/site-scout.html`: geocode → parcel select → zoning/overlays → OSM surroundings
→ snapshot export; 13/13 CDP checks) · zoning backfill for BOTH sites · validator + 28/28
interaction suite green. Backups: program-input.html.bak-260712 still current enough
(pre-feature); no backup taken 260713 — **take one before the next edit session.**

**NOT done — the open queue, in priority order:**
1. **DTLA 2040 code-reading pass** — we now hold mapped codes ([CX2-FA] College St,
   [IX3-FA] City Market) but deliberately did NOT interpret what they permit. This gates
   scenario A plausibility on both sites. One research task: read the DTLA 2040 zoning
   code (use districts CX2/IX3, form G1/SH1, FAR/height tables) and update both dossiers.
2. **ZIMAS human verification** — promote the machine-fetched (`reported`) zoning/APN facts
   to `verified`; also resolve: College St assemblage APNs, TOC tier, whether College
   Station is truly across the street, CASP boundary (College St), FAR/height for both.
3. ~~G4: scout entry link~~ **DONE at session end** — "▸ scout a new site" added to the
   forecast panel header (next to ✕ close), opens site-scout.html in a new tab. Added after
   the user reported "no results": the tool worked, but had NO entry point in the UI.
   Also confirmed by file:// screenshot: scout works from file:// too (geocode, parcels,
   zoning, overlays all returned); only Overpass was rate-limited at that moment — its
   red "retry in a minute" message is the panel working as designed, not a failure.
**Late addition (user request): zoning-envelope basics in the scout.** `interpretZone()`
parses the mapped zone string: LEGACY codes (M2-2D…) → use-district description +
FAR/height derived from the LAMC 12.21.1 height-district table (rendered + exported as
ESTIMATED tier, with the "D-limitation overrides" warning); DTLA 2040 NEW-FORMAT codes
([DM2-G1-5][CX2-FA][CPIO]) → parts named (form · use · overlay) and numbers **refused, not
guessed** — the new code's tables aren't encoded; panel says to read the form-district
standards. Lot coverage: honestly shown as not-a-citywide-control. Smoke-tested at 130
College (new-format branch renders); legacy branch is a pure lookup, untested live — try
an address in an M2-2/C2-1L area next session.

4. **Scout niceties not built:** land-use mix ring (only POI composition bar exists);
   Overpass retry/backoff (single attempt + message); no CDP test for the non-LA path.
5. **N4 (optional, from the original roadmap):** standalone timeline visualization page.
6. **transitions.md URL-resolution pass** — examples cite publications, urls are null.
7. **130-college-st N1 completion** — the original research was cut by an API outage;
   pre-2023 parcel history (Sanborn/LAPL) and case numbers (ENV/CPC) never gathered.
8. Old open item (260712): `MODULE-TOOLS/structure-zone-test.html` header still says "VORO".
9. **API socket** — still deferred by user decision; C3 as amended 260713 stands.

**Where things live:** platform = root pair; intel = `NEXA/intel/` (INTEL-*.md docs,
data/*.js, site-scout.html, prompts/); tests = scratchpad `cdp-test.js` (28 interaction
checks), `cdp-scout-test.js` (13 scout checks), `validate-intel.js` (data validator) —
scratchpad is session-bound, so they were **copied into TEST/ at session end**:
`TEST/_cdp-interaction-test.js` (28 checks) · `TEST/_cdp-scout-test.js` (13 checks) ·
`TEST/_validate-intel.js` (data validator) · `TEST/_server-8099.js` (static server).
Run: `node TEST\_server-8099.js` (background) then `node TEST\_cdp-*.js`. Note the two CDP
scripts still reference scratchpad paths for their screenshot output — trivial to repoint.

## Site Scout — address → GIS analysis tool (planned, approved, BUILT same session)

User asked for "輸入地址就能載入基地以及基地周遭分析(gis?)". Plan confirmed via three
decisions: standalone page · LA-deep + US-shallow coverage · G1–G3 in one pass.
**C3 amended (user-approved):** public GIS endpoints allowed, but only inside the scout
tool; LLM runtime API still forbidden; forecast data layer stays offline.

### Endpoint probing (6 node probes before writing any UI — all documented in scratchpad)

| Endpoint | Verdict |
|---|---|
| US Census geocoder | works, US-only, primary |
| Nominatim | works, fallback, needs UA |
| **LADCP Zoning (GeoHub hosted)** `services5.arcgis.com/7nsPwEMP38bSkCjy/.../Zoning/FeatureServer/15` | **CORS \*, works everywhere** — field `Zoning`, `CATEGORY` |
| LA County parcels `public.gis.lacounty.gov/.../LACounty_Parcel/MapServer/0` | works; CORS echoes http origins but NOT `file://` |
| City Planning overlays `maps.lacity.org/lahub/.../City_Planning_Department/MapServer` (HPOZ 10, SpecificPlan 19, AdaptiveReuse 6) | works; same CORS caveat |
| Overpass | works with a meaningful User-Agent (browser sends one automatically) |

Traps found by probing: geocoded points sit on the **street centerline** → point queries
need `distance=` and zoning should be re-queried at the **parcel centroid**; exact
situs-address WHERE queries are unreliable → the UI lists parcel candidates and the user
clicks the right one (auto-pick scores house number + street name — proximity alone
selected a Main St parcel).

### Built: `NEXA/intel/site-scout.html` (single file, Leaflet CDN)

Address (`?addr=` hook) → geocode → map with marker + 400/800 m rings → parcel candidates
(click to select, polygon highlighted, regulation re-queried at centroid) → zoning +
HPOZ/specific-plan/adaptive-reuse panels → OSM surroundings (nearest rail + distance, bus
≤400 m, food/retail ≤400/800 m, schools, nearest park, POI mix bar) → **export**: downloads
a schema-correct `site-<slug>.js` dossier skeleton, every machine-fetched field
`reported`-tier with source + accessed date, timeline empty pending N1. Test hook
`window.__scout`. CDP acceptance test (scratchpad `cdp-scout-test.js`): **13/13 PASS**
live at 130 W College St — auto-picked parcel 5409-008-002 (114 W College), zoning
fetched, snapshot evals as valid JS.

### The backfill — real findings for both existing sites (queried 260713, reported tier)

- **130 College block (all 9 parcels):** mapped zoning **[DM2-G1-5] [CX2-FA] [CPIO]
  'Commercial-Mixed'** — a **DTLA 2040 new-format code**, superseding the 2023 press
  framing (GPA + zone change under legacy M2). Overlay hits: CORNFIELD/ARROYO SECO
  specific plan (boundary caution — centerline point) + Downtown Adaptive Reuse Program.
  APN 5409-008-002 = 114 W College measured; assemblage APNs still unestablished.
- **City Market (San Pedro St parcels):** mapped zoning **[DM1-SH1-5] [IX3-FA] [CPIO]
  'Industrial-Mixed'** — **IX3, NOT the IX2** the 260712 research generalized; FASHION
  DISTRICT specific plan + Adaptive Reuse Program overlays. The IX2-tension caveat is
  reworded in dossier + scenario A risk + both .md files. What IX3-FA/CX2-FA permit was
  deliberately NOT interpreted — flagged for a code-reading pass.
- Per the regen rule, both scenario files' `generation.inputsHash`/`date` updated to the
  new site-file hashes; scenario A notes annotated (College St: "zoning does not allow it"
  premise now *uncertain*, not supported).

⚠️ Process lesson: a PowerShell `Get-Content|-replace|Set-Content` roundtrip **corrupted
UTF-8 punctuation** (— → ≤ ⚠ became `??`) in scenarios-collegest.js; caught via the
file-change diff and fixed by a full clean rewrite. Use node or the Edit tool for
content edits, never PS text roundtrips.

Verification after backfill: mechanical validator (2 sites, 8 scenarios, 19 transitions)
ALL PASS; platform interaction suite 28/28 PASS. Scout page screenshot read.


## Second site added to the Intel layer: 130 W. College Street (LA Chinatown)

User asked for a new site. Disambiguated first (130 College St exists in New Haven and
Toronto too) — user confirmed **LA Chinatown**.

### Platform: single-site → multi-site (program-input.html)

- `initSiteForecast()` no longer hardcodes `citymarket-la`; it enumerates
  `window.NEXA_INTEL.sites` and renders a **site-tab switcher** (`#fc-tabs`, hidden when
  only one site is loaded, so the previous behaviour is unchanged for a single site).
  **Adding a site = adding two `<script src>` tags; no JS edit.**
- New URL hook `?site=<key>` alongside `?forecast=1` / `?forecast=<id>`.
- `TEST/_forecast-test.html` now takes `?site=<key>&id=<scenario>`.
- **Spine now follows `succeeded_by` edges, not "all program nodes".** Two consequences,
  both driven by this site's data: (a) a program node in no succession chain is excluded —
  *China City* (1938–48) was the **rival** replacement for Old Chinatown that failed, not
  this site's successor; (b) consecutive nodes with no succession edge get a dashed `⇢`
  at 50% opacity instead of a solid arrow — the College St record changes resolution
  (district → parcel) between 1938 and 2023 and must not pretend to be continuous.
- Display names strip the parenthetical qualifier (`meta.name` for this site is a
  sentence; tabs and titles need a label).

### Data (NEXA/intel/data/)

- `site-collegest.{js,md}` (research agent) — site key `130-college-st`, **24 nodes /
  28 edges**. Spine: Old Chinatown (1880s–1933) → New Chinatown / Central Plaza (1938–)
  ⇢ surface parking lot (present) → 2023 Grimshaw creative-office proposal.
  Key facts: the parcel is a **surface parking lot beside the Metro A Line Chinatown
  station** (opened 2003, sits above College St); Riboli family proposed ~225,000 sf,
  5 storeys, March 2023; in environmental review, **needs a General Plan Amendment + zone
  change**.
- `scenarios-collegest.{js,md}` + `prompts/260713-scenarios-collegest.md` — 4 scenarios:
  **D** entitlement stalls / lot persists (2029, the null hypothesis) · **A** proposed
  office build-out (2030) · **B** housing pivot (2034 — transition DB's *high* tier, and
  College Station's 725 approved units across the street prove it on this block face) ·
  **C** community anchor, affordable housing + market hall (2038, subsidy-gated).

### ⚠️ Evidence quality — carried in both the .js header and the .md

The N1 run was **cut short by an API outage**. ZIMAS, the case file, the Central City North
plan page and the TOC guidelines were never queried, so **site-collegest.js contains no
`verified`-tier facts**: zoning string, FAR, height district, lot area, TOC tier are all
`unknown`. The scenarios are therefore **programmatic hypotheses, not capacity studies** —
no GFA in them is a zoning yield. Also unconfirmed: whether College Station is across the
street (address parity says yes) or on this parcel; which community plan governs
(Central City North vs DTLA 2040). **Verifying the zoning is the highest-value next action.**

### History strip → LANE CHART (user: "為什麼 2023 之前有這麼多支線")

The user was right and the diagnosis was structural, not cosmetic: the old single-line
spine was chaining programs that **coexisted in time**, which asserts a succession the
record does not contain. New Chinatown (1938–) is still running; the parking lot (2023–)
and the office proposal (2023–) are concurrent, not sequential.

`#fc-spine` is now a CSS-grid lane chart:
- **column** = rank of the start year (not array index),
- **row** = first lane with no *interval* overlap (two-sided test, not just "ends before"),
- **arrow** = drawn (`.succ::after`) only where a `succeeded_by` edge actually links two
  neighbours on the same row, one column apart. No edge ⇒ no arrow. No faked continuity.
- **Chain-first lane assignment:** succession-chain nodes are placed before the rest, so
  the site's real lineage holds the top row. Without this, *China City* (1938–48, the
  rival replacement that **failed**) sorted ahead of New Chinatown and stole the primary
  lane — a rival was being drawn as the site's successor.
- Coexisting non-chain nodes are re-included (they were previously dropped) and shown
  dashed at 75% opacity with a tooltip: "coexisted — not a step in its succession".

Result: City Market (two non-overlapping programs) still renders as one clean line with an
arrow; College St renders three rows — lineage on top (Old Chinatown → New Chinatown →
parking lot), China City dashed below, the 2023 office proposal on its own row.
`ARROW` const removed (dead after this change).

### Back-navigation on every input stage (user request)

Previously the wizard was one-way: a wrong answer meant "↺ start over" (which discards the
draft). Added:
- **Wizard steps:** back is a **mirrored twin of the Enter arrow** (`.btn-send` geometry,
  path reversed), sitting **left of the active input row** — `#input-wrap` is now a flex row
  reading `←  [ input ] →`. Outlined (transparent + `--ink-border`) rather than filled,
  because it sits on the blue field and must not compete with Enter. Hidden on step 1.
  It shows on all of steps 2–4 (number row, floors row, and left of the Continue button). Answers are now
  kept as **data** (`answered[]`), not only as DOM rows, so a revisited step **prefills its
  previous value** (GFA) and the answered-rows list re-renders from `answered.slice(0, step)`.
  Answers *ahead* of the current step are kept, not deleted — stepping forward re-confirms
  and overwrites them. `loadStep(i)` now owns `step` (single source of truth); `submit()`
  no longer increments it independently.
- **Review stage ("Draft program — floor by floor"):** the same arrow button, as the
  **first element of the footer bar** (far left, before the stats), outlined in the dark
  border colour since the footer is white (`.btn-back-arrow-light`). It **keeps the draft**
  (commits any open inline edit first) — unlike "↺ start over", which discards it.
- **`Skip → open visualizer` link removed** from the footer (user request); its CSS deleted too.
- **Forecast-aware return:** `reviewOrigin` ('wizard' | 'forecast') is tracked and persisted
  in the draft. A draft applied from a scenario returns to the **forecast panel**, not into
  the wizard. `initSiteForecast` exposes `openForecast()` for this.
- `fc-close` now restores the wizard behind it when no draft is in review.

### Verification tooling: CDP interaction test (new)

Screenshots cannot click. No puppeteer in this repo — so the test drives headless Edge over
**CDP directly** using Node 24's built-in `WebSocket` + `fetch` (zero deps):
`scratchpad/cdp-test.js` → spawns Edge with `--remote-debugging-port`, evaluates JS in the
page, clicks real buttons, asserts DOM state. **28/28 checks pass**, covering: back hidden on
step 1, back through steps 3→2→1, GFA prefill on revisit ("9000"), answered-row count
shrinking, review→back→wizard with answers intact, forecast→apply→back→**forecast** (not
wizard), fc-close→wizard, site-tab switching re-rendering the spine.
Worth keeping — this is the first test in the repo that exercises behaviour, not pixels.

### Verification

- Validator extended to both sites (scratchpad `validate-intel.js`): JS loads, no dangling
  or duplicate node ids, every node sourced, succession chains temporally consistent,
  **every scenario `driver` resolves to a real timeline node id**, ProgramFormat grammar,
  category ∈ {public,private,circulation}, ≥3 fire-stair cores/level, |w·h−area|/area ≤10%,
  mix sums = 1, level contiguity → **ALL CHECKS PASS** (2 sites, 8 scenarios, 19 transitions).
- Headless Edge: College St forecast panel (tabs, 4-node spine with the dashed gap,
  4 option cards), City Market panel still correct, and `_forecast-test.html?site=130-college-st&id=B`
  → shortfloor massing renders (8,649 m², 9 floors). Server stopped, profiles cleaned.

## Floor labels: 1-indexed display (user request "不要有L0")

Internal levels stay 0-indexed everywhere (ProgramFormat, localStorage, layout); only the
**display** shifts: ground = L1, level 2 = L3, basements = B1/B2 (unchanged).
- `program-input.html`: `levelLabel()` / `levelSub()` (one change covers wizard "add to",
  review floor rows, ft-range, SHORT-floor list).
- `program-massing-shortfloor.html`: new shared `levelLabel()` helper (mirrors input page),
  applied to the levels stat row, code-check violation rows, exit-shaft ranges, hover
  tooltip, and the OBJ export group names (`..._L1`, `..._B1` — note: downstream parsers of
  OBJ names see 1-indexed labels now).
- Trap found while verifying: College St scenario B has a basement (level −1); naive `+1`
  displayed it as **L0** — exactly what the user banned. Hence B-notation in shortfloor too.
- Verified: 28/28 interaction suite still green; new CDP label check (scratchpad
  `cdp-label-check.js`) — levelLabel unit evals + full-page innerText scan for `\bL0\b` on
  both pages, exit shafts render `B1–L8`. ALL PASS.

## Space-quantity audit of all 8 scenario drafts (user: "確認一下空間量夠嗎")

Mechanical audit (scratchpad `space-audit.js`) of both sites' programFormatDrafts against
ProgramFormat core rules + RESTROOM-GUIDELINES + validator conventions. Verdict:
- **Totals/floors consistent** — plates 700–1,250 m², levels contiguous, w×h ≤10%,
  circulation 13–26%, 3 cores on every floor of every scenario. Slices are slices by
  declaration (College A = 6,973 m² study slice of the ~20,900 m² real proposal).
- **2 real gaps** (public program on a floor with no toilets): College-St **B level 7**
  (lounge bar 154 m²) and **C level 5** (meditation room 103 m²). Fix = add one
  `{toilets}/{80}` cluster each. NOT yet fixed — user decision pending.
- **1 softer gap:** City-Market **B level 3** is a 3×278 m² office floor with no toilets
  (College-St A puts toilets on every office floor — inconsistent generation).
- **Spec-scale conflict, all 8 scenarios:** every core is 40 m² vs ProgramFormat's
  120–250 m² — but that rule was calibrated at TPAC scale; 3×150 m² on a ~1,000 m² plate
  eats half the floor. Rule needs a small-floorplate variant rather than data edits.
- Housing floors (in-unit baths) and basements (parking/mech) without toilets: acceptable.
- Separate but adjacent: shortfloor's S4 check fires on these drafts ("2/3 cores") — the
  layout generator only places 2 shafts though the program defines 3; egress count is
  satisfied in data, dropped in visualization.
