"""
TPAC Architecture Generator
===========================
A reusable Blender Python module that takes a programmatic TPAC-style massing
and generates the full architectural envelope on top of it:
  - Structural system (mega-columns, piloti, transfer truss, bracing)
  - Floor slabs per level (with Globe sphere penetration cuts)
  - Curtain walls for central cube, upper tower, lobby
  - Three theater volumes: Grand (fly tower), Blue Box, Globe (sphere)
  - Roof elements (terraces, parapets, mechanical, penthouse)
  - Site landscape (sunken amphitheater, entry plaza, planting, water)
  - Cameras, lighting, render setup

USAGE
-----
Open the massing .blend in Blender, then in the Scripting workspace:

    import tpac_generator
    tpac_generator.generate()                  # run with default config
    tpac_generator.generate(CONFIG_OVERRIDE)   # run with custom config

Or from command line / background:

    blender massing.blend --python tpac_generator.py

The script auto-detects level heights, shaft positions, and cube/tower
footprints from the existing massing objects. Adjust CONFIG to customize
column sizes, materials, curtain-wall grid, camera positions, etc.

REQUIREMENTS
------------
  * Massing blocks named `<program>|<level>` (e.g. `backstage|L4`)
  * Shafts named `SHAFT|<description>` or contain "fire stair"/"elevator"
  * Fly tower blocks named `fly tower|<level>`
  * Z-up, meters, origin at site center.

Re-runnable: existing ARCHITECTURE / SITE / etc. collections are cleared first.
"""

import bpy
import bmesh
import math
import os
from collections import defaultdict
from mathutils import Vector


# ============================================================================
# STRUCTURE GRID CONFIGURATION
# ============================================================================

STRUCT_GRID_X = 6.0       # Column spacing X direction (m)
STRUCT_GRID_Y = 6.0       # Column spacing Y direction (m)
FLOOR_HEIGHT  = 4.5       # Floor-to-floor height (m)

COLUMN_SIZE = 0.6         # Column section (0.6 × 0.6 m)
BEAM_SIZE   = 0.5         # Beam section (0.5 × 0.5 m)
SLAB_T      = 0.3         # Slab thickness (m)

ENABLE_FRAME = True       # Enable structural frame generation


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    # --- Site ---
    "site_size":              70.0,     # square site side length (m)
    "site_elevation":         0.0,

    # --- Structural ---
    "mega_column_main":       (10.0, 12.0),   # (sx, sy) for largest mega-col
    "mega_column_typical":    (8.0, 8.0),     # 3 smaller mega-cols
    "mega_column_wall_t":     0.8,            # diaphragm wall thickness
    "mega_column_material":   "concrete",

    "piloti_section":         1.2,
    "piloti_material":        "steel",
    "piloti_count_per_side":  3,

    "transfer_truss_depth":   1.0,
    "transfer_truss_width":   0.8,
    "transfer_truss_material":"steel",

    "brace_thickness":        0.5,
    "brace_material":         "steel",

    # --- Slabs ---
    "slab_thickness":         0.5,
    "slab_material":          "slab",

    # --- Curtain wall ---
    "cw_grid_h":              3.0,     # horizontal spacing of vertical mullions
    "cw_grid_v":              4.5,     # vertical spacing of horizontal mullions
    "cw_mullion_thickness":   0.15,
    "cw_glass_thickness":     0.05,
    "cw_cube_glass":          "glass_frit",
    "cw_tower_glass":         "glass",
    "cw_lobby_glass":         "glass",

    # --- Theaters ---
    "globe_radius":           17.5,
    "globe_center_offset_y":  -17.0,   # relative to site center
    "globe_center_z_ratio":   0.5,     # fraction up the cube height
    "globe_material":         "globe",
    "globe_panel_thickness":  0.15,
    "globe_support_struts":   3,

    "bluebox_material":       "blue",
    "bluebox_band_spacing":   2.0,
    "bluebox_mullion_spacing":3.0,
    "bluebox_brace_count":    4,
    "bluebox_bevel_offset":   0.3,

    "grand_tower_material":   "alu_panel",
    "grand_tower_rib_spacing":4.0,
    "grand_tower_cap_height": 3.5,
    "grand_bevel_offset":     0.4,

    # --- Roof ---
    "parapet_height":         1.2,
    "parapet_thickness":      0.2,
    "parapet_material":       "alu_panel",
    "roof_slab_material":     "roof",
    "penthouse_height":       4.0,

    # --- Lobby canopy ---
    "canopy_projection":      2.5,
    "canopy_thickness":       0.3,
    "canopy_height":          4.2,
    "canopy_material":        "alu_panel",

    # --- Site landscape ---
    "build_site":             True,
    "sunken_tiers":           5,
    "sunken_tier_drop":       0.5,
    "sunken_tier_width":      3.0,
    "sunken_y_outer":         -20.0,
    "entry_platform_height":  0.5,
    "entry_step_count":       3,
    "entry_step_rise":        0.17,
    "water_pool_x":           [-34, -26],
    "water_pool_y":           [-15, 15],

    # --- Camera & lighting ---
    "setup_cameras_lights":   True,
    "render_resolution":      (1600, 1000),
    "render_engine":          "BLENDER_EEVEE",   # or "CYCLES"
    "sun_energy_primary":     3.5,
    "sun_energy_fill":        0.8,
    "sky_type":               "HOSEK_WILKIE",    # fallback auto-handled

    # --- Cleanup ---
    "hide_massing_reference": True,
    "clear_previous_output":  True,
}


# Material palette — (name, rgba, metallic, roughness, transmission, alpha)
MATERIAL_PALETTE = {
    "concrete":   ("ARCH_Concrete",   (0.72, 0.70, 0.68, 1.0), 0.0, 0.70, 0.0, 1.00),
    "steel":      ("ARCH_Steel",      (0.35, 0.37, 0.40, 1.0), 0.9, 0.35, 0.0, 1.00),
    "mullion":    ("ARCH_Mullion",    (0.18, 0.18, 0.20, 1.0), 0.85,0.30, 0.0, 1.00),
    "glass":      ("ARCH_Glass",      (0.55, 0.72, 0.82, 0.25),0.0, 0.05, 0.9, 0.25),
    "glass_frit": ("ARCH_GlassFrit",  (0.78, 0.85, 0.90, 0.55),0.0, 0.15, 0.5, 0.55),
    "alu_panel":  ("ARCH_AluPanel",   (0.85, 0.86, 0.87, 1.0), 0.7, 0.35, 0.0, 1.00),
    "globe":      ("ARCH_GlobeClad",  (0.90, 0.60, 0.20, 1.0), 0.4, 0.45, 0.0, 1.00),
    "blue":       ("ARCH_BlueClad",   (0.15, 0.35, 0.70, 1.0), 0.3, 0.45, 0.0, 1.00),
    "roof":       ("ARCH_Roof",       (0.30, 0.30, 0.32, 1.0), 0.2, 0.70, 0.0, 1.00),
    "slab":       ("ARCH_Slab",       (0.78, 0.76, 0.74, 1.0), 0.0, 0.80, 0.0, 1.00),
    "paving":     ("SITE_Paving",     (0.68, 0.64, 0.58, 1.0), 0.0, 0.80, 0.0, 1.00),
    "grass":      ("SITE_Grass",      (0.35, 0.48, 0.28, 1.0), 0.0, 0.85, 0.0, 1.00),
    "water":      ("SITE_Water",      (0.28, 0.45, 0.55, 1.0), 0.0, 0.10, 0.0, 1.00),
}


# ============================================================================
# UTILITIES
# ============================================================================

def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col


def make_material(key):
    """Get or create a material from the palette by key."""
    if key not in MATERIAL_PALETTE:
        raise ValueError(f"Unknown material key: {key}")
    name, rgba, metallic, roughness, transmission, alpha = MATERIAL_PALETTE[key]
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    for tkey in ("Transmission Weight", "Transmission"):
        if tkey in bsdf.inputs:
            bsdf.inputs[tkey].default_value = transmission
            break
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    return m


def move_to_collection(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)


def assign_mat(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def create_box(name, x0, y0, z0, x1, y1, z1, mat, coll):
    """Axis-aligned box from two corner coords."""
    cx, cy, cz = (x0+x1)/2, (y0+y1)/2, (z0+z1)/2
    sx = max(abs(x1-x0), 0.001)
    sy = max(abs(y1-y0), 0.001)
    sz = max(abs(z1-z0), 0.001)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)
    obj.name = name
    assign_mat(obj, mat)
    move_to_collection(obj, coll)
    return obj


