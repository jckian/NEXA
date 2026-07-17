// Mechanical validation of ALL NEXA/intel/data files (program-auditor pattern: numbers only)
const fs = require('fs');
const path = 'C:/SCI-Arc/SP26-RESEARCH/programAgent/NEXA/intel/data/';
global.window = {};
for (const f of ['site-citymarket.js', 'scenarios-citymarket.js', 'site-collegest.js', 'scenarios-collegest.js', 'transitions.js']) {
  eval(fs.readFileSync(path + f, 'utf8'));
  console.log('LOADED', f);
}
const fails = [];
const KINDS = ['program', 'building', 'regulation', 'transit', 'economy', 'society', 'climate'];
const CAT = ['public', 'private', 'circulation'];

for (const [key, site] of Object.entries(window.NEXA_INTEL.sites)) {
  console.log('\n=== SITE', key, '===');
  const nodes = site.timeline.nodes, edges = site.timeline.edges;
  const ids = new Set(nodes.map(n => n.id));
  if (ids.size !== nodes.length) fails.push(`${key}: duplicate node ids`);
  edges.forEach((e, i) => { if (!ids.has(e.from) || !ids.has(e.to)) fails.push(`${key} edge ${i}: dangling ${e.from}->${e.to}`); });
  nodes.forEach(n => {
    if (!KINDS.includes(n.kind)) fails.push(`${key} node ${n.id}: bad kind ${n.kind}`);
    if (!n.facts || !n.facts.length || n.facts.some(f => !f.source)) fails.push(`${key} node ${n.id}: unsourced`);
  });
  edges.filter(e => e.relation === 'succeeded_by').forEach(e => {
    const a = nodes.find(n => n.id === e.from), b = nodes.find(n => n.id === e.to);
    if (a.tEnd != null && b.tStart != null && a.tEnd > b.tStart + 5) fails.push(`${key} succession ${e.from}->${e.to}: tEnd ${a.tEnd} > tStart+5 ${b.tStart}`);
  });
  const spine = nodes.filter(n => n.kind === 'program' && n.epoch !== 'future');
  console.log(`timeline: ${nodes.length} nodes, ${edges.length} edges, ${spine.length} non-future program nodes`);

  (site.scenarios || []).forEach(sc => {
    const mixSum = sc.programMix.reduce((s, m) => s + m.share, 0);
    if (Math.abs(mixSum - 1) > 0.001) fails.push(`${key} scenario ${sc.id}: mix sums ${mixSum.toFixed(3)}`);
    if (!sc.generation || !sc.generation.promptFile) fails.push(`${key} scenario ${sc.id}: no generation record`);
    (sc.drivers || []).forEach(d => { if (!ids.has(d)) fails.push(`${key} scenario ${sc.id}: driver "${d}" is not a timeline node id`); });
    const perLevel = {}; let gfa = 0, lines = 0;
    sc.programFormatDraft.split('\n').forEach((raw, li) => {
      const t = raw.trim();
      if (!t || t.startsWith('#')) return;
      lines++;
      const m = t.match(/^\{([^}]+)\}\/\{(\d+(?:\.\d+)?)\}\/\{(-?\d+)\}\/\{(\w+)\}\/\{(\d+),(\d+)\}$/);
      if (!m) { fails.push(`${key} sc ${sc.id} line ${li + 1}: grammar fail: ${t.slice(0, 50)}`); return; }
      const [, type, areaS, lvS, cat, wS, hS] = m;
      const area = +areaS, lv = +lvS, w = +wS, h = +hS;
      if (!CAT.includes(cat)) fails.push(`${key} sc ${sc.id} line ${li + 1}: category ${cat}`);
      if (Math.abs(w * h - area) / area > 0.10) fails.push(`${key} sc ${sc.id} line ${li + 1}: w*h ${w * h} vs area ${area}`);
      perLevel[lv] = perLevel[lv] || { cores: 0 };
      if (/fire stair/i.test(type)) perLevel[lv].cores++;
      gfa += area;
    });
    const levels = Object.keys(perLevel).map(Number).sort((a, b) => a - b);
    for (let i = 1; i < levels.length; i++) if (levels[i] !== levels[i - 1] + 1) fails.push(`${key} sc ${sc.id}: level gap ${levels[i - 1]}->${levels[i]}`);
    levels.forEach(lv => { if (perLevel[lv].cores < 3) fails.push(`${key} sc ${sc.id} L${lv}: ${perLevel[lv].cores} fire-stair cores (<3)`); });
    console.log(`  scenario ${sc.id} (${sc.horizon}): ${lines} lines, L${levels[0]}..L${levels[levels.length - 1]}, GFA ${gfa} m2`);
  });
  if (!site.scenarios) console.log('  (no scenarios)');
}

const tr = window.NEXA_INTEL.transitions;
tr.forEach((t, i) => {
  if (!['high', 'medium', 'low'].includes(t.likelihood)) fails.push(`transition ${i}: bad tier`);
  if (!t.basis) fails.push(`transition ${i} (${t.from}): no basis`);
  if (!t.examples || !t.examples.length) fails.push(`transition ${i} (${t.from}): no example`);
});
console.log(`\ntransitions: ${tr.length} entries, ${new Set(tr.map(t => t.from)).size} distinct from-types`);
console.log(fails.length ? '\nFAIL:\n' + fails.join('\n') : '\nALL CHECKS PASS');
process.exit(fails.length ? 1 : 0);
