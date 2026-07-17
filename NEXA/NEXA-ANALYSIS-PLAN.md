# NEXA — Strategic Analysis & Execution Plan (Task Prompt)

> Saved 2026-07-09; evaluated and grounded against the actual repo the same day (Fable 5).
> **Read §0 (Grounding) before executing anything below — it corrects the original
> prompt's blind spots and replaces its Phase 0.**

---

## §0 Grounding — what NEXA actually is (verified 2026-07-09)

**NEXA = this repo.** `NEXA-site.html` self-describes as "NEXA — Program Distribution
Agent", an SCI-Arc SP26 research prototype. (VORO is the earlier brand; `chat.html`
still carries the old "Voro" title.) The product pipeline today:

```
program-input.html (brief wizard → ProgramFormat .txt, RIGID/CALIBRATED/SPONGE scaling)
        │
        ▼
program-massing-shortfloor.html (module layout → LONG structure ∥ SHORT kit → render)
        │
        ▼
OBJ / kit exports · Rhino/Blender bridges · NEXA-site.html (public face)
```

**Critical facts the original prompt does not know:**

1. **A full project audit already exists**: `agentops/AGENT-ARCHITECTURE.md`
   (2026-07-04) — line-level pipeline analysis, functional decomposition,
   coupling/bottleneck list, a 10-agent roster with specs, and a build-order
   roadmap. **Do NOT re-audit the codebase. Read that file + the newest
   `session-log/` entries + `session-log/260707-HANDOFF.md` instead.**
2. **Zero LLM integration in the product**: all four HTML apps are deterministic,
   client-only, no API calls (`chat.html` is a UI mock). All existing "AI agents"
   are dev-time Claude Code subagents, not runtime product agents.
3. **Single-file constraint**: HTML apps open via `file://` — they cannot fetch
   external sidecars (that is why BLOCKS mesh data is inlined). An external YAML
   rule engine conflicts with this; inline-or-server is a real trade-off.
4. **Verification culture is the project's strength**: node harness (166
   assertions), replica scripts, headless-Edge screenshot pipeline, session
   logs, BACKUP/ copies. Any new phase must plug into this, not bypass it.
5. **Open item to check first**: 260707 log flags an UNVERIFIED P2
   depth-discipline edit in program-massing-shortfloor.html (re-verify or revert
   before building on it). Later logs don't mention it — confirm status.

**Gap map — the 7 target capabilities vs current state:**

| Capability | Status | Note |
|---|---|---|
| 1. Understand requirements | Partial | program-input wizard is rule-based; no NL/LLM brief intake |
| 2. Interpret constraints | Mostly done | module/core/interlock/egress-spacing rules implemented + spec'd |
| 3. Apply building regulations | **Missing** | only heuristics (restrooms, ≥3 stairs, core separation) |
| 4. Generate design options | Partial | single-scheme; multi-scheme started (260708-two-scheme-core-PLAN.md) |
| 5. Validate code compliance | **Missing** | harness = regression tests, not compliance |
| 6. Optimize spatial performance | Partial | metrics exist (overlap/corridorΣ/fill/float) but scattered; no auto loop |
| 7. Produce outputs | Done | OBJ/kit export, Rhino/Blender bridge, screenshots |

**Decisions reserved for the USER (do not decide autonomously):**

- **Runtime AI vs dev-time AI** — **DECIDED by user 2026-07-09: dev-time first.**
  This semester: stabilize the deterministic pipeline + build compliance
  validation as dev-time tooling. Runtime AI (LLM in the product loop) is
  reserved as a later roadmap phase; chat.html → Claude API integration is a
  future item, not current scope. The roadmap must reflect this sequencing.
