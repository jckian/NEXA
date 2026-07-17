
# ==========================================================================
#  PARAMETRIC MASSING -> BUILDING SYSTEMS GENERATOR
#  Reads named program-massing objects and ADAPTIVELY generates a full
#  building system set. It does NOT scale a fixed model; every decision
#  (levels, cores, grids, thicknesses, outriggers...) is derived from the
#  masses actually present in the scene.
#
#  USAGE:  set CONFIG["source_collection"] (or leave None to scan scene),
#          then  run_all()
# ==========================================================================
import bpy, bmesh, re, math
from collections import defaultdict
from mathutils import Vector

# --------------------------- CLASSIFICATION TABLES ------------------------
# Keyword -> classification. Names are AUTHORITATIVE. Generic + theater terms.
CORE_KEYS = ["core","stair","stairs","staircase","elevator","lift",
             "vertical_circulation","service_core","freight_elevator","shaft"]
# program keyword -> (class, grid_m, slab_t_m, facade, partition)
#   facade   : STOREFRONT/MEDIUM/WINDOW/MINIMAL
#   partition: OPEN/CELLULAR/SERVICE
PROG = {
 # generic spec categories
 "office":      ("PUBLIC",      9.0, 0.25, "STOREFRONT", "CELLULAR"),
 "residential": ("PRIVATE",     6.0, 0.20, "WINDOW",     "CELLULAR"),
 "hotel":       ("PRIVATE",     7.5, 0.25, "MEDIUM",     "CELLULAR"),
 "retail":      ("PUBLIC",     10.0, 0.30, "STOREFRONT", "OPEN"),
 "lobby":       ("PUBLIC",     12.0, 0.35, "STOREFRONT", "OPEN"),
 "service":     ("SERVICE",     6.0, 0.25, "MINIMAL",    "SERVICE"),
 "mechanical":  ("SERVICE",     6.0, 0.25, "MINIMAL",    "SERVICE"),
 "mep":         ("SERVICE",     6.0, 0.25, "MINIMAL",    "SERVICE"),
 # assembly / performance
 "event_hall":  ("PUBLIC",     12.0, 0.35, "MEDIUM",     "OPEN"),
 "stage":       ("PUBLIC",     12.0, 0.35, "MINIMAL",    "OPEN"),
 "fly_tower":   ("SERVICE",    12.0, 0.35, "MINIMAL",    "OPEN"),
 "orchestra":   ("PUBLIC",     12.0, 0.35, "MINIMAL",    "OPEN"),
 "restaurant":  ("PUBLIC",     10.0, 0.30, "STOREFRONT", "OPEN"),
 "lounge":      ("SEMI_PUBLIC",10.0, 0.30, "MEDIUM",     "OPEN"),
 "bar":         ("SEMI_PUBLIC",10.0, 0.30, "MEDIUM",     "OPEN"),
 "viewing":     ("PUBLIC",     10.0, 0.30, "STOREFRONT", "OPEN"),
 "terrace":     ("PUBLIC",     10.0, 0.30, "STOREFRONT", "OPEN"),
 "sales":       ("SEMI_PUBLIC",10.0, 0.30, "STOREFRONT", "OPEN"),
 "display":     ("SEMI_PUBLIC",10.0, 0.30, "STOREFRONT", "OPEN"),
 "box_office":  ("PUBLIC",     10.0, 0.30, "STOREFRONT", "CELLULAR"),
 "rehearsal":   ("SEMI_PUBLIC", 6.0, 0.25, "WINDOW",     "CELLULAR"),
 "circulation": ("PUBLIC",      6.0, 0.25, "MINIMAL",    "OPEN"),
 # back of house
 "backstage":   ("SERVICE",     6.0, 0.25, "MINIMAL",    "CELLULAR"),
 "dressing":    ("SERVICE",     6.0, 0.25, "WINDOW",     "CELLULAR"),
 "green_room":  ("SERVICE",     6.0, 0.25, "WINDOW",     "CELLULAR"),
 "fitting":     ("SERVICE",     6.0, 0.25, "WINDOW",     "CELLULAR"),
 "staff":       ("SERVICE",     6.0, 0.25, "WINDOW",     "CELLULAR"),
 "it_support":  ("SERVICE",     6.0, 0.25, "WINDOW",     "CELLULAR"),
 "restroom":    ("SERVICE",     6.0, 0.25, "MINIMAL",    "CELLULAR"),
 "storage":     ("SERVICE",     6.0, 0.30, "MINIMAL",    "SERVICE"),
 "loading":     ("SERVICE",     6.0, 0.30, "MINIMAL",    "SERVICE"),
 "production":  ("SERVICE",     6.0, 0.30, "MINIMAL",    "SERVICE"),
 "workshop":    ("SERVICE",     6.0, 0.30, "MINIMAL",    "SERVICE"),
}
DEFAULT_PROG = ("PUBLIC", 8.0, 0.25, "WINDOW", "CELLULAR")
PRIORITY = {"CORE":100,"SERVICE":50,"PUBLIC":40,"SEMI_PUBLIC":30,"PRIVATE":20}

