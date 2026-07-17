# PROGRAM-TRANSITION-DB — companion report

Written 260712 (N2). Machine data: `transitions.js` (same folder). Schema: `../INTEL-DATA.md` §4.

## What this is

A database of observed building-program transitions — which programs buildings *actually*
become — with the physical/regulatory preconditions that decide feasibility and at least
one built example per transition. It feeds the M4 forecast step: given a site's current
program (from the SITE-TIMELINE), the DB proposes plausible next programs and the
conditions under which each is credible.

## Honesty rules applied (constraint C5)

- **`likelihood` is a tier (high / medium / low) with a stated `basis` sentence — never a
  percentage.** No transition-frequency dataset exists for this domain; a number would be
  fake precision. "High" here means: the transition is a recognized, repeatedly executed
  pattern with a regulatory template; "medium": repeatedly executed but sponsor- or
  cycle-dependent; "low": physically or economically exceptional, landmark one-offs.
- Example citations are **publication/institution-tier** (`reported`), named in each
  entry's `source` field. `url` is null until a verification pass resolves it — a null
  URL is honest; an invented one is not.
- LA examples are deliberately over-represented: they are the pilot site's own market and
  the ones the research can field-check.

## The 19 transitions (summary table)

| From | To | Tier | Key precondition | Anchor example |
|---|---|---|---|---|
| warehouse | artist studio/loft | high | live-work ordinance | LA AIR ordinance districts, 1981– |
| warehouse | housing | high | ARO + light access | Toy Factory Lofts, LA 2004 |
| warehouse | creative office | high | district amenity mass | Ford Factory → Warner Music, 2019 |
| wholesale market | food hall / retail | medium | curatorial operator | Anaheim Packing House, 2014 |
| factory | museum/gallery | medium | institutional anchor | Tate Modern, 2000 |
| factory/refinery | mixed-use campus | medium | remediation capital | Domino Refinery, Brooklyn 2017–23 |
| office | housing | high | plate depth ≤ ~13 m | Eastern Columbia (ARO), LA 2006; 25 Water St, NYC 2025 |
| office/bank hall | hotel | medium | tourism district | NoMad LA, 2018; Ace Hotel DTLA, 2014 |
| department store | museum/education/office | medium | institutional buyer | May Co → Academy Museum, 2021 |
| shopping mall | logistics | medium | highway superblock | Randall Park Mall → Amazon, 2018 |
| shopping mall | medical | medium | health-system tenant | One Hundred Oaks → Vanderbilt, 2009 |
| shopping mall | housing/mixed | medium | specific-plan rezone | Promenade 2035, Warner Center 2019 |
| parking structure | any occupied program | low | flat slabs + ≥3.4 m clear | 84.51° Centre, Cincinnati 2015 (designed-for) |
| hotel/motel | supportive housing | high | public funding stream | Project Homekey, CA 2020– |
| church | event venue / housing | medium | SB 4 (2023) / acoustics | Vibiana, LA 2005 |
| theater/cinema | retail/church/hotel amenity | medium | assembly continuity | Ace Hotel/United Artists, LA 2014 |
| train station | museum / campus | medium | flagship sponsor | Michigan Central → Ford, 2024 |
| power plant | culture/retail/mixed | medium | extreme land value | Battersea, London 2022 |
| jail | hotel | low | landmark cachet | Liberty Hotel, Boston 2007 |

## Reading the preconditions

The precondition fields are the **Building Adaptability test** (original proposal's agent 8):
given a real building, check `structure / span / floorHeight / core / mep / zoningClass`
against a candidate transition — misses become the `blockers` list. The recurring physical
gatekeepers across all 19 entries are exactly three: **floor-plate depth** (housing needs
daylight), **clear height** (parking's 2.2 m kills everything), and **structural grid
regularity**. Regulation is the fourth gate and the most volatile: LA's 1999 Adaptive
Reuse Ordinance, Project Homekey (2020), and SB 4 (2023) each unlocked a whole row of
this table more or less overnight — which is why the M4 forecast treats regulation nodes
as first-class drivers, not background.

## Relevance to the pilot site

The City Market of Los Angeles sits on the first three rows' home turf: its own history
(produce market → decline → City Market South creative reuse → entitled mixed-use master
plan) instantiates `wholesale market → food hall/creative office` and points next at
`→ housing / education / event` under DTLA 2040 — the scenario space M4 will draw.

## Known gaps

- No entry yet for `school →`, `hospital →`, or `data center →` (rising relevance; add
  when a cited example is in hand).
- URLs unresolved (all examples `reported` tier). A verification pass should promote the
  LA entries to `verified` via LA Conservancy / City Planning records first.
