# 260703 Session Log

One-time Fable 5 session used to build the **agentops/ rule system** — externalizing judgment for future weaker-model sessions. No feature work.

## Deliverables

| File | What |
|---|---|
| `CLAUDE.md` (rewritten) | Thin router: danger rules, date-stamped current focus, routing table. Old version → `BACKUP/CLAUDE.md.bak-260703` |
| `agentops/A-DIAGNOSIS.md` | Top-3 harness failure modes (giant-HTML reads, unscoped searches, stale project map) + hard-rule fixes |
| `agentops/C-MODEL-DISPATCH.md` | Delegation protocol: commander-doesn't-descend, dispatch trio, report contract, escalation ladder, never self-verify |
| `agentops/D-JUDGMENT-RUBRICS.md` | When to escalate / call done / ask user / switch approach; quality floors; honest limits. Each with ✅/❌ example |
| `agentops/E-DELEGATION-TEMPLATES.md` | Fill-in prompts: search, implement, refactor, research, review |
| `agentops/F-MAINTENANCE.md` | Who may change what, backup rule, LESSONS.md format, compaction thresholds, 30-day drift check |
| `agentops/G-LETTER.md` | Orientation for new sessions + predicted decay modes and countermeasures |
| `agentops/ARCH-NOTES.md` | Old CLAUDE.md preserved verbatim under a status header (TPAC/53W53 visualizers now in `references/`) |

## Verification

- Fresh-context sonnet agent adversarial-reviewed all files: 6 findings (1 rule conflict, 1 overstated allowlist claim, 1 wrong path, 2 guess-required refs, 1 vague directive) — all fixed.
- All paths, model names, agent names verified against the live environment.
- Auto-memory updated: `project_agentops.md` + MEMORY.md index line.

## Open items

- Tile editor still dark-themed (carried over from 260625 log).
- Optional: add a wildcard permission for the headless-Edge screenshot command so it never prompts (needs user decision — current entries are literal strings from past runs).
