# Consistency Check Across Phases 1–15 (behaviour-based)

**Updated:** 2026-09-13, repair pass · **Scope:** outside-in portfolio case study on public information and **synthetic** data.

> The first version of this report checked identifiers and wording only, and it passed while the prototype showed network figures to a regional manager, displayed values for Red data weeks and revealed suppressed counts through a chart. This version is based on **executed behaviour tests** as well as document checks. It does not claim stakeholder approval, real-source reconciliation, production security, usability results or accessibility compliance.

---

## 1. How consistency was checked

| Evidence level | What it establishes | Tool | Result (latest run) |
|---|---|---|---|
| **Seeded-pattern and structural checks** | The synthetic CSV is well formed and contains the deliberate patterns P1–P6 | `build/validate_and_analyze.py` | 32/32 |
| **Independent calculation reconciliation** | Calculation rules behave as documented (unit frames and dataset baselines); the dashboard's JavaScript aggregates and peer groups equal the Python engine for every store-week-KPI | `tests/test_calculations.py`, `tests/test_dashboard_logic.js` | 30 Python tests OK; 15 Node tests pass |
| **UI regression tests** | The rendered page shows the right scope, states, explanations and navigation across four simulated roles, three pages, historical weeks, five viewport widths and real key events | `tests/ui_regression.js` (headless Microsoft Edge) | 83/83 |
| **Document and deck consistency checks** | Documents, deck and README describe the prototype as it behaves; identifier families are contiguous | `build/consistency_scan.py` | 21/21 |
| **Proposed internal UAT** | Business-user acceptance, reconciliation to control totals, security, usability, accessibility audit | Phase 14 plan | **Not executed** |

All automated levels run with `python build/run_tests.py`; results are in `evidence/test-results.md`, and scope and manual checks in `evidence/test-report.md`.

## 2. Contradictions found and resolved in the repair pass

Each row links to the issue register (`issue-register.md`) and to the test that now guards it.

| # | Contradiction (before) | Resolution | Guarded by |
|---|---|---|---|
| 1 | Role scope limited selectors only; Page 1 cards, trend, map and banner used network figures for the Atlantic manager (30 stores, 2 Amber) | Scope applied first on every visual; Atlantic week of 17 Aug 2026 shows 6 stores, 545 exams, 81.0% / 94.6% / 55.8% / 77.3%, 9.1 days, 0 Amber | UI-RRM-01/02, JS-AGG-01, PY-BASE-02 |
| 2 | Regional manager could see named out-of-region peers | Out-of-region peers anonymous; comparison population stated | UI-RRM-03, JS-PEER-02 |
| 3 | Phase 13 and the deck said the role switch "demonstrated" RLS and OLS | "Simulated role view" on the page; documents say simulated; production security kept separate | UI-ALL-01, DOC-01 |
| 4 | Red weeks still received 4-week values from earlier weeks and entered peer groups (SYN-022 60.8%; SYN-027 56.5%, ramp 99.7) | Engine withholds at the Red week; excluded from peers and ramp peers | PY-RED-01…04, UI-RED-01…03 |
| 5 | Windows were "last four rows"; the funnel silently used 1–4 weeks | 4 calendar weeks, minimum 3 usable, selected week must be usable; usable weeks stated | PY-WIN-01/02, UI-FUN-01/02 |
| 6 | The recall chart plotted 1–4 bookings at their true height while the caption said "<5"; PR-04 and the dictionary disagreed on derived rates | Demonstration rule v0.2 documented once; weekly counts shown as text; rates hidden for small numerators | PY-SUP-01…03, JS-SUP-01/02, UI-SUP-01, DOC-02 |
| 7 | Ramp prompt used the latest week although KPI-10 says 4+ weeks (was UC-3) | Trigger after 4 consecutive weeks with an available index | PY-RAMP-01 |
| 8 | Every flag was explained as a peer difference, including rule (b) | Rule-specific explanations | UI-EXC-02, JS-TEXT-01 |
| 9 | Stage grouping dropped the second fulfilment KPI; consecutive weeks undefined | Every triggering KPI listed; runs defined per KPI and computed for every week | PY-EXC-03/04, UI-EXC-04 |
| 10 | "No exceptions" shown where comparisons were unavailable | Flagged · no triggered rule · comparison unavailable (with reasons) · data check | PY-EXC-05, UI-EXC-03 |
| 11 | "Prior 4-week average" averaged weekly rates | Pooled rate over the 4 prior weeks | JS-AGG-03 |
| 12 | Recall parameter called both a rule-set v0.1 parameter and a dictionary v0.2 change (was UC-2) | Exception rule set v0.2 holds the parameter; dictionary v0.2 has a note; banner shows both versions | DOC-08, UI-ALL-02 |
| 13 | KPI-11 combined equal weighting with Σ received ÷ Σ expected | One method with a worked example; simulated values stated | DOC-04 |
| 14 | KPI-07 denominator (orders ready) differed from the analysis (orders placed); KPI-06 negatives vs a "revenue ≥ 0" check | Simplification and generator assumption stated and tested | PY-DEF-01/02 |
| 15 | Conversion and recall provisional periods in Phase 6 vs "all weeks final" hidden in Phase 12 | Finalised-snapshot assumption shown in the dashboard banner and documents | UI-ALL-02, DOC-05 |
| 16 | FACT_SALES paired exam-week purchasers and transaction-week revenue on one row | Separate facts; TQ-06 resolved | DOC-06 |
| 17 | Monday-only "date table"; undefined selector objects; OLS "None" on a measure; DAX not aligned | Daily contiguous calendar; model and relationships defined; OLS per Microsoft documentation; DAX aligned and labelled unexecuted | DOC-07 |
| 18 | Access tests used a Prairies manager while the prototype and baseline use Atlantic (the earlier report described this as "ACC-03 only tests own-region rows") | ACC-03, UAT-10 and US-07 AC2 use Atlantic | DOC-09 |
| 19 | Phase 1–2 said "awaiting approval"; other phases said "Complete" | Status lines say drafted; `feature-status-matrix.md` separates implemented, simulated, specified only and deferred | DOC-10, DOC-11 |
| 20 | Phase 12 said "22 requested columns" | 23 requested + `weeks_since_opening` = 24 | DOC-12 |
| 21 | Deck: "today's network", a FACT tag on "roughly half", "would rank every young store last", "one New store is hidden", undated periods | Dated counts; EV-17 added; inference tag; precise wording; periods on every synthetic figure | DOC-13, DOC-14 |
| 22 | Appendix A1 URLs truncated with ellipses; slide 7 did not show the dashboard | 16 complete hyperlinks; dashboard images with a synthetic walkthrough | DOC-15, DOC-16 |
| 23 | Promised KPI placement (Phase 11) differed from the prototype | Recall and turnaround cards, completed-exams row, ramp index and revenue context added; Phase 11 updated | UI-PLACE-01, DOC-03 |

