# Phase 3 — Business Objectives and Business Requirements

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–2 · **Evidence:** `evidence-log.md`

> **Outside-in disclaimer.** These objectives and requirements are hypotheses for an outside-in case study. They do not describe confirmed Specsavers requirements, targets or reporting gaps. Every success measure is **illustrative** and needs a baseline before it can be used.

**Primary business decision (approved):** *"Which stores warrant attention relative to comparable stores, which candidate factors should be investigated, and which business team should follow up?"*

**Stakeholder references** use Phase 2 IDs: SH-01 Retail Partners · SH-02 Optometry Partners · SH-03 Regional Retail Managers · SH-04 Retail Operations leadership · SH-05 Marketing · SH-06 Supply Chain · SH-07 Finance · SH-08 Product Owner · SH-09 Data Business Analyst · SH-10 Data Engineers · SH-11 Visualization Analysts · SH-12 Data Delivery Manager · SH-13 Governance/Privacy/Security · SH-14 Partnership Advisory Committee · SH-15 Business Development · SH-16 Clinical Services · SH-17 Source-system owners · SH-18 Executive leadership.

---

## 1. Business objectives

| ID | Objective | Business rationale | Stakeholder | Decision supported | Priority | Proposed success measure (illustrative) | Assumptions | Validation questions |
|---|---|---|---|---|---|---|---|---|
| **BO-01** | Enable **fair, like-for-like assessment** of store performance across a growing, diverse network. | Around half the network opened in 2025 (EV-02); stores differ by province, format and market (EV-01, EV-04). Ranking unlike stores together could mislead. | SH-04, SH-03, SH-01 | Which stores warrant attention *relative to comparable stores*? | Must | At least 80% of pilot users agree comparisons are "fair or mostly fair" (post-pilot survey). | A-10, A-11 | Which comparisons do users make today, and which feel unfair? |
| **BO-02** | **Surface stores that warrant attention earlier**, especially during ramp-up. | Early support is likely more useful in the first months of a new store (inference I-01). | SH-03, SH-04, SH-15 | Which store should be contacted this week, and about what? | Must | Median time from the end of a reporting week to identifying stores needing attention falls from the baseline to 2 business days or less. | A-01, A-03 | How long does it take today to spot an under-performing new store? |
| **BO-03** | Establish **trusted, governed and consistently defined KPIs** across functions. | Store performance data likely comes from several functions and systems (EV-05, I-03, I-04). | SH-04, SH-07, SH-05, SH-06, SH-13 | Can we rely on this figure, and does everyone mean the same thing by it? | Must | 100% of MVP KPIs have an approved definition, owner and version; zero unresolved definition conflicts at release. | A-15 | Do conflicting definitions exist today? Who resolves them? |
| **BO-04** | **Improve how follow-up is targeted** by linking each finding to a candidate investigation area and a responsible team. | Descriptive reporting creates value only when it leads to an appropriate conversation or action. | SH-03, SH-04, SH-06, SH-05 | Which team should follow up, and on what? | Must | At least 70% of flagged exceptions reviewed in the pilot have a recorded follow-up owner within 10 business days (recorded manually in the pilot). | A-04 | How is follow-up tracked today? |
| **BO-05** | Present a **balanced view** of patient-access and commercial performance. | Specsavers' stated purpose emphasises accessible eyecare, and public research highlights overdue exams and coverage confusion (EV-07, prospectus). | SH-02, SH-16, SH-04, SH-07 | Is the store growing access to eyecare as well as sales? | Should | Access indicators (completed exams, attendance, recall bookings) appear on every MVP page with the same prominence as commercial KPIs. | A-06 | How should access and commercial indicators be weighted in views? |
| **BO-06** | **Protect patient privacy and partner commercial confidentiality** by design. | Clinical activity is health-related; partners are independent business owners (EV-03, EV-12). | SH-13, SH-02, SH-01, SH-07 | Who may see what, at what aggregation? | Must | Zero privacy or confidentiality incidents; 100% of role-based access tests pass in UAT. | A-06, A-16 | Which privacy obligations and aggregation rules apply? |
| **BO-07** | **Reduce manual reporting effort** and reliance on unmanaged spreadsheets, *if validation confirms they exist*. | Many growing networks rely on manual compilation; unconfirmed for Specsavers (U-13). | SH-03, SH-04, SH-09 | Where should analyst and manager time go? | Could | 30% reduction in self-reported weekly hours spent compiling store-performance information (baseline survey versus 8 weeks after the pilot). | A-19 (new) | Is manual compilation actually happening, and how much? |

