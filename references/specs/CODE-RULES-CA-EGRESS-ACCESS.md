# CODE-RULES — CBC Ch.10 (Means of Egress) + Ch.11B (Accessibility)

> **Status: DRAFT — model-researched, NOT professionally verified.**
> Source code: 2025 California Building Code (Title 24 Part 2, eff. 2026-01-01), researched
> 2026-07-09 via DGS/BSC → ICC / UpCodes. Each rule is tagged **[verified]** (value confirmed
> against a published code source on that date) or **[unverified]** (from model knowledge of
> the IBC base code — confirm before relying on it).
>
> **This file defines violation checks, not compliance.** A checker consuming these rules may
> report "measured X, rule requires Y" and nothing else. The word "compliant" is forbidden in
> any output derived from this file. A licensed reading of CBC/LABC supersedes every line here.
>
> Scope: egress + accessibility only — the parts that geometrically constrain **program
> massing arrangement** (core count/placement, floor-plate depth, corridor runs, level access).
> Zoning envelope (FAR/height/setback) is a separate future file per NEXA-EXECUTION-PLAN §6.
> Intended consumer: `checkCompliance(layout) → violations[]` (NEXA-EXECUTION-PLAN Phase 3).
>
> **Implementation status (260710):** `program-massing-shortfloor.html` implements
> `checkCompliance()` (rules E-1…E-9, X-1, S4 → in-app "Code check" panel + `__DEBUG__.CODE_CHECK`)
> and enforces at generation: **E-3** (compact/inset: coreN pushed until the best-separated exit
> pair ≥ ⅓ diagonal), **E-7** (the corridor spine extends to touch every active exit core — no
> dead-end can survive and the E-2 count stays honest), and **3rd+ core placement** (extra
> `fire stair` shafts dock on the south band flush against the widest south run — SE corner on
> pinwheel — with every shaft's SHORT edge facing the corridor, and their **vertical extent is
> OL-driven**: each rises only to the highest floor whose need(lv) = max(exit count, capacity,
> loss-of-one) + E-9 still requires it, always continuous down to discharge per CBC 1023).
> SAMPLE carries 4 stair cores (E-2 needs 3 at OL>500; E-8 capacity needs 4 at OL 573).
> `?coderules=0` disables enforcement; checks always run. X-2/X-3/X-4 are not implemented
> (X-2 trivially holds while every core contains an elevator; X-4 is sub-module).
> Spec change here ⇒ update that implementation in the same task (spec-first rule).

---

## 0. Standing assumptions

