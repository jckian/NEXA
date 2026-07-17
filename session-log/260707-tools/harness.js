'use strict';
// Verification harness for program-input.html generateEntries.
// Loads the LIVE generateEntries source out of program-input.html (single source
// of truth) via genlib.loadGenerator, then asserts the SHORT-band contract against
// a replica of program-massing-shortfloor.html's computeShortFloors rule.
const G = require('./genlib.js');
const HTML = 'C:/SCI-Arc/SP26-RESEARCH/programAgent/program-input.html';
G.loadGenerator(HTML);

let pass = 0, fail = 0;
function assert(name, cond, detail) {
  if (cond) { pass++; console.log('  PASS  ' + name); }
  else { fail++; console.log('  FAIL  ' + name + (detail ? '  → ' + detail : '')); }
}

// per-level {tot, shrt} restricted to SHORT-receiving levels, sorted ascending
function shortBand(entries) {
  const m = G.shortLevels(entries);
  return [...m.entries()].filter(([, pf]) => pf.shrt > 0)
    .sort((a, b) => a[0] - b[0])
    .map(([lv, pf]) => ({ lv, shrt: pf.shrt, tot: pf.tot, share: pf.shrt / pf.tot }));
}
function allValid(entries) {
  for (const line of G.serialize(entries).split('\n')) {
    const r = G.validateLine(line);
    if (r.error) return { ok: false, line, err: r.error };
  }
  return { ok: true };
}
function strictlyDec(arr) { for (let i = 1; i < arr.length; i++) if (!(arr[i] < arr[i - 1])) return false; return true; }

const ALL = G.ACTIVITY_GROUPS.flatMap(([, k]) => k);
const MATRIX = [
  ['ALL activities',   ALL,                                              { minFloors: 4, exactFloors: 4 }],
  ['Show & event',     ['exhibition', 'event hall', 'showroom', 'pop-up'], { minFloors: 1 }],
  ['Learning',         ['classroom', 'seminar', 'computer lab', 'project review'], { minFloors: 1 }],
  ['Wellness',         ['yoga', 'pilates', 'fitness', 'meditation', 'recovery lounge'], { minFloors: 1 }],
  ['Social',           ['coffee', 'lounge bar'],                          { minFloors: 1 }],
  ['exhibition+coffee', ['exhibition', 'coffee'],                         { minFloors: 1 }],
  ['single coffee',    ['coffee'],                                        { minFloors: 1 }],
  ['zero activities',  [],                                               { zero: true }],
];

const GFA = 12000, ABOVE = 8, BASE = 2, BT = 'mixed-use';

for (const [name, keys, opt] of MATRIX) {
  console.log('\n══ ' + name + '  (' + keys.length + ' keys)');
  const e = G.generateEntries(BT, GFA, ABOVE, BASE, keys);
  const band = shortBand(e);
  const sfs = G.computeShortFloors(e);
  console.log('  band levels: ' + JSON.stringify(band.map(b => b.lv)) +
    '  shares: ' + JSON.stringify(band.map(b => +b.share.toFixed(3))) +
    '  raw: ' + JSON.stringify(band.map(b => b.shrt)));
  console.log('  computeShortFloors(>0.5): ' + JSON.stringify(sfs) + '  total=' + G.totalArea(e));

  const v = allValid(e);
  assert(name + ': every serialized line valid', v.ok, v.ok ? '' : v.line + ' :: ' + v.err);
  assert(name + ': total within ±2% of GFA', Math.abs(G.totalArea(e) - GFA) / GFA <= 0.02, 'total=' + G.totalArea(e));

  if (opt.zero) {
    assert(name + ': no SHORT lines emitted', !e.some(x => G.isShort(x.type)), '');
    // no "filler-only" floor: every non-core/corridor level either has full main-use
    // plate area or is the ground anchors; specifically no level above 0 should exist
    // that carries only private LONG filler with <300 m² (a stub plate). Verify each
    // above-grade level's packed area is a real plate.
    const lvls = [...new Set(e.filter(x => x.level > 0 && !G.isCore(x.type) && !G.isCorridor(x.type)).map(x => x.level))];
    const stub = lvls.filter(lv => e.filter(x => x.level === lv && !G.isCore(x.type) && !G.isCorridor(x.type))
      .reduce((s, x) => s + x.area, 0) < 300);
    assert(name + ': no filler-only/stub upper floors', stub.length === 0, 'stub levels=' + JSON.stringify(stub));
    const l0 = e.filter(x => x.level === 0 && !G.isCore(x.type) && !G.isCorridor(x.type)).map(x => x.type).sort();
    assert(name + ': ground has only lobby/sales/toilets',
      JSON.stringify(l0) === JSON.stringify(['lobby', 'sales and display', 'toilets']), JSON.stringify(l0));
    continue;
  }

  // every SHORT-receiving level must clear the collapse threshold
  assert(name + ': every SHORT level share > 0.5', band.every(b => b.share > 0.5),
    JSON.stringify(band.map(b => +b.share.toFixed(3))));
  // the computeShortFloors set must equal the SHORT-receiving set (all collapse)
  assert(name + ': every SHORT level collapses (band == shortFloors)',
    JSON.stringify(band.map(b => b.lv)) === JSON.stringify(sfs),
    'band=' + JSON.stringify(band.map(b => b.lv)) + ' sf=' + JSON.stringify(sfs));
  // strictly decreasing raw SHORT area and share up the band
  assert(name + ': SHORT raw strictly decreasing', strictlyDec(band.map(b => b.shrt)), JSON.stringify(band.map(b => b.shrt)));
  assert(name + ': SHORT share strictly decreasing', strictlyDec(band.map(b => b.share)),
    JSON.stringify(band.map(b => +b.share.toFixed(3))));
  assert(name + ': collapsed floor count ≥ ' + opt.minFloors, sfs.length >= opt.minFloors, 'count=' + sfs.length);
  if (opt.exactFloors != null)
    assert(name + ': collapses EXACTLY ' + opt.exactFloors + ' floors', sfs.length === opt.exactFloors, 'count=' + sfs.length);
}