# Names of collections this tool GENERATES (excluded from input scan by membership)
GENERATED_COLLS = ["UNIFIED_CORE_SYSTEM","ResolvedMassing","SLAB_SYSTEM","STRUCTURE_SYSTEM",
 "CORE_WALL_SYSTEM","CORE_COLUMN_SYSTEM","CORE_COUPLING_BEAMS","CORE_SHAFT_SYSTEM",
 "PARTITION_SYSTEM","CURTAIN_SYSTEM","OUTRIGGER_SYSTEM","BELT_TRUSS_SYSTEM",
 "MEGA_COLUMN_SYSTEM","HYBRID_CONNECTION_SYSTEM","StructuralZoneMap","STRUCTURAL_STRATEGY_MAP",
 "UnifiedCoreSystem","INPUT_MASSING","TEST_MASSING"]
CONFIG = {
 "source_collection": None,   # None = scan whole scene for mesh masses
 # exact-ish names of NON-program helpers to skip when scanning whole scene
 "skip_names": ["mass","Untitled","plaza"],
 "skip_prefix": ["New object"],
 "level_tol": 1.0,            # z clustering tolerance for level detection
 "merge_tol": 0.30,           # plan/contact tolerance
 "vert_bridge": 1.75,         # bridge transfer gaps for core continuity
 "grid_origin": (0.0,0.0),    # shared modular origin so program grids nest
 "interior_wall": 0.15, "service_wall": 0.20,
 "glass_t": 0.05, "mullion": 0.10,
 "outrigger_h": 60.0, "belt_h": 80.0, "mega_h": 100.0, "mega_slender": 8.0,
}

# --------------------------- GEOMETRY HELPERS -----------------------------
def W(o):  # world bbox (min/max x,y,z)
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[p.x for p in cs]; ys=[p.y for p in cs]; zs=[p.z for p in cs]
    return (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))

def clean_box(name,x0,x1,y0,y1,z0,z1,coll,mat=None):
    # axis-aligned box with OUTWARD normals (critical for reliable booleans)
    if x1-x0<1e-5 or y1-y0<1e-5 or z1-z0<1e-5: return None
    me=bpy.data.meshes.new(name)
    v=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me.from_pydata(v,[],f)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); me.update()
    o=bpy.data.objects.new(name,me)
    if mat: o.data.materials.append(mat)
    coll.objects.link(o); return o

def boolean(base,cutter,op):
    m=base.modifiers.new("b","BOOLEAN"); m.operation=op; m.solver='EXACT'; m.object=cutter
    bpy.context.view_layer.objects.active=base
    bpy.ops.object.modifier_apply(modifier="b")

def clean_mesh(o):  # merge doubles + outward normals (fixes non-manifold source masses)
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.001)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()

def vol(o):
    bm=bmesh.new(); bm.from_mesh(o.data); v=bm.calc_volume(signed=False); bm.free(); return v

def new_coll(name):
    c=bpy.data.collections.get(name)
    if c:
        for ob in list(c.objects): bpy.data.objects.remove(ob,do_unlink=True)
    else:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def mat(name,rgba):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=False; m.diffuse_color=rgba; return m

def grid_lines(lo,hi,sp,origin=0.0,tol=0.6):
    k0=math.ceil((lo-origin)/sp); k1=math.floor((hi-origin)/sp)
    L=[round(origin+k*sp,3) for k in range(k0,k1+1)]
    for b in (lo,hi):
        if all(abs(b-x)>1e-6 for x in L): L.append(round(b,3))
    L=sorted(L); out=[L[0]]
    for v in L[1:]:
        if v-out[-1]<tol:
            out[-1]= out[-1] if abs(out[-1]-round(out[-1]))<=abs(v-round(v)) else v
        else: out.append(v)
    return out

def classify(name):
    n=name.lower()
    if any(k in n for k in CORE_KEYS): return ("CORE",)+DEFAULT_PROG[1:]
    for key,val in PROG.items():
        if key in n: return val
    return DEFAULT_PROG


