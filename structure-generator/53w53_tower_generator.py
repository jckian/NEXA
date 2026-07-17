"""
53W53-Type Tower Generator for Blender
=======================================
Converts existing program massing into a complete structural facade system:
  1. Floor extraction & convex hull
  2. Faceted asymmetric envelope with vertex drift + taper + crown
  3. Structurally correct RC diagrid (face-aligned, height-tapered)
  4. Node reinforcement blocks
  5. Floor slabs extending to diagrid nodes
  6. Glass infill panels (triangular + quad)

Usage:
  - Open your Blender scene with program massing geometry
  - Run this script from Blender's Text Editor (Alt+P)
  - Or from command line: blender --python 53w53_tower_generator.py

Requirements:
  - Blender 3.x or 4.x
  - Existing mesh objects in the scene (the program massing)
"""

import bpy
from mathutils import Vector
import math
import random
from collections import defaultdict

random.seed(53)

# ============================================================
# CONFIGURATION
# ============================================================
CONFIG = {
    # Envelope
    'num_perimeter_verts': 8,       # vertices per floor ring
    'drift_rate_range': (0.03, 0.10),  # vertex drift per floor (meters)
    'taper_per_vert': [0.03, 0.12, 0.25, 0.50, 0.55, 0.45, 0.20, 0.08],
    'crown_start_frac': 0.80,       # top 20% = crown zone
    'crown_peak_offset': (4, 8),    # peak height offset range
    'crown_valley_offset': (-2, 0), # valley offset range
    'num_cap_levels': 4,            # blunted tip cap levels
    'envelope_subdivisions': 2,     # interpolation between floors
    'flatten_top_rings': 8,         # rings to flatten at top

    # Diagrid
    'diagrid_floor_spacing': 9.0,   # meters between diagrid levels
    'diagrid_angle': 60,            # degrees from horizontal
    'angle_tolerance': 20,          # degrees tolerance for filtering
    'min_member_length': 3.5,       # meters
    'node_merge_tolerance': 0.5,    # meters
    'surface_offset': 0.25,         # meters outward from envelope

    # RC Structure
    'thickness_base': 1.2,          # meters at bottom
    'thickness_top': 0.35,          # meters at top
    'primary_scale': 1.25,          # thickness multiplier for primary members
    'secondary_scale': 0.65,        # thickness multiplier for secondary members
    'depth_ratio': 1.2,             # depth = thickness * ratio
    'node_size_scale': 1.4,         # node block = avg_thickness * scale
    'max_thickness_cap': 1.3,       # cap maximum thickness

    # Floor Slabs
    'floor_spacing': 4.5,           # meters between floors
    'slab_thickness': 0.35,         # meters
    'slab_extend_dist': 0.4,        # meters beyond envelope to nodes
    'slab_node_search_radius': 2.5, # Z tolerance for finding nodes

    # Glass Panels
    'glass_inset': 0.08,            # fractional inset from edges
    'glass_recess': 0.15,           # meters behind structure

    # Materials
    'glass_color_a': (0.08, 0.12, 0.18, 1.0),
    'glass_color_b': (0.06, 0.10, 0.16, 1.0),
    'glass_transmission': 0.65,
    'rc_primary_color': (0.30, 0.29, 0.27, 1.0),
    'rc_secondary_color': (0.35, 0.34, 0.32, 1.0),
    'rc_node_color': (0.25, 0.24, 0.22, 1.0),
    'slab_color': (0.35, 0.34, 0.32, 1.0),
    'envelope_color': (0.08, 0.12, 0.18, 1.0),
}


# ============================================================
# PHASE 1: FLOOR EXTRACTION
# ============================================================
def extract_floors():
    """Group all mesh geometry by floor (Z clustering), compute convex hulls."""
    print("\n=== PHASE 1: FLOOR EXTRACTION ===")
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']

    obj_data = []
    for obj in meshes:
        bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        zmin = min(v.z for v in bb)
        zmax = max(v.z for v in bb)
        obj_data.append({
            'obj': obj,
            'zmin': zmin, 'zmax': zmax,
            'zmid': (zmin + zmax) / 2.0,
            'xy_pts': [(v.x, v.y) for v in bb]
        })

    obj_data.sort(key=lambda d: d['zmid'])

    # Cluster by Z
    floors_raw = []
    current = [obj_data[0]]
    for od in obj_data[1:]:
        if abs(od['zmid'] - current[-1]['zmid']) < 1.5:
            current.append(od)
        else:
            floors_raw.append(current)
            current = [od]
    floors_raw.append(current)

    floor_info = []
    for fobjs in floors_raw:
        zmin = min(od['zmin'] for od in fobjs)
        zmax = max(od['zmax'] for od in fobjs)
        axy = []
        for od in fobjs:
            axy.extend(od['xy_pts'])
        floor_info.append({
            'zmin': zmin, 'zmax': zmax,
            'zmid': (zmin + zmax) / 2.0,
            'xy_pts': axy
        })

    print(f"  Extracted {len(floor_info)} floors from {len(meshes)} objects")
    return floor_info, meshes


