# TPAC Generator v2 Integration Summary

## Objective
Transfer Internal Structure + Curtain Wall generation rules from `tpac_architecture_generator.py` to `tpac_generator.py` with massing-adaptive shapes and concert-hall-only main structure generation.

## Changes Made

### 1. **Concert Hall Volume Classification** (`identify_concert_hall_volume()`)
- **Location:** New function at line ~500
- **Purpose:** Classify massing objects into functional areas based on spatial position
- **Algorithm:**
  - Calculates cube center from `info["cube_xy"]`
  - Iterates through all massing objects in the levels
  - Classifies by relative distance from cube center:
    - **Grand Theater:** `dx > 5` (East/+X side)
    - **Blue Box:** `dx < -5` (West/−X side)
    - **Globe:** `dy < -5` (South/−Z side)  
    - **Concert Hall:** Central core (default)
- **Output:** Dictionary with classified object lists and footprint info

### 2. **Massing-Adaptive Curtain Wall Generation** (`build_adaptive_curtain_walls_from_massing()`)
- **Location:** New function at line ~1050
- **Purpose:** Generate curtain walls based on actual concert hall massing boundaries
- **Features:**
  - Extracts overall footprint from concert hall massing objects
  - Derives curtain wall extents directly from massing footprint (`cx0, cx1, cy0, cy1, cz0, cz1`)
  - Generates 4-face curtain walls (N, S, W, E) using massing-derived bounds
  - Adapts grid spacing and mullion patterns from config
  - Print diagnostics with actual footprint extents
- **Integration:** Called in `generate()` step [6] instead of hardcoded walls

### 3. **Concert-Hall-Only Structural System** (Modified `generate()`)
- **Location:** Updated main function at line ~1530
- **Changes:**
  - Added step [1b] to call `identify_concert_hall_volume()` after massing analysis
  - Modified step [3] (Structural system) to only run if `concert_hall["concert_hall_objs"]` is non-empty
  - Added conditional guards for all theater volume generation in step [5]
  - Each theater (Globe, Blue Box, Grand) now generates only if corresponding massing exists
  - Fallback curtain walls for tower/lobby are retained, but adaptive walls used for main cube
- **Logging:** Enhanced diagnostics show:
  - Count of objects per functional area
  - Warnings if expected areas have no massing
  - Confirmation of theater generation with massing counts

### 4. **Structure Organization**
```
[1] Massing Analysis
[1b] CONCERT HALL CLASSIFICATION ← NEW
[2] Collections & Materials
[3] Structural System (CONCERT HALL ONLY) ← CONDITIONAL
[4] Slabs
[5] Theater Volumes (from classification) ← CONDITIONAL
[6] Curtain Walls (MASSING-ADAPTIVE) ← MODIFIED
[7] Roof
[8] Globe cuts
[9] Site
[10] Cameras & Lighting
[11] Cleanup
```

## Key Design Decisions

### Why Spatial Classification by Position?
- **Spatial offset:** ±5m threshold uses relative position from cube center
- **Rationale:** Geometric separation in TPAC design naturally clusters:
  - Concert hall core stays within ±5m of center
  - Fly tower (Grand) extends into +X half-space
  - Blue Box occupies −X half-space
  - Globe/Playhouse sits in −Z half-space
- **Robustness:** Works regardless of actual massing volume sizes

### Why Massing-Derived Curtain Wall Bounds?
- **Problem:** Hardcoded coordinates don't adapt to user-modified massing
- **Solution:** Extract footprint from actual massing geometry:
  - Get all massing object bounding boxes
  - Compute outer bounds (min/max X, Y, Z)
  - Use these bounds directly in curtain wall generation
  - Grid spacing and mullions still configurable in `DEFAULT_CONFIG`
- **Trade-offs:**
  - Requires massing objects to be present and valid
  - Falls back gracefully if no concert hall massing exists
  - Maintains architectural coherence while adapting to user input

### Why Concert-Hall-Only Main Structure?
- **Architectural Logic:** TPAC design separates:
  - **Concert Hall Core:** Primary load path (mega-columns, mega-trusses, piloti)
  - **Theatrical Arms:** Cantilevered or independent (supported on cube or separate shafts)
- **Benefits:**
  - Cleaner structural logic tied to function
  - Theater volumes can be modified independently
  - Main structure remains stable if theater massing changes

## Usage

### In Blender (Scripting workspace)
```python
import tpac_generator
tpac_generator.generate()  # Run with defaults

# Or with overrides:
custom_config = {
    "site_size": 75,
    "piloti_count_per_side": 4,
    "globe_radius": 18.0,
}
tpac_generator.generate(custom_config)
```

### Program Data Requirements
- Massing named in format `{program type}|{level}`
- Must be MESH objects with valid bounds
- Shafts named `SHAFT|...` and containing "fire stair" or "elevator"
- For best results:
  - Concert hall core vs theater arms should be in distinct object regions
  - Z-up coordinate system, meters
  - Origin at site center

## Testing Checklist
- [ ] Verify `identify_concert_hall_volume()` correctly classifies all massing objects
- [ ] Check that structure only generates in central core area
- [ ] Confirm adaptive curtain walls span from actual massing footprint
- [ ] Validate theater volumes only generate if corresponding massing exists
- [ ] Test with modified massing (e.g., expand blue box, add fly tower)
- [ ] Ensure no objects extend beyond site boundary (except Globe)
- [ ] Check collections are properly organized (ARCHITECTURE/STRUCTURE/etc.)
- [ ] Verify material assignments (concrete, steel, glass, etc.)

## Files Modified
- **[tpac_generator.py](tpac_generator.py)** (Primary)
  - Added `identify_concert_hall_volume()` function
  - Added `build_adaptive_curtain_walls_from_massing()` function
  - Updated `generate()` to use functional volume classification
  - Enhanced logging and diagnostics

## Related Files (Reference)
- **[tpac_architecture_generator.py](../tpac_architecture_generator.py)** — Original hardcoded curtain wall rules (preserved for reference)
- **references/TPAC-PROGRAM-DISTRIBUTION.txt** — Program data format and volumes
- **references/ProgramFormat.txt** — Core generation rules and constraints

## Future Enhancements
1. **Per-Volume Config Overrides:** Allow different configs for concert hall, grand, blue, globe
2. **Geometric Constraint Validation:** Warn if theater volumes intersect or exceed bounds
3. **Program-Driven Structure:** Infer mega-column positions from program adjacency (not just from shafts)
4. **Export to CAD:** Direct Rhino integration to export geometry and program areas
5. **Parametric Design:** Interactive UI sliders to adjust structural sys independently from massing

---
Generated: April 2026 | TPAC Parametric Generator v2
