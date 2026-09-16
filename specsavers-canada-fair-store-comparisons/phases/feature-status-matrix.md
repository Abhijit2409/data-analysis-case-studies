# Feature-Status Matrix

**Updated:** 2026-09-13 (repair pass) · **Scope:** outside-in portfolio case study on public information and **synthetic** data.

> This matrix separates four things that the phase documents alone can blur: a requirement being **written**, being **demonstrated in the prototype**, being **only simulated**, and being **deferred**. Nothing here has been accepted by Specsavers stakeholders, and no production system exists.

**Status key**
- **Implemented (prototype)**: works in `dashboard-mockup.html` on synthetic data and is covered by automated tests (test IDs listed).
- **Simulated**: the prototype shows the intended behaviour, but not the real control (for example, a role selector instead of authentication).
- **Specified only**: documented requirement or design, not built or tested in this project.
- **Deferred**: intentionally out of the MVP or later release.

"Business accepted" is **not** a status any item has: stakeholder review, UAT with real users and sign-off (Phase 14) have not taken place.

---

## 1. Functional requirements (Phase 4)

| ID | Requirement | Status | Evidence / notes |
|---|---|---|---|
| FR-01 | Network overview | Implemented (prototype) | 10 cards incl. recall-booking rate and turnaround; pooled ratio-of-sums; prior-4-week pooled comparison; weekly trend; province tiles; region table · UI-ROL-01, UI-PLACE-01, JS-AGG-01…03 |
| FR-02 | Region, province, format, banner, cohort, week filters | Implemented (prototype) | Applied after role scope; filter summary and reset; options limited to scope · UI-NAV-01/02, JS-SCOPE-01. Data-quality status filter also implemented. Reporting-week *range* not implemented (single week + 26-week trends) |
| FR-03 | Maturity classification as at week | Implemented (prototype) | Cohort as at selected week; boundary 26→27 · PY-COH-01. "Unclassified" handling specified and unit-tested in the engine, not present in the synthetic data |
| FR-04 | Store-to-peer comparison | Implemented (prototype) | Median, variance, quartile position, basis and n; peers reproduced in JS and reconciled with Python for every store-week-KPI · PY-PEER-01…04, JS-PEER-01 |
| FR-05 | Drill-through with context | Implemented (prototype) | Exception row → diagnostic, benchmarking ⇄ diagnostic, Back keeps week and filters; focus moves to page heading · UI-NAV-03/04, UI-KEY-03 |
| FR-06 | Exception highlighting (rule set v0.2) | Implemented (prototype) | Rules (a) and (b), recall eligibility, Red-week exclusion, stage grouping listing every KPI, consecutive-week counts · PY-EXC-01…06, UI-EXC-02…04. Thresholds unvalidated |
| FR-07 | KPI definitions and ownership | Implemented (prototype) | Definition dialog: formula, units, period, exclusions, proposed owner, version, limitations · UI-HELP-01, UI-KEY-04. Governed dictionary *table* and approval workflow are specified only |
| FR-08 | Data-quality and freshness warnings | Implemented (prototype) | Scoped banner counts; Red withholds values; Amber provisional marker · PY-RED-01…04, PY-AMBER-01, UI-RED-01…03, UI-RRM-02. Per-source status (target model) specified only; completeness values are simulated |
| FR-09 | Role landing views | Simulated | Role selector sends partners to their store diagnostic · UI-RP-01. No identity integration |
| FR-10 | Role-based access (RLS/OLS) | Simulated | Presentation-level scope and revenue restriction only; full dataset is embedded in the page · UI-RRM-03, UI-RP-01, UI-OP-01. Real RLS/OLS: specified only (SR-01…SR-03, Phase 13 §5.5) |
| FR-11 | Approved aggregate exports | Deferred | Not built; suppression rule for exports specified (PR-04) |
| FR-12 | Persistent filter selections | Specified only (partial) | URL state keeps selections within a link/session; no per-user persistence across sessions |
| FR-13 | Ramp-up trend by weeks since opening | Implemented (prototype) | Same chart for every eligible store; IQR band split at gaps; actual missing ranges; cohort-change marker · PY-RAMP-01/02, UI-RAMP-01 |
| FR-14 | Appointment-to-purchase funnel | Implemented (prototype) | HTML table with separate cells; window and usable weeks stated; held definition · UI-FUN-01/02, PY-FUN-01 |
| FR-15 | Investigation prompts (library v0.2) | Implemented (prototype) | Rule-specific explanation + prompt + typical team; no prohibited causal terms · JS-TEXT-01, UI-TEXT-01. Library ownership and approval specified only |
| FR-16 | Small-peer-group fallback and suppression | Implemented (prototype) | Fallback and "not available" states with n · UI-PEER-01, PY-PEER-02/03 |
| FR-17 | Context annotations | Deferred | — |
| FR-18 | Follow-up action log (write-back) | Deferred | — |

## 2. Non-functional, data, privacy and security requirements (Phase 5)

