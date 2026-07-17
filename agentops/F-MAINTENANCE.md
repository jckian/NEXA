# F — Maintenance Protocol for agentops/ and CLAUDE.md

## Change permissions

May change WITHOUT asking the user:
- Append lessons to agentops/LESSONS.md (format below; create the file on first lesson).
- Update CLAUDE.md "Current focus" (with a new date stamp) and the file-size/danger tables when reality has changed.
- Add new templates to E; add rows to the C Rule 4 table.
- Fix factually wrong paths/names anywhere in agentops/ except G-LETTER.md (verify first; note the fix in LESSONS.md). A wrong path inside G-LETTER: ask first, like any other G-LETTER edit.

ASK the user first:
- Changing thresholds or the ladder in C Rule 5, or any rubric in D (these encode the user's cost tolerance and standards).
- Deleting or rewriting any agentops file; editing G-LETTER at all (except its Handover section).
- Loosening any hard rule in CLAUDE.md's danger section.
- Anything on the "may change" list, if the real reason is that a rule was inconvenient this session rather than wrong.

## Backups (no git in this repo)

Before editing CLAUDE.md or any agentops/ file: `cp <file> BACKUP/<name>.bak-YYMMDD`. One backup per file per day is enough.

## Recording lessons

After any incident where a rule was missing, wrong, or ignored, append to agentops/LESSONS.md:

    ## YYMMDD — ⟨short title⟩
    Trigger: ⟨what happened, 1–2 lines⟩
    Rule: ⟨one imperative line: what to do next time⟩
    Home: ⟨which agentops file this rule belongs in, if promoted⟩

Rules enter the main files only with a trigger behind them — no speculative rules. A lesson recurring is the signal to promote it into its Home file.

## Compaction

When LESSONS.md exceeds ~25 entries, or any agentops file exceeds ~250 lines:
1. Promote recurring lessons into their Home files.
2. Move superseded raw text to BACKUP/.
3. Do compaction with sonnet or better, in a session that has read ALL agentops files first; never mid-task, never with haiku.

## Drift check

Any session that notices CLAUDE.md's focus date is >30 days old: verify against the newest session-log, then update or re-confirm the date stamp. This is the single most important maintenance act — a stale map caused the pre-260703 failure documented in A-DIAGNOSIS §3.
