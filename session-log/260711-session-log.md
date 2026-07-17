# 260711 — Session Log

## 01:25 — program-massing-shortfloor.html RESTORED to 260710 16:44 (user request)

- User: 備份現在的檔案，回復到 `program-massing-shortfloor-260710-preInputSource.html`（260710 16:44）。
- Discarded state backed up first: `BACKUP/program-massing-shortfloor-260711-preRestore444.html` (296,702 B). Restore verified byte-identical to the 16:44 backup with `cmp`.
- The 16:44 baseline the file now equals: everything through 260710 Round 10's COMPACT/LEGACY auto-toilet base (single-ratio proxy) — i.e. code rules (E-1…E-9/X-1/S4), 3rd+ cores + E-7 spine, rebalance, OL-driven shaft extent, Program Mode palette, embedded extras, auto-toilets on compact/centre.

### Rolled back by the restore (all recoverable — per-round backups + `preRestore444`)

| Feature (260710 round) | Backup that still holds it |
|---|---|
| Program source auto-select + "Program source" stats row + cross-tab `storage` live-follow (8c) | preRestore444 / preCorrTouch |
| Corridor minimal-touch — never swallow a shaft's full width (8e) | preRestore444 / prePinwheelRevert |
| SHORT-floor corridor excludes SHORT zones (8f) | preRestore444 / prePinwheelRevert |
| Pinwheel auto-toilet REVERT (8g — the concurrent session's post-16:44 pinwheel toilets are also absent from 16:44, so this stays effectively "reverted") | n/a |
| CPC Table 422.1 per-group toilet sizing + §J.5 proportions (8h) | preRestore444 / (pre-state: preToiletCode) |

### Still in effect (different files, untouched by the restore)

- `program-input.html` Round 8b fixes: Build commits open inline/add forms, dirty raw text is applied-or-blocks with visible errors, `programInputDraft` restore on load, "↺ start over" button.
- Session-log entries for all of the above: `260710-session-log.md` Rounds 8a–8i.

### Known traps re-opened by the restore (next session, read before debugging "input 沒反應")

1. **Massing reads wizard data ONLY via `?src=input`** — double-clicking the HTML shows the built-in SAMPLE again. The input page's "Build massing →" still works (it appends the param itself). The diagnosis and fix live in 260710 Round 8c if the user wants it back.
2. An open massing tab does not auto-update when Build is pressed in another tab (no `storage` listener at 16:44).
3. Toilets are back to the near-square `1 WC/40 occ` proxy — the CPC 422.1 implementation (with R-floors exempt, M/F clusters, 1:1.5–1:2 proportions) is complete and verified inside `preRestore444` if it should be re-landed.

### Process note

- This session ran CONCURRENTLY with another session editing the same file on 260710 (its Rounds 9–10). After this restore, that session's post-16:44 pinwheel work is gone from the working file too — coordinate before either side re-lands parked features. F-MAINTENANCE's backup-per-round convention made the restore trivial; keep it up.

## 23:44 — Harness overhead audit + cleanup (no app-code changes)

User asked why sessions felt slow / token-heavy and whether earlier Fable-era harness rules were the cause. Audited everything, then applied user-approved fixes. **The agentops system itself was NOT the problem** — CLAUDE.md (3.4 KB thin router), agentops/ files (4–8 KB, lazy-loaded), and memory index are all lean and were left untouched.

### Diagnosis (measured, not guessed)

| Suspect | Verdict |
|---|---|
| `"model": "claude-fable-5[1m]"` (1M context) | **Biggest latency factor** late in long sessions (no compaction → ever-growing prompt; >200K tokens also bills higher). User chose to KEEP it. Revisit at `~/.claude/settings.json` → `"model"` if slowness persists. |
| Toast Stop/Notification hooks | NOT a problem — measured 0.26 s per fire. Left as-is. |
| Permission-prompt waits | Real cost. Old allowlists were ~90% dead one-off rules (absolute paths / inline scripts that never re-match), so common ops re-prompted every session. |
| Global design skills + fat agent description | ~600 tokens injected into every request's system prompt. |
| agentops/, CLAUDE.md, memory, MCP config | All healthy. No local MCP servers; `~/.claude.json` a normal 58 KB. |

### Changes applied (all config — zero behavior change to the apps)

1. **`.claude/agents/3d-arch-diagram-gen.md`** — frontmatter description trimmed ~1.9 KB → ~0.5 KB (3 embedded `<example>` blocks → one sentence + inline examples). Agent body + agent-memory untouched. Aligns with the refresh already planned in AGENT-ARCHITECTURE.md §4.6.
2. **Project `.claude/settings.json`** — now 6 read-only rules chosen from a 50-transcript frequency scan: `Bash(node --check *)` (91 uses), `PowerShell(Get-ChildItem *)`, `PowerShell(Get-Process *)`, `PowerShell(Get-CimInstance Win32_Process *)`, `PowerShell(Test-Path *)`, `PowerShell(Get-Content *)`. Deliberately NOT allowed: curl (network), awk (can `system()`), Start-Process / http.server — so the screenshot-verification pipeline still prompts once per session; user declined a blanket grant.
3. **Project `.claude/settings.local.json`** — pruned ~67 → 21 rules; kept only generic ones (`node *`, `npm run *`, http.server ports, localhost curls, Read paths, WebFetch domains).
4. **User-level `~/.claude/settings.json`** — pruned 28 → 10 rules (dropped env probes, exact ffprobe/export-deck one-offs, grep/ls/sort forms that are auto-allowed anyway). model/hooks untouched.
5. **Global skills** — `banner-design`, `brand`, `design-system` moved to `~/.claude/skills-disabled/` (move back to restore). Kept: design, slides, ui-styling, ui-ux-pro-max, find-skills.
6. **Notion connector** disconnected mid-session (user action via /mcp).

Final verification: all 3 settings JSONs valid, zero cross-file duplicate rules (user 10 / project 6 / local 21), net permission set unchanged by the dedupe, agent frontmatter + skills folders + hook scripts intact.

### Notes for next session

- **All of this takes effect from the NEXT session** — system prompt and settings are assembled at session start.
- Harness self-modification guard exists: the auto-mode classifier blocks Claude writing its own permission `allow` rules until the user names the specific grants. Expected behavior, not a bug.
- Remaining levers if slowness returns, in order: drop `[1m]` from the model setting; disable more claude.ai connectors (Google Drive 8 tools / Indeed 4 still attached, ~200 tokens); ui-ux-pro-max has the fattest remaining skill description (~240 tokens) if ever unused.

## 23:5x — Agent roster vs. full-workflow needs (handoff prep for a second account)

User asked which agents the full HTML workflow (program .txt → massing → structure → export) actually uses. Audit against AGENT-ARCHITECTURE.md:

**Exist today (3):** `program-planner` (stage 1: author/rebalance program schedules), `structure-frame` (stage 4: columns/transfer/girders/HYBRID rules), `3d-arch-diagram-gen` (stage 6: scene/camera/materials — description trimmed earlier today). Everything else currently rides on the built-ins (Explore / Plan / general-purpose) + the main session.

**Blueprint roles NOT built yet (7):** `program-auditor`, `module-packer`, `kit-of-parts`, `ui-panels`, `geo-interop`, `spec-guardian`, `visual-verifier`. Orchestration is deliberately NOT an agent (Phase 3 decision #1).

**The gap:** Phase 6 roadmap marks `visual-verifier`, `program-auditor`, `module-packer` as **Critical / "Now"**, but none were created since the blueprint landed 260703. Full specs are ready in AGENT-ARCHITECTURE.md §4.10 / §4.2 / §4.3; definitions belong in `.claude/agents/*.md` (drafts may exist in `agentops/agent-defs/` — check before writing from scratch).

**Handoff:** user is switching to a second account to build these. Prompt given to the user; the next session should read CLAUDE.md → this log → AGENT-ARCHITECTURE.md before creating anything, and follow F-MAINTENANCE for any agentops edits.

## 260712 02:2x — The three Critical/"Now" agents BUILT + verified (second account, answering the handoff above)

Read CLAUDE.md → this log's last two sections → AGENT-ARCHITECTURE.md Phase 4–6 first, per the handoff. `agentops/agent-defs/` held only program-planner + structure-frame drafts — **no drafts for these three**, so built from the §4 specs. No app code touched (program-massing-shortfloor.html left at its 01:25 restored state, deliberately).

### Built (`.claude/agents/`)

1. **`program-auditor.md`** — haiku. Read-only mechanical validator; 7-check checklist (syntax / category / area sums / ≥3 stairs / LONG-SHORT ratio / w×h vs area / core stacking) encoded verbatim; hard rule "compute with a script, never in-head".
2. **`visual-verifier.md`** — sonnet. Fresh-context screenshot acceptance officer; G-LETTER serve+headless-Edge recipe institutionalized; expectations-before-looking, "can't-tell" ⇒ second shot, blank canvas = FAIL. No memory (fresh context is the point).
3. **`module-packer.md`** — sonnet, memory:project. Owns computeLayout + helpers; module system + determinism (hash3, no Math.random); layout-shape contract + spec-first (MASSING-MODULE-LOGIC.md).

Frontmatter descriptions kept lean (one sentence + inline examples, no `<example>` blocks) per the 260711 23:44 slim-down policy.

### Verification (each agent's encoded procedure run live — see note on dispatch below)

- **program-auditor** — ran its 7-check script (node port) on `references/TPAC-PROGRAM-DISTRIBUTION.txt`: 162 records, floors −1..12, syntax PASS, category PASS, every floor ≥3 stairs (4 cores, 0 dupes), w×h all ≤10%, LONG/SHORT 88/12. Correctly FLAGGED total 56,220 m² vs 58,600 ref (−4.1% >2%). Bonus catch: the file's own AREA SUMMARY hand-totals ~62,042 — off from the exact line-sum, exactly what the auditor exists to surface. ✓
- **module-packer** — contract Q&A test: def claimed 6-field `{levels,coreShafts,floorRects,floorCorr,FW,FD}`, but live code (`program-massing-shortfloor.html:799`) returns **9** (+`zMid,progAdj,moves`); AGENT-ARCH §4.3 is stale too. Fixed the def to mark the 6 as the frozen contract and the extras as "don't strip, always grep the real shape". ✓ (verify-not-self-verify caught a real defect → fixed to pass)
- **visual-verifier** — served repo via node, headless-Edge shot of shortfloor (virtual-time-budget 25000), Read the 221 KB PNG. All 3 pre-set expectations PASS: non-blank massing on iso grid; stacked volumes; full 4-color palette (blue Private / orange Public+SHORT / yellow Circulation / dark-blue Core, legend matches). STATISTICS panel built (GFA 12,736 m², 8F, SHORT L1–L2, 4 exit shafts, code-check Clear). ACCEPTED. ✓

Note: new `.claude/agents/*.md` are **not dispatchable until next session** (settings/agents assemble at session start — 260711 23:44 note). So each agent was verified by executing its *encoded procedure* inline, which is the real acceptance. First actual `subagent_type` dispatch of these will be next session.

### Routing table change (F-MAINTENANCE followed)

- Backed up `agentops/C-MODEL-DISPATCH.md` + this log → `BACKUP/*.bak-260712`.
- Added 3 rows to **C Rule 4** table (permitted without asking per F-MAINTENANCE): program-auditor/haiku, module-packer/sonnet, visual-verifier/sonnet.
- AGENT-ARCHITECTURE §5 routing table already listed all three — left unchanged.

### Environment facts worth knowing (not acted on, flagged for user)

- **Python is not usable on PATH** — only the WindowsApps Store stubs (`python.exe`/`py.exe` → exit 49 "not found"). Node IS available (`C:\Program Files\nodejs`). Ran the audit + a minimal static server in node instead. G-LETTER's recipe assumes `py -m http.server 8099`; a node fallback is needed. **Did NOT edit G-LETTER** (F-MAINTENANCE requires asking first) — surfacing here for the user to decide. Same applies to `pythonFiles/` sim if it's run this session.
