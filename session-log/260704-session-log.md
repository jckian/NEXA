# 260704 Session Log

Designed and deployed a complete Claude Code Agent Ecosystem blueprint for the program→massing workflow. Built on top of the institutional agentops system from 260703.

---

## Phase I — Agent Architecture Blueprint (PHASE 1–6 analysis)

### Methodology

Analyzed `program-massing-shortfloor.html` (204 KB) without full-file reads: deployed two parallel subagents (general-purpose sonnet + Explore sonnet) to map (1) internal pipeline/coupling, (2) spec ecosystem (references/ + sibling apps). Results synthesized into a six-phase design document.

### Key findings

**System topology**
- Single-file, self-contained Three.js pipeline: `parse → computeShortFloors → computeLayout → buildStructure (LONG) ∥ buildShortBlocks (SHORT) → render → OBJ export`.
- One closure, 11 shared mutable globals, zero module boundaries.
- Architectural rules split: four markdown specs (MASSING-MODULE-LOGIC, PROGRAM-MODULE-AREA-TABLE, PROGRAM-LONGSHORT-TABLE, HYBRID-STRUCTURE-RULES) + scattered magic numbers in code (COLSTEP=3, member-sizing grading, corridor-suppression 0.30, protrusion fractions).
- Copy-paste drift: MODULE=8.5ft exists in 4 apps (shortfloor, tile-editor, composer, program-massing) as separate constants; palette #172FC7/#E67033/#EEC341 duplicated verbatim in composer + program-massing; parse() forked (not synced); tile-editor's PROGRAM_SPECS mirrors PROGRAM-MODULE-AREA-TABLE.md by comment only.

**Coupling & bottlenecks**
- `buildShortBlocks` (789–990) mixes program classification + structural gravity + Three.js mesh emission in one function.
- `buildStructure` (477–788) interleaves architectural rules (grounded vs transfer/cantilever) with geometry.
- Magic numbers encode the entire structural vocabulary (COL_MAIN/COL_CANT column sizing, PRI/CANT/SEC girder grading).
- No LLM integration anywhere; deterministic hash3-based pseudo-randomness for reproducible packing.

**Functional domains** (10 identified + 2 future)
1. Program planning — author/edit schedules; LONG/SHORT balance; floor allocation.
2. Program validation — machine-check grammar, area sums, core counts, module-snap.
3. Module layout & packing — integer-space layout, corridors, 1×2 brick packing, porosity; the research core.
4. Structural system — column grids, MAIN vs transfer/cantilever, girder/joist grading (HYBRID-STRUCTURE-RULES).
5. Kit-of-parts (SHORT stack) — demountable brick system, FRAME/INFILL split, stairs, DfD kit export.
6. Visualization — scene, camera, lighting, materials, instancing, palette.
7. UI/interaction — panels, controls, wiring, rebuild triggers.
8. Data/interop — OBJ export, Rhino/Blender bridges, output.txt ecosystem.
9. Spec governance — single-source-of-truth policing (constants, palettes, parse forks, PROGRAM_SPECS↔table sync).
10. Visual acceptance — independent screenshot-based verification (C Rule 6 made flesh).
+ Future: performance/LCA/carbon/energy/daylight (no code yet); BIM/IFC (no code yet).

### Deliverable: `agentops/AGENT-ARCHITECTURE.md` (34 KB)

Six-phase blueprint:
- **Phase 1** — Repository analysis: current app workflow, data flow, UI/rendering behavior, coupling points (11 globals), bottlenecks, repeated patterns.
- **Phase 2** — Functional decomposition: 10 domains + 2 future, each with purpose/inputs/outputs/current impl/scalability/whether deserves agent.
- **Phase 3** — Ecosystem design: 10-agent roster, design decisions (orchestrator is main session not subagent; FOAM paused; spec-first rule; no generic agents; ownership by code-section + spec-doc; no refactoring without user approval).
- **Phase 4** — Agent specifications: for each of 10 agents — mission, owned code/specs, never-modify list, inputs/outputs, acceptance criteria, validation checklist, escalation rules, model/effort, typical prompts/mistakes, future expansion.
- **Phase 5** — Collaboration: routing table, ownership/conflict rules, verification chain, escalation (inherits C Rule 5), never-communicate pairs (hard rules: hub-and-spoke absolute; verifiers never edit; LONG-frame/SHORT-kit boundary frozen).
- **Phase 6** — Roadmap: priority/complexity/maintenance per agent, suggested creation order. First three: visual-verifier (critical, cheap, low-maint) → program-auditor (critical, cheap, low-maint) → module-packer (critical, the research core).

