"""Write the v2 design note from the final build statistics."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
S = json.loads((ROOT / "build" / "v2_stats.json").read_text())
OUT = ROOT / "outputs" / "v2_redesign" / "Design_Notes_v2.md"
h = S["hashes"]

note = f"""# Design notes: case study v2 (redesign)

## Files

| File | What it is |
|---|---|
| `Vancouver311_What_Does_Closed_Mean_v2.pdf` | Redesigned report, {S['pages']} pages (4 main pages + 2 appendix pages) |
| `Vancouver311_Case_Study_v2_source.html` | Editable source: one self-contained HTML file with the charts inline as SVG |
| `Numbers_Trace_v2.csv` | Every displayed figure with its workbook cell ({S['trace_rows']} entries) |
| `../../scripts/v2/build_v2.py` | Rebuilds the HTML and PDF from the workbook's saved values |

The originals were read but not changed. Their SHA-256 hashes were checked before and after the build:
- `Vancouver311_What_Does_Closed_Mean_Case_Study.pdf`: `{h['Vancouver311_What_Does_Closed_Mean_Case_Study.pdf'][:16]}...`
- `Vancouver311_Closure_Outcomes_Workbook.xlsx`: `{h['Vancouver311_Closure_Outcomes_Workbook.xlsx'][:16]}...`

## Main design changes

- **Much less text.** v1 pages 1-3 held about 2,300 words. The v2 main pages (1-4) hold {sum(S['words_narrative_p1_4'])} words of narrative
  ({sum(S['words_incl_tables_p1_4'])} including table text). That count excludes chart labels, sources, footers and the kicker and date lines.
- **One idea per page.** Page 1 gives the finding, page 2 the evidence, page 3 the recommendation and page 4 the next steps.
  The appendices hold the department comparison, the method and the full closure-reason mapping.
- **Three main charts, each with a headline and one sentence on why it matters:** closure outcomes (page 1), monthly demand (page 2)
  and the street and sidewalk repair comparison (page 2). The department comparison is kept as a supporting chart in Appendix A.
- **Restrained palette:** navy, teal and neutral greys. Each report category keeps the same colour on every chart. Segments are
  labelled directly, so colour never carries the meaning on its own.
- **Legible charts.** Charts are drawn at their exact printed size, so text renders at 8 pt or larger. v1 charts were scaled down to fit their columns.
- **Qualifications sit next to the finding** as short notes under each chart. There is one limitations list and one sources list.
- **New features:** a "What we can conclude / What needs confirmation" box, and "Already applied in this study" set against
  "Proposed: needs validation with City staff".
- **Removed from the main pages:** the process-hypothesis, root-cause, stakeholder-roles and requirements tables. That detail still lives in the v1 report and the workbook.

## Chart choices

- **Service-family comparison.** Outcome mix by request type in street and sidewalk repair (3,820 / 1,808 / 1,882 closed cases). This is
  the strongest-supported comparison: the subgroups are large and it shows the thesis directly. The duration comparison has smaller subgroups
  (n = 551 vs 904 in sidewalk repair), so it appears as one observation with its sample sizes rather than a chart.
- **Display categories.** The six analyst-defined workbook groups appear as five report categories. "Other outcomes" combines workbook
  groups 4 and 6 (2.5% of closed cases) for display only; Appendix B maps all 17 original reasons to both the category and the workbook group.
- **Label wording.** Workbook group 2 ("Work assigned, referred or continuing") is shown as "Handed off or planned", which says what the record
  shows without implying the work is unfinished. Closed cases carry "Unknown" only; "N/A" appears only on open cases.

## Analytical corrections and changes

1. **Department range.** v1 said "Service provided" ranges from 1.8% to 98.8% across 30 departments. The workbook lists only the 12 largest
   departments, so 98.8% could not be verified against it. v2 uses the workbook range for those 12: 1.8% to 86.7% (Analysis!C56, C51).
2. **Overstated wording.** v1 said a closed case is "often a handoff, not a finished job" and that cases were "handed on, not that the work
   was done." The public record does not show that the work was left undone. v2 says the record shows a handoff or planned work and that completion is not published.
3. **Option 3 rationale.** v1 cited "12 of 7,510" repair closures as "Insufficient info". The workbook holds only the group share
   (insufficient info or unreachable, 0.17%). v2 says "few repair closures record missing information" and cites no count.
4. **Figures not in the workbook removed.** These are the same-day "Unknown" count, open-case ages and the channel split of "Unknown".

The cohort, filters, exclusions and definitions were checked and kept unchanged. No errors were found in them.

## Verification performed

- Every displayed number is read from the workbook's saved values and listed in the trace ({S['trace_rows']} entries).
  Headline counts ({S['trace_python_checked']}) also match the independent Python calculation.
- Option scores are analyst judgement from the v1 report, not workbook figures, and are labelled as such in the report and the trace.
- Privacy: the report HTML and the PDF text were checked against all {S['addresses_checked']:,} published address strings and an address
  pattern. There were {S['privacy_html_hits']} HTML matches and {S['privacy_pdf_hits']} PDF matches.
- All pages were rendered and inspected for clipping, spacing, label legibility, contrast and page breaks.

## Editing

- **Text or layout:** edit `Vancouver311_Case_Study_v2_source.html` and print it from Edge or Chrome (Letter, default margins, background graphics on).
- **Figures:** run `py -3.13 scripts/v2/build_v2.py`. It re-reads the workbook, regenerates the charts, HTML, PDF and trace, and re-runs the checks.
- **Author name:** set `AUTHOR` in `scripts/config.py`.
"""
OUT.write_text(note, encoding="utf-8")
print("wrote", OUT)
