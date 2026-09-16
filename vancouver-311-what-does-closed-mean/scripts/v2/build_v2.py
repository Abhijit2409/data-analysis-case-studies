"""Version 2 of the case study: a shorter, visual redesign.

Every displayed number is read from the saved workbook (values as last calculated by
Excel) and logged to a trace file with its sheet!cell source. Figures that are not in
the workbook (option scores) are logged as analyst judgement from the v1 report.
The original v1 PDF and workbook are read only; nothing in outputs/ is overwritten.
"""
import csv
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pypdfium2 as pdfium
from openpyxl import load_workbook

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
from config import AUTHOR  # noqa: E402

SRC_PDF = ROOT / "outputs" / "Vancouver311_What_Does_Closed_Mean_Case_Study.pdf"
SRC_XLSX = ROOT / "outputs" / "Vancouver311_Closure_Outcomes_Workbook.xlsx"
OUT = ROOT / "outputs" / "v2_redesign"
OUT.mkdir(parents=True, exist_ok=True)
HTML = OUT / "Vancouver311_Case_Study_v2_source.html"
PDF = OUT / "Vancouver311_What_Does_Closed_Mean_v2.pdf"
TRACE = OUT / "Numbers_Trace_v2.csv"
STATS = ROOT / "build" / "v2_stats.json"
NPAGES = 6

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
HASH_BEFORE = {p.name: sha(p) for p in (SRC_PDF, SRC_XLSX)}

# ------------------------------------------------------------------ figures from the workbook
wb = load_workbook(SRC_XLSX, data_only=True)
A, MAP, README = wb["Analysis"], wb["Closure_Outcome_Mapping"], wb["README"]
R = json.loads((ROOT / "build" / "results.json").read_text())   # independent Python reference
trace = []

def w(ws, ref, label_ref=None, label=None):
    """Read a workbook value, asserting the row label so a shifted layout can't go unnoticed."""
    if label_ref:
        got = ws[label_ref].value
        assert got == label, f"{ws.title}!{label_ref} is {got!r}, expected {label!r}"
    return ws[ref].value

def show(value, text, source, check=None):
    """Register a displayed figure (with its workbook source) and return its display text."""
    ok = "n/a"
    if check is not None:
        ok = "match" if abs(float(value) - float(check)) < 1e-9 else "MISMATCH"
        assert ok == "match", (text, source, value, check)
    trace.append({"displayed": text, "value": value, "source": source,
                  "python_reference": "" if check is None else check, "check": ok})
    return text

n = lambda x: f"{int(round(x)):,}"
p1 = lambda x: f"{x * 100:.1f}%"
p0 = lambda x: f"{x * 100:.0f}%"

TOT = w(A, "B5", "A5", "Total 2025 records")
CLOSED = w(A, "B6", "A6", "Closed cases")
OPEN = w(A, "B7", "A7", "Open at extraction")
GRP_ROWS = {"G1": (16, "1. Service recorded as provided"), "G2": (17, "2. Work assigned, referred or continuing"),
            "G3": (18, "3. No service or no action recorded"), "G4": (19, "4. Insufficient information / could not proceed"),
            "G5": (20, "5. Unknown or N/A"), "G6": (21, "6. Other - requires review")}
G = {k: {"n": w(A, f"B{r}", f"A{r}", lab), "s": w(A, f"C{r}"), "nx": w(A, f"D{r}"), "sx": w(A, f"E{r}"), "row": r}
     for k, (r, lab) in GRP_ROWS.items()}
assert sum(g["n"] for g in G.values()) == CLOSED
refg = {x["group"][:2]: x for x in R["outcomes_all"]["groups"]}
for k, g in G.items():
    assert g["n"] == refg[k[1] + "."]["count"]

# Report categories = the six analyst groups, with the two smallest (G4, G6) shown together.
CATS = [
    {"key": "sp", "name": "Service provided", "groups": ["G1"], "color": "#1D3557", "ink": "#FFFFFF",
     "desc": "Reason: \u201cService provided\u201d"},
    {"key": "ho", "name": "Handed off or planned", "groups": ["G2"], "color": "#2A9D8F", "ink": "#FFFFFF",
     "desc": "Assigned, dispatched, referred, routed or planned"},
    {"key": "na", "name": "No service or no action", "groups": ["G3"], "color": "#8D99AE", "ink": "#10202F",
     "desc": "No action planned, not found, not a City service"},
    {"key": "un", "name": "Unknown", "groups": ["G5"], "color": "#B8DDD8", "ink": "#10202F",
     "desc": "Reason recorded as \u201cUnknown\u201d"},
    {"key": "ot", "name": "Other outcomes", "groups": ["G4", "G6"], "color": "#D5DAE0", "ink": "#10202F",
     "desc": "Insufficient info, unreachable, alternate service"},
]
for c in CATS:
    c["n"] = sum(G[g]["n"] for g in c["groups"])
    c["s"] = sum(G[g]["s"] for g in c["groups"])
    c["rows"] = [G[g]["row"] for g in c["groups"]]
COL = {c["key"]: c for c in CATS}

MONTHS = [(w(A, f"A{r}"), w(A, f"B{r}"), r) for r in range(65, 77)]
assert [m for m, _, _ in MONTHS] == ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
assert sum(v for _, v, _ in MONTHS) == TOT

FAM = []   # focus family rows 145-148: E..J = shares of groups G1..G6
for r, lab in ((145, "Pothole Case"), (146, "Street Repair Case"), (147, "Sidewalk Repair Case"), (148, "All three types")):
    row = {"label": w(A, f"A{r}", f"A{r}", lab), "records": w(A, f"B{r}"), "closed": w(A, f"C{r}"), "open": w(A, f"D{r}"), "row": r}
    sh = {f"G{i}": w(A, f"{L}{r}") for i, L in zip(range(1, 7), "EFGHIJ")}
    row["cat"] = {c["key"]: sum(sh[g] for g in c["groups"]) for c in CATS}
    FAM.append(row)
