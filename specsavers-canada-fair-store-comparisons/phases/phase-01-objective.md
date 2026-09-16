# Phase 1 — Case-Study Objective and Problem Definition

**Status:** Drafted by the author, including the refined primary business decision and the corrections to the starting research (not reviewed or approved by Specsavers stakeholders) · **Prepared:** 2026-09-13 · **Evidence references:** EV-xx IDs link to `evidence-log.md`

> **Outside-in disclaimer.** This case study relies only on public information and synthetic data. It makes no claims about Specsavers' confidential information, internal systems, internal performance or current reporting. Every hypothesis in it would need validation with internal stakeholders.

---

## 1. Refined case-study title

**Fair Comparisons for a Fast-Growing Network: Store Ramp-Up and Partner Performance Intelligence**
*An Outside-In Data Business Analysis Case Study for Specsavers Canada*

This keeps the working title's focus on store growth and partner performance intelligence. The added phrase "fair comparisons" names the core analytical problem: comparing stores that are not alike.

---

## 2. Executive summary

Public evidence shows that Specsavers Canada grew to more than 270 stores across nine provinces and one territory, opening more than 130 of them in 2025 (EV-02). About 111 of those locations sit inside Loblaw grocery stores (EV-01). Each location is locally owned: a Retail Partner leads the store and an Optometry Partner leads the clinic, through separate corporations, backed by a central Support Office (EV-03, EV-05). Ownership structures follow provincial regulations (EV-04).

This case study hypothesizes that simple store rankings could mislead in a network like this, because stores differ in age, province, host retail format and local market. It proposes a small, governed reporting product. The product would help partners and Support Office teams **see which stores warrant attention, compare each store against similar stores, find candidate factors worth investigating, and route follow-up to the right team.**

The case study runs through requirements, KPI governance, an assumed data model, a synthetic dataset, a Power BI prototype design and a UAT plan. All of it is framed as a hypothesis for internal validation, not as a diagnosis of a known problem.

---

## 3. Business context

| Theme | Public evidence | Source |
|---|---|---|
| Rapid expansion | 111 locations inside Loblaw grocery stores announced 30 Jul 2025, replacing Theodore & Pringle; first wave Sep 2025; network projected at more than 260 locations. | EV-01 |
| Current scale | More than 270 stores, nine provinces and one territory, more than 130 opened in 2025 (release dated 11 Mar 2026). | EV-02 |
| Geographic reach | Entry into NB, NL, NS, PE, SK and YT through the Loblaw expansion. | EV-01 |
| Strategic ambition | New Managing Director effective 1 Mar 2026; stated aim to become "the number one provider of eyewear and eyecare in Canada." | EV-02 |
| Operating model | Two locally owned entities per location: an optometry corporation (Optometry Partner, clinical leader) and a retail corporation (Retail Partner, store leader), plus central Support Services. | EV-03 |
| Regulation | Businesses are owned "in accordance with provincial regulations." | EV-04 |
| Central support | Nine support-service areas, including supply chain, marketing and patient recall, patient-record systems, and accounting and financial statements. | EV-05 |
| Store maturity (historical) | In Feb 2024, 20% of locations had been open less than six months. | EV-06 |
| Eyecare access | One in three adults are overdue for an eye exam; 51% cite cost as a concern; 61% of people who qualify for provincial coverage don't think they are covered (commissioned survey). | EV-07 |
| Loyalty | PC Optimum earning at all locations from 22 Jun 2026. | EV-08 |
| Data capability | Live postings for Data Business Analyst, Data Analyst and Data Delivery Manager roles mention Power BI, SQL, Databricks, and retail, clinical and supply-chain stakeholders. A Product Owner posting references PMS/EMR, POS and ERP systems. | EV-09a–d |

---

## 4. Problem or opportunity hypothesis

> **This case study hypothesizes** that, as Specsavers Canada expands a geographically diverse, locally owned store network, Retail Partners, Optometry Partners and Support Office teams may need a **consistent, trusted and fair** way to monitor new-store ramp-up, compare each store with genuinely comparable stores, and prioritise where support is needed.

