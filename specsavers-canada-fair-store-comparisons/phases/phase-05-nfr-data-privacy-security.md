# Phase 5 — Non-Functional, Data, Privacy and Security Requirements

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–4

> **Outside-in disclaimer.** **All numerical targets in this phase are illustrative.** They are not confirmed Specsavers standards, service levels or policies. Legal and regulatory references are general context only, not legal advice. Applicability must be confirmed by Specsavers' Privacy Officer and legal advisers.

**Owner codes** use Phase 2 stakeholder IDs.

---

## 1. Non-functional requirements (NFR)

| ID | Statement | Rationale | Proposed target *(illustrative)* | Measurement method | Owner | Dependency | Validation question |
|---|---|---|---|---|---|---|---|
| **NFR-01** Performance | Report pages and interactions must respond quickly enough for weekly triage. | Slow reports reduce adoption during time-pressured store reviews. | 90% of page loads and slicer interactions complete in **5 seconds or less**; drill-through in **8 seconds or less** (1,000-store synthetic volume test). | Performance analyzer and load test in UAT; service usage metrics after release. | SH-11 (build), SH-12 (accountable) | Semantic model design; capacity | What response time do field users consider acceptable on store Wi-Fi or mobile? |
| **NFR-02** Refresh frequency | Data must be refreshed weekly and published by an agreed time. | Decisions are weekly (A-03); daily data raises cost and noise. | Prior week (Mon–Sun) published by **Tuesday 12:00 Pacific**; refresh success rate **98% or higher** per quarter. | Refresh logs; freshness KPI-12. | SH-10 | Source extract schedules (DEP) | Is a weekly cadence enough for new-store ramp-up monitoring? |
| **NFR-03** Availability | The report must be available during Canadian business hours across time zones. | Stores span Pacific to Newfoundland time. | **99%** availability, 07:00 NT to 20:00 PT on business days; planned maintenance announced 2 business days ahead. | Platform service health; incident log. | SH-12 | Platform SLA (assumed) | Are there existing platform service levels to inherit? |
| **NFR-04** Accessibility | The report must be usable by people with disabilities. | Inclusion; Canadian accessibility expectations, including provincial legislation such as Ontario's AODA (applicability to confirm). | Conform to **WCAG 2.1 AA** where the platform allows: contrast 4.5:1 or higher for text, no colour-only encoding, logical tab order, alt text on every visual, screen-reader tested. | Accessibility checklist; keyboard-only and screen-reader test in UAT (Phase 14). | SH-11 | Report theme; FR-06 icon design | Is there a corporate accessibility standard for internal tools? |
| **NFR-05** Usability | Users must complete core triage tasks without training beyond a short onboarding. | Adoption by busy partners and managers (Phase 2 D-09 and adoption risk). | **80%** of pilot users complete "identify the top 3 stores warranting attention and a candidate area for each" in **3 minutes or less**; System Usability Scale **70 or higher**. | Moderated task test in the pilot; SUS survey. | SH-09 | Prototype (Phase 13) | Which tasks matter most to each role? |
| **NFR-06** Scalability | The model and design must accommodate network growth without redesign. | Continued expansion (EV-02). | Supports **400 stores** and **3 years** of weekly history with NFR-01 still met; adding a store requires no report change. | Volume test with synthetic data; change review. | SH-10 | Store master process | What growth horizon should the model plan for? |
| **NFR-07** Supportability | The product must be documented and supportable by the data team. | Continuity as teams change. | Data dictionary, lineage, runbook and access procedure published **before go-live**; support requests acknowledged in **2 business days or less**. | Release-readiness checklist. | SH-12 | Support model | Who provides tier-1 support for partners? |
| **NFR-08** Device support | Partners must be able to view their store summary on a tablet or mobile. | Partners work on the store floor, not always at a desk. | Store Diagnostic page has a mobile layout; core KPIs legible at a **375 px** width. | Device test in UAT. | SH-11 | Platform mobile capability | Do partners use tablets or phones in-store? |

---

## 2. Data requirements (DR)

