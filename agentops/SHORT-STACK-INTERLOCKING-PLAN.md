# SHORT Stack Cross-Layer Interlocking — Implementation Plan

**Status:** 260704, approved by user.  
**Owner:** module-packer agent (or sonnet-level direct work).  
**Impact:** `buildShortBlocks` (789–990), `rests()` gravity check (819), brick/floor height contract.

---

## Problem Statement

Current `buildShortBlocks` stacks 1×2 bricks **per-level** within each SHORT-floor run: bricks are forced to align with floor slabs, unable to interlock across layers. Result: wasted packing efficiency and a non-monolithic feel.

**Target:** Same program's bricks can physically span up to 3 consecutive layers, interlocking like real stacking — a brick placed at L1 can have its top edge at L3 slab level, with L2 slab cutting through the middle of the brick (the brick carries its own support frame at each slab intersection; slab has no openings).

---

## Constraints (User-Specified)

1. **Max span:** bricks may cross ≤3 layers (e.g., a brick from L0 to L2 is OK; L0 to L3 is out).
2. **Self-supporting:** bricks self-carry at each floor level via internal structure (slab openings → user will model separately in Rhino).
3. **LONG boundary:** bricks NEVER cross from SHORT into LONG cells — SHORT cells must stay entirely within the range of SHORT-classified levels.

---

## Data Structure Changes

### Current

```javascript
SHORT_PLACE = {
  frameHx: [{x,z,w,d}],  // per-floor lists
  frameHz: [{x,z,w,d}],
  infillX: [{x,z,w,d}],
  infillZ: [{x,z,w,d}],
  frameV: [{x,z,w,d}],
  stair: [{x,z,w,d,levels}]
}
```

Each list is a flat array of bricks at a floor level; level is implicit in the context.

### Proposed

```javascript
SHORT_PLACE = {
  bricks: [
    { x, z, w, d, level_base, level_top, program, axis, role }
    // level_base: foundation level
    // level_top: top level (base + 0/1/2, so span ≤3)
    // program: which SHORT program this belongs to
    // axis: 'x' or 'z' (1×2 orientation)
    // role: 'frame', 'infill', 'stair', 'vertical'
  ],
  stairs: [ { x, z, w, d, level_base, level_top, shaft_id } ]
}

// Derived at export time:
FRAME_PARTS = [...] // all bricks with role ∈ {frame, vertical, stair}
INFILL_PARTS = [...] // all bricks with role = infill
```

**Why:** level_base + level_top make the brick's 3D extent explicit; role moves out of the dict key structure (cleaner per-brick logic).

---

## Algorithm Rewrite — `buildShortBlocks`

### Stage 1: Identify SHORT runs (unchanged)

```javascript
const shortRuns = [];  // [{level_first, level_last}, ...]
let inRun = false, runStart = null;
for (let lv of shortFloors.sort((a,b) => a-b)) {
  if (!inRun) {
    runStart = lv;
    inRun = true;
  }
  if (lv is not consecutive from runStart) {
    shortRuns.push({ level_first: runStart, level_last: prev_lv });
    runStart = lv;
  }
}
// close last run
```

### Stage 2: Pack each run with cross-layer bricks (NEW)

For each `run = {level_first, level_last}`:

**2a. Collect all SHORT cells in the run across all levels**

```javascript
const cells = [];
for (let lv = level_first; lv <= level_last; lv++) {
  for (let rect of L.floorRects[lv]) {
    if (rect.isShort or rect in shortFloors[lv]) {
      cells.push({ ...rect, level: lv });
    }
  }
}
// cells: flat list of all SHORT cells, each tagged with its level
```

**2b. Greedy brick placement with cross-layer stacking**

