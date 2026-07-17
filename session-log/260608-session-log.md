# 260608 — Session Log

**Role of this doc:** senior PM / tech-lead review of today's activity on the
AI-driven architectural design platform (Voro / Program Agent).
**Focus of the day:** standing up the **Structure Zoning Engine**, the **Hybrid
Structure Allocation**, and tightening the **Program Massing** geometry.

---

## 1. What was accomplished
### A. New "Structure Zoning" stage (Massing → **Zoning** → Structure → LCA)
- Added a 4th workflow tab/mode (`tab-zoning`, `sb-zoning`, `rp-zoning`) in
  `index.html`, sitting between Program/Massing and Structure.
- The stage re-colours every program mass by its **allocated structural system**
  (Skin / Foam / Internal), with sidebar principle text, a colour legend, an
  area-by-system **Building Summary**, and a **Transition Zones** panel that flags
  floors where the system changes vertically (transfer-floor candidates).
- Sourced the allocation principle from
  `references/Hybrid_Zoning_Transition_Engine.xlsx` (+ `HYBRID-STRUCTURE-RULES.md`).

### B. Allocation logic rebuilt to match the engine matrix
- Replaced the initial first-match rules (which collapsed mid-rise buildings to a
  single system) with the **xlsx `Allocation` scoring model**, verified
  **cell-by-cell** against the live formulas:
  - `Fitness% = SUMPRODUCT(demand, L3_Genome) / (SUM(demand)×5) × 100`
  - L4 multipliers (Faç>4→Skin×1.15; MEP/Load/Span/Lat triggers; >120 m Foam×0.7) with 0.6–1.25 clamp
  - `Final = 0.7·(Fitness·Mult) + 0.3·Circularity` → lead = argmax (matrix `Primary`)
- Removed the non-matrix **skin eligibility gate** so all three systems compete
  purely on score (per user decision).
- Added **environmental exposure by N/S/E/W orientation** (engine L0 §0C / Ladybug
  proxy) into the demand vector: S/W = high, E = med, N = low → drives façade-
  integration demand, so the same floor now differentiates by orientation.
- **Core policy** finalised: all fire-stair / elevator / core zones → **Internal
  Structure** (core+frame spine).

### C. Hybrid Structure Allocation (new Structure option)
- Added a **"Hybrid (Zoning)"** card in the Structure tab that builds each zone
  with its allocated system.
- Iterated to a **faithful port of the three source generators**, per zone:
  - **Internal** ← `curtainBox_architecture_generator.py` (GRID 6.0, COL 0.40,
    BEAM 0.30×0.55, SLAB 0.25, mullions/glass, exact materials)
  - **Skin** ← `structural_skin_generator.py` (perimeter arc-length resample,
    alternating ±SKIP diagonals, PRIMARY 1.0×1.2 / SECONDARY 0.7×0.85 ring beams)
  - **Foam** ← `TAMA-GRID.py` (ridge_curve sine arch, loft-to-slab merged shell, flat slab)
- Members carry each generator's real cross-sections/materials; reuses the existing
  layer-group toggles and opacity slider.

### D. Pipeline + geometry polish
- Wired **`chat.html` → `index.html`** (was `index2.html`); added `mode=zoning`
  deep-link support.
- **Massing gap cleanup** across all three case studies:
  - Horizontal: TPAC strip gap 0.12→0.02 (+ depth insets, front/back split);
    53W53 `VIS_SHRINK` 0.94→1.0 & `PAD` 0.25→0.02; TAMA `PAD` 0.35→0.02 and the
    per-block 0.95 shrink removed.
  - Vertical: floor slabs now full height (`SLAB_H = floorHeight`; 53W53
    `SLAB_GAP` 0→0) so floors stack flush.
- Every change syntax-checked (`node --check` on the extracted module).

---

## 2. How it advances the platform vision

The platform's thesis is a **continuous AI pipeline: Brief → Program → Massing →
Structure → LCA**, where each stage is generated, not hand-modelled. Today closed
the biggest gap in that chain: there was **no principled bridge from program to
structure**. We now have:

- A **transparent, matrix-grounded allocator** that turns program + geometry +
  position + height + orientation into a per-zone structural strategy — the
  "decision layer" the whole hybrid-structure thesis depends on.
- A **legible Zoning stage** that makes the allocation reviewable by a human
  (colour-by-system, % mix, transition flags) before committing to geometry.
- A **buildable Hybrid mode** that proves the allocation is constructible by
  routing each zone to a real generator — i.e., the diagram is not just paint,
  it produces structure.

Net effect: the demo can now walk a single building from chat-driven program all
the way to a mixed structural system with a defensible, spreadsheet-auditable
rationale — a strong narrative for the SP26 review.

---

## 3. What remains unresolved

- **Transition members not yet built.** The Zoning panel *detects* transfer floors
  but the Hybrid generator doesn't yet model transfer beams / belt trusses /
  hybrid nodes at system changes (engine L5.5).
