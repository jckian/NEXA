"""
Blender53W53.py — 53 West 53rd Street (Jean Nouvel, 2019)
Program massing: B1 to L30, 30-floor tower

Run from Blender → Scripting workspace → Run Script.

Coordinate mapping (Three.js → Blender):
  Three.js X (east)   → Blender X
  Three.js Y (height) → Blender Z
  Three.js Z (depth)  → Blender Y

All dimensions in metres.
"""

import bpy
import bmesh
import math

# ─────────────────────────────────────────────────────────────────
# PARAMETERS  (match 53w53-program-diagram.html defaults)
# ─────────────────────────────────────────────────────────────────
SITE_W    = 40.0   # X
SITE_D    = 40.0   # Z (→ Blender Y)
FLOOR_H   = 4.5
TAPER     = 0.55   # footprint scale at TAPER_TOP
TAPER_TOP = 30
SLAB_GAP  = 0.12   # fraction of floor height left as gap
PAD       = 0.25   # padding between blocks
VIS_SHRINK = 0.94  # visual shrink per block (matches HTML)

SITE_CX = SITE_W / 2
SITE_CZ = SITE_D / 2  # "Z" in Three.js = "Y" in Blender

# ─────────────────────────────────────────────────────────────────
# COLORS  (sRGB hex → Blender linear RGBA)
# ─────────────────────────────────────────────────────────────────
def srgb_to_linear(c):
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

def hex_to_linear(h):
    h = h.lstrip('#')
    r, g, b = [int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)

TYPE_COLORS = {
    'museum_gallery':                  '#2C7873',
    'exhibition_hall':                 '#1d6b67',
    'museum_shop':                     '#4a9e99',
    'art_storage':                     '#2a5c58',
    'lobby':                           '#F5A623',
    'reception':                       '#e8941f',
    'restaurant':                      '#F5A623',
    'private_dining':                  '#d47e18',
    'lounge_bar':                      '#8B5CF6',
    'event_lounge':                    '#7C3AED',
    'residents_lounge':                '#9B59B6',
    'screening_room':                  '#7E57C2',
    'library':                         '#5C6BC0',
    'gym':                             '#E8735A',
    'pool':                            '#2196F3',
    'spa':                             '#E91E8C',
    'changing_room':                   '#c2185b',
    'residence_duplex':                '#4A90D9',
    'residence_corner':                '#357ABD',
    'residence_full_floor':            '#5BA3E8',
    'residence_penthouse':             '#6BB5F5',
    'kitchen':                         '#795548',
    'staff':                           '#607D8B',
    'it_support':                      '#455A64',
    'wine_cellar':                     '#6D4C41',
    'loading':                         '#424242',
    'service_corridor':                '#3a3a3a',
    'storage':                         '#3a3a4a',
    'mechanical':                      '#2a2a3a',
    'restroom':                        '#4a4a5a',
    'fire_stair_and_freight_elevator': '#1a1a22',
    'fire_stair_and_elevator_1':       '#252535',
    'fire_stair_and_elevator_2':       '#202030',
}
FALLBACK_COLOR = '#667788'

# Pre-convert to Blender linear for the material cache
_mat_cache = {}

def get_material(type_key):
    if type_key in _mat_cache:
        return _mat_cache[type_key]
    hex_col = TYPE_COLORS.get(type_key, FALLBACK_COLOR)
    mat = bpy.data.materials.new(name=f'53w53_{type_key}')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = hex_to_linear(hex_col)
        bsdf.inputs['Roughness'].default_value = 0.72
        bsdf.inputs['Metallic'].default_value  = 0.08
    _mat_cache[type_key] = mat
    return mat