The hypothesis rests on four plausible mechanisms. Each would need internal validation.

1. **Maturity mix.** Public figures imply that roughly half the network opened during 2025 (EV-02). New stores ranked directly against mature stores could look like underperformers simply because they are young (EV-06 shows Specsavers itself tracks store age publicly).
2. **Structural diversity.** Stores differ by province and regulation (EV-04), by host retail format such as inside a grocery store (EV-01), and by local market. Pooled averages could hide these differences.
3. **Split data domains.** Each location has separate clinical and retail entities (EV-03), and system categories such as PMS/EMR and POS are publicly referenced (EV-09d). Examination activity and purchase activity may therefore be recorded in different systems. That would make a cross-domain measure such as exam-to-purchase conversion hard to define and reconcile consistently.
4. **Multiple central functions.** Store performance touches several Support Office functions, including supply chain, marketing and recall, and finance (EV-05). Definitions, ownership and data quality may vary between them.

**What the evidence does not show.** Public evidence shows growth and operating complexity. **It does not show that Specsavers currently has inadequate, inconsistent or untrusted reporting.** Existing reporting may already cover some or all of these needs. Discovery would begin by understanding it.

---

## 5. Why the opportunity matters now

| Driver | Evidence | Why it matters now (inference) |
|---|---|---|
| A young network | More than 130 of 270+ stores opened in 2025 (EV-02) | Through 2026, a large share of stores will be in ramp-up, when fair comparison matters most. |
| New provinces and a new format | Six new provinces or territories and 111 in-grocery locations (EV-01) | Some store groups are new to the network, so there may be little historical baseline to compare against. |
| Continued growth | Ambition to be the number-one provider (EV-02) | Reporting would need to scale with further openings, not be a one-off exercise. |
| Leadership transition | New Managing Director from Mar 2026 (EV-02) | A new leader may want network-level visibility of growth. *Low-confidence inference.* |
| A new data stream | PC Optimum live from Jun 2026 (EV-08) | Purchasing behaviour may shift after June 2026, which could complicate before/after comparisons. Loyalty analytics comes later; its effect on trends should be noted now. |
| Investment in data capability | Four live data and technology postings (EV-09) | Suggests an active data programme. It is **not** evidence of a specific reporting gap. |

---

## 6. Primary business decision

**Original (master context):**
> "Which stores require attention, why are they performing differently from comparable stores, and what action should the appropriate business team take?"

**Refined decision (adopted for this portfolio case study):**
> **"Which stores warrant attention relative to comparable stores, which candidate factors should be investigated, and which business team should follow up?"**

**Why the change.** The meaning is the same, but the causal wording is removed. A descriptive reporting product can show *where* a store differs and *which measures* differ. It cannot prove *why*. The answer to "why" comes from the follow-up conversation between the partners and the relevant Support Office team. The refinement is the author's portfolio decision; it has not been reviewed by Specsavers stakeholders and would be validated in discovery (U-01, U-02).

Supporting decisions (to be expanded in Phase 2):
- Is this new store ramping up in line with stores that opened around the same time and in similar conditions?
- Is a difference in performance concentrated in one stage: capacity, booking, attendance, conversion or fulfilment?
- Is a pattern local to one store, or shared across a region, province or format?
- Is the data complete and current enough to act on?

---

## 7. Desired business outcomes

These are qualitative outcomes. Measurable targets and BO-xx IDs will be set in Phase 3. No target in this case study is a confirmed Specsavers target.

1. **Fair comparison.** Stores are compared with peers of similar maturity and context, not only ranked nationally.
2. **Earlier visibility of ramp-up issues.** Stores tracking below their cohort are surfaced sooner for a support conversation.
3. **Trusted, shared definitions.** Partners and Support Office teams use one documented definition, with a named owner, for each core KPI.
4. **Transparent data quality.** Users can see when data is incomplete or stale before drawing conclusions.
5. **Better-targeted follow-up.** Findings point to a candidate investigation area and a responsible team, not just a score.
6. **Balanced view of performance.** Patient-access indicators (e.g., completed exams, recall bookings) sit alongside commercial indicators.
7. **Privacy and confidentiality by design.** Only aggregated, role-appropriate information is exposed.
8. **Less manual reporting effort.** Recurring manual compilation is reduced, if validation shows it exists today.