def make_diagonal_beam(name, p0, p1, thickness, mat, coll):
    """Create a square-section beam between two 3D points."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    v = Vector(p1) - Vector(p0)
    length = v.length
    obj.scale = (thickness, thickness, length)
    bpy.ops.object.transform_apply(scale=True)
    mid = (Vector(p0) + Vector(p1)) / 2
    obj.location = mid
    up = Vector((0, 0, 1))
    v_norm = v.normalized()
    if v_norm != up and v_norm != -up:
        axis = up.cross(v_norm)
        angle = up.angle(v_norm)
        obj.rotation_mode = 'AXIS_ANGLE'
        obj.rotation_axis_angle = (angle, axis.x, axis.y, axis.z)
    assign_mat(obj, mat)
    move_to_collection(obj, coll)
    return obj


def bevel_object(obj, offset, segments=2):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=offset, segments=segments)
    bpy.ops.object.mode_set(mode='OBJECT')


def boolean_difference(target, cutter, apply_immediately=True):
    mod = target.modifiers.new("_bool_diff", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    if apply_immediately:
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier="_bool_diff")


# ============================================================================
# MASSING INTROSPECTION
# ============================================================================

def is_massing_object(obj):
    """Heuristic: programmatic massing block is a MESH with `<program>|<level>`
       and NOT one of our generated ARCH objects."""
    if obj.type != 'MESH':
        return False
    if "|" not in obj.name:
        return False
    # Exclude generated architecture prefixes
    arch_prefixes = ("SLAB|", "MEGACOL", "PILOTI", "TRUSS", "BRACE",
                     "CUBE|", "TOWER|", "LOBBY|", "BLUEBOX|", "GRAND|",
                     "GLOBE|", "ROOF|", "SHAFT|cap", "SHAFT|clad",
                     "SITE|", "ENTRY|", "SUNKEN|")
    if obj.name.startswith(arch_prefixes):
        return False
    if obj.name.startswith("GROUND"):
        return False
    return True


def is_shaft_object(obj):
    if obj.type != 'MESH':
        return False
    n = obj.name.lower()
    return n.startswith("shaft|") and ("fire stair" in n or "elevator" in n)


def object_world_bbox(obj):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not verts:
        return None
    xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def analyze_massing():
    """Auto-extract level heights, shaft bboxes, cube/tower extents.
       Returns a dict with structured info used throughout generation."""

    levels = defaultdict(lambda: {
        "z_min": 1e9, "z_max": -1e9,
        "x_min": 1e9, "x_max": -1e9,
        "y_min": 1e9, "y_max": -1e9,
        "objs": []
    })
    shafts = []

    for obj in bpy.data.objects:
        if is_shaft_object(obj):
            bb = object_world_bbox(obj)
            if bb:
                shafts.append({"name": obj.name, "bbox": bb})
            continue
        if not is_massing_object(obj):
            continue
        lvl = obj.name.split("|")[-1].split(".")[0]
        bb = object_world_bbox(obj)
        if not bb:
            continue
        d = levels[lvl]
        d["x_min"] = min(d["x_min"], bb[0])
        d["y_min"] = min(d["y_min"], bb[1])
        d["z_min"] = min(d["z_min"], bb[2])
        d["x_max"] = max(d["x_max"], bb[3])
        d["y_max"] = max(d["y_max"], bb[4])
        d["z_max"] = max(d["z_max"], bb[5])
        d["objs"].append(obj)

    def lvl_key(k):
        try: return int(k.replace("L", ""))
        except: return 99

    sorted_levels = sorted(levels.keys(), key=lvl_key)

    # Derive cube (widest level) and tower (levels above cube)
    max_span = 0
    cube_level = None
    for lvl in sorted_levels:
        d = levels[lvl]
        span = max(d["x_max"] - d["x_min"], d["y_max"] - d["y_min"])
        if span > max_span:
            max_span = span
            cube_level = lvl

    # Cube z extent = from first wide-level z_min to last wide-level z_max
    wide_levels = [l for l in sorted_levels
                   if (levels[l]["x_max"] - levels[l]["x_min"]) > 50]
    cube_z = None
    if wide_levels:
        cube_z = (
            min(levels[l]["z_min"] for l in wide_levels),
            max(levels[l]["z_max"] for l in wide_levels)
        )

    # Tower levels = after cube (narrower footprint again)
    tower_levels = []
    after_cube = False
    for lvl in sorted_levels:
        d = levels[lvl]
        span_x = d["x_max"] - d["x_min"]
        if lvl in wide_levels:
            after_cube = True
            continue
        if after_cube and span_x < 30:
            tower_levels.append(lvl)

    tower_z = None
    if tower_levels:
        tower_z = (
            min(levels[l]["z_min"] for l in tower_levels),
            max(levels[l]["z_max"] for l in tower_levels)
        )
        tower_xy = (
            min(levels[l]["x_min"] for l in tower_levels),
            min(levels[l]["y_min"] for l in tower_levels),
            max(levels[l]["x_max"] for l in tower_levels),
            max(levels[l]["y_max"] for l in tower_levels),
        )
    else:
        tower_xy = None

    # Lobby / ground core = levels BEFORE cube
    ground_levels = []
    for lvl in sorted_levels:
        if lvl in wide_levels:
            break
        ground_levels.append(lvl)

    ground_z = None
    if ground_levels:
        ground_z = (
            min(levels[l]["z_min"] for l in ground_levels),
            max(levels[l]["z_max"] for l in ground_levels)
        )
        ground_xy = (
            min(levels[l]["x_min"] for l in ground_levels),
            min(levels[l]["y_min"] for l in ground_levels),
            max(levels[l]["x_max"] for l in ground_levels),
            max(levels[l]["y_max"] for l in ground_levels),
        )
    else:
        ground_xy = None

    # Fly tower extent (Grand Theater)
    fly_bbox = None
    fly_objs = [o for o in bpy.data.objects
                if o.type == 'MESH' and o.name.lower().startswith("fly tower|")]
    if fly_objs:
        all_bb = [object_world_bbox(o) for o in fly_objs]
        all_bb = [b for b in all_bb if b]
        if all_bb:
            fly_bbox = (
                min(b[0] for b in all_bb), min(b[1] for b in all_bb),
                min(b[2] for b in all_bb),
                max(b[3] for b in all_bb), max(b[4] for b in all_bb),
                max(b[5] for b in all_bb),
            )

    return {
        "levels": dict(levels),
        "sorted_levels": sorted_levels,
        "shafts": shafts,
        "wide_levels": wide_levels,
        "tower_levels": tower_levels,
        "ground_levels": ground_levels,
        "cube_z": cube_z,
        "cube_xy": (
            min(levels[l]["x_min"] for l in wide_levels),
            min(levels[l]["y_min"] for l in wide_levels),
            max(levels[l]["x_max"] for l in wide_levels),
            max(levels[l]["y_max"] for l in wide_levels),
        ) if wide_levels else None,
        "tower_z": tower_z,
        "tower_xy": tower_xy,
        "ground_z": ground_z,
        "ground_xy": ground_xy,
        "fly_bbox": fly_bbox,
    }


# ============================================================================
# GENERATION MODULES
# ============================================================================

def clear_previous_output():
    """Remove objects from our generator's collections so re-runs are clean."""
    target_cols = ["ARCHITECTURE", "SITE", "SUNKEN_AMPH", "ENTRY_PLAZA",
                   "MASSING_REFERENCE", "SHAFTS_ORIGINAL"]
    for cname in target_cols:
        c = bpy.data.collections.get(cname)
        if not c:
            continue
        # unlink all objects (but don't delete — originals are restored to scene)
        for sub in list(c.children):
            for obj in list(sub.objects):
                # generated objects (our prefixes) are deleted
                if _is_generated(obj.name):
                    bpy.data.objects.remove(obj, do_unlink=True)
                else:
                    # restore original to scene master collection
                    move_to_collection(obj, bpy.context.scene.collection)
            bpy.data.collections.remove(sub)
        for obj in list(c.objects):
            if _is_generated(obj.name):
                bpy.data.objects.remove(obj, do_unlink=True)
            else:
                move_to_collection(obj, bpy.context.scene.collection)
        bpy.data.collections.remove(c)

    # Also remove prior cameras/lights we named
    for obj in list(bpy.data.objects):
        if obj.name.startswith(("CAM_", "SUN_")) or obj.name == "CAM_target":
            bpy.data.objects.remove(obj, do_unlink=True)


def _is_generated(name):
    prefixes = ("SLAB|", "MEGACOL", "PILOTI", "TRUSS", "BRACE",
                "CUBE|", "TOWER|", "LOBBY|", "BLUEBOX|", "GRAND|",
                "GLOBE|", "ROOF|", "SHAFT|cap", "SHAFT|clad",
                "SITE|", "ENTRY|", "SUNKEN|")
    return name.startswith(prefixes)


# -----------------------------------------------------------------------
# CONCERT HALL DETECTION & VOLUME CLASSIFICATION
# -----------------------------------------------------------------------

def identify_concert_hall_volume(info):
    """Identify massing objects belonging to concert hall core vs theater arms.
    
    Returns dict with:
    - concert_hall_objs: list of massing objects in main concert hall
    - grand_objs: objects in Grand Theater (fly tower) region (+X)
    - blue_objs: objects in Blue Box region (-X)
    - globe_objs: objects in Globe region (-Z)
    - cube_xy: concert hall footprint
    """
    if not info["cube_xy"]:
        return {"concert_hall_objs": [], "grand_objs": [], 
                "blue_objs": [], "globe_objs": []}
    
    cx0, cy0, cx1, cy1 = info["cube_xy"]
    cube_cx = (cx0 + cx1) / 2
    cube_cy = (cy0 + cy1) / 2
    
    result = {
        "concert_hall_objs": [],
        "grand_objs": [],
        "blue_objs": [],
        "globe_objs": [],
        "cube_xy": info["cube_xy"],
        "cube_cx": cube_cx,
        "cube_cy": cube_cy,
    }
    
    # Classify massing objects by their position
    for lvl in info["levels"].values():
        for obj in lvl["objs"]:
            if obj.type != 'MESH' or "|" not in obj.name:
                continue
            
            # Get object center
            bbox = object_world_bbox(obj)
            obj_cx = (bbox[0] + bbox[3]) / 2
            obj_cy = (bbox[1] + bbox[4]) / 2
            
            # Classify by relative position to cube center
            dx = obj_cx - cube_cx
            dy = obj_cy - cube_cy
            
            # Grand Theater: +X side (x > cube_cx + threshold)
            if dx > 5:
                result["grand_objs"].append(obj)
            # Blue Box: -X side (x < cube_cx - threshold)
            elif dx < -5:
                result["blue_objs"].append(obj)
            # Globe: -Z side (y < cube_cy - threshold)
            elif dy < -5:
                result["globe_objs"].append(obj)
            # Concert hall: central core
            else:
                result["concert_hall_objs"].append(obj)
    
    return result


