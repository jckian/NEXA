"""
====================================================================
 PARAMETRIC BUILDING PROGRAM MASSING
====================================================================
 Run inside Blender (Scripting tab > New > paste > Run),
 or:  blender --background --python parametric_massing.py

 The massing is driven by the PROGRAM AREA inputs in the CONFIG
 block below. Change the numbers, re-run, and the volumes resize.

 What is parametric:
   - Floor plate (width x depth) derived from bay grid
   - Floor heights per program
   - Core size + position (fixed full height)
   - Each residential UNIT carries a TARGET AREA (sqm).
     Units are placed on perimeter bands; the script sizes each
     unit's frontage = target_area / band_depth so the volume's
     footprint matches the requested area, then snaps to grid.
   - Per-level program stacks are data-driven lists you can edit.

 Output: program massing only (no walls / structure / facade).
 Color by program category.
====================================================================
"""

import bpy
import json

# ====================================================================
# CONFIG  --  EDIT THESE INPUTS
# ====================================================================

BAY = 4.8                 # structural bay (m)
BAYS_X = 6                # -> width  = 28.8 m
BAYS_Y = 4                # -> depth  = 19.2 m

CORE_W = 8.0              # core size X (m)
CORE_D = 10.0             # core size Y (m)

SNAP_TO_GRID = True       # snap unit frontages to BAY multiples
GRID_SNAP_STEP = BAY / 2  # snap resolution (set to BAY for full-bay)

# ---- Floor heights per program category (m) ----
FLOOR_H = {
    "retail":  5.0,
    "amenity": 4.0,
    "resi":    3.3,
    "loft":    3.3,
    "roof":    4.0,
}

# ---- PROGRAM AREA INPUTS (sqm per unit type) ----
# These drive the footprint of each residential / loft unit.
UNIT_AREA = {
    "studio":  46.0,
    "onebr":   69.0,
    "twobr":   92.0,
    "threebr": 138.0,
    "loft":    138.0,
}

# ---- PROGRAM STACK ----
# For each level: program type + the list of units placed on it.
# 'full' levels are open-plan slabs (retail / amenity).
# 'units' levels list (unit_type, side) pairs. side in N/S/E/W.
# You can freely edit counts/types here; areas come from UNIT_AREA.
def resi(units):
    return {"kind": "units", "units": units}

STACK = {
    1:  {"kind": "full", "prog": "retail",  "name": "RETAIL_L01"},
    2:  {"kind": "full", "prog": "retail",  "name": "RETAIL_L02"},
    3:  {"kind": "full", "prog": "amenity", "name": "AMENITY_L03"},

    # L04-06 : 4 studio + 2 1BR + 1 2BR
    4:  resi([("studio","N"),("studio","N"),("studio","N"),("studio","N"),
              ("onebr","S"),("onebr","S"),("twobr","E")]),
    5:  "copy:4",
    6:  "copy:4",

    # L07-10 : 2 1BR + 2 2BR + 1 3BR
    7:  resi([("onebr","N"),("onebr","N"),
              ("twobr","S"),("twobr","S"),("threebr","E")]),
    8:  "copy:7", 9: "copy:7", 10: "copy:7",

    # L11-13 : 2 2BR + 2 3BR
    11: resi([("twobr","N"),("twobr","N"),
              ("threebr","S"),("threebr","E")]),
    12: "copy:11", 13: "copy:11",

    # L14-15 : 3 lofts (larger continuous volumes)
    14: resi([("loft","N"),("loft","S"),("loft","E")]),
    15: "copy:14",
}

ROOF_PROGRAM = ["farm", "greenhouse", "terrace", "solar_canopy"]

# ---- Colors per program category (RGBA) ----
COLORS = {
    "retail":  (0.90, 0.35, 0.20, 1),
    "amenity": (0.95, 0.75, 0.15, 1),
    "studio":  (0.20, 0.60, 0.85, 1),
    "onebr":   (0.25, 0.75, 0.65, 1),
    "twobr":   (0.35, 0.70, 0.35, 1),
    "threebr": (0.55, 0.45, 0.80, 1),
    "loft":    (0.85, 0.45, 0.65, 1),
    "roof":    (0.40, 0.80, 0.40, 1),
    "core":    (0.45, 0.45, 0.50, 1),
}

# Unit type -> short tag used in object names
NAME_TAG = {
    "studio": "STUDIO", "onebr": "ONEBR", "twobr": "TWOBR",
    "threebr": "THREEBR", "loft": "LOFT",
}

# ====================================================================
# DERIVED DIMENSIONS
# ====================================================================
W = BAY * BAYS_X
D = BAY * BAYS_Y
XE, YE = W / 2.0, D / 2.0          # building half-extents
XC, YC = CORE_W / 2.0, CORE_D / 2.0  # core half-extents

# Perimeter band depths
BAND_DEPTH_NS = YE - YC   # depth of north/south bands (along Y)
BAND_DEPTH_EW = XE - XC   # depth of east/west bands  (along X)

# ====================================================================
# HELPERS
# ====================================================================
def clear_scene():
    for o in list(bpy.data.objects):
        if o.type not in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(o, do_unlink=True)
    # remove our old materials so colors refresh
    for m in list(bpy.data.materials):
        if m.name.startswith("PROG_"):
            bpy.data.materials.remove(m)

def get_material(cat):
    name = "PROG_" + cat
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = COLORS[cat]
        m.diffuse_color = COLORS[cat]
    return m

