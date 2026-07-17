# G — Letter to Future Sessions (Fable 5, 2026-07-03)

Read once when you first work in this repo, and again whenever the system feels like it is fighting you.

## Three things the user didn't ask me to tell you

**1. The deliverable is architecture, not software.** This is SCI-Arc design research. The user's real output is an argument made visible — diagrams, massings, screenshots for reviews and crits. A working demo tonight beats an elegant module next week. Concrete test: a refactor or cleanup is justified only if it is required to implement the requested change or to fix a demonstrated bug — otherwise leave working code alone, even if it is ugly. When time is short, ship the visible result first and note the internal debt in the session log. Respond to the user in Traditional Chinese; keep code and file contents in English.

**2. The mess is the version control.** There is no git. BACKUP/, index.html vs index2.html, program-massing vs -shortfloor — the copies ARE the history. Do not clean up, dedupe, or delete without asking; you may be destroying the only copy of a state the user wants back. If a natural moment arises, suggest `git init` once. If declined, drop it permanently.

**3. Verification is already cheap here — use it.** Past sessions ran a local-server + headless-Edge screenshot pipeline (settings.local.json holds allow-entries from those runs, but they are literal strings — a new output filename may still trigger one permission prompt; accept it and continue). The loop for ANY visual change: (1) `py -m http.server 8099` from the repo root (background) — and STOP it when verification ends, don't leave it running all session; (2) take the shot with `Start-Process -Wait` — NOT the `&` call operator, which returns before the PNG is written and spawns zombie processes/phantom failures (260707 lesson):

    $p = "$env:TEMP\edgeshot-$(Get-Random)"
    Start-Process -Wait "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList "--headless=new --disable-gpu --no-sandbox --enable-unsafe-swiftshader --user-data-dir=`"$p`" --window-size=1500,950 --virtual-time-budget=16000 --screenshot=`"<out.png>`" `"http://localhost:8099/<page>.html`""
    Remove-Item $p -Recurse -Force

Fresh `--user-data-dir` every run (a reused/locked profile silently writes NO png), delete it right after (21 leftovers = 1.8 GB on 260707); heavy Three.js scenes (structure mode) need `--virtual-time-budget` 25000-30000. A missing PNG after `-Wait` is a REAL failure — diagnose, don't retry-loop. (3) Read the PNG. One command turns "should work" into "works". Sessions that skipped it shipped broken scenes.

## How this system will decay, and the countermeasures

- **CLAUDE.md re-bloats.** Every session is tempted to add "just one note". Countermeasure: CLAUDE.md only routes; notes go to session-log or LESSONS.md (F protocol). If CLAUDE.md exceeds ~90 lines, that is the alarm.
- **Ritual compliance.** Weaker models will fill the E templates but skip the evidence: "done" with no screenshot, "reviewed" with no file:line. The acceptance-criteria and report-contract lines are the load-bearing parts — a report lacking evidence is a failed delegation; send it back.
- **Stale focus.** The exact failure that rotted the old CLAUDE.md. Countermeasure: the 30-day drift check in F. It only works if you actually run it.
- **Escalation avoidance.** A cheap model grinding retry #3 "to save budget" costs more than opus doing it once. The 2-retry cap in C Rule 5 is a hard rule, not advice.
- **Rules without triggers.** If agentops fills with plausible-sounding rules nobody can trace to an incident, trust in the whole system erodes and models start ignoring all of it. F requires a trigger per rule — keep it that way.

## Handover

(Empty at creation, 2026-07-03. If a session must stop mid-institution-work, list unfinished items here.)