---

## 8. In-scope items

- Outside-in research, evidence log and stakeholder hypotheses
- Canadian store network only
- **Store-week aggregated** operational measures in these domains: appointment capacity and utilization, attendance, completed examinations (counts only), exam-to-purchase conversion, revenue per completed exam (aggregated), order fulfilment, recall bookings, data completeness and freshness
- A store-maturity cohort concept and a **peer-comparison hypothesis**: maturity × province × host retail format × local market type
- Users: Retail Partners, Optometry Partners (aggregated clinical activity only) and Support Office teams (titles to be validated in Phase 2)
- Deliverables for Phases 2–15: stakeholder map, BRD-style requirements, functional, non-functional, data, privacy and security requirements, KPI dictionary, conceptual data model and data flow, user stories, traceability matrix, RAID registers, MVP definition, synthetic dataset, Power BI prototype design, UAT and implementation plan, and the final deck
- Generic **system categories** (store master, scheduling, PMS/EMR, POS, order management, marketing/recall, finance). These categories are publicly referenced (EV-05, EV-09d, EV-10); the specific Specsavers platforms are not.

## 9. Out-of-scope items

- **PC Optimum and loyalty analytics** (future enhancement, EV-08)
- Patient-level data, clinical diagnoses, clinical outcomes or clinical-quality measures
- Individual employee or individual clinician performance
- Store profitability, P&L, partner profit distributions, franchise fees or partner financial terms
- Financial ROI claims
- Forecasting, predictive models or causal inference
- Inventory, assortment, pricing and procurement analytics
- Marketing attribution and campaign ROI
- E-commerce and contact-lens subscription analytics
- Staff rostering or per-practitioner schedules (capacity is store-level only)
- Competitor benchmarking
- Real Specsavers data, real system integration, production build or deployment
- Operations outside Canada

---

## 10. Known facts

See `evidence-log.md` for URLs, access status and exact wording.

| ID | Fact |
|---|---|
| EV-01 | 111 Specsavers locations announced inside Loblaw grocery stores (30 Jul 2025), replacing Theodore & Pringle; projected network of more than 260; entry into NB, NL, NS, PE, SK, YT. |
| EV-02 | More than 270 stores, nine provinces and one territory; more than 130 opened in 2025; number-one ambition; new Managing Director effective 1 Mar 2026. |
| EV-03 | Two-entity local ownership: Optometry Partner (clinical leader) and Retail Partner (store leader), plus central Support Services. |
| EV-04 | Businesses are owned in accordance with provincial regulations. |
| EV-05 | Support Office provides nine service areas, including patient recall, patient-record systems and financial statements. |
| EV-06 | Feb 2024: 20% of locations open less than six months; 250,000 exams and 450,000 pairs of glasses in the prior year. |
| EV-07 | Commissioned survey (Angus Reid, n = 2,022, Feb 2025): one in three overdue for an exam; 17% last exam over five years ago; 51% cost concern; 61% of people who qualify for provincial coverage don't think they are covered. |
| EV-08 | PC Optimum earning at all locations, announced 22 Jun 2026. |
| EV-09 | Live data and technology postings mention Power BI, SQL, Databricks, PMS/EMR, POS and ERP, and retail, clinical and supply-chain stakeholders. |
| EV-10 | Each store's web page offers online appointment booking. |

## 11. Reasonable inferences

