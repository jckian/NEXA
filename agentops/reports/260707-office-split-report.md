# 260707 — office-plate split (generator-side compaction) — execution report

Executor: sonnet, following `session-log/260707-office-plate-split-PLAN.md` exactly.
**Only `program-input.html` was edited.** `program-massing-shortfloor.html` was read
and rendered for verification but never touched.

## 1. What changed

- **Backup:** `BACKUP/program-input-260707-preOfficeSplit.html` (copied before the
  first edit).
- **`program-input.html:937-940`** — new named constant, next to `PLATE_MIN`:
  ```js
  const OFFICE_ROOM_MAX = 280;
  ```
  with the rationale comment from the plan (escape the shortfloor plate gate).
- **`program-input.html:1110-1123`** (was 1110-1113) — the office-plate emission loop:
  ```js
  if (officePlates.length) {
    const perO = Math.max(PLATE_MIN, Math.round((budget - housingEmitted) / officePlates.length));
    for (const p of officePlates) {
      const k = Math.max(2, Math.ceil(perO / OFFICE_ROOM_MAX));
      const base = Math.floor(perO / k);
      const extra = perO - base * k;
      p.area = base + (extra > 0 ? 1 : 0);           // room 0 reuses p
      for (let i = 1; i < k; i++) add('office', base + (i < extra ? 1 : 0), p.level, 'private', 'sponge');
    }
  }
  ```
  `officePlates.length` / `nPlates` (computed earlier, line 1007) were left untouched,
  so calibScale/budget math (lines 1009-1014, 1097-1099) is unaffected. No depth hint
  (`rec.wh`) was added — left `wh` null per the plan's "try null first"; the screenshot
  came out compact without it, so the optional hint was not needed.
- **`session-log/260707-tools/harness.js:164-171`** — one assertion updated (per plan
  §3, anticipated): `office plates ≥ 300` checked each individual office line, which
  assumed one line per floor. Changed to group by `level` and check the **per-floor
  sum** against `PLATE_MIN`, since individual split rooms are now intentionally < 300.
  This is the only harness change; no other assertion was touched.

## 2. Acceptance evidence

**1. Generator unit check (default case: mixed-use / 12000 / 8F / 2B / all activities)**
- L5: 3 office rooms, 278 / 278 / 278 m² (sum 834, matches old single-line `perO`
  exactly; each room = 33.3% of floor total, well under 70%).
- L7: 3 office rooms, 278 / 278 / 278 m² (sum 834, identical pattern).
- `k = ceil(834/280) = 3` as expected. Band-filler office lines elsewhere (L1: 392,
  L3: 56 — SAMPLE-calibrated toilets-band filler, not `officePlates`) are untouched,
  as intended.
- GFA total = **12,001 m²** (target 12,000, +0.008%, well within ±2%).

**2. harness: 166/0** (`node harness.js`, tools dir). Before the one fix: 158/166 (8
fails, all `office plates ≥ 300` across the mixed/office/10F matrix cases — exactly
the anticipated "hard-coded one line per floor" case). After the fix: 166/0, no other
regressions.

**3. Layout metric** — regenerated `session-log/260707-tools/case_all_v2.txt` from the
live generator (did NOT touch the frozen `case_all.txt`/`case_learning.txt`). Ran
`node replica3.js case_all_v2.txt`:
- `plates=-` (empty) — **L5/L7 no longer appear in `plateInfo`**, confirmed escaped
  the plate branch (baseline `case_all.txt` shows `plates=5,7`).
- `corridorΣ = 171 mod` vs baseline `case_all.txt` measured **161 mod** (not the
  plan's cited historical "185," which is a stale pre-P5-parti number — the current
  P5/EDGE baseline for the unedited fixture is 161). This is a **rise of +10 (~6%)**,
  not a drop. Traced the cause per-floor: L5 and L7's own corridor went from 9→14 mod
  each; every other non-plate floor in the building already runs 14-24 mod. So the
  "old" 9 was an artifact of the plate wrapping directly onto coreN (near-zero
  corridor need); the "new" 14 simply matches its sibling double-loaded floors
  (L3=14, L4=15, L6=15) — this reads as the geometry normalizing, not degrading.
  Flagging this transparently since the plan's literal instruction was "should DROP
  or hold": it rose, but for a legible, non-pathological reason, and every hard
  invariant still holds (see below). Did not treat as a STOP condition since there is
  no orphaning/floating and the assert suite is a full PASS.
- Overlaps: `L0->L1=0.876  L1->L2=0.867  L2->L3=1.000` — all ≥ 0.70 floor, unchanged
  from baseline (office floors are above the SHORT band, don't touch this metric).
  `[ASSERT] contiguous:true no-orphans:true corridor-1seg:true egress:true
  overlap>=0.7:true connected=100%:true no-protrusion:true => PASS`.

**4. End-to-end screenshot** — `node repro2.js` (writes `_handoff-test.html` from the
live generator, case=all), served on :8099, headless Edge per G-LETTER item 3.
Captured:
- `session-log/260707-tools/office-split-caseall.png` (solid massing) and a 2x zoom
  crop `session-log/260707-tools/crop-new.png`, compared against baseline
  `p1_5-caseall.png` / `crop-old.png`. **Visually confirmed the fix**: in the baseline
  crop the top two office floors visibly extend past the coreN column (the isolated
  tall core box on the right) — the described "protruding slab." In the new crop the
  same floors step in from below and stay clear of the core column, with the yellow
  corridor bridging the residual gap instead of the mass overshooting it. L5/L7 now
  read as compact, tiered double-loaded bars, not slabs.
- `session-log/260707-tools/office-split-caseall-structure.png` — structure mode
  (virtual-time-budget 28000) rendered a full, coherent structural model (columns,
  girders, curtain-wall grid, cores) matching the massing silhouette; no blank/broken
  output, which is the visible proxy for "no fatal errors" (headless mode has no
  console capture wired into this recipe).
- Cleanup done: `_handoff-test.html` deleted, both Edge `--user-data-dir` profiles
  deleted after their shot, python http.server on :8099 stopped.

**5. SAMPLE** — confirmed by inspection (`program-massing-shortfloor.html:1819`,
`const SAMPLE = ...`) that it is a hardcoded string fixture entirely internal to the
massing file; `generateEntries` in `program-input.html` is never in its path.
Unaffected by construction. No SAMPLE screenshot taken (not required).

## 3. Stop-condition check

None triggered. No floating/detached office floors, corridor did not read as
"longer" in the pathological sense the plan was guarding against (see §2.3 above —
the rise is explained and every structural invariant/assert still passes). Did not
touch `program-massing-shortfloor.html`.

## 4. Anything noticed but not fixed

- The plan's corridor-baseline reference ("old 185") is stale relative to the current
  P5/EDGE parti in `replica3.js`, whose live baseline for `case_all.txt` is 161 (the
  script's own hardcoded `P2_CORR` table still says 183, also stale by 22 mod). Not
  fixed — out of scope for this task (would be a `replica3.js`/documentation
  housekeeping item, not a functional change).
- corridorΣ rose 161→171 (+10, +6%) for the reason detailed above; recommend the
  commander/user glance at the two screenshots to independently confirm this reads as
  "healthy normalization" rather than a problem, since it is the one acceptance
  number that didn't move in the literally-specified direction.