console.log(`\n==== part 1: ${pass} passed, ${fail} failed ====`);

// ═══════════════════════════════════════════════════════════════════════
// TIERED-AREA MATRIX (rules A–E rework): rigid presets, band toilets,
// residential ≤160, office filler ≥54, adaptive core count, ±5% fidelity.
// ═══════════════════════════════════════════════════════════════════════
const RIGID_PRESET = {
  'fire stair & freight elevator core': 40,
  'fire stair & passenger elevator core a': 40,
  'fire stair & passenger elevator core b': 40,
  'circulation': 107,
  'toilets': 80,
  'parking bay group': 322,
  'mechanical room': 161,
  'electrical room': 54,
  'loading dock': 161,
};
const RES_TYPES = ['studio apartment', '1b1b apartment', '2b2b apartment'];

const MATRIX2 = [
  ['mixed 8F all',        'mixed-use', 8,  ALL],
  ['mixed 8F showevent',  'mixed-use', 8,  ['exhibition', 'event hall', 'showroom', 'pop-up']],
  ['mixed 8F learning',   'mixed-use', 8,  ['classroom', 'seminar', 'computer lab', 'project review']],
  ['mixed 8F social',     'mixed-use', 8,  ['coffee', 'lounge bar']],
  ['mixed 8F exh+coffee', 'mixed-use', 8,  ['exhibition', 'coffee']],
  ['mixed 8F zero',       'mixed-use', 8,  []],
  ['office 8F all',       'office',    8,  ALL],
  ['housing 8F all',      'housing',   8,  ALL],
  ['mixed 10F all',       'mixed-use', 10, ALL],
];