# -----------------------------------------------------------------------
# STRUCTURE
# -----------------------------------------------------------------------

def build_mega_columns(info, config, coll):
    """4 mega-columns wrapping shaft cores. Largest one matches the mega-col
       spec sizes from config. Position from shaft centers."""
    shafts = info["shafts"]
    if len(shafts) < 4:
        print(f"[WARN] Expected 4 shafts, got {len(shafts)}. Skipping mega-cols.")
        return

    mat = make_material(config["mega_column_material"])
    # Sort shafts by (y, x) so NE/SE/SW/NW assignment is stable
    shaft_info = []
    for s in shafts:
        bb = s["bbox"]
        cx = (bb[0] + bb[3]) / 2
        cy = (bb[1] + bb[4]) / 2
        shaft_info.append({"name": s["name"], "cx": cx, "cy": cy,
                           "z_min": bb[2], "z_max": bb[5]})
    # Main mega-col = one with the largest program behind it (arbitrarily NE)
    # Sort so NE (+x,+y) first to receive the big 10×12
    def quadrant_key(s):
        qx = 1 if s["cx"] > 0 else 0
        qy = 1 if s["cy"] > 0 else 0
        # NE, SE, SW, NW ordering: (qx,qy) = (1,1),(1,0),(0,0),(0,1)
        return {(1,1):0, (1,0):1, (0,0):2, (0,1):3}[(qx, qy)]
    shaft_info.sort(key=quadrant_key)

    sizes = [config["mega_column_main"]] + [config["mega_column_typical"]] * 3
    z_min = min(s["z_min"] for s in shaft_info)
    z_max = max(s["z_max"] for s in shaft_info)

    labels = ["NE", "SE", "SW", "NW"]
    for i, (s, sz) in enumerate(zip(shaft_info, sizes)):
        sx, sy = sz
        label = labels[i]
        tag = "10x12" if i == 0 else "8x8"
        name = f"MEGACOL|MC{i+1}_{label}_{tag}"
        outer = create_box(name,
            s["cx"]-sx/2, s["cy"]-sy/2, z_min,
            s["cx"]+sx/2, s["cy"]+sy/2, z_max,
            mat, coll)
        # Hollow core
        t = config["mega_column_wall_t"]
        inner = create_box(f"_inner_{name}",
            s["cx"]-sx/2+t, s["cy"]-sy/2+t, z_min-0.1,
            s["cx"]+sx/2-t, s["cy"]+sy/2-t, z_max+0.1,
            mat, coll)
        boolean_difference(outer, inner)
        bpy.data.objects.remove(inner, do_unlink=True)


def build_piloti_and_transfer_truss(info, config, coll):
    """Secondary piloti columns along ground core + transfer truss at cube L4."""
    if not info["ground_xy"] or not info["cube_z"]:
        return
    gx0, gy0, gx1, gy1 = info["ground_xy"]
    gz0 = info["levels"][info["sorted_levels"][0]]["z_min"]
    cube_bottom = info["cube_z"][0]

    mat_steel = make_material(config["piloti_material"])
    mat_truss = make_material(config["transfer_truss_material"])

    s = config["piloti_section"]
    n_per_side = config["piloti_count_per_side"]
    # Piloti along +X and -X faces of ground core
    # Spread n evenly between gy0 and gy1
    y_positions = []
    if n_per_side > 1:
        for i in range(n_per_side):
            t = i / (n_per_side - 1)
            y_positions.append(gy0 + t * (gy1 - gy0))
    else:
        y_positions = [(gy0 + gy1) / 2]

    # Inset slightly from core edge
    for i, y in enumerate(y_positions):
        for side, x in [("E", gx1 - 0.6), ("W", gx0 + 0.6)]:
            name = f"PILOTI|col_{side}_{i+1:02d}"
            create_box(name, x-s/2, y-s/2, gz0, x+s/2, y+s/2, cube_bottom,
                       mat_steel, coll)

    # Transfer truss ring at cube bottom
    if not info["cube_xy"]:
        return
    cx0, cy0, cx1, cy1 = info["cube_xy"]
    tw = config["transfer_truss_width"]
    td = config["transfer_truss_depth"]
    z_top = cube_bottom
    z_bot = cube_bottom - td

    # Perimeter ring (clamped inside site)
    half_site = config["site_size"] / 2 - 0.05  # small inset to stay inside
    cx0c = max(cx0, -half_site); cx1c = min(cx1, half_site)
    cy0c = max(cy0, -half_site); cy1c = min(cy1, half_site)
    ring = [
        (cx0c, cy0c-tw/2, z_bot, cx1c, cy0c+tw/2, z_top, "ring_S"),
        (cx0c, cy1c-tw/2, z_bot, cx1c, cy1c+tw/2, z_top, "ring_N"),
        (cx0c-tw/2, cy0c, z_bot, cx0c+tw/2, cy1c, z_top, "ring_W"),
        (cx1c-tw/2, cy0c, z_bot, cx1c+tw/2, cy1c, z_top, "ring_E"),
    ]
    for x0, y0, z0, x1, y1, z1, tag in ring:
        create_box(f"TRUSS|cube_bottom|{tag}", x0,y0,z0, x1,y1,z1, mat_truss, coll)

    # Internal grid beams at mega-col axes (use shaft centers)
    mc_x = sorted(set(round((s["bbox"][0]+s["bbox"][3])/2, 1) for s in info["shafts"]))
    mc_y = sorted(set(round((s["bbox"][1]+s["bbox"][4])/2, 1) for s in info["shafts"]))
    for y in mc_y:
        create_box(f"TRUSS|cube_bottom|xbeam_y{y:+.1f}",
                   cx0c, y-tw/2, z_bot, cx1c, y+tw/2, z_top, mat_truss, coll)
    for x in mc_x:
        create_box(f"TRUSS|cube_bottom|ybeam_x{x:+.1f}",
                   x-tw/2, cy0c, z_bot, x+tw/2, cy1c, z_top, mat_truss, coll)


def build_ground_bracing(info, config, coll):
    """Diagonal X-bracing between mega-cols on 3 outer faces."""
    if len(info["shafts"]) < 4:
        return
    mat = make_material(config["brace_material"])
    ground_z = info["levels"][info["sorted_levels"][0]]["z_min"]
    if info["cube_z"]:
        ground_top = info["cube_z"][0]
    else:
        ground_top = 0

    # Mega-col centers
    centers = []
    for s in info["shafts"]:
        bb = s["bbox"]
        centers.append(((bb[0]+bb[3])/2, (bb[1]+bb[4])/2))

    # Pair adjacent mega-cols on S, E, W faces (skip N where fly tower sits)
    # Sort by angle from origin
    centers.sort(key=lambda p: math.atan2(p[1], p[0]))
    # Find NE, SE, SW, NW
    ne = max(centers, key=lambda p: p[0] + p[1])
    se = max(centers, key=lambda p: p[0] - p[1])
    sw = max(centers, key=lambda p: -p[0] - p[1])
    nw = max(centers, key=lambda p: -p[0] + p[1])

    pairs = [
        (ne, se, "E"),
        (se, sw, "S"),
        (sw, nw, "W"),
    ]
    thk = config["brace_thickness"]
    for (a, b, tag) in pairs:
        ax, ay = a; bx, by = b
        p0 = (ax, ay, 0)
        p1 = (bx, by, ground_top)
        make_diagonal_beam(f"BRACE|ground_X_{tag}_1", p0, p1, thk, mat, coll)
        p2 = (ax, ay, ground_top)
        p3 = (bx, by, 0)
        make_diagonal_beam(f"BRACE|ground_X_{tag}_2", p2, p3, thk, mat, coll)


# -----------------------------------------------------------------------
# SLABS
# -----------------------------------------------------------------------

def build_slabs(info, config, coll):
    """Floor slabs at top of each level."""
    mat = make_material(config["slab_material"])
    t = config["slab_thickness"]
    half_site = config["site_size"] / 2

    def lvl_key(k):
        try: return int(k.replace("L", ""))
        except: return 99

    for lvl in sorted(info["levels"].keys(), key=lvl_key):
        d = info["levels"][lvl]
        if d["z_max"] < -1e8:
            continue
        x0 = max(d["x_min"] - 0.2, -half_site)
        x1 = min(d["x_max"] + 0.2,  half_site)
        y0 = max(d["y_min"] - 0.2, -half_site)
        y1 = min(d["y_max"] + 0.2,  half_site)
        create_box(f"SLAB|{lvl}_top", x0, y0, d["z_max"]-t, x1, y1, d["z_max"],
                   mat, coll)

    # Ground plaza slab
    create_box("SLAB|L0_plaza", -half_site, -half_site, -0.3,
               half_site, half_site, 0.0, make_material("paving"), coll)
    # Basement slab
    if info["ground_xy"] and info["levels"]:
        gx0, gy0, gx1, gy1 = info["ground_xy"]
        gz0 = info["levels"][info["sorted_levels"][0]]["z_min"]
        create_box("SLAB|basement_base",
                   gx0 - 2, gy0 - 0.5, gz0 - 0.3,
                   gx1 + 2, gy1 + 0.5, gz0, mat, coll)


