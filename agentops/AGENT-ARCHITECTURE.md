# Agent Architecture Blueprint — program→massing platform

Written 2026-07-04 (Fable 5) from a grounded analysis of `program-massing-shortfloor.html` and its spec ecosystem. This is the blueprint for creating project agents via `/agents`. Every claim about code carries a line reference verified on 2026-07-04; re-verify line numbers before relying on them (the file changes weekly).

How to use: create agents in the Phase-6 order, one at a time, copying the Phase-4 spec into the agent definition. Do not create all at once — each agent should earn its place by being used.

---

## Phase 1 — Repository analysis (the shortfloor workflow)

### What the app is

`program-massing-shortfloor.html` (~204 KB) is a **fully self-contained, client-only** Three.js app: CDN importmap (Three + OrbitControls + RoomEnvironment, lines 119–129), zero local imports, zero network calls, zero LLM integration (verified: no fetch/XHR/api-key anywhere). Input: a program `.txt` in the `ProgramFormat.txt` grammar via load/paste/drag-drop. Output: rendered massing + OBJ exports. Coordinates in the input are **ignored** — layout is generated (comment at 138).

### Pipeline (data flow)

```
output.txt ──parse(170)──▶ records {type, area, level, category, w, h, isCore}
                │
                ├─ computeShortFloors(418): level is SHORT when shortArea/totalArea > 0.5
                │    ("short" = plug-in types matched by isShort regex, line 144)
                │
                └─ computeLayout(274) ──▶ { levels, coreShafts, floorRects, floorCorr, FW, FD }
                     • packSide(312, nested): corner-flush ("edge") or pocket ("inset", CORE_INSET_MOD=4)
                     • corridor at z=zMid; suppressed when floor >30% SHORT with no deep-served LONG room (343–349)
                            │
              ┌─────────────┴──────────────┐
   buildStructure(477)            buildShortBlocks(789)
   LONG cells only (493–505)      SHORT stacks (runs of consecutive SHORT floors, 800–806)
   grounded MAIN vs hung          1×2-module bricks 3D-packed across the stack (porousMasked, 810),
   transfer/cantilever columns    gravity check rests(819), stair per multi-floor cluster (901–916),
   (526–546), 2-tier girders +    FRAME vs INFILL split by exterior distance (928–934)
   joists, slabs, curtain wall,   ──▶ SHORT_PLACE {frameHx,frameHz,infillX,infillZ,frameV,stair} (970)
   timber fins (548–677+)                  │
              │                            │
              └──────── build(992) orchestrates all of it, full dispose+rebuild ────────┘
                            │
        frameCamera(1068) · renderStats(1080) · renderLegend(1096)
        exportOBJ(1196) reads exportBoxes · exportKitOBJ(1165) maps SHORT_PLACE onto
        real Rhino meshes stored inline as BLOCKS (785, giant JSON — file:// can't fetch sidecars)
```

### UI / rendering behavior

Controls (markup 60–116, wiring 1122–1220): load/paste/drop → `loadText` (1122); floor-height input → `FLOOR_H`; segmented toggles via `seg()` (1133) for `COLOR_MODE`, `RENDER_MODE` (solid vs structure), `CORE_OPTION` (edge vs inset), `GROUND_MODE`; sliders for `SHORT_OPACITY`, `PROTRUDE`. **Every control except the opacity slider triggers a full `build()`** (dispose + rebuild); opacity mutates materials in place (1144–1147). Export buttons do not rebuild.

### Coupling & bottlenecks

