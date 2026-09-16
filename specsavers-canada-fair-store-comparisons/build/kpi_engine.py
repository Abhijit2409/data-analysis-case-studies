"""
KPI calculation engine for the SYNTHETIC case-study prototype (Phases 6, 12 and 13).

This module is the single authoritative implementation of the prototype's calculation rules:
rolling windows, data-quality withholding, small-count suppression, peer groups, exception rules
and the ramp index. `validate_and_analyze.py` calls it to produce the dashboard data, and
`tests/test_calculations.py` tests it directly. All outputs are synthetic and unrelated to
actual Specsavers performance.

Rule summary (documented in phase-06-kpi-dictionary.md, "Calculation conventions v0.2"):
  * Window: the 4 calendar weeks ending at the selected week. Weeks with no row (store not open)
    or with Red data quality are not usable. At least 3 usable weeks are required, and the selected
    week itself must be usable; otherwise the value is unavailable with a stated reason.
  * Rates are ratios of sums over usable weeks (never averages of weekly ratios).
  * Small counts (demonstration rule v0.2): a count of 1-4 is shown as "<5"; a rate is shown only when
    its denominator is at least 5 AND, for count-based numerators, the numerator is not 1-4.
    Zero, unavailable, suppressed and not-applicable are distinct states.
  * Peers: other stores in the same week with a reportable value, same maturity cohort and format;
    fall back to the cohort across formats; suppress if still under 5 stores.
  * Exceptions (rule set v0.2): rule (a) peer-based, rule (b) own-baseline for 3 consecutive weeks,
    recall only for Developing/Mature stores with 40+ contacts; any unavailable week breaks a run.
  * Ramp index: same-age peers; trigger when below 80 for 4 consecutive weeks with an available index.
"""
import math

import numpy as np
import pandas as pd

VERSIONS = {"kpi_dictionary": "v0.2", "exception_rules": "v0.2", "prompt_library": "v0.2", "cohort_bands": "v0.1"}

PEER_FLOOR = 5            # PR-03 (illustrative; set by SH-13)
SMALL_COUNT = 5           # PR-04 demonstration rule v0.2 (illustrative)
WINDOW_WEEKS = 4          # A-22
MIN_USABLE_WEEKS = 3
BASELINE_WEEKS = 8        # rule (b): the 8 weeks immediately before the 4-week window
BASELINE_MIN_USABLE = 6
RULE_A_MARGIN = 0.10
RULE_B_CHANGE = 0.15
RULE_B_RUN = 3
RECALL_MIN_CONTACTS = 40
RAMP_MIN_AGE = 3          # KPI-10: first 3 weeks after opening are n/a
RAMP_MAX_AGE = 104
RAMP_THRESHOLD = 80.0
RAMP_RUN = 4
COHORT_BANDS = [("New", 0, 26), ("Developing", 27, 104), ("Mature", 105, None)]

# key: numerator, denominator, higher-is-better, count-based numerator, journey stage, exception KPI
KPIS = {
    "utilization": ("held", "available_appointment_slots", True, True, "Booking", True),
    "attendance": ("completed_exams", "held", True, True, "Attendance", True),
    "conversion": ("purchasing_customers", "completed_exams", True, True, "Conversion", True),
    "on_time": ("orders_ready_on_time", "orders_placed", True, True, "Fulfilment", True),
    "turnaround": ("turn_x_orders", "orders_placed", False, False, "Fulfilment", True),
    "recall_rate": ("recall_bookings", "recall_contacts", True, True, "Recall", True),
    "rev_per_exam": ("eyewear_revenue", "completed_exams", True, False, "Context", False),
}
EXCEPTION_KPIS = [k for k, v in KPIS.items() if v[5]]
PEER_KPIS = list(KPIS) + ["exams"]
STAGE = {k: v[4] for k, v in KPIS.items()}

STATE_TEXT = {
    "ok": "Available",
    "red": "Data check required: data quality Red in the selected week",
    "insufficient_history": "Unavailable: fewer than 3 usable weeks in the 4-week window",
    "low_volume": "n/a (low volume): denominator under 5",
    "suppressed": "Suppressed: numerator under 5",
    "not_applicable": "Not applicable: no recall programme in the selected week",
}


