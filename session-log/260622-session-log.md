# 260622 — Session Log

**Role of this doc:** senior PM / tech-lead review of today's activity on the
AI-driven architectural design platform (Voro / Program Agent).
**Focus of the day:** reverse-engineer the **DfD 14ft cube** Rhino prototype and
build it into `index.html` as a full structural system + Hybrid-zoning option,
with real materials, a section tool, and program-lifecycle-driven allocation.

---

## 1. What was accomplished

### A. Read & analysed the Rhino prototype `references/260620_unitTest_DfD.3dm`
- Parsed the `.3dm` with `rhino3dm` (Python). Decoded the Design-for-Disassembly
  system: a **14 ft (4.2672 m / 426.7 cm) cube module**, arrayed 5×5×3 (75 modules).
- Per module: **4 columns + 8 beams** (19 cm ≈ 8" sections), **8 corner connection
  nodes** (31.6 cm), a **hollow raised-floor deck** cassette, clip-on facade panels,
  demountable partitions — all dry/bolted = reversible.
- Confirmed with the user the design intent: cube frame matrix with **partitions
  bolted to the corner connection parts**.

### B. Standalone viewer `dfd-unit-diagram.html`
- New single-file CDN-Three.js viewer (repo convention): parametric cube matrix,
  connection nodes, partitions bolted to nodes, controls + bill of components.
  (First deliverable; the real work then moved into `index.html`.)

### C. DfD as a new Structure system in `index.html`
- Added the **"DfD · 14ft Cube Modules"** card (`sc-dfd`) + dispatch in
  `buildStructureSystem`; wired click handler; deep-link `?struct=dfd`.
- `buildStructureDfD` **voxelises the program massing** into stacked 14ft cubes
  (cube-centre-inside-massing occupancy) → frame + nodes + deck + partitions.
- Skips the program-based partition layer for DfD (it builds its own).

### D. Frame corrected to the REAL built-up members
- Initial version wrongly **merged** members into a single lattice. Re-measured the
  `.3dm`: each module carries its **own** 4 columns + 8 beams, **inset 11.9 cm**
  from the cube edge. Rewrote as **per-module (not deduped)** so abutting cubes
  stack into the true built-up members — **pairs along a shared edge, 2×2 clusters
  of four 8" columns (≈0.238 m centres)** at shared corners.

### E. Connection detail = the user's ACTUAL part
- Replaced the placeholder cube, then the parametric node, with the **real
  connector geometry extracted from the `.3dm`** (brep render meshes, 8 corner
  angle-bracket connectors, welded → 404 v / 816 t each).
- Saved as **`references/dfd_connector.json`** + **inlined** into `index.html`
  (`window.__DFD_CONNECTOR__`, `<script id="dfd-connector-data">`) so it works
  from `file://` with **no fetch** (the earlier black-box bug was the fetch
  failing on `file://` + a >6000-node fallback). Instanced per module via
  `InstancedMesh`. Helper `references/_inject_connector.py` regenerates it.

### F. Double-layer hollow deck
- Real cassette rebuilt: **18 cm bottom slab (top face flush with the very top of
  the column) + 30 cm pedestal void + 10 cm top access panel**. Datum =
  `colTop = y0 + M`.

### G. Interactive Section Box (structure mode)
- 6-plane **local clipping** box, **draggable handles** in the viewport + 6
  sliders + live wireframe box; handles/outline excluded from clipping; re-applies
  on rebuild; deep-links `?section=1&cut=`. Toggle + Reset in the structure panel.

### H. Real materials per construction element
- Mapped each element to its real material (confirmed with user):
  glulam frame `#b8884a`, steel connectors `#8b9096`, steel bolts `#34373d`,
  **CLT** bottom slab `#d8c391`, **steel** pedestals + access panel `#9aa0a6`,
  **gypsum** partitions `#e7e3da` (opaque). Card legend updated.

### I. Structural Foam paused in zoning
- `classifyZone` now remaps a winning `foam` → `internal` (FRAME); `ZONE_ORDER`
  drops foam; `zc-foam` card marked **PAUSED**. (Front-end/allocation pause only.)

### J. Program-lifecycle → DfD allocation in Hybrid
- New **`references/program-lifecycle.json`** (+ inline `PROGRAM_LIFECYCLE`):
  avg interior renew/turnover years for 83 program types; **threshold ≤ 10 yr ⇒
  DfD**. `dfdShortLife()` (exact key, then `_`→space, then conservative keyword
  fallback).
- Added a **`dfd` zone** (teal `#17b3c4`) to ZONE_COLORS/LABELS/ORDER + areaBySys.
  `classifyZone` returns `'dfd'` for short-life programs.
- Refactored `buildStructureDfD` → reusable **`dfdBuild(recs, G, mat)`** +
  **`dfdMaterials()`**; `buildStructureHybrid` collects short-life masses into
  `dfdRecs` and builds them with the DfD cube system (others stay Skin / Frame).
- **Residential ancillary amenities** (gym, spa, residents_lounge, changing_room,
  screening_room, 53W53 `lounge_bar`/`event_lounge`, mixed-use `amenity`) moved to
  **long-life (20 yr) → not DfD**; TPAC theatre lounges (space-named) stay short.

### K. Hybrid Structural Skin fixed (was incomplete)
- Hybrid built a **closed diagrid per program box** with per-box node counts →
  fragmented/incomplete. Replaced with **`skinFrameContinuous(skinRecs)`**: one
  ring per floor over the per-level union footprint, **consistent node count**, ±SKIP
  X-diagonals connecting consecutive rings + ring beams + top cap → one continuous
  diagrid envelope (mirrors the standalone `buildStructuralSkin`).

---

## 2. Files touched
- `index.html` — DfD system, connector inline, section box, materials, foam pause,
  lifecycle allocation, hybrid DfD + continuous skin, deep-link params
  (`struct`, `hide`, `section`/`cut`).
- **New:** `dfd-unit-diagram.html`, `references/dfd_connector.json`,
  `references/program-lifecycle.json`, `references/_inject_connector.py`.

## 3. Verification
- Every change syntax-checked (`node --check` on the module) and **visually
  verified** via headless Edge renders (frame clusters, real connector close-ups,
  double-layer deck section, section-box cut, real-material palette, zoning DfD
  teal allocation, residential amenities reverting to long-life, continuous skin
  on the 53W53 tower).

## 4. Open / possible next steps
- Add skin **slabs / node spheres** in hybrid to match the standalone visually.
- Mark **DfD↔other-system transition floors** in the zoning Transition panel.
- Optional: textures (wood/steel) for materials; tweak lifecycle threshold/values.
- Note: `references/dfd_connector.json` is now a required asset (also inlined).
