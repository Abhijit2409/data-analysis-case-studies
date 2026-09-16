# Phase 2 — Stakeholder Analysis

**Status:** Drafted by the author (not stakeholder-validated); the SH-03 rename and SH-14 to SH-18 additions are the author's portfolio decisions · **Prepared:** 2026-09-13 · **Builds on:** Phase 1 · **Evidence:** `evidence-log.md` (EV-01 to EV-17)

> **Outside-in disclaimer.** Stakeholder groups are proposed from public evidence. Job titles, team structures, reporting lines and decision rights are **not** confirmed unless marked "Confirmed". Influence, interest and RACI assignments are hypotheses to test in discovery.

**Primary business decision (adopted in Phase 1):** *"Which stores warrant attention relative to comparable stores, which candidate factors should be investigated, and which business team should follow up?"*

---

## Evidence status key

| Label | Meaning |
|---|---|
| **Confirmed** | The role or group is named in a current public source. |
| **Function confirmed · title assumed** | The business function is publicly evidenced; the team name or title used here is illustrative. |
| **Indirect evidence** | Suggested only by a closed posting or a search snippet (low confidence). |
| **Assumed** | No public evidence found; included because a reporting product of this kind would typically need this group. |

---

## 1. Stakeholder register

IDs SH-01 to SH-13 follow the 13 groups in the original brief, in order. SH-14 to SH-18 are **additions made by the author** from public evidence; they are hypotheses to test in discovery, not confirmed stakeholder groups.

### SH-01 Retail Partners
| Field | Detail |
|---|---|
| Evidence status | **Confirmed.** Store Leader of the Specsavers Retail Corporation; responsible for day-to-day operations and long-term growth (EV-03). |
| Goals | Grow a sustainable store business; build a strong team; deliver customer service; succeed through ramp-up. |
| Business decisions | Where to focus team effort (bookings, attendance, conversion, fulfilment follow-up); when to ask the Support Office for help. |
| Information needs | Own store's weekly KPIs; trend since opening; comparison with similar stores (not a national league table); which data is incomplete; plain-language KPI definitions. |
| Likely concerns | Being judged unfairly against mature or dissimilar stores; exposure of their commercial figures to other partners; reporting that feels like surveillance; extra admin work. |
| Influence | **High collectively** (owner-operators, and adoption depends on them). Medium individually. |
| Interest | **High.** The product describes their business. |
| Engagement method | Interviews with a sample of partners (new, developing and mature stores; multiple provinces); store visits to observe current reporting use; short survey for scale; prototype walkthroughs; endorsement via the Partnership Advisory Committee (SH-14). |
| Role in requirements | Source of store-level needs, usability requirements and fairness concerns. |
| Role in approval | Not a formal approver of a Support Office product (assumed). Endorsement recommended through SH-14. |
| Role in UAT | Pilot users: test the store-detail view, peer comparison, definitions and data-quality warnings. |

### SH-02 Optometry Partners
| Field | Detail |
|---|---|
| Evidence status | **Confirmed.** Clinical Leader of the Independent Optometry Corporation (EV-03). |
| Goals | Deliver high-quality, accessible eyecare; run a sustainable clinic; manage clinical capacity. |
| Business decisions | Clinic capacity and scheduling patterns; recall follow-up; how clinical activity connects to the retail side. |
| Information needs | Capacity, utilization, attendance, completed exams and recall bookings (aggregated); comparison with similar clinics. |
| Likely concerns | Patient privacy and control of health records; clinical activity reduced to commercial measures; exam-to-purchase conversion implying pressure to sell; professional-regulation boundaries that vary by province (EV-04). |
| Influence | **High** on clinical-data use, privacy acceptance and professional credibility. |
| Interest | **Medium–High.** Rises if clinical measures are shown to retail or Support Office users. |
| Engagement method | Separate interviews from Retail Partners so clinical concerns can be raised freely; a KPI-definition workshop for clinical measures; privacy walkthrough together with SH-13. |
| Role in requirements | Defines acceptable clinical-activity measures, their wording and privacy boundaries; challenges conversion framing. |
| Role in approval | Consulted on clinical KPI definitions and on how clinical-activity data is exposed. |
| Role in UAT | Pilot users for appointment, attendance and recall views; confirm no patient-identifying detail is visible. |

