"""Step 7 - Build the case-study report (HTML -> PDF via Edge). All figures are read from
build/results.json and build/reconciliation.json; nothing numeric is typed by hand except the
option scores, which are the analyst's stated preliminary judgement.
"""
import json
import pathlib
import re
import subprocess
from config import GROUPS, SHORT, G1, G2, G3, G4, G5, G6, MAPPING, ADMIN_RULE_TEXT, CANDIDATES, FOCUS_FAMILY, AUTHOR

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "build" / "results.json").read_text())
REC = json.loads((ROOT / "build" / "reconciliation.json").read_text())
CH = ROOT / "build" / "charts"
HTML = ROOT / "build" / "report.html"
PDF = ROOT / "outputs" / "Vancouver311_What_Does_Closed_Mean_Case_Study.pdf"
# AUTHOR comes from config.py

n = lambda x: f"{int(x):,}"
p = lambda x, d=1: f"{x * 100:.{d}f}%"
def svg(name):
    s = (CH / f"{name}.svg").read_text(encoding="utf-8")
    s = re.sub(r"<\?xml[^>]*\?>", "", s)
    s = re.sub(r"<!DOCTYPE[^>]*>", "", s)
    return s

N = R["profile"]["rows"]
OA, OX = R["outcomes_all"], R["outcomes_excl_admin"]
g = {x["group"]: x for x in OA["groups"]}
gx = {x["group"]: x for x in OX["groups"]}
NC, NO = OA["closed"], OA["open"]
DV = R["dept_variation"]
drow = {r["department"]: r for r in DV["rows"]}
pui = drow["DBL - Property Use Inspections"]
ufo = drow["PR - Urban Forestry"]
spmin, spmax = DV["service_provided_min"], DV["service_provided_max"]
U = R["unknown"]
unk_t = {t["type"]: t for t in U["top_types"]}
dur = {x["group"]: x for x in R["duration_by_group"]}
mixed = R["duration_all_mixed"]
OC = R["open_cases"]
D = R["demand"]
F = R["focus"]
fg = {x["group"]: x for x in F["groups"]}
fbt = {x["type"]: x for x in F["by_type"]}
fd = {(x["type"], x["group"]): x for x in F["durations"]}
Q = R["quality"]
A = R["admin"]
CRC = R["cohort_reconciliation"]
chan = {x["value"]: x for x in D["by_channel"]}
fchan = {x["value"]: x for x in F["channels"]}
fco = {x["channel"]: x for x in F["channel_outcomes"]}
fam_dept, fam_types = CANDIDATES[FOCUS_FAMILY]
far = F["local_area_continuing_range"]
fr = {x["value"]: x["count"] for x in F["reasons"]}
sel = {s["family"]: s for s in R["focus_selection"]}
ext_utc = R["extraction"]["extracted_at_utc"].replace("T", " ").replace("+00:00", " UTC")
unk_chan = {x["value"]: x for x in U["by_channel"]}
sidewalk_fa = fd[("Sidewalk Repair Case", "  of which: Further action has been planned")]
sidewalk_sp = fd[("Sidewalk Repair Case", "Service provided")]
all3_fa = fd[("All three types", "  of which: Further action has been planned")]
all3_sp = fd[("All three types", "Service provided")]
all3_ref = fd[("All three types", "  of which: Referred to another service group")]
fullmeet = [s for s in R["focus_selection"] if s["criteria_met"] == 4]
runner = next(s for s in fullmeet if s["family"] != FOCUS_FAMILY)

# ------------------------------------------------------------------ options (analyst judgement)
CRIT = ["Benefit", "Evidence", "Effort", "Risk", "Data", "People", "Scale"]
OPTS = [
    ("1. Maintain the current public-data interpretation", [1, 1, 5, 2, 5, 3, 1],
     "No effort, but &lsquo;closed&rsquo; keeps mixing handoffs with completed work."),
    ("2. Clarify closure and outcome definitions in management reporting", [5, 5, 4, 4, 4, 4, 5],
     "Targets the department-level variation; uses existing fields; no system change."),
    ("3. Improve intake or classification guidance for the focus family", [2, 2, 3, 3, 2, 2, 3],
     f"Weak evidence: {fr.get('Insufficient info', 0)} of {n(F['closed'])} repair closures were &lsquo;Insufficient info&rsquo;; extra questions may burden residents."),
    ("4. Introduce a repeatable outcome and exception-review report", [4, 4, 3, 4, 3, 3, 4],
     "Useful next step, but needs agreed definitions (Option 2) and a standing owner."),
]
totals = [sum(s) for _, s, _ in OPTS]
best = max(range(4), key=lambda i: totals[i])
assert best == 1, "recommendation text below assumes Option 2 scores highest"

def table(headers, rows, cls="", widths=None):
    h = "".join(f"<th{f' style=\"width:{widths[i]}\"' if widths else ''}>{x}</th>" for i, x in enumerate(headers))
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'

PAL = dict(zip(GROUPS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]))
sw = lambda grp: f'<span class="sw" style="background:{PAL[grp]}"></span>'

