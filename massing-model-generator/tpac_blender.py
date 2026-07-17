"""
TPAC Program Massing — Blender Python Script
OMA Taipei Performing Arts Center
Generated from tpac-program-diagram.html (latest version)

HOW TO USE:
  1. Open Blender (3.x or later)
  2. Open the Scripting workspace
  3. Paste / open this file
  4. Click "Run Script"

Includes:
  - Aspect ratio subdivision (skinny threshold 1:4)
  - Cruciform layout (Z extends to curtain walls)
  - 40% BOH / 60% FOH depth split
  - 3.5m circulation gaps between theaters and cube
  - Mega-columns: 1x 10×12m + 3x 8×8m

Units: metres.  Blender Z-up.
"""

import bpy
from mathutils import Vector

# ═════════════════════════════════════════════
# 0. HELPERS
# ═════════════════════════════════════════════
def hex_to_rgb(h):
    h = h.lstrip('#')
    return (int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255, 1.0)

_mats = {}
def get_mat(prog_type):
    if prog_type in _mats:
        return _mats[prog_type]
    col = TYPE_COLORS.get(prog_type, '#888888')
    m = bpy.data.materials.new(name=prog_type)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = hex_to_rgb(col)
    bsdf.inputs['Roughness'].default_value = 0.65
    bsdf.inputs['Alpha'].default_value = 0.85
    m.blend_method = 'BLEND'
    _mats[prog_type] = m
    return m

_cols = {}
def get_col(name):
    if name not in _cols:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        _cols[name] = c
    return _cols[name]

_n = [0]
def make_box(name, cx, cy, cz, sx, sy, sz, prog_type):
    """cx/cz = center XY, cy = BOTTOM of box, sy = height."""
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=(cx, cz, cy + sy / 2))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (sx, sz, sy)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(get_mat(prog_type))
    col = get_col(prog_type.upper()[:30])
    for oc in list(obj.users_collection):
        oc.objects.unlink(obj)
    col.objects.link(obj)
    _n[0] += 1
    return obj

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ═════════════════════════════════════════════
# 1. COLOR PALETTE  (same as HTML)
# ═════════════════════════════════════════════
TYPE_COLORS = {
    'event hall':'#e8543a','stage':'#c0392b','orchestra pit':'#922b21',
    'fly tower':'#884400','lobby':'#f0c040','box office':'#ffa726',
    'event lounge':'#ce93d8','lounge bar':'#ef9a9a','restaurant':'#f48fb1',
    'roof terrace':'#80cbc4','viewing platform':'#4dd0e1',
    'circulation':'#a5d6a7','plaza':'#2a2a2a',
    'sales and display':'#ffb347','fitting rooms':'#f06292',
    'restroom':'#ffd07a','backstage':'#7a6e5f','rehearsal room':'#9b7d4a',
    'dressing room':'#b8860b','green room':'#4caf50','loading':'#546e7a',
    'production workshop':'#6d4c41','set storage':'#5d4037',
    'storage':'#4a4a4a','mechanical':'#263238','staff':'#7986cb',
    'IT support':'#5c6bc0',
    'fire stair and freight elevator':'#ff7043',
    'fire stair and elevator 1':'#ffcc02',
    'fire stair and elevator 2':'#66bb6a',
    'fire stair and elevator 3':'#42a5f5',
}

# ═════════════════════════════════════════════
# 2. BUILDING CONSTANTS
# ═════════════════════════════════════════════
SITE_W = 70.0;  SITE_D = 70.0
FLOOR_STEP = 4.5;  PILOTIS_H = 6.0
SLAB_H = FLOOR_STEP * 0.85;  SLAB_OP = 0.80
EPS = 0.15

CUBE_W = SITE_W * 0.5;  CUBE_D = SITE_D * 0.5
CHX = CUBE_W / 2;  CHZ = CUBE_D / 2

SHAFT_W = 10.0;  SHAFT_D = 12.0
MECH_X_START = CHX * 0.49