### SH-03 Regional Retail Managers *(title to be validated; originally proposed as "Retail Performance Managers")*
| Field | Detail |
|---|---|
| Evidence status | **Assumed.** No public evidence of this title (searched 2026-09-13). **Indirect evidence** of a similar role: a closed "Retail Regional Manager" posting described as ensuring new stores launch and meet performance expectations (EV-13). |
| Goals | Help assigned stores ramp up and perform; prioritise limited time across a growing portfolio. |
| Business decisions | Which stores to contact or visit first; which issue to raise; when to escalate to another function. |
| Information needs | Exceptions across their portfolio compared with cohort peers; store diagnostics; data-quality status; a record of which follow-up team applies. |
| Likely concerns | Too many false alarms; data too late to be useful; being asked to explain numbers they don't trust; the product being used to rate their own performance. |
| Influence | **Medium–High.** Likely the day-to-day users whose adoption signals success. |
| Interest | **High.** |
| Engagement method | Contextual interviews (how they prepare for store conversations today); job-shadowing a store review; low-fidelity prototype testing; fortnightly review during build. |
| Role in requirements | Primary source for exception logic, drill-through paths and workflow needs. |
| Role in approval | Consulted. Recommend approval of exception rules through SH-04. |
| Role in UAT | **Core UAT testers** for portfolio, peer comparison and diagnostic scenarios. |

### SH-04 Regional or Retail Operations (leadership)
| Field | Detail |
|---|---|
| Evidence status | **Function confirmed · title assumed.** Retail operations stakeholders appear in the public Product Owner posting (EV-09d) and retail functions in the Data Delivery Manager posting (EV-09c). Leadership titles are unknown. Defined here as the national or regional leadership over retail operations, **distinct from SH-03**, which is field-based. |
| Goals | A consistently strong network through rapid expansion; efficient allocation of support. |
| Business decisions | Where to direct regional support; whether a pattern is store-specific or regional; approval of peer-group and maturity rules. |
| Information needs | Network and regional patterns; cohort ramp-up curves; count of stores needing attention; data-quality confidence. |
| Likely concerns | Conflicting numbers between teams; comparisons that erode partner trust; delivery timelines and scope creep. |
| Influence | **High.** Likely business sponsor for this product (assumed). |
| Interest | **High.** |
| Engagement method | Sponsor 1:1s; problem-validation workshop; steering check-ins at phase gates; prototype demos. |
| Role in requirements | Sets business objectives and priorities; arbitrates conflicts between user groups. |
| Role in approval | **Proposed accountable approver** for business requirements, peer and maturity rules, and UAT business sign-off. |
| Role in UAT | Reviews UAT summary; signs off (with the Product Owner) against exit criteria. |

### SH-05 Marketing
| Field | Detail |
|---|---|
| Evidence status | **Function confirmed · title assumed.** Marketing Services, including patient recall (EV-05). |
| Goals | Grow awareness and store traffic; effective patient recall; support new-store launches. |
| Business decisions | Where to direct local or launch marketing support; recall campaign design and follow-up. |
| Information needs | Recall contacts and recall bookings by store and cohort; booking demand trends. |
| Likely concerns | Recall bookings attributed incorrectly; a store's result read as marketing effectiveness; pressure to add PC Optimum and campaign analytics early. |
| Influence | **Medium.** |
| Interest | **Medium.** Higher for the recall KPI; likely to grow with PC Optimum. |
| Engagement method | Targeted interview; recall-KPI definition session; review of attribution rules. |
| Role in requirements | Defines recall-booking rules and attribution window; supplies recall-platform source knowledge. |
| Role in approval | Proposed business owner of the recall KPI definition (to confirm in Phase 6). |
| Role in UAT | Validates recall figures against its own platform totals (reconciliation test). |

### SH-06 Supply Chain
| Field | Detail |
|---|---|
| Evidence status | **Function confirmed · title assumed.** Supply Chain support service (EV-05); supply-chain stakeholders named in the data postings (EV-09c). |
| Goals | Timely, accurate order fulfilment across a growing network. |
| Business decisions | Whether fulfilment delays are store-specific, regional or systemic; where to intervene in the supply chain. |
| Information needs | Order turnaround and on-time fulfilment by store, region and period; order status definitions. |
| Likely concerns | Store delays blamed on supply chain (or the reverse); how "on time" is defined; orders needing remakes. |
| Influence | **Medium.** |
| Interest | **Medium.** High for fulfilment KPIs. |
| Engagement method | Process-mapping session (order lifecycle); KPI definition workshop; data-profiling review with Data Engineers. |
| Role in requirements | Defines fulfilment milestones, "on-time" standard and exclusions. |
| Role in approval | Proposed business owner of fulfilment KPIs. |
| Role in UAT | Reconciles fulfilment measures with order-management totals. |

