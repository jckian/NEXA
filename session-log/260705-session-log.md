# 260705 Session Log

## SHORT kit modules updated from `references/MODULE/rule_build_group_260704.py`

**Request:** replace the SHORT FRAME and INFILL kit geometry in `program-massing-shortfloor.html` with the new Rhino module designs (163 instances / 14 block definitions, exported as a Rhino→Blender script). Stair untouched by request.

**Module mapping (identified by baking all 163 instances to world space):**
| Kit part | Source module | Notes |
|---|---|---|
| `frameH` | `FRAME-HORIZONTAL` | 34-member box truss, local metres, 2×1×1 modules + ±2–5 cm connector overhangs |
| `frameV` | `VERTICALFRAME` baked | CON-UPPER×2 + CON-LOWER×2 + diagonal "1"×2 composed via instance matrices; two "1" matrices are MIRRORED (det<0) → triangle winding flipped during bake |
| `infill` | `1_@ 01` | full 1×2 module frame-and-deck unit (468 v / 302 t), local cm, long axis Y |
| `stair` | — kept as before | |
| (removed) | old `frameH.gray` group | never referenced by geomOf/exports — dead data |

**Conversion (scratchpad/convert_kit.py):** Rhino Z-up → Three Y-up; frames mapped (x,z,−y)·100 (m→cm), infill (y,z,x) (already cm, rotated so long axis = X to match geomOf's 'x' base orientation); module corner kept at origin so connector plates overhang negative — no re-min. Box members re-triangulated with canonical outward winding (original quad order untrustworthy in JS, unlike Blender's from_pydata). BLOCKS JSON patched in place (35,970 chars vs old ~previous size); backup at `BACKUP/program-massing-shortfloor.html.bak-260705`.

**Verification:** node JSON/NaN/index-bounds check ✓ · vm syntax ✓ · headless dump-dom: stats render, zero page console errors ✓ · before/after structure-mode screenshots: new modules aligned to same cells, no floaters ✓. Kit OBJ export reads the same BLOCKS → exports updated automatically.

**Known cosmetic gap:** `?mode=structure` URL param sets RENDER_MODE but does not highlight the segmented-control chip (UI shows "Solid massing" active while rendering structure). Harmless for headless verification; fix belongs to ui-panels agent if it ever matters.
