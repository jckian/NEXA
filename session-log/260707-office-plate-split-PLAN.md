# 260707 PLAN — office-plate split (generator-side compaction)

**Audience:** a sonnet executor. Self-contained. **Scope: EDIT ONLY `program-input.html`.** Do NOT edit `program-massing-shortfloor.html` (read-only, for rendering the verification) or any other file. Authored by Fable 5 after reading both files.

## 0. Problem (user report, verified against the code)

Generator-driven massing (`?src=input`) renders the office-only upper floors (user cited **L5 and L7** of the default mixed-use / 12000 / 8F / all-activities case) as a wide slab that **protrudes past the two cores** and drags a **long corridor**. Root cause is in the *layout* file but is *triggered by the generator*:

- `program-input.html` emits **exactly one** `office` line per office floor: placeholder `add('office', 900, f, 'private', 'sponge')` at ~:1002, final area `perO` set at ~:1110-1113 (`p.area = perO`, ≈834 m² for the default case).
- `program-massing-shortfloor.html` `computeLayout` classifies a floor as a **PLATE** at ~:355 when `rs.length === 1 || mx/tot > 0.70` (single room, or largest room >70% of packed area) and lays a plate as one slab **right-anchored wrapping coreN** — that is the protrusion + long straddling corridor. A single-office-line floor ALWAYS hits `rs.length === 1`.
- Housing floors already emit MULTIPLE units (`decomposeHousing`, 67/107/134) → never single-room → already avoid the plate branch. **So the defect is office floors only.**

Non-plate floors instead go through normal double-loaded packing at ~:363, which honors the emitted `{w,h}` depth (`rectDims(p.area, p.h)`), producing a compact bar hugging coreS with the double-loaded corridor spine.

## 1. Goal

Make office floors escape the plate branch by emitting **≥2 office rooms per office floor, none exceeding 70% of the floor's office area** — so `computeLayout` packs them as a compact double-loaded bar instead of a core-wrapping plate. Total area, GFA, tiering, band logic, core logic all UNCHANGED.

## 2. Exact change (single site, inside `buildAttempt`)

At the office-plate emission (~:1110-1113):

```js
if (officePlates.length) {
  const perO = Math.max(PLATE_MIN, Math.round((budget - housingEmitted) / officePlates.length));
  for (const p of officePlates) p.area = perO;
}
```

Replace the inner `for` loop so each per-floor `perO` is split into `k` office rooms that sum EXACTLY to `perO`:

- `const OFFICE_ROOM_MAX = 280;` — a single named constant near PLATE_MIN (~:937), with a comment: "office plate split — keep ≥2 rooms/floor so the massing packs a double-loaded bar, not a core-wrapping plate (shortfloor plate gate: single room OR >70%)". 280 m² ≈ a large office suite; tuneable.
- `const k = Math.max(2, Math.ceil(perO / OFFICE_ROOM_MAX));` — **≥2 guarantees non-single**; even split keeps every room ≤ ⌈perO/2⌉ = 50% ≤ 70% ✓.
- Reuse `p` as room 0; `add('office', a, p.level, 'private', 'sponge')` for rooms 1..k-1. Distribute the remainder so `Σ area === perO` exactly (e.g. `base = Math.floor(perO/k)`, first `perO - base*k` rooms get `+1`).
- Keep `officePlates.length` and `nPlates` as the per-FLOOR count (do NOT recount by room) so the calibScale / budget / PLATE_MIN math at :1009-1014 and :1097-1099 is untouched.

**Why this site:** `buildAttempt` rewinds `out` to `baseLen` each call (:947), so the split is naturally idempotent across the two-pass solve. It runs AFTER `bandOk()` (:1084) and touches only non-band office floors, so band shares / monotonic taper / SAMPLE-independent logic are all unaffected.

**Optional depth hint (only if the screenshot in §4 shows the office bar too deep or floating):** set `wh` on each split office rec to a shallow depth, e.g. `rec.wh = [Math.max(1, Math.round(a / H)), H]` with `H ≈ 8` m (≈3 modules), matching the meters convention in `dims()` (:785) and `serialize()` (:1167). Default is to leave `wh` null (the current behavior) and let the layout's depth handling proportion the bar. Do NOT add the hint pre-emptively — try null first.