### SH-07 Finance
| Field | Detail |
|---|---|
| Evidence status | **Function confirmed · title assumed.** Accounting & Administration services and "accounting and finance professionals" in the Support Office (EV-05, EV-16). |
| Goals | Accurate, reconcilable financial reporting; partner financial statements. |
| Business decisions | Which revenue figure is authoritative for operational reporting; treatment of returns, refunds and timing. |
| Information needs | Consistent revenue definitions; reconciliation between operational sales and financial records. |
| Likely concerns | Operational revenue differing from ledger figures; exposure of partner commercial data; the dashboard being mistaken for financial reporting. |
| Influence | **High** on revenue definitions and commercial confidentiality. |
| Interest | **Medium.** |
| Engagement method | Definition workshop for revenue measures; reconciliation-rule review; confidentiality review with SH-13. |
| Role in requirements | Defines eligible revenue, returns and refunds treatment, and reconciliation tolerance. |
| Role in approval | Proposed business owner of revenue-based KPIs. |
| Role in UAT | Executes the revenue reconciliation test. |

### SH-08 Product Owner (data product)
| Field | Detail |
|---|---|
| Evidence status | **Confirmed role type.** The Data Business Analyst posting references a Product Owner for backlog refinement and prioritisation (EV-09a); the Data Analyst posting references Product Owners (EV-09b). Which Product Owner would own this product is assumed. *Distinct from the PMS/EMR application Product Owner (EV-09d), see SH-17.* |
| Goals | Deliver a valuable, adopted data product; manage the backlog; maximise value per sprint. |
| Business decisions | Backlog priority; MVP scope; acceptance of stories; trade-offs between requests. |
| Information needs | Clear, prioritised requirements; value and effort estimates; risks and dependencies; UAT results. |
| Likely concerns | Scope creep; unclear or conflicting requirements; late data dependencies; low adoption. |
| Influence | **High** on scope and priority. |
| Interest | **High.** |
| Engagement method | Daily or weekly working sessions; backlog refinement; sprint reviews. |
| Role in requirements | Prioritises and accepts requirements and stories; owns the backlog. |
| Role in approval | **Accountable** for backlog priority and story acceptance; co-signs UAT. |
| Role in UAT | Accepts or rejects stories against acceptance criteria; decides defect priority with the delivery team. |

### SH-09 Data Business Analyst
| Field | Detail |
|---|---|
| Evidence status | **Confirmed** (EV-09a). |
| Goals | Translate business needs into clear, testable, traceable requirements; ensure the product answers the decision. |
| Business decisions | How to structure requirements; which conflicts need escalation; readiness of stories. |
| Information needs | Stakeholder needs; source-system knowledge; data profiling results; constraints. |
| Likely concerns | Stakeholder availability; changing requirements; undocumented business rules; poor source-data quality. |
| Influence | **Medium.** High on requirement quality. |
| Interest | **High.** |
| Engagement method | Facilitates all workshops; maintains the BRD, FSD, KPI dictionary, mappings and traceability. |
| Role in requirements | **Responsible** for elicitation, documentation, mapping and traceability. |
| Role in approval | Prepares artefacts for approval; not an approver. |
| Role in UAT | Writes the UAT plan and scenarios; coordinates testers; triages defects. |

### SH-10 Data Engineers
| Field | Detail |
|---|---|
| Evidence status | **Confirmed** (EV-09a, EV-09b). |
| Goals | Reliable, maintainable, well-modelled data pipelines. |
| Business decisions | Integration approach; model design; feasibility and effort. |
| Information needs | Source-to-target mappings; business rules; grain; refresh needs; data-quality rules. |
| Likely concerns | Ambiguous business rules; unavailable or poor-quality sources; late changes to KPI logic. |
| Influence | **Medium–High** (feasibility and effort). |
| Interest | **High.** |
| Engagement method | Data-mapping workshops; profiling reviews; backlog refinement. |
| Role in requirements | Validates technical feasibility; contributes lineage and data-quality requirements. |
| Role in approval | Technical approval of the data model and mappings. |
| Role in UAT | Supports data-reconciliation tests; fixes data defects. |

