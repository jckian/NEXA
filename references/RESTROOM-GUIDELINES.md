## RESTROOM GUIDELINES (THEATER / LARGE PUBLIC BUILDING)

### A. FIXTURE-LEVEL DIMENSIONS (UNIT MODULES)

#### Female Toilet Stall
- Width: 0.9 – 1.0 m
- Depth: 1.5 – 1.7 m
- Recommended (TPAC-scale): 1.0 × 1.6 m

#### Male Urinal Unit
- Width per unit: 0.6 – 0.7 m
- Spacing (center to center): 0.75 – 0.9 m
- Depth: 1.2 – 1.5 m

#### Accessible Toilet (ADA / Universal)
- Minimum: 1.8 × 2.2 m
- Recommended: 2.0 × 2.4 m
- Turning radius: 1.5 m (required)

---

### B. FIXTURE COUNT (THEATER STANDARD)

#### Calculation Logic

- Female: 1 fixture / 50–70 seats
- Male:
  - 1 toilet / 100–150 seats
  - 1 urinal / 50–80 seats

#### Example (1500-seat theater)

- Female: 20–30 stalls
- Male:
  - 8–12 toilets
  - 10–15 urinals

---

### C. RESTROOM CLUSTER SIZE (PER FLOOR)

#### Typical FOH Restroom Area

- Female restroom:
  - ~8 m × 12 m ≈ 90–100 m²

- Male restroom:
  - ~6 m × 10 m ≈ 60 m²

- Accessible toilets:
  - 2–3 units ≈ 10–15 m²

#### Total per cluster:
- 150 – 200 m² per floor (FOH level)

---

### D. PROGRAM FORMAT (FOR DATASET)

Use this format for integration with FLOOR_DATA:

restroom_female / 90 / L2 / public / 8,12  
restroom_male / 60 / L2 / public / 6,10  
accessible_restroom / 12 / L2 / public / 3,4  

---

### E. SPATIAL DISTRIBUTION RULES (CRITICAL)

#### 1. Adjacency
- restroom MUST be adjacent to lobby
- restroom MUST connect to public circulation

#### 2. Distance Constraints
- restroom NEAR lobby (≤ 15m)
- restroom FAR_FROM stage and performance hall

#### 3. Vertical Strategy (STACKING)
- All restrooms SHOULD stack vertically across floors
- Align with plumbing core

#### 4. Core Relationship
- restroom ATTACHED_TO service core
- restroom NEAR vertical circulation

#### 5. Distribution Strategy
- Each major theater SHOULD have ≥ 2 restroom clusters
- Distribute symmetrically to avoid congestion

---

### F. GENERATIVE RULES (FOR SOLVER / AGENT)

Pseudo-logic:

```
for each restroom:
    attach_to(nearest_core)
    place_near(lobby, max_distance=15m)
    avoid(stage, min_distance=20m)
    align_vertical_stack()

for each floor:
    ensure restroom_area >= 150m2 (if FOH level)
```

---

### G. DESIGN INTENT (IMPORTANT)

- Restrooms are sized based on peak intermission load, not average occupancy
- Placement is driven by circulation efficiency, not residual space
- Vertical stacking is required for mechanical and plumbing efficiency

### H. FLOOR COVERAGE REQUIREMENT (HARD CONSTRAINT)

#### Rule
- EVERY floor MUST include:
  - 1 × restroom_female
  - 1 × restroom_male
  - 1 × accessible_restroom

---

#### Validation Logic (Pre-Generation)

for each floor in building:
    if not exists(restroom_female):
        flag_error("Missing female restroom on floor " + level)

    if not exists(restroom_male):
        flag_error("Missing male restroom on floor " + level)

    if not exists(accessible_restroom):
        flag_error("Missing accessible restroom on floor " + level)

---

#### Auto-Completion Logic (Recommended)

for each floor:
    if missing restroom_female:
        add program:
            restroom_female / 90 / level / public / 8,12

    if missing restroom_male:
        add program:
            restroom_male / 60 / level / public / 6,10

    if missing accessible_restroom:
        add program:
            accessible_restroom / 12 / level / public / 3,4

---

#### Placement Constraints (Per Floor)

- All three restroom types SHOULD:
    - be co-located as a cluster
    - share plumbing wall
    - attach to same service core

Pseudo:

cluster = group(restroom_female, restroom_male, accessible_restroom)

place(cluster):
    attach_to(nearest_service_core)
    align_to(plumbing_axis)
    near(lobby, max_distance=15m)

---

#### Vertical Consistency

- Restroom clusters SHOULD align vertically across all floors
- If one floor shifts, ALL floors must update

Pseudo:

for each floor:
    cluster.position = reference_floor.cluster.position

---

#### Minimum Area Guarantee

for each floor:
    restroom_total_area >= 150 m² (FOH floors)

---

### I. PRIORITY LEVEL

- This rule is HARD CONSTRAINT (cannot be violated)
- Overrides:
    - aesthetic layout
    - equal distribution
    - program packing optimization
    

    ### J. GEOMETRY CONSTRAINTS (CRITICAL)

#### 1. Aspect Ratio Constraint

All restroom volumes MUST satisfy:

- aspect_ratio = max(width, length) / min(width, length)

Constraints:
- MIN: 1.0 (square)
- MAX: 2.5 (recommended)
- HARD MAX: 3.0 (cannot exceed)

---

#### 2. Maximum Dimensions (Hard Limits)

To prevent unrealistic stretched geometry:

- restroom_female:
    max_width = 12 m
    max_length = 15 m

- restroom_male:
    max_width = 10 m
    max_length = 12 m

- accessible_restroom:
    max_width = 4 m
    max_length = 5 m

---

#### 3. Minimum Dimensions (Based on Fixture Logic)

- restroom_female:
    min_width = 6 m
    min_length = 8 m

- restroom_male:
    min_width = 5 m
    min_length = 6 m

- accessible_restroom:
    min_width = 2 m
    min_length = 2.2 m

---

#### 4. Shape Correction Logic (IMPORTANT)

If generated geometry violates constraints:

Pseudo:

function enforceRestroomGeometry(w, l, type):

    ratio = max(w,l) / min(w,l)

    # Step 1: Clamp extreme ratio
    if ratio > 3.0:
        l = sqrt(area * 3.0)
        w = area / l

    # Step 2: Clamp max dimensions
    w = min(w, max_width[type])
    l = min(l, max_length[type])

    # Step 3: Clamp min dimensions
    w = max(w, min_width[type])
    l = max(l, min_length[type])

    # Step 4: Rebalance to preserve area
    area = w * l

    return w, l

---

#### 5. Preferred Proportions (Design Bias)

- restroom_female:
    prefer ratio ≈ 1:1.2 ~ 1:1.5

- restroom_male:
    prefer ratio ≈ 1:1.5 ~ 1:2

- accessible_restroom:
    prefer near-square (1:1 ~ 1:1.3)

---

#### 6. Layout Logic (Spatial Reality Constraint)

- restroom_female:
    rectangular with double-loaded stalls

- restroom_male:
    linear + urinal wall

- accessible_restroom:
    single enclosed box (no elongation)

---

### K. GENERATION OVERRIDE

- Geometry constraints OVERRIDE:
    - area-perfect fitting
    - bin-packing efficiency

If conflict occurs:
    → preserve geometry realism over area accuracy