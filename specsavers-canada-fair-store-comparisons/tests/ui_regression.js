/*
 * Rendered-page regression runner for dashboard-mockup.html (Phase E). SYNTHETIC data only.
 *
 * Loads the built page in headless Microsoft Edge through the DevTools protocol, runs tests/ui_selftest.js
 * (functional checks at 1440 px; layout checks at 375, 640@2x ≈ 200% zoom of 1280 px, 768, 1280, 1440 px),
 * and runs keyboard checks with real key events (Tab, arrow keys, Enter, Escape).
 * Writes evidence/ui-test-results.json and exits 1 on any failure.
 *
 * Run: node tests/ui_regression.js   (after python build/build_mockup.py)
 * Not covered: real screen readers, real browser zoom UI, touch hardware, other browsers.
 */
const fs = require("fs");
const path = require("path");
const { launch, fileUrl, sleep } = require("./cdp");

const ROOT = path.join(__dirname, "..");
const PAGE = path.join(ROOT, "dashboard-mockup.html");
const SELFTEST = fs.readFileSync(path.join(__dirname, "ui_selftest.js"), "utf8");
const OUT = path.join(ROOT, "evidence", "ui-test-results.json");
const LAYOUTS = [[375, 812, 1, "375 px (mobile)"], [640, 800, 2, "640 px at 2x (≈1280 px window at 200% zoom)"], [768, 1024, 1, "768 px (tablet)"], [1280, 900, 1, "1280 px"], [1440, 900, 1, "1440 px"]];

async function selftest(browser, mode, [w, h, scale, label]) {
  const page = await browser.newPage();
  try {
    await page.viewport(w, h, scale);
    await page.goto(fileUrl(PAGE));
    const errors = await page.eval("window.__dash ? 'ok' : 'app did not initialise'");
    if (errors !== "ok") return [{ id: "RUNNER", name: `${mode} @${label}: ${errors}`, pass: false, detail: "" }];
    await page.eval(SELFTEST.replace("__MODE__", mode));
    const res = await page.eval("JSON.stringify(window.__selftestResults || null)");
    const out = JSON.parse(res);
    if (!out) return [{ id: "RUNNER", name: `${mode} @${label}: self-test did not complete`, pass: false, detail: "" }];
    return out.map((r) => Object.assign(r, { viewport: label }));
  } finally { page.close(); }
}

