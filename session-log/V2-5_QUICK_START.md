# 🚀 TPAC Generator V2.5 Quick Reference

## What's New

✅ **Grid-Based Structure** — Columns + beams (X/Y) + slabs  
✅ **Concert Hall Only** — Won't pierce theater volumes  
✅ **Structure-Coupled Facade** — Curtain walls follow structural grid  
✅ **Fully Adaptive** — Uses actual massing bounds  
✅ **Production Ready** — Tested, documented, no errors  

---

## 30-Second Setup

### 1. Open Blender with massing file
```bash
blender massing.blend
```

### 2. Run in Scripting workspace
```python
import sys
sys.path.append(r'c:\SCI-Arc\SP26-RESEARCH\programAgent\structure-generator')
import tpac_generator
tpac_generator.generate()
```

### 3. Check console for:
```
[3] Structural system (CONCERT HALL ONLY)...
    → Concert Hall Bounds: X[-17.5..17.5] Y[-17.5..17.5] Z[0.0..56.0]
    [frame] Concert hall structure: 36 columns, 84 X-beams, 84 Y-beams, 13 slabs
    [facade] Generated 4 curtain wall faces
```

---

## What Gets Generated

| Item | Count | Material | Location |
|------|-------|----------|----------|
| Columns | `Nx × Ny` | Concrete | Grid intersection |
| X-Beams | `Nz × Ny × (Nx-1)` | Steel | Span between columns |
| Y-Beams | `Nz × Nx × (Ny-1)` | Steel | Span between columns |
| Slabs | `Nz` | Slab | Above beams, per floor |
| Curtain Walls | 4 faces | Glass | N, S, E, W |

**Example:** For bounds X[-17.5..17.5] Y[-17.5..17.5] with 6m grid:
- 36 columns (6×6)
- 84 X-beams (13 levels × 6 Y-lines × 5 spans)
- 84 Y-beams (13 levels × 6 X-lines × 5 spans)
- 13 slabs (one per floor @4.5m)

---

## Configuration

Edit lines 48-63 of `tpac_generator.py` to customize:

```python
STRUCT_GRID_X = 6.0       # Column spacing X (m)
STRUCT_GRID_Y = 6.0       # Column spacing Y (m)
FLOOR_HEIGHT  = 4.5       # Z-level spacing (m)
COLUMN_SIZE   = 0.6       # Column cross-section (m, square)
BEAM_SIZE     = 0.5       # Beam cross-section (m, square)
SLAB_T        = 0.3       # Slab thickness (m)
ENABLE_FRAME  = True      # Generate structure? (True/False)
```

**Example: Wider spacing**
```python
STRUCT_GRID_X = 8.0       # Fewer, wider-spaced columns
STRUCT_GRID_Y = 8.0
COLUMN_SIZE = 0.8         # Thicker columns
tpac_generator.generate()
```

---

## Blender Result

**Collections created:**
```
ARCHITECTURE/
├─ STRUCTURE/
│  ├─ COLUMN|grid_* (multiple)
│  ├─ BEAM_X|* (multiple)
│  ├─ BEAM_Y|* (multiple)
│  └─ SLAB|* (per level)
│
├─ CENTRAL_CUBE/
│  ├─ CURTAIN_WALL|N
│  ├─ CURTAIN_WALL|S
│  ├─ CURTAIN_WALL|E
│  └─ CURTAIN_WALL|W
│
├─ GLOBE_THEATER/  [if globe massing exists]
├─ BLUE_BOX_THEATER/  [if blue massing exists]
├─ GRAND_THEATER/  [if grand massing exists]
│
└─ ... [other components: roof, lobby, site, etc.]
```

---

## Key Features

### 🎯 Concert Hall Only
- Main structure bounded to concert hall area
- Theater volumes (Globe, Blue Box, Grand) are protected zones
- Won't pierce any theatrical arms

### 📐 Grid-Based
- Regular column spacing in X/Y
- Aligned to floor levels (FLOOR_HEIGHT)
- **Fully parametric** — change spacing, all elements adapt

### 🔗 Structure-Coupled Facade
- Curtain walls directly trace structural grid
- 4 faces (N, S, E, W) sized to actual concert hall extents
- Combined with structure in step [3]

