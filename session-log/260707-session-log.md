# 260707 — Session Log

> **Continuation entry point: `260707-HANDOFF.md`** — current-state rules for the whole program-massing pipeline (generator tiers, layout/interlock/core rules, verification kit in `260707-tools/`, regression floors, open items). Entries below are chronology; the handoff is the map.

## program-input.html — SHORT floor distribution rework (delegated to opus subagent)

- Replaced the `PACK_TARGET`/consecutive-100%-SHORT packing (old :821-841) with a spread rule mirroring the shortfloor SAMPLE taper: SHORT levels = 0..min(3, floorsAbove-1) (1F–4F, GL = level 0), capped by activity-line count.
- Whole activity lines fill greedily against 4:3:2:1 per-level area weights; floor-affinity order derived from ACTIVITY_GROUPS (coffee + Show & event → GL, Learning → L2, Wellness → L3, lounge bar last).
- SHORT levels ≥1 get partial LONG main-use filler (office 400 / housing 348) via shared `useHousingAt`; main-use-only floors resume after the mixed band.
- Default case (mixed-use, 12000 m², 8/2, all activities): SHORT per level 748/587/413/101 m², share 0.674/0.660/0.611/0.251 — levels 0-2 remain 8'-6" floors (>0.5), level 3 carries plug-ins on a normal floor (matches SAMPLE's lounge-bar-on-L6 pattern).
- Verified by node harness (scratchpad/harness.js, 13/13 assertions: distribution, monotonic taper, validateLine on all serialized lines, GFA ±2%, zero-activity path unchanged) + headless-Edge screenshot.
- Known wrinkle (accepted): sparse selections (e.g. only exhibition+coffee) can put the larger line on L2 due to affinity ordering, and diluted floors may fall under the 0.5 threshold.

## program-input.html — SHORT band threshold fix (delegated to opus subagent)

- Bug: handoff massing collapsed only ONE floor to 8'-6" (user report). Confirmed root cause by end-to-end repro (localStorage helper page + headless Edge, before-fix: ALL keys → 3 floors, one activity group → 1, sparse → 0): the fixed 480 m² ground anchors + fixed 400/348 m² per-level LONG filler diluted SHORT share below the visualizer's >0.5 collapse threshold (computeShortFloors, shortfloor:456-466).
- Fix (program-input.html:823-925): `splitBins()` picks the largest n≤4 with strictly-decreasing whole-line bins; ground joins the band only when its bin clears the anchors with taper headroom (else band starts at level 1); LONG filler is adaptive — `min(recipeCap, floor(short·(1-s)/s))` against a 0.70→0.53 per-level target-share taper — so every SHORT level ends >0.5. Hint text + comments updated.
- Verified: harness extended to a selection matrix (all / each single group / 2 keys / 1 key / zero), 55/55 assertions; genlib.js now loads the LIVE generateEntries source from the file. End-to-end after-fix: ALL → 4 SHORT floors (L1-L4 in visualizer labels), Show & event → 3, single group → 2, sparse → 1.
- Note (accepted): the adaptive filler is emitted as ONE sized LONG line (office / 1b1b apartment) — on housing levels this can be an unrealistically large single "apartment"; cosmetic, editable in the review UI.

## program-massing-shortfloor.html — SHORT stack interlock fix (delegated to opus subagent)