# ─────────────────────────────────────────────────────────────────
# PROGRAM DATA  (B1 = -1 to L30, type key uses underscore)
# Format: (type_key, area_m2, level, category, w, d)
# ─────────────────────────────────────────────────────────────────
PROGRAM = [
    # ── B1 ──────────────────────────────────────────────────────
    ('loading',                         300, -1, 'private',     15, 20),
    ('storage',                         400, -1, 'private',     20, 20),
    ('mechanical',                      350, -1, 'private',     15, 24),
    ('wine_cellar',                      80, -1, 'private',      8, 10),
    ('service_corridor',                150, -1, 'private',      6, 25),
    ('restroom',                         80, -1, 'public',       8, 10),
    ('fire_stair_and_freight_elevator', 200, -1, 'circulation', 10, 20),
    ('fire_stair_and_elevator_1',       150, -1, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130, -1, 'circulation', 10, 13),

    # ── L0 ──────────────────────────────────────────────────────
    ('lobby',                           600,  0, 'public',      20, 30),
    ('reception',                       100,  0, 'public',      10, 10),
    ('museum_gallery',                  500,  0, 'public',      20, 25),
    ('restaurant',                      400,  0, 'public',      16, 25),
    ('museum_shop',                     150,  0, 'public',      10, 15),
    ('restroom',                        168,  0, 'public',      12, 14),
    ('loading',                         120,  0, 'private',      8, 15),
    ('storage',                          80,  0, 'private',      8, 10),
    ('mechanical',                      100,  0, 'private',      8, 13),
    ('fire_stair_and_freight_elevator', 200,  0, 'circulation', 10, 20),
    ('fire_stair_and_elevator_1',       150,  0, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130,  0, 'circulation', 10, 13),

    # ── L1 ──────────────────────────────────────────────────────
    ('museum_gallery',                 1000,  1, 'public',      25, 40),
    ('exhibition_hall',                 350,  1, 'public',      14, 25),
    ('restroom',                        168,  1, 'public',      12, 14),
    ('art_storage',                     120,  1, 'private',      8, 15),
    ('staff',                            60,  1, 'private',      6, 10),
    ('it_support',                       40,  1, 'private',      5,  8),
    ('fire_stair_and_freight_elevator', 200,  1, 'circulation', 10, 20),
    ('fire_stair_and_elevator_1',       150,  1, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130,  1, 'circulation', 10, 13),

    # ── L2 ──────────────────────────────────────────────────────
    ('museum_gallery',                 1000,  2, 'public',      25, 40),
    ('exhibition_hall',                 350,  2, 'public',      14, 25),
    ('restroom',                        168,  2, 'public',      12, 14),
    ('art_storage',                     120,  2, 'private',      8, 15),
    ('staff',                            60,  2, 'private',      6, 10),
    ('it_support',                       40,  2, 'private',      5,  8),
    ('fire_stair_and_freight_elevator', 200,  2, 'circulation', 10, 20),
    ('fire_stair_and_elevator_1',       150,  2, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130,  2, 'circulation', 10, 13),

    # ── L3 ──────────────────────────────────────────────────────
    ('restaurant',                      600,  3, 'public',      20, 30),
    ('private_dining',                  150,  3, 'public',      10, 15),
    ('lounge_bar',                      120,  3, 'public',      10, 12),
    ('museum_shop',                     120,  3, 'public',      10, 12),
    ('restroom',                        168,  3, 'public',      12, 14),
    ('kitchen',                         120,  3, 'private',     10, 12),
    ('storage',                          80,  3, 'private',      8, 10),
    ('fire_stair_and_freight_elevator', 200,  3, 'circulation', 10, 20),
    ('fire_stair_and_elevator_1',       150,  3, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130,  3, 'circulation', 10, 13),
]

# ── L4–L11  Lower Residential ────────────────────────────────────
for _lvl in range(4, 12):
    PROGRAM += [
        ('residence_duplex',                280, _lvl, 'private',     14, 20),
        ('residence_corner',                280, _lvl, 'private',     14, 20),
        ('restroom',                         60, _lvl, 'public',       6, 10),
        ('storage',                          40, _lvl, 'private',      5,  8),
        ('fire_stair_and_freight_elevator', 170, _lvl, 'circulation', 10, 17),
        ('fire_stair_and_elevator_1',       150, _lvl, 'circulation', 10, 15),
        ('fire_stair_and_elevator_2',       130, _lvl, 'circulation', 10, 13),
    ]

# ── L12  Fitness ─────────────────────────────────────────────────
PROGRAM += [
    ('gym',                             260, 12, 'private',     16, 16),
    ('changing_room',                    80, 12, 'private',      8, 10),
    ('storage',                          40, 12, 'private',      5,  8),
    ('restroom',                         80, 12, 'public',       8, 10),
    ('staff',                            40, 12, 'private',      5,  8),
    ('fire_stair_and_freight_elevator', 170, 12, 'circulation', 10, 17),
    ('fire_stair_and_elevator_1',       150, 12, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130, 12, 'circulation', 10, 13),
]

