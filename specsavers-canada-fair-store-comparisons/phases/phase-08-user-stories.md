# Phase 8 — User Stories and Acceptance Criteria

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–7

> **Outside-in disclaimer.** Personas are role-based and fictional. Story values, thresholds and test data refer to the **synthetic dataset** (Phase 12) and illustrative rules. Nothing here reflects actual Specsavers users, targets or results.

**Causation rule for all stories.** Reporting identifies **areas to investigate**. It must never state or imply that a KPI variance is *caused* by a factor. Prohibited wording in the product: "caused by", "because of", "due to", "driver of", "root cause". This is tested in UAT-21.

---

## Personas (role-based)

| Persona | Stakeholder | Context | Main decision |
|---|---|---|---|
| **P1 · Retail Operations Lead** | SH-04 | Oversees retail performance across regions; business sponsor | Where should regional support go? |
| **P2 · Regional Retail Manager** | SH-03 | Supports 15–30 stores (illustrative); weekly triage | Which stores should I contact first, and about what? |
| **P3 · Retail Partner** | SH-01 | Leads a store opened 20 weeks ago (illustrative) | Where should my team focus? |
| **P4 · Optometry Partner** | SH-02 | Leads the clinic in the same store | Is clinic capacity and attendance on track? |
| **P5 · Finance Analyst** | SH-07 | Verifies commercial figures | Can revenue KPIs be trusted? |
| **P6 · Privacy Officer** | SH-13 | Approves data use and access | Is sensitive information protected? |
| **P7 · Product Owner** | SH-08 | Owns the data product backlog | Is the release fit to go live? |

---

## Definition of Ready (baseline, applies to all stories)
1. The story has a persona, a clear value statement and linked BR/FR IDs.
2. Acceptance criteria are written in Given/When/Then form and are testable with synthetic data.
3. The KPIs used have at least a **v0.1 draft** dictionary entry (Phase 6), with open questions noted.
4. Data sources and mappings are identified (Phase 7), even if some are assumed.
5. Privacy and access implications are reviewed with SH-13 if the story exposes clinical-activity or commercial data.
6. Dependencies are identified and sized; the story fits in one sprint or is split.

## Definition of Done (baseline, applies to all stories)
1. All acceptance criteria pass in the test environment with synthetic data (PR-08).
2. Measures reconcile to independent calculation (Python or SQL check) for the test cases.
3. Accessibility checklist completed for affected visuals (NFR-04).
4. KPI dictionary, lineage register and release notes updated (DR-01, DR-02).
5. Role-based access verified for the affected visuals (SR-01 to SR-03).
6. Product Owner accepts; no open Severity 1 or 2 defects (Phase 14 definitions).

Story-specific additions are listed in each story.

---

## US-01 — National network overview
| Field | Detail |
|---|---|
| Persona | P1 Retail Operations Lead |
| User story | **As a** Retail Operations Lead, **I want** a weekly network overview of access, operational, commercial and data-quality KPIs with trends and a provincial view, **so that** I can see whether the network is moving as expected and where to direct attention. |
| Business value | One consistent starting point for weekly network review; supports BO-01, BO-02, BO-03. |
| Linked requirements | BR-01, BR-05, BR-11 · FR-01, FR-02, FR-08, FR-09 · NFR-01, NFR-02, NFR-04 · DR-06 · KPI-01 to KPI-09, KPI-11, KPI-12 |
| Priority | Must |
| Dependencies | Phase 6 dictionary; semantic model; FR-08 status logic; SR-03 (revenue visibility) |

**Acceptance criteria**
1. **Given** the latest published week is W26 in the synthetic dataset, **when** I open the report, **then** the Network Overview shows W26 by default with KPI cards for total active stores, completed exams, utilization, attendance, conversion, revenue per completed exam, on-time fulfilment, recall-booking rate and data-quality status.
2. **Given** a KPI card, **when** I compare its value with an independent calculation, **then** each rate equals Σ numerator ÷ Σ denominator across included stores (not an average of store ratios), within ±0.1 percentage points (rounding).
3. **Given** stores with Red data quality in the selected week, **when** the overview renders, **then** those store-weeks are excluded from rates and the card footnote shows "Excludes n stores (data check required)".
4. **Given** I select a province on the map or tile visual, **when** the page updates, **then** every visual filters to that province and the filter summary line states the selection.
5. **Given** a 26-week period, **when** I view the weekly trend, **then** 26 points are shown, and weeks with any Amber or Red stores are marked.