def cut_globe_through_slabs(info, config):
    """Boolean-cut circular openings where Globe passes through floor slabs."""
    if not info["cube_z"]:
        return
    gr = config["globe_radius"]
    gcx = 0.0
    gcy = config["globe_center_offset_y"]
    cube_h = info["cube_z"][1] - info["cube_z"][0]
    gcz = info["cube_z"][0] + cube_h * config["globe_center_z_ratio"]

    cut_count = 0
    for obj in list(bpy.data.objects):
        if not obj.name.startswith("SLAB|"):
            continue
        if obj.type != 'MESH':
            continue
        verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
        if not verts:
            continue
        zs = [v.z for v in verts]
        z_center = (min(zs) + max(zs)) / 2
        dz = z_center - gcz
        if abs(dz) >= gr:
            continue
        r_at_z = (gr**2 - dz**2) ** 0.5
        if r_at_z < 0.3:
            continue
        xs = [v.x for v in verts]; ys = [v.y for v in verts]
        if max(xs) < gcx-r_at_z or min(xs) > gcx+r_at_z: continue
        if max(ys) < gcy-r_at_z or min(ys) > gcy+r_at_z: continue

        bpy.ops.mesh.primitive_cylinder_add(
            radius=r_at_z + 0.3, depth=2.0, vertices=48,
            location=(gcx, gcy, z_center))
        cutter = bpy.context.active_object
        cutter.name = f"_cut_{obj.name}"
        boolean_difference(obj, cutter)
        bpy.data.objects.remove(cutter, do_unlink=True)
        cut_count += 1
    print(f"  [slabs] Cut {cut_count} Globe penetration openings")


# -----------------------------------------------------------------------
# THEATERS
# -----------------------------------------------------------------------

