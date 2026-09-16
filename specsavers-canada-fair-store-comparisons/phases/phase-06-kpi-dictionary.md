# Phase 6 — KPI Dictionary

**Status:** Drafted by the author (not stakeholder-validated) · **Prepared:** 2026-09-13 · **Dictionary version:** v0.2 (see the change log at the end; v0.1 wording is preserved there) · **Builds on:** Phases 1–5

> **Outside-in disclaimer.** These are **proposed** KPI definitions for a case study. They are **not** Specsavers' actual KPI definitions, which are unknown. All thresholds are **illustrative**. Proposed owners are hypotheses based on Phase 2 stakeholders.

**Standard conventions (apply to every KPI)**
- **Grain:** store × reporting week (Monday–Sunday), DR-06. Any higher level (region, province, cohort, network) is **re-aggregated from numerators and denominators**, never averaged from store ratios.
- **Standard dimensions:** Date/week · Store · Province · Region · Store format · Host banner · Maturity cohort (as at the week) · Weeks since opening.
- **Refresh:** weekly, published by Tuesday 12:00 PT (NFR-02), unless stated otherwise.
- **Rolling views (v0.2 clarification):** comparisons and exceptions use 4-week values (A-22) = sum(numerators) ÷ sum(denominators) over the **4 calendar weeks ending at the selected week**. A week with no record, or with Red data quality, is not usable. At least **3 usable weeks** are required, and the **selected week itself must be usable**; otherwise the value is unavailable with its reason ("data check required", "insufficient history"). A missing week is never replaced by an earlier week ("last four available records" is not used). See "Calculation conventions v0.2" below.
- **Maturity cohorts v0.1 (illustrative):** New = 0–26 weeks since opening · Developing = 27–104 · Mature = 105 or more. weeks_since_opening = floor((week_start − opening_date) ÷ 7). The "New" boundary is anchored to Specsavers' public "open less than six months" reference (EV-06); the other boundaries need validation (U-07).
- **Peer group:** cohort × format; fallback to cohort only; suppress below the floor of 5 stores (PR-03, FR-16).
- **Suppression (PR-04 demonstration rule v0.2):** counts of people or events from 1 to 4 are shown as "<5" (zero is shown as 0). A rate is shown only if its denominator is at least 5 **and**, for a count-based numerator, the numerator is not 1–4 — otherwise a visible denominator would reveal the suppressed numerator. Rates with a denominator under 5 show "n/a (low volume)"; rates with a suppressed numerator show "Suppressed (<5)". Suppressed values are never plotted at their true position. Complementary suppression is an open question (U-39), so this primary rule is **not** claimed to be sufficient for production.
- **Dataset alignment:** field names in `code` refer to the Phase 12 synthetic CSV.

---

## KPI-01 — Available appointment capacity
| Field | Definition |
|---|---|
| Business name | Available appointment capacity |
| Business purpose | Shows how much examination capacity a store offered. It is the denominator for utilization and gives context for exam volumes. |
| Formula | Σ bookable examination appointment slots scheduled in the week |
| Numerator | Count of bookable exam slots (`available_appointment_slots`) |
| Denominator | n/a (count) |
| Grain | Store-week |
| Dimensions | Standard |
| Assumed source | Scheduling system (slot templates and clinician calendars, aggregated) |
| Refresh | Weekly |
| Proposed business owner | SH-04 Retail Operations (with SH-02 input) |
| Exclusions | Slots blocked for non-exam activity (training, admin, equipment downtime); non-exam appointment types (eyewear collection, adjustments); slots on days the store was closed. |
| Data-quality rules | ≥ 0; null if the scheduling extract is missing (not 0); flag if the week-on-week change is over ±40% without a recorded closure or capacity change; must be ≥ booked appointments (see cancellations note). |
| Interpretation guidance | Capacity reflects staffing and opening hours. Low utilization with high capacity may point to demand or booking-visibility issues; high utilization may point to capacity constraints. |
| Risk of misuse | Read as clinician productivity (prohibited, PR-05); comparing stores with very different room counts without normalisation. |
| Open definition questions | Are same-day released slots counted? How are double-booked or overbooked slots represented? |

