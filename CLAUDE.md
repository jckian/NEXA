# CLAUDE.md

SCI-Arc Spring 2026 research: agent-based distribution of architectural program spaces, visualized as single-file Three.js HTML apps plus a Python simulation. Case studies: OMA TPAC, Jean Nouvel 53W53. **Now a public git repo** — `jckian/NEXA` (pushed 260717, MIT). `BACKUP/` still holds old versions by copy and is gitignored (along with `node_modules/`, `my-video/`, `RENDER/`, `forVideo/`, `VORO/`, `fileTransfer/`). Commit only when the user asks.

## ⚠️ Before touching files

- **Never fully Read:** `VORO/index.html` (1.1 MB), `VORO/index2.html` (850 KB), `program-massing-shortfloor.html` (285 KB). Grep for the target first, then Read a ±60-line window. Any file >100 KB requires offset+limit.
- **Never search unscoped:** no bare `**/*` globs from root. Exclude `node_modules/`, `my-video/`, `RENDER/`, `forVideo/`, `BACKUP/`, `UIUX/`, `VORO/`. Search only `pythonFiles/`, `references/`, `agentops/`, `session-log/`, `site/`, `structure-generator/`, `massing-model-generator/`, `MODULE-TOOLS/`, or root `*.html` by name.
- Retired VORO-era pages live in `VORO/` (index.html, index2.html, chat.html — moved 260712, internal fetch paths rewritten to `../references/`, `../RENDER/`). If they are ever moved again, those prefixes must be rewritten to match.
- **Bulk work goes to subagents.** The main conversation reads conclusions, not raw file dumps → `agentops/C-MODEL-DISPATCH.md`.

## Current focus (updated 260712 — if this date is >30 days old, verify against the newest session-log before trusting)

- Active platforms: `program-input.html` (wizard) → `program-massing-shortfloor.html` (visualizer), handoff via localStorage. Branding is NEXA (renamed from VORO 260712).
- Module-system dev tools (8'-6" / 1:2 domino) moved to `MODULE-TOOLS/` 260712: `program-tile-editor.html`, `massing-composer.html`, `program-massing.html`, `dfd-unit-diagram.html`, `structure-zone-test.html` — self-contained, verified working there.
- Module logic spec: `references/MASSING-MODULE-LOGIC.md`; program-to-module sizing: `references/PROGRAM-MODULE-AREA-TABLE.md`.
- Site Forecast intel layer (260712–13): design docs + data in `NEXA/intel/` (INTEL-*.md, data/*.js — 2 sites); entry in program-input.html (`?site=<key>` / `?forecast=1|<id>` hooks); Site Scout GIS tool `NEXA/intel/site-scout.html` (`?addr=` hook, needs local server for LA layers); LLM offline-only, VORO/ frozen.
- FOAM (arch-shell) module is paused — fall through to FRAME.

## Routing

| Need | Read |
|---|---|
| Harness pitfalls & fixes | agentops/A-DIAGNOSIS.md |
| Delegation, model choice, escalation ladder | agentops/C-MODEL-DISPATCH.md |
| When to escalate / stop / ask / switch approach; done-criteria | agentops/D-JUDGMENT-RUBRICS.md |
| Delegation prompt templates | agentops/E-DELEGATION-TEMPLATES.md |
| How to update these files safely | agentops/F-MAINTENANCE.md |
| Accumulated lessons | agentops/LESSONS.md (create on first lesson) |
| Orientation letter for new sessions | agentops/G-LETTER.md |
| Agent ecosystem blueprint (roster, ownership, routing) | agentops/AGENT-ARCHITECTURE.md |
| Python sim & retired TPAC/53W53 visualizer architecture | agentops/ARCH-NOTES.md (historical — verify files exist before use) |
| Program data format spec + core rules | references/ProgramFormat.txt |
| Case-study program distributions | references/TPAC-PROGRAM-DISTRIBUTION.txt, references/53W53-PROGRAM-DISTRIBUTION.txt |
| Restroom sizing rules | references/RESTROOM-GUIDELINES.md |

## Conventions

- Program data format: `{type}/{area m2}/{level}/{category}/{w,h}` — curly braces are literal; full spec in references/ProgramFormat.txt.
- Python sim: `cd pythonFiles && python ProgramDeveloperEllipseBoundary.py`; requires `pythonFiles/fileTransfer/` (create if absent); deps `openai`, `numpy`; details in agentops/ARCH-NOTES.md.
- HTML apps: single-file, CDN Three.js — open directly in a browser, no build step. Verify every visual change with the local-server + headless-Edge screenshot pipeline (recipe: the "Verification is already cheap" item in agentops/G-LETTER.md; expect at most one permission prompt on first use per session).
- Session logs: `session-log/YYMMDD-session-log.md`, one per working day. Session start: skim the newest one. Session end: append what changed.
- Respond to the user in Traditional Chinese; keep code identifiers and file contents in English.
