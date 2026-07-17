import bpy
from mathutils import Vector

# =========================
# SETTINGS
# =========================
GRID_X       = 12.0      # column grid X spacing (library: long spans, open reading rooms)
GRID_Y       = 12.0      # column grid Y spacing
FLOOR_HEIGHT = 5.5       # floor-to-floor height (double-height reading rooms)
SLAB_T       = 0.35      # slab thickness (post-tensioned for long span)

COL_W        = 0.60      # column section width (larger — carries long-span load)
COL_D        = 0.60      # column section depth

BEAM_W       = 0.40      # beam width
BEAM_H       = 0.90      # beam depth (deep — spanning 12 m bays)

CORE_RATIO   = 0.18      # core width/depth as fraction of mass footprint

# Facade: stone/concrete panel alternating with ribbon windows
MULLION_W    = 0.18
MULLION_D    = 0.35      # deep — expressed masonry / travertine edge

# =========================
# COLLECTION SETUP
# =========================
COL_NAME = "LIBRARY_STRUCTURAL"

if COL_NAME in bpy.data.collections:
    old = bpy.data.collections[COL_NAME]
    for obj in list(old.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(old)

col = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(col)

def safe_link(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

# =========================
# MATERIALS
# =========================
def make_mat(name, r, g, b, alpha=1.0):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = "BLEND"
    return mat

mat_core    = make_mat("LIB_CORE",    0.32, 0.29, 0.25)   # warm stone core
mat_col     = make_mat("LIB_COLUMN",  0.78, 0.74, 0.68)   # travertine column
mat_beam    = make_mat("LIB_BEAM",    0.72, 0.68, 0.62)
mat_slab    = make_mat("LIB_SLAB",    0.60, 0.57, 0.52, 0.90)
mat_mullion = make_mat("LIB_MULLION", 0.85, 0.81, 0.74)   # light stone panel
mat_glass   = make_mat("LIB_GLASS",   0.55, 0.62, 0.50, 0.16)  # warm grey-green glass

# =========================
# PRIMITIVE HELPERS
# =========================
def add_box(name, sx, sy, sz, x, y, z, mat):
    """Add a box centred at (x, y, z) with full dimensions sx/sy/sz."""
    bpy.ops.mesh.primitive_cube_add(location=(x, y, z))
    obj = bpy.context.object
    obj.scale = (sx / 2, sy / 2, sz / 2)
    bpy.ops.object.transform_apply(scale=True)
    obj.name = name
    obj.data.materials.append(mat)
    safe_link(obj)
    return obj

# =========================
# MASS DEFINITIONS
# Library: main reading hall (tall) + book stacks wing + entrance pavilion
# =========================
masses = [
    dict(minX=-24, maxX=24, minY=-12, maxY=12, minZ=0,    maxZ=16.5),  # reading hall  (3 double-height floors)
    dict(minX=0,   maxX=24, minY=-18, maxY=18, minZ=0,    maxZ=33.0),  # stacks wing   (6 floors, denser)
    dict(minX=-24, maxX=0,  minY=-18, maxY=-12, minZ=0,   maxZ=11.0),  # entrance pavilion (2 floors)
]

# =========================
# MAIN LOOP — PER MASS
# =========================
for mi, m in enumerate(masses):
    tag = f"M{mi}"

    mx0, mx1 = m["minX"], m["maxX"]
    my0, my1 = m["minY"], m["maxY"]
    mz0, mz1 = m["minZ"], m["maxZ"]

    W   = mx1 - mx0
    D   = my1 - my0
    H   = mz1 - mz0
    cx  = (mx0 + mx1) / 2
    cy  = (my0 + my1) / 2

    floors = max(1, round(H / FLOOR_HEIGHT))

    # --------------------------------------------------
    # CORE  (full-height concrete wall block)
    # --------------------------------------------------
    core_w = W * CORE_RATIO
    core_d = D * CORE_RATIO
    add_box(f"CORE_{tag}", core_w, core_d, H,
            cx, cy, mz0 + H / 2, mat_core)

    # --------------------------------------------------
    # COLUMN GRID POSITIONS  (snapped to grid)
    # --------------------------------------------------
    xs = []
    x = mx0
    while x <= mx1 + 1e-4:
        xs.append(round(x, 6))
        x += GRID_X

    ys = []
    y = my0
    while y <= my1 + 1e-4:
        ys.append(round(y, 6))
        y += GRID_Y

    def in_core(x, y):
        return (cx - core_w / 2 - 1e-4 < x < cx + core_w / 2 + 1e-4 and
                cy - core_d / 2 - 1e-4 < y < cy + core_d / 2 + 1e-4)

    # --------------------------------------------------
    # PER-FLOOR STRUCTURAL SYSTEM
    # --------------------------------------------------
    for fi in range(floors):
        floor_z0 = mz0 + fi * FLOOR_HEIGHT
        floor_z1 = floor_z0 + FLOOR_HEIGHT

        slab_top_z = floor_z1
        slab_bot_z = slab_top_z - SLAB_T
        beam_top_z = slab_bot_z
        beam_bot_z = beam_top_z - BEAM_H
        col_top_z  = slab_bot_z
        col_bot_z  = floor_z0

        col_h   = col_top_z - col_bot_z
        col_cz  = (col_bot_z + col_top_z) / 2
        beam_cz = (beam_bot_z + beam_top_z) / 2

        # ---- COLUMNS ----
        for xi in xs:
            for yi in ys:
                if in_core(xi, yi):
                    continue
                add_box(f"COL_{tag}_F{fi}_X{xi}_Y{yi}",
                        COL_W, COL_D, col_h,
                        xi, yi, col_cz, mat_col)

        # ---- BEAMS in X direction ----
        for yi in ys:
            for seg in range(len(xs) - 1):
                xi0 = xs[seg]; xi1 = xs[seg + 1]
                mid_x = (xi0 + xi1) / 2
                span  = xi1 - xi0
                if in_core(xi0, yi) and in_core(xi1, yi):
                    continue
                add_box(f"BEAM_X_{tag}_F{fi}_Y{yi}_S{seg}",
                        span - COL_W, BEAM_W, BEAM_H,
                        mid_x, yi, beam_cz, mat_beam)

        # ---- BEAMS in Y direction ----
        for xi in xs:
            for seg in range(len(ys) - 1):
                yi0 = ys[seg]; yi1 = ys[seg + 1]
                mid_y = (yi0 + yi1) / 2
                span  = yi1 - yi0
                if in_core(xi, yi0) and in_core(xi, yi1):
                    continue
                add_box(f"BEAM_Y_{tag}_F{fi}_X{xi}_S{seg}",
                        BEAM_W, span - COL_D, BEAM_H,
                        xi, mid_y, beam_cz, mat_beam)

        # ---- SLAB ----
        add_box(f"SLAB_{tag}_F{fi}",
                W, D, SLAB_T,
                cx, cy, slab_top_z - SLAB_T / 2, mat_slab)

    # --------------------------------------------------
    # FACADE MULLIONS  (stone panel + ribbon window)
    # --------------------------------------------------
    for fi in range(floors):
        slab_top_z = mz0 + (fi + 1) * FLOOR_HEIGHT
        mul_bot_z  = slab_top_z - FLOOR_HEIGHT + SLAB_T
        mul_top_z  = slab_top_z
        mul_h      = mul_top_z - mul_bot_z
        mul_cz     = (mul_bot_z + mul_top_z) / 2

        for xi in xs:
            for ys_edge in [my0, my1]:
                add_box(f"MUL_NS_{tag}_F{fi}_X{xi}_Y{ys_edge}",
                        MULLION_W, MULLION_D, mul_h,
                        xi, ys_edge, mul_cz, mat_mullion)

        for yi in ys:
            for xs_edge in [mx0, mx1]:
                add_box(f"MUL_EW_{tag}_F{fi}_Y{yi}_X{xs_edge}",
                        MULLION_D, MULLION_W, mul_h,
                        xs_edge, yi, mul_cz, mat_mullion)

    # --------------------------------------------------
    # GLASS INFILL PANELS
    # --------------------------------------------------
    for fi in range(floors):
        slab_top_z = mz0 + (fi + 1) * FLOOR_HEIGHT
        pnl_bot    = slab_top_z - FLOOR_HEIGHT + SLAB_T
        pnl_top    = slab_top_z
        pnl_h      = pnl_top - pnl_bot
        pnl_cz     = (pnl_bot + pnl_top) / 2
        glass_t    = 0.04

        for seg in range(len(xs) - 1):
            mid_x = (xs[seg] + xs[seg + 1]) / 2
            span  = xs[seg + 1] - xs[seg] - MULLION_W
            add_box(f"GLS_N_{tag}_F{fi}_S{seg}",
                    span, glass_t, pnl_h,
                    mid_x, my0, pnl_cz, mat_glass)
            add_box(f"GLS_S_{tag}_F{fi}_S{seg}",
                    span, glass_t, pnl_h,
                    mid_x, my1, pnl_cz, mat_glass)

        for seg in range(len(ys) - 1):
            mid_y = (ys[seg] + ys[seg + 1]) / 2
            span  = ys[seg + 1] - ys[seg] - MULLION_W
            add_box(f"GLS_E_{tag}_F{fi}_S{seg}",
                    glass_t, span, pnl_h,
                    mx0, mid_y, pnl_cz, mat_glass)
            add_box(f"GLS_W_{tag}_F{fi}_S{seg}",
                    glass_t, span, pnl_h,
                    mx1, mid_y, pnl_cz, mat_glass)

    print(f"✅ {tag}: {floors} floors | {len(xs)} x {len(ys)} grid")

# =========================
# DONE
# =========================
print("📚 LIBRARY STRUCTURAL SYSTEM COMPLETE — reading hall / stacks / entrance.")