---

## 2. Business requirements

The draft wording from the master prompt is preserved beneath each refined statement.

### BR-01 — Network performance monitoring
| Field | Detail |
|---|---|
| Draft | "Monitor performance across the Canadian store network." |
| **Refined statement** | The business needs a consistent, regularly refreshed view of core access, operational and commercial KPIs across all Canadian stores, which can be viewed at network, region, province and store level. |
| Business rationale | More than 270 stores across ten jurisdictions (EV-02) need one common view instead of fragmented store-by-store checking. |
| Linked objective | BO-01, BO-02, BO-03 |
| Stakeholder | SH-04, SH-03, SH-18 (informed) |
| Decision supported | Is the network, or part of it, moving in the expected direction, and where should attention go? |
| Priority | **Must** |
| Proposed success measure | 100% of active stores present in each weekly refresh (or explicitly flagged as missing); users can reach any store's KPIs within 3 clicks from the network view (illustrative). |
| Assumptions | A-01, A-02, A-03 |
| Validation questions | Which KPIs are monitored network-wide today? What refresh cadence is useful? |

### BR-02 — Maturity-aware comparison
| Field | Detail |
|---|---|
| Draft | "Compare new stores with stores at similar maturity stages." |
| **Refined statement** | The business needs to compare each store with **peer stores at a similar maturity stage and in a similar operating context**, and to see ramp-up progress by time since opening. The rules must handle peer groups too small to compare reliably or safely. |
| Business rationale | Specsavers publicly tracked the share of stores open under six months (EV-06). Comparing young stores with mature stores directly can mislead (I-01). |
| Linked objective | BO-01, BO-02 |
| Stakeholder | SH-03, SH-04, SH-01, SH-15 |
| Decision supported | Is this store ramping up in line with comparable stores? |
| Priority | **Must** |
| Proposed success measure | 100% of stores are assigned a maturity cohort *as at each week*; peer statistics are shown only where the peer group meets the minimum size (floor set by SH-13, Phase 2). |
| Assumptions | A-10, A-11; maturity boundaries are illustrative until approved (Phase 6) |
| Validation questions | What defines "opening date"? Which peer dimensions matter most? What is the minimum peer-group size? |

### BR-03 — Candidate factors for investigation
| Field | Detail |
|---|---|
| Draft | "Identify factors potentially contributing to performance differences." |
| **Refined statement** | The business needs to see **which stage of the patient and customer journey** (capacity, booking, attendance, conversion, fulfilment, recall) differs most from peers, so these can be treated as **candidate factors to investigate**, not as proven causes. |
| Business rationale | Breaking performance down by journey stage narrows the conversation. Causal claims would need investigation outside the report (Phase 1 decision). |
| Linked objective | BO-04, BO-01 |
| Stakeholder | SH-03, SH-01, SH-02, SH-06, SH-05 |
| Decision supported | Which candidate factors should be investigated first? |
| Priority | **Should** |
| Proposed success measure | In pilot testing, at least 80% of users correctly state that a flagged variance is "an area to investigate" rather than a proven cause (comprehension check). |
| Assumptions | Journey-stage KPIs can be produced for each store-week (A-01). |
| Validation questions | Which journey stages do field teams already examine? Which variances are routinely explained by known local events? |