1. **One closure, 11 shared mutable globals** (`PROGRAM`, `FLOOR_H`, `COLOR_MODE`, `SHORT_OPACITY`, `PROTRUDE`, `GROUND_MODE`, `RENDER_MODE`, `CORE_OPTION`, `shortFloors`, `exportBoxes`, `SHORT_PLACE`) read/written across all stages. No module boundaries.
2. **Responsibilities interleaved per function**: `buildShortBlocks` mixes program classification, structural gravity logic, and Three.js mesh emission in one 200-line function; `buildStructure` mixes architectural rules (grounded vs transfer classification) with geometry emission.
3. **Architectural rules live as magic numbers**: `MODULE=8.5ft` (159), `SHORT_THRESHOLD=0.5` (416), `COLSTEP=3` "~8 m bay" (487), column/girder grading `COL_MAIN/COL_CANT=0.70/0.38`, `PRI/CANT/SEC` girder sections (483–486), corridor-suppression `0.30` (349), protrusion fractions ½ and ⅔ (251, 957), `CORE_INSET_MOD=4` (411).
4. **Cross-app copy-paste**: `MODULE=8.5ft` exists independently in 4 HTML apps (shortfloor:159, tile-editor:276, composer:118, program-massing:143); the `#172FC7/#E67033/#EEC341` palette and `hash3` are duplicated verbatim in composer + program-massing; `parse()` is forked (shortfloor:170, program-massing:154); tile-editor's `PROGRAM_SPECS` (354) mirrors `PROGRAM-MODULE-AREA-TABLE.md` by comment only, not verified byte-identical. **Any rule change must currently be applied N times by hand.**
5. **Token bottleneck for AI work**: the file is ~55k tokens; whole-file reads are forbidden (see A-DIAGNOSIS). All agents must work grep-window style.

### Repeated engineering patterns

- Integer module-space computation first, mesh emission second (the one clean seam in the code).
- Deterministic hash-based pseudo-randomness (`hash3`) for reproducible packing across platforms.
- Spec-in-markdown, implementation-in-HTML: `MASSING-MODULE-LOGIC.md` ↔ composer; `PROGRAM-MODULE-AREA-TABLE.md` ↔ tile-editor `PROGRAM_SPECS`; `HYBRID-STRUCTURE-RULES.md` ↔ (partially) `buildStructure`.
- Everything rebuilds from scratch on any change (except opacity) — acceptable now, a perf ceiling later.

---

## Phase 2 — Functional decomposition (by responsibility, not by file)

