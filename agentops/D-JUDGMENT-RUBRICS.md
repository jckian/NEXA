# D — Judgment Rubrics

Decision rules that normally live in a stronger model's head, written down so any model can apply them. Each rubric: signals → action, one positive example (apply it), one negative example (don't).

## 1. When to escalate to a stronger model

Escalate when ANY of:
- The task couples 3+ interacting constraints that must be traded off, not just satisfied one at a time.
- The spec is ambiguous AND guessing wrong is expensive to undo.
- The previous attempt produced output that *looked* right but was wrong. (Plausible-but-wrong is the signature of under-powered reasoning; a syntax error is not.)
- You are about to make an architectural decision that later work will build on.

✅ Escalate: "Redesign the floor-layout packing so the core cluster, the aspect-ratio cap, adjacency pulls AND the tapered footprint all hold at once." Coupled constraints — a greedy one-constraint-at-a-time fix breaks the others.
❌ Don't escalate: "Rename SLAB_H to SLAB_HEIGHT everywhere" or "add three program types to the distribution file following the existing pattern." Mechanical; sonnet with a clear template is correct, escalation just burns budget.

## 2. When it's actually done

Done = every acceptance criterion demonstrated with evidence that exists outside your own claim: a command output, a screenshot, a read-back, a matching count. "I made the change and it should work" is not a state; it is a hypothesis.

✅ Done: changed the taper math → served the page locally, headless screenshot shows the new taper, zero new console errors, screenshot path reported.
❌ Not done: edited buildScene(), the Edit tool succeeded, replied "the taper is fixed." Edit success only proves the string was replaced, not that the scene renders. If you notice you are about to report done without evidence, that IS the signal: go produce the evidence first.

## 3. When to stop and ask the user

Ask when:
- The action is destructive or hard to reverse in a repo with no git: deleting/overwriting any file you didn't create this session, restructuring directories, rewriting a `*-DISTRIBUTION.txt`.
- It is a design-taste call: proportions, massing reading, color meaning — anything an architecture crit would argue about and the spec doesn't pin down.
- Fulfilling the request literally would contradict something else the user said or a spec file.
- You have changed approach twice and are still failing (§4) — bring the trail, 2–3 options, and a recommendation.

Do NOT ask about: reversible edits within spec, tool choice, layouts already covered by conventions, or "shall I proceed" on the thing the user just asked for.
✅ Ask: "The new site boundary makes the front/back area ratio in the spec unachievable — relax the ratio, or shrink the plaza?" (taste + spec conflict)
❌ Don't ask: "Should I use Grep or open the file?" — decide and act; asking costs a round-trip and the user's trust.

## 4. Signals the approach is wrong — switch, don't retry

Switch approach (do not attempt round 3 of the same move) when:
- The same *class* of error survives a fix that should have killed it.
- Your fixes are numeric fudges (nudging constants, adding offsets) rather than addressing a mechanism.
- Each fix breaks something that previously worked (whack-a-mole).
- You cannot explain in one sentence why the current attempt should succeed where the last one failed.

When switching, write down what the failed approach *assumed* — the assumption is usually the bug — in the session log or the delegation trail.

✅ Switch: ellipse agents keep escaping the site boundary; you strengthened the containment force twice, they still escape → stop tuning forces; check the units/coordinate mapping between border.txt and agent space. (Mechanism, not magnitude.)
❌ Don't switch: the first run throws a NameError from a typo you just introduced. That is not an approach signal, it is a typo — fix it and rerun. Abandoning an approach after one shallow error wastes as much as retrying forever.

## 5. Quality floor — minimum verification per artifact type

| Artifact | Floor (all required) |
|---|---|
| Python change | `python -m py_compile` passes + one real run with actual fileTransfer inputs + output file spot-checked |
| HTML app change | Page loads via local server, zero new console errors, headless screenshot taken; if the change is visual, screenshot shown/linked to the user |
| Program-distribution data | Format matches references/ProgramFormat.txt; per-floor and total areas within 2% of target; core rules (≥3 fire-stair types per floor) hold — verified by counting, not eyeballing |
| Docs / rule files | Read back in full; every referenced path confirmed to exist |

✅ Meets floor: distribution regenerated; a script summed areas = 58,320 m² vs 58,250 target (0.1%); grep counted 3 cores on every floor.
❌ Below floor: "regenerated the distribution, looks right" — no sum, no core count. Eyeballing 70 floors of data is exactly what models get wrong.

## Honest limits — what these rubrics cannot fix

Rubrics recover *execution* quality (decomposition, verification, multi-sample judging). They cannot supply taste or resolve genuine ambiguity:
- Architectural/visual judgment beyond "renders correctly and matches the stated numbers" → produce the screenshot and ask the user. Do not simulate having an opinion strong enough to overrule them.
- Ambiguous goals ("make it feel more OMA") → propose 2–3 concrete interpretations with a recommendation and let the user pick; or escalate to the strongest available model AND still show the user before committing.
- If you cannot verify a claim from the repo or via claude-code-guide, write "unverified" in your report. An honest gap costs one question; a confident fabrication costs a rebuild.
