# Phase 4 — Functional and Reporting Requirements

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Builds on:** Phases 1–3

> **Outside-in disclaimer.** These functional requirements describe a proposed prototype reporting product. They are not a description of Specsavers systems. Thresholds and numbers are **illustrative**.

**Conventions**
- **Users:** RP = Retail Partner (SH-01) · OP = Optometry Partner (SH-02) · RRM = Regional Retail Manager (SH-03) · ROL = Retail Operations leadership (SH-04) · FUN = functional analysts in Marketing, Supply Chain or Finance (SH-05/06/07) · GOV = Governance/Privacy (SH-13) · ADM = report administrator (SH-11/SH-10).
- **Reporting week:** Monday–Sunday. Grain: store-week (DR-06, Phase 5).
- **Maturity cohorts (illustrative, to be approved in Phase 6):** **New** = 0–26 weeks since opening (anchored to the public "less than six months" boundary, EV-06); **Developing** = 27–104 weeks; **Mature** = more than 104 weeks. Cohorts are assigned *as at each week*.
- **Peer group (default rule):** same maturity cohort **and** same store format. If there are fewer peers than the minimum floor (illustrative **5 stores**, floor owned by SH-13), fall back to the same maturity cohort across all formats and show a warning. If still below the floor, show no peer statistic.

---

## 1. Functional requirements catalogue

### FR-01 — National network overview
| Field | Detail |
|---|---|
| Requirement | Provide a network overview page showing headline KPIs for the selected reporting week and trend: total active stores, completed examinations, appointment utilization, attendance rate, exam-to-purchase conversion, revenue per completed exam (role-restricted), on-time fulfilment, recall-booking rate and data-quality status. |
| Related BR | BR-01, BR-11, BR-05 |
| User | ROL, RRM, FUN |
| Trigger | User opens the report or selects a reporting week. |
| Expected behaviour | KPI cards show the current-week value, change against the prior 4-week average, and a 13-week sparkline. A map or tile view by province shows the selected KPI. A weekly trend line covers 26 weeks. Cards for KPIs with incomplete data show a data-quality icon. |
| Business rule | Default week = latest **complete and published** week. Network KPIs are recalculated from summed numerators and denominators (never averages of store ratios). Stores flagged "withheld" (FR-08) are excluded from rates, and the count of excluded stores is displayed. |
| Priority | Must |
| Acceptance summary | Totals reconcile to the sum of store values; ratio KPIs equal sum(numerator) ÷ sum(denominator); the default week is the latest published week; the excluded-store count is visible. |
| Dependency | KPI dictionary (Phase 6); DR-06; FR-08; SR-03 |
| Open validation question | Which 6–8 KPIs should leadership see first? |

### FR-02 — Province and region filtering
| Field | Detail |
|---|---|
| Requirement | Allow filtering by region, province, store format, host-retail banner, maturity cohort and reporting-week range. |
| Related BR | BR-01, BR-07 |
| User | All roles (within their access scope) |
| Trigger | User changes a slicer. |
| Expected behaviour | All visuals on the page update. The active filters are summarised in a "Filters applied" text line. Filter options are limited to the stores the user is authorised to see. |
| Business rule | Region → province hierarchy comes from the store master (as at the selected week). Cohort filter uses the cohort as at each week (a store can move cohort during a date range). |
| Priority | Must |
| Acceptance summary | Filtering changes all visuals consistently; the filter summary is accurate; unauthorised stores never appear in slicer lists. |
| Dependency | Store master (DR-07); SR-02 |
| Open validation question | How are regions defined internally, and do region assignments change over time? |

### FR-03 — Store-maturity classification
| Field | Detail |
|---|---|
| Requirement | Classify every store-week into a maturity cohort based on weeks since opening, and display the store's current cohort and weeks since opening. |
| Related BR | BR-02 |
| User | All roles |
| Trigger | Weekly refresh. |
| Expected behaviour | Each store-week carries `weeks_since_opening` and `maturity_cohort`. The store header shows, for example, "Developing · week 41". The cohort definition version is shown in the tooltip. |
| Business rule | weeks_since_opening = floor((week_start − opening_date) ÷ 7). Cohort boundaries come from a versioned cohort table (DR-10), not hard-coded logic. Stores with a missing or invalid opening date are classified "Unclassified" and excluded from peer statistics, with a data-quality warning. |
| Priority | Must |
| Acceptance summary | A store crossing week 27 changes from New to Developing in that week; unclassified stores are flagged and excluded from peer statistics. |
| Dependency | Opening-date master data (DQ-33, SH-15); Phase 6 cohort approval |
| Open validation question | Which event defines "opening" (e.g., first exam, grand opening)? How are conversions and relocations treated? |