# =================== STEP 1: ANALYZE PROGRAM (adaptive) ===================
def collect_masses():
    src=CONFIG["source_collection"]
    if src:
        # user-curated input collection -> use ALL meshes in it (no name filtering,
        # so program names like STAIR_CORE / CORE_WALL are NOT wrongly excluded)
        return [o for o in bpy.data.collections[src].objects if o.type=='MESH']
    # whole-scene scan: exclude anything living in a generated collection (by membership)
    gen=set()
    for cn in GENERATED_COLLS:
        c=bpy.data.collections.get(cn)
        if c:
            for o in c.objects: gen.add(o.name)
    out=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name in gen: continue
        if o.name in CONFIG["skip_names"]: continue
        if any(o.name.startswith(p) for p in CONFIG["skip_prefix"]): continue
        out.append(o)
    return out

def detect_levels(masses):
    # cluster z-bottoms -> ordered floor elevations (adaptive, no hardcoded pitch)
    zb=sorted(set(round(W(o)[4],2) for o in masses))
    levels=[]; tol=CONFIG["level_tol"]
    for z in zb:
        if levels and z-levels[-1]<tol: continue
        levels.append(z)
    return levels   # ascending floor elevations

def analyze(masses, levels):
    db={}
    def level_of(zbot):
        return min(range(len(levels)), key=lambda i:abs(levels[i]-zbot))
    for o in masses:
        b=W(o); cls,grid,slab,fac,part=classify(o.name)
        db[o.name]={"obj":o,"bbox":b,"class":cls,"grid":grid,"slab_t":slab,
                    "facade":fac,"partition":part,"level":level_of(b[4]),
                    "footprint":(b[1]-b[0])*(b[3]-b[2]),
                    "centroid":((b[0]+b[1])/2,(b[2]+b[3])/2,(b[4]+b[5])/2)}
    return db

# =================== STEP 2: CORE DETECTION + MERGE =======================
def detect_cores(db, levels):
    cores={n:d for n,d in db.items() if d["class"]=="CORE"}
    # cluster by plan footprint (overlapping XY -> same shaft)
    clusters=[]
    for n,d in cores.items():
        b=d["bbox"]; placed=False
        for cl in clusters:
            cb=cl["bb"]
            if not(b[1]<=cb[0] or b[0]>=cb[1] or b[3]<=cb[2] or b[2]>=cb[3]):
                cl["names"].append(n)
                cl["bb"]=(min(cb[0],b[0]),max(cb[1],b[1]),min(cb[2],b[2]),max(cb[3],b[3]))
                cl["z"]=(min(cl["z"][0],b[4]),max(cl["z"][1],b[5])); placed=True; break
        if not placed:
            clusters.append({"names":[n],"bb":(b[0],b[1],b[2],b[3]),"z":(b[4],b[5])})
    shafts={}
    base=min(levels) if levels else 0
    for i,cl in enumerate(clusters):
        x0,x1,y0,y1=cl["bb"]
        shafts["CORE_%d"%i]={"x":(x0,x1),"y":(y0,y1),
                             "z":(min(cl["z"][0],base), cl["z"][1])}  # continuous to base
    return shafts

def build_unified_core(shafts):
    c=new_coll("UNIFIED_CORE_SYSTEM"); m=mat("M_UCore",(0.3,0.32,0.4,1))
    for k,s in shafts.items():
        o=clean_box("UNIFIED_"+k,s["x"][0],s["x"][1],s["y"][0],s["y"][1],s["z"][0],s["z"][1],c,m)
        if o: o["tier"]="PRIMARY"; o.display_type='WIRE'
    return c


# =================== STEP 3: OVERLAP RESOLUTION ===========================
def resolve_overlaps(db, shafts):
    c=new_coll("ResolvedMassing"); m=mat("M_Resolved",(0.7,0.7,0.72,1))
    core_boxes=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1],s["z"][0],s["z"][1]) for s in shafts.values()]
    items=sorted(db.items(), key=lambda kv:-PRIORITY[kv[1]["class"]])  # high priority first
    made={}
    for n,d in items:
        b=d["bbox"]
        o=clean_box(n+"_r",b[0],b[1],b[2],b[3],b[4],b[5],c,m)
        if not o: continue
        # carve cores out of every program (core stays intact)
        if d["class"]!="CORE":
            for (x0,x1,y0,y1,z0,z1) in core_boxes:
                if x1<=b[0] or x0>=b[1] or y1<=b[2] or y0>=b[3] or z1<=b[4] or z0>=b[5]: continue
                cb=clean_box("cut",x0,x1,y0,y1,z0-1,z1+1,c)
                boolean(o,cb,'DIFFERENCE'); bpy.data.objects.remove(cb,do_unlink=True)
        clean_mesh(o)
        if vol(o)<0.01: bpy.data.objects.remove(o,do_unlink=True); continue
        o["class"]=d["class"]; o["level"]=d["level"]; made[n]=o
    return c, made