def build_globe_theater(info, config, coll):
    """Sphere + panel grid + collar ring + support struts."""
    if not info["cube_z"]:
        return
    gr = config["globe_radius"]
    gcx = 0.0
    gcy = config["globe_center_offset_y"]
    cube_h = info["cube_z"][1] - info["cube_z"][0]
    gcz = info["cube_z"][0] + cube_h * config["globe_center_z_ratio"]

    # Sphere shell
    bpy.ops.mesh.primitive_uv_sphere_add(radius=gr, segments=48, ring_count=32,
                                         location=(gcx, gcy, gcz))
    globe = bpy.context.active_object
    globe.name = "GLOBE|sphere_shell"
    bpy.ops.object.shade_smooth()
    assign_mat(globe, make_material(config["globe_material"]))
    move_to_collection(globe, coll)

    # Panel grid (wireframe duplicate)
    bpy.ops.object.select_all(action='DESELECT')
    globe.select_set(True); bpy.context.view_layer.objects.active = globe
    bpy.ops.object.duplicate()
    grid = bpy.context.active_object
    grid.name = "GLOBE|panel_grid"
    mod = grid.modifiers.new("wire", 'WIREFRAME')
    mod.thickness = config["globe_panel_thickness"]
    mod.use_even_offset = True
    bpy.ops.object.modifier_apply(modifier="wire")
    assign_mat(grid, make_material("mullion"))
    move_to_collection(grid, coll)

    # Collar ring at y = cube south face (cube_xy[1])
    if info["cube_xy"]:
        collar_y = info["cube_xy"][1]
        # Only add collar if it's within sphere range
        dy = collar_y - gcy
        if abs(dy) < gr:
            ring_r = (gr**2 - dy**2) ** 0.5
            bpy.ops.mesh.primitive_torus_add(
                major_radius=ring_r, minor_radius=0.35,
                major_segments=64, minor_segments=12,
                location=(gcx, collar_y, gcz))
            ring = bpy.context.active_object
            ring.name = "GLOBE|collar_ring"
            ring.rotation_euler = (math.pi/2, 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.object.shade_smooth()
            assign_mat(ring, make_material("mullion"))
            move_to_collection(ring, coll)

    # Support struts
    mat_steel = make_material("steel")
    n = config["globe_support_struts"]
    cube_face_y = info["cube_xy"][1] if info["cube_xy"] else gcy + gr*0.5
    for i in range(n):
        # Spread struts along x from -14 to +14, anchor to cube face at y=cube south
        t = i / max(n-1, 1)
        x_anchor = -14 + t * 28
        x_tip = -10 + t * 20
        y_tip = gcy - gr * 0.75
        anchor_z = info["cube_z"][0] + 1.5
        tip_z = gcz - gr * 0.25
        make_diagonal_beam(f"GLOBE|support_strut_{i+1}",
            (x_anchor, cube_face_y, anchor_z),
            (x_tip,   y_tip,       tip_z),
            0.6, mat_steel, coll)


def build_bluebox_theater(info, config, coll):
    """Blue cantilevered cuboid on +X side of cube."""
    if not info["cube_z"] or not info["cube_xy"]:
        return
    cx0, cy0, cx1, cy1 = info["cube_xy"]
    cz0, cz1 = info["cube_z"]

    # Blue box: +X half of cube-level volume, inset in y to shaft line
    # Infer from shaft y positions
    shaft_ys = []
    for s in info["shafts"]:
        bb = s["bbox"]
        shaft_ys.append((bb[1] + bb[4]) / 2)
    shaft_ys.sort()
    # Use shaft y span for Blue Box width
    bx0 = 17.0 if cx1 > 20 else cx1 * 0.5
    by0 = min(shaft_ys) if shaft_ys else cy0 + 5
    by1 = max(shaft_ys) if shaft_ys else cy1 - 5
    bx1 = cx1
    bz0 = cz0
    bz1 = cz1

    mat_clad = make_material(config["bluebox_material"])
    mat_mull = make_material("mullion")
    mat_glass = make_material(config["cw_cube_glass"])
    mat_steel = make_material("steel")

    shell = create_box("BLUEBOX|shell", bx0,by0,bz0, bx1,by1,bz1, mat_clad, coll)
    bevel_object(shell, config["bluebox_bevel_offset"])

    # Horizontal bands
    band_spacing = config["bluebox_band_spacing"]
    n_bands = int((bz1-bz0)/band_spacing)
    for i in range(1, n_bands):
        z = bz0 + i*band_spacing
        create_box(f"BLUEBOX|band_{i}",
            bx0-0.05, by0-0.05, z-0.08,
            bx1+0.05, by1+0.05, z+0.08,
            mat_mull, coll)

    # Vertical mullions on east face
    mull_spacing = config["bluebox_mullion_spacing"]
    n_mull = int((by1-by0)/mull_spacing)
    for j in range(1, n_mull):
        y = by0 + j*mull_spacing
        create_box(f"BLUEBOX|mull_E_{j}",
            bx1-0.02, y-0.1, bz0,
            bx1+0.12, y+0.1, bz1,
            mat_mull, coll)

    # Horizontal glazing slot on east face
    slot_z = bz0 + (bz1-bz0)*0.4
    slot_h = (bz1-bz0)*0.2
    create_box("BLUEBOX|glazing_slot",
        bx1-0.15, by0+1.5, slot_z,
        bx1+0.05, by1-1.5, slot_z+slot_h,
        mat_glass, coll)

    # Diagonal braces on N and S faces
    n_brace = config["bluebox_brace_count"]
    for face_tag, y_plane, y_offset in [("N", by1, 0.08), ("S", by0, -0.08)]:
        make_diagonal_beam(f"BLUEBOX|brace_{face_tag}_1",
            (bx0+0.5, y_plane+y_offset, bz0+0.5),
            (bx1-0.5, y_plane+y_offset, bz1-0.5),
            0.45, mat_steel, coll)
        make_diagonal_beam(f"BLUEBOX|brace_{face_tag}_2",
            (bx0+0.5, y_plane+y_offset, bz1-0.5),
            (bx1-0.5, y_plane+y_offset, bz0+0.5),
            0.45, mat_steel, coll)


def build_grand_theater(info, config, coll):
    """Fly tower cladding + ribs + cap + entry glazing for Grand Theater."""
    if not info["fly_bbox"]:
        print("  [grand] No fly tower found, skipping.")
        return
    fx0, fy0, fz0, fx1, fy1, fz1 = info["fly_bbox"]

    mat_panel = make_material(config["grand_tower_material"])
    mat_mull  = make_material("mullion")
    mat_glass = make_material("glass_frit")
    mat_roof  = make_material("roof")

    shell = create_box("GRAND|fly_tower_shell",
        fx0-0.1, fy0-0.1, fz0, fx1+0.1, fy1+0.1, fz1, mat_panel, coll)
    bevel_object(shell, config["grand_bevel_offset"])

    # Vertical ribs on N, S, E faces
    rib_w = 0.15
    rib_spacing = config["grand_tower_rib_spacing"]
    n = int((fx1-fx0)/rib_spacing)
    for i in range(1, n):
        x = fx0 + i*rib_spacing
        create_box(f"GRAND|rib_S_{i}", x-rib_w/2, fy0-0.15, fz0, x+rib_w/2, fy0+0.05, fz1, mat_mull, coll)
        create_box(f"GRAND|rib_N_{i}", x-rib_w/2, fy1-0.05, fz0, x+rib_w/2, fy1+0.15, fz1, mat_mull, coll)
    n2 = int((fy1-fy0)/rib_spacing)
    for j in range(1, n2):
        y = fy0 + j*rib_spacing
        create_box(f"GRAND|rib_E_{j}", fx1-0.05, y-rib_w/2, fz0, fx1+0.15, y+rib_w/2, fz1, mat_mull, coll)

    # Lantern cap
    ch = config["grand_tower_cap_height"]
    cap = create_box("GRAND|fly_tower_cap",
        fx0+1.5, fy0+1.5, fz1, fx1-1.5, fy1-1.5, fz1+ch, mat_roof, coll)
    bevel_object(cap, 0.3)

    # Entry glazing slot
    create_box("GRAND|entry_glazing",
        fx1-0.2, fy0+3, fz0+2, fx1+0.05, fy1-3, fz0+8,
        mat_glass, coll)


# -----------------------------------------------------------------------
# CURTAIN WALLS
# -----------------------------------------------------------------------

def build_curtain_wall(name, x0, y0, z0, x1, y1, z1,
                       grid_h, grid_v, mull_t, glass_t,
                       glass_mat, mull_mat, coll):
    """Curtain wall in a vertical plane (one dimension has zero extent)."""
    if abs(x1-x0) < 0.001:
        # YZ plane at x=x0
        x = x0
        create_box(f"{name}|glass", x-glass_t/2, y0, z0, x+glass_t/2, y1, z1, glass_mat, coll)
        n_h = int((z1-z0)/grid_v)
        for i in range(n_h+1):
            zi = z0 + i*grid_v
            if zi > z1+0.01: continue
            create_box(f"{name}|mH_{i}", x-mull_t, y0, zi-mull_t/2, x+mull_t, y1, zi+mull_t/2, mull_mat, coll)
        n_v = int((y1-y0)/grid_h)
        for j in range(n_v+1):
            yj = y0 + j*grid_h
            if yj > y1+0.01: continue
            create_box(f"{name}|mV_{j}", x-mull_t, yj-mull_t/2, z0, x+mull_t, yj+mull_t/2, z1, mull_mat, coll)
        create_box(f"{name}|mTop", x-mull_t, y0, z1-mull_t/2, x+mull_t, y1, z1+mull_t/2, mull_mat, coll)
        create_box(f"{name}|mBot", x-mull_t, y0, z0-mull_t/2, x+mull_t, y1, z0+mull_t/2, mull_mat, coll)
    else:
        # XZ plane at y=y0
        y = y0
        create_box(f"{name}|glass", x0, y-glass_t/2, z0, x1, y+glass_t/2, z1, glass_mat, coll)
        n_h = int((z1-z0)/grid_v)
        for i in range(n_h+1):
            zi = z0 + i*grid_v
            if zi > z1+0.01: continue
            create_box(f"{name}|mH_{i}", x0, y-mull_t, zi-mull_t/2, x1, y+mull_t, zi+mull_t/2, mull_mat, coll)
        n_v = int((x1-x0)/grid_h)
        for j in range(n_v+1):
            xj = x0 + j*grid_h
            if xj > x1+0.01: continue
            create_box(f"{name}|mV_{j}", xj-mull_t/2, y-mull_t, z0, xj+mull_t/2, y+mull_t, z1, mull_mat, coll)
        create_box(f"{name}|mTop", x0, y-mull_t, z1-mull_t/2, x1, y+mull_t, z1+mull_t/2, mull_mat, coll)
        create_box(f"{name}|mBot", x0, y-mull_t, z0-mull_t/2, x1, y+mull_t, z0+mull_t/2, mull_mat, coll)


# -----------------------------------------------------------------------
# MASSING-ADAPTIVE CURTAIN WALL GENERATION
# -----------------------------------------------------------------------

def build_adaptive_curtain_walls_from_massing(info, concert_hall, config, coll):
    """Generate curtain walls based on actual massing boundaries.
    
    Uses massing footprints to determine curtain wall extents for the
    concert hall volume, making them adaptive to the actual building form.
    """
    if not concert_hall or not info["cube_xy"] or not info["cube_z"]:
        return
    
    mat_glass = make_material(config["cw_cube_glass"])
    mat_mull = make_material("mullion")
    grid_h = config["cw_grid_h"]
    grid_v = config["cw_grid_v"]
    mull_t = config["cw_mullion_thickness"]
    glass_t = config["cw_glass_thickness"]
    
    # Extract cube extents from concert hall massing
    objs = concert_hall["concert_hall_objs"]
    if not objs:
        return
    
    # Get overall concert hall footprint
    all_x = [object_world_bbox(o)[0] if object_world_bbox(o) else 0 for o in objs]
    all_x += [object_world_bbox(o)[3] if object_world_bbox(o) else 0 for o in objs]
    all_y = [object_world_bbox(o)[1] if object_world_bbox(o) else 0 for o in objs]
    all_y += [object_world_bbox(o)[4] if object_world_bbox(o) else 0 for o in objs]
    all_z = [object_world_bbox(o)[2] if object_world_bbox(o) else 0 for o in objs]
    all_z += [object_world_bbox(o)[5] if object_world_bbox(o) else 0 for o in objs]
    
    if not all_x or not all_y or not all_z:
        return
    
    cx0, cx1 = min(all_x), max(all_x)
    cy0, cy1 = min(all_y), max(all_y)
    cz0, cz1 = min(all_z), max(all_z)
    
    # Generate curtain walls on 4 faces using massing-derived extents
    args = dict(grid_h=grid_h, grid_v=grid_v,
                mull_t=mull_t, glass_t=glass_t,
                glass_mat=mat_glass, mull_mat=mat_mull, coll=coll)
    
    # North face
    if cy1:
        build_curtain_wall(f"CUBE|CW_N|adaptive", cx0, cy1, cz0, cx1, cy1, cz1, **args)
    # South face
    if cy0:
        build_curtain_wall(f"CUBE|CW_S|adaptive", cx0, cy0, cz0, cx1, cy0, cz1, **args)
    # West face
    if cx0:
        build_curtain_wall(f"CUBE|CW_W|adaptive", cx0, cy0, cz0, cx0, cy1, cz1, **args)
    # East face
    if cx1:
        build_curtain_wall(f"CUBE|CW_E|adaptive", cx1, cy0, cz0, cx1, cy1, cz1, **args)
    
    print(f"    [CW] Generated adaptive curtain walls for concert hall "
          f"({cx0:.1f}..{cx1:.1f} x {cy0:.1f}..{cy1:.1f} x {cz0:.1f}..{cz1:.1f})")


def build_cube_curtain_walls(info, config, coll):
    if not info["cube_xy"] or not info["cube_z"]:
        return
    cx0, cy0, cx1, cy1 = info["cube_xy"]
    cz0, cz1 = info["cube_z"]
    mat_glass = make_material(config["cw_cube_glass"])
    mat_mull = make_material("mullion")
    args = dict(grid_h=config["cw_grid_h"], grid_v=config["cw_grid_v"],
                mull_t=config["cw_mullion_thickness"],
                glass_t=config["cw_glass_thickness"],
                glass_mat=mat_glass, mull_mat=mat_mull, coll=coll)
    build_curtain_wall("CUBE|CW_N", cx0, cy1, cz0, cx1, cy1, cz1, **args)
    build_curtain_wall("CUBE|CW_S", cx0, cy0, cz0, cx1, cy0, cz1, **args)
    build_curtain_wall("CUBE|CW_W", cx0, cy0, cz0, cx0, cy1, cz1, **args)
    # East cube face is subsumed by Blue Box

    # Corner fins
    mat_panel = make_material("alu_panel")
    for tag, x, y in [("SW", cx0, cy0), ("NW", cx0, cy1),
                       ("NE", cx1, cy1), ("SE", cx1, cy0)]:
        sx = -0.2 if x < 0 else +0.2
        sy = -0.2 if y < 0 else +0.2
        create_box(f"CUBE|corner_{tag}_fin",
            min(x, x+sx), min(y, y+sy), cz0,
            max(x, x+sx), max(y, y+sy), cz1,
            mat_panel, coll)


def build_tower_curtain_walls(info, config, coll):
    if not info["tower_xy"] or not info["tower_z"]:
        return
    tx0, ty0, tx1, ty1 = info["tower_xy"]
    tz0, tz1 = info["tower_z"]
    mat_glass = make_material(config["cw_tower_glass"])
    mat_mull = make_material("mullion")
    args = dict(grid_h=config["cw_grid_h"], grid_v=config["cw_grid_v"],
                mull_t=config["cw_mullion_thickness"],
                glass_t=config["cw_glass_thickness"],
                glass_mat=mat_glass, mull_mat=mat_mull, coll=coll)
    build_curtain_wall("TOWER|CW_N", tx0, ty1, tz0, tx1, ty1, tz1, **args)
    build_curtain_wall("TOWER|CW_S", tx0, ty0, tz0, tx1, ty0, tz1, **args)
    build_curtain_wall("TOWER|CW_W", tx0, ty0, tz0, tx0, ty1, tz1, **args)
    # East face: only where not blocked by NE shaft
    shaft_ne_y0 = None
    for s in info["shafts"]:
        bb = s["bbox"]
        cx = (bb[0]+bb[3])/2; cy = (bb[1]+bb[4])/2
        if cx > 0 and cy > 0:
            shaft_ne_y0 = bb[1]
            break
    if shaft_ne_y0 is not None and shaft_ne_y0 > ty0:
        build_curtain_wall("TOWER|CW_E", tx1, ty0, tz0, tx1, shaft_ne_y0, tz1, **args)
    else:
        build_curtain_wall("TOWER|CW_E", tx1, ty0, tz0, tx1, ty1, tz1, **args)


def build_lobby_curtain_walls(info, config, coll):
    if not info["ground_xy"] or not info["cube_z"]:
        return
    lx0, ly0, lx1, ly1 = info["ground_xy"]
    lz0 = info["levels"][info["sorted_levels"][0]]["z_min"] if info["ground_levels"] else 0
    lz0 = max(lz0, 0.0)
    lz1 = info["cube_z"][0]

    mat_glass = make_material(config["cw_lobby_glass"])
    mat_mull = make_material("mullion")
    mat_panel = make_material(config["canopy_material"])
    args = dict(grid_h=config["cw_grid_h"], grid_v=config["cw_grid_v"],
                mull_t=config["cw_mullion_thickness"],
                glass_t=config["cw_glass_thickness"],
                glass_mat=mat_glass, mull_mat=mat_mull, coll=coll)
    build_curtain_wall("LOBBY|CW_N", lx0, ly1, lz0, lx1, ly1, lz1, **args)
    build_curtain_wall("LOBBY|CW_S", lx0, ly0, lz0, lx1, ly0, lz1, **args)
    build_curtain_wall("LOBBY|CW_W", lx0, ly0, lz0, lx0, ly1, lz1, **args)
    build_curtain_wall("LOBBY|CW_E", lx1, ly0, lz0, lx1, ly1, lz1, **args)

    # Canopies
    cp = config["canopy_projection"]
    ct = config["canopy_thickness"]
    ch = config["canopy_height"]
    create_box("LOBBY|canopy_N", lx0-cp, ly1, ch, lx1+cp, ly1+cp, ch+ct, mat_panel, coll)
    create_box("LOBBY|canopy_S", lx0-cp, ly0-cp, ch, lx1+cp, ly0, ch+ct, mat_panel, coll)
    create_box("LOBBY|canopy_E", lx1, ly0-cp, ch, lx1+cp, ly1+cp, ch+ct, mat_panel, coll)
    create_box("LOBBY|canopy_W", lx0-cp, ly0-cp, ch, lx0, ly1+cp, ch+ct, mat_panel, coll)


# -----------------------------------------------------------------------
# ROOF
# -----------------------------------------------------------------------

def build_roof_elements(info, config, coll_roof, coll_cube, coll_tower):
    mat_roof = make_material(config["roof_slab_material"])
    mat_panel = make_material(config["parapet_material"])
    mat_glass = make_material("glass_frit")
    ph = config["parapet_height"]
    pt = config["parapet_thickness"]

    # Cube roof on portion not covered by fly tower
    if info["cube_xy"] and info["cube_z"] and info["fly_bbox"]:
        cx0, cy0, cx1, cy1 = info["cube_xy"]
        cz1 = info["cube_z"][1]
        fx0 = info["fly_bbox"][0]
        # Roof terrace on -X side (west of fly tower)
        create_box("CUBE|roof_W_terrace",
            cx0, cy0, cz1, fx0, cy1, cz1+0.3, mat_roof, coll_cube)
        # Parapets
        create_box("CUBE|parapet_N", cx0, cy1-pt, cz1+0.3, fx0, cy1, cz1+0.3+ph, mat_panel, coll_cube)
        create_box("CUBE|parapet_S", cx0, cy0, cz1+0.3, fx0, cy0+pt, cz1+0.3+ph, mat_panel, coll_cube)
        create_box("CUBE|parapet_W", cx0, cy0, cz1+0.3, cx0+pt, cy1, cz1+0.3+ph, mat_panel, coll_cube)

        # Mechanical units on cube terrace
        create_box("ROOF|mech_unit_1",
            cx0+6, cy0+6, cz1+0.3, cx0+16, cy0+14, cz1+3.5, mat_roof, coll_roof)
        create_box("ROOF|mech_unit_2",
            cx0+6, cy1-12, cz1+0.3, cx0+16, cy1-4, cz1+2.5, mat_roof, coll_roof)
        create_box("ROOF|stair_bulkhead_1",
            cx0+22, cy0+20, cz1+0.3, cx0+27, cy0+26, cz1+3.8, mat_panel, coll_roof)

    # Tower roof
    if info["tower_xy"] and info["tower_z"]:
        tx0, ty0, tx1, ty1 = info["tower_xy"]
        tz1 = info["tower_z"][1]
        create_box("TOWER|roof_slab", tx0, ty0, tz1, tx1, ty1, tz1+0.3, mat_roof, coll_roof)
        for tag, x0,y0,x1,y1 in [
            ("N", tx0, ty1-pt, tx1, ty1),
            ("S", tx0, ty0, tx1, ty0+pt),
            ("W", tx0, ty0, tx0+pt, ty1),
            ("E", tx1-pt, ty0, tx1, ty1),
        ]:
            create_box(f"TOWER|parapet_{tag}", x0, y0, tz1+0.3, x1, y1, tz1+0.3+ph, mat_panel, coll_tower)

        # Mechanical penthouse
        ph_h = config["penthouse_height"]
        create_box("TOWER|mech_penthouse",
            tx0+2.5, ty0+2.5, tz1+0.3, tx1-2.5, ty1-2.5, tz1+0.3+ph_h,
            mat_roof, coll_roof)
        # Skylight strip
        create_box("TOWER|skylight",
            tx0+4, ty0+4, tz1+0.3+ph_h, tx1-4, ty1-4, tz1+0.3+ph_h+0.2,
            mat_glass, coll_roof)


# -----------------------------------------------------------------------
# SHAFT CLADDING
# -----------------------------------------------------------------------

def build_shaft_cladding(info, config, coll):
    """Cap the top of each shaft and clad the exterior portions above cube."""
    mat_panel = make_material("alu_panel")
    if not info["cube_z"]:
        return
    cube_top = info["cube_z"][1]

    for s in info["shafts"]:
        bb = s["bbox"]
        x0, y0, z0, x1, y1, z1 = bb
        # Top cap
        tag = s["name"].split("|")[-1].replace(" ", "_")[:10]
        create_box(f"SHAFT|cap_{tag}",
            x0-0.1, y0-0.1, z1, x1+0.1, y1+0.1, z1+1.5,
            mat_panel, coll)
        # Above-cube cladding for shafts outside tower footprint
        if info["tower_xy"]:
            tx0, ty0, tx1, ty1 = info["tower_xy"]
            cx = (x0+x1)/2; cy = (y0+y1)/2
            outside_tower = cx < tx0 or cx > tx1 or cy < ty0 or cy > ty1
            if outside_tower:
                create_box(f"SHAFT|clad_{tag}",
                    x0-0.15, y0-0.15, cube_top-0.5,
                    x1+0.15, y1+0.15, z1,
                    mat_panel, coll)


# -----------------------------------------------------------------------
# SITE
# -----------------------------------------------------------------------

def build_site(info, config):
    if not config["build_site"]:
        return
    SITE = get_or_create_collection("SITE")
    SUNKEN = get_or_create_collection("SUNKEN_AMPH")
    ENTRY = get_or_create_collection("ENTRY_PLAZA")

    mat_paving = make_material("paving")
    mat_grass  = make_material("grass")
    mat_water  = make_material("water")
    mat_conc   = make_material("concrete")
    mat_roof   = make_material("roof")

    half = config["site_size"] / 2

    # Sunken amphitheater
    td = config["sunken_tier_drop"]
    tw = config["sunken_tier_width"]
    y_outer = config["sunken_y_outer"]
    n_tiers = config["sunken_tiers"]

    for i in range(n_tiers):
        z_top = -td * (i+1)
        inner_y = y_outer - (i+1)*tw
        outer_y = y_outer - i*tw
        half_w = 20.0 - i*1.5
        create_box(f"SUNKEN|step_{i+1}_tread",
            -half_w, inner_y, z_top-0.15, half_w, outer_y, z_top, mat_paving, SUNKEN)
        create_box(f"SUNKEN|step_{i+1}_riser",
            -half_w, inner_y, z_top-td, half_w, inner_y+0.2, z_top, mat_conc, SUNKEN)

    # Central pit floor
    pit_y_inner = y_outer - n_tiers*tw
    create_box("SUNKEN|pit_floor",
        -10, pit_y_inner, -n_tiers*td - 0.2,
         10, y_outer - (n_tiers-1)*tw, -n_tiers*td, mat_paving, SUNKEN)

    # Cut plaza slab to match sunken amphitheater
    plaza = bpy.data.objects.get("SLAB|L0_plaza")
    if plaza:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (y_outer + pit_y_inner)/2, -0.5))
        cutter = bpy.context.active_object
        cutter.scale = (40.1, abs(pit_y_inner - y_outer) + 0.1, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        boolean_difference(plaza, cutter)
        bpy.data.objects.remove(cutter, do_unlink=True)

    # Entry plaza (north)
    eph = config["entry_platform_height"]
    if info["ground_xy"]:
        gx0, gy0, gx1, gy1 = info["ground_xy"]
        create_box("ENTRY|north_platform", gx0-7, gy1, 0, gx1+7, gy1+13, eph, mat_paving, ENTRY)
        rise = config["entry_step_rise"]
        for i in range(config["entry_step_count"]):
            create_box(f"ENTRY|north_step_{i+1}",
                gx0-8, gy1+13 + i*0.4, rise*i,
                gx1+8, gy1+13 + (i+1)*0.4 + 0.4, rise*i + rise,
                mat_paving, ENTRY)

    # Grass strips
    if info["ground_xy"]:
        gx0, _, gx1, _ = info["ground_xy"]
        create_box("SITE|grass_strip_W", -half, -17, 0, gx0-10, 17, 0.25, mat_grass, SITE)
        create_box("SITE|grass_strip_E",  gx1+10, -17,  0, half,   17, 0.25, mat_grass, SITE)

    # Planters
    create_box("SITE|planter_SE_1", 22, -33, 0, 30, -26, 0.6, mat_roof, SITE)
    create_box("SITE|planter_NE_1", 22,  22, 0, 30,  32, 0.6, mat_roof, SITE)
    create_box("SITE|planter_grass_SE", 22.2, -32.8, 0.6, 29.8, -26.2, 0.75, mat_grass, SITE)
    create_box("SITE|planter_grass_NE", 22.2,  22.2, 0.6, 29.8,  31.8, 0.75, mat_grass, SITE)

    # Water pool
    wx = config["water_pool_x"]
    wy = config["water_pool_y"]
    create_box("SITE|water_pool", wx[0], wy[0], -0.15, wx[1], wy[1], 0, mat_water, SITE)

    # Curbs
    for tag, x0,y0,x1,y1 in [
        ("S", -half, -half,  half, -half+0.3),
        ("N", -half,  half-0.3, half, half),
        ("W", -half, -half, -half+0.3, half),
        ("E",  half-0.3, -half, half, half),
    ]:
        create_box(f"SITE|curb_{tag}", x0, y0, -0.1, x1, y1, 0.15, mat_conc, SITE)


# -----------------------------------------------------------------------
# CAMERAS AND LIGHTING
# -----------------------------------------------------------------------

def setup_cameras_and_lights(info, config):
    if not config["setup_cameras_lights"]:
        return

    # Sun primary
    bpy.ops.object.light_add(type='SUN', location=(60, -80, 90))
    sun = bpy.context.active_object
    sun.name = "SUN_primary"
    sun.data.energy = config["sun_energy_primary"]
    sun.data.color = (1.0, 0.96, 0.88)
    sun.data.angle = math.radians(3.0)
    sun.rotation_euler = (math.radians(55), math.radians(10), math.radians(35))

    # Sun fill
    bpy.ops.object.light_add(type='SUN', location=(-50, 60, 70))
    fill = bpy.context.active_object
    fill.name = "SUN_fill"
    fill.data.energy = config["sun_energy_fill"]
    fill.data.color = (0.80, 0.88, 1.0)
    fill.data.angle = math.radians(10.0)
    fill.rotation_euler = (math.radians(-50), math.radians(-15), math.radians(-140))

    # Sky world shader
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World"); bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg  = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = config["sky_type"]
        if hasattr(sky, "sun_direction"):
            sky.sun_direction = (0.3, -0.8, 0.5)
        if hasattr(sky, "turbidity"):
            sky.turbidity = 3.0
        if hasattr(sky, "ground_albedo"):
            sky.ground_albedo = 0.25
    except Exception as e:
        print(f"  [sky] {config['sky_type']} not available, using default")
    nt.links.new(sky.outputs[0], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], out.inputs["Surface"])
    bg.inputs["Strength"].default_value = 0.6

    # Target empty
    bpy.ops.object.empty_add(location=(0, -5, 26))
    target = bpy.context.active_object
    target.name = "CAM_target"

    # Cameras
    cameras = [
        ("CAM_hero_SE",   (95, -80, 40), 35),
        ("CAM_south_low", (20, -75, 8),  28),
        ("CAM_aerial",    (40, -40, 110),50),
    ]
    for name, loc, lens in cameras:
        bpy.ops.object.camera_add(location=loc)
        cam = bpy.context.active_object
        cam.name = name
        cam.data.lens = lens
        cam.data.clip_end = 500
        tc = cam.constraints.new('TRACK_TO')
        tc.target = target
        tc.track_axis = 'TRACK_NEGATIVE_Z'
        tc.up_axis = 'UP_Y'

    bpy.context.scene.camera = bpy.data.objects["CAM_hero_SE"]

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = config["render_engine"]
    scene.render.resolution_x = config["render_resolution"][0]
    scene.render.resolution_y = config["render_resolution"][1]
    scene.render.resolution_percentage = 100
    try:
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
    except Exception:
        pass