def box(name, sx, sy, sz, cx, cy, z0, cat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, z0 + sz / 2.0))
    o = bpy.context.active_object
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    o.name = name
    o.data.materials.append(get_material(cat))
    return o

def snap(v):
    if not SNAP_TO_GRID:
        return v
    return round(v / GRID_SNAP_STEP) * GRID_SNAP_STEP

def level_height(level, entry):
    if isinstance(entry, dict) and entry.get("kind") == "full":
        return FLOOR_H[entry["prog"]]
    if 14 <= level <= 15:
        return FLOOR_H["loft"]
    return FLOOR_H["resi"]

def resolve(entry):
    """Resolve 'copy:N' references to the real entry."""
    if isinstance(entry, str) and entry.startswith("copy:"):
        return STACK[int(entry.split(":")[1])]
    return entry

# ----- Place units along one side, sized by target AREA -----
def place_side_units(level, side, unit_list, h, z0):
    """unit_list: list of unit_type strings on this side.
       Each unit footprint = target_area, frontage = area/band_depth."""
    if not unit_list:
        return
    counter = {}
    if side in ("N", "S"):
        band_depth = BAND_DEPTH_NS
        # available frontage along X is full width W
        # frontage per unit from area, snapped
        widths = [snap(UNIT_AREA[u] / band_depth) for u in unit_list]
        total = sum(widths)
        # normalize to fit W (keeps grid alignment proportionally)
        scale = W / total if total > 0 else 1.0
        widths = [w * scale for w in widths]
        ysign = 1 if side == "N" else -1
        cy = ysign * (YC + band_depth / 2.0)
        x = -W / 2.0
        for u, w in zip(unit_list, widths):
            cx = x + w / 2.0
            tag = NAME_TAG[u]
            counter[tag] = counter.get(tag, 0) + 1
            suffix = chr(64 + counter[tag])  # A,B,C...
            box(f"{tag}_L{level:02d}_{suffix}", w, band_depth, h, cx, cy, z0, u)
            x += w
    else:  # E / W -- units run along Y over the core depth
        band_depth = BAND_DEPTH_EW
        heights = [snap(UNIT_AREA[u] / band_depth) for u in unit_list]
        total = sum(heights)
        scale = CORE_D / total if total > 0 else 1.0
        heights = [hh * scale for hh in heights]
        xsign = 1 if side == "E" else -1
        cx = xsign * (XC + band_depth / 2.0)
        y = -CORE_D / 2.0
        for u, hh in zip(unit_list, heights):
            cy = y + hh / 2.0
            tag = NAME_TAG[u]
            counter[tag] = counter.get(tag, 0) + 1
            suffix = chr(64 + counter[tag])
            box(f"{tag}_L{level:02d}_{suffix}", band_depth, hh, h, cx, cy, z0, u)
            y += hh

# ====================================================================
# BUILD
# ====================================================================
def build():
    clear_scene()

    # ---- Z stack ----
    z_base = {}
    z = 0.0
    for L in range(1, 16):
        entry = resolve(STACK[L])
        h = level_height(L, entry)
        z_base[L] = z
        z += h
    roof_z = z
    total_h = roof_z + FLOOR_H["roof"]

    # ---- CORE (continuous, full height) ----
    box("CORE_MAIN", CORE_W, CORE_D, total_h, 0, 0, 0.0, "core")

    # ---- Levels ----
    for L in range(1, 16):
        entry = resolve(STACK[L])
        h = level_height(L, entry)
        z0 = z_base[L]
        if entry["kind"] == "full":
            box(entry["name"], W, D, h, 0, 0, z0, entry["prog"])
        else:
            # group this level's units by side
            by_side = {"N": [], "S": [], "E": [], "W": []}
            for utype, side in entry["units"]:
                by_side[side].append(utype)
            for side, ulist in by_side.items():
                place_side_units(L, side, ulist, h, z0)

    # ---- ROOF program ----
    rh = FLOOR_H["roof"]
    if "farm" in ROOF_PROGRAM:
        box("ROOF_FARM", W, D, 0.6, 0, 0, roof_z, "roof")
    if "greenhouse" in ROOF_PROGRAM:
        box("ROOF_GREENHOUSE", W*0.4, D*0.45, rh*0.9, -W*0.28, D*0.25, roof_z+0.6, "roof")
    if "terrace" in ROOF_PROGRAM:
        box("ROOF_TERRACE", W*0.45, D*0.4, 0.4, W*0.25, -D*0.28, roof_z+0.6, "roof")
    if "solar_canopy" in ROOF_PROGRAM:
        box("ROOF_SOLAR_CANOPY", W*0.95, D*0.95, 0.3, 0, 0, roof_z+rh, "roof")

    # ---- Camera / light framing (optional) ----
    cam = bpy.data.objects.get("Camera")
    if cam:
        import mathutils
        cam.location = (60, -70, 55)
        d = mathutils.Vector((0, 0, total_h*0.5)) - cam.location
        cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    lt = bpy.data.objects.get("Light")
    if lt and lt.data.type == 'SUN':
        lt.data.energy = 3

    print("Built massing: plate %.1f x %.1f m, %d floors, total height %.2f m"
          % (W, D, 15, total_h))
    print("Mesh objects:", len([o for o in bpy.data.objects if o.type == 'MESH']))


if __name__ == "__main__":
    build()
