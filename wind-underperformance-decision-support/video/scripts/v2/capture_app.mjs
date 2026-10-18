/**
 * Captures the real Streamlit decision-support application as PNGs for the v2
 * product film, together with the on-screen position of every element the film
 * points a cursor at or highlights.
 *
 * Nothing here draws or invents interface. Each capture is the running
 * application at http://localhost:8515, photographed after a real interaction.
 * The boxes written to boxes.json are the browser's own measurements, so a
 * cursor or a focus mask placed from them lands on the actual control.
 *
 * Each page is captured at its full height in one image. The film then pans and
 * pushes inside that single sharp panel instead of cutting between scroll
 * positions, which is what makes the camera move feel continuous.
 *
 * Usage:  node scripts/v2/capture_app.mjs
 */
import {ensureBrowser, openBrowser} from '@remotion/renderer';
import fs from 'node:fs/promises';
import path from 'node:path';

const APP = 'http://localhost:8515';
const OUT = path.resolve('src/v2/assets/screens');

// Captured at twice the final pixel density so the camera can push into a panel
// without the interface turning soft.
const VIEW = {width: 1440, height: 1040, scale: 2};
const MAX_HEIGHT = 7600; // guards against a Chrome texture limit on tall pages

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Streamlit's toolbar, deploy button and status widget are development chrome,
 * not part of the analysis. They are hidden for the capture; nothing about the
 * application's own content is altered.
 */
const HIDE_CHROME = `
  (() => {
    const id = '__film_chrome__';
    if (document.getElementById(id)) return;
    const style = document.createElement('style');
    style.id = id;
    style.textContent = \`
      [data-testid="stToolbar"], [data-testid="stDecoration"],
      [data-testid="stStatusWidget"], [data-testid="stToolbarActions"],
      header[data-testid="stHeader"] { display: none !important; }
      [data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; }
    \`;
    document.head.appendChild(style);
  })();
`;

/** Page-side helpers, injected after every navigation. */
const HELPERS = `
  window.__find = (text, sel) => {
    const nodes = [...document.querySelectorAll(sel || '*')];
    return nodes.filter(n => {
      const t = (n.textContent || '').trim();
      return t === text || (t.startsWith(text) && t.length < text.length + 40);
    }).pop() || null;
  };
  window.__has = (text, sel) => {
    const nodes = [...document.querySelectorAll(sel || '*')];
    return nodes.filter(n => (n.textContent || '').includes(text)).pop() || null;
  };
  window.__box = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: Math.round(r.x), y: Math.round(r.y),
            w: Math.round(r.width), h: Math.round(r.height)};
  };
  window.__contentHeight = () => Math.max(
    document.body.scrollHeight, document.documentElement.scrollHeight,
    ...[...document.querySelectorAll('section, [data-testid="stMain"], .main')]
      .map(n => n.scrollHeight || 0));
`;

// Remotion's CDP wrapper returns {value, size}; the CDP payload is in `value`.
async function cdp(page, method, params = {}) {
  const result = await page._client().send(method, params);
  return result && 'value' in result ? result.value : result;
}

async function setSize(page, height) {
  await cdp(page, 'Emulation.setDeviceMetricsOverride', {
    width: VIEW.width, height: Math.min(Math.round(height), MAX_HEIGHT),
    deviceScaleFactor: VIEW.scale, mobile: false,
  });
}

/** True once Streamlit has stopped running and every Plotly chart has drawn. */
async function settled(page) {
  for (let i = 0; i < 90; i += 1) {
    const ready = await page.evaluate(`(() => {
      const running = document.querySelector('[data-testid="stStatusWidget"]');
      const plots = document.querySelectorAll('.js-plotly-plot');
      return !running && plots.length > 0
        && [...plots].every(p => p.querySelector('.main-svg'));
    })()`);
    if (ready) {await sleep(700); return true;}
    await sleep(400);
  }
  return false;
}

async function shoot(page, name) {
  const {data} = await cdp(page, 'Page.captureScreenshot', {format: 'png'});
  const file = path.join(OUT, `${name}.png`);
  await fs.writeFile(file, Buffer.from(data, 'base64'));
  const kb = ((await fs.stat(file)).size / 1024).toFixed(0);
  const size = await page.evaluate(`[window.innerWidth, window.innerHeight]`);
  console.log(`  ${name}.png  ${kb} KB  ${size[0]}x${size[1]} css`);
  return {file: `${name}.png`, cssWidth: size[0], cssHeight: size[1], scale: VIEW.scale};
}

