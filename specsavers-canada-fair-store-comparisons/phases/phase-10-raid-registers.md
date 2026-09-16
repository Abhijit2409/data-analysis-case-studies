# Phase 10 — Risks, Assumptions, Constraints, Dependencies and Open Questions

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–9

> **Outside-in disclaimer.** These registers are case-study hypotheses. Probability and impact ratings are the analyst's illustrative judgements, not Specsavers risk assessments.

**Rating scale.** Probability (P) 1 = rare … 5 = almost certain · Impact (I) 1 = minimal … 5 = severe · **Rating = P × I**: 1–6 **Low**, 8–12 **Medium**, 15–25 **High**.

---

## 1. Risk register

| ID | Risk | Cause | Consequence | P | I | Rating | Mitigation | Contingency | Owner | Early-warning indicator |
|---|---|---|---|---|---|---|---|---|---|---|
| R-01 | **Conflicting KPI definitions** across functions | Functions define conversion, revenue or turnaround differently (I-04) | Numbers disputed; trust lost; rework | 4 | 4 | **16 High** | KPI workshops per domain; governed dictionary (FR-07, DR-02); single approver (Phase 2 RACI) | Show both definitions labelled during the pilot; escalate to SH-04 | SH-04 / SH-13 | Two or more definitions surface in discovery; reconciliation disputes in UAT |
| R-02 | **Unfair store comparisons** | Maturity, format, province or market not controlled | Partners alienated; wrong stores targeted | 3 | 5 | **15 High** | Cohort × format peers; as-at-week cohorts (DR-10); anonymised distributions; comprehension testing | Remove rankings; show own-trend-only views until rules are revised | SH-04 | Pilot fairness score under 80% (EO-01); partner complaints via SH-14 |
| R-03 | **Insufficient peer-group size** | Small cohorts in new provinces or formats; floor of 5 | Comparisons suppressed or noisy | 4 | 3 | **12 Medium** | Fallback hierarchy (FR-16); a broader peer basis for the ramp index; review floor after pilot. *Synthetic data confirms the issue: the New cohort falls below 5 stores late in the window.* | Show own-trend and network context without peer statistics | SH-13 / SH-09 | Share of store-weeks with suppressed peer statistics over 25% |
| R-04 | **Missing or delayed data** | Source outages; new-store onboarding lag; manual feeds | False exceptions; stale decisions | 4 | 4 | **16 High** | Completeness and freshness checks (CP-01, CP-09); withholding rules (FR-08); publish gate | Keep prior week published with banner; manual data-quality note to users | SH-10 | Refresh success under 98%; Red store-weeks over 5% |
| R-05 | **Privacy exposure** | Identifiers or small counts leak; clinical content extracted | Legal, regulatory and trust harm | 2 | 5 | **10 Medium (critical impact)** | Privacy boundary (CP-06); PR-01 to PR-04; privacy review before UAT (PR-06); synthetic non-prod data (PR-08) | Withdraw report; incident process; privacy officer notification | SH-13 | Schema scan finds identifier-like fields; export anomalies in audit log |
| R-06 | **Commercial-data exposure** | Partners see others' revenue; exports forwarded | Partner trust damaged; confidentiality breach | 3 | 4 | **12 Medium** | RLS and OLS (SR-02, SR-03); anonymised peers (PR-07); export controls (SR-05) | Disable exports; revoke access; notify affected partners per policy | SH-13 / SH-07 | Access test failures; unusual export volumes |
| R-07 | **Low dashboard adoption** | Not embedded in routines; low trust; poor usability | No value realised; spreadsheets persist | 3 | 4 | **12 Medium** | Co-design with SH-03; embed in weekly review; training; role landing pages (FR-09) | Targeted coaching; simplify pages; revisit KPI set | SH-04 / SH-08 | Weekly active pilot users under 60%; declining visits after week 2 |
| R-08 | **Continued spreadsheet usage** | Familiar tools; missing fields; distrust | Parallel versions of truth | 4 | 3 | **12 Medium** | Inventory spreadsheets (U-13); close gaps; approved exports (FR-11); retire named reports (BR-12) | Reconcile spreadsheet to report publicly; sponsor directive | SH-04 | Requests for raw extracts; spreadsheets cited in meetings |
| R-09 | **Changing priorities** | Expansion, leadership agenda, loyalty programme | Scope churn; delays | 3 | 3 | **9 Medium** | MVP constraint (CON-01); fortnightly priority review; decision log | Re-baseline scope with SH-04 and SH-08 | SH-08 | New urgent requests displacing sprint goals |
| R-10 | **Scope expansion** | Requests for PC Optimum, inventory, P&L | MVP delayed; quality diluted | 4 | 3 | **12 Medium** | Explicit exclusions (Phase 1, Phase 11); enhancement backlog with rationale | Time-box extras to Release 2 | SH-08 | Over 10% of story points added after sprint planning |
| R-11 | **Incorrect causal interpretation** | Users read flags or prompts as causes | Wrong actions; unfair blame | 4 | 4 | **16 High** | Non-causal prompt vocabulary (FR-15); prohibited terms test (UAT-21); training; tooltips | Rewrite prompts; add "correlation ≠ cause" training module | SH-09 / SH-04 | Pilot comprehension under 80%; meeting notes citing "the dashboard shows X caused Y" |
| R-12 | **Provincial differences** misread as performance | Regulation, coverage and awareness differ by province (EV-04, EV-07) | Unfair province comparisons | 3 | 3 | **9 Medium** | Province as context and filter; peers not forced across provinces for sensitive KPIs; notes on coverage differences | Province-specific peer basis (post-pilot) | SH-04 / SH-13 | Consistent province-level outliers without an operational explanation |
| R-13 | **Store-format differences** | Grocery-hosted versus shopping centre versus street-front traffic and space | Format effects mistaken for store issues | 3 | 3 | **9 Medium** | Format in the peer rule; format views | Format-only comparisons | SH-04 | Exceptions concentrated in one format |
| R-14 | **Source-system integration** | Sources not in the platform; API or extract limits; vendor constraints (EV-09d) | Delays; missing KPIs | 4 | 4 | **16 High** | Early data-access checks (TQ-01); Sprint 0 profiling; prioritise KPIs by source readiness | Release with available KPIs; mark others "coming soon" | SH-10 / SH-17 | Data access not granted by end of Sprint 0 |
| R-15 | **Master-data inconsistency** | Opening dates, formats or regions differ by system; conversions and relocations | Wrong cohorts; wrong peers; broken joins | 4 | 4 | **16 High** | Store crosswalk (MDM-02); opening-date definition (DQ-33); CP-02 and CP-04 | "Unclassified" handling; manual correction list with SH-15 | SH-15 / SH-10 | Unmapped store codes over 0; opening date after first sale |
| R-16 | **Exam–purchase linkage infeasible** | Custody, consent or technical limits (TQ-03) | KPI-05 unavailable or unreliable | 3 | 4 | **12 Medium** | Early privacy and technical assessment; aggregate-only design | Replace with store-level ratio (purchasing customers ÷ exams, unlinked) labelled as a proxy | SH-13 / SH-10 | Linkage match rate under 95% in profiling |
| R-17 | **Stakeholder availability** for workshops and UAT | Partners run stores; seasonal peaks | Delays; weak validation | 3 | 3 | **9 Medium** | Short sessions; book early; SH-14 representation; remote options | Extend UAT by one week; smaller tester set with SH-13 witnesses | SH-12 | Under 70% of booked sessions attended |
| R-18 | **Exception fatigue** | Too many flags per week | Flags ignored | 3 | 3 | **9 Medium** | Rule thresholds tuned in pilot; severity sort; cap per region | Raise thresholds; show top N | SH-03 / SH-04 | Over 15 flags per manager per week; low follow-up rate (EO-04) |
| R-19 | **Metrics used as individual performance management** | Flags read as partner or manager ratings (D-09) | Resistance; gaming | 3 | 4 | **12 Medium** | No individual scoring (PR-05); support-trigger framing; SH-14 principles | Remove ranking visuals; governance reminder | SH-04 | Flags quoted in performance reviews |
| R-20 | **Loyalty-programme launch distorts trends** | PC Optimum from 22 Jun 2026 (EV-08) may shift purchasing | Before/after comparisons misread | 2 | 3 | **6 Low** | Annotate launch date (FR-17, deferred); compare peers in the same period rather than pre/post | Exclude launch weeks from baseline windows | SH-07 / SH-05 | Network-wide step change around the launch week |
| R-22 | **Prototype mistaken for secured or production-ready** *(repair pass)* | The HTML mockup embeds all synthetic data and simulates roles; screenshots look finished | Security, privacy or data claims repeated without evidence | 3 | 3 | **9 Medium** | "Simulated role view" note on every page; feature-status matrix; SR-01–SR-08 kept as production requirements; DAX labelled unexecuted | Withdraw the claim; restate the status matrix | SH-09 | The prototype described as "secured", "tested with users" or "compliant" |
| R-21 | **Official-language requirements** | New Brunswick is officially bilingual; partner language preferences unknown | Accessibility and adoption gaps | 2 | 3 | **6 Low** | Validate language needs (U-40); design labels for translation | Provide French labels and definitions in Release 2 | SH-04 | Requests for French material from pilot partners |

