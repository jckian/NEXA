# Lessons Log

Format per F-MAINTENANCE.md: Trigger / Rule / Home.

## 260704 — Identical screenshots can hide working logic
Trigger: before/after screenshots were md5-identical after the program-interlock change; first hypothesis was "code not executing". Real cause: the swaps happened between same-category (then same-hue) programs, so the pixels never changed.
Rule: when verifying by screenshot, always test in the color mode with the FINEST distinction (Type, not Category), and when in doubt A/B the feature flag (P=0 vs P=on) and pixel-diff the two shots — byte-size or md5 equality is a signal to dig, not a verdict.
Home: D-JUDGMENT-RUBRICS §5 (quality floor, HTML row).

## 260707 — `& msedge --headless` returns before the PNG exists
Trigger: all day, agents' screenshot steps "failed" (no PNG), retried with fresh profiles and long sleeps; the last agent found the real cause — the `&` call operator returns immediately while Edge writes the file afterwards, leaving zombie processes and phantom failures. Cost: the single biggest wall-clock sink across 8 delegated tasks.
Rule: launch headless-Edge with `Start-Process -Wait` (plus fresh --user-data-dir per run); treat a missing PNG after -Wait as a real failure, not a timing issue. Delete the profile dir right after the shot and stop the http.server when verification ends — 260707 left 21 profiles (1.8 GB in %TEMP%) and a server running all day.
Home: G-LETTER item 3 (screenshot recipe) — PROMOTED 260707 with user OK (backup: BACKUP/G-LETTER.md.bak-260707).

## 260707 — Verification ceremony compounds across a task chain
Trigger: 6 sequential layout/generator tasks each re-ran the FULL harness matrix (grew 13→166 assertions), re-took 'before' screenshots, and re-derived handoff cases from scratch; later tasks spent more time re-verifying unchanged invariants than making their change. Task durations grew 10→33 min.
Rule: keep canonical baseline artifacts (before-shots, generated case texts, replica metrics) in the session scratchpad and tell the next agent to REUSE them; demand the full matrix only when the change touches the invariant being asserted — a resize that can't affect interlock doesn't need interlock re-measured from scratch.
Home: E-DELEGATION-TEMPLATES §2 (implementation template, context line).

## 260707 — Opus-everywhere burns the session cap mid-task
Trigger: two of eight delegated tasks died mid-run on the plan's session limit (resets hours later) and needed transcript-resume; both were Opus agents whose tool loops were dominated by mechanical verification (screenshot retries, harness re-runs).
Rule: reserve opus for the design/edit core; when a task is mostly mechanical verify loops, either split the verify tier to sonnet or explicitly size the brief smaller so an interrupt loses less.
Home: C-MODEL-DISPATCH Rules 4-5.

## 260712 — Root reorganization REVERTED: moving root HTML breaks live links
Trigger: user-requested cleanup moved root loose files into `NEXA/`/`VORO/`/`INDEX/`/`CHAT/`/`TEST/`; relative-path check was done only INSIDE the moved cluster (NEXA-site.html→logos), not for links pointing AT the moved files from elsewhere. User reported broken HTML links; everything was moved back to root and all doc edits restored from BACKUP/*.bak-260712 the same day.
Rule: before moving ANY root HTML, grep the remaining HTML/js for the moved filenames (inbound links: hrefs, fetch/window.open targets, bookmarks the user keeps outside the repo can't be grepped — ask); treat root-level position of the HTML apps as part of their API. G-LETTER item 2 already warned "the mess IS the version control — do not clean up without asking"; approval to reorganize does not equal proof that nothing links in.
Home: G-LETTER item 2 / CLAUDE.md danger section.
Still true after revert: `references/25_26 AT Studio.fig` (1.05 GB) remains deleted (Recycle Bin, user-approved, recoverable); the two `VORO-*.mp4` at root are MD5-identical; `UI_ClaudeDesign/` in the exclusion lists does not exist on disk; shortfloor is ~285 KB not 200 KB.

## 260704 — Headless-Edge shots can arrive late, not fail
Trigger: two parallel headless-Edge screenshots reported MISSING after 50 s, then appeared minutes later; 15 zombie msedge processes had accumulated.
Rule: launch headless-Edge shots one at a time with a distinct --user-data-dir each, poll up to ~80 s, and if a shot is missing, re-check for the file before relaunching; never kill msedge.exe broadly (the user's real browser may be open) — filter by --headless in the command line.
Home: G-LETTER item 3 (screenshot recipe).
