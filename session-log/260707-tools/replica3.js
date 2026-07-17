'use strict';
// Replica of program-massing-shortfloor.html layout stage.
//   --before : CURRENT-of-yesterday buggy path (float-min scan, one-sided plate)  [reference]
//   default  : P1 CORNER-CORE PARTI (§0.5) — coreS at SW (x0), coreN at NE (FW-cwN);
//              corner-justified packing (south L->R after coreS, north R->L flush coreN);
//              plate floors right-anchored over coreN. opt=edge.
//   --opt=inset : LEGACY option-B scan/pack (reworked in P4); kept running, not the P1 target.
// splitSides / rectDims copied verbatim from the HTML; computeLayout mirrors the HTML edit.
const fs = require('fs');
const BEFORE = process.argv.includes('--before');
const CORE_OPTION = (process.argv.find(a => a.startsWith('--opt=')) || '--opt=compact').split('=')[1];
const CORE_INSET_MOD = 4;

const isCore = t => /fire stair|elevator|escalator|\bstair\b|\bcore\b|shaft/i.test(t);
const isFreight = t => /freight/i.test(t);
const isShort = t => /coffee|showroom|pop[- ]?up|exhibition|event hall|\bdemo\b|classroom|seminar|computer lab|project review|yoga|pilates|fitness|recovery lounge|physical therapy|meditation|health coaching|lounge bar/i.test(t);
const isCorridor = t => /circulation|corridor|hallway/i.test(t);
const isSelfServed = t => /foyer|lobby|atrium|entrance|toilet|restroom|\bwc\b|storage|mechanical|electrical|loading|\bplant\b/i.test(t);
const FT = 0.3048, MODULE = 8.5 * FT, MA = MODULE * MODULE;

