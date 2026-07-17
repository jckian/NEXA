---
name: Project — Tama Art University Library Diagram
description: Toyo Ito Tama Library 3D program diagram — 70x70 square site, perimeter-distributed cores, category-based color palette
type: project
---

Output file: `C:\SCI-Arc\SP26-RESEARCH\programAgent\tama-program-diagram.html`

**Why:** SP26 research project. Precedent case study for Toyo Ito's distributed-core, open-floor-plate tectonic — contrasts with TPAC (central cube logic) and 53W53 (central core cluster).

**How to apply:** Use this as the reference implementation whenever the diagram needs perimeter-anchored cores (no central core), category-based coloring, and a low-rise (2–3 floor) building.

## Building / Site
- Site: 70 m × 70 m square, centered at origin (cx=35, cz=35)
- 3 levels: B1 (level=-1, yBase=-4.0), L0 (level=0, yBase=0), L1 (level=1, yBase=4.0)
- Floor height default 4.0 m; slabH = FLOOR_H * (1 - SLAB_GAP), SLAB_GAP default 0.15

## Structural / Architectural principle (CRITICAL)
Tama has NO central core. All fire stairs sit at perimeter edges — this is architecturally significant and must be visible in the diagram:
- `fire stair and freight elevator` → SW corner
- `fire stair and elevator 1`       → NE corner
- `fire stair and elevator 2`       → SE corner
- `open stair` (L0, L1)            → NW interior (near main entry, not corner)
- `service corridor` (B1 only)     → south edge, east of center

Corner anchor zone: ~14% of site edge per stair box.

## Layout algorithm
1. Anchor perimeter fire stairs to corners via `PERIMETER_ANCHORS` lookup.
2. Place open stair NW interior; service corridor south edge (B1 only).
3. Strip-pack remaining entries into 3 E-W zone bands:
   - center strip: cz ± 14 m — public entries first (largest area)
   - north strip:  cz-hd to cz-14 — overflow / private
   - south strip:  cz+14 to cz+hd — overflow / private
4. Column-packing within each strip (left→right, top→bottom). Max aspect ratio 1:5.
5. Fallback: centre of site at reduced dims if all zones exhausted.

## Color palette
Category-based (not type-based like 53W53):
- `public`      → amber family  (#E8A838 base, sub-tones per type)
- `private`     → blue-grey family (#5B7FA6 base, sub-tones per type)
- `circulation` → charcoal family (#3D3D3D base, sub-tones per type)

`TYPE_TONES` map overrides `CAT_COLORS[category]` for individual types.
`getColor(type, category)` = TYPE_TONES[type] || CAT_COLORS[category] || fallback.

## Program data (3 floors)
- B1:  12 entries, gross ~1,650 m² — archive, compact stacks, mechanical, servers
- L0:  14 entries, gross ~2,030 m² — entry hall, galleries, lounges, cafe
- L1:  13 entries, gross ~2,070 m² — book stacks (700 m²), reading room, study zone

## UI Panels
- Building Info: open by default, includes structural note about perimeter cores
- Program Statistics: open by default, per-type area rows + floor breakdown + FAR
- Load Program: collapsed by default; drag-drop + file picker
- Parameters: collapsed by default; Site W/D, Floor Height, Slab Gap inputs + Apply + category legend

## Gradient theme
Amber-to-blue-grey: `linear-gradient(135deg, #c27a2a, #5B7FA6)` — different from 53W53 (blue-purple) and TPAC.