All line references tied to 260704 state of shortfloor.html; notes must be re-verified when file changes.

---

## Phase II — Deploy First Two Agents

### Agent definitions written

1. **`program-planner.md`** (sonnet, memory: project)
   - Responsibilities: author/revise program schedules in ProgramFormat grammar; LONG/SHORT balance; floor allocation; adjacency; keep isShort regex and PROGRAM_SPECS synchronized.
   - Key coupling: type names resolved by substring matching downstream (isShort regex in shortfloor.html, PROGRAM_SPECS in tile-editor.html); inventing a new type without checking the regex is a silent defect.
   - Verification: custom Python script (area sums within 2%, ratio ±5%, ≥3 cores per floor, w×h within 10% of area); no eyeballing.
   - Hard stop: two failed attempts to satisfy conflicting constraints → report trail; grammar/historical distribution changes → ask user; pure design taste → present options.
   - Reports: file path, floor count, GFA, LONG/SHORT ratio; verification script output; rationale ≤5 lines; flags on NEW type names.

2. **`structure-frame.md`** (sonnet, memory: project)
   - Responsibilities: buildStructure (LONG frame) + HYBRID-STRUCTURE-RULES spec; column grids, MAIN vs transfer/cantilever, girder/joist grading, slabs, curtain wall, fins.
   - Key principle: "rule-based geometry, not structural engineering" — when task needs real loads/code compliance, say so instead of faking.
   - Verification: local server + headless-Edge screenshot (full command embedded in prompt); zero new console errors; rule-touching requires script-counted proof (e.g., every hung column has a back-span partner), not eyeballs.
   - Hard stop: FOAM work without explicit user approval; changes to computeLayout or SHORT-cell emission (cross-domain); two failed attempts.
   - Reports: file:line per edit; screenshot path; rule-check output; HYBRID-STRUCTURE-RULES.md update status.

Both definitions stored at `agentops/agent-defs/` and copied to `.claude/agents/` for immediate deployment.

### System integration

- Copied to `.claude/agents/program-planner.md` and `.claude/agents/structure-frame.md` (ready for `/agents` or manual invocation).
- Both inherit memory: project (will accumulate domain context across sessions).
- Big-File Surgery Protocol baked into prompts (no whole-file reads, Grep → ±60-line windows).
- Verification loop and stop conditions explicit for each.

---

## Integration with Institutional System

