'use strict';
// P1.5 acceptance audit: extracts the LIVE computeLayout (+ parse/isShort) from replica3.js
// (byte-verified in sync with the HTML), applies the SAME subdivideBlock post-process just added
// to program-massing-shortfloor.html (copied verbatim below), then checks:
//   (a) every rendered non-SHORT program block has wMod<=MAX_SIDE_MOD AND dMod<=MAX_SIDE_MOD
//   (b) sum of sub-block areas per parent room == parent room area (within 0.5 m^2)
// SHORT rects are exempt (buildShortBlocks renders them cell-by-cell already).
const fs = require('fs');
const dir = __dirname + '/';
const src = fs.readFileSync(dir + 'replica3.js', 'utf8');
const wrapped = src.replace(/const dir = __dirname.*$/s, 'module.exports={parse,computeLayout,isShort};');
eval(wrapped);
const { parse, computeLayout, isShort } = module.exports;

const MA = 8.5 * 0.3048 * 8.5 * 0.3048;
const MAX_SIDE_MOD = 4;
function subdivideBlock(r) {
  if (isShort(r.type)) return [r];
  if (r.wMod <= MAX_SIDE_MOD && r.dMod <= MAX_SIDE_MOD) return [r];
  const splitDim = n => {
    if (n <= MAX_SIDE_MOD) return [n];
    const parts = Math.ceil(n / MAX_SIDE_MOD), base = Math.floor(n / parts), rem = n % parts;
    return Array.from({ length: parts }, (_, i) => base + (i < rem ? 1 : 0));
  };
  const wParts = splitDim(r.wMod), dParts = splitDim(r.dMod), totalCells = r.wMod * r.dMod;
  const out = []; let z = r.zMod;
  for (const dj of dParts) {
    let x = r.xMod;
    for (const wi of wParts) { out.push({ ...r, xMod: x, zMod: z, wMod: wi, dMod: dj, area: r.area * (wi * dj) / totalCells }); x += wi; }
    z += dj;
  }
  return out;
}

function audit(file) {
  const prog = parse(fs.readFileSync(dir + file, 'utf8'));
  const L = computeLayout(prog);
  let maxW = 0, maxD = 0, oversizeBefore = 0, blocksAfter = 0, worstAreaDiff = 0, checkedRooms = 0, fail = false;
  for (const lv of L.levels) {
    const rects = L.floorRects.get(lv);
    let parentId = 0;
    for (const r of rects) {
      if (r.wMod > MAX_SIDE_MOD || r.dMod > MAX_SIDE_MOD) oversizeBefore++;
      const parentArea = r.area;
      const kids = subdivideBlock(r);
      blocksAfter += kids.length;
      let sumA = 0;
      for (const k of kids) {
        if (!isShort(k.type)) { maxW = Math.max(maxW, k.wMod); maxD = Math.max(maxD, k.dMod); if (k.wMod > MAX_SIDE_MOD || k.dMod > MAX_SIDE_MOD) fail = true; }
        sumA += k.area;
      }
      const diff = Math.abs(sumA - parentArea);
      worstAreaDiff = Math.max(worstAreaDiff, diff);
      if (diff > 0.5) fail = true;
      checkedRooms++;
      parentId++;
    }
  }
  console.log(`${file}: rooms=${checkedRooms} oversizeBefore=${oversizeBefore} blocksAfter=${blocksAfter} maxW(non-short)=${maxW} maxD(non-short)=${maxD} worstAreaDiff=${worstAreaDiff.toFixed(4)}m2  => ${fail ? 'FAIL' : 'PASS'}`);
}
const files = process.argv.slice(2).filter(a => a.endsWith('.txt'));
for (const f of (files.length ? files : ['case_all.txt', 'case_learning.txt', 'sample.txt'])) audit(f);
