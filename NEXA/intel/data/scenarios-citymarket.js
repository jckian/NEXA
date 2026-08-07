// NEXA Intel — M4 FORECAST output: scenario cards for City Market of Los Angeles
// Generated 260712, annotated 260713 (zoning backfill) by the main Claude Code session from:
//   site-citymarket.js  (md5 27E049CC859276F483E8A846203876BA — after the 260713 zoning backfill)
//   transitions.js      (md5 23280A41C595ACCC438EDA77E2C1F185)
// 260713: mapped zoning machine-queried as [DM1-SH1-5][IX3-FA][CPIO] Industrial-Mixed —
// IX3, not the IX2 the 260712 research generalized. Scenario A's zoning risk reworded.
// Method + reasoning archived: NEXA/intel/prompts/260712-scenarios-citymarket.md
// Companion prose: scenarios-citymarket.md (same folder)
// likelihoodNote is a qualitative estimate with a stated basis — never a probability.
// programFormatDraft is a STUDY-SCALE slice (~6,000–10,000 m2 GFA) sized for the NEXA
// massing platform, not the full ~1.8M sf master plan. Draft vocabulary and area/{w,h}
// pairs reuse the platform's verified handoff-test set.
window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.sites = window.NEXA_INTEL.sites || {};
(function () {
  const site = window.NEXA_INTEL.sites["citymarket-la"] = window.NEXA_INTEL.sites["citymarket-la"] || {};
  const CORES = lv =>
    "{fire stair & freight elevator core}/{40}/{" + lv + "}/{circulation}/{6,7}\n" +
    "{fire stair & passenger elevator core a}/{40}/{" + lv + "}/{circulation}/{6,7}\n" +
    "{fire stair & passenger elevator core b}/{40}/{" + lv + "}/{circulation}/{6,7}\n" +
    "{circulation}/{107}/{" + lv + "}/{circulation}/{10,11}\n";

  site.scenarios = [

  {
    id: "A", name: "Entitled build-out — housing-led mixed-use",
    horizon: 2035,
    likelihoodNote: "Highest-likelihood path: this is the entitled program itself, under the March 2024 development agreement with a 20-year fulfillment window (2024–2044). The open risk is execution capital, not permission — no groundbreaking is confirmed as of mid-2026.",
    drivers: ["r-2024-revised-agreement", "r-2024-entitlement-enables", "e-dtla-population-growth", "e-dtla-office-vacancy", "t-future-southeast-gateway"],
    risks: ["construction-cost environment delays phasing", "zoning interaction unresolved — 260713 machine query shows mapped DTLA 2040 zoning [DM1-SH1-5][IX3-FA][CPIO] Industrial-Mixed (IX3, not the IX2 generalized earlier); how the 2024 vesting entitlement sits against the new mapped code is unestablished", "hotel demand cycle"],
    strategy: ["phase over the 20-year window", "housing above an active retail/education plinth", "reserve ground floor for the elevated-park / piazza public-space commitments"],
    programMix: [
      { type: "housing", share: 0.50 }, { type: "office + education", share: 0.17 },
      { type: "retail + food", share: 0.15 }, { type: "hotel", share: 0.12 }, { type: "event", share: 0.06 }
    ],
    programFormatDraft:
      "# Scenario A — entitled build-out (study slice, L-1..L7)\n" +
      "{parking bay group}/{322}/{-1}/{private}/{18,18}\n{parking bay group}/{322}/{-1}/{private}/{18,18}\n{parking bay group}/{322}/{-1}/{private}/{18,18}\n{mechanical room}/{161}/{-1}/{private}/{13,12}\n{storage}/{123}/{-1}/{private}/{11,11}\n{electrical room}/{54}/{-1}/{private}/{7,8}\n" + CORES(-1) +
      "{lobby}/{207}/{0}/{public}/{14,15}\n{sales and display}/{253}/{0}/{public}/{16,16}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{event hall}/{277}/{0}/{public}/{17,16}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{classroom}/{123}/{1}/{public}/{11,11}\n{classroom}/{123}/{1}/{public}/{11,11}\n{seminar room}/{123}/{1}/{public}/{11,11}\n{computer lab}/{123}/{1}/{public}/{11,11}\n{office}/{278}/{1}/{private}/{17,16}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{hotel rooms}/{278}/{2}/{private}/{17,16}\n{hotel rooms}/{278}/{2}/{private}/{17,16}\n{lounge bar}/{154}/{2}/{public}/{12,13}\n{toilets}/{80}/{2}/{public}/{9,9}\n" + CORES(2) +
      "{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{studio apartment}/{67}/{3}/{private}/{8,8}\n" + CORES(3) +
      "{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n" + CORES(4) +
      "{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{studio apartment}/{67}/{5}/{private}/{8,8}\n{studio apartment}/{67}/{5}/{private}/{8,8}\n" + CORES(5) +
      "{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n" + CORES(6) +
      "{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{studio apartment}/{67}/{7}/{private}/{8,8}\n" + CORES(7),
    generation: { promptFile: "NEXA/intel/prompts/260712-scenarios-citymarket.md", inputsHash: "site:27E049CC859276F483E8A846203876BA transitions:23280A41C595ACCC438EDA77E2C1F185", date: "260713" }
  },

  {
    id: "B", name: "Fashion & design education campus",
    horizon: 2040,
    likelihoodNote: "Moderate: the entitled program already reserves education space and the Fashion District identity supplies the school. Gated on an institutional anchor — the transition database shows large-plate stock converts to education only with an institutional buyer (cf. Westside Pavilion → UCLA, 2024).",
    drivers: ["p-2014-creative-reuse", "e-dtla-office-vacancy", "r-2023-dtla2040", "s-immigrant-merchants"],
    risks: ["no committed education institution identified in any source", "enrollment-driven programs are cyclical", "competes with scenario A's higher-value housing"],
    strategy: ["classroom floors as reconfigurable open plates", "shared ground floor with exhibition + food keeps the campus public", "housing floors double as student housing without plan change"],
    programMix: [
      { type: "education", share: 0.30 }, { type: "creative office", share: 0.25 },
      { type: "housing", share: 0.20 }, { type: "event + exhibition", share: 0.15 }, { type: "retail + food", share: 0.10 }
    ],
    programFormatDraft:
      "# Scenario B — education campus (study slice, L-1..L5)\n" +
      "{mechanical room}/{161}/{-1}/{private}/{13,12}\n{storage}/{123}/{-1}/{private}/{11,11}\n{loading dock}/{161}/{-1}/{private}/{13,12}\n{electrical room}/{54}/{-1}/{private}/{7,8}\n" + CORES(-1) +
      "{lobby}/{207}/{0}/{public}/{14,15}\n{exhibition gallery}/{308}/{0}/{public}/{18,17}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{classroom}/{123}/{1}/{public}/{11,11}\n{classroom}/{123}/{1}/{public}/{11,11}\n{classroom}/{123}/{1}/{public}/{11,11}\n{seminar room}/{123}/{1}/{public}/{11,11}\n{computer lab}/{123}/{1}/{public}/{11,11}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{classroom}/{123}/{2}/{public}/{11,11}\n{classroom}/{123}/{2}/{public}/{11,11}\n{project review room}/{123}/{2}/{public}/{11,11}\n{computer lab}/{123}/{2}/{public}/{11,11}\n{seminar room}/{123}/{2}/{public}/{11,11}\n{toilets}/{80}/{2}/{public}/{9,9}\n" + CORES(2) +
      "{office}/{278}/{3}/{private}/{17,16}\n{office}/{278}/{3}/{private}/{17,16}\n{office}/{278}/{3}/{private}/{17,16}\n{toilets}/{80}/{3}/{public}/{9,9}\n" + CORES(3) +
      "{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{studio apartment}/{67}/{4}/{private}/{8,8}\n{studio apartment}/{67}/{4}/{private}/{8,8}\n" + CORES(4) +
      "{event hall}/{277}/{5}/{public}/{17,16}\n{lounge bar}/{154}/{5}/{public}/{12,13}\n{toilets}/{80}/{5}/{public}/{9,9}\n" + CORES(5),
    generation: { promptFile: "NEXA/intel/prompts/260712-scenarios-citymarket.md", inputsHash: "site:27E049CC859276F483E8A846203876BA transitions:23280A41C595ACCC438EDA77E2C1F185", date: "260713" }
  },

  {
    id: "C", name: "Event & culture district",
    horizon: 2038,
    likelihoodNote: "Moderate-low: scales up City Market South's proven event/food DNA and the site's Market Chinatown cultural history into a site-wide identity. The transition database rates market→food-hall/creative-retail as operator-gated — plausible, but no committed cultural operator exists in any source.",
    drivers: ["p-2014-creative-reuse", "r-1992-historic-eligible", "e-dtla-population-growth", "t-future-southeast-gateway"],
    risks: ["operator-dependent (curatorial, not just landlord, per transition DB)", "event economics are cyclical and thin-margin", "night-use conflicts with adjacent wholesale operations"],
    strategy: ["keep the big found volumes as event/exhibition halls", "food + retail as the connective ground tissue", "a thin housing layer keeps the district inhabited off-hours"],
    programMix: [
      { type: "event", share: 0.25 }, { type: "food + retail", share: 0.22 },
      { type: "creative office", share: 0.20 }, { type: "exhibition", share: 0.18 }, { type: "housing", share: 0.15 }
    ],
    programFormatDraft:
      "# Scenario C — event & culture district (study slice, L-1..L4)\n" +
      "{storage}/{123}/{-1}/{private}/{11,11}\n{storage}/{123}/{-1}/{private}/{11,11}\n{mechanical room}/{161}/{-1}/{private}/{13,12}\n{loading dock}/{161}/{-1}/{private}/{13,12}\n{electrical room}/{54}/{-1}/{private}/{7,8}\n" + CORES(-1) +
      "{lobby}/{207}/{0}/{public}/{14,15}\n{event hall}/{277}/{0}/{public}/{17,16}\n{exhibition gallery}/{308}/{0}/{public}/{18,17}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{exhibition gallery}/{308}/{1}/{public}/{18,17}\n{showroom}/{246}/{1}/{public}/{16,15}\n{pop-up retail}/{123}/{1}/{public}/{11,11}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{event hall}/{277}/{2}/{public}/{17,16}\n{lounge bar}/{154}/{2}/{public}/{12,13}\n{sales and display}/{253}/{2}/{public}/{16,16}\n{toilets}/{80}/{2}/{public}/{9,9}\n" + CORES(2) +
      "{office}/{278}/{3}/{private}/{17,16}\n{office}/{278}/{3}/{private}/{17,16}\n{office}/{278}/{3}/{private}/{17,16}\n{toilets}/{80}/{3}/{public}/{9,9}\n" + CORES(3) +
      "{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{studio apartment}/{67}/{4}/{private}/{8,8}\n" + CORES(4),
    generation: { promptFile: "NEXA/intel/prompts/260712-scenarios-citymarket.md", inputsHash: "site:27E049CC859276F483E8A846203876BA transitions:23280A41C595ACCC438EDA77E2C1F185", date: "260713" }
  },

  {
    id: "D", name: "Prolonged interim — creative reuse continues",
    horizon: 2032,
    likelihoodNote: "Moderate: the default trajectory if build-out capital stays stalled. Basis: no confirmed groundbreaking as of mid-2026, DTLA office vacancy at 22% (Q2 2025), and the 2018→2020→2024 entitlement saga shows the plan can wait — the 2024 agreement allows 20 years.",
    drivers: ["e-dtla-office-vacancy", "p-2014-creative-reuse", "r-2020-veto"],
    risks: ["interim uses entrench and raise later redevelopment costs", "low-rise interim yields far below entitled 4.1:1 FAR", "wholesale-district truck traffic limits evening programming"],
    strategy: ["demountable, reversible interventions only (per transition DB: keep the master-plan option open)", "extend the City Market South formula north across the site", "logistics/storage floors bank income at near-zero conversion cost"],
    programMix: [
      { type: "creative office", share: 0.35 }, { type: "food hall", share: 0.22 },
      { type: "retail", share: 0.20 }, { type: "event", share: 0.13 }, { type: "logistics/storage", share: 0.10 }
    ],
    programFormatDraft:
      "# Scenario D — prolonged interim (study slice, L0..L2, low-rise)\n" +
      "{coffee shop}/{185}/{0}/{public}/{14,13}\n{lounge bar}/{154}/{0}/{public}/{12,13}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{sales and display}/{253}/{0}/{public}/{16,16}\n{event hall}/{277}/{0}/{public}/{17,16}\n{loading dock}/{161}/{0}/{private}/{13,12}\n{storage}/{123}/{0}/{private}/{11,11}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{office}/{278}/{1}/{private}/{17,16}\n{office}/{278}/{1}/{private}/{17,16}\n{showroom}/{246}/{1}/{public}/{16,15}\n{project review room}/{123}/{1}/{public}/{11,11}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{office}/{278}/{2}/{private}/{17,16}\n{office}/{278}/{2}/{private}/{17,16}\n{exhibition gallery}/{308}/{2}/{public}/{18,17}\n{toilets}/{80}/{2}/{public}/{9,9}\n" + CORES(2),
    generation: { promptFile: "NEXA/intel/prompts/260712-scenarios-citymarket.md", inputsHash: "site:27E049CC859276F483E8A846203876BA transitions:23280A41C595ACCC438EDA77E2C1F185", date: "260713" }
  }

  ];
})();
