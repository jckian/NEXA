"""
TPAC (Taipei Performing Arts Center) — Architectural Geometry Generator v2
==========================================================================
Complete curtain wall coverage on ALL facade faces, including:
- Theater arm cutout zones on central cube (ear strips)
- Glazing overlay panels on cube faces
- Proper Blue Box height (Z 19.5–32.3) and Globe height (Z 19.5–23.3)

Usage:  Paste into Blender Text Editor → Run Script (Alt-P)
Units:  meters, Z-up.  Site: 70 × 70 m.
"""
import bpy, bmesh, math
from mathutils import Vector, Euler

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════
GRAND = (8.2, 34.8, -13.3, 13.3, 19.5, 45.8)
BLUE  = (-34.8, -13.9, -10.5, 10.5, 19.5, 32.3)
GLOBE = (-10.5, 10.5, -34.8, -13.9, 19.5, 23.3)
FW = 0.5; MW = 0.12; MD = 0.15; PT = 0.08
LEVELS_Z = [-4.5,0,6,10.5,15,19.5,24,28.5,33,37.5,42,46.5,51,55.5,59.3]
LEVEL_NAMES = ["L-1","L0","L1","L2","L3","L4","L5","L6","L7","L8","L9","L10","L11","L12","ROOF"]
MASSING_COLLECTIONS = [
    "BACKSTAGE","BOX OFFICE","CIRCULATION","DRESSING ROOM","EVENT HALL",
    "EVENT LOUNGE","FITTING ROOMS","FLY TOWER","GREEN ROOM","IT SUPPORT",
    "LOADING","LOBBY","LOUNGE BAR","PRODUCTION WORKSHOP","REHEARSAL ROOM",
    "RESTAURANT","RESTROOM","ROOF TERRACE","SALES AND DISPLAY","SET STORAGE",
    "STAFF","STORAGE","VIEWING PLATFORM",
    "FIRE STAIR AND ELEVATOR 1","FIRE STAIR AND ELEVATOR 2",
    "FIRE STAIR AND ELEVATOR 3","FIRE STAIR AND FREIGHT ELEVATO",
]

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════
def _col(name, parent=None):
    if name in bpy.data.collections:
        c = bpy.data.collections[name]
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
        return c
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c); return c

def _mat(name, color, metallic=0, roughness=0.5, alpha=1):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name=name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = color
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = roughness
        if alpha < 1: b.inputs["Alpha"].default_value = alpha
    return m

def _box(name, center, size, material, collection):
    mesh = bpy.data.meshes.new(name); obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = v.co.x*size[0]+center[0]; v.co.y = v.co.y*size[1]+center[1]; v.co.z = v.co.z*size[2]+center[2]
    bm.to_mesh(mesh); bm.free(); obj.data.materials.append(material); return obj

def _diagonal(name, start, end, thickness, material, collection):
    dx,dy,dz = end[0]-start[0],end[1]-start[1],end[2]-start[2]
    length = math.sqrt(dx*dx+dy*dy+dz*dz)
    center = ((start[0]+end[0])/2,(start[1]+end[1])/2,(start[2]+end[2])/2)
    mesh = bpy.data.meshes.new(name); obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x *= thickness; v.co.y *= length; v.co.z *= thickness
    bm.to_mesh(mesh); bm.free(); obj.location = Vector(center); obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0,1,0)).rotation_difference(Vector((dx,dy,dz)).normalized())
    obj.data.materials.append(material); return obj

def cw_face_y(pfx, yp, x0, x1, z0, z1, n, mat_p, mat_m, col, art=True):
    span=x1-x0; h=z1-z0; zc=(z0+z1)/2; ps=(span-2*FW)/n
    _box(f"{pfx}|fr|bot",((x0+x1)/2, yp, z0+FW/2),(span,FW,FW), mat_m, col)
    _box(f"{pfx}|fr|top",((x0+x1)/2, yp, z1-FW/2),(span,FW,FW), mat_m, col)
    _box(f"{pfx}|fr|L",(x0+FW/2, yp, zc),(FW,FW,h), mat_m, col)
    _box(f"{pfx}|fr|R",(x1-FW/2, yp, zc),(FW,FW,h), mat_m, col)
    for i in range(n):
        xc=x0+FW+ps*(i+0.5); yo=0.12*(1 if i%2==0 else -1) if art else 0
        _box(f"{pfx}|pn|{i}",(xc, yp+yo, zc),(ps-MW, PT, h-2*FW), mat_p, col)
        _box(f"{pfx}|mu|V{i}",(x0+FW+ps*i, yp, zc),(MW, MD, h), mat_m, col)