css = """
@page { size: Letter; margin: 0.36in 0.5in 0.34in 0.5in; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 7.95pt; line-height: 1.31; color: #1d1d1b; margin: 0; }
.page { page-break-after: always; position: relative; height: 10.28in; overflow: hidden; }
.page:last-child { page-break-after: auto; }
.foot { position: absolute; bottom: 0; left: 0; right: 0; font-size: 6.4pt; color: #898781; border-top: 0.5pt solid #e1e0d9; padding-top: 3pt; display: flex; justify-content: space-between; }
h1 { font-size: 19pt; line-height: 1.1; margin: 0 0 2pt; color: #17324d; letter-spacing: -0.2pt; }
.sub { font-size: 11pt; color: #17324d; margin: 0 0 5pt; }
.meta { font-size: 7pt; color: #52514e; margin-bottom: 7pt; }
h2 { font-size: 9.8pt; color: #17324d; margin: 6pt 0 2.5pt; padding-bottom: 1.5pt; border-bottom: 1pt solid #17324d; }
h3 { font-size: 8.2pt; color: #17324d; margin: 4pt 0 2pt; }
p { margin: 0 0 3.5pt; }
.pagehead { font-size: 6.8pt; color: #898781; text-transform: uppercase; letter-spacing: 0.6pt; margin-bottom: 1pt; }
.qbox { border-left: 3pt solid #2a78d6; background: #f3f6f9; padding: 5pt 8pt; margin: 4pt 0 7pt; font-size: 8.6pt; }
.kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6pt; margin: 4pt 0 8pt; }
.kpi { background: #f3f6f9; padding: 6pt 7pt; border-radius: 3pt; }
.kpi .v { font-size: 15pt; font-weight: 700; color: #17324d; line-height: 1.1; }
.kpi .l { font-size: 6.9pt; color: #52514e; line-height: 1.25; margin-top: 2pt; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; }
.cols.w60 { grid-template-columns: 1.4fr 1fr; }
.cols.w40 { grid-template-columns: 1fr 1.2fr; }
ol.find { margin: 0; padding-left: 13pt; font-size: 8.3pt; }
ol.find li { margin-bottom: 4pt; }
.rec { border: 1pt solid #17324d; border-radius: 3pt; padding: 6pt 8pt; background: #fff; }
.rec h3 { margin-top: 0; }
.note { font-size: 6.8pt; color: #52514e; }
.cap { font-size: 6.8pt; color: #52514e; margin: 1pt 0 4pt; }
table { border-collapse: collapse; width: 100%; font-size: 6.85pt; line-height: 1.22; margin: 2pt 0 4pt; }
th { background: #17324d; color: #fff; font-weight: 600; text-align: left; padding: 2pt 3.5pt; vertical-align: bottom; }
td { padding: 1.8pt 3.5pt; border-bottom: 0.5pt solid #e1e0d9; vertical-align: top; }
table.num td:not(:first-child) { text-align: right; font-variant-numeric: tabular-nums; }
table.opts td:last-child { text-align: left; }
tr.hl td { background: #eef4fb; font-weight: 600; }
.sw { display: inline-block; width: 7pt; height: 7pt; border-radius: 1.5pt; margin-right: 3pt; vertical-align: -0.5pt; }
svg { width: 100%; height: auto; display: block; }
.lim { background: #faf6ee; border-left: 3pt solid #eda100; padding: 4pt 8pt; margin-top: 3pt; }
.lim ul { margin: 2pt 0 0; padding-left: 12pt; columns: 2; column-gap: 16pt; } .lim li { margin-bottom: 1.5pt; break-inside: avoid; }
.flow { display: flex; gap: 3pt; align-items: stretch; margin: 3pt 0 4pt; }
.flow div { flex: 1; background: #f3f6f9; border-radius: 3pt; padding: 3pt 4pt; font-size: 6.7pt; line-height: 1.2; }
.flow b { display: block; color: #17324d; font-size: 7pt; }
.tag { font-size: 6.3pt; font-weight: 600; color: #fff; background: #52514e; border-radius: 2pt; padding: 0.5pt 3pt; margin-left: 3pt; vertical-align: 1pt; }
ul.tight { margin: 1pt 0 3pt; padding-left: 12pt; } ul.tight li { margin-bottom: 1.2pt; }
.score5 { font-weight: 700; }
"""

def foot(pg):
    return (f'<div class="foot"><span>Independent outside-in case study using public City of Vancouver open data. '
            f'Not affiliated with or endorsed by the City of Vancouver.</span><span>{AUTHOR} &middot; {pg}</span></div>')