fam = {x["label"]: x for x in FAM}
ref_bt = {x["type"]: x for x in R["focus"]["by_type"]}
for x in FAM[:3]:
    assert x["closed"] == ref_bt[x["label"]]["closed"]

assert w(A, "A48") == "Department"
DEPT = []
for r in range(49, 61):
    d = {"name": w(A, f"A{r}"), "closed": w(A, f"B{r}"), "row": r}
    sh = {f"G{i}": w(A, f"{L}{r}") for i, L in zip(range(1, 7), "CDEFGH")}
    d["cat"] = {c["key"]: sum(sh[g] for g in c["groups"]) for c in CATS}
    DEPT.append(d)
DEPT_COVER = w(A, "B61", "A61", "Share of all closed cases covered by these 12 departments")
sp_max = max(DEPT, key=lambda d: d["cat"]["sp"])
sp_min = min(DEPT, key=lambda d: d["cat"]["sp"])

UNK = [{"type": w(A, f"A{r}"), "n": w(A, f"B{r}"), "rate": w(A, f"D{r}"), "share": w(A, f"E{r}"), "row": r} for r in (109, 110)]
UNK_TOP2 = w(A, "B113", "A113", "Top two request types' share of all 'Unknown' closures")
SEL_SS = w(A, "E152", "A152", "Street and sidewalk repair (selected)")
SEL_LS = w(A, "E153", "A153", "Street lights and signs")
assert w(A, "G152") == 4 and w(A, "G153") == 4
assert w(A, "A198") == "Sidewalk Repair - Service provided"
assert w(A, "A200") == "Sidewalk Repair - of which: Further action has been planned"
SW_SP = {k: w(A, f"{c}198") for k, c in zip(("n", "p50", "p75", "p90"), "CDEF")}
SW_FA = {k: w(A, f"{c}200") for k, c in zip(("n", "p50", "p75", "p90"), "CDEF")}
CITY_DUR = []
for r, key in ((165, "sp"), (166, "ho"), (167, "na"), (169, "un")):
    d = {"key": key, "pop": w(A, f"B{r}"), "n": w(A, f"C{r}"), "p50": w(A, f"D{r}"), "p90": w(A, f"F{r}"), "row": r}
    assert d["pop"] == "All published records"
    CITY_DUR.append(d)
MIXED = {"n": w(A, "C164", "A164", "Citywide - all outcomes mixed"), "p50": w(A, "D164"), "p90": w(A, "F164")}
ELIG = w(A, "B205", "A205", "Eligible closed cases")
EX_NEG = w(A, "B207", "A207", "Excluded: close date before local opening date")
CLOSED_X = w(A, "D22", "A22", "Total closed")
ADMIN_N = w(wb["Data_Quality_Log"], "D18", "B18", "Administrative/internal-sounding types")
EXTRACT_TXT = w(README, "B7", "A7", "Extraction")
m = re.search(r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})", EXTRACT_TXT)
EXTRACT_DATE, EXTRACT_TIME = m.group(1), m.group(2)
MAPROWS = [{"reason": w(MAP, f"A{r}"), "group": w(MAP, f"B{r}"), "closed": w(MAP, f"D{r}"), "open": w(MAP, f"E{r}"), "row": r}
           for r in range(5, 22)]
assert sum(x["closed"] for x in MAPROWS) == CLOSED and sum(x["open"] for x in MAPROWS) == OPEN
assert w(A, "B212", "A212", "All checks TRUE") is True

# Option scores are not workbook figures: analyst judgement from the v1 report (page 4).
OPTIONS = [("Keep the current interpretation", 18, "No effort, but \u201cclosed\u201d keeps mixing recorded outcomes."),
           ("Clarify outcome definitions in reporting", 31, "Targets the pattern found; uses fields already recorded; no system change."),
           ("Improve intake guidance for repairs", 17, "Weak evidence: few repair closures record missing information."),
           ("Add a recurring exception-review report", 25, "Useful later, but depends on agreed definitions first.")]

# ------------------------------------------------------------------ charts (exact physical size, 8pt+ text)
INK, INK2, MUTED, GRID = "#1F2933", "#52606D", "#7B8794", "#E4E7EB"
plt.rcParams.update({"font.family": ["Segoe UI", "Arial", "sans-serif"], "svg.fonttype": "none", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
                     "axes.spines.bottom": False, "figure.facecolor": "white", "axes.facecolor": "white"})

def svg_of(fig):
    buf = io.StringIO()
    fig.savefig(buf, format="svg")          # no bbox_inches: the SVG keeps its exact physical size
    plt.close(fig)
    s = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", buf.getvalue())
    return re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)

def two_line_labels(ax, ys, names, subs, size=9.5):
    tr = ax.get_yaxis_transform()
    for y, a, b in zip(ys, names, subs):
        ax.text(-0.012, y + 0.03, a, transform=tr, ha="right", va="bottom", fontsize=size, fontweight="semibold", color=INK)
        ax.text(-0.012, y - 0.03, b, transform=tr, ha="right", va="top", fontsize=8, color=INK2)

def chart_outcomes():
    W, H = 7.1, 2.4
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([2.7 / W, 0.03, (W - 2.7 - 0.1) / W, 0.94])
    cats = sorted(CATS, key=lambda c: -c["n"])
    ys = list(range(len(cats)))[::-1]
    for y, c in zip(ys, cats):
        ax.barh(y, c["s"], height=0.6, color=c["color"])
        ax.text(c["s"] + 0.012, y, p1(c["s"]), va="center", fontsize=10, color=INK, fontweight="bold")
        ax.text(c["s"] + 0.108, y, f"{n(c['n'])} cases", va="center", fontsize=8.5, color=INK2)
    two_line_labels(ax, ys, [c["name"] for c in cats], [c["desc"] for c in cats])
    ax.set_xlim(0, 0.86)
    ax.set_ylim(-0.6, len(cats) - 0.4)
    ax.set_xticks([]); ax.set_yticks([])
    ax.axvline(0, color="#9AA5B1", linewidth=0.8)
    return svg_of(fig)

