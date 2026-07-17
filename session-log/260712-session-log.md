# 260712 Session Log

## Root reorganization — DONE, then REVERTED same session

1. **Reorg (user-approved plan):** moved root loose files into new folders — `NEXA/` (plans, site, logos, 2 mp4), `VORO/` (2 mp4 + pdf), `INDEX/` (index.html, index2.html), `CHAT/` (chat.html), `TEST/` (structure-zone-test.html, _handoff-test.html); updated paths in CLAUDE.md + agentops + agent defs (backups taken as `BACKUP/*.bak-260712`).
2. **Revert (user reported broken HTML links):** all files moved back to root, the five folders deleted, all doc edits restored from the `.bak-260712` backups. Root is byte-identical to the pre-reorg state for every moved file (moves, not copies; contents never edited).

**Cause noted in agentops/LESSONS.md (260712 entry):** relative links were only checked inside the moved cluster, not inbound links pointing at the moved files. Root-level position of the HTML apps is effectively part of their API.

## Still true after revert

- `references/25_26 AT Studio.fig` (1.05 GB Figma) **deleted to Recycle Bin** (user-approved, recoverable). references/ ≈ 48 MB now.
- `VORO-demo.mp4` and `VORO-video.mp4` at root are MD5-identical (user chose to keep both).
- `UI_ClaudeDesign/` listed in CLAUDE.md exclusions does not exist on disk.
- `program-massing-shortfloor.html` is ~285 KB (docs say 200–204 KB).
- `my-video/`, `RENDER/`, `forVideo/` untouched throughout.

The `.bak-260712` files in BACKUP/ are now redundant copies of the live docs — kept per convention (one backup per file per day).

## Second attempt — link-aware VORO move (SUCCESS, verified)

User re-requested: move the VORO-era HTML trio (chat.html, index.html, index2.html) into `VORO/`, this time keeping links working.