# ================================================================== PAGE 1
p1 = f"""
<section class="page">
<div class="pagehead">Case study &middot; Business analysis &middot; Public-sector service reporting</div>
<h1>What Does Closed Mean?</h1>
<div class="sub">Making Vancouver 3-1-1 Performance Reporting Decision-Ready</div>
<div class="meta">Independent outside-in analysis of the City of Vancouver's public &ldquo;3-1-1 service requests&rdquo; dataset &middot;
Cohort: {n(N)} requests opened on a 2025 Vancouver-local date &middot; Extracted {ext_utc} &middot; Prepared by {AUTHOR}</div>
<div class="qbox"><b>Main question.</b> How can Vancouver's public 3-1-1 data be interpreted and reported so that &ldquo;closed&rdquo; cases
are not automatically mistaken for completed services?</div>
<div class="kpis">
 <div class="kpi"><div class="v">{n(N)}</div><div class="l">requests opened in 2025</div></div>
 <div class="kpi"><div class="v">{p(NC / N)}</div><div class="l">closed by extraction ({n(NC)}); {n(NO)} still open</div></div>
 <div class="kpi"><div class="v">{p(g[G1]['share'])}</div><div class="l">of closed cases recorded as &ldquo;Service provided&rdquo;</div></div>
 <div class="kpi"><div class="v">{p(g[G2]['share'])}</div><div class="l">closed while work was assigned, referred, dispatched, routed or planned</div></div>
 <div class="kpi"><div class="v">{p(g[G5]['share'])}</div><div class="l">of closed cases recorded as &ldquo;Unknown&rdquo;</div></div>
</div>
<h2>Verified findings</h2>
<ol class="find">
<li><b>A closed case is often a handoff, not a finished job.</b> Of {n(NC)} closed cases, {n(g[G1]['count'])} ({p(g[G1]['share'])}) were recorded as
&ldquo;Service provided.&rdquo; Another {n(g[G2]['count'])} ({p(g[G2]['share'])}) closed with a reason showing the work had been assigned to an inspector,
dispatched, referred, routed automatically, or planned for later.</li>
<li><b>What &ldquo;closed&rdquo; means differs sharply by department.</b> Across the {DV['n_departments_min1000_closed']} departments with at least 1,000
closed cases, the &ldquo;Service provided&rdquo; share ranges from {p(spmin['share'])} ({spmin['department'].split(' - ', 1)[1]}, where
{p(pui['top_reason_share'], 0)} of cases close as &ldquo;Assigned to inspector&rdquo;) to {p(spmax['share'])} ({spmax['department'].split(' - ', 1)[1]}).
A single closure rate therefore cannot be compared across departments.</li>
<li><b>Unclear outcomes are concentrated, not widespread.</b> {p(U['top2_share'])} of the {n(U['total'])} &ldquo;Unknown&rdquo; closures come from two
request types: Garbage Bin Request ({p(unk_t['Garbage Bin Request Case']['rate_within_type'], 0)} of its closures) and Parking Enforcement Transfer
({p(unk_t['Parking Enforcement Transfer Case']['rate_within_type'], 0)}). Almost all of them ({n(round(dur[G5]['same_day_share'] * dur[G5]['n']))} of {n(U['total'])}) were closed the day they opened. That points to a
definition question for two intake paths, not a citywide data-quality problem.</li>
<li><b>Closure timing depends on the outcome.</b> Handoff-type closures had a median of {dur[G2]['p50']} recorded day, compared with {dur[G1]['p50']}
days for &ldquo;Service provided.&rdquo; The combined median ({mixed['p50']} days) describes neither. In sidewalk repair, cases closed as
&ldquo;Further action has been planned&rdquo; took longer to close (median {sidewalk_fa['p50']} days) than those recorded as &ldquo;Service provided&rdquo; (median {sidewalk_sp['p50']}).</li>
</ol>
<div class="cols w40" style="margin-top:6pt">
 <div>
  <h3>Closed 2025 cases by outcome group (n = {n(NC)})</h3>
  {svg('ch1_outcome_groups')}
  <div class="cap">Outcome groups are the analyst's interpretation of the City's published closure-reason wording; all 17 original values are preserved and mapped (Appendix).
  Open cases ({n(NO)}) are reported separately.</div>
 </div>
 <div class="rec">
  <h3>Recommendation: pilot outcome-aware closure reporting</h3>
  <p><b>Option 2 &ndash; clarify closure and outcome definitions in management reporting</b>, tested on one service family:
  street and sidewalk repair ({n(F['records'])} requests in 2025).</p>
  <ul class="tight">
   <li>Report closed cases by agreed outcome group, never as one &ldquo;closed&rdquo; figure.</li>
   <li>Always show open cases and unclear outcomes alongside, with counts and denominators.</li>
   <li>Publish each metric's definition, exclusions and data date with the report.</li>
  </ul>
  <p><b>Why this option:</b> it scored highest in the options assessment ({totals[1]} of 35). It rests on the strongest evidence and needs no system change.
  It is also the prerequisite for a recurring exception-review report (Option 4), the natural second phase.</p>
  <p class="note">This is an outside-in proposal. Public data cannot show how the City's internal management reports already treat these
  outcomes, so the first pilot step is validation with City staff.</p>
 </div>
</div>
<h2>How the analysis was done</h2>
<div class="flow">
 <div><b>1. Frame</b>One decision question; 2025 local-date cohort; closed cases as the outcome denominator.</div>
 <div><b>2. Profile</b>13 published fields checked; 19 data-quality checks logged; UTC and date-only fields resolved.</div>
 <div><b>3. Map</b>All 17 closure reasons mapped to six analyst-defined outcome groups, with a sensitivity test.</div>
 <div><b>4. Analyse</b>Demand, outcomes by department and channel, closure timing, and one focus service family.</div>
 <div><b>5. Recommend</b>Four options scored on seven criteria; a phased pilot with measures and decision rules.</div>
</div>
<p class="note">Every figure is reproduced in the accompanying Excel workbook (Power Query and formulas) and reconciled with the Python analysis: {n(REC['figures_compared'])} figures compared, {REC['differences']} differences.</p>
{foot("Page 1 of 5")}
</section>"""

# ================================================================== PAGE 2
dept_rows_sorted = sorted(DV["rows"], key=lambda r: -r["closed"])[:12]
sens_rows = [[f"{sw(G)}{SHORT[G]}", p(g[G]['share']), p(gx[G]['share']), f"{(gx[G]['share'] - g[G]['share']) * 100:+.1f}"]
             for G in (G1, G2, G3, G5)]
