// NEXA/intel/data/signals-collegest.js
// M9 SITE-SIGNALS — 130 W. College Street (Chinatown, Los Angeles)
// Schema + honesty rules: NEXA/intel/INTEL-DATA.md §6. Prose report: signals-collegest.md
// Confidence tags per INTEL-DATA.md §1: verified | reported | estimated | unknown.
//
// ⚠ NO SOCIAL-MEDIA METRIC IS IN THIS FILE. `trend` and `landmark` items are things a
// publication SAID about this district, not measurements of attention. Nothing here may be
// read as popularity or footfall.
// ⚠ BOUNDARY CAVEAT, applies to the CASP item: the parcel is mapped with a DTLA 2040 code
// ([DM2-G1-5][CX2-FA][CPIO], GeoHub query 260713), which suggests it sits in the Downtown
// plan area rather than inside the Cornfield Arroyo Seco Specific Plan boundary. Whether the
// CASP update reaches this parcel was NOT established. The item says so on its face.

window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.signals = window.NEXA_INTEL.signals || {};

window.NEXA_INTEL.signals["130-college-st"] = {

  meta: {
    site: "130-college-st",
    district: "Chinatown, Los Angeles",
    // Estimated from the address, not surveyed: the dossier carries no parcel geometry and
    // the project is an assemblage across College, Bruno and N. Main Streets.
    where: { lat: 34.0641, lon: -118.2367, radiusM: 800, confidence: "estimated" },
    compiled: "260802",
    method: "Web search session 260802: LA City Planning for the Cornfield Arroyo Seco Specific " +
      "Plan update and the Citywide Adaptive Reuse Ordinance; Urbanize LA and LA Downtown News " +
      "for the project's own press record and for College Station; LA Public Press, USC Center " +
      "for Health Journalism and Prism for tenant and small-business reporting; Public Counsel " +
      "and legal alerts for SB 1103; gallery, food and district guides for landmarks.",
    limits: "This layer has no measurement in it. No free source gives social-media attention, " +
      "footfall or trade area at parcel resolution, so the trend and landmark items are " +
      "published claims about a district. The CASP boundary question above is unresolved and " +
      "the update's adoption status was not confirmed past the Planning Commission vote. The " +
      "site dossier this sits beside contains almost no verified-tier facts and its research " +
      "was cut short by an outage; that warning still stands. Compiled 260802, nothing " +
      "refreshes it automatically."
  },

  items: [

    {
      id: "pol-casp-update",
      channel: "policy",
      label: "Cornfield Arroyo Seco plan update rezones Main Street land in Chinatown for housing",
      detail: "The CASP update covers roughly 660 acres around the LA River and LA State Historic " +
        "Park in Chinatown and Lincoln Heights. It grows the Urban Village zone from 19% to 28% " +
        "of the plan area, 132 acres, largely by converting Urban Innovation land along Main and " +
        "Naud Streets in Chinatown; it removes the ban on purely residential buildings in Urban " +
        "Village; and it adds a Community Benefits Programme. The environmental report puts the " +
        "plan area's capacity at up to 36,000 residents and over 10,000 jobs, against about " +
        "6,000 residents and 5,400 jobs today. It cleared the City Planning Commission on 7 " +
        "December; Council adoption was not confirmed in this search.",
      date: "2023-12",
      strength: "structural",
      direction: "for",
      affects: { to: ["housing", "mixed-use", "any occupied program"], from: [] },
      basis: "Whether the boundary reaches this parcel is unestablished — the parcel is mapped " +
        "with a DTLA 2040 code, which points to the Downtown plan area instead. Read this as the " +
        "policy direction of the blocks one street over on Main, not as a rule that governs here.",
      source: "LA City Planning CASP Update page; Urbanize LA coverage of the Planning Commission vote",
      url: "https://planning.lacity.gov/plans-policies/casp-update",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "pol-citywide-aro-2026",
      channel: "policy",
      label: "Citywide Adaptive Reuse Ordinance in effect since 1 Feb 2026; Chinatown's designated-area status repealed",
      detail: "Ordinance 188793, approved December 2025, effective 1 February 2026. Buildings at " +
        "least 15 years old convert to residential by right, 5 to 15 years by conditional use; " +
        "minimum unit sizes cut, off-street parking eliminated, open space exempted. The Adaptive " +
        "Reuse Areas Specific Plan, which had confined the programme to downtown, Hollywood, " +
        "Koreatown and Chinatown, was repealed at the same time.",
      date: "2026-02",
      strength: "structural",
      direction: "context",
      affects: { to: ["housing", "loft", "artist studio", "supportive & affordable housing"], from: [] },
      basis: "This parcel is a surface parking lot with no building on it, so a conversion " +
        "ordinance does not reach it. It is listed because it changes what the surrounding " +
        "building stock is worth doing, which is what the competition for a new-build here is.",
      source: "LA Conservancy, Citywide Adaptive Reuse Ordinance page; Greenberg Glusker and Propmodo summaries",
      url: "https://www.laconservancy.org/save-places/at-a-glance-policies-for-neighborhoods/citywide-adaptive-reuse-ordinance-aro/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "pol-sb1103-commercial-tenants",
      channel: "policy",
      label: "SB 1103 gives small commercial tenants lease protections from 1 Jan 2025",
      detail: "California's Commercial Tenant Protection Act, enacted 2024 and effective 1 January " +
        "2025, extends protections to qualified commercial tenants: microenterprises, restaurants " +
        "under 10 employees, nonprofits under 20. It requires translated leases where the " +
        "negotiation was in Chinese, Spanish, Tagalog, Vietnamese or Korean, and reporting has " +
        "described it as a lifeline for immigrant-owned businesses in Chinatown specifically.",
      date: "2025-01",
      strength: "structural",
      direction: "for",
      affects: { to: ["food hall", "creative retail", "retail"], from: [] },
      basis: "Ground-floor retail let to small independent tenants is now a more durable tenancy " +
        "than it was, which is the tenancy this district's ground floor actually has.",
      source: "Public Counsel legislative alert on SB 1103; Prism Reports, Jan 2025",
      url: "https://publiccounsel.org/publications/sb-1103-commercial-lease-protection-small-business-california/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "civ-chinatown-displacement-organizing",
      channel: "civic",
      label: "Organized opposition to market-rate housing on the adjacent block",
      detail: "College Station, at Spring and College one block away, was approved by City Council " +
        "with 725 units and 51,600 sf of retail but without the 37 very-low-income units the " +
        "Planning Commission had recommended, substituted by a $2 million in-lieu contribution " +
        "and $500,000 over ten years toward a rent increase at the Metro @ Chinatown Senior " +
        "Lofts. In 2026, Chinatown tenants in tax-credit buildings not covered by the city's rent " +
        "stabilization ordinance are organizing with Chinatown Community for Equitable " +
        "Development over rent increases outpacing social security.",
      date: "2026-04",
      strength: "structural",
      direction: "against",
      affects: { to: ["housing", "mixed-use"], from: [] },
      basis: "This is the nearest comparable entitlement to this parcel and it cost an " +
        "affordability fight. A housing future here inherits that condition rather than avoiding " +
        "it.",
      source: "Urbanize LA on the College Station approval; LA Public Press, April 2026, on Chinatown senior rents",
      url: "https://lapublicpress.org/2026/04/la-chinatown-senior-rent/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "news-collegest-project-quiet",
      channel: "news",
      label: "The site's own office project has no coverage after June 2024",
      detail: "The Riboli family's 130 College Street proposal with Grimshaw — five storeys, " +
        "225,000 sf of office over 8,200 sf of ground-floor commercial, next to the Metro A Line " +
        "Chinatown station — was last reported moving through environmental review in June 2024. " +
        "Nothing on entitlement, financing or a construction start appeared in the searched " +
        "range, which ended 2 August 2026.",
      date: "2024-06",
      strength: "cyclical",
      direction: "against",
      affects: { to: ["creative office"], from: [] },
      basis: "Two years of silence on a speculative office building, in the office market the " +
        "next item describes. An absence of coverage is not an absence of activity, but it is " +
        "not evidence of one either.",
      source: "Urbanize LA and LA YIMBY coverage of 130 W. College Street; project site 130college.com not read",
      url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "mkt-dtla-office-collapse",
      channel: "market",
      label: "Downtown office vacancy 33.3% at end of Q3 2025",
      detail: "Downtown LA office vacancy reported at 33.3% with availability 36.8% at the end of " +
        "Q3 2025, around 40% of Financial District space empty, and roughly 1,000 businesses " +
        "leaving downtown during 2024.",
      date: "2025-09",
      strength: "cyclical",
      direction: "against",
      affects: { to: ["creative office"], from: [] },
      basis: "The scenario set for this site treats a creative-office build-out as the entitled " +
        "direction. This is the market it would be delivered into.",
      source: "Press summaries of CoStar and Gensler downtown reporting. Neither underlying report was read.",
      url: "https://toljcommercial.com/downtown-la-office-amenities-2026/",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "news-chinatown-retail-attrition",
      channel: "news",
      label: "Chinatown storefronts closing faster than they refill",
      detail: "Yue Wa, one of the last markets serving the neighbourhood's lowest-income residents, " +
        "closed in 2026; reporting describes shuttered restaurants, boarded storefronts and " +
        "fewer pedestrians, and frames the loss of local businesses as producing a health desert. " +
        "About 30% of downtown retail space is reported vacant.",
      date: "2026-01",
      strength: "cyclical",
      direction: "against",
      affects: { to: ["food hall", "creative retail", "retail"], from: [] },
      basis: "It cuts against the retail item above it, and both are in the file for that reason. " +
        "The protection is real and so is the attrition; what a ground floor here has to survive " +
        "is the second one.",
      source: "USC Center for Health Journalism on Chinatown business loss; LA Times / AOL syndication on Yue Wa",
      url: "https://centerforhealthjournalism.org/our-work/reporting/loss-chinatowns-local-businesses-creating-health-desert",
      accessed: "260802",
      confidence: "reported"
    },

    {
      id: "land-chinatown-culture-anchors",
      channel: "landmark",
      label: "A dense culture and food anchor set within walking distance",
      detail: "Central Plaza with its pagoda roofs and lanterns; the Chinese American Museum in the " +
        "Garnier Building, the last surviving structure of the original Chinatown; the Chung King " +
        "Road gallery row, described as a centre of art and nightlife in Downtown LA with nearly " +
        "weekly openings, including Charlie James, Human Resources, Nous Tous and Subliminal " +
        "Projects; Far East Plaza, built 1976, as a food destination with Howlin' Ray's, Kim " +
        "Chuy, Lasita and Scoops; Mandarin Plaza at 979 N Broadway with independent fashion " +
        "labels and Angry Egret Diner.",
      date: "2026-06",
      strength: "anecdotal",
      direction: "for",
      affects: { to: ["museum", "gallery", "event venue", "food hall", "creative retail", "artist studio", "culture"], from: [] },
      basis: "Guides and gallery listings are the source, so this is what the district is known " +
        "for, not what is counted in it. It is the one thing in this file that argues for a " +
        "cultural rather than a commercial future on a parking lot.",
      source: "WWD Chinatown guide; PBS SoCal Artbound on Chinatown galleries; Discover Los Angeles dining guide to Far East Plaza",
      url: "https://www.pbssocal.org/shows/artbound/inside-the-world-of-chinatowns-galleries",
      accessed: "260802",
      confidence: "reported"
    }

  ]
};