### FR-04 — Store-to-peer comparison
| Field | Detail |
|---|---|
| Requirement | For a selected store and KPI, show the store value against the **peer median**, the variance (absolute and %) and the store's position in the peer distribution (quartile band). |
| Related BR | BR-02, BR-06, BR-03 |
| User | RP, OP, RRM, ROL |
| Trigger | User selects a store, or drills through to a store. |
| Expected behaviour | A KPI comparison table lists store value, peer median, variance, quartile band and peer-group basis ("Developing · Grocery-hosted · n = 7"). A distribution chart (dot or box plot) shows anonymised peer values; the selected store is highlighted. |
| Business rule | Peer group per the default rule above. **Peer store identities are never shown to RP or OP roles** (PR-07). Peer statistics require at least the minimum floor (PR-03). Variance is calculated on 4-week rolling values to reduce weekly noise (illustrative). |
| Priority | Must |
| Acceptance summary | The peer median matches an independent calculation; the peer basis and n are displayed; partners see no peer store names; below-floor groups trigger the fallback or suppression (FR-16). |
| Dependency | FR-03; FR-16; PR-03; PR-07 |
| Open validation question | Is median plus quartile the most understandable comparison for partners? |

### FR-05 — National-to-store drill-through
| Field | Detail |
|---|---|
| Requirement | Allow drill-through from network, region or cohort visuals to the store benchmarking page and the store diagnostic page, carrying the selected store and week context. |
| Related BR | BR-01, BR-07, BR-09 |
| User | ROL, RRM, FUN |
| Trigger | User right-clicks (or uses a button) on a store, region or exception row. |
| Expected behaviour | The target page opens filtered to the store and week, with a "Back" button returning to the source page with its filters intact. |
| Business rule | Drill-through is only available to stores within the user's RLS scope. The store and week context passes; other slicers keep the target page's defaults unless explicitly passed. |
| Priority | Must |
| Acceptance summary | The drill-through lands on the correct store and week; Back restores the prior view; out-of-scope stores cannot be reached. |
| Dependency | FR-04; FR-14; SR-02 |
| Open validation question | Which paths do regional managers use most? |

### FR-06 — Exception highlighting
| Field | Detail |
|---|---|
| Requirement | Flag store-weeks where a KPI differs materially from the peer median, or trends adversely, and list them in an exception table sorted by severity. |
| Related BR | BR-09, BR-01, BR-02 |
| User | RRM, ROL, RP (own store only) |
| Trigger | Weekly refresh. |
| Expected behaviour | Exception table columns: store, cohort, KPI, journey stage, store value, peer median, variance, weeks flagged consecutively, data-quality status and suggested investigation area (FR-15). Colour plus icon plus text label (never colour alone). |
| Business rule | **Illustrative rule set v0.1:** (a) 4-week rolling value below the peer 25th percentile **and** at least 10% below the peer median; or (b) a decline of 15% or more versus the store's own prior 8-week average for 3 consecutive weeks. No exception is raised when data-quality status is **red** (it shows as a "data check" row instead). Rules are versioned and approved by SH-04. *Repair-pass note:* the prototype uses **exception rule set v0.2** (Phase 13 §4), which keeps rules (a) and (b) unchanged and adds versioned parameters: recall exceptions only for Developing/Mature stores with 40+ contacts; consecutive weeks counted per KPI with unavailable weeks resetting the run; no evaluation in a Red selected week; ramp trigger after 4 consecutive weeks below 80. |
| Priority | Must |
| Acceptance summary | Seeded synthetic patterns (Phase 12) generate the expected flags; red data-quality weeks do not generate performance exceptions; the rule version is displayed. |
| Dependency | FR-04; FR-08; KPI dictionary thresholds |
| Open validation question | What exception volume per week is manageable for a regional manager? |

### FR-07 — KPI definitions and ownership
| Field | Detail |
|---|---|
| Requirement | Provide in-report access to each KPI's business definition, formula, inclusions and exclusions, owner, version and last change date. |
| Related BR | BR-04 |
| User | All roles |
| Trigger | User hovers over the info icon on a KPI, or opens the "Definitions" panel. |
| Expected behaviour | The tooltip shows a short definition. The Definitions page or panel shows the full entry from the governed KPI dictionary table. |
| Business rule | Definitions are sourced from a maintained dictionary table (DR-02), not typed into visuals. Every displayed KPI must have an "Approved" status; draft KPIs are hidden in production. |
| Priority | Must |
| Acceptance summary | Every KPI on every page links to a dictionary entry whose version matches the measure version. |
| Dependency | Phase 6 dictionary; DR-02 |
| Open validation question | Is there an existing enterprise glossary to reuse? |