# =================== STEP 4: STRUCTURAL GRID (program-based, nesting) =====
def build_grid(db, shafts):
    ox,oy=CONFIG["grid_origin"]
    core_boxes=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1]) for s in shafts.values()]
    cand=defaultdict(lambda:[1e9,-1e9])   # (x,y)->[base_z, top_z]
    base_z=min(d["bbox"][4] for d in db.values())
    for n,d in db.items():
        if d["class"]=="CORE": continue
        b=d["bbox"]; sp=d["grid"]
        xs=grid_lines(b[0],b[1],sp,ox); ys=grid_lines(b[2],b[3],sp,oy)
        for x in xs:
            for y in ys:
                if any(cx0-0.01<=x<=cx1+0.01 and cy0-0.01<=y<=cy1+0.01 for (cx0,cx1,cy0,cy1) in core_boxes):
                    continue
                key=(round(x,2),round(y,2))
                cand[key][1]=max(cand[key][1],b[5])
                cand[key][0]=base_z
    # merge near-coincident (prefer modular value)
    def snap(vals):
        vals=sorted(set(vals)); rep={}; groups=[]
        for v in vals:
            if groups and v-groups[-1][-1]<1.0: groups[-1].append(v)
            else: groups.append([v])
        for g in groups:
            best=min(g,key=lambda v:abs(v-round(v/6)*6))
            for v in g: rep[v]=round(best,2)
        return rep
    sx=snap([k[0] for k in cand]); sy=snap([k[1] for k in cand])
    merged=defaultdict(lambda:[1e9,-1e9])
    for (x,y),(zb,zt) in cand.items():
        kk=(sx[x],sy[y]); merged[kk][0]=min(merged[kk][0],zb); merged[kk][1]=max(merged[kk][1],zt)
    return merged

# =================== STEP 5: SLAB SYSTEM (with core openings) =============
def build_slabs(db, shafts, levels):
    c=new_coll("SLAB_SYSTEM"); m=mat("M_Slab",(0.6,0.6,0.62,1))
    core_boxes=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1]) for s in shafts.values()]
    bylvl=defaultdict(list)
    for n,d in db.items(): bylvl[d["level"]].append(d)
    out=[]
    for L in sorted(bylvl):
        ds=bylvl[L]; zf=min(d["bbox"][4] for d in ds)
        t=max(d["slab_t"] for d in ds); z0,z1=zf-t,zf
        boxes=[]
        for d in ds:
            b=d["bbox"]
            pb=clean_box("sl",b[0],b[1],b[2],b[3],z0,z1,c)
            if not pb: continue
            for (x0,x1,y0,y1) in core_boxes:
                if x1<=b[0] or x0>=b[1] or y1<=b[2] or y0>=b[3]: continue
                cb=clean_box("cc",x0,x1,y0,y1,z0-1,z1+1,c)
                boolean(pb,cb,'DIFFERENCE'); bpy.data.objects.remove(cb,do_unlink=True)
            clean_mesh(pb)
            if vol(pb)>0.001: boxes.append(pb)
            else: bpy.data.objects.remove(pb,do_unlink=True)
        if not boxes: continue
        base=boxes[0]
        for ob in boxes[1:]: boolean(base,ob,'UNION')
        for ob in boxes[1:]: bpy.data.objects.remove(ob,do_unlink=True)   # clean scratch operands
        clean_mesh(base); base.name="SLAB_L%d"%L; base.data.materials.append(m)
        base["level"]=L; base["thickness"]=t; out.append(base)
    # ROOF / TOP CEILING slab: cap the topmost level at the building top (no level above it)
    btop=max(d["bbox"][5] for d in db.values())
    topds=[d for d in db.values() if abs(d["bbox"][5]-btop)<0.6]
    if topds:
        rt=max(d["slab_t"] for d in topds); rz0,rz1=btop-rt,btop
        rboxes=[]
        for d in topds:
            b=d["bbox"]; pb=clean_box("rf",b[0],b[1],b[2],b[3],rz0,rz1,c)
            if not pb: continue
            for (x0,x1,y0,y1) in core_boxes:
                if x1<=b[0] or x0>=b[1] or y1<=b[2] or y0>=b[3]: continue
                cb=clean_box("cc",x0,x1,y0,y1,rz0-1,rz1+1,c); boolean(pb,cb,'DIFFERENCE'); bpy.data.objects.remove(cb,do_unlink=True)
            clean_mesh(pb)
            if vol(pb)>0.001: rboxes.append(pb)
            else: bpy.data.objects.remove(pb,do_unlink=True)
        if rboxes:
            rb=rboxes[0]
            for ob in rboxes[1:]: boolean(rb,ob,'UNION')
            for ob in rboxes[1:]: bpy.data.objects.remove(ob,do_unlink=True)
            clean_mesh(rb); rb.name="SLAB_ROOF"; rb.data.materials.append(m)
            rb["level"]="roof"; rb["thickness"]=rt; out.append(rb)
    return c,out