1. **Link map first.** Inbound: only the trio link to each other (`chat→index`, `index→chat`, `index2→chat`) — same-dir relative, safe when moved together; all other mentions (references/*-diagram.html, program-input.html) are comments only. Outbound: index.html + index2.html fetch `references/*.txt`, `references/dfd_connector.json` and play `RENDER/*.mp4`; chat.html is fully self-contained.
2. **Backups:** `BACKUP/{index,index2,chat}.html.bak-260712-preVORO`.
3. **Move:** trio → `VORO/`.
4. **Path rewrite** inside VORO/index.html (`references/` ×25, `RENDER/` ×4) and VORO/index2.html (×13, ×4) → `../references/`, `../RENDER/`.
5. **Verified via local node server (8099) + headless Edge screenshots:** all three pages render fully — index (TPAC massing + 162-entry program list), index2 (massing), chat (precedent picker). Server log shows zero 404 except pre-existing favicon.ico. Server stopped, Edge profiles cleaned.
6. **Docs updated** (same files as morning, backups already exist from today): CLAUDE.md (never-read paths → `VORO/...`, exclusions += `VORO/`, note about rewritten fetch prefixes), A-DIAGNOSIS, AGENT-ARCHITECTURE, both program-planner defs, program-auditor, module-packer.

⚠️ If the trio ever moves again, the `../references/` and `../RENDER/` prefixes inside VORO/index*.html must be rewritten to match the new depth.

## Boot-state snapshot for future rollback

`BACKUP/260712-BOOT-STATE-RESTORE.md` — full record of the pre-change (boot) state: root file listing with sizes, folder list, complete link map (chat↔index↔index2, index*→references/RENDER), what changed today, which byte-exact backups cover it, and a paste-ready PowerShell block that restores everything (plus optional Recycle-Bin recovery of the 1.05 GB .fig).

## VORO media consolidated

`VORO-demo.mp4`, `VORO-video.mp4`, `VORO-intro-deck.pdf` (≈107 MB) moved from root into `VORO/`. Verified referenced by nothing (docs only). A-DIAGNOSIS §2 updated. To restore boot state these three move back to root (the restore doc's 5b guard already covers not deleting a non-empty VORO/).

## Brand rename VORO → NEXA on active platforms

- `program-input.html:343` brand-name span "Voro" → "NEXA" (top-left mark; CSS uppercases). shortfloor already showed only NEXA-logo.png — no change needed.
- ⚠️ Dependency: `program-input.html` uses `NEXA-logo-mask.png` and `program-massing-shortfloor.html` uses `NEXA-logo.png`, both root-relative. If NEXA-* files are ever folded into a `NEXA/` folder, these two PNGs must stay at root or both HTML paths must be rewritten.

## MODULE-TOOLS consolidation (verified)

Five root HTML tools checked for links to program-input.html / program-massing-shortfloor.html — none found in either direction (current shortfloor's old "→ full-height" link to program-massing.html survives only in BACKUP copies). Internal chain `program-massing → massing-composer → program-tile-editor` is same-dir relative, so all five moved together into `MODULE-TOOLS/`: program-massing.html, massing-composer.html, program-tile-editor.html, dfd-unit-diagram.html, structure-zone-test.html. All are self-contained (Google-Fonts CDN only; references/ mentions are comments).

**Verified via server + headless-Edge screenshots: all five render fully in the new location** (massing scenes, tile grid, DfD frame, zone classifier). Docs updated: CLAUDE.md (Current focus re-stamped 260712 — active pair is now program-input → shortfloor; MODULE-TOOLS added to search scope), A-DIAGNOSIS (tile-editor path), AGENT-ARCHITECTURE (dfd-unit-diagram paths ×2), boot-state restore doc (steps 5c-2 + §3 rows E–G).

Noticed: `MODULE-TOOLS/structure-zone-test.html` top-left still says "VORO" (its own header, not yet renamed — flag for the user).

## TEST/ and NEXA/ consolidation (verified)

- `_handoff-test.html` → `TEST/` — judged worth keeping: it seeds localStorage with a canned MIX program and redirects into shortfloor, i.e. a one-click end-to-end handoff test (the 260707 verification pipeline used exactly this pattern). Its redirect was rewritten to `../program-massing-shortfloor.html` and **verified end-to-end via headless Edge: the redirect lands on shortfloor and renders the MIX massing (12,001 m², 10F, code-check panel live)**.
- `NEXA-ANALYSIS-PLAN.md` + `NEXA-EXECUTION-PLAN.md` → `NEXA/` — doc-only, no runtime links; cross-mentions in session-logs/specs are textual. (Note: ANALYSIS-PLAN line 323 says EXECUTION-PLAN is "at project root" — now NEXA/, harmless staleness.)
- Boot-state restore doc: §3 rows H–I + step 5c-3 added (moves both back and reverts the redirect line).

## NEXA site + logos consolidated (verified)

`NEXA-site.html` + `NEXA-logo.png` + `NEXA-logo-mask.png` → `NEXA/` (site's 3 same-dir refs untouched). Active platforms updated: `program-input.html:60` mask url and `program-massing-shortfloor.html:78` img src now point to `NEXA/NEXA-logo...`. **Headless-Edge verified all three: input brand mark (mask) renders, shortfloor logo renders, NEXA-site header + hero render.** Restore doc: row J + step 5c-4. The earlier "logos must stay at root" warning in this log is superseded by this change.

## NEXA videos consolidated — root reorganization COMPLETE

`260707_NEXA_DEMO.mp4` + `assembly_animation_v5_lineart.mp4` (≈118 MB, zero references) → `NEXA/`. Restore doc row K + 5c-4 extended.

**Final root: 5 files** — program-input.html, program-massing-shortfloor.html, CLAUDE.md, package.json, package-lock.json. Project folders: NEXA/ (site, logos, plans, videos), VORO/ (retired trio + media), MODULE-TOOLS/ (5 module-system tools), TEST/ (_handoff-test.html). Every move was link-mapped first and screenshot-verified after.

Memory updated: `project_folder_reorg_260712.md` added; `project_module_platforms.md` re-pointed to MODULE-TOOLS/.

Open item: `MODULE-TOOLS/structure-zone-test.html` top-left header still says "VORO".

## NEXA Intel layer — N0 design docs (new feature planned + approved)

User requested a site-program prediction feature (current need + future forecast),
seeded by an external 12-agent "AI Design Intelligence Platform" proposal. Plan agreed:

- **Architecture:** collapsed to a document pipeline (M1 SITE-DOSSIER, M2 SITE-TIMELINE
  temporal knowledge graph, M3 PROGRAM-TRANSITION-DB, M4 FORECAST scenario cards →
  ProgramFormat drafts, M5 wizard "Site Forecast" entry). Existing platform additive-only;
  no orchestrator; deterministic kernel untouched.
- **User decisions (260712):** existing features all stay, feature is added on top;
  pilot site = **The City Market of Los Angeles** (Fashion District, DTLA);
  **offline-first — no runtime API until the whole system is built**;
  ⚠️ "the platform" from now on = root NEXA pair; **`VORO/` is frozen, never modify**.
- **N0 delivered:** `NEXA/intel/INTEL-ARCHITECTURE.md` (modules, constraints C1–C6,
  12-agent traceability, upgrade path), `INTEL-DATA.md` (schemas, confidence tagging,
  City Market source inventory, file layout), `INTEL-ROADMAP.md` (N1 dossier+timeline →
  N2 transition DB → N3 forecast + wizard integration → N4 optional timeline page;
  done-criteria + risk register).
- Next: N1 — one-shot research task for the City Market dossier + timeline.

## NEXA Intel layer — N1→N3 BUILT AND VERIFIED (same session)

Backups first: `BACKUP/program-input.html.bak-260712`, `BACKUP/program-massing-shortfloor.html.bak-260712`.

**N1 (research agent, sonnet + WebSearch):** `NEXA/intel/data/site-citymarket.{js,md}` —
dossier (8 sections, confidence-tagged, honest nulls) + temporal knowledge graph
(23 nodes / 23 edges). Spine: produce market 1909–2009 → City Market South creative
reuse 2014–2024 → entitled master plan 2026–2049 (est). Known gaps flagged in the .md:
APN/ZIMAS unverified, EIR pages 403'd (zoning facts are `reported`), DTLA 2040 IX2 vs
project entitlement unresolved, no confirmed groundbreaking.

**N2 (main session):** `NEXA/intel/data/transitions.{js,md}` — 19 transitions,
15 from-types, every one with basis + cited example; likelihoods are tiers, no fake
percentages; typeMap → ProgramFormat vocabulary included.

**N3a (M4 forecast):** `NEXA/intel/data/scenarios-citymarket.{js,md}` +
`NEXA/intel/prompts/260712-scenarios-citymarket.md` (generation record w/ input MD5s).
4 scenarios: A entitled housing-led build-out (2035) · B education campus (2040) ·
C event & culture district (2038) · D prolonged interim (2032). Drafts are study slices
(4,109–9,607 m² GFA) in the handoff-test vocabulary, 3 cores + circulation per level.
Mechanical validation (node script): grammar, category, ≥3 fire-stair cores/level,
|w·h−area|/area ≤10%, mix sums=1, level contiguity — ALL PASS.

**N3b (program-input.html):** additive only — `<title>` Voro→NEXA; CSS block; forecast
link under the wizard hint (hidden unless intel data loads); full-screen overlay
(timeline strip + scenario cards + apply); 3 `<script src="NEXA/intel/data/*.js">` tags
(missing file = dormant feature); `initSiteForecast()` IIFE at script end reusing
validateLine/enterReview/saveDraft; URL hooks `?forecast=1` (open) and `?forecast=<id>`
(apply). New `TEST/_forecast-test.html` (scenario → localStorage → shortfloor, same
pattern as _handoff-test).

**N3c verified (node server 8099 + headless Edge, 5 shots, all read):**
1. wizard step 1 intact, forecast link visible — manual path regression OK;
2. `?forecast=1` overlay: timeline (future node dashed) + 4 cards w/ mix bars render;
3. `?forecast=A` → review stage, GFA 9,607 m² = validator's number, B1…L7, footer live;
4. `TEST/_forecast-test.html?id=A` → shortfloor massing renders, stats 9,607 m² / 9 floors,
   code-check 2 advisory issues (S4 2/3 cores, E-7 15.5/15.24 m);
5. baseline `_handoff-test.html` (MIX) shows 7 issues on the same panel → the 2 issues are
   normal advisory behavior, not a feature regression.
Server stopped, Edge profiles cleaned.

⚠️ Path coupling: `program-input.html` and `TEST/_forecast-test.html` reference
`NEXA/intel/data/*.js` relatively — if intel data files or the root HTML move, rewrite.

**Forecast overlay layout, revision 1 (superseded):** one arrow-connected horizontal band,
history + scenarios in a single line, edge-to-edge.

**Revision 2 (final, user request):** scenarios are *parallel options*, not a further
sequence, so the band forks:
- `#fc-spine` — observed program succession only, horizontal, arrow-connected. **Future-epoch
  program nodes are now filtered out** (`n.epoch !== 'future'`): the 2026–2049 entitled
  build-out node duplicated Scenario A and its years overlapped the scenario horizons.
- `#fc-fork` — dashed stem + vertical rail (CSS `::before`/`::after`).
- `#fc-options` — the four scenarios stacked vertically, left-aligned, horizon-sorted
  (D 2032 / A 2035 / C 2038 / B 2040), each a wide 3-column card
  (meta+name · note · mix bar+legend+apply).
- Band flush left (no inset), 24px right padding only to keep cards off the scrollbar.
- Two layout bugs found and fixed by screenshot: spine nodes stretched full band height
  (`align-items: stretch` → `center`), and cards overflowed the viewport (a plain `1fr`
  track takes the paragraph's min-content width — now `minmax(0, …)` on every track).
Verified at 1920px and 1500px: fork reads as a branch, no clipping, no page-level h-scroll.
