# Phase 9 — Requirements Traceability Matrix (RTM)

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–8

> **Outside-in disclaimer.** The traceability below links **proposed** case-study artefacts. Expected outcomes are illustrative and unvalidated.

**Method.** IDs were extracted automatically from the Phase 1–8 files (`build/id_scan.py`). The scan confirmed contiguous numbering for BO (7), BR (12), FR (18), NFR (8), DR (10), PR (8), SR (8), KPI (12) and US (10). Each link was then reviewed by hand. **No approved identifiers were changed.** UAT scenario IDs UAT-01 to UAT-24, reserved in Phase 8, are titled here and fully specified in Phase 14.

---

## 1. Expected business outcomes (EO)

| ID | Expected business outcome *(illustrative measure)* | Business objective |
|---|---|---|
| EO-01 | At least 80% of pilot users rate store comparisons as fair or mostly fair | BO-01 |
| EO-02 | Median time to identify stores warranting attention is 2 business days or less after week end | BO-02 |
| EO-03 | 100% of MVP KPIs have an approved definition, owner and version; zero unresolved definition conflicts | BO-03 |
| EO-04 | At least 70% of pilot exceptions have a recorded follow-up owner within 10 business days | BO-04 |
| EO-05 | Access indicators appear with equal prominence on every MVP page | BO-05 |
| EO-06 | Zero privacy or confidentiality incidents; 100% of access tests pass | BO-06 |
| EO-07 | 30% reduction in self-reported manual compilation hours (conditional on baseline) | BO-07 |

## 2. UAT scenario index (detail in Phase 14)

| UAT | Scenario | UAT | Scenario |
|---|---|---|---|
| UAT-01 | Network overview KPIs and totals | UAT-13 | Accessibility checks |
| UAT-02 | Region and province filtering; regional pattern | UAT-14 | Page performance |
| UAT-03 | Maturity cohort assignment and boundary crossing | UAT-15 | Reconciliation – appointments and exams |
| UAT-04 | Peer median, variance and basis | UAT-16 | Reconciliation – revenue |
| UAT-05 | Drill-through network → region → store | UAT-17 | Reconciliation – fulfilment and recall |
| UAT-06 | Exception flags on seeded patterns | UAT-18 | Small peer group and small-count suppression |
| UAT-07 | KPI definition access and versioning | UAT-19 | Persistent filters and reset |
| UAT-08 | Data-quality status and withholding | UAT-20 | Go/no-go and business sign-off |
| UAT-09 | RLS – Retail Partner own store | UAT-21 | Non-causal wording and comprehension |
| UAT-10 | RLS – Regional Retail Manager scope | UAT-22 | Ramp-up trend and ramp index |
| UAT-11 | OLS – revenue measures visibility | UAT-23 | Role landing pages |
| UAT-12 | Export restrictions, suppression and logging | UAT-24 | Usability task test |

---

## 3. Master traceability matrix (forward: objective → outcome)