| ID | Statement | Rationale | Proposed target *(illustrative)* | Measurement method | Owner | Dependency | Validation question |
|---|---|---|---|---|---|---|---|
| **DR-01** Data lineage | Every displayed KPI must trace from visual → measure → model table → transformation → source system and field. | Trust, impact analysis and audit (BR-04). | **100%** of MVP KPIs have documented lineage; lineage reviewed at each KPI version change. | Lineage register (Phase 7) review; tooling-generated lineage where available. | SH-09 (document), SH-10 (maintain) | Phase 7 mappings | Does the platform capture lineage automatically? |
| **DR-02** KPI versioning | KPI definitions, thresholds, cohort boundaries, exception rules and prompt libraries must be versioned with effective dates and approvals. | Prevents silent definition changes (master rule 4). | **100%** of changes carry a version, approver, effective date and change reason; prior version retrievable. Changes communicated to users **5 or more business days** before taking effect (except urgent fixes). | Change log audit. | SH-13 (accountable), SH-09 | KPI change control (Phase 2 RACI) | Is there an existing change-control forum? |
| **DR-03** Data retention | The reporting model keeps only the history needed for decisions and trends. | Minimisation; cost; privacy. | Store-week aggregates kept for **current year plus 3 prior years** in the reporting model; source-level data follows source-system retention policies (not duplicated). | Retention job logs; annual review. | SH-13 | Corporate retention schedule | What retention schedule applies to operational and health-derived aggregates? |
| **DR-04** Data completeness | Each source must deliver expected records for each active store-week. | Incomplete data misleads comparisons (BR-05). | Store-week completeness **98% or higher** = Green; **90% to under 98%** = Amber; **under 90%** = Red (KPI-11). Network-level completeness **99% or higher** of active store-weeks each refresh. | Automated completeness checks per source per store-week (Phase 7 checkpoints). | SH-10 | A-20 load metadata | What are the known completeness issues by source? |
| **DR-05** Data freshness | Each source's latest load must be recent enough for the reporting week. | Stale data can generate false exceptions. | "Current" = source loaded **48 hours or less** before refresh and covers the full week; "Delayed" = over 48 hours to 7 days; "Stale" = over 7 days or week not covered (KPI-12). | Load timestamp comparison. | SH-10 | Source schedules | What latency does each source have today? |
| **DR-06** Aggregation and grain | The reporting model grain is **store × reporting week (Mon–Sun)**; all rates are computed from summed numerators and denominators. | Matches weekly decisions; limits privacy exposure; avoids averaging ratios. | **0** measures averaging store-level ratios; all facts keyed by store and week. | Measure code review; UAT reconciliation. | SH-09, SH-11 | Phase 7 model | Is a Monday week start consistent with internal reporting calendars? |
| **DR-07** Store master data | One authoritative store record per store, with a stable store key and effective-dated attributes: name, province, region, format, host banner, opening date, status. | Every comparison depends on correct attributes, especially opening date. | **100%** of active stores have a valid opening date, province, region and format; attribute changes are history-tracked; mismatched store keys across sources are **0** at release. | Master-data quality report; cross-source key reconciliation. | SH-15 or SH-04 (business owner, to confirm); SH-10 (technical) | DQ-33; SH-17 | Who maintains store attributes today, and in which system? |
| **DR-08** Reconciliation | Report totals must reconcile to agreed source or control totals within tolerance. | Credibility with Finance and functional owners (Phase 2 D-04). | Completed exams within **±0.5%** of scheduling or PMS control totals; net eyewear revenue within **±1.0%** of the finance control total for the week (timing differences documented); orders within **±0.5%** of order-management totals. | Weekly automated reconciliation report; UAT reconciliation tests. | SH-07, SH-06, SH-05 (sign-off per domain); SH-10 | Control totals availability | What tolerances does Finance accept for operational (non-financial) reporting? |
| **DR-09** Zero versus null | Genuine zero activity must be distinguishable from missing data. | Nulls treated as zero understate performance and trigger false exceptions. | **100%** of missing store-week source records stored as null with a data-quality reason; zero only where the source confirms zero activity (e.g., store closed with 0 slots). | Data-quality rule tests. | SH-10 | Phase 6 rules | Can sources confirm "no activity" (e.g., closure calendars)? |
| **DR-10** Maturity cohort derivation | Cohort must be derived **as at each week** from opening date using a versioned cohort table. | A store changes cohort during a period; a static cohort would misclassify ramp-up (Phase 7 design). | **100%** of store-weeks carry weeks_since_opening and cohort; cohort table version recorded per refresh. | Model test with stores crossing boundaries. | SH-04 (rules), SH-10 (build) | DR-07; Phase 6 approval | Are temporary closures excluded from weeks since opening? |

