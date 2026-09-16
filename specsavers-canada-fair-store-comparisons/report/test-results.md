# Automated Test Results (generated)

**Run:** 2026-09-13 13:53 · **Overall:** PASS · **Command:** `python build/run_tests.py`

**Environment:** Python 3.11.0 (pandas 3.0.5, numpy 2.4.6); Node v24.15.0; Microsoft Edge 153.0.4234.32; Windows 10

> Synthetic data only. These are automated prototype checks. They are not Power BI tests, not user acceptance testing and not an accessibility audit. See `evidence/test-report.md` for scope and manual checks.

| # | Step | Command | Result | Summary | Seconds |
|---|---|---|---|---|---|
| 0 | Reproducibility: regenerated CSV is byte-identical (seed 20260913) | `python build/generate_synthetic.py` | PASS | SHA-256 unchanged | 0.1 |
| 1 | Structural and seeded-pattern checks | `python build/validate_and_analyze.py` | PASS | Checks passed: 32/32 | 4.3 |
| 2 | Calculation regression tests (Python) | `python -m unittest discover -s tests -p "test_*.py"` | PASS | Ran 30 tests; all OK | 7.7 |
| 3 | Dashboard logic and reconciliation tests (Node) | `node --test tests/test_dashboard_logic.js` | PASS | pass 15, fail 0 | 0.3 |
| 4 | Build dashboard; generated page embeds the current template, logic and data | `python build/build_mockup.py` | PASS | consistent | 0.1 |
| 5 | Rendered-page regression tests (headless Edge) | `node tests/ui_regression.js` | PASS | UI checks passed: 83/83 | 19.4 |
| 6 | Document and deck consistency checks | `python build/consistency_scan.py` | PASS | Document checks passed: 21/21 | 0.4 |

## Calculation regression tests (Python)

```
test_PY_BASE_01_network_latest_week (test_calculations.Baselines.test_PY_BASE_01_network_latest_week) ... ok
test_PY_BASE_02_atlantic_latest_week (test_calculations.Baselines.test_PY_BASE_02_atlantic_latest_week) ... ok
test_PY_FUN_01_syn014_funnel_window (test_calculations.Baselines.test_PY_FUN_01_syn014_funnel_window) ... ok
test_PY_DEF_01_turnaround_simplification_documented_and_applied (test_calculations.DefinitionsAndSafety.test_PY_DEF_01_turnaround_simplification_documented_and_applied) ... ok
test_PY_DEF_02_negative_revenue_allowed_by_calculation (test_calculations.DefinitionsAndSafety.test_PY_DEF_02_negative_revenue_allowed_by_calculation) ... ok
test_PY_JSON_01_summary_is_strict_json_and_red_rows_null (test_calculations.DefinitionsAndSafety.test_PY_JSON_01_summary_is_strict_json_and_red_rows_null) ... ok
test_PY_SAFE_01_empty_and_zero_denominators (test_calculations.DefinitionsAndSafety.test_PY_SAFE_01_empty_and_zero_denominators) ... ok
test_PY_EXC_01_rule_a_boundaries (test_calculations.Exceptions.test_PY_EXC_01_rule_a_boundaries) ... ok
test_PY_EXC_02_rule_b_three_consecutive_weeks_and_interruption (test_calculations.Exceptions.test_PY_EXC_02_rule_b_three_consecutive_weeks_and_interruption) ... ok
test_PY_EXC_03_stage_grouping_keeps_every_kpi (test_calculations.Exceptions.test_PY_EXC_03_stage_grouping_keeps_every_kpi) ... ok
test_PY_EXC_04_consecutive_runs_defined_every_week (test_calculations.Exceptions.test_PY_EXC_04_consecutive_runs_defined_every_week) ... ok
test_PY_EXC_05_exception_states (test_calculations.Exceptions.test_PY_EXC_05_exception_states) ... ok
test_PY_EXC_06_recall_eligibility (test_calculations.Exceptions.test_PY_EXC_06_recall_eligibility) ... ok
test_PY_PEER_01_fallback (test_calculations.Peers.test_PY_PEER_01_fallback) ... ok
test_PY_PEER_02_suppression_below_floor_and_self_excluded (test_calculations.Peers.test_PY_PEER_02_suppression_below_floor_and_self_excluded) ... ok
test_PY_PEER_03_dataset_cases (test_calculations.Peers.test_PY_PEER_03_dataset_cases) ... ok
test_PY_PEER_04_quantile_matches_pandas (test_calculations.Peers.test_PY_PEER_04_quantile_matches_pandas) ... ok
test_PY_RAMP_01_persistence_boundary_and_interruption (test_calculations.Ramp.test_PY_RAMP_01_persistence_boundary_and_interruption) ... ok
test_PY_RAMP_02_dataset_ramp_records (test_calculations.Ramp.test_PY_RAMP_02_dataset_ramp_records) ... ok
test_PY_AMBER_01_provisional_marker (test_calculations.RedWithholding.test_PY_AMBER_01_provisional_marker) ... ok
test_PY_RED_01_red_selected_week_is_unavailable (test_calculations.RedWithholding.test_PY_RED_01_red_selected_week_is_unavailable) ... ok
test_PY_RED_02_history_preserved_and_recovery (test_calculations.RedWithholding.test_PY_RED_02_history_preserved_and_recovery) ... ok
test_PY_RED_03_red_rows_excluded_from_peer_pools (test_calculations.RedWithholding.test_PY_RED_03_red_rows_excluded_from_peer_pools) ... ok
test_PY_RED_04_unit_red_week_with_three_prior_usable_weeks (test_calculations.RedWithholding.test_PY_RED_04_unit_red_week_with_three_prior_usable_weeks) ... ok
test_PY_SUP_01_count_display_states (test_calculations.Suppression.test_PY_SUP_01_count_display_states) ... ok
test_PY_SUP_02_rate_rule (test_calculations.Suppression.test_PY_SUP_02_rate_rule) ... ok
test_PY_SUP_03_engine_states (test_calculations.Suppression.test_PY_SUP_03_engine_states) ... ok
test_PY_COH_01_cohort_boundaries (test_calculations.Windows.test_PY_COH_01_cohort_boundaries) ... ok
test_PY_WIN_01_calendar_window_with_missing_rows (test_calculations.Windows.test_PY_WIN_01_calendar_window_with_missing_rows) ... ok
test_PY_WIN_02_minimum_history_and_ratio_of_sums (test_calculations.Windows.test_PY_WIN_02_minimum_history_and_ratio_of_sums) ... ok
```