| ID | Inference | Based on | Confidence |
|---|---|---|---|
| I-01 | Roughly half the network opened within about 15 months of Mar 2026, so ramp-up comparison is a material, current need. | EV-02 (arithmetic: 130+ of 270+) | Medium–High |
| I-02 | Store groups differ in regulation, format and market, so pooled averages could hide meaningful differences. | EV-01, EV-04 | Medium |
| I-03 | Clinical and retail activity may be recorded in separate system domains, making cross-domain KPIs hard to define and reconcile. | EV-03, EV-09d | Medium |
| I-04 | Store performance information may come from several Support Office functions with separate data owners, so master data and definitions matter. | EV-05 | Medium |
| I-05 | Partners own their businesses, so reporting must feel useful and fair to them, not only serve central oversight. | EV-03 | Medium |
| I-06 | An access-focused purpose makes patient-access indicators relevant alongside revenue; coverage confusion (61%) may vary by province. | EV-07, prospectus purpose statement | Medium |
| I-07 | Specsavers is investing in Canadian data capability. This does **not** imply current reporting gaps. | EV-09 | Medium |
| I-08 | PC Optimum may change purchasing patterns after Jun 2026, affecting trend interpretation. | EV-08 | Low–Medium |
| I-09 | New leadership may increase demand for network-level growth visibility. | EV-02 | Low |

## 12. Assumptions

| ID | Assumption |
|---|---|
| A-01 | Appointments, examinations, sales, orders and recall activity are recorded digitally and can be aggregated to store-week. |
| A-02 | A store master exists, or can be created, holding opening date, province, region, host retail format and status. |
| A-03 | Store-week grain is enough for the MVP decisions; daily detail is not required. |
| A-04 | One or more Support Office functions support store performance (e.g., retail operations). The titles are **not** confirmed. |
| A-05 | Partners would accept peer comparison if it is fair, aggregated and clearly explained. |
| A-06 | Aggregated exam counts (not clinical content) could be shared with retail users, **subject to privacy review.** |
| A-07 | Store formats other than in-grocery exist (e.g., shopping centre, street-front). *Not verified.* |
| A-08 | Power BI is an appropriate prototype tool (consistent with EV-09). |
| A-09 | Synthetic data can realistically represent the analytical patterns without reflecting real results. |
| A-10 | Store maturity is the strongest single driver of expected performance during the first one to two years. *Hypothesis.* |
| A-11 | Candidate peer dimensions are maturity, province, host retail format and local market type. The final set requires validation. |

## 13. Unknowns requiring internal validation

| ID | Unknown |
|---|---|
| U-01 | What store-performance reporting exists today, who uses it, and how much it is trusted. |
| U-02 | Whether the hypothesized comparison problem is actually experienced, and by whom. |
| U-03 | Which KPI definitions are currently used, and whether they differ across functions. |
| U-04 | Source systems, integration patterns and data latency for each domain. |
| U-05 | Whether examinations and purchases can be linked, at what grain, and under what privacy constraints. |
| U-06 | Who owns the store master (opening dates, format, region) and how reliable it is. |
| U-07 | How store maturity is defined internally, if at all. Public evidence uses a "less than six months" boundary (EV-06); Developing and Mature boundaries are unknown. |
| U-08 | Applicable federal and provincial privacy and health-information obligations for aggregated clinical activity data. |
| U-09 | Whether partners may see other stores' figures, given commercial confidentiality between independently owned businesses. |
| U-10 | Any data-sharing constraints linked to host-retailer (e.g., Loblaw) arrangements. |
| U-11 | How order fulfilment works (e.g., central versus local finishing) and what "on time" means. |
| U-12 | Who owns recall programmes and how recall bookings are attributed. |
| U-13 | Current spreadsheet or manual reporting effort. |
| U-14 | Stakeholder availability for discovery, prototyping and UAT. |
| U-15 | How PC Optimum launch timing should be flagged in trend analysis. |

## 14. Research limitations

- **Public sources only.** No internal data, system documentation or stakeholder input.
- **Mostly company-authored or promotional sources.** Press releases and a recruitment prospectus present the business favourably.
- **Commissioned survey.** EV-07 was commissioned by Specsavers. It is national in scope and does not measure store performance.
- **Access issues.** Four specsavers.ca pages returned HTTP 403. Claims were verified through official newswire.ca and loblaw.ca republications instead.
- **Dated material.** The prospectus reports 151 Canadian stores (2024/2025) and is cited only for the ownership model and support services. EV-06 is about 2.5 years old.
- **Job postings show intent, not internal reality.** Postings change or close. Some tool names came from automated page summaries and should be re-confirmed before quoting.
- **Unverified items.** Store formats beyond in-grocery; first-year revenue figures from Feb 2024.
- **Point in time.** Findings reflect public information as of 13 Sep 2026.
- **Synthetic data.** Every quantitative "finding" later in this case study is illustrative only.