## KPI-02 — Appointment utilization
| Field | Definition |
|---|---|
| Business name | Appointment utilization |
| Business purpose | The share of offered capacity taken by appointments that were not cancelled. It shows demand relative to capacity. |
| Formula | (Booked appointments − Cancelled appointments) ÷ Available appointment slots |
| Numerator | `booked_appointments − cancelled_appointments` (held appointments: completed + no-show + status not recorded) |
| Denominator | `available_appointment_slots` |
| Grain | Store-week |
| Dimensions | Standard |
| Assumed source | Scheduling system |
| Refresh | Weekly |
| Proposed business owner | SH-04 |
| Exclusions | Non-exam appointment types; slots and appointments on closure days. |
| Data-quality rules | 0–100%; null if the denominator is null or 0; Amber if unresolved statuses exceed 2% of booked. |
| Interpretation guidance | High utilization combined with low attendance suggests reviewing reminders and no-show follow-up, not capacity. Low utilization in a New store is expected early in ramp-up; compare with cohort peers. |
| Risk of misuse | Treating 100% as ideal (no room for urgent appointments); ignoring cancellations that were refilled. |
| Open definition questions | If a cancelled slot is re-booked, is the slot counted once or twice? (This case study assumes cancellations are late and usually not re-booked in the same week, A-28.) |

## KPI-03 — Attendance rate
| Field | Definition |
|---|---|
| Business name | Attendance rate |
| Business purpose | Shows whether booked patients who kept their booking actually attended. It separates demand from attendance behaviour. |
| Formula | Completed examinations ÷ (Booked appointments − Cancelled appointments) |
| Numerator | `completed_exams` |
| Denominator | `booked_appointments − cancelled_appointments` |
| Grain | Store-week |
| Dimensions | Standard |
| Assumed source | Scheduling system (status), PMS/EMR (completion confirmation) |
| Refresh | Weekly |
| Proposed business owner | SH-04, with SH-02 consulted |
| Exclusions | Cancelled appointments (the patient gave notice); rescheduled originals (see rules). |
| Data-quality rules | 0–100%; denominator under 5 → "n/a (low volume)"; Amber if unresolved statuses (booked − completed − cancelled − no-show) exceed 2% of booked; Red above 10%. |
| Interpretation guidance | Lower attendance → **investigate** reminder process, booking lead time and local access barriers. It is not evidence of patient behaviour causes. |
| Risk of misuse | Blaming patients or staff; unresolved statuses depressing the rate (appears as low attendance when the real issue is missing data). |
| Open definition questions | Is a late cancellation (e.g., under 24 hours) treated as a no-show? (Proposed: no; tracked separately later.) |