dur_rows = [[f"{sw(x['group'])}{x['short']}", n(x['n']), x['p50'], x['p75'], x['p90'], p(x['same_day_share'], 0)] for x in R["duration_by_group"] if x["n"] >= 30]
dur_rows.append(["<b>All outcomes mixed</b>", f"<b>{n(mixed['n'])}</b>", f"<b>{mixed['p50']}</b>", f"<b>{mixed['p75']}</b>", f"<b>{mixed['p90']}</b>", f"<b>{p(mixed['same_day_share'], 0)}</b>"])
p2 = f"""
<section class="page">
<div class="pagehead">Findings &middot; Citywide</div>
<h2 style="margin-top:0">1. Recorded demand: large and concentrated</h2>
<div class="cols">
 <div>
  <p>{n(N)} requests were opened in 2025, between {n(D['month_min']['count'])} (December) and {n(D['month_max']['count'])} (July) per month.
  Demand is concentrated: five departments recorded {p(D['top5_depts_share'])} of all requests (Sanitation Services alone {p(D['sanitation_share'])}),
  and the ten largest request types account for {p(D['top10_types_share'])}.</p>
  <p>Requests arrived mainly by web ({p(chan['WEB']['share'])}), phone ({p(chan['Phone']['share'])}) and the mobile app ({p(chan['Mobile App']['share'])}).</p>
  <p class="note">Counts are <i>recorded</i> demand. High volume can reflect more assets, people or awareness, so it is not treated as a sign of poor
  performance. One year of data cannot establish a seasonal pattern.</p>
 </div>
 <div>
  <h3>Requests by local opening month, 2025</h3>
  {svg('ch3_monthly_demand')}
 </div>
</div>
<h2>2. The same status means different things in different departments</h2>
<h3>Closed-case outcome mix for the 12 departments with the most closed cases (together {p(sum(r['closed'] for r in dept_rows_sorted) / NC)} of closed cases)</h3>
{svg('ch2_department_mix')}
<div class="cap">Each bar sums to 100% of that department's closed 2025 cases. Colour follows the analyst-defined outcome group throughout this report.</div>
<p><b>What a manager should take from this:</b> in Property Use Inspections, {p(pui['top_reason_share'], 0)} of closures are &ldquo;Assigned to inspector,&rdquo;
and in Urban Forestry {p(ufo['top_reason_share'], 0)} are &ldquo;Further action has been planned.&rdquo; For these services, a high closure count shows that
cases were <i>handed on</i>, not that the work was done. Comparing closure rates across departments without these distinctions would mislead.</p>
<div class="cols">
 <div>
  <h2>3. &ldquo;Unknown&rdquo; comes from two intake paths</h2>
  {table(["Request type", "Closed as Unknown", "Rate in type", "Share of all Unknown"],
         [[t['type'].replace(' Case', ''), n(t['count']), p(t['rate_within_type']), p(t['count'] / U['total'])] for t in U['top_types'][:3]], cls="num")}
  <p class="note">The remaining {n(U['total'] - U['top2_count'])} &ldquo;Unknown&rdquo; closures are spread across other types. They sit under phone
  ({p(unk_chan['Phone']['share'], 0)}) and chat ({p(unk_chan.get('Chat', {'share': 0})['share'], 0)}) because those two types arrive there, so channel differences mostly reflect request-type mix.</p>
  <h2>4. Sensitivity: administrative/internal-sounding types</h2>
  <p class="note">Four types match a transparent name rule ({A['rule'].rstrip('.')}). They are {p(A['share'])} of records ({n(A['rows'])}) but hold
  {p(R['admin_share_of_unknown'], 0)} of &ldquo;Unknown&rdquo; and {p(R['auto_closed']['admin_sounding_share'], 0)} of automatic closures. They are flagged for validation, not assumed internal.</p>
  {table(["Outcome group (closed cases)", f"All ({n(NC)})", f"Excl. flagged ({n(OX['closed'])})", "Change (pts)"], sens_rows, cls="num")}
 </div>
 <div>
  <h2>5. Time to closure varies by outcome</h2>
  <p class="note">Recorded calendar days from local opening date to recorded close date, eligible closed cases, nearest-rank percentiles. Not service-delivery or resolution time.</p>
  {table(["Outcome group", "n", "Median", "p75", "p90", "Same day"], dur_rows, cls="num")}
  <p class="note">Excluded: {n(OC['count'])} open cases and {Q['negative_days']} cases whose close date precedes the local opening date (counted, not set to zero).
  No published service standard was located in the public sources consulted, so no case is called &ldquo;late.&rdquo;</p>
  <p><b>Open cases.</b> {n(OC['count'])} requests ({p(OC['share'])}) were still open at extraction, aged {OC['age_min']}&ndash;{OC['age_max']} days (median {OC['age_p50']}).
  The largest group is in {OC['top_departments'][0]['department']} ({n(OC['top_departments'][0]['count'])}, {p(OC['top_departments'][0]['rate'])} of its 2025 requests).
  Closed-case durations do not describe these requests, so they are reported separately.</p>
 </div>
</div>
{foot("Page 2 of 5")}
</section>"""

# ================================================================== PAGE 3
selrows = []
for name in [FOCUS_FAMILY, "Street lights and signs", "Bin requests"]:
    s = sel[name]
    selrows.append([("<b>" + name + " (selected)</b>") if name == FOCUS_FAMILY else name, n(s['records']), s['groups_ge5pct'],
                    p(s['continuing'], 0), p(s['unclear'], 0), f"{s['criteria_met']} of 4"])