| # | Domain | Purpose | Inputs | Outputs | Current implementation | Own agent? |
|---|--------|---------|--------|---------|------------------------|------------|
| 1 | Program planning | Author/edit program schedules; LONG/SHORT balance; floor allocation; adjacency | Briefs, area targets, spec tables | `.txt` in ProgramFormat grammar | `parse` 170, `isShort` 144, `computeShortFloors` 418; specs: ProgramFormat.txt, PROGRAM-LONGSHORT-TABLE.md, PROGRAM-MODULE-AREA-TABLE.md | **Yes — program-planner** |
| 2 | Program validation | Machine-check schedules: grammar, area sums, core counts, module-snap | A `.txt` + targets | pass/fail + numbers | Nowhere — done by eye today | **Yes — program-auditor** (cheap, mechanical) |
| 3 | Module layout & packing | Integer-space layout: floorplates, cores, corridors, 1×2 packing, porosity | Parsed records | `computeLayout` result shape; brick place-lists | `computeLayout` 274, `rectDims` 194, `porousVol` 208, `packSide` 312; spec: MASSING-MODULE-LOGIC.md; sibling: massing-composer.html | **Yes — module-packer** (the core IP of the research) |
| 4 | Structural system | Column grids, MAIN vs transfer/cantilever, girder grading, slabs, envelope frame | Layout occupancy grid | `addStruct` mesh calls | `buildStructure` 477–788 (port of internal_structure_SeagramBuilding.py); spec: HYBRID-STRUCTURE-RULES.md (SKIN/FOAM/FRAME; FOAM paused → FRAME) | **Yes — structure-frame** |
| 5 | Kit-of-parts / assembly | SHORT-stack brick system: FRAME/INFILL split, stairs, DfD kit export | floorRects + shortFloors | `SHORT_PLACE`, kit OBJs | `buildShortBlocks` 789–990, `BLOCKS` 785, `exportKitOBJ` 1165; related: MODULE-TOOLS/dfd-unit-diagram.html, references/dfd_connector.json | **Yes — kit-of-parts** (closest real thing to "construction system") |
| 6 | Visualization | Scene, camera, lighting, materials, instancing, palette discipline | Mesh emissions | Rendered viewport | scattered through build/addBox/addStruct/addInst; `frameCamera` 1068; palette 152/476 | **Yes — refresh existing `3d-arch-diagram-gen`** (keeps its accumulated memory) |
| 7 | UI / interaction | Panels, controls, wiring, rebuild triggers, drag-drop | User events | Global mutations + `build()` | markup 60–116, wiring 1122–1220 | **Yes — ui-panels** (small, low churn) |
| 8 | Data & interop | OBJ export, output.txt ecosystem, Rhino/Blender bridges | Scene data / place-lists | `.obj`, `.txt`, Blender scripts | `exportOBJ` 1196, `download` 1152; massing-model-generator/*.py; pythonFiles fileTransfer | **Yes — geo-interop**. IFC/BIM: nothing exists — Future tier, don't build now |
| 9 | Cross-app spec consistency | Single-source-of-truth policing: MODULE, palette, parse forks, PROGRAM_SPECS↔tables | Spec docs + 4 HTML apps | Drift report; approved batch fixes | Nowhere — drift is already real (Phase 1 §4) | **Yes — spec-guardian** |
| 10 | Visual acceptance | Independent screenshot-based verification of any visual change | Page + expected-result description | pass/fail + PNG | Headless-Edge pipeline exists as shell commands (G-LETTER item 3), run ad hoc | **Yes — visual-verifier** (institutionalizes C Rule 6) |
| 11 | Building performance (LCA/carbon/energy/daylight) | — | — | — | **No implementation exists anywhere in the workflow** | Future — creating it now would be an agent with no code to own |
| 12 | Orchestration | Task routing, delegation, escalation | User intent | Dispatched subagents | agentops/C-MODEL-DISPATCH.md, executed by the main session | **No agent.** See Phase 3 design decision #1 |

---

## Phase 3 — Ecosystem design

**Roster: 10 specialized agents** (9 new + 1 refresh), 2 future placeholders, orchestration as a role not an agent.

### Design decisions (read before creating anything)

1. **The orchestrator is the main session, not a subagent.** Claude Code's main conversation already is the dispatcher, governed by `agentops/C-MODEL-DISPATCH.md` + `E-DELEGATION-TEMPLATES.md`. A spawned "orchestrator agent" would add a context-blind middleman, double token cost, and let the main session dump responsibility. Nothing here may spawn sub-orchestrators.
2. **Ownership is by code section + spec file, not by file.** The app is single-file; agents own named functions/line-ranges plus the spec doc for their domain. The Phase-4 "owned" lists are the authority. Two agents editing the same function = a routing error by the commander.
3. **Big-File Surgery Protocol (shared SOP, all agents):** never whole-file Read; Grep → ±60-line window → Edit; after editing, verify via local server + headless-Edge screenshot (recipe in G-LETTER item 3); report diffs as file:line. This protocol is written into every agent definition — it is why there is no separate "html-surgeon" agent.
4. **Spec-first rule:** when a domain has a spec doc (MASSING-MODULE-LOGIC, HYBRID-STRUCTURE-RULES, PROGRAM-MODULE-AREA-TABLE, ProgramFormat), the spec is the source of truth. Code change that contradicts the spec → update the spec in the same task or stop and ask. This keeps the specs alive instead of rotting.
5. **No generic agents.** Every agent below owns a domain with existing code and a real recurring workload. Performance/BIM agents are deferred until there is code for them to own (F-MAINTENANCE: no rules — or agents — without triggers).
6. **Refactoring stance:** multi-agent ownership will create pressure to extract the single file into modules. Per G-LETTER, extraction happens only when a requested change already requires touching that seam (the integer-layout ↔ mesh-emission seam is the natural first cut), and only with user approval. No agent may propose repo-wide restructuring as a task outcome.

---

## Phase 4 — Agent specifications

Common to ALL agents (do not repeat per spec): follow Big-File Surgery Protocol; obey agentops/C rules 2–6 (dispatch trio, report contract ≤30 lines + file:line, escalation ladder, never self-verify); never touch `BACKUP/`, `node_modules/`, `my-video/`, `VORO/` (incl. index.html, index2.html); stop and ask on any D §3 trigger. "Effort" = the `reasoning effort` frontmatter field of the agent definition; if the harness version doesn't support it, model choice alone carries the setting.

### 4.1 `program-planner`
- **Mission:** author and revise building program schedules in the ProgramFormat grammar, balancing LONG/SHORT timespan mix, floor allocation, and area targets.
- **Responsibilities:** generate/edit `.txt` program files; per-floor allocation; LONG/SHORT ratio design (reference: LONG≈70/SHORT≈30 in PROGRAM-LONGSHORT-TABLE.md); adjacency reasoning; keep `isShort` regex (shortfloor:144) consistent with new type names; maintain PROGRAM-LONGSHORT-TABLE.md.
- **Owned:** references/PROGRAM-LONGSHORT-TABLE.md, program `.txt` instance files it creates; read-write on `parse`(170)/`computeShortFloors`(418)/`isShort`(144)/`SAMPLE`(1222) only when grammar or classification changes.
- **Never modify:** ProgramFormat.txt grammar itself (ask user), historical distributions (TPAC/53W53) — those are case-study records; layout/structure/render functions.
- **Inputs:** brief + area targets + site footprint. **Outputs:** program `.txt` + a 5-line design rationale.
- **Acceptance:** output passes `program-auditor` (below) with zero errors; LONG/SHORT ratio within ±5% of target; every type resolvable by PROGRAM-MODULE-AREA-TABLE.md or explicitly flagged as new.
- **Validation checklist:** grammar per ProgramFormat.txt; area sum vs target ≤2%; ≥3 fire-stair types per floor; every SHORT type matches the `isShort` regex; module-snapped `{w,h}` where the table specifies one.
- **Escalation / stop:** taste calls on program mix beyond stated ratios → ask user; new program type with no table entry → propose sizing, flag, continue; two failed attempts to satisfy conflicting area constraints → stop with options.
- **Model/effort:** sonnet / medium. **Typical prompts:** "Generate an 8F mixed-use program, 12,000 m², LONG 65%", "Move all office floors above retail and rebalance". **Typical mistakes:** inventing type names that break the `isShort`/`PROGRAM_SPECS` substring matching; forgetting basement levels are negative; eyeballing area sums (that's the auditor's job — always run it).
- **Future:** occupancy/code-compliance rules; site-specific FAR reasoning.

### 4.2 `program-auditor`
- **Mission:** mechanically verify any program `.txt` against grammar and numeric rules. Read-only on the repo; writes only throwaway scripts to scratchpad.
- **Owned:** nothing in the repo. **Never modify:** anything.
- **Inputs:** path + targets. **Outputs:** pass/fail table with computed numbers (per-floor sums, totals, core counts, ratio, format violations with line numbers).
- **Acceptance:** every check produces a number or a line number, never an adjective.
- **Checklist (the whole agent, encode verbatim):** ① every line matches `{type}/{area}/{level}/{category}/{w,h}` with literal braces; ② categories ∈ {public, private, circulation}; ③ per-floor and total area within 2% of stated targets; ④ ≥3 fire-stair types per floor; ⑤ LONG/SHORT ratio vs target; ⑥ `{w,h}` present ⇒ w×h within 10% of area; ⑦ duplicates/overlapping cores flagged.
- **Escalation / stop:** never escalates on content — it reports; ambiguous target ("looks right?") → return the numbers and let the commander judge.
- **Model/effort:** haiku / low (this is the demote-to-cheap pattern from C Rule 5). **Typical prompts:** "Audit references/MIXEDUSE-PROGRAM-DISTRIBUTION.txt against 14,000 m² total." **Typical mistakes:** trusting its own arithmetic instead of writing a script — it must compute via a script, not in-head.
- **Future:** module-tileability check (rect: ≥1 even side; L: all even) once tile rules are finalized.

### 4.3 `module-packer`
- **Mission:** own the integer module-space layout logic — the research core. Floorplates, core placement, corridors, program packing, 1×2 brick packing, porosity/protrusion.
- **Responsibilities:** `computeLayout`(274) incl. `packSide`(312), `rectDims`(194), `porousVol`(208), `protrudeOffset`(244), `splitSides`(257); constants `CORE_INSET_MOD`(411), `SHORT_THRESHOLD`(416), corridor-suppression 0.30 (349); keep `MASSING-MODULE-LOGIC.md` in sync (spec-first rule); parallel logic in massing-composer.html.
- **Never modify:** mesh emission (`addBox`/`addStruct`/`addInst`), `buildStructure`, UI wiring, BLOCKS data.
- **Inputs:** parsed program records + layout requirements. **Outputs:** layout algorithm changes, with the layout-shape contract (`{levels, coreShafts, floorRects, floorCorr, FW, FD}`) kept stable or the change to it explicitly reported — downstream agents depend on that shape.
- **Acceptance:** screenshot proves the spatial claim; determinism preserved (same input+seed ⇒ same layout — hash3-based, no `Math.random`); no brick overlaps/out-of-bounds ("放不下不要硬放" rule); spec updated in the same task.
- **Validation checklist:** corridor continuity on LONG floors; core shafts continuous minL→maxL; every program rect inside FW×FD; packing counts printed (placed/total).
- **Escalation / stop:** changes coupling ≥3 constraints (core+aspect+adjacency+taper class of problem) → this is D §1 territory; agent def stays sonnet, commander escalates the task to opus. Layout-shape contract change → stop, report impact on structure-frame/kit-of-parts first.
- **Model/effort:** sonnet / high. **Typical prompts:** "Add a courtyard void option to computeLayout", "Make corridor width parametric (1 or 2 modules)". **Typical mistakes:** breaking determinism with real randomness; changing the layout shape silently; fixing packing by nudging constants instead of the mechanism (D §4).
- **Future:** multi-tower layouts; site-boundary polygon input (border.txt) instead of rectangle.

### 4.4 `structure-frame`
- **Mission:** own the structural system — column grids, MAIN vs transfer/cantilever classification, girder grading, slabs, curtain wall, fins — per HYBRID-STRUCTURE-RULES.md.
- **Responsibilities:** `buildStructure`(477–788), `addStruct`(455), STRUCT palette(476), member-sizing constants(483–487); HYBRID-STRUCTURE-RULES.md (spec owner); cross-reference port source `structure-generator/internal_structure*.py` (read-only).
- **Never modify:** `computeLayout` (it consumes the grid, never reshapes it), SHORT-block logic, program parsing. FOAM module is paused — implement FRAME fallbacks, do not build FOAM without user go-ahead.
- **Inputs:** layout occupancy grid + rules. **Outputs:** structural geometry changes + rule updates in the spec.
- **Acceptance:** screenshot in structure mode; every hung/cantilever column tied back to a grounded run (spec §5.5: cantilever roots within 1.5× span — verify by grep/count, not eyeball); no floating members (every member's support chain reaches ground or a transfer).
- **Validation checklist:** column spacing = COLSTEP unless task says otherwise; member palette matches STRUCT colors; SHORT cells still excluded (493–505); slabs/roofs close every terminated cell.
- **Escalation / stop:** real engineering judgment (actual load values, code compliance) → out of scope, say so plainly — this agent does *rule-based geometry*, not structural engineering; conflicts between spec and requested change → spec-first rule.
- **Model/effort:** sonnet / high. **Typical prompts:** "Thicken transfer girders and color them by span", "Add outrigger level at L10 per HYBRID rules §3.1". **Typical mistakes:** treating visual plausibility as structural validity; editing member constants without updating the spec table.
- **Future:** SKIN (diagrid) module implementation; per-member CSV takeoff export.

### 4.5 `kit-of-parts`
- **Mission:** own the SHORT-stack demountable kit: brick packing hand-off, FRAME/INFILL split, stair insertion, DfD connector logic, kit OBJ export.
- **Responsibilities:** `buildShortBlocks`(789–990), `SHORT_PLACE` contract(970), `FRAME_PARTS`/`INFILL_PARTS`(1163–4), `exportKitOBJ`(1165), `BLOCKS` inline mesh data(785); references/dfd_connector.json; MODULE-TOOLS/dfd-unit-diagram.html.
- **Never modify:** `porousVol`/packing math (module-packer's), `buildStructure`, UI.
- **Inputs:** floorRects + shortFloors + packed brick lists. **Outputs:** kit geometry/exports + assembly logic changes.
- **Acceptance:** exported kit OBJ opens with correct part counts (report counts per part type); gravity rule holds (`rests`, 819) — no unsupported brick; one stair per multi-floor cluster verified by count(901–916); screenshot for visual changes.
- **Escalation / stop:** BLOCKS mesh data regeneration needs Rhino source — if asked to change brick geometry itself, stop: that's a user/Rhino task, the agent only re-imports.
- **Model/effort:** sonnet / medium. **Typical prompts:** "Export INFILL bricks split per floor", "Make the FRAME/INFILL ratio a slider". **Typical mistakes:** editing the giant BLOCKS line by hand (never — regenerate or leave); breaking the SHORT_PLACE shape that exportKitOBJ reads.
- **Future:** assembly-sequence animation; connector-level detail from dfd_connector.json.

### 4.6 `3d-arch-diagram-gen` (refresh, keep name + memory)
- **Mission:** visualization quality — scene, camera, lighting, materials, instancing, palette discipline — across all four HTML apps.
- **Refresh needed:** its project-constraints section predates the module system. Add: MODULE=8.5ft world, 4-color palette (#F5F5F5/#172FC7/#E67033/#EEC341), instanced-mesh kit rendering, `frameCamera` conventions. Mark old TPAC ratio constraints as legacy.
- **Owned:** scene/camera/light/material code in the apps (shortfloor: importmap 119–129, frameCamera 1068, material creation inside add* functions — coordinate with section owners), palette definitions.
- **Never modify:** layout/structure/program logic — if a visual fix requires touching logic, report back instead.
- **Acceptance:** before/after screenshots; zero new console errors; frame rate not visibly degraded on rebuild (SHORT stacks are instanced — keep them so).
- **Model/effort:** sonnet / medium (existing definition already sonnet + memory: project).
- **Typical mistakes:** disposing geometry without materials (leaks); changing palette hexes locally instead of everywhere (that's spec-guardian's alarm).

### 4.7 `ui-panels`
- **Mission:** panels, controls, wiring, drag-drop, stats/legend readouts.
- **Owned:** shortfloor markup 1–118, wiring 1122–1220, `seg()` helper(1133), `renderStats`(1080)/`renderLegend`(1096); equivalent UI layers of the sibling apps.
- **Never modify:** what the controls *compute* — only how they're presented and wired. New control = wire global + `build()` trigger; heavy sliders may use the in-place-mutation pattern (cf. `ctl-short-op`, 1144) only when no re-layout is needed.
- **Acceptance:** screenshot showing the control; every new control actually round-trips (change → visible scene effect); no orphan listeners after rebuild.
- **Model/effort:** sonnet / low. **Typical mistakes:** adding a control that mutates a global but forgets `build()`; breaking the one-exception opacity pattern by rebuilding on slider drag (jank).

### 4.8 `geo-interop`
- **Mission:** everything that crosses the browser boundary: OBJ exports, output.txt ecosystem, Rhino/Blender bridge scripts.
- **Owned:** `exportOBJ`(1196)/`download`(1152), export buttons; `massing-model-generator/*.py` (incl. tpac_blender.py, Blender53W53.py, Patch22_retail_housing_massing.py); pythonFiles fileTransfer conventions (ARCH-NOTES).
- **Never modify:** in-browser layout/structure logic; SHORT_PLACE/exportBoxes producers (it consumes them).
- **Acceptance:** exported file re-imported or parsed by a script proving counts/coordinates (e.g., OBJ vertex count sanity, Blender import runs headless if available); for Python: py_compile + real run per D §5.
- **Model/effort:** sonnet / medium. **Typical mistakes:** assuming Y-up/Z-up conventions instead of checking (Three Y-up → Blender Z-up mapping documented in ARCH-NOTES); writing exports that only work served, not from file://.
- **Future:** glTF export; JSON scene-state save/load (the missing "save my design" feature); IFC lives here *if* it ever becomes real.

### 4.9 `spec-guardian`
- **Mission:** police the single-source-of-truth: constants, palettes, parse forks, PROGRAM_SPECS↔table sync across the 4 apps + spec docs.
- **Owned:** nothing exclusively; it audits and, with explicit per-run approval, batch-applies synchronized fixes.
- **Standing checks:** MODULE value identical at shortfloor:159 / tile-editor:276 / composer:118 / program-massing:143; palette hexes match MASSING-MODULE-LOGIC.md 250–255 wherever used; tile-editor `PROGRAM_SPECS`(354) vs PROGRAM-MODULE-AREA-TABLE.md diffed field-by-field; `parse()` forks (shortfloor:170 vs program-massing:154) behaviorally aligned on the grammar corpus.
- **Acceptance:** drift report with file:line pairs and the differing values; fixes only after commander/user approval, each verified by the relevant app's screenshot.
- **Model/effort:** haiku / low for the audit runs; sonnet when applying fixes. **Run cadence:** after any task that touched a shared constant, and on request.
- **Typical mistakes:** "fixing" an intentional divergence (tile-editor's different UI theme is deliberate) — report, don't assume.

### 4.10 `visual-verifier`
- **Mission:** fresh-context acceptance officer for any visual change (C Rule 6 made flesh). Read-only + Bash.
- **Protocol:** receive page + expected-result description written *before* it looks → serve → headless-Edge screenshot (G-LETTER item 3 recipe) → Read PNG → per-expectation pass/fail with what it actually sees. It did not write the code; it hunts for failure.
- **Owned/modifies:** nothing; screenshots to scratchpad.
- **Acceptance of its own work:** every expectation gets an explicit verdict; "can't determine from this angle" is a valid verdict that must trigger a second camera/URL-param shot, not a guess.
- **Model/effort:** sonnet / low (needs vision, not depth). **Typical mistakes:** passing a scene because it "looks reasonable" instead of checking the listed expectations; screenshotting before the CDN scene finishes (use virtual-time-budget, verify non-blank).

### Future tier (do not create yet — no code to own)
- **performance-analyst** (LCA/carbon/cost/daylight): becomes real when analysis code or a data pipeline exists. Trigger: user starts carbon/LCA work.
- **bim-data** (IFC/digital twin): trigger: first IFC requirement. Until then geo-interop covers import/export.

---

## Phase 5 — Collaboration architecture

**Topology: hub-and-spoke. The main session (commander) is the only hub. Agents never message each other.** All coordination passes through the commander using E-DELEGATION-TEMPLATES with the dispatch trio (goal+why / acceptance / report format).

### Routing table (commander's dispatch key)

| Task smells like | Route to |
|---|---|
| "generate/rebalance/edit a program" | program-planner → program-auditor (always, in sequence) |
| "check this program file" | program-auditor |
| "layout / packing / corridor / core / porosity" | module-packer |
| "columns / cantilever / slabs / frame / diagrid" | structure-frame |
| "short blocks / kit / stairs-in-stacks / DfD / kit export" | kit-of-parts |
| "looks wrong / camera / materials / colors / lag" | 3d-arch-diagram-gen |
| "button / slider / panel / stats display" | ui-panels |
| "export / Blender / Rhino / file format" | geo-interop |
| "constants drifted / sync the apps" | spec-guardian |
| any visual change just made | visual-verifier (mandatory before "done") |
| find something first | built-in Explore (haiku/sonnet per C Rule 4) |

### Ownership & conflict rules

- Section ownership per Phase 4 is exclusive. A task spanning two domains (e.g., "new packing option + its slider") = two sequential delegations (module-packer, then ui-panels), never one agent crossing the line.
- **Contract freeze points:** the layout shape (`{levels, coreShafts, floorRects, floorCorr, FW, FD}`) and `SHORT_PLACE` shape are inter-agent contracts. Changing either requires the commander to notify the downstream owner's next task explicitly.
- Conflicts about a shared value → spec doc wins; no spec → spec-guardian reports options → user decides (D §3: taste calls go to the user).

### Verification chain (never self-verify)

producer agent → evidence in its own report (command output/screenshot) → **independent check**: program work → program-auditor; visual work → visual-verifier; exports/Python → geo-interop's re-import proof; docs → commander read-back. High-stakes redesigns additionally get a second-opinion review (E template 5, fresh sonnet/opus).

### Escalation (inherits C Rule 5 verbatim)

haiku wrong once → sonnet. sonnet fails same subtask twice → opus **with full failure trail**. Solved pattern → demote for batch application. Hard cap 2 retry rounds per approach, then D §4 (switch approach) or user.

### Token optimization

- Big-File Surgery Protocol in every agent definition (no whole-file reads, ever).
- Report contract: ≤30 lines + file:line; artifacts to scratchpad/agentops/reports (create if absent), path returned.
- Agents receive *paths and line hints*, not pasted code, in their briefs.
- program-auditor and spec-guardian run on haiku — the recurring mechanical checks must be nearly free or they'll be skipped.

### Never-communicate pairs (hard rules)

- Nobody ↔ nobody directly: hub-and-spoke is absolute; no agent spawns another domain agent.
- visual-verifier / program-auditor never receive edit rights — the moment a verifier edits, self-verification returns.
- module-packer never touches mesh emission; structure-frame and kit-of-parts never touch each other's systems (LONG frame vs SHORT kit is the load-bearing boundary of the whole design, enforced at 493–505).

---

## Phase 6 — Roadmap

| Order | Agent | Priority | Why it exists | Complexity to create | Maintenance | When |
|---|---|---|---|---|---|---|
| 1 | visual-verifier | **Critical** | Every other agent's acceptance depends on it; institutionalizes verify-not-self-verify | Low (protocol + screenshot recipe) | Near zero | Now |
| 2 | program-auditor | **Critical** | Turns "looks right" into numbers; gate for all program work | Low (checklist is written above) | Low (rules change rarely) | Now |
| 3 | module-packer | **Critical** | Owns the research core; most future work lands here; most coupled code | High (must encode layout contract + spec-first) | Medium (spec sync) | Now |
| 4 | program-planner | High | The generative front of the pipeline; pairs with auditor | Medium | Low | Week 1–2 |
| 5 | structure-frame | High | Weekly iteration territory; HYBRID rules partially unimplemented (SKIN) | Medium-High | Medium | Week 1–2 |
| 6 | kit-of-parts | High | The thesis differentiator (DfD/demountable); BLOCKS handling needs care | Medium | Medium | Week 2–3 |
| 7 | 3d-arch-diagram-gen refresh | Medium | Exists; just stale — cheap win, keeps its memory | Low (edit constraints section) | Low | Week 2–3 |
| 8 | spec-guardian | Medium | Drift already observed; grows more valuable with every new app | Low | Low (haiku runs) | Week 3–4 |
| 9 | geo-interop | Medium | Exports work today; becomes critical when Rhino/Blender loop tightens | Medium | Medium | Week 3–4 |
| 10 | ui-panels | Medium | Small surface, low churn; general-purpose + E template covers it until then | Low | Low | When UI work queues up |
| — | performance-analyst | Future | No code to own | — | — | On first LCA/carbon task |
| — | bim-data | Future | No IFC anywhere | — | — | On first IFC requirement |

---

## Final report

1. **Architecture summary:** a self-contained client-side pipeline — parse → short-floor classification → integer module layout → (LONG structural frame ∥ SHORT brick kit) → instanced Three.js render → OBJ/kit export — implemented as one closure with 11 shared globals in a 204 KB single file, with domain rules split between four markdown specs and in-code magic numbers, duplicated by copy-paste across four sibling apps.
2. **Ecosystem:** 10 domain agents (hub-and-spoke under the main session; no orchestrator agent), 2 future placeholders. Ownership by code-section + spec-doc, contracts frozen at the layout shape and SHORT_PLACE.
3. **Dependency graph:**
```
                    commander (main session, C-MODEL-DISPATCH)
   ┌──────────┬──────────┬─────────┬──────────┬─────────┬────────┬──────────┐
program-planner module-packer structure-frame kit-of-parts 3d-arch ui-panels geo-interop
   │(validates)     │ layout shape ▲    │ SHORT_PLACE ▲        (render/UI consume all)
   ▼                └───────────────────┴──────────────┘
program-auditor          contracts frozen; changes routed via commander
        spec-guardian (audits all apps/specs) · visual-verifier (verifies all visual output)
```
   Data direction: program-planner → module-packer → {structure-frame, kit-of-parts} → {3d-arch, geo-interop}; auditors/verifiers sit outside the production chain by design.
4. **Implementation order:** as the Phase-6 table (1→10).
5. **First three:** `visual-verifier`, `program-auditor`, `module-packer`.
6. **Why these three:** the two verifiers are the enforcement layer — without them every later agent self-certifies and the whole architecture degrades into ritual (the exact decay mode predicted in G-LETTER); they're also the cheapest to build and run. `module-packer` owns the intellectual core of the research — the module/packing logic is where the next 12–24 months of design iteration will land, it guards the two inter-agent contracts, and it keeps MASSING-MODULE-LOGIC.md (the portable spec meant to outlive any single platform) synchronized with reality. Verification floor + research core = the pair everything else can be added onto safely.

### Honest limits

- Line numbers decay as the file is edited — agents must re-grep, never trust this document's numbers blindly.
- No agent here does real structural engineering, energy simulation, or code compliance — rule-based geometry only; say so when asked.
- The single-file architecture caps how clean agent ownership can be; if edit collisions become frequent, the fix is the module extraction at the integer-layout/mesh seam — a user decision, not an agent's.
- "Effort" recommendations depend on agent-definition frontmatter support in the installed Claude Code version; if absent, model choice is the only lever (per C-MODEL-DISPATCH).
