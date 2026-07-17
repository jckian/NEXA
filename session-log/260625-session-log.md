# 260625 Session Log

Built two new browser platforms from scratch and the supporting docs, all driven
by the **8'-6" (2.5908 m) module / 1:2** system.

---

## Deliverables (new files)

| File | What |
|---|---|
| `program-tile-editor.html` | 3D drag-and-drop **program tile editor** (per-floor placement) |
| `massing-composer.html` | **Total-massing → module assembly** generator |
| `references/PROGRAM-MODULE-AREA-TABLE.md` | Common programs sized in modules (calibrated to TPAC/53W53) |
| `references/MASSING-MODULE-LOGIC.md` | Portable, platform-agnostic spec of the composer algorithm |

---

## 1. Program Tile Editor (`program-tile-editor.html`)

3D isometric editor: drag program blocks on an 8'-6" grid, load program `.txt`,
export positions back to the `EllipseAgent.outputValues` format (`x,y,z,area,
radx,rady,type,category`).

Features added across the session:
- **Module grid + snapping**; tiles auto-size per program from `PROGRAM_SPECS`.
- **Vertical / full-height volumes** for cores; `V` toggles flat↔volume, `R`
  rotates (4-way), `L` toggles rect↔L-shape.
- **Auto-orientation heuristic** — cores (`fire stair`, `elevator`, `shaft`…)
  auto-stand vertical.
- **PROGRAM_SPECS area table** calibrated to real TPAC/53W53 `{w,h}`; substring
  matching so LLM naming variants resolve.
- **Tileability normalisation** — every footprint rounded so it's perfectly
  fillable by 1×2 dominoes (rect: one even side; L: all even). Verified 0 leftover.
- **L-shape geometry** (ExtrudeGeometry) with the notch aligned to the module
  subdivision (fixed a rotateX/−Z flip bug).
- **Module subdivision lines** — each massing shown as a **1×2 domino tiling**
  (mixed orientation, greedy) on the top face + module lines on sides.
- **Timespan colour** — long (warm: core/housing/performance) vs short (cool:
  retail/F&B/office) families, distinct shade per program.
- **Vertical stacking** — drop/drag a tile onto another → rests on top (stackOff).
- **Auto core height** — cores auto-span from their base up to the tallest placed
  program (elevation-based, works with levels *and* stacking); stay solid on every
  floor they cross. Manual override available.
- **Group placement mode** — stamps a core + its adjacency bundle (from
  `EllipseAgent` rules); Arrange button cycles Cluster / Row / Column.

## 2. Massing Composer (`massing-composer.html`)

Input total **L×W×H** → snap to module cube grid → generate assembly options that
fill the box with 1×2 modules. The vertical unit is **also fixed at 8'-6"**.

Evolution of the packing logic (each step a user steer):
1. Shape variants (box / L / courtyard / ziggurat / twin) → rejected ("want a
   complete solid box, no L / holes").
2. Full-box, pattern-only variants (running / basketweave / banded).
3. **3D bricks incl. vertical** (1×1×2 standing = 長1:寬1:高2), rendered as
   InstancedMesh per axis.
4. **Cross-weave** (strict H/V alternation up each column) → still "too zoned".
5. **Even-Mix** (`evenVol`/`evenVolB`) — 2×2×2 checker, verticals scattered in 3D,
   ~40–50 % vertical, no banding. + **Porous** mode = true 3D interlock (no two
   adjacent bricks share an axis), ~70 % dense with woven voids.

> Proved by backtracking `solve()` that a **solid** box can never have every
> adjacency alternate orientation → delivered both: solid even-mix *and* porous
> interlock as two Modes.

Controls / features:
- **Opacity** slider (live), **Density** slider (even voids via position hash),
  **Protrude** slider — surface modules pop out **½ or ⅔** module along their face.
- **Dedupe safety net** — never place an overlapping / out-of-bounds module; leave
  it empty instead ("放不下不要硬放").
- **Two-colour by orientation** (horizontal blue / vertical orange) + yellow brick
  edges whose brightness follows the opacity slider.
- Modules **flush (seam 0)**; depthWrite kept on to stop transparent overlap mush.
- **Export** vertical / horizontal modules as **separate OBJ** files.

## 3. Colour scheme

Whole composer switched to a **light theme** with the 4-colour palette:
`#F5F5F5` bg · `#172FC7` blue (horizontal/UI) · `#E67033` orange (vertical) ·
`#EEC341` yellow (edges). Brick fills softened for legibility.

## 4. Spec doc

`references/MASSING-MODULE-LOGIC.md` documents the pipeline
(`SNAP → PACK → DENSITY → PROTRUDE → DEDUPE → render/export`), the integer
generators, the stable `hash3` randomness, and per-feature extension points — so
the logic can be re-implemented on other platforms (Grasshopper / Blender / etc.)
and keep being developed.

---

## Notes / open items

- Tile editor still dark-themed + timespan colours; **not yet** switched to the
  4-colour palette (pending user decision on how to re-encode timespan).
- Protrude supports negative (recess) as a future extension; currently outward only.
- All packing is integer → identical layouts across platforms for the same
  `(Wm,Dm,F, density, protrude, seed)`.