- **Rule engine format**: YAML engine vs the existing spec-markdown pattern
  (see constraint #3). Recommendation: extend spec-markdown now, defer YAML.
- Building-code MVP scope beyond the recommended three categories below.

**Known overlap warning**: the original prompt's 6-agent proposal overlaps the
existing 10-agent roster in AGENT-ARCHITECTURE.md (compliance≈program-auditor
extension; validation≈visual-verifier; optimization≈module-packer scoring loop).
Merge with the existing roster — do not create a parallel one. Note the roster's
own "first three" (visual-verifier, program-auditor, module-packer) are NOT yet
created; the agents that exist are program-planner, structure-frame,
3d-arch-diagram-gen.

---

## §0.5 Revised execution split (run as three separate tasks)

- **Task A — Gap analysis & roadmap revision** (Sonnet): inputs =
  AGENT-ARCHITECTURE.md, 260707-HANDOFF.md, newest session log, this file.
  Output = plan-vs-reality gap list + a revised phase roadmap that reuses what
  exists. Re-auditing source code is out of scope.
- **Task B — Building-code MVP spec** (Sonnet, research): collect and structure
  LA rules for **zoning envelope (FAR/height/setbacks), egress (stair count /
  travel distance), occupancy classification** only — fire/parking/energy/
  structural are explicitly deferred (research-prototype narrative doesn't need
  them yet). Output = a spec markdown in `references/` following the
  HYBRID-STRUCTURE-RULES.md style: rule table + source citation + how it maps to
  existing pipeline values.
- **Task C — Roadmap merge** (user review or Opus): merge A+B outputs with the
  existing Phase-6 agent roadmap into one execution order. Judgment-heavy.

**Recommended pre-work before Task A** (cheap, do first):
1. Confirm/resolve the unverified P2 edit (grounding fact #5).
2. Create `program-auditor` + `visual-verifier` agents verbatim from
   AGENT-ARCHITECTURE.md §4.2/§4.10 — the verification floor for everything after.

---

# Original prompt (as received 2026-07-09)

You are the Chief Architect and AI Product Strategist for NEXA.

Your task is NOT to build anything yet.

Your task is to analyze the current NEXA project state and create an execution plan.

You will receive:
- Existing project files
- Current architecture
- Existing prompts
- Existing code
- Existing design concepts
- Existing documents

Analyze everything before making recommendations.

==================================================

## OBJECTIVE

Determine the optimal roadmap to transform NEXA into an AI-powered architectural design system.

The system goal — NEXA should be able to:

1. Understand project requirements
2. Interpret architectural constraints
3. Apply building regulations
4. Generate design options
5. Validate code compliance
6. Optimize spatial performance
7. Produce architectural outputs

==================================================

## ANALYSIS TASKS

Analyze the existing files and answer:

### 1. Current State Assessment

Identify:

- What already exists
- What is missing
- What is duplicated
- What should be removed
- What should be improved

Classify every existing component:

- KEEP
- MODIFY
- REBUILD
- REMOVE

Explain why.

> Grounding note: start from AGENT-ARCHITECTURE.md Phase 1–2 instead of
> re-deriving; classify at the component level (apps, specs, agents), not
> line level.

==================================================

### 2. System Architecture Review

Evaluate whether the current architecture supports:

- AI agent workflow
- Rule engine
- Knowledge base
- Design generation
- Code validation
- Optimization loop

Identify architectural weaknesses.

> Grounding note: the known weaknesses are already listed in
> AGENT-ARCHITECTURE.md Phase 1 §4 (one closure / 11 globals; magic numbers;
> 4-app copy-paste drift; token bottleneck). Add to that list, don't rewrite it.

==================================================

### 3. AI Agent Strategy

Design the required AI agent system.

Determine which tasks should be handled by:

- Strategic reasoning agent
- Research agent
- Code compliance agent
- Design generation agent
- Validation agent
- Optimization agent

For each agent define:

- Purpose
- Input
- Output
- Required model capability
- Recommended Claude model: Opus / Sonnet / Haiku

> Grounding note: MERGE with the existing 10-agent roster (see §0 overlap
> warning). The runtime-vs-devtime question is a USER decision — present both
> paths, recommend one, do not implement either.

==================================================

### 4. Knowledge Base Strategy

Evaluate:

- Existing documents
- Existing rules
- Existing prompts

Determine — should we:

- Keep current documents?
- Convert into structured rules?
- Create YAML rule engine?
- Create RAG knowledge base?
- Separate code rules and design heuristics?

Provide recommended structure.

> Grounding note: spec-in-markdown ↔ implementation-in-HTML is the established
> pattern and it works; RAG is over-engineering at this repo size; YAML engine
> conflicts with the single-file/file:// constraint (§0 fact #3).

==================================================

### 5. Building Code Strategy

Do NOT immediately collect all codes.

First determine: what codes are actually needed for MVP.

Prioritize: California / Los Angeles

Categories:

- Zoning
- Occupancy
- Height & Area
- Construction Type
- Egress
- Accessibility
- Fire
- Parking
- Energy
- Structural constraints

Explain priority.

> Grounding note: recommended MVP = zoning envelope + egress + occupancy
> (see Task B in §0.5). Justify any deviation.

==================================================

### 6. Development Roadmap

Create phases:

- Phase 0: Project audit — **already done (AGENT-ARCHITECTURE.md); replace with a delta-audit**
- Phase 1: Foundation
- Phase 2: Knowledge system
- Phase 3: Rule engine
- Phase 4: Design generation — **partially exists; extend to multi-scheme**
- Phase 5: Validation
- Phase 6: Optimization

For each phase provide:

- Goal
- Tasks
- Deliverables
- Required AI model
- Estimated complexity
- Dependencies

==================================================

### 7. Immediate Next Actions

At the end provide "Next 7 Actions".

Only list actions that should actually be done next.

Rank: Priority 1 / Priority 2 / Priority 3

Do not suggest unnecessary work.

==================================================

## IMPORTANT RULES

- Do not assume missing information.
- Do not blindly follow existing architecture.
- Challenge weak decisions.

Think like:

- AI system architect
- Architectural computational designer
- Building code expert
- Startup CTO

Your output should be a strategic execution plan, not a technical tutorial.

==================================================

## Execution notes (for the Sonnet session running this)

- Follow `CLAUDE.md` file-access rules: never fully read `index.html` /
  `index2.html` / `program-massing-shortfloor.html`; scope all searches; exclude
  `node_modules/`, `BACKUP/`, `RENDER/`, `forVideo/`, `my-video/`,
  `UI_ClaudeDesign/`, `UIUX/`.
- Deliverable: a strategic execution plan document (suggest saving as
  `NEXA-EXECUTION-PLAN.md` at project root).
- Respond to the user in Traditional Chinese; keep file contents in English.