---

## 3. Privacy requirements (PR)

**Applicable context (to be confirmed).** Specsavers Canada's candidate privacy policy references PIPA or PIPEDA (EV-12). Personal health information may also fall under provincial health-information legislation, depending on province and custodian (e.g., Optometry Partner corporations). This case study does not determine applicability.

| ID | Statement | Rationale | Proposed target *(illustrative)* | Measurement method | Owner | Dependency | Validation question |
|---|---|---|---|---|---|---|---|
| **PR-01** No patient identifiers | The reporting model and reports must contain **no patient-identifiable data** (names, contact details, health numbers, dates of birth, appointment-level records). | Minimisation; purpose limitation; the MVP needs only aggregates. | **0** patient-identifying fields in the semantic model; aggregation to store-week happens **before** data enters the reporting zone. | Schema scan; privacy review sign-off; UAT field inspection. | SH-13 | Phase 7 privacy boundary | Where must patient-to-purchase linkage occur, and under whose custody? |
| **PR-02** No clinical diagnoses | No clinical diagnoses, findings, prescriptions or referral details may be included. | Outside decision scope; high sensitivity. | **0** clinical-content fields; exam counts only by generic appointment type. | Schema scan; PMS extract specification review. | SH-13, SH-02 | SH-17 | Do appointment-type codes themselves reveal sensitive information? |
| **PR-03** Minimum peer-group size | Peer statistics (median, quartiles, distribution) shown only when the peer group meets the minimum floor. | Prevents inferring an individual partner's results; improves statistical reliability. | Floor **5 stores** (set by SH-13; SH-04 may raise it, not lower it). Fallback to broader cohort; otherwise suppress. | UAT with small synthetic peer groups (FR-16). | SH-13 | FR-04, FR-16 | What floor does the Privacy Officer require for partner commercial data? |
| **PR-04** Small-count suppression | Displayed or exported counts of patient events below the threshold are suppressed at the displayed aggregation, and rates derived from them are not shown. | Reduces re-identification risk in small clinics and early ramp-up weeks. | **Demonstration rule v0.2 (illustrative):** counts from **1 to 4** displayed as "<5" (zero shown as 0); a rate is hidden when its denominator is under 5 ("n/a (low volume)") **or** its count-based numerator is 1–4 ("Suppressed (<5)"), because a visible denominator would otherwise reveal the count. Suppressed values are never plotted at their true position or listed in tooltips or data tables. Applies to recall bookings, statuses not recorded, no-shows, cancellations and any sub-store segment. *Clarification of the earlier wording, which covered only small denominators (issue ISS-08).* Primary suppression alone is **not** claimed to prevent disclosure through differencing; complementary suppression is U-39. | Suppression test cases (PY-SUP-01…03, JS-SUP-01/02, UI-SUP-01); export comparison when exports exist. | SH-13 | Phase 6 KPI rules | Is suppression required at store-week level for all event types, or only for sub-segments? Is complementary suppression required (U-39)? |
| **PR-05** No individual performance | No individual employee, optician or optometrist dimension or measure. | Phase 1 exclusion; employment and professional sensitivities. | **0** practitioner or employee attributes in the model. | Schema scan. | SH-13, SH-04 | Source extract design | Does capacity data require practitioner-level input upstream, and how is it aggregated? |
| **PR-06** Purpose and privacy review | Use of health-derived aggregates must be documented, reviewed and approved before the pilot. | Accountability; appropriate purpose. | Privacy impact assessment (or equivalent) approved **before UAT with real data**; reviewed annually or on material change. | Approval record. | SH-13 (accountable) | Phase 7 data flows | What review process exists for new analytics uses of health data? |
| **PR-07** Partner commercial confidentiality | Partners may view only their own store's commercial KPIs; peer comparisons use anonymised aggregates with no peer store names. | Partners are independent businesses (EV-03); Phase 2 D-01. | **0** peer store identifiers visible to RP or OP roles in visuals, tooltips, exports or drill-through. | Role-based UAT (Phase 14). | SH-13, SH-07, SH-14 (consulted) | SR-02, SR-03 | Would partners accept named peer comparisons under any condition (e.g., opt-in)? |
| **PR-08** Synthetic data in non-production | Development and demonstration use synthetic or de-identified data only. | Prevents exposure during build and demos. | **100%** of non-production datasets approved as synthetic or de-identified. | Environment audit. | SH-12, SH-13 | Phase 12 dataset | Are there existing de-identification standards? |

