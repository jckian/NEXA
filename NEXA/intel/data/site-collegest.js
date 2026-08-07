// NEXA/intel/data/site-collegest.js
// Phase N1 — 130 W. College Street (Chinatown, Los Angeles)
// Human-readable cited report: NEXA/intel/data/site-collegest.md
// Confidence tags per NEXA/intel/INTEL-DATA.md §1: verified | reported | estimated | unknown.
//
// ⚠️ TWO CAVEATS — see the .md header before using any of this:
// (1) Research was TERMINATED MID-STREAM by an API outage. ZIMAS, the project case file, the Central City
//     North Community Plan page, the TOC tier lookup and 130college.com were never queried. Those fields are
//     "unknown", not guessed.
// (2) Everything before 2023 is DISTRICT/BLOCK resolution, not parcel resolution: the parcel's own pre-2023
//     history is undocumented beyond "surface parking lot" (start date unknown). Node facts say which.
// 260713 BACKFILL: zoning/overlay/APN fields below were machine-queried from the LA City Planning GeoHub
//     zoning layer + LA County Assessor parcels (reported tier — a live layer query, not a read document).
//     The mapped zoning is a DTLA 2040 NEW-FORMAT code, which partially resolves caveat (1)'s zoning gap.
// 260729 CODE READING: regulation.codeReading was read DIRECTLY from the adopted New Zoning Code text
//     (zoning.lacity.gov, Articles 2/3/5/6), so those entries are the FIRST "verified"-tier facts in this
//     file — the earlier blanket statement that nothing here was verified no longer holds. What is still
//     only `reported` is the MAPPING of this parcel to the code string; the meaning of the string is now
//     read from the primary document. FAR and height are consequently no longer "unknown".

window.NEXA_INTEL = window.NEXA_INTEL || {};
window.NEXA_INTEL.sites = window.NEXA_INTEL.sites || {};