**Heat summary:** High = R-01, R-02, R-04, R-11, R-14, R-15 · Medium = R-03, R-05, R-06, R-07, R-08, R-09, R-10, R-12, R-13, R-16, R-17, R-18, R-19 · Low = R-20, R-21. R-05 is Medium by score but tracked as critical because of its impact.

---

## 2. Assumptions register

**Confidence:** H = high · M = medium · L = low.

| ID | Assumption | Phase | Confidence | Impact if wrong | Validation method | Owner |
|---|---|---|---|---|---|---|
| A-01 | Operational activity is recorded digitally and can be aggregated to store-week | 1 | M | No data product possible for some KPIs | Data inventory (TQ-01) | SH-10 |
| A-02 | A store master exists or can be created | 1 | M | Cohorts and peers unreliable | MDM review | SH-10 / SH-15 |
| A-03 | Store-week grain is sufficient | 1 | M | Rework to daily grain | User interviews | SH-09 |
| A-04 | Support Office functions support store performance | 1 | M | Wrong audience | Stakeholder mapping | SH-04 |
| A-05 | Partners accept fair, aggregated peer comparison | 1 | M | Adoption failure | Partner interviews; SH-14 | SH-04 |
| A-06 | Aggregated exam counts can be shared with retail users | 1 | L | Views redesigned | Privacy review | SH-13 |
| A-07 | Formats other than grocery-hosted exist | 1 | M | Format peer rule changes | Store master review | SH-04 |
| A-08 | Power BI is appropriate | 1 | H | Tool change | Confirm with data team (EV-09) | SH-11 |
| A-09 | Synthetic data can represent patterns realistically | 1 | H | Misleading prototype | Stakeholder walkthrough | SH-09 |
| A-10 | Maturity is the main driver during years 1–2 | 1 | M | Peer rule changes | Historical analysis | SH-09 |
| A-11 | Peer dimensions are maturity, province, format, market | 1 | M | Peer rule changes | Workshop | SH-04 |
| A-12 | A retail-operations leader would sponsor | 2 | M | No sponsor | Sponsor conversation | SH-08 |
| A-13 | Partners are consultees, not approvers | 2 | M | Governance redesign | Operating model review | SH-04 |
| A-14 | A regional field-management function exists | 2 | M | Persona changes | Org review | SH-04 |
| A-15 | Domain functions nominate KPI owners | 2 | M | Definitions stall | RACI confirmation | SH-04 |
| A-16 | The Privacy Officer reviews the access model | 2 | H | Approval route unclear | Governance process | SH-13 |
| A-17 | The Partnership Advisory Committee suits endorsement | 2 | L | Alternative channel needed | SH-14 remit | SH-04 |
| A-18 | Stakeholders available for 8–10 weeks (illustrative) | 2 | M | Delay | Calendar booking | SH-12 |
| A-19 | Some manual compilation exists | 3 | L | BO-07 retired | Survey (U-13) | SH-09 |
| A-20 | Load metadata available per source and store | 3 | M | Data-quality indicators limited | Platform review | SH-10 |
| A-21 | KPI domain maps to a follow-up team | 3 | M | Prompts less actionable | Workshop | SH-04 |
| A-22 | A 4-week rolling window smooths volatility | 4 | M | Noisy or late flags | Pilot tuning | SH-09 |
| A-23 | Platform supports RLS, OLS, drill-through, export controls | 4 | H | Design workarounds | Technical spike | SH-11 |
| A-24 | Users can be mapped to stores or regions from an authoritative source | 4 | M | Access errors | HR or partner data review | SH-10 |
| A-25 | Platform provides SSO/MFA, audit, labels, export controls | 5 | M | Security gaps | Tenant review | SH-13 |
| A-26 | Finance provides weekly revenue control totals | 5 | L | Reconciliation weaker | Finance workshop (TQ-07) | SH-07 |
| A-27 | Monday–Sunday week acceptable | 5 | M | Calendar change | Confirm reporting calendar | SH-07 |
| A-28 | Cancelled slots rarely re-booked in the same week | 6 | L | Utilization overstated | Scheduling data profiling | SH-10 |
| A-29 | Reschedules resolved upstream | 6 | M | Double counting | TQ-05 | SH-17 |
| A-30 | 30-day attribution windows reasonable | 6 | M | KPI-05 and KPI-09 bias | Data analysis | SH-05 / SH-04 |
| A-31 | Upstream linkage possible without exposing identifiers | 6 | L | KPI-05 proxy only (R-16) | Privacy and technical assessment | SH-13 |
| A-32 | Layered data platform available or feasible | 7 | M | Architecture rework | Platform review | SH-10 |
| A-33 | Pseudonymous linkage keys can be created | 7 | L | As A-31 | As A-31 | SH-13 |
| A-34 | Store codes crosswalk to one store_id | 7 | M | Join failures | MDM profiling | SH-10 |
| A-35 | Role-based test accounts available | 8 | M | Access testing weakened | Environment setup | SH-12 |
| A-36 | Pilot users available for comprehension checks | 8 | M | BR-03 measure untested | Pilot planning | SH-09 |
| A-37 | Operational requirements verified by readiness and operations | 9 | H | Gaps unnoticed | Readiness checklist | SH-12 |
| A-38 | **(new)** The pilot group can include stores from at least one recently entered province | 10 | M | Pilot lacks new-market insight | Pilot selection | SH-04 |
| A-39 to A-43 | Recorded in Phases 11–14 (see those documents) | 11–14 | — | — | — | — |
| A-44 | *(repair pass)* A finalised synthetic snapshot is acceptable for demonstration if labelled; production marks attribution and fulfilment windows provisional | 12 | H | Users compare provisional with final weeks | Dashboard banner; KPI-05/07/09 rules | SH-09 |
| A-45 | *(repair pass, demonstration assumption)* Regional managers see own-region stores and a labelled network reference, not other regions' figures, until U-38 is decided | 13 | M | Wrong scope design | Privacy and sponsor decision (U-38) | SH-13 / SH-04 |
| A-46 | *(repair pass, demonstration assumption)* Optometry Partners see conversion (KPI-05) but not revenue, until U-41 is decided | 13 | L | Clinical-sensitivity objection | U-41 decision with SH-02 | SH-02 / SH-13 |
| A-47 | *(repair pass)* Turnaround weighted by orders placed (all orders reach ready) is acceptable for the synthetic demonstration only | 12 | H | Misread as production logic | KPI-07 v0.2 note | SH-06 |