| BO | BR | FR | NFR / DR / PR / SR | KPI | US | UAT | EO | Release |
|---|---|---|---|---|---|---|---|---|
| BO-01, BO-02, BO-03 | **BR-01** Network monitoring | FR-01, FR-02, FR-05, FR-09 | NFR-01, NFR-02, NFR-03, NFR-06, DR-06, DR-07 | KPI-01–KPI-09 | US-01, US-02 | UAT-01, UAT-02, UAT-05, UAT-14, UAT-15, UAT-16, UAT-23 | EO-02, EO-03 | MVP |
| BO-01, BO-02 | **BR-02** Maturity-aware comparison | FR-03, FR-04, FR-13, FR-16 | DR-07, DR-10, PR-03, PR-07 | KPI-04, KPI-10 | US-03, US-10 | UAT-03, UAT-04, UAT-18, UAT-22 | EO-01, EO-02 | MVP |
| BO-04, BO-01 | **BR-03** Candidate factors | FR-04, FR-14, FR-15, FR-17 (deferred) | NFR-05 | KPI-02, KPI-03, KPI-05, KPI-07, KPI-08, KPI-09 | US-04 | UAT-06, UAT-21, UAT-24 | EO-04 | MVP (FR-17 deferred) |
| BO-03 | **BR-04** Governed KPIs | FR-07 | DR-01, DR-02, DR-08, NFR-07 | KPI-01–KPI-12 | US-05 | UAT-07, UAT-15, UAT-16, UAT-17 | EO-03 | MVP |
| BO-03, BO-01 | **BR-05** Visible data quality | FR-08, FR-01 (banner) | DR-04, DR-05, DR-09 | KPI-11, KPI-12 | US-06 | UAT-08, UAT-15 | EO-03 | MVP |
| BO-01, BO-04, BO-06 | **BR-06** Partner information | FR-04, FR-09, FR-10, FR-12 | NFR-05, NFR-08, PR-07 | KPI-02–KPI-06, KPI-10 | US-03, US-04, US-07 | UAT-09, UAT-19, UAT-23, UAT-24 | EO-01, EO-06 | MVP (FR-12 if low effort) |
| BO-01, BO-04 | **BR-07** Regional patterns | FR-02, FR-05, FR-06 | DR-07 | KPI-07, KPI-08, KPI-02, KPI-05 | US-02 | UAT-02, UAT-05, UAT-17 | EO-04 | MVP |
| BO-06 | **BR-08** Protect sensitive info | FR-10, FR-11, FR-16 | PR-01–PR-08, SR-01–SR-08, DR-03 | KPI-06 (restricted), KPI-09 (small counts) | US-07, US-08, US-10 | UAT-09, UAT-10, UAT-11, UAT-12, UAT-18 | EO-06 | MVP |
| BO-04, BO-02 | **BR-09** Support action | FR-06, FR-15, FR-18 (deferred) | — | KPI-02, KPI-03, KPI-05, KPI-07, KPI-10 | US-04 | UAT-06, UAT-21 | EO-04 | MVP (FR-18 deferred) |
| All (constraint) | **BR-10** MVP constraint → CON-01 | *(none by design)* | — | — | US-09 | UAT-20 | — | Constraint |
| BO-05 | **BR-11** Access indicators | FR-01, FR-14 | — | KPI-03, KPI-04, KPI-09 | US-01, US-04 | UAT-01, UAT-06 | EO-05 | MVP |
| BO-07 | **BR-12** Reduce manual compilation | FR-11 | SR-05 | — | US-08 | UAT-12 | EO-07 | MVP if low effort (Could) |

---

## 4. Backward traceability

### 4.1 Functional requirement → business requirement → story → UAT

| FR | BR | User story | UAT | Release |
|---|---|---|---|---|
| FR-01 | BR-01, BR-05, BR-11 | US-01 | UAT-01 | MVP |
| FR-02 | BR-01, BR-07 | US-01, US-02 | UAT-02 | MVP |
| FR-03 | BR-02 | US-03 | UAT-03 | MVP |
| FR-04 | BR-02, BR-03, BR-06 | US-03 | UAT-04 | MVP |
| FR-05 | BR-01, BR-07, BR-09 | US-02 | UAT-05 | MVP |
| FR-06 | BR-09, BR-01, BR-02 | US-02, US-04 | UAT-06 | MVP |
| FR-07 | BR-04 | US-05 | UAT-07 | MVP |
| FR-08 | BR-05 | US-06, US-01 | UAT-08 | MVP |
| FR-09 | BR-01, BR-06, BR-07 | US-01, US-07 | UAT-23 | MVP if low effort |
| FR-10 | BR-08, BR-06 | US-07 | UAT-09, UAT-10, UAT-11 | MVP |
| FR-11 | BR-08, BR-12 | US-08 | UAT-12 | MVP if low effort |
| FR-12 | BR-01, BR-06 | **— (no story)** | UAT-19 | MVP if low effort |
| FR-13 | BR-02 | US-03 | UAT-22 | MVP |
| FR-14 | BR-03, BR-11 | US-04 | UAT-06 | MVP |
| FR-15 | BR-09, BR-03 | US-04 | UAT-21 | MVP |
| FR-16 | BR-02, BR-08 | US-10, US-03 | UAT-18 | MVP |
| FR-17 | BR-03, BR-05 | **— (no story)** | — | Deferred |
| FR-18 | BR-09 | **— (no story)** | — | Deferred |

