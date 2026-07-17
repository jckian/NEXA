'use strict';
const G = require('./genlib.js');
G.loadGenerator('C:/SCI-Arc/SP26-RESEARCH/programAgent/program-input.html');
const cases = {
  all:       G.ACTIVITY_GROUPS.flatMap(([,k])=>k),
  showevent: ['exhibition','event hall','showroom','pop-up'],
  learning:  ['classroom','seminar','computer lab','project review'],
  wellness:  ['yoga','pilates','fitness','meditation','recovery lounge'],
  social:    ['coffee','lounge bar'],
};
// intended raw presets per type (generator's own add() values = SAMPLE-calibrated)
for (const [name, keys] of Object.entries(cases)) {
  const e = G.generateEntries('mixed-use', 12000, 8, 2, keys);
  const total = e.reduce((s,x)=>s+x.area,0);
  // reconstruct raw total: rerun with gfa=0 → scale=1? generator scales only if gfaTarget>0.
  const raw = G.generateEntries('mixed-use', 0, 8, 2, keys);
  const rawTotal = raw.reduce((s,x)=>s+x.area,0);
  const scale = total/rawTotal;
  // per-type min/max scaled area
  const byType = new Map();
  for (const x of e) {
    const b = byType.get(x.type) || {min:1e9,max:0,n:0,tot:0};
    b.min=Math.min(b.min,x.area); b.max=Math.max(b.max,x.area); b.n++; b.tot+=x.area;
    byType.set(x.type,b);
  }
  console.log(`\n=== ${name} · scaled total ${total} m² (target 12000, ${(100*(total-12000)/12000).toFixed(1)}%) · scale ×${scale.toFixed(3)} ===`);
  for (const [t,b] of [...byType.entries()].sort((a,c)=>a[0].localeCompare(c[0]))) {
    const tag = G.isShort(t)?'S':(G.isCore(t)?'C':(t.includes('circulation')?'c':'L'));
    console.log(`${tag}  ${t.padEnd(42)} n=${String(b.n).padStart(2)}  ${b.min===b.max?b.min+' m²':b.min+'-'+b.max+' m²'}`);
  }
}