## KPI-04 — Completed examinations
| Field | Definition |
|---|---|
| Business name | Completed examinations |
| Business purpose | A core access measure: how many eye examinations were delivered. |
| Formula | Count of examination appointments with completed status in the week |
| Numerator | `completed_exams` |
| Denominator | n/a (count) |
| Grain | Store-week |
| Dimensions | Standard (no clinician or patient attributes, PR-05) |
| Assumed source | PMS/EMR (completed exam record) reconciled to scheduling status |
| Refresh | Weekly |
| Proposed business owner | SH-16 Clinical Services / SH-02 (definition); SH-04 (use) |
| Exclusions | Non-exam visits (eyewear pickup, adjustment, repairs); test or training records; exams voided in PMS. |
| Data-quality rules | ≥ 0; ≤ booked − cancelled; reconcile within ±0.5% of PMS control totals (DR-08); null if the PMS extract is missing. |
| Interpretation guidance | Compare with peers at the same maturity. Read together with capacity and utilization. |
| Risk of misuse | Used as a clinician productivity target (prohibited); compared across stores with different capacity without context. |
| Open definition questions | Which exam types are included (comprehensive, contact-lens, follow-up, children's)? Are exams counted by appointment date or completion date? |

## KPI-05 — Exam-to-purchase conversion
| Field | Definition |
|---|---|
| Business name | Exam-to-purchase conversion |
| Business purpose | Shows how often a completed examination is followed by an eyewear purchase at the same store. It connects the clinical and retail journey stages. |
| Formula | Exam-linked purchasing customers ÷ Completed examinations |
| Numerator | `purchasing_customers`: **distinct customers** with a completed exam in the week who made an eligible eyewear purchase at the same store within an attribution window of **30 days** (illustrative), attributed to the **exam week** |
| Denominator | `completed_exams` |
| Grain | Store-week (exam week) |
| Dimensions | Standard |
| Assumed source | PMS/EMR (exam) + POS (purchase), linked **upstream in a restricted zone**; only aggregates leave (PR-01) |
| Refresh | Weekly. **The latest 4 weeks are provisional** until the 30-day window closes. |
| Proposed business owner | SH-04, with SH-02 and SH-07 consulted (definition sensitivity D-03) |
| Exclusions | Purchases without a linked exam (external prescriptions); non-eyewear items; fully refunded purchases within the window; staff purchases. |
| Data-quality rules | 0–100% (numerator ≤ denominator); denominator under 5 → n/a; Amber if the linkage match rate falls below the agreed threshold (e.g., 95%); provisional weeks shown with a marker. |
| Interpretation guidance | A decline in a mature store → **review** product range availability, pricing communication, benefits and coverage explanation, and hand-off from exam to eyewear selection. Customers may legitimately choose not to purchase. |
| Risk of misuse | **Implying sales pressure on clinical care** (D-03); comparing final weeks with provisional weeks; counting transactions instead of customers. |
| Open definition questions | Attribution window length; whether purchases at another Specsavers store count; whether contact-lens purchases count; whether Optometry Partners should see this KPI. |

## KPI-06 — Revenue per completed exam
| Field | Definition |
|---|---|
| Business name | Revenue per completed exam |
| Business purpose | Commercial intensity relative to clinical activity. It helps interpret store revenue in the context of exam volume. |
| Formula | Net eligible eyewear revenue ÷ Completed examinations |
| Numerator | `eyewear_revenue`: net eligible eyewear revenue recognised at the store in the week (CAD, excluding sales taxes), **after returns and refunds processed in the week** |
| Denominator | `completed_exams` |
| Grain | Store-week |
| Dimensions | Standard |
| Assumed source | POS (sales, returns); Finance system (control totals) |
| Refresh | Weekly |
| Proposed business owner | SH-07 Finance |
| Exclusions | Sales taxes; non-eyewear items; gift-card sales (recognised on redemption); staff purchases. Treatment of third-party insurer or benefit payments and loyalty redemptions is an **open question**. |
| Data-quality rules | Denominator under 5 → n/a; numerator can be negative in a week with high returns (flag, not an error); reconcile within ±1% of finance control totals (DR-08); **role-restricted** (SR-03). *v0.2 note:* the synthetic generator happens to produce no negative weeks; the validation check "no negative weekly net revenue" is a **generator assumption for this run**, not a business-data rule. The calculation accepts negative weeks (test PY-DEF-02). |
| Interpretation guidance | Revenue is **not** exam-linked in MVP: stores with many external-prescription customers show a higher ratio. Use as context, not as a primary exception driver. |
| Risk of misuse | Read as profitability (it isn't); used to pressure clinical staff; exposed to unapproved roles. |
| Open definition questions | Should the numerator be exam-linked revenue only? Include contact lenses? How should insurer direct-billing and PC Optimum redemptions be treated? |

## KPI-07 — Average order turnaround
| Field | Definition |
|---|---|
| Business name | Average order turnaround (days) |
| Business purpose | Speed of getting eyewear to customers. It is a customer-experience and supply-chain indicator. |
| Formula | Σ (ready-for-collection date − order placed date, in calendar days) ÷ Count of orders that reached "ready" |
| Numerator | Total turnaround days for orders **placed in the week** that have reached "ready" |
| Denominator | Count of those orders |
| Grain | Store-week (order-placed week) |
| Dimensions | Standard |
| Assumed source | Order-management system |
| Refresh | Weekly. Order cohorts remain **provisional for 21 days** (illustrative) until most orders close. |
| Proposed business owner | SH-06 Supply Chain |
| Exclusions | Cancelled orders; warranty and repair orders (reported separately later); remakes counted as a new order linked to the original (turnaround measured from the original placement, illustrative). |
| Data-quality rules | ≥ 0; ready date ≥ placed date; flag turnaround over 60 days as a possible data error; `average_turnaround_days` in the dataset is this measure. *v0.2 note — synthetic simplification:* the CSV has no count of orders that reached "ready", so the prototype assumes **every order placed reached ready** and weights turnaround by `orders_placed` (Σ turnaround × orders placed ÷ Σ orders placed). This is not production-correct: a production model needs `orders_ready` and `total_turnaround_days` (Phase 7, FACT_ORDER_FULFILMENT) and must treat orders not yet ready as provisional (test PY-DEF-01). |
| Interpretation guidance | Elevated turnaround shared across a region → **review** logistics and lab routing with Supply Chain; isolated to one store → **review** order-entry accuracy and remakes with the store. |
| Risk of misuse | Averages hide long tails (consider a median in a later release); comparing provisional weeks with final weeks. |
| Open definition questions | Calendar or business days? Does the promised date vary by lens type? Measure from placement to "ready" or to "collected"? |

## KPI-08 — On-time fulfilment rate
| Field | Definition |
|---|---|
| Business name | On-time fulfilment rate |
| Business purpose | Reliability against the promise made to the customer. |
| Formula | Orders ready on or before the promised date ÷ Orders placed |
| Numerator | `orders_ready_on_time` |
| Denominator | `orders_placed` (excluding cancelled orders) |
| Grain | Store-week (order-placed week) |
| Dimensions | Standard |
| Assumed source | Order-management system |
| Refresh | Weekly; provisional for 21 days |
| Proposed business owner | SH-06 Supply Chain |
| Exclusions | Cancelled orders; orders without a promised date (counted in data quality, not silently excluded). |
| Data-quality rules | 0–100%; numerator ≤ denominator; Amber if over 2% of orders lack a promised date. |
| Interpretation guidance | Use with KPI-07. A promised date set too generously can make the rate look better than turnaround suggests. |
| Risk of misuse | Stores changing promised dates to improve the rate; blaming stores for regional supply delays (D-06). |
| Open definition questions | Who sets the promised date, and is it standardised by product type? |

## KPI-09 — Recall-booking rate
| Field | Definition |
|---|---|
| Business name | Recall-booking rate |
| Business purpose | Effectiveness of patient recall in bringing patients back for examinations. It is an access indicator. |
| Formula | Recall bookings ÷ Recall contacts |
| Numerator | `recall_bookings`: distinct recalled patients who booked an exam within **30 days** (illustrative) of contact, attributed to the **contact week** |
| Denominator | `recall_contacts`: distinct patients sent a deliverable recall contact in the week |
| Grain | Store-week (contact week) |
| Dimensions | Standard, plus channel (future release) |
| Assumed source | Marketing/recall platform (contacts) + scheduling system (bookings), linked upstream (PR-01) |
| Refresh | Weekly; the latest 4 weeks provisional |
| Proposed business owner | SH-05 Marketing |
| Exclusions | Undeliverable contacts; patients who opted out; bookings made before the contact. |
| Data-quality rules | Numerator ≤ denominator; counts under 5 → "<5" and rate n/a (PR-04). New stores often have few or no recall-eligible patients, so **null** (no programme) is distinct from **0** (contacts sent, no bookings). |
| Interpretation guidance | Most meaningful for Developing and Mature stores with an established patient base. *v0.2 note:* the **exception rule set v0.2** (a separate versioned artefact, Phase 13 §4) only evaluates recall exceptions for Developing and Mature stores with **40 or more recall contacts** in the 4-week window. The KPI itself is still shown for other stores. |
| Risk of misuse | Crediting all bookings to recall; comparing New stores with no recall base against Mature stores. |
| Open definition questions | Attribution window; multi-contact sequences; whether a booking is later completed. |

## KPI-10 — Store ramp index
| Field | Definition |
|---|---|
| Business name | Store ramp index (completed examinations) |
| Business purpose | Shows whether a New or Developing store is ramping up in line with stores at the **same age**, regardless of calendar date. |
| Formula | 100 × Store's 4-week rolling average completed exams per week at weeks-since-opening *w* ÷ Median of peer stores' 4-week rolling average completed exams at the same weeks-since-opening *w* |
| Numerator | Store 4-week rolling average of `completed_exams` at age *w* |
| Denominator | Median of the same measure across peer stores observed at age *w* (any calendar week, within available history) |
| Grain | Store-week (for stores with weeks since opening of 104 or fewer) |
| Dimensions | Store, format, province, region, cohort, weeks since opening |
| Assumed source | Derived from KPI-04 and the store master |
| Refresh | Weekly |
| Proposed business owner | SH-04, with SH-15 consulted |
| Exclusions | Mature stores (use cohort variance instead); stores with an unclassified opening date; weeks with Red data quality (for the store and for peers). |
| Data-quality rules | Peer n at age *w* must be at least 5 (format peers, then fallback to all formats); otherwise index = n/a with a warning; the first 3 weeks after opening are n/a (incomplete rolling window). |
| Interpretation guidance | 100 = in line with the peer median at the same age; 80 = 20% below. A sustained index under 80 for 4 or more weeks → **discuss** local marketing, booking visibility and capacity with the store and Business Development (illustrative threshold). |
| Risk of misuse | Treated as a performance score for partners (D-09); stores with structurally smaller capacity always appear low. A capacity-normalised variant (completed exams per 100 available slots) is an open option. |
| Open definition questions | Is completed exams the right ramp measure, or should it be capacity-normalised or composite? Should peers be restricted to the same province? |

## KPI-11 — Data completeness
| Field | Definition |
|---|---|
| Business name | Data completeness |
| Business purpose | Tells users whether a store-week's data is complete enough to trust. |
| Formula | **v0.2 (one method chosen):** mean of per-source completeness across the sources expected for the store-week, each source weighted equally: completeness = (1 ÷ S) × Σₛ (received recordsₛ ÷ expected recordsₛ), capped at 100% per source. *Worked example (illustrative):* scheduling 480/500 = 96%, PMS/EMR 300/300 = 100%, POS 190/200 = 95%, order management 210/210 = 100%, recall 50/50 = 100% → (96 + 100 + 95 + 100 + 100) ÷ 5 = **98.2%** (Green). The pooled alternative Σ received ÷ Σ expected = 1,230/1,260 = 97.6% (Amber) would let high-volume sources dominate, which is why it is **not** used. |
| Numerator | Per source: records received for the store-week (including resolved appointment statuses) |
| Denominator | Per source: records expected (from store calendar, prior patterns and control totals); sources not expected for the store are excluded from S |
| Grain | Store-week-source (model); store-week (display, `data_completeness_pct`) |
| Dimensions | Store, week, source |
| Assumed source | Pipeline load metadata and data-quality rule results (A-20) |
| Refresh | Every refresh |
| Proposed business owner | SH-13 (governance), SH-10 (operational) |
| Exclusions | Sources not applicable to a store (e.g., recall platform for a store without a recall programme = not expected). |
| Data-quality rules | 0–100%; Green ≥ 98% · Amber 90% to under 98% · Red < 90% (DR-04). |
| Interpretation guidance | Check before acting on any exception. Red withholds KPIs (FR-08). |
| Risk of misuse | Treated as a store performance measure (it measures the data pipeline, not the store). |
| Open definition questions | How are "expected records" estimated reliably for new stores with no history? *Prototype note:* `data_completeness_pct` in the synthetic CSV is **simulated directly**; it is not reconstructed from per-source load metadata. |

## KPI-12 — Data freshness
| Field | Definition |
|---|---|
| Business name | Data freshness |
| Business purpose | Tells users whether the most recent data has arrived on time. |
| Formula | Status per store-week: **Current** if every source loaded within 48 hours before refresh and covers the full week; **Delayed** if any source is over 48 hours to 7 days late; **Stale** if any source is over 7 days late or the week is not covered (DR-05). Also shown as hours since last successful load. |
| Numerator / Denominator | n/a (status); optional % of stores Current |
| Grain | Store-week-source (model); store-week (display, `data_refresh_status`) |
| Dimensions | Store, week, source |
| Assumed source | Pipeline load metadata |
| Refresh | Every refresh |
| Proposed business owner | SH-10 (operational), SH-13 |
| Exclusions | Sources not expected for the store. |
| Data-quality rules | Worst source status determines the store-week status. |
| Interpretation guidance | Delayed → treat KPIs as provisional. Stale → KPIs withheld. |
| Risk of misuse | Hiding late data by reusing the prior week's values (prohibited; show null and status instead). |
| Open definition questions | Should freshness thresholds differ by source? |

---

## Cross-cutting definition rules

| Topic | Rule (v0.1, illustrative) | KPIs affected |
|---|---|---|
| **Cancellations** | A cancelled appointment is counted in `booked_appointments` and in `cancelled_appointments`. It is excluded from the utilization numerator and the attendance denominator, because the patient gave notice and the slot was released. | KPI-02, KPI-03 |
| **No-shows** | A booked, non-cancelled appointment the patient did not attend. It stays in the attendance denominator and the utilization numerator (the slot was held). | KPI-02, KPI-03 |
| **Rescheduled appointments** | The original appointment is **not** counted as booked or cancelled. The rebooked appointment is counted once, in the week of its final scheduled date. The dataset has **no rescheduled column**; rescheduling is resolved upstream (A-29). | KPI-02, KPI-03, KPI-04 |
| **Status not recorded** | booked − (completed + cancelled + no-show) = unresolved. Shown explicitly and counted against completeness. Never silently treated as completed or no-show. | KPI-02, KPI-03, KPI-11 |
| **Arithmetic invariant** | completed + cancelled + no-show ≤ booked ≤ available slots; purchasing customers ≤ completed exams; orders ready on time ≤ orders placed; recall bookings ≤ recall contacts. | All volume KPIs |
| **Customers versus transactions** | Conversion counts **distinct customers**, not transactions or items. A customer buying two pairs counts once. Revenue counts all eligible transactions. | KPI-05, KPI-06 |
| **Eligible revenue** | Frames, prescription lenses and prescription sunglasses; net of discounts; excluding sales tax, gift-card sales and staff purchases. Contact lenses excluded in v0.1 (open question). | KPI-06 |
| **Returns and refunds** | Deducted in the **week processed** (revenue), which can make weekly revenue negative. For conversion, a purchase fully refunded within the attribution window is excluded. | KPI-05, KPI-06 |
| **Small peer groups** | Peer floor 5 stores (PR-03); fallback cohort × format → cohort; else suppress with an explanation (FR-16). | KPI comparisons, KPI-10 |
| **Small counts** | *v0.2:* counts 1–4 shown as "<5"; zero shown as 0. Rates hidden when the denominator is under 5 ("n/a (low volume)") **or** a count-based numerator is 1–4 ("Suppressed (<5)"). Applied at the displayed aggregation in cards, tables, charts, tooltips and data tables (PR-04). | KPI-02, KPI-03, KPI-05, KPI-08, KPI-09 |
| **Rolling window** *(v0.2)* | 4 calendar weeks ending at the selected week; minimum 3 usable weeks; the selected week must be usable. Rule (b) baseline: the 8 calendar weeks immediately before the window, minimum 6 usable weeks. | All rate KPIs, KPI-10 |
| **Red selected week** *(v0.2)* | All KPI values for that store-week are unavailable ("Data check required"); no exception or prompt; the store-week is excluded from other stores' peer groups and ramp peers; earlier valid weeks are unaffected. | All |
| **Consecutive weeks** *(v0.2)* | Counted per KPI over consecutive calendar weeks; any week where the KPI is unavailable (including Red) resets the run. A stage flag reports the longest current run among its triggering KPIs. Ramp trigger: index below 80 in 4 consecutive weeks with an available index. | FR-06, KPI-10 |
| **Store maturity** | Derived as at each week from opening date (DR-10); New 0–26 · Developing 27–104 · Mature 105+ weeks; "Unclassified" if opening date is invalid. | All (dimension), KPI-10 |
| **Missing data** | Missing source records → **null** with a data-quality reason; never zero; never carried forward from a prior week. | All |
| **Zero versus null** | **Zero** = source confirms no activity (e.g., recall contacts sent = 0 because no eligible patients). **Null** = data not received or not applicable. Rates with a zero denominator are null ("n/a"), not 0%. | All |
| **Provisional periods** | KPIs with attribution or fulfilment windows are marked provisional for the window length (conversion and recall 4 weeks; fulfilment 21 days). Production separates three dates: the **reporting week** (Mon–Sun), the **refresh time** (e.g., Tuesday 12:00 PT, NFR-02) and the **attribution completion date** (reporting week end + window). *Prototype (v0.2 note):* the synthetic dataset is a **finalised snapshot** — every week, including the latest four, is treated as final, and the dashboard says so in its banner. Amber data quality in the window is marked provisional separately. | KPI-05, KPI-07, KPI-08, KPI-09 |

## KPI-to-decision map

| KPI | Primary decision supported | Journey stage | Follow-up team (typical) |
|---|---|---|---|
| KPI-01 | Is capacity constraining or exceeding demand? | Capacity | Store and Retail Operations |
| KPI-02 | Is demand filling capacity compared with peers? | Booking | Store, RRM, Marketing |
| KPI-03 | Are booked patients attending? | Attendance | Store, RRM |
| KPI-04 | Is access growing in line with peers? | Examination | Store, RRM, Clinical Services |
| KPI-05 | Is the exam-to-eyewear hand-off working? | Conversion | Store, RRM |
| KPI-06 | Is commercial intensity in line with peers? (context) | Conversion / revenue | RRM, Finance |
| KPI-07 | Are orders delayed, and where? | Fulfilment | Supply Chain, store |
| KPI-08 | Are promises to customers met? | Fulfilment | Supply Chain, store |
| KPI-09 | Is recall bringing patients back? | Recall | Marketing, store |
| KPI-10 | Is this new store ramping like its peers? | Overall ramp-up | RRM, Business Development |
| KPI-11 | Is the data complete enough to act on? | Data trust | Data team |
| KPI-12 | Is the data current enough to act on? | Data trust | Data team |

---

## Phase 6 close

### Decisions made
1. 12 KPIs defined (KPI-01 to KPI-12), v0.1 draft, all aligned to Phase 12 dataset fields.
2. Utilization = held appointments ÷ slots; attendance = completed ÷ held; cancellations are excluded from held appointments, no-shows are included.
3. Conversion = **distinct exam-linked customers** within 30 days; linkage happens upstream in a restricted zone.
4. Revenue per completed exam is **not exam-linked** in MVP and is context-only, role-restricted, and not an exception driver.
5. Ramp index is age-aligned (weeks since opening), for New and Developing stores only, with a peer floor of 5.
6. Zero, null, provisional and suppressed values are all distinct states.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-28 | Cancelled slots are rarely re-booked in the same week, so booked ≤ available slots holds for reporting. |
| A-29 | Rescheduling is resolved upstream so each appointment is counted once, at its final date. |
| A-30 | A 30-day attribution window is reasonable for conversion and recall (illustrative). |
| A-31 | Exam-to-purchase linkage can be performed upstream under appropriate custody without exposing identifiers. |

### Questions requiring validation
- U-33. Exam types in scope, and whether counts are by appointment date or completion date.
- U-34. Attribution windows for conversion and recall.
- U-35. Treatment of contact lenses, insurer direct billing and loyalty redemptions in revenue.
- U-36. Promised-date standards for fulfilment.
- U-37. Whether the ramp index should be capacity-normalised.

### Recommended corrections
- None to earlier phases. Utilization and attendance rules supersede the informal "utilization" wording in Phase 4 FR-14 (same meaning, now precisely defined).

---

## Change log

| Version | Date | Change | Reason | Issue |
|---|---|---|---|---|
| v0.1 | 2026-09-13 | First draft (12 KPIs) | Phase 6 | — |
| v0.2 | 2026-09-13 (repair pass) | Rolling-window wording clarified: calendar weeks, minimum 3 usable weeks, selected week must be usable. *v0.1 text:* "comparisons and exceptions use 4-week rolling values (A-22) = sum(numerators over 4 weeks) ÷ sum(denominators over 4 weeks)." | The prototype produced values for Red weeks from preceding weeks | ISS-05, ISS-06 |
| v0.2 | 2026-09-13 | Suppression rule extended to rates with a suppressed numerator. *v0.1 text:* "counts under 5 are shown as "<5"; rates with a denominator under 5 are shown as "n/a (low volume)"." | A visible denominator plus a rate disclosed the suppressed count | ISS-07, ISS-08 |
| v0.2 | 2026-09-13 | KPI-11 formula: one method (equal-weighted mean of per-source completeness) with a worked example. *v0.1 text* combined "weighted equally by source" with "Σ received ÷ Σ expected" | Two different calculations | ISS-26 |
| v0.2 | 2026-09-13 | KPI-07 synthetic simplification stated (all placed orders reach ready) | Denominator mismatch between dictionary and analysis | ISS-27 |
| v0.2 | 2026-09-13 | KPI-06: negative weeks remain valid; "no negative revenue" is a generator assumption | Validator check read as a business rule | ISS-28 |
| v0.2 | 2026-09-13 | KPI-09: note referencing the exception rule set v0.2 recall parameter (the parameter belongs to the rule set, not the dictionary) | Version conflict between documents | ISS-36 |
| v0.2 | 2026-09-13 | Cross-cutting rows added: rolling window, Red selected week, consecutive weeks; provisional-period row separates reporting week, refresh and attribution completion and states the finalised-snapshot assumption | Behaviour now tested | ISS-12, ISS-29 |

*No KPI IDs, names or core formulas (other than the KPI-11 method choice) changed between v0.1 and v0.2.*