**Negative / exception scenario:** **Given** the latest refresh failed the publish gate (CP-09), **when** I open the report, **then** the prior published week is shown with the banner "Latest week not yet published – data as at [timestamp]", and no partial week is displayed.

**Story-specific DoR:** agree the 6–8 headline KPIs with SH-04. **Story-specific DoD:** page performance meets NFR-01 on the synthetic volume test.

---

## US-02 — Regional comparison
| Field | Detail |
|---|---|
| Persona | P2 Regional Retail Manager |
| User story | **As a** Regional Retail Manager, **I want to** compare my region with other regions and see whether a pattern is shared across stores or concentrated in a few, **so that** I can decide between store-specific follow-up and escalation to a central team. |
| Business value | Distinguishes local from systemic issues (BO-04; D-06). |
| Linked requirements | BR-07, BR-01 · FR-02, FR-05, FR-06 · DR-07 · KPI-02, KPI-03, KPI-05, KPI-07, KPI-08 |
| Priority | Should |
| Dependencies | Region master data (MDM-04); US-01 |

**Acceptance criteria**
1. **Given** the Network Overview, **when** I view the region comparison table, **then** each region shows KPI values, the network value and the number of stores contributing.
2. **Given** the synthetic Atlantic region pattern of elevated turnaround (Phase 12, pattern P2), **when** I sort the region table by average order turnaround, **then** Atlantic ranks highest, and the share of Atlantic stores above the network median is shown (e.g., "5 of 6 stores").
3. **Given** I drill through from a region to its stores, **when** the store list opens, **then** it is filtered to that region with the selected week and KPI retained, and "Back" returns me to the region view.
4. **Given** a regional pattern is visible, **when** I view the suggested follow-up, **then** it reads as a prompt (e.g., "Review order routing and lab turnaround with Supply Chain") and not as a cause.

**Negative / exception scenario:** **Given** I am a Regional Retail Manager for the West region only, **when** I try to drill through to an Atlantic store, **then** the drill-through is unavailable. Region-level aggregates for other regions are shown only if SH-13 approves region-level visibility (open question U-38); otherwise only my region and a network total labelled as a comparison population are shown. *(The prototype uses this conservative default as a demonstration assumption; it is not a stakeholder decision.)*

**Story-specific DoR:** region definitions confirmed (MDM-04). **Story-specific DoD:** synthetic regional pattern detected in UAT-02 and UAT-05.

---

## US-03 — Store-maturity benchmarking
| Field | Detail |
|---|---|
| Persona | P2 Regional Retail Manager (primary); P3 Retail Partner (secondary) |
| User story | **As a** Regional Retail Manager, **I want to** compare a store with peers at the same maturity stage and format, including a ramp-up curve by weeks since opening, **so that** I judge new stores against realistic expectations rather than against mature stores. |
| Business value | Fair comparison (BO-01); earlier identification of ramp-up concerns (BO-02). |
| Linked requirements | BR-02, BR-06 · FR-03, FR-04, FR-13, FR-16 · DR-07, DR-10 · PR-03, PR-07 · KPI-04, KPI-10 |
| Priority | Must |
| Dependencies | Opening-date master data (MDM-03); cohort approval (Phase 6); US-10 |

**Acceptance criteria**
1. **Given** a synthetic store whose weeks since opening cross 26 → 27 during the period, **when** I view its weekly cohort, **then** it shows "New" up to the week where weeks_since_opening = 26 and "Developing" from week 27 onward.
2. **Given** I select a Developing, Grocery-hosted store, **when** the comparison table loads, **then** it shows store value, peer median, variance (absolute and %), quartile band and the basis text "Developing · Grocery-hosted · n = X".
3. **Given** the peer median shown, **when** it is recalculated independently from the synthetic data for the same peer set and 4-week window, **then** the values match.
4. **Given** a New store, **when** I view the ramp-up chart, **then** the x-axis is weeks since opening, the store line and peer median line are shown, and the ramp index (KPI-10) label matches the KPI-10 formula.
5. **Given** I am logged in as a Retail Partner, **when** I view the peer distribution, **then** peers appear as anonymous points with no store names in labels, tooltips or exports.

