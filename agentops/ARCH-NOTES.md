# ARCH-NOTES — Legacy Architecture Documentation

> **Status (2026-07-03):** This is the full pre-260703 CLAUDE.md, preserved verbatim below the line. It accurately documents the Python simulation (`pythonFiles/`) and the TPAC / 53W53 HTML visualizers, but those two visualizers have been retired from the repo root: they now live at `references/tpac-program-diagram.html` and `references/53w53-program-diagram.html` (an older copy of the TPAC one is in `BACKUP/`). Treat every file reference below as unverified until you confirm the file exists. Known error kept for fidelity: the "Blender Pipeline" section cites `pythonFiles/BlenderTPAC.py`, which does not exist — the actual Blender scripts are `massing-model-generator/tpac_blender.py` and `massing-model-generator/Blender53W53.py`. For current project state, see CLAUDE.md "Current focus" and the newest session-log.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

SCI-Arc Spring 2026 research project. An agent-based system that distributes architectural program spaces within a site boundary and outputs positions to Rhino for 3D visualization. Two case studies: OMA's Taipei Performing Arts Center (TPAC) and Jean Nouvel's 53W53.

---

## Running the Simulation

```bash
cd pythonFiles
python ProgramDeveloperEllipseBoundary.py
```

**Dependencies:** `openai`, `numpy`. No build step.

`pythonFiles/fileTransfer/` must exist before running — create it manually if absent. The script reads from and writes to it:

| File | Direction | Purpose |
|---|---|---|
| `fileTransfer/output.txt` | input | Program data in `{type}/{area}/{level}/{category}/{w,h}` format |
| `fileTransfer/border.txt` | input | Site boundary vertices, one `x,y` per line |
| `fileTransfer/cores.txt` | input | Core/stair anchor positions, one `x,y` per line |
| `fileTransfer/outAgent.txt` | output | Resolved agent positions → import into Rhino |

`modeSwitch = 0` calls the LLM program generator first and writes `output.txt`. `modeSwitch = 1` skips the LLM and runs simulation directly (expects `output.txt` already present).

---

## Program Data Format

All program data — used by both the Python simulation and the HTML visualizers — follows `references/ProgramFormat.txt`:

```
{program type}/{area in m2}/{floor level}/{program category}/{width,length}
```

- **Categories:** `public`, `private`, `circulation`
- **Floor levels:** `-1` (basement), `0` (ground), `1`–`N` (upper floors)
- **Curly braces are literal** in the `.txt` distribution files; the HTML parsers strip them

**Case study distributions:**
- `references/TPAC-PROGRAM-DISTRIBUTION.txt` — 14 floors, 28 types, ~58,250 m²
- `references/53W53-PROGRAM-DISTRIBUTION.txt` — 75 floors (B1–L73), 33 types, luxury residential tower

**Core generation rules** (from `references/ProgramFormat.txt`): minimum 3 fire-stair types per floor, minimum 4 recommended; freight elevator core ~150–250 m² near the service/loading side; passenger elevator cores ~120–180 m² distributed to meet ≥ ½-diagonal separation.

---

## Architecture

### Python Simulation (`pythonFiles/EllipseAgent.py`)

Each program space is an `Agent` — an ellipse with semi-axes from `w/2` and `h/2`. Per step, each agent accumulates four forces:

- **Avoidance** — separation vector from overlapping ellipses (64-point perimeter sampling via `ellipsesOverlap`)
- **Cohesion** — inverse-square attraction toward non-overlapping neighbors
- **Adjacency** — pull toward a preferred partner type (defined in `__init__`)
- **Boundary containment** — push back inside site polygon when any perimeter point exits

Core types (`fire stair and freight elevator`, `fire stair and elevator`) pin to `corePts` on construction and have `self.death = False`, which skips `update()`. Toilets are additionally pulled toward the toilet on the floor below (vertical plumbing stack). Simulation runs **5000 iterations per floor level**, sequential.

Adjacency rules use substring matching (`in`), not equality — LLM-generated type names may vary:
```
'toilets'    in type  → adjacent to  'fire stair and elevator'
'storage'    in type  → adjacent to  'fire stair and freight elevator'
'loading'    in type  → adjacent to  'fire stair and freight elevator'
'mechanical' in type  → adjacent to  'fire stair and elevator'
'fitting'    in type  → adjacent to  'display'
```

### Blender Pipeline (`pythonFiles/BlenderTPAC.py`)

Run from Blender → Scripting workspace → Run Script. Builds the TPAC massing as Blender mesh objects in a `TPAC` collection with per-floor sub-collections. Coordinate mapping: Three.js X→Blender X, Three.js Y (height)→Blender Z, Three.js Z (depth)→Blender Y. Maintains its own `TYPE_COLORS` dict with `_hex()` helper. Does not read any external file — program data is hardcoded in the script.