def chart_months():
    W, H = 7.1, 1.25
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0.45 / W, 0.2, (W - 0.55) / W, 0.72])
    vals = [v for _, v, _ in MONTHS]
    hi, lo = vals.index(max(vals)), vals.index(min(vals))
    ax.bar(range(12), vals, width=0.62, color=["#1D3557" if i in (hi, lo) else "#AEB8C4" for i in range(12)])
    for i in (hi, lo):
        ax.text(i, vals[i] + 700, n(vals[i]), ha="center", va="bottom", fontsize=8.5, color=INK, fontweight="semibold")
    ax.set_xticks(range(12), [mth for mth, _, _ in MONTHS], fontsize=8.5, color=INK2)
    ax.set_yticks([0, 10000, 20000, 30000], ["0", "10k", "20k", "30k"], fontsize=8, color=MUTED)
    ax.tick_params(length=0)
    ax.set_ylim(0, 32000)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    return svg_of(fig)

def stacked(rows, W, H, left_in, sep_last=False, name_size=9.5, one_line=False):
    fig = plt.figure(figsize=(W, H))
    bottom_in = 0.3
    ax = fig.add_axes([left_in / W, bottom_in / H, (W - left_in - 0.12) / W, (H - bottom_in - 0.05) / H])
    ys, y = [], 0.0
    for i, r in enumerate(rows):
        if sep_last and i == len(rows) - 1:
            y += 0.35
        ys.append(-y)
        left = 0.0
        for c in CATS:
            v = r["cat"][c["key"]]
            if v <= 0:
                continue
            ax.barh(-y, v, left=left, height=0.62, color=c["color"], edgecolor="white", linewidth=1.2)
            if v >= 0.075:
                ax.text(left + v / 2, -y, p0(v), ha="center", va="center", fontsize=8.5, color=c["ink"], fontweight="semibold")
            left += v
        y += 1
    if one_line:
        tr = ax.get_yaxis_transform()
        for yy, r in zip(ys, rows):
            ax.text(-0.012, yy, r["title"], transform=tr, ha="right", va="center", fontsize=name_size, fontweight="semibold", color=INK)
            ax.text(1.015, yy, r["sub"], ha="left", va="center", fontsize=8, color=INK2)
        ax.set_xlim(0, 1.13)
    else:
        two_line_labels(ax, ys, [r["title"] for r in rows], [r["sub"] for r in rows], size=name_size)
        ax.set_xlim(0, 1)
    ax.set_ylim(min(ys) - 0.5, 0.5)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1], ["0%", "25%", "50%", "75%", "100%"], fontsize=8, color=MUTED)
    ax.tick_params(length=0)
    ax.xaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    return svg_of(fig)

def chart_family():
    rows = [{"title": x["label"].replace(" Case", ""), "sub": f"{n(x['closed'])} closed cases", "cat": x["cat"]} for x in FAM]
    return stacked(rows, 7.1, 2.0, 1.75, sep_last=True)

SHORT_DEPT = {"Traffic and Electrical Operations and Design": "Traffic & Electrical Ops & Design",
              "Parking Enforcement and Operations": "Parking Enforcement & Operations",
              "Business and Election Services": "Business & Election Services"}
def dept_title(name):
    unit, dept = name.split(" - ", 1) if " - " in name else ("", name)
    dept = SHORT_DEPT.get(dept, dept)
    return f"{dept} ({unit})" if unit else dept

def chart_depts():
    rows = [{"title": dept_title(d["name"]), "sub": n(d["closed"]), "cat": d["cat"]}
            for d in sorted(DEPT, key=lambda d: -d["cat"]["sp"])]
    return stacked(rows, 7.1, 3.6, 2.75, name_size=9, one_line=True)

SVG_OUT, SVG_MON, SVG_FAM, SVG_DEP = chart_outcomes(), chart_months(), chart_family(), chart_depts()

# ------------------------------------------------------------------ traced display values
t = {}
t["tot"] = show(TOT, n(TOT), "Analysis!B5", R["profile"]["rows"])
t["closed"] = show(CLOSED, n(CLOSED), "Analysis!B6", R["outcomes_all"]["closed"])
t["open"] = show(OPEN, n(OPEN), "Analysis!B7", R["outcomes_all"]["open"])
t["closed_pct"] = show(CLOSED / TOT, p1(CLOSED / TOT), "Analysis!B6 / Analysis!B5")
for c in CATS:
    t[c["key"] + "_n"] = show(c["n"], n(c["n"]), " + ".join(f"Analysis!B{r}" for r in c["rows"]))
    t[c["key"] + "_s"] = show(c["s"], p1(c["s"]), " + ".join(f"Analysis!C{r}" for r in c["rows"]) + " (share of closed cases)")
hi = max(MONTHS, key=lambda x: x[1]); lo = min(MONTHS, key=lambda x: x[1])
t["mon_hi"] = show(hi[1], n(hi[1]), f"Analysis!B{hi[2]} ({hi[0]})")
t["mon_lo"] = show(lo[1], n(lo[1]), f"Analysis!B{lo[2]} ({lo[0]})")
for _, v, r in MONTHS:
    show(v, n(v), f"Analysis!B{r} (monthly chart bar)")
for x in FAM:
    k = x["label"].split()[0].lower()
    for fld, col in (("closed", "C"),) + ((("open", "D"),) if k == "all" else ()):
        t[f"f_{k}_{fld}"] = show(x[fld], n(x[fld]), f"Analysis!{col}{x['row']}")
    for c in CATS:
        cols = {"G1": "E", "G2": "F", "G3": "G", "G4": "H", "G5": "I", "G6": "J"}
        t[f"f_{k}_{c['key']}"] = show(x["cat"][c["key"]], p0(x["cat"][c["key"]]),
                                      " + ".join(f"Analysis!{cols[g]}{x['row']}" for g in c["groups"]))
for d in DEPT:
    show(d["closed"], n(d["closed"]), f"Analysis!B{d['row']} (department chart label)")
    for c in CATS:
        cols = {"G1": "C", "G2": "D", "G3": "E", "G4": "F", "G5": "G", "G6": "H"}
        show(d["cat"][c["key"]], p0(d["cat"][c["key"]]), " + ".join(f"Analysis!{cols[g]}{d['row']}" for g in c["groups"]) + " (department chart)")
