# 260706 Session Log

## LONG structure export — checkbox category picker + single-OBJ export

**Request:** the `exp-long` button only exported LONG program-massing solids; the LONG structural frame from `buildStructure` had no export path. Added a checkbox panel to pick structural categories (columns, girders, joists, slabs, roof, curtain wall, fins, core) and export the selection as one grouped OBJ.

**Implementation (`program-massing-shortfloor.html`):**
- CSS: `.struct-chk-grid`, `.struct-chk-btns`, `.btn.small` — minimal styling reusing existing panel tokens (border-dim, text-mid, var(--blue) accent-color on checkboxes).
- New `<div class="panel-section">` "LONG structure export" inserted right after the existing Export section: 8 checkboxes (2-col grid, default all checked) + `All`/`None` buttons + `#exp-long-struct` button.
- New `STRUCT_BUCKETS` array (8 entries, each `{key,label,match(type)}`) mapping `addStruct()` `type` strings to buckets, reusing `exportOBJ()` as-is with a new predicate.
- New `exportLongStructOBJ()`: reads checked buckets → `matchesSelection`; if `exportBoxes` has no `b.struct` records yet (last build wasn't `RENDER_MODE==='structure'`), temporarily switches mode, rebuilds, exports, restores mode, rebuilds again; filename `LONG-structure_all.obj` when all 8 picked, else `LONG-structure_{key+key…}.obj`; no-op with alert if zero picked.
- Wired `#exp-long-struct` click + `All`/`None` buttons next to the existing export wiring.

**Flag — label mismatch found during `addStruct(` audit:** the spec's "Fins" bucket assumed `type === 'fin'`, but the timber-frame builder (`frame()`, ~line 706 in the pre-edit file) actually tags every bar with one of three size labels: `"timber frame 8'-6\"×8'-6\""`, `"timber frame 17'×8'-6\""`, `"timber frame 8'-6\"×17'"` — never the literal string `'fin'`. Implemented the Fins bucket as `type.startsWith('timber frame')` instead of an exact match, and confirmed via the counting check (below) that this correctly captures all 1,560 fin/frame boxes with zero unmatched and zero double-matched records.

**Verification:**
- `node --check` on the extracted `type="module"` inline script — pass.
- Headless Edge screenshot (`?mode=structure`) — new panel section renders correctly (2-col checkboxes all checked, All/None, export button) once the left-panel is scrolled to it (panel has `overflow-y:auto`, section sits below the fold at default viewport height — same pre-existing panel behavior as other sections, not a regression).
- Console-error check via puppeteer-core (headless Edge, `page.on('console')`/`page.on('pageerror')`): zero JS errors/pageerrors. One `[error]` console line is a `favicon.ico` 404 — confirmed pre-existing/unrelated (browser auto-request, `curl` reproduces the same 404 independent of this page).
- Counting check (temporary `window.__DEBUG_EXPORT_BOXES__` hook, added then removed after use): with `?mode=structure`, total `b.struct` records = 2997; per-bucket counts col 82 / gird 466 / joist 88 / slab 67 / roof 222 / cw 510 / fin 1560 / core 2, summing to 2997; union-matched count = 2997; unmatched list = empty. Confirms all 8 buckets exactly partition the struct-box set (no gaps, no overlaps).

**Backup:** `BACKUP/program-massing-shortfloor.html.bak-260706` (written before any edit).

## Program-authoring wizard — `program-input.html` + shortfloor handoff hook

**Request:** shortfloor always opened with the built-in SAMPLE; wanted a guided front-stage — wizard Q&A → template-generated ProgramFormat draft → editable review with live validation → handoff via `localStorage` → visualizer builds from it.

**New file `program-input.html`** (visual language copied from `chat.html` — palette, noise-canvas shader, brand mark, step pips, `steps[]` wizard pattern; `chat.html` itself untouched):
- Wizard (4 steps, chips + inputs): building type (mixed-use/office/housing) → total GFA (numeric + quick chips) → floors above/basement (two numeric fields, defaults 8/2) → SHORT share (0%/~20%/~35%/~50%).
- Deterministic generator (`generateProgram`): per-floor recipe — basements get storage/mechanical/loading + cores; ground gets lobby/sales and display/toilets + cores; SHORT quota fills *consecutive* floors from L1 up with 100%-SHORT-vocabulary programs (guarantees >50% share, "concentrated not spread"); remaining upper floors get main-use (office / apartment mix / alternating blend for mixed-use) + cores; every floor gets exactly 3 cores (`fire stair & freight elevator core`, `fire stair & passenger elevator core a`/`b`) + one `circulation` line; a final uniform scale factor normalizes total area to the GFA target (±2%, effectively exact).
- Review stage: full-width editable `<textarea>`, revalidated on every `input` event by a validator that ports `parse()`'s line grammar plus the four classifier regexes (`isCore`, `isFreight`, `isShort`, `isCorridor`) verbatim from `program-massing-shortfloor.html`, each tagged `// copied from program-massing-shortfloor.html — keep in sync`. Side panel shows stats (total GFA, level range, LONG/SHORT % by area, per-floor SHORT-share flags) and a per-line list with LONG/SHORT/CORE/ERR badges; error lines (too few parts / NaN area / NaN level / unknown category) render red with a reason. `Build massing →` disabled while any error exists; on click writes `localStorage.setItem('programInputText', text)` and navigates to `program-massing-shortfloor.html?src=input`. `Skip → open visualizer` is a plain `<a href>`, no JS, no storage write.

**Shortfloor hook** (`program-massing-shortfloor.html`, in the URL-param startup block, ~line 1438): purely additive — if `?src=input` and `localStorage.programInputText` is non-empty, `loadText()` that text instead of `loadText(SAMPLE)`; otherwise unchanged. Storage key is never cleared. `parse`/`build`/`isShort`/panel UI untouched (confirmed by diff against the pre-edit backup — only these 3 lines differ).

**Core/freight spelling used:** `fire stair & freight elevator core`, `fire stair & passenger elevator core a`, `fire stair & passenger elevator core b` — matches the SAMPLE's `&` convention. Note: `isCore`/`isFreight` actually match on the substrings `fire stair`/`elevator`/`freight` alone, so `&` vs `and` makes no regex difference — `&` was chosen only for visual consistency with SAMPLE.

**Verification (puppeteer-core + local headless Edge, `py -m http.server 8099`):**
- `node --check` on both extracted inline scripts of `program-input.html` and the `type="module"` script of `program-massing-shortfloor.html` — all pass.
- Full wizard run (mixed-use / 12,000 m² / 8 above + 2 basement / ~35% SHORT): review stats — Total GFA 12,005 m² (within ±2% of 12,000), level range -2…7, LONG/SHORT 87%/13%, 2 SHORT floors (L1, L2) flagged >50%, zero error lines, Build enabled.
- Cross-check via `page.evaluate` re-parsing the same draft text with the same regexes independently: GFA 12,005, SHORT floors [1,2], LONG/SHORT 87.17%/12.83% — matches review-stage stats exactly.
- Click Build → navigated to `program-massing-shortfloor.html?src=input`; its own stats panel: Total GFA 12,005 m², Floors 10 (= 8 above + 2 basement), SHORT floors 2 (L2, L3 in shortfloor's own +1 display convention) — consistent with input. Zero console errors besides the pre-existing `favicon.ico` 404.
- Negative test: appended a malformed line (`{malformed line no area no level}`) — flagged red with an ERR badge, `Build massing` correctly disabled; removing it re-enabled the button.
- Regression: opened `program-massing-shortfloor.html` with no query params — SAMPLE loaded (Total GFA 14,272 m², 8 floors, 101 spaces, 3 SHORT floors L1–L3), identical to pre-edit behavior; `diff` against `BACKUP/program-massing-shortfloor.html.bak-260706b` shows only the 3-line hook changed.
- Screenshots (wizard step 1, review stage) saved to the session scratchpad.

**Backup:** `BACKUP/program-massing-shortfloor.html.bak-260706b` (written before this edit, distinct from the same-day `.bak-260706` from the structure-export work above).

### v2 — activity multi-select + per-floor card editor (same day, user design review)

**Request:** two revisions after user review. (1) The step-4 "SHORT share %" chips were internal jargon and contradicted the system philosophy (SHORT-ness derives from type names, never declared) — the v1 flag (~35% chip → 13% actual) proved the confusion. Replaced with a grouped ACTIVITY MULTI-SELECT. (2) The textarea-first review clashed with the wizard's visual language — replaced with a PER-FLOOR CARD EDITOR. Shortfloor untouched in v2 (hook from v1 unchanged, verified read-only).

**Wizard step 4 (rebuilt):** "What activities plug into the building?" — 15 toggle chips in 4 mono-labeled groups (Show & event: exhibition / event hall / showroom / pop-up; Learning: classroom / seminar / computer lab / project review; Wellness: yoga / pilates / fitness / meditation / recovery lounge; Social: coffee / lounge bar — every label verified against the copied isShort regex) + a Continue button; zero selections allowed (all-LONG building). Answered-history shows "6 activities" / "no activities".

**Generator (revised):** SHORT-share parameter dropped. Each selected activity emits preset lines (`ACTIVITY_DEFS`): areas mostly reused from the SAMPLE's own instances (exhibition gallery 268, event hall 241, showroom 214, pop-up retail 107×2, coffee shop 161, lounge bar 134), fitness 242 from the AREA-TABLE "gym" row, remaining Learning/Wellness types preset 90–134 m² (the AREA-TABLE had no rows for classroom/seminar/yoga/etc.). Activities pack sequentially onto consecutive floors from L1 up (`PACK_TARGET` 800 m² raw per floor → floor count falls out of the total activity budget); each SHORT floor holds only activities + cores/circulation, so its packable SHORT share is 100% — always above the 0.5 threshold. Remaining floors main-use as v1; uniform scale to GFA target.

**Review stage (rebuilt as card editor):** single source of truth `entries[] = {type, area, level, category, wh}`; ProgramFormat text serialized on demand. Floors render as cards top-floor-first (L7…L0, B1, B2), programs as pills (blue LONG / orange SHORT / muted core+circulation), per-floor SHORT-share bar with 50% tick and an "8'-6\" floor" tag past it. Pill click → inline editor (area / category / delete); per-floor "+ add" → form with datalist vocabulary (SHORT activities + main uses + cores). Sticky footer: GFA, level range, LONG/SHORT %, SHORT-floor count, [▸ raw text] toggle, [Build massing →] (never disabled — cards can't produce malformed lines). Raw panel (collapsed by default) = escape hatch: serialized text + [Apply] that re-parses through the v1 validator; errors listed, entries[] untouched on failure. Build serializes entries[] → `localStorage.programInputText` → `?src=input` redirect as v1. Read-only test hook `window.__debug = { entries, serialize }` exposed for the headless pipeline.

**Verification (puppeteer-core + headless Edge, port 8099):**
- `node --check` both inline scripts — pass.
- Flow mixed-use / 12,000 / 8+2 / 6 activities: 10 floor cards, footer GFA 12,019 m² (±2% ✓), 2 SHORT floors (L1, L2) each 100% share with 8'-6" tags, LONG/SHORT 85%/15%.
- Card interactions: edit office 747→555 m² → footer 12,019→11,827 (exact expected); delete yoga studio pill → serialized occurrences 1→0, entries 82→81 (first attempt failed only because puppeteer's coordinate click landed on the fixed footer overlaying a bottom-of-page card — scroll-safe rerun passed; app logic fine, real users scroll); add staff area 95 m² to L7 → present in card and serialized text.
- Raw panel: open text === serialize(entries) exactly; malformed append → "line 94: too few parts" listed, entries byte-identical; valid edit (95→120) applied → card and footer update, no error.
- Build → `?src=input`: shortfloor stats GFA 11,947 m² == review footer after edits, Floors 10, 2 SHORT floors; zero page errors (favicon 404 pre-existing).
- Zero-activity path: "no activities", 0 SHORT pills, 0 tags, footer SHORT floors 0, GFA 11,995; Build works, shortfloor shows 0 SHORT floors, zero errors.
- Screenshots in session scratchpad: `v2-step4-activities.png`, `v2-review-cards.png`, `v2-raw-panel.png`.

## STRUCTURE mode — boundary floor above SHORT run now flush with ACTUAL brick top

**Request (user):** 4F sat too high; its bottom face should be flush with the top of the SHORT module stack's bounding box.

**Cause:** `buildStructure`'s SHORT-STACK BOUNDARY SHIFT block lifted the first floor above a SHORT run using the course BUDGET `K` (`stackTop = base + K*M`, up to natK+4 courses ≈ 3.4 m above nominal) + `PRI_H` 0.8 m — an upper bound the porous packer often doesn't reach → air gap between actual brick top and the girder underside.

**Fix (delegated to structure-frame agent, sonnet):** `buildShortBlocks` now computes each run's ACTUAL stack top from placed geometry (bricks incl. vertical 2-course modules + stair-shaft courses) and publishes it to a new module-level `SHORT_STACK_TOP` Map (keyed by run's first level, reset in `build()` next to `SHORT_PLACE`). `buildStructure` reads it first (`excess = actualTop + PRI_H − topY`, `>1e-6` clamp kept — floors never drop below nominal); falls back to the old K-budget formula only when no entry exists (`structure && !BLOCKS` early-return path). Packer, K budget, solid mode, INTERLOCK/PROTRUDE untouched.

**Verification:** on the built-in SAMPLE (run L0–L2, boundary L3): oldBudgetTop = actualTop = 15.5448, excess = 0.8 (= PRI_H); direct mesh query confirms nearest main girder bottom face at L3 == actualTop exactly (true flush). SOLID mode unchanged; zero new console errors. Screenshots `structure_final.png` / `solid_final.png` in session scratchpad. **Caveat:** SAMPLE happens to fill every course, so old and new formulas coincide there — the fix only changes output on programs whose top course is left partially unfilled (unpaired footprint cells). Re-test against the user's actual output.txt; if a gap persists there, the remaining cause would be the nominal floor top itself sitting above the brick top, which would need allowing a downward (negative) shift — deliberately excluded for now (collision risk with LONG frames inside the run).

**Backup:** `BACKUP/program-massing-shortfloor-260706-preflush.html` (pre-edit copy).

## SHORT skin — decks / windows / facade panes per platform assembly rules (late night, past midnight)

**Request (user):** apply the M=259 platform skin system (`references/MODULE/platform_assembly_rules.md` + `build_platform.cs`) onto the SHORT module stacks: 樓板 module-deck, 窗 window 173 + window-1 66, 帷幕/飾板 FACADE_PANE07.

**Implementation (delegated; structure-frame agent correctly REFUSED — buildShortBlocks/kit/UI are its hard boundaries — re-routed to general-purpose sonnet):** all in `program-massing-shortfloor.html`, STRUCTURE mode only, gated by new `SKIN_ON` flag (panel checkbox `#ctl-skin`, default ON, plus `?skin=0|1` URL param). Inside `buildShortBlocks`: occupancy derived from PLACED bricks (vertical modules count base course only); deck pairs (121×239×10, bottom = course + 5·BLOCK_S, half-span math from build_platform.cs) at every brick base course + roof pairs per column, stair cells skipped; facade columns (exposed faces) decided once via hash3 → 60% windows / 40% curtain; windows 173+66 fill the 239 opening, top = course + 243·BLOCK_S, glass flush with outer grid line; curtain panes 249×249×19 offset 19 out, pitch 250·BLOCK_S from column top (measured 2.4913 m — intentionally un-snapped to the 259 line), one row may drop past bottom. Rendered as 4 InstancedMeshes (`addInstR` rotation-aware helper); materials concreteSlab / glazing / new pale panel 0xdedad2. New `Export SHORT · SKIN (.obj)` button.

**Verification:** node --check pass; SAMPLE counts decks 492 / winL 219 / winS 219 / panes 243; SKIN OBJ = 1,173 groups / 9,384 v / 7,038 f = exactly 1173×(8v,6f); `?skin=0` → zero skin instances, kit unchanged; SOLID mode unchanged; zero new console errors. Screenshots in session scratchpad (`FINAL_deck_window_zoom.png`, `FINAL_pane_stack_zoom.png`, `1_structure_whole_skinON.png` …); main-agent eyeball check confirmed decks in frames, 173/66 split, pane seam drift.

**Known nits (not fixed):** `#ctl-skin` checkbox appears unlabeled in the panel; deck InstancedMesh userData.type reads "short module block" (kit label) instead of "short skin"; window/pane glazing reuses the LONG curtain material so they blend visually — flagged as intentional per spec. **Roster gap:** no dedicated agent owns the SHORT kit domain (buildShortBlocks/SHORT_PLACE/kit export/panel UI) — structure-frame's refusal exposed it; consider adding one per agentops/AGENT-ARCHITECTURE.md if SHORT-kit work keeps coming.

**Backup:** `BACKUP/program-massing-shortfloor-260706-preskin.html`.

### Correction (260707, same session) — FACADE_PANE07 is a vertical timber LOUVER, not a solid pane

User caught it: `assembly_rules.md:36` — FACADE_PANE07 = 498×498 百葉板, **25 vertical blades** (full scale 5.08×10.16 section, pitch 20; ×0.5 → 249 panel, 25 blades pitch 10, section 2.54×5.08, depth band 13.9–19 out) + top/bottom rails, confirmed against `MESH["FACADE_PANE07"]` in rule_build_group_260704.py. The solid 249×249×19 box was replaced (general-purpose sonnet): new `louverBoxSpecs()` + `mergeBoxGeometries()` (~885–925), pane material now the existing `timber()` (same wood tone as LONG fins) — 0xdedad2 removed; placements untouched. `exportSkinOBJ` writes 27 boxes per pane: 7,491 groups = decks 492 + winL 219 + winS 219 + panes 243×27 = exact match, 59,928 vertices. Tooltip labels fixed: "short skin · deck" / "short skin · louver". Zoom screenshot (`02b-structure-zoom-louver-canvasonly.png`) confirms separate slats with gaps. **Pre-existing nit found:** RENDER MODE button highlight doesn't sync when mode set via `?mode=structure` URL param (internal state correct, cosmetic only). **Backup:** `BACKUP/program-massing-shortfloor-260707-preLouver.html`.