### FR-08 — Data-quality and freshness warnings
| Field | Detail |
|---|---|
| Requirement | Show data completeness and freshness status per store-week and per source, and apply warning or withholding rules to affected KPIs. |
| Related BR | BR-05 |
| User | All roles |
| Trigger | Weekly refresh; user views any KPI. |
| Expected behaviour | Report-level banner: "Data as at [timestamp] · [n] stores with data warnings". Store-level status: **Green** (complete and current), **Amber** (warning, KPI shown with icon), **Red** (KPI withheld for that store-week, shown as "Data check required"). |
| Business rule | Illustrative thresholds: completeness 98% or more **and** refresh "current" = Green; completeness 90% to under 98% **or** refresh "delayed" = Amber; completeness under 90% **or** refresh "stale" = Red. Unresolved appointment statuses (booked minus completed, cancelled and no-show > 0) count against appointment-source completeness. |
| Priority | Must |
| Acceptance summary | Seeded data-quality rows (Phase 12) show the correct status; red KPIs are withheld; the banner count is correct. |
| Dependency | DR-04; DR-05; KPI-11; KPI-12; A-20 |
| Open validation question | Should Amber data be included in network totals? (Proposed: yes, with a flag.) |

### FR-09 — Executive and store-detail views
| Field | Detail |
|---|---|
| Requirement | Provide an executive-level summary view (network, region, cohort) and a store-detail view, so each audience starts from the level relevant to its decisions. |
| Related BR | BR-01, BR-06, BR-07 |
| User | ROL and SH-18 (executive view); RP, OP, RRM (store-detail view) |
| Trigger | Role-based landing page. |
| Expected behaviour | Leadership lands on the Network Overview; partners land on their own store's diagnostic page; regional managers land on the Network Overview filtered to their region. |
| Business rule | Landing page determined by role mapping (SR-01). Views share the same semantic model and definitions (no duplicate logic). |
| Priority | Should |
| Acceptance summary | Each test role lands on the correct page and scope; KPI values are identical across views for the same store-week. |
| Dependency | SR-01; FR-01; FR-14 |
| Open validation question | Do Optometry Partners want a distinct clinic-focused landing view? |

*Note:* FR-09 overlaps FR-01 and FR-14 (logged in Phase 9). It is kept as the requirement for **role-appropriate entry points**.

### FR-10 — Role-based access
| Field | Detail |
|---|---|
| Requirement | Restrict data visibility by user role and store assignment (row-level), and restrict commercial measures by role (object-level). |
| Related BR | BR-08, BR-06 |
| User | All roles; administered by ADM, approved by GOV |
| Trigger | Every report session. |
| Expected behaviour | Partners see only their own store's detailed KPIs plus anonymised peer statistics. RRMs see stores in their assigned region(s). ROL and approved Support Office analysts see the whole network. Revenue measures are hidden from roles not approved for them. |
| Business rule | Access mapping table (user → role → store or region) is maintained under access governance (SR-02, SR-06). Access is denied by default when a user has no mapping. |
| Priority | Must |
| Acceptance summary | All role test cases pass (Phase 14): no cross-store leakage through visuals, tooltips, drill-through, exports or "Analyze in Excel". |
| Dependency | SR-01 to SR-03; identity provider (assumed) |
| Open validation question | Can one person hold multiple roles (e.g., a partner in two stores)? |

### FR-11 — Approved aggregate exports
| Field | Detail |
|---|---|
| Requirement | Allow authorised roles to export **aggregated, store-week-level** tables shown in approved visuals, with a confidentiality label. |
| Related BR | BR-08, BR-12 |
| User | ROL, RRM, FUN (network or region scope); RP and OP (own store only) |
| Trigger | User selects "Export data" on an approved visual. |
| Expected behaviour | CSV or Excel export of the visual's summarised data only. Exports carry "Internal – Confidential – Aggregated data" in the file name or header. Export is disabled on visuals not on the approved list. |
| Business rule | No underlying (row-level) data export. Small-count suppression (PR-04) applies to exported values. Export events are logged (SR-04). |
| Priority | Should |
| Acceptance summary | Only approved visuals allow export; exported values match on-screen suppressed values; the export is logged. |
| Dependency | SR-04; SR-05; PR-04; tenant export settings (assumed) |
| Open validation question | Which exports replace current manual reports (BR-12)? |

