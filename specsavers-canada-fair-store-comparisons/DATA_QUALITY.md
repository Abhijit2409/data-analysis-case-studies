# Data quality

This study has **no real source data**, so this file cannot be the usual profiling log of a published dataset. It has
three jobs instead:

1. what the synthetic dataset is checked for, and what those checks do and do not prove;
2. how data quality is **designed into the reporting** — the part that would carry over to a real build;
3. what a real implementation would have to check that **has not been checked here**, because there is no real feed.

Nothing in this file describes the quality of any Specsavers system or data.

---

## The principle

Every data-quality situation is handled by **stating a rule and applying it visibly**. Nothing is imputed, smoothed or
back-filled to make a figure look complete. Where a limit cannot be fixed, it appears on screen as a state — withheld,
provisional, suppressed, not applicable, insufficient history — instead of disappearing into a blank cell.

## 1. What the synthetic dataset is checked for

`build/validate_and_analyze.py` runs **32 checks** on every build and exits with an error if any fails. They are
structural and pattern checks on generated data, not evidence about the real world.

| Group | Checks | What they assert |
|---|---|---|
| Calendar and keys | 1–5 | 26 distinct weeks, consecutive 7-day steps, all Mondays, 30 stores, unique store × week |
| Store attributes | 6–7, 24–26 | Attributes constant per store, one region per province, generic banner values only, grocery-hosted ⇔ host banner, every store name prefixed "Synthetic - " |
| Opening and cohorts | 8–11 | No rows before opening, no missing store-weeks after opening, `weeks_since_opening = floor(days/7)`, cohort band matches age as at that week |
| Arithmetic containment | 12–16, 19 | Counts non-negative integers; completed + cancelled + no-show ≤ booked; booked ≤ slots; purchasers ≤ completed exams; orders on time ≤ orders placed; recall bookings ≤ contacts |
| Null semantics | 17–18 | Recall contacts and bookings are null together, and only where the programme is not yet active (before week 12) |
| Value ranges | 20–23 | Turnaround positive where orders exist, completeness within 0–100, refresh status from a fixed vocabulary, and a generator assumption that no weekly revenue is negative in this run (the KPI rule permits negative weeks and flags them) |
| Seeded patterns | 27–32 | The six patterns P1–P6 below are actually present |

**Reproducibility.** The whole dataset regenerates byte-identically from seed 20260913, so any figure in this package
can be recomputed exactly.

### The six seeded patterns

| Pattern | What was seeded | Why |
|---|---|---|
| P1 | New stores improving over their first weeks | Gives the ramp index something to measure |
| P2 | Elevated turnaround in the Atlantic region | Produces peer-based (rule a) fulfilment flags |
| P3 | Two stores with high demand and low attendance | Separates a booking problem from an attendance problem |
| P4 | A mature store with a conversion decline | Fires rule (b) against the store's own baseline |
| P5 | Amber and Red data-quality weeks | Exercises withholding and provisional marking |
| P6 | Cohort ordering New < Developing < Mature | Makes unfair like-for-like ranking visible if cohorts were ignored |

These patterns exist so the reporting rules have something to find. **They are not claims about how any real network
behaves**, and no finding in this package should be read as one.

## 2. How data quality is treated in the design

Each store-week carries a completeness percentage and a refresh status, which combine into one status:

| Status | Rule | Treatment | In the synthetic data |
|---|---|---|---:|
| **Green** | Completeness ≥ 98% and refresh current | Values shown normally | 752 store-weeks |
| **Amber** | Completeness 90–98%, or refresh delayed | Values shown, marked **provisional** | 5 store-weeks |
| **Red** | Completeness < 90%, or refresh stale | **Every KPI withheld** for that store-week; a data prompt replaces the values; excluded from peer groups, from the ramp index and from every exception rule | 4 store-weeks |

Completeness in the synthetic run ranges from 78.5% to 100% (median 99.3%); 4 store-weeks are delayed and 2 stale.

Three consequences are deliberate:

- **A Red week does not inherit last week's number.** The 4-week window requires the selected week to be usable, so a
  withheld week shows as withheld rather than silently reusing older data. This was a real defect, caught by testing the
  rendered page, and is now asserted by `PY_RED_01…04` and `UI-RED-01…03`.
- **A Red week cannot raise a performance flag.** Data quality must never look like a performance problem.
- **Withholding is visible in the peer group too.** A Red store-week is excluded from other stores' comparisons, not
  just from its own display.

### Small counts

| Case | Display | Synthetic count |
|---|---|---:|
| Count 1–4 | "<5", and any rate built on it is hidden | 216 weekly recall counts |
| Count 0 | 0 | 2 weekly recall counts |
| Programme not active | "Not applicable" | 42 store-weeks |
| Fewer than 3 usable weeks | "Insufficient history" | 62 four-week recall rates |

A count of 1–4 is shown as text only and never plotted at its true height, so it cannot be read back off a chart — the
first draft of the prototype did exactly that, which is why this check exists.

**This is a demonstration of a suppression rule, not a production privacy control.** Complementary suppression, so a
suppressed cell cannot be derived from a total or from the other rows, is **not implemented** and is recorded as an open
decision.

## 3. What a real implementation would have to check — and has not been checked here

None of the following has been tested, because there is no real data, no real system and no access to one. They are the
checks I would expect to design and run first:

| Area | What would have to be checked |
|---|---|
| Reconciliation | Exam counts, purchase counts and revenue against the source systems' own control totals, per store and per week |
| Cross-domain matching | How an exam is linked to a purchase across separate clinical and retail systems, and how many purchases cannot be linked at all — conversion is only as good as that link |
| Late and restated data | A provisional period for conversion and recall, and what happens to a published figure when a week is restated. This package assumes a **final** snapshot, which is a simplification, not a design |
| Appointment status | Appointments with no recorded outcome — counted against completeness, not silently treated as attended or as a no-show |
| Master data | Opening dates, store format, banner and region, which drive every cohort and peer group. A wrong opening date silently moves a store into the wrong comparison |
| Store lifecycle | Converted, relocated and rebranded stores. The synthetic data contains none, and cohort logic assumes genuine openings |
| Week boundaries and time zones | One definition of a reporting week across provinces and systems |
| Refresh latency | Actual refresh times against the Green/Amber/Red thresholds, which are illustrative proposals here |
| Duplicates and voids | Duplicate transactions, refunds, remakes and voided orders, and their effect on revenue and turnaround |
| Access controls | That row-level and object-level security actually restrict data, which the simulated role switch here does **not** demonstrate |

## 4. Known limitations of this package

- The prototype embeds the whole synthetic dataset in one HTML file; roles are simulated, not enforced.
- Data-quality thresholds (98%, 90%), the peer floor (5), the rule margins (10%, 15%) and the ramp threshold (80) are
  illustrative proposals awaiting stakeholder input, not standards.
- The Power BI model, its DAX, and its row- and object-level security design have never been executed.
- There has been no user acceptance testing, usability study, screen-reader test or accessibility audit.
- Three decisions are deliberately left open: regional visibility for a regional manager, complementary suppression, and
  whether optometry partners should see conversion.

The full issue list and its close-out status is in [`phases/issue-register.md`](phases/issue-register.md); what is
implemented, simulated, specified only or deferred is in
[`phases/feature-status-matrix.md`](phases/feature-status-matrix.md).
