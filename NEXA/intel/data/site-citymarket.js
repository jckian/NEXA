// NEXA/intel/data/site-citymarket.js
// Phase N1 — City Market of Los Angeles (Fashion District, DTLA)
// Human-readable cited report: NEXA/intel/data/site-citymarket.md
// Confidence tags per NEXA/intel/INTEL-DATA.md §1: verified | reported | estimated | unknown.
// NOTE: LA City Planning EIR pages returned HTTP 403 to direct fetch this session; facts drawn from
// them (zoning M2-2D, vesting change to C2-2, FAR 3:1->4.1:1, ENV-2012-3003-EIR) are tagged "reported"
// (search-snippet sourced), not "verified", per the "primary source seen" rule. See .md for full detail.

window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.sites = window.NEXA_INTEL.sites || {};

window.NEXA_INTEL.sites["citymarket-la"] = {

  dossier: {

    meta: {
      name: { value: "City Market of Los Angeles", source: "multiple", url: "https://www.citymarketla.com/", accessed: "260712", confidence: "reported" },
      address: { value: "1057 S. San Pedro Street, Los Angeles, CA 90015", source: "Downtown LA building profile", url: "https://downtownla.com/building/city-market-of-los-angeles", accessed: "260712", confidence: "reported" },
      apn: { value: null, confidence: "unknown" },
      areaSqm: { value: 40469, source: "10 acres reported (Urbanize LA / Commercial Observer); converted 1 acre = 4046.86 m2", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "estimated" },
      accessedRange: { value: "sources dated 1986-2025, research session 260712", source: "session log", url: null, accessed: "260712", confidence: "verified" }
    },

    physical: {
      parcelGeometry: { value: null, confidence: "unknown" },
      siteArea: { value: "~10 acres (~40,469 m2), bounded by 9th, San Pedro, 12th, San Julian Streets", source: "Urbanize LA / Commercial Observer", url: "https://commercialobserver.com/2024/03/la-city-council-approves-agreement-city-market/", accessed: "260712", confidence: "reported" },
      existingFootprint: { value: "~91,729 sf of existing structures on the project site (per EIR project description)", source: "LA City Planning EIR project description (search snippet, 403 on direct fetch)", url: "https://planning.lacity.gov/eir/citymarketproject/deir_recirculated/assets/II.%20Project%20Description.pdf", accessed: "260712", confidence: "reported" },
      existingGFA: { value: null, confidence: "unknown" },
      far: {
        current: { value: "3:1 (M2-2D, Height District 2, 'D' limitation)", source: "LA City Planning EIR page (search snippet)", url: "https://planning.lacity.gov/development-services/eir/city-market-los-angeles-project-1", accessed: "260712", confidence: "reported" },
        entitled: { value: "4.1:1 (requested Height District Change)", source: "LA City Planning EIR page (search snippet)", url: "https://planning.lacity.gov/development-services/eir/city-market-los-angeles-project-1", accessed: "260712", confidence: "reported" }
      },
      heightLimit: { value: "No absolute numeric height cap under current 'D' FAR limitation; 2015-era proposal envisioned buildings 3-38 stories, office tower up to ~455 ft (not reconfirmed against 2024 approved terms)", source: "Urbanize LA 2015", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "reported" },
      easements: { value: null, confidence: "unknown" }
    },

    urban: {
      streetHierarchy: { value: "Bounded by 9th St (N), San Pedro St (E), 12th St (S), San Julian St (W); two outlying parcels on west side of San Julian between 9th-11th", source: "Urbanize LA / LA City Planning EIR (search snippet)", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "reported" },
      transitStops: [
        { value: "Bus stop 9th/Maple, ~3 min walk", source: "Moovit (via search)", url: "https://moovitapp.com/index/en/public_transit-Los_Angeles_Fashion_District-Los_Angeles_CA-site_24471344-302", accessed: "260712", confidence: "reported" },
        { value: "Pico Station (A Line light rail), ~20 min walk", source: "Moovit (via search)", url: "https://moovitapp.com/index/en/public_transit-Los_Angeles_Fashion_District-Los_Angeles_CA-site_24471344-302", accessed: "260712", confidence: "reported" },
        { value: "Pershing Square Station (B/D Line subway), ~20 min walk", source: "Moovit (via search)", url: "https://moovitapp.com/index/en/public_transit-Los_Angeles_Fashion_District-Los_Angeles_CA-site_24471344-302", accessed: "260712", confidence: "reported" },
        { value: "Future: Southeast Gateway Line Fashion District station near 8th & Los Angeles St, opening ~2035", source: "Wikipedia / Urbanize LA", url: "https://en.wikipedia.org/wiki/Southeast_Gateway_Line", accessed: "260712", confidence: "reported" }
      ],
      walkability: { value: "Moderate — dense downtown street grid but no rail station directly on-site; industrial-era truck/wholesale-oriented infrastructure", source: "synthesis of transit + zoning sources", url: null, accessed: "260712", confidence: "estimated" },
      bikeNetwork: { value: null, confidence: "unknown" },
      parkingSupply: { value: "3,671 vehicle spaces planned at full build-out (proposed, not existing)", source: "Urbanize LA 2015", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "reported" }
    },

    environmental: {
      solarOrientation: { value: null, confidence: "unknown" },
      windNotes: { value: null, confidence: "unknown" },
      noiseSources: { value: "Likely dense truck/wholesale traffic (Fashion District character) and proximity to I-10 (Fashion District's southern boundary)", source: "DTLA 2040 Fashion District neighborhood profile", url: "http://www.ccala.org/clientuploads/comms/2020/DTLA_2040_Fashion_District_News.pdf", accessed: "260712", confidence: "estimated" },
      topography: { value: "Flat (central LA basin) — assumed, not surveyed", source: "general LA basin geography", url: null, accessed: "260712", confidence: "estimated" },
      floodRisk: { value: null, confidence: "unknown" },
      heatIsland: { value: "Site sits within a citywide/regional UHI hotspot pattern; downtown industrial blocks generally under-canopied relative to wealthier LA neighborhoods; no site-specific measurement found", source: "LBNL Heat Island Group / MDPI Sustainability / National Geographic", url: "https://heatisland.lbl.gov/projects/monitoring-local-urban-heat-islands", accessed: "260712", confidence: "reported" }
    },

    context: {
      adjacentUses: [
        { value: "Fashion District wholesale/light-industrial and garment/textile businesses surrounding the site", source: "DTLA 2040 Fashion District profile / WWD", url: "https://fashiondistrict.org/dtla2040", accessed: "260712", confidence: "reported" },
        { value: "City Market South (creative office/retail/event space) occupies the southern portion of the site itself, operating", source: "HansonLA / citymarketsouth.com", url: "https://citymarketsouth.com/about", accessed: "260712", confidence: "reported" }
      ],
      publicSpace: [
        { value: "Proposed (not yet built): elevated linear park ~20 ft above street level, two piazzas, mid-block pedestrian crossings", source: "Urbanize LA 2015", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "reported" }
      ],
      culturalDistricts: [
        { value: "Historic 'Market Chinatown' district association (City Market and Market Chinatown District, CRA-identified 1992)", source: "LA Conservancy", url: "https://www.laconservancy.org/learn/historic-places/city-market-and-market-chinatown-district/", accessed: "260712", confidence: "reported" },
        { value: "LA Fashion District", source: "fashiondistrict.org", url: "https://fashiondistrict.org/dtla2040", accessed: "260712", confidence: "reported" }
      ],
      institutions: { value: null, confidence: "unknown" }
    },

    regulation: {
      zoning: { value: "Current (project parcel, reported): M2-2D — Light Manufacturing, Height District 2, 'D' limitation FAR 3:1. Entitlement requests Vesting Zone Change to C2-2 with FAR raised to 4.1:1. NOT reconciled against DTLA 2040 IX2 zoning shown for the general Fashion District area (see communityPlan below) — flagged for ZIMAS verification.", source: "LA City Planning EIR page (search snippet, 403 on direct fetch)", url: "https://planning.lacity.gov/development-services/eir/city-market-los-angeles-project-1", accessed: "260712", confidence: "reported" },
      zoningMapped260713: { value: "MACHINE-QUERIED UPDATE (260713): the LA City Planning GeoHub zoning layer returns [DM1-SH1-5] [IX3-FA] [CPIO] — category 'Industrial-Mixed' — for the site's San Pedro St block parcels (e.g. 5132-011-023/-025). Three consequences: (a) DTLA 2040's NEW-FORMAT code is now mapped on the site, superseding the old M2-2D as the mapped zoning; (b) the mapped use district is IX3, NOT the IX2 generalized in the 260712 research — the 'IX2 prohibits housing/hotels' tension recorded below may not apply as stated; (c) how the project's 2024 vesting entitlement interacts with the new mapped code remains unresolved. What IX3-FA permits was NOT interpreted. Overlays at the same point: FASHION DISTRICT specific plan (layer 19) + Downtown Adaptive Reuse Program (layer 6).", source: "LA City Planning Zoning layer (GeoHub hosted FeatureServer) + City Planning MapServer overlays, point queries at parcel centroids", url: "https://services5.arcgis.com/7nsPwEMP38bSkCjy/arcgis/rest/services/Zoning/FeatureServer/15", accessed: "260713", confidence: "reported" },
      communityPlan: { value: "DTLA 2040 (Downtown Community Plan), adopted by LA City Council May 3, 2023. General Fashion District IX2 zoning under this plan: FAR up to 4.5:1, no citywide max height, but new housing/hotels prohibited in IX2 'industrial' parcels — apparently in tension with City Market's own housing/hotel program; resolution (does the project's own vesting entitlement supersede IX2 for this parcel?) not confirmed.", source: "CCALA DTLA 2040 adoption statement + Fashion District neighborhood profile PDF", url: "https://www.ccala.org/news/2023/05/03/recent-news/statement-dtla-2040-community-plan-approval-by-la-city-council/", accessed: "260712", confidence: "reported" },
      overlayZones: { value: null, confidence: "unknown" },
      // ── DTLA 2040 CODE READING (260729) ────────────────────────────────────────────────
      // Read directly from the adopted New Zoning Code text at zoning.lacity.gov, so the
      // MEANING of each district below is `verified` (primary document seen). The mapping of
      // this parcel to the string [DM1-SH1-5][IX3-FA][CPIO] remains `reported`: it came from a
      // GeoHub point query, not from ZIMAS.
      codeReading: {
        formDistrict: { value: "DM1 = Moderate-Rise Medium 1 (Sec. 2B.16.1). Base FAR 3.0, bonus FAR max 8.0, NO maximum height, building width max 210 ft, building coverage max 90%. The DM family sits in the Moderate-Rise FAR category (>6.0-8.5) and the Medium width category (100-210 ft).", source: "LA New Zoning Code Art. 2 (Form), Sec. 2A.1.4 + 2B.16.1", url: "https://zoning.lacity.gov/browse/2", accessed: "260729", confidence: "verified" },
        useDistrict: { value: "IX3 = Industrial-Mixed 3 (Sec. 5B.6.3). Intent: mixing of uses supporting creative production industries. DWELLING = 'S*': permitted only through the Inclusionary Housing Special Use Program (Sec. 5C.3.1) AND subject to a use standard that requires it to be IN CONJUNCTION WITH Light Manufacturing (General, Artistic & Artisanal, or Garment & Accessory) at a MINIMUM AREA OF 1.0 FAR. Campus Unified Development is exempt from that pairing. Residential also carries a 50 ft minimum separation from heavy industrial uses (relief via CU1).", source: "LA New Zoning Code Art. 5 (Use), Sec. 5B.6.3", url: "https://zoning.lacity.gov/browse/5", accessed: "260729", confidence: "verified" },
        densityDistrict: { value: "FA = 'Floor Area' Density District (Art. 6). Floor area is the ONLY practical limit on density: the effective minimum lot area per household or efficiency dwelling unit is zero square feet. Unit count is therefore capped by FAR, not by a per-unit lot-area rule.", source: "LA New Zoning Code Art. 6 (Density), Density District Naming Convention", url: "https://zoning.lacity.gov/browse/6", accessed: "260729", confidence: "verified" },
        frontageDistrict: { value: "SH1 = Shopfront 1 (Sec. 3B.4.1). Build-to depth max 5 ft primary / 10 ft side, build-to width min 90% primary / 70% side, pedestrian amenity allowance max 20% primary, parking setback min 20 ft primary. Applies from the ground through story 5.", source: "LA New Zoning Code Art. 3 (Frontage), Sec. 3B.4.1", url: "https://zoning.lacity.gov/browse/3", accessed: "260729", confidence: "verified" },
        permissionKey: { value: "P = permitted, no specific standards. * = a use standard applies (combined with the underlying permission). S = permitted only as established by an applied Special Use Program. CU1/CU2/CU3 = conditional use permit at Zoning Administrator / ZA / City Planning Commission. '--' = not permitted.", source: "LA New Zoning Code Sec. 5A.3.2-5A.3.7", url: "https://zoning.lacity.gov/browse/5", accessed: "260729", confidence: "verified" },
        implication: { value: "The 260712 dossier flagged an unresolved tension between the entitled housing-led programme and the DTLA 2040 zoning for the Fashion District. It is now resolved in substance: as MAPPED, this parcel's IX3 district does NOT permit a pure housing scheme. Housing here has to be paired with at least 1.0 FAR of light manufacturing (the garment-industry protection the Fashion District fought for), unless the project qualifies as a Campus Unified Development. The 2024 vesting entitlement was granted under the legacy M2-2D -> C2-2 path and may carry vested rights that pre-empt the mapped code; WHICH of the two governs this specific build-out is a legal question this research cannot settle and is the remaining open item.", confidence: "estimated" },
      },
      far: { value: "As mapped (DM1): base FAR 3.0, bonus FAR max 8.0. See codeReading.formDistrict. The entitlement's own figure (3:1 -> 4.1:1, legacy code) is in physical.far and is a different instrument.", source: "LA New Zoning Code Sec. 2B.16.1", url: "https://zoning.lacity.gov/browse/2", accessed: "260729", confidence: "verified" },
      height: { value: "No maximum height in the DM1 form district. Height is governed by FAR, building width (210 ft max) and coverage (90% max) instead of by a height limit.", source: "LA New Zoning Code Sec. 2B.16.1", url: "https://zoning.lacity.gov/browse/2", accessed: "260729", confidence: "verified" },
      setbacks: { value: null, confidence: "unknown" },
      parkingReq: { value: null, confidence: "unknown" },
      historicStatus: { value: "City Market and Market Chinatown District found eligible for National Register of Historic Places (former CRA survey, 1992); Culturally Significant / California Register-eligible. No confirmed formal City of LA Historic-Cultural Monument (HCM) designation found. Six of eight original 1909 buildings demolished in 2012, reportedly before environmental review began.", source: "LA Conservancy", url: "https://www.laconservancy.org/learn/historic-places/city-market-and-market-chinatown-district/", accessed: "260712", confidence: "reported" },
      affordableHousingBonuses: { value: "Revised development agreement (approved March 6, 2024) requires 10% of residential units as affordable, reported as ~94 units total: 47 low-income (50-80% AMI) + 47 moderate-income (80-120% AMI)", source: "Urbanize LA, Aug 18 2022 + Commercial Observer, Mar 2024", url: "https://la.urbanize.city/post/revised-development-agreement-would-add-more-affordable-housing-fashion-districts-city-market", accessed: "260712", confidence: "reported" },
      pendingRezoning: { value: "Vesting Zone Change (M2-2D -> C2-2) and Height District Change pending/entitled under Case No. ENV-2012-3003-EIR; Development Agreement approved March 6, 2024, 20-year term to fulfill terms", source: "LA City Planning EIR page (search snippet) + Commercial Observer", url: "https://commercialobserver.com/2024/03/la-city-council-approves-agreement-city-market/", accessed: "260712", confidence: "reported" }
    },

    market: {
      population: { value: "DTLA population ~90,000, +47% growth since 2010 (vs. ~1% for greater LA, -2% for LA County)", source: "DTLA market report (press synthesis)", url: "https://downtownla.com/business/why-dtla", accessed: "260712", confidence: "reported" },
      income: { value: null, confidence: "unknown" },
      age: { value: null, confidence: "unknown" },
      employmentBase: { value: null, confidence: "unknown" },
      housingDemand: { value: "DTLA multifamily occupancy ~95%, sustained demand despite office downturn", source: "CoStar", url: "https://www.costar.com/article/307674643/are-better-days-ahead-for-downtown-la-boosters-count-the-ways", accessed: "260712", confidence: "reported" },
      officeVacancy: { value: "DTLA office vacancy risen from 15.3% (Q1 2020) to 22.0% (Q2 2025); average sale price down ~27% over same period", source: "CoStar / Avison Young", url: "https://www.avisonyoung.us/w/market-dynamics-in-downtown-los-angeles-rising-office-vacancies-price-adjustments-and-adaptive-reuse-strategies", accessed: "260712", confidence: "reported" },
      retailDemand: { value: null, confidence: "unknown" },
      tourism: { value: null, confidence: "unknown" },
      creativeIndustry: { value: "City Market South positioned as creative-office/fashion-showroom anchor within the historic garment/apparel Fashion District", source: "WWD / Digs.net", url: "https://wwd.com/business-news/real-estate/city-market-developers-talk-los-angeles-fashion-district-city-market-south-10954842/", accessed: "260712", confidence: "reported" }
    },

    climate: {
      heatProjection: { value: "UHI hotspots citywide up to +12C (22F) above rural surroundings; daytime UHI +4C (7.2F); hotspot areas projected to expand by 2050 (regional, not site-specific)", source: "LBNL Heat Island Group / ArcGIS StoryMap", url: "https://heatisland.lbl.gov/projects/monitoring-local-urban-heat-islands", accessed: "260712", confidence: "reported" },
      floodProjection: { value: null, confidence: "unknown" },
      waterEnergyNotes: { value: null, confidence: "unknown" },
      transitInvestment: { value: "Southeast Gateway Line (fmr. West Santa Ana Branch) Fashion District station planned near 8th & Los Angeles St; ~10-year build, construction from ~2025, opening ~2035. Vermont Transit Corridor BRT (west of site) targets 2028 opening.", source: "Wikipedia / Urbanize LA / Metro", url: "https://en.wikipedia.org/wiki/Southeast_Gateway_Line", accessed: "260712", confidence: "reported" },
      resilienceOpportunities: { value: "Proposed elevated linear park + two piazzas in the master plan could mitigate heat/impervious surface if built as rendered; this is inference, not a stated climate commitment in any source found", source: "own analysis of Urbanize LA 2015 project description", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "estimated" }
    }
  },

  timeline: {
    nodes: [
      {
        id: "b-1909-complex",
        kind: "building",
        label: "Original City Market complex built (Morgan & Walls; 8 industrial buildings)",
        tStart: 1909, tEnd: 2012, epoch: "past",
        facts: [
          { value: "8 brick/reinforced-concrete industrial buildings, Mission Revival towers/belvederes, designed by Morgan & Walls", source: "LA Conservancy", url: "https://www.laconservancy.org/learn/historic-places/city-market-and-market-chinatown-district/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-1909-market",
        kind: "program",
        label: "Wholesale produce market (City Market)",
        tStart: 1909, tEnd: 2009, epoch: "past",
        facts: [
          { value: "Founded 1909 by Louis Quan; multi-ethnic (Chinese/Japanese/Caucasian) shareholder capital of ~$200,000; produce operations ended 2009", source: "CHSSC; HansonLA", url: "https://chssc.org/a-history-of-the-los-angeles-city-market-1930-1950/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "s-immigrant-merchants",
        kind: "society",
        label: "Chinese/Japanese immigrant merchant economy anchors the market",
        tStart: 1909, tEnd: 1950, epoch: "past",
        facts: [
          { value: "Japanese farmers controlled ~15% of LA County produce land but grew ~68% of vegetables (1930s); Chinese merchant shareholders held plurality capital at founding", source: "CHSSC", url: "https://chssc.org/a-history-of-the-los-angeles-city-market-1930-1950/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "s-community-dispersal",
        kind: "society",
        label: "WWII internment + postwar dispersal of Chinese produce community",
        tStart: 1942, tEnd: 1952, epoch: "past",
        facts: [
          { value: "1942 Japanese-American incarceration removed competition temporarily; postwar, China City/New Chinatown construction and housing access dispersed the Chinese merchant community — only ~25 Chinese families remained near City Market by 1952", source: "CHSSC", url: "https://chssc.org/a-history-of-the-los-angeles-city-market-1930-1950/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-produce-decline",
        kind: "economy",
        label: "Decline of terminal wholesale produce distribution model",
        tStart: 1960, tEnd: 2009, epoch: "past",
        facts: [
          { value: "Company shifted toward 'other urban uses' as produce operations wound down through 2009; specific decline drivers (trucking/regional terminal-market shifts) not independently documented this session", source: "HansonLA (basis: general narrative, decline mechanics estimated)", url: "https://www.hansonla.com/city-market-south", accessed: "260712", confidence: "estimated" }
        ]
      },
      {
        id: "r-1992-historic-eligible",
        kind: "regulation",
        label: "CRA identifies City Market/Market Chinatown District as National Register-eligible",
        tStart: 1992, tEnd: 1992, epoch: "past",
        facts: [
          { value: "20 structures (8 original + 12 nearby) found eligible for National Register; Culturally Significant / California Register-eligible", source: "LA Conservancy", url: "https://www.laconservancy.org/learn/historic-places/city-market-and-market-chinatown-district/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "b-2012-demolition",
        kind: "building",
        label: "Six of eight original 1909 buildings demolished",
        tStart: 2012, tEnd: 2012, epoch: "past",
        facts: [
          { value: "Demolition occurred before environmental review began, per LA Conservancy; became a focal preservation controversy in the subsequent EIR process", source: "LA Conservancy", url: "https://www.laconservancy.org/learn/historic-places/city-market-and-market-chinatown-district/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2012-eir-opened",
        kind: "regulation",
        label: "Redevelopment EIR process opened (Case No. ENV-2012-3003-EIR)",
        tStart: 2012, tEnd: 2012, epoch: "past",
        facts: [
          { value: "Discretionary approvals sought: Vesting Zone Change M2-2D to C2-2, Height District Change, CUP for floor area averaging, Site Plan Review", source: "LA City Planning EIR page (search snippet)", url: "https://planning.lacity.gov/development-services/eir/city-market-los-angeles-project-1", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-2014-creative-reuse",
        kind: "program",
        label: "City Market South — creative office / retail / event adaptive reuse",
        tStart: 2014, tEnd: 2024, epoch: "past",
        facts: [
          { value: "75,000 sf adaptive reuse on 2.5 acres of the site's southern portion; brick/bow-truss warehouses converted to creative office, showrooms, restaurants, event space around a central plaza", source: "HansonLA / citymarketsouth.com", url: "https://citymarketsouth.com/about", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2018-original-agreement",
        kind: "regulation",
        label: "City Council approves original entitlements / development agreement",
        tStart: 2018, tEnd: 2018, epoch: "past",
        facts: [
          { value: "Original development agreement and entitlements approved by City Council in 2018 (per later 2022 retrospective reporting)", source: "Urbanize LA, Aug 2022", url: "https://la.urbanize.city/post/revised-development-agreement-would-add-more-affordable-housing-fashion-districts-city-market", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2020-veto",
        kind: "regulation",
        label: "Mayor Garcetti vetoes development agreement (Huizar corruption fallout)",
        tStart: 2020, tEnd: 2020, epoch: "past",
        facts: [
          { value: "June 2020 veto followed corruption allegations against then-CD14 Councilmember Jose Huizar, who had inserted district-specific terms", source: "Urbanize LA, Aug 2022 / Commercial Observer, Mar 2024", url: "https://commercialobserver.com/2024/03/la-city-council-approves-agreement-city-market/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "s-2024-huizar-sentenced",
        kind: "society",
        label: "Jose Huizar sentenced to 13 years for corruption",
        tStart: 2024, tEnd: 2024, epoch: "past",
        facts: [
          { value: "Sentenced January 2024, closing the corruption case that had shaped the City Market agreement's renegotiation", source: "Commercial Observer, Mar 2024", url: "https://commercialobserver.com/2024/03/la-city-council-approves-agreement-city-market/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2023-dtla2040",
        kind: "regulation",
        label: "DTLA 2040 Community Plan adopted",
        tStart: 2023, tEnd: null, epoch: "past",
        facts: [
          { value: "Adopted by LA City Council May 3, 2023; governs Downtown LA land use/zoning through 2040; Fashion District generally rezoned IX2 (FAR up to 4.5:1, no height cap, housing/hotels excluded in industrial parcels)", source: "CCALA statement + Fashion District neighborhood profile PDF", url: "https://www.ccala.org/news/2023/05/03/recent-news/statement-dtla-2040-community-plan-approval-by-la-city-council/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2024-aro",
        kind: "regulation",
        label: "Citywide Adaptive Reuse Ordinance expanded (Downtown carved out)",
        tStart: 2024, tEnd: null, epoch: "past",
        facts: [
          { value: "Ord. No. 188,793 expands adaptive reuse citywide (buildings 15+ years old); LAMC Sec. 9.4.5 excludes Downtown Community Plan Area, which retains its own Downtown Adaptive Reuse Program", source: "LA City Planning / Bisnow", url: "https://planning.lacity.gov/citywide-adaptive-reuse-ordinance", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2024-revised-agreement",
        kind: "regulation",
        label: "City Council approves revised development agreement (10% affordable)",
        tStart: 2024, tEnd: 2024, epoch: "past",
        facts: [
          { value: "Approved March 6, 2024; 20-year term to fulfill terms; requires 10% of residential units affordable (~94 units: 47 low-income + 47 moderate-income)", source: "Commercial Observer, Mar 2024", url: "https://commercialobserver.com/2024/03/la-city-council-approves-agreement-city-market/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "t-existing-transit",
        kind: "transit",
        label: "Existing transit context (no on-site rail; bus + ~20min walk to A/B/D Lines)",
        tStart: 2010, tEnd: null, epoch: "present",
        facts: [
          { value: "9th/Maple bus stop ~3 min walk; Pico Station (A Line) and Pershing Square Station (B/D Line) each ~20 min walk", source: "Moovit (via search)", url: "https://moovitapp.com/index/en/public_transit-Los_Angeles_Fashion_District-Los_Angeles_CA-site_24471344-302", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-dtla-office-vacancy",
        kind: "economy",
        label: "DTLA office vacancy crisis",
        tStart: 2020, tEnd: null, epoch: "present",
        facts: [
          { value: "Office vacancy risen from 15.3% (Q1 2020) to 22.0% (Q2 2025); sale prices down ~27%", source: "CoStar / Avison Young", url: "https://www.avisonyoung.us/w/market-dynamics-in-downtown-los-angeles-rising-office-vacancies-price-adjustments-and-adaptive-reuse-strategies", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-dtla-population-growth",
        kind: "economy",
        label: "DTLA residential population growth",
        tStart: 2010, tEnd: null, epoch: "present",
        facts: [
          { value: "DTLA population ~90,000, +47% since 2010, vs. ~flat/declining growth citywide/countywide; multifamily occupancy ~95%", source: "DTLA market report (press synthesis) / CoStar", url: "https://downtownla.com/business/why-dtla", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "c-heat-island-present",
        kind: "climate",
        label: "Regional urban heat island context",
        tStart: 2020, tEnd: null, epoch: "present",
        facts: [
          { value: "UHI hotspots up to +12C (22F) above rural surroundings; DTLA industrial blocks generally under-canopied", source: "LBNL Heat Island Group / National Geographic", url: "https://heatisland.lbl.gov/projects/monitoring-local-urban-heat-islands", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-future-masterplan",
        kind: "program",
        label: "Entitled mixed-use master plan build-out (office / residential / hotel / retail / education)",
        tStart: 2026, tEnd: 2049, epoch: "future",
        facts: [
          { value: "Up to ~1.7-1.9M gsf total; ~945-948 residential units, 210-room hotel, ~225,000 sf retail, ~295,000-310,000+ sf commercial/office and education space, phased over an estimated 25-year build-out per the original EIR phasing narrative", source: "Urbanize LA 2015 + downtownla.com; start year 2026 and end year 2049 are estimated (basis: 2024 agreement date + ~2yr pre-construction lead + 25yr EIR-era phasing horizon, not a disclosed schedule)", url: "https://la.urbanize.city/post/breaking-down-massive-city-market-development", accessed: "260712", confidence: "estimated" }
        ]
      },
      {
        id: "r-2024-entitlement-enables",
        kind: "regulation",
        label: "20-year development agreement window (2024-2044)",
        tStart: 2024, tEnd: 2044, epoch: "future",
        facts: [
          { value: "Development agreement approved March 6, 2024 grants a 20-year period to fulfill its terms", source: "Commercial Observer, Mar 2024", url: "https://commercialobserver.com/2024/03/la-city-council-approves-agreement-city-market/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "t-future-southeast-gateway",
        kind: "transit",
        label: "Southeast Gateway Line Fashion District station (projected)",
        tStart: 2025, tEnd: 2035, epoch: "future",
        facts: [
          { value: "Fashion District station planned near 8th & Los Angeles St; ~10-year build, construction from ~2025, opening projected ~2035", source: "Wikipedia: Southeast Gateway Line / Urbanize LA TOD concepts", url: "https://en.wikipedia.org/wiki/Southeast_Gateway_Line", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "c-future-resilience-policy",
        kind: "climate",
        label: "DTLA/LA climate resilience and greening expectations through 2040+",
        tStart: 2023, tEnd: 2040, epoch: "future",
        facts: [
          { value: "DTLA 2040 plan horizon extends to 2040; UHI hotspot areas projected to expand by 2050 absent mitigation, framing shade/tree-canopy and open-space expectations for new large-scale development", source: "CCALA DTLA 2040 statement + LBNL Heat Island Group projection", url: "https://heatisland.lbl.gov/projects/monitoring-local-urban-heat-islands", accessed: "260712", confidence: "reported" }
        ]
      }
    ],

    edges: [
      { from: "b-1909-complex", to: "p-1909-market", relation: "enabled", note: "1909 Morgan & Walls complex physically housed the founding market operation" },
      { from: "s-immigrant-merchants", to: "p-1909-market", relation: "caused", note: "Multi-ethnic immigrant merchant shareholder capital founded and financed the market" },
      { from: "s-community-dispersal", to: "p-1909-market", relation: "constrained", note: "Loss of the Chinese merchant community after WWII eroded the market's original social/economic base" },
      { from: "e-produce-decline", to: "p-1909-market", relation: "constrained", note: "Decline of the terminal wholesale produce model eroded the business, ending operations in 2009" },
      { from: "r-1992-historic-eligible", to: "b-2012-demolition", relation: "constrained", note: "1992 National Register eligibility made 2012 demolition of contributing buildings a CEQA historic-resources issue" },
      { from: "b-2012-demolition", to: "r-2012-eir-opened", relation: "caused", note: "Pre-review demolition became a focal controversy shaping the subsequent EIR process" },
      { from: "p-1909-market", to: "p-2014-creative-reuse", relation: "succeeded_by", note: "Produce operations ended 2009; site repositioned toward creative-office/retail reuse, construction from ~2014" },
      { from: "r-2012-eir-opened", to: "r-2018-original-agreement", relation: "caused", note: "EIR review process led to original entitlement/development agreement approval in 2018" },
      { from: "r-2018-original-agreement", to: "r-2020-veto", relation: "constrained", note: "Huizar-linked district-specific terms in the 2018 agreement triggered the 2020 mayoral veto" },
      { from: "r-2020-veto", to: "r-2024-revised-agreement", relation: "caused", note: "Veto forced renegotiation, resulting in the 2024 revised agreement with on-site affordable housing" },
      { from: "s-2024-huizar-sentenced", to: "r-2024-revised-agreement", relation: "coexisted", note: "Sentencing closed out the corruption scandal contemporaneously with council approval of the revised agreement" },
      { from: "r-2023-dtla2040", to: "p-future-masterplan", relation: "constrained", note: "DTLA 2040 community-plan framework/zoning (with its IX2 housing/hotel restriction, unresolved vs. project entitlement) governs the site's future build-out capacity" },
      { from: "r-2024-aro", to: "p-2014-creative-reuse", relation: "coexisted", note: "Citywide ARO is a parallel adaptive-reuse pathway; City Market South's own reuse predates it and Downtown has a separate ARO track" },
      { from: "p-2014-creative-reuse", to: "p-future-masterplan", relation: "succeeded_by", note: "Creative-office/retail reuse phase is projected to be succeeded by the full entitled mixed-use build-out" },
      { from: "r-2024-revised-agreement", to: "p-future-masterplan", relation: "enabled", note: "March 2024 development agreement entitles the master-plan build-out" },
      { from: "r-2024-revised-agreement", to: "r-2024-entitlement-enables", relation: "caused", note: "Approval created the 20-year (2024-2044) window to fulfill the agreement's terms" },
      { from: "r-2024-entitlement-enables", to: "p-future-masterplan", relation: "enabled", note: "20-year entitlement window frames the build-out horizon" },
      { from: "t-existing-transit", to: "p-2014-creative-reuse", relation: "enabled", note: "Existing bus/subway-adjacent access supported the creative-office repositioning" },
      { from: "t-future-southeast-gateway", to: "p-future-masterplan", relation: "enabled", note: "Planned Fashion District Metro station strengthens the TOD/ridership case for the master plan's density" },
      { from: "e-dtla-office-vacancy", to: "p-future-masterplan", relation: "caused", note: "Post-2020 office vacancy crisis is a market factor favoring the plan's housing/mixed-use emphasis over pure office" },
      { from: "e-dtla-population-growth", to: "p-future-masterplan", relation: "enabled", note: "DTLA residential population growth and high occupancy support housing demand for the plan's ~945-948 units" },
      { from: "c-heat-island-present", to: "c-future-resilience-policy", relation: "caused", note: "Current heat-island conditions and projected 2050 hotspot expansion motivate DTLA greening/resilience expectations" },
      { from: "c-future-resilience-policy", to: "p-future-masterplan", relation: "constrained", note: "Climate resilience expectations (shade, permeable surface, open space) bear on the master plan's open-space design (elevated linear park, piazzas), though this is not a confirmed formal requirement" }
    ]
  }
};
