# Test Report — Repair Pass

**Date:** 2026-09-13 · **Build under test:** `dashboard-mockup.html` generated from `build/mockup_template.html`, `build/dashboard_logic.js` and `data/analysis_summary.json` · **Data:** synthetic only (seed 20260913)

> These are tests of a **portfolio prototype on synthetic data with simulated roles**. They are not Power BI tests, not user acceptance testing, not a security test and not an accessibility audit. Generated detail for the latest run: `evidence/test-results.md` (all steps) and `evidence/ui-test-results.json` (rendered-page checks).

## 1. What was executed

| Level | Type | Command | Result |
|---|---|---|---|
| Reproducibility | Automated | `python build/generate_synthetic.py` (CSV hash compared) | Byte-identical |
| Structural and seeded-pattern checks | Automated | `python build/validate_and_analyze.py` | 32/32 |
| Calculation regression tests | Automated | `python -m unittest discover -s tests -p "test_*.py"` | 30 tests OK |
| Logic and Python ↔ JavaScript reconciliation | Automated | `node --test tests/test_dashboard_logic.js` | 15 pass, 0 fail (peer reconciliation covers every store-week × KPI) |
| Generated-page consistency | Automated | `python build/build_mockup.py` + embedded-source comparison | Consistent |
| Rendered-page regression | Automated (headless Microsoft Edge via DevTools protocol) | `node tests/ui_regression.js` | 83/83 |
| Document and deck consistency | Automated | `python build/consistency_scan.py` | 21/21 |
| Visual inspection of the dashboard | Manual | Browser pane (≈800 px wide) and 10 full-page screenshots at 1440, 640 and 375 px | Done; issues found and fixed (Section 4) |
| Keyboard check with real key presses | Manual | Browser pane: Tab from the page header to the reporting-week selector (visible focus outline), then ArrowRight | Focus visible; ArrowRight on the focused, closed week selector changed the week to 10 Aug 2026 and the banner updated (native select behaviour) |
| Deck | Automated + manual | pptx validator; all 19 slides exported through PowerPoint and inspected | Validator passed; no clipping or overlap found after fixes; A1 hyperlinks present in the file (not clicked) |
| Power BI (DAX, RLS, OLS) | — | — | **Not executed** (no Power BI build) |
| Internal UAT (Phase 14) | — | — | **Not executed** |

## 2. Actual versus expected — demonstration scenarios

| Scenario | Expected | Actual | Evidence | Type |
|---|---|---|---|---|
| Network, week of 17 Aug 2026 | 30 stores; 3,496 exams; 2 Amber, 0 Red | 30 · 3,496 · ▲ 2 Amber · ■ 0 Red | UI-ROL-01, PY-BASE-01, JS-AGG-01 · `after/p1-1440.png` | Automated |
| Atlantic manager, same week | 6 stores; 545 exams; utilization ≈81.0%, attendance ≈94.6%, conversion ≈55.8%, on-time ≈77.3%, turnaround ≈9.1 days; all six Green; no out-of-region names | 6 · 545 · 81.0% · 94.6% · 55.8% · 77.3% · 9.1 days · ● 6 Green ▲ 0 Amber; no SYN-001–024 anywhere in the rendered DOM on any page, store or KPI | UI-RRM-01…03, PY-BASE-02 · `after/p1-rrm-atlantic-1440.png` | Automated |
| SYN-014 funnel (4 weeks ending 17 Aug 2026) | 460 slots, 350 held, 326 exams, 187 purchasers; no overlapping text | 460 / 350 / 326 / 187 in separate cells; no overlapping cell boxes; "4 of 4 weeks usable" | UI-FUN-01, PY-FUN-01 · `before/p3-SYN-014-funnel-1440.png` vs `after/p3-SYN-014-funnel-1440.png` | Automated + manual |
| SYN-014 latest recall | 3 bookings shown as "<5", not plotted; rate not derivable | Weekly strip shows "<5"; 4-week recall rate available only when numerator ≥5; no 1–4 count shown as a number for any store or week | UI-SUP-01, PY-SUP-01…03 | Automated |
| SYN-005 conversion decline | Rule (a) from 27 Apr 2026; rule (b) 11 May – 8 Jun 2026, explained against its own baseline | Same weeks; week of 25 May shows "Rule (b), own trend … below this store's own baseline" | UI-EXC-02, PY-EXC-05 · `after/p3-SYN-005-rule-b-1440.png` | Automated |
| SYN-022 Red weeks (25 May – 8 Jun 2026) | Values withheld in the Red week itself; data prompt only; no flags; excluded from peers; later windows state usable weeks | Funnel withheld; only the Data prompt; 60.8% no longer displayed; peer pools exclude SYN-022; 15 Jun shows "only 1 usable week" | UI-RED-01, UI-RED-03, UI-FUN-02, PY-RED-01…03 · `after/p3-SYN-022-red-week-1440.png` | Automated |
| SYN-027 stale week (6 Jul 2026) | Conversion and ramp index withheld; 29 Jun still available | Withheld ("Ramp index: withheld (data quality Red)"); 29 Jun shows a ramp index | UI-RED-02, PY-RED-01 | Automated |
| SYN-029 peer fallback | Whole-cohort comparison with format and cohort n | Warning: 1 Street-front peer, 12 Developing peers used | UI-PEER-01 · `after/p2-SYN-029-1440.png` | Automated |
| SYN-030 insufficient peers and early recall | Peer comparison unavailable but own values visible; exception status "own-trend rule only"; early recall counts suppressed or n/a | As expected; early 4-week recall rate "insufficient history" | UI-EXC-03, UI-PEER-01, PY-EXC-05, PY-SUP-03 | Automated |
| SYN-003 / SYN-016 latest Amber | Amber data quality with provisional marker; banner counts 2 | SYN-003 header "Data quality: ▲ Amber (provisional …)"; both listed as "▲ Amber · Provisional" in the exception table | UI-AMBER-01 (SYN-003); SYN-016 by screenshot `after/p1-1440.png` | Automated + manual |
| Historical weeks, filters, reset, drill-through | Week selectable; filters after scope with summary; Back restores week and filters; focus moves to the page heading | As expected (Atlantic + Grocery-hosted = 4 stores) | UI-NAV-01…04, UI-KEY-03 | Automated |
| Mobile and zoom | No page-level horizontal overflow at 375, 768, 1280, 1440 px and at 640 px CSS width with 2× scale (≈1280 px window at 200% zoom); controls ≥36 px tall | 7 page/role combinations pass at every width | UI-RESP-01…03 · `after/p1-375-mobile.png`, `after/p3-SYN-014-375-mobile.png`, `after/p2-640-zoom200.png` | Automated (emulated) |
| Keyboard-only | Skip link, role, active tab, filters in order; arrow keys switch tabs; Enter drills through; dialog traps focus and Escape returns it | As expected with real key events | UI-KEY-01…05 + manual check (Section 1) | Automated + manual |

