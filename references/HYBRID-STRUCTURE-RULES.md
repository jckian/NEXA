# HYBRID-STRUCTURE-RULES

Rules for the **hybrid structure** mode: instead of forcing one structural
system on the whole building, the agent reads each program entry (and the floor
/ geometry it sits in) and **auto-allocates a structural system zone-by-zone**.
One building can therefore mix a diagrid skin, an arch shell, and a framed floor
with a curtain wall — each where it makes structural sense.

This file is the decision spec. It consumes the standard program format
(`ProgramFormat.txt`) and emits a per-entry **structural tag** plus building-wide
**lateral / transfer** assignments. Every tag maps to a real generator already in
`structure-generator/`.

---

## 1. The three buildable system modules

These are the actual systems the repo can build. The allocator's job is to pick
one of these three per zone, then apply the §3.1 element modifiers inside it.

| key | system | generator | what it builds | native zone |
|---|---|---|---|---|
| `SKIN` | **Structural Skin** (diagrid) | `structural_skin_generator.py` | perimeter diagrid tube + ring beams (+ optional glass) that conforms to any massing | slender / tapered / twisted tower **envelope**; doubles as primary lateral |
| `FOAM` | **Structural Foam** (arch shell) | `tama_structural_generator.py` | gridded single-layer arch/vault shell + flat slab, auto-celled from the bbox | low-rise spanning **ground-scape & roof**, public halls, library floors |
| `FRAME` | **Internal Structure + Curtain** | `office_…` / `condo_…` / `curtainBox_architecture_generator.py` | shear-wall **core** + column **grid** + **beams** + **slab** + facade **mullions** + **glass curtain** | regular stacked floors: offices, residential, BOH, podiums |

`FRAME` is the default workhorse. `SKIN` and `FOAM` are envelope/shell
specialists chosen only when the geometry calls for them.

### 1.1 FRAME grid presets (from the generators)

`FRAME` is parametric — pick the grid spacing from the program it wraps:

| preset | `gridSpacing` | floor-to-floor | source | use when |
|---|---|---|---|---|
| `FRAME.cellular` | 6.0 m | 3.8 m | `condo_/curtainBox_…` (Seagram) | residential, hotel, cellular private rooms |
| `FRAME.office`   | 9.0 m | 4.2 m | `office_architecture_generator.py` | offices, flexible public floors, podium |

---

## 2. Inputs the allocator reads (per entry)

Derived directly from `{type}/{area}/{level}/{category}/{w,l}`:

- **`span`** = `max(w, l)` — controlling clear dimension (m)
- **`aspect`** = `max(w,l) / min(w,l)`
- **`area`** (m²)
- **`level`** — `-1` basement, `0` ground, `1..N` upper
- **`category`** — `public` | `private` | `circulation`
- **`type`** — substring-matched (same convention as adjacency rules)

Building-scope inputs (from the whole distribution + site):

- **`Hfloors`** — total floor count; **`tall = Hfloors ≥ 20`**
- **`taper`** — footprint shrinks with height? (53W53-style → favours `SKIN`)
- **`lowRiseSpan`** — building is low-rise (≤ ~4 floors) and dominated by large
  public spans? (TAMA-style → favours `FOAM`)
- **`podiumTop`** — highest level still using the full site footprint
- **`mepFloors`** — levels flagged as mechanical/plant

---

## 3. Module allocation rules (priority-ordered, first match wins)

Step A — pick the **module** (`SKIN` / `FOAM` / `FRAME`) for the entry:

```
A0  SKIN    tall AND taper AND entry is on the perimeter ring
             → SKIN          (envelope carries gravity + lateral; 53W53)

A1  FOAM    lowRiseSpan AND category == 'public'
             AND span 3–12 AND aspect ≤ 2
             AND (level == 0 OR level is top/roof)
             → FOAM          (arch/vault ground-scape & roof; TAMA)

A2  FRAME   default — everything else
             → FRAME, then choose preset:
                 FRAME.office   if category == 'public' OR span ≥ 9
                 FRAME.cellular otherwise
```

Step B — apply **element modifiers** inside the chosen module (§3.1). These
override the local bay/element, not the whole module.

### 3.1 Element modifiers (override a bay within the module)