GRAND_PW = CUBE_W*0.8;  GRAND_D = CUBE_D*0.8;  GRAND_XS = CHX
BLUE_PW  = CUBE_W*0.63; BLUE_D  = CUBE_D*0.63; BLUE_XS  = -CHX
GLOBE_PD = CUBE_D*0.63;  GLOBE_W = CUBE_W*0.63; GLOBE_ZS = -CHZ
GAP = 3.5

BACK_TYPES = {'backstage','rehearsal room','dressing room','green room',
              'loading','production workshop','set storage','storage',
              'mechanical','staff','IT support'}
FRONT_TYPES = {'lobby','box office','event lounge','lounge bar','restaurant',
               'roof terrace','viewing platform','circulation','restroom',
               'sales and display','fitting rooms'}
CIRC_TYPES = {'fire stair and freight elevator','fire stair and elevator 1',
              'fire stair and elevator 2','fire stair and elevator 3'}

def floor_y(lv):
    if lv == -1: return -FLOOR_STEP
    if lv ==  0: return 0.0
    return PILOTIS_H + (lv-1)*FLOOR_STEP

# ═════════════════════════════════════════════
# 3. FLOOR DATA  (exact copy from HTML)
# ═════════════════════════════════════════════
FD = [
  # B1
  dict(t='loading',a=800,lv=-1),dict(t='set storage',a=1200,lv=-1),
  dict(t='mechanical',a=900,lv=-1),dict(t='storage',a=600,lv=-1),
  dict(t='production workshop',a=400,lv=-1),dict(t='restroom',a=110,lv=-1),
  # L0
  dict(t='plaza',a=3500,lv=0),dict(t='lobby',a=800,lv=0),
  dict(t='box office',a=120,lv=0),dict(t='sales and display',a=300,lv=0),
  dict(t='fitting rooms',a=60,lv=0),dict(t='restroom',a=168,lv=0),
  dict(t='mechanical',a=400,lv=0),dict(t='storage',a=200,lv=0),
  # L1
  dict(t='loading',a=600,lv=1),dict(t='production workshop',a=800,lv=1),
  dict(t='set storage',a=1000,lv=1),dict(t='mechanical',a=600,lv=1),
  dict(t='storage',a=400,lv=1),dict(t='restroom',a=110,lv=1),
  # L2
  dict(t='backstage',a=1000,lv=2),dict(t='dressing room',a=600,lv=2),
  dict(t='rehearsal room',a=500,lv=2),dict(t='green room',a=300,lv=2),
  dict(t='mechanical',a=400,lv=2),dict(t='storage',a=300,lv=2),
  dict(t='staff',a=200,lv=2),dict(t='restroom',a=110,lv=2),
  # L3
  dict(t='stage',a=800,lv=3),dict(t='orchestra pit',a=250,lv=3),
  dict(t='backstage',a=600,lv=3),dict(t='dressing room',a=400,lv=3),
  dict(t='green room',a=200,lv=3),dict(t='mechanical',a=300,lv=3),
  dict(t='lobby',a=600,lv=3),dict(t='event lounge',a=200,lv=3),
  dict(t='sales and display',a=150,lv=3),dict(t='circulation',a=400,lv=3),
  dict(t='restroom',a=168,lv=3),
  # L4 — grand/blue/globe
  dict(t='event hall',a=1800,lv=4,z='grand'),
  dict(t='event hall',a=900,lv=4,z='blue'),
  dict(t='event hall',a=600,lv=4,z='globe'),
  dict(t='lobby',a=500,lv=4),dict(t='lounge bar',a=200,lv=4),
  dict(t='circulation',a=400,lv=4),
  dict(t='restroom',a=168,lv=4),dict(t='restroom',a=168,lv=4),
  dict(t='backstage',a=400,lv=4),dict(t='mechanical',a=200,lv=4),
  # L5
  dict(t='event hall',a=1200,lv=5,z='grand'),
  dict(t='event hall',a=800,lv=5,z='blue'),
  dict(t='event lounge',a=300,lv=5),dict(t='lobby',a=300,lv=5),
  dict(t='circulation',a=400,lv=5),
  dict(t='restroom',a=168,lv=5),dict(t='restroom',a=168,lv=5),
  dict(t='backstage',a=300,lv=5),dict(t='staff',a=150,lv=5),
  dict(t='mechanical',a=200,lv=5),
  # L6
  dict(t='event hall',a=800,lv=6,z='grand'),
  dict(t='event hall',a=500,lv=6,z='blue'),
  dict(t='viewing platform',a=600,lv=6),dict(t='circulation',a=400,lv=6),
  dict(t='restroom',a=168,lv=6),
  dict(t='backstage',a=200,lv=6),dict(t='mechanical',a=300,lv=6),
  dict(t='storage',a=150,lv=6),
  # L7
  dict(t='fly tower',a=900,lv=7,z='grand'),
  dict(t='backstage',a=400,lv=7),dict(t='rehearsal room',a=500,lv=7),
  dict(t='staff',a=200,lv=7),dict(t='mechanical',a=300,lv=7),
  dict(t='storage',a=200,lv=7),dict(t='viewing platform',a=400,lv=7),
  dict(t='circulation',a=400,lv=7),dict(t='restroom',a=110,lv=7),
  # L8
  dict(t='fly tower',a=900,lv=8,z='grand'),
  dict(t='backstage',a=300,lv=8),dict(t='mechanical',a=400,lv=8),
  dict(t='staff',a=150,lv=8),dict(t='storage',a=150,lv=8),
  dict(t='circulation',a=400,lv=8),dict(t='restroom',a=110,lv=8),
  # L9
  dict(t='fly tower',a=900,lv=9,z='grand'),
  dict(t='mechanical',a=500,lv=9),dict(t='staff',a=150,lv=9),
  dict(t='storage',a=150,lv=9),dict(t='restroom',a=110,lv=9),
  # L10
  dict(t='staff',a=1200,lv=10),dict(t='rehearsal room',a=400,lv=10),
  dict(t='IT support',a=150,lv=10),dict(t='mechanical',a=300,lv=10),
  dict(t='storage',a=150,lv=10),dict(t='restroom',a=168,lv=10),
  # L11
  dict(t='staff',a=800,lv=11),dict(t='rehearsal room',a=500,lv=11),
  dict(t='green room',a=200,lv=11),dict(t='IT support',a=100,lv=11),
  dict(t='mechanical',a=200,lv=11),dict(t='storage',a=150,lv=11),
  dict(t='restroom',a=168,lv=11),
  # L12
  dict(t='roof terrace',a=1000,lv=12),dict(t='restaurant',a=400,lv=12),
  dict(t='lounge bar',a=150,lv=12),dict(t='restroom',a=168,lv=12),
  dict(t='mechanical',a=300,lv=12),
]

