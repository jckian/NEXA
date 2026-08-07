// NEXA/intel/data/dynamics-citymarket.js
// M10 SITE-DYNAMICS — City Market of Los Angeles (Fashion District, DTLA)
// Schema + honesty rules: NEXA/intel/INTEL-DATA.md §7. Prose report: dynamics-citymarket.md
// Confidence tags per INTEL-DATA.md §1: verified | reported | estimated | unknown.
//
// ⚠ THE TWO-OBSERVATION RULE (§7). A metric with fewer than two dated observations carries
// trend "unknown", is forced to direction "context" and ranks nothing. One dated number is a
// fact about today, which is M1's job or M9's. Only a series carries a direction of travel.
//
// ⚠ NO SOCIAL-MEDIA METRIC IS IN THIS FILE. `soc-fd-attention` is a DECLARED GAP: the layer
// says out loud that no count of attention to this block exists in a free source, rather than
// substituting the BID's own follower numbers, which measure the BID's audience.
//
// ⚠ Placer.ai figures are a sampled mobile-location panel extrapolated to a 107-block business
// improvement district and published by that district's own BID. They are `reported`, they are
// a district estimate, and they are not a count of people on the sidewalk outside this parcel.

window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.dynamics = window.NEXA_INTEL.dynamics || {};