# ── L13  Aquatics + Spa ──────────────────────────────────────────
PROGRAM += [
    ('pool',                            200, 13, 'private',     14, 14),
    ('spa',                             120, 13, 'private',     10, 12),
    ('changing_room',                    80, 13, 'private',      8, 10),
    ('restroom',                         80, 13, 'public',       8, 10),
    ('storage',                          30, 13, 'private',      5,  6),
    ('fire_stair_and_freight_elevator', 170, 13, 'circulation', 10, 17),
    ('fire_stair_and_elevator_1',       150, 13, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130, 13, 'circulation', 10, 13),
]

# ── L14  Residents Lounge + Private Dining ───────────────────────
PROGRAM += [
    ('residents_lounge',                200, 14, 'public',      14, 14),
    ('private_dining',                  120, 14, 'public',      10, 12),
    ('lounge_bar',                       80, 14, 'public',       8, 10),
    ('restroom',                         80, 14, 'public',       8, 10),
    ('kitchen',                          60, 14, 'private',      6, 10),
    ('fire_stair_and_freight_elevator', 170, 14, 'circulation', 10, 17),
    ('fire_stair_and_elevator_1',       150, 14, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130, 14, 'circulation', 10, 13),
]

# ── L15  Media + Library ─────────────────────────────────────────
PROGRAM += [
    ('screening_room',                  180, 15, 'public',      12, 15),
    ('library',                         120, 15, 'public',      10, 12),
    ('residents_lounge',                100, 15, 'public',      10, 10),
    ('restroom',                         80, 15, 'public',       8, 10),
    ('it_support',                       40, 15, 'private',      5,  8),
    ('fire_stair_and_freight_elevator', 170, 15, 'circulation', 10, 17),
    ('fire_stair_and_elevator_1',       150, 15, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130, 15, 'circulation', 10, 13),
]

# ── L16  Amenity Sky Terrace ─────────────────────────────────────
PROGRAM += [
    ('event_lounge',                    200, 16, 'public',      14, 14),
    ('residents_lounge',                120, 16, 'public',      10, 12),
    ('lounge_bar',                       80, 16, 'public',       8, 10),
    ('restroom',                         80, 16, 'public',       8, 10),
    ('storage',                          30, 16, 'private',      5,  6),
    ('fire_stair_and_freight_elevator', 170, 16, 'circulation', 10, 17),
    ('fire_stair_and_elevator_1',       150, 16, 'circulation', 10, 15),
    ('fire_stair_and_elevator_2',       130, 16, 'circulation', 10, 13),
]

# ── L17–L25  Mid Residential A ───────────────────────────────────
for _lvl in range(17, 26):
    PROGRAM += [
        ('residence_corner',                200, _lvl, 'private',     13, 15),
        ('residence_corner',                130, _lvl, 'private',     10, 13),
        ('restroom',                         60, _lvl, 'public',       6, 10),
        ('storage',                          30, _lvl, 'private',      5,  6),
        ('fire_stair_and_freight_elevator', 170, _lvl, 'circulation', 10, 17),
        ('fire_stair_and_elevator_1',       150, _lvl, 'circulation', 10, 15),
        ('fire_stair_and_elevator_2',       130, _lvl, 'circulation', 10, 13),
    ]

# ── L26–L30  Mid Residential B ───────────────────────────────────
for _lvl in range(26, 31):
    PROGRAM += [
        ('residence_corner',                150, _lvl, 'private',     12, 13),
        ('residence_corner',                100, _lvl, 'private',     10, 10),
        ('restroom',                         50, _lvl, 'public',       5, 10),
        ('fire_stair_and_freight_elevator', 170, _lvl, 'circulation', 10, 17),
        ('fire_stair_and_elevator_1',       150, _lvl, 'circulation', 10, 15),
        ('fire_stair_and_elevator_2',       130, _lvl, 'circulation', 10, 13),
    ]

# ─────────────────────────────────────────────────────────────────
# CORE TYPES
# ─────────────────────────────────────────────────────────────────
CORE_TYPES = {
    'fire_stair_and_freight_elevator',
    'fire_stair_and_elevator_1',
    'fire_stair_and_elevator_2',
}

