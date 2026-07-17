# 260707 HANDOFF — program 量體排列 pipeline (read this first, then continue)

**Audience:** a cold-start Fable session asked to keep improving the program-massing pipeline.
**State:** everything below is LIVE in the files as of 260707 end-of-day. Line numbers were true at write time — re-grep before editing, don't trust them blindly.
**Read next if needed:** `260707-session-log.md` (full chronology), `agentops/LESSONS.md` (today's 3 new lessons), G-LETTER item 3 (UPDATED screenshot recipe — use `Start-Process -Wait`, never `&`).

---

## 1. The pipeline

```
program-input.html  (wizard → deterministic generator → review UI)
        │  Build → localStorage['programInputText'] → ?src=input
        ▼
program-massing-shortfloor.html  (parse → computeShortFloors → computeLayout → buildShortBlocks/structure)
```

- Program line format: `{type}/{area m²}/{level}/{category}/{w,h}` (spec: references/ProgramFormat.txt).
- Classifiers `isShort/isCore/isCorridor` + `SHORT_THRESHOLD=0.5` are DUPLICATED in both files with "keep in sync" comments (program-input.html ~:522-529). Never fork them.
- A floor collapses to an 8'-6" SHORT storey when SHORT share of packed (non-core, non-circulation) area **> 0.5** (`computeShortFloors`, shortfloor ~:456-466). Cores/circulation are excluded from the share; **toilets are NOT excluded** (they count as packed LONG — this drove today's filler-budget math).
- shortfloor's built-in SAMPLE (~:1623-1733) is the untouched reference fixture (keeps old 201/161 cores, stats 14,272 m², 3 SHORT floors L1-L3). Regression checks compare against it; do not edit it casually.
- Floor labels: generator levels are 0-indexed (0 = GL); the visualizer displays `L(level+1)` (GL = L1).

## 2. Current generator rules (program-input.html, all in `generateEntries`)

Today's six-task chain replaced the old "PACK_TARGET consecutive 100%-SHORT floors" logic. Current rules:

1. **SHORT band spread** — activity lines spread over up to 4 lower levels (GL upward), whole lines only, per-level area targets weighted 4:3:2:1 via `splitBins()`; affinity order derived from ACTIVITY_GROUPS (coffee + Show&event → lowest, Learning, Wellness, lounge bar last). Band shrinks 4→1 for sparse selections; GL joins only when its SHORT bin clears the fixed GL anchors (lobby 180 + sales 220 + toilets 80) with taper headroom, else band starts at level 1.
2. **>0.5 guarantee** — every band level's SHORT share (POST-scaling, serialized areas) must be strictly > 0.5 and strictly decreasing upward, so all band floors collapse in the visualizer. Adaptive LONG filler + toilets are budgeted per level: `fillerBudget = short_i·(1-s_i)/s_i − 80(toilets)`; a bin too small to carry its toilet merges downward.
3. **Toilets** — one RIGID 80 m² toilets line (public) on every band level; GL keeps its own.
4. **Three-tier scaling** (replaced uniform gfa/rawTotal):
   - RIGID (exact preset, never scaled): 3 core types, circulation 107, toilets 80, parking 322, mechanical 161, electrical 54, loading 161.
   - CALIBRATED (clamp ×0.85–1.15): activities, apartment units, lobby, sales, staff, it, storage.
   - SPONGE (absorbs remainder): office plates (≥300 each), band filler (≥54 office / unit-decomposed housing / may drop to 0), housing plates emitted as standard-unit mixes (67/107/134; no residential line > 160).
   - Two-pass solve (`buildAttempt`); each line carries a `tier` tag + `rawA`. All 9 harness cases land within ±2% of GFA target.
5. **Cores = 17'×25'-6" ≈ 40 m²** (user spec 17'×25'; 25' isn't module-true → 3 modules). `addCores` (~:805) is the SOLE emission site: freight 40, passenger a 40, passenger b 40. shortfloor resolves core footprints from AREA ALONE (ignores emitted w,h) → 40 m² ⇒ exactly 2×3 modules (proven in replica).
6. **Adaptive core count** — passenger core b emitted only when `gfaTarget/floorsAbove ≥ 1400` (12000/8F → 3 cores; 12000/10F → 2, matching SAMPLE).
7. **Color palette** — aligned to house scheme: bg #F5F5F5, blue #172FC7, orange #E67033 (SHORT/public), yellow #EEC341 = circulation (`.pill.circ`); mirrors CAT_COLOR in the massing platforms.

Current expected defaults (mixed-use / 12000 / 8F / 2B / ALL activities): calibScale 1.15 (clamped), plates 834×2, total 12,001, band levels 0-3 shares .678/.654/.602/.531, circulation stat 2,270 m², visualizer shows **4 SHORT floors L1-L4**.

## 3. Current layout rules (program-massing-shortfloor.html, `computeLayout` region ~:285-412)

The massing is a double-loaded corridor bar: central 8'-6" circulation spine along x, program rooms on north/south sides, two cores as continuous vertical shafts (south band + north band).