### SH-11 Data / Visualization Analysts
| Field | Detail |
|---|---|
| Evidence status | **Confirmed.** "Visualization Analysts" (EV-09a); Data Analysts (EV-09b). |
| Goals | Clear, performant, accessible Power BI reports that drive action. |
| Business decisions | Visual design; measure implementation; report navigation. |
| Information needs | User personas, decisions, KPI definitions, filter and drill requirements, accessibility needs. |
| Likely concerns | Too many visuals requested; unclear definitions; performance of complex peer calculations. |
| Influence | **Medium.** |
| Interest | **High.** |
| Engagement method | Prototype co-design sessions; sprint reviews. |
| Role in requirements | Contributes report-design and usability requirements; builds prototypes. |
| Role in approval | Technical approval of report design. |
| Role in UAT | Fixes report defects; supports testers. |

### SH-12 Data Delivery Manager
| Field | Detail |
|---|---|
| Evidence status | **Confirmed** (EV-09c). |
| Goals | Deliver data products on time, within scope, with managed risks. |
| Business decisions | Delivery plan; resourcing; risk escalation; release readiness. |
| Information needs | Scope, estimates, dependencies, risks, test status. |
| Likely concerns | Dependencies on source-system teams; stakeholder availability; privacy approvals delaying release. |
| Influence | **High** on delivery. |
| Interest | **High.** |
| Engagement method | Delivery stand-ups; RAID reviews; release-readiness meetings. |
| Role in requirements | Ensures requirements are sized, sequenced and dependency-managed. |
| Role in approval | **Accountable** for release readiness and go-live. |
| Role in UAT | Confirms UAT entry and exit criteria are met; manages the defect process. |

### SH-13 Data Governance, Privacy or Security representatives
| Field | Detail |
|---|---|
| Evidence status | **Privacy Officer confirmed** (EV-12; candidate privacy policy references PIPA or PIPEDA). **Data-governance and information-security teams assumed.** |
| Goals | Lawful, proportionate, secure use of personal and health information; consistent data ownership and quality standards. |
| Business decisions | Whether aggregated clinical-activity measures may be shown to retail users; access model; minimum aggregation; retention; export rules. |
| Information needs | Data inventory; data flows; user roles; aggregation levels; export options. |
| Likely concerns | Re-identification risk from small counts; health information reaching unauthorised users; uncontrolled exports; cross-partner commercial exposure. |
| Influence | **High** (can block release). |
| Interest | **Medium–High.** |
| Engagement method | Early privacy consultation (before design); privacy impact assessment input; access-model review; UAT access tests. |
| Role in requirements | Defines privacy, security, access and retention requirements (Phase 5). |
| Role in approval | **Accountable** for privacy and access approval; KPI change-control governance (assumed). |
| Role in UAT | Witnesses role-based access and export-restriction tests. |

### Recommended additions (adopted in this draft; reversible)

| ID | Proposed stakeholder | Evidence status | Why include |
|---|---|---|---|
| SH-14 | **Partnership Advisory Committee** | **Confirmed exists** (EV-15). Membership and remit unknown. | A representative channel for partner endorsement, instead of consulting 270+ partners one by one. Could reduce the adoption and fairness risk around peer comparison. |
| SH-15 | **Business Development / New-Store Opening** | **Function confirmed** (EV-05) · title assumed | Likely source of store opening dates and pipeline; highly interested in ramp-up curves; possible owner of maturity-related master data. |
| SH-16 | **Clinical / Professional Services leadership** | **Indirect.** Clinical trainers and clinical programmes referenced (EV-16, prospectus p. 11) · title assumed | A central clinical voice on clinical KPI wording, alongside individual Optometry Partners. |
| SH-17 | **Source-system owners** (PMS/EMR, POS, scheduling, order management) | **Confirmed role type** for PMS/EMR (EV-09d); others assumed | Needed for data access, field meaning and change notifications. |
| SH-18 | **Executive leadership** (e.g., Managing Director) | **Confirmed role** (EV-02) | Strategic context (the growth ambition); informed rather than engaged directly in an MVP. |

---

## 2. Influence-versus-interest assessment

