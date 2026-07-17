# Program Module Area Table

Common architectural programs sized to the project **structural module**, calibrated
to the TPAC and 53W53 distributions (representative `{w,h}` in metres → modules ÷ 2.5908).

| Quantity | Value |
|---|---|
| Module | **8'-6" = 2.5908 m** |
| 1 module (1×1) | **6.71 m²** |
| 1×2 tile | 13.42 m² |

- **w×d** = footprint bounding box, in modules
- **shape** — `rect`, or `L` (an `nw×nd` corner notched out, e.g. to wrap a core/entry)
- **vertical** — full floor-height volume / shaft that runs *through* floors (cores). Clicking a placed core sets how many floors it spans.
- **timespan** — pace-layering class driving tile **colour**:
  - **long** = slow-changing / permanent → **warm family** (cores, housing, performance, museum, structure, mechanical). Cores render darkest.
  - **short** = fast-changing / fit-out → **cool family** (retail, F&B, events, offices, amenity).
  - Each program keeps a distinct shade *within* its family.
- Area is the **net** program area (L notch removed). Lookup is by **substring** (first match wins) so LLM naming variants resolve — mirrors the `in` matching in `EllipseAgent.py`.
- **Tileability rounding:** at runtime every footprint is normalised so it can be perfectly filled by 1×2 dominoes — rectangles get at least one even side (the *length* is rounded up), and L-shapes round W, D and the notch to even. So a few listed sizes round up by one module on use (e.g. 5×5 → 5×6; lobby notch 3×3 → 4×4; circulation notch 5×5 → 6×6).

This is the source of truth for `PROGRAM_SPECS` in `program-tile-editor.html`; keep them in sync.

---

## LONG timespan — warm family

### Cores / shafts (vertical ⊥, click to set floors)

| Program | w×d | Shape | Net area |
|---|---|---|---|
| fire stair and freight elevator | 4×8 | rect | 215 m² |
| freight elevator | 4×8 | rect | 215 m² |
| fire stair and elevator (1/2/3) | 4×6 | rect | 161 m² |
| core (generic) | 4×6 | rect | 161 m² |
| elevator | 4×5 | rect | 134 m² |
| escalator | 3×6 | rect | 121 m² |
| fire stair | 3×5 | rect | 101 m² |
| stair | 2×4 | rect | 54 m² |
| shaft | 2×2 | rect | 27 m² |

### Performance / theater

| Program | w×d | Shape | Net area |
|---|---|---|---|
| fly tower | 10×14 | rect | 940 m² |
| event hall | 8×15 | rect | 805 m² |
| stage | 10×12 | rect | 805 m² |
| theater | 10×12 | rect | 805 m² |
| backstage | 8×15 | rect | 805 m² |
| auditorium | 8×12 | rect | 644 m² |
| dressing room | 6×15 | rect | 604 m² |
| rehearsal room | 8×10 | rect | 537 m² |
| green room | 6×8 | rect | 322 m² |
| orchestra pit | 4×10 | rect | 268 m² |

### Museum / gallery · housing · long civic

| Program | w×d | Shape | Net area |
|---|---|---|---|
| museum gallery / museum | 8×10 | rect | 537 m² |
| gallery | 6×10 | rect | 403 m² |
| exhibition hall | 5×10 | rect | 336 m² |
| plaza | 27×19 | rect | 3443 m² |
| viewing platform | 4×23 | rect | 617 m² |
| residence duplex | 5×8 | rect | 268 m² |
| residence full floor / residence / apartment | 5×6 | rect | 201 m² |
| residence corner / penthouse | 5×5 | rect | 168 m² |
| pool | 5×5 | rect | 168 m² |
| mechanical | 6×8 | rect | 322 m² |

### Horizontal circulation (L, wraps the core)

| Program | w×d | Shape | Net area |
|---|---|---|---|
| circulation / corridor / service corridor | 8×8 | **L** (notch 5×5) | 262 m² |

---

## SHORT timespan — cool family

| Program | w×d | Shape | Net area |
|---|---|---|---|
| set storage | 12×15 | rect | 1208 m² |
| loading | 8×15 | rect | 805 m² |
| production workshop | 8×15 | rect | 805 m² |
| lobby | 6×8 | **L** (notch 3×3) | 262 m² |
| restaurant | 8×10 | rect | 537 m² |
| roof terrace | 10×15 | rect | 1007 m² |
| sales and display / display / retail | 6×8 | rect | 322 m² |
| staff | 5×8 | rect | 268 m² |
| gym | 6×6 | rect | 242 m² |
| event lounge | 4×8 | rect | 215 m² |
| screening room | 5×6 | rect | 201 m² |
| lounge bar / museum shop / office / IT support / storage | 4×6 | rect | 161 m² |
| restroom | 5×5 | rect | 168 m² |
| box office / kitchen / private dining / residents lounge / lounge / library / spa / toilets | 4×5 | rect | 134–134 m² |
| reception | 4×4 | rect | 107 m² |
| wine cellar / art storage | 3×4 | rect | 81 m² |
| fitting rooms / changing room | 2×4 | rect | 54 m² |

---

**Fallback** — any unmatched program defaults to **2×3 rect (40 m²)**, vertical if its name matches a core keyword (`fire stair`, `elevator`, `stair`, `core`, `shaft`, `duct`, `flue`, `riser`, `chimney`), and **short** timespan unless it matches a long keyword.

In the editor these are recommended starting sizes — `R` rotates, `V` toggles flat ↔ full-height volume, `L` toggles rect ↔ L-shape, drag to move (rides on top of any tile under it for vertical stacking). **Group Mode** stamps a core/anchor together with its adjacency bundle; the **Arrange** button cycles Cluster / Row / Column.