def cw_face_x(pfx, xp, y0, y1, z0, z1, n, mat_p, mat_m, col, art=True):
    span=y1-y0; h=z1-z0; zc=(z0+z1)/2; ps=(span-2*FW)/n
    _box(f"{pfx}|fr|bot",(xp, (y0+y1)/2, z0+FW/2),(FW,span,FW), mat_m, col)
    _box(f"{pfx}|fr|top",(xp, (y0+y1)/2, z1-FW/2),(FW,span,FW), mat_m, col)
    _box(f"{pfx}|fr|L",(xp, y0+FW/2, zc),(FW,FW,h), mat_m, col)
    _box(f"{pfx}|fr|R",(xp, y1-FW/2, zc),(FW,FW,h), mat_m, col)
    for i in range(n):
        yc=y0+FW+ps*(i+0.5); xo=0.12*(1 if i%2==0 else -1) if art else 0
        _box(f"{pfx}|pn|{i}",(xp+xo, yc, zc),(PT, ps-MW, h-2*FW), mat_p, col)
        _box(f"{pfx}|mu|V{i}",(xp, y0+FW+ps*i, zc),(MD, MW, h), mat_m, col)

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    print("TPAC Generator v2 — starting …")
    M = {
        "steel":_mat("Steel_Structure",(0.45,0.45,0.48,1),metallic=0.9,roughness=0.3),
        "concrete":_mat("Concrete_Structure",(0.72,0.70,0.67,1),roughness=0.8),
        "glazing":_mat("Glazing",(0.6,0.75,0.85,0.3),metallic=0.1,roughness=0.05,alpha=0.3),
        "mullion":_mat("Mullion_Frame",(0.25,0.25,0.27,1),metallic=0.85,roughness=0.25),
        "panel_grand":_mat("Panel_Grand",(0.78,0.72,0.65,1),metallic=0.3,roughness=0.4),
        "panel_blue":_mat("Panel_Blue",(0.5,0.55,0.65,1),metallic=0.4,roughness=0.35),
        "panel_globe":_mat("Panel_Globe",(0.65,0.6,0.55,1),metallic=0.3,roughness=0.45),
        "slab":_mat("Floor_Slab",(0.65,0.63,0.6,1),roughness=0.9),
        "roof":_mat("Roof_Metal",(0.35,0.35,0.38,1),metallic=0.8,roughness=0.4),
        "event":_mat("event hall",(0.85,0.75,0.6,1)),
    }
    ms=M["steel"];mc=M["concrete"];mg=M["glazing"];mm=M["mullion"];mr=M["roof"]
    gp=M["panel_grand"];bp=M["panel_blue"];glp=M["panel_globe"]

    struct=_col("STRUCTURE"); curtain=_col("CURTAIN_WALLS")
    C={"mega":_col("MEGA_COLUMNS",struct),"brace":_col("BRACING",struct),"slab":_col("FLOOR_SLABS",struct),
       "pilotis":_col("PILOTIS",struct),"junction":_col("JUNCTIONS",struct),"edge":_col("EDGE_BEAMS",struct),
       "underside":_col("UNDERSIDE_STRUCTURE",struct),"core":_col("CORE_WALLS",struct),"struct":struct,
       "grand_cw":_col("GRAND_THEATER_CW",curtain),"blue_cw":_col("BLUE_BOX_CW",curtain),
       "globe_cw":_col("GLOBE_PLAYHOUSE_CW",curtain),"cube_cw":_col("CENTRAL_CUBE_CW",curtain),
       "curtain":curtain,"roof":_col("ROOF_ELEMENTS"),"fly_detail":_col("FLY_TOWER_DETAIL",_col("ROOF_ELEMENTS")),
       "facade":_col("FACADE_ARTICULATION"),"entrance":_col("ENTRANCE_ELEMENTS"),
       "basement":_col("BASEMENT_WALLS"),"stair_enc":_col("STAIR_ENCLOSURES"),
       "escalator":_col("ESCALATORS"),"terrace":_col("TERRACE_DETAIL"),
       "theater_vol":_col("THEATER_VOLUMES"),"site":_col("SITE")}

    # ── 1. STRUCTURE ──
    zbot,ztop=-4.5,60.0; h=ztop-zbot; zc=(zbot+ztop)/2
    for i,(cx,cy,w,d) in enumerate([(-12.3,11.3,10,12),(13.3,13.3,8,8),(13.3,-13.3,8,8),(-13.3,-13.3,8,8)]):
        _box(f"MEGA|{['NW','NE','SE','SW'][i]}",(cx,cy,zc),(w,d,h),mc,C["mega"])
    t=0.4
    for z,ln in zip(LEVELS_Z,LEVEL_NAMES): _box(f"SL|cb|{ln}",(0,0,z-t/2),(34.6,34.6,t),M["slab"],C["slab"])
    for z,ln in [(19.5,"L4"),(45.8,"RF")]: _box(f"SL|gr|{ln}",(21.5,0,z-t/2),(26.6,26.6,t),M["slab"],C["slab"])
    for z,ln in [(19.5,"L4"),(27.8,"RF")]:
        _box(f"SL|bl|{ln}",(-24.35,0,z-t/2),(20.9,21,t),M["slab"],C["slab"])
        _box(f"SL|gl|{ln}",(0,-24.35,z-t/2),(21,20.9,t),M["slab"],C["slab"])
    positions=[]
    for x in [-4,0,4]:
        for y in [-12,-6,0,6,12]:
            if abs(x)>6 and abs(y)>6: continue
            positions.append((x,y))
    for x in [-8,8]:
        for y in [-4,0,4]: positions.append((x,y))
    for idx,(px,py) in enumerate(positions):
        mesh=bpy.data.meshes.new(f"PIL|{idx}"); obj=bpy.data.objects.new(f"PIL|{idx}",mesh)
        C["pilotis"].objects.link(obj); bm=bmesh.new()
        bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=8,radius1=0.45,radius2=0.45,depth=6)
        for v in bm.verts: v.co.x+=px; v.co.y+=py; v.co.z+=3
        bm.to_mesh(mesh); bm.free(); obj.data.materials.append(mc)
    cw2=0.8
    for x in [-5,0,5]:
        for zb,zt,lbl in [(0,6,"01"),(6,10.5,"12")]:
            _box(f"CL|N{x}|{lbl}",(x,17,(zb+zt)/2),(cw2,cw2,zt-zb),mc,C["struct"])
            _box(f"CL|S{x}|{lbl}",(x,-17,(zb+zt)/2),(cw2,cw2,zt-zb),mc,C["struct"])
    for y in [-5,0,5]:
        for zb,zt,lbl in [(0,10.5,"02"),(10.5,19.5,"24")]:
            _box(f"CL|E{y}|{lbl}",(17,y,(zb+zt)/2),(cw2,cw2,zt-zb),mc,C["struct"])
            _box(f"CL|W{y}|{lbl}",(-17,y,(zb+zt)/2),(cw2,cw2,zt-zb),mc,C["struct"])
    tw,td=1.2,0.8
    for i,yp in enumerate([-8,8]):
        _box(f"TR|gr|b{i}",(8.7,yp,18.5),(tw,26.6,td),ms,C["brace"])
        _box(f"TR|gr|t{i}",(8.7,yp,23),(tw,26.6,td),ms,C["brace"])
    for i,yp in enumerate([-6,6]):
        _box(f"TR|bl|b{i}",(-14.3,yp,18.5),(tw,20.9,td),ms,C["brace"])
        _box(f"TR|bl|t{i}",(-14.3,yp,23),(tw,20.9,td),ms,C["brace"])
    for i,xp in enumerate([-6,6]):
        _box(f"TR|gl|b{i}",(xp,-14.3,18.5),(20.9,tw,td),ms,C["brace"])
        _box(f"TR|gl|t{i}",(xp,-14.3,23),(20.9,tw,td),ms,C["brace"])
    for i,yb in enumerate([-10,-5,0,5,10]):
        _diagonal(f"BR|Vl{i}",(8.7,yb,18.5),(8.7,yb-2,23),0.4,ms,C["brace"])
        _diagonal(f"BR|Vr{i}",(8.7,yb,18.5),(8.7,yb+2,23),0.4,ms,C["brace"])
    rw,rh2=0.8,1.0
    _box("JC|gr|t",(8.7,0,45.8),(rw,26.6,rh2),ms,C["junction"]); _box("JC|gr|b",(8.7,0,19.5),(rw,26.6,rh2),ms,C["junction"])
    _box("JC|gr|L",(8.7,-13.3,32.65),(rw,rh2,26.3),ms,C["junction"]); _box("JC|gr|R",(8.7,13.3,32.65),(rw,rh2,26.3),ms,C["junction"])
    _box("JC|bl|t",(-14.3,0,27.8),(rw,21,rh2),ms,C["junction"]); _box("JC|bl|b",(-14.3,0,19.5),(rw,21,rh2),ms,C["junction"])
    _box("JC|bl|L",(-14.3,-10.5,25.9),(rw,rh2,12.8),ms,C["junction"]); _box("JC|bl|R",(-14.3,10.5,25.9),(rw,rh2,12.8),ms,C["junction"])
    _box("JC|gl|t",(0,-14.3,23.3),(21,rw,rh2),ms,C["junction"]); _box("JC|gl|b",(0,-14.3,19.5),(21,rw,rh2),ms,C["junction"])
    _box("JC|gl|L",(-10.5,-14.3,21.4),(rh2,rw,3.8),ms,C["junction"]); _box("JC|gl|R",(10.5,-14.3,21.4),(rh2,rw,3.8),ms,C["junction"])
    ew,eh=0.6,0.8
    for z in [19.5,45.8]:
        _box(f"EG|gr|N{z:.0f}",(21.5,13.3,z),(26.6,ew,eh),ms,C["edge"]); _box(f"EG|gr|S{z:.0f}",(21.5,-13.3,z),(26.6,ew,eh),ms,C["edge"])
        _box(f"EG|gr|E{z:.0f}",(34.8,0,z),(ew,26.6,eh),ms,C["edge"])
    for z in [19.5,27.8]:
        _box(f"EG|bl|N{z:.0f}",(-24.35,10.5,z),(20.9,ew,eh),ms,C["edge"]); _box(f"EG|bl|S{z:.0f}",(-24.35,-10.5,z),(20.9,ew,eh),ms,C["edge"])
        _box(f"EG|bl|W{z:.0f}",(-34.8,0,z),(ew,21,eh),ms,C["edge"]); _box(f"EG|gl|E{z:.0f}",(10.5,-24.35,z),(ew,20.9,eh),ms,C["edge"])
        _box(f"EG|gl|W{z:.0f}",(-10.5,-24.35,z),(ew,20.9,eh),ms,C["edge"]); _box(f"EG|gl|S{z:.0f}",(0,-34.8,z),(21,ew,eh),ms,C["edge"])
    bw=0.5
    for y in [-10,-5,0,5,10]: _box(f"UN|gr|EW{y}",(21.5,y,18.5),(26.6,bw,1),ms,C["underside"])
    for x in [12,16,20,25,30,34]: _box(f"UN|gr|NS{x}",(x,0,18.7),(bw,26.6,0.6),ms,C["underside"])
    for y in [-7,-3.5,0,3.5,7]: _box(f"UN|bl|EW{y}",(-24.35,y,18.7),(20.9,bw,0.8),ms,C["underside"])
    for x in [-18,-22,-26,-30,-34]: _box(f"UN|bl|NS{x}",(x,0,18.9),(bw,21,0.5),ms,C["underside"])
    for x in [-7,-3.5,0,3.5,7]: _box(f"UN|gl|NS{x}",(x,-24.35,18.7),(bw,20.9,0.8),ms,C["underside"])
    for y in [-18,-22,-26,-30,-34]: _box(f"UN|gl|EW{y}",(0,y,18.9),(21,bw,0.5),ms,C["underside"])
    _box("CR|BOH",(0,3.5,30),(16,0.35,60),mc,C["core"]); _box("CR|N",(0,17,30),(18,0.35,60),mc,C["core"]); _box("CR|S",(0,-17,30),(18,0.35,60),mc,C["core"])
    print("  Structure ✓")

    # ── 2. CURTAIN WALLS (ALL FACES) ──
    gc=C["grand_cw"]; cw_face_x("GR_E",34.8,-13.3,13.3,19.5,45.8,8,gp,mm,gc); cw_face_y("GR_N",13.3,8.2,34.8,19.5,45.8,8,gp,mm,gc); cw_face_y("GR_S",-13.3,8.2,34.8,19.5,45.8,8,gp,mm,gc)
    bc2=C["blue_cw"]; cw_face_x("BL_W",-34.8,-10.5,10.5,19.5,32.3,7,bp,mm,bc2); cw_face_y("BL_N",10.5,-34.8,-13.9,19.5,32.3,7,bp,mm,bc2); cw_face_y("BL_S",-10.5,-34.8,-13.9,19.5,32.3,7,bp,mm,bc2)
    glc=C["globe_cw"]; cw_face_y("GL_S",-34.8,-10.5,10.5,19.5,23.3,7,glp,mm,glc); cw_face_x("GL_W",-10.5,-34.8,-13.9,19.5,23.3,7,glp,mm,glc); cw_face_x("GL_E",10.5,-34.8,-13.9,19.5,23.3,7,glp,mm,glc)
    cc=C["cube_cw"]
    # North full
    cw_face_y("CB_N",17.3,-17.3,17.3,0,60,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; xc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_N|gl|{i}",(xc,17.35,30),(ps-MW,0.02,56),mg,cc)
    # South with Globe cutout
    cw_face_y("CB_SL",-17.3,-17.3,17.3,0,19.5,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; xc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_SL|gl|{i}",(xc,-17.35,9.75),(ps-MW,0.02,15.5),mg,cc)
    cw_face_y("CB_SgL",-17.3,-17.3,-10.5,19.5,23.3,2,mc,mm,cc,art=False)
    cw_face_y("CB_SgR",-17.3,10.5,17.3,19.5,23.3,2,mc,mm,cc,art=False)
    cw_face_y("CB_SH",-17.3,-17.3,17.3,23.3,60,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; xc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_SH|gl|{i}",(xc,-17.35,41.65),(ps-MW,0.02,32.7),mg,cc)
    # East with Grand cutout
    cw_face_x("CB_EL",17.3,-17.3,17.3,0,19.5,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; yc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_EL|gl|{i}",(17.35,yc,9.75),(0.02,ps-MW,15.5),mg,cc)
    cw_face_x("CB_EgB",17.3,-17.3,-13.3,19.5,45.8,1,mc,mm,cc,art=False)
    cw_face_x("CB_EgT",17.3,13.3,17.3,19.5,45.8,1,mc,mm,cc,art=False)
    cw_face_x("CB_EH",17.3,-17.3,17.3,45.8,60,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; yc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_EH|gl|{i}",(17.35,yc,52.9),(0.02,ps-MW,10.2),mg,cc)
    # West with Blue cutout
    cw_face_x("CB_WL",-17.3,-17.3,17.3,0,19.5,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; yc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_WL|gl|{i}",(-17.35,yc,9.75),(0.02,ps-MW,15.5),mg,cc)
    cw_face_x("CB_WbL",-17.3,-17.3,-10.5,19.5,32.3,2,mc,mm,cc,art=False)
    cw_face_x("CB_WbR",-17.3,10.5,17.3,19.5,32.3,2,mc,mm,cc,art=False)
    cw_face_x("CB_WH",-17.3,-17.3,17.3,32.3,60,12,mc,mm,cc,art=False)
    for i in range(12):
        ps=(34.6-2*FW)/12; yc=-17.3+FW+ps*(i+0.5)
        if i%3==0: _box(f"CB_WH|gl|{i}",(-17.35,yc,46.15),(0.02,ps-MW,23.7),mg,cc)
    print("  Curtain walls ✓")

    # ── 3. ROOF ──
    r=C["roof"]
    _box("RF|gr|cl",(21.5,0,46.05),(27,27,.1),mr,r); _box("RF|gr|me",(21.5,0,47),(12,8,2),ms,r); _box("RF|gr|fl",(25,0,46.5),(14,14,1),ms,r)
    for tg,y in [("N",13.3),("S",-13.3)]: _box(f"RF|gr|p{tg}",(21.5,y,46.3),(26.6,.2,1),gp,r)
    _box("RF|gr|pE",(34.8,0,46.3),(.2,26.6,1),gp,r)
    _box("RF|bl|cl",(-24.35,0,32.55),(21.3,21.4,.1),mr,r); _box("RF|bl|me",(-24.35,0,33.3),(8,6,1.6),ms,r)
    for tg,y in [("N",10.5),("S",-10.5)]: _box(f"RF|bl|p{tg}",(-24.35,y,32.8),(20.9,.2,1),bp,r)
    _box("RF|bl|pW",(-34.8,0,32.8),(.2,21,1),bp,r)
    _box("RF|gl|cl",(0,-24.35,23.55),(21.4,21.3,.1),mr,r); _box("RF|gl|me",(0,-24.35,24.3),(6,8,1.6),ms,r)
    for tg,x in [("E",10.5),("W",-10.5)]: _box(f"RF|gl|p{tg}",(x,-24.35,23.8),(.2,20.9,1),glp,r)
    _box("RF|gl|pS",(0,-34.8,23.8),(21,.2,1),glp,r)
    _box("RF|cb|mn",(0,0,59.5),(34.6,34.6,.4),mr,r)
    for tg,p,s in [("N",(0,17.3,59.9),(34.6,.25,1.2)),("S",(0,-17.3,59.9),(34.6,.25,1.2)),("E",(17.3,0,59.9),(.25,34.6,1.2)),("W",(-17.3,0,59.9),(.25,34.6,1.2))]:
        _box(f"RF|pa|{tg}",p,s,mc,r)
    _box("RF|m1",(-5,5,60.5),(6,6,2),ms,r); _box("RF|m2",(5,-5,60.5),(5,5,2),ms,r)
    _box("RF|eNW",(-12.3,11.3,61),(4,4,3),mc,r); _box("RF|eNE",(13.3,13.3,61),(3.5,3.5,3),mc,r)
    fd=C["fly_detail"]
    for x in [12,17,22,27,32]: _box(f"RF|cE{x}",(x,0,46),(.6,26,.15),ms,fd)
    for y in [-10,-5,0,5,10]: _box(f"RF|cN{y}",(21.5,y,46),(26,.6,.15),ms,fd)
    for i in range(6): _box(f"RF|lv{i}",(17+i*3,0,47.5),(.1,12,2.5),ms,fd)
    print("  Roof ✓")

    # ── 4. FACADE ──
    fc=C["facade"]
    for i in range(5):
        z=22+i*5
        for j,yp in enumerate([-9,-4.5,0,4.5,9]): _box(f"FA|gr|{i}_{j}",(34.9+abs(0.4*math.sin((i+j)*0.8)),yp,z),(.15,3.8,4.2),gp,fc)
    _box("FA|gr|sf",(21.5,0,19.3),(26.6,26.6,.15),gp,fc)
    for i in range(4):
        z=21+i*2
        for j,yp in enumerate([-7,-3.5,0,3.5,7]): _box(f"FA|bl|{i}_{j}",(-34.9-abs(0.3*math.cos((i+j)*0.9)),yp,z),(.12,3,1.5),bp,fc)
    _box("FA|bl|sf",(-24.35,0,19.3),(20.9,21,.15),bp,fc)
    for i in range(4):
        z=21+i*2
        for j,xp in enumerate([-7,-3.5,0,3.5,7]): _box(f"FA|gl|{i}_{j}",(xp,-34.9-abs(0.35*math.sin((i+j)*0.7+0.5)),z),(3,.12,1.5),glp,fc)
    _box("FA|gl|sf",(0,-24.35,19.3),(21,20.9,.15),glp,fc)
    for i in range(8): _box(f"FA|lb|{i}",(-14+i*4,-17.35,1.9),(3.5,.04,3.6),mg,fc)
    for z,lbl in [(30,"L6"),(34.5,"L7")]: _box(f"FA|vw|{lbl}",(-3.5,-17.3,z),(14,.04,1.2),mg,fc)
    print("  Facade ✓")

    # ── 5. ANCILLARY ──
    ec=C["entrance"]; _box("EN|cn",(0,-20,5.5),(20,6,.2),ms,ec)
    for xp in [-8,-3,3,8]:
        mesh=bpy.data.meshes.new(f"EN|s{xp}"); obj=bpy.data.objects.new(f"EN|s{xp}",mesh); ec.objects.link(obj)
        bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
        for v in bm.verts: v.co.x*=0.15; v.co.y*=4; v.co.z*=0.15
        bm.to_mesh(mesh); bm.free(); obj.location=Vector((xp,-18.5,4)); obj.rotation_euler=(math.radians(30),0,0); obj.data.materials.append(ms)
    _box("EN|gz",(0,-22.8,5.4),(18,.5,.08),mg,ec)
    bsc=C["basement"]
    for tg,p,s in [("N",(0,17.3,-2.25),(34.6,.4,4.5)),("S",(0,-17.3,-2.25),(34.6,.4,4.5)),("E",(17.3,0,-2.25),(.4,34.6,4.5)),("W",(-17.3,0,-2.25),(.4,34.6,4.5))]:
        _box(f"BS|{tg}",p,s,mc,bsc)
    _box("BS|sl",(0,0,-4.7),(36,36,.5),mc,bsc)
    sc=C["stair_enc"]; eh3=3.5; ez3=59.3+eh3/2
    for tg,sx,sy,sw,sd in [("NW",-12.3,11.3,10,12),("NE",13.3,13.3,8,8),("SE",13.3,-13.3,8,8),("SW",-13.3,-13.3,8,8)]:
        for side,p,s in [("N",(sx,sy+sd/2,ez3),(sw,.15,eh3)),("S",(sx,sy-sd/2,ez3),(sw,.15,eh3)),("E",(sx+sw/2,sy,ez3),(.15,sd,eh3)),("W",(sx-sw/2,sy,ez3),(.15,sd,eh3))]:
            _box(f"SE|{tg}|{side}",p,s,mg,sc)
        _box(f"SE|{tg}|rf",(sx,sy,59.3+eh3+.1),(sw+.4,sd+.4,.25),mr,sc)
    esc=C["escalator"]
    for i,(zb,zt) in enumerate([(0,6),(6,15),(15,19.5)]):
        _box(f"ES|t{i}",(-2,-15,(zb+zt)/2),(4,3,zt-zb),mg,esc); _box(f"ES|ft{i}",(-2,-15,zt-.1),(4.2,3.2,.2),mm,esc); _box(f"ES|fb{i}",(-2,-15,zb+.1),(4.2,3.2,.2),mm,esc)
    tc=C["terrace"]; trh=1.1; trt=0.02
    _box("TR|6S",(-3.5,-17.3,28.5+trh/2),(14,trt,trh),mg,tc); _box("TR|6W",(-7.1,-10,28.5+trh/2),(trt,14,trh),mg,tc); _box("TR|7S",(-4,-17.3,33+trh/2),(14,trt,trh),mg,tc)
    for x in range(-10,5,3):
        for lbl,z in [("6",28.5),("7",33)]: _box(f"TR|p|{lbl}_{x}",(x,-17.3,z+trh/2),(.06,.06,trh),mm,tc)
    for tg,p,s in [("12S",(0,-17.3,55.5+trh/2),(34,trt,trh)),("12W",(-17.3,-7,55.5+trh/2),(trt,20,trh)),("12E",(17.3,-7,55.5+trh/2),(trt,20,trh))]:
        _box(f"TR|r|{tg}",p,s,mg,tc)
    sic=C["site"]
    for tg,p,s in [("N",(0,35,.025),(70,.1,.05)),("S",(0,-35,.025),(70,.1,.05)),("E",(35,0,.025),(.1,70,.05)),("W",(-35,0,.025),(.1,70,.05))]:
        _box(f"SI|{tg}",p,s,ms,sic)
    print("  Ancillary ✓")

    # ── 6. UNIFIED THEATERS + HIDE ──
    victims=[o for o in bpy.data.objects if o.type=="MESH" and ("event hall" in o.name or "fly tower" in o.name)]
    for o in victims: bpy.data.objects.remove(o,do_unlink=True)
    tv=C["theater_vol"]; me=M["event"]
    for tag,bb in [("grand",GRAND),("blue",BLUE),("globe",GLOBE)]:
        x0,x1,y0,y1,z0,z1=bb; _box(f"TV|{tag}",((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),(x1-x0,y1-y0,z1-z0),me,tv)
    for name in MASSING_COLLECTIONS:
        if name in bpy.data.collections: bpy.data.collections[name].hide_viewport=True; bpy.data.collections[name].hide_render=True
    for o in bpy.data.objects:
        if o.name=="GROUND_PLANE": o.hide_viewport=True; o.hide_render=True

    # ── 7. VIEWPORT ──
    for area in bpy.context.screen.areas:
        if area.type=="VIEW_3D":
            for space in area.spaces:
                if space.type=="VIEW_3D":
                    rv=space.region_3d; rv.view_perspective="PERSP"; rv.view_location=Vector((5,-5,22)); rv.view_distance=130
                    rv.view_rotation=Euler((math.radians(58),0,math.radians(-42))).to_quaternion()
                    space.shading.type="MATERIAL"; space.overlay.show_overlays=False; break

    total=len([o for o in bpy.data.objects if o.type=="MESH" and not o.hide_viewport])
    print(f"\n  ✓ TPAC v2 done — {total} visible objects")

if __name__ == "__main__":
    main()
