"""
============================================================================
  PARAMETRIC DIAGRID STRUCTURAL SKIN GENERATOR  —  Blender Python
============================================================================
  Adapted from 53W53 (MoMA Tower / Jean Nouvel) structural diagrid analysis.
  
  This script generates a diagrid structural skin that automatically conforms
  to ANY closed massing geometry — tapered towers, twisted forms, freeform
  shapes, irregular footprints, etc.

  HOW TO USE:
    1. Open Blender, create or import your massing mesh (must be a closed
       watertight solid so raycasting works).
    2. Select the massing object.
    3. Adjust the PARAMETERS section below to taste.
    4. Run this script from Blender's Text Editor (Alt+P) or paste into
       Blender's Python console.

  HOW IT WORKS:
    - Slices the massing horizontally at each floor level
    - Uses adaptive-centroid raycasting to extract the perimeter outline
      at every height, regardless of how the shape shifts or tapers
    - Resamples each outline into N evenly-spaced nodes
    - Connects nodes between adjacent floors in a diagrid pattern
      (alternating diagonals)
    - Adds horizontal ring beams at each floor for lateral bracing
    - Optionally generates glass infill panels

  TESTED ON:
    - 53W53 envelope (asymmetric taper, shifting centroid)
    - Tapered cylinder
    - Twisted square tower (90° rotation over height)
============================================================================
"""

import bpy
import mathutils
from mathutils import Vector
import math


# ============================================================================
#  PARAMETERS  —  Adjust these to control the structural skin
# ============================================================================

# --- Massing Input -----------------------------------------------------------
MASSING_OBJECT_NAME = ""    # Name of your massing object.
                            # Leave "" to use the currently selected object.

# --- Floor / Level Settings --------------------------------------------------
FLOOR_HEIGHT       = 9.0    # Vertical spacing between diagrid node levels.
                            # Larger = fewer floors, bigger diamonds.
                            # 53W53 uses ~9 m floor-to-floor.
Z_START            = None   # Override start Z. None = auto (massing bottom).
Z_END              = None   # Override end Z.   None = auto (massing top).
SKIP_BOTTOM_FLOORS = 0      # Skip N floors from the bottom (e.g. podium zone).
SKIP_TOP_FLOORS    = 0      # Skip N floors from the top   (e.g. open crown).

# --- Diagrid Pattern ---------------------------------------------------------
PERIMETER_DIVISIONS = 24    # Number of nodes around the perimeter per floor.
                            # More = denser grid. 53W53 has ~24-26 nodes.
                            # For smaller massing try 12-16; for large try 32+.
DIAGRID_SKIP        = 1     # Each node connects to neighbour ± this offset on
                            # the floor above/below.
                            #   1 = standard tight diagrid (53W53-like)
                            #   2 = wider diamond pattern
ALTERNATING         = True  # Flip diagrid direction every other floor.
                            # True = classic X-pattern; False = all same slant.

# --- Beam Cross-Section ------------------------------------------------------
PRIMARY_WIDTH   = 1.0       # Width of primary (diagonal) beams.
PRIMARY_DEPTH   = 1.2       # Depth of primary beams.
SECONDARY_WIDTH = 0.7       # Width of secondary (horizontal ring) beams.
SECONDARY_DEPTH = 0.85      # Depth of secondary beams.
MIN_BEAM_LENGTH = 0.3       # Beams shorter than this are skipped.

# --- Outline Extraction (advanced) -------------------------------------------
RAY_SAMPLES       = 180     # Rays cast per floor to find the perimeter.
                            # Higher = more accurate on complex shapes.
CENTROID_ITERS     = 3      # Iterations to converge the adaptive centroid.
DEDUP_THRESHOLD    = 0.01   # Min distance between consecutive outline points.

# --- Materials ---------------------------------------------------------------
PRIMARY_COLOR   = (0.78, 0.75, 0.70, 1.0)   # RGBA — light concrete
SECONDARY_COLOR = (0.68, 0.65, 0.60, 1.0)   # RGBA — slightly darker
GLASS_COLOR     = (0.40, 0.60, 0.80, 0.25)  # RGBA — translucent blue