# ─────────────────────────────────────────────────────────────────
# CORE REDUCTION RULE  (mirrors HTML getActiveCores())
#
#   level < 0          → all 3 cores (basement: full BOH service)
#   t ≤ 0.55 * TAPER_TOP → all 3 cores
#   t ≤ 0.85 * TAPER_TOP → drop freight elevator (terminates at mid-rise)
#   t >  0.85 * TAPER_TOP → single main elevator only
# ─────────────────────────────────────────────────────────────────
def get_active_cores(level):
    if level < 0:
        return set(CORE_TYPES)
    t = level / max(1, TAPER_TOP)
    if t <= 0.55:
        return {'fire_stair_and_freight_elevator',
                'fire_stair_and_elevator_1',
                'fire_stair_and_elevator_2'}
    elif t <= 0.85:
        return {'fire_stair_and_elevator_1',
                'fire_stair_and_elevator_2'}
    else:
        return {'fire_stair_and_elevator_1'}

# ─────────────────────────────────────────────────────────────────
# FLOOR FOOTPRINT  (mirrors Three.js floorFootprint())
# Returns (cx, cz, hw, hd)  — all in Three.js space
# ─────────────────────────────────────────────────────────────────
def floor_footprint(level):
    if level < 0:
        return (SITE_CX, SITE_CZ, SITE_W / 2, SITE_D / 2)
    taper_start = min(4, TAPER_TOP)
    if level <= taper_start - 1:
        return (SITE_CX, SITE_CZ, SITE_W / 2, SITE_D / 2)
    span  = max(1, TAPER_TOP - taper_start)
    t     = min(1.0, (level - taper_start) / span)
    scale = 1.0 - t * (1.0 - TAPER)
    hw    = (SITE_W / 2) * scale
    hd    = (SITE_D / 2) * scale
    return (SITE_CX, SITE_CZ, hw, hd)

# ─────────────────────────────────────────────────────────────────
# LAYOUT  (mirrors Three.js layoutFloor())
# Returns list of dicts: {type, area, category, w, d, px, pz, pw, pd}
# px/pz are Three.js X/Z block centres; pw/pd are final rendered dims
# ─────────────────────────────────────────────────────────────────
def layout_floor(entries, level):
    cx, cz, hw, hd = floor_footprint(level)

    active_cores  = get_active_cores(level)
    core_entries  = [e for e in entries if e[0] in active_cores]
    other_entries = [e for e in entries if e[0] not in CORE_TYPES]

    placed = []

    # ── Core cluster ─────────────────────────────────────────────
    sorted_cores = sorted(core_entries, key=lambda e: -e[1])  # largest area first
    clamped = [(e, max(1.0, min(e[4], hw * 0.8)), max(1.0, min(e[5], hd * 1.8)))
               for e in sorted_cores]

    total_core_w = sum(c[1] for c in clamped) + PAD * max(0, len(clamped) - 1)
    cur_core_x   = cx - total_core_w / 2

    cl_x0 = cx - total_core_w / 2
    cl_x1 = cx + total_core_w / 2
    cl_z0 = cz
    cl_z1 = cz

    for e, cw, cd in clamped:
        px = cur_core_x + cw / 2
        pz = cz
        placed.append({'type': e[0], 'area': e[1], 'level': e[2], 'category': e[3],
                        'px': px, 'pz': pz, 'pw': cw, 'pd': cd})
        cl_z0 = min(cl_z0, pz - cd / 2)
        cl_z1 = max(cl_z1, pz + cd / 2)
        cur_core_x += cw + PAD

    if not other_entries:
        return placed

    min_x = cx - hw
    max_x = cx + hw
    min_z = cz - hd
    max_z = cz + hd

    # Four zones around core cluster
    raw_zones = [
        (min_x,        cl_x0 - PAD, min_z,        max_z),         # West
        (cl_x1 + PAD,  max_x,       min_z,        max_z),         # East
        (cl_x0 - PAD,  cl_x1 + PAD, min_z,        cl_z0 - PAD),  # North
        (cl_x0 - PAD,  cl_x1 + PAD, cl_z1 + PAD,  max_z),        # South
    ]
    zones = [z for z in raw_zones if (z[1] - z[0]) > 1 and (z[3] - z[2]) > 1]
    zones.sort(key=lambda z: -((z[1] - z[0]) * (z[3] - z[2])))

    if not zones:
        for e in other_entries:
            placed.append({'type': e[0], 'area': e[1], 'level': e[2], 'category': e[3],
                            'px': cx, 'pz': cz,
                            'pw': min(e[4], hw * 2 - 0.2),
                            'pd': min(e[5], hd * 2 - 0.2)})
        return placed

    sorted_others = sorted(other_entries, key=lambda e: -e[1])
    state = [{'curX': z[0], 'curZ': z[2], 'colMaxX': z[0]} for z in zones]

    for e in sorted_others:
        was_placed = False
        for zi, (zone, st) in enumerate(zip(zones, state)):
            zone_w = zone[1] - zone[0]
            zone_d = zone[3] - zone[2]

            bw = min(e[4], zone_w)
            bd = min(e[5], zone_d)
            if bw > 0 and bd / bw > 5: bd = bw * 5
            if bd > 0 and bw / bd > 5: bw = bd * 5
            bw = max(bw, 1.0)
            bd = max(bd, 1.0)

            if st['curX'] + bw > zone[1] + 0.01:
                continue  # zone exhausted

            if st['curZ'] + bd > zone[3] + 0.01:
                # Advance column
                st['curX'] = st['colMaxX'] + PAD
                st['curZ'] = zone[2]
                if st['curX'] + bw > zone[1] + 0.01:
                    continue

            px = st['curX'] + bw / 2
            pz = st['curZ'] + bd / 2
            placed.append({'type': e[0], 'area': e[1], 'level': e[2], 'category': e[3],
                            'px': px, 'pz': pz, 'pw': bw, 'pd': bd})
            st['curZ'] += bd + PAD
            if st['curX'] + bw > st['colMaxX']:
                st['colMaxX'] = st['curX'] + bw
            was_placed = True
            break

        if not was_placed:
            placed.append({'type': e[0], 'area': e[1], 'level': e[2], 'category': e[3],
                            'px': cx, 'pz': cz,
                            'pw': min(e[4], hw),
                            'pd': min(e[5], hd)})

    return placed