console.log('\n\n════ TIERED MATRIX ════');
const twoPct = [], fivePct = [];
for (const [name, bt, above, keys] of MATRIX2) {
  console.log('\n══ ' + name);
  const e = G.generateEntries(bt, GFA, above, BASE, keys);
  const total = G.totalArea(e);
  const dev = (total - GFA) / GFA;
  const band = shortBand(e);
  const sfs = G.computeShortFloors(e);

  // tier scale factors: calib via lobby/180; sponge via plate areas
  const lobby = e.find(x => x.type === 'lobby');
  const calibScale = lobby ? (lobby.area / 180) : NaN;
  const bandLvSet = new Set(band.map(b => b.lv));
  const plates = e.filter(x => x.type === 'office' && !bandLvSet.has(x.level));
  const fillers = e.filter(x => x.type === 'office' && bandLvSet.has(x.level));
  console.log(`  calibScale=${calibScale.toFixed(3)}  officePlates=[${plates.map(p => p.area)}]  officeFiller=[${fillers.map(p => p.area)}]`);
  console.log(`  total=${total}  dev=${(100 * dev).toFixed(2)}%  band=${JSON.stringify(band.map(b => b.lv))} shares=${JSON.stringify(band.map(b => +b.share.toFixed(3)))}`);
  if (Math.abs(dev) <= 0.02) twoPct.push(name);
  if (Math.abs(dev) <= 0.05) fivePct.push(name);

  // 1. rigid lines at exact preset
  const badRigid = e.filter(x => RIGID_PRESET[x.type] != null && x.area !== RIGID_PRESET[x.type]);
  assert(name + ': every rigid line at exact preset', badRigid.length === 0,
    JSON.stringify(badRigid.map(x => [x.type, x.area, x.level])));
  // 2. calibScale within clamp
  assert(name + ': calib scale in [0.85,1.15]', calibScale >= 0.849 && calibScale <= 1.151, 'scale=' + calibScale);
  // 3. every band level has exactly one toilets line
  const badToilet = [...bandLvSet].filter(lv => e.filter(x => x.type === 'toilets' && x.level === lv).length !== 1);
  assert(name + ': exactly one toilets per band level', badToilet.length === 0, 'levels=' + JSON.stringify(badToilet));
  // 4. band levels clear >0.5 POST-SCALING (computeShortFloors replica on final areas)
  assert(name + ': band == computeShortFloors (all clear >0.5)',
    JSON.stringify(band.map(b => b.lv)) === JSON.stringify(sfs),
    'band=' + JSON.stringify(band.map(b => b.lv)) + ' sf=' + JSON.stringify(sfs));
  // 5. SHORT raw + share strictly decreasing
  assert(name + ': SHORT raw strictly decreasing', strictlyDec(band.map(b => b.shrt)), JSON.stringify(band.map(b => b.shrt)));
  assert(name + ': SHORT share strictly decreasing', strictlyDec(band.map(b => b.share)),
    JSON.stringify(band.map(b => +b.share.toFixed(3))));
  // 6. no residential line > 160
  const badRes = e.filter(x => RES_TYPES.includes(x.type) && x.area > 160);
  assert(name + ': no residential line > 160', badRes.length === 0, JSON.stringify(badRes.map(x => [x.type, x.area])));
  // 7. office filler ≥ 54, office plates ≥ 300
  assert(name + ': office filler ≥ 54', fillers.every(x => x.area >= 54), JSON.stringify(fillers.map(x => x.area)));
  // 260707 office-plate split: a plate floor now emits k>=2 office room lines
  // (none over OFFICE_ROOM_MAX) instead of one — check the PER-FLOOR sum against
  // PLATE_MIN, not each individual line (which is intentionally now < 300).
  const plateFloorTotals = new Map();
  for (const p of plates) plateFloorTotals.set(p.level, (plateFloorTotals.get(p.level) || 0) + p.area);
  assert(name + ': office plates ≥ 300 (per floor)', [...plateFloorTotals.values()].every(v => v >= 300),
    JSON.stringify([...plateFloorTotals.values()]));
  // 8. every serialized line validates
  const v = allValid(e);
  assert(name + ': every serialized line valid', v.ok, v.ok ? '' : v.line + ' :: ' + v.err);
  // 9. fidelity ≤ ±5%
  assert(name + ': |total − 12000| ≤ 5%', Math.abs(dev) <= 0.05, 'dev=' + (100 * dev).toFixed(2) + '%');
  // 10. adaptive core count (rule B)
  const hasCoreB = e.some(x => x.type === 'fire stair & passenger elevator core b');
  const expect3 = (GFA / above) >= 1400;
  assert(name + ': core b iff plate ≥ 1400 (' + (expect3 ? 3 : 2) + ' cores)', hasCoreB === expect3, 'hasCoreB=' + hasCoreB);
  // 11. zero-activities: no SHORT, no band toilets, anchors intact
  if (keys.length === 0) {
    assert(name + ': no SHORT lines', !e.some(x => G.isShort(x.type)), '');
    assert(name + ': toilets only on ground', e.filter(x => x.type === 'toilets').every(x => x.level === 0)
      && e.filter(x => x.type === 'toilets').length === 1, '');
    const l0 = e.filter(x => x.level === 0 && !G.isCore(x.type) && !G.isCorridor(x.type)).map(x => x.type).sort();
    assert(name + ': ground anchors intact', JSON.stringify(l0) === JSON.stringify(['lobby', 'sales and display', 'toilets']), JSON.stringify(l0));
  }
}
console.log('\nwithin ±2%: ' + twoPct.length + '/' + MATRIX2.length + ' → ' + twoPct.join(', '));
console.log('within ±5%: ' + fivePct.length + '/' + MATRIX2.length);
console.log(`\n==== GRAND TOTAL: ${pass} passed, ${fail} failed ====`);
process.exit(fail ? 1 : 0);