**Negative / exception scenario:** **Given** a store with a missing or invalid opening date, **when** I open benchmarking, **then** the store shows "Unclassified – opening date requires review", is excluded from all peer statistics, and no ramp index is shown.

**Story-specific DoR:** peer floor confirmed by SH-13 (illustrative 5). **Story-specific DoD:** boundary-crossing and unclassified test cases pass (UAT-03, UAT-22).

---

## US-04 — Store-level diagnostic
| Field | Detail |
|---|---|
| Persona | P3 Retail Partner (primary); P4 Optometry Partner; P2 Regional Retail Manager |
| User story | **As a** Retail Partner, **I want to** see my store's appointment-to-purchase funnel, fulfilment and recall performance against peers, with flagged areas to investigate, **so that** I can focus my team's effort where the largest differences are. |
| Business value | Turns monitoring into targeted, non-causal follow-up (BO-04, BO-05). |
| Linked requirements | BR-03, BR-09, BR-11, BR-06 · FR-06, FR-14, FR-15 · NFR-05, NFR-08 · KPI-02 to KPI-09 |
| Priority | Must |
| Dependencies | US-03 (peer logic); prompt library (FR-15); SR-03 |

**Acceptance criteria**
1. **Given** my store and week, **when** I open the Store Diagnostic page, **then** I see a funnel: available slots → held appointments → completed exams → purchasing customers, with stage rates and peer medians, plus a "status not recorded" segment where unresolved statuses exist.
2. **Given** the synthetic high-demand, low-attendance stores (pattern P3) in a week where rule (a) is met (e.g., SYN-012 in the week of 2026-08-03; SYN-019 in the week of 2026-08-17), **when** their diagnostic loads, **then** attendance is flagged as the stage with the largest negative variance, with the prompt "Check reminder and confirmation process, booking lead times and no-show follow-up · Typical follow-up: store team with Regional Retail Manager".
3. **Given** the synthetic mature store with declining conversion (pattern P4), **when** I view the conversion trend, **then** an adverse-trend exception is shown (rule b: a decline of 15% or more versus the store's own prior 8-week average for 3 or more consecutive weeks) with a non-causal prompt.
4. **Given** any exception prompt, **when** its text is checked against the prohibited-terms list, **then** no prohibited causal term appears.
5. **Given** I am an Optometry Partner, **when** I open the page, **then** capacity, utilization, attendance, completed exams and recall are visible, and revenue per completed exam is hidden (SR-03 default). *Conversion (KPI-05) visibility for Optometry Partners is unresolved (U-41); the prototype shows it as a demonstration assumption, not as a decision.*

**Negative / exception scenario:** **Given** a store-week with Red data quality (pattern P5), **when** I open the diagnostic, **then** affected KPIs show "Data check required", **no** performance exception or investigation prompt is raised for those KPIs, and a data-quality prompt is shown instead ("Review data completeness with the data team").

**Story-specific DoR:** prompt wording approved by SH-04, with SH-02/SH-16 input for clinical stages. **Story-specific DoD:** comprehension check with 5 or more pilot users. At least 80% describe a flag as "an area to investigate" (BR-03 measure).

---

## US-05 — KPI-definition access
| Field | Detail |
|---|---|
| Persona | P5 Finance Analyst (primary); all users |
| User story | **As a** Finance Analyst, **I want to** see the approved definition, formula, exclusions, owner and version of every KPI from within the report, **so that** I can confirm figures mean what I think they mean before using them. |
| Business value | Trusted, consistent definitions (BO-03). |
| Linked requirements | BR-04 · FR-07 · DR-01, DR-02, DR-08 · KPI-01 to KPI-12 |
| Priority | Must |
| Dependencies | REF_KPI_DICTIONARY table; KPI change control |

**Acceptance criteria**
1. **Given** any KPI visual, **when** I hover over its info icon, **then** a tooltip shows the business name, a one-line definition, the owner and the version.
2. **Given** the Definitions panel, **when** I select "Revenue per completed exam", **then** I see formula, numerator, denominator, exclusions (including returns, refunds and taxes treatment), grain, source, owner, version and last change date, matching Phase 6 v0.1.
3. **Given** a KPI definition version changes from v0.1 to v0.2, **when** the report refreshes after the effective date, **then** the displayed version updates, and the change log shows reason, approver and effective date.
4. **Given** every measure in the model, **when** the dictionary coverage check runs, **then** 100% of displayed measures map to an "Approved" dictionary entry.

**Negative / exception scenario:** **Given** a KPI whose dictionary status is "Draft", **when** the production report is published, **then** that KPI does not appear in production visuals, and the publish checklist records the exclusion.

**Story-specific DoR:** dictionary table structure agreed. **Story-specific DoD:** coverage check automated.

---

## US-06 — Data-quality transparency
| Field | Detail |
|---|---|
| Persona | P2 Regional Retail Manager |
| User story | **As a** Regional Retail Manager, **I want to** see whether each store's data is complete and current before I act on it, **so that** I don't raise concerns with a partner based on incomplete data. |
| Business value | Prevents unfair conclusions and wasted effort (BO-03, BO-01). |
| Linked requirements | BR-05 · FR-08 · DR-04, DR-05, DR-09 · KPI-11, KPI-12 |
| Priority | Must |
| Dependencies | Load metadata (A-20); CP-01 to CP-09 |

**Acceptance criteria**
1. **Given** a synthetic store-week with completeness 98% or higher and status Current, **when** I view it, **then** status is Green with no warning.
2. **Given** a synthetic store-week with completeness 90% to under 98% **or** status Delayed, **when** I view it, **then** status is Amber and affected KPI values show a warning icon and the text "Provisional – data incomplete or delayed".
3. **Given** a synthetic store-week with completeness below 90% **or** status Stale, **when** I view it, **then** status is Red and KPI values are withheld ("Data check required").
4. **Given** the report banner, **when** the page loads, **then** it shows the data-as-at timestamp and the correct count of stores with Amber or Red status for the selected week.
5. **Given** a store-week where no recall contacts were expected (no programme), **when** I view recall KPIs, **then** it shows "No recall programme (not applicable)", not 0% and not a data error.

**Negative / exception scenario:** **Given** a source extract missing for a store-week, **when** the model refreshes, **then** the KPIs are **null** (not zero), the reason "Source not received" is shown, and prior-week values are **not** carried forward.

**Story-specific DoR:** illustrative thresholds accepted for testing. **Story-specific DoD:** all seeded data-quality patterns (P5) produce the expected status in UAT-08.

---

## US-07 — Role-based access
| Field | Detail |
|---|---|
| Persona | P6 Privacy Officer (primary); P3 Retail Partner; P2 Regional Retail Manager |
| User story | **As a** Privacy Officer, **I want** users to see only the stores and measures their role permits, **so that** patient-derived and partner commercial information is protected. |
| Business value | Privacy and confidentiality by design (BO-06); a precondition for release. |
| Linked requirements | BR-08, BR-06 · FR-09, FR-10 · SR-01, SR-02, SR-03, SR-06, SR-07 · PR-01, PR-02, PR-05, PR-07 |
| Priority | Must |
| Dependencies | Access mapping table (MDM-08); identity integration (assumed); role model approval |

**Acceptance criteria**
1. **Given** a test Retail Partner mapped to store SYN-014, **when** they open any page, **then** only SYN-014 appears in store-level visuals, slicers, tooltips and drill-through, and peers are anonymous.
2. **Given** a test Regional Retail Manager mapped to the Atlantic region, **when** they open any page, **then** cards, charts, tables, selectors, tooltips and the data-quality banner use Atlantic stores only (SYN-025 to SYN-030), and no out-of-region store is named.
3. **Given** a test Optometry Partner, Supply Chain analyst or Marketing analyst, **when** they view any page, **then** revenue per completed exam and eyewear revenue are hidden in visuals, tooltips, exports and "Analyze in Excel" (UAT-11).
4. **Given** a test user with no access mapping, **when** they open the report, **then** access is denied with a message to request access.
5. **Given** the semantic model schema, **when** the privacy scan runs, **then** 0 patient-identifier, clinical-content or practitioner fields are present (PR-01, PR-02, PR-05).

**Negative / exception scenario:** **Given** a Retail Partner edits a report URL or filter to request another store, **when** the page loads, **then** no data for that store is returned and the attempt does not reveal whether the store exists.

**Story-specific DoR:** role matrix (Phase 5) approved by SH-13. **Story-specific DoD:** SH-13 witnesses and signs the access test results.

---

## US-08 — Approved report export
| Field | Detail |
|---|---|
| Persona | P2 Regional Retail Manager |
| User story | **As a** Regional Retail Manager, **I want to** export approved aggregated tables for my region, **so that** I can prepare for partner meetings without rebuilding figures manually. |
| Business value | Reduces manual compilation (BO-07, conditional) without uncontrolled data distribution. |
| Linked requirements | BR-08, BR-12 · FR-11 · SR-04, SR-05 · PR-04, PR-07 |
| Priority | Should |
| Dependencies | Export settings (A-25); US-07 |

**Acceptance criteria**
1. **Given** an approved visual (e.g., the store KPI comparison table), **when** I choose Export, **then** a file downloads containing only the aggregated values displayed, with "Internal – Confidential – Aggregated data" in the header or file name.
2. **Given** a displayed count from 1 to 4 (e.g., recall bookings in a New store), **when** I export, **then** the file shows "<5" and the derived rate as "Suppressed (<5)" (or "n/a (low volume)" if the denominator is under 5), matching the screen.
3. **Given** an export event, **when** the audit log is checked, **then** it records user, timestamp, report, visual and row count.
4. **Given** a visual not on the approved export list (e.g., the peer distribution), **when** I open its menu, **then** no export option is available.

**Negative / exception scenario:** **Given** I attempt to export underlying data from any visual, **when** I open the export dialog, **then** only the summarised option is available or export is blocked, and no row-level or patient-level data can be obtained.

**Story-specific DoR:** approved export list agreed with SH-13. **Story-specific DoD:** UAT-12 passes, witnessed by SH-13.

---

## US-09 — UAT and business sign-off
| Field | Detail |
|---|---|
| Persona | P7 Product Owner (primary); P1 Retail Operations Lead (sponsor sign-off) |
| User story | **As the** Product Owner, **I want** a structured UAT with traceable scenarios, defect triage and explicit exit criteria, **so that** the business can make an evidence-based go/no-go decision for the pilot. |
| Business value | Controlled release within the MVP constraint (BR-10); stakeholder confidence. |
| Linked requirements | BR-10 (constraint) and all Must BRs · NFR-05 · Phase 14 UAT plan · Phase 9 traceability |
| Priority | Must (enabler story) |
| Dependencies | US-01 to US-08 and US-10 complete in test; testers available (A-18); synthetic and reconciliation data |

**Acceptance criteria**
1. **Given** the traceability matrix, **when** UAT planning completes, **then** every Must story has at least one UAT scenario with an expected result.
2. **Given** UAT execution is complete, **when** results are summarised, **then** 100% of Must scenarios are executed, at least 95% pass, and all failures have a logged defect with severity.
3. **Given** open defects, **when** the go/no-go meeting is held, **then** there are 0 open Severity 1 and 0 open Severity 2 defects, and all Severity 3 defects have an agreed workaround and target date.
4. **Given** the privacy and access tests, **when** sign-off is requested, **then** SH-13 has signed the access and privacy results **before** SH-04 signs business acceptance.
5. **Given** sign-off is granted, **when** the decision is recorded, **then** the record lists approvers (SH-04, SH-08, SH-13, SH-12), date, scope version, known limitations and pilot start date.

**Negative / exception scenario:** **Given** a Severity 2 reconciliation defect remains open (e.g., revenue outside ±1% tolerance), **when** the go/no-go meeting is held, **then** the decision is "No-go" or "Conditional go", with the revenue KPI withheld and the condition documented. The pilot cannot start with the defective KPI visible.

**Story-specific DoR:** UAT plan (Phase 14) approved; testers booked. **Story-specific DoD:** signed UAT completion report stored with the release record.

---

## US-10 — Small-peer-group and small-count protection *(additional story)*
| Field | Detail |
|---|---|
| Persona | P6 Privacy Officer (primary); P3 Retail Partner |
| User story | **As a** Privacy Officer, **I want** peer statistics and small counts suppressed or broadened when groups are too small, **so that** no partner's results or patient-event counts can be inferred, and comparisons stay statistically meaningful. |
| Business value | Resolves the conflict between comparison and confidentiality (C-03) safely. |
| Linked requirements | BR-02, BR-08 · FR-16 · PR-03, PR-04 · KPI-03, KPI-05, KPI-09, KPI-10 |
| Priority | Must |
| Dependencies | Floor and threshold decision (U-30); US-03 |

**Acceptance criteria**
1. **Given** a synthetic store whose cohort × format peer group has fewer than 5 stores, **when** I view benchmarking, **then** the comparison falls back to the cohort across all formats and the warning states both n values.
2. **Given** the cohort-level group also has fewer than 5 stores, **when** I view benchmarking, **then** no peer statistic is shown and the text reads "Peer comparison not available (minimum group size not met)".
3. **Given** a store with 1 to 4 recall bookings in a period, **when** I view recall KPIs, **then** the count shows "<5", the rate shows "Suppressed (<5)" (or "n/a (low volume)" if contacts are under 5), and no chart position, tooltip or data table reveals the value.
4. **Given** the ramp-up chart, **when** fewer than 5 peers are observed at a weeks-since-opening point, **then** the peer line is not drawn for that point and a note explains the gap.

**Negative / exception scenario:** **Given** a Regional Retail Manager tries to derive a suppressed value by filtering to a single store, **when** the filters are applied, **then** suppression still applies at the displayed aggregation, and the suppressed value cannot be recovered from totals on the same page (complementary suppression, where needed, reviewed with SH-13).

**Story-specific DoR:** SH-13 confirms the floor and threshold for testing. **Story-specific DoD:** UAT-18 passes, witnessed by SH-13.

---

## Story summary

| Story | Topic | Priority | MVP page | Key UAT scenarios (Phase 14) |
|---|---|---|---|---|
| US-01 | National network overview | Must | 1 | UAT-01, UAT-13, UAT-14, UAT-15, UAT-16, UAT-23 |
| US-02 | Regional comparison | Should | 1 | UAT-02, UAT-05, UAT-17 |
| US-03 | Store-maturity benchmarking | Must | 2 | UAT-03, UAT-04, UAT-22 |
| US-04 | Store-level diagnostic | Must | 3 | UAT-06, UAT-21, UAT-24 |
| US-05 | KPI-definition access | Must | All | UAT-07 |
| US-06 | Data-quality transparency | Must | 1, 3 | UAT-08, UAT-15 |
| US-07 | Role-based access | Must | All | UAT-09, UAT-10, UAT-11, UAT-23 |
| US-08 | Approved report export | Should | All | UAT-12 |
| US-09 | UAT and business sign-off | Must (enabler) | — | UAT-20 |
| US-10 | Small-group protection | Must | 2, 3 | UAT-18 |

---

## Phase 8 close

### Decisions made
1. Ten stories: nine requested plus **US-10** for small-group and small-count protection, which the synthetic data will exercise.
2. Baseline Definition of Ready and Definition of Done, with story-specific additions.
3. A prohibited causal-wording list becomes a testable acceptance criterion (UAT-21).
4. Privacy sign-off must precede business sign-off (US-09 AC4).
5. UAT scenario IDs UAT-01 to UAT-24 reserved for Phase 14.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-35 | Test user accounts can be created per role in a non-production environment. |
| A-36 | Pilot users are available for a comprehension check (5 or more users). |

### Questions requiring validation
- U-38. Should Regional Retail Managers see other regions' aggregates? (US-02 negative scenario.)
- U-39. Is complementary suppression required, or is primary suppression sufficient? (US-10.)

### Recommended corrections
- **FR-12 (persistent filters) has no user story.** This is intentional, given its Could priority, and will surface as an orphan finding in Phase 9.
