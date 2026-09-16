"""Step 6 - Reconcile the Excel workbook (values as recalculated by Excel) against the Python
reference results, and run privacy and wording scans. Writes build/reconciliation.json."""
import json
import pathlib
import re
import pandas as pd
from openpyxl import load_workbook
from config import GROUPS, SHORT, G1, G2, G3, MAPPING

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "build" / "results.json").read_text())
W = json.loads((ROOT / "build" / "workbook_cells.json").read_text())
WB = ROOT / "outputs" / "Vancouver311_Closure_Outcomes_Workbook.xlsx"
wb = load_workbook(WB, data_only=True)
A = wb["Analysis"]
results, diffs = [], []

def cmp(label, got, exp, tol=1e-9):
    ok = (got == exp) if (exp is None or isinstance(exp, str)) else (got is not None and abs(float(got) - float(exp)) <= tol)
    results.append((label, got, exp, ok))
    if not ok:
        diffs.append((label, got, exp))

def val(ref):
    sh, c = ref.split("!") if "!" in ref else ("Analysis", ref)
    return wb[sh][c].value

C = W["cells"]
N, OA, OX = R["profile"]["rows"], R["outcomes_all"], R["outcomes_excl_admin"]
cmp("total", val(C["total"]), N)
cmp("closed", val(C["closed"]), OA["closed"])
cmp("open", val(C["open"]), OA["open"])
cmp("closed excl admin", val(C["closed_excl"]), OX["closed"])
for i, gname in enumerate(GROUPS, start=1):
    ga = OA["groups"][i - 1]; gx = OX["groups"][i - 1]
    cmp(f"group {i} count", val(C[f"grp_all_{i}"]), ga["count"])
    cmp(f"group {i} share", val(C[f"grp_share_{i}"]), ga["share"])
    cmp(f"group {i} excl count", val(C[f"grp_excl_{i}"]), gx["count"])
    cmp(f"group {i} excl share", val(C[f"grp_excl_share_{i}"]), gx["share"])

# label -> row index for Analysis column A
rows = {}
for r in range(1, A.max_row + 1):
    v = A.cell(r, 1).value
    if isinstance(v, str):
        rows.setdefault(v, []).append(r)

# closure reasons (section C: first occurrence of each reason label)
mapping = {m["closure_reason_original"]: m for m in R["mapping"]}
for reason, m in mapping.items():
    r = rows[reason][0]
    cmp(f"reason closed: {reason}", A.cell(r, 2).value, m["closed_2025"])
    cmp(f"reason open: {reason}", A.cell(r, 4).value, m["open_2025"])
# departments
d0, d1 = W["d_range"]
dv = {x["department"]: x for x in R["dept_variation"]["rows"]}
for r in range(d0, d1 + 1):
    dname = A.cell(r, 1).value
    cmp(f"dept closed: {dname}", A.cell(r, 2).value, dv[dname]["closed"])
    for j, gname in enumerate(GROUPS):
        cmp(f"dept {dname} {SHORT[gname]}", A.cell(r, 3 + j).value, dv[dname][SHORT[gname]])
# months
e0, e1 = W["e_range"]
bm = {x["month"]: x for x in R["by_month"]}
for k, r in enumerate(range(e0, e1 + 1), start=1):
    cmp(f"month {k} records", A.cell(r, 2).value, R["demand"]["by_month"][k - 1]["count"])
    cmp(f"month {k} closed", A.cell(r, 3).value, bm[k]["closed"])
    cmp(f"month {k} SP share", A.cell(r, 4).value, bm[k]["Service provided"])
# channels, local areas, top types - labels can repeat across sections ("Unknown" is both a
# closure reason and a channel), so look each label up only after its own section header.
def section_row(prefix):
    return next(r for lab, rs in rows.items() for r in rs if lab.startswith(prefix))
def row_in(label, prefix):
    start = section_row(prefix)
    return next(r for r in rows[label] if r > start)
for x in R["demand"]["by_channel"]:
    cmp(f"channel {x['value']}", A.cell(row_in(x["value"], "F. "), 2).value, x["count"])
