# E — Delegation Prompt Templates

Copy, fill every ⟨slot⟩, delete unused lines. A delegation missing Goal / Acceptance / Report is malformed (C-MODEL-DISPATCH Rule 2). Recommended agent+model per type; override per C Rules 4–5.

## 1. Search / locate — Explore; haiku (single target) or sonnet (multi-location)

    Find ⟨what⟩ in ⟨scope: dirs/files⟩.
    Why: ⟨what the main task needs this for⟩.
    Known context: ⟨naming hints, related terms; exclude junk dirs per CLAUDE.md⟩.
    Acceptance: every hit listed; if zero hits, name the 3 next-likeliest places you checked.
    Report: file:line + one-line description per hit, ≤20 lines total. No file contents.

## 2. Implementation — general-purpose, sonnet

    Implement: ⟨change⟩ in ⟨file(s)⟩.
    Why: ⟨purpose within the larger task⟩.
    Context: ⟨relevant functions as file:line, constraints, conventions⟩. Do NOT touch ⟨files⟩.
    Steps if known: ⟨…⟩
    Acceptance: ⟨command that must pass / string that must appear / behavior visible in a screenshot⟩. Run the verification yourself before reporting.
    Report: what changed (file:line per edit), verification evidence (command output / screenshot path), anything noticed but not fixed. ≤30 lines.

## 3. Refactor — general-purpose, sonnet (opus if it spans coupled systems)

    Refactor: ⟨what⟩ from ⟨current shape⟩ to ⟨target shape⟩. Behavior must not change.
    Why: ⟨the concrete problem the current shape causes⟩.
    Invariants: ⟨behaviors/outputs that must be provably identical — e.g. same screenshot, same output.txt⟩.
    Acceptance: each invariant demonstrated before/after with the same command. If any invariant cannot be checked, STOP and report instead of proceeding.
    Report: diff summary by file + invariant evidence. ≤30 lines.

## 4. Research (web/docs) — general-purpose, sonnet; claude-code-guide for Claude/Anthropic topics

    Question: ⟨precise question, plus the decision it feeds⟩.
    Prior belief: ⟨what we currently think, to confirm or refute⟩.
    Acceptance: every claim carries a source (URL/doc); anything unsourced is marked UNVERIFIED; prefer primary sources; note publication dates.
    Report: answer first, then evidence bullets with sources. Long notes → write to ⟨path⟩ and return the path. ≤25 lines inline.

## 5. Review — general-purpose, sonnet (opus for load-bearing changes); ALWAYS fresh context, never the author

    Review ⟨files/diff⟩ against ⟨spec / acceptance criteria / rule files⟩.
    You did not write this. Hunt for reasons it fails, not confirmation it works.
    Check specifically: ⟨correctness concerns for this change — e.g. unit/coordinate assumptions, boundary cases, rule conflicts, paths that don't exist⟩.
    Acceptance: every issue has file:line + why it is wrong + a suggested fix; explicitly list what you verified clean.
    Report: issues ranked by severity, then the verified-clean list. ≤30 lines; full detail to ⟨path⟩ if longer.
