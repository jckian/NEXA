# NEXA — Strategic Execution Plan

> **Task A deliverable** (gap analysis + revised roadmap), written 2026-07-09.
> Scope per `NEXA-ANALYSIS-PLAN.md` §0.5: inputs were `agentops/AGENT-ARCHITECTURE.md`,
> `session-log/260707-HANDOFF.md`, `session-log/260708-two-scheme-core-PLAN.md`,
> `session-log/260709-session-log.md`, plus a **delta-audit** of the live files
> (grep-window only; no re-audit of source).
> Task B (building-code MVP spec) and Task C (roadmap merge) are **not** in this document.
>
> **Standing decision (user, 2026-07-09): dev-time AI first.** Runtime AI (an LLM inside
> the product loop) is Phase R, deferred. `chat.html` → Claude API is a future item.

---

## 1. Delta-audit — what changed since the 2026-07-04 blueprint

`AGENT-ARCHITECTURE.md` was written 5 days ago and is already materially out of date.
Verified today against the live files:

| Blueprint says | Reality (2026-07-09) | Consequence |
|---|---|---|
| shortfloor ≈ 204 KB, ~1220 lines | **251 KB, 2112 lines** | Every line number in the blueprint is off by 40–70%. Its Phase-4 "owned line ranges" are unusable as written. |
| `CORE_OPTION` = edge \| inset | **compact (default) \| pinwheel \| inset** (`:338–344`) | Multi-scheme generation *already shipped*. Capability #4 is further along than the plan assumed. |
| P2 depth-normalization is LIVE but UNVERIFIED | **Gated behind `if (PINWHEEL)` (`:376`) — inert on the default path, still live on `pinwheel`** | The 260707 open item is **not closed**. Scoping made it harmless by default; it did not verify it. Nobody has confirmed P2 under `pinwheel`, and 260708 left no log to say otherwise. Its header comment (`:368`) still says "edge parti only" — a value that no longer exists. See §8 action 2. |
| — | New since blueprint: `SKIN_ON`, `INTERLOCK_P` slider, `MOVE_OFFSETS` free-move + `?move=` debug hook, `subdivideBlock`/`MAX_SIDE_MOD` (P1.5), `exportSkinOBJ` | Four unowned surfaces. `kit-of-parts` and `module-packer` specs don't mention them. |
| Roster "first three" = visual-verifier, program-auditor, module-packer | **None of the three exist.** Existing agents: `program-planner`, `structure-frame`, `3d-arch-diagram-gen` | The roster was built **inverted**: the producers exist, the verifiers don't. |

Checks run today: `node harness.js` → **166 passed, 0 failed**. Grep for
`fetch(` / `XMLHttpRequest` / `api-key` / `openai` / `anthropic` across all six apps → **zero hits**.
Grounding facts #2 (no LLM in product) and #4 (verification culture) hold.

**Three findings the blueprint could not have predicted:**

1. **`program-planner` shipped with an unsatisfiable acceptance gate.** Its spec
   (§4.1) says "output passes `program-auditor` with zero errors". `program-auditor`
   does not exist. The agent has been self-certifying since it was created — the exact
   decay mode `G-LETTER` predicts.
2. **Session-log discipline failed on the biggest day.** `260708` produced three
   backups (`preTwoScheme`, `preCompactCore`, `preP5`) and landed the two-scheme
   parti — and has **no session log**. The 260709 log doesn't mention it either. The
   one convention that costs nothing was skipped on the one day it mattered most.
3. **The verification kit is a second copy-paste fork of the core IP.**
   `replica3.js` hand-mirrors `computeLayout` so the harness can measure it, and it
   lives at `session-log/260707-tools/` — a *dated session artifact* path for what is
   actually project infrastructure. It is already stale against compact/pinwheel. This
   is the same failure class as `MODULE=8.5ft` living in four files, applied to the
   research core itself.

---

## 2. Current-state classification

Component-level, per the grounding note. Rationale is the point; the verdict is the summary.

### KEEP (works, verified, don't touch)

