# Massing Composer — Module Logic Spec

Portable specification of the algorithm behind `massing-composer.html`.
Everything here is **platform-agnostic**: the core is pure integer/array logic
(no Three.js), so it ports directly to Grasshopper/C#, Blender/Python,
Processing, Rhino.Python, glsl, etc. The HTML file is just one renderer of it.

---

## 0. Core idea

A total massing (L × W × H in metres) is filled with **1×2 modules** snapped to
an **8'-6" cube grid**. A module/brick covers two adjacent grid cells and points
along one of three axes:

| axis code | spans cells | shape | name |
|---|---|---|---|
| `0` | `(i,j,k)`+`(i+1,j,k)` | 2×1×1 | horizontal, along **X** |
| `1` | `(i,j,k)`+`(i,j+1,k)` | 1×1×2 | horizontal, along **Z** |
| `2` | `(i,j,k)`+`(i,j,k+1)` | 1×1×2 (standing) | **vertical** (長1:寬1:高2) |

The whole system is four independent stages, each a pure function:

```
dims → SNAP → PACK → (DENSITY) → (PROTRUDE) → DEDUPE → render/export
```

Keep these stages separate when porting — each can be swapped or extended alone.

---

## 1. Constants & snapping

```js
FT      = 0.3048
MODULE  = 8.5 * FT          // 2.5908 m — the cube edge (plan AND height)
evenUp  = n => n % 2 ? n + 1 : n
evenDown= n => n % 2 ? n - 1 : n
```

Snap the input box to an integer module grid. Round **up to even** so the plan is
always perfectly tileable by 1×2 dominoes (a rectangle tiles with no leftover iff
at least one side is even; forcing both even is the simplest guarantee, and lets
L-shapes decompose into even sub-rectangles too):

```js
Wm = max(2, evenUp(round(L / MODULE)))   // modules along X
Dm = max(2, evenUp(round(W / MODULE)))   // modules along Z
F  = max(1, round(H / MODULE))           // vertical modules (courses)
```

> **Why even:** see `PROGRAM-MODULE-AREA-TABLE.md` §tileability. Odd×odd leaves a
> single 1×1 cell that no domino can cover.

---

## 2. PACK — arrangement strategies

A packing function takes `(Wm, Dm, F)` and returns an array of bricks
`[i, j, k, axis]`. Two production strategies; both **fully fill** the box.

### 2a. Even-Mix (solid, evenly distributed V/H)

Goal: vertical & horizontal modules spread as a **3D checkerboard** — no bands,
no zoning. Work in 2×2×2 macro-blocks; each block = 2 vertical + 2 horizontal
bricks, and **which row/column is vertical flips by block parity (including
height)** so verticals scatter in 3D.

```js
function evenVol(W, D, F, phase) {            // verticals in a j-row, horizontals run X
  const b = [], Fe = F - (F % 2)
  for (k = 0; k < Fe; k += 2)
    for (bi = 0; bi < W; bi += 2)
      for (bj = 0; bj < D; bj += 2) {
        par = (bi/2 + bj/2 + k/2 + phase) mod 2     // <-- the 3D checker key
        vC  = par ? bj+1 : bj                       // which row is vertical
        hC  = par ? bj   : bj+1
        b.push([bi, vC, k, 2], [bi+1, vC, k, 2])    // two vertical bricks
        b.push([bi, hC, k, 0], [bi, hC, k+1, 0])    // two horizontal (one per course)
      }
  if (F % 2) // odd top course: fill flat with X bricks
    for (j) for (i += 2) b.push([i, j, F-1, 0])
  return b
}
```

`evenVolB` is the transpose (verticals in an i-column, horizontals run Z). Four
catalogue variants = `evenVol(.,0)`, `evenVol(.,1)`, `evenVolB(.,0)`,
`evenVolB(.,1)` — same massing, different even mix. Result ≈ 40–50 % vertical.