window.NEXA_INTEL.sites["130-college-st"] = {

  dossier: {

    meta: {
      name: { value: "130 College Street (proposed creative-office building; currently a surface parking lot)", source: "Urbanize LA / downtownla.com", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" },
      address: { value: "130 W. College Street, Los Angeles, CA 90012 (Chinatown). Project site reported as an assemblage: 110, 114 and 130 W. College St; 117 and 119 W. Bruno St; 945, 949, 953, 955, 959, 963 and 973 N. Main St.", source: "downtownla.com; assemblage list from the project's CEQA Environmental Setting PDF via search snippet (PDF fetched but returned unparseable binary — NOT directly read)", url: "https://downtownla.com/building/130-college", accessed: "260712", confidence: "reported" },
      apn: { value: "114 W College St parcel = APN 5409-008-002 (assessor use: Industrial). Adjacent block parcels 5409-008-001/-003/-004/-005/-015 and 5409-007-001/-002/-003 measured on the same block; WHICH APNs compose the project assemblage (110/114/130 W College + Bruno + Main St lots) is NOT established.", source: "LA County Assessor parcels layer (public.gis.lacounty.gov), point query at the geocoded address", url: "https://public.gis.lacounty.gov/public/rest/services/LACounty_Cache/LACounty_Parcel/MapServer/0", accessed: "260713", confidence: "reported" },
      areaSqm: { value: null, confidence: "unknown" },
      accessedRange: { value: "sources dated 1875-2023 (history) and 2023 (current proposal); research session 260712, cut short by API outage", source: "session log", url: null, accessed: "260712", confidence: "reported" }
    },

    physical: {
      parcelGeometry: { value: null, confidence: "unknown" },
      siteArea: { value: null, confidence: "unknown" },
      existingFootprint: { value: "Zero — the parcel's existing condition is a surface parking lot", source: "Urbanize LA, Mar 17 2023; downtownla.com", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" },
      existingGFA: { value: "0 (surface parking lot)", source: "Urbanize LA, Mar 17 2023", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" },
      far: {
        current: { value: null, confidence: "unknown" },
        proposed: { value: null, confidence: "unknown" }
      },
      heightLimit: { value: null, confidence: "unknown" },
      easements: { value: null, confidence: "unknown" },
      proposedProgram: { value: "5 stories; ~225,000 sf office + ~8,200 sf ground-floor commercial (~233,200 sf total) + 440-car garage; Grimshaw Architects; 'three stacked massings that progressively step back from Bruno Street as it rises'", source: "Urbanize LA (both articles) + downtownla.com", url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
    },

    urban: {
      streetHierarchy: { value: "Block framed by N. Spring St (rail/station side, W), N. Main St (E), College St (N-S frame, E-W street) and Bruno St; proposed plaza at Alameda & College. Broadway/Hill (Central Plaza, Bamboo Lane, Far East Plaza retail-tourist spine) uphill to the west; Alameda the industrial arterial edge to the east.", source: "Urbanize LA project descriptions", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" },
      transitStops: [
        { value: "Metro A Line Chinatown station — ADJACENT. Elevated light-rail station on Spring Street directly above College Street. Opened July 26, 2003.", source: "Wikipedia: Chinatown station (Los Angeles Metro)", url: "https://en.wikipedia.org/wiki/Chinatown_station_(Los_Angeles_Metro)", accessed: "260712", confidence: "reported" },
        { value: "Project markets itself as 'transit oriented ... adjacent to the Chinatown Metro Line Station'", source: "130college.com (developer marketing)", url: "https://130college.com/", accessed: "260712", confidence: "reported" }
      ],
      walkability: { value: "Rail-adjacent with a dense Chinatown grid to the west, but the parcel itself is an industrial, low-porosity block face (surface parking). No Walk Score lookup performed.", source: "own synthesis of the source descriptions; basis = existing surface-lot condition + stated station adjacency", url: null, accessed: "260712", confidence: "estimated" },
      bikeNetwork: { value: null, confidence: "unknown" },
      parkingSupply: { value: "Existing: surface parking lot (count unknown). Proposed: 440-car garage.", source: "Urbanize LA", url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
    },

    environmental: {
      solarOrientation: { value: null, confidence: "unknown" },
      windNotes: { value: null, confidence: "unknown" },
      noiseSources: { value: "Elevated A Line light rail directly adjacent (Spring St above College St) is the obvious dominant noise source; not measured or confirmed in any acoustic study seen.", source: "own inference from the station's stated position", url: "https://en.wikipedia.org/wiki/Chinatown_station_(Los_Angeles_Metro)", accessed: "260712", confidence: "estimated" },
      topography: { value: "Flat industrial-edge block (Chinatown's retail core rises to the west toward Broadway/Hill); not surveyed", source: "own inference from district descriptions", url: null, accessed: "260712", confidence: "estimated" },
      floodRisk: { value: null, confidence: "unknown" },
      heatIsland: { value: "The parcel's existing condition — an uncovered surface parking lot — is a locally maximal impervious/low-albedo heat-island condition. No site-specific measurement found; regional UHI data was NOT re-gathered for this site (research cut short).", source: "own inference from the stated existing condition", url: null, accessed: "260712", confidence: "estimated" }
    },

    context: {
      adjacentUses: [
        { value: "College Station (Atlas Capital Group) — mixed-use, reported 725 market-rate units (770 at full build-out above ~51,000 sf ground-floor commercial), at 129-135 W. College St and 924 N. Spring St. Described by Urbanize LA as 'across the street' from 130 College — i.e. a NEIGHBOR, NOT this parcel. Address parity (odd vs. even side of College St) is consistent with that, but this was NOT confirmed on a parcel map.", source: "Urbanize LA, Mar 2023 + LA City Planning College Station DEIR page", url: "https://planning.lacity.gov/eir/CollegeStation/Deir/CollegeStationDEIR.html", accessed: "260712", confidence: "reported" },
        { value: "Capitol Milling Building — restored by the same developer (Riboli family) as leasable offices, across the street", source: "Urbanize LA, Mar 17 2023", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" },
        { value: "Redcar Properties mass-timber office building at 843 N. Spring Street", source: "Urbanize LA, Mar 17 2023", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" },
        { value: "Homeboy Industries, to the north", source: "Urbanize LA, Mar 17 2023", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
      ],
      publicSpace: [
        { value: "Los Angeles State Historic Park ('the Cornfield') — the district's major open space; former Southern Pacific River Station rail yard; acquired by CA State Parks 2001, interim park 2006, full park opened April 2017 (~$32M acquisition + ~$20M development)", source: "Wikipedia: Los Angeles State Historic Park; The Architect's Newspaper (Apr 2017)", url: "https://en.wikipedia.org/wiki/Los_Angeles_State_Historic_Park", accessed: "260712", confidence: "reported" },
        { value: "Proposed on-site (not built): mid-block central courtyard on Bruno Street + a plaza at Alameda and College", source: "Urbanize LA", url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
      ],
      culturalDistricts: [
        { value: "Chinatown, Los Angeles ('New Chinatown', founded 1938 after Old Chinatown was cleared for Union Station). Central Plaza / Bamboo Lane / Gin Ling Way / Chung King Road form the retail-tourist core uphill (west) of this parcel.", source: "Wikipedia: Chinatown, Los Angeles", url: "https://en.wikipedia.org/wiki/Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" }
      ],
      institutions: { value: "Homeboy Industries (north); Far East Plaza (1976) and Central Plaza are the district's commercial/civic anchors, several blocks west", source: "Urbanize LA; Discover LA / LA Downtown News", url: "https://www.ladowntownnews.com/news/how-an-aging-chinatown-mall-became-a-hipster-food-haven/article_b407e372-f2c3-11e5-a794-e70f2ee0afe3.html", accessed: "260712", confidence: "reported" }
    },

    regulation: {
      zoning: { value: "Mapped current zoning (all parcels on the block, incl. 5409-008-002 = 114 W College): [DM2-G1-5] [CX2-FA] [CPIO] — category 'Commercial-Mixed'. This is a DTLA 2040 NEW-FORMAT code (form district DM2, use district CX2, CPIO overlay), i.e. the new Downtown zoning code is mapped on this parcel — which supersedes the old-code framing of the 2023 entitlement reporting (GPA + zone change sought under legacy zoning). What CX2-FA permits by right (office? housing?) was NOT interpreted — read the DTLA 2040 zoning code before concluding.", source: "LA City Planning Zoning layer (GeoHub hosted FeatureServer), point query at parcel centroid", url: "https://services5.arcgis.com/7nsPwEMP38bSkCjy/arcgis/rest/services/Zoning/FeatureServer/15", accessed: "260713", confidence: "reported" },
      specificPlan: { value: "CORNFIELD / ARROYO SECO specific plan polygon returned at the geocoded point (layer 19). Boundary caution: the point sits on the street centerline; confirm the parcel itself is inside CASP before citing.", source: "LA City Planning MapServer/19 point query", url: "https://maps.lacity.org/lahub/rest/services/City_Planning_Department/MapServer/19", accessed: "260713", confidence: "reported" },
      adaptiveReuseArea: { value: "Downtown Adaptive Reuse Program area (ARIA) — polygon hit at the geocoded point", source: "LA City Planning MapServer/6 point query", url: "https://maps.lacity.org/lahub/rest/services/City_Planning_Department/MapServer/6", accessed: "260713", confidence: "reported" },
      communityPlan: { value: "Reported as the Central City North Community Plan area (which covers Chinatown, Arts District, Little Tokyo, Victor Heights). WHETHER Chinatown has been folded into DTLA 2040 (adopted May 2023) or remains under the older Central City North plan was NOT RESOLVED — the LA City Planning page fetch never completed. A 'DTLA 2040 Chinatown plan summary' PDF exists, suggesting Chinatown is inside the DTLA 2040 study area, but this is unconfirmed. Largest open regulatory question for this site.", source: "Project CEQA Environmental Setting via search snippet + LA City Planning Central City North page (never fetched)", url: "https://planning.lacity.gov/plans-policies/community-plan-area/central-city-north", accessed: "260712", confidence: "reported" },
      overlayZones: { value: "Transit Priority Area (TPA) per SB 743, as identified in ZIMAS per the project's environmental setting document (search snippet, PDF not directly read). TPA status removes vehicle-LOS from CEQA analysis and supports reduced parking.", source: "CEQAnet Environmental Setting PDF (via search snippet)", url: "https://files.ceqanet.lci.ca.gov/300697-2/", accessed: "260712", confidence: "reported" },
      // ── DTLA 2040 CODE READING (260729) ────────────────────────────────────────────────
      // Read directly from the adopted New Zoning Code text at zoning.lacity.gov, so the
      // MEANING of each district is `verified` (primary document seen). The mapping of this
      // parcel to [DM2-G1-5][CX2-FA][CPIO] remains `reported`: GeoHub point query, not ZIMAS.
      // These are the first `verified`-tier facts in this file.
      codeReading: {
        formDistrict: { value: "DM2 = Moderate-Rise Medium 2 (Sec. 2B.16.2). Base FAR 3.0, bonus FAR max 8.5, NO maximum height, building width max 160 ft, building coverage max 90%. Moderate-Rise FAR category (>6.0-8.5), Medium width category (100-210 ft).", source: "LA New Zoning Code Art. 2 (Form), Sec. 2A.1.4 + 2B.16.2", url: "https://zoning.lacity.gov/browse/2", accessed: "260729", confidence: "verified" },
        useDistrict: { value: "CX2 = Commercial-Mixed 2 (Sec. 5B.5.2). Intent: commercial uses generally within a 50,000 sq ft establishment size on the ground story, plus 'a wide range of housing types', supporting a broad range of residential, commercial and civic facility uses. DWELLING = 'S': permitted through the Inclusionary Housing Special Use Program (Sec. 5C.3.1). NO manufacturing-pairing requirement, unlike the IX3 district on the sibling City Market site.", source: "LA New Zoning Code Art. 5 (Use), Sec. 5B.5.2", url: "https://zoning.lacity.gov/browse/5", accessed: "260729", confidence: "verified" },
        densityDistrict: { value: "FA = 'Floor Area' Density District (Art. 6). Floor area is the ONLY practical limit on density: effective minimum lot area per dwelling unit is zero square feet. Unit count is capped by FAR, not by a per-unit lot-area rule.", source: "LA New Zoning Code Art. 6 (Density), Density District Naming Convention", url: "https://zoning.lacity.gov/browse/6", accessed: "260729", confidence: "verified" },
        frontageDistrict: { value: "G1 = General 1 (Sec. 3B.3.1). Build-to depth max 10 ft primary / 15 ft side, build-to width min 90% primary / 70% side, pedestrian amenity allowance max 30% primary, parking setback min 15 ft primary. Applies from the ground through story 5.", source: "LA New Zoning Code Art. 3 (Frontage), Sec. 3B.3.1", url: "https://zoning.lacity.gov/browse/3", accessed: "260729", confidence: "verified" },
        permissionKey: { value: "P = permitted, no specific standards. * = a use standard applies. S = permitted only as established by an applied Special Use Program. CU1/CU2/CU3 = conditional use permit. '--' = not permitted.", source: "LA New Zoning Code Sec. 5A.3.2-5A.3.7", url: "https://zoning.lacity.gov/browse/5", accessed: "260729", confidence: "verified" },
        implication: { value: "This overturns the premise the 2023 reporting rested on. The mapped CX2-FA district already allows a wide range of housing (via the Inclusionary Housing Program) and commercial up to ~50,000 sq ft ground-story establishments, with density limited only by floor area. So the scenario B housing pivot is SUPPORTED by the mapped code, not blocked by it: the 260713 note that its 'zoning does not allow it' premise was uncertain is now resolved in favour of housing being permitted. The GPA + zone change the press reported was sought under the legacy code framing; whether it is still required depends on when the new code became operative for this parcel, which this research did not establish.", confidence: "estimated" },
      },
      far: { value: "As mapped (DM2): base FAR 3.0, bonus FAR max 8.5. See codeReading.formDistrict.", source: "LA New Zoning Code Sec. 2B.16.2", url: "https://zoning.lacity.gov/browse/2", accessed: "260729", confidence: "verified" },
      height: { value: "No maximum height in the DM2 form district. Height is governed by FAR, building width (160 ft max) and coverage (90% max) instead of by a height limit.", source: "LA New Zoning Code Sec. 2B.16.2", url: "https://zoning.lacity.gov/browse/2", accessed: "260729", confidence: "verified" },
      setbacks: { value: null, confidence: "unknown" },
      parkingReq: { value: null, confidence: "unknown" },
      historicStatus: { value: "NONE FOUND for this parcel (currently a surface parking lot). Chinatown Central Plaza IS City of LA Historic-Cultural Monument No. 826 (designated 2005; East and West Gates) — but Central Plaza is several blocks WEST and does NOT cover 130 College Street.", source: "Historical Marker Database; Wikipedia: List of LA Historic-Cultural Monuments in Downtown LA", url: "https://www.hmdb.org/m.asp?m=219859", accessed: "260712", confidence: "reported" },
      affordableHousingBonuses: { value: "TOC tier NOT looked up (research cut short). Rail-station adjacency implies a high tier on its face, but TOC is a housing incentive and the current proposal is office — so TOC may be moot for this project while decisive for any residential alternative. Recorded as unknown rather than guessed.", source: "LA City Planning TOC Guidelines (not read)", url: "https://planning.lacity.gov/ordinances/docs/toc/tocguidelines.pdf", accessed: "260712", confidence: "unknown" },
      pendingRezoning: { value: "YES — the 130 College project requires a General Plan Amendment AND a Zone Change; an initial study has been published by LA City Planning and the project is in environmental review. Case numbers were NOT obtained. That a GPA + zone change are needed is itself the strongest available signal that current zoning does not permit ~225,000 sf of office here.", source: "Urbanize LA, 'Metro-adjacent office project moves forward at 130 W. College Street'", url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
    },

    market: {
      population: { value: "Chinatown: 7,798 residents (2020 U.S. Census); density ~19,230/sq mi", source: "Wikipedia: Chinatown, Los Angeles, citing the 2020 census", url: "https://en.wikipedia.org/wiki/Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" },
      income: { value: "Characterized in the literature as a low-income neighborhood; a neighborhood-aggregator figure of ~$100,020 average household income (2024) also circulates and sits oddly against that characterization — likely an artifact of new market-rate housing shifting the average. NOT RECONCILED; both figures are soft.", source: "Wikipedia + consumer demographic aggregators (Point2Homes/AreaVibes tier)", url: "https://www.point2homes.com/US/Neighborhood/CA/Los-Angeles-County/Los-Angeles/Chinatown-Demographics.html", accessed: "260712", confidence: "reported" },
      age: { value: "Aging population; aggregator data reports median age ~37 with ~14.6% aged 65+", source: "consumer demographic aggregators (weak tier)", url: "https://www.point2homes.com/US/Neighborhood/CA/Los-Angeles-County/Los-Angeles/Chinatown-Demographics.html", accessed: "260712", confidence: "reported" },
      employmentBase: { value: null, confidence: "unknown" },
      housingDemand: { value: "Strong pipeline signal: College Station (~725-770 units, approved 2018) plus other Chinatown multifamily. Demand figures themselves (occupancy, absorption) were NOT gathered for this site.", source: "LA City Planning College Station DEIR page / Urbanize LA", url: "https://la.urbanize.city/post/college-station-takes-another-step-forward", accessed: "260712", confidence: "reported" },
      officeVacancy: { value: "Not gathered for Chinatown specifically. The relevant DTLA backdrop (from the sibling City Market dossier) is office vacancy rising 15.3% (Q1 2020) -> 22.0% (Q2 2025) — an UNFAVORABLE market for the 130 College office program. Flagged as the site's central tension.", source: "CoStar / Avison Young (via site-citymarket research, not re-verified for Chinatown)", url: "https://www.avisonyoung.us/w/market-dynamics-in-downtown-los-angeles-rising-office-vacancies-price-adjustments-and-adaptive-reuse-strategies", accessed: "260712", confidence: "estimated" },
      retailDemand: { value: "Far East Plaza's food-hall revival (Chego 2013, Pok Pok 2014, Howlin' Ray's Apr 2016) demonstrates strong destination-F&B demand in Chinatown — while displacing older tenants", source: "LA Downtown News; Time Out; Discover LA", url: "https://www.timeout.com/los-angeles/restaurants/guide-to-far-east-plaza", accessed: "260712", confidence: "reported" },
      tourism: { value: "Chinatown Central Plaza (1938) was purpose-built as a tourist attraction and remains one; Far East Plaza food tourism is the contemporary layer", source: "Wikipedia: Chinatown, Los Angeles; LA Downtown News", url: "https://en.wikipedia.org/wiki/Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" },
      creativeIndustry: { value: "Chung King Road gallery wave from the late 1990s (China Art Objects; Bernard St cluster Oct 2003) made Chinatown an art-world node; China Art Objects left for Culver City in 2010. The 130 College proposal is explicitly a 'creative office' bet on that lineage.", source: "PBS SoCal Artbound; Wikipedia: Chung King Road; 130college.com", url: "https://www.pbssocal.org/shows/artbound/inside-the-world-of-chinatowns-galleries", accessed: "260712", confidence: "reported" }
    },

    climate: {
      heatProjection: { value: null, confidence: "unknown" },
      floodProjection: { value: null, confidence: "unknown" },
      waterEnergyNotes: { value: null, confidence: "unknown" },
      transitInvestment: { value: "Existing: Metro A Line Chinatown station adjacent (2003). No FUTURE Metro investment specific to this station was researched (session cut short).", source: "Wikipedia: Chinatown station", url: "https://en.wikipedia.org/wiki/Chinatown_station_(Los_Angeles_Metro)", accessed: "260712", confidence: "reported" },
      resilienceOpportunities: { value: "Two: (a) Los Angeles State Historic Park (2017) is a large green/cooling adjacency, unusual for an industrial-edge parcel; (b) the parcel's current surface-lot condition means ANY redevelopment with the proposed courtyard + plaza landscaping is a net heat improvement. Both are inference, not a stated climate commitment in any source found.", source: "own analysis of the LASHP opening + the project's stated open-space program", url: "https://en.wikipedia.org/wiki/Los_Angeles_State_Historic_Park", accessed: "260712", confidence: "estimated" }
    }
  },

  timeline: {
    nodes: [
      {
        id: "b-1875-river-station",
        kind: "building",
        label: "Southern Pacific River Station rail yard (district adjacency)",
        tStart: 1875, tEnd: 1901, epoch: "past",
        facts: [
          { value: "Southern Pacific's River Station (opened 1875, operating c.1876-1901) — the 'Ellis Island of Los Angeles' where new arrivals disembarked; waterwheel, freight house, roundhouse, depot, station yard. DISTRICT RESOLUTION: immediately east of the block, later the 'Cornfield' brownfield, today LA State Historic Park. Not the parcel itself.", source: "Wikipedia: Los Angeles State Historic Park; California State Parks", url: "https://en.wikipedia.org/wiki/Los_Angeles_State_Historic_Park", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-1880-old-chinatown",
        kind: "program",
        label: "Old Chinatown (Alameda & Macy) — district program, 1880s-1933",
        tStart: 1880, tEnd: 1933, epoch: "past",
        facts: [
          { value: "Old Chinatown, the original settlement centered on Alameda and Macy Streets, existed from the 1880s until c.1933. DISTRICT RESOLUTION — south-east of this block, not on the parcel.", source: "Wikipedia: Old Chinatown, Los Angeles", url: "https://en.wikipedia.org/wiki/Old_Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-1933-union-station-clearance",
        kind: "regulation",
        label: "Old Chinatown condemned and cleared for Union Station",
        tStart: 1933, tEnd: 1933, epoch: "past",
        facts: [
          { value: "By the 1930s most of Old Chinatown was destroyed to clear the site for Union Station; hundreds of Chinese families displaced. The founding act of dispossession that produced today's Chinatown.", source: "NBC Los Angeles; California Historical Society; Wikipedia: Old Chinatown", url: "https://www.nbclosangeles.com/news/local/los-angeles-union-station-original-chinatown-exhibit/3423032/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "b-1939-union-station",
        kind: "building",
        label: "Union Station opens",
        tStart: 1939, tEnd: null, epoch: "past",
        facts: [
          { value: "Union Station opened in 1939 on the cleared Old Chinatown site.", source: "NBC Los Angeles; Wikipedia: Old Chinatown, Los Angeles", url: "https://en.wikipedia.org/wiki/Old_Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "s-1937-soo-hoo",
        kind: "society",
        label: "Peter Soo Hoo Sr. / LA Chinatown Project Association organize the replacement",
        tStart: 1937, tEnd: 1938, epoch: "past",
        facts: [
          { value: "In 1937 the Los Angeles Chinatown Project Association, galvanized by community leader Peter Soo Hoo Sr., raised funds to acquire, design and construct New Chinatown's Central Plaza — design/operational concepts evolved through a collective community process, producing a blend of Chinese and American architecture.", source: "Wikipedia: Chinatown, Los Angeles; LA Conservancy (via Google Arts & Culture)", url: "https://en.wikipedia.org/wiki/Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-1938-new-chinatown",
        kind: "program",
        label: "New Chinatown / Central Plaza — the district's replacement program",
        tStart: 1938, tEnd: null, epoch: "past",
        facts: [
          { value: "New Chinatown (1938-present) built north of the cleared Old Chinatown: Central Plaza, a tourist-oriented, Hollywood-set-designed 'Chinese' commercial district containing Bamboo Lane, Gin Ling Way and Chung King Road. DISTRICT RESOLUTION — the retail-tourist core is several blocks uphill (west) of 130 College.", source: "Wikipedia: Chinatown, Los Angeles", url: "https://en.wikipedia.org/wiki/Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-1938-china-city",
        kind: "program",
        label: "China City — the rival replacement that failed",
        tStart: 1938, tEnd: 1948, epoch: "past",
        facts: [
          { value: "China City (1938-1948), the competing, more explicitly theatrical replacement Chinatown, did not survive.", source: "Wikipedia: Chinatown, Los Angeles", url: "https://en.wikipedia.org/wiki/Chinatown,_Los_Angeles", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "b-1976-far-east-plaza",
        kind: "building",
        label: "Far East Plaza built (Broadway)",
        tStart: 1976, tEnd: null, epoch: "past",
        facts: [
          { value: "Far East Plaza, built 1976 on Broadway — the district's postwar commercial mall anchor; later the vehicle of Chinatown's food-hall revival. DISTRICT RESOLUTION.", source: "Discover Los Angeles; LA Downtown News", url: "https://www.ladowntownnews.com/news/how-an-aging-chinatown-mall-became-a-hipster-food-haven/article_b407e372-f2c3-11e5-a794-e70f2ee0afe3.html", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-1998-gallery-wave",
        kind: "economy",
        label: "Chung King Road gallery wave (gentrification inflection)",
        tStart: 1998, tEnd: 2012, epoch: "past",
        facts: [
          { value: "From the late 1990s vacant Chung King Road storefronts were converted into art galleries (China Art Objects, Giovanni Intra / Steve Hanson); a further cluster launched on Bernard St in Oct 2003; China Art Objects left for Culver City in 2010. Jan Lin's 'Los Angeles Chinatown: Tourism, Gentrification, and the Rise of an Ethnic Growth Machine' (2008) frames this as the district's gentrification inflection. End year 2012 is ESTIMATED (basis: the wave's documented peak c.2003-2010 and the anchor gallery's 2010 departure); no source gives an end date.", source: "PBS SoCal Artbound; Wikipedia: Chung King Road; Jan Lin (2008)", url: "https://www.pbssocal.org/shows/artbound/inside-the-world-of-chinatowns-galleries", accessed: "260712", confidence: "estimated" }
        ]
      },
      {
        id: "t-2003-chinatown-station",
        kind: "transit",
        label: "Metro Chinatown station opens — ADJACENT TO THE PARCEL",
        tStart: 2003, tEnd: null, epoch: "past",
        facts: [
          { value: "Opened July 26, 2003 as part of the original Gold Line (Pasadena), now the A Line. Elevated light-rail station on Spring Street directly ABOVE COLLEGE STREET. Island-platform canopies inspired by pagoda architecture; Metro Art installation 'Wheels of Change' by Chusien Chang unveiled 2003. THE decisive event for this parcel: it converts an industrial back-block into transit-adjacent land.", source: "Wikipedia: Chinatown station (Los Angeles Metro); Metro The Source", url: "https://en.wikipedia.org/wiki/Chinatown_station_(Los_Angeles_Metro)", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2005-hcm826",
        kind: "regulation",
        label: "Chinatown Central Plaza designated HCM No. 826 — does NOT cover this parcel",
        tStart: 2005, tEnd: null, epoch: "past",
        facts: [
          { value: "Central Plaza designated City of Los Angeles Historic-Cultural Monument No. 826 in 2005 (East and West Gates). Also known as the New Chinatown Historic District. IMPORTANT: this is several blocks west and confers NO historic protection on 130 College Street.", source: "Historical Marker Database; Wikipedia: List of LA Historic-Cultural Monuments in Downtown LA; LA Conservancy", url: "https://www.hmdb.org/m.asp?m=219859", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-2013-far-east-food-revival",
        kind: "economy",
        label: "Far East Plaza food-hall revival",
        tStart: 2013, tEnd: 2016, epoch: "past",
        facts: [
          { value: "Under George Yu (Macco Investments), Far East Plaza was re-tenanted: Roy Choi's Chego (May 2013), Scoops (2014), Andy Ricker's Pok Pok Phat Thai (2014), and Howlin' Ray's (April 2016). Old vendors were swept out as new restaurants moved in — the emblem of Chinatown's food-tourism turn and of tenant displacement.", source: "LA Downtown News; Time Out LA; Discover LA; Reappropriate", url: "https://www.ladowntownnews.com/news/how-an-aging-chinatown-mall-became-a-hipster-food-haven/article_b407e372-f2c3-11e5-a794-e70f2ee0afe3.html", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "c-2017-lashp",
        kind: "climate",
        label: "Los Angeles State Historic Park opens (green adjacency)",
        tStart: 2017, tEnd: null, epoch: "past",
        facts: [
          { value: "CA State Parks acquired the 'Cornfield' brownfield in 2001; an interim 13-acre park opened 2006; the full Los Angeles State Historic Park opened April 2017 after a ~20-year process (~$32M acquisition + ~$20M development). Converts the site's eastern rail-brownfield edge into the district's principal green/cooling asset.", source: "Wikipedia: Los Angeles State Historic Park; The Architect's Newspaper (Apr 2017)", url: "https://www.archpaper.com/2017/04/los-angeles-state-historic-park-opens/", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2018-college-station-approval",
        kind: "regulation",
        label: "College Station approved (adjacent parcel — 725 market-rate units, zero affordable)",
        tStart: 2018, tEnd: null, epoch: "past",
        facts: [
          { value: "In 2018 the LA City Planning Commission approved College Station — Atlas Capital Group, at 129-135 W. College St and 924 N. Spring St: reported as 725 market-rate units (full build-out described as 770 units above ~51,000 sf ground-floor commercial), with NONE designated affordable. Johnson Fain, architect. ADJACENCY CAVEAT: Urbanize LA describes it as 'across the street' from 130 College — a NEIGHBOR, NOT this parcel — and the address parity (odd vs. even side of College St) agrees. NOT confirmed on a parcel map.", source: "LA City Planning College Station DEIR page; Urbanize LA; LA Chinatown Community Land Trust", url: "https://planning.lacity.gov/eir/CollegeStation/Deir/CollegeStationDEIR.html", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "s-displacement-pressure",
        kind: "society",
        label: "Anti-displacement organizing (LA Chinatown CLT, Central City United)",
        tStart: 2018, tEnd: null, epoch: "present",
        facts: [
          { value: "The gallery wave, the Far East Plaza food revival and the market-rate housing wave are read by Chinatown organizers as one continuous displacement process; College Station's zero affordable units is the emblematic grievance. LA Chinatown Community Land Trust and the Central City United coalition are the organized response. Start year 2018 is ESTIMATED (basis: the College Station approval as the galvanizing event); the organizing predates it.", source: "LA Chinatown Community Land Trust, 'Changing Landscape'; Central City United; Reappropriate", url: "https://www.lachinatownclt.org/changing-landscape", accessed: "260712", confidence: "estimated" }
        ]
      },
      {
        id: "p-parking-lot",
        kind: "program",
        label: "Surface parking lot (the parcel's present program)",
        tStart: 2023, tEnd: null, epoch: "present",
        facts: [
          { value: "130 W. College Street's existing condition is a SURFACE PARKING LOT. tStart 2023 is a placeholder: 2023 is simply the earliest date at which a source documents this condition — THE DATE THE PARCEL BECAME A PARKING LOT, AND WHAT STOOD HERE BEFORE, WERE NOT ESTABLISHED (Sanborn maps / LAPL archives not consulted; research cut short). Do not read tStart as a real start date.", source: "Urbanize LA, Mar 17 2023; downtownla.com", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-2023-riboli-chinatown-bet",
        kind: "economy",
        label: "Riboli family's Chinatown investment programme",
        tStart: 2023, tEnd: null, epoch: "present",
        facts: [
          { value: "The 130 College proposal follows a series of Riboli family (San Antonio Winery, Lincoln Heights) investments in their Chinatown property holdings, notably the restoration of the Capitol Milling Building across the street as leasable offices. Stated intent: 'breathe new life into the more industrial side of Chinatown'. Contemporaneous neighbours: Redcar Properties' mass-timber office at 843 N. Spring St.", source: "Urbanize LA, Mar 17 2023", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-2023-office-proposal",
        kind: "program",
        label: "130 College Street — 5-storey creative-office proposal (Grimshaw)",
        tStart: 2023, tEnd: null, epoch: "present",
        facts: [
          { value: "Announced March 2023: five storeys, ~225,000 sf office above ~8,200 sf ground-floor commercial, 440-car garage, by Grimshaw Architects — 'three stacked massings that progressively step back from Bruno Street as it rises', with a mid-block courtyard on Bruno St and a plaza at Alameda & College. Currently a PROPOSAL in environmental review, not a built program.", source: "Urbanize LA (Mar 17 2023 + follow-up); downtownla.com; 130college.com", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-2023-entitlement",
        kind: "regulation",
        label: "Environmental review — GPA + zone change pending",
        tStart: 2023, tEnd: null, epoch: "present",
        facts: [
          { value: "An initial study has been published by the LA Dept. of City Planning; the project requires a GENERAL PLAN AMENDMENT and a ZONE CHANGE. Project site reported as 110/114/130 W. College St, 117/119 W. Bruno St, 945-973 N. Main St, within the Central City North Community Plan area, identified in ZIMAS as a Transit Priority Area (SB 743). Case numbers NOT obtained; the CEQA PDF was fetched but returned unparseable binary, so its content here is search-snippet sourced, NOT directly read.", source: "Urbanize LA, 'Metro-adjacent office project moves forward'; CEQAnet Environmental Setting PDF (via search snippet)", url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "e-dtla-office-softness",
        kind: "economy",
        label: "Soft DTLA office market (the proposal's central risk)",
        tStart: 2020, tEnd: null, epoch: "present",
        facts: [
          { value: "DTLA office vacancy rose from 15.3% (Q1 2020) to 22.0% (Q2 2025), with sale prices down ~27%. NOT re-verified for Chinatown specifically — carried over from the sibling City Market research as regional backdrop, hence ESTIMATED as applied here. It is an unfavourable market for a speculative 225,000 sf office program and is the single biggest question mark over the 130 College proposal.", source: "CoStar / Avison Young (regional DTLA data, applied by inference)", url: "https://www.avisonyoung.us/w/market-dynamics-in-downtown-los-angeles-rising-office-vacancies-price-adjustments-and-adaptive-reuse-strategies", accessed: "260712", confidence: "estimated" }
        ]
      },
      {
        id: "p-future-office-buildout",
        kind: "program",
        label: "130 College office build-out (projected complete 2028)",
        tStart: 2026, tEnd: 2028, epoch: "future",
        facts: [
          { value: "The project's initial study forecasts construction COMPLETE BY 2028, pending approvals (GPA + zone change). tStart 2026 is ESTIMATED (basis: a 2028 completion target back-cast against a ~2-year construction period for a 5-storey structure) — no construction-start date is disclosed in any source. A downtownla.com listing gives a 2026 completion, an older/stale figure; NOT reconciled. No 2025-2026 approval, denial or groundbreaking news was searched for (research cut short), so this projection may already be out of date.", source: "Urbanize LA, 'Metro-adjacent office project moves forward at 130 W. College Street' (citing the published initial study)", url: "https://la.urbanize.city/post/metro-adjacent-office-project-moves-forward-130-w-college-street-chinatown", accessed: "260712", confidence: "estimated" }
        ]
      },
      {
        id: "r-future-tpa-density",
        kind: "regulation",
        label: "Station-adjacency density policy (TPA / TOC) as the site's long-run entitlement frame",
        tStart: 2026, tEnd: 2050, epoch: "future",
        facts: [
          { value: "The parcel's ZIMAS-reported Transit Priority Area status (SB 743) plus direct A Line station adjacency place it inside LA's transit-density policy frame — TPA already removes vehicle-LOS from CEQA and supports reduced parking; TOC (a housing incentive granting 20-80% density bonus for affordable units) would apply to any RESIDENTIAL alternative on this parcel. THE TOC TIER WAS NOT LOOKED UP and is not asserted here. This node projects a policy frame, not an outcome.", source: "CEQAnet Environmental Setting (TPA, via search snippet); LA City Planning TOC Incentive Program / TOC Guidelines (not read)", url: "https://planning.lacity.gov/plans-policies/transit-oriented-communities-incentive-program", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "r-future-community-plan",
        kind: "regulation",
        label: "Community-plan uncertainty (Central City North vs. DTLA 2040) governs the site to ~2040",
        tStart: 2023, tEnd: 2040, epoch: "future",
        facts: [
          { value: "The parcel is reported to sit in the Central City North Community Plan area, but a 'DTLA 2040 Chinatown plan summary' PDF also exists, suggesting Chinatown falls inside the DTLA 2040 study area (DTLA 2040 was adopted May 2023 with a 2040 horizon). WHICH PLAN GOVERNS WAS NOT RESOLVED — the LA City Planning page fetch never completed. This is the largest open regulatory question for the site: it determines the FAR, height and use envelope the 130 College zone change is being measured against, and the frame for any successor program to ~2040.", source: "CEQAnet Environmental Setting (via snippet); LA City Planning Central City North page (fetch never completed); DTLA 2040 Chinatown plan summary PDF (hcnnc.org)", url: "https://planning.lacity.gov/plans-policies/community-plan-area/central-city-north", accessed: "260712", confidence: "reported" }
        ]
      },
      {
        id: "p-future-district-mixed-use",
        kind: "program",
        label: "Station-block mixed-use district (projection to ~2050)",
        tStart: 2028, tEnd: 2050, epoch: "future",
        facts: [
          { value: "PROJECTION, not a plan: the College/Spring/Main/Bruno block face is on a documented trajectory from surface parking and light industry toward a transit-adjacent mixed-use district — College Station's ~725-770 units (approved 2018) on one side, 130 College's ~233,200 sf office (proposed 2023) on the other, Redcar's mass-timber office at 843 N. Spring, Capitol Milling's office restoration, with LA State Historic Park (2017) as the amenity frame. Projected by the convergence of those four entitlements/investments plus the TPA/TOC policy frame — NOT by any adopted specific plan for this block. Horizon 2050 is our own; no source projects that far.", source: "own synthesis of the entitlement pipeline (Urbanize LA; LA City Planning College Station DEIR) + TPA status", url: "https://la.urbanize.city/post/five-story-office-building-planned-130-w-college-street-chinatown", accessed: "260712", confidence: "estimated" }
        ]
      }
    ],

    edges: [
      { from: "b-1875-river-station", to: "p-1880-old-chinatown", relation: "enabled", note: "The River Station rail yard drew the immigrant labour and commerce that formed Old Chinatown beside it" },
      { from: "r-1933-union-station-clearance", to: "p-1880-old-chinatown", relation: "constrained", note: "Condemnation and clearance for Union Station destroyed Old Chinatown and displaced hundreds of families" },
      { from: "r-1933-union-station-clearance", to: "b-1939-union-station", relation: "caused", note: "The clearance produced Union Station, opened 1939, on the Old Chinatown site" },
      { from: "p-1880-old-chinatown", to: "p-1938-new-chinatown", relation: "succeeded_by", note: "SPINE (district resolution): Old Chinatown (1880s-1933) was succeeded by New Chinatown / Central Plaza (1938-)" },
      { from: "s-1937-soo-hoo", to: "p-1938-new-chinatown", relation: "caused", note: "Peter Soo Hoo Sr. and the LA Chinatown Project Association organized the funding, design and construction of Central Plaza" },
      { from: "p-1938-china-city", to: "p-1938-new-chinatown", relation: "coexisted", note: "China City (1938-1948) was the rival replacement Chinatown; it failed, leaving New Chinatown as the sole successor" },
      { from: "p-1938-new-chinatown", to: "b-1976-far-east-plaza", relation: "enabled", note: "The established New Chinatown commercial district supported a postwar mall anchor on Broadway" },
      { from: "b-1976-far-east-plaza", to: "e-2013-far-east-food-revival", relation: "enabled", note: "The aging 1976 mall's cheap, subdividable retail bays were the physical container for the 2013-2016 food-hall revival" },
      { from: "e-1998-gallery-wave", to: "e-2013-far-east-food-revival", relation: "caused", note: "The gallery wave established Chinatown as a destination for non-Chinese cultural consumption; the food-hall revival is its commercial successor phase" },
      { from: "e-1998-gallery-wave", to: "s-displacement-pressure", relation: "caused", note: "Jan Lin (2008) and Chinatown organizers identify the gallery wave as the district's gentrification inflection point" },
      { from: "e-2013-far-east-food-revival", to: "s-displacement-pressure", relation: "caused", note: "Old Far East Plaza vendors were swept out as celebrity-chef tenants moved in — the displacement mechanism made legible" },
      { from: "t-2003-chinatown-station", to: "e-1998-gallery-wave", relation: "enabled", note: "Rail access from 2003 amplified outside visitation to Chung King Road; the Bernard St gallery cluster launched Oct 2003, the same year the station opened" },
      { from: "t-2003-chinatown-station", to: "r-2018-college-station-approval", relation: "enabled", note: "Station adjacency is the entire premise of a 725-unit transit-oriented housing project on this block" },
      { from: "t-2003-chinatown-station", to: "p-2023-office-proposal", relation: "enabled", note: "THE decisive parcel fact: the elevated A Line station on Spring St above College St converts an industrial back-block into transit-adjacent office land; the project markets itself on that adjacency" },
      { from: "t-2003-chinatown-station", to: "r-future-tpa-density", relation: "caused", note: "Station adjacency is what places the parcel inside LA's TPA/TOC transit-density policy frame" },
      { from: "c-2017-lashp", to: "p-2023-office-proposal", relation: "enabled", note: "LA State Historic Park (2017) turns the parcel's brownfield/rail edge into an amenity frontage, materially improving the office pitch" },
      { from: "r-2018-college-station-approval", to: "e-2023-riboli-chinatown-bet", relation: "enabled", note: "725-770 approved units across the street supply the daytime/evening population and validation that underwrite an adjacent speculative office bet" },
      { from: "r-2018-college-station-approval", to: "s-displacement-pressure", relation: "caused", note: "Zero affordable units among 725 market-rate units is the emblematic grievance galvanizing the Chinatown CLT / Central City United response" },
      { from: "p-parking-lot", to: "p-2023-office-proposal", relation: "succeeded_by", note: "SPINE (parcel resolution): the surface parking lot is the program the 2023 office proposal is intended to succeed" },
      { from: "e-2023-riboli-chinatown-bet", to: "p-2023-office-proposal", relation: "caused", note: "The Riboli family's Chinatown investment programme (Capitol Milling restoration, adjacent holdings) produced the 130 College proposal" },
      { from: "r-2023-entitlement", to: "p-2023-office-proposal", relation: "constrained", note: "The proposal cannot proceed without a General Plan Amendment and a Zone Change — current zoning does not permit it" },
      { from: "r-future-community-plan", to: "r-2023-entitlement", relation: "constrained", note: "Which community plan governs (Central City North vs. DTLA 2040) sets the FAR/height/use envelope the zone change is measured against — and is UNRESOLVED" },
      { from: "e-dtla-office-softness", to: "p-future-office-buildout", relation: "constrained", note: "A DTLA office market at 22% vacancy is the principal threat to a speculative 225,000 sf office build-out; the program may not survive financing in this form" },
      { from: "p-2023-office-proposal", to: "p-future-office-buildout", relation: "succeeded_by", note: "SPINE: the proposal, if entitled, becomes the built office program — initial study forecasts completion by 2028" },
      { from: "r-future-tpa-density", to: "p-future-office-buildout", relation: "enabled", note: "TPA status (reduced parking, no vehicle-LOS in CEQA) eases the build-out; a high TOC tier would apply only if the program turned residential" },
      { from: "p-future-office-buildout", to: "p-future-district-mixed-use", relation: "succeeded_by", note: "SPINE: the completed office block is projected to sit inside a fully transit-oriented mixed-use station block by ~2050" },
      { from: "r-future-community-plan", to: "p-future-district-mixed-use", relation: "constrained", note: "The governing community plan's 2040 horizon frames the density and use mix the block can reach" },
      { from: "s-displacement-pressure", to: "p-future-district-mixed-use", relation: "constrained", note: "Organized anti-displacement politics is the principal countervailing force on the block's market-rate trajectory — affordability requirements are the likeliest form it takes" }
    ]
  }
};
