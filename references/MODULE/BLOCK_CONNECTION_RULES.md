# Block Connection Rules — sub-block joints & combination grammar

How the four kit components (`frame_horizontal`, `frame_vertical`, `infill 1_@01`,
`build_str STR`) **decompose into sub-blocks**, how those sub-blocks **join**, and the
**rules for combining blocks into rooms of any size**. Numbers are measured from the
extracted geometry (cm; 1 unit = 1 cm, storey ≈ 260). Pairs with
[`BLOCK_ASSEMBLY_REFERENCE.md`](BLOCK_ASSEMBLY_REFERENCE.md) (the high-level idea) and
is the detailed joint layer under it.

---

## 0. The invariant  ⚠️ corrected

> **FRAME and INFILL are two independent populations on one 260 grid.**
> Frames are laid out first as a **structural lattice** (rings + columns at cell
> boundaries); INFILL modules then **drop into the interstitial cells *between* the
> frames**. They are **volumetrically disjoint — infill never sits *inside* a frame and
> the two never overlap** (a ~5 cm clearance keeps them apart). **Infill count ≠ frame
> count** — one frame is shared by the cells around it, and frames are placed only where
> structure is needed, so there are typically **far more infill modules than frames**.

Proof — the worked block `group-vertical frame` (`rule_build_group_vertical_frame.py`,
`SCENE`): **5 × `1_@01` infill, 2 × `frame-hor`, 1 × `VERTICALFRAME`, 3 × `STR`**. The
infills stack/tile through the height as the rooms; the two horizontal frames sit at two
storey junctions and the single vertical frame braces the base two storeys — i.e. frames
are **sparse joints between the infills**, not a wrapper around each one. A volume-overlap
test confirms frame ∩ infill = only edge-touching (≤ the 5 cm clearance), never solid overlap.

