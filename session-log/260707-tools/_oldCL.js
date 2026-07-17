function computeLayout(program) {
      const levels = [...new Set(program.map(p => p.level))].sort((a, b) => a - b);
      // ── core types (one continuous shaft each), embedded in the side bands ──
      const coreTypes = new Map();
      for (const c of program) { if (!c.isCore) continue; let e = coreTypes.get(c.type); if (!e) { e = { type: c.type, repArea: 0, minL: c.level, maxL: c.level, category: 'circulation', isCore: true }; coreTypes.set(c.type, e); } e.repArea = Math.max(e.repArea, c.area); e.minL = Math.min(e.minL, c.level); e.maxL = Math.max(e.maxL, c.level); }
      const cts = [...coreTypes.values()].sort((a, b) => (isFreight(b.type) - isFreight(a.type)) || b.repArea - a.repArea);

      // cores keep their own near-square footprint; freight → south band, passenger → north band
      cts.forEach(ct => { const d = rectDims(ct.repArea, Math.sqrt(ct.repArea)); ct.wMod = d.w; ct.dMod = d.d; });
      const coreS = cts[0] || null, coreN = cts[1] || null;
      const cwN = coreN ? coreN.wMod : 0, cwS = coreS ? coreS.wMod : 0;

      // 'edge' (A) = P1 CORNER-CORE PARTI (§0.5+§0.6); 'inset' (B) = LEGACY float-min scan (reworked in P4)
      const LEGACY = CORE_OPTION === 'inset';
      const floorSplit = new Map();
      let northDepth = 1, southDepth = 1, maxNW = 0, maxSW = 0;
      let FD, zMid, coreSx, coreNx, FW, coreShafts = [], floorRects = new Map();
      const plateInfo = new Map();

      if (!LEGACY) {
        // ── PLATE-floor detection: single LONG room, or largest room > 70% of packed area ──
        for (const lv of levels) {
          const rs = program.filter(p => p.level === lv && !p.isCore && !isCorridor(p.type));
          if (!rs.length) continue;
          const tot = rs.reduce((s, r) => s + r.area, 0); const mx = Math.max(...rs.map(r => r.area)); const dom = rs.find(r => r.area === mx);
          if ((rs.length === 1 || mx / tot > 0.70) && !isShort(dom.type)) plateInfo.set(lv, { cells: Math.max(1, Math.round(tot / MA)), area: tot, type: dom.type, category: dom.category || 'private' });
        }
      }
      // ── per-floor rooms (true module size) split onto the two sides; plate floors EXCLUDED from
      //    depths & band-width maxima so their big block no longer inflates FD or FW ──
      for (const lv of levels) {
        if (plateInfo.has(lv)) continue;
        const items = program.filter(p => p.level === lv && !p.isCore && !isCorridor(p.type))
          .map(p => { const d = rectDims(p.area, p.h); return { ...p, wMod: d.w, dMod: d.d }; });
        const s = splitSides(items);
        floorSplit.set(lv, s);
      }
      // ── P2 DEPTH NORMALIZATION (§P2 REVISED 260707) — edge parti only. Every non-plate LONG room
      //    on a band is re-proportioned to that floor+side's AREA-WEIGHTED modal depth D (tie →
      //    smaller D): dMod=D, wMod=ceil(cells/D), cells = round(area/MA). SHORT rooms are EXEMPT
      //    (measured 260707: normalizing SHORT breaks the vertical SHORT-weave overlap in every
      //    mode; plain count-mode flattens the big rooms and blows band widths/corridors instead).
      //    Per-room fallback: keep original dims if the normalized width exceeds the band's total
      //    run. Egress guard: if the normalized GL footprint would break the 1/3-band core
      //    separation (coreNx tracks E0), revert P2 on the E0-defining floor only. ──
      if (!LEGACY) {
        const normBand = rooms => {
          const pool = rooms.filter(r => !isShort(r.type));
          if (!pool.length) return;
          const counts = new Map();
          for (const r of pool) counts.set(r.dMod, (counts.get(r.dMod) || 0) + r.area);
          let D = 0, best = -Infinity;
          for (const [d, n] of [...counts].sort((a, b) => a[0] - b[0])) if (n > best) { best = n; D = d; }
          const runW = rooms.reduce((a, r) => a + r.wMod, 0);
          for (const r of pool) {
            if (r.dMod === D) continue;
            const cells = Math.max(1, Math.round(r.area / MA));
            const w = Math.max(1, Math.ceil(cells / D));
            if (w > runW) continue;                       // fallback: keep original dims
            r.p2orig = { w: r.wMod, d: r.dMod };
            r.wMod = w; r.dMod = D;
          }
        };
        const reW = s => { s.nW = s.north.reduce((a, r) => a + r.wMod, 0); s.sW = s.south.reduce((a, r) => a + r.wMod, 0); };
        for (const s of floorSplit.values()) { normBand(s.north); normBand(s.south); reW(s); }
        // egress guard
        const l0 = levels.find(l => l >= 0 && floorSplit.has(l));
        if (l0 !== undefined) {
          const minSep0 = cwS + cwN + 1;
          const s0 = floorSplit.get(l0);
          const E0g = Math.max(cwS + s0.sW, s0.nW + cwN, minSep0, 1);
          const cNx = Math.max(cwS + 1, E0g - cwN);
          let bm = 0; for (const s of floorSplit.values()) bm = Math.max(bm, s.nW, s.sW);
          if ((cNx + cwN / 2) - cwS / 2 < Math.ceil(bm / 3)) {
            for (const r of [...s0.north, ...s0.south]) if (r.p2orig) { r.wMod = r.p2orig.w; r.dMod = r.p2orig.d; }
            reW(s0);
          }
        }
        for (const s of floorSplit.values()) for (const r of [...s.north, ...s.south]) delete r.p2orig;
      }
      for (const s of floorSplit.values()) {
        northDepth = Math.max(northDepth, 1, coreN ? coreN.dMod : 1, ...s.north.map(r => r.dMod));
        southDepth = Math.max(southDepth, 1, coreS ? coreS.dMod : 1, ...s.south.map(r => r.dMod));
        maxNW = Math.max(maxNW, s.nW); maxSW = Math.max(maxSW, s.sW);
      }
      FD = southDepth + 1 + northDepth; zMid = southDepth;   // corridor at z = zMid
      const bandMax = Math.max(maxNW, maxSW), minSep = cwS + cwN + 1;

      const shortLvl = new Set(levels.filter(l => program.some(p => p.level === l && !p.isCore && !isCorridor(p.type) && isShort(p.type))));
      const lvIdx = new Map(levels.map((l, i) => [l, i]));
      const clusterFloor = l => { if (!shortLvl.has(l)) return false; const i = lvIdx.get(l); return shortLvl.has(levels[i - 1]) || shortLvl.has(levels[i + 1]); };

      if (LEGACY) {
        // ── LEGACY option B: float-min coreN scan + left-anchored core-skip pack (P4 reworks this) ──
        const INSET = Math.max(0, Math.min(CORE_INSET_MOD, bandMax - 1));
        coreSx = INSET;
        const anchorHi = Math.max(Math.max(maxNW, minSep) - INSET, coreSx + cwS);
        const eLoAdj = coreSx + cwS + 1;
        const eLoRem = coreSx + cwS / 2 - cwN / 2 + Math.ceil(bandMax / 3);
        const coreNxLo = Math.min(Math.max(coreSx + cwS, Math.ceil(Math.max(eLoAdj, eLoRem))), anchorHi);
        const agNW = levels.filter(l => l >= 0 && coreN && l >= coreN.minL && l <= coreN.maxL).map(l => floorSplit.get(l).nW);
        coreNx = coreNxLo; let bestFloat = Infinity;
        for (let cx = coreNxLo; cx <= anchorHi; cx++) { let f = 0; for (const nw of agNW) f += Math.max(0, cx - nw); if (f <= bestFloat) { bestFloat = f; coreNx = cx; } }
        coreNx = Math.max(coreSx + cwS + 1, coreNx - INSET);
        if (coreS) coreShafts.push({ ...coreS, xMod: coreSx, zMod: zMid - coreS.dMod });
        if (coreN) coreShafts.push({ ...coreN, xMod: coreNx, zMod: zMid + 1 });
        const packLegacy = (progs, side, lv) => {
          let list = [...progs].sort((a, b) => b.wMod - a.wMod);
          if (clusterFloor(lv)) { const longs = list.filter(p => !isShort(p.type)), shorts = list.filter(p => isShort(p.type)); list = [...shorts, ...longs]; }
          const coreW = side === 'south' ? cwS : cwN, coreX = side === 'south' ? coreSx : coreNx;
          let x = 0; const out = [];
          for (const p of list) { if (coreW > 0 && x < coreX + coreW && x + p.wMod > coreX) x = coreX + coreW; out.push({ ...p, xMod: x, zMod: side === 'north' ? zMid + 1 : zMid - p.dMod, side }); x += p.wMod; }
          return out;
        };
        for (const lv of levels) { const { north, south } = floorSplit.get(lv); floorRects.set(lv, [...packLegacy(north, 'north', lv), ...packLegacy(south, 'south', lv)]); }
        FW = 1;
        for (const lv of levels) for (const r of floorRects.get(lv)) FW = Math.max(FW, r.xMod + r.wMod);
        for (const c of coreShafts) FW = Math.max(FW, c.xMod + c.wMod);
      } else {
        // ── EDGE corner-core parti (§0.5) + compact packing (§0.6) ──
        //   coreS pinned at SW (x0); coreN pinned by the GROUND-FLOOR (level 0) footprint E0 at
        //   xN = E0 − cwN. Floors wider than E0 extend past coreN; the render grid FW is the actual
        //   max extent.
        coreSx = 0;
        const l0 = levels.find(l => l >= 0 && floorSplit.has(l));
        const s0 = l0 !== undefined ? floorSplit.get(l0) : null;
        const E0 = Math.max(s0 ? cwS + s0.sW : 0, s0 ? s0.nW + cwN : 0, minSep, cwN + cwS, 1);
        coreNx = Math.max(cwS + 1, E0 - cwN);          // NE corner of the GL footprint
        // grid = actual max extent: south grows right (cwS+maxSW); a north band wider than E0 overflows
        //   past coreN L→R from 0 (maxNW); plate/core reach coreNx+cwN.
        FW = Math.max(E0, cwS + maxSW, maxNW, coreNx + cwN, minSep, 1);
        if (coreS) coreShafts.push({ ...coreS, xMod: coreSx, zMod: zMid - coreS.dMod });
        if (coreN) coreShafts.push({ ...coreN, xMod: coreNx, zMod: zMid + 1 });
        // order a band width-desc; on cluster floors SHORT anchors first from the band's anchor edge
        const orderList = (progs, lv, anchorRight) => {
          let list = [...progs].sort((a, b) => b.wMod - a.wMod);
          if (clusterFloor(lv)) { const longs = list.filter(p => !isShort(p.type)), shorts = list.filter(p => isShort(p.type)); list = anchorRight ? [...longs, ...shorts] : [...shorts, ...longs]; }
          return list;
        };
        const layLR = (list, x0, side) => { let x = x0; const out = []; for (const p of list) { out.push({ ...p, xMod: x, zMod: side === 'north' ? zMid + 1 : zMid - p.dMod, side }); x += p.wMod; } return out; };
        const layRL = (list, xEnd, side) => { let xr = xEnd; const out = []; for (const p of list) { xr -= p.wMod; out.push({ ...p, xMod: xr, zMod: side === 'north' ? zMid + 1 : zMid - p.dMod, side }); } return out; };
        // PLATE slab: right-anchored to wrap coreN, grow leftward across both bands (skip corridor + core cells)
        const plateRects = (lv, info) => {
          const budget = info.cells;
          const coreNa = coreN && lv >= coreN.minL && lv <= coreN.maxL, coreSa = coreS && lv >= coreS.minL && lv <= coreS.maxL;
          const isCoreCell = (x, z) => {
            if (coreSa && x >= coreSx && x < coreSx + cwS && z >= zMid - coreS.dMod && z < zMid) return true;
            if (coreNa && x >= coreNx && x < coreNx + cwN && z >= zMid + 1 && z < zMid + 1 + coreN.dMod) return true;
            return false;
          };
          const rows = []; for (let z = zMid - southDepth; z < zMid; z++) rows.push(z); for (let z = zMid + 1; z <= zMid + northDepth; z++) rows.push(z);
          const cells = new Set(); let cnt = 0;
          for (let x = coreNx + cwN - 1; x >= 0 && cnt < budget; x--) { for (const z of rows) { if (cnt >= budget) break; if (isCoreCell(x, z)) continue; cells.add(x + ',' + z); cnt++; } }
          const rects = coverRects(cells); const totC = rects.reduce((s, r) => s + r.wMod * r.dMod, 0) || 1;
          return rects.map(r => ({ ...r, type: info.type, category: info.category, area: info.area * (r.wMod * r.dMod) / totC, side: r.zMod > zMid ? 'north' : 'south', plate: true }));
        };
        const progColsOf = rects => { const s = new Set(); for (const r of rects) for (let i = r.xMod; i < r.xMod + r.wMod; i++) s.add(i); return s; };
        const shortCellsOf = rects => { const s = new Set(); for (const r of rects) if (isShort(r.type)) for (let i = r.xMod; i < r.xMod + r.wMod; i++) for (let j = r.zMod; j < r.zMod + r.dMod; j++) s.add(i + ',' + j); return s; };
        const overlapCount = (cols, prev) => { let n = 0; if (prev) for (const i of cols) if (prev.has(i)) n++; return n; };
        let prevCols = null, prevShort = null;
        for (const lv of levels) {          // bottom-up so sparse windows stack on the floor below
          if (plateInfo.has(lv)) { const pr = plateRects(lv, plateInfo.get(lv)); floorRects.set(lv, pr); prevCols = progColsOf(pr); prevShort = shortCellsOf(pr); continue; }
          const { north, south, nW, sW } = floorSplit.get(lv);
          const sumBands = (cwS + sW) + (cwN + nW), Wwin = Math.max(sW, nW);
          // SPARSE (measured against the GL footprint E0) if both bands present and they would NOT
          //   touch under corner-justify (that would split the floor into two distant clumps → orphan).
          //   Sparse floors pack both bands over a COMMON contiguous window that stacks on the floor
          //   below (§0.6.1/§0.6.3).
          const sparse = sW > 0 && nW > 0 && sumBands < E0 && FW - Wwin >= 0;
          let rects;
          if (!sparse) {
            // DENSE / single-band → corner-justify: south L→R after coreS; north R→L flush at coreN.
            //   A north band wider than E0 overflows left of x0 → pack it L→R from 0 (extends past coreN).
            const nList = orderList(north, lv, true);
            const northRects = nW <= coreNx ? layRL(nList, coreNx, 'north') : layLR(nList, 0, 'north');
            rects = [...layLR(orderList(south, lv, false), coreSx + cwS, 'south'), ...northRects];
          } else {
            // SPARSE window: both bands left-aligned at w0; scan w0, keep the position that stacks best on
            //   the floor below — SHORT-cell overlap for cluster (interlock) floors, else program-column
            //   overlap; tie-break hugs the nearest active core (shorter corridor bridge, §0.6.3).
            const sList = orderList(south, lv, false), nList = orderList(north, lv, false);
            const useShort = clusterFloor(lv) && prevShort && prevShort.size;
            let best = null, bScore = -Infinity, bTie = Infinity;
            for (let w0 = 0; w0 <= FW - Wwin; w0++) {
              const cand = [...layLR(sList, w0, 'south'), ...layLR(nList, w0, 'north')];
              const score = useShort ? [...shortCellsOf(cand)].filter(k => prevShort.has(k)).length : overlapCount(progColsOf(cand), prevCols);
              const tie = Math.min(Math.max(0, w0 - (coreSx + cwS)), Math.max(0, coreNx - (w0 + Wwin)));
              if (score > bScore || (score === bScore && tie < bTie)) { bScore = score; bTie = tie; best = cand; }
            }
            rects = best;
          }
          floorRects.set(lv, rects);
          prevCols = progColsOf(rects); prevShort = shortCellsOf(rects);
        }
      }
      // ── corridor = single SHORTEST connector per floor (§0.6.2): minimal interval over all program
      //    columns, extended to reach the nearest active core. A floor drops its corridor ONLY if EVERY
      //    room already directly touches a core shaft (§0.7); otherwise it gets the minimal spine. ──
      const rectsTouch = (A, B) => {
        const ax2 = A.xMod + A.wMod, az2 = A.zMod + A.dMod, bx2 = B.xMod + B.wMod, bz2 = B.zMod + B.dMod;
        const xOv = Math.min(ax2, bx2) - Math.max(A.xMod, B.xMod), zOv = Math.min(az2, bz2) - Math.max(A.zMod, B.zMod);
        if (xOv >= 1 && zOv >= 1) return true;
        if (xOv >= 1 && (az2 === B.zMod || bz2 === A.zMod)) return true;
        if (zOv >= 1 && (ax2 === B.xMod || bx2 === A.xMod)) return true;
        return false;
      };
      const floorCorr = new Map();
      for (const lv of levels) {
        const rects = floorRects.get(lv);
        const active = coreShafts.filter(c => lv >= c.minL && lv <= c.maxL);
        if (!rects.length || rects.every(r => active.some(c => rectsTouch(r, c)))) { floorCorr.set(lv, []); continue; }
        let lo = Infinity, hi = -Infinity;
        for (const r of rects) { lo = Math.min(lo, r.xMod); hi = Math.max(hi, r.xMod + r.wMod); }
        const inside = active.some(c => c.xMod <= hi && c.xMod + c.wMod >= lo);   // overlap OR adjacency = reached
        if (active.length && !inside) {
          let bestC = null, bd = Infinity;
          for (const c of active) { const d = Math.max(0, lo - (c.xMod + c.wMod), c.xMod - hi); if (d < bd) { bd = d; bestC = c; } }
          if (bestC) { lo = Math.min(lo, bestC.xMod); hi = Math.max(hi, bestC.xMod + bestC.wMod); }
        }
        floorCorr.set(lv, [{ xMod: lo, zMod: zMid, wMod: hi - lo, dMod: 1 }]);
      }
      // ── P1.5 BLOCK SUBDIVISION (§3-P1.5): split any rect whose wMod/dMod > MAX_SIDE_MOD into a grid
      //    of adjacent blocks each ≤ MAX_SIDE_MOD per side, as evenly as possible (never a 1-wide
      //    sliver off a splittable dimension). Footprints/positions are untouched — this only adds
      //    seams — so packing, corridor, contiguity and overlap metrics computed above are unaffected.
      //    SHORT rects are exempt: buildShortBlocks already renders them cell-by-cell (porous kit), so
      //    subdividing the rect here would have no visual effect and only add dead work. Core shafts
      //    are exempt by construction (they live in coreShafts, not floorRects). ──
      for (const [lv, rects] of floorRects) floorRects.set(lv, rects.flatMap(r => subdivideBlock(r)));
      return { levels, coreShafts, floorRects, floorCorr, FW, FD };
    }
    