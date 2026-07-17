# =============================================================================
#  ADAPTIVE STRUCTURAL GENERATOR  (Blender 3.x / 4.x)
# -----------------------------------------------------------------------------
#  Turns ANY massing volume into a structural model: core, shafts, grid,
#  columns, beams, slabs, roofs, curtain wall, fins, and an underground system,
#  with load-path validation.
#
#  It is SHAPE-ADAPTIVE: it does not assume a footprint. It reads the massing by
#  inside-testing points against the actual geometry and building a per-floor
#  OCCUPANCY GRID. Setbacks, cantilevers, terraces, atriums and transfer levels
#  are all derived from how that occupancy changes floor to floor. The same code
#  works on an L-shape, a tower, a stepped podium, a single solid, or a set of
#  tagged room meshes.
#
#  USAGE (paste into Blender's Text Editor, or exec from console):
#     import importlib, sys
#     sys.path.append(r"/path/to/folder"); import adaptive_structural_generator as A
#     importlib.reload(A)
#     A.generate(A.DEFAULT_CONFIG)                 # uses selection / all massing
#     # or with overrides:
#     A.generate({**A.DEFAULT_CONFIG, "grid_spacing": 9.0, "fins": {"enable": False}})
#
#  The HTML rules platform exports a CONFIG dict you can paste here.
# =============================================================================

import bpy, bmesh, json, math, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# -----------------------------------------------------------------------------
# CONFIG  (every rule lives here; the HTML platform writes this object)
# -----------------------------------------------------------------------------
DEFAULT_CONFIG = {
    # ---- input ----
    "input": {
        "mode": "selected_or_all",   # "selected" | "collection" | "objects" | "selected_or_all"
        "collection": "",            # used when mode == "collection"
        "objects": [],               # used when mode == "objects"
        "exclude_collections": ["CORE","SHAFTS","GRID","COLUMNS","BEAMS","SLABS",
                                 "CURTAIN_WALL","FACADE_FINS","DIAPHRAGM_WALL","GRADE_BEAMS"],
    },

    # ---- floor detection ----
    "floors": {
        "mode": "auto",              # "tags" | "slice" | "auto"
        "tag_regex": r"_(B\d+|L\d+)(?:_\d+)?$",   # captures B1 / L0..Ln
        "slice_height": 4.5,         # used in "slice" mode (typical floor-to-floor)
        "grade_z": 0.0,              # z of ground level; below = basement
        "min_floor_thickness": 1.5,  # ignore slivers
    },

    # ---- occupancy sampling (drives shape adaptivity) ----
    "occupancy": {
        "cell": 2.0,                 # XY sample cell size (m); smaller = finer shape
        "ray_axis": "Z",             # inside-test ray direction
    },

    # ---- structural grid ----
    "grid": {
        "spacing": 8.0,              # base column module (m)
        "anchor": "centroid",        # "centroid" | "origin" | [x,y]
        "snap_to_edges": True,       # add grid lines on the footprint extremes
        "maximize_alignment": True,  # one global grid for whole tower (columns stack)
    },

    # ---- program -> structural category -> bay range (m) ----
    "bays": {                        # min,max clear bay by category
        "retail":            [10, 15],
        "office":            [8, 10],
        "residential":       [6, 8],
        "hotel":             [7, 9],
        "parking":           [8, 9],
        "assembly_longspan": [15, 30],   # halls / stages / atria roofs
        "default":           [8, 10],
    },
    "program_keywords": [            # first match wins; substring, case-insensitive
        (["retail","shop","store","sales","display","lobby","mall","restaurant",
          "bar","lounge","cafe","event_lounge","fitting","box_office"], "retail"),
        (["office","staff","admin","workstation","it_support","workshop","production"], "office"),
        (["resid","apartment","unit","dwell","bedroom","dressing","rehearsal","restroom","wc","toilet"], "residential"),
        (["hotel","guestroom","suite","green_room","backstage"], "hotel"),
        (["parking","garage","loading","storage","set_storage","mech","plant"], "parking"),
        (["event_hall","hall","auditorium","theater","theatre","stage","orchestra",
          "fly_tower","ballroom","arena","atrium"], "assembly_longspan"),
    ],

    # ---- core / shafts ----
    "core": {
        "mode": "detect",            # "detect" (use circ/core objects) | "auto" (place central)
        "detect_keywords": ["core","stair","elevator","lift","shaft","mep","escalator","freight"],
        "wall_thickness": 0.4,
        "auto_size_fraction": 0.18,  # auto core area as fraction of smallest upper floor
        "continuous_to_roof": True,  # extend detected/auto core to roof
    },

    # ---- member sizes (m) ----
    "members": {
        "column":        0.60,       # square col side
        "column_transfer":0.70,
        "beam_w":        0.35, "beam_d": 0.70,
        "transfer_w":    0.90, "transfer_d": 1.80,
        "slab_t":        0.30,
        "curtain_t":     0.08,
    },

    # ---- curtain wall ----
    "curtain": {"enable": True, "start_at_grade": True},

    # ---- facade fins ----
    "fins": {
        "enable": True,
        "mullion": 1.5,              # fin spacing (m)
        "depth_primary": 0.30, "width_primary": 0.15,   # on structural grid lines
        "depth_infill":  0.20, "width_infill":  0.10,
        "min_run": 1.0,
    },

    # ---- underground ----
    "underground": {
        "enable": True,
        "diaphragm_thickness": 0.8,  # 0.6..1.0
        "toe_below_foundation": 1.0, # extra embedment depth (m)
        "grade_beam_w": 0.50, "grade_beam_d": 0.90,
    },

    # ---- output ----
    "clear_previous": True,          # remove prior generated collections first
    "report_name": "structural_report.json",
}