# -----------------------------------------------------------------------
# CLEANUP / ORGANIZATION
# -----------------------------------------------------------------------

def organize_massing_collections(config):
    """Move original massing into a hidden MASSING_REFERENCE collection."""
    if not config["hide_massing_reference"]:
        return
    MASS = get_or_create_collection("MASSING_REFERENCE")
    SHAFTS = get_or_create_collection("SHAFTS_ORIGINAL")

    moved_mass = 0; moved_shafts = 0
    for obj in list(bpy.data.objects):
        if obj.type != 'MESH':
            continue
        if _is_generated(obj.name):
            continue
        if is_shaft_object(obj):
            move_to_collection(obj, SHAFTS)
            moved_shafts += 1
        elif is_massing_object(obj):
            move_to_collection(obj, MASS)
            moved_mass += 1

    MASS.hide_viewport = True; MASS.hide_render = True
    SHAFTS.hide_viewport = True; SHAFTS.hide_render = True

    # Remove empty program collections
    for c in list(bpy.data.collections):
        if c.name in ["ARCHITECTURE", "SITE", "SUNKEN_AMPH", "ENTRY_PLAZA",
                      "MASSING_REFERENCE", "SHAFTS_ORIGINAL", "Collection"]:
            continue
        is_sub = any(c.name == child.name for child in bpy.data.collections["ARCHITECTURE"].children) \
                 if "ARCHITECTURE" in bpy.data.collections else False
        if is_sub:
            continue
        if len(c.objects) == 0 and len(c.children) == 0:
            try: bpy.data.collections.remove(c)
            except: pass

    print(f"  [organize] {moved_mass} massing + {moved_shafts} shaft objects hidden")


