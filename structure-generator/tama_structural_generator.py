"""
============================================================================
  TAMA STRUCTURAL FOAM GENERATOR  —  Blender Python
============================================================================
  Based on TAMA-GRID.py arch/vault shell logic.
  Applies the single-layer TAMA arch structure to ANY massing object,
  auto-calculates grid cells and floor count from the massing bounding box,
  and stacks layers vertically.

  HOW TO USE:
    1. Open Blender, import or create your massing mesh.
    2. Select the massing object (or set MASSING_OBJECT_NAME below).
    3. Adjust parameters to taste.
    4. Run from Blender's Text Editor (Alt+P).

  APPLYING TO DIFFERENT MASSINGS:
    - Set MASSING_OBJECT_NAME to any mesh object in the scene.
    - Or leave "" and select the target object before running.
    - Grid dimensions and floor count auto-derive from the bounding box.
    - Use overrides (GRID_X_OVERRIDE etc.) to lock specific values.
============================================================================
"""

import bpy
import bmesh
import math
from mathutils import Vector


# ============================================================================
#  PARAMETERS
# ============================================================================

# --- Target Massing ----------------------------------------------------------
MASSING_OBJECT_NAME  = ""      # Leave "" to use the currently selected object.
                               # Or set to object name, e.g. "STRUCTURAL_FOAM"

# --- Grid / Cell -------------------------------------------------------------
CELL         = 3.0             # Cell size in metres (arch span)
FLOOR_HEIGHT = 4.0             # Height per floor = arch peak height

# --- Curve Quality -----------------------------------------------------------
SEG          = 20              # Segments per arch curve (higher = smoother)
THICKNESS    = 0.15            # Shell thickness in metres (15 cm concrete)

# --- Overrides (None = auto-derive from massing bbox) ------------------------
GRID_X_OVERRIDE       = None   # Force specific X cell count
GRID_Y_OVERRIDE       = None   # Force specific Y cell count
FLOOR_COUNT_OVERRIDE  = None   # Force specific floor count

# --- Output ------------------------------------------------------------------
COLLECTION_NAME  = "TAMA_STRUCTURE"
CLEANUP_PREVIOUS = True        # Remove previous generation before re-running


# ============================================================================
#  HELPERS
# ============================================================================

def get_massing():
    """Resolve massing mesh from name or active selection."""
    if MASSING_OBJECT_NAME:
        obj = bpy.data.objects.get(MASSING_OBJECT_NAME)
        if not obj:
            available = [o.name for o in bpy.data.objects if o.type == 'MESH']
            raise ValueError(
                f"Object '{MASSING_OBJECT_NAME}' not found.\n"
                f"Available meshes: {available}"
            )
    else:
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError(
                "No mesh selected. Select your massing object first, "
                "or set MASSING_OBJECT_NAME at the top of this script."
            )
    return obj


def get_bbox_world(obj):
    """
    Return bounding box in world space as (xmin, xmax, ymin, ymax, zmin, zmax).
    Uses matrix_world so it works regardless of object transform.
    """
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs = [v.x for v in corners]
    ys = [v.y for v in corners]
    zs = [v.z for v in corners]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def setup_collection():
    """Create (or clean and recreate) the output collection."""
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col and CLEANUP_PREVIOUS:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
    col = bpy.data.collections.new(COLLECTION_NAME)
    bpy.context.scene.collection.children.link(col)
    return col


# ============================================================================
#  SINGLE-LAYER TAMA ARCH BUILDER
# ============================================================================

