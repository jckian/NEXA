# TPAC Generator V2.5 -- Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  TPAC GENERATOR V2.5 ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────┘

INPUT (Blender Massing)
│
├─ Massing Objects: concert_hall|L*, blue_box|L*, grand|L*, globe|L*
├─ Shafts: SHAFT|fire_stair_*, SHAFT|elevator_*
│
└──────────────────────────────────────────────────────────────────────────
   │
   ▼
[1] MASSING ANALYSIS (tpac_generator.py: analyze_massing())
   ├─ Extract Z levels, X/Y footprints per level
   ├─ Identify shaft positions
   └─ Determine cube_xy, tower_xy extents

   │
   ▼
[1b] CONCERT HALL CLASSIFICATION (NEW!)
   │
   ├─────────────────────────────────────────────────────────────────┐
   │ identify_concert_hall_volume(info)                              │
   │                                                                  │
   │ Position-based separation:                                      │
   │  ✓ concert_hall_objs  → CENTER (dx,dy ≤ 5m from cube center)  │
   │  ✓ grand_objs         → EAST   (dx > 5)   [fly tower]          │
   │  ✓ blue_objs          → WEST   (dx < -5)  [cantilever]         │
   │  ✓ globe_objs         → SOUTH  (dy < -5)  [sphere]             │
   └─────────────────────────────────────────────────────────────────┘

   │
   ▼
[3] STRUCTURAL SYSTEM (V2.5 CORE) ✨
   │
   ├─────────────────────────────────────────────────────────────────┐
   │ get_concert_hall_bounds(concert_hall_objs)                      │
   │                                                                  │
   │ Input:  List of concert hall massing objects                    │
   │ Output: (cx0, cx1, cy0, cy1, cz0, cz1)  [world coords]         │
   │                                                                  │
   │ Algorithm:                                                       │
   │  └─ For each object:                                            │
   │     └─ For each vertex (in object.bound_box):                   │
   │        └─ Transform to world: world = matrix_world @ vertex    │
   │        └─ Update min/max x, y, z                                │
   │     Result: Tight bounding box of all concert hall objects     │
   └─────────────────────────────────────────────────────────────────┘

   │
   ├─────────────────────────────────────────────────────────────────┐
   │ build_concert_hall_structure(cx0, cx1, cy0, cy1, cz0, cz1)     │
   │                                                                  │
   │ Grid Generation:                                                │
   │  ├─ X positions: cx0, cx0+6.0, cx0+12.0, ... cx1               │
   │  ├─ Y positions: cy0, cy0+6.0, cy0+12.0, ... cy1               │
   │  └─ Z positions: cz0, cz0+4.5, cz0+9.0, ... cz1                │
   │
   │ Elements Generated:                                             │
   │  │                                                               │
   │  ├─── COLUMNS                                                    │
   │  │    └─ For each (x, y):                                      │
   │  │       ├─ Size: 0.6 × 0.6 m (square section)                │
   │  │       ├─ Height: cz1 - cz0 (full building)                 │
   │  │       ├─ Location: (x, y, cz0 + height/2)                  │
   │  │       └─ Material: concrete                                 │
   │  │       Count: Nx × Ny columns                                │
   │  │
   │  ├─── X-DIRECTION BEAMS                                         │
   │  │    └─ For each Z level, Y position:                        │
   │  │       ├─ Connects adjacent X columns                        │
   │  │       ├─ Size: (span) × 0.5 × 0.5 m                        │
   │  │       ├─ Material: steel                                    │
   │  │       └─ Count: Nz × Ny × (Nx-1) beams                     │
   │  │
   │  ├─── Y-DIRECTION BEAMS                                         │
   │  │    └─ For each Z level, X position:                        │
   │  │       ├─ Connects adjacent Y columns                        │
   │  │       ├─ Size: 0.5 × (span) × 0.5 m                        │
   │  │       ├─ Material: steel                                    │
   │  │       └─ Count: Nz × Nx × (Ny-1) beams                     │
   │  │
   │  └─── SLABS                                                     │
   │       └─ For each Z level:                                      │
   │          ├─ Size: (cx1-cx0) × (cy1-cy0) × 0.3 m                │
   │          ├─ Location: (cx_center, cy_center, z + 0.25)         │
   │          ├─ Material: slab                                      │
   │          └─ Count: Nz slabs                                     │
   │
   │ Safety Features:                                                │
   │  ├─ Slab positioned at z + BEAM_SIZE/2 → avoids beam piercing │
   │  ├─ All elements within concert hall bounds → no theater cross │
   │  └─ Grid-based → deterministic, reproducible structure         │
   └─────────────────────────────────────────────────────────────────┘

   ├─────────────────────────────────────────────────────────────────┐
   │ build_curtain_wall_with_structure(cx0, cx1, cy0, cy1, cz0, cz1)│
   │                                                                  │
   │ Four Facade Faces:                                              │
   │                                                                  │
   │  NORTH (Y = cy1):                                               │
   │  ┌──────────────────────────┐                                   │
   │  │  Size: (cx1-cx0) × (cz1-cz0)                                │
   │  │  Location: (cx_center, cy1, cz_center)                      │
   │  │  Material: glass_frit                                        │
   │  └──────────────────────────┘                                   │
   │  SOUTH (Y = cy0):     [Mirror of North]                         │
   │  EAST (X = cx1):      [Size: (cy1-cy0) × (cz1-cz0)]            │
   │  WEST (X = cx0):      [Mirror of East]                          │
   │                                                                  │
   │ Properties:                                                      │
   │  ├─ Directly traces structural grid → structure-coupled facade │
   │  ├─ Massing-adaptive → uses actual concert hall bounds         │
   │  └─ Won't pierce theaters → contained within concert hall      │
   └─────────────────────────────────────────────────────────────────┘

   │
   ▼