# ═════════════════════════════════════════════
# 4. CLEAR SCENE
# ═════════════════════════════════════════════
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
for m in list(bpy.data.materials):
    bpy.data.materials.remove(m)

# ═════════════════════════════════════════════
# 5. LAYOUT STRIPS  (with aspect-ratio subdivision)
# ═════════════════════════════════════════════
SKINNY_THRESH = 4.0

def layout_strips(entries, xmin, xmax, zmin, zmax, fy, lv):
    if not entries:
        return
    sum_a   = sum(e['a'] for e in entries)
    xw      = xmax - xmin
    zd      = zmax - zmin
    tot_a   = max(sum_a, xw * zd)
    cur_x   = xmin
    min_w   = 0.3
    max_x   = xmax - EPS

    # Group skinny vs normal
    chunks = []
    cur_chunk = []
    cur_skinny = None
    for e in entries:
        frac = e['a'] / tot_a
        w = xw * frac
        skinny = (zd / w) > SKINNY_THRESH if w > 0.01 else True
        if cur_chunk and cur_skinny == skinny:
            cur_chunk.append((e, w))
        else:
            if cur_chunk:
                chunks.append((cur_skinny, cur_chunk))
            cur_chunk = [(e, w)]
            cur_skinny = skinny
    if cur_chunk:
        chunks.append((cur_skinny, cur_chunk))

    for is_skinny, chunk in chunks:
        chunk_w = sum(w for _, w in chunk)
        if chunk_w <= 0.01:
            continue

        if not is_skinny or len(chunk) == 1:
            # Normal: full Z depth
            sd = max(0.1, zd - EPS * 2)
            cz = clamp((zmin+zmax)/2, -SITE_D/2+sd/2+EPS, SITE_D/2-sd/2-EPS)
            for e, w in chunk:
                sw = max(w, min_w)
                rem = max_x - cur_x
                if rem <= min_w: break
                if sw > rem: sw = max(min_w, rem)
                cx = cur_x + sw / 2
                if sw - 0.12 > 0.01:
                    make_box(f"{e['t']}|L{lv}", cx, fy, cz,
                             sw-0.12, SLAB_H, sd, e['t'])
                cur_x += sw
        else:
            # Halve Z into two rows
            sorted_c = sorted(chunk, key=lambda x: x[0]['a'], reverse=True)
            r1, r2 = [], []
            a1, a2 = 0, 0
            for item in sorted_c:
                if a1 <= a2:
                    r1.append(item); a1 += item[0]['a']
                else:
                    r2.append(item); a2 += item[0]['a']
            if a1 == 0: a1 = 1
            if a2 == 0 and r2: a2 = 1

            z1d = zd * (a1 / (a1 + a2))
            z2d = zd - z1d

            # Row 1
            if r1:
                cz1 = clamp(zmin + z1d/2, -SITE_D/2+z1d/2+EPS, SITE_D/2-z1d/2-EPS)
                d1 = max(0.1, z1d - EPS*2)
                rx = cur_x
                for e, _ in r1:
                    sw = max((e['a']/a1)*chunk_w, min_w)
                    rem = max(min_w, max_x - rx)
                    if sw > rem: sw = rem
                    if sw-0.12 > 0.01 and d1 > 0.01:
                        make_box(f"{e['t']}|L{lv}", rx+sw/2, fy, cz1,
                                 sw-0.12, SLAB_H, d1, e['t'])
                    rx += sw
            # Row 2
            if r2:
                cz2 = clamp(zmin+z1d+z2d/2, -SITE_D/2+z2d/2+EPS, SITE_D/2-z2d/2-EPS)
                d2 = max(0.1, z2d - EPS*2)
                rx = cur_x
                for e, _ in r2:
                    sw = max((e['a']/a2)*chunk_w, min_w)
                    rem = max(min_w, max_x - rx)
                    if sw > rem: sw = rem
                    if sw-0.12 > 0.01 and d2 > 0.01:
                        make_box(f"{e['t']}|L{lv}", rx+sw/2, fy, cz2,
                                 sw-0.12, SLAB_H, d2, e['t'])
                    rx += sw
            cur_x += chunk_w