| ID | Status | Notes |
|---|---|---|
| NFR-01 Performance | Specified only | Prototype interactions are fast on 761 rows; no Power BI volume test |
| NFR-02 Refresh, NFR-03 Availability, NFR-06 Scalability, NFR-07 Supportability | Specified only | No production platform |
| NFR-04 Accessibility | Implemented (prototype), partially verified | Keyboard tabs, visible focus, dialog focus handling, chart titles/descriptions and data tables, header scopes, ≥4.5:1 text colours · UI-A11Y-01…03, UI-KEY-01…05, JS-CONTRAST-01. **No screen-reader test and no WCAG audit; no compliance claim** |
| NFR-05 Usability | Specified only | No user testing; SUS and task-time targets untested |
| NFR-08 Device support | Implemented (prototype), emulated | No page-level horizontal overflow at 375, 640@2x (≈200% zoom of 1280), 768, 1280, 1440 px · UI-RESP-01…03. No physical device test |
| DR-01 Lineage, DR-02 Versioning | Partially implemented | Versions shown in the banner; change logs in Phases 6 and 13; no lineage tooling |
| DR-03 Retention, DR-07 Store master, DR-08 Reconciliation to control totals | Specified only | REC-01…REC-05 need real control totals |
| DR-04/05 Completeness and freshness | Simulated | Status thresholds implemented; source load metadata not modelled |
| DR-06 Grain and ratio of sums | Implemented (prototype) | PY-WIN-02, JS-AGG-02/03 |
| DR-09 Zero vs null | Implemented (prototype) | Recall not applicable vs zero vs suppressed vs withheld · PY-SUP-01/03, JS-SUP-01, UI-SUP-01 |
| DR-10 Cohort as at week | Implemented (prototype) | PY-COH-01 |
| PR-01/02/05 No identifiers, diagnoses, individual performance | Implemented (synthetic dataset design) | Store-week aggregates only; no person-level fields |
| PR-03 Peer floor | Implemented (prototype) | Floor 5 |
| PR-04 Small-count suppression (demonstration rule v0.2) | Implemented (prototype) | Counts 1–4 → "<5"; rates hidden for denominator <5 or numerator 1–4; weekly recall counts shown as text, never plotted · PY-SUP-01…03, JS-SUP-01/02, UI-SUP-01. **Complementary suppression (U-39) not implemented; primary suppression alone is not claimed to be sufficient for production** |
| PR-06 Privacy review | Specified only | — |
| PR-07 Partner confidentiality | Simulated | Anonymous peers for partners; named in-region peers for the regional manager · UI-RRM-03, UI-RP-01 |
| PR-08 Synthetic non-production data | Implemented | Whole project |
| SR-01…SR-08 | Specified only (SR-03 simulated in the UI) | No authentication, RLS, OLS, audit logging or environments exist. Phase 13 §5.5 gives unexecuted Power BI guidance |

## 3. KPIs (Phase 6, dictionary v0.2)

| KPI | Status | Placement in prototype |
|---|---|---|
| KPI-01 Capacity | Implemented | Page 3 funnel |
| KPI-02 Utilization, KPI-03 Attendance, KPI-05 Conversion, KPI-08 On-time | Implemented | Pages 1, 2, 3 |
| KPI-04 Completed exams | Implemented | Page 1 card (weekly total), Page 2 row (4-week average per week), Page 3 funnel |
| KPI-06 Revenue per exam | Implemented, role-restricted (simulated) | Page 1 card, Page 2 row, Page 3 funnel context; "Restricted" for Optometry Partner |
| KPI-07 Turnaround | Implemented (with synthetic simplification: all orders reach ready) | Page 1 card, region table and tiles; Pages 2 and 3 |
| KPI-09 Recall-booking rate | Implemented | Page 1 card, Pages 2 and 3; weekly counts as suppressed text strip |
| KPI-10 Ramp index | Implemented | Page 2 header and chart; Page 3 header |
| KPI-11 Completeness, KPI-12 Freshness | Simulated values; status logic implemented | Banner, Page 3 data-quality panel |
| Provisional periods (conversion, recall, fulfilment) | Specified only | Snapshot treated as final and labelled as such |

## 4. User stories (Phase 8) and UAT (Phase 14)

| Item | Status |
|---|---|
| US-01, US-03, US-04, US-06, US-10 | Acceptance criteria demonstrated on synthetic data where testable by automation (see test IDs above). Not accepted by a Product Owner |
| US-02 | Demonstrated with the conservative U-38 assumption (own region plus labelled network reference). Not Ready until U-38 is decided |
| US-05 | Definition access demonstrated; governed dictionary table and version workflow specified only |
| US-07 | Simulated only |
| US-08 | Deferred (exports) |
| US-09 | Specified only (process) |
| UAT-01…UAT-24 | **Not executed with business users.** Automated prototype checks map to parts of UAT-01…08, 13, 18, 21, 22 (see `evidence/test-report.md`). Reconciliation to control totals (UAT-15…17), security (UAT-09…12), usability (UAT-24), performance (UAT-14) and sign-off (UAT-20) are future internal UAT |

## 5. Power BI

| Item | Status |
|---|---|
| Data model, measures, RLS/OLS guidance (Phase 13 §5) | Specified only — **DAX is unexecuted guidance**, not tested in Power BI Desktop |
| `.pbix` file | Not created |
