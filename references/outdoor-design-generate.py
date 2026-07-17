import bpy
import bmesh
from mathutils import Vector
import random

# =========================
# PARAMETERS
# =========================

PRIMARY_WIDTH = 3.5
SECONDARY_WIDTH = 2.0

PLAZA_RADIUS = 10.0
PLAZA_SEGMENTS = 32

TREE_MIN_DIST = 2.5
TREE_DENSITY = 0.35

PATH_SMOOTH = 0.3

# =========================
# HELPERS
# =========================

def get_obj(name):
    obj = bpy.data.objects.get(name)
    if not obj:
        raise Exception(f"Missing: {name}")
    return obj

def get_entries():
    return [o for o in bpy.data.objects if "Entry_" in o.name]

# =========================
# 1. CREATE PLAZA (REAL SURFACE)
# =========================

def create_plaza_mesh(name, center, radius, segments=32):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    verts = []
    for i in range(segments):
        angle = (i / segments) * 3.14159 * 2
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        verts.append(bm.verts.new((x, y, center.z)))

    center_v = bm.verts.new(center)

    for i in range(segments):
        bm.faces.new((center_v, verts[i], verts[(i+1) % segments]))

    bm.to_mesh(mesh)
    bm.free()

    return obj

# =========================
# 2. CREATE WALKWAY (MESH STRIP)
# =========================

def create_path_mesh(name, p0, p1, width=3.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    dir_vec = (p1 - p0).normalized()
    perp = Vector((-dir_vec.y, dir_vec.x, 0)) * width

    v1 = bm.verts.new(p0 + perp)
    v2 = bm.verts.new(p0 - perp)
    v3 = bm.verts.new(p1 - perp)
    v4 = bm.verts.new(p1 + perp)

    bm.faces.new((v1, v2, v3, v4))

    bm.to_mesh(mesh)
    bm.free()

    return obj

# =========================
# 3. MAIN DATA
# =========================

building = get_obj("Building")
site = get_obj("Site")
entries = get_entries()

center = building.location

plazas = []
paths = []

# =========================
# 4. PLAZA GENERATION (EDGE-BASED)
# =========================

for e in entries:
    direction = (e.location - center).normalized()

    # plaza slightly offset from building
    plaza_center = center + direction * 12.0

    plaza = create_plaza_mesh(
        f"Plaza_{e.name}",
        plaza_center,
        PLAZA_RADIUS
    )

    plazas.append(plaza)

# =========================
# 5. PATH GENERATION (REAL SURFACE)
# =========================

for i, e in enumerate(entries):
    # Entry → Plaza (not straight line feel: slight offset midpoint)
    plaza = plazas[i]

    mid = (e.location + plaza.location) / 2

    # curve logic: slight deviation
    offset = Vector((-(plaza.location - e.location).y,
                      (plaza.location - e.location).x,
                      0)).normalized() * random.uniform(-3, 3)

    mid += offset

    # build segmented walkway
    p0 = e.location
    p1 = mid
    p2 = plaza.location

    path1 = create_path_mesh(f"Path_A_{i}", p0, p1, PRIMARY_WIDTH)
    path2 = create_path_mesh(f"Path_B_{i}", p1, p2, PRIMARY_WIDTH)

    paths.append(path1)
    paths.append(path2)

# =========================
# 6. PLANTING (VOID-BASED LOGIC)
# =========================

def distance(pt, obj):
    return (pt - obj.location).length

bbox = [site.matrix_world @ Vector(c) for c in site.bound_box]

min_x = min(v.x for v in bbox)
max_x = max(v.x for v in bbox)
min_y = min(v.y for v in bbox)
max_y = max(v.y for v in bbox)

x = min_x
trees = []

while x < max_x:
    y = min_y
    while y < max_y:

        pt = Vector((x, y, 0))

        # avoid plaza
        near_plaza = any(distance(pt, p) < PLAZA_RADIUS * 1.3 for p in plazas)

        # avoid paths
        near_path = any(
            (pt - obj.location).length < 2.5
            for obj in paths
        )

        # void condition (key concept)
        if not near_plaza and not near_path:
            if random.random() < TREE_DENSITY:
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=pt)
                trees.append(bpy.context.active_object)

        y += 4.5
    x += 4.5

print("V3.1 Real Landscape System Generated")