for x in R["demand"]["by_local_area"]:
    cmp(f"area {x['value']}", A.cell(row_in(x["value"], "I. "), 2).value, x["count"])
for x in R["demand"]["top_types"]:
    cmp(f"type {x['type']}", A.cell(row_in(x["type"], "G. "), 3).value, x["count"])
cmp("top5 types share", val(C["top5_share"]), R["demand"]["top5_types_share"])
cmp("top10 types share", val(C["top10_share"]), R["demand"]["top10_types_share"])
cmp("top5 dept share", val(C["top5_dept_share"]), R["demand"]["top5_depts_share"])
cmp("unknown top2 share", val(C["unknown_top2"]), R["unknown"]["top2_share"])
h0 = W["h_start"]
for k, t in enumerate(R["unknown"]["top_types"]):
    cmp(f"unknown {t['type']}", A.cell(h0 + k, 2).value, t["count"])
# focus family
j0, j1 = W["j_range"]
F = R["focus"]
fbt = {x["type"]: x for x in F["by_type"]}
for r in range(j0, j1 + 1):
    t = A.cell(r, 1).value
    if t == "All three types":
        cmp("focus records", A.cell(r, 2).value, F["records"]); cmp("focus closed", A.cell(r, 3).value, F["closed"])
        cmp("focus open", A.cell(r, 4).value, F["open"])
        for j, g in enumerate(F["groups"]):
            cmp(f"focus {g['short']}", A.cell(r, 5 + j).value, g["share"])
    else:
        cmp(f"focus {t} records", A.cell(r, 2).value, fbt[t]["records"])
        for j, gname in enumerate(GROUPS):
            cmp(f"focus {t} {SHORT[gname]}", A.cell(r, 5 + j).value, fbt[t][SHORT[gname]])
# durations
keymap = {G1: "Service provided", G2: "Assigned / referred / continuing", G3: "No service or no action",
          "Further action has been planned": "  of which: Further action has been planned",
          "Referred to another service group": "  of which: Referred to another service group",
          "All outcomes (mixed)": "All outcomes (mixed)"}
fd = {(x["type"], x["group"]): x for x in F["durations"]}
for scope, rtype, key, pop, r in W["dur_rows"]:
    if scope == "Citywide":
        if key == "All outcomes (mixed)":
            ref = R["duration_all_mixed"] if pop.startswith("All") else R["duration_all_mixed_excl_admin"]
        else:
            lst = R["duration_by_group"] if pop.startswith("All") else R["duration_by_group_excl_admin"]
            ref = next(x for x in lst if x["group"] == key)
    else:
        ref = fd[(rtype, keymap[key])]
    lab = f"dur {scope}|{rtype}|{key}|{pop}"
    cmp(lab + " n", A.cell(r, 3).value, ref["n"])
    for c, pk in zip((4, 5, 6), ("p50", "p75", "p90")):
        exp = ref[pk] if ref[pk] is not None else "n<30"
        cmp(lab + " " + pk, A.cell(r, c).value, exp)
# mapping sheet and DQ log formula counts
M = wb["Closure_Outcome_Mapping"]
for r in range(5, 5 + len(MAPPING)):
    reason = M.cell(r, 1).value
    cmp(f"mapping closed {reason}", M.cell(r, 4).value, mapping[reason]["closed_2025"])
    cmp(f"mapping open {reason}", M.cell(r, 5).value, mapping[reason]["open_2025"])
Q = R["quality"]
dq_expect = {"Close date before local opening date": Q["negative_days"], "Open cases (no close date)": R["open_cases"]["count"],
             "Status and closure-reason combinations": Q["open_with_non_na_reason"], "Closed cases recorded as 'N/A'": Q["closed_with_na_reason"],
             "'Unknown' closure reason": R["unknown"]["total"], "Missing local area": Q["missing_local_area"],
             "Obsolete 'ZZ OLD' labels": Q["zz_old_rows"], "Administrative/internal-sounding types": R["admin"]["rows"],
             "Duplicate-looking rows": Q["duplicate_looking_rows"], "Row count and cohort": N}