Everything registers to a **260 cube grid** (M = 260). A bay is **2M × 1M × 1 storey**.
The **CON node is the only joint type** — every member-to-member and unit-to-unit
connection resolves through it. (This kit is built **without** CON — the group script strips
them — so the members meet directly at the grid lines they'd otherwise share via a node.)

---

## 1. Sub-block decomposition (measured)

### FRAME-HORIZONTAL — a 2M×1M storey ring (≈ 520 × 270 × 270)
| sub-block | size (cm) | ×n | role / where |
|---|---|---|---|
| `frame_main` | 519.8 × 259.1 × 259.1 | 1 | the ring body (2-bay box edge) |
| `rail_bottom` / `rail_top` | 519.8 × 10 × 10 | 1+1 | long **C-rails**, bottom (z≈−10) & top of ring, run X |
| `crail_a` / `crail_b` | 519.8 × 5 × 10 | 1+1 | secondary C-rails at the front/back top (z≈244) |
| `plate_a`/`b` (floor) | 115.7 × 239.1 × 5 | 2+2 | horizontal **deck plates** (z≈−10) → floor face |
| `plate_c`/`d` (soffit) | 115.7 × 5 × 239.1 | 1+1 | plates on the top ring (y≈254) |
| `bar_a…d` | ~73–76 × 5 × 5 | 11 | small top-edge in-fill bars closing the ring top |
| `clip_a`/`b` | ~5–12 × 10 × 5 | 2+2 | end **clips** that lock the ring to the corner CON |
| `CON node` | 31.4³ | 8 | corner joints (octant-mirror of one node) |

CON centres (one bay): `X = {−254.2, +237.3}`, `Y = {14.1, 245}`, `Z = {4.1, 235}`
→ node-to-node span ≈ **491 × 231 × 231**, overall ≈ **523 × 262 × 262 ≈ 2M×1M×1 storey**.

### FRAME-VERTICAL — a 1M×1M column spanning 2 storeys (≈ 260 × 260 × 520)
| sub-block | size (cm) | ×n | role |
|---|---|---|---|
| `column_COL` | 259.1 × 259.1 × 519.8 | 1 | the 2-storey **column** body (vertical edge) |
| `rail_bottom` | 259.1 × 5 × 10 | 2 | ring-register rail at **z ≈ −5** (storey 0) |
| `bar_top_a` / `bar_mid` | 259 × 5 × 10 / small | 2+ | register rail at **z ≈ 254** (storey 1 line) |
| `rail_top_a`/`b` | 259.1 × 5 × 10 | 4 | register rail at **z ≈ 515** (storey 2 / top) |
| `post_side` | 5 × 259 × 10 | 1 | side stiffener |

> Key: the vertical frame carries **register rails at every storey (z ≈ 0, 260, 520)** so a
> horizontal ring can land on it at each level. (Its CON block is commented out in the
> source → vertical frame ships **members only**; nodes come from the horizontal rings.)

### INFILL 1_@01 — the 1M×2M×1-storey volume module (≈ 260 × 520 × 260)
| sub-block | size (cm) | role |
|---|---|---|
| `part_03` | 259.1 × 518.2 × 259.1 | the module shell (the filler volume) |
| `part_01` / `part_02` | 5 × 114.1 × 239.1 | thin **end partitions** (the ±long-end faces) |

Nominal **260 × 520 × 260** → **10 cm smaller than the 270 frame internal** ⇒ **~5 cm
clearance per side**: the module *slides into* the ring, it does not bear on it laterally.

### STR stair — a ~1M×1M×1-storey circulation filler (≈ 231 × 239 × 249)
| sub-block | size (cm) | ×n | role |
|---|---|---|---|
| `step` | 27.9 × 91.4 × 17.8 | 10 | treads; **rise +17.8**, run 27.9; two flights |
| `block` | 91.4 × 91.4 × 17.8 | 2 | landings |
| `bar` | 91.4 × 27.9 × 17.8 | 2 | landing support |

One STR climbs ≈ 249 ≈ **one storey**; stack at storey pitch (260) to go higher.

---

## 2. The joint — CON node (the whole grammar hangs here)

A 32³ slotted cube at **all 8 corners** of every cell. One node resolves **three
behaviours simultaneously**, in up to 6 directions:

| direction of the incoming part | joint behaviour | engagement |
|---|---|---|
| **vertical member end** (column / post) | deep **plug-in socket** | ~30 (near full node depth) |
| **horizontal member end** (rail / bar) | **beam-corner merge** (the ring corner *is* the node) | ~32 |
| **unit stacked above** (next frame / module) | **stack / register** on the node's top face | ~2 gap |

Rules:
- **R-CON1** Place one CON at each of the 8 cell corners; generate one, **octant-mirror**
  about the cell-centre planes for the other 7.
- **R-CON2** A member only connects where its end lands **inside a CON's socket zone**
  (corner ± ~16 cm). No node ⇒ no valid joint ⇒ leave the edge open.
- **R-CON3** Adjacent cells **share the CON column line** on the shared edge — emit the
  node once, not per cell (dry, reversible, demountable).

---

## 3. INFILL ↔ FRAME — how infill inserts *between* frames  ⚠️ corrected

Infill is **not** placed inside a frame. The frame lattice is laid down first; each infill
module then **fills a grid cell that is bounded by frames on its faces**, held off them by a
~5 cm clearance so **infill and frame occupy disjoint volumes**. The frame borders the cell;
the infill *is* the cell. Per infill face (local module axes: **X** = 2M long, **Y** = 1M,
**Z** = up):

| infill face | the frame it butts against (across the gap) | rule |
|---|---|---|
| **bottom −Z** | the `frame-hor` ring **below** (the lattice line at this storey) | **seats / registers** on the ring's top face (stack gap ~2). Floor `module-deck` tiles this face. |
| **top +Z** | the `frame-hor` ring **above** | sits **just under** it; ~5 gap. |
| **long ends ±X** (2M) | `frame-vertical` **columns on the shared cell edges** | module end partitions (`part_01/02`) face the columns across **~5 clearance** (nest, don't bear). A column is **shared** with the neighbouring cell. |
| **side faces ±Y** (1M) | the ring's Y members / the adjacent cell | open (glazing) **or** a `module-deck` panel; if a neighbour cell abuts, the two infills share that plane. |

- **R-IF0 (disjoint, not nested):** infill and frame **never overlap**. The frame is the
  lattice; infill drops into the hole between frame members. Counts differ — do **not**
  emit one frame per infill.
- **R-IF1 (nest with clearance):** the module (260) sits in a cell whose framed opening is
  ~270 ⇒ **≥5 cm all round**; never size infill to the frame.
- **R-IF2 (seat down):** infill **registers on the ring below** (gravity); it hangs from nothing.
- **R-IF3 (swap-in-place):** any filler (`1_@01`, `STR`, or void) is **interchangeable in a
  cell** without touching the surrounding frames.
- **R-IF4 (orientation):** infill's 2M axis aligns with the cell's 2M direction; rotating a
  cell 90° (rotZ) rotates its infill with it. Neighbouring cells may run 2M **perpendicular**,
  so an infill's long end can face another infill's side — they still just share the grid plane.

---

## 4. FRAME ↔ FRAME — tiling & stacking

**In plan (grow a floor):**
- **R-FT1** Lay `frame-hor` rings on the M grid. Each ring = one **2M×1M bay**.
- **R-FT2** Two bays meeting on an edge **share that edge's CON line + column** (R-CON3);
  don't double the members.
- **R-FT3** A ring may point **X-long (rotZ 0)** or **Z-long (rotZ 90)**. Prefer adjacent
  bays to **alternate direction** → the 2M spans interlock (woven, no continuous seam).
- **R-FT4** Odd leftover cell (a 1×1 that no 2M bay covers) → **leave void** or cap with a
  half-level insert; never force a partial module.

**In section (grow height):**
- **R-FV1** Stack a `frame-hor` ring at **every storey** (z = 0, 260, 520 …).
- **R-FV2** Put `frame-vertical` columns on the **vertical edges**; each spans **2 storeys**
  and carries register rails at z ≈ 0 / 260 / 520, so the intermediate ring lands on it.
- **R-FV3** Add a new vertical frame **every 2 storeys** (parity), aligned to the same
  column line so columns **stack continuously to the ground** (else it is a cantilever/transfer).
- **R-FV4** Mezzanine / half-level ring inserts at **+130**.

---

## 5. STAIR (circulation) connection

- **R-ST1** A stair occupies a **whole cell** as the infill (swap rule R-IF3): drop `STR`
  instead of `1_@01`.
- **R-ST2** It seats on the lower ring (R-IF2) and **stacks at storey pitch 260** — one STR
  per storey climbed; align landings across floors so flights are continuous.
- **R-ST3** A stair cell wants a **vertical frame on ≥2 of its edges** (it is the vertical-
  circulation core → treat as main structure, full column, not cantilever).

---

## 6. Growing to an arbitrary W × D × H space

Given a target room of `W × D` modules and `H` storeys — **lattice first, then infill the gaps**:

1. **Grid** → mark the 260 lines over `W × D × H`; define cells as 2M×1M bays, alternating
   orientation (R-FT3); odd cell → void (R-FT4).
2. **Frame lattice (sparse, shared)** → lay `frame-hor` rings along the **storey planes** and
   `frame-vertical` columns on the **vertical cell edges**. Frames are **shared between
   adjacent cells and placed only where structure is needed** (bay boundaries, braced bays,
   every-2-storey verticals R-FV3) — **not one per cell**.
3. **Insert infill** → drop a `1_@01` into each cell **between** the frames (R-IF0..4),
   seating on the ring below with clearance; swap to `STR` where circulation is needed (R-ST1).
   Expect **more infills than frames**.
4. **Height** → repeat storey rings; verticals span 2 storeys and must stack to ground (R-FV1..3).
5. **Skin** → `module-deck` on exposed ±Y faces (wall) and each floor's −Z face (deck); leave faces open for glazing.
6. **Close the top** → a `frame-hor` ring caps the top storey (roof), decked.

Everything stays on the **260 grid**, rotations only `{0, 90, 180, −90}`, every join through a
CON node — so the same kit assembles a 1-bay pod or a full floor plate identically, and any
cell is **demountable / swappable** without disturbing its neighbours.

---

## 7. Machine-readable connector table

Per block face → what must be present for a valid dry joint (`M = 260`):

```
populations: FRAME = sparse shared lattice ; INFILL = fills cells BETWEEN frames ; disjoint (≥5 gap) ; #infill ≠ #frame
CON:        6 faces → sockets; accepts {vertical:plug(30), horizontal:merge(32), unit:stack(2)}
frame-hor:  ends(±X,±Y) → CON corner-merge ; top(+Z) → stack/next ring ; bottom(−Z) → CON/lower ring
frame-vert: ends(±Z) → CON plug(30) ; sides → register rails meet ring at z∈{0,260,520}
infill:     −Z → seat on lower ring ; +Z → nest under upper ring(≥5 gap) ; ±X → face columns(≥5) ; ±Y → deck/open
stair:      −Z → seat on lower ring ; +Z → next STR at +260 ; ≥2 edges → vertical frame
grid:       plan 260 ; bay 520×260 ; storey 260 ; half-level 130 ; frame internal 270 = module 260 + 5/side
```