| | **Lower interest** | **Higher interest** |
|---|---|---|
| **Higher influence** | **Keep satisfied:** SH-07 Finance · SH-13 Governance and Privacy (interest rises at design and release) · SH-18 Executive leadership · SH-14 Partnership Advisory Committee | **Manage closely:** SH-04 Retail Operations leadership · SH-08 Product Owner · SH-01 Retail Partners (collectively) · SH-02 Optometry Partners · SH-12 Data Delivery Manager · SH-03 Regional Retail Managers |
| **Lower influence** | **Monitor / keep informed:** SH-17 Source-system owners (until data access is needed) | **Keep informed and involved:** SH-05 Marketing · SH-06 Supply Chain · SH-15 Business Development · SH-16 Clinical Services · SH-09 Data Business Analyst · SH-10 Data Engineers · SH-11 Visualization Analysts |

**Notes**
- **SH-02 and SH-13 are veto-capable** on clinical-data exposure. Engage them *before* design, not at UAT.
- **SH-01 influence is collective.** One partner has limited influence; partners as a group decide adoption.
- **Interest is dynamic.** SH-05 is likely to rise as PC Optimum analytics is requested. SH-07 rises when revenue definitions are debated.
- **SH-10 has technical influence** beyond its quadrant position: feasibility findings can reshape scope.

---

## 3. Proposed RACI

**R** = Responsible · **A** = Accountable (one per activity) · **C** = Consulted · **I** = Informed · blank = not involved. Additions SH-14 to SH-18 are shown in the notes column.

| Activity | RP (01) | OP (02) | RRM (03) | ROps (04) | Mkt (05) | SC (06) | Fin (07) | PO (08) | DBA (09) | DE (10) | DVA (11) | DDM (12) | Gov (13) | Additions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Problem validation and discovery | C | C | C | C | C | C | C | **A** | R | I | I | I | C | SH-14 C, SH-15 C |
| Business requirements approval | C | C | C | **A** | C | C | C | R | R | C | C | I | C | SH-14 C |
| KPI definition approval (per-KPI owner named in Phase 6) | C | C | C | **A** | R* | R* | R* | C | R | C | C | I | C | SH-16 C · *R for their own domain KPIs* |
| Store-maturity and peer-group rules | C | C | C | **A** | I | I | C | C | R | C | C | I | I | SH-15 C, SH-14 C |
| Source-to-target mapping | | | | I | C | C | C | I | R | **A** | C | I | C | SH-17 C |
| Store master data (attributes, opening dates) | I | I | C | **A** | | | C | I | C | R | I | I | C | SH-15 R (possible owner) |
| Data-quality rules and thresholds | | | C | C | C | C | C | C | R | R | C | I | **A** | SH-17 C |
| Privacy, access and export model | C | C | I | C | I | I | C | C | R | R | C | I | **A** | SH-16 C |
| Minimum peer-group size and small-count suppression floor | C | C | C | C | | | C | C | R | C | C | I | **A** | SH-14 C · SH-13 sets the non-identifiability floor; SH-04 may choose an analytical threshold **at or above** it (never below) |
| Backlog prioritisation | | | C | C | I | I | I | **A** | R | C | C | C | C | |
| Prototype and report design | C | C | C | C | | | | **A** | R | I | R | I | C | SH-14 C |
| Data pipeline build | | | | | | | | C | C | R | I | **A** | C | SH-17 C |
| Report build | | | | | | | | C | C | C | R | **A** | C | |
| Test planning | | | C | I | | | | C | R | C | C | **A** | C | |
| UAT execution | R | R | R | I | R | R | R | **A** | R | C | C | C | R | |
| UAT business sign-off | C | C | C | **A** | C | C | C | R | R | I | I | C | C | SH-14 C |
| Release and pilot go-live | I | I | I | C | I | I | I | R | R | R | R | **A** | C | SH-18 I |
| Training and adoption | I | I | R | **A** | I | I | I | C | R | | R | I | I | SH-14 C |
| KPI change control (after release) | I | I | I | C | C | C | C | C | R | C | C | I | **A** | |

**RACI design notes**
- **SH-04 is accountable for business sign-off, and SH-08 for backlog and story acceptance.** This separates business approval from product acceptance. It needs validation against Specsavers' actual operating model.
- **Partners are Consulted, not Accountable.** Partners run independent businesses but are users of a Support Office product (assumption A-13). Their endorsement is sought through SH-14.
- **Per-KPI business owners** (Marketing for recall, Supply Chain for fulfilment, Finance for revenue) will be named in Phase 6. The single "A" here is the approver of the overall KPI set.

