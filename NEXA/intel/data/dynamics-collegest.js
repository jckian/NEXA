// NEXA/intel/data/dynamics-collegest.js
// M10 SITE-DYNAMICS — 130 W. College Street (Chinatown, Los Angeles)
// Schema + honesty rules: NEXA/intel/INTEL-DATA.md §7. Prose report: dynamics-collegest.md
// Confidence tags per INTEL-DATA.md §1: verified | reported | estimated | unknown.
//
// ⚠ THE TWO-OBSERVATION RULE (§7). A metric with fewer than two dated observations carries
// trend "unknown", is forced to direction "context" and ranks nothing. The rule bites hard in
// this file: the tenure and rent-pressure metrics bear directly on a housing future and still
// rank nothing, because nobody publishes them here as a series.
//
// ⚠ NO SOCIAL-MEDIA METRIC IS IN THIS FILE. `soc-ct-attention` is a DECLARED GAP.
//
// ⚠ THIS DISTRICT HAS NO BID VISITATION PANEL. The Fashion District's own BID buys and
// publishes Placer.ai data; Chinatown's does not, so "pedestrian movement" here degrades to
// boardings at one rail station. The two sites are therefore NOT comparable on footfall, and
// nothing in the platform may present them as if they were.

window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.dynamics = window.NEXA_INTEL.dynamics || {};

