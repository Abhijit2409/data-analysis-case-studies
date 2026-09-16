"""
Validation and analysis of the SYNTHETIC dataset (Phases 12-13).
All results are synthetic and unrelated to actual Specsavers performance.

Calculation rules live in build/kpi_engine.py (single source). This script:
  1. runs the 32 structural and seeded-pattern checks on the CSV,
  2. computes every store-week KPI, peer, exception and ramp value through the engine,
  3. writes data/analysis_summary.json (dashboard and deck input) and data/validation-results.md.

Exit status is 1 if any check fails, so a failed validation stops the build.
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kpi_engine as E  # noqa: E402

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CSV = os.path.join(BASE, "data", "synthetic_store_weekly.csv")
OUT_MD = os.path.join(BASE, "data", "validation-results.md")
OUT_JSON = os.path.join(BASE, "data", "analysis_summary.json")
GENERIC_BANNERS = {"Host Banner A", "Host Banner B", "Standalone (no host)"}

df = E.derive(E.load(CSV))
count_cols = ["available_appointment_slots", "booked_appointments", "completed_exams", "cancelled_appointments",
              "no_show_appointments", "purchasing_customers", "orders_placed", "orders_ready_on_time"]
checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


# ------------------------------------------------------------------ structural checks (1-29)
weeks = sorted(df["week_start"].unique())
check("26 distinct reporting weeks", len(weeks) == 26, f"{len(weeks)} weeks")
diffs = {int((pd.Timestamp(weeks[i + 1]) - pd.Timestamp(weeks[i])).days) for i in range(len(weeks) - 1)}
check("Weeks are consecutive (7-day steps)", diffs == {7}, f"steps={sorted(diffs)}")
check("All week_start dates are Mondays", all(pd.Timestamp(w).weekday() == 0 for w in weeks))
check("30 distinct stores", df["store_id"].nunique() == 30, f"{df['store_id'].nunique()} stores")
check("Unique store_id x week_start", not df.duplicated(["store_id", "week_start"]).any())
attr_cols = ["store_name", "province", "region", "retail_banner", "store_format", "opening_date"]
check("Store attributes constant per store", (df.groupby("store_id")[attr_cols].nunique() == 1).all().all())
check("Each province maps to one region", (df.groupby("province")["region"].nunique() == 1).all())
check("No rows before opening date", (df["week_start"] >= df["opening_date"]).all())
expected_rows = sum(sum(1 for w in weeks if pd.Timestamp(w) >= od) for od in df.groupby("store_id")["opening_date"].first())
check("No missing store-weeks after opening", len(df) == expected_rows, f"rows={len(df)}, expected={expected_rows}")
wso = ((df["week_start"] - df["opening_date"]).dt.days // 7)
check("weeks_since_opening = floor(days/7)", (wso == df["weeks_since_opening"]).all())
check("maturity_cohort matches as-at-week band (New 0-26, Developing 27-104, Mature 105+)",
      (df["weeks_since_opening"].map(E.cohort_for) == df["maturity_cohort"]).all())
check("Count fields non-negative integers", (df[count_cols] >= 0).all().all() and all((df[c] == df[c].round()).all() for c in count_cols))
check("completed + cancelled + no_show <= booked",
      (df["completed_exams"] + df["cancelled_appointments"] + df["no_show_appointments"] <= df["booked_appointments"]).all())
check("booked <= available slots", (df["booked_appointments"] <= df["available_appointment_slots"]).all())
check("purchasing_customers <= completed_exams", (df["purchasing_customers"] <= df["completed_exams"]).all())
check("orders_ready_on_time <= orders_placed", (df["orders_ready_on_time"] <= df["orders_placed"]).all())
rc_null, rb_null = df["recall_contacts"].isna(), df["recall_bookings"].isna()
check("recall_contacts and recall_bookings null together", (rc_null == rb_null).all())
check("recall null only where programme not active (weeks_since_opening < 12)",
      (df.loc[rc_null, "weeks_since_opening"] < 12).all() and (df.loc[~rc_null, "weeks_since_opening"] >= 12).all())
check("recall_bookings <= recall_contacts", (df.loc[~rc_null, "recall_bookings"] <= df.loc[~rc_null, "recall_contacts"]).all())
check("Generator assumption: no negative weekly net revenue in this synthetic run (the KPI-06 business rule permits negative weeks, flagged)",
      (df["eyewear_revenue"] >= 0).all())
check("average_turnaround_days > 0 where orders placed", (df.loc[df["orders_placed"] > 0, "average_turnaround_days"] > 0).all())
check("data_completeness_pct within 0-100", df["data_completeness_pct"].between(0, 100).all())
check("data_refresh_status in {Current, Delayed, Stale}", set(df["data_refresh_status"]) <= {"Current", "Delayed", "Stale"})
check("retail_banner uses generic values only", set(df["retail_banner"]) <= GENERIC_BANNERS, str(sorted(set(df["retail_banner"]))))
fmt_ok = ((df["store_format"] == "Grocery-hosted") == df["retail_banner"].str.startswith("Host Banner")).all()
check("Grocery-hosted <=> Host Banner A/B; other formats standalone", fmt_ok)
check("All store names prefixed 'Synthetic - '", df["store_name"].str.startswith("Synthetic - ").all())

# ------------------------------------------------------------------ engine
sw, _ = E.compute(df)
latest = pd.Timestamp(weeks[-1])
last4_weeks = [pd.Timestamp(w) for w in weeks[-4:]]

# ------------------------------------------------------------------ seeded-pattern checks (30-35)
pattern = {}
p1 = []
for sid, s in df.groupby("store_id"):
    if s["maturity_cohort"].iloc[0] != "New" or len(s) < 12:
        continue
    a, b = s.head(4), s.tail(4)
    p1.append({"store_id": sid, "rows": int(len(s)), "age_first": int(s["weeks_since_opening"].iloc[0]), "age_last": int(s["weeks_since_opening"].iloc[-1]),
               "util_first4": a["held"].sum() / a["available_appointment_slots"].sum(), "util_last4": b["held"].sum() / b["available_appointment_slots"].sum(),
               "exams_first4": a["completed_exams"].mean(), "exams_last4": b["completed_exams"].mean(),
               "conv_first4": a["purchasing_customers"].sum() / a["completed_exams"].sum(), "conv_last4": b["purchasing_customers"].sum() / b["completed_exams"].sum(),
               "cohort_first": s["maturity_cohort"].iloc[0], "cohort_last": s["maturity_cohort"].iloc[-1]})
pattern["P1_new_stores_improving"] = p1
check("P1 every New-at-start store (12+ weeks) improves utilization and exams (first 4 vs last 4 weeks)",
      all(x["util_last4"] > x["util_first4"] and x["exams_last4"] > x["exams_first4"] for x in p1), f"{len(p1)} stores")

store_turn = df.groupby("store_id").apply(lambda s: s["turn_x_orders"].sum() / s["orders_placed"].sum(), include_groups=False)
net_med_turn = float(store_turn.median())
atl = sorted(df.loc[df["region"] == "Atlantic", "store_id"].unique())
atl_above = int((store_turn[atl] > net_med_turn).sum())
atl_p, oth_p = E.pooled(df[df["region"] == "Atlantic"]), E.pooled(df[df["region"] != "Atlantic"])
pattern["P2_atlantic_turnaround"] = {"period": "all 26 weeks", "atlantic_turnaround": atl_p["turnaround"], "other_turnaround": oth_p["turnaround"],
                                     "atlantic_on_time": atl_p["on_time"], "other_on_time": oth_p["on_time"],
                                     "atlantic_stores_above_network_store_median": atl_above, "atlantic_stores": len(atl),
                                     "network_store_median_turnaround": net_med_turn}
check("P2 Atlantic turnaround elevated vs other regions; 5 of 6 Atlantic stores above network store median",
      atl_p["turnaround"] > oth_p["turnaround"] + 2 and atl_above == 5, f"{atl_p['turnaround']:.1f} vs {oth_p['turnaround']:.1f} days (all weeks); {atl_above}/{len(atl)} above")

p3 = {sid: {k: E.pooled(df[df["store_id"] == sid])[k] for k in ["utilization", "attendance"]} for sid in ["SYN-012", "SYN-019"]}
others = E.pooled(df[~df["store_id"].isin(["SYN-012", "SYN-019"])])
pattern["P3_high_demand_low_attendance"] = {"period": "all 26 weeks", "stores": p3, "rest_of_network": {"utilization": others["utilization"], "attendance": others["attendance"]}}
check("P3 SYN-012 & SYN-019 utilization >= 90% and attendance <= 86% (rest of network attendance >= 92%)",
      all(v["utilization"] >= 0.90 and v["attendance"] <= 0.86 for v in p3.values()) and others["attendance"] >= 0.92)

s5raw = df[df["store_id"] == "SYN-005"]
s5 = sw[sw["store_id"] == "SYN-005"]
conv_first = s5raw.head(6)["purchasing_customers"].sum() / s5raw.head(6)["completed_exams"].sum()
conv_last = s5raw.tail(8)["purchasing_customers"].sum() / s5raw.tail(8)["completed_exams"].sum()
exams_first, exams_last = s5raw.head(6)["completed_exams"].mean(), s5raw.tail(8)["completed_exams"].mean()
b_weeks = s5.loc[s5["conversion_rule_b"], "week_start"].dt.date.astype(str).tolist()
a_weeks = s5.loc[s5["conversion_rule_a"], "week_start"].dt.date.astype(str).tolist()
pattern["P4_mature_declining_conversion"] = {
    "store_id": "SYN-005", "conv_weeks1_6": conv_first, "conv_last8": conv_last, "exams_per_week_weeks1_6": exams_first, "exams_per_week_last8": exams_last,
    "rule_b_weeks": b_weeks, "rule_a_weeks": a_weeks,
    "weekly": [{"week_start": r["week_start"].date().isoformat(), "conversion_r4": None if pd.isna(r["conversion_r4"]) else float(r["conversion_r4"]),
                "peer_median": None if pd.isna(r["conversion_peer_median"]) else float(r["conversion_peer_median"])} for _, r in s5.iterrows()]}
check("P4 SYN-005 conversion declines >= 10 pts while exams stay within +/-10%; rule (b) fires for 3+ weeks",
      (conv_first - conv_last) >= 0.10 and abs(exams_last / exams_first - 1) <= 0.10 and len(b_weeks) >= 3,
      f"{conv_first:.1%} -> {conv_last:.1%}; rule b weeks={len(b_weeks)}")

dq_rows = df[df["dq_status"] != "Green"]
pattern["P5_data_quality"] = [{"week_start": r["week_start"].date().isoformat(), "store_id": r["store_id"], "completeness": float(r["data_completeness_pct"]),
                               "refresh": r["data_refresh_status"], "unresolved": int(r["unresolved"]), "status": r["dq_status"]} for _, r in dq_rows.iterrows()]
red_rows = sw[sw["dq_status"] == "Red"]
red_clean = (not red_rows[[f"{k}_flag" for k in E.EXCEPTION_KPIS]].any().any()) and red_rows[[f"{k}_r4" for k in E.KPIS]].isna().all().all()
check("P5 data-quality warnings present (Amber and Red); Red store-weeks have no KPI values and raise no performance exceptions",
      (dq_rows["dq_status"] == "Red").sum() >= 3 and (dq_rows["dq_status"] == "Amber").sum() >= 3 and red_clean,
      f"Amber={int((dq_rows['dq_status'] == 'Amber').sum())}, Red={int((dq_rows['dq_status'] == 'Red').sum())}")

cohort_kpis = {c: E.pooled(df[df["maturity_cohort"] == c]) for c in ["New", "Developing", "Mature"]}
pattern["P6_cohort_differences"] = cohort_kpis
check("P6 cohort ordering New < Developing < Mature for utilization, conversion and exams per store-week",
      all(cohort_kpis["New"][k] < cohort_kpis["Developing"][k] < cohort_kpis["Mature"][k] for k in ["utilization", "conversion", "exams_per_store_week"]))

# ------------------------------------------------------------------ summaries
fw = df[df["week_start"] == latest]
last4 = df[df["week_start"].isin(last4_weeks)]
regions = sorted(df["region"].unique())
flags_all = E.stage_flags(sw)
flags_latest = [f for f in flags_all if f["week_start"] == latest.date().isoformat()]
ramp_elig = sw[(sw["weeks_since_opening"] >= E.RAMP_MIN_AGE) & (sw["weeks_since_opening"] <= E.RAMP_MAX_AGE)]
ramp_cov = float((ramp_elig["ramp_state"] == "ok").mean())
rb = df["recall_bookings"]
suppression = {"weekly_recall_bookings_1_to_4": int(((rb >= 1) & (rb <= 4)).sum()), "weekly_recall_bookings_zero": int((rb == 0).sum()),
               "weekly_recall_not_applicable": int(rb.isna().sum()),
               "recall_rate_states_4wk": sw["recall_rate_state"].value_counts().to_dict()}
red_effect = [{"store_id": r["store_id"], "week_start": r["week_start"].date().isoformat(), "states": {k: r[f"{k}_state"] for k in E.KPIS},
               "ramp_state": r["ramp_state"]} for _, r in red_rows.iterrows()]


def fnum(x, nd=6):
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        pass
    x = float(x)
    return None if (math.isnan(x) or math.isinf(x)) else round(x, nd)


def fint(x):
    return None if x is None or pd.isna(x) else int(x)


store_master = [{"id": sid, "name": g["store_name"].iloc[0], "province": g["province"].iloc[0], "region": g["region"].iloc[0],
                 "format": g["store_format"].iloc[0], "banner": g["retail_banner"].iloc[0], "opened": g["opening_date"].iloc[0].date().isoformat()}
                for sid, g in df.groupby("store_id")]

store_weekly = {}
for sid, s in sw.groupby("store_id"):
    recs = []
    for _, r in s.sort_values("week_start").iterrows():
        rec = {"w": r["week_start"].date().isoformat(), "c": r["maturity_cohort"], "a": int(r["weeks_since_opening"]), "dq": r["dq_status"],
               "comp": fnum(r["data_completeness_pct"], 1), "ref": r["data_refresh_status"], "prov": bool(r["provisional"]),
               "slots": int(r["available_appointment_slots"]), "booked": int(r["booked_appointments"]), "cancel": int(r["cancelled_appointments"]),
               "held": int(r["held"]), "noshow": int(r["no_show_appointments"]), "unres": int(r["unresolved"]), "done": int(r["completed_exams"]),
               "buy": int(r["purchasing_customers"]), "rev": fnum(r["eyewear_revenue"], 2), "orders": int(r["orders_placed"]),
               "ontime": int(r["orders_ready_on_time"]), "turnx": fnum(r["turn_x_orders"], 2),
               "rc": fint(r["recall_contacts"]), "rb": fint(r["recall_bookings"]), "k": {}}
        for k in E.PEER_KPIS:
            kr = {"v": fnum(r[f"{k}_r4"]), "s": r[f"{k}_state"], "m": fnum(r[f"{k}_peer_median"]), "q1": fnum(r[f"{k}_peer_p25"]),
                  "q3": fnum(r[f"{k}_peer_p75"]), "n": fint(r[f"{k}_peer_n"]), "b": r[f"{k}_peer_basis"],
                  "nf": fint(r[f"{k}_peer_n_format"]), "nc": fint(r[f"{k}_peer_n_cohort"]), "wk": fint(r[f"{k}_weeks"])}
            if k in E.EXCEPTION_KPIS:
                kr.update({"x": bool(r[f"{k}_flag"]), "xa": bool(r[f"{k}_rule_a"]), "xb": bool(r[f"{k}_rule_b"]), "xr": int(r[f"{k}_flag_run"]),
                           "br": int(r[f"{k}_b_run"]), "bs": fnum(r[f"{k}_base8"]), "ch": fnum(r[f"{k}_change"]), "es": r[f"{k}_exc_state"],
                           "ae": bool(r[f"{k}_a_eval"]), "be": bool(r[f"{k}_b_eval"])})
            if k == "recall_rate":
                kr["d4"] = fnum(r["recall_rate_d4"], 0)
            rec["k"][k] = kr
        rec["ramp"] = {"i": fnum(r["ramp_index"], 3), "s": r["ramp_state"], "m": fnum(r["ramp_peer_median"], 3), "q1": fnum(r["ramp_peer_p25"], 3),
                       "q3": fnum(r["ramp_peer_p75"], 3), "n": fint(r["ramp_peer_n"]), "b": r["ramp_basis"], "run": int(r["ramp_below_run"]), "x": bool(r["ramp_flag"])}
        rec["sr"] = {st: int(r[f"stage_{st}_run"]) for st in sorted(set(E.STAGE[k] for k in E.EXCEPTION_KPIS)) if r[f"stage_{st}_run"] > 0}
        recs.append(rec)
    store_weekly[sid] = recs

PROMPTS = {
    "Booking": ["Review booking visibility (online and in-store), the appointment availability pattern and local awareness activity.", "Store team with Regional Retail Manager; Marketing if the pattern is regional"],
    "Attendance": ["Check the reminder and confirmation process, booking lead times and no-show follow-up.", "Store team with Regional Retail Manager"],
    "Conversion": ["Review the exam-to-eyewear hand-off, frame and lens availability, and how pricing and coverage options are explained.", "Retail and Optometry Partners with Regional Retail Manager"],
    "Fulfilment": ["Review order routing, lab turnaround and remakes; check whether nearby stores show the same pattern.", "Supply Chain with store team"],
    "Recall": ["Review recall list quality, contact channel mix and booking follow-up.", "Marketing with store team"],
    "Ramp": ["Discuss local launch activity, booking visibility and the capacity plan.", "Regional Retail Manager with Business Development"],
    "Data": ["Review data completeness with the data team before discussing performance for this store-week.", "Data team"],
}

summary = {
    "disclaimer": "SYNTHETIC DATA - fictional stores and values, unrelated to actual Specsavers performance.",
    "meta": {
        "versions": E.VERSIONS,
        "parameters": {"peer_floor": E.PEER_FLOOR, "small_count": E.SMALL_COUNT, "window_weeks": E.WINDOW_WEEKS, "min_usable_weeks": E.MIN_USABLE_WEEKS,
                       "baseline_weeks": E.BASELINE_WEEKS, "baseline_min_usable": E.BASELINE_MIN_USABLE, "rule_a_margin": E.RULE_A_MARGIN,
                       "rule_b_change": E.RULE_B_CHANGE, "rule_b_run": E.RULE_B_RUN, "recall_min_contacts": E.RECALL_MIN_CONTACTS,
                       "ramp_min_age": E.RAMP_MIN_AGE, "ramp_max_age": E.RAMP_MAX_AGE, "ramp_threshold": E.RAMP_THRESHOLD, "ramp_run": E.RAMP_RUN},
        "snapshot": {"latest_week": latest.date().isoformat(), "seed": 20260913,
                     "treatment": ("Finalised synthetic snapshot: every week, including the latest 4 weeks of conversion and recall and the latest "
                                   "21 days of fulfilment, is treated as final. In production those periods would be marked provisional until "
                                   "their attribution or fulfilment windows close (KPI-05, KPI-07 to KPI-09).")},
        "period_text": E.PERIOD_TEXT, "state_text": E.STATE_TEXT, "kpi_help": E.KPI_HELP, "prompts": PROMPTS,
    },
    "weeks": [pd.Timestamp(w).date().isoformat() for w in weeks],
    "stores": store_master,
    "store_weekly": store_weekly,
    # --- summaries used by documents and the deck (periods stated in keys) ---
    "network_week_latest": E.pooled(fw),
    "region_week_latest": {rg: E.pooled(fw[fw["region"] == rg]) for rg in regions},
    "network_last4": E.pooled(last4),
    "region_last4": {rg: E.pooled(last4[last4["region"] == rg]) for rg in regions},
    "network_all_weeks": E.pooled(df),
    "cohort_kpis": cohort_kpis,
    "patterns": pattern,
    "stage_flags_total": len(flags_all),
    "stage_flags_per_week_avg": len(flags_all) / len(weeks),
    "stage_flags_by_stage": pd.Series([f["stage"] for f in flags_all]).value_counts().sort_index().to_dict(),
    "stage_flags_latest_week": flags_latest,
    "exceptions_by_kpi": {k: int(sw[f"{k}_flag"].sum()) for k in E.EXCEPTION_KPIS},
    "ramp_index_coverage": ramp_cov,
    "ramp_triggers": sw.loc[sw["ramp_flag"], ["store_id", "week_start", "ramp_index", "ramp_below_run"]].assign(week_start=lambda x: x["week_start"].dt.date.astype(str)).to_dict(orient="records"),
    "suppression": suppression,
    "red_store_weeks": red_effect,
    "checks": [{"check": c, "passed": p, "detail": d} for c, p, d in checks],
}


def default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if math.isnan(o) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return o.date().isoformat()
    raise TypeError(type(o))


def clean(o):
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


with open(OUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(clean(summary), fh, default=default, separators=(",", ":"), allow_nan=False)

# ------------------------------------------------------------------ Power BI-ready tables (Phase 13 §5.1)
PBI = os.path.join(BASE, "data", "powerbi")
os.makedirs(PBI, exist_ok=True)
kpi_rows, rev_rows = [], []
for _, r in sw.iterrows():
    wk_iso = r["week_start"].date().isoformat()
    for k in E.PEER_KPIS:
        rec = {"store_id": r["store_id"], "week_start": wk_iso, "kpi_key": k, "value": fnum(r[f"{k}_r4"]), "state": r[f"{k}_state"],
               "usable_weeks": fint(r[f"{k}_weeks"]), "peer_median": fnum(r[f"{k}_peer_median"]), "peer_p25": fnum(r[f"{k}_peer_p25"]),
               "peer_p75": fnum(r[f"{k}_peer_p75"]), "peer_n": fint(r[f"{k}_peer_n"]), "peer_basis": r[f"{k}_peer_basis"]}
        if k in E.EXCEPTION_KPIS:
            rec.update({"rule_a": bool(r[f"{k}_rule_a"]), "rule_b": bool(r[f"{k}_rule_b"]), "flag": bool(r[f"{k}_flag"]), "consecutive_weeks": int(r[f"{k}_flag_run"]),
                        "baseline_8wk": fnum(r[f"{k}_base8"]), "change_vs_baseline": fnum(r[f"{k}_change"]), "exception_state": r[f"{k}_exc_state"]})
        if k == "rev_per_exam":
            rec["eyewear_revenue_week"] = fnum(r["eyewear_revenue"], 2)
            rev_rows.append(rec)
        else:
            kpi_rows.append(rec)
pd.DataFrame(kpi_rows).to_csv(os.path.join(PBI, "store_week_kpi.csv"), index=False)
pd.DataFrame(rev_rows).to_csv(os.path.join(PBI, "store_week_revenue.csv"), index=False)
sw.assign(week_start=sw["week_start"].dt.date.astype(str))[["store_id", "week_start", "weeks_since_opening", "ramp_index", "ramp_state", "ramp_peer_median",
                                                            "ramp_peer_p25", "ramp_peer_p75", "ramp_peer_n", "ramp_basis", "ramp_below_run", "ramp_flag"]].to_csv(
    os.path.join(PBI, "ramp_index.csv"), index=False)


# ------------------------------------------------------------------ markdown report
def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


L = ["# Validation Results — Synthetic Dataset (Phase 12)\n",
     "> **SYNTHETIC DATA.** Fictional stores and values, unrelated to actual Specsavers performance. Generated by `build/generate_synthetic.py` (seed 20260913); "
     "calculations by `build/kpi_engine.py`; validated by `build/validate_and_analyze.py`. This file is regenerated on every build.\n",
     f"**Rows:** {len(df)} · **Columns:** {len(pd.read_csv(CSV, nrows=1).columns)} · **Stores:** {df['store_id'].nunique()} · **Weeks:** {len(weeks)} "
     f"({pd.Timestamp(weeks[0]).date()} to {latest.date()}) · **Checks passed:** {sum(p for _, p, _ in checks)}/{len(checks)}\n",
     "These are **structural and seeded-pattern checks** on the CSV. Calculation-rule regression tests (Red withholding, suppression, windows, peers, "
     "exception rules, ramp persistence) are separate: see `tests/` and `evidence/test-results.md`.\n",
     "## 1. Automated checks\n\n| # | Check | Result | Detail |\n|---|---|---|---|"]
for i, (c, p, d) in enumerate(checks, 1):
    L.append(f"| {i} | {c} | {'PASS' if p else '**FAIL**'} | {d} |")
L.append("\n## 2. Pattern evidence\n")
L.append("### P1 — New stores improving over time (first 4 vs last 4 rows in window)\n\n| Store | Rows | Age first→last | Cohort first→last | Utilization | Exams / week | Conversion |\n|---|---|---|---|---|---|---|")
for x in p1:
    L.append(f"| {x['store_id']} | {x['rows']} | {x['age_first']}→{x['age_last']} | {x['cohort_first']}→{x['cohort_last']} | {pct(x['util_first4'])} → {pct(x['util_last4'])} | {x['exams_first4']:.0f} → {x['exams_last4']:.0f} | {pct(x['conv_first4'])} → {pct(x['conv_last4'])} |")
p2 = pattern["P2_atlantic_turnaround"]
atl_l4, atl_wk = E.pooled(last4[last4["region"] == "Atlantic"]), E.pooled(fw[fw["region"] == "Atlantic"])
L.append(f"\n### P2 — Region with elevated turnaround\n\n| Measure | Atlantic, all 26 weeks | Other regions, all 26 weeks | Atlantic, last 4 weeks | Atlantic, week of {latest.date()} |\n|---|---|---|---|---|\n"
         f"| Avg order turnaround (days, order-weighted) | {p2['atlantic_turnaround']:.1f} | {p2['other_turnaround']:.1f} | {atl_l4['turnaround']:.1f} | {atl_wk['turnaround']:.1f} |\n"
         f"| On-time fulfilment | {pct(p2['atlantic_on_time'])} | {pct(p2['other_on_time'])} | {pct(atl_l4['on_time'])} | {pct(atl_wk['on_time'])} |\n\n"
         f"{p2['atlantic_stores_above_network_store_median']} of {p2['atlantic_stores']} Atlantic stores are above the network store median turnaround ({p2['network_store_median_turnaround']:.1f} days, all weeks).\n")
L.append("### P3 — High demand, lower attendance (all 26 weeks)\n\n| Store | Utilization | Attendance |\n|---|---|---|")
for sid, v in p3.items():
    L.append(f"| {sid} | {pct(v['utilization'])} | {pct(v['attendance'])} |")
L.append(f"| Rest of network | {pct(others['utilization'])} | {pct(others['attendance'])} |\n")
p4 = pattern["P4_mature_declining_conversion"]
L.append(f"### P4 — Mature store with declining conversion (SYN-005)\n\nWeekly conversion, weeks 1–6 pooled: **{pct(p4['conv_weeks1_6'])}** → last 8 weeks pooled: **{pct(p4['conv_last8'])}**. "
         f"Exams per week: {p4['exams_per_week_weeks1_6']:.0f} → {p4['exams_per_week_last8']:.0f}.\n\nRule (b) weeks (own 8-week baseline): {', '.join(p4['rule_b_weeks']) or 'none'}  \nRule (a) weeks (peer comparison): {', '.join(p4['rule_a_weeks']) or 'none'}\n")
L.append("### P5 — Data-quality warnings\n\n| Week | Store | Completeness | Refresh | Unresolved appts | Status |\n|---|---|---|---|---|---|")
for x in pattern["P5_data_quality"]:
    L.append(f"| {x['week_start']} | {x['store_id']} | {x['completeness']:.1f}% | {x['refresh']} | {x['unresolved']} | {x['status']} |")
L.append("\n**Red withholding (engine output):** at every Red store-week, all KPI values are unavailable (state `red`), no exception is raised and the ramp index is unavailable where applicable:\n")
for x in red_effect:
    L.append(f"- {x['store_id']} {x['week_start']}: conversion `{x['states']['conversion']}`, ramp `{x['ramp_state']}`")
L.append("\n### P6 — Cohort differences (all 26 weeks, pooled by as-at-week cohort; Red store-weeks excluded)\n\n| Cohort | Store-weeks | Exams / store-week | Utilization | Attendance | Conversion | Revenue / exam | On-time | Recall-booking rate |\n|---|---|---|---|---|---|---|---|---|")
for c, v in cohort_kpis.items():
    L.append(f"| {c} | {v['store_weeks']} | {v['exams_per_store_week']:.0f} | {pct(v['utilization'])} | {pct(v['attendance'])} | {pct(v['conversion'])} | ${v['rev_per_exam']:.0f} | {pct(v['on_time'])} | {pct(v['recall_rate'])} |")
L.append("\n## 3. Peer groups in the latest week (FR-16; floor = 5)\n\n| Cohort | Format | Stores | Peers excl. store | Outcome |\n|---|---|---|---|---|")
sizes = fw.groupby(["maturity_cohort", "store_format"]).size().rename("stores").reset_index()
coh = fw.groupby("maturity_cohort").size().to_dict()
for _, r in sizes.iterrows():
    n_ex, coh_n = r["stores"] - 1, coh[r["maturity_cohort"]] - 1
    L.append(f"| {r['maturity_cohort']} | {r['store_format']} | {r['stores']} | {n_ex} | {'cohort x format' if n_ex >= 5 else ('fallback to cohort' if coh_n >= 5 else 'suppressed')} |")
L.append(f"\nRamp index (KPI-10) available for **{ramp_cov:.0%}** of store-weeks aged 3–104 weeks; the rest are unavailable because fewer than 5 peers were observed at the same age, history is insufficient, or the week is Red. "
         f"Ramp triggers (index under 80 for 4 consecutive available weeks): **{len(summary['ramp_triggers'])}**.\n")
L.append(f"## 4. Small-count suppression (PR-04 demonstration rule v0.2)\n\nWeekly recall bookings of 1–4: **{suppression['weekly_recall_bookings_1_to_4']}** store-weeks (displayed as \"<5\"); zero bookings: {suppression['weekly_recall_bookings_zero']}; "
         f"not applicable (no programme): {suppression['weekly_recall_not_applicable']}. 4-week recall-rate states: " + ", ".join(f"{k}: {v}" for k, v in suppression["recall_rate_states_4wk"].items()) + ".\n")
L.append(f"## 5. Exceptions (rule set {E.VERSIONS['exception_rules']}, illustrative)\n\nFlags by KPI across 26 weeks: " + ", ".join(f"{k}: {v}" for k, v in summary["exceptions_by_kpi"].items()) + ".\n")
L.append(f"Grouped by journey stage (one row per store-week-stage, **listing every triggering KPI**): **{len(flags_all)}** flags, **{len(flags_all) / len(weeks):.1f} per week** across 30 stores. By stage: " +
         ", ".join(f"{k}: {v}" for k, v in summary["stage_flags_by_stage"].items()) + ".\n")
L.append(f"\n**Latest week ({latest.date()}):**\n\n| Store | Stage | KPIs (rule) | Consecutive weeks (stage) | Data quality |\n|---|---|---|---|---|")
for f in flags_latest:
    L.append(f"| {f['store_id']} | {f['stage']} | {', '.join(k + ' (' + f['rules'][k] + ')' for k in f['kpis'])} | {f['stage_run']} | {f['dq_status']} |")
L.append("\n*All results above are synthetic and illustrate the analytical design only.*\n")
with open(OUT_MD, "w", encoding="utf-8") as fh:
    fh.write("\n".join(L))

failed = [c for c, p, _ in checks if not p]
print(f"Checks passed: {len(checks) - len(failed)}/{len(checks)}")
print(f"Wrote {os.path.abspath(OUT_JSON)} ({os.path.getsize(OUT_JSON) / 1024:.0f} KB) and {os.path.abspath(OUT_MD)}")
if failed:
    print("FAILED CHECKS:", failed)
    sys.exit(1)