- Bug: input-handoff SHORT band didn't weave at its top seam (L2→L3 SHORT column overlap = 0.000 in a packSide/splitSides replica; interlock needs both floors' SHORT footprints to share plan columns, :1061).
- Two SAMPLE-era relics in `computeLayout`: (1) packSide's "LONG hugs core / SHORT to facade" ordering hardcoded to `lv >= 0 && lv <= 2` — replaced with neighbor-aware `clusterFloor(lv)` (floor carries SHORT and an adjacent floor does too); (2) splitSides could strand a lone SHORT on one side with no LONG anchor (handoff L3: 1 office + 1 lounge bar split to opposite sides) — added a guarded SHORT-anchor repair merging the lone LONG onto the SHORT side.
- After: L2→L3 overlap 0.563 (others unchanged); replica proves SAMPLE floor rects byte-identical pre/post (the new gate also correctly excludes SAMPLE's isolated L5 lounge-bar floor). Screenshots: 4-floor woven band (stack-after.png), SAMPLE no-regression, ?interlock=0 path intact, structure mode clean (zero console errors via --enable-logging=stderr).
- Backup: BACKUP/program-massing-shortfloor-260707-preStackFix.html. buildShortBlocks/interlock math/exports untouched.
- Lesson: headless-Edge structure-mode captures need ~25-30 s virtual-time budget + fresh --user-data-dir; a locked/reused edgeshot profile makes Edge exit WITHOUT writing the PNG.

## program-input.html — three-tier area scaling (delegated to opus subagent; resumed once after session-limit interrupt)

- Audit (audit.js) found uniform GFA scaling (×0.77-0.88) shrinking rigid programs: cores 201→154, parking 322→247, single 61-70 m² toilets on GL only, and absurd filler lines (267 m² "1b1b").
- Rework in generateEntries: RIGID tier (cores/circulation/toilets/parking/mech/elec/loading — exact presets, never scaled) · CALIBRATED tier (activities/units/lobby/sales/staff/it/storage — clamp ×0.85-1.15) · SPONGE (office plates ≥300, band filler ≥0, housing plates emitted as standard-unit mixes) absorbs the remainder. Two-pass solve; band levels each get one rigid 80 m² toilets line counted inside the filler budget; tiny bins that can't carry their toilet merge downward; POST-SCALING >0.5 guarantee asserted on serialized output.
- Adaptive core count: passenger core b only when gfa/floorsAbove ≥ 1400 m² (12000/8F keeps 3 cores; 10F drops to 2, matching the SAMPLE recipe).
- Documented deviation from the brief: housing plates moved CALIBRATED→SPONGE (unit presets intact, quantity flexes) — CALIBRATED literal made housing/all bottom out at +15.8%; with the change all 9 matrix cases land within ±2%.
- Verified: 166/166 harness assertions over 9-case matrix; e2e screenshots (all → 4 SHORT floors L2-L5, learning → 2, weave intact); wizard clean; helper page deleted. All-case band now starts at level 1 (second-pass monotonicity rule), shares .914/.893/.854/.590.
- Open observation: with cores rigid, core+circulation = 6,300 m² = 52% of a 12,000 m² / 10-plate building — the 1400 m² plate threshold for the 3rd core may deserve lowering (2 cores → 39%).

## program-massing-shortfloor.html — compact layout rework (delegated to opus subagent; resumed once after session-limit interrupt)

- User report: input-generated massing scattered — sparse floors packed south band flush-left / north band flush-right (packSide option-A dual-corner branch), leaving a void between, inside a max-over-floors envelope.
- Fix (packSide :363-385, 23 lines, single site): both sides + both CORE_OPTIONs now pack one contiguous row from common origin x=0 with the option-B core-skip pattern (coreW>0 guard); clusterFloor floors order SHORT first from the anchor end (nests the taper for interlock). Corridor trim + basements inherited for free. Cores keep fixed shaft x per brief.
- Metrics (replica): SHORT cross-floor overlap all pairs ≥ before (all-case L1→L2 0.594→0.708; learning 0.600→1.000; SAMPLE 0.744/0.739→0.821/0.957); intra-band gaps 0; floor-bbox fill 1.00 (before: sparse floors floating at x=5-13, fill ~0.71). A pocket look-ahead for inset-mode pre-core holes was tried and reverted (degraded overlap); those holes are pre-existing subset-sum leftovers.
- Stats unchanged (all: 12,000 m² / 4 SHORT L2-L5; learning: 2; SAMPLE identical incl. 3 SHORT L1-L3 — honest diff: SAMPLE south bands swap SHORT to core-side, overlap improved). interlock=0 and structure mode clean (zero JS errors).
- Backup: BACKUP/program-massing-shortfloor-260707-preCompactFix.html. Screenshots: scratchpad/cmp-*.png.
- OPEN ITEM: passenger core shaft stays fixed at FW-cwN (far right), so it reads as a detached tower next to the left-compacted massing — cores were explicitly out of scope; re-anchoring cores to the occupied extent is the natural next task.

## program-massing-shortfloor.html — adaptive core anchoring, 2 iterations (delegated to opus subagents)

- Iter 1 (:329-354 + FW two-pass :393-403; BACKUP …-preCoreAnchor.html): coreN anchored to max per-side band width instead of envelope corner. Honest result: only ~1 module better (splitSides balance makes maxNW ≈ FW−cwN); sparse-floor float up to 14 modules remained.
- Iter 2 (:343-368; BACKUP …-preCoreAnchor2.html): float-minimizing 1-D scan — coreNx minimizes Σ above-grade max(0, coreNx − nW(lv)); floors wider than coreNx wrap it via the existing core-skip. Egress: non-adjacency span floor + c2c ≥ ceil(⅓·bandMax) (agent flagged: the literal minSep=cwS+cwN+1 c2c reading is infeasible vs the float targets; span reading adopted).
- Results (before/iter1/iter2, above-grade): all coreNx 20/19/8, mean float 10.38/9.38/0.88, max 15/14/3, touch 0/13/50%; learning mean 0.13, touch 88%; SAMPLE float 0, touch 100% (coreNx 23→16, wraps on every floor), stats identical. Visual: passenger core reads as part of the massing (verified in iter2-all.png).
- Accepted trade-off: all-case L1→L2 SHORT overlap 0.708→0.679 (one interlock cell); probe (scratchpad/iter2probe.js) proved touch≥50% and overlap≥0.708 mutually exclusive for that case. Other pairs unchanged; weave intact. FW grew where wide floors wrap the core (25→27 all) — correct bookkeeping.
- Structure mode zero JS errors; interlock=0 sane; temp files deleted.

## program-input.html — cores resized to 17'×25' (delegated to opus subagent)

- User spec: both core types 17'×25'. Module-true implementation: 2×3 modules = 17'×25'-6" ≈ 40 m² (25' isn't a multiple of 8'-6"; rounding flagged). addCores (:805-807) is the sole emission site: freight 201→40, passenger a/b 161→40, all RIGID; circulation 107 unchanged. shortfloor SAMPLE keeps its own 201/161 (untouched, stats identical 14,272).
- Footprint proof: shortfloor's core resolution IGNORES emitted {w,h} (rectDims from repArea alone); replica shows 40 m² → exactly 2×3 modules for all three types.
- Rebalance: ~4.4k m² rigid freed → calibScale hits the 1.15 clamp in every matrix case, plates grow (e.g. all-case 318→834), all 9 cases within ±2%, 166/166 assertions. All-case band back to levels 0-3 (GL rejoins — SHORT lines ×1.15 now clear the anchors), shares 0.678/0.654/0.602/0.531. Circulation stat 6,300→2,270 m².
- Visual (rz-*.png): small gold 2×3 shafts embedded in a cohesive massing; weave intact; structure mode zero JS errors.
- Pipeline lesson: `& msedge.exe --headless=new` returns before the PNG is written and leaves lingering processes — use `Start-Process -Wait`; kill strays by filtering Win32_Process CommandLine for '--headless' (never blanket-kill msedge).

