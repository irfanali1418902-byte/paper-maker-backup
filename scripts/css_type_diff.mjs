/**
 * css_type_diff.mjs — diffs two css_type_probe.mjs runs.
 *
 * WHY THIS EXISTS AS A REPO FILE. Every migration has to answer the same
 * question — "did anything move on the three live pages?" — and until now the
 * comparison was done ad hoc in whatever session was running. css_margin_diff
 * .mjs already exists for exactly this reason on the print side. PROBES.md
 * records that this epic lost a whole set of measurement scripts once by
 * leaving them in a session scratchpad; this is the type-probe half, written
 * into scripts/ the first time it was needed rather than the second.
 *
 * WHAT IT COMPARES. pages[page].snapshot.all is a map of element path ->
 * { property: computed value }. This walks every path present in either run
 * and reports, per page:
 *
 *   deltas      element x property pairs whose value changed
 *   beforeOnly  paths in the BEFORE run and not the AFTER run
 *   afterOnly   paths in the AFTER run and not the BEFORE run
 *
 * A path appearing on one side only is NOT counted as a delta — it is counted
 * separately, because the usual cause is benign (the removed <link> is itself
 * an element, so element counts fall by exactly 1 on a migration) and folding
 * it into the delta count hides that. STATUS.md records the -1 for taqseem,
 * bank and index.
 *
 * READING THE RESULT. For a LIVE page the only acceptable answer is 0 deltas,
 * 0 beforeOnly, 0 afterOnly. For the page being migrated, deltas are expected
 * and the point is to name them, which --names does.
 *
 * Drift is checked first and separately: if either run has driftCount > 0 on a
 * page, that page's render was not deterministic and no delta from it should
 * be believed. UI-031b's rule.
 *
 * Usage:
 *   node scripts/css_type_diff.mjs <before.json> <after.json> [--names] [--page <p>]
 *   --names   list every changed property (capped, see LIST_CAP)
 *   --page    restrict output to one page
 */

import { readFileSync } from 'node:fs';

const LIST_CAP = 60;

const args = process.argv.slice(2);
const files = args.filter((a) => !a.startsWith('--'));
const wantNames = args.includes('--names');
const pageIdx = args.indexOf('--page');
const onlyPage = pageIdx === -1 ? null : args[pageIdx + 1];

if (files.length < 2) {
  console.error('usage: node scripts/css_type_diff.mjs <before.json> <after.json> [--names] [--page <p>]');
  process.exit(2);
}

const before = JSON.parse(readFileSync(files[0], 'utf8'));
const after = JSON.parse(readFileSync(files[1], 'utf8'));

console.log(`before: ${before.label}  ${files[0]}`);
console.log(`after : ${after.label}  ${files[1]}`);
console.log(`browser: ${before.browser}${before.browser === after.browser ? '' : ` -> ${after.browser}`}`);

/* VIEWPORT LISTS ARE COMPARED, LOUDLY — UI-064.
 *
 * Both probes now write `viewports`, and the reference width's keys are UNSUFFIXED while
 * every other band carries `@<width>`. That asymmetry is convenient and it is a trap:
 * diff a `--viewports 1280` run against the 5-band default and the four extra bands land
 * in `afterOnly`, which this file's own reading rule ("the only acceptable answer is 0
 * deltas, 0 beforeOnly, 0 afterOnly") reports as a failure that is not one. Change WHICH
 * width is the reference and it is worse: every bare key silently changes meaning and the
 * whole page reads as beforeOnly + afterOnly with no stated cause.
 *
 * Neither case is detectable from the numbers, so it is stated before them. Old snapshots
 * that predate this field print nothing extra. */
const vpList = (d) => (d.viewports ?? (d.viewport ? [d.viewport] : [])).map((v) => v.width).join(',');
const vpB = vpList(before);
const vpA = vpList(after);
if (vpB || vpA) {
  console.log(`viewports: ${vpB || '?'}${vpB === vpA ? '' : ` -> ${vpA || '?'}`}`);
  if (vpB !== vpA) {
    console.log('⚠ THE TWO RUNS DID NOT MEASURE THE SAME WIDTHS. beforeOnly/afterOnly keys');
    console.log('  below are expected and are NOT a regression; the reference viewport is the');
    console.log('  unsuffixed one, so if it differs the bare keys are not comparable at all.');
  }
}
console.log('');

