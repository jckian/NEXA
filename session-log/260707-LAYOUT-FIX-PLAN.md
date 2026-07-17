# 260707 LAYOUT-FIX-PLAN — program-massing-shortfloor.html layout repair

**Audience:** an executor agent (sonnet/opus) implementing fixes phase by phase. Self-contained; do NOT re-derive the diagnosis.
**Authored by:** Fable 5, 260707, after evidence-based diagnosis (screenshots + ASCII plan dumps + replica metrics).
**Scope:** ONLY `program-massing-shortfloor.html` (layout stage, `computeLayout` region :285-441) + the verification tools in `session-log/260707-tools/`. Do NOT touch `program-input.html`, the SAMPLE text (~:1623-1780), `computeShortFloors` (:503), or the classifiers (duplicated in program-input.html — "keep in sync" comments).

## 0. Problem statement (verified evidence, don't re-litigate)

Generator-driven programs (`?src=input`) render as scattered confetti instead of a coherent bar stack. SAMPLE renders fine — the layout engine's assumptions were tuned to SAMPLE-shaped input. Five verified causes:

1. **Single-plate floors drift** — e.g. ALL-case L5/L7 `{office}/{834}` → rectDims gives an 11w×11d block; packSide's core-skip (:401) jumps it wholesale past coreN (x8-10) to x11-21, while lower floors anchor at x0. Upper plates read as a detached table hovering diagonally off the base. Its d=11 also inflates `northDepth` → FD=19 for every floor.
2. **Systematic 3-module N/S shear** — coreS pinned at x0 forces every south room to start at x3; north bands start at x0 (coreN at x8). Every floor's two bands are offset by 3.
3. **Core-skip holes** — greedy one-pass packing without backfill leaves 1-4 module holes before the core interval on every north band (replica: MAX intra-band gap=3). Floors fragment into 2-3 chunks.
4. **Depth heterogeneity** — per-room dMod ranges 3..11 on the same band (apartments d4, offices d8-11, parking 7×7 squares) → bands read as lumpy piles, not bars.
5. **CORE_OPTION 'inset' (B-centre) is broken** — coreSx=INSET=4 makes the first south room jump to x7 (wastes x0-3), and the inset clamp (:369) only enforces non-adjacency, NOT the ⅓-band remoteness → replica egress FAIL (c2c 4 < required 8).

## 0.5 DESIGN DIRECTION CHANGE (user, 260707 — overrides anything below that conflicts)