fam_sel = sel[FOCUS_FAMILY]
proc = [
    ["1. Resident submits", f"Repair requests: app {p(fchan['Mobile App']['count'] / F['records'], 0)}, web {p(fchan['WEB']['count'] / F['records'], 0)}, phone {p(fchan['Phone']['count'] / F['records'], 0)}. Van311 allows submission without an account and status checks.", "Is the same detail captured on every channel?", "Intake walkthrough; form review"],
    ["2. Recorded and classified", f"{R['profile']['n_request_types']} request types across {R['profile']['n_departments']} departments; 3 obsolete &lsquo;ZZ OLD&rsquo; types still used.", "How are borderline repairs classified?", "3-1-1 Contact Centre"],
    ["3. Assigned, referred, dispatched", f"{p(fg[G2]['share'])} of closed repair cases close at a handoff or with work planned.", "Does a handoff create a linked work order?", "Process walkthrough"],
    ["4. Department acts", "Not visible in public data.", "Where is repair completion recorded?", "Service-owner workshop"],
    ["5. Status and reason updated", "Last known status only; 17 closure reasons citywide.", "Who sets the reason, and when?", "CRM configuration review"],
    ["6. Used for reporting", "One status per case in the public data.", "Do reports separate planned from done?", "Report inventory; user interviews"],
]
hyp = [
    [f"Street repair {p(fbt['Street Repair Case'][SHORT[G2]], 0)} and sidewalk repair {p(fbt['Sidewalk Repair Case'][SHORT[G2]], 0)} of closures are handoffs or planned work.",
     "Case closes when repair is scheduled; completion tracked elsewhere.", "Lifecycle rules; linked work orders.", "Streets Operations", "Report &lsquo;scheduled&rsquo; separately; link completion."],
    [f"&ldquo;Unknown&rdquo; on {p(unk_t['Garbage Bin Request Case']['rate_within_type'], 0)} of Garbage Bin Request and {p(unk_t['Parking Enforcement Transfer Case']['rate_within_type'], 0)} of Parking Enforcement Transfer closures, almost all same-day.",
     "A default value set by an intake or integration path.", "Field configuration; integration mapping.", "Sanitation, Parking; CRM admin", "Replace the default, or exclude it from outcome reporting."],
    [f"Property Use Inspections: {p(pui['top_reason_share'], 0)} of closures are &ldquo;Assigned to inspector&rdquo;.",
     "The case records the handoff; the inspection is tracked elsewhere.", "Inspection records linked to cases.", "Inspection managers", "Report the inspection result as the outcome."],
    [f"{n(Q['duplicate_looking_rows'])} duplicate-looking records, mostly bin requests.",
     "One case per bin, or repeat submissions.", "Case-creation rules.", "Sanitation; Van311 team", "Agree a demand-counting rule."],
]
p3 = f"""
<section class="page">
<div class="pagehead">Focused analysis &middot; Street and sidewalk repair &middot; Process implications</div>
<h2 style="margin-top:0">6. Focus family: street and sidewalk repair ({fam_dept})</h2>
<div class="cols w60">
 <div>
  <p><b>Why this family.</b> Seven candidates were tested on four criteria: 5,000+ records; three or more outcome groups at &ge;5%; unclear outcomes &le;5%;
  2&ndash;5 comparable request types. Two met all four. Street and sidewalk repair was chosen because it has far more handoff or planned-work closures
  ({p(fam_sel['continuing'], 0)} vs {p(runner['continuing'], 0)}), the question under study, and is clearly about service delivery.</p>
  {table(["Candidate", "Records", "Groups &ge;5%", "Handoff / planned", "Unclear", "Criteria"], selrows, cls="num")}

 </div>
 <div>
  <h3>Outcome mix by request type (closed cases)</h3>
  {svg('ch4_family_mix')}
  <p><b>What the records show.</b> {n(F['records'])} requests; {n(F['closed'])} closed, {F['open']} open. {p(fg[G1]['share'])} of closures were recorded as
  &ldquo;Service provided&rdquo;. {p(fg[G2]['share'])} were handoffs or planned work: {n(fr['Further action has been planned'])} &ldquo;Further action has been planned&rdquo; and
  {n(fr['Referred to another service group'])} referrals. Another {p(fg[G3]['share'])} recorded no service or no action. Potholes are mostly recorded as provided,
  while {p(fbt['Street Repair Case'][SHORT[G2]], 0)} of street-repair closures are handoffs or planned work.</p>
 </div>
</div>
<div class="cols w40">
 <div>
  <h3>Recorded days to closure by outcome (median / p75 / p90)</h3>
  {svg('ch5_family_durations')}
  <div class="cap">Filled dot = median, tick = 75th, open dot = 90th percentile. Eligible closed cases; {F['open']} open cases excluded.</div>
 </div>
 <div>
  <p><b>Planned-work closures are not quick administrative closures.</b> In sidewalk repair, &ldquo;Further action has been planned&rdquo; cases closed at a
  median of {sidewalk_fa['p50']} days (p90 {sidewalk_fa['p90']}), against {sidewalk_sp['p50']} (p90 {sidewalk_sp['p90']}) for &ldquo;Service provided&rdquo;. Across all three types the medians are equal
  ({all3_fa['p50']} days) but the p90 is {all3_fa['p90']} vs {all3_sp['p90']}. Referrals closed fastest (median {all3_ref['p50']}).
  So the case record closes after review, but whether and when the planned repair was finished is not visible in the public data.</p>
  <p><b>Channels and areas.</b> Handoff/planned shares were similar across the app ({p(fco['Mobile App'][SHORT[G2]])}), web ({p(fco['WEB'][SHORT[G2]])}) and phone
  ({p(fco['Phone'][SHORT[G2]])}), so intake channel does not appear to drive the pattern. Across the {far['areas']} local areas ({far['min_closed_per_area']}+ closed cases each), the
  share ranged from {p(far['min'])} to {p(far['max'])}. That is a description, not a ranking, because street stock and workload differ.
  {p(F['local_area_missing_share'])} of repair requests had no local area.</p>
 </div>
</div>
<h2>7. Current-state process hypothesis <span class="tag">To validate</span></h2>
{table(["Stage", "Public evidence", "Reporting or process question", "Confirm through"], proc, widths=["16%", "44%", "23%", "17%"])}
<h2>8. Root-cause hypotheses (not proven causes)</h2>
{table(["Observation", "Possible explanation", "Evidence required", "Consult", "Action if confirmed"], hyp, widths=["30%", "22%", "15%", "14%", "19%"])}
<div class="lim"><b>Data limitations: what the public data cannot show</b>
<ul>
 <li><b>Outside-in only:</b> no interviews, internal documents or system access; stages and causes above are hypotheses.</li>
 <li><b>Closure reasons describe the case record</b>, not a verified outcome; even &ldquo;Service provided&rdquo; needs definition.</li>
 <li><b>No case identifier; last known status only:</b> referrals, reopenings and true duplicates can't be traced.</li>
 <li><b>Close field is a date:</b> durations are calendar days, not elapsed or resolution time.</li>
 <li><b>One year, live source:</b> the portal refreshes daily; figures are tied to the {ext_utc} extract.</li>
 <li><b>Location gaps:</b> local area is blank for {p(Q['missing_local_area'] / N)} of requests, mostly types without a street location.</li>
</ul></div>
{foot("Page 3 of 5")}
</section>"""

