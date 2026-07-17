---
name: feedback_debug_hooks
description: How to get real (not eyeballed) verification data out of this module-scoped Three.js app for counting-script checks
metadata:
  type: feedback
---

`program-massing-shortfloor.html` is a single `<script type="module">` — its top-level
`const`/`let` bindings (`exportBoxes`, `SHORT_PLACE`, `scene`, `root`, etc.) are NOT on
`window` and are invisible to a Puppeteer `page.evaluate()`. There is no permanent debug
hook in the file as of 2026-07-06.

**Working pattern**: add a temporary `if (typeof window !== 'undefined') window.__X__ = {...}`
line at the very END of the function you're verifying (so it fires after all the relevant
mutations for that build pass), exposing whatever module-scope variables you need by
closure. `buildStructure` runs after `buildShortBlocks` in `build()`, so by the time
`buildStructure` finishes, `SHORT_PLACE` and `exportBoxes` already hold the full picture for
one build — both are readable from inside `buildStructure` via closure without touching
`buildShortBlocks` itself. Remove the hook once the counting script has run and the
before/after numbers are captured — don't leave debug globals in the shipped file.

There's a repo-local `node_modules/puppeteer-core` already installed
(`C:/SCI-Arc/SP26-RESEARCH/programAgent/node_modules/puppeteer-core`) — use it with
`executablePath` pointed at the system msedge.exe rather than trying to drive headless Edge
via raw CLI flags. Raw `msedge.exe --headless=new --screenshot=...` invoked directly from
PowerShell was flaky in this session (processes hung or exited nonzero even after killing
stale profile locks with `Get-Process msedge | Stop-Process -Force`); the same recipe
sometimes worked and sometimes didn't with no code change. Puppeteer-core driving the same
binary was reliable every time for both scripted data extraction AND screenshots
(`page.screenshot({path})`). Prefer Puppeteer-core over raw CLI screenshotting in this repo
going forward.

To extract a specific range mid-file, `Read` with a large `limit` (e.g. 27-32 lines) can
mysteriously exceed the 25000-token cap even though the file is only 200 KB total — drop to
`limit: 10-15` and re-issue; it resolves. Don't burn a read-window budget on this file
guessing at limits — start small.
