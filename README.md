# NEXA

**An open-source, browser-based platform for how buildings change over time, not just how they get built the first time.**

NEXA is built around one idea: a building's program has a much shorter lifespan than its
structure. A restaurant lasts a few years, an office fit-out maybe five to ten, but the
frame stands for fifty to a hundred. NEXA pairs a permanent long-life structure with
plug-in, relocatable short-life modules, so a building can be refreshed, re-tenanted, or
converted instead of demolished.

You describe a program in plain language, and NEXA lays out the massing, an 8'-6"
demountable module system, and a hybrid structure, all in the browser with no install.

> SCI-Arc Spring 2026 research by Yenhsing Cheng.

---

## Why it exists

Existing design tools each cover only one stage of a building's life, and most are closed
and expensive:

| Tool | Covers | Stops at |
|---|---|---|
| Modular platforms (Gropyus, AUAR) | How a building is built | Handover |
| Circular tools (Madaster) | Material records | Doesn't generate adaptive systems |
| Digital twins (Autodesk Tandem) | Monitoring | Can't reconfigure |

NEXA connects adaptive design, program-lifespan logic, and reuse into a single continuous
lifecycle, and does it in the open so students and small practices who can't afford the
proprietary suites can use and extend it.

---

## Workflow

![NEXA system workflow: from lifespan mismatch to lifecycle management](references/System%20Workflow-%20FOR%20GITHUB.png)

A narrative brief (program, area, site) is analyzed by program lifespan and split into
long-duration and short-duration programs. Structural zoning resolves these into a
permanent structure and relocatable units, producing Architecture Version 0. From there a
digital twin monitors the building and drives refresh, turnover, conversion, and reuse,
feeding an economic analysis and looping back into the next architecture.

---

## What's here

Every app is a single HTML file using CDN Three.js. **No build step. Open it in a browser.**

| File | What it does |
|---|---|
| `program-input.html` | Plain-language program-input wizard (building type, per-floor recipe, GFA, floors). Hands off to the visualizer via `localStorage`. |
| `program-massing-shortfloor.html` | Massing and structure visualizer: module packing, RC core / aluminium frame / glass curtain wall / timber fins, OBJ export, and automatic code, egress, and restroom checks. |
| `NEXA/NEXA-site.html` | Project intro site (concept, pipeline, program-lifespan / design-for-disassembly). |
| `NEXA/intel/` | Site-intelligence layer: reads a real site's history and forecasts its plausible future programs. |
| `NEXA/intel/site-scout.html` | GIS tool: address to parcel to zoning and neighborhood context. |
| `MODULE-TOOLS/` | Module-system dev tools (8'-6" / 1:2 domino kit of parts). |
| `references/` | Program-format spec, case-study distributions, module logic, sizing rules. |
| `agentops/` | The Claude Code multi-agent workflow used to develop NEXA. |

---

## Quick start

The web apps need no setup:

```
# any static server works, e.g.
npx serve .
# then open program-input.html in a browser
```

Start at `program-input.html`, describe a program, and continue into
`program-massing-shortfloor.html` to see the massing and structure.

### Python simulation (optional)

An earlier agent-based distribution simulation lives in `pythonFiles/`:

```
cd pythonFiles
python ProgramDeveloperEllipseBoundary.py
```

Dependencies: `openai`, `numpy`. It expects an `OpenAI_ProgramDetails.py` module supplying
your own API key (not included in the repo; keep keys out of version control).

---

## Program data format

Program data uses a compact grammar: `{type}/{area m2}/{level}/{category}/{w,h}`
(curly braces are literal). Full spec in
[`references/ProgramFormat.txt`](references/ProgramFormat.txt).

Case-study distributions are included for OMA's TPAC and Jean Nouvel's 53W53
(`references/*-PROGRAM-DISTRIBUTION.txt`).

---

## Status

Early and actively developed by a solo developer. The web toolchain runs and is tested;
the digital-twin decision engine and economic analysis described in the concept are on the
roadmap.

## License

[MIT](LICENSE) © 2026 Yenhsing Cheng
