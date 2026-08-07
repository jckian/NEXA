// NEXA/intel/data/signals-citymarket.js
// M9 SITE-SIGNALS — City Market of Los Angeles (Fashion District, DTLA)
// Schema + honesty rules: NEXA/intel/INTEL-DATA.md §6. Prose report: signals-citymarket.md
// Confidence tags per INTEL-DATA.md §1: verified | reported | estimated | unknown.
//
// ⚠ NO SOCIAL-MEDIA METRIC IS IN THIS FILE. No free API sells post volume, hashtag velocity
// or check-in counts for a parcel, so `trend` items below are things a publication SAID about
// this district, not measurements of attention. Nothing here may be read as popularity or
// footfall. Two of the `market` items ride on press summaries of CoStar/Gensler reports that
// were not themselves read; they are `reported`, not `verified`.

window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.signals = window.NEXA_INTEL.signals || {};

window.NEXA_INTEL.signals["citymarket-la"] = {

  meta: {
    site: "citymarket-la",
    district: "Fashion District, Downtown Los Angeles",
    // Estimated from the block bounded by 9th / San Pedro / 12th / San Julian. The dossier
    // carries no parcel geometry, so this is a centre-of-block guess, not a survey.
    where: { lat: 34.0362, lon: -118.2528, radiusM: 900, confidence: "estimated" },
    compiled: "260802",
    method: "Web search session 260802: LA City Planning and LA Conservancy for the Citywide " +
      "Adaptive Reuse Ordinance; Urbanize LA's City Market tag index for the project's own press " +
      "record; press summaries of CoStar / Gensler downtown office data; LA28 venue and " +
      "accommodation reporting; Metro and FTA pages for the Southeast Gateway Line; district " +
      "travel guides and The Infatuation for street-level trend items.",
    limits: "This layer has no measurement in it. There is no free source for social-media " +
      "attention, footfall or trade area at parcel resolution, so the trend and landmark items " +
      "are published claims about a district, not counts. The LA City Planning ordinance PDF " +
      "returned HTTP 403 to direct fetch, so ordinance figures come from the LA Conservancy " +
      "summary. Items go stale: this set was compiled 260802 and nothing refreshes it " +
      "automatically."
  },

  items: [

    {
      id: "pol-citywide-aro-2026",
      channel: "policy",
      label: "Citywide Adaptive Reuse Ordinance in effect since 1 Feb 2026",
      detail: "Ordinance 188793, approved by City Council in December 2025, effective 1 February 2026. " +
        "Buildings at least 15 years old convert to residential by right; 5 to 15 years old by " +
        "Zoning Administrator conditional use. Minimum unit sizes cut, off-street parking " +
        "eliminated, open space and landscaping exempted. The Adaptive Reuse Areas Specific Plan " +
        "was repealed at the same time, so the geographic limits are gone. The ordinance also " +
        "carries incentives to retain legacy small businesses and commercial tenants.",
      date: "2026-02",
      strength: "structural",
      direction: "for",
      // residential conversion only. The ordinance is a housing instrument; it does not make a
      // creative-office future easier, and listing it there would have read as support the
      // ordinance does not give.
      affects: { to: ["housing", "loft", "artist studio", "supportive & affordable housing"], from: [] },
      basis: "The conversion path this site's found industrial volumes would take is now a by-right " +
        "one with no parking to build. That is a rule change, not a market mood.",
      source: "LA Conservancy, Citywide Adaptive Reuse Ordinance page (LA City Planning's own Feb 2026 press release PDF returned HTTP 403 to direct fetch)",
      url: "https://www.laconservancy.org/save-places/at-a-glance-policies-for-neighborhoods/citywide-adaptive-reuse-ordinance-aro/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "pol-fashion-district-conversion",
      channel: "policy",
      label: "Adaptive reuse streamlined in parts of the Fashion District; IX2 opened to residential conversion",
      detail: "Reporting on the ordinance says conversions are streamlined in parts of the Fashion " +
        "District, and that the IX2 use district will permit converting existing buildings to " +
        "residential, with office conversions allowed where they take only a share of the building. " +
        "This parcel's mapped use district is IX3, not IX2 (GeoHub query, 260713), so whether the " +
        "carve-out reaches this block is unresolved.",
      date: "2026-02",
      strength: "structural",
      direction: "for",
      affects: { to: ["housing", "mixed-use", "loft"], from: [] },
      basis: "The 260712 dossier recorded a standing tension between a housing-led programme and " +
        "the district's industrial zoning. This is the first policy movement in the other " +
        "direction. Read it as district-level: the parcel is mapped IX3 and the carve-out is " +
        "reported for IX2.",
      source: "Search-snippet reporting on the Citywide ARO's Fashion District provisions; LA City Planning Exhibit F.2 (Analysis for the Fashion Industry in Downtown) not read in full",
      url: "https://planning.lacity.gov/odocument/bfd269ba-61e6-4a76-afb8-eb1b5b98ec9f/Exhibit_F.2.pdf",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "mkt-dtla-office-collapse",
      channel: "market",
      label: "Downtown office vacancy 33.3% at end of Q3 2025",
      detail: "Downtown LA office vacancy reported at 33.3% with availability 36.8% at the end of " +
        "Q3 2025. Around 40% of Financial District office space and about 30% of downtown retail " +
        "space reported empty, and roughly 1,000 businesses left downtown during 2024.",
      date: "2025-09",
      strength: "cyclical",
      direction: "against",
      affects: { to: ["creative office"], from: [] },
      basis: "The dossier's 2025 figure was 22.0% vacancy. The later reporting is half again as " +
        "high. A creative-office future here is being written into a district that cannot fill " +
        "the office it already has.",
      source: "Press summaries of CoStar and Gensler downtown reporting (Tolj Commercial 2026 market note; Latination summary of the Gensler 2026 report). Neither underlying report was read.",
      url: "https://toljcommercial.com/downtown-la-office-amenities-2026/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "mkt-office-to-housing-wave",
      channel: "market",
      label: "Downtown office towers converting to housing at scale",
      detail: "Jamison Properties is converting the 32-storey L.A. Care tower at 1055 W. 7th Street " +
        "into 686 apartments, with a first phase of 241 affordable units starting August 2026. " +
        "Reported as one of several downtown-adjacent towers being redrawn as housing after " +
        "failing to hold office tenants.",
      date: "2026-07",
      strength: "cyclical",
      direction: "for",
      affects: { to: ["housing", "supportive & affordable housing", "loft"], from: [] },
      basis: "The conversion is happening at tower scale, not as a pilot, which is what makes the " +
        "ordinance above a live instrument rather than a paper one.",
      source: "Planetizen, July 2026",
      url: "https://www.planetizen.com/news/2026/07/137939-vacant-downtown-la-office-building-will-be-transformed-512-affordable-homes",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "news-citymarket-press-silence",
      channel: "news",
      label: "No City Market coverage found after March 2024",
      detail: "Urbanize LA's City Market tag index runs 2014 to 11 March 2024 and stops. The last " +
        "item is the Council's approval of the revised development agreement. Nothing on a " +
        "construction start, a phasing change or a sale appeared in the searched range, which " +
        "ended 2 August 2026.",
      date: "2024-03",
      strength: "cyclical",
      direction: "against",
      affects: { to: ["mixed-use campus", "housing", "hotel"], from: [] },
      basis: "A 20-year development agreement with no press for two and a half years is weak " +
        "evidence for a near-horizon build-out. An absence of coverage is not an absence of " +
        "activity: one publication's index is all that was searched.",
      source: "Urbanize LA, City Market tag index (fetched and read, 260802)",
      url: "https://la.urbanize.city/tags/city-market",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "civ-la28-games",
      channel: "civic",
      label: "LA28 puts five Olympic sports in the Convention Center, about 1 km from the site",
      detail: "The Convention Center hosts fencing, judo, table tennis, taekwondo and wrestling in " +
        "2028; the Games build no new permanent venues. The IOC projects roughly 10 million " +
        "ticketed sessions and 3 to 5 million unique visitors, modelled at about 7.4 million " +
        "room-nights compressed into a 17-day Olympic and 12-day Paralympic window, with peak " +
        "occupancy approaching capacity across all hotel categories.",
      date: "2026-02",
      strength: "structural",
      direction: "for",
      affects: { to: ["hotel", "event venue", "food hall", "creative retail", "retail"], from: [] },
      basis: "A fixed date with a fixed venue a kilometre away. The same reporting warns that " +
        "hospitality capacity built in anticipation can underperform once the Games leave, so " +
        "this argues for a peak, not a plateau.",
      source: "LA28 venue plan; Airbnb / IOC accommodation modelling (Feb 2026); Los Angeles Hospitality Authority outlook",
      url: "https://la28.org/en/games-plan/venues.html",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "civ-southeast-gateway-works",
      channel: "civic",
      label: "Southeast Gateway Line advance works start 2026, opening 2035",
      detail: "Metro's Southeast Gateway Line begins advanced and early works construction in 2026, " +
        "with nine new stations in Phase 1 and an opening projected for 2035. The dossier records " +
        "a planned Fashion District station near 8th and Los Angeles Street; that station's own " +
        "status was not confirmed in this search.",
      date: "2026-01",
      strength: "structural",
      direction: "for",
      affects: { to: ["housing", "mixed-use campus", "mixed-use", "food hall"], from: [] },
      basis: "A funded line moving from planning into construction inside the horizon this " +
        "forecast covers. It is the strongest dated argument for density on this block after " +
        "the ordinance.",
      source: "LA Metro Southeast Gateway Line project page; FTA project profile; Metro Board report 2025-0007",
      url: "https://www.metro.net/projects/southeastgateway/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "land-santee-alley-market-street",
      channel: "landmark",
      label: "The district's public draw is street retail, not an institution",
      detail: "Santee Alley's open-air bazaar, the California Market Center's trade shows and " +
        "Gallery Row's exhibitions are what district guides send visitors to. There is no museum, " +
        "campus or civic anchor in the guides' account of the Fashion District.",
      date: "2026-01",
      strength: "anecdotal",
      direction: "for",
      affects: { to: ["food hall", "creative retail", "retail"], from: [] },
      basis: "Travel-guide copy is the source, so this is what the district is marketed as, not " +
        "what is counted in it. It matches the 260729 ring read, where learning and culture came " +
        "back thin.",
      source: "Expedia and Tripadvisor Fashion District guides, 2026 editions",
      url: "https://www.expedia.com/Los-Angeles-Fashion-District.dx6156075",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "trend-evening-use-arriving",
      channel: "trend",
      label: "Evening and leisure uses opening in a wholesale district",
      detail: "Skyduster Brewing opened its first permanent location in the Fashion District as an " +
        "indoor-outdoor beer garden and sports bar with a rotating food pop-up. Restaurant guides " +
        "record new bars, lofts and hotels appearing across Downtown on a continuing basis.",
      date: "2026-03",
      strength: "anecdotal",
      direction: "for",
      affects: { to: ["food hall", "creative retail", "event venue"], from: [] },
      basis: "One opening is one opening. It is listed because the dossier's own risk note for the " +
        "event scenario was that wholesale truck traffic blocks evening programming, and this is " +
        "the first dated counter-example found.",
      source: "The Infatuation, LA new restaurant openings guide",
      url: "https://www.theinfatuation.com/los-angeles/guides/new-la-restaurants-openings",
      accessed: "260802",
      confidence: "reported"
    }

  ]
};