### 4.2 Non-functional, data, privacy and security requirements → verification

| Req | Parent BR | Verified by | Release |
|---|---|---|---|
| NFR-01 | BR-01 | US-01 DoD · UAT-14 | MVP |
| NFR-02 | BR-01 | UAT-08 (freshness) · release readiness | MVP |
| NFR-03 | BR-01 | **Post-release monitoring only (no story or UAT)** | MVP (operational) |
| NFR-04 | BR-01, BR-06 | Baseline DoD · UAT-13 | MVP |
| NFR-05 | BR-03, BR-06 | US-04 DoD · UAT-24 | MVP |
| NFR-06 | BR-01 | **Volume test in release readiness (no story)** | MVP (operational) |
| NFR-07 | BR-04 | **Release readiness checklist (no story)** | MVP (operational) |
| NFR-08 | BR-06 | US-04 · UAT-24 (device subset) | MVP if low effort |
| DR-01, DR-02 | BR-04 | US-05 · UAT-07 | MVP |
| DR-03 | BR-08 | **Governance review (no story)** | MVP (operational) |
| DR-04, DR-05, DR-09 | BR-05 | US-06 · UAT-08 | MVP |
| DR-06 | BR-01 | US-01 AC2 · UAT-01 | MVP |
| DR-07, DR-10 | BR-02 | US-03 · UAT-03 | MVP |
| DR-08 | BR-04 | UAT-15, UAT-16, UAT-17 | MVP |
| PR-01, PR-02, PR-05 | BR-08 | US-07 AC5 · UAT-09 | MVP |
| PR-03, PR-04 | BR-08, BR-02 | US-10 · UAT-18 | MVP |
| PR-06 | BR-08 | **UAT entry criterion (privacy review approved), no story** | MVP (gate) |
| PR-07 | BR-08, BR-06 | US-03 AC5, US-07 · UAT-09 | MVP |
| PR-08 | BR-08 | Environment audit · UAT entry criterion | MVP (gate) |
| SR-01–SR-03 | BR-08 | US-07 · UAT-09, UAT-10, UAT-11 | MVP |
| SR-04, SR-05 | BR-08 | US-08 · UAT-12 | MVP |
| SR-06 | BR-08 | **Quarterly recertification (post-release)** | MVP (operational) |
| SR-07 | BR-08 | US-07 AC4 · UAT-09 | MVP |
| SR-08 | BR-08 | **Environment review (no story)** | MVP (gate) |

### 4.3 KPI → decision → requirements → stories

