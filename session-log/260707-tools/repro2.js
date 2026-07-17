'use strict';
const fs = require('fs');
const G = require('./genlib.js');
G.loadGenerator('C:/SCI-Arc/SP26-RESEARCH/programAgent/program-input.html');
const cases = {
  all:       G.ACTIVITY_GROUPS.flatMap(([,k])=>k),
  showevent: ['exhibition','event hall','showroom','pop-up'],
  learning:  ['classroom','seminar','computer lab','project review'],
  social:    ['coffee','lounge bar'],
};
const texts = {};
for (const [name, keys] of Object.entries(cases)) {
  const e = G.generateEntries('mixed-use', 12000, 8, 2, keys);
  texts[name] = G.serialize(e);
  // per-level short share (packed only), mirroring computeShortFloors
  const tot = new Map(), shrt = new Map();
  for (const x of e) {
    if (G.isCore(x.type) || G.isCorridor(x.type)) continue;
    tot.set(x.level, (tot.get(x.level)||0) + x.area);
    if (G.isShort(x.type)) shrt.set(x.level, (shrt.get(x.level)||0) + x.area);
  }
  const bands = [...tot.keys()].filter(l => l >= 0 && (shrt.get(l)||0) > 0).sort((a,b)=>a-b)
    .map(l => `${l}:${((shrt.get(l)||0)/tot.get(l)).toFixed(3)}`);
  console.log(name.padEnd(10), 'SHORT levels(share):', bands.join('  '));
}
const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>handoff-test</title></head><body>
<script>
const CASES=${JSON.stringify(texts)};
const q=new URLSearchParams(location.search);
const c=q.get('case')||'all';
localStorage.setItem('programInputText', CASES[c]||CASES.all);
q.delete('case'); q.set('src','input');
location.replace('program-massing-shortfloor.html?'+q.toString());
</script>
</body></html>`;
fs.writeFileSync('C:/SCI-Arc/SP26-RESEARCH/programAgent/_handoff-test.html', html);
console.log('wrote _handoff-test.html');