async function keyboard(browser) {
  const R = [];
  const T = async (id, name, fn) => { try { const d = await fn(); R.push({ id, name, pass: !d, detail: d || "", viewport: "1440 px, real key events" }); } catch (e) { R.push({ id, name, pass: false, detail: String(e.message || e), viewport: "1440 px, real key events" }); } };
  const page = await browser.newPage();
  const Tab = () => page.key("Tab", "Tab", 9);
  const active = () => page.eval("(() => { const a = document.activeElement; return a ? (a.id || a.className || a.tagName) + '|' + (a.textContent || '').trim().slice(0, 40) + '|' + getComputedStyle(a).outlineStyle : 'none'; })()");
  try {
    await page.viewport(1440, 1000);
    await page.goto(fileUrl(PAGE));
    await T("UI-KEY-01", "Tab order starts with skip link, role, report tabs, then filters; focus outline visible", async () => {
      await page.eval("document.activeElement && document.activeElement.blur(); window.scrollTo(0,0)");
      const seen = [];
      for (let i = 0; i < 6; i++) { await Tab(); seen.push(await active()); }
      const ids = seen.map((s) => s.split("|")[0]);
      const problems = [];
      if (!/skip/.test(ids[0])) problems.push("first stop " + ids[0]);
      if (ids[1] !== "role") problems.push("second stop " + ids[1]);
      if (ids[2] !== "tab-p1") problems.push("third stop " + ids[2]);
      if (ids.includes("tab-p2")) problems.push("inactive tab in tab order (roving tabindex broken)");
      if (ids[3] !== "f-week") problems.push("fourth stop " + ids[3]);
      if (seen.some((s) => s.endsWith("|none"))) problems.push("focus without outline: " + seen.filter((s) => s.endsWith("|none")).join(", "));
      return problems.join("; ");
    });
    await T("UI-KEY-02", "Arrow keys move between report tabs and activate the page", async () => {
      await page.eval("document.getElementById('tab-p1').focus()");
      await page.key("ArrowRight", "ArrowRight", 39);
      const a = await page.eval("[__dash.getState().page, document.activeElement.id].join(',')");
      await page.key("End", "End", 35);
      const b = await page.eval("[__dash.getState().page, document.activeElement.id].join(',')");
      await page.key("Home", "Home", 36);
      const c = await page.eval("[__dash.getState().page, document.activeElement.id].join(',')");
      return [a === "p2,tab-p2" ? "" : "ArrowRight " + a, b === "p3,tab-p3" ? "" : "End " + b, c === "p1,tab-p1" ? "" : "Home " + c].filter(Boolean).join("; ");
    });
    await T("UI-KEY-03", "Enter on an exception row opens the diagnostic, moves focus to its heading; Enter on Back returns", async () => {
      await page.eval("__dash.backStack.length = 0; __dash.setState({page:'p1', week:'2026-05-25', region:'', province:'', format:'', banner:'', cohort:'', dq:''}); document.querySelector('[data-test=\"exc-row\"][data-store=\"SYN-005\"] button').focus()");
      await page.key("Enter", "Enter", 13);
      const a = await page.eval("[__dash.getState().page, __dash.getState().store, __dash.getState().week, document.activeElement.id].join(',')");
      await page.eval("document.getElementById('backBtn').focus()");
      await page.key("Enter", "Enter", 13);
      const b = await page.eval("[__dash.getState().page, __dash.getState().week].join(',')");
      return [a === "p3,SYN-005,2026-05-25,h-p3" ? "" : "drill " + a, b === "p1,2026-05-25" ? "" : "back " + b].filter(Boolean).join("; ");
    });
    await T("UI-KEY-04", "Help dialog: Enter opens, focus moves to Close, Tab stays inside, Escape closes and returns focus", async () => {
      await page.eval("__dash.setState({page:'p1', week:'2026-08-17'}); document.querySelector('#kpiCards [data-help=\"attendance\"]').focus()");
      await page.key("Enter", "Enter", 13);
      const open = await page.eval("!document.getElementById('helpDialog').hidden && document.activeElement.id");
      await Tab();
      const trapped = await page.eval("document.activeElement.id");
      await page.key("Escape", "Escape", 27);
      const closed = await page.eval("document.getElementById('helpDialog').hidden && document.activeElement.dataset.help");
      return [open === "help-close" ? "" : "open " + open, trapped === "help-close" ? "" : "trap " + trapped, closed === "attendance" ? "" : "close " + closed].filter(Boolean).join("; ");
    });
    await T("UI-KEY-05", "Data-quality week cells are keyboard operable (Enter selects the week)", async () => {
      await page.eval("__dash.setState({page:'p3', store:'SYN-027', week:'2026-08-17'}); document.querySelector('[data-set-week=\"2026-07-06\"]').focus()");
      await page.key("Enter", "Enter", 13);
      const st = await page.eval("[__dash.getState().week, document.querySelector('[data-test=\"funnel-withheld\"]') ? 'withheld' : 'shown'].join(',')");
      return st === "2026-07-06,withheld" ? "" : st;
    });
  } finally { page.close(); }
  return R;
}

(async () => {
  if (!fs.existsSync(PAGE)) { console.error("dashboard-mockup.html not found; run python build/build_mockup.py"); process.exit(1); }
  const browser = await launch();
  const results = [];
  try {
    results.push(...(await selftest(browser, "full", [1440, 1100, 1, "1440 px"])));
    for (const lay of LAYOUTS) results.push(...(await selftest(browser, "layout", lay)));
    results.push(...(await keyboard(browser)));
  } finally { await browser.close(); }
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify({ generated: new Date().toISOString(), browser: "Microsoft Edge (headless, Chromium)", results }, null, 1));
  const checks = results.filter((r) => r.id !== "INFO");
  const failed = checks.filter((r) => !r.pass);
  for (const r of results) console.log(`${r.id === "INFO" ? "INFO" : r.pass ? "PASS" : "FAIL"}  ${r.id.padEnd(11)} ${r.name} [${r.viewport}]${!r.pass || r.id === "INFO" ? " — " + r.detail : ""}`);
  console.log(`\nUI checks passed: ${checks.length - failed.length}/${checks.length} (${path.relative(ROOT, OUT)})`);
  process.exit(failed.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
