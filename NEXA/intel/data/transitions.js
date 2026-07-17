// NEXA Intel — PROGRAM-TRANSITION-DB (M3)
// Schema: NEXA/intel/INTEL-DATA.md §4 · Prose + citations: transitions.md (same folder)
// likelihood is a TIER WITH A STATED BASIS, never a percentage (constraint C5).
// Example urls are filled only when verified; null = see transitions.md citation, to be
// resolved in a verification pass.
window.NEXA_INTEL = window.NEXA_INTEL || {};

// Building-level vocabulary → ProgramFormat entry types used by the NEXA wizard.
window.NEXA_INTEL.typeMap = {
  "housing":         ["2b2b apartment", "studio apartment"],
  "creative office": ["office"],
  "office":          ["office"],
  "retail":          ["sales and display", "pop-up retail", "showroom"],
  "food hall":       ["coffee shop", "lounge bar", "event lounge"],
  "education":       ["classroom", "seminar room", "computer lab", "project review room"],
  "museum/gallery":  ["exhibition gallery"],
  "event/music":     ["event hall", "event lounge", "lounge bar"],
  "hotel":           ["hotel room", "lobby", "lounge bar"],
  "wellness":        ["fitness center", "yoga studio", "pilates studio", "meditation room", "recovery lounge"],
  "logistics":       ["storage", "loading dock"],
  "medical":         ["clinic exam room", "waiting lounge"],
  "parking":         ["parking bay group"]
};