### BR-04 — Standardised, documented KPIs
| Field | Detail |
|---|---|
| Draft | "Standardize and document KPI calculations." |
| **Refined statement** | Every KPI in the product must have one governed definition covering formula, grain, inclusions and exclusions, source, owner and version. The definition must be visible to users, and changes must be controlled. |
| Business rationale | Consistent definitions are the foundation of trust across functions and partners (BO-03). |
| Linked objective | BO-03 |
| Stakeholder | SH-04 (approver), SH-05, SH-06, SH-07 (domain owners), SH-13, SH-09 |
| Decision supported | Can this figure be relied on and compared? |
| Priority | **Must** |
| Proposed success measure | 100% of displayed KPIs link to an approved dictionary entry; every definition change has a version and a change record. |
| Assumptions | A-15 |
| Validation questions | Is there an existing KPI glossary? Who has authority to approve changes? |

### BR-05 — Visible data quality
| Field | Detail |
|---|---|
| Draft | "Make data-quality issues visible." |
| **Refined statement** | Users must be able to see, before acting, whether data for a store and period is **complete and current**. Affected KPIs must be clearly flagged or withheld under agreed rules. |
| Business rationale | Growth, new provinces and multiple sources increase the chance of late or missing data (I-04). Acting on incomplete data could cause unfair conclusions. |
| Linked objective | BO-03, BO-01 |
| Stakeholder | SH-03, SH-01, SH-10, SH-13 |
| Decision supported | Is this data fit to act on? |
| Priority | **Must** |
| Proposed success measure | 100% of store-weeks below the completeness threshold, or with stale data, show a visible warning; zero exceptions raised on data flagged "red" (UAT). |
| Assumptions | Load metadata is available per source and store (A-20, new). |
| Validation questions | What known data-quality issues exist by source? |

### BR-06 — Relevant information for store partners
| Field | Detail |
|---|---|
| Draft | "Provide relevant information to store partners." |
| **Refined statement** | Retail Partners and Optometry Partners need a **store-focused view of their own store**, with anonymised peer benchmarks and plain-language definitions. The view must respect their different roles and must not expose other partners' commercial data. |
| Business rationale | Partners own and lead the stores (EV-03). Adoption and fairness depend on the report being useful to them (I-05). |
| Linked objective | BO-01, BO-04, BO-06 |
| Stakeholder | SH-01, SH-02, SH-14 |
| Decision supported | Where should my team focus this month? |
| Priority | **Must** |
| Proposed success measure | At least 60% of pilot partners view their store page in at least 3 of 4 pilot weeks; average usefulness rating of 4 out of 5 or higher (illustrative). |
| Assumptions | A-05, A-13 |
| Validation questions | What do partners need that they do not get today? Should Retail and Optometry Partners see the same measures? |

### BR-07 — Regional and network patterns
| Field | Detail |
|---|---|
| Draft | "Enable support-office users to identify regional and network patterns." |
| **Refined statement** | Support Office users need to tell whether a performance pattern is **local to one store or shared** across a region, province, format or cohort, so they can choose between store-specific and systemic follow-up. |
| Business rationale | Some issues (e.g., fulfilment delays) may be regional or supply-chain related rather than store-caused (Phase 2 D-06). |
| Linked objective | BO-01, BO-04 |
| Stakeholder | SH-04, SH-06, SH-05, SH-03 |
| Decision supported | Should the follow-up be one store, a region, or a central function? |
| Priority | **Should** |
| Proposed success measure | In UAT, users identify a seeded regional pattern (Phase 12) within 5 minutes in at least 90% of attempts. |
| Assumptions | Region and province attributes are maintained in the store master (A-02). |
| Validation questions | How are regions defined internally, and do they change? |