const pages = [...new Set([...Object.keys(before.pages), ...Object.keys(after.pages)])]
  .filter((p) => !onlyPage || p === onlyPage);

const rows = [];
let grandDeltas = 0;
let anyDrift = false;
let anyMissing = false;

for (const page of pages) {
  const b = before.pages[page];
  const a = after.pages[page];
  if (!b || !a) {
    rows.push({ page, role: (a || b).role, note: b ? 'AFTER missing' : 'BEFORE missing' });
    anyMissing = true;
    continue;
  }

  const drift = (b.driftCount || 0) + (a.driftCount || 0);
  if (drift > 0) anyDrift = true;

  const bAll = b.snapshot.all || {};
  const aAll = a.snapshot.all || {};
  const bKeys = new Set(Object.keys(bAll));
  const aKeys = new Set(Object.keys(aAll));

  const beforeOnly = [...bKeys].filter((k) => !aKeys.has(k));
  const afterOnly = [...aKeys].filter((k) => !bKeys.has(k));

  let deltas = 0;
  let props = 0;
  const changed = [];
  for (const k of bKeys) {
    if (!aKeys.has(k)) continue;
    const bv = bAll[k];
    const av = aAll[k];
    const names = new Set([...Object.keys(bv), ...Object.keys(av)]);
    for (const p of names) {
      if (p === '@') continue;
      props++;
      if (bv[p] !== av[p]) {
        deltas++;
        if (changed.length < LIST_CAP) changed.push({ path: k, tag: bv['@'], prop: p, from: bv[p], to: av[p] });
      }
    }
  }
  grandDeltas += deltas;

  rows.push({
    page,
    role: b.role,
    elemsBefore: b.snapshot.elements,
    elemsAfter: a.snapshot.elements,
    props,
    deltas,
    beforeOnly: beforeOnly.length,
    afterOnly: afterOnly.length,
    drift,
    changed,
  });
}

const pad = (s, n) => String(s).padEnd(n);
const lpad = (s, n) => String(s).padStart(n);

console.log(`${pad('page', 12)} ${lpad('elems', 13)} ${lpad('props', 8)} ${lpad('deltas', 8)} ${lpad('b-only', 7)} ${lpad('a-only', 7)} ${lpad('drift', 6)}`);
console.log(`${'-'.repeat(12)} ${'-'.repeat(13)} ${'-'.repeat(8)} ${'-'.repeat(8)} ${'-'.repeat(7)} ${'-'.repeat(7)} ${'-'.repeat(6)}`);
for (const r of rows) {
  if (r.note) { console.log(`${pad(r.page, 12)}  ${r.note}`); continue; }
  const elems = r.elemsBefore === r.elemsAfter ? `${r.elemsBefore}` : `${r.elemsBefore} -> ${r.elemsAfter}`;
  console.log(`${pad(r.page, 12)} ${lpad(elems, 13)} ${lpad(r.props, 8)} ${lpad(r.deltas, 8)} ${lpad(r.beforeOnly, 7)} ${lpad(r.afterOnly, 7)} ${lpad(r.drift, 6)}`);
}

if (wantNames) {
  for (const r of rows) {
    if (!r.changed || r.changed.length === 0) continue;
    console.log('');
    console.log(`--- ${r.page}: ${r.deltas} delta(s)${r.deltas > LIST_CAP ? `, first ${LIST_CAP}` : ''}`);
    for (const c of r.changed) {
      console.log(`  ${c.path} <${c.tag}>  ${c.prop}: ${c.from}  ->  ${c.to}`);
    }
  }
}

console.log('');
if (anyDrift) console.log('DRIFT > 0 on at least one page — that page was not deterministic; do not believe its deltas.');
if (anyMissing) console.log('A page is present in only one run — the page lists differ between the two probes.');
console.log(`total element x property deltas: ${grandDeltas}`);