t["sel_ss"] = show(SEL_SS, p0(SEL_SS), "Analysis!E152")
t["sel_ls"] = show(SEL_LS, p0(SEL_LS), "Analysis!E153")
t["sw_fa_p50"] = show(SW_FA["p50"], str(SW_FA["p50"]), "Analysis!D200")
t["sw_fa_n"] = show(SW_FA["n"], n(SW_FA["n"]), "Analysis!C200")
t["sw_sp_p50"] = show(SW_SP["p50"], str(SW_SP["p50"]), "Analysis!D198")
t["sw_sp_n"] = show(SW_SP["n"], n(SW_SP["n"]), "Analysis!C198")
t["dep_min"] = show(sp_min["cat"]["sp"], p1(sp_min["cat"]["sp"]), f"Analysis!C{sp_min['row']} ({sp_min['name']})")
t["dep_max"] = show(sp_max["cat"]["sp"], p1(sp_max["cat"]["sp"]), f"Analysis!C{sp_max['row']} ({sp_max['name']})")
t["dep_cover"] = show(DEPT_COVER, p1(DEPT_COVER), "Analysis!B61")
t["unk_top2"] = show(UNK_TOP2, p1(UNK_TOP2), "Analysis!B113", R["unknown"]["top2_share"])
t["fam_un"] = show(fam["All three types"]["cat"]["un"], p1(fam["All three types"]["cat"]["un"]), "Analysis!I148")
t["elig"] = show(ELIG, n(ELIG), "Analysis!B205")
t["ex_neg"] = show(EX_NEG, n(EX_NEG), "Analysis!B207")
t["admin_n"] = show(ADMIN_N, n(ADMIN_N), "Data_Quality_Log!D18", R["admin"]["rows"])
t["closed_x"] = show(CLOSED_X, n(CLOSED_X), "Analysis!D22")
HO_DUR = next(d for d in CITY_DUR if d["key"] == "ho")
assert HO_DUR["n"] + EX_NEG == COL["ho"]["n"], "the negative-duration exclusions are expected to sit in the handed-off group"
t["ho_dur_n"] = show(HO_DUR["n"], n(HO_DUR["n"]), f"Analysis!C{HO_DUR['row']}")
for name, score, _ in OPTIONS:
    trace.append({"displayed": f"{score} of 35", "value": score, "python_reference": "", "check": "n/a (judgement)",
                  "source": f"v1 report p.4 options table: analyst judgement, not a workbook figure ({name})"})

# ------------------------------------------------------------------ HTML helpers and styles
LEGEND = '<div class="legend">' + "".join(
    f'<span class="chip"><i style="background:{c["color"]}"></i>{c["name"]}</span>' for c in CATS) + "</div>"