window.NEXA_INTEL.dynamics["citymarket-la"] = {

  meta: {
    site: "citymarket-la",
    district: "Fashion District, Downtown Los Angeles",
    // Same centre-of-block estimate the M9 signal set uses, so one typed address picks up both
    // layers or neither. The dossier still carries no parcel geometry.
    where: { lat: 34.0362, lon: -118.2528, radiusM: 900, confidence: "estimated" },
    compiled: "260803",
    method: "Web search session 260803. The LA Fashion District BID Q2 2025 Trend Report (PDF, " +
      "text extracted locally) for district visitation, dwell and visitor demography, all of it " +
      "Placer.ai panel data the BID publishes. LA Metro's October 2025 ridership release for " +
      "county boardings and the Pico Station event-day figure. Press summaries of Colliers and " +
      "CoStar downtown office data for submarket vacancy. RentCafe-derived press reporting for " +
      "the adaptive reuse pipeline. DTLA Alliance and Downtown News reporting for the resident " +
      "population series. A broker market page for DTLA retail, read only as a search-result " +
      "summary.",
    limits: "Every number here was measured somewhere larger than this parcel: a 107-block " +
      "business improvement district, the Downtown office submarket, the city, or the county. " +
      "The visitation figures are a sampled phone panel extrapolated by a vendor, not a count " +
      "of people. The newest district visitation reading is Q2 2025: later BID trend reports " +
      "returned HTTP 403 and could not be retrieved, so the freshest pedestrian series here is " +
      "already a year old. Three of the nine streams are declared gaps with no number at all. " +
      "Nothing refreshes automatically. Compiled 260803."
  },

  metrics: [

    // ── pedestrian movement ──────────────────────────────────────────────────────────────
    {
      id: "ped-fd-visits",
      stream: "pedestrian",
      label: "District visits down 14% year over year",
      unit: "visits per quarter",
      geography: "district",
      measures: "Placer.ai's estimate of total visits to the LA Fashion District BID's 107-block " +
        "area, which runs 7th Street to the 10 Freeway and Broadway to Paloma. This parcel sits " +
        "inside that area. It is a phone-panel estimate for a district, not a count at a door.",
      series: [
        { t: "2024-Q2", v: 5700000, source: "LA Fashion District BID, Q2 2025 Trend Report (benchmark quarter)", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
        { t: "2025-Q2", v: 4900000, source: "LA Fashion District BID, Q2 2025 Trend Report, Placer.ai", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
      ],
      trend: "falling",
      change: "-14% year over year; unique visitors 2.9m to 2.5m, visit frequency flat at 1.93",
      strength: "cyclical",
      direction: "against",
      affects: { to: ["food hall", "creative retail", "retail", "culture"] },
      reading: "A food-hall or creative-retail future for this building is a bet on district " +
        "footfall, and district footfall fell while the number of trips each visitor makes stayed " +
        "flat. Fewer people came, not fewer times each.",
      caveat: "Panel data, not a count, and the drop is concentrated in one month with a stated " +
        "cause. See the monthly breakdown and the June shock below before reading this as a trend " +
        "in demand.",
      outlook: {
        text: "The BID expected a seasonal summer decline and an uptick from around mid-September " +
          "2025, which it said would show in its Q3 report. That report could not be retrieved.",
        horizon: "2025-Q3",
        source: "LA Fashion District BID, Q2 2025 Trend Report",
        url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf",
        confidence: "reported"
      }
    },

    {
      id: "ped-fd-monthly",
      stream: "pedestrian",
      label: "The fall is one month, not three",
      unit: "visits per month",
      geography: "district",
      measures: "The same Placer.ai district panel as above, broken out by month with each " +
        "month's own year-over-year change.",
      series: [
        { t: "2025-04", v: 1700000, note: "-7.2% year over year", source: "LA Fashion District BID, Q2 2025 Trend Report, Placer.ai", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
        { t: "2025-05", v: 1900000, note: "-3.8% year over year", source: "LA Fashion District BID, Q2 2025 Trend Report, Placer.ai", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
        { t: "2025-06", v: 1200000, note: "-32.5% year over year, the largest drop in the series", source: "LA Fashion District BID, Q2 2025 Trend Report, Placer.ai", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
      ],
      trend: "volatile",
      change: "April -7.2%, May -3.8%, June -32.5% year over year",
      strength: "cyclical",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "retail"] },
      reading: "April and May were close to normal. June collapsed. A quarterly average hides " +
        "that, and a program decision made on the average would be made on the wrong number.",
      caveat: "This is the same panel as the quarterly metric above, split by month, so it is " +
        "carried as context and ranks nothing. Counting both would count one dataset twice."
    },

    {
      id: "ped-fd-rhythm",
      stream: "pedestrian",
      label: "A lunchtime and Saturday district, 95 minutes a visit",
      unit: "minutes per visit",
      geography: "district",
      measures: "Average visit duration across the district in Q2 2025, with the peak hour and " +
        "peak day the same panel reports.",
      series: [
        { t: "2025-Q2", v: 95, note: "peak hour 12 PM, peak day Saturday", source: "LA Fashion District BID, Q2 2025 Trend Report, Placer.ai", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one observation, no earlier quarter retrieved",
      strength: "anecdotal",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "retail", "culture"] },
      reading: "A 95-minute midday visit peaking on Saturday is a shopping and eating rhythm, " +
        "not a workplace one. Program that only opens Monday to Friday misses the district's " +
        "busiest hour.",
      caveat: "One observation, so this ranks nothing under the two-observation rule."
    },

    // ── event activity ───────────────────────────────────────────────────────────────────
    {
      id: "evt-pico-eventday",
      stream: "events",
      label: "Event days lift the nearest station 65%",
      unit: "% above non-event days",
      geography: "venue",
      measures: "The change in boardings at Pico Station, the Metro stop serving the Los Angeles " +
        "Convention Center about 1 km from this parcel, during LA Comic Con on 26 to 28 September " +
        "2025, compared with non-event days. It measures boardings at one station, not people on " +
        "this block.",
      series: [
        { t: "2025-09", v: 65, source: "LA Metro, ridership release, 31 October 2025", url: "https://www.metro.net/about/metro-ridership-holds-strong-amid-regional-challenges-driven-by-rail-growth-weekend-travel-improved-safety/", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one event, one comparison",
      strength: "anecdotal",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "event venue", "hotel", "culture"] },
      reading: "The convention calendar is a real and repeating demand pulse this end of Downtown, " +
        "and it arrives by rail. Program that can expand and contract with it is worth more here " +
        "than program sized to an average day.",
      caveat: "One event day against an unnamed baseline, at a station 1 km away. It shows the " +
        "mechanism, not its size at this parcel.",
      outlook: {
        text: "LA28 puts events at the Convention Center about 1 km from this parcel, and the " +
          "BID was already planning district branding around the 2026 World Cup in its Q2 2025 " +
          "report. That tournament has since taken place and no post-event reading was retrieved " +
          "for this compile, so its actual effect on the district is unmeasured here.",
        horizon: "2026 to 2028",
        source: "LA Fashion District BID Q2 2025 Trend Report; LA28 venue reporting (see M9 signals)",
        url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf",
        confidence: "reported"
      }
    },

    // ── market signals ───────────────────────────────────────────────────────────────────
    {
      id: "mkt-dtla-office-vacancy",
      stream: "market",
      label: "Downtown office vacancy stuck around a third",
      unit: "% vacant",
      geography: "submarket",
      measures: "Vacancy across the whole Downtown Los Angeles office submarket as brokerages " +
        "report it. It is not a reading of this parcel and not of the Fashion District.",
      series: [
        { t: "2025-Q3", v: 33.3, note: "availability 36.8% the same quarter", source: "Press summary of CoStar downtown office data", url: "https://propmodo.com/playbook/los-angeles-unlocks-citywide-office-to-housing-conversions-with-sweeping-adaptive-reuse-reform/", accessed: "260803", confidence: "reported" },
        { t: "2026-Q1", v: 32.4, note: "reported flat quarter over quarter", source: "Colliers, Downtown Los Angeles Office Research Report 2026 Q1 (page returned HTTP 403 to direct fetch; figure from the search-result summary)", url: "https://www.colliers.com/en/research/los-angeles/downtown-los-angeles-office-research-report-2026-q1", accessed: "260803", confidence: "reported" },
      ],
      trend: "flat",
      change: "33.3% to 32.4% over two quarters, a plateau rather than a recovery",
      strength: "structural",
      direction: "against",
      affects: { to: ["creative office"] },
      reading: "A creative-office future for these volumes is being proposed into a submarket " +
        "that cannot fill a third of the space it already has, and the plateau says the space is " +
        "not coming back on its own.",
      caveat: "The two points come from two different brokerages and their vacancy definitions " +
        "may differ. The site dossier carries an earlier and much lower reading of 22.0%, whose " +
        "basis and date were never reconciled with these, so it is left out of the series rather " +
        "than spliced in."
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
      reading: "Conversion here would not be an experiment. It would join a city-wide pipeline " +
        "that already has contractors, lenders and a by-right path through the new ordinance.",
      caveat: "One observation, so this ranks nothing. The M9 signal set already carries the " +
        "ordinance itself, which is the thing with force.",
      outlook: {
        text: "The Citywide Adaptive Reuse Ordinance is expected to generate roughly 4,400 " +
          "additional housing units across the city.",
        horizon: "unstated",
        source: "Press reporting on Ordinance 188793",
        url: "https://therealdeal.com/la/2026/02/13/los-angeles-enacts-commercial-to-housing-conversion-law/",
        confidence: "reported"
      }
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
      reading: "The growth is on rail and at the weekend, and it is shrinking on the weekday " +
        "commute. That favours program people travel to by choice over program they are " +
        "contractually required to show up at.",
      caveat: "County-wide, and the 2024 point is derived from a published percentage rather " +
        "than read directly. Rail boardings are a mode share, not a measure of street life."
    },

    // ── leasing ──────────────────────────────────────────────────────────────────────────
    {
      id: "lse-dtla-retail",
      stream: "leasing",
      label: "Downtown retail rents reset from the 2023 peak",
      unit: "$ per sq ft asking, basis not stated in the source",
      geography: "submarket",
      measures: "Asking retail rent across Downtown Los Angeles as a broker's market page " +
        "describes it. Neither the lease basis nor the period was stated in what could be read.",
      series: [
        { t: "2026-Q1", v: 3.00, note: "described as stabilising around this level after softening from a 2023 peak", source: "illi Commercial Real Estate, Los Angeles market report (read only as a search-result summary; the page itself was not fetched)", url: "https://illicre.com/market-reports/market-losangeles/", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one usable observation, so no trend is claimed here",
      strength: "cyclical",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "retail"] },
      reading: "The prose behind this number says Downtown retail vacancy climbed through 2024 " +
        "and 2025 and steadied in the most recent quarter, with leasing arriving in bursts rather " +
        "than steadily. Ground-floor program here should be priced against a reset market, not " +
        "the 2023 one.",
      caveat: "The underlying series was never obtained, only a broker's prose summary of it, " +
        "and the rent basis is unknown. Under the two-observation rule this ranks nothing. It is " +
        "in the set so the gap is visible rather than silent."
    },

    // ── demographic change ───────────────────────────────────────────────────────────────
    {
      id: "dem-dtla-residents",
      stream: "demographic",
      label: "Downtown gained 41% more residents since 2010",
      unit: "residents",
      geography: "submarket",
      measures: "Residential population of Downtown Los Angeles as the district's own alliance " +
        "reports it. Downtown is far larger than this district and much larger than this parcel.",
      series: [
        { t: "2010", v: 63800, note: "derived from the reported 90,000 and the +41% change; not a published 2010 figure", source: "DTLA Alliance figures as reported by Downtown LA", url: "https://downtownla.com/business/residential", accessed: "260803", confidence: "estimated" },
        { t: "2024", v: 90000, note: "almost 25,000 residential units delivered since 2010, 26% of the city's total", source: "DTLA Alliance, DTLA Outlook and Insights, via LA Downtown News", url: "https://downtownla.com/business/residential", accessed: "260803", confidence: "reported" },
      ],
      trend: "rising",
      change: "+41% over about fourteen years, with a quarter of the city's new housing landing here",
      strength: "structural",
      direction: "for",
      affects: { to: ["housing", "mixed-use", "loft", "supportive & affordable housing", "food hall", "creative retail"] },
      reading: "The population that would use a housing or ground-floor food future here has been " +
        "arriving steadily for over a decade, and Downtown has absorbed a quarter of the city's " +
        "new units doing it.",
      caveat: "Reported by the business improvement organisation that benefits from the number, " +
        "and the 2010 point is derived from a percentage. Downtown-wide, not this district.",
      outlook: {
        text: "SCAG projects 125,000 more residents, 70,000 more housing units and 55,000 more " +
          "jobs in Downtown Los Angeles by 2040.",
        horizon: "2040",
        source: "SCAG growth forecast as reported by Urban Land Magazine",
        url: "https://urbanland.uli.org/development-and-construction/growth-spurt-l-a-s-ambitious-downtown-plan-balances-a-future-of-new-uses",
        confidence: "reported"
      }
    },

    {
      id: "dem-fd-visitor",
      stream: "demographic",
      label: "The district's visitor earns $65k, not $95k",
      unit: "$ median household income of visitors",
      geography: "district",
      measures: "Median household income of the panel Placer.ai identifies as visiting the " +
        "district in Q2 2025, alongside the average of the same panel. It describes who comes " +
        "to shop, not who lives here.",
      series: [
        { t: "2025-Q2", v: 65000, note: "average $93,000; median visitor age 33; 63% Latino, 13.3% white, 11.1% Black, 9.2% Asian; 91.7% employed; 44.7% non-family households", source: "LA Fashion District BID, Q2 2025 Trend Report, Placer.ai", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "one observation, no earlier quarter retrieved",
      strength: "anecdotal",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "retail", "housing"] },
      reading: "A conversion pro forma here usually assumes the high-income creative-office " +
        "worker. The people actually coming to this district are working shoppers at a $65,000 " +
        "median, and the gap between median and average says the high earners are a tail.",
      caveat: "One observation, so this ranks nothing. Panel demography is modelled from device " +
        "home locations, not asked."
    },

    // ── business-mix ─────────────────────────────────────────────────────────────────────
    {
      id: "biz-fd-june-2025",
      stream: "business-mix",
      label: "June 2025: enforcement activity, protests, and a third of the footfall gone",
      unit: "% year-over-year change in monthly visits",
      geography: "district",
      measures: "The district's own account of why its June 2025 visits fell 32.5%, published " +
        "in the same report as the number.",
      series: [
        { t: "2025-06", v: -32.5, note: "the BID ties the drop to federal immigration enforcement activity and the protests against it in Downtown", source: "LA Fashion District BID, Q2 2025 Trend Report", url: "https://ctycms.com/ca-fashion-district/docs/trend-report-q2-2025-web.pdf", accessed: "260803", confidence: "reported" },
      ],
      trend: "unknown",
      change: "a single shock, recovery unmeasured in this set",
      strength: "cyclical",
      direction: "context",
      affects: { to: ["food hall", "creative retail", "retail"] },
      reading: "Many of the district's businesses are immigrant and family owned, and the BID " +
        "answered with recovery campaigns rather than treating the drop as demand. Retail program " +
        "here carries a political exposure that a vacancy rate will not show.",
      caveat: "One month, and the report was published while it was still happening. No recovery " +
        "reading exists in this set because the later trend reports could not be retrieved."
    },

    // ── declared gaps: streams this layer was asked to carry and cannot measure ───────────
    {
      id: "ret-fd-storefront-churn",
      stream: "retail-turnover",
      label: "No storefront turnover series exists for this district",
      unit: null,
      geography: "district",
      measures: "Nothing. A turnover rate needs storefront openings and closures counted on the " +
        "same footprint over time, and no free source publishes that for the Fashion District.",
      series: [],
      trend: "unknown",
      change: "declared gap",
      strength: "anecdotal",
      direction: "context",
      affects: { to: [] },
      reading: "The nearest available reads are the district's visit series above and the M9 " +
        "signal items, and neither of them counts a shop opening or closing.",
      caveat: "Los Angeles publishes active business registrations, but not as a district time " +
        "series that could be differenced, and reconstructing one was out of scope for this " +
        "compile. Recorded as a gap so the stream is visibly missing rather than silently absent."
    },

    {
      id: "gen-fd-displacement",
      stream: "gentrification",
      label: "No displacement measure fits a wholesale district",
      unit: null,
      geography: "district",
      measures: "Nothing. The standard indicators are household ones: rent burden, tenure change, " +
        "median rent. The displacement pressure around this parcel falls mostly on garment and " +
        "wholesale businesses, and no free dataset tracks commercial tenant displacement here.",
      series: [],
      trend: "unknown",
      change: "declared gap",
      strength: "structural",
      direction: "context",
      affects: { to: [] },
      reading: "This is a real exposure, not an absent one. The M9 set carries the ordinance's " +
        "legacy small business retention incentives, which exist because the pressure does.",
      caveat: "Applying a residential gentrification index to a wholesale district would produce " +
        "a number that means nothing. Left empty on purpose."
    },

    {
      id: "soc-fd-attention",
      stream: "social",
      label: "No count of attention to this block exists",
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
      reading: "The BID publishes its own follower counts and social reach. Those measure the " +
        "BID's audience, not the district's, and they are deliberately not carried here.",
      caveat: "This gap is permanent under the project's own rule: no scraped attention figure " +
        "may be added to this layer later. The M9 trend items remain the only social read, and " +
        "they are published claims, not counts."
    },

  ]
};