- `CLAUDE.md` (updated) now routes to `agentops/AGENT-ARCHITECTURE.md` in the routing table.
- Both new agents documented in Phase 4 of the blueprint with examples of typical prompts.
- Program-planner forward-compatible with program-auditor (which validates its output); will be built next per Phase 6 roadmap.
- Structure-frame ready for parallel deployment with geometry agents once module-packer (Phase 6 priority #3) exists.

---

## Open items / Next steps

1. **Test run:** try program-planner on a small task (e.g., "Generate a 4F test program, 2,000 m², LONG 70%") to validate report format fits the ≤30-line contract and file:line references work.
2. **Build the remaining 8 agents** per Phase 6 roadmap:
   - Next critical: program-auditor (haiku), module-packer (sonnet) — both are on the verification path.
   - Then spec-guardian (haiku), geo-interop (sonnet), 3d-arch-diagram-gen refresh.
   - Lower priority: ui-panels, kit-of-parts (when SHORT-block work is planned), kit-of-parts actually owns much of the DfD specialist knowledge.
3. **Session workflow:** next main-conversation sessions will load the new CLAUDE.md → route by AGENT-ARCHITECTURE.md → dispatch via C-MODEL-DISPATCH + E templates. No agent is spawned until a task explicitly names one or the commander (main session) judges the task fits a domain from the routing table.

---

## Files modified/created

| File | Status |
|---|---|
| `CLAUDE.md` | Updated routing table (added AGENT-ARCHITECTURE) |
| `agentops/AGENT-ARCHITECTURE.md` | New (34 KB, 6-phase blueprint) |
| `agentops/agent-defs/program-planner.md` | New (dropped into `.claude/agents/`) |
| `agentops/agent-defs/structure-frame.md` | New (dropped into `.claude/agents/`) |

---

## Notes

- The blueprint is frozen at 260704 shortfloor.html state. Line numbers are reference-only; any agent working in that file must Grep first.
- The 10-agent ecosystem is designed for 12–24 month evolution; future work (performance, BIM, FOAM, multi-tower) is mapped but not built.
- Orchestration stays in the main session, governed by agentops/C-MODEL-DISPATCH.md + E templates. No orchestrator agent means no context-blind middleman.
- This is the first production deployment of the institutional system built in 260703. Lessons learned will go to agentops/LESSONS.md per F-MAINTENANCE protocol.

---

## Addendum (later session, Fable 5): SHORT program cross-floor interlock

**Request:** SHORT programs should interlock across floor lines — one storey reads as [top of the program below] + [its own program] + [bottom of the program above]. Constraints: span ≤3 storeys, self-supported (slabs stay solid; user models openings in Rhino), never enter LONG cells.

**Key insight:** the brick fill already crossed floor lines physically (continuous 8'-6" course grid per run, vertical 1:2 modules span 2 courses). What did NOT interlock was **program identity**: `progByCourse[k]` assigned every course to its height-slice floor, so program volumes rendered as flat horizontal bands.

**Change (program-massing-shortfloor.html, backup at BACKUP/program-massing-shortfloor.html.bak-260704):**
- New `INTERLOCK_P = 0.8` constant (near SHORT_THRESHOLD): fraction of eligible columns whose program boundary shifts ±1 course; 0 restores old flat bands.
- In `buildShortBlocks`: per column (i,j), the boundary course between consecutive floors shifts -1/0/+1 via `hash3` (deterministic), only where BOTH floors' SHORT footprints contain that column; bands kept ordered per column. New `progAt(i,j,k)` lookup with nominal-slice fallback.
- Brick coloring in massing mode now uses `progAt` instead of the height-slice map. Volume, packing, gravity, stairs, FRAME/INFILL, exports: all untouched (identity-only swap). Constraints hold by construction: intrusion is exactly 1 course into immediate neighbours (≤3 storeys); footByFloor holds only SHORT cells inside the run (never LONG).
- Added URL params for headless verification: `?color=type|category&mode=solid|structure` (read at init, before loadText).

**Verification:** node vm syntax check OK; served + headless-Edge screenshots; A/B with INTERLOCK_P 0 vs 0.8 in Type color mode → images differ, pixel-diff localizes changes to the SHORT plug-in zone (bbox 571,438–902,950). Category-mode shots are md5-identical because the sample's swaps are apartment↔apartment (same category/hue) — see LESSONS.md 260704.

**Open question for user:** interlock is visually subtle with the built-in SAMPLE because plug-in floors are mostly one type (`2b2b apartment`) and Type mode hashes hue by type string — same-type interlock is invisible. Options: leave as is (varied real programs will show it) / hue per type+level so cross-floor intrusions pop / add a UI slider for INTERLOCK_P.

**Follow-up (user chose both options):**
- `colorFor` type mode: hue stays per-type, lightness now steps by HOME floor (40/49/58/67 cycling every 4 levels) — same-type interlock (apartment over apartment) reads as light/dark intrusions.
- New "Interlock (program ↕ span)" slider (`ctl-interlock`, 0–1, default 0.8) wired like the protrude slider (rebuild on input); `INTERLOCK_P` is now `let`; also settable via `?interlock=0..1` URL param (slider/readout sync on load).
- Verified: syntax OK; on/off screenshots differ exactly in the SHORT zone; crops show green/pink bricks interlocked into the apartment mass at 0.8 vs clean bands at 0.