## program-input.html — color scheme aligned to house palette

- Swapped to the family palette used by massing-composer / program-massing*: bg `#FAFAFA`→`#F5F5F5`, accent `#0000FF` (+ all `rgba(0,0,255,…)`, `#1717c7`)→`#172FC7`, orange `#E67033` kept, added `--yellow #EEC341`.
- Yellow's role follows CAT_COLOR convention (circulation): core/circulation pills renamed `.pill.muted`→`.pill.circ`, now yellow; review legend text updated (orange = SHORT · blue = LONG · yellow = circulation).
- Verified: headless-Edge screenshot of wizard step 1 renders with new blue, no JS errors. Note: first screenshot attempt silently produced no file — reused `$env:TEMP\edgeshot` profile was locked by an earlier headless run; fresh `--user-data-dir` fixed it.

## P1 layout fix — corner-core parti + compact packing + shortest-connector corridor (program-massing-shortfloor.html)

- Implemented LAYOUT-FIX-PLAN §3-P1 (folding in four in-flight user direction changes §0.5/§0.6/§0.7). `computeLayout` rewritten for option A ('edge'); option B ('inset') kept on legacy path for P4.
- Parti: coreS at SW (x0), coreN pinned by GL footprint E0 at coreNx=E0−cwN. Dense floors corner-justify (south L→R, north R→L flush coreN); sparse floors = common window scanned to max SHORT-cell / program overlap with floor below; plate floors (single LONG or >70% room) right-anchor wrapping coreN via greedy rect-cover. Corridor = single shortest connector; floor drops it only if every room touches a core.
- Replica (session-log/260707-tools/replica3.js) kept byte-identical; new metrics: contiguity/orphan, corridor Σ + 1-seg, vertical shared-col, §0.7 connectivity. ASSERT PASS case_all+sample+learning. sample.txt created from SAMPLE constant.
- Results: case_all overlaps .862/.857/1.000, corridorΣ 207→185, 0 orphans, 100% connectivity, cores@0,23. SAMPLE 14,272 m² / 3 SHORT L1-L3 (HARD held), new overlap baseline .788/.957. harness 166/0. Screenshots p1-caseall/p1-sample/p1-caseall-structure.png — coherent massing, structure mode clean.
- NOT met: FD=16 (>13 target) — deepest non-plate rooms (office d8 + parking d7) set FD; needs P2 depth discipline. float=0 dropped for sparse floors (superseded by §0.6.3 interior-window+corridor-bridge). Full report: agentops/reports/260707-P1-report.md.