/** Grows the viewport to the whole page so one capture holds the entire screen. */
async function growToFit(page) {
  await page.evaluate(HELPERS);
  await page.evaluate(HIDE_CHROME);
  const h = await page.evaluate(`window.__contentHeight()`);
  await setSize(page, h + 40);
  await sleep(700);
  await settled(page);
  await page.evaluate(HELPERS);
  await page.evaluate(HIDE_CHROME);
  return h;
}

/** Clicks a control by its visible text and waits for Streamlit to re-run. */
async function clickText(page, text, sel) {
  const hit = await page.evaluate(`(() => {
    const el = window.__find(${JSON.stringify(text)}, ${JSON.stringify(sel || null)});
    if (!el) return null;
    const b = window.__box(el);
    el.click();
    return b;
  })()`);
  if (!hit) throw new Error(`control not found: ${text}`);
  await sleep(1000);
  await settled(page);
  await page.evaluate(HELPERS);
  await page.evaluate(HIDE_CHROME);
  return hit;
}

async function openSection(page, section) {
  await setSize(page, VIEW.height);
  await page.goto({url: APP, timeout: 60000});
  await page.evaluate(HELPERS);
  await page.evaluate(HIDE_CHROME);
  await settled(page);
  if (section) await clickText(page, section, 'label, [data-testid="stRadio"] label p, p');
  return growToFit(page);
}

/**
 * Measures named targets. A target is either {text, sel} for a text match or
 * {query, index} for a direct selector, optionally walking up `up` parents.
 */
async function measure(page, targets) {
  const out = {};
  for (const [key, spec] of Object.entries(targets)) {
    out[key] = await page.evaluate(`(() => {
      let el = ${spec.query
        ? `document.querySelectorAll(${JSON.stringify(spec.query)})[${spec.index || 0}] || null`
        : spec.has
          ? `window.__has(${JSON.stringify(spec.has)}, ${JSON.stringify(spec.sel || null)})`
          : `window.__find(${JSON.stringify(spec.text)}, ${JSON.stringify(spec.sel || null)})`};
      for (let i = 0; i < ${spec.up || 0} && el; i++) el = el.parentElement || el;
      return window.__box(el);
    })()`);
  }
  return out;
}

/**
 * Measures every bar of a grouped Plotly bar chart, trace by trace. A callout
 * aimed at "Method A, R80790" then lands on that exact rectangle rather than at
 * a guessed position.
 */
async function measureBars(page, plotIndex) {
  return page.evaluate(`(() => {
    const plot = document.querySelectorAll('.js-plotly-plot')[${plotIndex}];
    if (!plot) return null;
    const traces = [...plot.querySelectorAll('g.trace.bars')];
    return traces.map((trace, t) => [...trace.querySelectorAll('g.point path')].map((node, i) => {
      const r = node.getBoundingClientRect();
      return {trace: t, index: i, x: Math.round(r.x), y: Math.round(r.y),
              w: Math.round(r.width), h: Math.round(r.height)};
    }));
  })()`);
}

