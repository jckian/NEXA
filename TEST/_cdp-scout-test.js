// Live acceptance test of site-scout.html at 130 W College St, over CDP.
const { spawn } = require('child_process');
const fs = require('fs');
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const SP = 'C:\\Users\\stu40\\AppData\\Local\\Temp\\claude\\C--SCI-Arc-SP26-RESEARCH-programAgent\\a231a163-4b42-4a75-a014-2e7bfe7c6f6b\\scratchpad';
const PROF = process.env.TEMP + '\\cdp-scout-' + Date.now();
const PORT = 9336;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-sandbox', '--enable-unsafe-swiftshader',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROF}`, '--window-size=1700,1000', 'about:blank'], { stdio: 'ignore' });
let id = 0, ws; const pending = new Map();
const send = (m, p = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method: m, params: p })); });
const evalJs = async e => { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error('JS: ' + (r.exceptionDetails.exception && r.exceptionDetails.exception.description || '').slice(0, 300));
  return r.result.value; };
const shot = async n => { const r = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${SP}\\shot-${n}.png`, Buffer.from(r.data, 'base64')); console.log('shot', n); };
const fails = [];
const check = (name, cond, detail) => { console.log((cond ? 'PASS  ' : 'FAIL  ') + name + (detail !== undefined ? '   [' + String(detail).slice(0, 120) + ']' : '')); if (!cond) fails.push(name); };

(async () => {
  let list;
  for (let i = 0; i < 40; i++) { try { list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); if (list.find(t => t.type === 'page')) break; } catch (e) {} await sleep(250); }
  ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); } });
  await send('Page.enable'); await send('Runtime.enable');

  await send('Page.navigate', { url: 'http://localhost:8099/NEXA/intel/site-scout.html?addr=' + encodeURIComponent('130 W College St, Los Angeles, CA 90012') });
  // wait until all three panels have resolved (or 40 s)
  for (let i = 0; i < 40; i++) {
    await sleep(1000);
    const done = await evalJs(`(() => {
      const s = window.__scout && window.__scout.state();
      return !!(s && s.geocode && (s.zoning || document.querySelector('#p-reg .unavail')) && (s.osm || document.querySelector('#p-sur .unavail')));
    })()`);
    if (done) break;
  }
  await sleep(1500);

  const st = await evalJs('window.__scout.state()');
  check('geocoded', !!st.geocode, st.geocode && st.geocode.label);
  check('geocode near Chinatown', st.geocode && Math.abs(st.geocode.lat - 34.063) < 0.005, st.geocode && st.geocode.lat);
  check('parcel selected', !!st.parcel, st.parcel && (st.parcel.apn + ' ' + st.parcel.situs));
  check('zoning fetched', !!st.zoning, st.zoning && st.zoning.code);
  check('zoning is DTLA-2040 format', !!(st.zoning && /DM2|CX2/.test(st.zoning.code)), st.zoning && st.zoning.code);
  check('adaptive-reuse overlay hit', st.overlays['Adaptive Reuse Area'] != null, st.overlays['Adaptive Reuse Area']);
  check('osm metrics', !!st.osm, st.osm && JSON.stringify({ rail: st.osm.nearestRail, bus400: st.osm.bus400 }));
  check('nearest rail = Chinatown', !!(st.osm && st.osm.nearestRail && /Chinatown/.test(st.osm.nearestRail.name)), st.osm && st.osm.nearestRail && st.osm.nearestRail.name);
  check('export enabled', await evalJs(`!document.getElementById('btn-export').disabled`));

  // snapshot structure sanity
  const snap = await evalJs('window.__scout.buildSnapshot()');
  check('snapshot key slug', /130-w-college/.test(snap.key), snap.key);
  check('snapshot is valid JS', (() => { try { const w = {}; new Function('window', snap.text)(w); return !!w.NEXA_INTEL.sites[snap.key].dossier.regulation.zoning.value; } catch (e) { return false; } })());
  const zfact = (() => { const w = {}; new Function('window', snap.text)(w); return w.NEXA_INTEL.sites[snap.key].dossier.regulation.zoning; })();
  check('zoning fact reported-tier + sourced', zfact.confidence === 'reported' && !!zfact.source && !!zfact.accessed, JSON.stringify(zfact).slice(0, 120));
  check('timeline empty (pending N1)', (() => { const w = {}; new Function('window', snap.text)(w); const t = w.NEXA_INTEL.sites[snap.key].timeline; return t.nodes.length === 0 && t.edges.length === 0; })());

  await shot('scout-130college');

  console.log(fails.length ? '\n=== FAILURES: ' + fails.join(' | ') : '\n=== ALL SCOUT CHECKS PASS ===');
  ws.close(); edge.kill();
  try { fs.rmSync(PROF, { recursive: true, force: true }); } catch (e) {}
  process.exit(fails.length ? 1 : 0);
})().catch(e => { console.error('ERROR', e.message); edge.kill(); process.exit(2); });
