// Storybook audit: runs axe-core (WCAG 2.0/2.1/2.2 A+AA + best-practice) on every story in every
// theme, then Tabs through the story and pixel-diffs each focused element against its unfocused
// rendering to flag missing focus indicators (SC 2.4.7). Visually hidden inputs (custom
// checkbox/radio/switch) are diffed on their visible container (closest <label> or parent).
//
// usage (run from the project root so playwright/axe-core resolve from its node_modules):
//   node storybook_audit.mjs <storybook-static-dir> <out.json>
// env:
//   THEMES=theme:light,theme:dark   Storybook globals per run (?globals=...); empty = one run, no globals
//   STORY_FILTER=^components-       regex on story id (default: all stories, docs entries skipped)
//   AXE_PATH=.../axe.min.js         when axe-core isn't resolvable from cwd (e.g. pnpm nested deps)
//   CHROME=/path/to/chrome          optional browser executable
//   CONC=6                          parallel pages
import { createRequire } from 'node:module';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const [dir, out] = process.argv.slice(2);
if (!dir || !out) {
  console.error('usage: node storybook_audit.mjs <storybook-static-dir> <out.json>');
  process.exit(1);
}
const require = createRequire(path.join(process.cwd(), 'noop.js'));
const { chromium } = require('playwright');
const axeSrc = fs.readFileSync(process.env.AXE_PATH || require.resolve('axe-core/axe.min.js'), 'utf8');
const themes = (process.env.THEMES || '').split(',').filter(Boolean);
if (!themes.length) themes.push('');
const filter = new RegExp(process.env.STORY_FILTER || '.');
const CONC = Number(process.env.CONC || 6);
const MAX_TABS = 15;

const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.ttf': 'font/ttf', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp' };
const server = http.createServer((req, res) => {
  let p = path.join(dir, decodeURIComponent(req.url.split('?')[0]));
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const base = `http://127.0.0.1:${server.address().port}`;

const index = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
const stories = Object.values(index.entries).filter((e) => e.type === 'story' && filter.test(e.id));
const jobs = stories.flatMap((s) => themes.map((theme) => ({ s, theme })));

async function auditStory(page, { s, theme }) {
  const globals = theme ? `&globals=${theme}` : '';
  await page.goto(`${base}/iframe.html?id=${s.id}&viewMode=story${globals}`, { waitUntil: 'load', timeout: 30000 });
  await page.waitForSelector('#storybook-root > *, #root > *', { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(400);
  await page.addScriptTag({ content: axeSrc });
  const axe = await page.evaluate(async () => {
    const root = document.querySelector('#storybook-root') || document.querySelector('#root');
    const res = await window.axe.run(root, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] },
    });
    return {
      violations: res.violations.map((v) => ({ id: v.id, impact: v.impact, tags: v.tags, help: v.help, count: v.nodes.length,
        nodes: v.nodes.slice(0, 5).map((nd) => ({ target: nd.target.join(' '), html: nd.html.slice(0, 200),
          summary: (nd.failureSummary || '').slice(0, 300), data: nd.any?.[0]?.data ?? null })) })),
      incomplete: res.incomplete.map((v) => ({ id: v.id, count: v.nodes.length })),
    };
  });

  const focus = [];
  const seen = new Set();
  for (let t = 0; t < MAX_TABS; t++) {
    await page.keyboard.press('Tab');
    await page.waitForTimeout(150);
    const info = await page.evaluate(() => {
      const root = document.querySelector('#storybook-root') || document.querySelector('#root');
      const el = document.activeElement;
      if (!el || el === document.body || !root.contains(el)) return null;
      el.setAttribute('data-focus-probe', '1');
      let r = el.getBoundingClientRect();
      let proxy = null;
      if (r.width <= 1 || r.height <= 1) { // visually hidden input: its focus shows on the container
        const c = el.closest('label') || el.parentElement;
        r = c.getBoundingClientRect();
        proxy = c.tagName.toLowerCase() + (c.className ? `.${String(c.className).split(' ')[0]}` : '');
      }
      return { html: el.outerHTML.slice(0, 160), proxy, x: r.x, y: r.y, w: r.width, h: r.height };
    });
    if (!info || seen.has(info.html)) break;
    seen.add(info.html);
    if (info.w === 0 || info.h === 0) { focus.push({ ...info, status: 'zero-size' }); continue; }
    const clip = { x: Math.max(0, info.x - 6), y: Math.max(0, info.y - 6), width: info.w + 12, height: info.h + 12 };
    const focused = await page.screenshot({ clip, animations: 'disabled' });
    await page.evaluate(() => { // park focus off-screen so the element renders unfocused
      const sink = document.createElement('div');
      sink.tabIndex = -1; sink.id = 'focus-sink';
      sink.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;height:1px';
      document.body.appendChild(sink); sink.focus();
    });
    await page.waitForTimeout(150);
    const blurred = await page.screenshot({ clip, animations: 'disabled' });
    focus.push({ ...info, status: Buffer.compare(focused, blurred) === 0 ? 'NO-VISIBLE-FOCUS' : 'ok' });
    await page.evaluate(() => { // restore focus so the next Tab continues from the probed element
      document.getElementById('focus-sink')?.remove();
      const el = document.querySelector('[data-focus-probe]');
      el?.removeAttribute('data-focus-probe');
      el?.focus({ focusVisible: true });
    });
  }
  return { ...axe, focus };
}

const browser = await chromium.launch({ executablePath: process.env.CHROME });
const results = [];
let next = 0;
async function worker() {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  while (next < jobs.length) {
    const n = next++;
    const { s, theme } = jobs[n];
    const meta = { id: s.id, title: s.title, name: s.name, importPath: s.importPath, theme };
    try {
      results.push({ ...meta, ...(await auditStory(page, jobs[n])) });
    } catch (e) {
      results.push({ ...meta, error: String(e).slice(0, 200) });
    }
    if (n % 40 === 0) console.error(`${n}/${jobs.length}`);
  }
  await page.close();
}
await Promise.all(Array.from({ length: CONC }, worker));
await browser.close();
server.close();
fs.writeFileSync(out, JSON.stringify(results, null, 1));

const byRule = {};
for (const r of results) for (const v of r.violations || []) byRule[v.id] = (byRule[v.id] || 0) + v.count;
const noFocus = results.flatMap((r) => r.focus || []).filter((f) => f.status === 'NO-VISIBLE-FOCUS').length;
console.error(`done: ${stories.length} stories × ${themes.length} theme(s), ${results.filter((r) => r.error).length} errors`);
console.error('violations by rule (node count):', byRule);
console.error('elements with no visible focus:', noFocus);