def table(head, rows, cls="", widths=None):
    th = "".join(f'<th{f" style=width:{widths[i]}" if widths else ""}>{h}</th>' for i, h in enumerate(head))
    tb = "".join("<tr>" + "".join(f"<td>{v}</td>" for v in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table>'

def foot(i):
    return (f'<footer><span>Independent analysis of public City of Vancouver open data. Not affiliated with or endorsed by the City.</span>'
            f'<span>{AUTHOR} &middot; {i} of {NPAGES}</span></footer>')

css = """
@page { size: Letter; margin: 0.62in 0.7in 0.55in 0.7in; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #1F2933; }
.page { position: relative; height: 9.83in; page-break-after: always; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.content { height: 9.45in; }
footer { position: absolute; left: 0; right: 0; bottom: 0; display: flex; justify-content: space-between;
  font-size: 7.5pt; color: #7B8794; border-top: 0.75pt solid #E4E7EB; padding-top: 5pt; }
.kicker { font-size: 8pt; letter-spacing: 1.2pt; text-transform: uppercase; color: #1F7A70; font-weight: 600; margin: 0 0 6pt; }
h1 { font-size: 23pt; line-height: 1.15; color: #1D3557; margin: 0 0 8pt; font-weight: 700; letter-spacing: -0.2pt; }
h2 { font-size: 16pt; line-height: 1.2; color: #1D3557; margin: 0 0 14pt; font-weight: 700; }
h3 { font-size: 11.5pt; line-height: 1.3; color: #1D3557; margin: 0 0 2pt; font-weight: 700; }
.dek { font-size: 11.5pt; color: #3E4C59; margin: 0 0 8pt; max-width: 6.6in; }
.meta { font-size: 8.5pt; color: #616E7C; margin: 0 0 18pt; }
.why { font-size: 9.5pt; color: #3E4C59; margin: 0 0 6pt; }
.note { font-size: 8pt; color: #616E7C; margin: 4pt 0 0; }
p { margin: 0 0 6pt; }
.metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14pt; margin: 0 0 20pt; }
.metric { border-top: 3pt solid #1D3557; padding-top: 7pt; }
.metric.teal { border-top-color: #2A9D8F; }
.metric .v { font-size: 26pt; font-weight: 700; color: #1D3557; line-height: 1; }
.metric.teal .v { color: #1F7A70; }
.metric .l { font-size: 9.5pt; color: #1F2933; margin-top: 5pt; line-height: 1.3; }
.metric .d { font-size: 8pt; color: #616E7C; margin-top: 3pt; }
.block { margin: 0 0 20pt; }
.callout { background: #EEF6F5; border-left: 4pt solid #2A9D8F; padding: 10pt 13pt; margin: 0 0 18pt; font-size: 10pt; }
.callout b { color: #1D3557; }
.cols3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16pt; }
.cols3 > div { font-size: 9.5pt; line-height: 1.4; border-top: 1.5pt solid #D5DAE0; padding-top: 6pt; }
.cols3 b { display: block; color: #1D3557; font-size: 10pt; margin-bottom: 2pt; }
.legend { display: flex; flex-wrap: nowrap; gap: 14pt; margin: 6pt 0 4pt; font-size: 8.5pt; color: #3E4C59; white-space: nowrap; }
.chip i { display: inline-block; width: 9pt; height: 9pt; border-radius: 2pt; margin-right: 4pt; vertical-align: -1pt; }
svg { display: block; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 16pt; }
.box { border: 1pt solid #D5DAE0; border-radius: 4pt; padding: 10pt 13pt; }
.box h4 { margin: 0 0 5pt; font-size: 10pt; color: #1D3557; }
.box.teal { background: #EEF6F5; border-color: #B8DDD8; }
.box.grey { background: #F5F7FA; }
ul { margin: 0; padding-left: 13pt; } li { margin: 0 0 4pt; font-size: 9.5pt; line-height: 1.38; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; line-height: 1.3; }
th { text-align: left; font-weight: 600; color: #52606D; font-size: 7.8pt; text-transform: uppercase; letter-spacing: 0.4pt;
  border-bottom: 1.2pt solid #1D3557; padding: 0 8pt 4pt 0; vertical-align: bottom; }
td { padding: 6pt 8pt 6pt 0; border-bottom: 0.75pt solid #E4E7EB; vertical-align: top; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.rec td { background: #EEF6F5; }
tr.rec td:first-child { box-shadow: inset 3pt 0 0 #2A9D8F; padding-left: 7pt; }
.score { white-space: nowrap; font-variant-numeric: tabular-nums; }
.bar { display: inline-block; height: 8pt; background: #AEB8C4; border-radius: 1pt; vertical-align: -0.5pt; margin-right: 7pt; }
tr.rec .bar { background: #2A9D8F; }
.rec-box { background: #1D3557; color: #FFFFFF; border-radius: 4pt; padding: 13pt 16pt; margin: 18pt 0 20pt; }
.rec-box .k { font-size: 8pt; letter-spacing: 1.2pt; text-transform: uppercase; color: #B8DDD8; font-weight: 600; }
.rec-box .h { font-size: 14pt; font-weight: 700; margin: 3pt 0 5pt; line-height: 1.25; }
.rec-box p { margin: 0; font-size: 10pt; color: #E4E7EB; }
.flow { display: flex; align-items: stretch; margin: 6pt 0 22pt; }
.flow .s { flex: 1; background: #F5F7FA; border: 1pt solid #D5DAE0; border-top: 3pt solid #2A9D8F; border-radius: 3pt; padding: 7pt 8pt; font-size: 9pt; line-height: 1.3; }
.flow .s b { display: block; color: #1D3557; font-size: 9.5pt; margin-bottom: 2pt; }
.flow .a { width: 16pt; display: flex; align-items: center; justify-content: center; color: #7B8794; font-size: 12pt; }
.steps td { font-size: 9.5pt; }
.steps td:first-child b { color: #1D3557; }
.small, .small li { font-size: 8.8pt; line-height: 1.42; color: #3E4C59; }
.src { font-size: 8pt; color: #616E7C; line-height: 1.4; }
.tbl-s table { font-size: 8.8pt; }
.tbl-s td { padding: 4.5pt 8pt 4.5pt 0; }
table.map td { padding: 3.2pt 8pt 3.2pt 0; font-size: 8.6pt; }
.method { columns: 2; column-gap: 22pt; }
.method li { break-inside: avoid; font-size: 8.8pt; }
.tight .block { margin-bottom: 13pt; }
.tight h2 { margin-bottom: 10pt; }
"""

# ------------------------------------------------------------------ pages
P1 = f"""
<section class="page"><div class="content">
<div class="kicker">Independent case study &middot; Public data &middot; Business analysis</div>
<h1>What does &ldquo;closed&rdquo; mean in Vancouver&rsquo;s 3-1-1 service-request data?</h1>
<p class="dek">An independent look at the City&rsquo;s public 3-1-1 records: can a closed case be read as a completed service?</p>
<div class="meta">Requests opened 1 Jan &ndash; 31 Dec 2025 (Vancouver time) &nbsp;&middot;&nbsp; {t['tot']} records &nbsp;&middot;&nbsp;
Data extracted {EXTRACT_DATE} &nbsp;&middot;&nbsp; Prepared by {AUTHOR}</div>

<div class="metrics">
 <div class="metric"><div class="v">{t['closed_pct']}</div><div class="l">of 2025 requests were closed at extraction</div>
  <div class="d">{t['closed']} of {t['tot']} records</div></div>
 <div class="metric"><div class="v">{t['sp_s']}</div><div class="l">of closed cases record &ldquo;Service provided&rdquo;</div>
  <div class="d">{t['sp_n']} of {t['closed']} closed cases</div></div>
 <div class="metric teal"><div class="v">{t['ho_s']}</div><div class="l">of closed cases record a handoff or planned work</div>
  <div class="d">{t['ho_n']} of {t['closed']} closed cases</div></div>
</div>

<div class="block">
 <h3>Just over half of closed cases record that the service was provided</h3>
 <p class="why">The rest record handoffs, decisions not to act or no specified outcome: a count of closed cases is not a count of completed services.</p>
 {SVG_OUT}
 <p class="note">Share of {t['closed']} closed cases; {t['open']} open cases excluded. Analyst-defined groups of the 17 published closure reasons (Appendix B).</p>
</div>

<div class="callout"><b>Closed is a record status, not proof of completion.</b> Whether the work was done is a separate fact, shown only through
the closure reason, and even &ldquo;Service provided&rdquo; needs its meaning confirmed.</div>

<div class="cols3">
 <div><b>&ldquo;Closed&rdquo; covers several outcomes</b>Closures also record handoffs ({t['ho_s']}), decisions not to act ({t['na_s']})
 and &ldquo;Unknown&rdquo; ({t['un_s']}).</div>
 <div><b>The mix varies by department</b>Across the 12 largest departments, &ldquo;Service provided&rdquo; ranges from {t['dep_min']} to {t['dep_max']}
 of each department&rsquo;s closed cases (Appendix A).</div>
 <div><b>Unclear outcomes are concentrated</b>{t['unk_top2']} of &ldquo;Unknown&rdquo; closures come from just two request types.</div>
</div>
</div>{foot(1)}</section>"""

P2 = f"""
<section class="page tight"><div class="content">
<div class="kicker">Evidence and interpretation</div>
<h2>Where the pattern shows up</h2>

<div class="block">
 <h3>Demand was spread across the whole year</h3>
 <p class="why">Monthly requests ranged from {t['mon_lo']} (December) to {t['mon_hi']} (July): a full year of activity, not one peak.</p>
 {SVG_MON}
 <p class="note">All {t['tot']} records, by Vancouver-local opening month.</p>
</div>

<div class="block">
 <h3>In street and sidewalk repair, what &ldquo;closed&rdquo; records depends on the request type</h3>
 <p class="why">&ldquo;Service provided&rdquo; ranges from {t['f_street_sp']} of closed street-repair cases to {t['f_pothole_sp']} of pothole cases, so one closure count
 would blur different outcomes.</p>
 {LEGEND}
 {SVG_FAM}
 <p class="note">Share of closed cases per request type; {t['f_all_open']} open cases excluded. Chosen from seven candidate families: it passed all four
 selection tests with the most handoff or planned closures ({t['sel_ss']} vs {t['sel_ls']} for the other qualifier).</p>
</div>

<div class="cols3 block">
 <div><b>Handoffs are common in repairs</b>{t['f_street_ho']} of street-repair and {t['f_sidewalk_ho']} of sidewalk-repair closures record a handoff or
 planned work (potholes: {t['f_pothole_ho']}).</div>
 <div><b>Planned work closes later</b>Sidewalk closures recorded as &ldquo;Further action has been planned&rdquo; took a median of {t['sw_fa_p50']} recorded
 calendar days (n&nbsp;=&nbsp;{t['sw_fa_n']}); &ldquo;Service provided,&rdquo; {t['sw_sp_p50']} (n&nbsp;=&nbsp;{t['sw_sp_n']}).</div>
 <div><b>Not every other outcome is unfinished</b>{t['f_street_na']} of street-repair closures record a decision or finding, such as no action planned.</div>
</div>

<div class="two">
 <div class="box teal"><h4>What we can conclude</h4><ul>
  <li>&ldquo;Closed&rdquo; covers several recorded outcomes.</li>
  <li>About a quarter record a handoff or planned work.</li>
  <li>Completion of planned work is not published.</li></ul></div>
 <div class="box grey"><h4>What needs confirmation with City staff</h4><ul>
  <li>What each closure reason means, including &ldquo;Service provided.&rdquo;</li>
  <li>Whether completion of handed-off work is recorded.</li>
  <li>Whether &ldquo;Unknown&rdquo; is a default for some intake paths.</li></ul></div>
</div>
</div>{foot(2)}</section>"""

best = max(OPTIONS, key=lambda o: o[1])
opt_rows = "".join(
    f'<tr class="{"rec" if o[0] == best[0] else ""}"><td><b>{o[0]}</b></td>'
    f'<td class="score"><span class="bar" style="width:{o[1] * 2.3:.0f}pt"></span>{o[1]}</td><td>{o[2]}</td></tr>' for o in OPTIONS)
OPT_TBL = ('<table><thead><tr><th style="width:34%">Option</th><th style="width:20%">Score (of 35)</th><th>Main consideration</th></tr></thead>'
           f"<tbody>{opt_rows}</tbody></table>")
P3 = f"""
<section class="page"><div class="content">
<div class="kicker">Recommendation</div>
<h2>Make closure outcomes visible in reporting</h2>

<div class="block">
 <h3>Four options compared</h3>
 <p class="why">Clarifying outcome definitions scored highest: it addresses the pattern found with the least effort and risk.</p>
 {OPT_TBL}
 <p class="note">Seven criteria (decision benefit, evidence, effort, risk, data needs, stakeholder impact, scalability), each scored 1&ndash;5 where 5 is more favourable.
 Preliminary outside-in judgement; needs validation with City staff.</p>
</div>

<div class="rec-box"><div class="k">Recommendation</div>
 <div class="h">Pilot outcome-aware closure reporting for street and sidewalk repair</div>
 <p>It addresses one status covering different recorded outcomes, needs no system change, and lays the foundation for later
 exception reviews.</p></div>

<div class="two block">
 <div class="box teal"><h4>Already applied in this study</h4><ul>
  <li>Outcome shares use closed cases; open cases shown separately.</li>
  <li>All 17 original closure reasons kept and mapped.</li>
  <li>Durations compared within request type and outcome.</li></ul></div>
 <div class="box grey"><h4>Proposed: needs validation with City staff</h4><ul>
  <li>Agreed definitions for each closure reason.</li>
  <li>An outcome-split view for the pilot service.</li>
  <li>A way to link completion of planned or referred work to the case.</li></ul></div>
</div>

</div>{foot(3)}</section>"""

steps = [
    ["<b>1. Confirm definitions</b><br>Agree what each repair closure reason means and where completion is recorded.",
     "Streets Operations service owner, 3-1-1 intake lead, reporting analyst, business analyst",
     "Every closure reason used for repairs has an agreed written definition."],
    ["<b>2. Pilot the report</b><br>Three monthly cycles of an outcome-split view for street and sidewalk repair.",
     "Reporting analyst, service owner",
     f"Users can tell recorded provision from handoffs in a short check; &ldquo;Unknown&rdquo; share tracked (2025 public baseline: {t['fam_un']})."],
    ["<b>3. Evaluate and decide</b><br>Review usefulness and effort, then expand, adjust or stop.",
     "Sponsor, service owner, business analyst",
     "A decision against agreed criteria. Targets are set only after baselines are measured."],
]
P4 = f"""
<section class="page"><div class="content">
<div class="kicker">Practical next steps</div>
<h2>How the pilot would work</h2>


<h3>Proposed reporting flow</h3>
<p class="why">Each step keeps the published data intact and adds only definitions and review.</p>
<div class="flow">
 <div class="s"><b>1. Preserve</b>Keep the original status and closure reason</div><div class="a">&rarr;</div>
 <div class="s"><b>2. Group</b>Apply agreed outcome definitions</div><div class="a">&rarr;</div>
 <div class="s"><b>3. Separate</b>Show open and unclear cases alongside</div><div class="a">&rarr;</div>
 <div class="s"><b>4. Review</b>Service owner checks exceptions monthly</div><div class="a">&rarr;</div>
 <div class="s"><b>5. Publish</b>With definitions and the data date</div>
</div>

<h3>Three implementation steps</h3>
<div class="block steps">
 {table(["Step", "Who (proposed)", "Success measure"], steps, widths=["36%", "28%", "36%"])}
</div>

<div class="two">
 <div class="box grey small"><h4>Limitations</h4><ul>
  <li>Public data only; no interviews or internal documents.</li>
  <li>Closure reasons describe the record, not a verified outcome.</li>
  <li>No case ID, so referrals and reopenings can&rsquo;t be traced.</li>
  <li>Calendar-day durations from a date-only field; one year of data.</li></ul></div>
 <div class="box src"><h4>Sources</h4>
  City of Vancouver Open Data Portal, &ldquo;3-1-1 service requests&rdquo; dataset and catalogue record (opendata.vancouver.ca), extracted {EXTRACT_DATE}.<br><br>
  City of Vancouver, &ldquo;Report issues and request services with Van311&rdquo; (vancouver.ca/van311.aspx).<br><br>
  Contains information licensed under the Open Government Licence &ndash; Vancouver. Method and mapping: Appendix B.</div>
</div>
</div>{foot(4)}</section>"""

unk_rows = []
for x in UNK:
    unk_rows.append([x["type"].replace(" Case", ""), show(x["n"], n(x["n"]), f"Analysis!B{x['row']}"),
                     show(x["rate"], p1(x["rate"]), f"Analysis!D{x['row']}"), show(x["share"], p1(x["share"]), f"Analysis!E{x['row']}")])
sens_rows = []
for key in ("sp", "ho", "na", "un"):
    g = G[COL[key]["groups"][0]]
    sens_rows.append([COL[key]["name"], show(g["s"], p1(g["s"]), f"Analysis!C{g['row']}"), show(g["sx"], p1(g["sx"]), f"Analysis!E{g['row']}")])
dur_rows = []
for d in CITY_DUR:
    dur_rows.append([COL[d["key"]]["name"], show(d["n"], n(d["n"]), f"Analysis!C{d['row']}"),
                     show(d["p50"], str(d["p50"]), f"Analysis!D{d['row']}"), show(d["p90"], str(d["p90"]), f"Analysis!F{d['row']}")])
dur_rows.append(["<b>All outcomes combined</b>", show(MIXED["n"], n(MIXED["n"]), "Analysis!C164"),
                 show(MIXED["p50"], str(MIXED["p50"]), "Analysis!D164"), show(MIXED["p90"], str(MIXED["p90"]), "Analysis!F164")])
num = lambda rows, idx: [[f'<span class="nm">{v}</span>' if i in idx else v for i, v in enumerate(r)] for r in rows]
P5 = f"""
<section class="page"><div class="content">
<div class="kicker">Appendix A &middot; Supporting evidence</div>
<h2>Why one closure rate cannot compare departments</h2>
<div class="block">
 <h3>The outcome mix behind &ldquo;closed&rdquo; varies widely across departments</h3>
 <p class="why">Among the 12 largest departments ({t['dep_cover']} of closed cases), &ldquo;Service provided&rdquo; ranges from {t['dep_min']} to {t['dep_max']} of each
 department&rsquo;s closed cases, so closure rates are not comparable without the outcome split.</p>
 {LEGEND}
 {SVG_DEP}
 <p class="note">Share of each department&rsquo;s own closed 2025 cases, sorted by the &ldquo;Service provided&rdquo; share. Numbers at right are closed cases. Three long names are shortened.</p>
</div>
<div class="two tbl-s">
 <div><h3>Where &ldquo;Unknown&rdquo; comes from</h3>
  {table(["Request type", "Unknown", "Rate in type", "Share of all"], unk_rows, widths=["40%", "18%", "20%", "22%"])}
  <h3 style="margin-top:14pt">Sensitivity check</h3>
  {table(["Closed-case share", "All records", "Excl. flagged"], sens_rows, widths=["46%", "27%", "27%"])}
  <p class="note">&ldquo;Excl. flagged&rdquo; drops four administrative-sounding request types ({t['admin_n']} records; {t['closed_x']} closed cases remain).</p></div>
 <div><h3>Recorded calendar days to closure</h3>
  {table(["Outcome (citywide)", "Eligible n", "Median", "90th pct"], dur_rows, widths=["40%", "22%", "18%", "20%"])}
  <p class="note">Eligible closed cases ({t['elig']}); open cases and {t['ex_neg']} cases with a close date before the opening date are excluded
  (all {t['ex_neg']} are in &ldquo;Handed off or planned,&rdquo; so its n is {t['ho_dur_n']} rather than {t['ho_n']}).
  Nearest-rank percentiles; not resolution or service-delivery time. The combined median describes no single group.</p></div>
</div>
</div>{foot(5)}</section>"""

cat_of = {g: c["name"] for c in CATS for g in c["groups"]}
map_rows = []
for x in MAPROWS:
    map_rows.append([x["reason"], cat_of["G" + x["group"][0]], x["group"],
                     show(x["closed"], n(x["closed"]), f"Closure_Outcome_Mapping!D{x['row']}"),
                     show(x["open"], n(x["open"]), f"Closure_Outcome_Mapping!E{x['row']}")])
P6 = f"""
<section class="page"><div class="content">
<div class="kicker">Appendix B &middot; Method, definitions and traceability</div>
<h2>How the figures were produced</h2>
<ul class="method small">
 <li><b>Source:</b> City of Vancouver open dataset &ldquo;3-1-1 service requests,&rdquo; API export {EXTRACT_DATE} {EXTRACT_TIME} UTC.</li>
 <li><b>Cohort:</b> requests whose opening timestamp, converted from UTC to Vancouver time, falls in 2025 ({t['tot']} records).</li>
 <li><b>Denominators:</b> outcome shares use closed cases ({t['closed']}); demand counts use all records.</li>
 <li><b>Recorded calendar days to closure:</b> close date minus local opening date; {t['elig']} eligible closed cases. Open cases and {t['ex_neg']} negative values are excluded, not set to zero.</li>
 <li><b>Outcome groups</b> are the analyst&rsquo;s interpretation of published wording. Original values are preserved and mapped below.</li>
 <li><b>Privacy:</b> address and coordinate fields were removed before analysis; geography appears only as totals.</li>
 <li><b>Tools:</b> Python for extraction and profiling; an Excel workbook (Power Query and formulas) recalculates every figure.</li>
 <li><b>Verification:</b> __VERIFY__</li>
</ul>
<h3 style="margin-top:14pt">Closure-reason mapping (all 17 published values)</h3>
<div class="tbl-s">{table(["Published closure reason", "Report category", "Workbook group (analyst-defined)", "Closed", "Open"], num(map_rows, {3, 4}), "map",
                            widths=["34%", "20%", "32%", "8%", "6%"])}</div>
<p class="note">&ldquo;Other outcomes&rdquo; combines workbook groups 4 and 6 for display only. &ldquo;N/A&rdquo; appears only on open cases in 2025.</p>
<p class="src" style="margin-top:12pt"><b>Sources.</b> City of Vancouver. <i>3-1-1 service requests</i> [dataset] and catalogue record.
https://opendata.vancouver.ca/explore/dataset/3-1-1-service-requests/ (accessed {EXTRACT_DATE}). City of Vancouver. <i>Report issues and request services
with Van311.</i> https://vancouver.ca/van311.aspx (accessed September 2026). Contains information licensed under the Open Government Licence &ndash; Vancouver.</p>
</div>{foot(6)}</section>"""

PAGES = [P1, P2, P3, P4, P5, P6]

# ------------------------------------------------------------------ word count (main pages 1-4)
def words(html, drop_tables=True):
    s = re.sub(r"<svg.*?</svg>", " ", html, flags=re.S)
    s = re.sub(r"<footer>.*?</footer>", " ", s, flags=re.S)
    s = re.sub(r'<div class="box src">.*?</div>', " ", s, flags=re.S)
    s = re.sub(r'<div class="legend">.*?</div>', " ", s, flags=re.S)
    s = re.sub(r'<div class="(?:kicker|meta)">.*?</div>', " ", s, flags=re.S)
    if drop_tables:
        s = re.sub(r"<table.*?</table>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&[a-z]+;", " ", s)
    return len(re.findall(r"[A-Za-z0-9][\w.,%'\u2019-]*", s))
wc_narr = [words(pg) for pg in PAGES[:4]]
wc_all = [words(pg, drop_tables=False) for pg in PAGES[:4]]

# ------------------------------------------------------------------ privacy scan, then write HTML and PDF
addr_re = re.compile(r"\b\d{1,5}\s+(?:[NSEW]\s+)?[A-Z0-9][A-Za-z0-9]*\s+(?:ST|AV|AVE|DR|RD|BLVD|WAY|PL|CRES|HWY|MALL|LANE|STREET|AVENUE)\b")
uniq = {a.strip() for a in pd.read_csv(ROOT / "data" / "raw" / "311_requests_raw_window.csv", usecols=["address"], dtype=str,
        keep_default_na=False)["address"] if len(a.strip()) >= 6}
def addr_hits(text):
    return len(addr_re.findall(text)) + sum(1 for a in uniq if a in text)
body = "".join(PAGES)
html_hits = addr_hits(re.sub(r"<[^>]+>", " ", body))
vis = re.sub(r"<[^>]+>", " ", body)
shown = lambda s: re.search(r"(?<![\w.,])" + re.escape(s) + r"(?![\w.,%])", vis) is not None
trace = [x for x in trace if "chart" in x["source"] or x["check"].startswith("n/a (") or shown(x["displayed"])]
verify = (f"every figure is read from the workbook&rsquo;s saved values and listed with its cell in Numbers_Trace_v2.csv ({len(trace):,} entries; "
          f"headline counts also match the independent Python calculation). Option scores are analyst judgement, labelled as such. "
          f"Report text checked against all {len(uniq):,} published address strings: {html_hits} matches.")
body = body.replace("__VERIFY__", verify)
html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>What does closed mean? Vancouver 3-1-1 case study (v2)</title>'
        f"<style>{css}</style></head><body>{body}</body></html>")
HTML.write_text(html, encoding="utf-8")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", HTML.resolve().as_uri()],
               check=True, capture_output=True, timeout=180)
doc = pdfium.PdfDocument(str(PDF))
npages = len(doc)
pdf_hits = addr_hits(" ".join(doc[i].get_textpage().get_text_range() for i in range(npages)))
doc.close()

with open(TRACE, "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=["displayed", "value", "source", "python_reference", "check"])
    wr.writeheader()
    wr.writerows(trace)

HASH_AFTER = {p.name: sha(p) for p in (SRC_PDF, SRC_XLSX)}
stats = {"pages": npages, "words_narrative_p1_4": wc_narr, "words_incl_tables_p1_4": wc_all,
         "trace_rows": len(trace), "trace_python_checked": sum(1 for x in trace if x["check"] == "match"),
         "privacy_html_hits": html_hits, "privacy_pdf_hits": pdf_hits, "addresses_checked": len(uniq),
         "originals_unchanged": HASH_BEFORE == HASH_AFTER, "hashes": HASH_AFTER}
STATS.write_text(json.dumps(stats, indent=2))
print(json.dumps({k: v for k, v in stats.items() if k != "hashes"}, indent=1))
print("main narrative words (p1-4):", sum(wc_narr), "| incl. tables:", sum(wc_all))
assert npages == NPAGES and html_hits == 0 and pdf_hits == 0 and stats["originals_unchanged"]