# ---------------------------------------------------------------------------------------------- basics
def cohort_for(weeks_since_opening):
    if weeks_since_opening is None or (isinstance(weeks_since_opening, float) and math.isnan(weeks_since_opening)):
        return "Unclassified"
    for name, lo, hi in COHORT_BANDS:
        if weeks_since_opening >= lo and (hi is None or weeks_since_opening <= hi):
            return name
    return "Unclassified"


def dq_status(completeness, refresh):
    """FR-08 / KPI-11 / KPI-12 thresholds (illustrative)."""
    completeness = pd.Series(completeness, dtype=float)
    refresh = pd.Series(refresh, dtype=object)
    red = (completeness < 90) | (refresh == "Stale")
    amber = (completeness < 98) | (refresh == "Delayed")
    return pd.Series(np.where(red, "Red", np.where(amber, "Amber", "Green")), index=completeness.index)


def count_display(v):
    """Display state for a count of people or events (PR-04 demonstration rule v0.2)."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "not_applicable", None
    if v == 0:
        return "zero", 0
    if 0 < v < SMALL_COUNT:
        return "suppressed", "<5"
    return "value", int(v)


def rate_state(numerator, denominator, count_based=True):
    """State of a rate for display, before data-quality and history checks."""
    if denominator is None or (isinstance(denominator, float) and math.isnan(denominator)):
        return "not_applicable"
    if denominator < SMALL_COUNT:
        return "low_volume"
    if count_based and numerator is not None and 0 < numerator < SMALL_COUNT:
        return "suppressed"
    return "ok"


def load(path):
    df = pd.read_csv(path, parse_dates=["week_start", "opening_date"])
    return df.sort_values(["store_id", "week_start"]).reset_index(drop=True)


def derive(df):
    df = df.copy()
    df["held"] = df["booked_appointments"] - df["cancelled_appointments"]
    df["unresolved"] = df["booked_appointments"] - df["completed_exams"] - df["cancelled_appointments"] - df["no_show_appointments"]
    df["dq_status"] = dq_status(df["data_completeness_pct"].values, df["data_refresh_status"].values).values
    # KPI-07 synthetic simplification: every order placed reaches "ready", so the order-weighted
    # turnaround uses orders placed as the denominator. Not production-correct (see Phase 6 KPI-07).
    df["turn_x_orders"] = df["average_turnaround_days"] * df["orders_placed"]
    return df


# ---------------------------------------------------------------------------------------------- helpers
def _calendar(df):
    # Contiguous weekly calendar from the first to the last week, so a week missing for every store still counts
    # as a calendar week inside a window (it is simply not usable).
    weeks = list(pd.date_range(df["week_start"].min(), df["week_start"].max(), freq="7D"))
    stores = sorted(df["store_id"].unique())
    idx = pd.MultiIndex.from_product([stores, weeks], names=["store_id", "week_start"])
    cal = df.set_index(["store_id", "week_start"]).reindex(idx)
    cal["present"] = cal["store_name"].notna()
    return cal, weeks


def _roll(series, window, shift=0):
    """Calendar-week rolling sum per store; NaN when no usable value in the window."""
    return series.groupby(level=0, group_keys=False).transform(
        lambda s: s.shift(shift).rolling(window, min_periods=1).sum())


def _run_length(cond):
    """Consecutive calendar weeks (ending at each week) where cond is True, per store."""
    def f(s):
        out, r = np.zeros(len(s), dtype=int), 0
        for i, v in enumerate(s.values):
            r = r + 1 if bool(v) else 0
            out[i] = r
        return pd.Series(out, index=s.index)
    return cond.groupby(level=0, group_keys=False).apply(f)


def quantile_linear(values, q):
    """Linear-interpolation quantile (same as pandas default and dashboard_logic.js)."""
    v = sorted(values)
    if not v:
        return None
    pos = (len(v) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


def peer_stats(candidates):
    """candidates: list of (store_id, value, cohort, format) excluding the focal store; returns dict."""
    return {"median": quantile_linear([c[1] for c in candidates], 0.5),
            "p25": quantile_linear([c[1] for c in candidates], 0.25),
            "p75": quantile_linear([c[1] for c in candidates], 0.75)}


def choose_peers(focal_id, cohort, fmt, pool):
    """pool: list of (store_id, value, cohort, format) with reportable values. Returns (basis, list, n_format, n_cohort)."""
    if cohort == "Unclassified":
        return "suppressed", [], 0, 0
    same_cohort = [p for p in pool if p[0] != focal_id and p[2] == cohort]
    same_format = [p for p in same_cohort if p[3] == fmt]
    if len(same_format) >= PEER_FLOOR:
        return "cohort x format", same_format, len(same_format), len(same_cohort)
    if len(same_cohort) >= PEER_FLOOR:
        return "cohort (fallback)", same_cohort, len(same_format), len(same_cohort)
    return "suppressed", [], len(same_format), len(same_cohort)


# ---------------------------------------------------------------------------------------------- engine
def compute(df):
    """Run every calculation. Returns (store_week DataFrame, ramp DataFrame, weeks)."""
    cal, weeks = _calendar(df)
    present = cal["present"]
    usable = present & (cal["dq_status"] != "Red")
    selected_red = present & (cal["dq_status"] == "Red")
    amber_in_window = _roll((present & (cal["dq_status"] == "Amber")).astype(float), WINDOW_WEEKS) > 0

    c = {}  # column name -> Series (assembled once at the end to avoid frame fragmentation)
    c["present"] = present
    c["selected_red"] = selected_red
    c["provisional"] = amber_in_window & present & ~selected_red

    for k, (num_c, den_c, hib, count_num, stage, is_exc) in KPIS.items():
        u = usable & cal[den_c].notna() if k == "recall_rate" else usable
        num = cal[num_c].where(u)
        den = cal[den_c].where(u)
        n4, d4 = _roll(num, WINDOW_WEEKS), _roll(den, WINDOW_WEEKS)
        uw = _roll(u.astype(float), WINDOW_WEEKS)
        with np.errstate(divide="ignore", invalid="ignore"):
            raw = (n4 / d4).where(d4 > 0)
        state = pd.Series("ok", index=cal.index, dtype=object)
        state[(d4.fillna(0) < SMALL_COUNT)] = "low_volume"
        if count_num:
            state[(n4 >= 1) & (n4 <= SMALL_COUNT - 1) & (d4 >= SMALL_COUNT)] = "suppressed"
        state[uw < MIN_USABLE_WEEKS] = "insufficient_history"
        if k == "recall_rate":
            state[present & ~selected_red & cal[den_c].isna()] = "not_applicable"
        state[selected_red] = "red"
        state[~present] = None
        c[f"{k}_n4"], c[f"{k}_d4"], c[f"{k}_weeks"] = n4, d4, uw
        c[f"{k}_state"] = state
        c[f"{k}_r4"] = raw.where(state == "ok")

        bn, bd = _roll(num, BASELINE_WEEKS, WINDOW_WEEKS), _roll(den, BASELINE_WEEKS, WINDOW_WEEKS)
        buw = _roll(u.astype(float), BASELINE_WEEKS, WINDOW_WEEKS)
        base_ok = (buw >= BASELINE_MIN_USABLE) & (bd >= SMALL_COUNT)
        if count_num:
            base_ok &= ~((bn >= 1) & (bn <= SMALL_COUNT - 1))
        with np.errstate(divide="ignore", invalid="ignore"):
            c[f"{k}_base8"] = (bn / bd).where(base_ok)

    # KPI-04 context: 4-week average completed exams per usable week (also the ramp-index input)
    ex = cal["completed_exams"].where(usable)
    en4, euw = _roll(ex, WINDOW_WEEKS), _roll(usable.astype(float), WINDOW_WEEKS)
    ex_state = pd.Series("ok", index=cal.index, dtype=object)
    ex_state[euw < MIN_USABLE_WEEKS] = "insufficient_history"
    ex_state[selected_red] = "red"
    ex_state[~present] = None
    c["exams_n4"], c["exams_weeks"], c["exams_state"] = en4, euw, ex_state
    c["exams_r4"] = (en4 / euw).where(ex_state == "ok")

    # ------------------------------------------------------------------ peers (FR-04, FR-16, PR-03)
    meta = cal[["maturity_cohort", "store_format", "region"]]
    rows = []
    for wk in weeks:
        wk_index = [(sid, wk) for sid in cal.index.get_level_values(0).unique() if present.loc[(sid, wk)]]
        for k in PEER_KPIS:
            pool = [(sid, c[f"{k}_r4"].at[(sid, wk)], meta.at[(sid, wk), "maturity_cohort"], meta.at[(sid, wk), "store_format"])
                    for sid, _ in wk_index if not pd.isna(c[f"{k}_r4"].at[(sid, wk)])]
            for sid, _ in wk_index:
                basis, peers, nf, nc = choose_peers(sid, meta.at[(sid, wk), "maturity_cohort"], meta.at[(sid, wk), "store_format"], pool)
                stats = peer_stats(peers) if peers else {"median": None, "p25": None, "p75": None}
                rows.append((sid, wk, k, stats["median"], stats["p25"], stats["p75"], len(peers), basis, nf, nc))
    peer = pd.DataFrame(rows, columns=["store_id", "week_start", "kpi", "median", "p25", "p75", "n", "basis", "n_format", "n_cohort"])
    for k in PEER_KPIS:
        sub = peer[peer["kpi"] == k].set_index(["store_id", "week_start"])
        for col in ["median", "p25", "p75", "n", "basis", "n_format", "n_cohort"]:
            c[f"{k}_peer_{col}"] = sub[col].reindex(cal.index)

    # ------------------------------------------------------------------ exceptions (FR-06, rule set v0.2)
    cohort = meta["maturity_cohort"]
    for k in EXCEPTION_KPIS:
        hib = KPIS[k][2]
        v, med, p25, p75, base = c[f"{k}_r4"], c[f"{k}_peer_median"].astype(float), c[f"{k}_peer_p25"].astype(float), c[f"{k}_peer_p75"].astype(float), c[f"{k}_base8"]
        value_ok = v.notna()
        peer_ok = c[f"{k}_peer_basis"].isin(["cohort x format", "cohort (fallback)"])
        eligible = pd.Series(True, index=cal.index)
        if k == "recall_rate":
            eligible = (cohort != "New") & (c["recall_rate_d4"] >= RECALL_MIN_CONTACTS)
        a_eval = value_ok & peer_ok & eligible
        b_eval = value_ok & base.notna() & eligible
        with np.errstate(divide="ignore", invalid="ignore"):
            if hib:
                a = a_eval & (v < p25) & (v <= (1 - RULE_A_MARGIN) * med)
                cond_b = b_eval & ((v - base) / base <= -RULE_B_CHANGE)
            else:
                a = a_eval & (v > p75) & (v >= (1 + RULE_A_MARGIN) * med)
                cond_b = b_eval & ((v - base) / base >= RULE_B_CHANGE)
            c[f"{k}_change"] = ((v - base) / base).where(b_eval)
        cond_b = cond_b.fillna(False).astype(bool)
        b_run = _run_length(cond_b)
        b = b_run >= RULE_B_RUN
        flag = (a.fillna(False).astype(bool) | b) & present
        c[f"{k}_a_eval"], c[f"{k}_b_eval"] = a_eval, b_eval
        c[f"{k}_rule_a"], c[f"{k}_rule_b"] = a.fillna(False).astype(bool) & present, b & present
        c[f"{k}_b_run"] = b_run
        c[f"{k}_flag"] = flag
        c[f"{k}_flag_run"] = _run_length(flag)
        # Order matters: flagged, then withheld (Red), then not eligible, then neither rule evaluable, then peer rule unavailable.
        state = np.select([~present, flag, selected_red, ~eligible, ~(a_eval | b_eval), ~a_eval],
                          [None, "flag", "unavailable", "not_eligible", "unavailable", "no_flag_own_baseline_only"], default="no_flag")
        c[f"{k}_exc_state"] = pd.Series(state, index=cal.index, dtype=object)

    for stage in sorted(set(STAGE[k] for k in EXCEPTION_KPIS)):
        ks = [k for k in EXCEPTION_KPIS if STAGE[k] == stage]
        any_flag = pd.concat([c[f"{k}_flag"] for k in ks], axis=1).any(axis=1)
        c[f"stage_{stage}_run"] = _run_length(any_flag)

    # ------------------------------------------------------------------ ramp index (KPI-10)
    age = cal["weeks_since_opening"]
    fmt = cal["store_format"]
    ramp_pool = [(sid, int(age.loc[(sid, wk)]), c["exams_r4"].at[(sid, wk)], fmt.loc[(sid, wk)])
                 for sid, wk in cal.index if present.loc[(sid, wk)] and RAMP_MIN_AGE <= age.loc[(sid, wk)] <= RAMP_MAX_AGE
                 and not pd.isna(c["exams_r4"].at[(sid, wk)])]
    ramp_rows = []
    for sid, wk in cal.index:
        if not present.loc[(sid, wk)]:
            ramp_rows.append((sid, wk, None, None, None, None, None, 0, None, None))
            continue
        a_ = int(age.loc[(sid, wk)])
        f_ = fmt.loc[(sid, wk)]
        if a_ > RAMP_MAX_AGE:
            ramp_rows.append((sid, wk, a_, None, None, None, None, 0, "not_eligible", None))
            continue
        at_age = [p for p in ramp_pool if p[1] == a_ and p[0] != sid]
        same = [p for p in at_age if p[3] == f_]
        if len(same) >= PEER_FLOOR:
            use, basis = same, "same format"
        elif len(at_age) >= PEER_FLOOR:
            use, basis = at_age, "all formats (fallback)"
        else:
            use, basis = [], "suppressed"
        vals = [p[2] for p in use]
        med = quantile_linear(vals, 0.5) if vals else None
        p25 = quantile_linear(vals, 0.25) if vals else None
        p75 = quantile_linear(vals, 0.75) if vals else None
        store_v = c["exams_r4"].at[(sid, wk)]
        if selected_red.loc[(sid, wk)]:
            st, idx_ = "red", None
        elif a_ < RAMP_MIN_AGE or pd.isna(store_v):
            st, idx_ = "insufficient_history", None
        elif med is None:
            st, idx_ = "peer_suppressed", None
        else:
            st, idx_ = "ok", 100.0 * store_v / med
        ramp_rows.append((sid, wk, a_, med, p25, p75, idx_, len(use) if use else len(at_age), st, basis))
    ramp = pd.DataFrame(ramp_rows, columns=["store_id", "week_start", "age", "peer_median", "peer_p25", "peer_p75", "ramp_index", "peer_n", "ramp_state", "ramp_basis"]).set_index(["store_id", "week_start"])
    for col in ramp.columns:
        c[f"ramp_{col}" if not col.startswith("ramp_") else col] = ramp[col]
    below = (c["ramp_state"] == "ok") & (c["ramp_index"].astype(float) < RAMP_THRESHOLD)
    c["ramp_below_run"] = _run_length(below.fillna(False))
    c["ramp_flag"] = c["ramp_below_run"] >= RAMP_RUN

    out = pd.concat(c, axis=1)
    joined = cal.join(out.drop(columns=["present"]))
    joined = joined[joined["present"]].reset_index()
    return joined, weeks


# ---------------------------------------------------------------------------------------------- aggregates
def get_row(sw, store_id, week):
    """Return the computed store-week row (a Series) or None if the store has no row that week."""
    m = sw[(sw["store_id"] == store_id) & (sw["week_start"] == pd.Timestamp(week))]
    return None if m.empty else m.iloc[0]


def pooled(frame):
    """Ratio-of-sums aggregate for a set of store-week rows (Red rows excluded from measures).

    Mirrors aggregate() in dashboard_logic.js. Returns None for unavailable rates (zero or small
    denominators, suppressed numerators) rather than 0 or NaN.
    """
    f = frame[frame["dq_status"] != "Red"]

    def ratio(n, d, count_num=True):
        n, d = float(f[n].sum()), float(f[d].sum())
        st = rate_state(n, d, count_num) if len(f) else "not_applicable"
        return (n / d) if st == "ok" else None

    rc = f["recall_contacts"].dropna()
    rb = f.loc[rc.index, "recall_bookings"] if len(rc) else rc
    recall = None
    if len(rc) and rate_state(float(rb.sum()), float(rc.sum()), True) == "ok":
        recall = float(rb.sum()) / float(rc.sum())
    return {
        "stores": int(frame["store_id"].nunique()),
        "store_weeks": int(len(frame)),
        "excluded_red_store_weeks": int((frame["dq_status"] == "Red").sum()),
        "amber_store_weeks": int((frame["dq_status"] == "Amber").sum()),
        "completed_exams": int(f["completed_exams"].sum()),
        "utilization": ratio("held", "available_appointment_slots"),
        "attendance": ratio("completed_exams", "held"),
        "conversion": ratio("purchasing_customers", "completed_exams"),
        "rev_per_exam": ratio("eyewear_revenue", "completed_exams", False),
        "on_time": ratio("orders_ready_on_time", "orders_placed"),
        "turnaround": ratio("turn_x_orders", "orders_placed", False),
        "recall_rate": recall,
        "exams_per_store_week": (float(f["completed_exams"].sum()) / len(f)) if len(f) else None,
    }


def stage_flags(sw, week=None):
    """Stage-grouped flags: one row per store-week-stage listing every triggering KPI and its rules."""
    rows = []
    frame = sw if week is None else sw[sw["week_start"] == pd.Timestamp(week)]
    for _, r in frame.iterrows():
        sid, wk = r["store_id"], r["week_start"]
        by_stage = {}
        for k in EXCEPTION_KPIS:
            if r[f"{k}_flag"]:
                rules = ("a+b" if r[f"{k}_rule_a"] and r[f"{k}_rule_b"] else ("a" if r[f"{k}_rule_a"] else "b"))
                by_stage.setdefault(STAGE[k], []).append((k, rules, int(r[f"{k}_flag_run"])))
        for stage, items in by_stage.items():
            rows.append({"week_start": pd.Timestamp(wk).date().isoformat(), "store_id": sid, "stage": stage,
                         "kpis": [i[0] for i in items], "rules": {i[0]: i[1] for i in items},
                         "kpi_runs": {i[0]: i[2] for i in items}, "stage_run": int(r[f"stage_{stage}_run"]),
                         "dq_status": r["dq_status"]})
    return rows


# ---------------------------------------------------------------------------------------------- KPI help (FR-07)
KPI_HELP = {
    "capacity": {"id": "KPI-01", "name": "Available appointment capacity", "units": "slots per week",
                 "formula": "Σ bookable examination slots in the week", "owner": "Retail Operations (proposed)",
                 "exclusions": "Blocked non-exam slots; non-exam appointment types; closed days.",
                 "limitations": "Context and denominator only; not a productivity measure."},
    "utilization": {"id": "KPI-02", "name": "Appointment utilization", "units": "%",
                    "formula": "Held appointments ÷ available slots, where held = booked − cancelled (includes no-shows and statuses not recorded)",
                    "owner": "Retail Operations (proposed)", "exclusions": "Non-exam appointment types; closure days.",
                    "limitations": "High utilization is not automatically good; read with attendance."},
    "attendance": {"id": "KPI-03", "name": "Attendance rate", "units": "%",
                   "formula": "Completed exams ÷ held appointments", "owner": "Retail Operations, Optometry Partners consulted (proposed)",
                   "exclusions": "Cancelled appointments; rescheduled originals (resolved upstream).",
                   "limitations": "Unrecorded statuses depress the rate; they are shown separately as a data-quality issue."},
    "exams": {"id": "KPI-04", "name": "Completed examinations (4-week average per week)", "units": "exams per week",
              "formula": "Σ completed exams in usable weeks ÷ number of usable weeks", "owner": "Clinical Services / Optometry Partners (definition, proposed)",
              "exclusions": "Non-exam visits; voided or test records.", "limitations": "Not a clinician productivity measure; depends on capacity."},
    "conversion": {"id": "KPI-05", "name": "Exam-to-purchase conversion", "units": "%",
                   "formula": "Distinct exam-linked purchasing customers (eligible eyewear within 30 days, attributed to exam week) ÷ completed exams",
                   "owner": "Retail Operations; Optometry Partners and Finance consulted (proposed)",
                   "exclusions": "Purchases without a linked exam; non-eyewear items; fully refunded purchases; staff purchases.",
                   "limitations": "Customers may legitimately not purchase. In production the latest 4 weeks are provisional; this synthetic snapshot treats them as final."},
    "rev_per_exam": {"id": "KPI-06", "name": "Revenue per completed exam (context, role-restricted)", "units": "CAD per exam",
                     "formula": "Net eligible eyewear revenue (after returns processed in the week) ÷ completed exams",
                     "owner": "Finance (proposed)", "exclusions": "Sales tax; gift cards; staff purchases; non-eyewear items.",
                     "limitations": "Not exam-linked and not profitability; never an exception driver. Weekly net revenue can be negative in production."},
    "turnaround": {"id": "KPI-07", "name": "Average order turnaround", "units": "calendar days",
                   "formula": "Σ (ready date − placed date) ÷ orders that reached ready, by order-placed week",
                   "owner": "Supply Chain (proposed)", "exclusions": "Cancelled orders; warranty and repair orders.",
                   "limitations": "Synthetic simplification: every order placed is assumed to reach ready, so orders placed is the denominator. Averages hide long tails."},
    "on_time": {"id": "KPI-08", "name": "On-time fulfilment", "units": "%",
                "formula": "Orders ready on or before the promised date ÷ orders placed (excluding cancelled)",
                "owner": "Supply Chain (proposed)", "exclusions": "Cancelled orders; orders without a promised date (counted as a data issue).",
                "limitations": "Generous promised dates inflate the rate. Production marks the latest 21 days provisional."},
    "recall_rate": {"id": "KPI-09", "name": "Recall-booking rate", "units": "%",
                    "formula": "Recall bookings within 30 days ÷ deliverable recall contacts, by contact week",
                    "owner": "Marketing (proposed)", "exclusions": "Undeliverable contacts; opt-outs; bookings before the contact.",
                    "limitations": "Not applicable before a store's recall programme starts (null, not zero). Recall exceptions require a Developing or Mature store with 40+ contacts in the window (exception rule set v0.2 parameter)."},
    "ramp": {"id": "KPI-10", "name": "Store ramp index", "units": "index (100 = same-age peer median)",
             "formula": "100 × store 4-week average completed exams per week ÷ median of peers at the same weeks since opening",
             "owner": "Retail Operations, Business Development consulted (proposed)",
             "exclusions": "Mature stores (over 104 weeks); first 3 weeks after opening; Red weeks for the store and peers.",
             "limitations": "Needs 5+ peers observed at the same age; stores with smaller capacity look low. Trigger: under 80 for 4 consecutive weeks with an available index."},
    "completeness": {"id": "KPI-11", "name": "Data completeness", "units": "%",
                     "formula": "Mean of per-source completeness (records received ÷ records expected) across the sources expected for the store-week; each source weighted equally",
                     "owner": "Governance (proposed); data team operational",
                     "exclusions": "Sources not expected for the store (e.g., recall before programme start).",
                     "limitations": "In this prototype the value is simulated directly in the CSV, not reconstructed from source load metadata."},
    "freshness": {"id": "KPI-12", "name": "Data freshness", "units": "status",
                  "formula": "Current (all sources loaded ≤48 h before refresh) · Delayed (>48 h to 7 days) · Stale (>7 days or week not covered); worst source wins",
                  "owner": "Data team (proposed)", "exclusions": "Sources not expected for the store.",
                  "limitations": "Simulated status in the prototype."},
}
PERIOD_TEXT = ("4 calendar weeks ending the selected week; at least 3 usable weeks; unavailable if the selected week "
               "has Red data quality. Rates are ratios of sums.")