# ================================================================== PAGE 4
opt_rows = []
for i, (name, s, why) in enumerate(OPTS):
    cells = [f"<b>{name}</b>" if i == best else name] + [f'<span class="score5">{v}</span>' if v == 5 else str(v) for v in s]
    cells += [f"<b>{totals[i]}</b>", why]
    opt_rows.append(cells)
opt_tbl = table(["Option"] + CRIT + ["Total /35", "Rationale"], opt_rows, cls="num opts",
                widths=["27%"] + ["5.4%"] * 7 + ["6%", "29%"])
opt_tbl = opt_tbl.replace("<tr><td><b>2.", '<tr class="hl"><td><b>2.')
roles = [["Sponsor (data and analytics leadership)", "Approves scope; decides expand or stop."],
         ["Service owner (Streets Operations)", "Owns outcome definitions and exception follow-up."],
         ["3-1-1 intake lead", "Confirms classification and routing behaviour."],
         ["Reporting / CRM analyst", "Maintains the mapping table and report."],
         ["Business analyst", "Facilitates, documents requirements, runs the evaluation."],
         ["Residents (indirect)", "Anticipated need: status wording that says whether work is done. Not consulted here."]]
req = [
    ["BR1", "Report closed cases by agreed outcome group, not one &lsquo;closed&rsquo; figure.", "Split, counts and denominator on every view."],
    ["BR2", "Show open cases and unclear outcomes alongside.", "Open count and &lsquo;Unknown / N/A&rsquo; share shown."],
    ["BR3", "State each metric's definition, exclusions and data date.", "Definitions panel approved by service owner."],
    ["DR1", "Keep original closure reasons; control grouping in a mapping table.", "Figures trace to source; unmapped = 0 or flagged."],
    ["DR2", "Report durations within request type and outcome group.", "n and exclusions shown with each duration."],
    ["DR3", "Flag exceptions (open with reason, close before open, Unknown, duplicate-looking).", "Exception counts reconcile to quality summary."],
]
plan = [
    ["1. Validate", "Weeks 1&ndash;4", "Confirm what each repair closure reason means; walk through the case lifecycle; find where completion is recorded; confirm any service standards.", "Service owner, 3-1-1 lead, reporting analyst, BA"],
    ["2. Design", "Weeks 5&ndash;8", "Agree outcome groups and definitions; mock up the report; set acceptance criteria; measure baselines.", "Service owner, reporting analyst, BA"],
    ["3. Pilot", "3 monthly cycles", "Produce the outcome-aware report; review exceptions with the service owner; log definition questions.", "Operational team, reporting analyst"],
    ["4. Evaluate", "1 month", "Test usefulness with users; review effort, exception volume and definition stability.", "BA, pilot users"],
    ["5. Decide", "End of pilot", "Expand, modify or stop against the criteria below.", "Sponsor, service owner"],
]
p4 = f"""
<section class="page">
<div class="pagehead">Options &middot; Recommendation &middot; Future state &middot; Pilot plan</div>
<h2 style="margin-top:0">9. Options analysis <span class="tag">Preliminary, outside-in</span></h2>
<p class="note"><b>Benefit</b> decision-making benefit &middot; <b>Evidence</b> evidence strength &middot; <b>Effort</b> implementation effort &middot; <b>Risk</b> operational risk &middot; <b>Data</b> data dependency &middot; <b>People</b> stakeholder impact &middot; <b>Scale</b> scalability. Scored 1&ndash;5; <b>5 is always the favourable end</b> (for example, lowest effort or lowest risk). Equal weights. Preliminary outside-in judgement for stakeholder validation.</p>
{opt_tbl}
<div class="cols">
 <div>
  <h2>10. Recommendation and future state</h2>
  <p><b>Pilot Option 2 in street and sidewalk repair.</b> The evidence is about how closure outcomes are <i>recorded and read</i>, not how requests are submitted.
  Clear definitions give the largest decision benefit for the least effort and risk, and they are the foundation Option 4 would need. Option 4 becomes phase 2 if the pilot succeeds.</p>
  <h3>Proposed future-state reporting process</h3>
  <div class="flow">
   <div><b>1. Preserve</b>Original status and closure reason kept.</div>
   <div><b>2. Classify</b>Agreed mapping assigns outcome groups.</div>
   <div><b>3. Flag</b>Exceptions and unmapped values listed.</div>
   <div><b>4. Review</b>Service owner reviews monthly.</div>
   <div><b>5. Report</b>Outcome split, open cases, definitions.</div>
  </div>
  <h3>Stakeholder roles (proposed)</h3>
  {table(["Role", "Responsibility in the pilot"], roles, widths=["42%", "58%"])}
 </div>
 <div>
  <h3>Business (BR) and data/reporting (DR) requirements</h3>
  {table(["ID", "Requirement", "Acceptance check"], req, widths=["8%", "50%", "42%"])}
  <div class="cols" style="gap:8pt">
   <div><h3>Risks</h3><ul class="tight">
    <li>Definitions contested between teams.</li>
    <li>Outcome splits misread as rankings.</li>
    <li>&lsquo;Service provided&rsquo; may not mean completed.</li>
    <li>Extra reporting workload.</li></ul></div>
   <div><h3>Dependencies</h3><ul class="tight">
    <li>Service-owner time for validation.</li>
    <li>Access to case history or work orders.</li>
    <li>Reporting-tool and 3-1-1 support.</li>
    <li>Privacy review before any publication.</li></ul></div>
  </div>
  <p class="note"><b>Change and communication:</b> brief managers before the first cycle on why the &lsquo;closed&rsquo; view changes; issue a one-page glossary; show old and new
  views side by side; present it as a clarification, not a correction of past reporting.</p>
 </div>
</div>
<h2>11. Phased pilot plan (indicative)</h2>
{table(["Phase", "Timing", "Activities", "Participants"], plan, widths=["10%", "11%", "56%", "23%"])}
<div class="cols">
 <div>
  <h3>Success measures</h3>
  <ul class="tight">
   <li>Share of repair closures with an agreed, documented reason definition.</li>
   <li>Share of report users who correctly tell completed from planned or handed-off work.</li>
   <li>Share closed as &lsquo;Unknown / N/A&rsquo; or unmapped (2025 baseline: {p(fg[G5]['share'])} repairs; {p(g[G5]['share'])} citywide).</li>
   <li>Staff time per monthly report; share of exceptions reviewed each cycle.</li>
  </ul>
  <p class="note">No numerical targets are proposed. Baselines are measured in phases 1&ndash;2; the sponsor and service owner then agree targets before the pilot runs.</p>
 </div>
 <div>
  <h3>Decision criteria at the end of the pilot</h3>
  <ul class="tight">
   <li><b>Expand</b> (then consider Option 4) if definitions stay stable for three cycles, users find the report more useful, and effort is acceptable to the service owner.</li>
   <li><b>Modify</b> if definitions are contested, more sub-groups are needed, or effort is higher than expected.</li>
   <li><b>Stop</b> if repair completion cannot be recorded or linked well enough to support the distinction, or users see no decision benefit.</li>
  </ul>
 </div>
</div>
{foot("Page 4 of 5")}
</section>"""