---

## 3. Constraints register

| ID | Constraint | Source | Implication |
|---|---|---|---|
| CON-01 | **MVP limited to 3 pages, store-week grain, approved KPIs; pilot within an illustrative 12 weeks of build start** | BR-10 (Phase 3) | Strict backlog control; FR-17 and FR-18 deferred |
| CON-02 | Case study limited to public information; no internal access | Master context | All internal facts are assumptions or questions |
| CON-03 | Only synthetic data used for prototype and demonstration | Master context; PR-08 | Findings illustrative only |
| CON-04 | No patient-identifiable data, clinical diagnoses or individual employee/clinician performance | Master context; PR-01, PR-02, PR-05 | Aggregation at privacy boundary; no practitioner dimension |
| CON-05 | Reporting must respect partner ownership and provincial regulation | EV-03, EV-04 | Anonymised peers; consultative governance |
| CON-06 | Power BI is the reporting platform for the prototype | Job posting (EV-09a); A-08 | Design uses Power BI capabilities |
| CON-07 | PC Optimum and loyalty analytics excluded from MVP | Master context | Future enhancement only |
| CON-08 | No named Specsavers platforms or architecture may be asserted | Master context | Generic system categories only |
| CON-09 | All numeric targets illustrative until validated | Master context; Phase 5 | Baselines required before targets are set |

