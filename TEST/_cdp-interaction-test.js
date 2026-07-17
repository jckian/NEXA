// Interaction test for program-input.html back-navigation, driven over CDP (no deps).
const { spawn } = require('child_process');
const fs = require('fs');
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PROF = process.env.TEMP + '\\cdp-prof-' + Date.now();
const PORT = 9333;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-sandbox', '--enable-unsafe-swiftshader',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${PROF}`, '--window-size=1600,1000', 'about:blank'],
  { stdio: 'ignore' });

let id = 0, ws;
const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => {
  const m = ++id;
  pending.set(m, { res, rej });
  ws.send(JSON.stringify({ id: m, method, params }));
});
const evalJs = async expr => {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error('JS: ' + JSON.stringify(r.exceptionDetails.exception && r.exceptionDetails.exception.description));
  return r.result.value;
};

const fails = [];
const check = (name, cond, detail) => {
  console.log((cond ? 'PASS  ' : 'FAIL  ') + name + (detail !== undefined ? '   [' + detail + ']' : ''));
  if (!cond) fails.push(name + ' :: ' + detail);
};

(async () => {
  // find the page target
  let list;
  for (let i = 0; i < 40; i++) {
    try { list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); if (list.find(t => t.type === 'page')) break; } catch (e) {}
    await sleep(250);
  }
  const target = list.find(t => t.type === 'page');
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r));
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); }
  });
  await send('Page.enable'); await send('Runtime.enable');

  const goto = async url => {
    await send('Page.navigate', { url });
    await sleep(2500);
  };
  const clearLS = () => evalJs('localStorage.clear(), 1');
  const q = sel => `document.querySelector('${sel}')`;
  const click = sel => evalJs(`${q(sel)}.click(), 1`);
  const vis = sel => evalJs(`(() => { const e = ${q(sel)}; return !!e && getComputedStyle(e).display !== 'none'; })()`);
  const txt = sel => evalJs(`(() => { const e = ${q(sel)}; return e ? e.textContent.trim() : null; })()`);

  console.log('\n--- A. wizard back navigation ---');
  await goto('http://localhost:8099/program-input.html');
  await clearLS();
  await goto('http://localhost:8099/program-input.html');
  check('step 1: back hidden', (await vis('#btn-back')) === false, 'btn-back visible=' + await vis('#btn-back'));
  check('step 1 pip', await txt('#step-num'), await txt('#step-num'));

  await click('#chips .chip'); await sleep(500);           // pick Mixed-Use → step 2 (GFA)
  check('step 2 reached', (await txt('#step-num')) === '02 / 04', await txt('#step-num'));
  check('step 2: back visible', (await vis('#btn-back')) === true);

  await evalJs(`(()=>{const i=document.getElementById('input-number'); i.value='9000'; i.dispatchEvent(new Event('input')); })()`);
  await click('#btn-number'); await sleep(500);            // → step 3 (floors)
  check('step 3 reached', (await txt('#step-num')) === '03 / 04', await txt('#step-num'));
  check('answered rows = 2', (await evalJs(`document.querySelectorAll('.answered-row').length`)) === 2);

  await click('#btn-back'); await sleep(600);              // ← back to GFA
  check('back → step 2', (await txt('#step-num')) === '02 / 04', await txt('#step-num'));
  check('GFA prefilled with previous answer', (await evalJs(`document.getElementById('input-number').value`)) === '9000',
        await evalJs(`document.getElementById('input-number').value`));
  check('answered rows now = 1', (await evalJs(`document.querySelectorAll('.answered-row').length`)) === 1,
        await evalJs(`document.querySelectorAll('.answered-row').length`));

  await click('#btn-back'); await sleep(600);              // ← back to building type
  check('back → step 1', (await txt('#step-num')) === '01 / 04', await txt('#step-num'));
  check('step 1: back hidden again', (await vis('#btn-back')) === false);
  check('answered rows now = 0', (await evalJs(`document.querySelectorAll('.answered-row').length`)) === 0);

  console.log('\n--- B. review → back → wizard (draft kept) ---');
  await click('#chips .chip'); await sleep(400);
  await evalJs(`(()=>{const i=document.getElementById('input-number'); i.value='9000'; i.dispatchEvent(new Event('input')); })()`);
  await click('#btn-number'); await sleep(400);
  await click('#btn-floors'); await sleep(400);
  await click('#btn-activities'); await sleep(700);        // → review
  check('review reached', await vis('#review'));
  const gfaShown = await txt('#ft-gfa');
  check('review shows a GFA', /m²/.test(gfaShown || ''), gfaShown);

  await click('#btn-back-review'); await sleep(700);
  check('back from review → wizard last step', (await txt('#step-num')) === '04 / 04', await txt('#step-num'));
  check('review hidden', (await vis('#review')) === false);
  check('answers preserved (3 rows)', (await evalJs(`document.querySelectorAll('.answered-row').length`)) === 3,
        await evalJs(`document.querySelectorAll('.answered-row').length`));

  console.log('\n--- C. forecast → apply → back returns to forecast ---');
  await clearLS();
  await goto('http://localhost:8099/program-input.html?forecast=1');
  check('forecast panel open', await vis('#forecast'));
  check('site tabs rendered', (await evalJs(`document.querySelectorAll('.fc-tab').length`)) === 2,
        await evalJs(`document.querySelectorAll('.fc-tab').length`));

  await click('.fc-apply'); await sleep(800);              // apply first scenario
  check('review reached from forecast', await vis('#review'));
  check('forecast panel hidden', (await vis('#forecast')) === false);
  const entriesN = await evalJs(`window.__debug.entries().length`);
  check('scenario entries loaded', entriesN > 20, entriesN);

  await click('#btn-back-review'); await sleep(700);
  check('back → FORECAST (not wizard)', await vis('#forecast'));
  check('review hidden after back', (await vis('#review')) === false);
  check('wizard NOT shown', (await vis('#dialog')) === false || (await evalJs(`document.getElementById('forecast').style.display`)) === 'block');

  await click('#fc-close'); await sleep(500);
  check('fc-close → wizard visible', await vis('#dialog'));

  console.log('\n--- D. site switch inside forecast ---');
  await goto('http://localhost:8099/program-input.html?site=130-college-st&forecast=1');
  const title = await txt('#fc-title');
  check('site=130-college-st honoured', /College/.test(title || ''), title);
  await evalJs(`document.querySelectorAll('.fc-tab')[0].click(), 1`); await sleep(400);
  check('tab switch → City Market', /City Market/.test(await txt('#fc-title')), await txt('#fc-title'));
  check('spine re-rendered', (await evalJs(`document.querySelectorAll('#fc-spine .fc-tl-node').length`)) === 2,
        await evalJs(`document.querySelectorAll('#fc-spine .fc-tl-node').length`));

  console.log(fails.length ? '\n=== FAILURES ===\n' + fails.join('\n') : '\n=== ALL INTERACTION CHECKS PASS ===');
  ws.close(); edge.kill();
  try { fs.rmSync(PROF, { recursive: true, force: true }); } catch (e) {}
  process.exit(fails.length ? 1 : 0);
})().catch(async e => {
  console.error('ERROR', e.message);
  try { ws && ws.close(); } catch (x) {}
  edge.kill();
  try { fs.rmSync(PROF, { recursive: true, force: true }); } catch (x) {}
  process.exit(2);
});