---

## 4. Stakeholder-engagement plan

*All week numbers, durations and cadences in this section are illustrative.*

| Stage | Objective | Stakeholders | Techniques | Outputs |
|---|---|---|---|---|
| **1. Mobilise** (week 1) | Confirm sponsor, scope and access to people | SH-04, SH-08, SH-12, SH-13 | Sponsor 1:1; kick-off; early privacy consultation | Confirmed sponsor; stakeholder list; engagement calendar; privacy constraints noted |
| **2. Validate the problem** (weeks 1–3) | Test the Phase 1 hypothesis; understand current reporting | SH-01, SH-02, SH-03, SH-04, SH-15; SH-14 briefing | Semi-structured interviews (sample across maturity, province and format); contextual inquiry and store visits; review of current reports and spreadsheets; short partner survey | Validated or revised problem statement; current-state process map; pain-point log |
| **3. Define requirements and KPIs** (weeks 3–6) | Agree requirements, KPI definitions and peer rules | SH-03, SH-04, SH-05, SH-06, SH-07, SH-02/SH-16, SH-09 | Requirements workshops; KPI definition workshops (one per domain); peer-group rule workshop; MoSCoW prioritisation | BRD; KPI dictionary draft; peer and maturity rules; conflict log |
| **4. Map the data** (weeks 4–7) | Confirm sources, grain, quality and access | SH-10, SH-17, SH-13, domain owners | Data-mapping workshops; profiling reviews; privacy and access-model review | Source-to-target mapping; data-quality rules; access model |
| **5. Prototype** (weeks 6–9) | Test comprehension and usefulness early | SH-01, SH-02, SH-03, SH-04, SH-11 | Low-fidelity wireframe tests; clickable prototype walkthroughs ("show me how you'd decide which store to call") | Validated design; story refinements |
| **6. Build and refine** (sprints) | Keep requirements current | SH-08, SH-09, SH-10, SH-11, SH-12 | Backlog refinement; sprint reviews with SH-03 and SH-04 | Ready stories; accepted increments |
| **7. UAT and pilot** | Confirm fitness for purpose, accuracy and access | Pilot partners (SH-01, SH-02), SH-03, domain owners, SH-13 | Scripted and exploratory UAT; reconciliation tests; access tests; pilot feedback sessions | UAT report; sign-off; pilot feedback |
| **8. Adopt and improve** | Embed use; manage change | SH-03, SH-04, SH-14, all users | Training; office hours; usage monitoring; quarterly feedback via SH-14 | Adoption metrics; enhancement backlog |

**Communication cadence (illustrative):** sponsor fortnightly · Product Owner and delivery weekly · field and domain users at workshops and sprint reviews · partners at interview, prototype and pilot touchpoints plus SH-14 updates · governance at design, access-model and release gates.

**Principles**
- Hear Retail Partners and Optometry Partners **separately** before bringing them together.
- Sample partners across **maturity, province and format** so the needs of young stores and newer provinces are represented.
- **"Show, don't specify":** use prototypes early, because the requirements for a comparison product are hard to state in the abstract.
- Keep a visible **decision and conflict log** so no definition changes silently.

---

## 5. Possible areas of disagreement

