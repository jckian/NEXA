import bpy
import bmesh
import math
from mathutils import Vector

# =========================
# 參數
# =========================

GRID_X = 4
GRID_Y = 4
CELL = 3.0

HEIGHT = 4.0
SEG = 20
THICKNESS = 0.15   # 🔥 15 cm

# =========================
# 清空
# =========================

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

bm = bmesh.new()

# =========================
# grid
# =========================

def grid(i,j,z=0):
    return Vector((i*CELL, j*CELL, z))

# =========================
# ridge curve
# =========================

def ridge_curve(p1, p2):

    direction = (p2 - p1)
    length = direction.length
    x_dir = direction.normalized()
    z_dir = Vector((0,0,1))

    center = (p1 + p2) / 2

    pts = []

    for i in range(SEG+1):
        t = i / SEG
        angle = math.pi * t

        x = (t - 0.5) * length
        z = math.sin(angle) * HEIGHT

        pt = center + x_dir * x + z_dir * z
        pts.append(pt)

    return pts

# =========================
# loft
# =========================

def loft_to_slab(curve_pts, top1, top2):

    slab_pts = []

    for i in range(SEG+1):
        t = i / SEG
        slab_pts.append(top1.lerp(top2, t))

    for i in range(SEG):

        c1 = bm.verts.new(curve_pts[i])
        c2 = bm.verts.new(curve_pts[i+1])

        s1 = bm.verts.new(slab_pts[i])
        s2 = bm.verts.new(slab_pts[i+1])

        try:
            bm.faces.new((c1, c2, s2, s1))
        except:
            pass

# =========================
# 主生成
# =========================

for i in range(GRID_X):
    for j in range(GRID_Y):

        p00 = grid(i,j)
        p10 = grid(i+1,j)
        p01 = grid(i,j+1)
        p11 = grid(i+1,j+1)

        t00 = grid(i,j,HEIGHT)
        t10 = grid(i+1,j,HEIGHT)
        t01 = grid(i,j+1,HEIGHT)
        t11 = grid(i+1,j+1,HEIGHT)

        loft_to_slab(ridge_curve(p00, p10), t00, t10)
        loft_to_slab(ridge_curve(p10, p11), t10, t11)
        loft_to_slab(ridge_curve(p11, p01), t11, t01)
        loft_to_slab(ridge_curve(p01, p00), t01, t00)

# slab
for i in range(GRID_X):
    for j in range(GRID_Y):

        v1 = bm.verts.new(grid(i,j,HEIGHT))
        v2 = bm.verts.new(grid(i+1,j,HEIGHT))
        v3 = bm.verts.new(grid(i+1,j+1,HEIGHT))
        v4 = bm.verts.new(grid(i,j+1,HEIGHT))

        try:
            bm.faces.new((v1,v2,v3,v4))
        except:
            pass

# =========================
# 輸出 mesh
# =========================

mesh = bpy.data.meshes.new("TAMA_FINAL")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("TAMA_FINAL", mesh)
bpy.context.collection.objects.link(obj)

# =========================
# 🔥 正確厚度（關鍵）
# =========================

bpy.context.view_layer.objects.active = obj

mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
mod.thickness = THICKNESS
mod.offset = 0
mod.use_even_offset = True

bpy.ops.object.modifier_apply(modifier=mod.name)

# =========================
# Smooth
# =========================

bpy.ops.object.shade_smooth()

print("✅ FINAL TAMA (15cm concrete shell)")