### BR-08 — Protect sensitive information
| Field | Detail |
|---|---|
| Draft | "Protect sensitive patient and commercial information." |
| **Refined statement** | The product must contain **no patient-identifiable or clinical-diagnosis data and no individual employee or clinician performance**. It must expose commercial KPIs only to authorised roles, apply small-count and minimum-peer-group rules, and restrict exports. |
| Business rationale | Health-related data and partner commercial data carry legal, ethical and trust obligations (EV-12; Phase 2 D-01, D-08). |
| Linked objective | BO-06 |
| Stakeholder | SH-13 (accountable), SH-02, SH-01, SH-07 |
| Decision supported | Who may see which information, at what aggregation? |
| Priority | **Must** |
| Proposed success measure | Privacy review completed before the pilot; 100% of access, suppression and export tests pass. |
| Assumptions | A-06, A-16 |
| Validation questions | Which legislation and internal policies apply? What is the minimum aggregation? |

### BR-09 — Support business action
| Field | Detail |
|---|---|
| Draft | "Support business action, not merely describe performance." |
| **Refined statement** | For each flagged exception, the product must indicate the **KPI and journey stage involved, the comparison basis, the data-quality status, a suggested investigation area and the typical follow-up team**, worded as prompts, not conclusions. |
| Business rationale | Converts monitoring into targeted follow-up (BO-04) while avoiding causal over-claiming. |
| Linked objective | BO-04, BO-02 |
| Stakeholder | SH-03, SH-04, SH-01 |
| Decision supported | What should happen next, and who should do it? |
| Priority | **Must** |
| Proposed success measure | 100% of exception flags carry an investigation prompt and follow-up team; pilot users rate prompts useful (4 out of 5 or higher, illustrative). |
| Assumptions | Follow-up teams can be mapped to KPI domains (A-15). |
| Validation questions | Who normally follows up on each type of issue? Is an in-product action log needed later? |

### BR-10 — First release small enough to validate quickly *(reclassified as a delivery constraint)*
| Field | Detail |
|---|---|
| Draft | "Keep the first release small enough to validate quickly." |
| **Refined statement** | **Constraint:** the first release shall be limited to the three MVP pages (Phase 11), store-week grain and the approved MVP KPIs, so it can be piloted and evaluated with a small user group within an illustrative 12 weeks from build start. |
| Classification note | **Delivery constraint, not a business capability.** The ID BR-10 is kept for traceability and cross-referenced as constraint CON-01 in Phase 10. It will not trace to functional requirements in Phase 9; this is expected. |
| Business rationale | Fast validation reduces the risk of building the wrong product in a changing environment (Phase 1 scope). |
| Linked objective | BO-02 (earlier value), all objectives (risk reduction) |
| Stakeholder | SH-08, SH-12, SH-04 |
| Decision supported | What goes into Release 1 versus later? |
| Priority | **Must** |
| Proposed success measure | MVP scope change requests after baseline are approved by SH-08 with an impact note; pilot starts within the planned window (illustrative). |
| Assumptions | A-18 |
| Validation questions | What delivery window and team capacity are realistic? |

### Additional requirements introduced in this phase

### BR-11 — Patient-access indicators *(new)*
| Field | Detail |
|---|---|
| **Statement** | The business needs patient-access indicators (completed examinations, attendance, recall bookings) presented **alongside** commercial indicators wherever store performance is assessed. |
| Business rationale | Supports BO-05. It is also a reason to avoid judging stores on revenue alone (EV-07). |
| Linked objective | BO-05 |
| Stakeholder | SH-02, SH-16, SH-04, SH-05 |
| Decision supported | Is the store growing access to eyecare? |
| Priority | **Should** |
| Proposed success measure | Each MVP page shows at least two access KPIs (illustrative design rule). |
| Assumptions | A-06 |
| Validation questions | Which access indicators do clinical leaders consider meaningful? |

### BR-12 — Reduce manual compilation *(new)*
| Field | Detail |
|---|---|
| **Statement** | Where current store-performance information is compiled manually, the product should replace the recurring compilation for MVP KPIs. |
| Business rationale | Supports BO-07. **Conditional:** only relevant if discovery confirms the manual effort (U-13). |
| Linked objective | BO-07 |
| Stakeholder | SH-03, SH-09, SH-04 |
| Decision supported | Which manual reports can be retired? |
| Priority | **Could** |
| Proposed success measure | Named manual reports retired or reduced within 8 weeks of the pilot (illustrative). |
| Assumptions | A-19 |
| Validation questions | Which spreadsheets exist? Who owns them? Which will users give up? |