## Dashboard logic tests (Node)

```
✔ JS-AGG-01 network and Atlantic latest-week aggregates match the regression baseline and Python (58.5372ms)
✔ JS-AGG-02 last-4-week and all-week pooled aggregates reconcile with Python for every region (3.6337ms)
✔ JS-AGG-03 prior 4-week comparison is a pooled rate, not an average of weekly rates (2.1006ms)
✔ JS-SCOPE-01 role scope is applied before filters; options never include out-of-scope values (0.415ms)
✔ JS-PEER-01 peer membership reproduced in JS matches Python median, n and basis for every store-week-KPI (41.7755ms)
✔ JS-PEER-02 regional managers never get out-of-region peer names; partners always anonymous (0.1774ms)
✔ JS-SUP-01 count display states keep zero, suppressed and not applicable distinct (0.2812ms)
✔ JS-SUP-02 rate suppression: small denominator OR suppressed numerator; applied at the displayed aggregation (0.4358ms)
✔ JS-SAFE-01..04 empty scopes, zero denominators and non-finite inputs produce explicit states (0.9057ms)
✔ JS-AXIS-01 axis tick labels are unique across realistic ranges (0.3842ms)
✔ JS-RANGE-01 missing intervals are reported as actual ranges (0.2858ms)
✔ JS-CONTRAST-01 text colours in the template meet 4.5:1 on white and on the page background (1.9579ms)
✔ JS-STATE-01 URL state round-trips and rejects invalid or out-of-role values (1.3557ms)
✔ JS-TEXT-01 exception explanations name the rule basis and contain no prohibited causal wording (2.4009ms)
✔ JS-EXC-01 stage grouping keeps every triggering KPI; exception status separates unavailable comparisons (0.516ms)
```

## Rendered-page tests (headless Edge)