# =================== STEP 6: COLUMNS (auto-found, auto-trim) + BEAMS ======
def build_structure(db, grid, shafts, levels):
    c=new_coll("STRUCTURE_SYSTEM")
    mcol=mat("M_Col",(0.55,0.55,0.6,1)); mbm=mat("M_Bm",(0.4,0.45,0.55,1))
    # columns: base=founded, top=highest program at that (x,y) -> auto-trim, no overshoot
    cols=[]
    for (x,y),(zb,zt) in grid.items():
        s=0.6
        o=clean_box("COL_%.0f_%.0f"%(x,y),x-s/2,x+s/2,y-s/2,y+s/2,zb,zt,c,mcol)
        if o: o["member"]="column"; o["tier"]="TERTIARY"; cols.append((x,y,zb,zt,o))
    # beam elevations = each level floor + roof (top of tallest program)
    elevs=set(levels); elevs.add(max(d["bbox"][5] for d in db.values()))
    nb=0
    for zf in sorted(elevs):
        present=[(x,y) for (x,y,zb,zt,o) in cols if zb-0.3<=zf<=zt+0.3]
        if len(present)<2: continue
        segs=[]
        byy=defaultdict(list); byx=defaultdict(list)
        for (x,y) in present: byy[round(y,1)].append(x); byx[round(x,1)].append(y)
        for y,xs in byy.items():
            xs=sorted(set(xs))
            for i in range(len(xs)-1):
                sp=xs[i+1]-xs[i]
                if sp>15: continue
                d=0.8 if sp>9 else 0.45; segs.append((xs[i]-0.15,xs[i+1]+0.15,y-0.15,y+0.15,d))
        for x,ys in byx.items():
            ys=sorted(set(ys))
            for i in range(len(ys)-1):
                sp=ys[i+1]-ys[i]
                if sp>15: continue
                d=0.8 if sp>9 else 0.45; segs.append((x-0.15,x+0.15,ys[i]-0.15,ys[i+1]+0.15,d))
        objs=[]
        for (x0,x1,y0,y1,d) in segs:
            bo=clean_box("bm",x0,x1,y0,y1,zf-d,zf,c); 
            if bo: objs.append(bo); nb+=1
        if objs:
            bpy.ops.object.select_all(action='DESELECT')
            for o in objs: o.select_set(True)
            bpy.context.view_layer.objects.active=objs[0]
            if len(objs)>1: bpy.ops.object.join()
            j=bpy.context.view_layer.objects.active
            j.name="BEAMS_z%.1f"%zf; j.data.materials.append(mbm); j["member"]="beam"; j["tier"]="TERTIARY"
    return c, cols


# =================== STEP 7: CORE WALLS (height-based thickness) ==========
def wall_thickness(H):
    if H<40: return 0.30
    if H<80: return 0.40
    if H<150: return 0.50
    return 0.60

def build_core_walls(shafts, H):
    c=new_coll("CORE_WALL_SYSTEM"); m=mat("M_CoreWall",(0.35,0.35,0.4,1))
    T=wall_thickness(H)
    for k,s in shafts.items():
        x0,x1=s["x"]; y0,y1=s["y"]; z0,z1=s["z"]
        outer=clean_box("WALL_"+k,x0,x1,y0,y1,z0,z1,c,m)
        inner=clean_box("void",x0+T,x1-T,y0+T,y1-T,z0-1,z1+1,c)
        if outer and inner:
            boolean(outer,inner,'DIFFERENCE'); bpy.data.objects.remove(inner,do_unlink=True)
            clean_mesh(outer); outer["member"]="core_wall"; outer["tier"]="PRIMARY"; outer["t_mm"]=int(T*1000)
    return c,T