---

## 3. Conflicts, overlaps and duplication

Nothing has been removed. These items are logged for resolution.

| # | Items | Type | Description | Proposed handling |
|---|---|---|---|---|
| C-01 | BR-01 ↔ BR-07 | Overlap | Both involve network-level viewing. | Keep both: BR-01 = **monitoring** KPIs at any level; BR-07 = **pattern diagnosis** (local vs shared). The functional requirements in Phase 4 should implement them as distinct capabilities. |
| C-02 | BR-03 ↔ BR-09 | Overlap | Candidate factors (BR-03) feed action prompts (BR-09). | Keep both: BR-03 = analytical breakdown; BR-09 = actionable presentation. Trace separately. |
| C-03 | BR-02 / BR-06 ↔ BR-08 | **Conflict** | Peer comparison and partner sharing versus confidentiality and small-count protection. | Anonymised peer medians and distributions only; minimum peer-group floor set by SH-13 (Phase 2 decision 7); fallback grouping. |
| C-04 | BR-06 ↔ BR-08 | **Conflict** | Optometry Partners and Retail Partners may need different exposure to clinical-activity and revenue KPIs. | Role-specific object-level security (Phase 5). |
| C-05 | BR-09 ↔ BR-03 wording | Risk of causal over-claim | Action prompts could be read as diagnosis. | Controlled prompt wording ("investigate…", "check…"); comprehension test (BR-03 success measure). |
| C-06 | BR-10 ↔ all | Scope tension | Requests from Marketing (PC Optimum), Supply Chain and Finance could exceed the constraint. | Enhancement backlog; SH-08 decision log. |
| C-07 | BR-05 ↔ BR-01 | Tension | "Complete coverage" versus withholding red-flagged data. | Show stores with missing or withheld data as explicitly flagged rows, not silent gaps. |
| C-08 | BO-07 / BR-12 | Weak evidence | Depends on unvalidated manual effort. | Keep as Could; confirm in discovery before investment. |

---

## 4. MoSCoW summary

| Priority | Business objectives | Business requirements |
|---|---|---|
| Must | BO-01, BO-02, BO-03, BO-04, BO-06 | BR-01, BR-02, BR-04, BR-05, BR-06, BR-08, BR-09, BR-10 (constraint) |
| Should | BO-05 | BR-03, BR-07, BR-11 |
| Could | BO-07 | BR-12 |
| Won't (this release) | — | PC Optimum analytics; profitability; causal or predictive analytics (Phase 1 exclusions) |

---

## Phase 3 close

### Decisions made
1. Seven business objectives defined (BO-01 to BO-07).
2. BR-01 to BR-10 refined with their original meaning kept and draft wording retained.
3. **BR-10 reclassified as a delivery constraint** (ID kept; cross-referenced as CON-01 in Phase 10).
4. BR-11 (access indicators) and BR-12 (manual-compilation reduction, conditional) added.
5. Triage wording ("warrant attention", "candidate factors", "investigation area", "follow-up team") applied throughout.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-19 | Some recurring store-performance information is compiled manually today (unverified). |
| A-20 | Load metadata (last load time, records received) is available per source and store to support data-quality indicators. |
| A-21 | Follow-up responsibility can be mapped from KPI domain to a team (e.g., fulfilment → Supply Chain). |

### Questions requiring validation
- U-22. Baselines for all success measures (time to identify exceptions, manual hours, current usage).
- U-23. Is an in-product follow-up or action log wanted in a later release?
- U-24. How much weight should access and commercial indicators each carry in default views?

### Recommended corrections
- None to earlier phases. Note that BO-07 and BR-12 are weakly evidenced and should be confirmed early in discovery.