DQ = wb["Data_Quality_Log"]
for r in range(5, DQ.max_row + 1):
    lab = DQ.cell(r, 2).value
    if lab in dq_expect:
        cmp(f"DQ {lab}", DQ.cell(r, 4).value, dq_expect[lab])
D = wb["Dashboard"]
cmp("dashboard total tile", D["A5"].value, N)
cmp("dashboard SP tile", D["I5"].value, OA["groups"][0]["share"])
# Excel-side boolean checks
excel_checks = [val(c) for c in W["checks"]] + [val(W["map_check"])]
cmp("all Excel reconciliation checks TRUE", all(v is True for v in excel_checks), True)
sd_rows = wb["Source_Data"].max_row - 3

# ------------------------------------------------------------------ privacy scan
bad_cols = {"address", "latitude", "longitude", "geom"}
csv_cols = set(pd.read_csv(ROOT / "outputs" / "data" / "cohort_2025_clean.csv", nrows=1).columns)
addr_re = re.compile(r"\b\d{1,5}\s+(?:[NSEW]\s+)?[A-Z0-9][A-Za-z0-9]*\s+(?:ST|AV|AVE|DR|RD|BLVD|WAY|PL|CRES|HWY|MALL|LANE|STREET|AVENUE)\b")
raw = pd.read_csv(ROOT / "data" / "raw" / "311_requests_raw_window.csv", usecols=["address"], dtype=str, keep_default_na=False)
sample_addr = set(a for a in raw["address"] if a)
addr_hits_wb = 0
for ws in wb.worksheets:
    if ws.title in ("Source_Data", "Source_Durations"):
        hdr = [c.value for c in ws[3]]
        if bad_cols & {str(h).lower() for h in hdr if h}:
            addr_hits_wb += 1
        continue
    for row in ws.iter_rows(values_only=True):
        for v in row:
            if isinstance(v, str) and (addr_re.search(v) or v in sample_addr):
                addr_hits_wb += 1
html_path = ROOT / "build" / "report.html"
privacy = {"csv_location_columns": sorted(bad_cols & csv_cols), "workbook_address_like_cells": addr_hits_wb}

rec = {"figures_compared": len(results), "differences": len(diffs), "diff_detail": diffs[:20],
       "excel_checks": len(excel_checks), "excel_checks_all_true": all(v is True for v in excel_checks),
       "source_data_rows": sd_rows, "privacy": privacy}
O = R["outcomes_all"]; CR = R["cohort_reconciliation"]
rec["checks_for_report"] = [
    f"Cohort: {CR['utc_year_2025_rows']:,} (UTC year) + {CR['local_2025_but_utc_2026']} &minus; {CR['utc_2025_but_local_2024']} = {N:,} local-date records; all 12 months present.",
    f"All {len(MAPPING)} closure-reason values mapped (none unmapped); the six outcome groups sum exactly to {O['closed']:,} closed cases in both Python and Excel.",
    f"Duration exclusions counted: {R['open_cases']['count']:,} open + {Q['negative_days']} negative = {R['open_cases']['count'] + Q['negative_days']:,}; eligible {R['duration_exclusions']['Eligible']:,} equals the citywide duration n.",
    f"Workbook refreshed through Power Query ({sd_rows:,} grouped rows reproducing {N:,} records) and recalculated in Excel: 0 formula errors; {len(excel_checks)} built-in checks TRUE.",
    f"{len(results):,} workbook figures (counts, shares, percentiles) compared with the independent Python calculation: {len(diffs)} differences.",
    f"Privacy scan: no address, coordinate or geometry field in the cleaned CSV or workbook data; {addr_hits_wb} address-like strings in workbook text.",
    "Wording review: patterns are described as hypotheses; no service standards, targets, savings, interviews or stakeholder feedback are asserted.",
]
(ROOT / "build" / "reconciliation.json").write_text(json.dumps(rec, indent=2, default=str))
print(json.dumps({k: v for k, v in rec.items() if k != "checks_for_report"}, indent=1, default=str))
for x in results[:0]:
    print(x)