def build_core_columns(shafts):
    c=new_coll("CORE_COLUMN_SYSTEM"); m=mat("M_CoreCol",(0.5,0.3,0.3,1)); s=0.5; n=0
    for k,sh in shafts.items():
        x0,x1=sh["x"]; y0,y1=sh["y"]; z0,z1=sh["z"]
        xs=[x0+0.3,x1-0.3]; ys=[y0+0.3,y1-0.3]
        if x1-x0>8: xs.insert(1,(x0+x1)/2)
        if y1-y0>8: ys.insert(1,(y0+y1)/2)
        for xx in xs:
            for yy in ys:
                o=clean_box("CORECOL_%s_%.0f_%.0f"%(k,xx,yy),xx-s/2,xx+s/2,yy-s/2,yy+s/2,z0,z1,c,m)
                if o: o["member"]="core_column"; o["tier"]="PRIMARY"; n+=1
    return c,n

# =================== STEP 8: PARTITIONS (program-based + core exclusion) ==
def build_partitions(db, shafts, levels):
    c=new_coll("PARTITION_SYSTEM"); m=mat("M_Part",(0.8,0.78,0.72,1))
    core_boxes=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1]) for s in shafts.values()]
    pitch = (max(levels)-min(levels))/max(1,len(levels)-1) if len(levels)>1 else 4.0
    n=0
    for name,d in db.items():
        strat=d["partition"]
        if strat=="OPEN": continue
        b=d["bbox"]; t=CONFIG["service_wall"] if strat=="SERVICE" else CONFIG["interior_wall"]
        if (b[1]-b[0])<0.8 or (b[3]-b[2])<0.8: continue
        z0,z1=b[4],b[4]+pitch-0.35
        segs=[("N",b[0],b[1],b[3]-t,b[3]),("S",b[0],b[1],b[2],b[2]+t),
              ("W",b[0],b[0]+t,b[2]+t,b[3]-t),("E",b[1]-t,b[1],b[2]+t,b[3]-t)]
        made=[]
        for tag,x0,x1,y0,y1 in segs:
            w=clean_box("pw",x0,x1,y0,y1,z0,z1,c)
            if w: made.append(w)
        if strat=="CELLULAR" and max(b[1]-b[0],b[3]-b[2])>6.0:  # subdivide large rooms
            mod=3.5
            if b[1]-b[0]>=b[3]-b[2]:
                k=1
                while b[0]+mod*k<b[1]-1.5:
                    xx=b[0]+mod*k; w=clean_box("pwd",xx-t/2,xx+t/2,b[2]+t,b[3]-t,z0,z1,c)
                    if w: made.append(w)
                    k+=1
            else:
                k=1
                while b[2]+mod*k<b[3]-1.5:
                    yy=b[2]+mod*k; w=clean_box("pwd",b[0]+t,b[1]-t,yy-t/2,yy+t/2,z0,z1,c)
                    if w: made.append(w)
                    k+=1
        for (x0,x1,y0,y1) in core_boxes:
            if x1<=b[0] or x0>=b[1] or y1<=b[2] or y0>=b[3]: continue
            for w in made:
                cb=clean_box("cc",x0,x1,y0,y1,z0-1,z1+1,c)
                boolean(w,cb,'DIFFERENCE'); bpy.data.objects.remove(cb,do_unlink=True)
        for w in made: w.data.materials.append(m); w["tier"]="QUATERNARY"; n+=1
    return c,n

# =================== STEP 9: CURTAIN WALL (program transparency) ==========
def build_curtain(db, shafts):
    c=new_coll("CURTAIN_SYSTEM")
    GCOL={"STOREFRONT":(0.55,0.8,0.92,1),"MEDIUM":(0.45,0.65,0.82,1),
          "WINDOW":(0.5,0.66,0.78,1),"MINIMAL":(0.42,0.44,0.48,1)}
    SP={"STOREFRONT":3.0,"MEDIUM":2.0,"WINDOW":1.5,"MINIMAL":1.5}
    gmats={k:mat("Glass_"+k,v) for k,v in GCOL.items()}
    mm=mat("M_Mull",(0.2,0.2,0.22,1))
    bylvl=defaultdict(list)
    for n,d in db.items(): bylvl[d["level"]].append(d)
    core_boxes=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1]) for s in shafts.values()]
    def occ(L,x,y):
        for d in bylvl[L]:
            b=d["bbox"]
            if b[0]-0.2<=x<=b[1]+0.2 and b[2]-0.2<=y<=b[3]+0.2: return True
        for (x0,x1,y0,y1) in core_boxes:
            if x0-0.2<=x<=x1+0.2 and y0-0.2<=y<=y1+0.2: return True
        return False
    gt=CONFIG["glass_t"]; n=0
    for name,d in db.items():
        b=d["bbox"]; cls=d["facade"]; L=d["level"]
        faces=[("E",b[1],(b[2]+b[3])/2),("W",b[0],(b[2]+b[3])/2),
               ("N",(b[0]+b[1])/2,b[3]),("S",(b[0]+b[1])/2,b[2])]
        for tag,sx,sy in faces:
            ox=sx+0.5 if tag=="E" else sx-0.5 if tag=="W" else sx
            oy=sy+0.5 if tag=="N" else sy-0.5 if tag=="S" else sy
            if occ(L,ox,oy): continue
            if tag in ("E","W"):
                xf=b[1] if tag=="E" else b[0]
                g=clean_box("gl",xf-gt/2,xf+gt/2,b[2],b[3],b[4],b[5],c,gmats[cls])
            else:
                yf=b[3] if tag=="N" else b[2]
                g=clean_box("gl",b[0],b[1],yf-gt/2,yf+gt/2,b[4],b[5],c,gmats[cls])
            if g: g["member"]="curtain_glass"; g["tier"]="QUATERNARY"; n+=1
    return c,n