function parse(raw) {
  const rows = [];
  for (const line of raw.split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const parts = t.split('/').map(s => s.replace(/[{}]/g, '').trim());
    if (parts.length < 3) continue;
    const type = parts[0].toLowerCase();
    const area = parseFloat(parts[1]);
    const level = parseInt(parts[2], 10);
    if (!type || isNaN(level) || isNaN(area)) continue;
    let w = 0, h = 0;
    for (let i = 3; i < parts.length; i++) { if (parts[i] && parts[i].includes(',')) { const [a, b] = parts[i].split(',').map(parseFloat); if (!isNaN(a) && !isNaN(b)) { w = a; h = b; } break; } }
    if (!w || !h) { w = h = Math.sqrt(area); }
    rows.push({ type, area, level, category: 'private', w, h, isCore: isCore(type) });
  }
  return rows;
}
function rectDims(area, hPref) {
  const mods = Math.max(1, Math.round(area / MA));
  const d = Math.max(1, Math.min(mods, Math.round((hPref || Math.sqrt(area)) / MODULE)));
  const w = Math.max(1, Math.round(mods / d));
  return { w, d };
}
function splitSides(rooms) {
  const north = [], south = []; let nW = 0, sW = 0;
  for (const r of [...rooms].sort((a, b) => b.wMod - a.wMod)) {
    if (nW <= sW) { north.push(r); nW += r.wMod; } else { south.push(r); sW += r.wMod; }
  }
  const anyShort = a => a.some(r => isShort(r.type)), longsOf = a => a.filter(r => !isShort(r.type));
  const moveLong = (from, to) => { const L = longsOf(from)[0]; from.splice(from.indexOf(L), 1); to.push(L); };
  const lN = longsOf(north), lS = longsOf(south);
  if (anyShort(north) && lN.length === 0 && lS.length === 1 && !anyShort(south)) moveLong(south, north);
  else if (anyShort(south) && lS.length === 0 && lN.length === 1 && !anyShort(north)) moveLong(north, south);
  nW = north.reduce((s, r) => s + r.wMod, 0); sW = south.reduce((s, r) => s + r.wMod, 0);
  return { north, south, nW, sW };
}
// do two rects share ≥1 module edge in plan (adjacency) or overlap? (§0.7 connectivity)
function rectsTouch(A, B) {
  const ax2 = A.xMod + A.wMod, az2 = A.zMod + A.dMod, bx2 = B.xMod + B.wMod, bz2 = B.zMod + B.dMod;
  const xOv = Math.min(ax2, bx2) - Math.max(A.xMod, B.xMod), zOv = Math.min(az2, bz2) - Math.max(A.zMod, B.zMod);
  if (xOv >= 1 && zOv >= 1) return true;                            // overlap
  if (xOv >= 1 && (az2 === B.zMod || bz2 === A.zMod)) return true;  // shared horizontal edge
  if (zOv >= 1 && (ax2 === B.xMod || bx2 === A.xMod)) return true;  // shared vertical edge
  return false;
}
// greedy maximal-rectangle cover of a Set of "x,z" cells (for the plate slab minus core holes)
function coverRects(cells) {
  const rem = new Set(cells); const rects = [];
  while (rem.size) {
    let bx = Infinity, bz = Infinity;
    for (const k of rem) { const c = k.indexOf(','); const x = +k.slice(0, c), z = +k.slice(c + 1); if (z < bz || (z === bz && x < bx)) { bz = z; bx = x; } }
    let w = 0; while (rem.has((bx + w) + ',' + bz)) w++;
    let h = 0, ok = true; while (ok) { for (let i = 0; i < w; i++) if (!rem.has((bx + i) + ',' + (bz + h))) { ok = false; break; } if (ok) h++; }
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) rem.delete((bx + i) + ',' + (bz + j));
    rects.push({ xMod: bx, zMod: bz, wMod: w, dMod: h });
  }
  return rects;
}
function computeLayout(program) {
  const levels = [...new Set(program.map(p => p.level))].sort((a, b) => a - b);
  const coreTypes = new Map();
  for (const c of program) { if (!c.isCore) continue; let e = coreTypes.get(c.type); if (!e) { e = { type: c.type, repArea: 0, minL: c.level, maxL: c.level, category: 'circulation', isCore: true }; coreTypes.set(c.type, e); } e.repArea = Math.max(e.repArea, c.area); e.minL = Math.min(e.minL, c.level); e.maxL = Math.max(e.maxL, c.level); }
  const cts = [...coreTypes.values()].sort((a, b) => (isFreight(b.type) - isFreight(a.type)) || b.repArea - a.repArea);
  cts.forEach(ct => { const d = rectDims(ct.repArea, Math.sqrt(ct.repArea)); ct.wMod = d.w; ct.dMod = d.d; });
  const coreS = cts[0] || null, coreN = cts[1] || null;
  const cwN = coreN ? coreN.wMod : 0, cwS = coreS ? coreS.wMod : 0;

  const LEGACY = BEFORE || CORE_OPTION === 'inset';   // option B / pre-fix reference path
  const PINWHEEL = CORE_OPTION === 'pinwheel';        // Scheme 2 (corner cores + parity)
  const COMPACT = !LEGACY && !PINWHEEL;               // Scheme 1 (float-min embedded coreN) — DEFAULT
  let floorSplit = new Map(), northDepth = 1, southDepth = 1, maxNW = 0, maxSW = 0;
  let FD, zMid, coreSx, coreNx, FW, coreShafts = [], floorRects = new Map();
  const plateInfo = new Map();

  if (PINWHEEL) {
    // ── plate-floor detection: single LONG room, or largest room > 70% of packed area ──
    for (const lv of levels) {
      const rs = program.filter(p => p.level === lv && !p.isCore && !isCorridor(p.type));
      if (!rs.length) continue;
      const tot = rs.reduce((s, r) => s + r.area, 0); const mx = Math.max(...rs.map(r => r.area)); const dom = rs.find(r => r.area === mx);
      if ((rs.length === 1 || mx / tot > 0.70) && !isShort(dom.type)) plateInfo.set(lv, { cells: Math.max(1, Math.round(tot / MA)), area: tot, type: dom.type, category: dom.category || 'private' });
    }
  }
  // ── per-floor split + depths + band widths (plate floors EXCLUDED in the edge parti) ──
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
  if (PINWHEEL) {
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
        if (w > runW) { if (process.env.P2LOG) console.log('   [P2 fallback] ' + r.type + ' w' + w + '>' + runW); continue; }   // fallback: keep original dims
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
        if (process.env.P2LOG) console.log('   [P2 egress-guard] reverted L' + l0);
      }
    }
    for (const s of floorSplit.values()) for (const r of [...s.north, ...s.south]) delete r.p2orig;
  }
  for (const s of floorSplit.values()) {
    northDepth = Math.max(northDepth, 1, coreN ? coreN.dMod : 1, ...s.north.map(r => r.dMod));
    southDepth = Math.max(southDepth, 1, coreS ? coreS.dMod : 1, ...s.south.map(r => r.dMod));
    maxNW = Math.max(maxNW, s.nW); maxSW = Math.max(maxSW, s.sW);
  }
  FD = southDepth + 1 + northDepth; zMid = southDepth;
  const bandMax = Math.max(maxNW, maxSW), minSep = cwS + cwN + 1;

  const shortLvl = new Set(levels.filter(l => program.some(p => p.level === l && !p.isCore && !isCorridor(p.type) && isShort(p.type))));
  const lvIdx = new Map(levels.map((l, i) => [l, i]));
  const clusterFloor = l => { if (!shortLvl.has(l)) return false; const i = lvIdx.get(l); return shortLvl.has(levels[i - 1]) || shortLvl.has(levels[i + 1]); };

  if (LEGACY || COMPACT) {
    // ── Scheme 1 COMPACT (INSET=0) + parked LEGACY (option B / --before): float-min coreN scan +
    //    left-anchored core-skip pack. Compact: coreN embedded (float→0), wider floors WRAP it. ──
    const INSET = CORE_OPTION === 'inset' ? Math.max(0, Math.min(CORE_INSET_MOD, bandMax - 1)) : 0;
    coreSx = INSET;
    const anchorHi = Math.max(Math.max(maxNW, minSep) - INSET, coreSx + cwS);
    const eLoAdj = coreSx + cwS + 1;
    const eLoRem = coreSx + cwS / 2 - cwN / 2 + Math.ceil(bandMax / 3);
    const lo = Math.min(Math.max(coreSx + cwS, Math.ceil(Math.max(eLoAdj, eLoRem))), anchorHi);
    const agN = levels.filter(l => l >= 0 && coreN && l >= coreN.minL && l <= coreN.maxL).map(l => floorSplit.get(l).nW);
    let bestX = lo, bestObj = Infinity;
    for (let cx = lo; cx <= anchorHi; cx++) { let obj = 0; for (const nw of agN) obj += Math.max(0, cx - nw); if (obj <= bestObj) { bestObj = obj; bestX = cx; } }
    coreNx = bestX;
    if (CORE_OPTION === 'inset') coreNx = Math.max(coreSx + cwS + 1, coreNx - INSET);
    if (coreS) coreShafts.push({ ...coreS, xMod: coreSx, zMod: zMid - coreS.dMod });
    if (coreN) coreShafts.push({ ...coreN, xMod: coreNx, zMod: zMid + 1 });
    function packLegacy(progs, side, lv) {
      let list = [...progs].sort((a, b) => b.wMod - a.wMod);
      if (clusterFloor(lv)) { const longs = list.filter(p => !isShort(p.type)), shorts = list.filter(p => isShort(p.type)); list = [...shorts, ...longs]; }
      const coreW = side === 'south' ? cwS : cwN, coreLo = side === 'south' ? coreSx : coreNx, coreHi = coreLo + coreW;
      const zOf = p => side === 'north' ? zMid + 1 : zMid - p.dMod;
      let x = 0; const out = [];
      for (const p of list) {
        let w = p.wMod;
        // COMPACT splits a core-crossing room around the shaft (contiguous wrap); LEGACY keeps the plain jump
        if (coreW > 0 && x < coreHi && x + w > coreLo) {
          if (COMPACT && x < coreLo) { const pre = coreLo - x; out.push({ ...p, xMod: x, wMod: pre, area: p.area * pre / p.wMod, zMod: zOf(p), side }); w -= pre; }
          x = coreHi;
        }
        if (w > 0) { out.push({ ...p, xMod: x, wMod: w, area: w === p.wMod ? p.area : p.area * w / p.wMod, zMod: zOf(p), side }); x += w; }
      }
      return out;
    }
    for (const lv of levels) { const { north, south } = floorSplit.get(lv); floorRects.set(lv, [...packLegacy(north, 'north', lv), ...packLegacy(south, 'south', lv)]); }
    FW = BEFORE ? Math.max(1, ...levels.flatMap(lv => floorRects.get(lv).map(r => r.xMod + r.wMod)), ...coreShafts.map(c => c.xMod + c.wMod)) : 1;
    if (!BEFORE) { for (const lv of levels) for (const r of floorRects.get(lv)) FW = Math.max(FW, r.xMod + r.wMod); for (const c of coreShafts) FW = Math.max(FW, c.xMod + c.wMod); }
  } else {
    // ── EDGE compact-bar parti (P5, SIXTH directive 260708) ──
    //   coreS pinned at SW (x0). coreN pinned to the TRUE NE corner: coreNx = cwS + winMax, where
    //   winMax = the widest COMMON double-loaded window Wwin(lv)=max(sW,nW) over ALL above-grade
    //   floors, folding in each plate floor's slab width. Envelope [0, coreNx+cwN] is FIXED. The
    //   GL-only E0 and the dense/sparse split are RETIRED: every non-plate floor packs both bands
    //   over ONE common window (unified scan), hugging coreS by tie-break.
    coreSx = 0;
    let winMax = bandMax;                 // bandMax = max(maxNW,maxSW) = winMax for non-plate floors
    for (const [lv, info] of plateInfo) {
      if (lv < 0) continue;               // above-grade only
      winMax = Math.max(winMax, Math.ceil(info.cells / (southDepth + northDepth)));
    }
    coreNx = Math.max(cwS + 1, cwS + winMax);   // right end of the widest window = true NE corner
    FW = coreNx + cwN;                          // fixed envelope
    if (coreS) coreShafts.push({ ...coreS, xMod: coreSx, zMod: zMid - coreS.dMod });
    if (coreN) coreShafts.push({ ...coreN, xMod: coreNx, zMod: zMid + 1 });
    // order a band width-desc; SHORT anchors first from the window's LEFT edge (hugs coreS)
    const orderList = (progs, lv, anchorRight) => {
      let list = [...progs].sort((a, b) => b.wMod - a.wMod);
      if (clusterFloor(lv)) { const longs = list.filter(p => !isShort(p.type)), shorts = list.filter(p => isShort(p.type)); list = anchorRight ? [...longs, ...shorts] : [...shorts, ...longs]; }
      return list;
    };
    const layLR = (list, x0, side) => { let x = x0; const out = []; for (const p of list) { out.push({ ...p, xMod: x, zMod: side === 'north' ? zMid + 1 : zMid - p.dMod, side }); x += p.wMod; } return out; };
    // plate slab: pack into window [w0, w0+wPlate), same overlap-with-below objective + hug-coreS
    //   tie-break as the unified scan; grows RIGHTWARD from w0, skipping the corridor row + core cells.
    function plateRects(lv, info, w0) {
      const budget = info.cells;
      const coreNa = coreN && lv >= coreN.minL && lv <= coreN.maxL, coreSa = coreS && lv >= coreS.minL && lv <= coreS.maxL;
      const isCoreCell = (x, z) => {
        if (coreSa && x >= coreSx && x < coreSx + cwS && z >= zMid - coreS.dMod && z < zMid) return true;
        if (coreNa && x >= coreNx && x < coreNx + cwN && z >= zMid + 1 && z < zMid + 1 + coreN.dMod) return true;
        return false;
      };
      const rows = []; for (let z = zMid - southDepth; z < zMid; z++) rows.push(z); for (let z = zMid + 1; z <= zMid + northDepth; z++) rows.push(z);
      const cells = new Set(); let cnt = 0;
      for (let x = w0; cnt < budget; x++) { for (const z of rows) { if (cnt >= budget) break; if (isCoreCell(x, z)) continue; cells.add(x + ',' + z); cnt++; } }
      const rects = coverRects(cells); const totC = rects.reduce((s, r) => s + r.wMod * r.dMod, 0) || 1;
      return rects.map(r => ({ ...r, type: info.type, category: info.category, area: info.area * (r.wMod * r.dMod) / totC, side: r.zMod > zMid ? 'north' : 'south', plate: true }));
    }
    const progColsOf = rects => { const s = new Set(); for (const r of rects) for (let i = r.xMod; i < r.xMod + r.wMod; i++) s.add(i); return s; };
    const shortCellsOf = rects => { const s = new Set(); for (const r of rects) if (isShort(r.type)) for (let i = r.xMod; i < r.xMod + r.wMod; i++) for (let j = r.zMod; j < r.zMod + r.dMod; j++) s.add(i + ',' + j); return s; };
    const overlapCount = (cols, prev) => { let n = 0; if (prev) for (const i of cols) if (prev.has(i)) n++; return n; };
    // PINWHEEL parity: even above-grade floor hugs coreS (left), odd hugs coreN (right) — both cores engage.
    const agLevels = levels.filter(l => l >= 0);
    const agIdx = new Map(agLevels.map((l, i) => [l, i]));
    const hugN = lv => lv >= 0 && (agIdx.get(lv) % 2 === 1);
    let prevCols = null, prevShort = null;
    for (const lv of levels) {            // bottom-up so every window/plate stacks on the floor below
      if (plateInfo.has(lv)) {
        const info = plateInfo.get(lv);
        const wPlate = Math.max(1, Math.min(winMax, Math.ceil(info.cells / (southDepth + northDepth))));
        let bw0 = coreSx + cwS, bScore = -Infinity, bTie = Infinity;
        for (let w0 = coreSx + cwS; w0 <= coreNx - wPlate; w0++) {
          const cols = new Set(); for (let i = w0; i < w0 + wPlate; i++) cols.add(i);
          const score = overlapCount(cols, prevCols);
          const tie = w0 - (coreSx + cwS);
          if (score > bScore || (score === bScore && tie < bTie)) { bScore = score; bTie = tie; bw0 = w0; }
        }
        const pr = plateRects(lv, info, bw0);
        floorRects.set(lv, pr); prevCols = progColsOf(pr); prevShort = shortCellsOf(pr); continue;
      }
      const { north, south, nW, sW } = floorSplit.get(lv);
      const Wwin = Math.max(sW, nW);
      // UNIFIED compact-window packing: both bands share ONE contiguous window [w0, w0+Wwin) — widths
      //   do NOT add. Scan w0 in [cwS, coreNx-Wwin] (never overflows either core); objective = overlap
      //   with the floor below (SHORT-cell for cluster floors, else program-column); tie-break hugs
      //   coreS (minimize w0−cwS). The widest floor has a single valid w0=cwS (full bar).
      const anchorR = hugN(lv);
      const sList = orderList(south, lv, anchorR), nList = orderList(north, lv, anchorR);
      const useShort = clusterFloor(lv) && prevShort && prevShort.size;
      let best = null, bScore = -Infinity, bTie = Infinity;
      for (let w0 = coreSx + cwS; w0 <= coreNx - Wwin; w0++) {
        const cand = [...layLR(sList, w0, 'south'), ...layLR(nList, w0, 'north')];
        const score = useShort ? [...shortCellsOf(cand)].filter(k => prevShort.has(k)).length : overlapCount(progColsOf(cand), prevCols);
        const tie = anchorR ? ((coreNx - Wwin) - w0) : (w0 - (coreSx + cwS));
        if (score > bScore || (score === bScore && tie < bTie)) { bScore = score; bTie = tie; best = cand; }
      }
      const rects = best || [];
      floorRects.set(lv, rects);
      prevCols = progColsOf(rects); prevShort = shortCellsOf(rects);
    }
  }
  // ── corridor = single shortest connector per floor: minimal interval over all program columns,
  //    extended to reach the nearest active core (§0.6.2). A floor drops its corridor ONLY if EVERY
  //    room already directly touches a core shaft (§0.7); otherwise it gets the minimal spine. ──
  const floorCorr = new Map();
  for (const lv of levels) {
    const rects = floorRects.get(lv);
    const active = coreShafts.filter(c => lv >= c.minL && lv <= c.maxL);
    if (!rects.length || rects.every(r => active.some(c => rectsTouch(r, c)))) { floorCorr.set(lv, []); continue; }
    let lo = Infinity, hi = -Infinity;
    for (const r of rects) { lo = Math.min(lo, r.xMod); hi = Math.max(hi, r.xMod + r.wMod); }
    const inside = active.some(c => c.xMod <= hi && c.xMod + c.wMod >= lo);   // overlap OR adjacency counts as reached
    if (active.length && !inside) {
      let best = null, bd = Infinity;
      for (const c of active) { const d = Math.max(0, lo - (c.xMod + c.wMod), c.xMod - hi); if (d < bd) { bd = d; best = c; } }
      if (best) { lo = Math.min(lo, best.xMod); hi = Math.max(hi, best.xMod + best.wMod); }
    }
    floorCorr.set(lv, [{ xMod: lo, zMod: zMid, wMod: hi - lo, dMod: 1 }]);
  }
  return { levels, floorRects, floorCorr, coreShafts, FW, FD, cwN, cwS, coreSx, coreNx, coreN, coreS, maxNW, maxSW, bandMax, minSep, northDepth, southDepth, zMid, plateInfo };
}