```
PASS  UI-ALL-01   Simulated role view note is visible and does not claim security [1440 px]
PASS  UI-ALL-02   Banner shows separate artefact versions and snapshot treatment [1440 px]
PASS  UI-ROL-01   Retail Operations lead, week of 2026-08-17: network cards and banner [1440 px]
PASS  UI-RRM-01   Regional Retail Manager (Atlantic), week of 2026-08-17: every card uses Atlantic scope [1440 px]
PASS  UI-RRM-02   Regional banner counts reflect the Atlantic scope (0 Amber, 0 Red, 6 Green) [1440 px]
PASS  UI-RRM-03   Regional manager never sees out-of-region store identities (all pages, stores, KPIs; text, titles and labels) [1440 px]
PASS  UI-RP-01    Retail Partner: own store only, anonymous peers, Network Overview unavailable [1440 px]
PASS  UI-OP-01    Optometry Partner: revenue restricted everywhere; conversion shown with U-41 note [1440 px]
PASS  UI-RED-01   SYN-022 week of 2026-05-25 (Red): values withheld, data prompt only, no performance prompt [1440 px]
PASS  UI-RED-02   SYN-027 week of 2026-07-06 (stale): conversion and ramp index withheld; earlier week available [1440 px]
PASS  UI-RED-03   Network view in a week with a Red store lists a data check and excludes it from rates [1440 px]
PASS  UI-FUN-01   SYN-014 funnel: 460 / 350 / 326 / 187 in separate cells that do not overlap [1440 px]
PASS  UI-FUN-02   Funnel window after Red weeks states usable weeks (SYN-022, week of 2026-06-15) [1440 px]
PASS  UI-SUP-01   Recall counts 1-4 never shown as numbers; SYN-014 latest shows <5 (all stores, all weeks) [1440 px]
PASS  UI-EXC-02   Rule-specific explanations: SYN-005 rule (b) cites own baseline; SYN-019 rule (a) cites peers [1440 px]
PASS  UI-EXC-03   SYN-030 latest: no triggered rule is distinguished from unavailable peer comparison [1440 px]
PASS  UI-EXC-04   Network exception list keeps both fulfilment KPIs for SYN-025 [1440 px]
PASS  UI-EMPTY-01 Compact empty state explains history and does not imply health [1440 px]
PASS  UI-NAV-01   Filters apply after role scope and show a summary (Atlantic + Grocery-hosted = 4 stores) [1440 px]
PASS  UI-NAV-02   Reset returns to latest week with no filters [1440 px]
PASS  UI-NAV-03   Drill-through from an exception keeps week and filters, moves focus, and Back restores the view [1440 px]
PASS  UI-NAV-04   Benchmarking ⇄ diagnostic keep the same store and week; historical week selectable from the filter bar [1440 px]
PASS  UI-HELP-01  KPI definition dialog shows formula, units, period, exclusions, owner, version, limitations; Escape returns focus [1440 px]
PASS  UI-A11Y-01  Tabs: aria-controls, roving tabindex and arrow-key navigation [1440 px]
PASS  UI-A11Y-02  Every chart SVG has a title and description and a data-table alternative [1440 px]
PASS  UI-A11Y-03  Tables use header scopes; controls and buttons have accessible names [1440 px]
PASS  UI-CHART-01 Unique y-axis labels; dashed peer lines have dashed legend samples; flag dots explained [1440 px]
PASS  UI-RAMP-01  Same ramp chart for every eligible store; Mature store explained; gaps and cohort change described [1440 px]
PASS  UI-PEER-01  Peer fallback (SYN-029) and unavailable peer comparison (SYN-030) are explained [1440 px]
PASS  UI-AMBER-01 SYN-003 latest week: Amber data quality and provisional marker [1440 px]
PASS  UI-PLACE-01 KPI placement: recall and turnaround cards (p1), completed exams row (p2), ramp index and revenue context (p3) [1440 px]
PASS  UI-SAFE-01  No NaN, Infinity, undefined or null in rendered output across roles, pages, stores and weeks [1440 px]
PASS  UI-TEXT-01  No prohibited causal wording anywhere in rendered prompts and explanations [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p1 @375px [375 px (mobile)]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p2 @375px [375 px (mobile)]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p3 @375px [375 px (mobile)]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p1 @375px [375 px (mobile)]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p2 @375px [375 px (mobile)]
PASS  UI-RESP-01  No page-level horizontal overflow · OP p3 @375px [375 px (mobile)]
PASS  UI-RESP-01  No page-level horizontal overflow · RP p2 @375px [375 px (mobile)]
PASS  UI-RESP-02  Controls usable @375px (tabs, filters and store selector within viewport; touch targets >= 36px) [375 px (mobile)]
PASS  UI-RESP-03  Chart text stays readable @375px (SVG drawn at container width; axis text 11px or larger) [375 px (mobile)]
INFO  INFO        viewport [375 px (mobile)] — innerWidth=375, devicePixelRatio=1
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p1 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p2 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p3 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p1 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p2 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-01  No page-level horizontal overflow · OP p3 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-01  No page-level horizontal overflow · RP p2 @640px [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-02  Controls usable @640px (tabs, filters and store selector within viewport; touch targets >= 36px) [640 px at 2x (≈1280 px window at 200% zoom)]
PASS  UI-RESP-03  Chart text stays readable @640px (SVG drawn at container width; axis text 11px or larger) [640 px at 2x (≈1280 px window at 200% zoom)]
INFO  INFO        viewport [640 px at 2x (≈1280 px window at 200% zoom)] — innerWidth=640, devicePixelRatio=2
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p1 @768px [768 px (tablet)]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p2 @768px [768 px (tablet)]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p3 @768px [768 px (tablet)]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p1 @768px [768 px (tablet)]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p2 @768px [768 px (tablet)]
PASS  UI-RESP-01  No page-level horizontal overflow · OP p3 @768px [768 px (tablet)]
PASS  UI-RESP-01  No page-level horizontal overflow · RP p2 @768px [768 px (tablet)]
PASS  UI-RESP-02  Controls usable @768px (tabs, filters and store selector within viewport; touch targets >= 36px) [768 px (tablet)]
PASS  UI-RESP-03  Chart text stays readable @768px (SVG drawn at container width; axis text 11px or larger) [768 px (tablet)]
INFO  INFO        viewport [768 px (tablet)] — innerWidth=768, devicePixelRatio=1
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p1 @1280px [1280 px]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p2 @1280px [1280 px]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p3 @1280px [1280 px]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p1 @1280px [1280 px]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p2 @1280px [1280 px]
PASS  UI-RESP-01  No page-level horizontal overflow · OP p3 @1280px [1280 px]
PASS  UI-RESP-01  No page-level horizontal overflow · RP p2 @1280px [1280 px]
PASS  UI-RESP-02  Controls usable @1280px (tabs, filters and store selector within viewport; touch targets >= 36px) [1280 px]
PASS  UI-RESP-03  Chart text stays readable @1280px (SVG drawn at container width; axis text 11px or larger) [1280 px]
INFO  INFO        viewport [1280 px] — innerWidth=1280, devicePixelRatio=1
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p1 @1440px [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p2 @1440px [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · ROL p3 @1440px [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p1 @1440px [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · RRM p2 @1440px [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · OP p3 @1440px [1440 px]
PASS  UI-RESP-01  No page-level horizontal overflow · RP p2 @1440px [1440 px]
PASS  UI-RESP-02  Controls usable @1440px (tabs, filters and store selector within viewport; touch targets >= 36px) [1440 px]
PASS  UI-RESP-03  Chart text stays readable @1440px (SVG drawn at container width; axis text 11px or larger) [1440 px]
INFO  INFO        viewport [1440 px] — innerWidth=1440, devicePixelRatio=1
PASS  UI-KEY-01   Tab order starts with skip link, role, report tabs, then filters; focus outline visible [1440 px, real key events]
PASS  UI-KEY-02   Arrow keys move between report tabs and activate the page [1440 px, real key events]
PASS  UI-KEY-03   Enter on an exception row opens the diagnostic, moves focus to its heading; Enter on Back returns [1440 px, real key events]
PASS  UI-KEY-04   Help dialog: Enter opens, focus moves to Close, Tab stays inside, Escape closes and returns focus [1440 px, real key events]
PASS  UI-KEY-05   Data-quality week cells are keyboard operable (Enter selects the week) [1440 px, real key events]
```
