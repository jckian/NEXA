# Demountable Frame + Infill — Assembly Reference

A reference for how the block-modules inside **`group-vertical frame`** combine,
**generalized so the same logic applies to every horizontal frame, vertical frame, and infill.**
Pairs with the machine-readable grammar in `frame_infill_assembly_grammar.json`.

> **Units.** The model carries no explicit unit. Storey ≈ 260 and lumber sizes
> (91.44 = 3 ft, 27.94 = 11 in, 17.78 = 7 in) imply **1 unit = 1 cm**. Treat all
> numbers as cm unless re-based. Relationships (ratios, clearances, grid) hold at any unit.

---

## 1. The one idea

Everything is built from one repeated object: a **frame cell**.

> **A cell = 8 corner CON nodes + frame members on the edges + infill in the volume.**

This invariant is identical whether the cell reads as a *horizontal bay* or a
*vertical bay*. Build any frame by composing cells; fill any cell with infill.

---

## 2. Coordinate system & grid

- Right-handed, **Z up**, strictly **orthogonal**. Parts are placed only at rotations of `0, 90, 180, -90`.
- Planning module **M = 260**. Long spans = **2M = 520**.
- Storey height **260**; mezzanine / half-level insert at **+130**.
- Frame cell **internal = 270**, module **= 260** → **10 total clearance (≈5 per side)** so infill slides in.
- Deck / partition panels tile faces on a **120 × 240** sub-grid.

---

## 3. Kit of parts

| id | role | class | size (cm) | scale | colour | notes |
|---|---|---|---|---|---|---|
| **CON** | connector node | joint | 32 × 32 × 32 | ×1 | gray (105,105,105) | hollow slotted cube, dry plug-in. Variants: `T-CON`, `CON-UPPER`, `CON-LOWER` |
| **frame-hor** | horizontal frame | frame | 520 × 270 × 270 | ×1 | black | bars + plates + C-rails + 8 corner CON; gives a storey ring edge |
| **VERTICALFRAME** | vertical frame | frame | 266 × 269 × 530 | ×100 (modelled 1/100) | black | COL column + rails + 8 corner CON; spans ~2 storeys |
| **1_@01** | volumetric module | infill | 260 × 520 × 260 nominal | ×1 | orange (255,127,0) | one per bay-cell; nests with clearance |
| **module-deck** | deck / partition | infill | 120 × 240 × 10 | ×100 (modelled 1/100) | black | floor if horizontal, wall if vertical |
| **STR** | stair unit | infill | 231 × 239 × 249 | ×1 | black | 14 boxes; treads step +17.78; stack to climb |

---

## 4. The joint — CON node

The whole system hangs on one standardized connector.

- **Geometry:** 32³ hollow slotted cube, ~13 % solid (thin walls), **no bolt holes** → a *dry* joint.
- **Placement:** at all **8 corners** of every cell (4 bottom + 4 top). Generate one base node, then **octant-mirror** it about the cell-centre planes (x = cx, y = cy, z = cz) into the other 7 corners.
- **Three joint behaviours** (one node does all of them, in up to 6 directions):
  - **Vertical member end → deep plug-in socket** (~30, near full depth) — columns/struts spigot into the node.
  - **Horizontal member end → beam-corner merge** (~32) — the horizontal frame's own corner *is* the node.
  - **Stacked unit above → stack / register** (~2) — the next frame/module rests on the node's top face.
- **Design-for-Disassembly:** reversible, dry, demountable. Same node resolves column–beam, beam–beam, module–module and level–level.

---

## 5. Frame cell — the generalization

A cell is an orthogonal box:

- **8 corners** → CON nodes.
- **12 edges** → frame members:
  - **horizontal edges** ← `frame-hor` rings (`rotZ 0` spans X, `rotZ -90` spans Y); a top and/or bottom ring.
  - **vertical edges** ← `VERTICALFRAME` columns (can span 2 storeys).
- **6 faces** → `module-deck` panels (horizontal face = floor, vertical face = wall/partition).
- **1 volume** → `1_@01` module, or `STR` circulation, or void.
- **Size** → N·M wide × N·M deep × storey(s) tall on the 260 grid.

**Apply to any frame:**

- A **horizontal frame** = a cell with `frame-hor` rings top/bottom; deck its horizontal faces for floors.
- A **vertical frame** = the *same* cell with `VERTICALFRAME` columns on the vertical edges (may span 2 storeys); deck its side faces for walls.
- **Infill** = drop a module, panels, or stairs into the cell volume; infill is swappable independent of the frame.

---

## 6. Assembly procedure (identical for H-frames, V-frames, infill)

1. **Lay grid** — 260 in X/Y/Z; storeys at 260, half-levels at 130.
2. **Place nodes** — a CON at each cell corner (octant-mirror one base).
3. **Span edges** — `frame-hor` on horizontal edges, `VERTICALFRAME` on vertical edges; member ends plug the CON sockets.
4. **Drop infill** — `1_@01` nests (≈5/side clearance); `module-deck` tiles faces; `STR` fills circulation cells and stacks at storey pitch.
5. **Orthogonal + reuse** — rotations only `{0,90,180,-90}`; reuse one CON via mirroring and one mesh per part via instancing.

---

## 7. Worked example — `group-vertical frame`

A 1-bay, multi-storey vertical unit (overall **1031 × 770 × 1058**) that instantiates the grammar once.

Top → bottom:

1. **Horizontal frame ring** (z ≈ 0): `frame-hor` (rotZ 0, spans X) + `frame-hor` (rotZ -90, spans Y); **8 CON nodes** at z = −14 and z = −245; one `1_@01` module nested (rotZ 90).
2. **Stair stack** (z ≈ −231): three `STR` units at z = −231, −498, −756 (pitch ≈ 260).
3. **Room band** (z ≈ −525): four `1_@01` modules forming a floor of rooms.
4. **Deck floor** (z ≈ −779): four `module-deck` panels (rotZ ±90 pairs).
5. **Base structure** (z ≈ −784): one `VERTICALFRAME` (2-storey, rotZ −90).

**8 CON node centres:**
`(491,−230,−14) (491,1,−14) (−1,−230,−14) (−1,1,−14)` /
`(491,−230,−245) (491,1,−245) (−1,−230,−245) (−1,1,−245)`

The 8 nodes define one structural cell (top); horizontal frames span its edges;
the cell and the cells below host modules, decks and stairs — the grammar in §5–6,
instantiated once.
