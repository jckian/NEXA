'use strict';
// ── copied verbatim from program-input.html classifiers/validator ──
const isCore = t => /fire stair|elevator|escalator|\bstair\b|\bcore\b|shaft/i.test(t);
const isShort = t => /coffee|showroom|pop[- ]?up|exhibition|event hall|\bdemo\b|classroom|seminar|computer lab|project review|yoga|pilates|fitness|recovery lounge|physical therapy|meditation|health coaching|lounge bar/i.test(t);
const isCorridor = t => /circulation|corridor|hallway/i.test(t);
const VALID_CATEGORIES = ['public', 'private', 'circulation'];
const SHORT_THRESHOLD = 0.5;

function validateLine(raw) {
  const t = raw.trim();
  if (!t || t.startsWith('#')) return { skip: true };
  const parts = t.split('/').map(s => s.replace(/[{}]/g, '').trim());
  if (parts.length < 3) return { error: 'too few parts (need type/area/level)' };
  const type = parts[0].toLowerCase();
  const area = parseFloat(parts[1]);
  const level = parseInt(parts[2], 10);
  let category = 'private';
  if (parts[3] && !parts[3].includes(',')) category = parts[3].toLowerCase();
  else if (parts[4] && !parts[4].includes(',')) category = parts[4].toLowerCase();
  if (!type) return { error: 'missing type' };
  if (isNaN(area)) return { error: 'NaN area' };
  if (isNaN(level)) return { error: 'NaN level' };
  if (!VALID_CATEGORIES.includes(category)) return { error: 'unknown category "' + category + '"' };
  let w = 0, h = 0, hasWH = false;
  for (let i = 3; i < parts.length; i++) {
    if (parts[i] && parts[i].includes(',')) {
      const [a, b] = parts[i].split(',').map(parseFloat);
      if (!isNaN(a) && !isNaN(b)) { w = a; h = b; hasWH = true; }
      break;
    }
  }
  return { type, area, level, category, wh: hasWH ? [w, h] : null };
}

const ACTIVITY_GROUPS = [
  ['Show & event', ['exhibition', 'event hall', 'showroom', 'pop-up']],
  ['Learning',     ['classroom', 'seminar', 'computer lab', 'project review']],
  ['Wellness',     ['yoga', 'pilates', 'fitness', 'meditation', 'recovery lounge']],
  ['Social',       ['coffee', 'lounge bar']],
];
const ACTIVITY_DEFS = {
  'exhibition':      [['exhibition gallery', 268]],
  'event hall':      [['event hall', 241]],
  'showroom':        [['showroom', 214]],
  'pop-up':          [['pop-up retail', 107], ['pop-up retail', 107]],
  'classroom':       [['classroom', 107], ['classroom', 107]],
  'seminar':         [['seminar room', 107]],
  'computer lab':    [['computer lab', 107]],
  'project review':  [['project review room', 107]],
  'yoga':            [['yoga studio', 134]],
  'pilates':         [['pilates studio', 107]],
  'fitness':         [['fitness center', 242]],
  'meditation':      [['meditation room', 90]],
  'recovery lounge': [['recovery lounge', 107]],
  'coffee':          [['coffee shop', 161]],
  'lounge bar':      [['lounge bar', 134]],
};

function dims(area) {
  const w = Math.max(1, Math.round(Math.sqrt(area)));
  const h = Math.max(1, Math.round(area / w));
  return [w, h];
}

// ══ PLACEHOLDER: generateEntries injected by loadGenerator() so we always test
//    the exact source living in program-input.html (single source of truth) ══
let generateEntries = null;

// Extracts the generateEntries function body from program-input.html and builds a
// callable that closes over the helpers above (add/addCores/affinity all rely on
// ACTIVITY_GROUPS/ACTIVITY_DEFS which we provide as globals in the eval scope).
function loadGenerator(htmlPath) {
  const fs = require('fs');
  const src = fs.readFileSync(htmlPath, 'utf8');
  const start = src.indexOf('function generateEntries(');
  if (start < 0) throw new Error('generateEntries not found');
  // brace-match to find the end of the function
  let i = src.indexOf('{', start), depth = 0, end = -1;
  for (; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  const fnSrc = src.slice(start, end);
  // eslint-disable-next-line no-new-func
  const factory = new Function('ACTIVITY_GROUPS', 'ACTIVITY_DEFS', 'isCore', 'isShort', 'isCorridor',
    fnSrc + '\nreturn generateEntries;');
  generateEntries = factory(ACTIVITY_GROUPS, ACTIVITY_DEFS, isCore, isShort, isCorridor);
  return generateEntries;
}

function serialize(list) {
  const levels = [...new Set(list.map(e => e.level))].sort((a, b) => a - b);
  let out = '';
  for (const lv of levels) {
    out += `# Level ${lv}\n`;
    for (const e of list.filter(x => x.level === lv)) {
      const [w, h] = e.wh || dims(e.area);
      out += `{${e.type}}/{${e.area}}/{${e.level}}/{${e.category}}/{${w},${h}}\n`;
    }
  }
  return out;
}

// exact replica of program-massing-shortfloor.html computeShortFloors rule as
// applied to entries (non-core, non-corridor packed area; shrt/tot > 0.5).
function shortLevels(entries) {
  const m = new Map();
  for (const e of entries) {
    if (isCore(e.type) || isCorridor(e.type)) continue;
    if (!m.has(e.level)) m.set(e.level, { tot: 0, shrt: 0 });
    const pf = m.get(e.level); pf.tot += e.area;
    if (isShort(e.type)) pf.shrt += e.area;
  }
  return m;
}
function computeShortFloors(entries) {
  return [...shortLevels(entries).entries()]
    .filter(([lv, pf]) => pf.tot > 0 && pf.shrt / pf.tot > SHORT_THRESHOLD)
    .map(([lv]) => lv).sort((a, b) => a - b);
}
function totalArea(entries) { return entries.reduce((s, e) => s + e.area, 0); }

module.exports = {
  isCore, isShort, isCorridor, VALID_CATEGORIES, SHORT_THRESHOLD,
  validateLine, ACTIVITY_GROUPS, ACTIVITY_DEFS, dims, loadGenerator,
  get generateEntries() { return generateEntries; },
  serialize, shortLevels, computeShortFloors, totalArea,
};