async function main() {
  await fs.mkdir(OUT, {recursive: true});
  await ensureBrowser();
  const browser = await openBrowser('chrome', {});
  const page = await browser.newPage({});

  const manifest = {viewport: VIEW, captured: new Date().toISOString(), screens: {}};
  const add = async (key, name, pageName, state, targets, extra = {}) => {
    manifest.screens[key] = {
      ...await shoot(page, name), page: pageName, state,
      boxes: await measure(page, targets), ...extra,
    };
  };

  const PLOT = (i) => ({query: '.js-plotly-plot', index: i});
  const METRIC = (text) => ({text, sel: '[data-testid="stMetricLabel"]', up: 2});

  console.log('Executive cockpit');
  await openSection(page, 'Executive cockpit');
  await add('cockpit', 'cockpit', 'Executive cockpit', 'full page, default controls', {
    title: {text: 'Which issue should be investigated first?', sel: 'h1'},
    energyBasis: {text: 'Energy basis', sel: 'label p'},
    methodView: {text: 'Method view', sel: 'label p'},
    recommendation: {text: 'Recommendation', sel: 'h3'},
    accounting: {text: '2015 energy accounting', sel: 'h3'},
    gross: METRIC('Gross shortfall'),
    reviewable: METRIC('In reviewable events'),
    nonPersistent: METRIC('Non-persistent'),
    missing: METRIC('Missing energy'),
    potentialMwh: METRIC('Potential MWh'),
    accountingChart: PLOT(0),
    rankingChart: PLOT(1),
    eventScatter: PLOT(2),
  });
  // Trace order is A, B, C as the chart adds them; point order is the turbines
  // sorted by name. Recorded so a callout can name which bar it points at.
  manifest.screens.cockpit.bars = await measureBars(page, 1);
  manifest.screens.cockpit.barOrder = {
    traces: ['A_turbine_specific', 'B_pooled_transparent', 'C_pooled_challenger'],
    points: ['R80711', 'R80721', 'R80736', 'R80790'],
  };

  // A real control that genuinely changes the ranking chart's metric.
  const basisClick = await clickText(page, 'Gross residual shortfall', 'label p, label');
  await growToFit(page);
  await add('cockpit_gross', 'cockpit_gross', 'Executive cockpit',
    'after clicking the Gross residual shortfall basis', {
      rankingChart: PLOT(1), accountingChart: PLOT(0),
    }, {clicked: basisClick, control: 'Energy basis radio'});

  console.log('Data trust');
  await openSection(page, 'Data trust');
  await add('datatrust', 'datatrust', 'Data trust', 'full page, default', {
    title: {text: 'Data trust', sel: 'h1'},
    rawRecords: METRIC('Raw records'),
    eligible: METRIC('Reference-eligible'),
    longestGap: METRIC('Longest data gap'),
    validation: METRIC('Validation checks'),
    funnelChart: PLOT(0),
    exclusionChart: PLOT(1),
    completenessChart: PLOT(2),
    timestampChart: PLOT(3),
    missingRunsChart: PLOT(4),
    expander: {text: 'Why the summer timestamps were an hour early', sel: 'summary, p'},
  });

  const expanderClick = await clickText(page,
    'Why the summer timestamps were an hour early', 'summary, p');
  await growToFit(page);
  await add('datatrust_expander', 'datatrust_expander', 'Data trust',
    'timestamp explanation opened by a real click', {
      expander: {text: 'Why the summer timestamps were an hour early', sel: 'summary, p'},
      timestampChart: PLOT(3),
      explanation: {has: 'all 48 duplicate and all 48 absent intervals', sel: 'p'},
    }, {clicked: expanderClick, control: 'expander'});

  console.log('Method and scenario lab');
  await openSection(page, 'Method and scenario lab');
  await add('lab', 'lab', 'Method and scenario lab', 'full page, default', {
    title: {text: 'Method and scenario lab', sel: 'h1'},
    turbines: {text: 'Turbines', sel: 'label p'},
    comparisonChart: PLOT(0),
    recoveryChart: PLOT(1),
  });

  console.log('Investigation explorer');
  await openSection(page, 'Investigation explorer');
  await add('explorer', 'explorer', 'Investigation explorer', 'full page, default', {
    title: {text: 'Investigation explorer', sel: 'h1'},
    scatter: PLOT(0),
    heatmap: PLOT(1),
    timeline: PLOT(2),
    neighbours: PLOT(3),
    explanations: {text: 'Possible explanations', sel: 'strong, p'},
    observedFacts: {text: 'Observed facts', sel: 'strong, p'},
    recordsRequired: {text: 'Operational records required', sel: 'strong, p'},
    nextAction: {text: 'Recommended next action', sel: 'strong, p'},
    escalate: {text: 'Escalate if', sel: 'strong, p'},
  });

  await fs.writeFile(path.join(OUT, 'boxes.json'), JSON.stringify(manifest, null, 2));
  console.log(`\n${Object.keys(manifest.screens).length} screens -> ${OUT}`);
  await browser.close({silent: true});
}

main().catch((e) => {console.error(e); process.exit(1);});
