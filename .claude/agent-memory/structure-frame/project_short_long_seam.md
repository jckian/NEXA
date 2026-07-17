---
name: project_short_long_seam
description: How the SHORT-kit/LONG-frame vertical seam works and where its overlap bug lived (fixed 2026-07-06)
metadata:
  type: project
---

The SHORT-kit (buildShortBlocks) and LONG-frame (buildStructure) boundary is not just a
nominal floor-height sum match — it has TWO independent sources of vertical mismatch:

1. **Course-count overshoot**: `buildShortBlocks` fills a run of consecutive SHORT floors
   on a continuous 8'-6" (MODULE) course grid. `K` (course count) is bumped past `natK`
   (the run's nominal height in courses) whenever the SHORT footprint area needs more
   courses than the nominal run height supplies (line ~916 in the file, `K = Math.min(natK+4,
   Math.max(natK, Math.ceil(area/S)))`). When this happens the module stack's TRUE top
   (`base + K*MODULE`) rises past the nominal top of the run.
2. **Hang-below structural depth**: every LONG floor's girders/slab in `buildStructure` are
   drawn hanging BELOW their nominal `yBase(lv)` line (main girder `PRI_H`=0.80 m is the
   deepest). This is harmless over a LONG floor below (sparse frame, open air) but is a real
   collision over a SHORT run, whose bricks are solid volume right up to the nominal line.

In the built-in SAMPLE (SHORT floors L1-L3, boundary at L4/level 3), mechanism #1 contributed
ZERO overshoot (K==natK==3 exactly) — the ENTIRE 0.8 m overlap the user saw was from
mechanism #2 alone. Chasing only the course-count formula (the task's stated hypothesis)
would have produced a fix with the shift map computed but all zeros — a fix that "works"
(no syntax errors, no crash) but doesn't touch the actual bug. Always verify the numeric
overshoot with a counting script BEFORE trusting a hypothesis about which mechanism causes
an overlap — the task description's proposed root cause was incomplete.

**Fix** (2026-07-06, program-massing-shortfloor.html, buildStructure): a "SHORT-STACK
BOUNDARY SHIFT" block re-derives K per SHORT run read-only (same formula as
buildShortBlocks, never edits it), computes `stackTop = base + K*MODULE`, and requires
`stackTop + PRI_H <= nominal yBase(boundaryLv)`; any shortfall is applied as a rigid
translation to the boundary floor and every level above it (shadows the `yBase` parameter
inside buildStructure so every downstream use — columns/girders/slabs/roof/curtain/fins —
picks it up automatically). See [[feedback_debug_hooks]] for how this was verified.

**How to apply**: any future SHORT/LONG seam work must account for BOTH mechanisms. If
asked to touch `COLSTEP`, `PRI_H`, or SHORT floor-height logic again, recheck this shift
block's math (particularly which member's depth is used as the required clearance — it's
hardcoded to `PRI_H` as the deepest hang-below member, main girder).

**Refinement (same day, 2026-07-06, second pass)**: the K-budget `stackTop` used above is
only an UPPER BOUND on courses — the porous packer (`porousMasked` in `buildShortBlocks`)
leaves any footprint cell that can't find a valid pairing partner UNPLACED (no brick, no
volume), so the true physical top can be below `base + K*MODULE` even when `K > natK`. User
reported a persisting air gap under the boundary floor ("4F too high") pointing at this. Fix:
`buildShortBlocks` now computes the REAL top per run from its own placed `bricks` (`[i,j,k,a]`,
top = `k + (a===2?2:1)`) plus `stairSet` occupied courses, and publishes it to a new
module-level `Map SHORT_STACK_TOP` (keyed by `run[0]`, reset in `build()` next to
`SHORT_PLACE = null`). `buildStructure`'s shift block now reads `SHORT_STACK_TOP.get(run[0])`
as the primary source of truth; the old K-budget re-derivation is demoted to a fallback used
only when the map has no entry (buildShortBlocks' early-return path at `if (structure &&
!BLOCKS) return;` — no packer ran, so no real top exists to publish).
Verified on the built-in SAMPLE (run levels 0-2, boundary L3/"4F"): `oldBudgetTop` and
`actualTop` happened to coincide exactly (15.5448 m, excess 0.8 m = PRI_H) — the SAMPLE's
SHORT footprint pairs perfectly with no leftover cells, so this dataset does not exercise the
differential case. Confirmed numerically (not just by eye) that after the shift the nearest
main girder's underside (`cy - h/2`) at the boundary level equals `actualTop` to floating-point
precision — true flush, zero gap. The K-budget/actual-top divergence will only show up on
programs whose SHORT footprint leaves unpairable cells at the top course — worth re-testing
against a real user-authored `output.txt` if this seam is revisited, since the SAMPLE alone
cannot falsify the old formula.