| # | Tension | Parties | Why it may arise | Proposed handling |
|---|---|---|---|---|
| D-01 | **Peer visibility vs. commercial confidentiality** | SH-01 vs. SH-04, SH-13 | Partners may not want other partners to see their figures; Support Office wants network comparison | Test anonymised peer medians and distributions (no named peer stores); decide via SH-13 and SH-14 |
| D-02 | **Commercial vs. patient-access emphasis** | SH-07, SH-04 vs. SH-02, SH-16 | A revenue focus may conflict with the clinical and access purpose (EV-07) | Balanced KPI set with access measures shown alongside commercial ones; sponsor decides the default view |
| D-03 | **Exam-to-purchase conversion framing** | SH-02 vs. SH-01, SH-07 | Optometry Partners may see conversion as sales pressure on clinical care | Neutral naming and interpretation guidance; clinical input on the definition; consider showing it only to appropriate roles |
| D-04 | **Source of truth for revenue** | SH-07 vs. SH-04, SH-03 | Point-of-sale timing differs from ledger timing; returns and refunds | Document operational vs. financial revenue; set a reconciliation tolerance; label the dashboard "operational, not financial reporting" |
| D-05 | **Maturity thresholds and peer groups** | SH-04 vs. SH-03, SH-15, SH-07 | Different views of when a store is "mature"; small peer groups in new provinces | Workshop on evidence-based options; minimum peer-group size; fallback grouping rule |
| D-06 | **Fulfilment delay attribution** | SH-06 vs. SH-01, SH-03 | Delays could be store-caused or supply-chain-caused | Milestone-level definitions; show stage-level turnaround where data allows |
| D-07 | **Timeliness vs. accuracy** | SH-03 vs. SH-10, SH-13 | Field users want near-real-time; engineering and governance want reconciled data | Weekly refresh for MVP with visible freshness status; revisit after pilot |
| D-08 | **Exposure of clinical-activity data** | SH-13, SH-02 vs. SH-03, SH-04 | Retail-side users may request clinical detail | Aggregation only; role-based views; small-count suppression |
| D-09 | **"Needs attention" used as performance management** | SH-01, SH-03 vs. SH-04 | Exception flags could be read as a rating of partners or managers | Frame as a support trigger; no individual-performance scoring; flags suggest investigation areas only |
| D-10 | **Scope expansion** | SH-05, SH-06, SH-07 vs. SH-08, SH-12 | Requests for PC Optimum, inventory or P&L | MVP boundary from Phase 1; enhancement backlog with explicit deferral reasons |

---

## 6. Discovery questions (35, by stakeholder)

**Retail Partners (SH-01)**
- DQ-01. How do you know today whether your store is on track for its stage? What do you compare it with?
- DQ-02. Which reports or spreadsheets do you use weekly, and how long do they take to prepare or find?
- DQ-03. Would you want to see how similar stores perform? What would make that comparison feel fair, or unfair?
- DQ-04. Which figures would you *not* want other partners or regions to see?

**Optometry Partners (SH-02)**
- DQ-05. Which clinic measures help you manage capacity and recall, and which feel inappropriate to share outside the clinic?
- DQ-06. How should exam activity and eyewear purchases be related in reporting, if at all?
- DQ-07. Are there provincial professional or regulatory considerations that should shape what is measured or shown?

**Regional Retail Managers (SH-03)**
- DQ-08. Walk me through preparing for a store conversation. What do you look at first, and where does it come from?
- DQ-09. How do you decide which store needs your attention this week?
- DQ-10. When figures from two reports disagree, what do you do?
- DQ-11. What would make an exception flag worth acting on, rather than noise?

**Retail Operations leadership (SH-04)**
- DQ-12. Which decisions about store support are hardest to make with current information?
- DQ-13. How do you currently define a "new", "developing" or "mature" store, and is that definition agreed?
- DQ-14. What would success for this product look like six months after release?
- DQ-15. Who has authority to approve KPI definitions and peer-group rules?

**Marketing (SH-05)**
- DQ-16. How is a recall booking attributed to a recall contact? What time window applies?
- DQ-17. Which recall or launch-marketing decisions would benefit from store-cohort views?

**Supply Chain (SH-06)**
- DQ-18. What are the milestones in an order's lifecycle, and which one defines "ready" or "fulfilled"?
- DQ-19. What is the "on-time" standard, and does it vary by product type, region or remake?

**Finance (SH-07)**
- DQ-20. Which revenue measure should operational reporting use, and how are returns, refunds and discounts treated?
- DQ-21. What reconciliation difference between operational and financial revenue is acceptable?
- DQ-22. What commercial information is confidential between independently owned partner businesses?

**Product Owner (SH-08)**
- DQ-23. How is value measured for data products, and how are competing requests prioritised?
- DQ-24. What is the realistic MVP timeline and team capacity?

**Data Engineers (SH-10) and source-system owners (SH-17)**
- DQ-25. Which systems hold appointments, exams, sales, orders and recall data? Are they already in the data platform?
- DQ-26. Is there a shared store key across systems? Who maintains the store master?
- DQ-27. What refresh latency and known quality issues exist for each source?

**Visualization Analysts (SH-11)**
- DQ-28. Which report patterns and accessibility standards are already established? Are there reusable components or a shared semantic model?

**Data Delivery Manager (SH-12)**
- DQ-29. What delivery dependencies (data access, privacy approval, environments) most often delay releases?