def clamp_to_site(config):
    """Ensure no architecture geometry extends beyond site boundary
       (except Globe which is allowed to cantilever)."""
    half = config["site_size"] / 2
    clamped = 0
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        if "GLOBE" in obj.name:
            continue
        if not _is_generated(obj.name):
            continue
        if obj.name.startswith(("SITE|", "ENTRY|", "SUNKEN|")):
            continue
        mw = obj.matrix_world; mwi = mw.inverted()
        changed = 0
        for v in obj.data.vertices:
            w = mw @ v.co
            nx = max(min(w.x, half), -half)
            ny = max(min(w.y, half), -half)
            if abs(nx-w.x) > 0.001 or abs(ny-w.y) > 0.001:
                v.co = mwi @ Vector((nx, ny, w.z))
                changed += 1
        if changed:
            obj.data.update()
            clamped += 1
    if clamped:
        print(f"  [clamp] Site-clamped {clamped} objects")


# ============================================================================
# CONCERT HALL STRUCTURE GENERATION (V2.5)
# ============================================================================

def get_concert_hall_bounds(concert_objs):
    """Extract bounding box from concert hall massing objects.
    
    Args:
        concert_objs: list of Blender mesh objects
        
    Returns:
        (min_x, max_x, min_y, max_y, min_z, max_z) in world coordinates
    """
    min_x = min_y = min_z =  1e9
    max_x = max_y = max_z = -1e9

    for obj in concert_objs:
        if obj.type != 'MESH':
            continue
        for v in obj.bound_box:
            world = obj.matrix_world @ Vector(v)
            min_x = min(min_x, world.x)
            max_x = max(max_x, world.x)
            min_y = min(min_y, world.y)
            max_y = max(max_y, world.y)
            min_z = min(min_z, world.z)
            max_z = max(max_z, world.z)

    return min_x, max_x, min_y, max_y, min_z, max_z


def build_concert_hall_structure(cx0, cx1, cy0, cy1, cz0, cz1, collection):
    """Generate aligned grid structure: columns, beams (X/Y), slabs.
    
    Creates a complete structural frame that:
    - Avoids piercing theater volumes (limited to concert hall bounds)
    - Aligns slabs to floor heights
    - Prevents beams from crossing slab surfaces
    
    Args:
        cx0, cx1, cy0, cy1, cz0, cz1: Concert hall bounds (world coords)
        collection: Blender collection to hold structure objects
    """
    if not ENABLE_FRAME:
        return
    
    dx = STRUCT_GRID_X
    dy = STRUCT_GRID_Y
    fh = FLOOR_HEIGHT
    col_size = COLUMN_SIZE
    beam_size = BEAM_SIZE
    slab_t = SLAB_T

    # Generate grid coordinates
    x_vals = []
    x = cx0
    while x <= cx1 + 0.01:
        x_vals.append(x)
        x += dx

    y_vals = []
    y = cy0
    while y <= cy1 + 0.01:
        y_vals.append(y)
        y += dy

    z_vals = []
    z = cz0
    while z <= cz1 + 0.01:
        z_vals.append(z)
        z += fh

    # =========================
    # COLUMNS
    # =========================
    col_count = 0
    for x in x_vals:
        for y in y_vals:
            height = cz1 - cz0
            
            bpy.ops.mesh.primitive_cube_add(size=1)
            col = bpy.context.active_object
            
            col.scale = (col_size / 2, col_size / 2, height / 2)
            col.location = (x, y, cz0 + height / 2)
            col.name = f"COLUMN|grid_{x:.1f}_{y:.1f}"
            
            # Assign material
            mat = make_material("concrete")
            if col.data.materials:
                col.data.materials[0] = mat
            else:
                col.data.materials.append(mat)
            
            collection.objects.link(col)
            bpy.context.scene.collection.objects.unlink(col)
            col_count += 1

    # =========================
    # BEAMS X direction
    # =========================
    beam_x_count = 0
    for z in z_vals:
        for y in y_vals:
            for i in range(len(x_vals) - 1):
                x0 = x_vals[i]
                x1 = x_vals[i + 1]
                length = x1 - x0

                bpy.ops.mesh.primitive_cube_add(size=1)
                beam = bpy.context.active_object

                beam.scale = (length / 2, beam_size / 2, beam_size / 2)
                beam.location = ((x0 + x1) / 2, y, z)
                beam.name = f"BEAM_X|z{z:.1f}_y{y:.1f}"

                mat = make_material("steel")
                if beam.data.materials:
                    beam.data.materials[0] = mat
                else:
                    beam.data.materials.append(mat)

                collection.objects.link(beam)
                bpy.context.scene.collection.objects.unlink(beam)
                beam_x_count += 1

    # =========================
    # BEAMS Y direction
    # =========================
    beam_y_count = 0
    for z in z_vals:
        for x in x_vals:
            for i in range(len(y_vals) - 1):
                y0 = y_vals[i]
                y1 = y_vals[i + 1]
                length = y1 - y0

                bpy.ops.mesh.primitive_cube_add(size=1)
                beam = bpy.context.active_object

                beam.scale = (beam_size / 2, length / 2, beam_size / 2)
                beam.location = (x, (y0 + y1) / 2, z)
                beam.name = f"BEAM_Y|z{z:.1f}_x{x:.1f}"

                mat = make_material("steel")
                if beam.data.materials:
                    beam.data.materials[0] = mat
                else:
                    beam.data.materials.append(mat)

                collection.objects.link(beam)
                bpy.context.scene.collection.objects.unlink(beam)
                beam_y_count += 1

    # =========================
    # SLABS (positioned to avoid piercing beams)
    # =========================
    slab_count = 0
    for z in z_vals:
        bpy.ops.mesh.primitive_cube_add(size=1)
        slab = bpy.context.active_object

        slab.scale = ((cx1 - cx0) / 2, (cy1 - cy0) / 2, slab_t / 2)
        slab.location = (
            (cx0 + cx1) / 2,
            (cy0 + cy1) / 2,
            z + beam_size / 2
        )
        slab.name = f"SLAB|z{z:.1f}"

        mat = make_material("slab")
        if slab.data.materials:
            slab.data.materials[0] = mat
        else:
            slab.data.materials.append(mat)

        collection.objects.link(slab)
        bpy.context.scene.collection.objects.unlink(slab)
        slab_count += 1

    print(f"  [frame] Concert hall structure: {col_count} columns, "
          f"{beam_x_count} X-beams, {beam_y_count} Y-beams, {slab_count} slabs")