```
M0  CORE      type contains 'fire stair' | 'elevator' | 'core'
               → that footprint becomes a shear-wall CORE
                 (always; the FRAME core block, also the lateral spine)

M1  MEGA      level == 0 AND category == 'public'        (pilotis / lifted ground)
               OR entry sits on a +X/-X/-Z protrusion / cantilever
               → replace columns under it with MEGA-columns + transfer

M2  LONGSPAN  span ≥ 15
               OR (category == 'public' AND area ≥ 400)
               OR type contains 'hall'|'theater'|'event'|'auditorium'
                     |'lobby'|'gallery'|'lounge'|'playhouse'
               → replace the regular grid in that bay with LONGSPAN
                 trusses / vierendeel / transfer girders (column-free room)

M3  OUTRIGGER level in mepFloors  (and primary lateral wants it — §4)
               → add belt/outrigger truss tying CORE to perimeter
```

Notes:
- A single floor normally comes out **mixed**: cores `CORE`, big rooms
  `LONGSPAN`, the rest `FRAME` grid. Inside a `SKIN` tower the *interior* is still
  `FRAME`/`CORE`; the diagrid is only the envelope. That layering *is* the hybrid.
- `15` (long-span trigger) and `9` (wide-bay / office trigger) are the spine
  thresholds — expose both as tunable parameters.

---

## 4. Building-wide lateral system selection

Cores (`CORE`) are always present. This decides what resists wind/seismic:

```
if taper OR slender tower (footprint diagonal / height ≤ ~1/7):
    primaryLateral = SKIN              # perimeter diagrid tube (53W53)
elif tall (≥ 20 floors):
    primaryLateral = CORE + OUTRIGGER  # core + outrigger at MEP floors
elif lowRiseSpan:
    primaryLateral = FOAM + CORE       # shell action + cores (TAMA)
else:                                  # low/mid-rise framed (TPAC-like)
    primaryLateral = CORE + MEGA frame # core walls braced by mega-frame
```

**Outrigger placement** (`M3`): at every `mepFloors` level, plus one near
mid-height (`round(Hfloors/2)`) if none lands there. Only when `primaryLateral`
includes `OUTRIGGER`.

---

## 5. Transfer / transition rules (where systems change vertically)

A tag must not flip floor-to-floor without a load path. On a change in a vertical
stack, insert a **transfer condition**:

1. **Vertical discontinuity** — if a `FRAME` column line does not continue to the
   floor below (a `LONGSPAN`/`MEGA` void below), the floor above the change is a
   **transfer floor**: tag its primary beams `LONGSPAN` and thicken to transfer
   depth.
2. **Podium → tower** — force a transfer floor at `podiumTop + 1`. Below =
   full-footprint `FRAME.office`/`MEGA`; above = tower lateral (`SKIN` or
   `CORE+OUTRIGGER`).
3. **Module change `FRAME` → `SKIN`** — where the framed interior meets the
   diagrid envelope, the perimeter `FRAME` columns at that level hand their
   gravity load to the diagrid nodes via the ring beam; verify a diagrid node
   exists within `≤ gridSpacing/2` of each perimeter column, else densify
   `PERIMETER_DIVISIONS`.
4. **Module change `FRAME`/`FOAM` at grade** — a `FOAM` shell springs from grade
   or from a stiff ring beam; do not land a `FOAM` arch foot on a `LONGSPAN`
   void. If it does, insert a transfer ring beam at the spring line.
5. **Protrusion / cantilever** — any `MEGA`/`LONGSPAN` overhang must root into a
   `CORE` or mega-column within `≤ 1.5 × span` horizontally, else reject (flag the
   layout agent to move it).
6. **Core continuity** — `CORE` stacks must be continuous foundation→top; verify
   and warn if a core type is missing on an intermediate floor.
7. **SHORT-kit → LONG-frame boundary clearance** — a run of consecutive SHORT
   (8'-6" module-kit) floors is filled on a continuous course grid whose actual
   height can differ from the run's nominal floor-height sum (the course count
   is bumped up whenever the SHORT footprint area needs more courses than the
   nominal run height supplies — see `buildShortBlocks`' K computation in
   `program-massing-shortfloor.html`). The first LONG floor above such a run must
   have its underside — the lowest point of its hang-below structure (main
   girder depth, the deepest member) — sit at or above the SHORT stack's TRUE
   top, not the nominal one. Required clearance = `stackTop + mainGirderDepth −
   nominalYBaseOfBoundaryFloor`; if positive, translate that floor and every
   level above it upward by the shortfall (floor-to-floor heights unchanged —
   this is a rigid shift, not a per-floor stretch). Implemented in
   `buildStructure`'s SHORT-STACK BOUNDARY SHIFT block (re-derives the SHORT
   run's course count read-only; never edits `buildShortBlocks`).