function shortCols(rects) {
  const s = new Set();
  for (const r of rects) if (isShort(r.type)) for (let i = r.xMod; i < r.xMod + r.wMod; i++) for (let j = r.zMod; j < r.zMod + r.dMod; j++) s.add(i + ',' + j);
  return s;
}
function bandCompact(rects, side, L) {
  const rs = rects.filter(r => r.side === side);
  if (!rs.length) return null;
  const cols = new Set(); let lo = Infinity, hi = -Infinity;
  for (const r of rs) { for (let i = r.xMod; i < r.xMod + r.wMod; i++) cols.add(i); lo = Math.min(lo, r.xMod); hi = Math.max(hi, r.xMod + r.wMod); }
  const coreW = side === 'south' ? L.cwS : L.cwN, coreX = side === 'south' ? L.coreSx : L.coreNx;
  let gap = 0;
  for (let i = lo; i < hi; i++) { if (cols.has(i)) continue; if (coreW > 0 && i >= coreX && i < coreX + coreW) continue; gap++; }
  return { occ: cols.size, bbox: hi - lo, fill: cols.size / (hi - lo), gap };
}
function analyze(label, raw) {
  const prog = parse(raw);
  const L = computeLayout(prog);
  const COMPACT = !(BEFORE || CORE_OPTION === 'inset' || CORE_OPTION === 'pinwheel');   // mirror computeLayout scheme flag
  if (process.env.DUMP) {
    for (const lv of L.levels) {
      const rs = L.floorRects.get(lv);
      const nb = rs.filter(r => r.side === 'north').map(r => `${r.xMod}:${r.wMod}${isShort(r.type) ? 's' : ''}`).join(' ');
      const sb = rs.filter(r => r.side === 'south').map(r => `${r.xMod}:${r.wMod}${isShort(r.type) ? 's' : ''}`).join(' ');
      console.log(`   L${lv}  N[${nb}]  S[${sb}]`);
    }
  }
  // (a) core separation (center-to-center)
  const sCen = L.coreSx + L.cwS / 2, nCen = L.coreNx + L.cwN / 2;
  const sep = nCen - sCen;
  // (b) per-floor anchor-gap: distance from the floor's program mass to its NEAREST active core
  //     (0 when the mass touches/wraps a core). Dense north touches coreN; sparse windows touch their
  //     nearest core; plate wraps coreN → all should be 0 by construction.
  const gaps = [], agGaps = [];
  for (const lv of L.levels) {
    const rs = L.floorRects.get(lv); if (!rs.length) continue;
    const active = L.coreShafts.filter(c => lv >= c.minL && lv <= c.maxL); if (!active.length) continue;
    let lo = Infinity, hi = -Infinity;
    for (const r of rs) { lo = Math.min(lo, r.xMod); hi = Math.max(hi, r.xMod + r.wMod); }
    let f = Infinity;
    for (const c of active) f = Math.min(f, Math.max(0, lo - (c.xMod + c.wMod), c.xMod - hi));
    gaps.push(f); if (lv >= 0) agGaps.push(f);
  }
  const gMax = gaps.length ? Math.max(...gaps) : 0;
  const gMean = gaps.length ? gaps.reduce((s, v) => s + v, 0) / gaps.length : 0;
  const agMax = agGaps.length ? Math.max(...agGaps) : 0;
  const agMean = agGaps.length ? agGaps.reduce((s, v) => s + v, 0) / agGaps.length : 0;
  const agTouch = agGaps.length ? 100 * agGaps.filter(f => f === 0).length / agGaps.length : 0;
  const eReq = Math.ceil(L.bandMax / 3);
  const egressOK = sep >= eReq && (L.coreNx >= L.coreSx + L.cwS + 1);
  // (c) SHORT overlap
  const hasShort = lv => L.floorRects.get(lv).some(r => isShort(r.type));
  const runs = []; let cur = [];
  for (const lv of L.levels) { if (hasShort(lv)) cur.push(lv); else { if (cur.length) runs.push(cur); cur = []; } }
  if (cur.length) runs.push(cur);
  const overlaps = [];
  for (const run of runs) for (let t = 0; t < run.length - 1; t++) {
    const a = shortCols(L.floorRects.get(run[t])), b = shortCols(L.floorRects.get(run[t + 1]));
    let inter = 0; for (const k of b) if (a.has(k)) inter++;
    overlaps.push(`L${run[t]}->L${run[t + 1]}=${(b.size ? inter / b.size : 0).toFixed(3)}`);
  }
  // (d) compactness
  let maxGap = 0; const floorFills = [];
  for (const lv of L.levels) {
    for (const side of ['south', 'north']) { const c = bandCompact(L.floorRects.get(lv), side, L); if (c) maxGap = Math.max(maxGap, c.gap); }
    const rs = L.floorRects.get(lv);
    if (rs.length) { const cols = new Set(); let lo = Infinity, hi = -Infinity; for (const r of rs) { for (let i = r.xMod; i < r.xMod + r.wMod; i++) cols.add(i); lo = Math.min(lo, r.xMod); hi = Math.max(hi, r.xMod + r.wMod); } floorFills.push(cols.size / (hi - lo)); }
  }
  const avgFF = floorFills.reduce((s, v) => s + v, 0) / (floorFills.length || 1);
  // (e) per-floor contiguity: program columns must form ONE run (no orphan clump); corridor must reach a core
  const orphans = [];
  for (const lv of L.levels) {
    const rs = L.floorRects.get(lv); if (!rs.length) continue;
    const cols = new Set(); for (const r of rs) for (let i = r.xMod; i < r.xMod + r.wMod; i++) cols.add(i);
    for (const c of L.coreShafts) if (lv >= c.minL && lv <= c.maxL) for (let i = c.xMod; i < c.xMod + c.wMod; i++) cols.add(i);   // §1.3: contiguous run INCLUDES active core shaft(s)
    const lo = Math.min(...cols), hi = Math.max(...cols);
    if (hi - lo + 1 !== cols.size) orphans.push('L' + lv);
  }
  // (f) corridor Σ modules + single-segment check
  let corrTot = 0, corrMulti = 0;
  if (L.floorCorr) for (const lv of L.levels) { const cs = L.floorCorr.get(lv) || []; if (cs.length > 1) corrMulti++; for (const c of cs) corrTot += c.wMod; }
  // (i) P5 no-protrusion: every rect must sit inside [0, coreNx+cwN] — nothing past either core
  let protrude = 0;
  for (const lv of L.levels) for (const r of L.floorRects.get(lv)) { if (r.xMod < 0 || r.xMod + r.wMod > L.coreNx + L.cwN) protrude++; }
  const P2_CORR = { 'case_all.txt': 183, 'sample.txt': 164, 'case_learning.txt': 120 };
  // (g) vertical shared-column ratio for consecutive above-grade pairs
  const colsOf = lv => { const s = new Set(); for (const r of L.floorRects.get(lv)) for (let i = r.xMod; i < r.xMod + r.wMod; i++) s.add(i); return s; };
  const agL = L.levels.filter(l => l >= 0);
  const shares = [];
  for (let i = 0; i < agL.length - 1; i++) { const a = colsOf(agL[i]), b = colsOf(agL[i + 1]); let inter = 0; for (const k of b) if (a.has(k)) inter++; const den = Math.min(a.size, b.size) || 1; shares.push(`L${agL[i]}->L${agL[i + 1]}=${(inter / den).toFixed(2)}${inter / den < 0.5 ? '!' : ''}`); }
  // (h) §0.7 connectivity: an above-grade ROOM is CONNECTED if its footprint touches its level's
  //     corridor segment or an active core shaft. Plate sub-blocks are merged back into one room
  //     (grouped by type) so a room counts connected if ANY of its footprint touches.
  let agRooms = 0, agConn = 0; const disc = [];
  for (const lv of L.levels) {
    if (lv < 0) continue;
    const active = L.coreShafts.filter(c => lv >= c.minL && lv <= c.maxL);
    const corr = L.floorCorr.get(lv) || [];
    const groups = new Map();   // plate rects of one room → single group; others each their own
    L.floorRects.get(lv).forEach((r, i) => { const k = r.plate ? 'plate:' + r.type : 'r' + i; (groups.get(k) || groups.set(k, []).get(k)).push(r); });
    for (const [k, parts] of groups) {
      agRooms++;
      const conn = parts.some(r => corr.some(c => rectsTouch(r, c)) || active.some(c => rectsTouch(r, c)));
      if (conn) agConn++; else disc.push('L' + lv + ':' + parts[0].type);
    }
  }
  const connPct = agRooms ? 100 * agConn / agRooms : 100;
  // per-core engagement: fraction of above-grade floors whose mass reaches (gap 0 to) coreS / coreN
  const cS = L.coreShafts[0], cN = L.coreShafts[1];
  let sEng = 0, nEng = 0, agCnt = 0;
  for (const lv of L.levels) {
    if (lv < 0) continue; const rs = L.floorRects.get(lv); if (!rs.length) continue;
    let lo = Infinity, hi = -Infinity; for (const r of rs) { lo = Math.min(lo, r.xMod); hi = Math.max(hi, r.xMod + r.wMod); }
    let any = false;
    if (cS && lv >= cS.minL && lv <= cS.maxL) { any = true; if (Math.max(0, lo - (cS.xMod + cS.wMod), cS.xMod - hi) === 0) sEng++; }
    if (cN && lv >= cN.minL && lv <= cN.maxL) { any = true; if (Math.max(0, lo - (cN.xMod + cN.wMod), cN.xMod - hi) === 0) nEng++; }
    if (any) agCnt++;
  }
  const sPct = agCnt ? 100 * sEng / agCnt : 0, nPct = agCnt ? 100 * nEng / agCnt : 0;
  const mode = BEFORE ? 'BEFORE' : CORE_OPTION === 'inset' ? 'LEGACY-inset' : CORE_OPTION === 'pinwheel' ? 'PINWHEEL' : 'COMPACT';
  console.log(`\n== ${label} [${mode} opt=${CORE_OPTION}] ==`);
  console.log(`   FW=${L.FW}  FD=${L.FD}  cwS=${L.cwS} cwN=${L.cwN}  coreSx=${L.coreSx} coreNx=${L.coreNx}  bandMax=${L.bandMax}  plates=${[...L.plateInfo.keys()].join(',') || '-'}`);
  console.log(`   (a) core sep (c2c)=${sep.toFixed(1)}  eReq(1/3 band)=${eReq}  non-adjacent=${L.coreNx >= L.coreSx + L.cwS + 1}  egress ${egressOK ? 'OK' : 'FAIL'}`);
  console.log(`   (b) ABOVE-GRADE mass→core gap (0=touches core; >0 = §0.6.3 corridor bridge): max=${agMax}  mean=${agMean.toFixed(2)}  touch=${agTouch.toFixed(0)}%  (per-floor: ${agGaps.join(',')})`);
  console.log(`   (c) SHORT overlap: ${overlaps.join('  ')}`);
  console.log(`   (d) MAX intra-band gap=${maxGap}${maxGap === 0 ? '(contiguous)' : '(GAPS!)'}  AVG floor bbox fill=${avgFF.toFixed(3)}`);
  console.log(`   (e) orphan floors (program cols not one run): ${orphans.length ? orphans.join(',') : 'NONE'}`);
  console.log(`   (f) corridor Σ=${corrTot} mod  multi-segment floors=${corrMulti}${P2_CORR[label] !== undefined ? `  (P2 baseline=${P2_CORR[label]}, ${corrTot < P2_CORR[label] ? 'DROPPED' : corrTot === P2_CORR[label] ? 'UNCHANGED' : 'ROSE'} by ${Math.abs(corrTot - P2_CORR[label])})` : ''}`);
  console.log(`   (g) vertical shared-col ratio (min-basis, !<.5): ${shares.join('  ')}`);
  console.log(`   (h) above-grade connectivity: ${connPct.toFixed(0)}% (${agConn}/${agRooms})${disc.length ? '  disconnected: ' + disc.join(',') : ''}`);
  console.log(`   (i) P5 no-protrusion (0=nothing past either core): violations=${protrude}`);
  console.log(`   (j) per-core engagement (mass reaches core): coreS=${sPct.toFixed(0)}%  coreN=${nPct.toFixed(0)}%  of ${agCnt} above-grade floors`);
  if (!BEFORE && CORE_OPTION !== 'inset') {
    // §0.6/§0.7 structural invariants. Overlap floor: case_all/learning ≥.70, sample ≥.75.
    //   COMPACT deliberately WRAPS coreN (wider floors extend past it) so the fixed-envelope
    //   no-protrusion invariant does NOT apply — FW is recomputed from actual extents. PINWHEEL
    //   keeps the fixed envelope, so no-protrusion is still asserted.
    const ovVals = overlaps.map(o => parseFloat(o.split('=')[1]));
    const ovFloor = /sample/.test(label) ? 0.75 : 0.70;
    const ovOK = ovVals.every(v => v >= ovFloor);
    const protrudeOK = COMPACT ? true : protrude === 0;
    const pass = maxGap === 0 && orphans.length === 0 && corrMulti === 0 && egressOK && ovOK && connPct === 100 && protrudeOK;
    console.log(`   [ASSERT] contiguous:${maxGap === 0}  no-orphans:${orphans.length === 0}  corridor-1seg:${corrMulti === 0}  egress:${egressOK}  overlap>=${ovFloor}:${ovOK}  connected=100%:${connPct === 100}  ${COMPACT ? 'wrap-ok(N/A protrusion)' : 'no-protrusion:' + (protrude === 0)}  => ${pass ? 'PASS' : 'FAIL'}`);
  }
}

const dir = __dirname + '/';
const which = process.argv.find(a => a.endsWith('.txt'));
const files = which ? [which] : ['case_all.txt', 'case_learning.txt', 'sample.txt'];
for (const f of files) analyze(f, fs.readFileSync(dir + f, 'utf8'));
