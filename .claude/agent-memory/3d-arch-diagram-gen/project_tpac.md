---
name: Project — TPAC Program Diagram
description: Taipei Performing Arts Center (OMA) 3D program diagram, conventions and geometry decisions
type: project
---

Output file: C:\SCI-Arc\SP26-RESEARCH\programAgent\tpac-program-diagram.html

**Why:** SP26 research project. Evolved from simple massing volumes (v1) to floor-by-floor program distribution (v2, 2026-04-08).

**How to apply:** Re-use the HTML/Three.js scaffold (importmap CDN, OrbitControls, HTML labels via projection, legend from TYPE_COLORS map, floor selector) as the standard template for subsequent buildings.

## Current state (v2 — floor-by-floor)
- 14 floor levels: B1 (Y=-4.5) through L12 (Y=44.5); floor step = 3.5m, slab height = 3.0m (0.5m gap for legibility)
- FLOOR_DATA array drives all geometry; format: { type, area, level, category, w, d, zone? }
- Per-floor slabs placed as X-axis strips within spatial zones:
  - Central cube (35×35m): back half (Z: 0 to +17.5) = private/BOH; front half (Z: -17.5 to 0) = public; mechanical inset right corner (X: +8.5 to +17.5)
  - Grand Theater zone (+X protrusion from X=+17.5): performance hall slabs L4–L6, fly tower L7–L9
  - Blue Box zone (-X protrusion from X=-17.5): performance hall slabs L3–L6
  - Globe Playhouse: single SphereGeometry R=11 at Z≈-28.5, Y=22.75; registered to levels 4/5/6
- Circulation cores: 4 BoxGeometry shafts (2.4×full_height×2.4) at cube corners — NOT per-floor slabs
- Central cube ghost: wireframe BoxGeometry opacity=0.12 spanning full B1–L12 height (52.5m)
- Material caching: getSlabMat(hexStr, opacity) and getEdgeMat(hexStr) use _matCache dict keyed by hex+opacity

## Floor selector
- floorMeshes dict keyed by level string ('-1'..'12') holds arrays of { mesh, lines, baseOpacity }
- Globe sphere registered to levels 4/5/6; shaft objects tracked separately
- applyFloorFocus(key | null) sets opacity per floor; dim opacity = 0.06 for non-active floors
- DOM buttons row at bottom (floor-selector div); ALL button resets to full visibility

## Labels
- volume-label (transform: translate(-50%,-50%)): Central Cube, Grand Theater, Blue Box, Globe Playhouse, Public Plaza
- floor-label (transform: translate(-100%,-50%)): B1..L12 ticks at left edge of cube

## Legend
- Grouped by PUBLIC / PRIVATE-BOH / CIRCULATION
- Scrollable: max-height 70vh, overflow-y auto
- Built from LEGEND_GROUPS dict and TYPE_COLORS map

## Color palette — TYPE_COLORS map (hex strings)
See full map in the HTML file. Key entries:
- performance hall: #e8543a  |  stage: #c0392b  |  fly tower: #884400
- backstage: #7a6e5f  |  staff office: #7986cb  |  mechanical: #263238
- lobby: #f0c040  |  public circulation loop: #a5d6a7  |  viewing platform: #4dd0e1
- Circulation shafts: freight=#ff7043, E1=#ffcc02, E2=#66bb6a, E3=#42a5f5

## Three.js version
three@0.163.0 via cdn.jsdelivr.net importmap.

## Geometry conventions retained from v1
- Site origin at XZ centre, Y=0 ground plane.
- Pilotis expressed as CylinderGeometry columns (0–6m).
- Each solid volume: MeshPhysicalMaterial + EdgesGeometry LineSegments overlay.
- HTML div labels projected via Vector3.project(camera), hidden when z > 1.