> **Hard fact (proven by backtracking, see `solve()` below):** a *solid* box can
> **never** be filled so that every face-adjacent pair of bricks differs in
> orientation. So "even distribution" is the best a solid fill can do; strict
> alternation requires voids (next strategy).

### 2b. Porous interlock (true 3D alternation, with voids)

Greedy fill where **no two face-adjacent bricks share an axis** (X∤X, Z∤Z,
vertical∤vertical). Solid fill is impossible under this rule, so it leaves a woven
lattice (~70 % dense). The position-based preference seed varies the weave.

```js
function porousVol(W, D, F, seed) {
  occupied = grid of -1
  for each cell (x,y,z) in scan order, if empty:
    candidates = [along+X, along+Z, along+Y] whose partner cell is empty
    forbidden  = set of axes of already-placed neighbours of BOTH cells
    pref = (x + y + z + seed) mod 3                       // rotates the weave
    sort candidates by ((axis - pref) mod 3)
    place first candidate whose axis ∉ forbidden; else leave the cell empty (void)
  return placed bricks
}
```

Because each placement only checks **already-placed** neighbours and later
placements check back against it, the final result is pairwise-valid by
construction.

### Feasibility checker (use when inventing new constraints)

Before committing a new adjacency rule, test it on small boxes with backtracking:

```js
function solve(W, D, F):                 // returns true/false/"timeout"
  backtrack filling first-empty cell with a brick (+X/+Z/+Y) whose CLASS
  differs from every already-filled neighbour's class; return true if full.
```

Run on 2×2×2, 4×4×2, 4×4×4… If those are `false`, the rule is infeasible for a
solid box — switch to a porous strategy or relax the rule.

---

## 3. Randomness — stable position hash

All "randomness" is a **deterministic hash of grid position**, never `Math.random()`.
This is essential: the result is reproducible, doesn't flicker while dragging a
slider, and ports identically to any language.

```js
hash3(x, y, z) = frac( sin(x*127.1 + y*311.7 + z*74.7) * 43758.5453 )   // → [0,1)
```

Vary the multipliers / add per-feature offsets to get independent streams from the
same coordinates (see density vs protrude below). Any good integer hash works;
this sine-hash is chosen because it's identical in GLSL/Python/JS.

---

## 4. DENSITY — even voids

Keep a fraction of bricks; drop the rest using the position hash so the holes are
**evenly scattered**, not clustered:

```js
if (density < 1)
  bricks = bricks.filter(b => hash3(b.i, b.j, b.k) < density)
```

`density = 1` → solid. Lower → porous. Removing bricks can never create an
overlap, so this is always safe.

---

## 5. PROTRUDE — surface relief (凹凸)

Some **surface** modules pop out by ½ or ⅔ of a module along the face they sit on.
This is a *render offset only* — it does not change the packing.

```js
function protrudeOffset(i, j, k, axis, Wm, Dm, F, amount):
  if amount <= 0: return none
  if hash3(i+0.5, j+1.5, k+2.5) >= amount: return none        // selection stream
  // which outward faces does this brick touch? (skip the ground -Y)
  dirs = []
  if i==0: dirs += (-1,0,0)         ; if iMax==Wm-1: dirs += (+1,0,0)
  if j==0: dirs += (0,0,-1)         ; if jMax==Dm-1: dirs += (0,0,+1)
  if kMax==F-1: dirs += (0,+1,0)                              // top only
  if dirs empty: return none                                 // interior brick, no pop
  d   = dirs[ floor(hash3(k+3,i+4,j+5) * dirs.length) ]       // direction stream
  amt = (hash3(i+6,j+7,k+8) < 0.5 ? 1/2 : 2/3) * MODULE       // amount stream
  return d * amt
```

`iMax = axis==0 ? i+1 : i` (likewise jMax/kMax). Three independent hash streams =
who pops, which way, how far. Add the returned vector to the brick's world centre.

---

## 6. DEDUPE — never force, leave empty