---

## 4. Dependencies register

| ID | Dependency | Type | Needed for | Owner | Needed by (illustrative) | Impact if late |
|---|---|---|---|---|---|---|
| DEP-01 | Access to source data (S2–S7) in a development environment | Internal technical | All KPIs | SH-10 / SH-17 | End of Sprint 0 | Build blocked (R-14) |
| DEP-02 | Authoritative store master with opening dates, formats, regions | Internal data | FR-03, FR-04, KPI-10 | SH-15 / SH-04 | Sprint 1 | Cohorts and peers unavailable (R-15) |
| DEP-03 | Privacy review approval (PR-06) | Governance | UAT with real data; pilot | SH-13 | Before UAT | Pilot delayed |
| DEP-04 | KPI definitions approved (v1.0) | Business | FR-07; UAT sign-off | SH-04 + KPI owners | Sprint 2 | Disputed numbers (R-01) |
| DEP-05 | Identity integration and user–store access mapping | Internal technical | FR-10, SR-02 | SH-10 / SH-13 | Sprint 3 | Access testing blocked |
| DEP-06 | Platform features: RLS, OLS, export controls, audit logs | Platform | SR-01 to SR-05 | SH-11 / SH-13 | Sprint 0 spike | Security redesign |
| DEP-07 | Finance weekly control totals | Business data | DR-08; UAT-16 | SH-07 | Sprint 2 | Revenue KPI withheld |
| DEP-08 | Stakeholder time: workshops, prototype tests, UAT | People | Requirements; UAT | SH-12 | Booked 4 weeks ahead | Weak validation (R-17) |
| DEP-09 | Partnership Advisory Committee endorsement of comparison principles | Governance | Partner rollout | SH-04 / SH-14 | Before pilot | Adoption risk (R-02, R-07) |
| DEP-10 | Investigation prompt library approved | Business | FR-15 | SH-04 (with SH-02, SH-16) | Sprint 3 | Exceptions without prompts |
| DEP-11 | Data engineering and visualization capacity | Resourcing | Build | SH-12 | Sprint 0 | Timeline slip |
| DEP-12 | Non-production environment with synthetic data and role test accounts | Technical | UAT-09 to UAT-12, UAT-18 | SH-12 / SH-10 | Before UAT | Access tests incomplete |