The user has set the parti explicitly:
1. **Cores sit at DIAGONALLY-OPPOSITE CORNERS of the GROUND-FLOOR footprint** (user clarification #4, 260707: 必須在整個建築量體「地面層」的對角) — coreS at the SW corner (x0), coreN at the NE corner of LEVEL 0's packed extent: xN = E0 − cwN, where E0 = max(cwS + sW(L0), nW(L0) + cwN), computed from L0's rooms only (fallback: lowest above-grade level if no L0). NOT the widest floor anywhere — an upper floor wider than GL simply extends past the core (contiguity per §0.6 still applies). This reverses yesterday's float-min scan that pulled coreN inward to x8; the scan is retired for option A.
2. **Compact packing, minimal voids.** Bands justify INTO their corner core: south band packs left→right flush after coreS; north band packs RIGHT→LEFT flush against coreN. Contiguous rows — core-skip holes become structurally impossible (each band's core is at its end, never mid-row). Float disappears because the north band always touches coreN by construction.
3. Sparse floors then read as south-left + north-right chunks joined by the corridor — an intentional pinwheel around the diagonal cores, not confetti. Plate floors (P1) right-anchor over coreN.
4. clusterFloor SHORT-first anchoring becomes side-dependent: south anchor = left end, north anchor = RIGHT end (SHORT packs first from the anchor end on both sides, so cross-floor interlock columns still stack).

**SAMPLE regression is accordingly RELAXED (design change, not a bug):** SAMPLE stats stay HARD (14,272 m² / 3 SHORT L1-L3 — computeShortFloors untouched). SAMPLE layout WILL change; acceptance becomes: each SAMPLE overlap pair ≥ .75, weave visibly intact in the screenshot, and the new numbers recorded in the report as the new baseline.

## 0.6 SECOND USER DIRECTIVE (260707, later) — compactness & circulation, refines §0.5

1. **No orphan volumes.** No room may float beyond a core, detached from the floor's main mass. Formal check: per floor, the union of occupied columns (program rects + active core shafts) is ONE contiguous x-run. Pure corner-justification on a sparse floor would leave two distant clumps — that is NOT acceptable; sparse floors cluster instead (rule 3).
2. **Circulation = shortest connector.** Per floor the corridor is a SINGLE contiguous segment of minimal length that covers all of that floor's program columns and reaches at least one active core shaft. Replaces the covered-columns fragmentation (:418-439). Keep the existing exemption for SHORT-dominant self-served floors (:420-426). Corridor length is now an optimized output — report Σ corridor modules per case before/after.
3. **Volumes pack one-against-another.** Bands are contiguous (no holes) AND:
   - **Dense floors** (combined band footprint ≥ ~60% of FW): corner-justified per §0.5 — they span between the corner cores anyway.
   - **Sparse floors:** both sides pack over a COMMON x-window (splitSides balance kept; each band contiguous; SHORT-first from the window's anchor edge). The window's x-position is chosen bottom-up (GL upward) to MAXIMIZE shared occupied columns with the floor below; tie-break = minimize distance to the nearest active core (shorter corridor). A window not touching any core gets its corridor extended to the nearest core (rule 2) — that extension counts in the tie-break cost.
   - **Plate floors** keep §0.5's right-anchor wrap of coreN (they define the upper massing; sparse floors between plates will nest under/over them via the overlap objective).
4. Net effect to verify visually: SHORT plinth spanning the bar at the base, upper floors stacking coherently (tower over the NE core), no confetti, corridor reads as one short spine per floor.

## 0.7 FIFTH USER DIRECTIVE (260707) — universal service connectivity

**Every volume connects to circulation or a core, as far as possible.** Operationally:
1. Metric: an above-grade program ROOM counts as CONNECTED if its footprint shares ≥1 module edge (in plan, same level) with that level's corridor segment or an active core shaft. (Rooms, not P1.5 sub-blocks — blocks of one room are mutually adjacent articulation.)
2. The double-loaded anchoring (north rooms at z=zMid+1, south at z=zMid−dMod, plates straddling) already guarantees corridor adjacency wherever a corridor exists — the binding change is the corridor exemption:
3. **REPLACE the SHORT-dominant corridor exemption (:420-426):** a floor may drop its corridor ONLY if every room on it directly touches a core shaft. Otherwise it gets the §0.6.2 shortest-connector corridor like everyone else (e.g. the L0 foyer floor now keeps a minimal spine so its rooms are served).
4. Acceptance: connectivity report per case (above-grade % + list of any disconnected rooms); target 100%, every exception explicitly justified in the report; basements reported too (informational).

## 1. Hard constraints (any violation = revert the step)

- **SAMPLE regression (as relaxed by §0.5):** stats identical (Total GFA 14,272 m², 3 SHORT floors L1-L3); overlap pairs ≥ .75 each, measured and reported (replica3 on `sample.txt` — regenerate: paste SAMPLE from the HTML into `session-log/260707-tools/sample.txt` if absent).
- **Baseline (measured 260707 on frozen case texts, ITER2/edge, case_all.txt):** overlap {L0→L1 .807, L1→L2 .776, L2→L3 1.000}, above-grade float mean .38 / max 3 / touch 88%, egress OK. After each phase these must not get WORSE except where the phase explicitly targets them. NOTE: handoff floor numbers (.679/.792/.750) came from yesterday's lost case texts — the frozen `case_all.txt` / `case_learning.txt` in the tools dir are now the canonical baseline inputs. Do not regenerate them; read them.
- **No new UI** unless a phase says so. `CORE_OPTION` seg control (:488, :1502) keeps its two values.
- **Backup exists:** `BACKUP/program-massing-shortfloor-260707-preLayoutFix.html` (already made). Make an additional `BACKUP/…-preP<N>.html` copy before EACH phase's first edit.
- This repo has NO git. Never delete/rename existing files.

## 2. Verification kit (run from `session-log/260707-tools/`)

- `node replica3.js case_all.txt` (+ `--opt=inset`) — layout metrics. **replica3.js MUST be kept in sync with every computeLayout change you make** (it copies splitSides/packSide/core-scan verbatim). Update it in the same phase, then its `[ASSERT]` line must PASS.
- `node harness.js` — 166 generator assertions (you're not touching the generator, so it must stay green; if it goes red you touched the wrong file).
- ASCII plan dump (visual truth without a browser): the inline node snippet in §6.
- End-to-end screenshots: `node repro2.js` writes repo-root `_handoff-test.html` (forwards URL params). Serve + shoot per the recipe in `agentops/G-LETTER.md` item 3 (Start-Process -Wait, fresh --user-data-dir, delete profile after, stop server when done). Key URLs:
  - `http://localhost:8099/_handoff-test.html?case=all` (generator case)
  - `http://localhost:8099/program-massing-shortfloor.html` (SAMPLE)
  - append `&mode=structure` (budget 25000-30000) for the structure-mode zero-console-error check.
  - DELETE `_handoff-test.html` when the phase is verified.

## 3. Phases — execute in order, verify each before the next

### P1 — Corner-core parti + compact packing + shortest-connector corridor (REVISED per §0.5 + §0.6)

**Goal.** Implement the §0.5+§0.6 parti in `computeLayout` for CORE_OPTION 'edge' (A):
(a) coreS pinned at x0 (SW corner of GL); coreN pinned at xN = E0 − cwN (NE corner of GL), where E0 = LEVEL 0's packed extent = max(cwS + sW(L0), nW(L0) + cwN) from L0's rooms only (fallback: lowest above-grade level). NOT the global widest floor — floors wider than E0 extend past coreN (their contiguity per §0.6 must still hold). The grid/render FW stays the actual max extent. The float-min scan (:343-372) is retired for option A (keep the code path for option B until P4 reworks it). Dense/sparse threshold in (b)/(b') is measured against E0, not render-FW.
(b) **Dense floors** (combined band footprint ≥ ~60% of FW columns): south band contiguous left→right flush after coreS (x = cwS); north band contiguous RIGHT→LEFT flush against coreN (rightmost edge = xN). No core-skip, no holes.
(b') **Sparse floors** (< the threshold): both sides pack contiguously over a COMMON x-window; window position chosen bottom-up to maximize shared occupied columns with the floor below, tie-break minimal distance to the nearest active core (§0.6.3). No floor may end up as two detached clumps (§0.6.1 contiguity check).
(c) clusterFloor SHORT-first anchor is side-dependent: south/dense = left end, north/dense = right end; sparse windows = the window edge nearer its anchor core (keep it consistent for consecutive band floors so interlock columns stack).
(d) **Plate floors** — single LONG room, or largest room >70% of packed area — skip splitSides/packSide: lay the plate as a corridor-straddling slab RIGHT-ANCHORED to wrap coreN (grow column-by-column leftward from xN + cwN, both sides of z = zMid, skipping the corridor row and active core cells; if the cell budget spans the full width it wraps coreS too). Cell budget = round(area/MA), conservation |emitted − budget| ≤ 1. Emit as plain rects per side (grep how floorRects entries are consumed downstream before choosing emission shape).
(e) `northDepth/southDepth` (:330-341) exclude plate rooms — FD shrinks back to ~11-13.
(f) **Corridor = shortest connector** (§0.6.2): per floor ONE segment [lo, hi] with lo/hi = the minimal interval covering all program columns and reaching ≥1 active core span; replaces the covered-columns fragmentation loop (:427-438). The SHORT-dominant exemption (:420-426) is REPLACED per §0.7.3: drop the corridor only when every room on the floor directly touches a core shaft.

**Why.** User parti (§0.5, §0.6) + cause 1 (plate drift/FD explosion) + cause 2 (shear) + cause 3 (holes) + orphan volumes + fragmented corridors.

**Acceptance.**
1. ASCII dump (§6) case_all: every band contiguous (replica MAX gap = 0); per-floor occupied-column union = ONE contiguous run (zero orphan clumps); coreS at x0 and coreN flush at L0's right edge (BOTH cores inside the GL footprint — print L0's row and verify the shafts sit at its two ends); north-band/window mass touches its anchor core (float = 0); L5/L7 plate wraps coreN, straddles corridor; FD ≤ 13.
2. Updated replica3 `[ASSERT] PASS` on case_all edge with the new checks (float 0, contiguity, corridor single-segment, egress c2c trivially max); overlap pairs re-measured and ≥ .70 each; Σ corridor modules reported before/after (must DROP).
3. Vertical stacking: report shared-column ratio for each consecutive above-grade pair; flag any pair < .5 (plate-adjacent pairs included) — no hard fail, but flag.
4. SAMPLE: stats 14,272 / 3 SHORT L1-L3 (HARD); overlap pairs ≥ .75 each; weave visible; coherent stack in screenshot.
5. Screenshots case=all: compact massing, volumes one-against-another, no orphan blocks beyond a core, upper plates stack over the NE core; structure mode zero console errors.
6. Connectivity (§0.7): per-case report of above-grade rooms adjacent to corridor/core; target 100%, exceptions listed and justified; basement figures informational.

### P1.5 — Block subdivision: max side 34 ft (THIRD user directive, 260707)

**Goal.** No rendered volume has a side longer than 34 ft. After packing (downstream of P1's floorRects emission, before rendering consumes them), any rect with wMod > `MAX_SIDE_MOD` or dMod > `MAX_SIDE_MOD` is subdivided into a grid of adjacent blocks each ≤ MAX_SIDE_MOD per side. `const MAX_SIDE_MOD = 4` (4 × 8'-6" = 34'-0"; the user wrote "<34ft" — if they meant strictly under, the constant becomes 3 = 25'-6"; make it a single named constant so the flip is one edit, and note the ambiguity in the report).

**Why.** User: 太大的量體拆成不同區塊 — grain/articulation. Blocks of one room stay mutually adjacent, so footprints, overlap metrics, contiguity and corridor results from P1 are all UNCHANGED — only seams appear.

**Mechanics.** Split each oversized dimension into ceil(n/MAX_SIDE_MOD) parts as EVENLY as possible (5→3+2, 7→4+3, 11→4+4+3 — never emit 1-wide slivers from a splittable dimension). Each block inherits the parent's type/category/level/side; area = parent area × (block cells ÷ parent cells) so Σ area is conserved (corridor rule :423-425 and any stats summing r.area stay correct). Apply to program rects AND plate-slab rects; core shafts are exempt (they are 2-3 modules anyway). Check how hover/detail and buildShortBlocks (:980) consume rects before choosing where exactly to subdivide — the SHORT kit may already granulate SHORT volumes; do not double-split SHORT if the kit handles it (verify visually).

**Acceptance.** (a) A rect audit after build: every rendered program block has wMod ≤ 4 AND dMod ≤ 4; Σ block area per room = room area ± 0.5 m². (b) replica metrics identical to post-P1 values (subdivision must not move footprints). (c) case_all + SAMPLE screenshots: same massing silhouette as post-P1, visible block seams on former mega-rects (plates, parking, exhibition); structure mode zero console errors. (d) SAMPLE stats unchanged (HARD).

### P2 — Depth discipline (band depth normalization)

**REVISED 260707 (commander, after executor STOP — see agentops/reports/260707-P2-report.md).** The original ≤200 m² gate + SAMPLE byte-identity pair is self-contradictory: SAMPLE's depth deviations (max 5) strictly dominate case_all's (max 4), so any threshold sparing SAMPLE also nulls case_all; and the FD=16 drivers (office 392→d8, parking 322→d7) sit above the gate. Amendments:
1. **Gate widened:** ALL non-plate program rooms on a band are re-proportioned to that floor+side's modal depth D (area-weighted mode of dMod, plate floors and cores excluded): dMod=D, wMod=ceil(cells/D). SHORT rooms included (their kit granulates downstream). Executor may pick plain vs area-weighted mode by measured FD/fill outcome — state the choice.
2. **SAMPLE acceptance relaxed to the §0.5 standard** (byte-identity retired): stats HARD (14,272 m² / 3 SHORT L1-L3), every overlap pair ≥ .75, weave visibly intact in the screenshot, new SAMPLE numbers recorded as baseline.

**Why.** Cause 4: mixed depths 3..11 on one band kill the bar reading; also the P1 open item FD=16 (target ≤13).

**Acceptance (revised).** (a) SAMPLE per §0.5 standard above. (b) case_all ASCII: each band reads as a near-constant-depth strip; per-floor bbox fill ≥ baseline; FD reported (target ≤13; if a room's normalized width would exceed available band run, fall back per-room to its original dims and report it). (c) replica3 kept in sync, ASSERT PASS all 3 cases; overlaps ≥ .70 case_all / ≥ .75 SAMPLE; corridorΣ/contiguity/connectivity not worse. (d) P1.5 subdivision operates on normalized rects (no change needed, verify). (e) Screenshots case_all + SAMPLE + structure mode zero fatal errors; harness 166/0.

### P3 — (RETIRED by §0.5) Pre-core backfill

Corner-justified packing makes mid-row cores impossible under option A; holes cannot form. Backfill survives only inside option B (P4) where a core CAN sit mid-row.

### P4 — Rebuild CORE_OPTION 'inset' (B) under the new parti

**Goal.** Option B = "centre pocket" alternative to A's corners: both cores pulled toward the middle of the bar, subject to non-adjacency AND c2c ≥ ceil(bandMax/3). Scan (coreSx, coreNx) minimizing void (pre-core waste + float), with backfill in packSide for rooms that fit before a mid-row core. No more fixed INSET=4; the clamp at :369 that ignores remoteness is deleted.

**Why.** Cause 5: current inset FAILS egress (c2c 4 < 8) and wastes x0-3 on the south band.

**Acceptance.** replica `--opt=inset` case_all: egress OK (c2c ≥ 8), intra-band MAX gap ≤ 1, fill ≥ .95, ASSERT PASS; option A results byte-identical to post-P2 (B must not perturb A); screenshots of both options (`inset` needs a temporary UI click or add `?core=` URL param — if you add the param, mirror the existing param block at :1781-1786 and document it in the session log).

## 4. Report contract (per phase, ≤30 lines back to the commander)

What changed (file:line per edit) · replica/harness output lines proving acceptance · screenshot path(s) · SAMPLE regression check result · anything noticed but not fixed. Long dumps → `agentops/reports/260707-P<N>-report.md`, return the path.

## 5. STOP conditions (report instead of proceeding)

- SAMPLE stats or SAMPLE rects change and you cannot make the phase a SAMPLE-no-op → STOP, show the diff.
- An acceptance metric conflicts with another (e.g. P3 backfill vs overlap floor) after ONE bounded retry → STOP with both measurements.
- You find yourself wanting to edit program-input.html or the classifiers → wrong approach, STOP.
- Two failed attempts at the same sub-goal → STOP with the failure trail (C-MODEL-DISPATCH Rule 5).

## 6. ASCII plan dump snippet (run in tools dir; adapt the txt name)

    node -e "const fs=require('fs');const src=fs.readFileSync('replica3.js','utf8');const mod={exports:{}};const wrapped=src.replace(/const dir = __dirname.*$/s,'module.exports={parse,computeLayout,isShort};');eval(wrapped);const {parse,computeLayout,isShort}=module.exports;const L=computeLayout(parse(fs.readFileSync('case_all.txt','utf8')));console.log('FW',L.FW,'FD',L.FD,'coreNx',L.coreNx);for(const lv of L.levels){const g=Array.from({length:L.FD},()=>Array(L.FW).fill('.'));const put=(r,ch)=>{for(let j=r.zMod;j<r.zMod+r.dMod;j++)for(let i=r.xMod;i<r.xMod+r.wMod;i++){if(g[j]&&g[j][i]!==undefined)g[j][i]=ch;}};for(const c of L.coreShafts)if(lv>=c.minL&&lv<=c.maxL)put(c,'#');let k=0;for(const r of L.floorRects.get(lv)){put(r,isShort(r.type)?'s':String.fromCharCode(97+(k%26)));k++;}console.log('--- L'+lv+' ---');for(let j=L.FD-1;j>=0;j--)console.log(g[j].join(''));}"

## 7. Current line anchors (re-grep before editing — they shift as you edit)

splitSides :287 · computeLayout :316 · core scan :343-372 · INSET :355 · inset clamp :369 · clusterFloor gate :374-382 · packSide :384-406 (core-skip :401) · FW tighten :412-417 · corridor rule :418-439 · rectDims :224 · computeShortFloors :503 · buildShortBlocks :980 · build() :1350 · CORE_OPTION default :488 · URL params :1781-1786.