**Governance, Privacy and Security (SH-13)**
- DQ-30. May aggregated exam counts be shown to retail-side users? What minimum aggregation or small-count rule applies?
- DQ-31. What access, export and retention controls are mandatory for health-related and partner commercial data?

**Partnership Advisory Committee (SH-14, if approved)**
- DQ-32. What principles should govern how partner stores are compared and how comparison information is shared?

**Business Development / New-Store Opening (SH-15)**
- DQ-33. Which date defines a store's "opening" (soft open, grand opening, first exam, first sale), who records it, and how are relocations, conversions (such as the Theodore & Pringle replacements) and temporary closures handled?

**Clinical / Professional Services leadership (SH-16)**
- DQ-34. Which aggregated clinical-activity measures are appropriate for network reporting, and what wording avoids implying commercial pressure on clinical care?

**Executive leadership (SH-18)**
- DQ-35. Which network-level questions about growth toward the stated ambition should this product help answer, and which are deliberately out of its scope?

---

## Phase 2 close

### Decisions made
1. Stakeholder IDs **SH-01 to SH-13** assigned in the order you proposed. **SH-14 to SH-18** adopted as additions in this draft (reversible). SH-14 and SH-15 are evidence-backed (EV-15, EV-05).
   **SH-03 renamed** "Regional Retail Managers (title to be validated)", with the ID unchanged. Reason: no public evidence for "Retail Performance Manager"; indirect evidence for a similar regional role (EV-13).
2. **SH-03 and SH-04 kept as separate groups**: SH-03 is field-based (portfolio triage); SH-04 is leadership (sponsor and approver).
3. **SH-08 defined as the data Product Owner**, distinct from the PMS/EMR application Product Owner (EV-09d), which is folded into SH-17.
4. **Proposed approval model:** SH-04 business sign-off · SH-08 backlog and story acceptance · SH-12 release readiness · SH-13 privacy and access · domain functions own their KPI definitions (named in Phase 6).
5. **Partners are Consulted, not Accountable.** Endorsement is sought through the Partnership Advisory Committee.
6. Evidence log extended with **EV-12 to EV-16**.
7. **Peer-group size rule:** SH-13 sets the minimum group size and small-count suppression floor; SH-04 may set an analytical threshold only at or above that floor. This resolves the potential conflict between D-01, D-05 and D-08 before Phase 6.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-12 | A retail-operations leader (SH-04) would sponsor a store-performance data product. |
| A-13 | Partners are users and consultees of Support Office data products, not formal approvers. |
| A-14 | A regional field-management function exists (indirect evidence EV-13); "Regional Retail Manager" is a placeholder title. |
| A-15 | Domain functions (Marketing, Supply Chain, Finance) can each nominate a KPI business owner. |
| A-16 | The Privacy Officer (or delegate) would review the access and aggregation model. |
| A-17 | The Partnership Advisory Committee is an appropriate channel for partner endorsement. |
| A-18 | Stakeholders are available for roughly 8–10 weeks of discovery, prototyping and UAT (illustrative). |

### Questions requiring validation
- **U-16.** Actual titles, reporting lines and decision rights for SH-03, SH-04 and the governance roles.
- **U-17.** Who is the business sponsor, and who approves KPI definitions?
- **U-18.** Whether partners may see anonymised peer benchmarks, and at what aggregation.
- **U-19.** The remit and membership of the Partnership Advisory Committee.
- **U-20.** Whether a data-governance council or KPI change-control forum already exists.
- **U-21.** Whether Optometry Partners and clinical leadership accept exam-to-purchase conversion as a reportable measure.

### Recommended corrections
1. **SH-03 rename applied** ("Retail Performance Managers" → "Regional Retail Managers, title to be validated"). The ID is unchanged. Reverse if you prefer the original label.
2. **SH-14 to SH-18 adopted.** Remove any you don't want; their IDs will not be reused.
3. **Store opening date is a critical master-data field.** The whole maturity-cohort concept depends on it. DQ-33 was added so its definition and ownership (likely SH-15) are resolved before Phase 6.
4. **Re-confirm the exact tool wording** in the Data Delivery Manager posting (EV-09c) before quoting it in the final deck.

*Document status: drafted by the author for the portfolio. Stakeholder groups, titles, RACI and decision rights are unvalidated hypotheses; no Specsavers stakeholder has reviewed or approved them.*