# ═════════════════════════════════════════════
# 6. CIRCULATION SHAFTS  (4 corners, full height)
# ═════════════════════════════════════════════
bot = floor_y(-1)
top = floor_y(12) + FLOOR_STEP
th  = top - bot

for stype, sw, sd, sx, sz in [
    ('fire stair and freight elevator',10,12, -CHX+10/2+0.2, CHZ-12/2-0.2),
    ('fire stair and elevator 1',       8, 8,  CHX-8/2-0.2,  CHZ-8/2-0.2),
    ('fire stair and elevator 2',       8, 8,  CHX-8/2-0.2, -CHZ+8/2+0.2),
    ('fire stair and elevator 3',       8, 8, -CHX+8/2+0.2, -CHZ+8/2+0.2),
]:
    make_box(f"SHAFT|{stype}", sx, bot, sz, sw, th, sd, stype)

# ═════════════════════════════════════════════
# 7. PER-FLOOR SLABS
# ═════════════════════════════════════════════
for lv in range(-1, 13):
    fy = floor_y(lv)

    all_e = [e for e in FD if e['lv'] == lv and e['t'] not in CIRC_TYPES]
    if not any(e['t'] in ('restroom','toilets') for e in all_e):
        all_e.append(dict(t='restroom', a=168, lv=lv))

    grand = [e for e in all_e if e.get('z') == 'grand']
    blue  = [e for e in all_e if e.get('z') == 'blue']
    globe = [e for e in all_e if e.get('z') == 'globe']
    cube  = [e for e in all_e if not e.get('z')]

    back_e  = [e for e in cube if e['t'] in BACK_TYPES]
    front_e = [e for e in cube if e['t'] in FRONT_TYPES]
    mech_e  = [e for e in back_e if e['t'] == 'mechanical']
    nmb     = [e for e in back_e if e['t'] != 'mechanical']

    # Cruciform Z bounds (to curtain wall)
    zmax = CHZ - 0.3
    zmin = -CHZ + 0.3
    sp   = zmax - (zmax - zmin) * 0.4  # 40% BOH split

    layout_strips(nmb,    -CHX+SHAFT_W+0.3, MECH_X_START,     sp+0.2, zmax, fy, lv)
    layout_strips(mech_e, MECH_X_START,      CHX-SHAFT_W-0.3, sp+0.2, zmax, fy, lv)
    layout_strips(front_e,-CHX+SHAFT_W+0.3,  CHX-SHAFT_W-0.3, zmin,   sp-0.2, fy, lv)

    # Grand Theater (+X)
    for e in grand:
        w = min(GRAND_PW*0.95, SITE_W-EPS*2)
        d = min(GRAND_D*0.95,  SITE_D-EPS*2)
        cx = clamp(GRAND_XS+w/2+GAP, -SITE_W/2+w/2+EPS, SITE_W/2-w/2-EPS)
        cz = 0.0
        make_box(f"{e['t']}|L{lv}", cx, fy, cz, w, SLAB_H, d, e['t'])
        lw = (cx - w/2) - GRAND_XS
        if lw > 0.1:
            make_box(f"circ_link|L{lv}", GRAND_XS+lw/2, fy, cz,
                     max(0.01,lw-0.05), SLAB_H, min(14,d*0.7), 'circulation')

    # Blue Box (-X)
    for e in blue:
        w = min(BLUE_PW*0.95, SITE_W-EPS*2)
        d = min(BLUE_D*0.95,  SITE_D-EPS*2)
        cx = clamp(BLUE_XS-w/2-GAP, -SITE_W/2+w/2+EPS, SITE_W/2-w/2-EPS)
        cz = 0.0
        make_box(f"{e['t']}|L{lv}", cx, fy, cz, w, SLAB_H, d, e['t'])
        lw = BLUE_XS - (cx + w/2)
        if lw > 0.1:
            make_box(f"circ_link|L{lv}", BLUE_XS-lw/2, fy, cz,
                     max(0.01,lw-0.05), SLAB_H, min(12,d*0.7), 'circulation')

    # Globe Playhouse (-Z)
    for e in globe:
        w = min(GLOBE_W*0.95, SITE_W-EPS*2)
        d = min(GLOBE_PD*0.95, SITE_D-EPS*2)
        cz = clamp(GLOBE_ZS-d/2-GAP, -SITE_D/2+d/2+EPS, SITE_D/2-d/2-EPS)
        cx = 0.0
        make_box(f"{e['t']}|L{lv}", cx, fy, cz, w, SLAB_H, d, e['t'])
        ld = GLOBE_ZS - (cz + d/2)
        if ld > 0.1:
            make_box(f"circ_link|L{lv}", cx, fy, GLOBE_ZS-ld/2,
                     min(14,w*0.7), SLAB_H, max(0.01,ld-0.05), 'circulation')

# ═════════════════════════════════════════════
# 8. GROUND PLANE
# ═════════════════════════════════════════════
bpy.ops.mesh.primitive_plane_add(size=SITE_W, location=(0, 0, -0.01))
gp = bpy.context.object
gp.name = "GROUND_PLANE"
gp.scale.y = SITE_D / SITE_W
bpy.ops.object.transform_apply(scale=True)
gm = bpy.data.materials.new("ground")
gm.use_nodes = True
gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.08,0.08,0.08,1)
gp.data.materials.append(gm)

print(f"\\n✅ TPAC massing complete — {_n[0]} objects created.")