def build_tama_layer(bm, grid_x, grid_y, origin_x, origin_y, z_base):
    """
    Add one floor's worth of TAMA arch+slab geometry into an existing bmesh.

    Parameters
    ----------
    bm        : bmesh.BMesh  — target bmesh to accumulate geometry into
    grid_x    : int          — number of cells in X
    grid_y    : int          — number of cells in Y
    origin_x  : float        — world X offset (massing bbox xmin)
    origin_y  : float        — world Y offset (massing bbox ymin)
    z_base    : float        — world Z of this floor's base
    """

    def gpt(i, j, dz=0.0):
        return Vector((origin_x + i * CELL, origin_y + j * CELL, z_base + dz))

    def ridge_curve(p1, p2):
        """Arch curve from p1 to p2, rising to FLOOR_HEIGHT at the midpoint."""
        direction = p2 - p1
        length    = direction.length
        x_dir     = direction.normalized()
        z_dir     = Vector((0, 0, 1))
        center    = (p1 + p2) / 2
        pts = []
        for s in range(SEG + 1):
            t     = s / SEG
            angle = math.pi * t
            x     = (t - 0.5) * length
            z     = math.sin(angle) * FLOOR_HEIGHT
            pts.append(center + x_dir * x + z_dir * z)
        return pts

    def loft_arch_to_slab(curve_pts, top1, top2):
        """
        Create quad faces between the arch curve and the flat slab line
        connecting top1 → top2.
        """
        slab_pts = [top1.lerp(top2, i / SEG) for i in range(SEG + 1)]
        for i in range(SEG):
            c1 = bm.verts.new(curve_pts[i])
            c2 = bm.verts.new(curve_pts[i + 1])
            s1 = bm.verts.new(slab_pts[i])
            s2 = bm.verts.new(slab_pts[i + 1])
            try:
                bm.faces.new((c1, c2, s2, s1))
            except Exception:
                pass

    # ---- Arch faces (4 sides per cell) ----
    for i in range(grid_x):
        for j in range(grid_y):
            p00 = gpt(i,     j)
            p10 = gpt(i + 1, j)
            p01 = gpt(i,     j + 1)
            p11 = gpt(i + 1, j + 1)
            t00 = gpt(i,     j,     FLOOR_HEIGHT)
            t10 = gpt(i + 1, j,     FLOOR_HEIGHT)
            t01 = gpt(i,     j + 1, FLOOR_HEIGHT)
            t11 = gpt(i + 1, j + 1, FLOOR_HEIGHT)

            loft_arch_to_slab(ridge_curve(p00, p10), t00, t10)   # front
            loft_arch_to_slab(ridge_curve(p10, p11), t10, t11)   # right
            loft_arch_to_slab(ridge_curve(p11, p01), t11, t01)   # back
            loft_arch_to_slab(ridge_curve(p01, p00), t01, t00)   # left

    # ---- Slab (flat top of each cell) ----
    for i in range(grid_x):
        for j in range(grid_y):
            v1 = bm.verts.new(gpt(i,     j,     FLOOR_HEIGHT))
            v2 = bm.verts.new(gpt(i + 1, j,     FLOOR_HEIGHT))
            v3 = bm.verts.new(gpt(i + 1, j + 1, FLOOR_HEIGHT))
            v4 = bm.verts.new(gpt(i,     j + 1, FLOOR_HEIGHT))
            try:
                bm.faces.new((v1, v2, v3, v4))
            except Exception:
                pass


# ============================================================================
#  MAIN
# ============================================================================

def generate():
    print("\n" + "=" * 64)
    print("  TAMA STRUCTURAL FOAM GENERATOR")
    print("=" * 64)

    # ---- Massing ----
    massing = get_massing()
    xmin, xmax, ymin, ymax, zmin, zmax = get_bbox_world(massing)

    width  = xmax - xmin
    depth  = ymax - ymin
    height = zmax - zmin

    print(f"  Massing : {massing.name}")
    print(f"  BBox    : W={width:.2f}  D={depth:.2f}  H={height:.2f}")
    print(f"  Origin  : ({xmin:.2f}, {ymin:.2f}, {zmin:.2f})")

    # ---- Derive grid & floor count ----
    grid_x  = GRID_X_OVERRIDE      if GRID_X_OVERRIDE      else max(1, int(width  / CELL))
    grid_y  = GRID_Y_OVERRIDE      if GRID_Y_OVERRIDE       else max(1, int(depth  / CELL))
    floors  = FLOOR_COUNT_OVERRIDE if FLOOR_COUNT_OVERRIDE  else max(1, int(round(height / FLOOR_HEIGHT)))

    footprint_x = grid_x * CELL
    footprint_y = grid_y * CELL
    total_h     = floors * FLOOR_HEIGHT

    print(f"\n  Grid    : {grid_x} × {grid_y} cells  ({footprint_x:.1f} m × {footprint_y:.1f} m)")
    print(f"  Floors  : {floors}  ×  {FLOOR_HEIGHT} m  =  {total_h:.1f} m total")
    print(f"  Cell    : {CELL} m,  Thickness: {THICKNESS * 100:.0f} cm")

    # ---- Build all layers into one bmesh ----
    print("\n  Generating layers …")
    bm = bmesh.new()

    for floor in range(floors):
        z_base = zmin + floor * FLOOR_HEIGHT
        build_tama_layer(bm, grid_x, grid_y, xmin, ymin, z_base)
        print(f"    Floor {floor:3d}  Z_base = {z_base:.2f}")

    # ---- Mesh output ----
    col  = setup_collection()
    mesh = bpy.data.meshes.new("TAMA_STRUCTURE")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("TAMA_STRUCTURE", mesh)
    col.objects.link(obj)

    # ---- Solidify ----
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)

    mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    mod.thickness      = THICKNESS
    mod.offset         = 0
    mod.use_even_offset = True
    bpy.ops.object.modifier_apply(modifier=mod.name)

    bpy.ops.object.shade_smooth()

    # ---- Summary ----
    print("\n" + "-" * 64)
    print(f"  COMPLETE  ✓")
    print(f"    Massing          : {massing.name}")
    print(f"    Grid per floor   : {grid_x} × {grid_y} = {grid_x * grid_y} cells")
    print(f"    Floors           : {floors}")
    print(f"    Total cells      : {grid_x * grid_y * floors}")
    print(f"    Collection       : '{COLLECTION_NAME}'")
    print("=" * 64 + "\n")

    return obj


generate()
