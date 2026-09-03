/* css_breakpoints.mjs — WHICH WIDTHS DOES THIS TREE ACTUALLY BEHAVE DIFFERENTLY AT,
 * and does a given viewport list observe all of them?
 *
 *   node scripts/css_breakpoints.mjs                 # report the bands and who covers them
 *   node scripts/css_breakpoints.mjs 1280 700        # check a specific viewport list
 *
 * WHY THIS EXISTS — UI-064 (the viewport pass), and it is D45's shape a third time.
 * D45 was "a gate that reads the page at rest cannot see a state". This is "a gate that
 * reads the page at ONE WIDTH cannot see a breakpoint": every probe in this repo ran at
 * 1280x900, so all fifteen screen `@media` blocks in static/css/ were measured only in
 * the band where most of them do not apply. A rule inside `@media (max-width: 720px)`
 * could be deleted, recoloured or inverted and every probe would return 0 deltas.
 *
 * The lesson from D45 and D49 is that the tool must be able to say what it cannot see,
 * rather than leave that to whoever remembers. So this module is not decoration: both
 * probes call it and PRINT THE UNCOVERED BANDS in their own summary. A band with no
 * viewport is reported every run, not filed away in a document.
 *
 * WHAT A BAND IS. Breakpoints partition the width axis into ranges within which the set
 * of matching `@media` rules never changes. Two widths in the same band cannot disagree
 * about which rules apply, so measuring both is waste; two widths in different bands can,
 * so measuring only one is a hole. `(max-width: 760px)` splits at 760/761, and
 * `(min-width: 761px)` splits at the same place — which is why the band list is computed
 * from the edges rather than from the count of queries.
 *
 * SCREEN ONLY. `@media print` blocks are deliberately ignored: css_print_probe.mjs and
 * css_margin_probe.mjs own print media and measure it in the media it prints in. A print
 * block has no width band to sit in here.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const CSS_ROOT = 'static/css';

function cssFiles(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...cssFiles(p));
    else if (name.endsWith('.css')) out.push(p);
  }
  return out;
}

/* Returns [{ file, line, raw, kind: 'max'|'min', px }] for every SCREEN width query.
 *
 * The `(?![^{]*\bprint\b)` guard is not used — `print` is matched and dropped explicitly
 * instead, because a comment mentioning print inside the condition would fool a lookahead
 * and this file's whole point is not to quietly miss things. */
/* Width-ish conditions this parser did NOT understand, refilled on every readBreakpoints
   call. Empty in this tree today; a probe prints it so it cannot be empty and unnoticed. */
export const unreadable = [];