# ─────────────────────────────────────────────────────────────────
# BLENDER MESH HELPERS
# ─────────────────────────────────────────────────────────────────
def make_box(name, bx, by, bz, sx, sy, sz, mat):
    """
    Create a box mesh at Blender position (bx, by, bz) with scale (sx, sy, sz).
    Coordinate mapping applied: Three.js (px, y_base+bh/2, pz) → Blender (px, pz, y_base+bh/2)
    """
    mesh = bpy.data.meshes.new(name)
    bm   = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = (bx, by, bz)
    obj.scale    = (sx, sy, sz)

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return obj

# ─────────────────────────────────────────────────────────────────
# CLEAR + REBUILD
# ─────────────────────────────────────────────────────────────────
def clear_collection(name):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
        # Remove all objects
        for obj in list(col.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)

def ensure_collection(name, parent=None):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

# ─────────────────────────────────────────────────────────────────
# MAIN BUILD
# ─────────────────────────────────────────────────────────────────
def build():
    # Clear existing 53W53 collection
    clear_collection('53W53')
    _mat_cache.clear()

    root_col = ensure_collection('53W53')

    # Group by floor
    by_floor = {}
    for entry in PROGRAM:
        lvl = entry[2]
        if lvl > TAPER_TOP:
            continue
        if lvl not in by_floor:
            by_floor[lvl] = []
        by_floor[lvl].append(entry)

    slab_h = FLOOR_H * (1.0 - SLAB_GAP)

    for level in sorted(by_floor.keys()):
        entries  = by_floor[level]
        y_base   = level * FLOOR_H    # Three.js Y = Blender Z
        floor_name = f'B1' if level == -1 else f'F{level:02d}'
        floor_col  = ensure_collection(floor_name, parent=root_col)

        layout = layout_floor(entries, level)

        for item in layout:
            type_key = item['type']
            is_mech  = type_key == 'mechanical'
            bh       = slab_h * 0.7 if is_mech else slab_h

            # Visual shrink
            bw = item['pw'] * VIS_SHRINK
            bd = item['pd'] * VIS_SHRINK

            # Three.js centre position
            tj_x = item['px']
            tj_y = y_base + bh / 2
            tj_z = item['pz']

            # → Blender position (X, Y, Z) = (tj_x, tj_z, tj_y)
            bl_x = tj_x
            bl_y = tj_z
            bl_z = tj_y

            # Scale: (width_X, depth_Y, height_Z)
            sx = bw
            sy = bd
            sz = bh

            mat  = get_material(type_key)
            name = f'{floor_name}_{type_key}'
            obj  = make_box(name, bl_x, bl_y, bl_z, sx, sy, sz, mat)
            floor_col.objects.link(obj)

    print(f'53W53: built {len(by_floor)} floors, B1 to L{TAPER_TOP}.')

build()