---

## 5. Open questions register

IDs are carried forward from earlier phases. The **Blocking** column marks questions that must be answered before the named milestone.

| ID | Question | Theme | Owner | Blocking? | Needed by |
|---|---|---|---|---|---|
| U-01 | What store-performance reporting exists today, and is it trusted? | Problem | SH-04 / SH-03 | Yes | Discovery |
| U-02 | Is the comparison problem real, and for whom? | Problem | SH-03 / SH-01 | Yes | Discovery |
| U-03 | Which KPI definitions are used today? | KPIs | SH-04 | Yes | Requirements |
| U-04 | Source systems, integration and latency? | Data | SH-10 | Yes | Sprint 0 |
| U-05 | Can exams and purchases be linked, and under what privacy controls? | Data / Privacy | SH-13 / SH-10 | Yes (KPI-05) | Sprint 1 |
| U-06 | Who owns the store master? | MDM | SH-04 / SH-15 | Yes | Sprint 0 |
| U-07 | Internal store-maturity definition? | KPIs | SH-04 | Yes | Sprint 1 |
| U-08 | Applicable privacy obligations for exam-derived aggregates? | Privacy | SH-13 | Yes | Before UAT |
| U-09 | May partners see peer figures? | Privacy | SH-13 / SH-14 | Yes | Sprint 2 |
| U-10 | Host-retailer data-sharing constraints? | Legal | SH-13 | No | Release 2 |
| U-11 | How fulfilment works; definition of "on time"? | KPIs | SH-06 | Yes (KPI-07/08) | Sprint 1 |
| U-12 | Recall programme ownership and attribution? | KPIs | SH-05 | No | Sprint 2 |
| U-13 | How much manual reporting effort exists? | Value | SH-09 | No (BO-07) | Discovery |
| U-14 | Stakeholder availability? | Delivery | SH-12 | Yes | Mobilise |
| U-15 | How to flag PC Optimum timing in trends? | KPIs | SH-07 / SH-05 | No | Release 2 |
| U-16 | Actual titles and decision rights for SH-03, SH-04, governance? | Stakeholders | SH-08 | No | Discovery |
| U-17 | Who is sponsor and KPI approver? | Governance | SH-08 | Yes | Mobilise |
| U-18 | Anonymised peer benchmarks allowed, at what aggregation? | Privacy | SH-13 | Yes | Sprint 2 |
| U-19 | Partnership Advisory Committee remit? | Governance | SH-04 | No | Before pilot |
| U-20 | Existing KPI change-control forum? | Governance | SH-13 | No | Sprint 1 |
| U-21 | Clinical acceptance of conversion as a measure? | KPIs | SH-02 / SH-16 | Yes (KPI-05 display) | Sprint 2 |
| U-22 | Baselines for success measures? | Value | SH-09 | No (before targets) | Pilot start |
| U-23 | Is an action log wanted later? | Scope | SH-08 | No | Release 2 |
| U-24 | Weighting of access versus commercial indicators? | Design | SH-04 | No | Sprint 2 |
| U-25 | Manageable exception volume per manager? | Design | SH-03 | No | Pilot |
| U-26 | Should OP see purchase-stage metrics? | Access | SH-02 / SH-13 | Yes (see U-41) | Sprint 2 |
| U-27 | Prompt library owner? | Governance | SH-04 | Yes | Sprint 3 |
| U-28 | Include Amber data in totals? | KPIs | SH-04 | No | Sprint 2 |
| U-29 | Legislation and custodianship by province? | Privacy | SH-13 | Yes | Before UAT |
| U-30 | Required peer floor and suppression threshold? | Privacy | SH-13 | Yes | Sprint 2 |
| U-31 | Should OP see commercial KPIs? | Access | SH-13 / SH-02 | Yes | Sprint 3 |
| U-32 | Authoritative source for user–store mapping? | Security | SH-10 | Yes | Sprint 3 |
| U-33 | Exam types in scope; appointment or completion date? | KPIs | SH-16 | Yes | Sprint 1 |
| U-34 | Attribution windows? | KPIs | SH-04 / SH-05 | No | Sprint 2 |
| U-35 | Contact lenses, insurer billing, loyalty redemptions in revenue? | KPIs | SH-07 | Yes (KPI-06) | Sprint 2 |
| U-36 | Promised-date standards? | KPIs | SH-06 | Yes (KPI-08) | Sprint 1 |
| U-37 | Capacity-normalised ramp index? | KPIs | SH-04 | No | Pilot review |
| U-38 | Can managers see other regions' aggregates? | Access | SH-13 / SH-04 | Yes (US-02 Ready) | Sprint 2 |
| U-39 | Complementary suppression required? | Privacy | SH-13 | Yes (US-10 Ready) | Sprint 2 |
| U-40 | **(new)** Are French-language labels and definitions required (e.g., New Brunswick partners)? | Accessibility | SH-04 | No | Before pilot |
| U-41 | **(new)** Confirm KPI-05 visible to Optometry Partners by default, revenue hidden (RTM-16 proposal, D-03) | Access | SH-02 / SH-13 | Yes | Sprint 2 |
| U-42 | *(repair pass)* How should converted, relocated or rebranded stores be treated in cohorts, peer groups and the ramp index (Phase 7 TQ-12)? | KPIs / MDM | SH-15 / SH-04 | Yes (FR-03, KPI-10) | Sprint 1 |

*Still open after the repair pass (internal-policy questions, not decided by the prototype):* **U-38** regional visibility (prototype assumption A-45), **U-39** complementary suppression (prototype applies primary suppression only), **U-41** conversion visibility for Optometry Partners (prototype assumption A-46).

---

## Phase 10 close

### Decisions made
1. 21 risks rated. Six are High: conflicting definitions, unfair comparisons, missing or delayed data, causal misinterpretation, source integration and master-data inconsistency.
2. Assumptions A-01 to A-38 consolidated with confidence, validation method and owner.
3. BR-10 formalised as **CON-01**.
4. 12 dependencies with illustrative need-by milestones.
5. Open questions consolidated under their original U-IDs; U-40 and U-41 added.

### Assumptions introduced
A-38 (pilot includes a recently entered province).

### Questions requiring validation
U-40 (official-language needs) and U-41 (KPI-05 visibility).

### Recommended corrections
- Phase 9 RTM-16 refers to a "Phase 10 decision log" for KPI-05 visibility. This is now recorded as **U-41**.
