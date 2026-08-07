// NEXA Intel — M4 FORECAST output: scenario cards for 130 W. College Street (LA Chinatown)
// Generated 260713 by the main Claude Code session from:
//   site-collegest.js  (md5 207D0FDD84CAD5A10985554B4D73BACB — after the 260713 zoning backfill)
//   transitions.js     (md5 23280A41C595ACCC438EDA77E2C1F185)
// Method + reasoning archived: NEXA/intel/prompts/260713-scenarios-collegest.md
// Companion prose: scenarios-collegest.md (same folder)
//
// ⚠ EVIDENCE WARNING (inherited from site-collegest.js, do not strip):
// that dossier contains NO verified-tier facts — no primary document was directly read.
// FAR, height district, lot area and TOC tier remain UNKNOWN. These scenarios are
// programmatic hypotheses about a station-adjacent parking lot, NOT capacity studies.
// No draft below should be read as a zoning-compliant yield.
// 260713 UPDATE: mapped zoning is now machine-queried (reported tier): [DM2-G1-5] [CX2-FA]
// [CPIO], 'Commercial-Mixed' — a DTLA 2040 new-format code. Scenario A's original premise
// ("current zoning does not allow the office") reflected the 2023 old-code reporting and is
// now UNCERTAIN rather than supported: what CX2-FA permits by right was not interpreted.
window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.sites = window.NEXA_INTEL.sites || {};
(function () {
  const site = window.NEXA_INTEL.sites["130-college-st"] = window.NEXA_INTEL.sites["130-college-st"] || {};
  const CORES = lv =>
    "{fire stair & freight elevator core}/{40}/{" + lv + "}/{circulation}/{6,7}\n" +
    "{fire stair & passenger elevator core a}/{40}/{" + lv + "}/{circulation}/{6,7}\n" +
    "{fire stair & passenger elevator core b}/{40}/{" + lv + "}/{circulation}/{6,7}\n" +
    "{circulation}/{107}/{" + lv + "}/{circulation}/{10,11}\n";
  const GEN = { promptFile: "NEXA/intel/prompts/260713-scenarios-collegest.md", inputsHash: "site:207D0FDD84CAD5A10985554B4D73BACB transitions:23280A41C595ACCC438EDA77E2C1F185", date: "260713" };

  site.scenarios = [

  {
    id: "D", name: "Entitlement stalls — the lot stays a lot",
    horizon: 2029,
    likelihoodNote: "The null hypothesis, and not a weak one: the proposal needs a General Plan Amendment AND a zone change, it was still in environmental review at last confirmed status, and DTLA office vacancy is ~22%. A speculative 225,000 sf office bet is exactly the kind of project that waits. Interim uses (market, events, film shoots) are what the lot already supports.",
    drivers: ["p-parking-lot", "r-2023-entitlement", "e-dtla-office-softness"],
    risks: ["surface parking is the highest-heat, lowest-value use of a station-adjacent parcel", "interim income entrenches the lot", "no housing produced while displacement pressure rises"],
    strategy: ["demountable, permit-light structures only", "weekend market / event use trades on the Chinatown food revival next door", "keep the parcel clear so any entitlement outcome stays available"],
    programMix: [
      { type: "event + market", share: 0.42 }, { type: "food", share: 0.25 },
      { type: "retail", share: 0.20 }, { type: "storage/back-of-house", share: 0.13 }
    ],
    programFormatDraft:
      "# Scenario D — interim market/event use on the lot (single level, demountable)\n" +
      "{event hall}/{277}/{0}/{public}/{17,16}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{sales and display}/{253}/{0}/{public}/{16,16}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{lounge bar}/{154}/{0}/{public}/{12,13}\n{storage}/{123}/{0}/{private}/{11,11}\n{loading dock}/{161}/{0}/{private}/{13,12}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0),
    generation: GEN
  },

  {
    id: "A", name: "Proposed build-out — Metro-adjacent creative office",
    horizon: 2030,
    likelihoodNote: "The proposal on the table (Riboli family, Grimshaw, ~225,000 sf, 5 storeys, 2023). Its permission is unresolved — the 2023 reporting describes a GPA plus zone change under the legacy code — and it lands into a ~22% DTLA office vacancy. 260713: the mapped zoning is now the DTLA 2040 code ([CX2-FA], Commercial-Mixed), so the permission picture may be easier than 2023 reporting implied; whether CX2 allows this office by right is uninterpreted.",
    drivers: ["p-2023-office-proposal", "e-2023-riboli-chinatown-bet", "t-2003-chinatown-station", "r-2023-entitlement"],
    risks: ["GPA + zone change may fail or be conditioned down", "office demand is the weakest of any program in this market", "no housing = political exposure in a district organizing against displacement"],
    strategy: ["deep-plate creative office over an active ground floor", "structure and floor height sized so office can convert to housing later (transition DB: plate depth ≤ ~13 m, clear ≥ 2.9 m)", "podium parking that can be re-tenanted"],
    programMix: [
      { type: "creative office", share: 0.62 }, { type: "retail + food", share: 0.14 },
      { type: "event + showroom", share: 0.12 }, { type: "parking + service", share: 0.12 }
    ],
    programFormatDraft:
      "# Scenario A — creative-office build-out (study slice, L-1..L4)\n" +
      "{parking bay group}/{322}/{-1}/{private}/{18,18}\n{parking bay group}/{322}/{-1}/{private}/{18,18}\n{mechanical room}/{161}/{-1}/{private}/{13,12}\n{electrical room}/{54}/{-1}/{private}/{7,8}\n{storage}/{123}/{-1}/{private}/{11,11}\n" + CORES(-1) +
      "{lobby}/{207}/{0}/{public}/{14,15}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{sales and display}/{253}/{0}/{public}/{16,16}\n{showroom}/{246}/{0}/{public}/{16,15}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{office}/{392}/{1}/{private}/{20,20}\n{office}/{392}/{1}/{private}/{20,20}\n{project review room}/{123}/{1}/{public}/{11,11}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{office}/{392}/{2}/{private}/{20,20}\n{office}/{392}/{2}/{private}/{20,20}\n{it support}/{62}/{2}/{private}/{8,8}\n{toilets}/{80}/{2}/{public}/{9,9}\n" + CORES(2) +
      "{office}/{392}/{3}/{private}/{20,20}\n{office}/{278}/{3}/{private}/{17,16}\n{event hall}/{277}/{3}/{public}/{17,16}\n{toilets}/{80}/{3}/{public}/{9,9}\n" + CORES(3) +
      "{office}/{392}/{4}/{private}/{20,20}\n{lounge bar}/{154}/{4}/{public}/{12,13}\n{staff area}/{92}/{4}/{private}/{10,9}\n{toilets}/{80}/{4}/{public}/{9,9}\n" + CORES(4),
    generation: GEN
  },

  {
    id: "B", name: "Housing pivot — transit-oriented residential",
    horizon: 2034,
    likelihoodNote: "The transition database's strongest signal (office→housing: high tier), and the block's own evidence: College Station, approved across the street in 2018, is 725 market-rate units on the same station frontage. If the office entitlement fails or the market stays soft, housing is the program the site rezones toward. Displacement politics decide whether it is market-rate or mixed-income.",
    drivers: ["r-2018-college-station-approval", "t-2003-chinatown-station", "r-future-tpa-density", "e-dtla-office-softness"],
    risks: ["market-rate housing here is precisely what anti-displacement organizing opposes", "affordability requirements shift the pro forma", "TOC is a housing incentive but its tier for this parcel is unverified"],
    strategy: ["housing over a Chinatown-serving retail plinth", "station-adjacent = low parking, high density argument", "unit mix carries the affordability commitment College Station did not"],
    programMix: [
      { type: "housing", share: 0.63 }, { type: "retail + food", share: 0.15 },
      { type: "community + wellness", share: 0.12 }, { type: "office", share: 0.10 }
    ],
    programFormatDraft:
      "# Scenario B — transit-oriented housing (study slice, L-1..L7)\n" +
      "{parking bay group}/{322}/{-1}/{private}/{18,18}\n{mechanical room}/{161}/{-1}/{private}/{13,12}\n{storage}/{123}/{-1}/{private}/{11,11}\n{electrical room}/{54}/{-1}/{private}/{7,8}\n" + CORES(-1) +
      "{lobby}/{207}/{0}/{public}/{14,15}\n{sales and display}/{253}/{0}/{public}/{16,16}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{office}/{278}/{1}/{private}/{17,16}\n{fitness center}/{278}/{1}/{public}/{17,16}\n{yoga studio}/{154}/{1}/{public}/{12,13}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{2b2b apartment}/{134}/{2}/{private}/{12,11}\n{2b2b apartment}/{134}/{2}/{private}/{12,11}\n{2b2b apartment}/{134}/{2}/{private}/{12,11}\n{2b2b apartment}/{134}/{2}/{private}/{12,11}\n{studio apartment}/{67}/{2}/{private}/{8,8}\n{studio apartment}/{67}/{2}/{private}/{8,8}\n" + CORES(2) +
      "{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{studio apartment}/{67}/{3}/{private}/{8,8}\n" + CORES(3) +
      "{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n" + CORES(4) +
      "{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{studio apartment}/{67}/{5}/{private}/{8,8}\n{studio apartment}/{67}/{5}/{private}/{8,8}\n" + CORES(5) +
      "{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n{2b2b apartment}/{134}/{6}/{private}/{12,11}\n" + CORES(6) +
      "{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{2b2b apartment}/{134}/{7}/{private}/{12,11}\n{studio apartment}/{67}/{7}/{private}/{8,8}\n{lounge bar}/{154}/{7}/{public}/{12,13}\n{toilets}/{80}/{7}/{public}/{9,9}\n" + CORES(7),
    generation: GEN
  },

  {
    id: "C", name: "Community anchor — Chinatown-serving mixed-use",
    horizon: 2038,
    likelihoodNote: "The scenario the district's own politics argue for: affordable housing plus cultural/community program on a parcel the community land trust and anti-displacement coalition have been organizing around since 2018. Gated on public or philanthropic capital, not on market demand — which is why it is slower and less likely than B, not less needed.",
    drivers: ["s-displacement-pressure", "p-1938-new-chinatown", "e-2013-far-east-food-revival", "c-2017-lashp"],
    risks: ["depends on subsidy stacks, not a private pro forma", "land cost on a station-adjacent parcel works against it", "cultural program without an operator becomes a vacant hall (transition DB: market→food-hall is operator-gated)"],
    strategy: ["affordable housing above a Chinatown market hall + community rooms", "cultural program tied to Central Plaza / Far East Plaza foot traffic rather than competing with it", "phaseable: the hall can open years before the housing floors"],
    programMix: [
      { type: "affordable housing", share: 0.42 }, { type: "market hall + food", share: 0.22 },
      { type: "community + education", share: 0.20 }, { type: "cultural/exhibition", share: 0.16 }
    ],
    programFormatDraft:
      "# Scenario C — community anchor: market hall + community + affordable housing (L-1..L5)\n" +
      "{storage}/{123}/{-1}/{private}/{11,11}\n{loading dock}/{161}/{-1}/{private}/{13,12}\n{mechanical room}/{161}/{-1}/{private}/{13,12}\n{electrical room}/{54}/{-1}/{private}/{7,8}\n" + CORES(-1) +
      "{lobby}/{207}/{0}/{public}/{14,15}\n{sales and display}/{253}/{0}/{public}/{16,16}\n{coffee shop}/{185}/{0}/{public}/{14,13}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{pop-up retail}/{123}/{0}/{public}/{11,11}\n{toilets}/{80}/{0}/{public}/{9,9}\n" + CORES(0) +
      "{exhibition gallery}/{308}/{1}/{public}/{18,17}\n{event hall}/{277}/{1}/{public}/{17,16}\n{toilets}/{80}/{1}/{public}/{9,9}\n" + CORES(1) +
      "{classroom}/{123}/{2}/{public}/{11,11}\n{classroom}/{123}/{2}/{public}/{11,11}\n{seminar room}/{123}/{2}/{public}/{11,11}\n{computer lab}/{123}/{2}/{public}/{11,11}\n{staff area}/{92}/{2}/{private}/{10,9}\n{toilets}/{80}/{2}/{public}/{9,9}\n" + CORES(2) +
      "{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{2b2b apartment}/{134}/{3}/{private}/{12,11}\n{studio apartment}/{67}/{3}/{private}/{8,8}\n{studio apartment}/{67}/{3}/{private}/{8,8}\n{studio apartment}/{67}/{3}/{private}/{8,8}\n" + CORES(3) +
      "{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{2b2b apartment}/{134}/{4}/{private}/{12,11}\n{studio apartment}/{67}/{4}/{private}/{8,8}\n{studio apartment}/{67}/{4}/{private}/{8,8}\n" + CORES(4) +
      "{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{2b2b apartment}/{134}/{5}/{private}/{12,11}\n{studio apartment}/{67}/{5}/{private}/{8,8}\n{meditation room}/{103}/{5}/{public}/{10,10}\n{toilets}/{80}/{5}/{public}/{9,9}\n" + CORES(5),
    generation: GEN
  }

  ];
})();