export function readBreakpoints(root = CSS_ROOT) {
  const found = [];
  unreadable.length = 0;
  for (const file of cssFiles(root)) {
    /* Comments are blanked, not deleted, so line numbers survive. This tree documents
       its own media rules IN PROSE — `shell.css`:58, `pages/index.css`:207 and
       `pages/blueprint.css`:50 all quote
       `@media (max-width: 760px)` inside a comment — and the first version of this file
       counted them as live queries. A checker that over-reports is as useless as one that
       under-reports: it would have demanded a viewport for a band that has no rules. */
    const src = readFileSync(file, 'utf8').replace(
      /\/\*[\s\S]*?\*\//g,
      (c) => c.replace(/[^\n]/g, ' '),
    );
    const re = /@media([^{]*)\{/g;
    let m;
    while ((m = re.exec(src)) !== null) {
      const cond = m[1];
      /* A condition mentioning print is dropped WHOLE. So `@media (max-width:760px), print`
         or `@media not print and (max-width:760px)` would lose a live SCREEN query.
         Neither spelling exists in this tree (checked 2026-08-26); recorded because review
         asked for the residual case, not because it bites today. */
      if (/\bprint\b/.test(cond)) continue;
      const line = src.slice(0, m.index).split('\n').length;
      let matched = 0;
      for (const q of cond.matchAll(/\((max|min)-width:\s*(\d+)px\)/g)) {
        found.push({ file, line, raw: cond.trim(), kind: q[1], px: Number(q[2]) });
        matched++;
      }
      /* THE PARSER SAYS WHAT IT COULD NOT READ. Only integer-px max/min-width is
         understood: em/rem widths, fractional px, media-range syntax
         (400px <= width <= 700px), @container, orientation and resolution all fall
         through. None exist in this tree today (grepped 2026-08-26), so the band list is
         complete — but the whole thesis of this file is that a tool must announce its
         blind spots, and the first version announced nothing. A width-ish condition this
         regex did not consume is recorded and printed rather than silently dropped.
         Without it, adding one (max-width: 47.5em) makes every probe report "every band
         observed" while being blind to it. */
      if (matched === 0 && /width|orientation|resolution|container/i.test(cond)) {
        unreadable.push({ file, line, raw: cond.trim() });
      }
    }
  }
  return found;
}

/* The edges at which the matching set changes, ascending.
 *
 * `(max-width: N)` stops applying above N, so N and N+1 are in different bands.
 * `(min-width: N)` starts applying at N, so N-1 and N differ. Both become a boundary
 * BELOW which one band ends: max-N -> boundary at N+1, min-N -> boundary at N. */
export function bandEdges(breakpoints) {
  const edges = new Set();
  for (const b of breakpoints) edges.add(b.kind === 'max' ? b.px + 1 : b.px);
  return [...edges].sort((x, y) => x - y);
}

/* Bands as [lo, hi] inclusive, hi = Infinity for the top one. */
export function bands(breakpoints) {
  const edges = bandEdges(breakpoints);
  const out = [];
  let lo = 1;
  for (const e of edges) { out.push([lo, e - 1]); lo = e; }
  out.push([lo, Infinity]);
  return out;
}

/* Which bands does this viewport list observe, and which does it miss? */
export function coverage(widths, breakpoints = readBreakpoints()) {
  const bs = bands(breakpoints);
  const rows = bs.map(([lo, hi]) => ({
    lo, hi,
    widths: widths.filter((w) => w >= lo && w <= hi),
    rules: breakpoints.filter((b) => (b.kind === 'max' ? lo <= b.px : hi >= b.px)),
  }));
  return { rows, uncovered: rows.filter((r) => r.widths.length === 0) };
}

const fmt = (lo, hi) => (hi === Infinity ? `${lo}+` : lo === hi ? `${lo}` : `${lo}-${hi}`);

/* One line per uncovered band, for a probe to print in its own summary. Empty array
 * when the viewport list is complete — a caller can just spread it. */
export function uncoveredLines(widths, breakpoints = readBreakpoints()) {
  const { uncovered } = coverage(widths, breakpoints);
  const lines = uncovered.map((r) => {
    const where = [...new Set(r.rules.map((b) => `${b.file}:${b.line}`))];
    return `  UNOBSERVED BAND ${fmt(r.lo, r.hi)}px — ${r.rules.length} rule(s): ${where.slice(0, 4).join(', ')}${where.length > 4 ? ` +${where.length - 4}` : ''}`;
  });
  /* An unparsed width query is worse than an uncovered band: the band list itself is then
     wrong, so "every band observed" would be a lie rather than an omission. It rides in
     the same array so every existing caller prints it without changing. */
  for (const u of unreadable) {
    lines.push(`  UNPARSED WIDTH QUERY — ${u.file}:${u.line}  @media ${u.raw}  (band list may be incomplete)`);
  }
  return lines;
}

/* pathToFileURL, not string-building: on Windows argv[1] is `C:\...` and import.meta.url
   is `file:///C:/...` — a hand-rolled `file://` + backslash swap gives two slashes, never
   matches, and the CLI silently prints nothing. It did exactly that on first run. */
if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const widths = process.argv.slice(2).map(Number).filter((n) => Number.isFinite(n));
  const bps = readBreakpoints();
  console.log(`${bps.length} screen width quer${bps.length === 1 ? 'y' : 'ies'} in ${CSS_ROOT}\n`);
  const seen = new Map();
  for (const b of bps) seen.set(`${b.kind}-${b.px}`, (seen.get(`${b.kind}-${b.px}`) ?? 0) + 1);
  for (const [k, n] of [...seen].sort()) console.log(`  ${k.padEnd(10)} x${n}`);
  const { rows } = coverage(widths, bps);
  console.log(`\nband            rules  observed by`);
  console.log(`--------------- -----  ------------`);
  for (const r of rows) {
    console.log(`${fmt(r.lo, r.hi).padEnd(15)} ${String(r.rules.length).padStart(5)}  ${r.widths.length ? r.widths.join(', ') : (widths.length ? 'NOTHING' : '—')}`);
  }
  if (widths.length) {
    const lines = uncoveredLines(widths, bps);
    console.log(lines.length ? `\n${lines.join('\n')}` : `\nevery band observed by ${widths.join(', ')}`);
  }
}