[4] SLABS (Pre-existing per-level slabs)
   │
   └─ build_slabs(info, config, SLAB)

   │
   ▼
[5] THEATER VOLUMES (Conditional)
   │
   ├─ Globe Playhouse   (if globe_objs exist)
   ├─ Blue Box Theater  (if blue_objs exist)
   └─ Grand Theater     (if grand_objs exist)

   │
   ▼
[6] ADDITIONAL CURTAIN WALLS (Tower, Lobby)
   │
   ├─ build_tower_curtain_walls()
   └─ build_lobby_curtain_walls()

   ... [7-11: Roof, Site, Cameras, Cleanup] ...

OUTPUT
│
├─ ARCHITECTURE collection:
│  ├─ STRUCTURE:
│  │  ├─ COLUMN|grid_*.*_*.* (36 objects)
│  │  ├─ BEAM_X|z*.* (84 objects)
│  │  ├─ BEAM_Y|z*.* (84 objects)
│  │  └─ SLAB|z*.* (15 objects)
│  │
│  ├─ CENTRAL_CUBE:
│  │  ├─ CURTAIN_WALL|N
│  │  ├─ CURTAIN_WALL|S
│  │  ├─ CURTAIN_WALL|E
│  │  └─ CURTAIN_WALL|W
│  │
│  ├─ GLOBE_THEATER, BLUE_BOX_THEATER, GRAND_THEATER
│  ├─ UPPER_TOWER, LOBBY_FACADE
│  └─ ROOF, SHAFT_CLADDING
│
├─ SITE collection
├─ MASSING_REFERENCE (hidden)
└─ SHAFTS_ORIGINAL (hidden)


┌─────────────────────────────────────────────────────────────────────────┐
│ KEY CONFIGURATION PARAMETERS                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ STRUCT_GRID_X    = 6.0 m   # Column X spacing                          │
│ STRUCT_GRID_Y    = 6.0 m   # Column Y spacing                          │
│ FLOOR_HEIGHT     = 4.5 m   # Z spacing between levels                  │
│ COLUMN_SIZE      = 0.6 m   # Column cross-section (0.6 × 0.6)          │
│ BEAM_SIZE        = 0.5 m   # Beam cross-section (0.5 × 0.5)            │
│ SLAB_T           = 0.3 m   # Slab thickness                            │
│ ENABLE_FRAME     = True    # Toggle structure generation               │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│ DESIGN PHILOSOPHY                                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ✓ ADAPTIVE:     All structure derived from massing bounds              │
│                 No hardcoded coordinates                                │
│                                                                         │
│ ✓ BOUNDED:      Structure limited to concert hall area                 │
│                 Won't pierce theater volumes (Blue, Globe, Grand)       │
│                                                                         │
│ ✓ GRID-BASED:   Regular column/beam spacing                            │
│                 Simple parametric modification                          │
│                                                                         │
│ ✓ RATIONAL:     Columns, beams, slabs align                            │
│                 Structural logic is clear and readable                  │
│                                                                         │
│ ✓ MATERIALIZED: Proper material assignments                            │
│                 Concrete columns, steel beams, glass facade             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Grid Layout Example

For concert hall bounds: X[-17.5..17.5] Y[-17.5..17.5] Z[0..56]
With STRUCT_GRID_X=6, STRUCT_GRID_Y=6, FLOOR_HEIGHT=4.5:

```
X positions: -17.5, -11.5, -5.5, 0.5, 6.5, 12.5
Y positions: -17.5, -11.5, -5.5, 0.5, 6.5, 12.5
Z positions: 0, 4.5, 9, 13.5, 18, 22.5, 27, 31.5, 36, 40.5, 45, 49.5, 54

Grid:        6 columns × 6 columns = 36 columns
X-beams:     13 levels × 6 Y-lines × 5 spans = 390 beams (theoretical)
             [Actually: Nz × Ny × (Nx-1)]
Y-beams:     13 levels × 6 X-lines × 5 spans = 390 beams (theoretical)
             [Actually: Nz × Nx × (Ny-1)]
Slabs:       13 levels = 13 slabs
```

**Console Output Example:**
```
[3] Structural system (CONCERT HALL ONLY)...
    → Concert Hall Bounds: X[-17.5..17.5] Y[-17.5..17.5] Z[0.0..56.0]
    [frame] Concert hall structure: 36 columns, 84 X-beams, 84 Y-beams, 13 slabs
    [facade] Generated 4 curtain wall faces
[4] Slabs...
```

---
**Version:** 2.5  
**Architecture Diagram Version:** 1.0  
**Date:** April 19, 2026
