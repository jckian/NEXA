# 260708 PLAN — compact-core parti (coreN embedded, no volume outside the cores)

**Audience:** an opus executor. Self-contained. **Scope: EDIT ONLY `program-massing-shortfloor.html`** (`computeLayout` EDGE region + the CORE-OPTION button label). Do NOT touch `program-input.html`, the SAMPLE fixture, `computeShortFloors`, or the classifiers. Authored by Fable 5 after reading the current computeLayout in full.

**SUPERSEDES the earlier two-scheme idea in this file — user simplified the ask (260708): ONE scheme only (compact core), plus pull the stray volumes currently sitting OUTSIDE the cores back into the mass. No UI selector work, no pinwheel.**

## 0. Why (user directive, 260708)

The generated massing (`session-log/260707-tools/office-split-caseall.png`) renders **coreN as a lone tower stranded far right**, with low ground/low-floor slabs + orange bits stretching out to reach it — volumes sitting OUTSIDE the compact mass. User wants: above-grade volumes **cluster compactly**, circulation **shortest path**, and **the volumes that fall outside the cores pulled back in** so nothing floats beyond a core.

**Root cause (current EDGE parti, :450-464):** `coreNx = cwS + winMax` pins coreN at the WIDEST floor's (the wide ground floor's) NE corner; the unified window scan tie-break (:517) makes every narrower upper floor hug coreS (left), so coreN is touched only by the widest floor and reads detached, while the wide GL's far cells stretch out toward it as stray slabs.

## 1. Deliverable — compact-core EDGE parti

Rework the EDGE branch (CORE_OPTION `'edge'`, the `else` block ~:449-531) so:

1. **coreN embeds in the mass (float-min), not at the widest-floor corner.** Place `coreNx` to minimize total float `Σ_above-grade max(0, coreNx − Wwin(lv))` over the packed window widths — coreN lands where most floors' right edges cluster (the INSET branch already runs this scan at ~:432-433; adapt it with `coreSx = 0`). coreS stays pinned at x0.
2. **Floors WIDER than coreNx WRAP it — no floating slab.** A floor whose window would overlap the coreN cells packs THROUGH/around them (reinstate the core-skip that `packLegacy` uses at ~:442: when the running x hits the core interval, jump past it and continue contiguously). The wide ground floor thus wraps coreN and stays one contiguous mass with the core embedded — its far cells are pulled IN against the core, not left stranded to the right.
3. **No volume outside the cores.** After packing, every above-grade floor's occupied columns form ONE contiguous run that includes its active core shaft(s); nothing sits beyond the outer core with a gap. Recompute `FW` from the actual packed extents + core cells (two-pass, like legacy :447-448) so the envelope is tight, not the old fixed `coreNx+cwN`.
4. **Shortest corridor** (existing §0.6.2 rule at ~:533 stays): with coreN embedded, per-floor corridors shorten automatically; report corridorΣ before/after.
5. **clusterFloor SHORT-anchor** consistency preserved so cross-floor interlock columns still stack (verify overlap doesn't collapse — acceptance below).

Relabel the `#seg-core` "A · corners" button (:94) to **"Compact"** for honesty (value stays `'edge'`; no other UI change). Leave the `'inset'`/"B · centre" path exactly as-is (separate pending P4 — do NOT touch it).

## 2. Current file state you MUST account for

- `computeLayout` evolved P1 → P1.5 (`subdivideBlock`, `MAX_SIDE_MOD`) → **P2 depth-normalization is LIVE but UNVERIFIED at ~:367-390** (a prior agent was killed mid-verification; its coreNx-tracking/E0-revert block is ~:375-402 and references the OLD `coreNx=E0−cwN` placement — reconcile it with your new float-min coreNx or neutralize it). Re-grep ALL line numbers; they have shifted. Your SAMPLE + structure acceptance also VALIDATES P2 coexistence — if SAMPLE breaks and you trace it to P2, note it and revert the P2 block only if needed to pass (report the decision); never leave SAMPLE broken.
- `replica3.js` (session-log/260707-tools/) mirrors computeLayout; keep it in sync with the new EDGE parti so `[ASSERT]` passes on the achievable invariants. Its hardcoded corridor baselines are already stale — screenshots are the primary proof, not exact baselines.

## 3. Hard constraints (violation = revert)

- **Backup `BACKUP/program-massing-shortfloor-260708-preCompactCore.html` BEFORE the first edit.** No git; never delete/rename existing files.
- **SAMPLE stats HARD:** Total GFA 14,272 m², 3 SHORT floors L1-L3 (computeShortFloors untouched). SAMPLE overlap pairs ≥ .75 each, weave visibly intact (§0.5 relaxed standard — layout MAY move; SAMPLE is expected to become compact too).
- `node harness.js` stays **166/0** (generator untouched; red ⇒ wrong file ⇒ revert + STOP).
- Do NOT overwrite frozen `case_all.txt`/`case_learning.txt`/`sample.txt`. Use `session-log/260707-tools/case_all_v2.txt` (office-split generator output) as the generated-program input; regenerate it via `node repro2.js`-style live generation if absent.

## 4. Acceptance — screenshots are the primary proof (massing/taste deliverable)

End-to-end per `agentops/G-LETTER.md` item 3 (Start-Process -Wait, fresh --user-data-dir per shot, delete profile after, stop server; structure budget 25000-30000):
1. **case=all:** one TIGHT compact block; **coreN embedded in the mass, NOT a detached tower**; **no volume sitting outside/beyond the cores** (compare directly against `session-log/260707-tools/office-split-caseall.png` — the stray bottom-right slabs must be gone/absorbed); corridor visibly short. Save `session-log/260708-tools/compact-caseall.png` (+ a zoom crop showing the former coreN region).
2. **SAMPLE:** coherent compact stack, weave intact, stats 14,272 / 3 SHORT L1-L3. Save `compact-sample.png`.
3. **structure mode** (`&mode=structure`) case=all: zero fatal console errors, full frame renders. Save `compact-caseall-structure.png`.
4. **replica3 on case_all_v2 (edge):** `[ASSERT] PASS`; SHORT overlap pairs ≥ .70; **coreN float mean → near 0** and **touch% high** (report both — this is the quantitative proof the core is embedded); every above-grade floor contiguous (0 orphan, MAX intra-band gap ≤ 1); corridorΣ reported and DROPPED vs 171 (if not, explain).
5. Delete `_handoff-test.html` + edge profiles, stop the server.

State in one sentence how coreN reads now and confirm the stray outside-volumes are absorbed.

## 5. STOP conditions (report instead of pushing on)

- coreN still reads detached, OR volumes still sit outside a core, after ONE bounded retry → STOP with the screenshot + float/touch metric + your read of the mechanism.
- Reviving core-wrap breaks the no-orphan/contiguity invariant and you can't reconcile in ≤2 attempts → STOP with both measurements.
- SAMPLE stats change and you can't restore them → STOP with the diff.
- You want to edit `program-input.html` or the classifiers → wrong file, STOP.
- Two failed attempts at the same sub-goal → STOP with the failure trail.

## 6. Report contract (≤30 lines back to commander)

What changed (file:line per edit) · the button relabel · screenshot paths + one sentence each on (a) how coreN reads now and (b) whether the outside volumes are absorbed · replica metric line (overlap / corridorΣ / coreN float / touch% / contiguity) · SAMPLE stats check · P2-coexistence result (and any revert) · harness result · anything noticed but not fixed. Full detail → `agentops/reports/260708-compact-core-report.md`; return the path + the ≤30-line summary. Your final text is data for the commander, not prose for a human.
