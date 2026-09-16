/*
 * Node unit and reconciliation tests for build/dashboard_logic.js (Phase E). SYNTHETIC data only.
 * Run:  node --test tests/
 * IDs match issue-register.md (JS-*).
 */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const L = require(path.join(ROOT, "build", "dashboard_logic.js"));
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "analysis_summary.json"), "utf8"));
const idx = L.index(D);
const LATEST = D.weeks[D.weeks.length - 1];
const close = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} vs ${b}`);
const r1 = (v) => Math.round(v * 1000) / 10;

test("JS-AGG-01 network and Atlantic latest-week aggregates match the regression baseline and Python", () => {
  const net = L.aggregate(L.filteredRows(D, idx, "ROL", {}, LATEST));
  assert.equal(net.stores, 30);
  assert.equal(net.exams, 3496);
  assert.equal(net.amber, 2);
  assert.equal(net.red, 0);
  for (const k of ["utilization", "attendance", "conversion", "on_time", "turnaround", "rev_per_exam", "recall_rate"]) close(net[k].v, D.network_week_latest[k]);
  const atl = L.aggregate(L.filteredRows(D, idx, "RRM", {}, LATEST));
  assert.equal(atl.stores, 6);
  assert.equal(atl.exams, 545);
  assert.deepEqual([r1(atl.utilization.v), r1(atl.attendance.v), r1(atl.conversion.v), r1(atl.on_time.v)], [81.0, 94.6, 55.8, 77.3]);
  assert.equal(atl.turnaround.v.toFixed(1), "9.1");
  assert.equal(atl.amber, 0);
  assert.equal(atl.red, 0);
  for (const k of ["utilization", "attendance", "conversion", "on_time", "turnaround"]) close(atl[k].v, D.region_week_latest.Atlantic[k]);
});

test("JS-AGG-02 last-4-week and all-week pooled aggregates reconcile with Python for every region", () => {
  const last4 = D.weeks.slice(-4);
  for (const [rg, py] of Object.entries(D.region_last4)) {
    const rows = last4.flatMap((w) => L.filteredRows(D, idx, "ROL", { region: rg }, w));
    const js = L.aggregate(rows);
    assert.equal(js.exams, py.completed_exams, rg);
    for (const k of ["utilization", "attendance", "conversion", "on_time", "turnaround"]) close(js[k].v, py[k]);
  }
  const all = L.aggregate(D.weeks.flatMap((w) => L.filteredRows(D, idx, "ROL", {}, w)));
  assert.equal(all.red, 4);
  close(all.conversion.v, D.network_all_weeks.conversion);
});

test("JS-AGG-03 prior 4-week comparison is a pooled rate, not an average of weekly rates", () => {
  const rows = L.filteredRows(D, idx, "ROL", {}, LATEST);
  const prior = L.aggregate(L.priorRows(D, idx, rows, LATEST, 4));
  const weekly = D.weeks.slice(-5, -1).map((w) => L.aggregate(L.filteredRows(D, idx, "ROL", {}, w)).conversion.v);
  const avgOfRates = weekly.reduce((a, b) => a + b, 0) / 4;
  let n = 0, d = 0;
  for (const w of D.weeks.slice(-5, -1)) for (const r of L.filteredRows(D, idx, "ROL", {}, w)) if (r.rec.dq !== "Red") { n += r.rec.buy; d += r.rec.done; }
  close(prior.conversion.v, n / d);
  assert.notEqual(prior.conversion.v.toFixed(6), avgOfRates.toFixed(6));
});

test("JS-SCOPE-01 role scope is applied before filters; options never include out-of-scope values", () => {
  assert.deepEqual(L.scopeStores(D, "RRM").map((s) => s.id), ["SYN-025", "SYN-026", "SYN-027", "SYN-028", "SYN-029", "SYN-030"]);
  assert.deepEqual(L.scopeStores(D, "OP").map((s) => s.id), ["SYN-014"]);
  const opts = L.filterOptions(D, idx, "RRM", LATEST);
  assert.deepEqual(opts.region, ["Atlantic"]);
  assert.deepEqual(opts.province, ["NB", "NL", "NS"]);
  assert.equal(L.filteredRows(D, idx, "RRM", { region: "West" }, LATEST).length, 0);
  assert.equal(L.filteredRows(D, idx, "ROL", { region: "Atlantic", format: "Grocery-hosted" }, LATEST).length, 4);
  assert.equal(L.filteredRows(D, idx, "ROL", { dq: "Amber" }, LATEST).length, 2);
  assert.equal(L.filteredRows(D, idx, "ROL", { cohort: "New" }, LATEST).length, 3);
});

test("JS-PEER-01 peer membership reproduced in JS matches Python median, n and basis for every store-week-KPI", () => {
  let checked = 0;
  for (const [sid, list] of Object.entries(D.store_weekly)) {
    for (const rec of list) {
      for (const k of Object.keys(rec.k)) {
        const py = rec.k[k];
        const js = L.peersFor(D, idx, sid, rec.w, k);
        assert.equal(js.basis, py.b, `${sid} ${rec.w} ${k}`);
        assert.equal(js.peers.length, py.n, `${sid} ${rec.w} ${k} n`);
        if (py.m !== null) close(L.quantile(js.peers.map((p) => p.v), 0.5), py.m, 1e-5);
        checked++;
      }
    }
  }
  assert.ok(checked > 5000);
});

test("JS-PEER-02 regional managers never get out-of-region peer names; partners always anonymous", () => {
  const byId = idx.byStore;
  assert.equal(L.peerLabel("RRM", byId["SYN-004"]), "Peer store outside Atlantic");
  assert.equal(L.peerLabel("RRM", byId["SYN-025"]), "SYN-025");
  assert.equal(L.peerLabel("RP", byId["SYN-025"]), "Anonymous peer store");
  assert.equal(L.peerLabel("ROL", byId["SYN-004"]), "SYN-004");
});

test("JS-SUP-01 count display states keep zero, suppressed and not applicable distinct", () => {
  assert.deepEqual(L.countDisplay(null), { state: "not_applicable", text: "n/a" });
  assert.deepEqual(L.countDisplay(0), { state: "zero", text: "0" });
  assert.deepEqual(L.countDisplay(3), { state: "suppressed", text: "<5" });
  assert.equal(L.countDisplay(5).text, "5");
  assert.equal(L.countDisplay(NaN).state, "unavailable");
});

test("JS-SUP-02 rate suppression: small denominator OR suppressed numerator; applied at the displayed aggregation", () => {
  assert.equal(L.rateState(3, 40), "suppressed");
  assert.equal(L.rateState(0, 40), "ok");
  assert.equal(L.rateState(10, 4), "low_volume");
  assert.equal(L.rateState(3, 40, false), "ok");
  const one = L.aggregate([{ id: "SYN-014", rec: idx.get("SYN-014", LATEST) }]);
  assert.equal(one.recallBookings.text, "<5");
  assert.equal(one.recall_rate.s, "suppressed");
  assert.equal(one.recall_rate.v, null);
});

test("JS-SAFE-01..04 empty scopes, zero denominators and non-finite inputs produce explicit states", () => {
  const empty = L.aggregate([]);
  assert.equal(empty.stores, 0);
  assert.equal(empty.utilization.s, "empty");
  assert.equal(empty.exams, null);
  const zero = L.aggregate([{ id: "Z", rec: { dq: "Green", slots: 0, held: 0, done: 0, buy: 0, orders: 0, ontime: 0, turnx: 0, rev: 0, rc: null, rb: null, unres: 0 } }]);
  assert.equal(zero.utilization.s, "low_volume");
  assert.equal(zero.recall_rate.s, "not_applicable");
  const redOnly = L.aggregate([{ id: "SYN-022", rec: idx.get("SYN-022", "2026-05-25") }]);
  assert.equal(redOnly.conversion.s, "red");
  assert.equal(redOnly.red, 1);
  for (const v of [NaN, Infinity, undefined, null]) assert.equal(L.fmtValue("conversion", v), "n/a");
  const t = L.niceTicks(5, 5, { kind: "count", min: 0 });
  assert.ok(t.ticks.every((x) => Number.isFinite(x.v)));
  const c = L.niceTicks(0, 3, { kind: "count", min: 0 });
  assert.ok(c.lo >= 0 && c.ticks.every((x) => x.v >= 0 && !x.label.startsWith("-")));
  assert.equal(L.niceTicks(NaN, 1), null);
});

test("JS-AXIS-01 axis tick labels are unique across realistic ranges", () => {
  const cases = [[0.93, 0.96, "pct"], [0.935, 0.945, "pct"], [0.48, 0.61, "pct"], [5.3, 10, "days"], [0, 3, "count"], [-0.05, 0.02, "delta_pct"], [78, 104, "index"]];
  for (const [lo, hi, kind] of cases) {
    const t = L.niceTicks(lo, hi, { kind, min: kind === "count" ? 0 : undefined });
    const labels = t.ticks.map((x) => x.label);
    assert.equal(new Set(labels).size, labels.length, `${lo}-${hi}: ${labels}`);
    assert.ok(t.lo <= lo + 1e-9 && t.hi >= hi - 1e-9, `${lo}-${hi} extent`);
  }
  const p = L.niceTicks(0.9, 1.0, { kind: "pct", min: 0, max: 1 });
  assert.ok(p.hi <= 1 && p.lo >= 0);
});

test("JS-RANGE-01 missing intervals are reported as actual ranges", () => {
  assert.equal(L.rangesText([3, 4, 5, 9, 11, 12]), "3–5, 9, 11–12");
  assert.deepEqual(L.segments([1, null, 2, 3, undefined, 4]), [[0], [2, 3], [5]]);
  assert.deepEqual(L.segments([[1, 2], [1, null], [3, 4]]), [[0], [2]]);
});

test("JS-CONTRAST-01 text colours in the template meet 4.5:1 on white and on the page background", () => {
  const tpl = fs.readFileSync(path.join(ROOT, "build", "mockup_template.html"), "utf8");
  const vars = {};
  for (const m of tpl.matchAll(/--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})/g)) vars[m[1]] = m[2];
  const textVars = ["ink", "muted", "brand", "text-accent", "text-amber", "text-red", "text-green"];
  for (const v of textVars) {
    assert.ok(vars[v], `missing --${v}`);
    assert.ok(L.contrastRatio(vars[v], "#ffffff") >= 4.5, `--${v} on white ${L.contrastRatio(vars[v], "#ffffff").toFixed(2)}`);
    assert.ok(L.contrastRatio(vars[v], vars.bg) >= 4.5, `--${v} on bg`);
  }
  assert.ok(L.contrastRatio("#b26a00", "#ffffff") < 4.5, "previous amber text colour failed (ISS-22 evidence)");
});

test("JS-STATE-01 URL state round-trips and rejects invalid or out-of-role values", () => {
  const st = L.decodeState("#role=RRM&page=p3&week=2026-07-06&store=SYN-027&format=Grocery-hosted&kpi=turnaround", D);
  assert.equal(st.role, "RRM");
  assert.equal(st.page, "p3");
  assert.equal(st.week, "2026-07-06");
  assert.equal(st.store, "SYN-027");
  assert.equal(st.format, "Grocery-hosted");
  const again = L.decodeState("#" + L.encodeState(st, D), D);
  assert.deepEqual(again, st);
  const bad = L.decodeState("#role=XX&week=1999-01-01&store=NOPE&kpi=bad", D);
  assert.equal(bad.role, "ROL");
  assert.equal(bad.week, LATEST);
  assert.equal(bad.store, "");
  assert.equal(bad.kpi, "conversion");
  assert.equal(L.decodeState("#role=OP&page=p1", D).page, "p3");
});

test("JS-TEXT-01 exception explanations name the rule basis and contain no prohibited causal wording", () => {
  let a = 0, b = 0;
  for (const [sid, list] of Object.entries(D.store_weekly)) {
    const s = idx.byStore[sid];
    for (const rec of list) for (const k of L.EXCEPTION_KPIS) {
      const kr = rec.k[k];
      if (!kr.x) continue;
      const text = L.explainFlag(k, kr, rec.c, s.format);
      assert.deepEqual(L.hasProhibited(text), [], text);
      if (kr.xa) { assert.match(text, /peer/); a++; }
      if (kr.xb) { assert.match(text, /own baseline/); assert.doesNotMatch(text.split("Rule (b)")[1], /peer median/); b++; }
    }
  }
  for (const [stage, [prompt, team]] of Object.entries(D.meta.prompts)) assert.deepEqual(L.hasProhibited(prompt + " " + team), [], stage);
  assert.ok(a > 0 && b > 0);
  assert.deepEqual(L.hasProhibited("This was caused by staffing"), ["caused by"]);
});

test("JS-EXC-01 stage grouping keeps every triggering KPI; exception status separates unavailable comparisons", () => {
  const flags = L.stageFlags(L.filteredRows(D, idx, "ROL", {}, LATEST));
  const f25 = flags.find((f) => f.id === "SYN-025" && f.stage === "Fulfilment");
  assert.deepEqual(f25.items.map((i) => i.k), ["on_time", "turnaround"]);
  assert.equal(L.exceptionStatus(idx.get("SYN-022", "2026-05-25")).status, "data_check");
  assert.equal(L.exceptionStatus(idx.get("SYN-030", LATEST)).status, "partial");
  assert.equal(L.exceptionStatus(idx.get("SYN-005", "2026-05-25")).status, "flagged");
  const rrmFlags = L.stageFlags(L.filteredRows(D, idx, "RRM", {}, LATEST));
  assert.ok(rrmFlags.every((f) => f.store.region === "Atlantic"));
});