- **Skin scale on small zones.** Diagrid members (1.0×1.2 m, tower-scale) look
  chunky on individual program blocks; node count is scaled but section sizes are
  literal.
- **Foam shell thickness.** TAMA `Solidify 0.15` rendered as a single DoubleSide
  surface — topology faithful, 15 cm extrusion omitted.
- **Orientation convention is assumed** (North = −Z); no site azimuth input in UI.
- **Whole-envelope vs per-block Skin.** Skin is physically an envelope; we build it
  per zone box. A true tower would want one continuous diagrid envelope + framed
  interior.
- **TAMA bin-packing leftovers.** Horizontal/vertical gaps removed, but packing can
  still leave end-of-row voids (not a fixed gap).
- **`index2.html` is now orphaned** (nothing links to it) — decide delete vs mirror.

---

## 4. Technical risks

- **Performance:** Hybrid builds per-floor-per-zone members; tall towers (53W53,
  ~75 floors) can produce tens of thousands of meshes → slow build / GPU load. No
  instancing or LOD yet.
- **Single-file monolith:** `index.html` is ~850 KB with all logic inline; growing
  risk to maintainability, merge-conflicts, and testability. No module boundaries.
- **Matrix drift:** allocation constants are hand-copied from the xlsx. If the
  spreadsheet evolves, code silently diverges (no import/test harness).
- **Geometry coupling:** classifier reads massing mesh `geometry.parameters` +
  positions; any change to how massing is built can break zoning/hybrid silently.
- **Coordinate/representation gaps:** Skin/Foam ported as surfaces or square-section
  bars via `makeBeam`; orientation of non-square sections isn't controlled.

---

## 5. Research opportunities

- **Transition Complexity Score (TCS):** implement engine L5.5 fully — score
  adjacent-zone differences, recommend transition members, and feed the
  `FinalScore = 0.5·Fitness + 0.3·Circularity − 0.2·TransitionPenalty` objective so
  the allocator avoids expensive hybrid interfaces.
- **Ladybug-grounded exposure:** replace the heuristic N/S/E/W map with real
  solar/wind/daylight analysis to drive façade demand (closes the 0C loop).
- **Envelope-aware Skin:** detect contiguous perimeter skin zones and emit one
  continuous diagrid envelope + framed interior (truer to 53W53).
- **Carbon-in-the-loop:** wire L6 circularity + Building_Summary carbon into the
  Zoning summary live, so allocation trade-offs show kgCO₂e impact immediately.
- **Optimisation:** softmax %-blend + multi-objective search over thresholds
  (the "9 / 15 m" spine params) as a design-exploration tool.

---

## 6. Tomorrow's highest-value tasks

1. **Transfer-floor geometry in Hybrid** — at detected system changes, emit a
   transfer beam / belt truss. Highest narrative payoff (closes L5.5 visibly).
2. **Live carbon/circularity in the Zoning summary** — show building Skin/Foam/Intl
   % → blended kgCO₂e and circularity score; ties Zoning → LCA.
3. **Skin envelope mode** — option to build one continuous perimeter diagrid for
   skin-dominant towers instead of per-block.
4. **Performance pass** — instance repeated members (columns/diagrid) or merge per
   group; cap build cost for 50+ floor towers.
5. **Decommission `index2.html`** (or mirror) to remove ambiguity.
6. *(stretch)* Site **azimuth input** so exposure follows the real north.

---

## Progress estimates

| Component | Progress | Basis |
|---|---:|---|
| **Program Agent** | **70%** | LLM generation + file load + parser + FLOOR_DATA across 3 case studies working; lacks validation/iteration loop & richer brief inputs. |
| **Massing Agent** | **78%** | 3 parametric building types, per-floor layout engines, live params, gap-free stacking; lacks freeform/irregular footprints & boundary-polygon massing. |
| **Structure Zoning Engine** | **72%** | Matrix scoring verified cell-by-cell, exposure + position + height + span in, transition *detection* done; missing TCS scoring + softmax %-blend output + stress zone (0D). |
| **Hybrid Structure Allocation** | **58%** | Faithful per-zone port of all 3 generators + core policy; missing transition members, envelope-mode skin, shell thickness, perf. |
| **LCA Engine** | **30%** | xlsx has L6 circularity + carbon Building_Summary; LCA tab exists but not yet wired live to allocation output. |
| **Rendering Pipeline** | **30%** | Prebaked render videos + exposure/sun UI; not real-time/AI render, no per-scene output. |
| **Comparison Dashboard** | **15%** | `references/competitive-analysis.html` exists standalone; not integrated, no multi-scheme compare on live models. |

> Estimates are relative to a credible SP26-final scope, not absolute completeness.
> Zoning + Hybrid moved the most today; LCA and Comparison are the clearest laggards
> and the best targets once transition geometry lands.