```javascript
const placed = [];  // final brick list
const occupied = new Set();  // (x,z,lv) → true if a cell is covered

for (let cell of cells sorted-by-area-descending) {
  // Try to place a brick at cell, optionally spanning up to 3 layers
  
  let brick = null;
  
  // Attempt 1: 3-layer brick (if possible)
  if (cell.level + 2 <= level_last) {
    brick = tryStackBrick(cell, 3, occupied, cells, run);
  }
  
  // Attempt 2: 2-layer brick
  if (!brick && cell.level + 1 <= level_last) {
    brick = tryStackBrick(cell, 2, occupied, cells, run);
  }
  
  // Attempt 3: 1-layer brick (fallback)
  if (!brick) {
    brick = tryStackBrick(cell, 1, occupied, cells, run);
  }
  
  if (brick) {
    placed.push(brick);
    // Mark all cells under the brick as occupied
    for (let lv = brick.level_base; lv <= brick.level_top; lv++) {
      occupied.add(`${brick.x},${brick.z},${lv}`);
    }
  }
}
```

**Helper: `tryStackBrick(cell, height, occupied, cells, run)`**

```javascript
function tryStackBrick(baseCell, height, occupied, allCells, run) {
  // Can we place a brick at baseCell, spanning from baseCell.level to baseCell.level + (height-1)?
  
  const { x, z, w, d, level } = baseCell;
  const level_top = Math.min(level + (height - 1), run.level_last);
  
  // Constraint 1: LONG boundary — never cross into LONG
  for (let lv = level; lv <= level_top; lv++) {
    if (!shortFloors.has(lv)) return null;  // would cross into LONG
  }
  
  // Constraint 2: all cells under the span must be SHORT and unoccupied
  for (let lv = level; lv <= level_top; lv++) {
    if (occupied.has(`${x},${z},${lv}`)) return null;
  }
  
  // Constraint 3: gravity — if height > 1, brick must rest on something below
  if (height > 1) {
    const hasSupport = occupied.has(`${x},${z},${level - 1}`)
      || (level === run.level_first);  // base of the run is ground
    if (!hasSupport) return null;
  }
  
  // Success
  return {
    x, z, w, d,
    level_base: level,
    level_top,
    program: baseCell.program,
    axis: (w >= d) ? 'x' : 'z',
    role: 'infill'  // will be reassigned by FRAME/INFILL logic later
  };
}
```

### Stage 3: FRAME vs INFILL split (MODIFIED)