# ============================================================
# PHASE 2: FACETED ENVELOPE
# ============================================================
def convex_hull_2d(points):
    pts = list(set(points))
    if len(pts) < 3:
        return pts
    start = min(pts, key=lambda p: (p[1], p[0]))
    pts.sort(key=lambda p: math.atan2(p[1] - start[1], p[0] - start[0]))
    hull = [pts[0], pts[1]]
    for p in pts[2:]:
        while len(hull) > 1:
            o, a, b = hull[-2], hull[-1], p
            if (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0]) <= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def build_envelope(floor_info):
    """Build faceted, asymmetric, tapered tower envelope."""
    print("\n=== PHASE 2: FACETED ENVELOPE ===")
    NV = CONFIG['num_perimeter_verts']

    # Global bounds
    all_x = [p[0] for fi in floor_info for p in fi['xy_pts']]
    all_y = [p[1] for fi in floor_info for p in fi['xy_pts']]
    cx = (min(all_x) + max(all_x)) / 2
    cy = (min(all_y) + max(all_y)) / 2
    nf = len(floor_info)
    tz = floor_info[0]['zmin']
    th = floor_info[-1]['zmax'] - tz

    # Angular sampling for consistent vertex correspondence
    sample_angles = [i * 2 * math.pi / NV for i in range(NV)]

    floor_radii = []
    floor_profiles = []
    for fi_idx, fi in enumerate(floor_info):
        hull = convex_hull_2d(fi['xy_pts'])
        profile = []
        radii = []
        for ai, angle in enumerate(sample_angles):
            dx, dy = math.cos(angle), math.sin(angle)
            max_t = 0
            for i in range(len(hull)):
                p1, p2 = hull[i], hull[(i+1) % len(hull)]
                ex, ey = p2[0]-p1[0], p2[1]-p1[1]
                denom = dx*ey - dy*ex
                if abs(denom) < 1e-10:
                    continue
                t = ((p1[0]-cx)*ey - (p1[1]-cy)*ex) / denom
                s = ((p1[0]-cx)*dy - (p1[1]-cy)*dx) / denom
                if t > 0 and 0 <= s <= 1 and t > max_t:
                    max_t = t
            # Enforce monotonic decrease
            if fi_idx > 0 and max_t > floor_radii[fi_idx-1][ai]:
                max_t = floor_radii[fi_idx-1][ai]
            radii.append(max_t)
            profile.append((cx + dx*max_t, cy + dy*max_t))
        floor_radii.append(radii)
        floor_profiles.append(profile)

    # Vertical smoothing
    smoothed = []
    for fi_idx in range(nf):
        sv = []
        for vi in range(NV):
            sx, sy, c = 0, 0, 0
            for di in range(-1, 2):
                ni = fi_idx + di
                if 0 <= ni < nf:
                    sx += floor_profiles[ni][vi][0]
                    sy += floor_profiles[ni][vi][1]
                    c += 1
            sv.append((sx/c, sy/c))
        smoothed.append(sv)

    # Transform: drift + asymmetric taper + crown
    drift_angles = [random.uniform(0, 2*math.pi) for _ in range(NV)]
    drift_rates = [random.uniform(*CONFIG['drift_rate_range']) for _ in range(NV)]
    taper = CONFIG['taper_per_vert']

    crown_start_frac = CONFIG['crown_start_frac']
    peak_verts = random.sample(range(NV), 3)
    crown_max = []
    for vi in range(NV):
        if vi in peak_verts:
            crown_max.append(random.uniform(*CONFIG['crown_peak_offset']))
        else:
            crown_max.append(random.uniform(*CONFIG['crown_valley_offset']))

    transformed = []
    for fi_idx in range(nf):
        zb = floor_info[fi_idx]['zmid']
        t = max(0, (zb - tz) / th)
        verts = []
        for vi in range(NV):
            x, y = smoothed[fi_idx][vi]
            # Drift
            x += math.cos(drift_angles[vi]) * drift_rates[vi] * fi_idx
            y += math.sin(drift_angles[vi]) * drift_rates[vi] * fi_idx
            # Asymmetric taper
            tf = 1.0 - t * taper[vi]
            x = cx + (x - cx) * tf
            y = cy + (y - cy) * tf
            # Crown
            z = zb
            if t > crown_start_frac:
                ct = (t - crown_start_frac) / (1.0 - crown_start_frac)
                crown_curve = math.sin(ct * math.pi * 0.5)
                z += crown_max[vi] * crown_curve
            verts.append((x, y, z))
        transformed.append(verts)

    # Add blunted cap profiles
    top = transformed[-1]
    top_cx2 = sum(v[0] for v in top) / NV
    top_cy2 = sum(v[1] for v in top) / NV
    top_avg_z = sum(v[2] for v in top) / NV
    for ci in range(1, CONFIG['num_cap_levels'] + 1):
        frac = ci / CONFIG['num_cap_levels']
        cap = []
        for vi in range(NV):
            x, y, z = top[vi]
            x += (top_cx2 - x) * frac * 0.5
            y += (top_cy2 - y) * frac * 0.5
            z += (top_avg_z - z) * frac * 0.7 + ci * 0.8
            shrink = 1.0 - frac * 0.25
            x = cx + (x - cx) * shrink
            y = cy + (y - cy) * shrink
            cap.append((x, y, z))
        transformed.append(cap)

    nf_total = len(transformed)

    # Subdivide
    SUBDIV = CONFIG['envelope_subdivisions']
    final_profiles = []
    for fi_idx in range(nf_total - 1):
        final_profiles.append(transformed[fi_idx])
        for s in range(1, SUBDIV + 1):
            frac2 = s / (SUBDIV + 1)
            interp = [(
                transformed[fi_idx][vi][0] + (transformed[fi_idx+1][vi][0]-transformed[fi_idx][vi][0])*frac2,
                transformed[fi_idx][vi][1] + (transformed[fi_idx+1][vi][1]-transformed[fi_idx][vi][1])*frac2,
                transformed[fi_idx][vi][2] + (transformed[fi_idx+1][vi][2]-transformed[fi_idx][vi][2])*frac2
            ) for vi in range(NV)]
            final_profiles.append(interp)
    final_profiles.append(transformed[-1])

    # Build mesh
    base_z = floor_info[0]['zmin']
    base_prof = [(v[0], v[1], base_z) for v in final_profiles[0]]
    all_verts = list(base_prof)
    for prof in final_profiles:
        all_verts.extend(prof)

    n_profs = len(final_profiles) + 1
    all_faces = []
    for pi in range(n_profs - 1):
        oa = pi * NV
        ob = (pi + 1) * NV
        for vi in range(NV):
            all_faces.append((oa+vi, oa+(vi+1)%NV, ob+(vi+1)%NV, ob+vi))
    all_faces.append(tuple(reversed(range(NV))))
    top_off = (n_profs - 1) * NV
    all_faces.append(tuple(top_off + i for i in range(NV)))

    mesh = bpy.data.meshes.new("53W53_Envelope")
    mesh.from_pydata(all_verts, [], all_faces)
    mesh.update()
    env_obj = bpy.data.objects.new("53W53_Envelope", mesh)
    bpy.context.collection.objects.link(env_obj)

    # Smooth + edge split
    bpy.context.view_layer.objects.active = env_obj
    env_obj.select_set(True)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_add(type='EDGE_SPLIT')
    env_obj.modifiers["EdgeSplit"].split_angle = math.radians(30)

    # Flatten top rings
    import bmesh
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(env_obj.data)
    bm.verts.ensure_lookup_table()
    n_verts = len(bm.verts)
    zmax_env = max(v.co.z for v in bm.verts)
    for ring_idx in range(CONFIG['flatten_top_rings']):
        ring_start = n_verts - (ring_idx + 1) * NV
        blend = 1.0 if ring_idx < 3 else max(0, 1.0 - (ring_idx - 2) / 6)
        for vi in range(NV):
            v = bm.verts[ring_start + vi]
            target_z = zmax_env - ring_idx * 0.3
            v.co.z = v.co.z + (target_z - v.co.z) * blend
    bmesh.update_edit_mesh(env_obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Glass material
    mat = bpy.data.materials.new("Tower_Glass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = CONFIG['envelope_color']
        bsdf.inputs['Metallic'].default_value = 0.3
        bsdf.inputs['Roughness'].default_value = 0.02
        try:
            bsdf.inputs['Transmission Weight'].default_value = 0.6
        except:
            try:
                bsdf.inputs['Transmission'].default_value = 0.6
            except:
                pass
    env_obj.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT')

    print(f"  Envelope: {len(all_verts)} verts, {len(all_faces)} faces")
    return env_obj, cx, cy


# ============================================================
# PHASE 3: RC DIAGRID STRUCTURE
# ============================================================
def build_diagrid(env_obj, cx, cy):
    """Generate structurally correct RC diagrid with tapered members."""
    print("\n=== PHASE 3: RC DIAGRID ===")
    ev = env_obj.data.vertices
    NV = CONFIG['num_perimeter_verts']
    n_rings = len(ev) // NV
    zmin = min(v.co.z for v in ev)
    zmax = max(v.co.z for v in ev)
    tower_h = zmax - zmin
    OFFSET = CONFIG['surface_offset']

    rings = []
    for ri in range(n_rings):
        rings.append([Vector(ev[ri*NV+i].co) for i in range(NV)])
    ring_z = [sum(v.z for v in rings[ri])/NV for ri in range(n_rings)]

    def push_out(pt):
        dx = pt.x - cx; dy = pt.y - cy
        ln = math.sqrt(dx*dx + dy*dy)
        if ln < 0.01:
            return Vector(pt)
        return Vector((pt.x + dx/ln*OFFSET, pt.y + dy/ln*OFFSET, pt.z))

    # Diagrid levels
    TARGET_SP = CONFIG['diagrid_floor_spacing']
    diagrid_z = [zmin]
    z = zmin
    while z < zmax - TARGET_SP * 0.5:
        z += TARGET_SP
        diagrid_z.append(min(z, zmax))
    if diagrid_z[-1] < zmax - 1.0:
        diagrid_z.append(zmax)
    n_levels = len(diagrid_z)

    def find_ring(tz):
        return min(range(n_rings), key=lambda ri: abs(ring_z[ri] - tz))

    level_ri = [find_ring(z) for z in diagrid_z]

    # Node generation
    nodes = []
    node_map = {}
    for fi in range(NV):
        fi_next = (fi + 1) % NV
        for li in range(n_levels):
            ri = level_ri[li]
            left = push_out(rings[ri][fi])
            right = push_out(rings[ri][fi_next])
            face_w = (right - left).length
            if face_w < 0.5:
                node_map[(fi, li, 0)] = len(nodes)
                nodes.append(left.lerp(right, 0.5))
                continue
            if li < n_levels - 1:
                ri2 = level_ri[li + 1]
            else:
                ri2 = level_ri[li - 1]
            avg_w = (face_w + (push_out(rings[ri2][(fi+1)%NV]) - push_out(rings[ri2][fi])).length) / 2
            panel_h = abs(diagrid_z[min(li+1, n_levels-1)] - diagrid_z[max(li-1, 0)]) / (2 if 0 < li < n_levels-1 else 1)
            if panel_h < 1:
                panel_h = TARGET_SP
            diag_span = panel_h / math.tan(math.radians(CONFIG['diagrid_angle']))
            n_bays = max(1, round(avg_w / diag_span))
            for bi in range(n_bays + 1):
                t = bi / n_bays
                node_map[(fi, li, bi)] = len(nodes)
                nodes.append(left.lerp(right, t))

    # Merge nodes
    MERGE_TOL = CONFIG['node_merge_tolerance']
    canonical = []
    old_to_new = {}
    for i, pt in enumerate(nodes):
        found = False
        for j, cpt in enumerate(canonical):
            if (pt - cpt).length < MERGE_TOL:
                old_to_new[i] = j
                found = True
                break
        if not found:
            old_to_new[i] = len(canonical)
            canonical.append(pt)
    for key in node_map:
        node_map[key] = old_to_new[node_map[key]]
    nodes = canonical

    # Member generation
    members = set()
    for fi in range(NV):
        for li in range(n_levels - 1):
            bot_keys = sorted([k for k in node_map if k[0]==fi and k[1]==li], key=lambda k: k[2])
            top_keys = sorted([k for k in node_map if k[0]==fi and k[1]==li+1], key=lambda k: k[2])
            bn = [node_map[k] for k in bot_keys]
            tn = [node_map[k] for k in top_keys]
            nb = len(bn); nt = len(tn)
            if nb < 2 or nt < 2:
                if nb >= 1 and nt >= 1 and bn[0] != tn[0]:
                    members.add((min(bn[0], tn[0]), max(bn[0], tn[0])))
                continue
            for i in range(nb - 1):
                a, b = bn[i], bn[i+1]
                if a != b:
                    members.add((min(a, b), max(a, b)))
            if nb == nt:
                for i in range(nb - 1):
                    a, b = bn[i], tn[i+1]
                    if a != b:
                        members.add((min(a, b), max(a, b)))
                    a, b = bn[i+1], tn[i]
                    if a != b:
                        members.add((min(a, b), max(a, b)))
            else:
                for i in range(nb):
                    tf = i / max(1, nb-1)
                    ti = int(tf * (nt-1))
                    for t in [ti, min(ti+1, nt-1)]:
                        a, b = bn[i], tn[t]
                        if a != b:
                            members.add((min(a, b), max(a, b)))
                for i in range(nt):
                    tf = i / max(1, nt-1)
                    bi2 = int(tf * (nb-1))
                    for b2 in [bi2, min(bi2+1, nb-1)]:
                        a, b = tn[i], bn[b2]
                        if a != b:
                            members.add((min(a, b), max(a, b)))
        top_keys2 = sorted([k for k in node_map if k[0]==fi and k[1]==n_levels-1], key=lambda k: k[2])
        tn2 = [node_map[k] for k in top_keys2]
        for i in range(len(tn2) - 1):
            a, b = tn2[i], tn2[i+1]
            if a != b:
                members.add((min(a, b), max(a, b)))

    # Filter by angle + length + dead-ends
    ANGLE_TOL = CONFIG['angle_tolerance']
    MIN_LEN = CONFIG['min_member_length']
    filtered = set()
    for m in members:
        a = nodes[m[0]]; b = nodes[m[1]]
        d = b - a; horiz = math.sqrt(d.x**2 + d.y**2)
        vert = abs(d.z); length = d.length
        if length < MIN_LEN:
            continue
        if vert < 0.5:
            filtered.add(m)
            continue
        angle = math.degrees(math.atan2(vert, horiz))
        if abs(angle - 60) < ANGLE_TOL or abs(angle - 45) < ANGLE_TOL:
            filtered.add(m)

    for _ in range(5):
        nd = defaultdict(int)
        for m in filtered:
            nd[m[0]] += 1; nd[m[1]] += 1
        to_rm = {m for m in filtered if nd[m[0]] < 2 or nd[m[1]] < 2}
        if not to_rm:
            break
        filtered -= to_rm

    # Hierarchy + sizing
    member_list = []
    node_deg = defaultdict(int)
    for m in filtered:
        node_deg[m[0]] += 1; node_deg[m[1]] += 1

    lengths_all = sorted((nodes[m[1]] - nodes[m[0]]).length for m in filtered)
    median_len = lengths_all[len(lengths_all) // 2]

    for m in filtered:
        p0 = nodes[m[0]]; p1 = nodes[m[1]]
        zmid = (p0.z + p1.z) / 2
        h = max(0, min(1, (zmid - zmin) / tower_h))
        length = (p1 - p0).length
        dz = abs(p0.z - p1.z)
        is_diag = dz > 1.0
        deg_avg = (node_deg[m[0]] + node_deg[m[1]]) / 2

        base_thick = CONFIG['thickness_base'] + (CONFIG['thickness_top'] - CONFIG['thickness_base']) * h

        if is_diag and length >= median_len * 0.8 and deg_avg >= 3:
            hierarchy = 'PRIMARY'
            thick = base_thick * CONFIG['primary_scale']
        else:
            hierarchy = 'SECONDARY'
            thick = base_thick * CONFIG['secondary_scale']

        member_list.append({
            'idx': m, 'p0': p0, 'p1': p1, 'thickness': thick,
            'hierarchy': hierarchy, 'h': h
        })

    # Smooth transitions
    m_adj = defaultdict(list)
    for i, md in enumerate(member_list):
        m_adj[md['idx'][0]].append(i)
        m_adj[md['idx'][1]].append(i)

    for _ in range(3):
        new_t = [md['thickness'] for md in member_list]
        for i, md in enumerate(member_list):
            nbrs = set()
            for ni in md['idx']:
                for mi in m_adj[ni]:
                    if mi != i:
                        nbrs.add(mi)
            if not nbrs:
                continue
            avg_n = sum(member_list[j]['thickness'] for j in nbrs) / len(nbrs)
            ratio = md['thickness'] / max(avg_n, 0.01)
            if ratio > 1.4 or ratio < 0.6:
                new_t[i] = md['thickness'] * 0.7 + avg_n * 0.3
        for i, md in enumerate(member_list):
            md['thickness'] = new_t[i]

    # Cap overweight
    for md in member_list:
        if md['thickness'] > CONFIG['max_thickness_cap']:
            md['thickness'] *= 0.85
        md['width'] = md['thickness']
        md['depth'] = md['thickness'] * CONFIG['depth_ratio']

    print(f"  Nodes: {len(nodes)}, Members: {len(member_list)}")
    pri = sum(1 for md in member_list if md['hierarchy'] == 'PRIMARY')
    print(f"  PRIMARY: {pri}, SECONDARY: {len(member_list) - pri}")
    tt = [md['thickness'] for md in member_list]
    print(f"  Thickness: {min(tt):.2f}m – {max(tt):.2f}m")

    return nodes, member_list, zmin, zmax, tower_h, diagrid_z


# ============================================================
# PHASE 4: CREATE RC GEOMETRY
# ============================================================
def create_rc_geometry(nodes, member_list, cx, cy):
    """Create solid rectangular prism beams + node blocks."""
    print("\n=== PHASE 4: RC GEOMETRY ===")

    # Materials
    mat_pri = bpy.data.materials.new("RC_Primary")
    mat_pri.use_nodes = True
    b = mat_pri.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = CONFIG['rc_primary_color']
    b.inputs['Roughness'].default_value = 0.85

    mat_sec = bpy.data.materials.new("RC_Secondary")
    mat_sec.use_nodes = True
    b2 = mat_sec.node_tree.nodes.get("Principled BSDF")
    b2.inputs['Base Color'].default_value = CONFIG['rc_secondary_color']
    b2.inputs['Roughness'].default_value = 0.88

    mat_node = bpy.data.materials.new("RC_Node")
    mat_node.use_nodes = True
    b3 = mat_node.node_tree.nodes.get("Principled BSDF")
    b3.inputs['Base Color'].default_value = CONFIG['rc_node_color']
    b3.inputs['Roughness'].default_value = 0.82

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    parent = bpy.context.active_object
    parent.name = "53W53_RC_Structure"

    def create_beam(p0, p1, width, depth, name, material):
        hw = width / 2; hd = depth / 2
        direction = p1 - p0
        length = direction.length
        if length < 0.1:
            return None
        mid = (p0 + p1) / 2
        z_axis = direction.normalized()
        to_out = Vector((mid.x - cx, mid.y - cy, 0))
        if to_out.length < 0.01:
            to_out = Vector((1, 0, 0))
        to_out.normalize()
        y_axis = z_axis.cross(to_out)
        if y_axis.length < 0.01:
            y_axis = Vector((0, 0, 1)).cross(to_out)
        y_axis.normalize()
        x_axis = y_axis.cross(z_axis)
        x_axis.normalize()

        verts = []
        for end in [-0.5, 0.5]:
            pt = mid + z_axis * (length * end)
            for sx in [-1, 1]:
                for sy in [-1, 1]:
                    verts.append(tuple(pt + x_axis*(hd*sx) + y_axis*(hw*sy)))
        faces = [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        mesh.materials.append(material)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        return obj

    # Build beams
    n_beams = 0
    for i, md in enumerate(member_list):
        mat = mat_pri if md['hierarchy'] == 'PRIMARY' else mat_sec
        prefix = "P" if md['hierarchy'] == 'PRIMARY' else "S"
        obj = create_beam(md['p0'], md['p1'], md['width'], md['depth'],
                          f"RC_{prefix}_{i:04d}", mat)
        if obj:
            obj.parent = parent
            n_beams += 1

    # Node blocks
    node_info = defaultdict(list)
    for md in member_list:
        k0 = (round(md['p0'].x,1), round(md['p0'].y,1), round(md['p0'].z,1))
        k1 = (round(md['p1'].x,1), round(md['p1'].y,1), round(md['p1'].z,1))
        node_info[k0].append(md['width'])
        node_info[k1].append(md['width'])

    n_nodes = 0
    for pos_key, thicknesses in node_info.items():
        if len(thicknesses) < 3:
            continue
        avg_t = sum(thicknesses) / len(thicknesses)
        ns = avg_t * CONFIG['node_size_scale']
        pos = Vector(pos_key)
        hn = ns / 2; hh = ns * 0.4
        dx = pos.x - cx; dy = pos.y - cy
        ln = math.sqrt(dx*dx + dy*dy)
        if ln < 0.01:
            dx, dy, ln = 1, 0, 1
        ox, oy = dx/ln, dy/ln
        px, py = -oy, ox
        verts = []
        for sz in [-1, 1]:
            for sx in [-1, 1]:
                for sy in [-1, 1]:
                    verts.append((pos.x+ox*hn*sx+px*hn*sy, pos.y+oy*hn*sx+py*hn*sy, pos.z+hh*sz))
        faces = [(0,1,3,2),(4,5,7,6),(0,1,5,4),(2,3,7,6),(0,2,6,4),(1,3,7,5)]
        mesh = bpy.data.meshes.new(f"Node_{n_nodes:03d}")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        mesh.materials.append(mat_node)
        nobj = bpy.data.objects.new(f"Node_{n_nodes:03d}", mesh)
        nobj.parent = parent
        bpy.context.collection.objects.link(nobj)
        n_nodes += 1

    print(f"  Beams: {n_beams}, Nodes: {n_nodes}")
    return parent


# ============================================================
# PHASE 5: FLOOR SLABS
# ============================================================
def build_slabs(env_obj, nodes_dg, zmin, zmax, cx, cy):
    """Create floor slabs extending to diagrid nodes."""
    print("\n=== PHASE 5: FLOOR SLABS ===")
    ev = env_obj.data.vertices
    NV = CONFIG['num_perimeter_verts']
    n_rings = len(ev) // NV
    rings = []
    for ri in range(n_rings):
        rings.append([Vector(ev[ri*NV+i].co) for i in range(NV)])
    ring_z = [sum(v.z for v in rings[ri])/NV for ri in range(n_rings)]
    tower_h = zmax - zmin

    FLOOR_SP = CONFIG['floor_spacing']
    SLAB_THICK = CONFIG['slab_thickness']
    NODE_SR = CONFIG['slab_node_search_radius']
    EXTEND = CONFIG['slab_extend_dist']

    floor_z_list = []
    z = zmin
    while z <= zmax + 0.1:
        floor_z_list.append(z)
        z += FLOOR_SP

    def find_ring(tz):
        return min(range(n_rings), key=lambda ri: abs(ring_z[ri] - tz))

    mat_slab = bpy.data.materials.new("RC_Slab")
    mat_slab.use_nodes = True
    bsdf = mat_slab.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = CONFIG['slab_color']
    bsdf.inputs['Roughness'].default_value = 0.9

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    slab_parent = bpy.context.active_object
    slab_parent.name = "53W53_Slabs"

    N_SUBDIV = 6
    n_slabs = 0
    for fi, fz in enumerate(floor_z_list):
        ri = find_ring(fz)
        ring = rings[ri]
        perim = sum((ring[(i+1)%NV] - ring[i]).length for i in range(NV))
        if perim < 5.0:
            continue

        nearby_nodes = [n for n in nodes_dg if abs(n.z - fz) < NODE_SR]

        slab_outline = []
        for ei in range(NV):
            p0 = ring[ei]; p1 = ring[(ei+1)%NV]
            for si in range(N_SUBDIV):
                t = si / N_SUBDIV
                pt = p0.lerp(p1, t)
                best_ext = 0
                for nn in nearby_nodes:
                    dxy = math.sqrt((pt.x-nn.x)**2 + (pt.y-nn.y)**2)
                    if dxy < 3.0:
                        best_ext = max(best_ext, EXTEND * (1.0 - dxy/3.0))
                dx = pt.x - cx; dy = pt.y - cy
                ln = math.sqrt(dx*dx + dy*dy)
                if ln > 0.01 and best_ext > 0:
                    pt = Vector((pt.x+dx/ln*best_ext, pt.y+dy/ln*best_ext, fz))
                else:
                    pt = Vector((pt.x, pt.y, fz))
                slab_outline.append(pt)

        for nn in nearby_nodes:
            d_node = math.sqrt((nn.x-cx)**2 + (nn.y-cy)**2)
            d_env = max(math.sqrt((v.x-cx)**2+(v.y-cy)**2) for v in ring)
            if d_node > d_env * 0.7:
                slab_outline.append(Vector((nn.x, nn.y, fz)))

        slab_outline.sort(key=lambda pt: math.atan2(pt.y-cy, pt.x-cx))
        cleaned = [slab_outline[0]]
        for pt in slab_outline[1:]:
            if (pt - cleaned[-1]).length > 0.3:
                cleaned.append(pt)
        slab_outline = cleaned
        if len(slab_outline) < 4:
            continue

        n_pts = len(slab_outline)
        thick = SLAB_THICK + (fi % 3) * 0.02
        top_v = [(pt.x, pt.y, fz) for pt in slab_outline]
        bot_v = [(pt.x, pt.y, fz - thick) for pt in slab_outline]
        all_v = top_v + bot_v
        ct_idx = len(all_v); all_v.append((cx, cy, fz))
        cb_idx = len(all_v); all_v.append((cx, cy, fz - thick))
        all_f = []
        for i in range(n_pts):
            all_f.append((ct_idx, i, (i+1)%n_pts))
            all_f.append((cb_idx, n_pts+(i+1)%n_pts, n_pts+i))
            all_f.append((i, (i+1)%n_pts, n_pts+(i+1)%n_pts, n_pts+i))

        mesh = bpy.data.meshes.new(f"Slab_F{fi:02d}")
        mesh.from_pydata(all_v, [], all_f)
        mesh.update()
        mesh.materials.append(mat_slab)
        obj = bpy.data.objects.new(f"Slab_F{fi:02d}", mesh)
        obj.parent = slab_parent
        bpy.context.collection.objects.link(obj)
        n_slabs += 1

    bpy.ops.object.select_all(action='DESELECT')
    print(f"  Slabs: {n_slabs}")
    return slab_parent


# ============================================================
# PHASE 6: GLASS INFILL PANELS
# ============================================================
def build_glass_panels(nodes, member_list, cx, cy):
    """Create triangular and quad glass infill panels."""
    print("\n=== PHASE 6: GLASS INFILL ===")

    # Build adjacency from members
    MERGE_TOL = CONFIG['node_merge_tolerance']
    node_pts = []
    nlookup = {}

    def gn(pt):
        key = (round(pt.x,1), round(pt.y,1), round(pt.z,1))
        if key in nlookup:
            return nlookup[key]
        pv = Vector(pt)
        for i, n in enumerate(node_pts):
            if (pv-n).length < MERGE_TOL:
                nlookup[key] = i
                return i
        idx = len(node_pts)
        node_pts.append(pv)
        nlookup[key] = idx
        return idx

    edge_set = set()
    for md in member_list:
        a = gn(md['p0']); b = gn(md['p1'])
        if a != b:
            edge_set.add((min(a,b), max(a,b)))

    adj = defaultdict(set)
    for a, b in edge_set:
        adj[a].add(b); adj[b].add(a)

    # Find triangles
    triangles = set()
    for a in range(len(node_pts)):
        for b in adj[a]:
            if b <= a: continue
            for c in (adj[a] & adj[b]):
                if c <= b: continue
                triangles.add((a, b, c))

    # Find quads
    quads = set()
    for a in range(len(node_pts)):
        for b in adj[a]:
            if b <= a: continue
            for c in adj[b]:
                if c == a: continue
                for d in (adj[c] & adj[a]):
                    if d == b or d == a or d == c: continue
                    quads.add(tuple(sorted([a, b, c, d])))

    # Materials
    mat_g1 = bpy.data.materials.new("Glass_Panel_A")
    mat_g1.use_nodes = True
    bs = mat_g1.node_tree.nodes.get("Principled BSDF")
    bs.inputs['Base Color'].default_value = CONFIG['glass_color_a']
    bs.inputs['Metallic'].default_value = 0.15
    bs.inputs['Roughness'].default_value = 0.03
    try: bs.inputs['Transmission Weight'].default_value = CONFIG['glass_transmission']
    except:
        try: bs.inputs['Transmission'].default_value = CONFIG['glass_transmission']
        except: pass

    mat_g2 = bpy.data.materials.new("Glass_Panel_B")
    mat_g2.use_nodes = True
    bs2 = mat_g2.node_tree.nodes.get("Principled BSDF")
    bs2.inputs['Base Color'].default_value = CONFIG['glass_color_b']
    bs2.inputs['Metallic'].default_value = 0.2
    bs2.inputs['Roughness'].default_value = 0.05
    try: bs2.inputs['Transmission Weight'].default_value = 0.55
    except:
        try: bs2.inputs['Transmission'].default_value = 0.55
        except: pass

    INSET = CONFIG['glass_inset']
    RECESS = CONFIG['glass_recess']

    all_verts = []
    all_faces = []
    face_mats = []

    # Triangles
    for tri in triangles:
        pa = node_pts[tri[0]]; pb = node_pts[tri[1]]; pc = node_pts[tri[2]]
        ab = pb-pa; ac = pc-pa
        area = ab.cross(ac).length / 2
        l1 = (pb-pa).length; l2 = (pc-pa).length; l3 = (pc-pb).length
        if area < 2.0 or min(l1,l2,l3) < 1.5 or max(l1,l2,l3) > 16:
            continue
        tc = (pa+pb+pc) / 3
        pts = [pa.lerp(tc, INSET), pb.lerp(tc, INSET), pc.lerp(tc, INSET)]
        for pt in pts:
            dx = pt.x-cx; dy = pt.y-cy; ln = math.sqrt(dx*dx+dy*dy)
            if ln > 0.01:
                pt.x -= dx/ln*RECESS; pt.y -= dy/ln*RECESS
        vi = len(all_verts)
        all_verts.extend([tuple(p) for p in pts])
        all_faces.append((vi, vi+1, vi+2))
        face_mats.append(hash(tri) % 2)

    # Quads
    for q in quads:
        pts = [node_pts[i] for i in q]
        qc = sum((p for p in pts), Vector()) / 4
        ab2 = pts[1]-pts[0]; ac2 = pts[2]-pts[0]
        normal = ab2.cross(ac2)
        if normal.length < 0.01: continue
        normal.normalize()
        u_ax = (pts[0]-qc).normalized()
        v_ax = normal.cross(u_ax).normalized()
        angles = [(math.atan2((p-qc).dot(v_ax), (p-qc).dot(u_ax)), p) for p in pts]
        angles.sort()
        sorted_pts = [a[1] for a in angles]
        area2 = sum(
            (sorted_pts[(i+1)%4]-qc).cross(sorted_pts[i]-qc).length/2
            for i in range(4)
        )
        edges_l = [(sorted_pts[(i+1)%4]-sorted_pts[i]).length for i in range(4)]
        if area2 < 3.0 or min(edges_l) < 1.5 or max(edges_l) > 18:
            continue
        pts_in = [p.lerp(qc, INSET) for p in sorted_pts]
        for pt in pts_in:
            dx = pt.x-cx; dy = pt.y-cy; ln = math.sqrt(dx*dx+dy*dy)
            if ln > 0.01:
                pt.x -= dx/ln*RECESS; pt.y -= dy/ln*RECESS
        vi = len(all_verts)
        all_verts.extend([tuple(p) for p in pts_in])
        all_faces.append((vi, vi+1, vi+2, vi+3))
        face_mats.append(hash(q) % 2)

    glass_mesh = bpy.data.meshes.new("Glass_Panels")
    glass_mesh.from_pydata(all_verts, [], all_faces)
    glass_mesh.update()
    glass_mesh.materials.append(mat_g1)
    glass_mesh.materials.append(mat_g2)
    for i, poly in enumerate(glass_mesh.polygons):
        if i < len(face_mats):
            poly.material_index = face_mats[i]

    glass_obj = bpy.data.objects.new("53W53_Glass_Panels", glass_mesh)
    bpy.context.collection.objects.link(glass_obj)
    bpy.context.view_layer.objects.active = glass_obj
    glass_obj.select_set(True)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action='DESELECT')

    print(f"  Glass panels: {len(all_faces)} ({len(triangles)} tri + quad search)")
    return glass_obj


# ============================================================
# PHASE 7: SCENE SETUP
# ============================================================
def setup_scene(env_obj):
    """Add ground plane, sky, and set viewport."""
    print("\n=== PHASE 7: SCENE SETUP ===")

    # Ground plane
    bpy.ops.mesh.primitive_plane_add(size=200, location=(20, 20, -4.5))
    ground = bpy.context.active_object
    ground.name = "Ground_Plane"
    mat_g = bpy.data.materials.new("Ground")
    mat_g.use_nodes = True
    b = mat_g.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.12, 0.12, 0.12, 1.0)
    b.inputs['Roughness'].default_value = 0.85
    ground.data.materials.append(mat_g)

    # Sky environment
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    nodes_w = world.node_tree.nodes
    links = world.node_tree.links
    for node in nodes_w:
        nodes_w.remove(node)
    bg = nodes_w.new('ShaderNodeBackground')
    sky = nodes_w.new('ShaderNodeTexSky')
    sky.sky_type = 'HOSEK_WILKIE'
    sky.turbidity = 3.0
    output = nodes_w.new('ShaderNodeOutputWorld')
    links.new(sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.2
    links.new(bg.outputs['Background'], output.inputs['Surface'])

    # Hide original massing, show envelope
    env_obj.hide_set(False)

    bpy.ops.object.select_all(action='DESELECT')
    print("  Scene setup complete")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("53W53-TYPE TOWER GENERATOR")
    print("=" * 60)

    # Phase 1
    floor_info, original_meshes = extract_floors()

    # Phase 2
    env_obj, cx, cy = build_envelope(floor_info)

    # Hide originals
    for obj in original_meshes:
        obj.hide_set(True)
        obj.hide_render = True

    # Phase 3
    nodes_dg, member_list, zmin, zmax, tower_h, diagrid_z = build_diagrid(env_obj, cx, cy)

    # Phase 4
    rc_parent = create_rc_geometry(nodes_dg, member_list, cx, cy)

    # Phase 5
    slab_parent = build_slabs(env_obj, nodes_dg, zmin, zmax, cx, cy)

    # Phase 6
    glass_obj = build_glass_panels(nodes_dg, member_list, cx, cy)

    # Phase 7
    setup_scene(env_obj)

    # Summary
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"  53W53_Envelope        — faceted glass shell")
    print(f"  53W53_RC_Structure    — {len(member_list)} RC beams + nodes")
    print(f"  53W53_Slabs           — floor slabs")
    print(f"  53W53_Glass_Panels    — infill panels")
    print(f"  Ground_Plane          — ground")
    print("=" * 60)


if __name__ == "__main__":
    main()