---

## HTML Visualizers

Both are **single-file, CDN-only Three.js (v0.163) apps** — open directly in a browser, no server needed.

### TPAC Visualizer (`tpac-program-diagram.html`)

Architecture specific to the TPAC building form:

- **Spatial zones per floor:** cube back-half (`private`/BOH), cube front-half (`public`), `zone:'grand'` (+X protrusion), `zone:'blue'` (-X protrusion), `zone:'globe'` (-Z protrusion)
- **`layoutStrips()`** — divides a floor zone's X width among entries proportional to area
- **Circulation shafts** — 4 continuous `BoxGeometry` columns at cube corners, full building height (not sliced per floor); color-coded freight/elevator 1-3
- **`buildScene(params)`** accepts `{ siteW, siteD, floorCount, floorHeight }` and does a full dispose + rebuild
- **`FLOOR_DATA`** (`let`) — parsed program entries, replaceable at runtime

Key constants:

| Constant | Default | Meaning |
|---|---|---|
| `CUBE_W / CUBE_D` | `siteW * 0.5` | Central cube footprint |
| `SLAB_H` | `floorHeight * 0.85` | Rendered slab height (15% gap) |
| `SHAFT_SIZE` | `2.4` | Circulation shaft cross-section (m) |
| `PILOTIS_H` | `6.0` | Building elevation off ground |
| `GLOBE_PROTRUDE_D` | `CUBE_D * 0.63` | Globe Playhouse northward protrusion |

### 53W53 Visualizer (`53w53-program-diagram.html`)

Architecture specific to the slender tapered tower form:

- **`PROGRAM_DATA`** (`let`) — parsed entries; replaced on file load
- **Mutable globals:** `SITE_W`, `SITE_D`, `SITE_CX`, `SITE_CZ`, `FLOOR_H`, `TAPER`, `TAPER_TOP`, `SHOW_DIAGRID` — all recalculated on Apply
- **`floorFootprint(level)`** — returns `{cx, cz, hw, hd}` for the tapered footprint at a given floor. Floors 0–3 (podium) use full site; above floor 4 the footprint scales linearly from 1.0 down to `TAPER` at `TAPER_TOP`
- **`CORE_TYPES`** — Set of the three fire-stair type keys. Core entries are placed in a horizontal cluster at the floor centroid; their bounding box defines the four surrounding program zones (W/E/N/S)
- **`layoutFloor(entries, level)`** — places core cluster first, then column-packs remaining entries into four zones sorted by area, largest first; max aspect ratio 1:5 enforced; fallback to floor centroid
- **`buildDiagridForFloor(level, yBase, slabH)`** — per-floor X-braced `LineSegments` at the tapered perimeter
- **`buildScene()`** recalculates `SITE_CX/CZ` at entry, disposes the full `sceneGroup`, rebuilds from scratch
- **`recentreCamera()`** — repositions `controls.target` and camera based on current site diagonal and tower height; call after `buildScene()` whenever dimensions change
- **`parseProgramText(raw)`** — strips `{}` from each `/`-delimited field, skips `##` comments and blank lines; handles both the `{type}/{area}` format and plain `type/area`

**Right-panel UI (3 collapsible panels):**
1. **Load Program** — file picker + drag-and-drop; accepts `.md`/`.txt`; on load updates title, `TAPER_TOP`, and `param-floor-count` from the data's max level, then calls `buildScene()` + `recentreCamera()`
2. **Program Statistics** — area by type, total GFA, FAR, tower height
3. **Parameters** — 2×3 grid: Site Width, Site Depth, Floor Count, Floor Height, Taper Factor, Diagrid toggle; Apply calls `buildScene()` + `recentreCamera()`

---

## References

| File | Content |
|---|---|
| `references/ProgramFormat.txt` | Format spec + core generation rules |
| `references/TPAC-PROGRAM-DISTRIBUTION.txt` | Complete TPAC floor-by-floor distribution |
| `references/53W53-PROGRAM-DISTRIBUTION.txt` | Complete 53W53 floor-by-floor distribution (B1–L73) |
| `references/260408-TPAC-PROGRAM` | Raw OMA TPAC program analysis (source material) |
| `references/53W53-PROGRAM` | Raw 53W53 architectural analysis (source material) |
| `references/RESTROOM-GUIDELINES.md` | Theater-scale restroom sizing: 1 female stall/50–70 seats, 1 male/100–150 seats; FOH cluster ~150–200 m²; must stack vertically and sit ≤15m from lobby |
