"""
Rebuild the Rhino block "STR" (stair / step unit) in Blender.

STR is the simplest of the kit: 14 planar box solids (no connectors, no curved
faces, no nesting) modelled at REAL scale (placed x1). They reduce to 3 unique
box shapes:
  * step  (27.94 x 91.44 x 17.78)  x10  -> the stair treads, stepping up in Z
  * block (91.44 x 91.44 x 17.78)  x2   -> square landing/support blocks
  * bar   (91.44 x 27.94 x 17.78)  x2   -> short support bars
(91.44 = 3 ft, 27.94 = 11 in, 17.78 = 7 in.)

Each unique shape is built once and instanced (linked duplicates) at its offsets.
Every face is planar, so the geometry is exact; a limited-dissolve pass merges
coplanar tris into clean n-gons and recomputes outward normals.

Run: Scripting workspace -> open -> Run Script
(or `blender --background --python build_str.py`).
"""

import bpy
import bmesh

SCALE = 1.0                 # STR is already at real scale (placed x1)
ROOT_NAME = "STR"
COL_BLACK = (0.0, 0.0, 0.0)
MERGE_DIST = 1.0e-3
DISSOLVE_ANGLE = 0.0349                 # ~2 deg

# ---------------------------------------------------------------------------
# Unique box shapes: local mesh (verts rel. to bbox-min) + instance offsets
# ---------------------------------------------------------------------------
PARTS = [
    {"name": "step", "nv": 8, "nf": 6,
     "off": [(0, 147.32, 213.36), (111.76, 147.32, 142.24), (83.82, 147.32, 160.02),
             (55.88, 147.32, 177.8), (27.94, 147.32, 195.58), (111.76, 0, 53.34),
             (83.82, 0, 35.56), (55.88, 0, 17.78), (27.94, 0, 0), (0, 0, -17.78)],
     "v": "27.94,91.44,17.78|27.94,91.44,0|27.94,0,17.78|27.94,0,0|0,91.44,17.78|0,91.44,0|0,0,17.78|0,0,0",
     "f": "2,3,1,0|0,1,5,4|4,5,7,6|6,7,3,2|7,5,1,3|6,2,0,4"},
    {"name": "block", "nv": 8, "nf": 6,
     "off": [(139.7, 0, 71.12), (139.7, 147.32, 124.46)],
     "v": "91.44,91.44,17.78|91.44,91.44,0|91.44,0,17.78|91.44,0,0|0,91.44,17.78|0,91.44,0|0,0,17.78|0,0,0",
     "f": "4,5,7,6|6,7,3,2|2,3,1,0|0,1,5,4|1,3,7,5|0,4,6,2"},
    {"name": "bar", "nv": 8, "nf": 6,
     "off": [(139.7, 91.44, 88.9), (139.7, 119.38, 106.68)],
     "v": "91.44,27.94,17.78|91.44,27.94,0|91.44,0,17.78|91.44,0,0|0,27.94,17.78|0,27.94,0|0,0,17.78|0,0,0",
     "f": "6,7,3,2|2,3,1,0|0,1,5,4|4,5,7,6|5,1,3,7|4,6,2,0"},
]


# ---------------------------------------------------------------------------
def pv(s):
    out = []
    for tok in s.strip().strip("|").split("|"):
        if not tok:
            continue
        x, y, z = tok.split(",")
        out.append((float(x) * SCALE, float(y) * SCALE, float(z) * SCALE))
    return out


def pf(s):
    out = []
    for tok in s.strip().strip("|").split("|"):
        if not tok:
            continue
        out.append(tuple(int(i) for i in tok.split(",")))
    return out


def material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        mat.diffuse_color = (*color, 1.0)
    return mat


def collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def build_mesh(name, verts, faces, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_DIST)
    bmesh.ops.dissolve_limit(bm, angle_limit=DISSOLVE_ANGLE,
                             use_dissolve_boundaries=False,
                             verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.update()
    me.materials.append(mat)
    return me


def main():
    coll = collection(ROOT_NAME)
    mat = material("STR_black", COL_BLACK)

    root = bpy.data.objects.new(ROOT_NAME + "_root", None)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 60.0 * SCALE
    coll.objects.link(root)

    n = 0
    for p in PARTS:
        verts = pv(p["v"])
        faces = pf(p["f"])
        assert len(verts) == p["nv"] and len(faces) == p["nf"], "%s count" % p["name"]
        me = build_mesh(p["name"], verts, faces, mat)
        for k, off in enumerate(p["off"]):
            nm = "%s_%02d" % (p["name"], k + 1) if len(p["off"]) > 1 else p["name"]
            ob = bpy.data.objects.new(nm, me)
            coll.objects.link(ob)
            ob.parent = root
            ob.location = (off[0] * SCALE, off[1] * SCALE, off[2] * SCALE)
            n += 1

    print("Built block '%s': %d objects (%d unique shapes)" % (ROOT_NAME, n, len(PARTS)))


if __name__ == "__main__":
    main()