GEN_COLLECTIONS = ["CORE","SHAFTS","GRID","COLUMNS","BEAMS","SLABS",
                   "CURTAIN_WALL","FACADE_FINS","DIAPHRAGM_WALL","GRADE_BEAMS"]


# =============================================================================
#  LOW-LEVEL HELPERS
# =============================================================================
def _coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def _mat(name, rgba, alpha=1.0, metallic=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = rgba
        if "Metallic" in b.inputs: b.inputs["Metallic"].default_value = metallic
        if alpha < 1.0:
            b.inputs["Alpha"].default_value = alpha; m.blend_method = 'BLEND'
    return m

def _box(name, x0, y0, z0, x1, y1, z1, coll, mat=None):
    """Axis-aligned cuboid built with from_pydata (fast, no bpy.ops)."""
    if x1 < x0: x0, x1 = x1, x0
    if y1 < y0: y0, y1 = y1, y0
    if z1 < z0: z0, z1 = z1, z0
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    if mat: ob.data.materials.append(mat)
    return ob

def _wbb(obj):
    cs = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    xs=[c.x for c in cs]; ys=[c.y for c in cs]; zs=[c.z for c in cs]
    return (min(xs),min(ys),min(zs),max(xs),max(ys),max(zs))

def _obj_bb(o):  # bbox of a generated (axis-aligned) object
    return _wbb(o)


# =============================================================================
#  INPUT + INSIDE TEST  (the heart of shape adaptivity)
# =============================================================================
def gather_massing(cfg):
    mode = cfg["input"]["mode"]
    excl = set(cfg["input"]["exclude_collections"])
    gen_objs = set()
    for cn in excl:
        c = bpy.data.collections.get(cn)
        if c:
            gen_objs.update(o.name for o in c.objects)

    if mode == "collection":
        c = bpy.data.collections.get(cfg["input"]["collection"])
        objs = [o for o in (c.objects if c else []) if o.type == 'MESH']
    elif mode == "objects":
        objs = [bpy.data.objects[n] for n in cfg["input"]["objects"]
                if n in bpy.data.objects and bpy.data.objects[n].type == 'MESH']
    elif mode == "selected":
        objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    else:  # selected_or_all
        sel = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        if sel:
            objs = sel
        else:
            objs = [o for o in bpy.data.objects
                    if o.type == 'MESH' and o.name not in gen_objs]
    # never treat previously generated structure as massing
    objs = [o for o in objs if o.name not in gen_objs]
    return objs

def build_bvh(objs):
    bm = bmesh.new()
    for o in objs:
        me = o.to_mesh()
        bm.from_mesh(me)
        # bake world transform onto the copied verts
        mw = o.matrix_world
        for v in bm.verts[-len(me.vertices):]:
            v.co = mw @ v.co
        o.to_mesh_clear()
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    return bvh

def inside(bvh, p, axis='Z'):
    """Even-odd ray-cast containment test against the combined massing."""
    d = Vector((0,0,1)) if axis == 'Z' else (Vector((1,0,0)) if axis=='X' else Vector((0,1,0)))
    o = Vector(p); count = 0
    for _ in range(64):
        hit = bvh.ray_cast(o, d)
        if hit[0] is None:
            break
        count += 1
        o = hit[0] + d * 1e-4
    return (count % 2) == 1


# =============================================================================
#  FLOOR DETECTION
# =============================================================================
def detect_floors(objs, cfg):
    fc = cfg["floors"]
    rx = re.compile(fc["tag_regex"])
    tagged = [(o, rx.search(o.name)) for o in objs]
    have_tags = sum(1 for _, m in tagged if m)
    use_tags = fc["mode"] == "tags" or (fc["mode"] == "auto" and have_tags >= 0.5*len(objs) and have_tags > 0)

    floors = []
    if use_tags:
        groups = {}
        for o, m in tagged:
            if not m: continue
            tok = m.group(1)
            idx = -int(tok[1:]) if tok[0].upper() == 'B' else int(tok[1:])
            groups.setdefault(idx, []).append(o)
        for idx in sorted(groups):
            gobjs = groups[idx]
            bbs = [_wbb(o) for o in gobjs]
            z0 = min(b[2] for b in bbs); z1 = max(b[5] for b in bbs)
            if z1 - z0 < fc["min_floor_thickness"]: 
                z1 = z0 + fc["slice_height"]
            programs = sorted(set(rx.sub('', o.name) for o in gobjs))
            floors.append({"index": idx, "z0": round(z0,3), "z1": round(z1,3),
                           "programs": programs, "objs": gobjs})
    else:
        # slice the whole volume into floors of slice_height
        bbs = [_wbb(o) for o in objs]
        zmin = min(b[2] for b in bbs); zmax = max(b[5] for b in bbs)
        fh = fc["slice_height"]; grade = fc["grade_z"]
        # align slicing so a floor boundary sits at grade
        n_below = max(0, math.ceil((grade - zmin) / fh - 1e-6))
        start = grade - n_below*fh
        z = start; idx = -n_below
        while z < zmax - 1e-6:
            floors.append({"index": idx, "z0": round(z,3), "z1": round(z+fh,3),
                           "programs": [], "objs": objs})
            z += fh; idx += 1
    # order + neighbour links
    floors.sort(key=lambda f: f["z0"])
    for i, f in enumerate(floors):
        f["zmid"] = round((f["z0"]+f["z1"])/2, 3)
    return floors


# =============================================================================
#  OCCUPANCY GRID  (per floor)
# =============================================================================
class OccGrid:
    def __init__(self, bvh, floors, cfg, objs):
        self.cs = cfg["occupancy"]["cell"]
        self.axis = cfg["occupancy"]["ray_axis"]
        bbs = [_wbb(o) for o in objs]
        self.x0 = math.floor(min(b[0] for b in bbs)/self.cs)*self.cs
        self.y0 = math.floor(min(b[1] for b in bbs)/self.cs)*self.cs
        self.x1 = math.ceil(max(b[3] for b in bbs)/self.cs)*self.cs
        self.y1 = math.ceil(max(b[4] for b in bbs)/self.cs)*self.cs
        self.nx = int(round((self.x1-self.x0)/self.cs))
        self.ny = int(round((self.y1-self.y0)/self.cs))
        self.bvh = bvh
        self.cells = {}   # floor index -> set((i,j))
        for f in floors:
            s = set()
            for i in range(self.nx):
                cx = self.x0 + (i+0.5)*self.cs
                for j in range(self.ny):
                    cy = self.y0 + (j+0.5)*self.cs
                    if inside(bvh, (cx, cy, f["zmid"]), self.axis):
                        s.add((i, j))
            self.cells[f["index"]] = s
            f["plate_area"] = round(len(s)*self.cs*self.cs, 1)
            if s:
                xs=[c[0] for c in s]; ys=[c[1] for c in s]
                f["bbox"] = [round(self.x0+min(xs)*self.cs,2), round(self.y0+min(ys)*self.cs,2),
                             round(self.x0+(max(xs)+1)*self.cs,2), round(self.y0+(max(ys)+1)*self.cs,2)]
            else:
                f["bbox"] = [0,0,0,0]

    def cell_center(self, i, j):
        return (self.x0+(i+0.5)*self.cs, self.y0+(j+0.5)*self.cs)

    def cell_rect(self, i, j):
        return (self.x0+i*self.cs, self.y0+j*self.cs,
                self.x0+(i+1)*self.cs, self.y0+(j+1)*self.cs)

    def occupied_xy(self, idx, x, y):
        i = int((x-self.x0)//self.cs); j = int((y-self.y0)//self.cs)
        return (i, j) in self.cells.get(idx, set())


# =============================================================================
#  PROGRAM CLASSIFICATION
# =============================================================================
def classify(name, cfg):
    n = name.lower()
    for kws, cat in cfg["program_keywords"]:
        if any(k in n for k in kws):
            return cat
    return "default"

def floor_categories(f, cfg):
    cats = {}
    for p in f.get("programs", []):
        c = classify(p, cfg)
        cats.setdefault(c, []).append(p)
    return cats


# =============================================================================
#  STRUCTURAL GRID
# =============================================================================
def build_grid(occ, floors, cfg):
    g = cfg["grid"]; s = g["spacing"]
    if g["anchor"] == "origin":
        ax, ay = 0.0, 0.0
    elif isinstance(g["anchor"], (list, tuple)):
        ax, ay = g["anchor"]
    else:  # centroid of widest floor
        wf = max(floors, key=lambda f: f["plate_area"])
        b = wf["bbox"]; ax, ay = (b[0]+b[2])/2, (b[1]+b[3])/2

    def lines(lo, hi, anchor):
        out = []; k = math.floor((lo-anchor)/s)
        while anchor + k*s <= hi + 1e-6:
            v = round(anchor + k*s, 3)
            if lo-1e-6 <= v <= hi+1e-6: out.append(v)
            k += 1
        return out

    GX = lines(occ.x0, occ.x1, ax)
    GY = lines(occ.y0, occ.y1, ay)
    if g["snap_to_edges"]:
        for f in floors:
            b = f["bbox"]
            for v in (b[0], b[2]):
                if all(abs(v-x) > 0.4 for x in GX): GX.append(round(v,3))
            for v in (b[1], b[3]):
                if all(abs(v-y) > 0.4 for y in GY): GY.append(round(v,3))
        GX = sorted(set(GX)); GY = sorted(set(GY))
    return GX, GY, (ax, ay)


# =============================================================================
#  MAIN GENERATE
# =============================================================================
def generate(cfg=None):
    cfg = cfg or DEFAULT_CONFIG
    report = {"config_echo": {k: cfg[k] for k in ("grid","members","bays")},
              "collections": {}, "validation": {}}

    # materials
    MAT = {
        "core":   _mat("AS_core",   (0.35,0.35,0.38,1)),
        "shaft":  _mat("AS_shaft",  (0.1,0.7,0.8,0.25), 0.25),
        "col":    _mat("AS_col",    (0.2,0.22,0.28,1)),
        "beam":   _mat("AS_beam",   (0.85,0.45,0.1,1)),
        "trans":  _mat("AS_trans",  (0.85,0.1,0.1,1)),
        "slab":   _mat("AS_slab",   (0.75,0.75,0.72,1)),
        "glass":  _mat("AS_glass",  (0.4,0.55,0.75,0.18), 0.18),
        "fin":    _mat("AS_fin",    (0.12,0.13,0.16,1), 1.0, 0.8),
        "grid":   _mat("AS_grid",   (0.1,0.8,0.2,1)),
        "dwall":  _mat("AS_dwall",  (0.30,0.30,0.32,1)),
        "gbeam":  _mat("AS_gbeam",  (0.45,0.40,0.30,1)),
    }
    COL = {n: _coll(n) for n in GEN_COLLECTIONS}
    if cfg["clear_previous"]:
        for c in COL.values():
            for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)

    # ---- input + analysis ----
    objs = gather_massing(cfg)
    if not objs:
        raise RuntimeError("No massing meshes found for the chosen input mode.")
    bvh = build_bvh(objs)
    floors = detect_floors(objs, cfg)
    occ = OccGrid(bvh, floors, cfg, objs)
    idxs = [f["index"] for f in floors]
    fmap = {f["index"]: f for f in floors}
    base_idx = idxs[0]
    roof_z = max(f["z1"] for f in floors)
    found_z = min(f["z0"] for f in floors)        # foundation level (lowest floor bottom)
    grade_z = cfg["floors"]["grade_z"]

    M = cfg["members"]

    # ===================================================================
    # CORE + SHAFTS
    # ===================================================================
    core_recs = []
    if cfg["core"]["mode"] == "detect":
        kws = cfg["core"]["detect_keywords"]
        groups = {}
        for o in objs:
            ln = o.name.lower()
            if any(k in ln for k in kws):
                key = re.sub(r"_(B\d+|L\d+)(?:_\d+)?$", "", o.name)  # group by base name
                groups.setdefault(key, []).append(_wbb(o))
        for key, bbs in groups.items():
            fp = [min(b[0] for b in bbs), min(b[1] for b in bbs),
                  max(b[3] for b in bbs), max(b[4] for b in bbs)]
            core_recs.append({"name": key, "fp": fp})
    if not core_recs:  # auto: central core sized to smallest upper floor
        up = [f for f in floors if f["z0"] >= grade_z and f["plate_area"] > 0]
        sm = min(up, key=lambda f: f["plate_area"]) if up else floors[-1]
        b = sm["bbox"]; cx, cy = (b[0]+b[2])/2, (b[1]+b[3])/2
        area = sm["plate_area"]*cfg["core"]["auto_size_fraction"]
        h = math.sqrt(max(area, 9.0))
        core_recs.append({"name": "core_auto",
                          "fp": [cx-h/2, cy-h/2, cx+h/2, cy+h/2]})

    TW = cfg["core"]["wall_thickness"]
    ctop = roof_z if cfg["core"]["continuous_to_roof"] else max(f["z1"] for f in floors)
    shaft_count = 0
    for r in core_recs:
        x0,y0,x1,y1 = r["fp"]
        _box(f"{r['name']}_wS", x0,y0,found_z, x1,y0+TW,ctop, COL["CORE"], MAT["core"])
        _box(f"{r['name']}_wN", x0,y1-TW,found_z, x1,y1,ctop, COL["CORE"], MAT["core"])
        _box(f"{r['name']}_wW", x0,y0+TW,found_z, x0+TW,y1-TW,ctop, COL["CORE"], MAT["core"])
        _box(f"{r['name']}_wE", x1-TW,y0+TW,found_z, x1,y1-TW,ctop, COL["CORE"], MAT["core"])
        _box(f"{r['name']}_shaft", x0+TW,y0+TW,found_z, x1-TW,y1-TW,ctop, COL["SHAFTS"], MAT["shaft"])
        shaft_count += 1
        r["z"] = [found_z, ctop]
    core_boxes = [_wbb(o) for o in COL["CORE"].objects]

    # ===================================================================
    # GRID
    # ===================================================================
    GX, GY, anchor = build_grid(occ, floors, cfg)
    # draw grid lines on grade
    gv=[]; ge=[]
    wf = max(floors, key=lambda f: f["plate_area"])["bbox"]
    for gx in GX:
        i=len(gv); gv += [(gx,wf[1],grade_z),(gx,wf[3],grade_z)]; ge.append((i,i+1))
    for gy in GY:
        i=len(gv); gv += [(wf[0],gy,grade_z),(wf[2],gy,grade_z)]; ge.append((i,i+1))
    gm = bpy.data.meshes.new("master_grid"); gm.from_pydata(gv, ge, []); gm.update()
    go = bpy.data.objects.new("master_grid", gm); COL["GRID"].objects.link(go); go.data.materials.append(MAT["grid"])

    # ===================================================================
    # COLUMNS  (foundation reachability + transfer detection)
    # ===================================================================
    def occ_pt(idx, x, y):
        return occ.occupied_xy(idx, x, y)

    longspan_levels = {}   # idx -> True if floor has a long-span program (column thinning)
    for f in floors:
        cats = floor_categories(f, cfg)
        longspan_levels[f["index"]] = "assembly_longspan" in cats

    hc = M["column"]/2; hct = M["column_transfer"]/2
    columns = []          # dicts: x,y,z0,z1,grounded,base_idx
    col_at = {idx: set() for idx in idxs}     # grid pts with a column touching slab idx
    transfers = []        # (x,y,z_base,base_idx)
    for gx in GX:
        for gy in GY:
            present = [idx for idx in idxs if occ_pt(idx, gx, gy)]
            if not present: continue
            # contiguous runs over consecutive floor indices
            runs=[]; cur=[present[0]]
            for k in range(1, len(present)):
                if present[k] == cur[-1]+1: cur.append(present[k])
                else: runs.append(cur); cur=[present[k]]
            runs.append(cur)
            for run in runs:
                a, b = run[0], run[-1]
                z0 = fmap[a]["z0"]; z1 = fmap[b]["z1"]
                grounded = (a == base_idx)
                if not grounded:
                    transfers.append((gx, gy, z0, a))
                halfc = hc if grounded else hct
                _box(f"col_{gx:+.1f}_{gy:+.1f}_{z0:.0f}".replace('.','p'),
                     gx-halfc,gy-halfc,z0, gx+halfc,gy+halfc,z1, COL["COLUMNS"], MAT["col"])
                columns.append({"x":gx,"y":gy,"z0":round(z0,2),"z1":round(z1,2),
                                "grounded":grounded,"base_idx":a})
                for idx in run:
                    col_at[idx].add((gx,gy))

    # transfer girders: tie each hung column base to nearest grounded column on its row/col
    grounded_xy = [(c["x"],c["y"]) for c in columns if c["grounded"]]
    tw=M["transfer_w"]/2; td=M["transfer_d"]
    done=set()
    for (gx,gy,zb,a) in transfers:
        key=(round(gx,1),round(gy,1),round(zb,1))
        if key in done: continue
        done.add(key)
        same_row=[x for (x,y) in grounded_xy if abs(y-gy)<0.6]
        same_col=[y for (x,y) in grounded_xy if abs(x-gx)<0.6]
        if same_row:
            tx=min(same_row,key=lambda x:abs(x-gx)); x0,x1=sorted([tx,gx])
            _box(f"transfer_X_{gy:+.0f}_{zb:.0f}".replace('.','p'),
                 x0,gy-tw,zb-td, x1,gy+tw,zb, COL["BEAMS"], MAT["trans"])
        elif same_col:
            ty=min(same_col,key=lambda y:abs(y-gy)); y0,y1=sorted([ty,gy])
            _box(f"transfer_Y_{gx:+.0f}_{zb:.0f}".replace('.','p'),
                 gx-tw,y0,zb-td, gx+tw,y1,zb, COL["BEAMS"], MAT["trans"])

    # ===================================================================
    # BEAMS  (connect adjacent columns per slab, both axes)
    # ===================================================================
    bw=M["beam_w"]/2; bd=M["beam_d"]
    beam_count=0
    def beams_for(level_pts, z, tag):
        nonlocal beam_count
        byrow={}; bycol={}
        for (x,y) in level_pts: byrow.setdefault(round(y,3),[]).append(x); bycol.setdefault(round(x,3),[]).append(y)
        for y,xs in byrow.items():
            xs=sorted(set(xs))
            for a,b in zip(xs,xs[1:]):
                _box(f"beam_{tag}_X_{a:+.0f}_{b:+.0f}_{y:+.0f}".replace('.','p'),
                     a,y-bw,z-bd, b,y+bw,z, COL["BEAMS"], MAT["beam"]); beam_count+=1
        for x,ys in bycol.items():
            ys=sorted(set(ys))
            for a,b in zip(ys,ys[1:]):
                _box(f"beam_{tag}_Y_{x:+.0f}_{a:+.0f}_{b:+.0f}".replace('.','p'),
                     x-bw,a,z-bd, x+bw,b,z, COL["BEAMS"], MAT["beam"]); beam_count+=1
    for f in floors:
        beams_for(col_at[f["index"]], f["z0"], f"L{f['index']}")
    # roof framing over top floor
    top_pts = col_at[idxs[-1]]
    beams_for(top_pts, roof_z, "ROOF")

    # core ring beams every floor (so cores are framed with beams+columns)
    for r in core_recs:
        x0,y0,x1,y1 = r["fp"]
        for f in floors:
            z=f["z0"]
            if z < r["z"][0]-0.1 or z > r["z"][1]+0.1: continue
            _box(f"beam_corering_{r['name']}_L{f['index']}_S".replace('.','p'),x0,y0-bw,z-bd,x1,y0+bw,z,COL["BEAMS"],MAT["beam"])
            _box(f"beam_corering_{r['name']}_L{f['index']}_N".replace('.','p'),x0,y1-bw,z-bd,x1,y1+bw,z,COL["BEAMS"],MAT["beam"])
            _box(f"beam_corering_{r['name']}_L{f['index']}_W".replace('.','p'),x0-bw,y0,z-bd,x0+bw,y1,z,COL["BEAMS"],MAT["beam"])
            _box(f"beam_corering_{r['name']}_L{f['index']}_E".replace('.','p'),x1-bw,y0,z-bd,x1+bw,y1,z,COL["BEAMS"],MAT["beam"])
            beam_count+=4

    # ===================================================================
    # SLABS  (voxel plate per floor -> follows arbitrary shape, leaves atrium holes)
    # ===================================================================
    st=M["slab_t"]; slab_count=0
    def voxel_slab(idx, ztop, name):
        nonlocal slab_count
        cells = occ.cells.get(idx, set())
        if not cells: return
        verts=[]; faces=[]
        for (i,j) in cells:
            rx0,ry0,rx1,ry1 = occ.cell_rect(i,j)
            base=len(verts)
            verts += [(rx0,ry0,ztop-st),(rx1,ry0,ztop-st),(rx1,ry1,ztop-st),(rx0,ry1,ztop-st),
                      (rx0,ry0,ztop),(rx1,ry0,ztop),(rx1,ry1,ztop),(rx0,ry1,ztop)]
            faces += [(base,base+1,base+2,base+3),(base+4,base+5,base+6,base+7),
                      (base,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),
                      (base+2,base+3,base+7,base+6),(base+3,base,base+4,base+7)]
        me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
        ob=bpy.data.objects.new(name,me); COL["SLABS"].objects.link(ob); ob.data.materials.append(MAT["slab"])
        slab_count+=1
    for f in floors:
        voxel_slab(f["index"], f["z0"], f"slab_L{f['index']}")
    voxel_slab(idxs[-1], roof_z, "slab_ROOF")

    # ===================================================================
    # ROOFS on terminated masses + extend columns/beams to them
    # ===================================================================
    masstop=0; roof_cols=0
    for k in range(len(idxs)-1):
        lo, up = idxs[k], idxs[k+1]
        diff = occ.cells[lo] - occ.cells[up]          # cells present below, gone above
        if not diff: continue
        ztop = fmap[up]["z0"]
        if ztop < grade_z - 1e-6: continue
        # roof voxel slab over the exposed cells
        verts=[]; faces=[]
        for (i,j) in diff:
            rx0,ry0,rx1,ry1 = occ.cell_rect(i,j); base=len(verts)
            verts += [(rx0,ry0,ztop-st),(rx1,ry0,ztop-st),(rx1,ry1,ztop-st),(rx0,ry1,ztop-st),
                      (rx0,ry0,ztop),(rx1,ry0,ztop),(rx1,ry1,ztop),(rx0,ry1,ztop)]
            faces += [(base,base+1,base+2,base+3),(base+4,base+5,base+6,base+7),
                      (base,base+1,base+5,base+4),(base+1,base+2,base+6,base+5),
                      (base+2,base+3,base+7,base+6),(base+3,base,base+4,base+7)]
        me=bpy.data.meshes.new(f"roof_masstop_L{lo}"); me.from_pydata(verts,[],faces); me.update()
        ob=bpy.data.objects.new(f"roof_masstop_L{lo}",me); COL["SLABS"].objects.link(ob); ob.data.materials.append(MAT["slab"])
        masstop+=1
        # extend columns up to ztop + roof beams at grid pts inside diff region
        rpts=[]
        for gx in GX:
            for gy in GY:
                i=int((gx-occ.x0)//occ.cs); j=int((gy-occ.y0)//occ.cs)
                if (i,j) in diff:
                    # existing top at this xy
                    tops=[c["z1"] for c in columns if abs(c["x"]-gx)<0.4 and abs(c["y"]-gy)<0.4]
                    base_z = max(tops) if tops else fmap[lo]["z0"]
                    if base_z < ztop-0.1:
                        _box(f"col_roof_L{lo}_{gx:+.1f}_{gy:+.1f}".replace('.','p'),
                             gx-hc,gy-hc,base_z, gx+hc,gy+hc,ztop, COL["COLUMNS"], MAT["col"]); roof_cols+=1
                    rpts.append((gx,gy))
        beams_for(rpts, ztop, f"roofL{lo}")

    # ===================================================================
    # CURTAIN WALL  (boundary of each floor's occupancy -> follows steps/terraces)
    # ===================================================================
    cw_count=0
    if cfg["curtain"]["enable"]:
        ct=M["curtain_t"]
        for f in floors:
            if cfg["curtain"]["start_at_grade"] and f["z1"] <= grade_z+1e-6:
                continue
            idx=f["index"]; cells=occ.cells[idx]
            z0=max(f["z0"], grade_z) if cfg["curtain"]["start_at_grade"] else f["z0"]
            z1=f["z1"]
            for (i,j) in cells:
                rx0,ry0,rx1,ry1 = occ.cell_rect(i,j)
                if (i-1,j) not in cells:  # west edge exposed
                    _box(f"cw_L{idx}_W_{i}_{j}", rx0-ct/2,ry0,z0, rx0+ct/2,ry1,z1, COL["CURTAIN_WALL"], MAT["glass"]); cw_count+=1
                if (i+1,j) not in cells:
                    _box(f"cw_L{idx}_E_{i}_{j}", rx1-ct/2,ry0,z0, rx1+ct/2,ry1,z1, COL["CURTAIN_WALL"], MAT["glass"]); cw_count+=1
                if (i,j-1) not in cells:
                    _box(f"cw_L{idx}_S_{i}_{j}", rx0,ry0-ct/2,z0, rx1,ry0+ct/2,z1, COL["CURTAIN_WALL"], MAT["glass"]); cw_count+=1
                if (i,j+1) not in cells:
                    _box(f"cw_L{idx}_N_{i}_{j}", rx0,ry1-ct/2,z0, rx1,ry1+ct/2,z1, COL["CURTAIN_WALL"], MAT["glass"]); cw_count+=1

    # ===================================================================
    # FACADE FINS  (mullion grid, vertical, merged over continuous boundary runs)
    # ===================================================================
    fin_count=0
    if cfg["fins"]["enable"]:
        F=cfg["fins"]; mull=F["mull"]
        struct_lines_x=set(round(x,2) for x in GX); struct_lines_y=set(round(y,2) for y in GY)
        # West/East faces -> fins along Y mullions; South/North -> along X mullions.
        # Collect, per (side, plane_cell_coord, mullion_pos), the z-intervals where boundary persists.
        from collections import defaultdict
        iv=defaultdict(list)
        def mlines(lo,hi):
            out=[]; k=math.floor(lo/mull)
            while k*mull<=hi+1e-6:
                if lo-1e-6<=k*mull<=hi+1e-6: out.append(round(k*mull,3))
                k+=1
            return out
        for f in floors:
            if f["z1"]<=grade_z+1e-6: continue
            idx=f["index"]; cells=occ.cells[idx]; z0=max(f["z0"],grade_z); z1=f["z1"]
            for (i,j) in cells:
                rx0,ry0,rx1,ry1=occ.cell_rect(i,j)
                if (i-1,j) not in cells:
                    for my in mlines(ry0,ry1): iv[("W",round(rx0,2),round(my,2))].append((z0,z1))
                if (i+1,j) not in cells:
                    for my in mlines(ry0,ry1): iv[("E",round(rx1,2),round(my,2))].append((z0,z1))
                if (i,j-1) not in cells:
                    for mx in mlines(rx0,rx1): iv[("S",round(ry0,2),round(mx,2))].append((z0,z1))
                if (i,j+1) not in cells:
                    for mx in mlines(rx0,rx1): iv[("N",round(ry1,2),round(mx,2))].append((z0,z1))
        def merge(ints):
            ints=sorted(ints); out=[list(ints[0])]
            for a,b in ints[1:]:
                if a<=out[-1][1]+0.01: out[-1][1]=max(out[-1][1],b)
                else: out.append([a,b])
            return out
        for (side,plane,mpos),ints in iv.items():
            for z0,z1 in merge(ints):
                if z1-z0 < F["min_run"]: continue
                on_struct = (mpos in struct_lines_y) if side in ("W","E") else (mpos in struct_lines_x)
                depth = F["depth_primary"] if on_struct else F["depth_infill"]
                half  = (F["width_primary"] if on_struct else F["width_infill"])/2
                if side=="W":   _box(f"fin_W_{mpos:+.1f}_{z0:.0f}".replace('.','p'), plane-depth,mpos-half,z0, plane,mpos+half,z1, COL["FACADE_FINS"], MAT["fin"])
                elif side=="E": _box(f"fin_E_{mpos:+.1f}_{z0:.0f}".replace('.','p'), plane,mpos-half,z0, plane+depth,mpos+half,z1, COL["FACADE_FINS"], MAT["fin"])
                elif side=="S": _box(f"fin_S_{mpos:+.1f}_{z0:.0f}".replace('.','p'), mpos-half,plane-depth,z0, mpos+half,plane,z1, COL["FACADE_FINS"], MAT["fin"])
                else:           _box(f"fin_N_{mpos:+.1f}_{z0:.0f}".replace('.','p'), mpos-half,plane,z0, mpos+half,plane+depth,z1, COL["FACADE_FINS"], MAT["fin"])
                fin_count+=1

    # ===================================================================
    # UNDERGROUND  (diaphragm wall around lowest occupied floor + grade beams)
    # ===================================================================
    dw_count=0; gb_count=0
    if cfg["underground"]["enable"] and found_z < grade_z - 1e-6:
        U=cfg["underground"]; T=U["diaphragm_thickness"]; toe=found_z-U["toe_below_foundation"]
        base_cells=occ.cells[base_idx]
        # diaphragm wall = thick boundary wall around base footprint, grade->toe
        for (i,j) in base_cells:
            rx0,ry0,rx1,ry1=occ.cell_rect(i,j)
            if (i-1,j) not in base_cells: _box(f"dwall_W_{i}_{j}", rx0-T,ry0,toe, rx0,ry1,grade_z, COL["DIAPHRAGM_WALL"], MAT["dwall"]); dw_count+=1
            if (i+1,j) not in base_cells: _box(f"dwall_E_{i}_{j}", rx1,ry0,toe, rx1+T,ry1,grade_z, COL["DIAPHRAGM_WALL"], MAT["dwall"]); dw_count+=1
            if (i,j-1) not in base_cells: _box(f"dwall_S_{i}_{j}", rx0,ry0-T,toe, rx1,ry0,grade_z, COL["DIAPHRAGM_WALL"], MAT["dwall"]); dw_count+=1
            if (i,j+1) not in base_cells: _box(f"dwall_N_{i}_{j}", rx0,ry1,toe, rx1,ry1+T,grade_z, COL["DIAPHRAGM_WALL"], MAT["dwall"]); dw_count+=1
        # grade beams at foundation: connect all columns whose base reaches found_z
        gw=U["grade_beam_w"]/2; gd=U["grade_beam_d"]
        fcols=sorted(set((round(c["x"],2),round(c["y"],2)) for c in columns if c["z0"]<=found_z+0.05))
        byrow={}; bycol={}
        for (x,y) in fcols: byrow.setdefault(y,[]).append(x); bycol.setdefault(x,[]).append(y)
        for y,xs in byrow.items():
            xs=sorted(set(xs))
            for a,b in zip(xs,xs[1:]):
                _box(f"gbeam_X_{a:+.0f}_{b:+.0f}_{y:+.0f}".replace('.','p'),a,y-gw,found_z-gd,b,y+gw,found_z,COL["GRADE_BEAMS"],MAT["gbeam"]); gb_count+=1
        for x,ys in bycol.items():
            ys=sorted(set(ys))
            for a,b in zip(ys,ys[1:]):
                _box(f"gbeam_Y_{x:+.0f}_{a:+.0f}_{b:+.0f}".replace('.','p'),x-gw,a,found_z-gd,x+gw,b,found_z,COL["GRADE_BEAMS"],MAT["gbeam"]); gb_count+=1
        for r in core_recs:
            x0,y0,x1,y1=r["fp"]
            _box(f"gbeam_core_{r['name']}_S".replace('.','p'),x0,y0-gw,found_z-gd,x1,y0+gw,found_z,COL["GRADE_BEAMS"],MAT["gbeam"])
            _box(f"gbeam_core_{r['name']}_N".replace('.','p'),x0,y1-gw,found_z-gd,x1,y1+gw,found_z,COL["GRADE_BEAMS"],MAT["gbeam"])
            _box(f"gbeam_core_{r['name']}_W".replace('.','p'),x0-gw,y0,found_z-gd,x0+gw,y1,found_z,COL["GRADE_BEAMS"],MAT["gbeam"])
            _box(f"gbeam_core_{r['name']}_E".replace('.','p'),x1-gw,y0,found_z-gd,x1+gw,y1,found_z,COL["GRADE_BEAMS"],MAT["gbeam"])
            gb_count+=4

    # ===================================================================
    # VALIDATION
    # ===================================================================
    col_objs=[_wbb(o) for o in COL["COLUMNS"].objects]
    beam_objs=[(o.name,_wbb(o)) for o in COL["BEAMS"].objects]
    girders=[b for n,b in beam_objs if n.startswith("transfer_")]
    grounded_set=[((b[0]+b[3])/2,(b[1]+b[4])/2) for b in col_objs if b[2]<=found_z+0.05]
    TOLV=0.4
    def supported_base(b):
        x=(b[0]+b[3])/2; y=(b[1]+b[4])/2; z=b[2]
        if z<=found_z+0.05: return True
        for g in girders:
            if g[0]-0.5<=x<=g[3]+0.5 and g[1]-0.5<=y<=g[4]+0.5 and abs(g[5]-z)<0.3: return True
        # column directly below
        for c in col_objs:
            cx=(c[0]+c[3])/2; cy=(c[1]+c[4])/2
            if abs(cx-x)<TOLV and abs(cy-y)<TOLV and abs(c[5]-z)<0.3: return True
        return False
    unsupported_cols=sum(0 if supported_base(b) else 1 for b in col_objs)

    def hard_pt(px,py,pz):
        for c in col_objs+core_boxes:
            if c[0]-TOLV<=px<=c[3]+TOLV and c[1]-TOLV<=py<=c[4]+TOLV and c[2]-0.6<=pz<=c[5]+0.6: return True
        return False
    single_ended=0
    for n,b in beam_objs:
        if max(b[3]-b[0],b[4]-b[1])<0.6: continue
        if (b[3]-b[0])>=(b[4]-b[1]):
            ym=(b[1]+b[4])/2; e1=(b[0],ym,b[5]); e2=(b[3],ym,b[5])
        else:
            xm=(b[0]+b[3])/2; e1=(xm,b[1],b[5]); e2=(xm,b[4],b[5])
        h1=hard_pt(*e1); h2=hard_pt(*e2)
        if not h1 and not h2: single_ended+=1

    # volumes
    def vol(coll):
        t=0
        for o in coll.objects:
            b=_wbb(o); t+=(b[3]-b[0])*(b[4]-b[1])*(b[5]-b[2])
        return round(t,1)

    report["analysis"]={
        "floors_detected":len(floors),"level_range":[idxs[0],idxs[-1]],
        "building_height_m":round(roof_z-found_z,2),"foundation_z":found_z,"roof_z":roof_z,
        "grid_lines":{"X":len(GX),"Y":len(GY),"spacing":cfg["grid"]["spacing"]},
        "transfer_levels":sorted(set(fmap[a]["index"] for (_,_,_,a) in transfers)),
    }
    report["counts"]={
        "cores":len(core_recs),"shafts":shaft_count,
        "columns":len(COL["COLUMNS"].objects),"beams":len(COL["BEAMS"].objects),
        "slabs":len(COL["SLABS"].objects),"curtain_panels":cw_count,"fins":fin_count,
        "diaphragm_segments":dw_count,"grade_beams":gb_count,
    }
    report["structural_volume_m3"]={
        "core":vol(COL["CORE"]),"columns":vol(COL["COLUMNS"]),"beams":vol(COL["BEAMS"]),
        "slabs":vol(COL["SLABS"]),"diaphragm_wall":vol(COL["DIAPHRAGM_WALL"]),
        "grade_beams":vol(COL["GRADE_BEAMS"]),
    }
    report["validation"]={
        "unsupported_columns":unsupported_cols,
        "single_ended_beams":single_ended,
        "result":"PASS" if (unsupported_cols==0 and single_ended==0) else "CHECK",
    }

    txt=cfg["report_name"]
    if txt in bpy.data.texts: bpy.data.texts.remove(bpy.data.texts[txt])
    bpy.data.texts.new(txt).write(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report["validation"], ensure_ascii=False),
          "| floors:", len(floors), "| columns:", report["counts"]["columns"],
          "| beams:", report["counts"]["beams"])
    return report


if __name__ == "__main__":
    generate(DEFAULT_CONFIG)
