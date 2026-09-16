# Phase 11 — MVP Definition

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–10

> **Outside-in disclaimer.** The MVP, pilot design, timelines and criteria are illustrative proposals for a case study. They are not Specsavers plans or commitments.

---

## 1. MVP objective

Give pilot Regional Retail Managers, Retail Operations leaders and store partners a **trusted, fair and privacy-safe weekly view**. It should show which stores warrant attention relative to comparable stores, which journey stage to investigate, and whether the data is fit to act on. The MVP must be validated within **CON-01** (three pages; pilot within an illustrative 12 weeks of build start).

**Hypotheses the MVP tests**
- **H1 Fairness:** maturity- and format-aware peer comparison is perceived as fairer than simple rankings (EO-01).
- **H2 Speed:** stores that warrant attention are identified faster than today (EO-02).
- **H3 Actionability:** journey-stage flags with non-causal prompts lead to a named follow-up owner (EO-04).
- **H4 Trust:** visible definitions and data-quality status reduce disputes about numbers (EO-03).

## 2. Included users

| User group | Stakeholder | MVP role | Scope of data |
|---|---|---|---|
| Regional Retail Managers (pilot regions) | SH-03 | **Primary users** | Assigned region(s) |
| Retail Operations leadership | SH-04 | Sponsor; network user | Network |
| Retail Partners (pilot stores) | SH-01 | Store users | Own store + anonymised peers |
| Optometry Partners (pilot stores) | SH-02 | Store users (clinical-activity view) | Own store; revenue hidden; KPI-05 visible by default pending U-41 |
| Finance, Supply Chain, Marketing analysts (one each) | SH-07, SH-06, SH-05 | Validation users for their KPIs | Per role model (Phase 5) |
| Privacy Officer or delegate | SH-13 | Access and privacy witness | Admin test scope |

*Not included in the MVP:* executive leadership as regular users (informed via summary), all non-pilot partners, Partnership Advisory Committee members as users (consulted instead).

## 3. Included decisions

| # | Decision | Primary user | Page |
|---|---|---|---|
| MD-1 | Which stores in my region warrant attention this week, relative to comparable stores? | SH-03 | 1, 2 |
| MD-2 | Is a pattern local to one store or shared across a region or format? | SH-03, SH-04 | 1 |
| MD-3 | Is this new store ramping like stores of the same age? | SH-03, SH-01 | 2 |
| MD-4 | Which journey stage should be investigated first, and who typically follows up? | SH-03, SH-01, SH-02 | 3 |
| MD-5 | Is the data complete and current enough to act on? | All | 1, 3 |

## 4. Included requirements

| Type | Included in MVP | If low effort | Excluded or deferred |
|---|---|---|---|
| Business | BR-01–BR-09, BR-11 (BR-10 = CON-01) | BR-12 | — |
| Functional | FR-01–FR-08, FR-10, FR-13–FR-16 | FR-09, FR-11, FR-12 | FR-17, FR-18 |
| Non-functional | NFR-01–NFR-07 | NFR-08 | — |
| Data | DR-01–DR-10 | — | — |
| Privacy | PR-01–PR-08 | — | — |
| Security | SR-01–SR-08 | — | — |
| User stories | US-01, US-03–US-07, US-09, US-10 | US-02, US-08 | — |

## 5. Included KPIs

| KPI | Page 1 Network | Page 2 Benchmarking | Page 3 Diagnostic | Notes |
|---|---|---|---|---|
| KPI-01 Available capacity | — | — | ✓ (funnel) | Context only |
| KPI-02 Appointment utilization | ✓ | ✓ | ✓ | Exception KPI |
| KPI-03 Attendance rate | ✓ | ✓ | ✓ | Exception KPI |
| KPI-04 Completed examinations | ✓ (weekly total) | ✓ (4-week average per week) | ✓ (funnel) | Access headline |
| KPI-05 Exam-to-purchase conversion | ✓ | ✓ | ✓ | Exception KPI; OP visibility per U-41 |
| KPI-06 Revenue per completed exam | ✓ (restricted) | ✓ (restricted) | ✓ (funnel context, restricted) | Context only; not an exception driver |
| KPI-07 Average order turnaround | ✓ (card, region table, tiles) | ✓ | ✓ | Exception KPI; synthetic simplification (KPI-07 v0.2 note) |
| KPI-08 On-time fulfilment rate | ✓ | ✓ | ✓ | Exception KPI |
| KPI-09 Recall-booking rate | ✓ | ✓ | ✓ | Exception KPI (Developing and Mature only) |
| KPI-10 Store ramp index | — | ✓ | ✓ (header) | New and Developing only |
| KPI-11 Data completeness | ✓ (status) | ✓ (icon) | ✓ | Trust gate |
| KPI-12 Data freshness | ✓ (banner) | ✓ (icon) | ✓ | Trust gate |

## 6. Included dimensions and filters