def build_curtain_wall_with_structure(cx0, cx1, cy0, cy1, cz0, cz1, collection):
    """Generate curtain walls directly coupled to structural grid.
    
    Creates facade panels on 4 faces (N, S, E, W) aligned with structure.
    
    Args:
        cx0, cx1, cy0, cy1, cz0, cz1: Concert hall bounds (world coords)
        collection: Blender collection to hold facade objects
    """
    # Define four faces: (name, is_y_plane, position)
    faces = [
        ("CURTAIN_WALL|N", True, cy1),   # North: Y = cy1
        ("CURTAIN_WALL|S", True, cy0),   # South: Y = cy0
        ("CURTAIN_WALL|E", False, cx1),  # East:  X = cx1
        ("CURTAIN_WALL|W", False, cx0),  # West:  X = cx0
    ]

    cw_count = 0
    for face_name, is_y, pos in faces:
        bpy.ops.mesh.primitive_plane_add(size=1)
        wall = bpy.context.active_object

        if is_y:
            # Y-plane (N/S face)
            wall.scale = ((cx1 - cx0) / 2, 1, (cz1 - cz0) / 2)
            wall.location = ((cx0 + cx1) / 2, pos, (cz0 + cz1) / 2)
        else:
            # X-plane (E/W face)
            wall.scale = (1, (cy1 - cy0) / 2, (cz1 - cz0) / 2)
            wall.location = (pos, (cy0 + cy1) / 2, (cz0 + cz1) / 2)

        wall.name = face_name

        mat = make_material("glass_frit")
        if wall.data.materials:
            wall.data.materials[0] = mat
        else:
            wall.data.materials.append(mat)

        collection.objects.link(wall)
        bpy.context.scene.collection.objects.unlink(wall)
        cw_count += 1

    print(f"  [facade] Generated {cw_count} curtain wall faces")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def generate(config_override=None):
    """Main entry point. Generate the full TPAC architecture on current scene.
    
    Architecture is partitioned by functional area:
    - CONCERT_HALL: main structure (mega-columns, piloti, bracing, slabs)
    - GRAND_THEATER: +X fly tower and articulation
    - BLUE_BOX_THEATER: -X cantilever arm
    - GLOBE_PLAYHOUSE: -Z spherical volume
    
    Curtain walls adapt to massing-derived extents per functional area.

    Args:
        config_override: dict of key/value pairs to override DEFAULT_CONFIG.
    """
    config = dict(DEFAULT_CONFIG)
    if config_override:
        config.update(config_override)

    print("="*70)
    print("TPAC GENERATOR v2 — massing-adaptive generation")
    print("="*70)

    if config["clear_previous_output"]:
        print("[0] Clearing previous generator output...")
        clear_previous_output()

    print("[1] Analyzing massing...")
    info = analyze_massing()
    print(f"    Found {len(info['sorted_levels'])} levels, "
          f"{len(info['shafts'])} shafts")
    if info["cube_z"]:
        print(f"    Cube: z [{info['cube_z'][0]:.1f}..{info['cube_z'][1]:.1f}]")
    if info["tower_z"]:
        print(f"    Tower: z [{info['tower_z'][0]:.1f}..{info['tower_z'][1]:.1f}]")
    if info["fly_bbox"]:
        b = info["fly_bbox"]
        print(f"    Fly tower: x[{b[0]:.1f},{b[3]:.1f}] "
              f"y[{b[1]:.1f},{b[4]:.1f}] z[{b[2]:.1f},{b[5]:.1f}]")

    print("[1b] Classifying functional volumes...")
    concert_hall = identify_concert_hall_volume(info)
    print(f"    Concert hall: {len(concert_hall['concert_hall_objs'])} objects")
    print(f"    Grand Theater: {len(concert_hall['grand_objs'])} objects")
    print(f"    Blue Box: {len(concert_hall['blue_objs'])} objects")
    print(f"    Globe: {len(concert_hall['globe_objs'])} objects")

    print("[2] Creating collections & materials...")
    ARCH   = get_or_create_collection("ARCHITECTURE")
    STRUCT = get_or_create_collection("STRUCTURE", ARCH)
    ROOF   = get_or_create_collection("ROOF", ARCH)
    SLAB   = get_or_create_collection("SLABS", ARCH)
    GLOBE  = get_or_create_collection("GLOBE_THEATER", ARCH)
    BLUE   = get_or_create_collection("BLUE_BOX_THEATER", ARCH)
    GRAND  = get_or_create_collection("GRAND_THEATER", ARCH)
    CUBE   = get_or_create_collection("CENTRAL_CUBE", ARCH)
    TOWER  = get_or_create_collection("UPPER_TOWER", ARCH)
    LOBBY  = get_or_create_collection("LOBBY_FACADE", ARCH)
    SHAFT  = get_or_create_collection("SHAFT_CLADDING", ARCH)
    # Ensure all materials exist
    for key in MATERIAL_PALETTE:
        make_material(key)

    print("[3] Structural system (CONCERT HALL ONLY)...")
    # Main structural system only exists in concert hall area
    if concert_hall["concert_hall_objs"]:
        cx0, cx1, cy0, cy1, cz0, cz1 = get_concert_hall_bounds(
            concert_hall["concert_hall_objs"]
        )
        print(f"    → Concert Hall Bounds: X[{cx0:.1f}..{cx1:.1f}] "
              f"Y[{cy0:.1f}..{cy1:.1f}] Z[{cz0:.1f}..{cz1:.1f}]")
        
        if ENABLE_FRAME:
            build_concert_hall_structure(
                cx0, cx1, cy0, cy1, cz0, cz1,
                STRUCT
            )
        
        build_curtain_wall_with_structure(
            cx0, cx1, cy0, cy1, cz0, cz1,
            CUBE
        )
    else:
        print("    [WARNING] No concert hall massing found; skipping main structure")

    print("[4] Slabs...")
    build_slabs(info, config, SLAB)

    print("[5] Theater volumes (from massing classification)...")
    # Generate only theaters that have massing backing
    if concert_hall["globe_objs"]:
        build_globe_theater(info, config, GLOBE)
        print(f"    ✓ Globe with {len(concert_hall['globe_objs'])} massing objects")
    else:
        print("    - Globe: no massing found")
    
    if concert_hall["blue_objs"]:
        build_bluebox_theater(info, config, BLUE)
        print(f"    ✓ Blue Box with {len(concert_hall['blue_objs'])} massing objects")
    else:
        print("    - Blue Box: no massing found")
    
    if concert_hall["grand_objs"]:
        build_grand_theater(info, config, GRAND)
        print(f"    ✓ Grand Theater with {len(concert_hall['grand_objs'])} massing objects")
    else:
        print("    - Grand Theater: no massing found")

    print("[6] Additional curtain walls (theatrical arms)...")
    # Curtain walls for main cube already generated in step [3]
    # Keep existing walls as fallback for theatrical arms
    build_tower_curtain_walls(info, config, TOWER)
    build_lobby_curtain_walls(info, config, LOBBY)

    print("[7] Roof elements...")
    build_roof_elements(info, config, ROOF, CUBE, TOWER)
    build_shaft_cladding(info, config, SHAFT)

    print("[8] Cutting Globe through slabs...")
    cut_globe_through_slabs(info, config)

    print("[9] Site landscape...")
    build_site(info, config)

    print("[10] Cameras & lighting...")
    setup_cameras_and_lights(info, config)

    print("[11] Cleanup & organization...")
    organize_massing_collections(config)
    clamp_to_site(config)

    # Final summary
    total_mesh = sum(1 for o in bpy.data.objects if o.type == 'MESH')
    arch_mesh = 0
    if "ARCHITECTURE" in bpy.data.collections:
        arch_mesh = sum(len(sub.objects)
                        for sub in bpy.data.collections["ARCHITECTURE"].children)
    print("="*70)
    print(f"GENERATION COMPLETE")
    print(f"  Total meshes:         {total_mesh}")
    print(f"  Architecture meshes:  {arch_mesh}")
    print(f"  Collections:          {len(bpy.data.collections)}")
    print(f"  Materials:            {len(bpy.data.materials)}")
    print("="*70)


# ============================================================================
# SCRIPT ENTRY
# ============================================================================

if __name__ == "__main__":
    generate()