Final safety net before rendering/exporting. Walk the bricks against an occupancy
grid; any brick that would **overlap** an occupied cell or fall **out of bounds**
is dropped (the cell stays empty). Guarantees zero overlap in every mode/setting,
and makes future experimental rules safe ("放不下就留空").

```js
function dedupe(bricks, Wm, Dm, F):
  occ = bool grid
  for [i,j,k,a] in bricks:
    (x2,y2,z2) = second cell from axis a
    if any cell out of [0,W)×[0,D)×[0,F): skip
    if occ[cell1] or occ[cell2]: skip            // would overlap → leave empty
    mark both; keep brick
```

For the validated generators this drops nothing (they're already exact); it only
bites when you add new/looser rules.

---

## 7. Render mapping (brick → box)

World centre and box size per axis (`M = MODULE`, `seam` = gap between modules;
`0` = flush, edges drawn separately mark divisions). `x0,z0` = this option's grid
origin if laying several side by side.

```
axis 0 (X):  size (2M, M, M)   centre ( x0+(i+1)M , (k+½)M , z0+(j+½)M )
axis 1 (Z):  size (M, M, 2M)   centre ( x0+(i+½)M , (k+½)M , z0+(j+1)M )
axis 2 (Y):  size (M, 2M, M)   centre ( x0+(i+½)M , (k+1)M , z0+(j+½)M )
```

Then add the protrude offset to the centre. **Colour by orientation**, not by
option: horizontal = one hue, vertical = another. Edges = a third colour outlining
every box (so flush modules still read individually).

Performance: group bricks by axis and draw each group as ONE instanced mesh (3
draw calls per option) + one merged line buffer for all edges. Keep `depthWrite`
on even when translucent, or transparent instances overlap into mush.

---

## 8. Export

Per orientation, emit the chosen option's boxes as OBJ (vertical and horizontal as
separate files so they can carry different structure/material downstream):

```js
exportOBJ(verticalOnly):
  sel = bricks where (axis==2) == verticalOnly
  for each: write 8 vertices (centre ± half-size, localised to option origin)
            write 6 quad faces (1-indexed, offset by 8 per brick)
```

---

## 9. Colour scheme (current)

| token | hex | use |
|---|---|---|
| background | `#F5F5F5` | scene + UI |
| blue | `#172FC7` (bricks softened `#8A97E5`) | horizontal modules, UI text |
| orange | `#E67033` (bricks softened `#F1A57A`) | vertical modules |
| yellow | `#EEC341` (edges softened `#F0D070`) | module edges |

---

## 10. Extension points

Add features without touching the rest by slotting into the pipeline:

- **New arrangement** → write a `gen(Wm,Dm,F) → bricks[]`, add to the options list.
  Validate with the fill checker (cover each cell exactly once) before shipping.
- **New constraint** → test feasibility with `solve()` first; if solid-infeasible,
  make it a porous greedy variant.
- **Weighted vertical ratio** → bias `evenVol`'s `par` or post-filter axis-2 bricks.
- **Directional density / gradient** → make `density` a function of `(i,j,k)`
  (e.g. taller = sparser) instead of a scalar in the filter step.
- **Bigger protrusions / recesses** → extend the amount set `{1/2, 2/3}`; negative
  amounts (push inward) make recesses — just guard the brick stays in-bounds.
- **L / courtyard / stepped outer form** → change which cells the generator fills
  (a `present(i,j,k)` mask) before packing; keep dims even so it stays tileable.

## 11. Porting checklist

1. Implement `hash3` (identical formula) — gives you reproducible randomness.
2. Port the integer generators (`evenVol`, `porousVol`) — pure loops, no deps.
3. Port `dedupe` — pure.
4. Map bricks to your platform's box primitive with the §7 centre/size table.
5. Wire four scalar controls: `density`, `protrude amount`, `opacity`, `mode`.
6. Everything else (colour, export) is presentation — adapt per platform.

The only floating-point that matters for geometry is `MODULE`; all packing is
integer, so two platforms will produce **identical module layouts** given the same
`(Wm,Dm,F, density, protrude, seed)`.