Currently (928–934): bricks are ranked by exterior distance per level.  
**New:** bricks ranked by exterior distance across the entire run (multi-level distance from the run's perimeter).

```javascript
// Compute exterior distance for each brick at the run level
// (distance = how many bricks deep it is from the run's outer boundary in XZ)
const distanceFromPerimeter = new Map();
for (let brick of placed) {
  const level = brick.level_base;  // use the base level for boundary calc
  const dist = computeExteriorDistance(brick.x, brick.z, brick.w, brick.d, level, cells);
  distanceFromPerimeter.set(brick, dist);
}

// Assign FRAME to deep bricks + all verticals; INFILL to shallow bricks
const shallowThreshold = Math.ceil(maxDistance / 2);
for (let brick of placed) {
  const dist = distanceFromPerimeter.get(brick);
  if (dist <= shallowThreshold || brick.axis === 'vertical') {
    brick.role = 'frame';
  } else {
    brick.role = 'infill';
  }
}
```

### Stage 4: Stair insertion (MODIFIED)

Current (901–916): one stair per multi-floor connected component.  
**New:** same logic, but now each stair spans the entire height of its cluster (from the lowest SHORT cell it serves to the highest), using the new `level_base` / `level_top` contract.

```javascript
const stairClusters = computeConnectedComponents(cells, shortFloors);
// Each cluster: a set of cells that touch (horizontally) across the run.

for (let cluster of stairClusters) {
  if (cluster.size < 4) continue;  // skip tiny clusters
  
  const min_lv = Math.min(...cluster.map(c => c.level));
  const max_lv = Math.max(...cluster.map(c => c.level));
  
  // Place a stair at the cluster's centroid, spanning min_lv to max_lv
  const centroid = clusterCentroid(cluster);
  const stair = {
    x: centroid.x,
    z: centroid.z,
    w: 2, d: 2,  // or your stair footprint
    level_base: min_lv,
    level_top: max_lv,
    role: 'stair'
  };
  
  placed.push(stair);
}
```

---

## Downstream Changes

### `rests()` gravity check (line 819)

**Current:** checks if `bricks[i].z >= bricks[j].z` (same level stacking).  
**New:** checks 3D support:

```javascript
function rests(brick_i, brick_j) {
  // Does brick_j support brick_i?
  // True if: brick_i.level_base === brick_j.level_top + 1 AND they overlap in (x,z)
  return (brick_i.level_base === brick_j.level_top + 1) &&
         doRectsOverlap(
           { x: brick_i.x, z: brick_i.z, w: brick_i.w, d: brick_i.d },
           { x: brick_j.x, z: brick_j.z, w: brick_j.w, d: brick_j.d }
         );
}
```

### `addInst` and `addBox` calls (mesh emission)

**Current:** bricks are 1×2×(single slab height).  
**New:** bricks are 1×2×(span height × slab height).

```javascript
// Current (assume one slab height per brick):
const h = floorHeightOf(brick.level);

// New:
const h_base = yBase(brick.level_base);
const h_top = yBase(brick.level_top) + slabHeight;
const h = h_top - h_base;
```

### Export (`SHORT_PLACE` → OBJ)

**Current:** `exportKitOBJ` reads flat lists per role per level.  
**New:** reads the unified `SHORT_PLACE.bricks` array, filters by `role`, emits one OBJ per role:

```javascript
// Before exporting, separate bricks by role:
const frame_bricks = placed.filter(b => b.role === 'frame');
const infill_bricks = placed.filter(b => b.role === 'infill');
const stairs = placed.filter(b => b.role === 'stair');

// Then mesh each, respecting their level_base / level_top spans
```

---

## Testing / Acceptance

1. **Geometry:** screenshot before/after; visually verify bricks now cross layers instead of stacking per-floor.
2. **Gravity:** run `rests()` on all placed bricks; every unsupported brick should be on the base level or resting on an earlier brick.
3. **LONG boundary:** verify no brick extends into a LONG-classified floor. Script: `for all bricks, max(brick.level_top for all levels) < min(LONG level)`.
4. **Span cap:** verify no brick spans >3 layers. Script: `max(brick.level_top - brick.level_base) = 2` (i.e., spans 3 floors total).
5. **FRAME/INFILL count:** compare before/after (should be roughly the same due to reassignment logic, not major changes).

---

## Files to Edit

**Primary:** `program-massing-shortfloor.html`
- `buildShortBlocks` (entire function 789–990, rewrite 80% of it)
- `rests()` helper (819)
- `SHORT_PLACE` shape definition comment (970)
- `addInst` calls that use single-level slab height (945–989) — adapt to multi-level heights
- `exportKitOBJ` (1165) — update to read new brick shape

**Spec doc:** `references/MASSING-MODULE-LOGIC.md`
- §3 (Packing): add "bricks may span up to 3 consecutive levels; max span constrained by gravity and LONG boundary"
- Add a new subsection on the multi-level brick contract (level_base, level_top, role)

---

## Effort & Model Recommendation

- **Complexity:** High. This is the core packing algorithm; many edge cases (gravity, LONG boundary, FRAME/INFILL logic).
- **Model:** sonnet is OK for implementation, but **escalate to opus if gravity logic + LONG boundary constraint proves difficult to enforce together**. (This is a coupled-constraint problem per D §1.)
- **Testing:** **mandatory fresh-context visual-verifier run** on the screenshot before signing off.
- **Timeline:** plan for 2–3 focused work cycles (initial rewrite → test gravity → test LONG boundary → export proof).

---

## Rollback / Fallback

If the cross-layer packing proves unstable (gravity loops, LONG-boundary breaches, or export misalignment), fallback to:
1. Keep the `tryStackBrick` helper but cap it at height=1 (revert to per-level).
2. Both `SHORT_PLACE` data structure and the rendering/export code remain updated (no rollback there), so the change is transparent to downstream.

---

## Handover to Agent

When `module-packer` (or executor) begins:
- Read this doc in full first.
- Then read current `buildShortBlocks` (lines 789–990) with understanding of the current per-level packing.
- Implement Stage 1–2 and Stage 4 (packing + stair insertion).
- Adapt Stage 3 (FRAME/INFILL) and downstream sections.
- **Critical:** after every edit, run the local server screenshot loop and verify at least one cross-layer brick actually appears in the 3D scene.