| KPI | Decision supported (Phase 6) | FR | US | Decision link strength |
|---|---|---|---|---|
| KPI-01 Capacity | Is capacity constraining or exceeding demand? | FR-01, FR-14 | US-01, US-04 | **Weak:** used mainly as a denominator; capacity-planning decisions are out of MVP scope |
| KPI-02 Utilization | Is demand filling capacity compared with peers? | FR-01, FR-04, FR-14 | US-01, US-04 | Strong |
| KPI-03 Attendance | Are booked patients attending? | FR-01, FR-14, FR-06 | US-04 | Strong |
| KPI-04 Completed exams | Is access growing in line with peers? | FR-01, FR-13 | US-01, US-03 | Strong |
| KPI-05 Conversion | Is the exam-to-eyewear hand-off working? | FR-01, FR-14, FR-06 | US-04 | Strong, **but visibility for Optometry Partners unresolved** (D-03) |
| KPI-06 Revenue per exam | Is commercial intensity in line with peers? | FR-01 | US-01, US-05, US-07 | **Weak:** context-only, not an exception driver; high misuse risk |
| KPI-07 Turnaround | Are orders delayed, and where? | FR-01, FR-06 | US-02 | Strong |
| KPI-08 On-time fulfilment | Are promises met? | FR-01, FR-06 | US-02 | Strong |
| KPI-09 Recall booking | Is recall bringing patients back? | FR-01, FR-14 | US-04, US-10 | Moderate (not meaningful for New stores) |
| KPI-10 Ramp index | Is this new store ramping like its peers? | FR-13 | US-03 | Strong |
| KPI-11 Completeness | Is data complete enough to act on? | FR-08 | US-06 | Strong (trust gate) |
| KPI-12 Freshness | Is data current enough to act on? | FR-08 | US-06 | Strong (trust gate) |

---

## 5. Gap and quality findings

### 5.1 Requirements without a business objective
| # | Finding | Assessment | Recommendation |
|---|---|---|---|
| RTM-01 | **BR-10** traces to no functional requirement and supports objectives only as a constraint. | Expected: reclassified in Phase 3. | Keep the ID; manage as CON-01 (Phase 10); exclude from requirement coverage metrics. |
| RTM-02 | **Operational requirements** NFR-03, NFR-06, NFR-07, DR-03, SR-06 and SR-08 have no user story. | Acceptable: verified through release readiness and operations, not user-facing stories. | Add them to the Phase 14 release-readiness checklist with named owners. |
| RTM-03 | **FR-12** (persistent filters) has a parent BR but no user story. | Gap (low risk; Could). | Either add a small story in Release 1 backlog refinement or defer; UAT-19 kept as an optional scenario. |

*No business requirement lacks a business objective.*

### 5.2 Business objectives without supporting requirements
| # | Finding | Assessment | Recommendation |
|---|---|---|---|
| RTM-04 | **BO-07** (reduce manual effort) is supported only by BR-12 (Could), FR-11 (Should) and US-08 (Should). There is **no Must-level MVP requirement**, and its measure (EO-07) has no baseline. | **Weakly supported objective.** | Confirm manual effort in discovery (U-13). If not confirmed, retire BO-07 or reframe it as a benefit hypothesis. Do not report EO-07 without a baseline. |
| RTM-05 | **BO-05** (balanced view) has no dedicated story; it is covered by acceptance criteria inside US-01 and US-04. | Acceptable but implicit. | Add an explicit design acceptance check to UAT-01 and UAT-06: access KPIs visible on each page. |

### 5.3 KPIs not connected to a decision
| # | Finding | Recommendation |
|---|---|---|
| RTM-06 | **KPI-01** (capacity) is not tied to a decision *within MVP scope*; it mainly serves as a denominator. | Keep as context on the diagnostic page; don't add capacity exceptions in MVP. |
| RTM-07 | **KPI-06** (revenue per completed exam) is context-only, not exam-linked, and has high misuse risk. | Keep role-restricted, excluded from exception rules and labelled "context". Revisit after the pilot whether it earns its place. |