## P1.5 block subdivision — VERIFIED (delegated opus)

- Found already implemented by a prior unreported run: `subdivideBlock` (shortfloor:515-531, applied :512 via floorRects.flatMap), `MAX_SIDE_MOD=4` (:583). Zero edits this session — verified end-to-end + wrote the missing report. Rect audit: every rendered block ≤4×4 mod, per-room area conserved (err ≤6e-14 m²), case_all 61→126 blocks. replica3 unchanged & IDENTICAL to post-P1 (subdivision is purely downstream). harness 166/0. SAMPLE 14,272 / 3 SHORT L1-L3. Report: agentops/reports/260707-P1_5-report.md. Genuine pre-P1.5 revert = BACKUP/…-preP1.html.

## P2 depth discipline — STOPPED then REVISED, edit made but NOT signed off (delegated opus, interrupted)

- First pass STOPPED (correctly): the plan's ≤200 m² gate + SAMPLE byte-identity are self-contradictory — SAMPLE's depth deviations (max 5) strictly dominate case_all's (max 4), so any threshold sparing SAMPLE also nulls case_all; and the FD=16 drivers (office 392→d8, parking 322→d7) sit ABOVE the gate. Report: agentops/reports/260707-P2-report.md.
- Commander REVISED the plan (§P2 REVISED block): gate widened to all non-plate rooms; SAMPLE acceptance relaxed to the §0.5 standard (byte-identity retired). Executor resumed and made the edit — P2 depth-normalization code is now LIVE at shortfloor:367-390 — but was KILLED by the user mid-verification (SAMPLE + structure shots not taken). **OPEN: program-massing-shortfloor.html carries an UNVERIFIED P2 edit.** Backup BACKUP/program-massing-shortfloor-260707-preP2.html should exist; re-verify or revert before trusting P2 numbers.

## program-input.html — office-plate split (generator-side compaction; user-requested, delegated sonnet)

- User report: generated massing's office-only upper floors (L5, L7 of the default case) protrude past the two cores with an over-long corridor. Root cause: generator emitted ONE `office` line per office floor → shortfloor's plate gate (`rs.length===1 || mx/tot>0.70`, :355) → slab right-anchored wrapping coreN. Housing floors already multi-unit, so office-only.
- Fix (program-input.html only, plan session-log/260707-office-plate-split-PLAN.md): at the office emission (~:1110-1123) split each floor's `perO` into `k=max(2,ceil(perO/OFFICE_ROOM_MAX))` office rooms summing exactly to perO; `OFFICE_ROOM_MAX=280` new named const (~:937). ≥2 rooms ⇒ never a plate. Per-floor nPlates/budget math untouched. `wh` left null (compact without a depth hint).
- L5/L7 now 3×278 m² each (was 1×834). plateInfo no longer contains 5/7. harness 166/0 (1 assertion updated: office-min ≥300 was per-line → per-floor sum, tools/harness.js:164-171). GFA 12,001. Overlaps 0.876/0.867/1.000, ASSERT PASS. corridorΣ 161→171 (+6%, honest normalization — L5/L7 corridor 9→14 now matches sibling floors; the old 9 was the plate hugging coreN).
- Verified visually (commander read-back of crop-old/crop-new.png): office floors step IN, clear of coreN, corridor bridges the gap — no longer protruding slabs. Screenshots session-log/260707-tools/office-split-caseall.png + -structure.png (structure mode clean). Backup BACKUP/program-input-260707-preOfficeSplit.html. New program text case_all_v2.txt (frozen case_all.txt left intact). Report: agentops/reports/260707-office-split-report.md.
- Note: replica3.js's hardcoded corridor baselines (183/164/120) are stale vs the current EDGE parti (161) — cosmetic script housekeeping, not touched.
