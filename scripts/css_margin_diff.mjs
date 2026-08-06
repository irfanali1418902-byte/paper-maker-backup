/* Compares two margin_probe.mjs runs and NAMES every element whose box moved.
 *
 * The gap this closes: the earlier before/after diff reported "padding-top/right/bottom/
 * left each changed on 12 element-instances" and never said which elements. A count is
 * not an answer when the question is whether the PRINTED MARGIN moved.
 *
 *   node margin_diff.mjs <before.json> <after.json>
 */

import { readFileSync } from 'node:fs';

const before = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const after = JSON.parse(readFileSync(process.argv[3], 'utf8'));

const BOX = [
  'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
];

const MARGIN_CHAIN = ['html', 'body', '.print-main', '.sheet'];

for (const paperId of Object.keys(before.papers)) {
  const b = before.papers[paperId];
  const a = after.papers[paperId];
  console.log(`\n${'='.repeat(78)}\nPAPER ${paperId}\n${'='.repeat(78)}`);

  if (!a) { console.log('  MISSING in after run'); continue; }
  if (b.errors?.length || a.errors?.length) {
    console.log(`  errors  before=${JSON.stringify(b.errors)}  after=${JSON.stringify(a.errors)}`);
  }

  const bs = b.snapshot, as = a.snapshot;
  if (!bs || !as) { console.log('  no snapshot'); continue; }

  console.log(`  media       ${bs.media} -> ${as.media}      fonts ${bs.fonts} -> ${as.fonts}`);
  console.log(`  elements    ${bs.elements} -> ${as.elements}   (expect -1: the removed <link> is itself an element)`);
  console.log(`  questions   ${bs.questions} -> ${as.questions}`);
  console.log(`  drift       before=${b.driftCount}  after=${a.driftCount}   (must be 0 before any delta is believed)`);
  console.log(`  PDF pages   ${b.pdf?.count} -> ${a.pdf?.count}   (/Type/Page objs ${b.pdf?.typePageObjects} -> ${a.pdf?.typePageObjects}, bytes ${b.pdf?.bytes} -> ${a.pdf?.bytes})`);

  // ------------------------------------------------ THE MARGIN CHAIN, by name
  console.log(`\n  --- THE MARGIN CHAIN (print.css:1-2 — @page margin 0, .sheet padding IS the page margin) ---`);
  for (const sel of MARGIN_CHAIN) {
    const cb = bs.chain?.[sel], ca = as.chain?.[sel];
    if (!cb && !ca) { console.log(`  ${sel.padEnd(13)} absent in both`); continue; }
    if (!cb || !ca) { console.log(`  ${sel.padEnd(13)} PRESENT IN ONLY ONE SNAPSHOT`); continue; }
    const same = (x, y) => JSON.stringify(x) === JSON.stringify(y);
    const flag = (same(cb.padding, ca.padding) && same(cb.margin, ca.margin) && same(cb.border, ca.border)) ? 'UNCHANGED' : '*** MOVED ***';
    console.log(`  ${sel.padEnd(13)} ${flag}   ${ca.desc}`);
    console.log(`      padding  ${cb.padding.join(' ')}   ->   ${ca.padding.join(' ')}`);
    console.log(`      margin   ${cb.margin.join(' ')}   ->   ${ca.margin.join(' ')}`);
    console.log(`      border   ${cb.border.join(' ')}   ->   ${ca.border.join(' ')}`);
    console.log(`      rect     x${cb.rect.x} y${cb.rect.y} ${cb.rect.w}x${cb.rect.h}   ->   x${ca.rect.x} y${ca.rect.y} ${ca.rect.w}x${ca.rect.h}`);
    console.log(`      box-sizing ${cb.boxSizing} -> ${ca.boxSizing}   max-width ${cb.maxWidth} -> ${ca.maxWidth}   overflow ${cb.overflow} -> ${ca.overflow}`);
  }

  // --------------------------------------------------------------- the knobs
  console.log(`\n  --- THE THREE PRINT KNOBS (setVar writes these inline; inline outranks every layer) ---`);
  for (const k of ['pageMarginRoot', 'qFontRoot', 'qGapRoot', 'pageMarginAtSheet']) {
    const same = bs.knobs?.[k] === as.knobs?.[k];
    console.log(`  ${k.padEnd(18)} ${bs.knobs?.[k]} -> ${as.knobs?.[k]}   ${same ? 'ok' : '*** CHANGED ***'}`);
  }
  console.log(`  root inline style  before: ${JSON.stringify(bs.knobs?.rootInline)}`);
  console.log(`                     after : ${JSON.stringify(as.knobs?.rootInline)}`);

  // ------------------------------------------------------------- @page rules
  console.log(`\n  --- @page RULES AS THE ENGINE SEES THEM (does the layer import change them?) ---`);
  const fmt = (rs) => (rs?.length ? rs.map((r) => `      [layer=${r.inLayer ?? 'none'}] ${r.origin}\n        ${r.text}`).join('\n') : '      (none reported)');
  console.log(`  before:\n${fmt(bs.pageRules)}`);
  console.log(`  after:\n${fmt(as.pageRules)}`);

  // -------------------------------------------- EVERY box delta, named
  const paths = new Set([...Object.keys(bs.all), ...Object.keys(as.all)]);
  const onlyBefore = [], onlyAfter = [];
  const deltas = new Map(); // prop -> [{path, desc, from, to}]
  for (const p of paths) {
    const eb = bs.all[p], ea = as.all[p];
    if (!eb) { onlyAfter.push(`${p}  ${ea['@']}`); continue; }
    if (!ea) { onlyBefore.push(`${p}  ${eb['@']}`); continue; }
    for (const prop of BOX) {
      if (eb[prop] !== ea[prop]) {
        if (!deltas.has(prop)) deltas.set(prop, []);
        deltas.get(prop).push({ path: p, desc: ea['@'], from: eb[prop], to: ea[prop] });
      }
    }
  }

  console.log(`\n  --- ALIGNMENT ---`);
  console.log(`  aligned paths ${paths.size - onlyBefore.length - onlyAfter.length}   only-before ${onlyBefore.length}   only-after ${onlyAfter.length}`);
  for (const x of onlyBefore.slice(0, 10)) console.log(`      only-before: ${x}`);
  for (const x of onlyAfter.slice(0, 10)) console.log(`      only-after : ${x}`);

  console.log(`\n  --- EVERY BOX DELTA, BY ELEMENT (this is what was never identified) ---`);
  if (!deltas.size) console.log('  none — no padding, margin or border-width moved anywhere on this page');
  let total = 0;
  for (const prop of BOX) {
    const list = deltas.get(prop);
    if (!list) continue;
    total += list.length;
    console.log(`\n  ${prop}  —  ${list.length} element-instance(s)`);
    // Group identical from->to so 12 buttons read as one fact, not twelve lines.
    const groups = new Map();
    for (const d of list) {
      const key = `${d.from} -> ${d.to}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(d);
    }
    for (const [key, ds] of groups) {
      console.log(`      ${key}   ×${ds.length}`);
      for (const d of ds.slice(0, 12)) console.log(`          ${d.desc}`);
      if (ds.length > 12) console.log(`          … and ${ds.length - 12} more`);
    }
  }
  console.log(`\n  TOTAL box deltas: ${total}`);

  // The decisive line.
  const chainMoved = MARGIN_CHAIN.filter((sel) => {
    const cb = bs.chain?.[sel], ca = as.chain?.[sel];
    if (!cb || !ca) return false;
    return JSON.stringify([cb.padding, cb.margin, cb.border]) !== JSON.stringify([ca.padding, ca.margin, ca.border]);
  });
  const chainPaths = new Set(MARGIN_CHAIN.map((s) => bs.chain?.[s]?.path).filter(Boolean));
  const deltasOnChain = [];
  for (const [prop, list] of deltas) for (const d of list) if (chainPaths.has(d.path)) deltasOnChain.push(`${d.desc} ${prop} ${d.from} -> ${d.to}`);

  console.log(`\n  ${'#'.repeat(74)}`);
  console.log(`  VERDICT for ${paperId}`);
  console.log(`    margin-chain elements whose box moved : ${chainMoved.length ? chainMoved.join(', ') : 'NONE'}`);
  console.log(`    box deltas landing on the chain       : ${deltasOnChain.length ? deltasOnChain.join('; ') : 'NONE'}`);
  console.log(`    .sheet padding                        : ${bs.chain?.['.sheet']?.padding.join(' ')}  ->  ${as.chain?.['.sheet']?.padding.join(' ')}`);
  console.log(`    PDF pages                             : ${b.pdf?.count} -> ${a.pdf?.count}`);
  console.log(`  ${'#'.repeat(74)}`);
}
