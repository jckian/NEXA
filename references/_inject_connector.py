import rhino3dm as r3
import json, re

SRC = r"C:\SCI-Arc\SP26-RESEARCH\programAgent\references\260620_unitTest_DfD.3dm"
HTML = r"C:\SCI-Arc\SP26-RESEARCH\programAgent\index.html"

f = r3.File3dm.Read(SRC)
layers = {l.Index: l for l in f.Layers}
objbyid = {str(o.Attributes.Id): o for o in f.Objects}
idefs = {d.Name: d for d in f.InstanceDefinitions}

d = idefs['prefab-stru-module']
cn = [o for o in (objbyid.get(str(i)) for i in d.GetObjectIds())
      if o and layers[o.Attributes.LayerIndex].FullPath == 'DfD_test::Connection']
print("connection breps:", len(cn))

MC = (0.0, 0.0, (-428.3 + -1.6) / 2.0)   # module centre (cm)

def tri_of_face(fc):
    a, b, c, e = fc[0], fc[1], fc[2], fc[3]
    return [(a, b, c)] if c == e else [(a, b, c), (a, c, e)]

def extract(brep):
    vmap = {}; pos = []; idx = []
    def vid(p):
        # model cm -> three Y-up metres, rel module centre, 3-dp (mm)
        tx = round((p.X - MC[0]) / 100.0, 3)
        ty = round((p.Z - MC[2]) / 100.0, 3)
        tz = round((p.Y - MC[1]) / 100.0, 3)
        k = (tx, ty, tz)
        if k not in vmap:
            vmap[k] = len(pos) // 3; pos.extend([tx, ty, tz])
        return vmap[k]
    for face in brep.Faces:
        m = face.GetMesh(r3.MeshType.Render)
        if not m or len(m.Vertices) == 0: continue
        ids = [vid(m.Vertices[i]) for i in range(len(m.Vertices))]
        for fi in range(m.Faces.Count):
            for (a, b, c) in tri_of_face(m.Faces[fi]):
                if a != b and b != c and a != c:
                    idx.extend([ids[a], ids[b], ids[c]])
    return pos, idx

nodes = []
for o in cn:
    pos, idx = extract(o.Geometry)
    nodes.append({"pos": pos, "idx": idx})
print("verts/node:", [len(n["pos"]) // 3 for n in nodes])
print("tris/node :", [len(n["idx"]) // 3 for n in nodes])

data = {"unit": "m", "module": 4.2672, "nodes": nodes}
blob = json.dumps(data, separators=(',', ':'))
print("blob bytes:", len(blob))

# also refresh the standalone json
with open(r"C:\SCI-Arc\SP26-RESEARCH\programAgent\references\dfd_connector.json", "w") as fh:
    fh.write(blob)

# inject / replace inline <script id="dfd-connector-data"> before the module script
with open(HTML, "r", encoding="utf-8") as fh:
    html = fh.read()

tag = '<script id="dfd-connector-data">window.__DFD_CONNECTOR__=' + blob + ';</script>'
pat = re.compile(r'<script id="dfd-connector-data">.*?</script>', re.DOTALL)
if pat.search(html):
    html = pat.sub(tag, html)
    print("replaced existing inline connector data")
else:
    anchor = '  <script type="module">'
    i = html.index(anchor)
    html = html[:i] + tag + "\n" + html[i:]
    print("inserted inline connector data before module script")

with open(HTML, "w", encoding="utf-8") as fh:
    fh.write(html)
print("index.html updated; size now", len(html), "bytes")