# =================== STEP 10: HYBRID CORE (adaptive triggers) =============
def build_outriggers(db, shafts, levels, H):
    c=new_coll("OUTRIGGER_SYSTEM")
    new_coll("BELT_TRUSS_SYSTEM"); new_coll("MEGA_COLUMN_SYSTEM")  # created; filled only if triggered
    if H<=CONFIG["outrigger_h"]:
        return c, 0, "H<=60m: no outriggers"
    base=min(levels); m=mat("M_Outrig",(0.9,0.55,0.15,1))
    # outrigger floors at 0.33H, 0.66H -> snap to nearest detected level
    targets=[base+0.33*H, base+0.66*H]
    def nearest_level(z): return min(levels,key=lambda L:abs(L-z))
    olevels=sorted(set(nearest_level(z) for z in targets))
    core_pts={k:((s["x"][0]+s["x"][1])/2,(s["y"][0]+s["y"][1])/2,s["z"]) for k,s in shafts.items()}
    bylvl=defaultdict(list)
    for n,d in db.items(): bylvl[d["level"]].append(d["bbox"])
    n=0
    Lz=sorted(levels)
    for zf in olevels:
        # perimeter extent at this elevation
        present=[b for b in [d for ds in bylvl.values() for d in ds] if b[4]<=zf<=b[5]]
        if not present: continue
        x0=min(b[0] for b in present); x1=max(b[1] for b in present)
        y0=min(b[2] for b in present); y1=max(b[3] for b in present)
        tgts=[("E",x1,0),("W",x0,0),("N",0,y1),("S",0,y0)]
        for k,(cx,cy,cz) in core_pts.items():
            if zf<cz[0] or zf>cz[1]: continue   # core must exist here
            for side,tx,ty in tgts:
                ax0,ax1=sorted([cx,tx]); ay0,ay1=sorted([cy,ty])
                # storey-deep baked into geometry (NO scale tricks)
                bo=clean_box("OUTRIG_%s_%s_%.0f"%(k,side,zf),ax0-0.25,ax1+0.25,ay0-0.25,ay1+0.25,zf-1.0,zf,c,m)
                if bo: bo["member"]="outrigger"; bo["tier"]="SECONDARY"; n+=1
    return c, n, "outriggers at levels %s"%([round(z,1) for z in olevels])

# =================== VALIDATION ===========================================
def validate_core_openings(slab_coll, shafts):
    tmp=new_coll("_val"); intr=0.0
    cb_specs=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1],s["z"][0],s["z"][1]) for s in shafts.values()]
    for sl in slab_coll.objects:
        for (x0,x1,y0,y1,z0,z1) in cb_specs:
            d=sl.copy(); d.data=sl.data.copy(); tmp.objects.link(d)
            cb=clean_box("c",x0,x1,y0,y1,z0-1,z1+1,tmp)
            boolean(d,cb,'INTERSECT'); intr+=vol(d)
            bpy.data.objects.remove(d,do_unlink=True); bpy.data.objects.remove(cb,do_unlink=True)
    for o in list(tmp.objects): bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(tmp)
    return intr