| Dimension or filter | Values (synthetic prototype) | Pages |
|---|---|---|
| Reporting week (single; range for trends) | Monday week start; default latest published week | All |
| Region | West, Prairies, Ontario, Atlantic (synthetic) | All |
| Province | BC, AB, SK, MB, ON, NS, NB, NL (synthetic subset) | All |
| Store format | Grocery-hosted, Shopping centre, Street-front | All |
| Host banner | Host Banner A, Host Banner B, Standalone (no host) — generic | All (global filter) |
| Maturity cohort (as at week) | New, Developing, Mature, Unclassified | All |
| Store | Within RLS scope | 2, 3 |
| KPI selector | Exception KPIs plus completed exams | 2 |
| Data-quality status | Green, Amber, Red (as at the selected week) | All (global filter) |

*Repair pass:* the placements above now match the HTML prototype (`feature-status-matrix.md`). Previously KPI-07 was tooltip-only on Page 1, and the prototype lacked the Page 1 recall card, the Page 2 completed-exams row and the Page 3 ramp index and revenue context.

## 7. Explicit exclusions

- PC Optimum and loyalty analytics (**future enhancement**)
- Patient-level data, diagnoses, prescriptions, clinical outcomes
- Individual employee, optician or optometrist performance
- Profitability, P&L, partner distributions, franchise fees, financial ROI
- Forecasting, predictive or causal models
- Inventory, assortment, pricing, procurement and marketing-attribution analytics
- Daily or intra-day reporting; real-time alerts
- Write-back or action tracking in the product (FR-18)
- Named peer-store comparisons for partners
- French-language version (pending U-40)

## 8. Deferred capabilities (candidate Release 2+)

| Capability | Trigger for reconsideration | Related |
|---|---|---|
| Context annotations (e.g., store events, PC Optimum launch 22 Jun 2026) | Event-table ownership agreed | FR-17, R-20 |
| Follow-up action log | Pilot shows manual logging is burdensome | FR-18, BO-04 |
| PC Optimum and loyalty measures | MVP adopted; loyalty data access and privacy review | CON-07 |
| Province-specific peer groups | Enough stores per province and cohort | R-12 |
| Capacity-normalised ramp index | U-37 decision | KPI-10 |
| Median turnaround and long-tail measures | Supply Chain request after pilot | KPI-07 |
| Mobile-optimised partner summary | NFR-08 feedback | NFR-08 |
| French-language labels | U-40 confirms need | R-21 |

## 9. Delivery assumptions (illustrative)

| # | Assumption | Links |
|---|---|---|
| DA-1 | Discovery, KPI workshops and prototype testing (Phase 2 engagement plan) are completed **before** build starts | A-18 |
| DA-2 | A cross-functional team is available: Product Owner, Data Business Analyst, 1–2 Data Engineers, 1 Visualization Analyst, Data Delivery Manager (part-time) | EV-09, DEP-11 |
| DA-3 | Source data for at least appointments, exams and sales is accessible by the end of Sprint 0; fulfilment and recall may follow in Sprint 2 | DEP-01, R-14 |
| DA-4 | Build-to-pilot timeline of 12 weeks: **Week 1** Sprint 0 · **Weeks 2–7** three 2-week sprints · **Week 8** UAT and sign-off · **Weeks 9–12** four-week pilot with evaluation at the end of week 12 | CON-01 |
| DA-5 | Privacy review is approved before UAT with real data | DEP-03 |
| DA-6 | KPI definitions v1.0 approved by Sprint 2 | DEP-04 |

## 10. MVP acceptance conditions (release to pilot)

| # | Condition | Evidence |
|---|---|---|
| AC-1 | All Must stories (US-01, US-03–US-07, US-09, US-10) accepted by the Product Owner | Sprint review records |
| AC-2 | UAT exit criteria met: 100% of Must scenarios executed; at least 95% pass; 0 open Severity 1 or 2 defects | UAT report (Phase 14) |
| AC-3 | Reconciliation within tolerance for exams, revenue and orders (DR-08), or the affected KPI withheld with sponsor agreement | UAT-15 to UAT-17 |
| AC-4 | 100% of role-based access, export and suppression tests pass, witnessed by SH-13 | UAT-09 to UAT-12, UAT-18 |
| AC-5 | Privacy review approved (PR-06); no identifier fields in the model (PR-01) | Approval record; schema scan |
| AC-6 | KPI dictionary v1.0 approved for all displayed KPIs | FR-07 coverage check |
| AC-7 | Accessibility checklist passed for all three pages (NFR-04) | UAT-13 |
| AC-8 | Release-readiness items complete: runbook, lineage, support route, volume test (NFR-03, NFR-06, NFR-07, DR-03, SR-06, SR-08) | Readiness checklist (RTM-02) |

## 11. Recommended pilot group (illustrative)