## 3. Before and after

*How the "before" set was captured:* the original page had no URL state, so the before screenshots were taken from the pre-repair backup copy (`Specsavers-Case-Study-BACKUP-2026-09-13-pre-repair/dashboard-mockup.html`) with a small script appended in a temporary copy that only selected the role, page and store before capture. The page's own code, data and rendering were not otherwise changed.

| View | Before (`evidence/screenshots/before/`) | After (`evidence/screenshots/after/`) |
|---|---|---|
| Network overview 1440 px | `p1-1440.png` — no filters, no recall or turnaround cards | `p1-1440.png` — filter bar, 10 cards, scoped banner, stage list with all KPIs |
| Atlantic manager | `p1-rrm-atlantic-1440.png` — 30 stores, 3,496 exams, Amber 2 | `p1-rrm-atlantic-1440.png` — 6 stores, 545 exams, Amber 0, network reference labelled |
| Store diagnostic SYN-014 | `p3-SYN-014-funnel-1440.png` — "350" overlapping "Utilization 76.1%"; raw recall counts plotted with a "−0" axis | `p3-SYN-014-funnel-1440.png` — funnel table; "<5" strip; gap reasons; dashed legend samples |
| Mobile 375 px | `p1-375-mobile.png` — page wider than the screen | `p1-375-mobile.png` — stacked layout, no page-level overflow |
| SYN-022 | `p3-SYN-022-1440.png` — latest week only; Red weeks not selectable | `p3-SYN-022-red-week-1440.png` — week of 25 May selected; values withheld |
| SYN-029 benchmarking | `p2-SYN-029-1440.png` | `p2-SYN-029-1440.png` — fallback explained once with n |

## 4. Defects found while testing the repair (and fixed)

| Found by | Defect | Fix |
|---|---|---|
| PY-WIN-01 (unit frame) | The engine's calendar was built from observed weeks, so a week missing for every store vanished from the window | Contiguous weekly calendar from first to last week |
| PY-EXC-05 | A New store's recall exception state showed "unavailable" instead of "not eligible" | Exception-state precedence corrected |
| UI-RP-01, UI-OP-01 | Content rendered for a previous role stayed in hidden page panels (store names and revenue in the DOM) | Inactive page containers cleared on every render |
| UI-RESP-01 | Axis and chart labels extended past the viewport at 375 px | Edge labels anchored inside the chart |
| Manual visual check | "▼ $0" for a change that rounds to zero; cramped exception table beside the region table; stretched empty investigation panel; long repeated fallback text | "■ no change"; full-width exception table; top-aligned grid; grouped fallback warning |
| Manual deck check | Dashboard images on slide 7 too small to read | Deck images captured at 2× and re-laid out |
| Test infrastructure | Headless Edge profiles filled the nearly full system drive (a file write failed) | Profiles deleted after every run; stale profiles removed at start |

## 5. Not tested

- Power BI Desktop or Service behaviour: DAX, RLS, OLS, performance.
- Real authentication or security: the page embeds all synthetic data; roles are simulated.
- Real screen readers (NVDA, JAWS, Narrator), browser zoom controls, physical phones or tablets, and browsers other than Microsoft Edge (Chromium).
- Usability with real users (task time, SUS), comprehension of non-causal wording, or partner acceptance.
- Reconciliation to real source systems or control totals (REC-01 to REC-05).
- Whether external links in the deck resolve today (they were verified as complete URLs, not opened from PowerPoint).