# --- Output Options ----------------------------------------------------------
CREATE_GLASS_PANELS = False          # Generate glass quad infill between beams.
COLLECTION_NAME     = "Structural_Skin"
PARENT_EMPTY_NAME   = "Diagrid_Structure"
CLEANUP_PREVIOUS    = True           # Delete previous generation in same
                                     # collection before re-generating.


# ============================================================================
#  INTERNAL FUNCTIONS  —  You shouldn't need to edit below this line
# ============================================================================

def get_massing():
    """Resolve the massing mesh object from name or selection."""
    if MASSING_OBJECT_NAME:
        obj = bpy.data.objects.get(MASSING_OBJECT_NAME)
        if not obj:
            raise ValueError(
                f"Object '{MASSING_OBJECT_NAME}' not found. "
                f"Available meshes: {[o.name for o in bpy.data.objects if o.type=='MESH']}"
            )
    else:
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError(
                "No mesh selected. Select your massing object and re-run, "
                "or set MASSING_OBJECT_NAME at the top of the script."
            )
    return obj


def get_z_bounds(obj):
    """Return (z_min, z_max) in world space."""
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return min(v.z for v in bb), max(v.z for v in bb)


def get_global_center_xy(obj):
    """Return (cx, cy) of the bounding box center in world space."""
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (
        (min(v.x for v in bb) + max(v.x for v in bb)) / 2,
        (min(v.y for v in bb) + max(v.y for v in bb)) / 2,
    )


def extract_outline(obj_eval, inv_matrix, z, prev_center, n_divisions):
    """
    Extract an evenly-spaced perimeter outline at height *z* using adaptive
    centroid raycasting.

    Returns (list[Vector] | None, Vector center).
    The returned center should be passed as *prev_center* for the next floor
    so the centroid tracks smoothly as the shape shifts.
    """
    center = Vector((prev_center.x, prev_center.y, z))

    # --- Adaptive centroid convergence ---
    hits = []
    for _ in range(CENTROID_ITERS):
        hits = []
        for i in range(RAY_SAMPLES):
            angle = 2 * math.pi * i / RAY_SAMPLES
            direction = Vector((math.cos(angle), math.sin(angle), 0))
            origin_local = inv_matrix @ center
            dir_local = (inv_matrix.to_3x3() @ direction).normalized()
            ok, loc, _, _ = obj_eval.ray_cast(
                origin_local, dir_local, distance=1000
            )
            if ok:
                hits.append((angle, obj_eval.matrix_world @ loc))
        if len(hits) < 3:
            return None, center
        center = Vector((
            sum(h[1].x for h in hits) / len(hits),
            sum(h[1].y for h in hits) / len(hits),
            z,
        ))

    # --- Sort by angle, deduplicate ---
    hits.sort(key=lambda x: x[0])
    pts = [h[1] for h in hits]
    filtered = [pts[0]]
    for p in pts[1:]:
        if (p - filtered[-1]).length > DEDUP_THRESHOLD:
            filtered.append(p)
    pts = filtered
    if len(pts) < 3:
        return None, center

    # --- Close loop & arc-length resample ---
    pts.append(pts[0])
    arcs = [0.0]
    for i in range(1, len(pts)):
        arcs.append(arcs[-1] + (pts[i] - pts[i - 1]).length)
    total = arcs[-1]
    if total < DEDUP_THRESHOLD:
        return None, center

    result = []
    for i in range(n_divisions):
        target = total * i / n_divisions
        for j in range(1, len(arcs)):
            if arcs[j] >= target:
                seg = arcs[j] - arcs[j - 1]
                t = (target - arcs[j - 1]) / seg if seg > 0 else 0
                pt = pts[j - 1].lerp(pts[j], t)
                pt.z = z
                result.append(pt)
                break

    return result, center


