/*
 * Dashboard presentation logic for the SYNTHETIC case-study prototype.
 * Pure functions (no DOM): role scope, filters, ratio-of-sums aggregation, display states,
 * suppression, peer reproduction, axis ticks, URL state and explanation text.
 * Inlined into dashboard-mockup.html by build/build_mockup.py and unit-tested by tests/test_dashboard_logic.js.
 * Store-level KPI values, peer statistics and exception flags are NOT recalculated here: they come from
 * build/kpi_engine.py via data/analysis_summary.json. This module only aggregates selected store-weeks and
 * reproduces peer membership for the anonymous distribution chart (reconciled against Python in tests).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.DashLogic = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const SMALL = 5;
  const FLOOR = 5;
  const isNum = (v) => typeof v === "number" && Number.isFinite(v);

  /* ------------------------------------------------------------------ KPI metadata */
  const KPI = {
    utilization: { label: "Appointment utilization", short: "Utilization", unit: "pct", hib: true, stage: "Booking", help: "utilization", countBased: true },
    attendance: { label: "Attendance rate", short: "Attendance", unit: "pct", hib: true, stage: "Attendance", help: "attendance", countBased: true },
    conversion: { label: "Exam-to-purchase conversion", short: "Conversion", unit: "pct", hib: true, stage: "Conversion", help: "conversion", countBased: true },
    on_time: { label: "On-time fulfilment", short: "On-time", unit: "pct", hib: true, stage: "Fulfilment", help: "on_time", countBased: true },
    turnaround: { label: "Average order turnaround", short: "Turnaround", unit: "days", hib: false, stage: "Fulfilment", help: "turnaround", countBased: false },
    recall_rate: { label: "Recall-booking rate", short: "Recall rate", unit: "pct", hib: true, stage: "Recall", help: "recall_rate", countBased: true },
    rev_per_exam: { label: "Revenue per completed exam", short: "Revenue / exam", unit: "money", hib: true, stage: "Context", help: "rev_per_exam", countBased: false, restricted: true },
    exams: { label: "Completed exams per week (4-week average)", short: "Exams / week", unit: "count", hib: true, stage: "Context", help: "exams", countBased: false },
  };
  const EXCEPTION_KPIS = ["utilization", "attendance", "conversion", "on_time", "turnaround", "recall_rate"];
  const STAGES = ["Booking", "Attendance", "Conversion", "Fulfilment", "Recall"];
  const PROHIBITED = ["caused by", "because", "due to", "driver", "root cause"];

  const ROLES = {
    ROL: { label: "Retail Operations lead (network)", scope: { type: "network" }, revenue: true, pages: ["p1", "p2", "p3"], landing: "p1" },
    RRM: { label: "Regional Retail Manager (Atlantic)", scope: { type: "region", region: "Atlantic" }, revenue: true, pages: ["p1", "p2", "p3"], landing: "p1" },
    RP: { label: "Retail Partner (SYN-014)", scope: { type: "store", store: "SYN-014" }, revenue: true, pages: ["p2", "p3"], landing: "p3" },
    OP: { label: "Optometry Partner (SYN-014)", scope: { type: "store", store: "SYN-014" }, revenue: false, pages: ["p2", "p3"], landing: "p3" },
  };

  /* ------------------------------------------------------------------ formatting and display states */
  function fmtNum(v, d = 0) {
    if (!isNum(v)) return "n/a";
    return v.toLocaleString("en-CA", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmtValue(k, v) {
    if (!isNum(v)) return "n/a";
    const u = KPI[k] ? KPI[k].unit : "count";
    if (u === "pct") return (v * 100).toFixed(1) + "%";
    if (u === "days") return v.toFixed(1) + " days";
    if (u === "money") return "$" + fmtNum(Math.round(v));
    if (u === "index") return v.toFixed(0);
    return fmtNum(v, 0);
  }
  function fmtDelta(k, d) {
    if (!isNum(d)) return "n/a";
    const a = Math.abs(d);
    const u = KPI[k] ? KPI[k].unit : "count";
    const txt = u === "pct" ? `${(a * 100).toFixed(1)} pts` : u === "days" ? `${a.toFixed(1)} days` : u === "money" ? `$${Math.round(a)}` : fmtNum(a, 0);
    if (parseFloat(txt.replace(/[^0-9.]/g, "")) === 0) return `■ no change (${txt})`;  // avoid "▼ $0" when the rounded change is zero
    return `${d > 0 ? "▲" : "▼"} ${txt}`;
  }
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function fmtWeek(iso, withYear = true) {
    if (typeof iso !== "string" || iso.length < 10) return "n/a";
    const m = +iso.slice(5, 7), d = +iso.slice(8, 10);
    return `${MONTHS[m - 1]} ${d}${withYear ? ", " + iso.slice(0, 4) : ""}`;
  }

  /** Count of people or events (PR-04 demonstration rule v0.2). */
  function countDisplay(v) {
    if (v === null || v === undefined) return { state: "not_applicable", text: "n/a" };
    if (!isNum(v)) return { state: "unavailable", text: "n/a" };
    if (v === 0) return { state: "zero", text: "0" };
    if (v > 0 && v < SMALL) return { state: "suppressed", text: "<5" };
    return { state: "value", text: fmtNum(v, 0) };
  }
  /** Rate state: denominator >= 5 and (for count-based numerators) numerator not 1-4. */
  function rateState(n, d, countBased = true) {
    if (!isNum(d)) return "not_applicable";
    if (d < SMALL) return "low_volume";
    if (countBased && isNum(n) && n > 0 && n < SMALL) return "suppressed";
    return "ok";
  }
  const STATE_SHORT = {
    ok: "", red: "Data check required", insufficient_history: "Insufficient history", low_volume: "n/a (low volume)",
    suppressed: "Suppressed (<5)", not_applicable: "Not applicable", restricted: "Restricted for this role",
    peer_suppressed: "Peer group under 5", not_eligible: "Not eligible", unavailable: "Unavailable", empty: "No stores match",
  };

  /* ------------------------------------------------------------------ aggregation (ratio of sums) */
  /** rows: [{id, rec}] store-week records. Red rows are excluded from every measure and counted separately. */
  function aggregate(rows) {
    const all = (rows || []).filter((r) => r && r.rec);
    const use = all.filter((r) => r.rec.dq !== "Red");
    const sum = (f, list = use) => list.reduce((a, r) => a + (isNum(r.rec[f]) ? r.rec[f] : 0), 0);
    const rate = (n, d, cb) => {
      if (!use.length) return { v: null, s: all.length ? "red" : "empty" };
      const s = rateState(n, d, cb);
      return { v: s === "ok" ? n / d : null, s };
    };
    const recallRows = use.filter((r) => r.rec.rc !== null && r.rec.rc !== undefined);
    const rb = sum("rb", recallRows), rc = sum("rc", recallRows);
    let recall;
    if (!use.length) recall = { v: null, s: all.length ? "red" : "empty" };
    else if (!recallRows.length) recall = { v: null, s: "not_applicable" };
    else { const s = rateState(rb, rc, true); recall = { v: s === "ok" ? rb / rc : null, s }; }
    const ids = new Set(all.map((r) => r.id));
    return {
      stores: ids.size,
      storeWeeks: all.length,
      red: all.filter((r) => r.rec.dq === "Red").length,
      amber: all.filter((r) => r.rec.dq === "Amber").length,
      green: all.filter((r) => r.rec.dq === "Green").length,
      exams: use.length ? sum("done") : null,
      examsDisplay: use.length ? countDisplay(sum("done")) : { state: "unavailable", text: "n/a" },
      utilization: rate(sum("held"), sum("slots"), true),
      attendance: rate(sum("done"), sum("held"), true),
      conversion: rate(sum("buy"), sum("done"), true),
      on_time: rate(sum("ontime"), sum("orders"), true),
      turnaround: rate(sum("turnx"), sum("orders"), false),
      rev_per_exam: rate(sum("rev"), sum("done"), false),
      recall_rate: recall,
      recallBookings: recallRows.length ? countDisplay(rb) : countDisplay(null),
      unresolved: use.length ? countDisplay(sum("unres")) : countDisplay(null),
    };
  }

  /* ------------------------------------------------------------------ data access */
  function index(D) {
    const byStore = {};
    for (const s of D.stores) byStore[s.id] = s;
    const rec = {};
    for (const [sid, list] of Object.entries(D.store_weekly)) for (const r of list) rec[sid + "|" + r.w] = r;
    return { byStore, rec, get: (sid, w) => rec[sid + "|" + w] || null };
  }
  /** Rows for the same stores over the n weeks before `week` (for "vs prior 4 weeks": pooled, Red excluded). */
  function priorRows(D, idx, rows, week, n = 4) {
    const out = [];
    for (let i = 1; i <= n; i++) {
      const w = weekOffset(D, week, -i);
      if (!w) continue;
      for (const r of rows) { const rec = idx.get(r.id, w); if (rec) out.push({ id: r.id, store: r.store, rec }); }
    }
    return out;
  }
  function weekOffset(D, w, n) {
    const i = D.weeks.indexOf(w);
    if (i < 0) return null;
    const j = i + n;
    return j >= 0 && j < D.weeks.length ? D.weeks[j] : null;
  }

  /* ------------------------------------------------------------------ role scope and filters */
  function scopeStores(D, role) {
    const r = ROLES[role] || ROLES.ROL;
    if (r.scope.type === "store") return D.stores.filter((s) => s.id === r.scope.store);
    if (r.scope.type === "region") return D.stores.filter((s) => s.region === r.scope.region);
    return D.stores.slice();
  }
  const FILTER_KEYS = ["region", "province", "format", "banner", "cohort", "dq"];
  /** Role scope is applied first, then filters. Cohort and data-quality filters are as at the selected week. */
  function filteredRows(D, idx, role, filters, week) {
    const out = [];
    for (const s of scopeStores(D, role)) {
      const rec = idx.get(s.id, week);
      if (!rec) continue;
      if (filters.region && s.region !== filters.region) continue;
      if (filters.province && s.province !== filters.province) continue;
      if (filters.format && s.format !== filters.format) continue;
      if (filters.banner && s.banner !== filters.banner) continue;
      if (filters.cohort && rec.c !== filters.cohort) continue;
      if (filters.dq && rec.dq !== filters.dq) continue;
      out.push({ id: s.id, store: s, rec });
    }
    return out;
  }
  function filterOptions(D, idx, role, week) {
    const scoped = scopeStores(D, role);
    const uniq = (f) => [...new Set(f)].sort();
    return {
      region: uniq(scoped.map((s) => s.region)),
      province: uniq(scoped.map((s) => s.province)),
      format: uniq(scoped.map((s) => s.format)),
      banner: uniq(scoped.map((s) => s.banner)),
      cohort: ["New", "Developing", "Mature"].filter((c) => scoped.some((s) => (idx.get(s.id, week) || {}).c === c)),
      dq: ["Green", "Amber", "Red"],
    };
  }
  function canSeeRevenue(role) { return !!(ROLES[role] || {}).revenue; }
  /** Peer naming policy: ROL named; RRM named only inside own region; partners anonymous. */
  function peerLabel(role, peerStore, focalRegion) {
    const r = ROLES[role] || ROLES.ROL;
    if (role === "ROL") return peerStore.id;
    if (r.scope.type === "region") return peerStore.region === r.scope.region ? peerStore.id : `Peer store outside ${r.scope.region}`;
    return "Anonymous peer store";
  }

  /* ------------------------------------------------------------------ peers (reproduces kpi_engine.choose_peers) */
  function quantile(values, q) {
    const v = values.slice().sort((a, b) => a - b);
    if (!v.length) return null;
    const pos = (v.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
    return v[lo] + (v[hi] - v[lo]) * (pos - lo);
  }
  function peersFor(D, idx, sid, week, k) {
    const focal = idx.get(sid, week), fs = idx.byStore[sid];
    if (!focal || !fs || focal.c === "Unclassified") return { basis: "suppressed", peers: [], nf: 0, nc: 0 };
    const pool = [];
    for (const s of D.stores) {
      if (s.id === sid) continue;
      const r = idx.get(s.id, week);
      if (!r || r.c !== focal.c || !r.k[k] || !isNum(r.k[k].v)) continue;
      pool.push({ id: s.id, store: s, v: r.k[k].v });
    }
    const fmt = pool.filter((p) => p.store.format === fs.format);
    if (fmt.length >= FLOOR) return { basis: "cohort x format", peers: fmt, nf: fmt.length, nc: pool.length };
    if (pool.length >= FLOOR) return { basis: "cohort (fallback)", peers: pool, nf: fmt.length, nc: pool.length };
    return { basis: "suppressed", peers: [], nf: fmt.length, nc: pool.length };
  }
  function basisText(kr, cohort, format) {
    if (!kr || !kr.b) return "Peer comparison not available";
    if (kr.b === "cohort x format") return `${cohort} · ${format} · n = ${kr.n}`;
    if (kr.b === "cohort (fallback)") return `All ${cohort} stores · n = ${kr.n} (fallback)`;
    return `Peer comparison not available: ${kr.nc} ${cohort} peer${kr.nc === 1 ? "" : "s"} with a reportable value (minimum 5)`;
  }

  /* ------------------------------------------------------------------ exceptions and explanations */
  function stageFlags(rows) {
    const out = [];
    for (const { id, store, rec } of rows) {
      const by = {};
      for (const k of EXCEPTION_KPIS) {
        const kr = rec.k[k];
        if (kr && kr.x) (by[KPI[k].stage] = by[KPI[k].stage] || []).push({ k, rule: kr.xa && kr.xb ? "a+b" : kr.xa ? "a" : "b", run: kr.xr });
      }
      for (const st of STAGES) if (by[st]) out.push({ id, store, rec, stage: st, items: by[st], stageRun: (rec.sr || {})[st] || by[st].length && Math.max(...by[st].map((i) => i.run)) });
    }
    return out;
  }
  /** Per store-week summary: flagged / no triggered exception / comparison unavailable (with reasons) / data check. */
  function exceptionStatus(rec) {
    if (!rec) return { status: "no_data", reasons: [] };
    if (rec.dq === "Red") return { status: "data_check", reasons: ["Data quality Red: performance KPIs withheld"] };
    const flagged = EXCEPTION_KPIS.filter((k) => rec.k[k] && rec.k[k].x);
    const unavailable = EXCEPTION_KPIS.filter((k) => rec.k[k] && rec.k[k].es === "unavailable");
    const partial = EXCEPTION_KPIS.filter((k) => rec.k[k] && rec.k[k].es === "no_flag_own_baseline_only");
    const reasons = [];
    for (const k of unavailable) reasons.push(`${KPI[k].short}: ${STATE_SHORT[rec.k[k].s] || "own and peer comparisons unavailable"}`);
    for (const k of partial) reasons.push(`${KPI[k].short}: peer comparison unavailable (own-baseline rule only)`);
    if (flagged.length) return { status: "flagged", flagged, reasons };
    if (unavailable.length || partial.length) return { status: "partial", flagged, reasons };
    return { status: "none", flagged, reasons };
  }
  function explainFlag(k, kr, cohort, format) {
    const parts = [];
    if (kr.xa) {
      const q = KPI[k].hib ? "25th percentile" : "75th percentile";
      const qv = KPI[k].hib ? kr.q1 : kr.q3;
      parts.push(`Rule (a), peer comparison: 4-week value ${fmtValue(k, kr.v)} is beyond the peer ${q} (${fmtValue(k, qv)}) and at least 10% ${KPI[k].hib ? "below" : "above"} the peer median ${fmtValue(k, kr.m)} (${basisText(kr, cohort, format)}).`);
    }
    if (kr.xb) {
      parts.push(`Rule (b), own trend: 4-week value ${fmtValue(k, kr.v)} is ${Math.abs((kr.ch || 0) * 100).toFixed(0)}% ${KPI[k].hib ? "below" : "above"} this store's own baseline ${fmtValue(k, kr.bs)} (the 8 weeks before the window), for ${kr.br} consecutive weeks (rule needs 3).`);
    }
    parts.push(`Flagged ${kr.xr} consecutive week${kr.xr === 1 ? "" : "s"} for this KPI.`);
    return parts.join(" ");
  }
  function hasProhibited(text) {
    const t = String(text).toLowerCase();
    return PROHIBITED.filter((p) => new RegExp("\\b" + p.replace(/ /g, "\\s+") + "\\b").test(t));
  }

  /* ------------------------------------------------------------------ chart helpers */
  /** Nice axis ticks with unique labels. kind: pct | days | count | index | money | delta_pct | delta_days */
  function niceTicks(lo, hi, opts = {}) {
    const target = opts.count || 4;
    if (!isNum(lo) || !isNum(hi)) return null;
    if (hi < lo) [lo, hi] = [hi, lo];
    if (hi === lo) { const pad = Math.abs(hi) * 0.05 || (opts.kind === "pct" ? 0.01 : 1); lo -= pad; hi += pad; }
    const pad = (hi - lo) * 0.06;
    lo -= pad; hi += pad;
    if (isNum(opts.min)) lo = Math.max(lo, opts.min);
    if (isNum(opts.max)) hi = Math.min(hi, opts.max);
    const raw = (hi - lo) / target;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => s >= raw) || 10 * mag;
    const start = Math.floor(lo / step + 1e-9) * step, end = Math.ceil(hi / step - 1e-9) * step;
    let nLo = isNum(opts.min) ? Math.max(start, opts.min) : start;
    let nHi = isNum(opts.max) ? Math.min(end, opts.max) : end;
    const ticks = [];
    for (let v = nLo, i = 0; v <= nHi + step * 1e-6 && i < 50; v = nLo + step * ++i) ticks.push(+v.toFixed(12));
    const scale = opts.kind === "pct" || opts.kind === "delta_pct" ? 100 : 1;
    let dec = Math.max(0, -Math.floor(Math.log10(step * scale) + 1e-9));
    if ((step * scale) % 1 !== 0 && dec === 0) dec = 1;
    const label = (v, d) => {
      const x = v * scale;
      const s = (Math.abs(x) < 1e-9 ? 0 : x).toFixed(d);
      if (opts.kind === "pct") return s + "%";
      if (opts.kind === "delta_pct") return (x > 0 ? "+" : "") + s + " pts";
      if (opts.kind === "money") return "$" + s;
      if (opts.kind === "delta_days") return (x > 0 ? "+" : "") + s;
      return s;
    };
    let labels = ticks.map((v) => label(v, dec));
    while (new Set(labels).size < labels.length && dec < 6) { dec++; labels = ticks.map((v) => label(v, dec)); }
    return { lo: nLo, hi: nHi, step, ticks: ticks.map((v, i) => ({ v, label: labels[i] })) };
  }
  function toRanges(nums) {
    const v = [...new Set(nums.filter(isNum))].sort((a, b) => a - b);
    const out = [];
    for (const x of v) {
      if (out.length && x === out[out.length - 1][1] + 1) out[out.length - 1][1] = x;
      else out.push([x, x]);
    }
    return out;
  }
  function rangesText(nums, fmt = (x) => String(x)) {
    return toRanges(nums).map(([a, b]) => (a === b ? fmt(a) : `${fmt(a)}–${fmt(b)}`)).join(", ");
  }
  /** Split a series into contiguous segments of non-null points (for bands and lines that must not bridge gaps). */
  function segments(values) {
    const segs = [];
    let cur = [];
    values.forEach((v, i) => {
      if (v === null || v === undefined || (Array.isArray(v) ? v.some((x) => !isNum(x)) : !isNum(v))) { if (cur.length) segs.push(cur); cur = []; }
      else cur.push(i);
    });
    if (cur.length) segs.push(cur);
    return segs;
  }
  function luminance(hex) {
    const c = hex.replace("#", "");
    const ch = [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16) / 255).map((x) => (x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)));
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
  }
  function contrastRatio(a, b) {
    const [l1, l2] = [luminance(a), luminance(b)].sort((x, y) => y - x);
    return (l1 + 0.05) / (l2 + 0.05);
  }

  /* ------------------------------------------------------------------ URL state */
  const DEFAULT_STATE = { role: "ROL", page: null, week: null, region: "", province: "", format: "", banner: "", cohort: "", dq: "", store: "", kpi: "conversion", trend: "conversion", map: "turnaround" };
  function encodeState(st, D) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(st)) {
      if (v === null || v === undefined || v === "") continue;
      if (k === "week" && D && v === D.weeks[D.weeks.length - 1]) continue;
      if (DEFAULT_STATE[k] === v && k !== "page") continue;
      p.set(k, v);
    }
    return p.toString();
  }
  function decodeState(hash, D) {
    const p = new URLSearchParams(String(hash || "").replace(/^#/, ""));
    const st = Object.assign({}, DEFAULT_STATE);
    const role = p.get("role");
    if (role && ROLES[role]) st.role = role;
    const week = p.get("week");
    st.week = week && D.weeks.includes(week) ? week : D.weeks[D.weeks.length - 1];
    const page = p.get("page");
    st.page = ROLES[st.role].pages.includes(page) ? page : ROLES[st.role].landing;
    for (const k of FILTER_KEYS) if (p.get(k)) st[k] = p.get(k);
    const store = p.get("store");
    if (store && D.stores.some((s) => s.id === store)) st.store = store;
    for (const k of ["kpi", "trend", "map"]) if (p.get(k) && KPI[p.get(k)]) st[k] = p.get(k);
    return st;
  }

  return {
    SMALL, FLOOR, KPI, EXCEPTION_KPIS, STAGES, ROLES, PROHIBITED, STATE_SHORT, FILTER_KEYS, DEFAULT_STATE,
    isNum, fmtNum, fmtValue, fmtDelta, fmtWeek, countDisplay, rateState, aggregate, index, weekOffset, priorRows,
    scopeStores, filteredRows, filterOptions, canSeeRevenue, peerLabel, quantile, peersFor, basisText,
    stageFlags, exceptionStatus, explainFlag, hasProhibited, niceTicks, toRanges, rangesText, segments,
    luminance, contrastRatio, encodeState, decodeState,
  };
});
