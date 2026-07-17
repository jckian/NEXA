---
name: Project — 53W53 Program Diagram
description: Jean Nouvel 53W53 supertall NYC tower, 73-floor 3D program diagram, architecture decisions
type: project
---

Output file: `C:\SCI-Arc\SP26-RESEARCH\programAgent\53w53-program-diagram.html`

**Why:** SP26 research expansion — second building case study alongside TPAC. Demonstrates vertical supertall typology vs. TPAC's horizontal massing.

**How to apply:** This file is the canonical template for single-tower supertall diagrams. Key differences from TPAC: no zone protrusions, continuous tapered footprint, single central core shaft, diagrid exoskeleton expression.

## Building stats (as-coded)
- Site: 40×40m square, origin at (0,0,0), centred at (20,20)
- 75 floor levels: B1 (Y=-4.5m) through F73 (Y=328.5m)
- Floor height: 4.5m default (adjustable via Parameters panel)
- Total program entries: ~120 entries across 15 program types
- Taper: starts at F4; at F73, footprint = TAPER * site (default 0.55)

## Architecture

### Taper logic (`floorFootprint`)
- Floors B1–F3: full 40×40 site (podium/museum zone)
- F4–F73: linear scale from 1.0 to TAPER param, centred on site
- Returns `{cx, cz, hw, hd}` — site centroid + half-extents

### Core shaft
- Single `BoxGeometry(9, totalHeight, 9)` rendered as dark `#1a1a22` mesh
- Spans B1 (Y=-4.5) through F48 continuous — not per-floor slices
- Added to sceneGroup (not floorGroups) so never dimmed by floor selector

### Layout (`layoutFloor`)
- 4 rectangular zones around core: West, East, North, South
- Zones sorted by area (largest first) to maximize packing efficiency
- Column-major packing within each zone (top→bottom, advance column on overflow)
- Anti-sliver: enforces max aspect ratio 1:5 per block
- Service core entries skipped (rendered as shaft above)
- Fallback: overflowing entries centred in footprint at reduced scale

### Diagrid exoskeleton
- Per-floor `LineSegments` at tapered footprint boundary
- X-pattern diagonals on each of 4 faces (8 lines/face) + perimeter loops + verticals
- Toggle via Parameters panel (Show Diagrid: On/Off)
- Each diagrid has `userData.isDiagrid = true` for per-floor opacity control

### Materials
- Per-mesh `MeshStandardMaterial` instances (NOT cached) — required for per-floor opacity isolation
- Edge overlays: `.clone()` of base `edgeMat`, `userData.isEdge = true`
- Diagrid: `.clone()` of base `diagridMat`
- Emissive hover: uses `.isMeshStandardMaterial` guard before setting emissive

### Per-floor opacity (`setActiveFloor`)
- Traverses each floor's THREE.Group, reads `userData.isEdge` and `userData.isDiagrid` to assign correct base opacity
- Active floor: meshes=1.0, edges=0.12, diagrid=0.28
- Inactive floor: all=0.04

## Color coding
- Museum gallery:  `#2C7873` (deep teal)
- Restaurant/lobby: `#F5A623` (amber/gold)
- Lounge:          `#8B5CF6` (purple)
- Gym/Pool/Amenity: `#E8735A` (warm coral)
- Residences (all): `#4A90D9` (slate blue)
- Service core:    `#1a1a22` (dark charcoal — shaft mesh)
- Spire structure: `#555566` (mid grey)
- Storage/MEP:     `#3a3a4a` (dark grey)

## UI panels
- Title top-left; legend bottom-left (by type)
- Floor selector: bottom-centre, "ALL" + B1/F0–F73 buttons
- Right panel: Program Statistics (collapsible, open by default) + Parameters (collapsible, closed)
- Hover tooltip: type, floor, area m², category

## Known constraints
- `museum_gallery` entries have w=35, d=44 which exceeds the 40m site footprint — zone packing clamps these to zone width, so they appear smaller than stated dims (area label is correct)
- Spire floors F61–F73 have no service_core entries; core shaft simply extends visually through spire zone