| # | Assumption | Basis | Consequence if false |
|---|---|---|---|
| S1 | Building is fully sprinklered (NFPA 13 / CBC 903.3.1.1). | High-rise and large mixed-use effectively require it. | Every sprinkler relaxation below reverts to the stricter base value. |
| S2 | Emergency voice/alarm system is **not** assumed. | Conservative. | Capacity factors stay at 0.3 / 0.2 in per occupant (E-8), not the reduced 0.2 / 0.15. |
| S3 | Module `M = 2.5908 m` (8'-6"); layout data = `{levels, coreShafts, floorRects, floorCorr, FW, FD}`. | MASSING-MODULE-LOGIC.md | — |
| S4 | Every `fire stair …` core counts as one exit (one interior exit stairway). | ProgramFormat.txt core rules | If a core is stair-less, exclude it from all exit counts. |

### Occupancy mapping (ProgramFormat type → CBC group)

Match by keyword on `{type}`; first hit wins. **[unverified]** as a mapping (the groups are
standard; the assignment of this project's vocabulary to them is a project decision).

| Keyword pattern | CBC group | OL factor (Table 1004.5) **[verified]** |
|---|---|---|
| `event hall`, `exhibition`, `gallery`, `theater`, `auditorium`, `lounge bar`, `foyer` | A (assembly) | concentrated 7 sf ≈ **0.65 m²/occ** net; unconcentrated 15 sf ≈ **1.39 m²/occ** net; standing 5 sf ≈ **0.46 m²/occ** net |
| `office`, `staff`, `it support`, `meeting` | B (business) | 150 sf gross ≈ **13.94 m²/occ** |
| `sales`, `display`, `showroom`, `retail`, `pop-up`, `coffee shop`, `fitting` | M (mercantile) | 60 sf gross ≈ **5.57 m²/occ** |
| `housing`, `residential`, `apartment`, `unit`, `hotel` | R-2 / R-1 | 200 sf gross ≈ **18.58 m²/occ** |
| `parking` | S-2 | 200 sf gross ≈ **18.58 m²/occ** |
| `storage`, `mechanical`, `electrical`, `loading` | S / accessory | 300 sf gross ≈ **27.87 m²/occ** |
| `toilets`, `circulation`, `fire stair`, `core` | — (no OL of its own) | excluded from OL |

---

## 1. EGRESS rules (CBC Chapter 10)

### E-1 · Occupant load — CBC Table 1004.5 **[verified]**
- **Rule:** OL of a space = area ÷ factor (table above). Per-story OL = Σ over that level.
- **Massing check:** `OL(level) = Σ p.area / factor(p.type)` over non-core, non-circulation
  programs at that level. This value feeds E-2, E-8; nothing else in the pipeline computes it today.

### E-2 · Minimum exits per story — CBC 1006.3.3 **[verified]**
- **Rule:** OL 1–500 → **2** exits · OL 501–1,000 → **3** · OL > 1,000 → **4**.
- **Massing check:** `stairsAt(level) = coreShafts` containing a fire stair present at that
  level; require `stairsAt(level) ≥ exitsRequired(OL(level))`.
- **Note:** ProgramFormat.txt's "min 3, preferred 4" is a project convention, stricter than
  code for OL ≤ 500 and exactly code at 501–1,000. Keep the convention; report against code.

### E-3 · Exit separation — CBC 1007.1.1 **[verified]**
- **Rule:** two exits must be separated by ≥ **½ the maximum overall diagonal** of the area
  served; **≥ ⅓ diagonal** where sprinklered (S1). Measured straight-line.
- **Massing check:** `diag(level) = M · √(FW² + FD²)` (use the level's own plate if it differs);
  require `maxPairwiseDistance(stair cores at level) ≥ diag/3` (S1), report against `diag/2` too.
- **⚠ Existing heuristic is NOT this rule.** The shortfloor egress guard
  (`program-massing-shortfloor.html`, P2 block) tests core separation ≥ ⅓ **band width** —
  a different measure on a different denominator. ProgramFormat.txt says "≥ ½ floor diagonal",
  which matches the unsprinklered code value. Reconcile: the code measure is the diagonal; ⅓
  of it only under S1.

### E-4 · Exit access travel distance — CBC Table 1017.2
- **Rule (sprinklered, S1):** A → **250 ft = 76.2 m** **[verified]** · B → **300 ft = 91.4 m**
  **[verified]** · M → 250 ft = 76.2 m **[unverified]** · R → 250 ft = 76.2 m **[unverified]** ·
  S → 250 ft **[unverified]**. Distance from the most remote point along the path of travel to
  the nearest exit.
- **Massing check (proxy):** true path measurement needs a walkable graph the pipeline doesn't
  have. Proxy: for each level, `max over floorRects of (Manhattan distance from rect's far
  corner via floorCorr to nearest stair core)` ≤ limit. In module units, 76.2 m = **29.4 M**,
  91.4 m = **35.3 M**. Flag the proxy as such in every report line.

### E-5 · Common path of egress travel — CBC Table 1006.2.1
- **Rule:** the distance an occupant travels before two distinct paths become available.
  B (sprinklered): **100 ft = 30.5 m = 11.8 M** **[verified]**; most other groups 75–100 ft
  **[unverified]**.
- **Massing check (proxy):** for each program rect, distance from rect centroid to the corridor
  spine ≤ limit is a weak proxy; a real check needs the room-door graph. **Not checkable well
  at massing level — report as "informational" severity only.**

### E-6 · Corridor width — CBC 1020 **[verified: 44 in general minimum]**
- **Rule:** ≥ **44 in = 1118 mm** (OL ≥ 50); capacity may govern: width ≥ OL served × 5.08 mm
  (0.2 in/occ, S2) → capacity of a 44-in corridor ≈ 220 occupants.
- **Massing check:** corridor band width in the layout is ≥ 1 module = 2591 mm ≥ 1118 mm →
  **passes by construction**. Assert it anyway (guards future corridor-width parameterization);
  check the 220-occ capacity threshold where a single corridor serves a large-OL level.

### E-7 · Dead-end corridor — CBC 1020 **[verified: 20 ft / 50 ft sprinklered]**
- **Rule:** dead-end length ≤ **20 ft = 6.10 m**; ≤ **50 ft = 15.24 m** where sprinklered (S1).
- **Massing check:** for each `floorCorr` segment, run from the last stair-core connection to
  the corridor's dead end ≤ **5 modules** (5 M = 12.95 m < 15.24 m; 6 M = 15.54 m fails).
  This directly constrains how far program bands may extend past the last core.

### E-8 · Egress capacity / stair width — CBC 1005.3.1, 1011.2
- **Rule:** stair capacity = width ÷ **7.6 mm/occ** (0.3 in, S2) **[verified]**; minimum stair
  width **44 in = 1118 mm** (OL ≥ 50) **[unverified]**. Loss of any single exit may not reduce
  available capacity below 50% of required **[unverified]**.
- **Massing check:** per level, `Σ stairWidth / 7.6mm ≥ OL(level)`, and with the largest stair
  removed, `≥ 0.5 · OL(level)`. Stair width inside a core isn't modeled → assume one 1118 mm
  stair per fire-stair core until the kit models it; say so in the report.

### E-9 · High-rise additional stairway — CBC 403.5.2 **[verified: 420 ft trigger]**
- **Rule:** buildings (other than R-2) with occupied floors > **420 ft = 128 m** above fire
  department access require **one additional** interior exit stairway beyond the 1006.3.3 count.
  High-rise stair remoteness (403.5.1) adds its own separation minimum **[unverified]**.
- **Massing check:** if `topOccupiedLevelHeight > 128 m` → `exitsRequired += 1` on all levels.

---

## 2. ACCESSIBILITY rules (CBC Chapter 11B + 1009)

11B governs public accommodations / commercial / public housing; 11A governs privately-funded
multifamily. The mixed-use test programs contain both — apply 11B as the stricter umbrella
until a licensed reading splits them. **[unverified]** as a scoping decision.

### X-1 · Accessible route to every story — CBC 11B-206.2.3 **[verified]**
- **Rule:** at least one accessible route connects each story and mezzanine. Exceptions are
  narrow (private buildings only, and waive only the elevator, nothing else). Egress-only
  stairs are exempt from route requirements.
- **Massing check:** at least one core containing a **passenger elevator** must be present at
  **every occupied level, including basements** (levels < 0 with occupiable program). A level
  reachable only by fire stair is a violation.

### X-2 · Vertical access within reach of each stair — CBC 11B-206.2.3 provisions **[verified]**
- **Rule:** where elevators are required and any floor exceeds **10,000 sf = 929 m²**, an
  accessible means of vertical access (ramp/elevator/lift) must exist within **200 ft = 61 m
  = 23.5 M** of travel of each stair and each escalator.
- **Massing check:** if `plateArea(level) > 929 m²`: for every stair core at that level,
  distance (corridor-path proxy, per E-4) to the nearest passenger-elevator core ≤ 61 m.
  This caps how far apart the freight-stair core may drift from the passenger cores.

### X-3 · Accessible means of egress — CBC 1009
- **Rule:** stairways serving as accessible MOE need **48 in = 1219 mm clear between
  handrails — waived where sprinklered (S1)** **[verified]**; areas of refuge waived where
  sprinklered **[unverified]**; buildings 4+ stories need an elevator with standby power as
  part of accessible MOE **[unverified]**.
- **Massing check:** under S1 the geometric consequences collapse to: ≥ 1 elevator core flagged
  `standbyPower` (metadata, not geometry) on 4+ story schemes. Report as informational.

### X-4 · Route/clearance geometry — CBC 11B-403.5.1, 11B-304 **[unverified values]**
- **Rule:** accessible route clear width ≥ 36 in = 915 mm; turning space 60 in = 1524 mm;
  accessible WC per RESTROOM-GUIDELINES.md (1.8 × 2.2 m min, 1.5 m turning radius).
- **Massing check:** below module resolution (1 M = 2.59 m exceeds all of these) → **passes by
  construction at massing level.** These bind at room layout, not massing. Keep for the
  room-scale pipeline (program-tile-editor), not `checkCompliance`.

---

## 3. Quick conversion table (module M = 2.5908 m)

| Quantity | Code value | Metric | Modules |
|---|---|---|---|
| Corridor min width | 44 in | 1.118 m | 0.43 M (1 M corridor passes) |
| Accessible stair clear | 48 in | 1.219 m | 0.47 M |
| Dead end (sprinklered) | 50 ft | 15.24 m | 5.88 M → **max 5 M run** |
| Common path, B (sprk.) | 100 ft | 30.48 m | 11.8 M |
| Travel distance A/M/R (sprk.) | 250 ft | 76.20 m | 29.4 M |
| Travel distance B (sprk.) | 300 ft | 91.44 m | 35.3 M |
| Stair↔elevator max (X-2) | 200 ft | 60.96 m | 23.5 M |
| High-rise extra-stair trigger | 420 ft | 128.0 m | (height, not plan) |
| Large-floor trigger (X-2) | 10,000 sf | 929 m² | ≈ 138 cells (M²=6.712 m²) |

## 4. What this file deliberately is not

- Not zoning (FAR/height/setback), not fire-resistance ratings, not construction type, not
  plumbing fixture counts (see RESTROOM-GUIDELINES.md), not structural.
- Not a claim that the checks above equal the code sections they cite — E-4/E-5 are explicit
  proxies, and every **[unverified]** tag means exactly that.
- Not LA-specific: LABC/LAMC amendments to these chapters are unchecked (future
  CODE-RULES-LA per NEXA-EXECUTION-PLAN §6).

## 5. Sources (accessed 2026-07-09)

- DGS/BSC Title 24 index: https://www.dgs.ca.gov/BSC/Codes (2025 edition, eff. 2026-01-01)
- CBC 2025 Ch.10: https://up.codes/viewer/california/ca-building-code-2025/chapter/10/means-of-egress
- CBC 2025 Ch.11B: https://up.codes/viewer/california/ca-building-code-2025/chapter/11B/accessibility-to-public-buildings-public-accommodations-commercial-buildings-and
- CBC/CFC 1007.1.1 (exit separation): https://codes.iccsafe.org/s/CAFC2025P1/part-iii-building-and-equipment-design-features/CAFC2025P1-Pt03-Ch10-Sec1007.1.1
- 1006.3.3 (exit count): https://codes.iccsafe.org/s/CABC2022P1/chapter-10-means-of-egress/CABC2022P1-Ch10-Sec1006.3.3
- 11B-206.2.3 (multi-story route): https://codes.iccsafe.org/s/CABC2022P1/chapter-11b-accessibility-to-public-buildings-public-accommodations-commercial-buildings-and-public-housing/CABC2022P1-Ch11B-SubCh02-Sec11B-206.2.3
- 1009 (accessible MOE): https://www.corada.com/documents/2025CBCPG/section-1009-accessible-means-of-egress