def make_box_beam(name, start, end, width, depth):
    """
    Create a rectangular box beam between *start* and *end*.
    Returns a Blender Object or None if the beam is too short.
    """
    direction = end - start
    length = direction.length
    if length < MIN_BEAM_LENGTH:
        return None

    dn = direction.normalized()
    up = Vector((0, 0, 1))
    if abs(dn.dot(up)) > 0.999:
        side = Vector((1, 0, 0))
    else:
        side = dn.cross(up).normalized()
    local_up = side.cross(dn).normalized()

    hw, hd = width / 2, depth / 2
    cs = [
        start + side * hw + local_up * hd,
        start - side * hw + local_up * hd,
        start - side * hw - local_up * hd,
        start + side * hw - local_up * hd,
    ]
    ce = [
        end + side * hw + local_up * hd,
        end - side * hw + local_up * hd,
        end - side * hw - local_up * hd,
        end + side * hw - local_up * hd,
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5),
        (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([v[:] for v in cs + ce], [], faces)
    mesh.update()
    return bpy.data.objects.new(name, mesh)


def get_or_create_material(name, color):
    """Get existing or create a new Principled BSDF material."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.65
        if color[3] < 1.0:
            bsdf.inputs["Alpha"].default_value = color[3]
            mat.surface_render_method = 'BLENDED' if hasattr(mat, 'surface_render_method') else mat.surface_render_method
    return mat


def setup_collection():
    """Create (or clean) the output collection."""
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col and CLEANUP_PREVIOUS:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
        col = None
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(col)
    return col


# ============================================================================
#  MAIN
# ============================================================================

def generate():
    """Entry point — generates the full structural skin."""

    print("\n" + "=" * 64)
    print("  DIAGRID STRUCTURAL SKIN GENERATOR")
    print("=" * 64)

    # ---- Massing ----
    massing = get_massing()
    print(f"  Massing : {massing.name}")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    massing_eval = massing.evaluated_get(depsgraph)
    inv = massing_eval.matrix_world.inverted()

    z_lo, z_hi = get_z_bounds(massing)
    z_start = Z_START if Z_START is not None else z_lo
    z_end   = Z_END   if Z_END   is not None else z_hi
    print(f"  Z range : {z_start:.2f} → {z_end:.2f}  (height {z_end - z_start:.2f})")

    # ---- Floor levels ----
    floor_zs = []
    z = z_start
    while z <= z_end + 0.01:
        floor_zs.append(z)
        z += FLOOR_HEIGHT
    # Guarantee at least one bay: if the massing is shorter than FLOOR_HEIGHT the
    # loop above produces only one Z value.  Always append z_end so every volume
    # gets a bottom + top outline regardless of height vs. floor spacing.
    if not floor_zs or (z_end - floor_zs[-1]) > 0.1:
        floor_zs.append(z_end)
    if SKIP_BOTTOM_FLOORS:
        floor_zs = floor_zs[SKIP_BOTTOM_FLOORS:]
    if SKIP_TOP_FLOORS:
        floor_zs = floor_zs[: -SKIP_TOP_FLOORS or None]
    # After skipping, enforce the minimum-2-levels guarantee again
    if len(floor_zs) < 2:
        floor_zs = [z_start, z_end]
    print(f"  Floors  : {len(floor_zs)}  (every {FLOOR_HEIGHT} units, "
          f"min 1 bay enforced)")

    # ---- Extract outlines ----
    print("  Extracting perimeter outlines …")
    gcx, gcy = get_global_center_xy(massing)
    prev_center = Vector((gcx, gcy, 0))
    floor_outlines = {}

    for i, z in enumerate(floor_zs):
        outline, prev_center = extract_outline(
            massing_eval, inv, z, prev_center, PERIMETER_DIVISIONS
        )
        if outline:
            floor_outlines[i] = outline
            print(f"    Floor {i:3d}  Z={z:8.2f}  →  {len(outline)} nodes")

    if len(floor_outlines) < 2:
        print("  ERROR: fewer than 2 valid outlines. Is the massing watertight?")
        return None

    # ---- Setup output ----
    col = setup_collection()
    mat_primary   = get_or_create_material("DSkin_Primary",   PRIMARY_COLOR)
    mat_secondary = get_or_create_material("DSkin_Secondary", SECONDARY_COLOR)

    parent = bpy.data.objects.new(PARENT_EMPTY_NAME, None)
    col.objects.link(parent)

    # ---- Primary (diagrid) beams ----
    print("  Generating primary diagrid beams …")
    p_count = 0
    valid = sorted(floor_outlines.keys())

    for fi in range(len(valid) - 1):
        lo_idx = valid[fi]
        hi_idx = valid[fi + 1]
        lower = floor_outlines[lo_idx]
        upper = floor_outlines[hi_idx]
        n = min(len(lower), len(upper))

        for j in range(n):
            if ALTERNATING and lo_idx % 2 == 0:
                targets = [
                    (j + DIAGRID_SKIP) % n,
                    (j - DIAGRID_SKIP) % n,
                ]
            else:
                targets = [
                    (j - DIAGRID_SKIP) % n,
                    (j + DIAGRID_SKIP) % n,
                ]

            for t in targets:
                beam = make_box_beam(
                    f"P_{lo_idx}_{j}_{t}",
                    lower[j], upper[t],
                    PRIMARY_WIDTH, PRIMARY_DEPTH,
                )
                if beam:
                    beam.data.materials.append(mat_primary)
                    col.objects.link(beam)
                    beam.parent = parent
                    p_count += 1

    print(f"    → {p_count} primary beams")

    # ---- Secondary (ring) beams ----
    print("  Generating secondary ring beams …")
    s_count = 0
    for fi in valid:
        outline = floor_outlines[fi]
        n = len(outline)
        for j in range(n):
            beam = make_box_beam(
                f"S_{fi}_{j}",
                outline[j], outline[(j + 1) % n],
                SECONDARY_WIDTH, SECONDARY_DEPTH,
            )
            if beam:
                beam.data.materials.append(mat_secondary)
                col.objects.link(beam)
                beam.parent = parent
                s_count += 1

    print(f"    → {s_count} secondary beams")

    # ---- Glass panels (optional) ----
    g_count = 0
    if CREATE_GLASS_PANELS:
        print("  Generating glass panels …")
        mat_glass = get_or_create_material("DSkin_Glass", GLASS_COLOR)
        for fi in range(len(valid) - 1):
            lo_idx = valid[fi]
            hi_idx = valid[fi + 1]
            lower = floor_outlines[lo_idx]
            upper = floor_outlines[hi_idx]
            n = min(len(lower), len(upper))
            for j in range(n):
                jn = (j + 1) % n
                verts = [lower[j][:], lower[jn][:], upper[jn][:], upper[j][:]]
                mesh = bpy.data.meshes.new(f"G_{lo_idx}_{j}")
                mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
                mesh.update()
                panel = bpy.data.objects.new(f"G_{lo_idx}_{j}", mesh)
                panel.data.materials.append(mat_glass)
                col.objects.link(panel)
                panel.parent = parent
                g_count += 1
        print(f"    → {g_count} glass panels")

    # ---- Summary ----
    total = p_count + s_count + g_count
    print("\n" + "-" * 64)
    print(f"  COMPLETE  ✓")
    print(f"    Primary  (diagrid) : {p_count:>6}")
    print(f"    Secondary (ring)   : {s_count:>6}")
    if g_count:
        print(f"    Glass panels       : {g_count:>6}")
    print(f"    TOTAL              : {total:>6}")
    print(f"    Collection         : '{COLLECTION_NAME}'")
    print(f"    Parent empty       : '{PARENT_EMPTY_NAME}'")
    print("=" * 64 + "\n")

    return parent


# ============================================================================
#  RUN
# ============================================================================
if __name__ == "__main__":
    generate()
