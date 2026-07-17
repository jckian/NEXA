# A — Harness Diagnosis (written by Fable 5, 2026-07-03)

Top three ways this environment wastes tokens, loses focus, or produces errors — with fixes. Every other agentops file assumes these.

## 1. Giant single-file HTMLs read whole (worst token leak)

The main apps are single HTML files, some enormous:

| File | Size | Full-read cost |
|---|---|---|
| VORO/index.html | ~1.1 MB | ~300k tokens — exceeds the entire context window |
| VORO/index2.html | ~850 KB | ~230k tokens — exceeds the window |
| program-massing-shortfloor.html | ~285 KB | ~75k tokens — over a quarter of the window in one call |
| MODULE-TOOLS/program-tile-editor.html | ~65 KB | ~18k tokens |

One careless `Read` of program-massing-shortfloor.html costs a quarter of the context. Two or three re-reads while iterating on a bug and the session is cognitively dead: the model starts forgetting the original task.

**Fix (hard rules):**
- Never `Read` a file over 100 KB without `offset`+`limit`. Check size first if unsure (`ls -la`, or the table above).
- Locate before reading: `Grep` for the function/id/string to get line numbers, then Read a window of ±60 lines around the hit.
- Work needing many reads across a big file goes to a subagent (C-MODEL-DISPATCH.md); the main conversation receives only a diff summary + file:line references.
- After 2 read-edit-read cycles on the same big file, stop and switch to targeted Grep windows — re-reading whole regions "to be sure" is the leak.

## 2. Unscoped searches sweep junk directories

`Glob **/*.md` from the repo root returns 600+ files — almost all from `my-video/node_modules/`. Similar traps: `node_modules/`, `RENDER/`, `forVideo/` (videos), `BACKUP/` (old copies), `UIUX/`, `VORO/` (retired 1.1 MB + 850 KB HTML plus ~110 MB of `VORO-*.mp4/pdf` binaries, all moved from root 260712).

**Fix (hard rules):**
- Never search with a bare `**/*` pattern from the repo root.
- Scope every Glob/Grep to the real working dirs: `pythonFiles/`, `references/`, `agentops/`, `session-log/`, `site/`, `structure-generator/`, `massing-model-generator/`, or root-level `*.html` by explicit name.
- `BACKUP/` is the project's version history (there is no git). Search it only when explicitly hunting an old version.

## 3. Stale project map — the docs lied about what was current

Before 2026-07-03, CLAUDE.md documented `tpac-program-diagram.html` and `53w53-program-diagram.html` as the two main root-level visualizers. Both had in fact been retired to `references/`. The actually-active files (program-tile-editor.html, massing-composer.html, program-massing-shortfloor.html) were not mentioned at all. Sessions either re-derived project state from scratch (slow) or trusted the stale map (wrong).

**Fix (institutional, not one-off):**
- CLAUDE.md now has a date-stamped "Current focus" section and routes detail elsewhere. If its date is >30 days old, verify against the newest `session-log/YYMMDD-session-log.md` before trusting it.
- Session-end ritual (F-MAINTENANCE.md): append what changed to a session log; if the focus shifted, update the CLAUDE.md focus section with a new date stamp.
- Architecture details for the retired visualizers live in agentops/ARCH-NOTES.md marked historical — verify a file exists before acting on its description.
