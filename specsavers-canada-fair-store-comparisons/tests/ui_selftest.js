/*
 * Rendered-page regression checks for dashboard-mockup.html (Phase E). SYNTHETIC data only.
 * Injected into a temporary copy of the page by tests/ui_regression.py and run in headless Microsoft Edge.
 * It drives the page through its state API (window.__dash) and real DOM events, then asserts on rendered output.
 * MODE is replaced by the runner: "full" (functional checks) or "layout" (overflow and text-sanity checks at the current width).
 */
(function () {
  "use strict";
  const MODE = "__MODE__";
  const R = [];
  const dash = window.__dash;
  const q = (s, root) => (root || document).querySelector(s);
  const qa = (s, root) => [...(root || document).querySelectorAll(s)];
  const txt = (s) => ((q(s) || {}).textContent || "").replace(/\s+/g, " ").trim();
  const mainHTML = () => q("main").innerHTML;
  const LATEST = dash.D.weeks[dash.D.weeks.length - 1];
  const blank = { region: "", province: "", format: "", banner: "", cohort: "", dq: "" };
  function T(id, name, fn) {
    try {
      const out = fn();
      const pass = out === true || (out && out.pass === true);
      R.push({ id, name, pass, detail: out && out.detail ? String(out.detail).slice(0, 400) : pass ? "" : JSON.stringify(out).slice(0, 400) });
    } catch (e) {
      R.push({ id, name, pass: false, detail: String((e && e.message) || e).slice(0, 400) });
    }
  }
  const go = (st) => { dash.backStack.length = 0; dash.setState(Object.assign({}, blank, { week: LATEST }, st)); };
  const expectAll = (checks) => { const bad = checks.filter(([ok]) => !ok).map(([, m]) => m); return { pass: !bad.length, detail: bad.join(" | ") }; };
  const fire = (el, type) => el.dispatchEvent(new Event(type, { bubbles: true }));
  const OUT_OF_ATLANTIC = /SYN-0(0[1-9]|1\d|2[0-4])\b/;
  const ATLANTIC = ["SYN-025", "SYN-026", "SYN-027", "SYN-028", "SYN-029", "SYN-030"];
  const KPIS = ["conversion", "utilization", "attendance", "on_time", "turnaround", "recall_rate", "exams", "rev_per_exam"];
  const badText = (s) => /\bNaN\b|\bInfinity\b|\bundefined\b|\bnull\b/.test(s);

  function sanityPass(label) {
    const main = q("main");
    const t = main.textContent;
    const attrs = qa("svg *", main).map((e) => [...e.attributes].map((a) => a.value).join(" ")).join(" ");
    return [!badText(t) && !/NaN|Infinity/.test(attrs), `${label}: NaN/Infinity/undefined/null in output`];
  }

  if (MODE === "layout") {
    const w = window.innerWidth;
    const combos = [["ROL", "p1", "SYN-014"], ["ROL", "p2", "SYN-014"], ["ROL", "p3", "SYN-014"], ["RRM", "p1", "SYN-027"], ["RRM", "p2", "SYN-027"], ["OP", "p3", "SYN-014"], ["RP", "p2", "SYN-014"]];
    for (const [role, page, store] of combos) {
      T("UI-RESP-01", `No page-level horizontal overflow · ${role} ${page} @${w}px`, () => {
        go({ role, page, store });
        const sw = document.documentElement.scrollWidth, bw = document.body.scrollWidth;
        const wideOutside = qa("main *").filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > w + 1 && !e.closest(".scroll") && !e.closest("nav.tabs"); }).slice(0, 3).map((e) => `${e.tagName} "${(e.textContent || "").trim().slice(0, 30)}" right=${Math.round(e.getBoundingClientRect().right)} in #${(e.closest("[id]") || {}).id}`);
        return expectAll([[sw <= w + 1 && bw <= w + 1, `scrollWidth ${sw}/${bw} > viewport ${w}`], [wideOutside.length === 0, `elements past viewport: ${wideOutside.join(", ")}`], sanityPass(page)]);
      });
    }
    T("UI-RESP-02", `Controls usable @${w}px (tabs, filters and store selector within viewport; touch targets >= 36px)`, () => {
      go({ role: "ROL", page: "p3", store: "SYN-014" });
      const ctrls = qa("select, .filters button, nav.tabs button, .storebar button").filter((e) => e.getClientRects().length && !e.closest("[hidden]"));
      const off = ctrls.filter((e) => { const r = e.getBoundingClientRect(); return r.width === 0 || r.left < -1 || (r.right > w + 1 && !e.closest("nav.tabs")); });
      const small = ctrls.filter((e) => e.getBoundingClientRect().height < 36);
      return expectAll([[off.length === 0, `off-screen: ${off.map((e) => e.id || e.textContent).join(", ")}`], [small.length === 0, `small targets: ${small.map((e) => e.id || e.textContent).join(", ")}`]]);
    });
    T("UI-RESP-03", `Chart text stays readable @${w}px (SVG drawn at container width; axis text 11px or larger)`, () => {
      go({ role: "ROL", page: "p3", store: "SYN-014" });
      const svgs = qa("#trendCards svg");
      const issues = svgs.filter((s) => { const r = s.getBoundingClientRect(); const vb = s.viewBox.baseVal; return vb && vb.width && r.width / vb.width < 0.95; });
      const tiny = qa("#trendCards svg text").filter((t) => parseFloat(t.getAttribute("font-size")) < 11);
      return expectAll([[svgs.length >= 6, `charts rendered: ${svgs.length}`], [issues.length === 0, `scaled-down charts: ${issues.length}`], [tiny.length === 0, `tiny labels: ${tiny.length}`]]);
    });
    R.push({ id: "INFO", name: "viewport", pass: true, detail: `innerWidth=${w}, devicePixelRatio=${window.devicePixelRatio}` });
  } else {
    T("UI-ALL-01", "Simulated role view note is visible and does not claim security", () => {
      const t = txt(".simnote");
      return expectAll([[/Simulated role view/.test(t), "note missing"], [/not\s+authentication, row-level security or object-level security/.test(t), "disclaimer wording"]]);
    });
    T("UI-ALL-02", "Banner shows separate artefact versions and snapshot treatment", () => {
      go({ role: "ROL", page: "p1" });
      const b = txt("#banner");
      return expectAll([[/KPI dictionary v0\.2/.test(b) && /Exception rules v0\.2/.test(b) && /Prompt library v0\.2/.test(b), b], [/treated as final/.test(b), "snapshot treatment missing"]]);
    });
    T("UI-ROL-01", "Retail Operations lead, week of 2026-08-17: network cards and banner", () => {
      go({ role: "ROL", page: "p1" });
      return expectAll([[txt('[data-test="val-stores"]') === "30", "stores " + txt('[data-test="val-stores"]')], [txt('[data-test="val-exams_total"]') === "3,496", "exams " + txt('[data-test="val-exams_total"]')],
        [txt('[data-test="banner-amber"]') === "▲ 2 Amber", txt('[data-test="banner-amber"]')], [txt('[data-test="banner-red"]') === "■ 0 Red", txt('[data-test="banner-red"]')],
        [txt('[data-test="val-utilization"]') === "82.4%", "util " + txt('[data-test="val-utilization"]')]]);
    });
    T("UI-RRM-01", "Regional Retail Manager (Atlantic), week of 2026-08-17: every card uses Atlantic scope", () => {
      go({ role: "RRM", page: "p1" });
      const regions = qa('[data-test="region-row"]').map((r) => r.dataset.region);
      return expectAll([
        [txt('[data-test="val-stores"]') === "6", "stores " + txt('[data-test="val-stores"]')], [txt('[data-test="val-exams_total"]') === "545", "exams " + txt('[data-test="val-exams_total"]')],
        [txt('[data-test="val-utilization"]') === "81.0%", "util " + txt('[data-test="val-utilization"]')], [txt('[data-test="val-attendance"]') === "94.6%", "att " + txt('[data-test="val-attendance"]')],
        [txt('[data-test="val-conversion"]') === "55.8%", "conv " + txt('[data-test="val-conversion"]')], [txt('[data-test="val-on_time"]') === "77.3%", "on-time " + txt('[data-test="val-on_time"]')],
        [txt('[data-test="val-turnaround"]') === "9.1 days", "turnaround " + txt('[data-test="val-turnaround"]')],
        [JSON.stringify(regions) === '["Atlantic"]', "region rows " + regions], [!!q('[data-test="network-reference"]') && /comparison population, not your scope/.test(txt('[data-test="network-reference-note"]')), "network reference label"],
        [/Regional Overview — Atlantic/.test(txt("#h-p1")), "heading"],
      ]);
    });
    T("UI-RRM-02", "Regional banner counts reflect the Atlantic scope (0 Amber, 0 Red, 6 Green)", () => {
      go({ role: "RRM", page: "p1" });
      return expectAll([[txt('[data-test="banner-amber"]') === "▲ 0 Amber", txt('[data-test="banner-amber"]')], [txt('[data-test="banner-green"]') === "● 6 Green", txt('[data-test="banner-green"]')], [txt('[data-test="banner-red"]') === "■ 0 Red", txt('[data-test="banner-red"]')]]);
    });
    T("UI-RRM-03", "Regional manager never sees out-of-region store identities (all pages, stores, KPIs; text, titles and labels)", () => {
      const leaks = [];
      go({ role: "RRM", page: "p1" });
      if (OUT_OF_ATLANTIC.test(mainHTML() + q(".filters").innerHTML)) leaks.push("p1");
      for (const store of ATLANTIC) {
        for (const kpi of KPIS) { go({ role: "RRM", page: "p2", store, kpi }); if (OUT_OF_ATLANTIC.test(mainHTML())) leaks.push(`p2 ${store} ${kpi}`); }
        go({ role: "RRM", page: "p3", store }); if (OUT_OF_ATLANTIC.test(mainHTML())) leaks.push(`p3 ${store}`);
      }
      const opts = qa("#p2store option").map((o) => o.value);
      return expectAll([[!leaks.length, "leaks: " + leaks.slice(0, 5).join(", ")], [opts.every((o) => ATLANTIC.includes(o)), "store options " + opts]]);
    });
    T("UI-RP-01", "Retail Partner: own store only, anonymous peers, Network Overview unavailable", () => {
      go({ role: "RP", page: "p1" });
      const st = dash.getState();
      const other = /SYN-0(0\d|1[0-35-9]|2\d|30)\b/;
      const leaks = [];
      for (const kpi of KPIS) { go({ role: "RP", page: "p2", kpi }); if (other.test(mainHTML())) leaks.push("p2 " + kpi); }
      go({ role: "RP", page: "p3" }); if (other.test(mainHTML())) leaks.push("p3");
      return expectAll([[st.page === "p3", "landing " + st.page], [q("#tab-p1").getAttribute("aria-disabled") === "true", "p1 tab not disabled"], [!leaks.length, "leaks " + leaks], [qa("#p3store option").length === 1, "store options"]]);
    });
    T("UI-OP-01", "Optometry Partner: revenue restricted everywhere; conversion shown with U-41 note", () => {
      const probs = [];
      for (const kpi of KPIS) { go({ role: "OP", page: "p2", kpi }); if (/\$\d/.test(q("main").textContent)) probs.push("p2 $ " + kpi); }
      go({ role: "OP", page: "p2" });
      if (!/Restricted/.test(txt('[data-test="cmp-rev_per_exam"]'))) probs.push("cmp row not restricted");
      go({ role: "OP", page: "p3" });
      if (/\$\d/.test(q("main").textContent)) probs.push("p3 $");
      if (!/U-41/.test(txt("#funnel"))) probs.push("U-41 note");
      return expectAll([[!probs.length, probs.join(", ")]]);
    });
    T("UI-RED-01", "SYN-022 week of 2026-05-25 (Red): values withheld, data prompt only, no performance prompt", () => {
      go({ role: "ROL", page: "p3", store: "SYN-022", week: "2026-05-25" });
      const perf = qa('[data-test^="prompt-"]').map((e) => e.dataset.test).filter((t) => t !== "prompt-Data");
      const p3 = [[!!q('[data-test="funnel-withheld"]'), "funnel not withheld"], [!!q('[data-test="prompt-Data"]'), "no data prompt"], [!perf.length, "performance prompts " + perf]];
      go({ role: "ROL", page: "p2", store: "SYN-022", week: "2026-05-25" });
      return expectAll(p3.concat([[!!q('[data-test="red-warning"]'), "p2 red warning"], [/Data check required/.test(txt('[data-test="cmp-conversion"]')), "cmp conversion " + txt('[data-test="cmp-conversion"]')], [!/■ Flag/.test(txt('[data-test="cmp-table"]')), "flag shown on Red week"], [!/60\.8%/.test(q("main").textContent), "60.8% still displayed"]]));
    });
    T("UI-RED-02", "SYN-027 week of 2026-07-06 (stale): conversion and ramp index withheld; earlier week available", () => {
      go({ role: "ROL", page: "p2", store: "SYN-027", week: "2026-07-06" });
      const head = txt("#p2head");
      const main = q("main").textContent;
      const withheld = [[/Ramp index: withheld/.test(head), head], [!/56\.5%/.test(txt('[data-test="cmp-table"]')), "56.5% displayed"], [!/99\.7|Ramp index 100\b/.test(head), "ramp value displayed"]];
      go({ role: "ROL", page: "p2", store: "SYN-027", week: "2026-06-29" });
      return expectAll(withheld.concat([[/Ramp index \d+/.test(txt("#p2head")), "earlier ramp missing " + txt("#p2head")], [!badText(main), "bad text"]]));
    });
    T("UI-RED-03", "Network view in a week with a Red store lists a data check and excludes it from rates", () => {
      go({ role: "ROL", page: "p1", week: "2026-05-25" });
      const rows = qa('[data-test="exc-row"]').filter((r) => r.dataset.store === "SYN-022");
      return expectAll([[rows.some((r) => r.dataset.stage === "Data"), "no data-check row"], [txt('[data-test="banner-red"]') === "■ 1 Red", txt('[data-test="banner-red"]')], [/rates exclude 1 Red/.test(txt("#p1-scope")), txt("#p1-scope")]]);
    });
    T("UI-FUN-01", "SYN-014 funnel: 460 / 350 / 326 / 187 in separate cells that do not overlap", () => {
      go({ role: "ROL", page: "p3", store: "SYN-014" });
      const vals = ["slots", "held", "done", "buy"].map((k) => txt(`[data-test="funnel-${k}"]`));
      const overlaps = qa("table.funnel tbody tr").filter((tr) => {
        const cells = qa("th, td", tr).map((c) => c.getBoundingClientRect()).filter((r) => r.width > 0);
        for (let i = 0; i < cells.length; i++) for (let j = i + 1; j < cells.length; j++) {
          const a = cells[i], b = cells[j];
          if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) return true;
        }
        return false;
      });
      return expectAll([[JSON.stringify(vals) === '["460","350","326","187"]', "counts " + vals], [!overlaps.length, "overlapping cells in " + overlaps.length + " rows"], [/Booked minus cancelled/.test(txt("#funnel")), "held definition"], [/4 of 4 weeks usable/.test(txt('[data-test="funnel-window"]')), txt('[data-test="funnel-window"]')]]);
    });
    T("UI-FUN-02", "Funnel window after Red weeks states usable weeks (SYN-022, week of 2026-06-15)", () => {
      go({ role: "ROL", page: "p3", store: "SYN-022", week: "2026-06-15" });
      return expectAll([[/only 1 usable week/.test(txt("#funnel")), txt("#funnel")]]);
    });
    T("UI-SUP-01", "Recall counts 1-4 never shown as numbers; SYN-014 latest shows <5 (all stores, all weeks)", () => {
      const bad = [];
      for (const s of dash.D.stores) {
        go({ role: "ROL", page: "p3", store: s.id });
        for (const c of qa('[data-test="rb-cell"]')) if (/^[1-4]$/.test(c.querySelector("b").textContent.trim())) bad.push(s.id + " " + c.dataset.week);
        if (qa("#dqPanel td").some((td) => /^[1-4]$/.test(td.textContent.trim()) && td.cellIndex === 4)) bad.push(s.id + " unresolved");
      }
      go({ role: "ROL", page: "p3", store: "SYN-014" });
      const latest = qa('[data-test="rb-cell"]').find((c) => c.dataset.week === LATEST);
      return expectAll([[!bad.length, "unsuppressed: " + bad.slice(0, 5)], [latest && latest.querySelector("b").textContent === "<5", "latest cell " + (latest && latest.textContent)]]);
    });
    T("UI-EXC-02", "Rule-specific explanations: SYN-005 rule (b) cites own baseline; SYN-019 rule (a) cites peers", () => {
      go({ role: "ROL", page: "p3", store: "SYN-005", week: "2026-05-25" });
      const c = txt('[data-test="prompt-Conversion"]');
      go({ role: "ROL", page: "p3", store: "SYN-019" });
      const a = txt('[data-test="prompt-Attendance"]');
      return expectAll([[/Rule \(b\), own trend/.test(c) && /own baseline/.test(c), c], [/Rule \(a\), peer comparison/.test(a) && /peer median/.test(a), a], [!/differs from comparable stores/.test(c), "generic peer wording on rule b"]]);
    });
    T("UI-EXC-03", "SYN-030 latest: no triggered rule is distinguished from unavailable peer comparison", () => {
      go({ role: "ROL", page: "p3", store: "SYN-030" });
      return expectAll([[!!q('[data-test="no-flags"]'), "no-flags state"], [/peer comparison unavailable/.test(txt('[data-test="unavailable-reasons"]')), txt('[data-test="unavailable-reasons"]')]]);
    });
    T("UI-EXC-04", "Network exception list keeps both fulfilment KPIs for SYN-025", () => {
      go({ role: "ROL", page: "p1" });
      const r = qa('[data-test="exc-row"]').find((x) => x.dataset.store === "SYN-025" && x.dataset.stage === "Fulfilment");
      return expectAll([[!!r && /On-time/.test(r.textContent) && /Turnaround/.test(r.textContent), r ? r.textContent : "row missing"], [/with a triggered rule/.test(txt('[data-test="exc-summary"]')), "summary"]]);
    });
    T("UI-EMPTY-01", "Compact empty state explains history and does not imply health", () => {
      go({ role: "ROL", page: "p3", store: "SYN-014" });
      const t = txt('[data-test="no-flags"]');
      return expectAll([[/does not show that every area is performing well/.test(t), t], [q("#prompts").getBoundingClientRect().height < 420, "panel height " + q("#prompts").getBoundingClientRect().height]]);
    });
    T("UI-NAV-01", "Filters apply after role scope and show a summary (Atlantic + Grocery-hosted = 4 stores)", () => {
      go({ role: "ROL", page: "p1" });
      const reg = q("#f-region"); reg.value = "Atlantic"; fire(reg, "change");
      const fmt = q("#f-format"); fmt.value = "Grocery-hosted"; fire(fmt, "change");
      return expectAll([[txt('[data-test="val-stores"]') === "4", "stores " + txt('[data-test="val-stores"]')], [/Filters: region: Atlantic, format: Grocery-hosted/.test(txt("#f-summary")), txt("#f-summary")], [/4 stores in view/.test(txt("#f-summary")), "count"]]);
    });
    T("UI-NAV-02", "Reset returns to latest week with no filters", () => {
      go({ role: "ROL", page: "p1", week: "2026-05-25", cohort: "Mature" });
      q("#f-reset").click();
      const st = dash.getState();
      return expectAll([[st.week === LATEST && !st.cohort, JSON.stringify(st)], [/No filters applied/.test(txt("#f-summary")), txt("#f-summary")]]);
    });
    T("UI-NAV-03", "Drill-through from an exception keeps week and filters, moves focus, and Back restores the view", () => {
      go({ role: "ROL", page: "p1", week: "2026-05-25", cohort: "Mature" });
      const btn = q('[data-test="exc-row"][data-store="SYN-005"] button');
      if (!btn) return { pass: false, detail: "SYN-005 row missing" };
      btn.click();
      const st = dash.getState();
      const focusOk = document.activeElement && document.activeElement.id === "h-p3";
      const back = q("#backBtn");
      const checks = [[st.page === "p3" && st.store === "SYN-005" && st.week === "2026-05-25" && st.cohort === "Mature", JSON.stringify(st)], [focusOk, "focus " + (document.activeElement && document.activeElement.id)], [!!back, "no back button"]];
      if (back) back.click();
      const st2 = dash.getState();
      checks.push([st2.page === "p1" && st2.week === "2026-05-25" && st2.cohort === "Mature", "after back " + JSON.stringify(st2)]);
      checks.push([/#.*page=p1/.test(location.hash) && /week=2026-05-25/.test(location.hash), "hash " + location.hash]);
      return expectAll(checks);
    });
    T("UI-NAV-04", "Benchmarking ⇄ diagnostic keep the same store and week; historical week selectable from the filter bar", () => {
      go({ role: "ROL", page: "p2", store: "SYN-029" });
      const wkSel = q("#f-week"); wkSel.value = "2026-04-06"; fire(wkSel, "change");
      q("#to-p3").click();
      const a = dash.getState();
      q("#to-p2").click();
      const b = dash.getState();
      return expectAll([[a.page === "p3" && a.store === "SYN-029" && a.week === "2026-04-06", JSON.stringify(a)], [b.page === "p2" && b.store === "SYN-029" && b.week === "2026-04-06", JSON.stringify(b)], [qa("#f-week option").length === 26, "week options"]]);
    });
    T("UI-HELP-01", "KPI definition dialog shows formula, units, period, exclusions, owner, version, limitations; Escape returns focus", () => {
      go({ role: "ROL", page: "p1" });
      const b = q('#kpiCards [data-help="conversion"]');
      b.focus(); b.click();
      const body = txt("#help-body"), title = txt("#help-title");
      const open = !q("#helpDialog").hidden;
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      return expectAll([[open, "not opened"], [/KPI-05/.test(title), title], [["Formula", "Units", "Period", "Exclusions", "Proposed owner", "Version", "Limitations"].every((w) => body.includes(w)), body.slice(0, 200)], [q("#helpDialog").hidden, "not closed"], [document.activeElement === b, "focus not returned"]]);
    });
    T("UI-A11Y-01", "Tabs: aria-controls, roving tabindex and arrow-key navigation", () => {
      go({ role: "ROL", page: "p1" });
      const tabs = qa('[role="tab"]');
      const ctrl = tabs.every((t) => q("#" + t.getAttribute("aria-controls")) && q("#" + t.getAttribute("aria-controls")).getAttribute("aria-labelledby") === t.id);
      const snapshot = tabs.map((t) => `${t.id}:${t.getAttribute("aria-selected")}:${t.tabIndex}`).join(" ");
      const selOk = snapshot === "tab-p1:true:0 tab-p2:false:-1 tab-p3:false:-1";
      q("#tab-p1").focus();
      q("#tab-p1").dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
      const st = dash.getState();
      return expectAll([[ctrl, "aria-controls/labelledby"], [selOk, "selected tab " + snapshot], [st.page === "p2" && document.activeElement.id === "tab-p2", `after ArrowRight page=${st.page} focus=${document.activeElement.id}`]]);
    });
    T("UI-A11Y-02", "Every chart SVG has a title and description and a data-table alternative", () => {
      const probs = [];
      for (const [page, store] of [["p1", ""], ["p2", "SYN-014"], ["p3", "SYN-014"]]) {
        go({ role: "ROL", page, store });
        for (const svg of qa("main section:not([hidden]) svg[role='img']")) {
          const ids = (svg.getAttribute("aria-labelledby") || "").split(" ").filter(Boolean);
          if (ids.length < 2 || ids.some((i) => !q("#" + i) || !q("#" + i).textContent.trim())) probs.push(page + " svg label");
        }
        for (const c of qa("main section:not([hidden]) .chart")) if (c.querySelector("svg[role='img']") && !c.querySelector("details.tbl table")) probs.push(page + " " + c.id + " no table");
      }
      return expectAll([[!probs.length, probs.slice(0, 5).join(", ")]]);
    });
    T("UI-A11Y-03", "Tables use header scopes; controls and buttons have accessible names", () => {
      const probs = [];
      for (const [page, store] of [["p1", ""], ["p2", "SYN-029"], ["p3", "SYN-022"]]) {
        go({ role: "ROL", page, store, week: page === "p3" ? "2026-06-01" : LATEST });
        for (const th of qa("main section:not([hidden]) thead th")) if (th.getAttribute("scope") !== "col") probs.push(page + " th scope");
        for (const b of qa("main button, header button, .filters button")) if (!(b.getAttribute("aria-label") || b.textContent.trim())) probs.push(page + " unnamed button");
        for (const s of qa("select")) if (!q(`label[for="${s.id}"]`)) probs.push("unlabelled select " + s.id);
      }
      return expectAll([[!probs.length, [...new Set(probs)].slice(0, 5).join(", ")]]);
    });
    T("UI-CHART-01", "Unique y-axis labels; dashed peer lines have dashed legend samples; flag dots explained", () => {
      const probs = [];
      for (const store of ["SYN-012", "SYN-014", "SYN-005", "SYN-030"]) {
        go({ role: "ROL", page: "p3", store });
        for (const svg of qa("#trendCards svg[role='img']")) {
          const labels = qa("text[text-anchor='end']", svg).map((t) => t.textContent);
          if (new Set(labels).size !== labels.length) probs.push(`${store} duplicate labels ${labels}`);
        }
        for (const li of qa("#trendCards .legend li")) if (/Peer median/.test(li.textContent) && !li.querySelector("line[stroke-dasharray]")) probs.push(store + " solid peer legend");
        for (const card of qa("#trendCards .card")) if (card.querySelector("circle[r='4.5']") && !/Exception flagged/.test(card.textContent)) probs.push(store + " unexplained dots");
        if (!/2026/.test(txt("#trendCards .sub"))) probs.push("no year");
      }
      return expectAll([[!probs.length, probs.slice(0, 4).join(" | ")]]);
    });
    T("UI-RAMP-01", "Same ramp chart for every eligible store; Mature store explained; gaps and cohort change described", () => {
      const probs = [];
      for (const s of ["SYN-004", "SYN-008", "SYN-011", "SYN-014", "SYN-018", "SYN-020", "SYN-023", "SYN-025", "SYN-027", "SYN-028", "SYN-030"]) {
        go({ role: "ROL", page: "p2", store: s });
        const t = txt("#ramp");
        if (!/This store: completed exams per week \(4-week average\)/.test(t)) probs.push(s + " series");
        if (!/Peer median at the same weeks since opening/.test(t)) probs.push(s + " peer");
      }
      go({ role: "ROL", page: "p2", store: "SYN-001" });
      if (!/Not applicable: this store is Mature/.test(txt("#ramp"))) probs.push("SYN-001 mature message");
      go({ role: "ROL", page: "p2", store: "SYN-014" });
      if (!/New → Developing/.test(q("#ramp").innerHTML)) probs.push("SYN-014 cohort marker");
      go({ role: "ROL", page: "p2", store: "SYN-030" });
      if (!/fewer than 5 peers observed at that age: weeks since opening/.test(txt("#ramp"))) probs.push("SYN-030 gap text " + txt("#ramp").slice(0, 160));
      return expectAll([[!probs.length, probs.join(", ")]]);
    });
    T("UI-PEER-01", "Peer fallback (SYN-029) and unavailable peer comparison (SYN-030) are explained", () => {
      go({ role: "ROL", page: "p2", store: "SYN-029" });
      const f = txt('[data-test="fallback-warning"]');
      go({ role: "ROL", page: "p2", store: "SYN-030" });
      const s = txt('[data-test="suppressed-peers"]');
      return expectAll([[/Small peer group/.test(f) && /Street-front peer/.test(f) && /Developing peers used/.test(f), f], [/Peer comparison not available/.test(s) && /own values remain visible/.test(s), s]]);
    });
    T("UI-AMBER-01", "SYN-003 latest week: Amber data quality and provisional marker", () => {
      go({ role: "ROL", page: "p3", store: "SYN-003" });
      return expectAll([[/Data quality: ▲ Amber/.test(txt("#p3head")) && /provisional/.test(txt("#p3head")), txt("#p3head")]]);
    });
    T("UI-PLACE-01", "KPI placement: recall and turnaround cards (p1), completed exams row (p2), ramp index and revenue context (p3)", () => {
      go({ role: "ROL", page: "p1" });
      const p1 = !!q('[data-test="card-recall_rate"]') && !!q('[data-test="card-turnaround"]');
      go({ role: "ROL", page: "p2", store: "SYN-014" });
      const p2 = !!q('[data-test="cmp-exams"]');
      go({ role: "ROL", page: "p3", store: "SYN-014" });
      return expectAll([[p1, "p1 cards"], [p2, "p2 exams row"], [/Ramp index 102/.test(txt("#p3head")), txt("#p3head")], [/revenue per completed exam \$/.test(txt("#funnel")), "revenue context"]]);
    });
    T("UI-SAFE-01", "No NaN, Infinity, undefined or null in rendered output across roles, pages, stores and weeks", () => {
      const probs = [];
      const weeks = [dash.D.weeks[0], dash.D.weeks[3], "2026-05-25", "2026-07-06", LATEST];
      for (const w of weeks) {
        go({ role: "ROL", page: "p1", week: w }); const [ok1] = sanityPass("p1"); if (!ok1) probs.push("p1 " + w);
        for (const s of dash.D.stores) for (const page of ["p2", "p3"]) {
          go({ role: "ROL", page, store: s.id, week: w });
          const [ok] = sanityPass(page); if (!ok) probs.push(`${page} ${s.id} ${w}`);
        }
      }
      go({ role: "ROL", page: "p1", region: "Atlantic", format: "Street-front", cohort: "New" });
      const empty = /No stores match/.test(txt("#kpiCards"));
      const [ok2] = sanityPass("empty");
      return expectAll([[!probs.length, probs.slice(0, 6).join(", ")], [empty && ok2, "empty scope state"]]);
    });
    T("UI-TEXT-01", "No prohibited causal wording anywhere in rendered prompts and explanations", () => {
      const hits = [];
      for (const s of dash.D.stores) for (const w of ["2026-05-25", LATEST]) {
        go({ role: "ROL", page: "p3", store: s.id, week: w });
        const found = dash.L.hasProhibited(txt("#prompts"));
        if (found.length) hits.push(`${s.id} ${w}: ${found}`);
      }
      return expectAll([[!hits.length, hits.slice(0, 4).join(" | ")]]);
    });
  }
  window.__selftestResults = R;
})();