| Component | Why |
|---|---|
| `program-input.html` generator (three-tier RIGID/CALIBRATED/SPONGE scaling) | 166 assertions, 9-case matrix, ±2% GFA. The most rigorously verified thing in the repo. |
| `harness.js` + the 9-case fixture set | The regression floor. Everything downstream leans on it. |
| Headless-Edge screenshot pipeline (G-LETTER item 3) | The only acceptance mechanism for taste deliverables. Cheap, repeatable. |
| Spec-in-markdown ↔ implementation-in-HTML pattern | It works. It is the reason `MASSING-MODULE-LOGIC.md` is portable beyond this codebase. |
| Determinism (`hash3`, zero `Math.random`) | **This is the research's citability.** See §4. |
| `BACKUP/` copy discipline | Ugly, effective, no git. |

### MODIFY

| Component | Change | Why |
|---|---|---|
| `agentops/AGENT-ARCHITECTURE.md` | Strip line numbers → function-name anchors; append the §1 delta | A blueprint that decays in 5 days must not use line numbers as its interface. |
| `replica3.js` + `260707-tools/` | Promote to a stable `tools/` path; re-sync to compact/pinwheel | Project infrastructure filed as a session artifact. |
| `program-auditor` spec (§4.2) | Extend the checklist with the MVP code rules (Task B) | The spec's own "Future" line already predicted this. It is the natural home for compliance. |
| `module-packer` spec (§4.3) | Add ownership of the three parti schemes, `subdivideBlock`, `INTERLOCK_P` | Four unowned surfaces landed in its domain. |
| `references/` | Triage into `references/specs/` (canonical) vs `references/archive/` | 45 items mixing spec markdown, `.fig`/`.3dm`/`.pdf`/`.xlsx` binaries, stray scripts (`temp_script.js`, `test.js`, `change_height.js`), a literal `New folder`. Nobody can tell what is authoritative. |
| `chat.html` | Rebrand Voro → NEXA (title `:5`, `#brand-name` `:263`) | Two brands in one repo. Cosmetic, one-line, do it while passing. |

### REBUILD

