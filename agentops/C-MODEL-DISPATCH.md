# C — Model Dispatch Protocol

How the main conversation (the "commander") uses subagents. Applies to every session regardless of which model is driving.

## Available models & agents (verified 2026-07-03)

- `Agent` tool `model` values usable here: `haiku`, `sonnet`, `opus`. (`fable` existed only for the one 2026-07-03 session; do not request it.)
- There is **no per-call effort parameter** on the Agent tool. Model and reasoning effort can only be preset in an agent definition (`.claude/agents/*.md` frontmatter). If a task needs non-default effort, either pick a stronger model or add a project agent definition — do not invent an `effort` argument.
- Project agents: `3d-arch-diagram-gen` (sonnet, Three.js/layout domain expert with its own memory in `.claude/agent-memory/`).
- Built-ins: `Explore` (read-only search), `Plan` (implementation planning), `general-purpose` (multi-step work), `claude-code-guide` (questions about Claude Code / Claude API — use it instead of answering from memory), `fork` (inherits the full conversation context — use when the subtask needs everything you currently know).
- Model facts (IDs, pricing, limits) go stale. When they matter, ask `claude-code-guide` or load the `claude-api` skill — never answer from training memory.

## Rule 1 — The commander does not descend

The main conversation NEVER does these itself; it delegates and receives conclusions:
- Reading >3 files in a row, or any file >100 KB, to answer one question → `Explore`
- Repo-wide sweeps ("find every place that…") → `Explore`
- Web research → `general-purpose` (or `claude-code-guide` for Claude-related questions)
- Batch edits (the same change in >3 places, or generating >100 lines of data) → `general-purpose`

Exception: a single targeted Read/Edit of a known small file is cheaper inline than a delegation round-trip — do those directly.

## Rule 2 — Every delegation carries three things

1. **Goal + why** — what to do and how it serves the larger task (so the agent can make sane micro-decisions).
2. **Acceptance criteria** — conditions checkable by someone other than the author: a command that must pass, a string that must appear, a count that must match.
3. **Report format** — what comes back and its maximum length.

Templates with these slots: E-DELEGATION-TEMPLATES.md. A delegation missing any of the three produces vague results; that is the commander's fault, not the agent's.

## Rule 3 — Report contract

- Subagents return conclusions + `file:line` references, ≤30 lines.
- Long outputs (generated data, full reviews, research notes) are written to a file — scratchpad for throwaways, `agentops/reports/` for keepers (create the directory if absent) — and the PATH is returned.
- Raw file contents never travel back into the main conversation.

## Rule 4 — Default assignments

| Task type | Agent | Model |
|---|---|---|
| Quick lookup ("where is X defined") | Explore | haiku |
| Multi-location codebase search | Explore | sonnet |
| Implementation, batch edits | general-purpose | sonnet |
| 3D layout / massing / Three.js domain work | 3d-arch-diagram-gen | (its default) |
| Architecture planning, coupled-constraint design | Plan | opus |
| Code/document review | general-purpose | sonnet; opus if the change is load-bearing |
| Claude Code / API questions | claude-code-guide | (its default) |
| Validate/audit a program .txt (grammar, area sums, cores, ratio) | program-auditor | haiku |
| Layout / packing / corridor / core / porosity (computeLayout) | module-packer | sonnet |
| Independent screenshot acceptance of any visual change | visual-verifier | sonnet |

## Rule 5 — Escalation & demotion ladder

- haiku gets it wrong once → redo on sonnet immediately. Do not debug haiku output.
- sonnet fails the SAME subtask twice → escalate to opus **with the full failure trail**: what was tried, exact error text, why each attempt was judged failed. Escalating without the trail wastes the stronger model on rediscovery.
- Once a stronger model has solved the pattern, demote: batch-apply the now-known recipe with sonnet/haiku.
- Hard cap: two retry rounds per approach on the same thing. After that it is a wrong-approach signal (D-JUDGMENT-RUBRICS §4) — change approach or ask the user. Never loop a third time.

## Rule 6 — Verification is never self-verification

Whoever produced the work does not sign off on it:
- Files written → a fresh-context agent (or at minimum a fresh Read in the main conversation) reads them back against the acceptance criteria.
- Code → run it: py_compile + a real run for Python; load + headless screenshot for HTML (quality floor in D §5).
- High-stakes judgment calls → a second opinion from an independent agent, or generate 2–3 candidate answers and have a judge agent pick one with reasons.

Cost guide: read-back is cheap — always do it. Second opinions are for decisions that are expensive to reverse.