### 5.4 User stories without fully testable acceptance criteria
| # | Finding | Recommendation |
|---|---|---|
| RTM-08 | **US-02** negative scenario depends on an unresolved decision (U-38: can managers see other regions' aggregates?). | Resolve U-38 before sprint commitment; until then the story is **not Ready**. |
| RTM-09 | **US-10** negative scenario depends on whether complementary suppression is required (U-39). | SH-13 decision required before the story is Ready. |
| RTM-10 | **US-04** comprehension check (80% describe a flag as "an area to investigate") is testable but depends on pilot sampling. | Define the script, sample size (5 or more) and question wording in Phase 14 (UAT-21). |
| RTM-11 | **US-09** is a process enabler; its criteria are testable against records (UAT report, sign-off record), not the product. | Acceptable; track as an enabler, not a feature. |

*All 10 stories have Given/When/Then criteria and a negative scenario.*

### 5.5 Duplicated or conflicting requirements
| # | Items | Type | Resolution status |
|---|---|---|---|
| RTM-12 | FR-09 ↔ FR-01 / FR-14 | Duplication (views versus pages) | Keep FR-09 as **role landing and entry-point** logic only; page content lives in FR-01 and FR-14. |
| RTM-13 | BR-01 ↔ BR-07 (C-01); BR-03 ↔ BR-09 (C-02) | Overlap | Kept distinct (monitoring versus pattern diagnosis; analysis versus action presentation). |
| RTM-14 | FR-04, FR-13 ↔ PR-03, PR-07 | Conflict (comparison versus confidentiality) | Resolved by FR-16 and US-10 (floor, fallback, anonymised peers). |
| RTM-15 | FR-11 ↔ SR-05, PR-04 | Conflict (export versus control) | Resolved by approved-visual list, aggregation, suppression and logging. |
| RTM-16 | **KPI-05 visibility for Optometry Partners.** Phase 5 hides *commercial* KPIs from OP by default, but does not classify conversion. US-04 AC5 lists OP-visible KPIs without conversion; FR-14 asks the question. | **Unresolved inconsistency** | **Proposed:** treat KPI-05 as a *clinical-retail bridge* measure, **visible to OP by default** (it contains no revenue), with neutral wording, pending the D-03 decision. Revenue stays hidden. No ID changes; decision logged in Phase 10 as U-41. |
| RTM-17 | **FR-06 rule (b) wording.** "Decline of 15% or more versus the store's own prior 8-week average" does not state what is compared. | Ambiguity | **Clarified (no meaning change):** compare the store's **4-week rolling value** with the **average of the 8 weeks immediately before that 4-week window**, for 3 consecutive weeks. Applied in Phases 12–13. |

### 5.6 Repair-pass traceability addendum (issue register → requirements → tests)

The repair pass (see `issue-register.md`) found behaviour that the ID-level matrix above could not detect: the requirements were traced, but the prototype did not meet several of them. No requirement IDs were changed; the rows below link the fixes to the existing IDs and to automated tests.

| # | Finding | Requirements affected | Resolution | Evidence |
|---|---|---|---|---|
| RTM-18 | Regional role scope not applied to Page 1, banner or peer names (ISS-01…03) | FR-01, FR-02, FR-10, SR-02, PR-07, US-02, US-07 | Scope applied before filters on every visual; out-of-region peers anonymous; network reference labelled | UI-RRM-01…03, JS-SCOPE-01, JS-PEER-02 |
| RTM-19 | Red selected week still produced values; Red rows entered peer groups (ISS-05) | FR-08, FR-06, KPI-10, US-04 negative scenario, US-06 AC3 | Engine withholds at the Red week; exclusion from peers and ramp peers | PY-RED-01…04, UI-RED-01…03 |
| RTM-20 | Suppression bypassed by chart positions; rate rule incomplete (ISS-07, ISS-08) | PR-04, US-10 AC3, UAT-18 | Demonstration rule v0.2; weekly counts shown as text | PY-SUP-01…03, JS-SUP-01/02, UI-SUP-01 |
| RTM-21 | Stage grouping dropped KPIs; rule (b) described as a peer difference; ramp trigger latest-week only (ISS-09…13) | FR-06, FR-15, KPI-10 | Exception rule set v0.2; rule-specific explanations | PY-EXC-01…06, PY-RAMP-01, UI-EXC-02…04 |
| RTM-22 | Filters, historical weeks and drill-through context missing (ISS-20) | FR-02, FR-05, US-02 AC3 | Implemented in the prototype | UI-NAV-01…04, UI-KEY-03 |
| RTM-23 | Definitions not reachable; accessibility and responsive gaps (ISS-21…23) | FR-07, US-05, NFR-04, NFR-08 | Definition dialog; keyboard and focus handling; responsive grid | UI-HELP-01, UI-A11Y-01…03, UI-KEY-01…05, UI-RESP-01…03 |
| RTM-24 | Access tests used a Prairies manager while the prototype and baseline use Atlantic (ISS-37) | US-07 AC2, UAT-10, ACC-03 | Aligned to Atlantic | Phase 8, Phase 14 |
| RTM-25 | Status wording implied acceptance (ISS-38, ISS-39) | All | Status lines say "drafted"; `feature-status-matrix.md` separates implemented, simulated, specified and deferred | DOC checks in `consistency-check.md` |

**Still unresolved (unchanged by the repair pass):** RTM-08 (US-02 not Ready: U-38), RTM-09 (US-10 not Ready: U-39), RTM-16 (KPI-05 visibility for Optometry Partners: U-41). The prototype uses labelled demonstration assumptions for all three (Phase 10, A-45 and A-46; primary suppression only for U-39).

---

## 6. MVP versus deferred requirements

| Category | MVP (Release 1) | MVP if low effort | Deferred / out of scope |
|---|---|---|---|
| Business requirements | BR-01–BR-09, BR-11 | BR-12 (Could) | — (BR-10 = constraint) |
| Functional | FR-01–FR-08, FR-10, FR-13–FR-16 | FR-09, FR-11, FR-12 | FR-17, FR-18 |
| Non-functional | NFR-01–NFR-07 | NFR-08 | — |
| Data | DR-01–DR-10 | — | — |
| Privacy | PR-01–PR-08 | — | — |
| Security | SR-01–SR-08 | — | — |
| KPIs | KPI-01–KPI-12 (KPI-06 context-only, restricted) | — | Loyalty (PC Optimum) KPIs |
| User stories | US-01, US-03–US-07, US-09, US-10 | US-02 (Should), US-08 (Should) | — |

## 7. Coverage summary

| Measure | Result |
|---|---|
| Business requirements with at least one objective | 12 / 12 |
| Business requirements (excluding BR-10 constraint) with at least one FR | 11 / 11 |
| FRs with at least one user story | 15 / 18 (FR-12, FR-17, FR-18 without) |
| MVP-core FRs with at least one UAT scenario | 13 / 13 |
| Stories with Given/When/Then and a negative scenario | 10 / 10 |
| Stories fully Ready (no unresolved dependency in criteria) | 8 / 10 (US-02, US-10 pending U-38, U-39) |
| KPIs with a strong decision link | 10 / 12 (KPI-01, KPI-06 weak) |
| Objectives with Must-level MVP support | 6 / 7 (BO-07 weak) |

---

## Phase 9 close

### Decisions made
1. Expected outcomes EO-01 to EO-07 defined; UAT-01 to UAT-24 titled.
2. No identifiers changed. Two clarifications recorded: RTM-16 (KPI-05 visibility proposal) and RTM-17 (FR-06 rule b), neither changing meaning.
3. 17 findings logged (RTM-01 to RTM-17). The most important: BO-07 weakly supported; US-02 and US-10 not yet Ready; KPI-06 weakly tied to a decision.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-37 | Operational requirements (availability, retention, recertification) are verified through release readiness and operations rather than user stories. |

### Questions requiring validation
- U-38, U-39 (carried forward); D-03 decision on KPI-05 visibility for Optometry Partners.

### Recommended corrections
- Adopt the RTM-16 proposal (KPI-05 visible to Optometry Partners, revenue hidden) unless SH-02 or SH-13 object.
- Add NFR-03, NFR-06, NFR-07, DR-03, SR-06 and SR-08 to the release-readiness checklist (Phase 14).