Today's three-task chain (each backed up in BACKUP/ before edit):

1. **Interlock gate un-hardcoded** (`…-preStackFix.html`): the "LONG hugs core / SHORT pushed out" ordering was pinned to `lv 0-2` (SAMPLE relic) → now `clusterFloor(lv)` = floor carries SHORT and a vertically-adjacent floor does too. Plus `splitSides` SHORT-anchor repair: a lone SHORT stranded opposite a lone LONG gets the LONG merged onto its side. WHY IT MATTERS: the weave (program interlock ~:1047-1075 and vertical 1:2 module spans) fires ONLY where consecutive floors' SHORT footprints share plan columns (`footByFloor[t].has(key) && footByFloor[t+1].has(key)`, ~:1061).
2. **Compact common-anchor packing** (`…-preCompactFix.html`, packSide ~:363-385): both side bands pack ONE contiguous row from x=0 (option-B core-skip generalized to both CORE_OPTIONs); on clusterFloor floors SHORT packs FIRST from the anchor end (nests the taper → strong cross-floor overlap). Fixed the old dual-corner packing that scattered sparse floors across a half-empty envelope.
3. **Core float minimization** (`…-preCoreAnchor.html` + `…-preCoreAnchor2.html`, ~:343-368): coreN x = 1-D scan minimizing Σ above-grade `max(0, coreNx − nW(lv))`, subject to non-adjacency + c2c ≥ ⅓·widest-floor; floors wider than coreNx WRAP the core via the core-skip. coreS stays left-anchored. FW recomputed two-pass from actual packed extents. Iter-1 (anchor to max band width) was a dead end — packing can wrap cores, so the core needn't clear the widest floor.

**Accepted trade-offs (do not "fix" without re-reading the numbers):**
- all-case L1→L2 SHORT overlap 0.708→0.679 (one interlock cell): proven mutually exclusive with core-touch ≥ 50% (probe scan). Weave visually intact.
- Egress separation uses the SOFT reading (non-adjacency span + ⅓ widest floor), not c2c ≥ cwS+cwN+1 — the literal reading is infeasible vs float targets. Massing study, not code compliance.
- Inset CORE_OPTION intentionally violates "sep ≥ ½ occupied" (it centralizes cores by design).

## 4. Verification kit (tools copied into `session-log/260707-tools/`)

- `genlib.js` — loads the LIVE `generateEntries` + validators out of program-input.html (`loadGenerator(path)`), so edits are picked up automatically. Injects global classifiers.
- `harness.js` — 166 assertions over a 9-case matrix (selections × building types × 10F 2-core case): rigid presets exact, toilets per band level, post-scaling shares >0.5 & decreasing, no residential >160, validateLine on all, GFA ±2%.
- `replica3.js` — layout replica (splitSides/packSide/core scan copied from shortfloor) + metrics: SHORT cross-floor overlap per pair, core float mean/max/touch%, intra-band gaps, egress. `--iter1` flag + `FORCE_NX` scan hook.
- `audit.js` — per-type scaled-area audit (the tool that caught the core/toilet/parking problems).
- `repro2.js` — generates case texts + writes a repo-root `_handoff-test.html` (localStorage → `?src=input`) for end-to-end screenshots. DELETE the helper after use.
- Run from the tools dir: `node harness.js` etc. (paths inside point at the repo copy of program-input.html — check the `loadGenerator(...)` argument if the repo moved).
- Screenshot recipe: **G-LETTER item 3 (updated 260707)** — `Start-Process -Wait`, fresh `--user-data-dir` per shot, delete the profile after, stop the http.server when done, structure mode needs budget 25000-30000.

**Regression floor for any future layout change:** harness green + overlap pairs not below {all: .679/.792/.750, learning: 1.0, SAMPLE: .821/.957} + SAMPLE stats identical (14,272 / 3 SHORT L1-L3) + structure mode zero console errors.

## 5. Backups made today (BACKUP/, this repo has no git)

`program-massing-shortfloor-260707-preStackFix.html` · `…-preCompactFix.html` · `…-preCoreAnchor.html` · `…-preCoreAnchor2.html` · `G-LETTER.md.bak-260707`. (program-input.html has no same-day backup — its generator was rewritten incrementally with harness cover; copy one before the next big edit.)

## 6. Open items / next candidates

1. **Sparse-selection affinity wrinkle:** with e.g. only {exhibition, coffee}, affinity puts coffee(161) below exhibition(268) → SHORT raw not decreasing across those two floors (band then collapses to 1 level by design). Cosmetic; revisit if a user case hits it.
2. **Egress hardening:** if the massing ever needs code-plausible exits, revisit the ⅓-width soft rule and the inset exemption.
3. **Housing filler realism:** filler decomposes into standard units now, but unit MIX per floor isn't balanced against the main housing recipe (e.g. a floor can end up all-2b2b). Low priority.
4. **program-input backup discipline:** see §5.
5. FOAM module remains paused (fall through to FRAME) — unrelated to today's work.