---

## 15. Problem-statement canvas

| Question | Answer |
|---|---|
| **Who experiences the problem?** | *Hypothesized:* Retail Partners and Optometry Partners running new or changing stores, and Support Office teams responsible for supporting store performance across a fast-growing, multi-province network (titles to be validated in Phase 2). |
| **What decision are they making?** | Which stores warrant attention relative to comparable stores, which candidate factors to investigate, and which team should follow up. |
| **What information do they need?** | Consistent, governed store-week KPIs for capacity, booking, attendance, examinations, conversion, fulfilment and recall; each store's position against a fair peer cohort; trend over time since opening; context (province, format, maturity); and visible data completeness and freshness. |
| **What is the potential consequence?** | *If the hypothesis holds:* young stores could be misjudged against mature ones; genuine problems could surface late; effort could go to the wrong stores; teams could disagree about the numbers; and conclusions could be drawn from incomplete data. |
| **What would successful improvement look like?** | Users identify stores that warrant attention **faster and with more confidence**, compare against appropriate peers, agree on definitions, see data-quality caveats up front, and route follow-up to a named team. The measure of success is quicker, better-targeted investigation, **not** the dashboard explaining performance on its own. |

---

## Phase 1 close

### Decisions made
1. Refined title adopted for the portfolio (author's decision; not stakeholder-approved).
2. Proposed refinement of the primary business decision to remove causal wording. The original is kept as the reference until approved.
3. Scope set at Canadian network, store-week aggregates and eight KPI domains; PC Optimum, patient-level, individual-performance, profitability and ROI items excluded.
4. Peer-comparison dimensions stated as a hypothesis (A-11) for later phases to inherit.
5. Generic system categories anchored to public evidence (EV-05, EV-09d, EV-10), with no platforms named.
6. Evidence IDs EV-01 to EV-11 created. EV-01 to EV-09 preserve Finding numbering.

### Assumptions introduced
A-01 to A-11 (section 12). The ones most likely to be challenged: A-06 (sharing aggregated exam counts), A-07 (other store formats) and A-10 (maturity as the main driver).

### Questions requiring validation
Priority items from U-01 to U-15:
- U-01 and U-02: Does current reporting already meet this need? Is the comparison problem real?
- U-05: Can examination and purchase activity be linked, and under what privacy controls?
- U-07: How is store maturity defined internally?
- U-09: Are partners allowed to see peer-store figures?

### Recommended corrections to the master context
1. **Finding 1 vs Finding 2:** label ">260 locations" as a July 2025 projection and ">270 stores" as the reported March 2026 figure.
2. **Findings 3 and 4 source:** cite the prospectus (pp. 2, 9–10) for the two-entity model and provincial regulation. The retail-partnership web page does not mention provincial regulation.
3. **Finding 5:** Training and Recruitment are two separate services. Nine areas in total.
4. **Finding 6:** the first-year revenue figures were not verified in this pass. Cite only the store-age share, exam count and glasses count.
5. **Finding 7:** use the source wording ("overdue for an eye exam"; "last eye exam was over five years ago") and drop "or never." Add the verified 61% coverage-misunderstanding statistic and the survey method.
6. **Finding 8:** add the announcement date, 22 Jun 2026.
7. **Finding 9:** the Product Owner posting (jid-13803) is a PMS/EMR application role, not a data product owner. Keep it as evidence of system categories. Base the data-team inference on the Data Business Analyst, Data Analyst and Data Delivery Manager postings.

*Document status: drafted by the author for the portfolio. No Specsavers stakeholder has reviewed or approved it. Later phases build on it.*