### FR-12 — Persistent filter selections
| Field | Detail |
|---|---|
| Requirement | Retain a user's last filter selections between sessions and allow a reset to defaults. |
| Related BR | BR-01, BR-06 (usability) |
| User | All roles |
| Trigger | User returns to the report. |
| Expected behaviour | Previous selections are restored; a "Reset to default" option is visible; the default week still moves to the latest published week unless the user pinned a week. |
| Business rule | Persisted selections can never widen access beyond RLS scope. |
| Priority | Could (low effort if native report features are used) |
| Acceptance summary | Selections persist across sessions; reset works; the week default rule applies. |
| Dependency | Report platform capability (assumed) |
| Open validation question | Do users prefer persistence or a clean default each week? |

### FR-13 — Ramp-up trend by weeks since opening *(new)*
| Field | Detail |
|---|---|
| Requirement | For stores in the New and Developing cohorts, show the KPI trend aligned by **weeks since opening** against the peer median curve for the same age band. |
| Related BR | BR-02 |
| User | RRM, ROL, RP, OP, SH-15 |
| Trigger | User selects a store on the benchmarking page. |
| Expected behaviour | Line chart: x = weeks since opening, y = KPI (default completed exams per week, or appointment utilization); store line against peer median line and interquartile band. |
| Business rule | Peer curve uses all peer stores' values at the same weeks-since-opening (any calendar date) within the available history; age bands with fewer than the floor are hidden. Store ramp index (KPI-10) is shown as a label. |
| Priority | Must |
| Acceptance summary | Curves align on weeks since opening; sparse bands are hidden with a note; index value matches the KPI-10 definition. |
| Dependency | FR-03; KPI-10; enough history (limitation in synthetic data) |
| Open validation question | Which KPI best represents "ramp-up" for leadership? |

### FR-14 — Store appointment-to-purchase funnel *(new)*
| Field | Detail |
|---|---|
| Requirement | Show a store-level funnel for the selected period: available slots → booked → not cancelled → completed exams → purchasing customers, with stage conversion rates and peer medians. |
| Related BR | BR-03, BR-11 |
| User | RP, OP, RRM |
| Trigger | User opens the Store Diagnostic page. |
| Expected behaviour | Funnel or stepped bar with stage rates (utilization, attendance, conversion). The stage with the largest negative variance against peers is highlighted as a **candidate area to investigate**. |
| Business rule | Stage definitions per KPI-02, KPI-03, KPI-05. Unresolved appointment statuses are shown as a separate "status not recorded" segment, not hidden. |
| Priority | Must |
| Acceptance summary | Stage counts reconcile to KPI values; the unresolved segment appears where present; highlight wording is non-causal. |
| Dependency | KPI dictionary; FR-04 |
| Open validation question | Should Optometry Partners see the purchasing stage? (Linked to D-03.) |

### FR-15 — Suggested investigation areas *(new)*
| Field | Detail |
|---|---|
| Requirement | For each exception, display a rule-based suggested investigation area and typical follow-up team from a maintained prompt library. |
| Related BR | BR-09, BR-03 |
| User | RRM, ROL, RP |
| Trigger | An exception is raised (FR-06). |
| Expected behaviour | Example: "Attendance below peers → Check reminder and confirmation process, booking lead times and no-show patterns · Typical follow-up: Store team with Regional Retail Manager." |
| Business rule | Prompts use approved wording that starts with a verb such as "Check", "Review" or "Discuss". **Prohibited wording:** "caused by", "because", "due to". Prompt library is versioned and approved by SH-04 with SH-02/SH-16 input for clinical stages. |
| Priority | Must |
| Acceptance summary | Every exception shows a prompt and team; no prohibited causal terms appear (UAT text check). |
| Dependency | FR-06; A-21 |
| Open validation question | Who owns and updates the prompt library? |