---

## 6. Output format

Two options — both keep `ProgramFormat.txt` intact.

**(a) Inline tag** — append a 6th field `{MODULE[.preset][+MODIFIER]}`:

```
{type}/{area}/{level}/{category}/{w,l}/{STRUCT}
{event hall}/520/2/public/24,30/FRAME.office+LONGSPAN
{apartments}/180/40/private/12,15/SKIN          ← perimeter of tapered tower
{offices}/200/5/public/12,15/FRAME.office
{reading hall}/300/0/public/10,10/FOAM
{storage}/40/-1/private/6,8/FRAME.cellular
{fire stair and elevator 1}/150/3/circulation/10,12/CORE
```

Parsers that don't expect the field ignore it (split on `/`, read `[5]` if
present). Visualizers can color by `STRUCT` instead of `type`.

**(b) Sidecar file** — `fileTransfer/structure.txt`, one line per entry index,
with a building-wide header:

```
## LATERAL: SKIN+CORE
## OUTRIGGER_FLOORS: 16,32
## TRANSFER_FLOORS: 4
0  CORE
1  SKIN
2  FRAME.office+LONGSPAN
...
```

Recommended: **(a)** for LLM generation (self-describing); **(b)** when a Blender
generator needs the building-wide lateral header.

### 6.1 Tag → generator routing

| tag | generator invoked | per-zone params passed |
|---|---|---|
| `SKIN` | `structural_skin_generator.py` | `FLOOR_HEIGHT`, `PERIMETER_DIVISIONS`, taper from massing |
| `FOAM` | `tama_structural_generator.py` | `CELL`(=span band), `FLOOR_HEIGHT`(=arch rise) |
| `FRAME.cellular` | `condo_/curtainBox_architecture_generator.py` | `GRID=6`, `FLOOR_HEIGHT=3.8` |
| `FRAME.office` | `office_architecture_generator.py` | `GRID=9`, `FLOOR_HEIGHT=4.2` |
| `+CORE` | core block of the FRAME generator | `CORE_RATIO`, footprint from the core entry |
| `+LONGSPAN` | truss/transfer routine (TPAC mega-truss) | `span`, transfer depth |
| `+MEGA` | mega-column routine (`tpac_architecture_generator.py`) | column positions, transfer level |
| `+OUTRIGGER` | belt-truss routine at MEP floor | core + perimeter tie |

---

## 7. Worked examples (sanity checks)

**TPAC (14 floors, cube + protrusions, low/mid-rise):**
- Module: mostly `FRAME.office`; cores → `+CORE`; ground public on pilotis →
  `+MEGA`; Grand/Blue/Globe theaters (span > 15) → `+LONGSPAN`; BOH cellular →
  `FRAME.cellular`. Lateral = `CORE + MEGA frame`. Transfer floor where theaters
  sit over the lifted ground.

**53W53 (75 floors, tapered tower):**
- Envelope → `SKIN`; interior residential → `FRAME.cellular` + `+CORE`; podium
  L0–3 → `FRAME.office`/`+MEGA`. Lateral = `SKIN + CORE`. Transfer at
  `podiumTop+1`. Module change `FRAME→SKIN` verified at the perimeter ring.

**TAMA (library, low-rise spanning ground-scape):**
- Public reading halls span 3–12 at grade/roof → `FOAM`; cores → `+CORE`;
  stacks/BOH → `FRAME.cellular`. Lateral = `FOAM + CORE`.

---

## 8. Implementation order (suggested)

1. `classify_module(entry, building)` → `SKIN`/`FOAM`/`FRAME[.preset]` (§3 step A).
2. `apply_modifiers(entry, building)` → `+CORE/+MEGA/+LONGSPAN/+OUTRIGGER` (§3.1).
3. `select_lateral(building)` → §4 result.
4. `find_transfer_floors(entries)` → §5.
5. Emit format §6(a) (or §6(b) sidecar) from the program generator.
6. Route each tag to its generator per §6.1; each generator builds only its
   system in the tagged zones.
7. Visualizers: add a "color by structure" toggle keyed on the tag.