| Element | Recommendation | Rationale |
|---|---|---|
| Regions | **Two regions**: one established region and one including a recently entered province (A-38) | Tests fairness across mature and new markets |
| Stores | **12–16 stores**, mixed across New, Developing and Mature cohorts and across all formats, including at least 4 grocery-hosted locations | Exercises peer, fallback and suppression rules in real conditions |
| Regional Retail Managers | 2–3 | Primary users; weekly triage routine |
| Retail and Optometry Partners | Partners of the pilot stores, opting in | Voluntary participation supports trust |
| Support Office validators | 1 each from Finance, Supply Chain and Marketing | KPI validation |
| Governance | Privacy Officer or delegate; SH-14 briefed | Oversight and endorsement |
| Duration | 4 weeks of use (weeks 9–12), followed by an evaluation decision | Four weekly cycles reveal adoption and exception usefulness |

## 12. Proposed feedback process

| Mechanism | Frequency | Participants | Output |
|---|---|---|---|
| In-report feedback link (short form) | Continuous | All pilot users | Tagged issues and ideas backlog |
| Office hours (30 minutes) | Weekly | SH-09, SH-11, pilot users | Quick fixes; usage coaching |
| Exception review huddle | Weekly | SH-03, SH-04, SH-09 | Flag usefulness rating; manual follow-up log (EO-04) |
| Pulse survey (5 questions: fairness, trust, usefulness, clarity, time saved) | Weeks 2 and 4 | All pilot users | EO-01, EO-03, EO-07 inputs |
| Comprehension check (non-causal interpretation) | Week 2 | 5 or more users | BR-03 measure (UAT-21 follow-up) |
| Partner roundtable | Week 4 | Pilot partners; SH-14 representative | Fairness and confidentiality feedback |
| Usage analytics review | Weekly | SH-08, SH-09 | Active users, page views, drill-through usage |
| Pilot evaluation workshop | End of week 12 | SH-04, SH-08, SH-12, SH-13 | Expand, iterate or stop decision |

## 13. Decision criteria for expansion (illustrative thresholds)

| Criterion | Expand if… | Iterate if… | Stop or re-think if… |
|---|---|---|---|
| Adoption | At least 60% of pilot users active in at least 3 of 4 weeks | 40–59% | Under 40% |
| Fairness (EO-01) | At least 80% rate comparisons fair or mostly fair | 60–79% | Under 60% |
| Speed (EO-02) | Median identification time 2 business days or less | 3–4 days | No improvement against baseline |
| Actionability (EO-04) | At least 70% of reviewed flags have a follow-up owner; at least 60% judged worth follow-up | 50–69% | Under 50% |
| Trust (EO-03) | Zero unresolved definition disputes; reconciliation within tolerance | Disputes with an agreed fix | Unresolvable definition conflicts |
| Privacy (EO-06) | Zero incidents; all access tests remain green | — | **Any** privacy or confidentiality incident (pause immediately) |
| Comprehension | At least 80% interpret flags as investigation areas | 60–79% (rework prompts and training) | Under 60% |
| Data quality | At least 95% of pilot store-weeks Green or Amber | 90–94% | Under 90% |

**Expansion path (if criteria met):** add regions in waves of about 25% of stores; confirm the peer floor and exception thresholds after each wave; begin Release 2 prioritisation (Section 8).

---

## MVP scope statement (for the case-study presentation)

> **The MVP is a three-page Power BI reporting product (Network Overview; Store and Cohort Benchmarking; Store Diagnostic and Data Quality) for a pilot of 2–3 Regional Retail Managers, their Retail Operations leadership and the partners of 12–16 opt-in stores across two regions.**
>
> **Using store-week aggregates only, it compares each store with peers of the same maturity stage and format. It shows ramp-up by weeks since opening, highlights journey-stage variances as areas to investigate (not causes) with a suggested follow-up team, and makes data completeness and freshness visible before action.**
>
> **It includes 12 governed KPIs, role-based access, anonymised peer statistics and small-count suppression. It excludes patient-level and clinical data, individual performance, profitability, forecasting and PC Optimum loyalty analytics (a future enhancement).**
>
> **Success is judged after a four-week pilot on adoption, perceived fairness, time to identify exceptions, follow-up ownership, trust in the numbers and zero privacy incidents. All targets are illustrative and require internal validation.**

---

## Phase 11 close

### Decisions made
1. MVP = 3 pages, 13 core functional requirements plus 3 low-effort ones, 12 KPIs, 8 core stories plus 2 Should stories.
2. Pilot: two regions (one including a recently entered province), 12–16 opt-in stores, 4 weeks of use.
3. Expansion criteria defined across adoption, fairness, speed, actionability, trust, privacy, comprehension and data quality, with a privacy stop rule.
4. PC Optimum analytics remains a future enhancement.

### Assumptions introduced
DA-1 to DA-6 (delivery assumptions, illustrative).

### Questions requiring validation
- Is a four-week pilot long enough to observe ramp-up changes? (New-store trends may need 8+ weeks; consider extending observation of KPI-10 after the go or no-go decision.)
- Will partners opt in without a formal endorsement from SH-14?

### Recommended corrections
- None.
