"""Write report/figures_trace.csv: every figure quoted in this package's documentation,
the key in data/analysis_summary.json it is read from, and the test that guards the rule behind it.

Values are read from the analysis output, never typed by hand. Run after build/validate_and_analyze.py:

    python build/validate_and_analyze.py
    python build/make_figures_trace.py
"""
import csv
import json
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(BASE, "data", "analysis_summary.json")
OUT = os.path.join(BASE, "report", "figures_trace.csv")

with open(SRC, encoding="utf-8") as fh:
    D = json.load(fh)


def get(path):
    """Read a dotted path out of the analysis JSON; 'len:' returns a length, 'rows:' the total rows of a dict of lists."""
    node = D
    if path.startswith("rows:"):
        return sum(len(v) for v in D[path[5:]].values())
    if path.startswith("len:"):
        for part in path[4:].split("."):
            node = node[part]
        return len(node)
    for part in path.split("."):
        node = node[int(part)] if part.isdigit() else node[part]
    return node


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


def num(v, d=0):
    return f"{v:,.{d}f}"


NW, AT = "network_week_latest", "region_week_latest.Atlantic"
LATEST = D["weeks"][-1]

# (figure as displayed in the documentation, dotted key in analysis_summary.json, formatter, rule or parameter, guarding test)
ROWS = [
    ("Stores in the synthetic network", "len:stores", num, "Generator: 30 fictional stores", "validate_and_analyze check 4"),
    ("Reporting weeks", "len:weeks", num, "Contiguous Mondays", "validate_and_analyze checks 1-3"),
    ("Store-weeks present", "rows:store_weekly", num, "One row per store per week after opening", "validate_and_analyze check 9"),
    ("First reporting week", "weeks.0", str, "Calendar week start", "validate_and_analyze check 3"),
    ("Latest reporting week", f"weeks.{len(D['weeks']) - 1}", str, "Calendar week start", "validate_and_analyze check 3"),

    (f"Network stores, week of {LATEST}", f"{NW}.stores", num, "Role scope: network", "PY_BASE_01, UI-ROL-01"),
    (f"Network completed exams, week of {LATEST}", f"{NW}.completed_exams", num, "Sum of completed exams", "PY_BASE_01, JS-AGG-01"),
    (f"Network appointment utilization, week of {LATEST}", f"{NW}.utilization", pct, "Ratio of sums (KPI-01)", "PY_BASE_01, JS-AGG-01"),
    (f"Network attendance, week of {LATEST}", f"{NW}.attendance", pct, "Ratio of sums (KPI-02)", "PY_BASE_01, JS-AGG-01"),
    (f"Network exam-to-purchase conversion, week of {LATEST}", f"{NW}.conversion", pct, "Ratio of sums (KPI-05)", "PY_BASE_01, JS-AGG-01"),
    (f"Network on-time fulfilment, week of {LATEST}", f"{NW}.on_time", pct, "Ratio of sums (KPI-07)", "PY_BASE_01, PY_DEF_01"),
    (f"Network average order turnaround, week of {LATEST}", f"{NW}.turnaround", lambda v: f"{v:.1f} days", "Weighted mean (KPI-08)", "PY_BASE_01"),
    (f"Network revenue per completed exam, week of {LATEST}", f"{NW}.rev_per_exam", lambda v: f"${v:,.0f}", "Ratio of sums (KPI-06); role-restricted", "PY_DEF_02, UI-OP-01"),
    (f"Network Amber store-weeks, week of {LATEST}", f"{NW}.amber_store_weeks", num, "Data quality Amber = provisional", "PY_AMBER_01, UI-AMBER-01"),
    (f"Network Red store-weeks excluded, week of {LATEST}", f"{NW}.excluded_red_store_weeks", num, "Red store-weeks withheld", "PY_RED_01, UI-RED-01"),

    (f"Atlantic stores, week of {LATEST}", f"{AT}.stores", num, "Role scope applied before filters", "PY_BASE_02, UI-RRM-01"),
    (f"Atlantic completed exams, week of {LATEST}", f"{AT}.completed_exams", num, "Sum within scope", "PY_BASE_02, UI-RRM-01"),
    (f"Atlantic appointment utilization, week of {LATEST}", f"{AT}.utilization", pct, "Ratio of sums within scope", "PY_BASE_02, JS-SCOPE-01"),
    (f"Atlantic attendance, week of {LATEST}", f"{AT}.attendance", pct, "Ratio of sums within scope", "PY_BASE_02, JS-SCOPE-01"),
    (f"Atlantic conversion, week of {LATEST}", f"{AT}.conversion", pct, "Ratio of sums within scope", "PY_BASE_02, JS-SCOPE-01"),
    (f"Atlantic on-time fulfilment, week of {LATEST}", f"{AT}.on_time", pct, "Ratio of sums within scope", "PY_BASE_02, JS-SCOPE-01"),
    (f"Atlantic average order turnaround, week of {LATEST}", f"{AT}.turnaround", lambda v: f"{v:.1f} days", "Weighted mean within scope", "PY_BASE_02, UI-RRM-01"),

    ("Stage flags raised across all 26 weeks", "stage_flags_total", num, "Exception rule set v0.2", "PY_EXC_01 to PY_EXC_06"),
    ("Average stage flags per week", "stage_flags_per_week_avg", lambda v: f"{v:.1f}", "228 flags / 26 weeks", "PY_EXC_03"),
    ("Flags in the Fulfilment stage", "stage_flags_by_stage.Fulfilment", num, "Both fulfilment KPIs kept in the stage group", "PY_EXC_03, UI-EXC-04"),
    ("Flags in the Attendance stage", "stage_flags_by_stage.Attendance", num, "Stage grouping", "PY_EXC_03"),
    ("Flags in the Recall stage", "stage_flags_by_stage.Recall", num, "Recall rules skip New stores and low contact counts", "PY_EXC_05"),
    ("Flags in the Conversion stage", "stage_flags_by_stage.Conversion", num, "Rules (a) and (b)", "PY_EXC_02, PY_EXC_04"),
    ("Flags in the Booking stage", "stage_flags_by_stage.Booking", num, "Rules (a) and (b)", "PY_EXC_02"),
    ("Store-weeks with a turnaround flag", "exceptions_by_kpi.turnaround", num, "Lower is better for turnaround", "PY_EXC_02"),
    ("Store-weeks with an on-time flag", "exceptions_by_kpi.on_time", num, "Rules (a) and (b)", "PY_EXC_02"),

    ("Share of store-weeks with a ramp index", "ramp_index_coverage", pct, "Same-age peers, floor 5, age 3-104 weeks", "PY_RAMP_01"),
    ("Ramp triggers in the demonstration data", "len:ramp_triggers", num, "Index below 80 for 4 consecutive available weeks", "PY_RAMP_01, PY_RAMP_02"),

    ("Weekly recall counts of 1-4 shown as '<5'", "suppression.weekly_recall_bookings_1_to_4", num, "Small-count suppression v0.2", "PY_SUP_01, JS-SUP-01, UI-SUP-01"),
    ("Weekly recall counts of exactly zero (shown as 0)", "suppression.weekly_recall_bookings_zero", num, "Zero is not suppressed", "PY_SUP_02"),
    ("Store-weeks where recall is not applicable", "suppression.weekly_recall_not_applicable", num, "Programme not active before week 12", "PY_SUP_03"),
    ("4-week recall rates displayed", "suppression.recall_rate_states_4wk.ok", num, "State: ok", "PY_SUP_01"),
    ("4-week recall rates suppressed", "suppression.recall_rate_states_4wk.suppressed", num, "State: suppressed (small numerator or denominator)", "PY_SUP_01, JS-SUP-02"),
    ("4-week recall rates with insufficient history", "suppression.recall_rate_states_4wk.insufficient_history", num, "State: insufficient_history", "PY_WIN_01, PY_WIN_02"),

    ("Red store-weeks in the dataset", "len:red_store_weeks", num, "Completeness under 90% or a stale refresh", "PY_RED_01 to PY_RED_04, UI-RED-01"),
    ("Structural and seeded-pattern checks passed", "len:checks", lambda v: f"{v}/{v}", "build/validate_and_analyze.py", "validate_and_analyze.py exit status"),
]

with open(OUT, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["figure", "displayed", "raw_value", "source_key", "rule_or_parameter", "guarded_by"])
    for label, key, fmt, rule, test in ROWS:
        raw = get(key)
        w.writerow([label, fmt(raw), raw, f"analysis_summary.json:{key.split(':')[-1]}" + (" (count)" if ':' in key else ""), rule, test])

print(f"Wrote {os.path.abspath(OUT)} ({len(ROWS)} figures)")