window.NEXA_INTEL.transitions = [
  {
    from: "warehouse", to: "artist studio / loft", likelihood: "high",
    basis: "Cheap span-heavy space plus permissive live-work ordinances made this the canonical first-wave reuse in LA.",
    preconditions: { structure: "timber or concrete frame", span: "wide clear spans", floorHeight: "≥4 m", core: "minimal, added later", mep: "light retrofit", zoningClass: "industrial with live-work allowance", other: "low rent phase of the district cycle" },
    blockers: ["seismic retrofit (URM)", "residential egress upgrades"],
    examples: [
      { project: "LA Arts District lofts under the Artist-in-Residence ordinance", city: "Los Angeles", yearFrom: 1981, yearTo: null, source: "LA City AIR ordinance (1981); LA Conservancy", url: null },
      { project: "The Brewery Art Colony (former Pabst/Eastside brewery)", city: "Los Angeles", yearFrom: 1982, yearTo: null, source: "Brewery Artist Lofts history; press", url: null }
    ]
  },
  {
    from: "warehouse", to: "housing", likelihood: "high",
    basis: "LA's 1999 Adaptive Reuse Ordinance turned the loft pattern into by-right housing conversion; deep floor plates are the main design cost.",
    preconditions: { structure: "concrete frame preferred", span: "regular grid", floorHeight: "≥3.5 m", core: "new cores required", mep: "full replacement", zoningClass: "ARO / mixed-use rezone", other: "window access for deep plates (light wells)" },
    blockers: ["deep floor plates without light", "seismic (URM/non-ductile)", "industrial adjacency (noise, trucks)"],
    examples: [
      { project: "Toy Factory Lofts", city: "Los Angeles (Arts District)", yearFrom: 2004, yearTo: null, source: "press (Curbed LA / LA Times)", url: null },
      { project: "Biscuit Company Lofts (1925 Nabisco bakery)", city: "Los Angeles (Arts District)", yearFrom: 2006, yearTo: null, source: "LA Conservancy; press", url: null }
    ]
  },
  {
    from: "warehouse", to: "creative office", likelihood: "high",
    basis: "Post-2010 the same span-heavy stock outbid housing for tech/media tenants; dominant Arts District & Fashion District pattern.",
    preconditions: { structure: "any sound frame", span: "wide", floorHeight: "≥3.5 m", core: "light", mep: "HVAC + data retrofit", zoningClass: "industrial-commercial hybrid", other: "district amenity mass (food, transit)" },
    blockers: ["office demand cycle (post-2020 vacancy)"],
    examples: [
      { project: "Ford Factory (1912 assembly plant → Warner Music HQ)", city: "Los Angeles (Arts District)", yearFrom: 2017, yearTo: 2019, source: "press (LA Times, Urbanize LA)", url: null },
      { project: "City Market South", city: "Los Angeles (Fashion District)", yearFrom: 2016, yearTo: null, source: "developer + press (Urbanize LA)", url: null }
    ]
  },
  {
    from: "wholesale market", to: "food hall / creative retail", likelihood: "medium",
    basis: "Market sheds convert well to public food/retail when the district gains foot traffic; requires an operator, not just a landlord.",
    preconditions: { structure: "sheds / single-story halls", span: "very wide", floorHeight: "high", core: "n/a", mep: "food-service grade", zoningClass: "commercial", other: "curatorial operator" },
    blockers: ["health-code retrofit cost", "district foot traffic below threshold"],
    examples: [
      { project: "Anaheim Packing House (1919 citrus packing → food hall)", city: "Anaheim", yearFrom: 2014, yearTo: null, source: "press; City of Anaheim", url: null },
      { project: "Covent Garden Market (produce market → retail district)", city: "London", yearFrom: 1980, yearTo: null, source: "Covent Garden history; GLC records", url: null },
      { project: "Grand Central Market repositioning", city: "Los Angeles", yearFrom: 2013, yearTo: null, source: "press (LA Times)", url: null }
    ]
  },
  {
    from: "factory", to: "museum / gallery", likelihood: "medium",
    basis: "Big volumes and daylight suit art; only works with an institutional sponsor, so frequency is low but visibility is high.",
    preconditions: { structure: "heavy frame", span: "very wide", floorHeight: "very high", core: "minimal", mep: "gallery-grade climate", zoningClass: "flexible / civic", other: "institutional anchor + endowment" },
    blockers: ["no sponsor institution", "climate-control cost"],
    examples: [
      { project: "Tate Modern (Bankside Power Station)", city: "London", yearFrom: 1995, yearTo: 2000, source: "Tate official history", url: null },
      { project: "MASS MoCA (Sprague Electric works)", city: "North Adams MA", yearFrom: 1999, yearTo: null, source: "MASS MoCA official history", url: null },
      { project: "Dia:Beacon (Nabisco box-printing plant)", city: "Beacon NY", yearFrom: 2003, yearTo: null, source: "Dia Art Foundation", url: null }
    ]
  },
  {
    from: "factory / refinery", to: "mixed-use campus", likelihood: "medium",
    basis: "Waterfront/urban industrial megasites redevelop as multi-phase campuses when land value crosses the remediation cost.",
    preconditions: { structure: "partial retention", span: "n/a (site-scale)", floorHeight: "n/a", core: "new build dominant", mep: "new", zoningClass: "master-plan rezone", other: "decade-scale capital" },
    blockers: ["environmental remediation", "entitlement duration"],
    examples: [
      { project: "Domino Sugar Refinery (refinery → park/office/housing)", city: "Brooklyn NY", yearFrom: 2017, yearTo: 2023, source: "press (NYT, Curbed NY)", url: null }
    ]
  },
  {
    from: "office", to: "housing", likelihood: "high",
    basis: "The dominant post-2020 conversion under high office vacancy; LA pioneered the regulatory template with the 1999 ARO downtown.",
    preconditions: { structure: "concrete or steel frame", span: "≤ ~13 m glass-to-core depth", floorHeight: "≥2.9 m clear", core: "central core preferred", mep: "full replacement", zoningClass: "ARO / conversion ordinance", other: "operable or replaceable facade" },
    blockers: ["deep floor plates (post-1970 towers)", "curtain-wall replacement cost", "condo-ization of ownership"],
    examples: [
      { project: "Eastern Columbia Building (1930 office/commercial → lofts)", city: "Los Angeles", yearFrom: 2006, yearTo: null, source: "LA Conservancy; ARO record", url: null },
      { project: "One Wall Street (1931 bank office → residential)", city: "New York", yearFrom: 2018, yearTo: 2023, source: "press (NYT)", url: null },
      { project: "25 Water Street (1969 office → ~1,300 units)", city: "New York", yearFrom: 2022, yearTo: 2025, source: "press (NYT, The Real Deal)", url: null }
    ]
  },
  {
    from: "office / bank hall", to: "hotel", likelihood: "medium",
    basis: "Ornate pre-war office stock with small plates converts to hospitality where tourism demand exists; plate depth that fails housing can pass hotel.",
    preconditions: { structure: "pre-war frame", span: "small-medium plates", floorHeight: "≥2.8 m", core: "existing usable", mep: "full replacement", zoningClass: "commercial", other: "tourism/nightlife district" },
    blockers: ["hospitality demand cycle"],
    examples: [
      { project: "NoMad Los Angeles (Giannini Place / Bank of Italy)", city: "Los Angeles", yearFrom: 2018, yearTo: null, source: "press (LA Times)", url: null },
      { project: "Ace Hotel DTLA (United Artists building + theatre)", city: "Los Angeles", yearFrom: 2014, yearTo: null, source: "LA Conservancy; press", url: null }
    ]
  },
  {
    from: "department store", to: "museum / education / creative office", likelihood: "medium",
    basis: "Huge deep plates fail housing but suit institutions; anchor-store deaths free entire blocks at once.",
    preconditions: { structure: "heavy concrete", span: "very deep plates", floorHeight: "high", core: "escalator voids reusable", mep: "replacement", zoningClass: "commercial/civic", other: "institutional buyer" },
    blockers: ["plate depth for any daylight use", "single-tenant scale"],
    examples: [
      { project: "May Company Building → Academy Museum of Motion Pictures", city: "Los Angeles", yearFrom: 2015, yearTo: 2021, source: "Academy Museum official; LA Conservancy", url: null },
      { project: "Westside Pavilion (mall) → UCLA Research Park", city: "Los Angeles", yearFrom: 2024, yearTo: null, source: "UCLA announcement (2024-01)", url: null }
    ]
  },
  {
    from: "shopping mall", to: "logistics / fulfillment", likelihood: "medium",
    basis: "Dead malls sit on highway-adjacent superblocks with parking fields — exactly a fulfillment center's site spec.",
    preconditions: { structure: "usually demolished, site reused", span: "n/a", floorHeight: "n/a", core: "n/a", mep: "new", zoningClass: "commercial→industrial rezone", other: "highway access" },
    blockers: ["municipal resistance to de-retailing", "tax-base politics"],
    examples: [
      { project: "Randall Park Mall → Amazon fulfillment center", city: "North Randall OH", yearFrom: 2017, yearTo: 2018, source: "press (Cleveland.com)", url: null },
      { project: "Euclid Square Mall → Amazon fulfillment center", city: "Euclid OH", yearFrom: 2016, yearTo: 2018, source: "press", url: null }
    ]
  },
  {
    from: "shopping mall", to: "medical", likelihood: "medium",
    basis: "Hospitals lease dead anchors for outpatient care: parking, single-level spans, and arterial access transfer directly.",
    preconditions: { structure: "retained", span: "wide", floorHeight: "adequate for plenum", core: "n/a", mep: "clinical-grade retrofit", zoningClass: "commercial (clinic use)", other: "health-system tenant" },
    blockers: ["imaging/OR loads exceed structure"],
    examples: [
      { project: "One Hundred Oaks Mall → Vanderbilt Health", city: "Nashville TN", yearFrom: 2009, yearTo: null, source: "Vanderbilt Health; press", url: null }
    ]
  },
  {
    from: "shopping mall", to: "housing / mixed-use", likelihood: "medium",
    basis: "Mall sites are entitled, transit-served superblocks; conversion is usually site-level redevelopment, not building reuse.",
    preconditions: { structure: "mostly demolition", span: "n/a", floorHeight: "n/a", core: "n/a", mep: "new", zoningClass: "specific-plan rezone", other: "regional housing pressure" },
    blockers: ["entitlement duration", "existing anchor leases (REA agreements)"],
    examples: [
      { project: "Westfield Promenade 2035 master plan (approved)", city: "Los Angeles (Warner Center)", yearFrom: 2019, yearTo: null, source: "LA City Planning approval; press", url: null }
    ]
  },
  {
    from: "parking structure", to: "any occupied program", likelihood: "low",
    basis: "Sloped slabs, low clear heights, and ramp cores make retrofit costlier than replacement; flat-plate 'convertible' garages are a designed exception, rarely yet executed.",
    preconditions: { structure: "flat slabs only", span: "regular grid", floorHeight: "≥3.4 m clear — rare", core: "external ramps (removable)", mep: "everything new", zoningClass: "any", other: "designed-for-conversion from day one" },
    blockers: ["sloped floor plates", "2.1–2.4 m clear heights", "live-load and vibration limits"],
    examples: [
      { project: "84.51° Centre (garage floors designed convertible to office)", city: "Cincinnati OH", yearFrom: 2015, yearTo: null, source: "architect (Gensler) publications", url: null }
    ]
  },
  {
    from: "hotel / motel", to: "supportive & affordable housing", likelihood: "high",
    basis: "Room-per-unit match makes this the cheapest housing conversion; California institutionalized it as a funded program.",
    preconditions: { structure: "retained as-is", span: "n/a", floorHeight: "as-built", core: "as-built", mep: "kitchenette additions", zoningClass: "by-right under Homekey/AB projects", other: "public funding stream" },
    blockers: ["operating-cost funding after acquisition"],
    examples: [
      { project: "Project Homekey motel conversions (statewide program)", city: "California", yearFrom: 2020, yearTo: null, source: "CA HCD Homekey program records", url: null },
      { project: "Cecil Hotel → affordable/supportive housing", city: "Los Angeles", yearFrom: 2021, yearTo: null, source: "press (LA Times)", url: null }
    ]
  },
  {
    from: "church / religious", to: "event venue / housing", likelihood: "medium",
    basis: "Declining congregations free high-volume naves; 'yes in God's backyard' legislation (CA SB 4, 2023) opens the housing path on the land.",
    preconditions: { structure: "retained shell", span: "single grand volume", floorHeight: "very high", core: "new", mep: "new", zoningClass: "SB4 / conditional use", other: "acoustics suit events & music" },
    blockers: ["historic-preservation constraints", "congregation politics"],
    examples: [
      { project: "Vibiana (St. Vibiana's Cathedral → event venue)", city: "Los Angeles", yearFrom: 2005, yearTo: null, source: "LA Conservancy; venue history", url: null }
    ]
  },
  {
    from: "theater / cinema", to: "retail / church / hotel amenity", likelihood: "medium",
    basis: "Single-volume, zero-daylight boxes resist most uses; they survive as assembly (church, venue) or as the flagship space of a larger conversion.",
    preconditions: { structure: "retained", span: "one long-span volume", floorHeight: "very high", core: "minimal", mep: "assembly-grade", zoningClass: "commercial", other: "assembly occupancy continuity" },
    blockers: ["raked floors", "no daylight", "historic interiors"],
    examples: [
      { project: "Broadway theaters as churches/retail (Los Angeles Theatre district)", city: "Los Angeles", yearFrom: 1980, yearTo: null, source: "LA Conservancy Broadway initiative", url: null },
      { project: "Michigan Theatre → parking garage (cautionary reverse case)", city: "Detroit MI", yearFrom: 1977, yearTo: null, source: "press; architectural histories", url: null }
    ]
  },
  {
    from: "train station", to: "museum / innovation campus", likelihood: "medium",
    basis: "Monumental halls with civic meaning attract flagship institutional reuse once rail volume collapses.",
    preconditions: { structure: "retained", span: "great hall", floorHeight: "monumental", core: "new", mep: "new", zoningClass: "civic/master plan", other: "flagship sponsor" },
    blockers: ["scale of capital", "decades of vacancy decay"],
    examples: [
      { project: "Michigan Central Station → Ford mobility campus", city: "Detroit MI", yearFrom: 2018, yearTo: 2024, source: "Ford announcements; press", url: null },
      { project: "Gare d'Orsay → Musée d'Orsay", city: "Paris", yearFrom: 1979, yearTo: 1986, source: "Musée d'Orsay official history", url: null }
    ]
  },
  {
    from: "power plant", to: "culture / retail / mixed-use", likelihood: "medium",
    basis: "Turbine halls are the largest found volumes in cities; conversion succeeds where land value is extreme.",
    preconditions: { structure: "heavy shell retained", span: "extreme", floorHeight: "extreme", core: "new inserted floors", mep: "new", zoningClass: "master-plan rezone", other: "remediation funding" },
    blockers: ["contamination", "shell-scale maintenance"],
    examples: [
      { project: "Battersea Power Station → retail/office/housing (Apple UK HQ)", city: "London", yearFrom: 2013, yearTo: 2022, source: "developer; press (Guardian)", url: null },
      { project: "Tate Modern (see factory→museum)", city: "London", yearFrom: 2000, yearTo: null, source: "Tate official history", url: null }
    ]
  },
  {
    from: "jail / institutional", to: "hotel", likelihood: "low",
    basis: "Cellular structure maps to rooms but stigma and layout limit it to landmark one-offs.",
    preconditions: { structure: "retained", span: "cellular", floorHeight: "as-built", core: "new", mep: "new", zoningClass: "conditional", other: "landmark cachet" },
    blockers: ["stigma", "cell dimensions below room minimums"],
    examples: [
      { project: "Liberty Hotel (Charles Street Jail)", city: "Boston MA", yearFrom: 2001, yearTo: 2007, source: "hotel history; press", url: null }
    ]
  }
];