# ================================================================== PAGE 5 - appendix
maprows = [[m["closure_reason_original"], f"{sw(m['outcome_group'])}{SHORT[m['outcome_group']]}", n(m["closed_2025"]), n(m["open_2025"])] for m in R["mapping"]]
checks = ["__PRIV__" if c.startswith("Privacy scan") else c for c in REC["checks_for_report"]]
assert all3_fa["p50"] == all3_sp["p50"], "page 3 text says the medians are equal"
p5 = f"""
<section class="page">
<div class="pagehead">Appendix &middot; Methodology and validation</div>
<h2 style="margin-top:0">A1. Data, cohort and definitions</h2>
<div class="cols">
 <div>
  <p><b>Source.</b> City of Vancouver Open Data Portal, &ldquo;3-1-1 service requests&rdquo;, accessed through the Explore API v2.1 CSV export on {ext_utc}
  (dataset last modified {R['extraction']['dataset_modified'].replace('T', ' ').replace('+00:00', ' UTC')}). Contains information licensed under the Open Government Licence &ndash; Vancouver.</p>
  <p><b>Filters.</b> The API filter was opening timestamp &ge; 2024-12-31 00:00 UTC and &lt; 2026-01-02 00:00 UTC ({n(CRC['raw_window_rows'])} rows). Records were then kept
  if the opening timestamp, converted to America/Vancouver, fell on a 2025 local date: <b>{n(N)} records</b>. This is {CRC['local_2025_but_utc_2026'] - CRC['utc_2025_but_local_2024']} more than the UTC-year count
  ({n(CRC['utc_year_2025_rows'])}): {CRC['local_2025_but_utc_2026']} requests opened on the evening of 31 Dec 2025 (local) were added and {CRC['utc_2025_but_local_2024']} from the evening of 31 Dec 2024 (local) were removed.</p>
  <p><b>Time zones.</b> Opening timestamps carry a +00:00 offset. After conversion, {p(R['date_behaviour']['peak_local_hours_share_9_to_16'], 0)} of requests open between 9:00 and 16:59 local time,
  which is consistent with true UTC. The close field is a date only. For evening automatic closures it matches the local opening date {p(R['date_behaviour']['evening_auto_closed_close_eq_local_open_date'], 0)} of the time
  and the UTC date {p(R['date_behaviour']['evening_auto_closed_close_eq_utc_open_date'], 0)}, so it is treated as a local calendar date.</p>
  <p><b>Recorded calendar days to closure</b> = close date &minus; local opening date, for closed cases with a close date and a non-negative result
  ({n(R['duration_exclusions']['Eligible'])} eligible; {n(OC['count'])} open and {Q['negative_days']} negative excluded). <b>Percentiles</b> use the nearest-rank method: the smallest
  number of days within which at least p% of eligible cases closed. Shown only where n &ge; 30.</p>
  <p><b>Denominators.</b> Outcome shares use closed cases ({n(NC)}); demand shares use all records ({n(N)}).</p>
  <p><b>Flags.</b> <i>Administrative/internal-sounding:</i> {ADMIN_RULE_TEXT} &lsquo;Disposal Facility &ndash; Transfer Station Inquiry Case&rsquo; is deliberately not flagged.
  <i>Duplicate-looking:</i> all published fields identical except the last-modified timestamp ({n(Q['duplicate_looking_rows'])} records in {n(Q['duplicate_looking_groups'])} groups). These can't be confirmed as duplicates because no case identifier is published.
  <i>Obsolete labels:</i> {Q['zz_old_rows']} records use &lsquo;ZZ OLD&rsquo; types.</p>
  <p><b>Privacy.</b> Address, coordinate and geometry fields were removed before analysis outputs were produced. Geography is reported only as local-area totals.</p>
 </div>
 <div>
  <h3>Closure-reason mapping (analyst-defined; all 17 original values preserved)</h3>
  {table(["Original closure reason", "Outcome group", "Closed", "Open"], maprows, cls="num")}
  <p class="note">'N/A' appears only on open cases in 2025. &lsquo;Alternate Service Required&rsquo; and &lsquo;Information received&rsquo; are ambiguous and are placed in
  &lsquo;Other &ndash; requires review&rsquo;. The workbook's Closure_Outcome_Mapping sheet gives a rationale and a validation question for each value.</p>
 </div>
</div>
<h2>A2. Validation and reconciliation performed</h2>
<ul class="tight">
{''.join(f'<li>{c}</li>' for c in checks)}
</ul>
<h2>A3. Tools and reproducibility</h2>
<p>Python (pandas) scripts download, profile, clean and analyse the extract; they produce every figure and chart. The Excel workbook rebuilds the grouped data with Power Query
(the outcome mapping is applied from a table in the workbook) and recalculates all analysis figures as formulas, which are then compared with the Python results.
Scripts, the cleaned extract (no location fields) and the workbook are provided with this report.</p>
<h2>A4. Sources</h2>
<ul class="tight">
 <li>City of Vancouver. <i>3-1-1 service requests</i> [dataset]. Open Data Portal. https://opendata.vancouver.ca/explore/dataset/3-1-1-service-requests/ (accessed {ext_utc}).</li>
 <li>City of Vancouver. Dataset catalogue record and field descriptions, including notes on withheld addresses, geocoding gaps, &lsquo;ZZ &ndash; OLD&rsquo; obsolete types and daily refresh of records from 17 Aug 2022.
 https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/3-1-1-service-requests</li>
 <li>City of Vancouver. <i>Report issues and request services with Van311.</i> https://vancouver.ca/van311.aspx (accessed September 2026): used only for resident-facing submission and status-check features.</li>
</ul>
<p class="note">No interviews, internal documents, service standards or stakeholder feedback were used. All process descriptions, stakeholder needs, option scores and pilot details are proposals for validation.</p>
{foot("Page 5 of 5")}
</section>"""

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>What Does Closed Mean? - Vancouver 3-1-1 case study</title>
<style>{css}</style></head><body>{p1}{p2}{p3}{p4}{p5}</body></html>"""
import pandas as pd
import pypdfium2 as pdfium
addr_re = re.compile(r"\b\d{1,5}\s+(?:[NSEW]\s+)?[A-Z0-9][A-Za-z0-9]*\s+(?:ST|AV|AVE|DR|RD|BLVD|WAY|PL|CRES|HWY|MALL|LANE|STREET|AVENUE)\b")
uniq = {a.strip() for a in pd.read_csv(ROOT / "data" / "raw" / "311_requests_raw_window.csv", usecols=["address"], dtype=str,
        keep_default_na=False)["address"] if len(a.strip()) >= 6}
def addr_hits(text):
    return len(addr_re.findall(text)) + sum(1 for a in uniq if a in text)
visible = re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>", " ", html, flags=re.S))
html_hits = addr_hits(visible)
html = html.replace("__PRIV__", f"Privacy scan: no address, coordinate or geometry field in the cleaned CSV or workbook data. Workbook cells and this report's text were "
                    f"checked against an address pattern and all {len(uniq):,} distinct published address strings: {REC['privacy']['workbook_address_like_cells'] + html_hits} matches.")
HTML.write_text(html, encoding="utf-8")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
subprocess.run([edge, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}",
                HTML.resolve().as_uri()], check=True, capture_output=True, timeout=180)
raw = PDF.read_bytes()
print("PDF:", PDF, "bytes", len(raw), "pages", len(re.findall(rb"/Type\s*/Page[^s]", raw)))
doc = pdfium.PdfDocument(str(PDF))
pdf_hits = addr_hits(" ".join(doc[i].get_textpage().get_text_range() for i in range(len(doc))))
print("privacy: report html hits", html_hits, "| pdf text hits", pdf_hits, "| distinct addresses checked", len(uniq))
doc.close()
assert html_hits == 0 and pdf_hits == 0