| Component | Why |
|---|---|
| The parti-scheme "spec" | It doesn't exist. `compact`/`pinwheel`/`inset` are documented **only as code comments** (`:338–344`), one of which is already wrong. This is the most valuable undocumented logic in the repo → `references/SCHEME-PARTI-RULES.md`. |
| Metrics ownership | Overlap / corridorΣ / core-float / touch% / fill live in `replica3.js` (dev-side). Optimization (capability #6) cannot exist while the app cannot score itself. Metrics must move **into** the app. |

### REMOVE

| Component | Why |
|---|---|
| `_handoff-test.html` (repo root) | The 260707 plan said delete after use. It's still there. |
| `references/temp_script.js`, `test.js`, `New folder/`, `website-placeholder` | Dead weight in the directory that's supposed to be the knowledge base. |
| The original prompt's parallel 6-agent roster | Four of its six roles already have written specs. A second roster doubles maintenance and halves authority. **Rejected.** |
| YAML rule engine | See §4. |
| RAG knowledge base | See §4. |

**Not removed, deliberately:** `index.html` / `index2.html` / `program-massing.html` /
`structure-zone-test.html` are legacy but are the TPAC/53W53 case-study record. Archive
later; deleting case-study evidence in a research repo is a one-way door.

---

## 3. Architecture review — weaknesses *added* to the blueprint's list

`AGENT-ARCHITECTURE.md` Phase 1 §4 already names: one closure / 11 globals; magic
numbers; 4-app copy-paste drift; token bottleneck. Those stand. Add:

5. **Spec-code drift is now bidirectional.** Code comments cite spec values that were
   renamed (`edge` → `compact`); the blueprint cites line numbers that moved. Both
   directions rot. Anchors, not line numbers; and specs must be updated in the same
   task as the code (this is already the "spec-first rule" — it was simply not enforced,
   because nothing enforces it).
6. **The verification infrastructure has no owner and no stable path.** `replica3.js`
   is a hand-maintained fork of the layout kernel. When it drifts, the metrics silently
   describe a layout that no longer exists.
7. **Session logging is the actual single point of failure.** With no git, the session
   log *is* the history. 260708 has none. Three backups exist with no record of what
   they preserve or why.
8. **There is nowhere to hang building code.** The harness tests the *generator*, not
   the *design*. Nothing in the system consumes a rule and reports a violation against a
   produced massing. Capabilities #3 and #5 are missing not because the rules are
   missing, but because **the socket they plug into is missing.**
9. **No scheme-comparison substrate.** Two schemes exist; nothing can say scheme A is
   better than scheme B. Capability #6 is blocked on §2's "metrics ownership" rebuild,
   not on any optimization algorithm.

### Does the architecture support the six target capabilities?

| Requirement | Supported? | The actual blocker |
|---|---|---|
| AI agent workflow | Yes | Hub-and-spoke is sound. It is only half-built, and built inverted (producers before verifiers). |
| Rule engine | No | No socket (#8). Not a format problem. |
| Knowledge base | Yes, already | It is `references/*.md`. It needs triage, not replacement. |
| Design generation | Yes | Working today, 2 schemes. Needs a registry, not a rewrite. |
| Code validation | No | Blocked on #8. |
| Optimization loop | No | Blocked on #9 (metrics are dev-side). |

**Nothing here requires an architectural rewrite.** The single-file/`file://` constraint
is livable. The two real structural gaps — a validation socket and in-app metrics — are
additive.

---

## 4. Decisions, including three the plan asked me to challenge

**Runtime AI is deferred — and the reason is stronger than scheduling.**
NEXA's differentiator is that it is *deterministic*: `hash3` seeds, no `Math.random`,
166 assertions, replica-verifiable layouts. Same input ⇒ same building, forever. An LLM
in the layout kernel destroys exactly that property, which is the one that makes the
research reproducible and citable. **Runtime LLM belongs at the edges — brief intake
(NL → ProgramFormat), scheme critique, report writing — never in the generation kernel.**
Write this down as a standing architectural constraint, not a scheduling preference. It
survives the semester.

**YAML rule engine: rejected.** Two reasons, and the second is the real one.
(a) `file://` apps cannot fetch sidecars — that's why `BLOCKS` is inlined. (b) More
fundamentally: *there is no interpreter*. A YAML file with no engine reading it is a
markdown table with worse ergonomics and no prose. Build the checker first; if a second
consumer of the same rules ever appears, extract the format then.

**RAG: rejected.** The knowledge base is ~10 spec markdown files. RAG over 10 documents
you could paste in full is over-engineering with a retrieval-failure mode attached.

**Recommended knowledge structure** (evolution, not replacement):

```
references/
  specs/                      ← canonical, spec-first rule applies
    ProgramFormat.txt              (grammar — user-owned, agents may not edit)
    MASSING-MODULE-LOGIC.md        (module system)
    SCHEME-PARTI-RULES.md          ← NEW: compact/pinwheel/inset (rescued from comments)
    HYBRID-STRUCTURE-RULES.md      (structure)
    PROGRAM-MODULE-AREA-TABLE.md   (sizing)
    PROGRAM-LONGSHORT-TABLE.md     (classification)
    CODE-RULES-LA.md               ← NEW: Task B output
    RESTROOM-GUIDELINES.md
  case-studies/               ← TPAC / 53W53 / TAMA distributions (frozen records)
  archive/                    ← binaries, stray scripts, old diagrams
```

**Separate code rules from design heuristics — yes, and this is the load-bearing split.**
`SCHEME-PARTI-RULES.md` (heuristics: taste, negotiable, the research) vs
`CODE-RULES-LA.md` (regulations: pass/fail, non-negotiable, external authority). They
have different owners, different failure modes, and different escalation paths. Merging
them is how a research prototype starts quietly claiming code compliance it does not have.
The 260707 HANDOFF is already honest about this ("massing study, not code compliance") —
the file structure should make that honesty structural.

---

## 5. AI agent strategy — merged roster

The original prompt's six roles map onto the existing roster. **One genuinely new agent.**

| Prompt's role | Resolution | Model / effort |
|---|---|---|
| Strategic reasoning | **The main session.** Blueprint design-decision #1 stands: no orchestrator agent. | — |
| Research | Built-in `Explore` + a **one-shot** general-purpose run for Task B. Do **not** make it permanent — no code to own (F-MAINTENANCE). | sonnet + WebSearch, one-shot |
| Code compliance | **NEW: `code-compliance`.** Owns `CODE-RULES-LA.md` + `checkCompliance()`. This is `program-auditor`'s own "Future" line, promoted to an agent because the rule surface is external, cited, and versioned. | sonnet/high to author rules; **haiku/low to run checks** |
| Design generation | `module-packer` (specced, uncreated) + `program-planner` (exists) | sonnet/high, sonnet/medium |
| Validation | `visual-verifier` + `program-auditor` (both specced, **both uncreated**) | sonnet/low, haiku/low |
| Optimization | **Deferred — no agent.** Fold scheme scoring into `module-packer` until a real loop exists. Create `design-scorer` on first genuine optimization task. | — |

### `code-compliance` — the one new spec

- **Mission:** check a produced massing against `CODE-RULES-LA.md`. Report violations
  with rule citation + measured value + threshold. Read-only on the repo.
- **Inputs:** a layout result (`{levels, coreShafts, floorRects, floorCorr, FW, FD}`) or
  a program `.txt` + occupancy assumption. **Outputs:** violation table; never an adjective.
- **Hard boundary:** *rule-based geometry checking, not a code consultant.* It reports
  "egress separation = 0.29·W, rule requires ≥ ⅓·W" — it never says "this building is
  compliant." Say so in the agent definition, verbatim.
- **Why haiku for the run:** the recurring mechanical check must be nearly free or it
  gets skipped (C Rule 5, the `program-auditor` pattern).

**Roster order stands as blueprint Phase 6, with one correction:** the roster was built
producers-first. Correct it by creating **`visual-verifier` and `program-auditor` before
anything else** — including before `module-packer`. `program-planner` is currently
self-certifying against an agent that does not exist.

---

## 6. Building-code strategy — MVP scope

**Recommendation confirmed: zoning envelope + egress + occupancy classification. No deviation.**

The priority argument is not "these are the most important codes." It is: *these are the
only three that bind on data the pipeline already produces, and all three are places
where the pipeline currently fakes it.*

*(Tiers below are code-scope tiers. They are unrelated to the P1/P1.5/P2 edit codenames
used for the 260707 layout work, and unrelated to §8's Priority 1/2/3.)*

| Category | MVP? | Why |
|---|---|---|
| **Zoning** (FAR / height / setback) | **Tier 1** | The pipeline already computes GFA, floor count, and `FW×FD`. FAR is a division. This is the cheapest real regulation in the entire code, and it constrains massing — which is the whole product. |
| **Egress** (stair count / travel distance / separation) | **Tier 1** | Already faked, *knowingly*: HANDOFF §3 admits the ⅓-width soft rule and the inset exemption are "massing study, not code compliance". The `≥3 fire stairs` check is a heuristic. There is an existing lie to replace with a measurement. |
| **Occupancy** classification | **Tier 1** | Free-ish: `ProgramFormat` types map to occupancy groups. It is also the *dependency* for everything below — you cannot compute height/area limits without it. |
| Height & Area limits | **Tier 1.5** | Falls out almost free once occupancy exists. Add it in the same pass if Task B's research is clean; do not scope it up front. |
| Construction type | Tier 2 | Depends on occupancy + a material system the model doesn't have. |
| Accessibility | Tier 2 | Cheap to state, but no geometry consumes it (no ramps, no clear-width modeling). A rule nothing can check is a rule nobody runs. |
| Fire / Parking / Energy / Structural | **Defer** | Fire and structural need engineering the project explicitly disclaims (blueprint "Honest limits"). Parking and energy need systems that don't exist. A research prototype's narrative does not need them, and each would add a rule surface with no consumer. |

**The socket comes before the rules.** Build `checkCompliance(layout) → violations[]`
against *one* rule (FAR) before Task B delivers thirty. A rule set with no checker is a
document; a checker with one rule is a system.

---

## 7. Revised roadmap

Phase 0 (audit) is **done** — replaced by §1 of this document. Each phase names its
dependency, and no phase begins before its verification floor exists.

### Phase 1 — Verification floor & repo hygiene · *Week 1* · complexity **Low**
- **Goal:** stop self-certification. Make the blueprint trustworthy again.
- **Tasks:** create `visual-verifier` (§4.10) and `program-auditor` (§4.2) verbatim ·
  promote `session-log/260707-tools/` → `tools/` and re-sync `replica3.js` to
  compact/pinwheel · delete `_handoff-test.html` · re-anchor `AGENT-ARCHITECTURE.md`
  (function names, not line numbers) + append the §1 delta · write the missing 260708 log.
- **Deliverables:** 2 agents · `tools/` · updated blueprint · 260708 retro log.
- **Model:** haiku (auditor runs) / sonnet (blueprint edit). **Depends on:** nothing.

### Phase 2 — Knowledge system · *Week 1–2* · complexity **Low-Medium**
- **Goal:** one place where each rule lives, and it is legible.
- **Tasks:** `references/` triage into `specs/` · `case-studies/` · `archive/` ·
  **write `SCHEME-PARTI-RULES.md`** (rescue compact/pinwheel/inset from code comments;
  fix the stale `:368` "edge parti" comment) · create `spec-guardian`, run the standing
  constant/palette drift audit · rebrand `chat.html`.
- **Deliverables:** `references/specs/` · `SCHEME-PARTI-RULES.md` · first drift report.
- **Model:** sonnet (write) / haiku (drift audit). **Depends on:** Phase 1 (visual-verifier
  gates any code edit).

### Phase 3 — The validation socket · *Week 2–3* · complexity **Medium**
- **Goal:** make it *possible* to check a design. Not to check it well.
- **Tasks:** run **Task B** → `references/specs/CODE-RULES-LA.md` · implement
  `checkCompliance(layout) → violations[]` in shortfloor against **FAR only** · mirror it
  node-side so `harness.js` can assert on it · create `code-compliance` agent.
- **Deliverables:** rule spec · one working checker · one harness assertion · 1 agent.
- **Model:** sonnet + WebSearch (Task B research) / sonnet (checker). **Depends on:** Phase 2.
- **Note:** this is the phase the entire plan hinges on. It is also the smallest.

### Phase 4 — Design generation (extend) · *Week 3–4* · complexity **Medium**
- **Goal:** from 2 hard-coded schemes to an N-scheme registry.
- **Tasks:** create `module-packer` (spec first — its blueprint entry needs the §2 MODIFY
  updates) · refactor `CORE_OPTION` branches into a scheme registry · deterministic
  parameter sweep over `hash3` seeds · **determinism assertion in the harness** (same
  seed ⇒ byte-identical layout).
- **Deliverables:** scheme registry · N-option generation · determinism test.
- **Model:** sonnet/high (opus if it couples ≥3 constraints — blueprint §4.3 escalation).
- **Depends on:** Phase 1 + 2.

### Phase 5 — Validation (real) · *Week 4–5* · complexity **Medium**
- **Goal:** every generated option carries its violations.
- **Tasks:** extend `checkCompliance` to the full MVP rule set (zoning + egress +
  occupancy) · in-app violations panel per scheme · `program-auditor` extended with
  occupancy classification · replace the ⅓-width egress *soft rule* with a measured
  check and **state plainly where the massing fails**.
- **Deliverables:** violations panel · honest egress report on SAMPLE + case_all.
- **Model:** haiku (checks) / sonnet (UI + rules). **Depends on:** Phase 3 + 4.
- **Expect:** current schemes to *fail* egress. That is the deliverable, not a setback.

### Phase 6 — Optimization · *Week 5–7* · complexity **High**
- **Goal:** rank options; then improve them.
- **Tasks:** **move metrics from `replica3.js` into the app** (overlap, corridorΣ, core
  float/touch%, fill, violation count) · define a scoring function with *stated weights*
  (a taste call → user decides, D §3) · rank the N schemes · only then consider a local
  search loop · create `design-scorer` if and when the loop is real.
- **Deliverables:** in-app metrics · scored comparison table · ranked options.
- **Model:** sonnet/high. **Depends on:** Phase 4 + 5. **Risk:** the scoring weights are a
  research claim, not an engineering choice. Do not let an agent pick them.

### Phase R — Runtime AI · *deferred, next semester* · complexity **High**
- **Goal:** LLM at the edges, never in the kernel (§4).
- **Tasks:** `chat.html` → Claude API brief intake (NL → ProgramFormat, validated by
  `program-auditor` before it enters the pipeline) · scheme critique against
  `SCHEME-PARTI-RULES.md` · narrative report generation.
- **Hard constraint:** the layout kernel stays deterministic. An LLM may *propose* a
  program or *critique* an output. It may never place a module.
- **Depends on:** Phases 1–5 complete. **Explicitly out of current scope.**

---

## 8. Next 8 actions

> Eight, not seven: the depth-normalization edit flagged in `NEXA-ANALYSIS-PLAN.md` §0
> fact #5 is still open (see §1) and earns its own line rather than hiding inside a
> documentation task.

**Priority 1 — do these before any new feature work**

1. **Create `visual-verifier` + `program-auditor`** verbatim from `AGENT-ARCHITECTURE.md`
   §4.10 / §4.2. *Why first:* `program-planner` already ships with an acceptance gate
   pointing at an agent that does not exist. Every day this stands, the verification
   architecture is ceremonial.
2. **Close the P2 depth-normalization item — verify it or neutralize it.** It is inert
   on `compact` (default) but live on `pinwheel` (`:376`), and has never been verified on
   either. Two acceptable outcomes: (a) screenshot `?core=pinwheel` against `SAMPLE` +
   `case_all_v2`, confirm the E0-revert egress guard fires as intended, and record the
   result; or (b) delete the P2 block outright — nothing on the default path depends on
   it. **Do not leave it live-and-unverified for a third week.** Fix the stale `:368`
   "edge parti only" comment either way. *Requires action 1 (visual-verifier) first.*
3. **Write the missing 260708 session log** and re-anchor `AGENT-ARCHITECTURE.md`
   (function-name anchors; append the §1 delta; correct `CORE_OPTION` to
   compact/pinwheel/inset). *Why:* with no git, an unlogged day is a lost day, and a
   blueprint with wrong line numbers actively misroutes agents.
4. **Promote `260707-tools/` → `tools/`; delete `_handoff-test.html`.** Re-sync
   `replica3.js` to the compact/pinwheel schemes, *or* formally demote it to
   "screenshots are the only proof" and say so in the file header. *Why:* the metrics
   currently describe a layout that no longer exists.

**Priority 2**

5. **Run Task B** → `references/specs/CODE-RULES-LA.md` (zoning envelope + egress +
   occupancy only). One-shot research agent, sonnet + WebSearch.
6. **Rescue `SCHEME-PARTI-RULES.md` from the code comments.** The three parti schemes are
   the most valuable undocumented logic in the repo, and one of their two comment blocks
   is already wrong (`:368`). Writing this spec is also what forces action 2 to a decision.

**Priority 3**

7. **Prototype `checkCompliance(layout)` against FAR alone**, on SAMPLE. The smallest
   slice that proves the validation socket. Do this *before* Task B's rules land — the
   socket, not the rule count, is the risk.
8. **`references/` triage** into `specs/` · `case-studies/` · `archive/`; create
   `spec-guardian` and run its first drift audit.

**Deliberately not next:** YAML rule engine · RAG · `chat.html` → API · IFC/BIM ·
`performance-analyst` · module extraction refactor · `ui-panels` · `geo-interop`.
Each is either rejected (§4), gated on user approval (blueprint design-decision #6), or
has no trigger yet (F-MAINTENANCE: no agents without triggers).

---

## 9. Honest limits of this plan

- Week estimates assume the current cadence (roughly one substantial feature per working
  day). They are sequencing, not commitments.
- Phase 5 will likely show that both parti schemes fail a literal egress reading. The
  260707 HANDOFF already suspects this. Deciding what to do about it — fix the massing,
  or document the deviation as a research position — is a **user call**, and it is the
  most interesting decision on this roadmap.
- Task B's output quality is unverified until a licensed reading of LABC/LAMC confirms
  it. A `code-compliance` agent that cites rules confidently is more dangerous than no
  agent at all. Its definition must forbid the word "compliant."
- This plan does not merge with the blueprint's Phase-6 order — that is Task C.
