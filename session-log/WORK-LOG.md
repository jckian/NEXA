# TPAC Program Agent — Work Log

**Project:** SCI-Arc SP26 Research — programAgent
**Date:** 2026-04-08
**Reference:** OMA Taipei Performing Arts Center

---

## 1. Initialization / Init

Created `CLAUDE.md` to record project context:

- SCI-Arc Spring 2026 research project
- Goal: generate parametric architectural program diagrams for a Blender MCP pipeline
- Case study: OMA Taipei Performing Arts Center (TPAC)
  - centralized BOH (back-of-house) core
  - plug-in theater ecology
  - public circulation as an architectural generator

---

## 2. Build Floor-by-Floor Program Distribution

**Input files:**
- `references/260408-TPAC-PROGRAM` — OMA TPAC program analysis
- `references/ProgramFormat.txt` — program format specification

**Format:**
```
{program type}/{area in m2}/{floor level}/{program category}/{width, length}
```

**Output file:** `references/TPAC-PROGRAM-DISTRIBUTION.txt`

### Floor Overview

| Floor | Elevation | Major Programs |
|---|---:|---|
| B1 | -4.5 m | Loading, set storage, mechanical |
| L0 | 0 m | Public plaza, box office, lobby |
| L1 | +6 m | Loading, workshops, set production |
| L2 | +9.5 m | Back-of-house, dressing rooms, rehearsal rooms |
| L3 | +13 m | Stage level, orchestra pit |
| L4 | +16.5 m | Auditorium lower tiers (three halls) |
| L5 | +20 m | Auditorium middle tiers |
| L6 | +23.5 m | Auditorium upper tiers, viewing platform |
| L7 | +27 m | Fly tower base level, technical corridors |
| L8 | +30.5 m | Fly tower mid level |
| L9 | +34 m | Fly tower upper level |
| L10 | +37.5 m | Offices (administration) |
| L11 | +41 m | Offices (upper) |
| L12 | +44.5 m | Roof terrace, restaurant |

### Program Types (28 types)

**PUBLIC**
- performance hall, stage, orchestra pit
- lobby, box office, bar, hospitality lounge
- restaurant, roof terrace, viewing platform
- public circulation loop, toilets, plaza

**PRIVATE / BOH**
- fly tower, backstage, rehearsal room, dressing room
- green room, loading dock, production workshop
- set storage, storage, mechanical, staff office

**CIRCULATION**
- fire stair and freight elevator
- fire stair and elevator 1 / 2 / 3

**Total Floor Area:** ~58,250 m² (reference ~58,600 m²)

### Vertical Core Rules
- Minimum of 3 fire escape cores; 4 recommended
- Core 1 (freight elevator): ~150–250 m², located toward loading side
- Cores 2–4 (public elevators): ~120–180 m², distributed evenly
- Must meet spacing requirements of at least half the floor diagonal

---

## 3. 3D Program Diagram Application

**Output file:** `tpac-program-diagram.html`
**Stack:** Three.js v0.163 (CDN importmap), plain HTML/JS/CSS, single-file no server

### Version 1 — Base Massing
Created the following geometry primitives:

| Massing | Geometry | Notes |
|---|---|---|
| Site plaza | PlaneGeometry 70×70 | Y=0, with grid |
| Pilotis columns | CylinderGeometry ×8 | from 0–6 m |
| Central cube | BoxGeometry 35×35×63 | semi-transparent wireframe |
| BOH lower levels | BoxGeometry | lower core levels |
| Grand Theater | BoxGeometry | eastward protrusion (+X) |
| Blue Box | BoxGeometry | westward protrusion (-X) |
| Globe Playhouse | SphereGeometry r=11 | northward cantilever (-Z) |
| Public circulation ring | 4× BoxGeometry | mid-level ring around core |

### Version 2 — Floor-by-Floor Program Distribution
Scene rebuilt from all 118 entries in `TPAC-PROGRAM-DISTRIBUTION.txt`.

**Zoning logic:**
- Central cube back half (Z: 0 → +17.5): private / BOH programs
- Central cube front half (Z: -17.5 → 0): public programs
- Mechanical located in back-right corner
- Grand Theater (+X protrusion): performance hall, stage, fly tower
- Blue Box (-X protrusion): performance hall
- Globe Playhouse (-Z protrusion): sphere zone, L4–L6

**4 circulation shafts** span full height (B1 → L12), placed in corners and color-coded:
- Freight/core: orange `#ff7043`
- Elevator 1: yellow `#ffcc02`
- Elevator 2: green `#66bb6a`
- Elevator 3: blue `#42a5f5`

**UI features:**
- Floor selector (button row at bottom): selecting a floor mutes other floors to opacity 0.06
- Scrollable legend (left panel), grouped by PUBLIC / PRIVATE-BOH / CIRCULATION
- Floor labels (B1…L12) projected to the left edge of the core
- Major volume labels: Central Cube, Grand Theater, Blue Box, Globe Playhouse

### Version 3 — All-box masses + interactive parameter panels
(work in progress / agent-driven)

**Changes in progress:**

1. Globe Playhouse replaced with box massing
   - Remove `SphereGeometry`
   - `zone:'globe'` entries now represented as northward-protruding BoxGeometry slabs
   - New constants: `GLOBE_PROTRUDE_D = 22`, `GLOBE_W = 22`

2. Site parameter panel (top-right)

   | Parameter | Default |
   |---|---:|
   | Site Width | 70 m |
   | Site Depth | 70 m |
   | Floor Count | 14 |
   | Floor Height | 3.5 m |

   - `Apply` recalculates derived constants and rebuilds scene
   - scene rebuild function: `buildScene(params)`
   - scene clear function: `disposeAndClear()` (preserve lights and camera)

3. Program loader (top-right)
   - `<textarea>` for pasting program data
   - `Load` button parses and replaces `FLOOR_DATA`
   - parse format: `{type}/{area}/{level}/{category}/{w,d}`
   - automatically updates legend and scene

---

## 4. File Structure

```
programAgent/
├── CLAUDE.md                          # Project guidance for Claude Code
├── WORK-LOG.md                        # This file
├── tpac-program-diagram.html          # 3D program diagram application (main)
└── references/
    ├── 260408-TPAC-PROGRAM            # Raw OMA TPAC program analysis
    ├── ProgramFormat.txt              # Program format specification
    └── TPAC-PROGRAM-DISTRIBUTION.txt  # Floor-by-floor distribution (28 types / 14 floors)
```

---

## 5. Key Design Decisions

| Decision | Rationale |
|---|---|
| 1 Three.js unit = 1 metre | Keep units intuitive — no conversion needed |
| Semi-transparent central cube wireframe (opacity 0.12) | Reveal internal BOH masses while keeping sectional logic visible |
| Material cache `_matCache` | Avoid recreating identical MeshPhysicalMaterial instances |
| Floor slabs partitioned into X-direction strips (area-driven) | Geometry driven by area rather than hardcoded positions |
| Vertical cores represented as continuous shafts | Emphasize structural continuity instead of per-floor slices |
| `EdgesGeometry` layered on top of all solids | Clear outlines and reduced aliasing on edges |
| HTML div labels projected (instead of Sprites) | No texture resolution limits; updates with view angle |