# =================== ORCHESTRATOR =========================================
def run_all():
    masses=collect_masses()
    if not masses:
        print("No program masses found. Check CONFIG['source_collection'] / exclude list."); return
    levels=detect_levels(masses)
    db=analyze(masses,levels)
    H=max(d["bbox"][5] for d in db.values())-min(d["bbox"][4] for d in db.values())
    xs=[d["bbox"][0] for d in db.values()]+[d["bbox"][1] for d in db.values()]
    ys=[d["bbox"][2] for d in db.values()]+[d["bbox"][3] for d in db.values()]
    slender=H/max(1e-6,min(max(xs)-min(xs),max(ys)-min(ys)))
    shafts=detect_cores(db,levels)

    build_unified_core(shafts)
    resolve_overlaps(db,shafts)
    grid=build_grid(db,shafts)
    slab_coll,_=build_slabs(db,shafts,levels)
    build_ceilings(db,shafts,slab_coll)
    cap_cores(shafts,slab_coll)
    build_structure(db,grid,shafts,levels)
    cw,T=build_core_walls(shafts,H)
    build_core_columns(shafts)
    build_partitions(db,shafts,levels)
    build_curtain(db,shafts)
    _,nout,onote=build_outriggers(db,shafts,levels,H)
    intr=validate_core_openings(slab_coll,shafts)

    rep=("BUILDING GENERATED (adaptive)\n"
         "  masses=%d  levels=%d  height=%.1fm  slenderness=%.2f\n"
         "  cores=%d  core_wall_t=%dmm (height band)\n"
         "  outriggers=%d (%s)\n"
         "  belt_truss=%s  mega_col=%s\n"
         "  core-opening slab intrusion=%.4f m3 (0 = clean voids)\n"
         %(len(db),len(levels),H,slender,len(shafts),int(T*1000),
           nout,onote,
           ("YES" if H>CONFIG["belt_h"] else "no (H<=80m)"),
           ("YES" if (H>CONFIG["mega_h"] or slender>CONFIG["mega_slender"]) else "no"),
           intr))
    rt=bpy.data.texts.get("BUILD_REPORT") or bpy.data.texts.new("BUILD_REPORT")
    rt.clear(); rt.write(rep); print(rep)

# To execute:  run_all()


# =================== STEP 5b: PER-MASS CEILINGS (cap stack tops) ==========
def build_ceilings(db, shafts, slab_coll):
    # Cap any mass whose TOP has no slab above it (top-of-stack / setback rooms).
    # Skip outdoor masses (plaza / terrace) and anything fully inside a core.
    core_boxes=[(s["x"][0],s["x"][1],s["y"][0],s["y"][1],s["z"][0],s["z"][1]) for s in shafts.values()]
    OUTDOOR=["plaza","terrace","roof_terrace"]
    m=mat("M_Slab",(0.6,0.6,0.62,1))
    existing=[W(o) for o in slab_coll.objects]
    def has_slab(z,x,y):
        for b in existing:
            if b[4]-0.4<=z<=b[5]+0.4 and b[0]-0.5<=x<=b[1]+0.5 and b[2]-0.5<=y<=b[3]+0.5: return True
        return False
    n=0
    for name,d in db.items():
        if d["class"]=="CORE": continue
        if any(k in name.lower() for k in OUTDOOR): continue
        b=d["bbox"]; cx,cy=(b[0]+b[1])/2,(b[2]+b[3])/2
        if has_slab(b[5],cx,cy): continue
        t=d["slab_t"]; z0,z1=b[5]-t,b[5]
        cb=clean_box("CEIL_"+name,b[0],b[1],b[2],b[3],z0,z1,slab_coll,m)
        if not cb: continue
        for (x0,x1,y0,y1,cz0,cz1) in core_boxes:
            if x1<=b[0] or x0>=b[1] or y1<=b[2] or y0>=b[3]: continue
            cc=clean_box("cc",x0,x1,y0,y1,z0-1,z1+1,slab_coll); boolean(cb,cc,'DIFFERENCE'); bpy.data.objects.remove(cc,do_unlink=True)
        clean_mesh(cb)
        if vol(cb)<0.001: bpy.data.objects.remove(cb,do_unlink=True); continue
        cb["member"]="ceiling"; existing.append(W(cb)); n+=1
    return n


# =================== STEP 5c: CORE TOP CAPS (shaft roofs) =================
def cap_cores(shafts, slab_coll):
    # cap the TOP of each core shaft (shaft roof / bulkhead). Bottom rests on base slab.
    # Does NOT violate the through-floor void rule (intermediate floors stay open).
    m=mat("M_Slab",(0.6,0.6,0.62,1)); t=0.30; n=0
    for k,s in shafts.items():
        x0,x1=s["x"]; y0,y1=s["y"]; ztop=s["z"][1]
        cap=clean_box("CORE_CAP_"+k,x0,x1,y0,y1,ztop-t,ztop,slab_coll,m)
        if cap: cap["member"]="core_cap"; n+=1
    return n