window.NEXA_INTEL.dynamics["130-college-st"] = {

  meta: {
    site: "130-college-st",
    district: "Chinatown, Los Angeles",
    // Same estimated centre the M9 signal set uses, so one address picks up both layers.
    where: { lat: 34.0641, lon: -118.2367, radiusM: 800, confidence: "estimated" },
    compiled: "260803",
    method: "Web search session 260803. LA Metro's October 2025 ridership release and the " +
      "station-level figures circulated from Metro's public records for boardings. Published " +
      "season attendance for Dodger Stadium. LA Public Press and USC Annenberg Media for rent " +
      "pressure and the age and tenure profile. Restaurant guides for named openings. Press " +
      "summaries of brokerage data for the Downtown office submarket and the city's adaptive " +
      "reuse pipeline.",
    limits: "There is no visitation panel for this district. The pedestrian reading is boardings " +
      "at one elevated rail station, which is not sidewalk footfall, and it has a single dated " +
      "point. The rent and tenure figures come from journalism citing studies that were not " +
      "themselves read, and neither is a series. Four of the nine streams carry no usable " +
      "number and two of those are declared gaps. Do not compare this site's footfall with the " +
      "City Market set: that district buys a commercial panel and this one does not. Compiled " +
      "260803, nothing refreshes automatically."
  },

  metrics: [

    // ── pedestrian movement ──────────────────────────────────────────────────────────────
    {
      id: "ped-chinatown-station",
      stream: "pedestrian",
      label: "1,180 weekday boardings at Chinatown station",
      unit: "average weekday boardings",
      geography: "venue",
      measures: "Average weekday boardings at the elevated A Line station at 901 N Spring Street, " +
        "about 700 m from the parcel. It counts people entering one station, not people walking " +
        "on Chinatown's streets, and it misses every arrival by car, bus or on foot.",
      series: [
        { t: "FY2025", v: 1180, source: "LA Metro 2025 ridership by station, released through public records and republished on Wikipedia", url: "https://en.wikipedia.org/wiki/Chinatown_station_(Los_Angeles_Metro)", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one observation; no earlier year on the same basis was retrieved",
      strength: "anecdotal",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "culture", "museum", "gallery"] },
      reading: "1,180 boardings a day is a small station. Program here cannot assume a transit " +
        "catchment does the work of drawing people; something on the site has to.",
      caveat: "The figure reaches this file through Wikipedia citing a Metro public-records " +
        "release, not from Metro directly. Station-by-station reporting nearby is also disturbed " +
        "by the Regional Connector opening, which cut Civic Center boardings 25% year over year " +
        "by removing transfers rather than riders."
    },

    {
      id: "ped-metro-mode",
      stream: "pedestrian",
      label: "Rail up, bus down, weekends up, weekdays down",
      unit: "monthly rail boardings, county-wide",
      geography: "county",
      measures: "Metro Rail boardings across Los Angeles County in September, both years. The " +
        "county is the wrong scale for a parcel decision; what carries here is the shape of the " +
        "change, not the level.",
      series: [
        { t: "2024-09", v: 5860900, note: "derived from the published +1.7% year-over-year change, not itself a published figure", source: "LA Metro, ridership release, 31 October 2025", url: "https://www.metro.net/about/metro-ridership-holds-strong-amid-regional-challenges-driven-by-rail-growth-weekend-travel-improved-safety/", accessed: "260803", confidence: "estimated" },
        { t: "2025-09", v: 5960493, note: "total system 26,260,796, down 1.9%; bus 20,300,303, down 2.9%", source: "LA Metro, ridership release, 31 October 2025", url: "https://www.metro.net/about/metro-ridership-holds-strong-amid-regional-challenges-driven-by-rail-growth-weekend-travel-improved-safety/", accessed: "260803", confidence: "reported" },
      ],
      trend: "rising",
      change: "rail +1.7% while bus fell 2.9%; rail Saturdays +6.5% and Sundays +9.4% while rail weekdays fell 2.0%",
      strength: "cyclical",
      direction: "for",
      affects: { to: ["food hall", "creative retail", "culture", "museum", "gallery", "event venue", "retail"] },
      reading: "The growth is on rail and at the weekend and it is shrinking on the weekday " +
        "commute. A district people visit on a Saturday is being served better by the network " +
        "every year; a district people commute into is not.",
      caveat: "County-wide, and the 2024 point is derived from a published percentage rather " +
        "than read directly. Rail boardings are a mode share, not a measure of street life."
    },

    // ── event activity ───────────────────────────────────────────────────────────────────
    {
      id: "evt-dodger-stadium",
      stream: "events",
      label: "Four million people a season, 1.5 km uphill",
      unit: "average attendance per home game",
      geography: "venue",
      measures: "Attendance at Dodger Stadium home games. The stadium sits about 1.5 km from the " +
        "parcel and its crowd currently arrives by car and by shuttle from Union Station, so this " +
        "counts people near Chinatown, not people in it.",
      series: [
        { t: "2023", v: 47371, note: "highest in the league, 81 home games", source: "Baseball Reference and league attendance reporting", url: "https://www.baseball-reference.com/teams/LAD/attend.shtml", accessed: "260803", confidence: "reported" },
        { t: "2024", v: 48657, source: "League attendance reporting", url: "https://www.baseball-reference.com/teams/LAD/attend.shtml", accessed: "260803", confidence: "reported" },
        { t: "2025", v: 49537, note: "season total 4,012,470 with 25 sellouts, a franchise first", source: "Dodger Blue and FOX Sports reporting on the 2025 season total", url: "https://dodgerblue.com/dodgers-attendance-4-million-first-time-in-franchise-history-dodger-stadium/2025/09/22/", accessed: "260803", confidence: "reported" },
      ],
      trend: "rising",
      change: "+4.6% average attendance over three seasons, crossing four million for the first time in 2025",
      strength: "cyclical",
      direction: "for",
      affects: { to: ["food hall", "creative retail", "retail", "culture", "hotel", "event venue"] },
      reading: "Eighty-one evenings a year, fifty thousand people converge a mile from this " +
        "parcel and currently pass Chinatown without stopping. Program that gives them a reason " +
        "to stop is the clearest event-driven case this site has.",
      caveat: "Attendance follows the team, which is why this is cyclical and not structural. " +
        "Nothing here measures how many of that crowd currently enter Chinatown, and the honest " +
        "answer is that nobody publishes it.",
      outlook: {
        text: "The proposed aerial gondola from Union Station to Dodger Stadium includes a stop " +
          "in Chinatown near the south-west edge of Los Angeles State Historic Park, and Metro " +
          "says it could move up to 5,000 people an hour in each direction on game days. It is " +
          "contested locally and not built.",
        horizon: "unbuilt, approvals in progress as of the cited reporting",
        source: "LAist and Metro reporting on the gondola project",
        url: "https://laist.com/news/transportation/dodger-stadium-traffic-gondola-walking-paths-buses-what-should-la-do",
        confidence: "reported"
      }
    },

    // ── gentrification ───────────────────────────────────────────────────────────────────
    {
      id: "gen-ct-senior-rent",
      stream: "gentrification",
      label: "A 7.95% rent rise on subsidised senior housing",
      unit: "% annual rent increase",
      geography: "block",
      measures: "The 2025 increase at Metro at Chinatown Senior Lofts, one affordable building. " +
        "It is one property's increase, not a district rent index.",
      series: [
        { t: "2025", v: 7.95, note: "reported as following earlier increases, which were not quantified in the source", source: "LA Public Press, on rent increases outpacing social security in Chinatown affordable housing", url: "https://lapublicpress.org/2026/04/la-chinatown-senior-rent/", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one observation; the earlier increases the source mentions carry no figures",
      strength: "structural",
      direction: "context",
      affects: { to: ["housing", "supportive & affordable housing"] },
      reading: "Rent is rising faster than the incomes of the people it is charged to, inside " +
        "the subsidised stock. A market-rate housing future on this parcel lands on top of that.",
      caveat: "One building, one year, and under the two-observation rule it ranks nothing even " +
        "though it bears directly on a housing future. That is the rule working, not a gap in it. " +
        "A separate study reported in the same coverage puts average rents at the south end of " +
        "Chinatown up $379, with neither the base nor the period stated, so it is not a series " +
        "either and is left out."
    },

    {
      id: "dem-ct-tenure",
      stream: "demographic",
      label: "A neighbourhood of renters, a fifth of them over 65",
      unit: "% of occupied housing that is rented",
      geography: "district",
      measures: "The share of Chinatown households that rent, with the share of residents aged " +
        "65 and over reported alongside it. Both are neighbourhood shares, not parcel figures.",
      series: [
        { t: "2025", v: 94, note: "reported as 94% of occupied housing, with over 95% of residents renters in a second source; 19.9% of residents aged 65 or older", source: "USC Annenberg Media, on senior residents in a shifting Chinatown", url: "https://www.uscannenbergmedia.com/2025/08/14/senior-residents-of-chinatown-navigate-a-shifting-neighborhood/", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one observation; no earlier year on the same basis was retrieved",
      strength: "structural",
      direction: "context",
      affects: { to: ["housing", "supportive & affordable housing"] },
      reading: "Almost nobody here owns, and a fifth of the population is past working age. That " +
        "combination is what makes rent movement in this district a displacement question rather " +
        "than a market one.",
      caveat: "Two sources give 94% and over 95% for the same thing, which is the level of " +
        "precision this figure actually has. One observation, so it ranks nothing."
    },

    // ── market signals ───────────────────────────────────────────────────────────────────
    {
      id: "mkt-dtla-office-vacancy",
      stream: "market",
      label: "Downtown office vacancy stuck around a third",
      unit: "% vacant",
      geography: "submarket",
      measures: "Vacancy across the whole Downtown Los Angeles office submarket as brokerages " +
        "report it. It is not a reading of this parcel and not of Chinatown.",
      series: [
        { t: "2025-Q3", v: 33.3, note: "availability 36.8% the same quarter", source: "Press summary of CoStar downtown office data", url: "https://propmodo.com/playbook/los-angeles-unlocks-citywide-office-to-housing-conversions-with-sweeping-adaptive-reuse-reform/", accessed: "260803", confidence: "reported" },
        { t: "2026-Q1", v: 32.4, note: "reported flat quarter over quarter", source: "Colliers, Downtown Los Angeles Office Research Report 2026 Q1 (page returned HTTP 403 to direct fetch; figure from the search-result summary)", url: "https://www.colliers.com/en/research/los-angeles/downtown-los-angeles-office-research-report-2026-q1", accessed: "260803", confidence: "reported" },
      ],
      trend: "flat",
      change: "33.3% to 32.4% over two quarters, a plateau rather than a recovery",
      strength: "structural",
      direction: "against",
      affects: { to: ["creative office"] },
      reading: "Any office component here competes with a submarket that cannot fill a third of " +
        "the space it already has, and the plateau says that space is not coming back on its own.",
      caveat: "The two points come from two different brokerages and their vacancy definitions " +
        "may differ. Chinatown is at the edge of the submarket these figures cover."
    },

    {
      id: "mkt-adaptive-reuse-pipeline",
      stream: "market",
      label: "Los Angeles is second in the country for adaptive reuse volume",
      unit: "apartments in the adaptive reuse pipeline",
      geography: "city",
      measures: "Apartments in the city's adaptive reuse pipeline, of which office conversions " +
        "are about half. A pipeline is projects announced or under way, not units delivered.",
      series: [
        { t: "2026", v: 5640, note: "2,843 of them office-to-residential, about 50%; Manhattan leads with 11,000", source: "Press reporting on national adaptive reuse rankings, following the Citywide Adaptive Reuse Ordinance", url: "https://propmodo.com/playbook/los-angeles-unlocks-citywide-office-to-housing-conversions-with-sweeping-adaptive-reuse-reform/", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one observation, no earlier pipeline count retrieved",
      strength: "structural",
      direction: "context",
      affects: { to: ["housing", "loft", "mixed-use", "supportive & affordable housing"] },
      reading: "Conversion capacity exists city-wide and has a by-right path since February 2026. " +
        "Whether it reaches this parcel is the boundary question the M9 set already flags.",
      caveat: "One observation, so this ranks nothing. The M9 signal set carries the ordinance " +
        "itself, which is the thing with force."
    },

    // ── surrounding business changes ─────────────────────────────────────────────────────
    {
      id: "biz-ct-succession",
      stream: "business-mix",
      label: "New food arriving into the spaces old food left",
      unit: "named openings in the searched range",
      geography: "district",
      measures: "A count of restaurant openings named in guides for 2025 and 2026, each of them " +
        "taking a space a previous operator vacated. It is a list from a guide, not a turnover " +
        "rate, and closures are not counted on the same basis.",
      series: [
        { t: "2026", v: 3, note: "Firstborn in the former PokPok space, March 2025; Souu LA taking the former Angry Egret Dinette space in Mandarin Plaza; Mitsi at the Chinatown and Mission Junction edge", source: "The Infatuation and Los Angeles restaurant opening guides", url: "https://www.theinfatuation.com/los-angeles/guides/la-restaurant-openings-2026", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one compile, no earlier count on the same basis",
      strength: "anecdotal",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "culture"] },
      reading: "The pattern is replacement, not vacancy: each of these took a space another " +
        "operator had just left. Food space in Chinatown turns over and stays occupied, which is " +
        "a different condition from a district emptying out.",
      caveat: "Guides publish openings, not closures, so this cannot show the other half of the " +
        "churn and must not be read as growth. Three is a count of what a guide mentioned."
    },

    // ── declared gaps ────────────────────────────────────────────────────────────────────
    {
      id: "ret-ct-storefront-churn",
      stream: "retail-turnover",
      label: "No storefront turnover series exists for this district",
      unit: null,
      geography: "district",
      measures: "Nothing. A turnover rate needs openings and closures counted on the same " +
        "footprint over time, and no free source publishes that for Chinatown.",
      series: [],
      trend: "unknown",
      change: "declared gap",
      strength: "anecdotal",
      direction: "context",
      affects: { to: [] },
      reading: "The only available reads are the named openings above and the M9 items on " +
        "storefront attrition and SB 1103 tenant protections. None of them counts a shop.",
      caveat: "Recorded as a gap so the stream is visibly missing rather than silently absent. " +
        "The M9 items point in opposite directions and were deliberately kept that way."
    },

    {
      id: "lse-ct-rents",
      stream: "leasing",
      label: "No commercial rent or vacancy series exists for Chinatown",
      unit: null,
      geography: "district",
      measures: "Nothing. Brokerage series stop at the Downtown submarket, which averages this " +
        "district into towers that have nothing to do with it.",
      series: [],
      trend: "unknown",
      change: "declared gap",
      strength: "cyclical",
      direction: "context",
      affects: { to: [] },
      reading: "The submarket office figure above is the closest thing available, and it is the " +
        "wrong geography for a two-storey commercial street.",
      caveat: "Using the Downtown submarket number as if it described Chinatown storefronts would " +
        "be the fake precision this project's C5 rule exists to prevent."
    },

    {
      id: "soc-ct-attention",
      stream: "social",
      label: "No count of attention to this district exists",
      unit: null,
      geography: "district",
      measures: "Nothing. Instagram, TikTok and X all sell or forbid the data that would answer " +
        "this, and none of them resolve to a parcel.",
      series: [],
      trend: "unknown",
      change: "declared gap",
      strength: "anecdotal",
      direction: "context",
      affects: { to: [] },
      reading: "Chung King Road's gallery nights and Far East Plaza's food tenancies are the " +
        "district's cultural draw and are carried in the M9 set as published claims, which is " +
        "what they are.",
      caveat: "This gap is permanent under the project's own rule: no scraped attention figure " +
        "may be added to this layer later."
    },

  ]
};