---

## 4. Security and access requirements (SR)

### Proposed role model (illustrative)

| Role | Row scope | Commercial KPIs (revenue per exam, eyewear revenue) | Clinical-activity KPIs (exams, attendance, recall) | Export |
|---|---|---|---|---|
| Retail Partner (RP) | Own store(s) | Own store only | Own store only | Own store, aggregated |
| Optometry Partner (OP) | Own clinic's store(s) | **Hidden by default** (pending D-03 decision) | Own store only | Own store, aggregated |
| Regional Retail Manager (RRM) | Assigned region(s) | Region stores | Region stores | Region, aggregated |
| Retail Operations leadership (ROL) | Network | Network | Network | Network, aggregated |
| Finance analyst (FUN-FIN) | Network | Network | Counts only | Network, aggregated |
| Supply Chain analyst (FUN-SC) | Network | **Hidden** | Hidden, except fulfilment KPIs | Fulfilment tables only |
| Marketing analyst (FUN-MKT) | Network | **Hidden** | Recall and booking KPIs | Recall tables only |
| Governance / administrator (GOV/ADM) | Network (admin, for testing) | As required, logged | As required, logged | Logged |

**Revenue per completed exam (KPI-06) visibility rule:** visible to RP (own store), RRM (region), ROL, FUN-FIN (network). Hidden from OP by default, FUN-SC and FUN-MKT. Tested in UAT-11 (Phase 14).

**Prototype versus production (added in the repair pass).** The HTML prototype (`dashboard-mockup.html`) embeds the full synthetic dataset and offers a "View as role" selector. It **simulates** what each role would see (scope, anonymous peers, revenue restriction); it does **not** implement authentication, row-level security, object-level security, audit logging or export control. SR-01 to SR-08 below remain production requirements that have not been built or tested in this case study. Demonstration assumptions used by the prototype, pending decisions: a Regional Retail Manager sees own-region stores plus a labelled network reference, but no other region's figures (U-38); Optometry Partners see conversion but not revenue (U-41).