*Resolved before the repair pass (kept for the record):* Phase 9 "OQ-08" → U-41; AGG_PEER_BENCHMARK and AGG_EXCEPTION_FLAG added to Phase 7; UAT-06 expected results corrected; US-04 AC2 week-specific; a synthetic decline moved away from the real PC Optimum date; Phase 13 wireframe numbers.

## 3. Unresolved items that need a decision or remain limitations

| # | Item | Documents in tension | Current handling (demonstration assumption, not a decision) | Decision owner |
|---|---|---|---|---|
| **UC-1** | **Conversion (KPI-05) for Optometry Partners** | Phase 5 role model and US-04 AC5 omit it; Phases 9–11, 14 and the prototype show it | Shown with a U-41 note (A-46); Phase 5 and US-04 note the open question | SH-02, SH-13 (U-41) |
| **UC-4** | **Exception volume thresholds** | R-18 tolerance vs 228 stage flags in 26 weeks (8.8 per week across 30 stores; recall 41) | Thresholds labelled illustrative; tune in the pilot | SH-03, SH-04 |
| **UC-5** | **Regional visibility for Regional Retail Managers** | US-02 asks to compare regions; U-38 undecided | Own region plus a labelled network reference; other regions hidden (A-45) | SH-13, SH-04 (U-38) |
| **UC-6** | **BO-07 (manual effort) has no baseline** | Deck and Phase 11 list it as a value measure | Stated as "only if a baseline exists"; RTM-04 recommends retiring BO-07 if not confirmed | SH-09, SH-04 |
| **UC-7** | **Complementary suppression** | PR-04 v0.2 applies primary suppression only; US-10 negative scenario asks that suppressed values cannot be recovered from totals | Not implemented; no claim that primary suppression is sufficient | SH-13 (U-39) |
| **UC-8** | **Provisional periods** | Production rule (latest 4 weeks provisional) vs finalised synthetic snapshot | Documented simplification (A-44), visible in the banner | SH-09 |
| **UC-9** | **Partly implemented filters** | FR-02 asks for a week range; FR-12 for persistence between sessions | Single week with 26-week trends; state kept in the URL only | SH-08 |
| **UC-10** | **Converted, relocated or rebranded stores** | FR-03 cohorts assume genuine openings | Open question (TQ-12, U-42); not in the synthetic data | SH-15, SH-04 |

UC-2 (recall parameter versioning) and UC-3 (ramp trigger) from the previous report are resolved (rows 12 and 7 above).

## 4. Positioning check (master-context rules)

| Rule | Status |
|---|---|
| No claim of Specsavers confidential information, systems, performance or reporting problems | ✅ Hypothesis language; slide 3 states the evidence does **not** show inadequate reporting |
| No claim of stakeholder approval | ✅ Status lines say "drafted by the author"; open decisions U-38, U-39, U-41 stay open (DOC-10, DOC-20) |
| Facts, inferences and assumptions distinguished | ✅ Evidence log with dated counts; inference tag on "roughly half"; A/U registers; slide tags |
| Synthetic findings never presented as Specsavers results | ✅ Labels on data, dashboard header, deck slides 3, 7, 8 and A8; every synthetic figure carries its period |
| Prototype features distinguished from production requirements | ✅ Simulated role view on the page; feature-status matrix; DAX labelled unexecuted |
| No identifiable patient information, diagnoses or individual employee performance | ✅ Store-week aggregates only |
| No named Specsavers platforms asserted | ✅ Generic categories; tools cited only as job-posting evidence |
| Numerical targets labelled illustrative; no financial ROI | ✅ |
| Clinical independence and non-causal interpretation explicit | ✅ Rule-specific explanations; prohibited-term tests (JS-TEXT-01, UI-TEXT-01, DOC-19); conversion for Optometry Partners left as an open decision |
| PC Optimum analytics excluded from the MVP | ✅ Phases 1, 4, 11; deck slides 3 and 8 |

## 5. Not checked

Real source systems and control totals; Power BI behaviour (DAX, RLS, OLS); real screen readers, browser zoom UI, physical mobile devices and browsers other than Microsoft Edge; usability with real users; external link availability beyond confirming complete URLs in the deck (links were not clicked from PowerPoint).