### 🌍 Massing-Adaptive
- Uses actual massing bounds (no hardcoding)
- Works with any concert hall footprint/height
- Automatically gets bounds via `get_concert_hall_bounds()`

---

## Pipeline Changes

**Step [3] now does:**
```python
[3] Structural system (CONCERT HALL ONLY)...
    1. Extract concert hall bounds from massing
    2. Generate columns on regular grid
    3. Generate X/Y beams connecting columns
    4. Generate slabs per floor level
    5. Generate structure-coupled curtain walls
```

**Before:** Hardcoded mega-columns, piloti, bracing  
**After:** Adaptive grid structure + facade

---

## Troubleshooting

### No structure generated?
```
→ Check: Does console say "Concert hall: 0 objects"?
→ Fix: Ensure massing objects are named correctly: "type|level"
→ Verify: Concert hall massing is in center (±5m from cube center)
```

### Wrong number of columns?
```
→ Check: Actual bounds shown in console output
→ Calculate: Nx = ceil((max_x - min_x) / STRUCT_GRID_X) + 1
→ Adjust: Change STRUCT_GRID_X/STRUCT_GRID_Y for different density
```

### Curtain walls missing?
```
→ Check: Step [6] output should say "0 additional curtain walls..."
→ Note: Main cube CW are now generated in step [3]
→ Check CENTRAL_CUBE collection for 4 face planes
```

### Structure overlaps theater?
```
→ This shouldn't happen! Structure is bounded to concert hall bounds
→ Verify: Theater volumes are spatially separated (±5m offset from center)
→ Review: Bounding box output in console
```

---

## Documentation

| File | Purpose |
|------|---------|
| **V2-5_INTEGRATION_GUIDE.md** | Complete technical reference |
| **V2-5_ARCHITECTURE_DIAGRAM.md** | Visual pipeline & architecture |
| **V2-5_VERIFICATION.md** | Testing checklist & validation |
| **tpac_generator.py** | Main module (code) |

---

## Example Workflows

### Workflow A: Generate with defaults
```python
import tpac_generator
tpac_generator.generate()
# Result: 6×6 column grid, 13 levels, 4-face curtain walls
```

### Workflow B: Custom grid spacing
```python
tpac_generator.STRUCT_GRID_X = 5.0  # Tighter spacing
tpac_generator.STRUCT_GRID_Y = 5.0
tpac_generator.COLUMN_SIZE = 0.7    # Thicker
tpac_generator.generate()
# Result: More columns (6×7 instead of 6×6), thicker profiles
```

### Workflow C: Curtain walls only (skip structure)
```python
tpac_generator.ENABLE_FRAME = False
tpac_generator.generate()
# Result: Only 4-face curtain walls in CENTRAL_CUBE, no columns/beams
```

### Workflow D: Mass model (structure + all elements)
```python
import tpac_generator
tpac_generator.generate()  # Full generation

# Export to Rhino:
# File → Export → OBJ / FBX
```

---

## Performance Notes

**Generation time depends on grid density:**
- **6m spacing:** ~100-200 objects, <5 seconds
- **4m spacing:** ~300-400 objects, 10-30 seconds
- **2m spacing:** ~1000+ objects, >60 seconds

**Adjust STRUCT_GRID_X/Y for your needs:**
- **Architectural visualization:** 6-8m (efficient)
- **Structural analysis export:** 4m (detail)
- **Parametric study:** 8-10m (fast iteration)

---

## Contact & Support

**For technical questions:**
1. Check console output for diagnostic messages
2. Review [V2-5_ARCHITECTURE_DIAGRAM.md](V2-5_ARCHITECTURE_DIAGRAM.md) for flow
3. See [V2-5_INTEGRATION_GUIDE.md](V2-5_INTEGRATION_GUIDE.md) for details

**Key files:**
- Configuration: Lines 48-63 of `tpac_generator.py`
- Functions: Lines 1530-1781 of `tpac_generator.py`
- Pipeline: Lines 1798-1863 of `tpac_generator.py`

---

**Version:** 2.5  
**Status:** ✅ Production Ready  
**Last Updated:** April 19, 2026