| ID | Statement | Rationale | Proposed target *(illustrative)* | Measurement method | Owner | Dependency | Validation question |
|---|---|---|---|---|---|---|---|
| **SR-01** Least privilege | Users receive the minimum role and scope needed; access is denied by default. | Protects patient-derived and commercial data (BR-08). | **100%** of users have a role mapping; **0** users with network scope without approval. | Access register review. | SH-13 (accountable), ADM | A-24 | Who approves network-level access? |
| **SR-02** Row-level security | Row visibility is filtered by an access mapping of user → store or region, maintained outside the report. | Scales with store openings and staff changes. | New or changed assignments are effective within **1 business day** of approval; leavers removed within **1 business day**. | Mapping table audit; joiner/mover/leaver test. | SH-10 (build), SH-13 (approve) | HR or partner records (A-24) | What is the authoritative source for store assignments? |
| **SR-03** Object-level security | Commercial measures are hidden from unapproved roles across all interfaces. | Commercial confidentiality; D-03. | **0** leakage of hidden measures through visuals, tooltips, Q&A, "Analyze in Excel" or exports. | Role-based UAT (UAT-11). | SH-11, SH-13 | A-23 | Which roles are approved for revenue data? |
| **SR-04** Auditability | Access, export and permission-change events are logged and reviewable. | Accountability; incident investigation. | Logs retained **12 months**; monthly review of export volumes and anomalies; permission changes logged with approver. | Audit log inspection. | SH-13 | Platform audit logs (assumed) | What audit retention is required? |
| **SR-05** Export restrictions | Exports limited to approved visuals, aggregated data, with confidentiality labels; no underlying data export. | Prevents uncontrolled distribution. | **100%** of exports labelled; **0** row-level exports; export disabled for unapproved visuals. | UAT-12; tenant setting review. | SH-13, SH-11 | FR-11; PR-04 | Are sensitivity labels available in the platform? |
| **SR-06** Access recertification | Access is periodically recertified by business owners. | Network growth and staff churn create access drift. | Quarterly recertification; **100%** of mappings reviewed; unconfirmed access removed within **10 business days**. | Recertification record. | SH-04 (business), SH-13 | SR-02 | Is there an existing access review cycle? |
| **SR-07** Authentication | Access via corporate single sign-on with multi-factor authentication. | Partners and staff span many locations and devices. | **100%** of sessions via SSO and MFA; no shared accounts. | Identity provider configuration review. | SH-13 | Identity platform (assumed) | Do partners use corporate identities? |
| **SR-08** Environment separation | Separate development, test and production environments; production data access restricted. | Prevents accidental exposure during build. | **3** environments; production access limited to named administrators; deployment via controlled pipeline. | Environment review. | SH-12 | PR-08 | What deployment pipeline exists? |

---

## 5. Coverage check against the Phase 5 prompt

| Topic | Requirement(s) |
|---|---|
| Performance | NFR-01 |
| Refresh frequency | NFR-02 |
| Availability | NFR-03 |
| Accessibility | NFR-04 |
| Usability | NFR-05, NFR-08 |
| Data lineage | DR-01 |
| KPI versioning | DR-02 |
| Data retention | DR-03 |
| Data completeness | DR-04 |
| Data freshness | DR-05 |
| Aggregation | DR-06, PR-03, PR-04 |
| Patient privacy | PR-01, PR-02, PR-04, PR-06, PR-08 |
| Commercial confidentiality | PR-07, SR-03 |
| Least-privilege access | SR-01, SR-02, SR-06 |
| Auditability | SR-04, DR-02 |
| Export restrictions | SR-05, FR-11 |

---

## Phase 5 close

### Decisions made
1. 8 NFRs, 10 DRs, 8 PRs and 8 SRs defined; all numeric targets labelled illustrative.
2. Aggregation to store-week happens **before** data enters the reporting zone (the privacy boundary).
3. Role model drafted; revenue per completed exam hidden from Optometry Partners by default, pending the D-03 decision.
4. Peer floor (PR-03) and small-count suppression (PR-04) are separate controls: one protects partners' commercial data, the other patient-event counts.
5. Maturity cohort derived as at each week (DR-10).

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-25 | The platform provides SSO/MFA, audit logs, sensitivity labelling and export controls. |
| A-26 | Finance can provide a weekly control total for net eyewear revenue by store. |
| A-27 | A Monday–Sunday reporting week is acceptable. |

### Questions requiring validation
- U-29. Which privacy legislation and custodianship model applies to exam-derived aggregates in each province?
- U-30. Required peer floor and suppression threshold.
- U-31. Should Optometry Partners see commercial KPIs? (Linked to D-03.)
- U-32. Authoritative source for user-to-store assignments.

### Recommended corrections
- None to earlier phases. FR-04 and FR-16 now reference PR-03 as the source of the floor.