## 3. Hard constraints (violation = revert)

- **Copy `BACKUP/program-input-260707-preOfficeSplit.html` BEFORE the first edit.** No git in this repo; never delete/rename existing files.
- Do NOT touch: `program-massing-shortfloor.html`, the SAMPLE fixture, `computeShortFloors`, the `isShort/isCore/isCorridor` classifiers (duplicated with "keep in sync" — you're not touching them, good).
- **GFA conservation:** total serialized area must stay within ±2% of 12,000 for the default case (splitting preserves `perO` exactly, so this is a check, not a risk).
- `session-log/260707-tools/harness.js` (loads the LIVE generator via genlib.js) must stay **166/0**. If a single assertion trips *because it hard-coded "one office line per floor"*, that assertion encoded the very thing we are intentionally changing — update it minimally (e.g. sum office area per floor instead of asserting one line) and note it in the report. Any OTHER harness failure = you touched the wrong thing → revert and STOP.
- **Do NOT overwrite the frozen `case_all.txt` / `case_learning.txt`** in session-log/260707-tools/ (they are the layout-phase baselines). Write the regenerated new program to `session-log/260707-tools/case_all_v2.txt` instead.

## 4. Acceptance (all required, evidence outside your own claim)

1. **Generator unit check:** regenerate the default case (mixed-use / 12000 / 8F / 2B / all activities). Every office floor now serializes **≥2 `office` lines**, each ≤70% of that floor's office total, `Σ` per floor == the old `perO` (±1 rounding). Print the per-floor office line breakdown for L5 and L7.
2. **harness 166/0** (`node harness.js` from the tools dir).
3. **Layout metric:** regenerate `case_all_v2.txt` from the new generator; run `node replica3.js case_all_v2.txt`. Report `corridorΣ` and whether L5/L7 are still flagged as plate floors (they must NOT be — plateInfo should not contain them). corridorΣ should DROP or hold vs the old 185; overlaps ≥ .70; `[ASSERT] PASS`.
4. **End-to-end screenshot (the real proof):** `node repro2.js` (writes repo-root `_handoff-test.html`, forwards `?case=all` through the LIVE generator), serve on :8099, headless Edge per `agentops/G-LETTER.md` item 3 (Start-Process -Wait, fresh --user-data-dir per shot, delete profile after, stop server). Capture `?case=all`. **L5 and L7 must read as compact double-loaded bars, no longer wide slabs protruding past coreN**; corridor visibly shorter/normal. Compare side-by-side with `session-log/260707-tools/p1_5-caseall.png` (the pre-change baseline). Also capture `&mode=structure` (virtual-time budget 25000-30000) → zero fatal console errors. Save shots as `session-log/260707-tools/office-split-caseall.png` + `-structure.png`. DELETE `_handoff-test.html` + edge profiles, stop the server.
5. **SAMPLE** is generator-independent (built-in fixture in the massing file we don't touch) — confirm in one line that it is unaffected by construction; no SAMPLE screenshot needed.

## 5. STOP conditions (report instead of pushing on)

- Screenshots show the office floors now **float detached** (orphan, clear gap to both cores) or the corridor gets **LONGER** than baseline → the residual is a layout-geometry issue in the OTHER file (out of scope) → STOP, attach both screenshots + corridorΣ, recommend escalating to the user for a layout-side follow-up. Do NOT start editing the layout file.
- Two failed attempts at the same sub-goal → STOP with the failure trail (C-MODEL-DISPATCH Rule 5).
- You find yourself wanting to edit `program-massing-shortfloor.html` → wrong file, STOP.

## 6. Report contract (≤30 lines back to commander)

What changed (file:line for the split site + the OFFICE_ROOM_MAX const) · per-floor office breakdown for L5/L7 (acceptance 1) · harness result · replica corridorΣ + plate-gate check (acceptance 3) · screenshot paths + one sentence on whether L5/L7 now read compact (acceptance 4) · whether you used the optional depth hint and why · GFA total · anything noticed but not fixed. Full detail → `agentops/reports/260707-office-split-report.md`; return the path + the ≤30-line summary. Your final text is data for the commander, not prose for a human.