### FR-16 — Small-peer-group warning and suppression *(new)*
| Field | Detail |
|---|---|
| Requirement | Apply peer-group fallback and suppression rules, and show why a peer statistic is missing or uses a broader group. |
| Related BR | BR-02, BR-08 |
| User | All roles |
| Trigger | A peer group is below the floor. |
| Expected behaviour | Warning text: "Peer group below minimum (n = 3). Comparison uses all Developing stores (n = 11)" or "Peer comparison not available." |
| Business rule | Floor set by SH-13 (illustrative 5). SH-04 may raise it, never lower it (Phase 2 decision 7). |
| Priority | Must |
| Acceptance summary | Synthetic small groups trigger the fallback and suppression correctly; the warning text states n and basis. |
| Dependency | PR-03; FR-04 |
| Open validation question | What floor does the Privacy Officer require? |

### FR-17 — Context annotations *(new)*
| Field | Detail |
|---|---|
| Requirement | Show dated annotations on trend visuals for known events (e.g., store opening, relocation, network-wide programme launches such as PC Optimum on 22 Jun 2026). |
| Related BR | BR-03, BR-05 |
| User | All roles |
| Trigger | A trend visual covers an annotated date. |
| Expected behaviour | Marker plus tooltip text: "Event recorded – not an explanation of performance." |
| Business rule | Annotations come from a governed event table; network-wide events are added by ADM after approval. |
| Priority | Could — **deferred** |
| Acceptance summary | Markers appear at the correct dates with the disclaimer. |
| Dependency | Event table ownership |
| Open validation question | Which events are useful to annotate? |

### FR-18 — Follow-up action log *(new)*
| Field | Detail |
|---|---|
| Requirement | Allow users to record follow-up owner, status and notes against an exception. |
| Related BR | BR-09, BO-04 measure |
| User | RRM, ROL |
| Trigger | A user reviews an exception. |
| Expected behaviour | A write-back or linked workflow captures owner, status and date. |
| Business rule | No patient or employee-performance notes permitted. |
| Priority | Won't (MVP) — **deferred**; pilot uses a simple manual log to measure BO-04. |
| Acceptance summary | Deferred. |
| Dependency | Workflow tooling decision |
| Open validation question | Is follow-up already tracked in another tool? |

---

## 2. MVP versus deferred

| Scope | Functional requirements | Rationale |
|---|---|---|
| **MVP (Release 1)** | FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, FR-10, FR-13, FR-14, FR-15, FR-16 | Minimum set that answers the primary decision fairly, safely and with visible data quality. |
| **MVP if low effort** | FR-09 (role landing pages), FR-11 (aggregate exports, limited to approved visuals), FR-12 (persistent filters) | Useful for adoption; can move to Release 2 without breaking the MVP decision. |
| **Deferred** | FR-17 (context annotations), FR-18 (action log) | Need event governance and workflow tooling; the pilot measures follow-up manually. |
| **Out of scope** | PC Optimum or loyalty analytics; profitability; forecasting; causal attribution | Phase 1 exclusions. |

## 3. Page mapping (preview for Phase 11 and Phase 13)

| MVP page | Primary functional requirements |
|---|---|
| 1. Network Overview | FR-01, FR-02, FR-05, FR-06 (summary), FR-08 (banner), FR-09 |
| 2. Store and Cohort Benchmarking | FR-03, FR-04, FR-13, FR-16, FR-02 |
| 3. Store Diagnostic and Data Quality | FR-14, FR-06, FR-15, FR-08, FR-07 |
| All pages | FR-07, FR-10, FR-11, FR-12 |

---

## Phase 4 close

### Decisions made
1. FR-01 to FR-12 refined from the proposed list; FR-13 to FR-18 added.
2. Default peer rule = cohort × format, with a fallback to cohort only, then suppression; illustrative floor of 5 stores.
3. Exceptions are rule-based and versioned (v0.1 illustrative); no exceptions raised on red data-quality weeks.
4. Investigation prompts use a controlled, non-causal vocabulary.
5. MVP = 13 core functional requirements plus 3 low-effort ones; FR-17 and FR-18 deferred.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-22 | A 4-week rolling window adequately smooths weekly volatility for comparison (illustrative). |
| A-23 | The report platform supports row-level and object-level security, drill-through, export controls and persistent filters (consistent with Power BI; EV-09). |
| A-24 | Users can be mapped to stores or regions from an authoritative source (e.g., HR or partner records). |

### Questions requiring validation
- U-25. Manageable exception volume per regional manager per week.
- U-26. Whether Optometry Partners should see purchase-stage metrics.
- U-27. Ownership of the investigation-prompt library.
- U-28. Whether Amber data should count in network totals.

### Recommended corrections
- None to earlier phases. Cohort boundaries and the peer floor stay illustrative until Phase 6 and SH-13 approval.
