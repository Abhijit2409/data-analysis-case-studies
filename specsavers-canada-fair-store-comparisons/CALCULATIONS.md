# Calculations and verification

Every figure in this package is computed by one engine, [`build/kpi_engine.py`](build/kpi_engine.py), and read back out
of its output file. Nothing is typed into a document by hand. For the figure-by-figure list, see
[`report/figures_trace.csv`](report/figures_trace.csv), which is itself generated from the analysis output by
`build/make_figures_trace.py`.

All figures below come from the **synthetic** dataset (30 fictional stores, 26 weeks ending 17 Aug 2026, seed
20260913). They demonstrate the rules and describe no real store.

---

## The rules behind the arithmetic

**1. Rates are a ratio of sums.** Every aggregate — network, region, cohort, 4-week store value — divides the summed
numerator by the summed denominator. A mean of weekly rates is never used, because it over-weights low-volume weeks.
The prototype's JavaScript recomputes these independently of Python, and the two are reconciled for every store-week ×
KPI (`JS-AGG-01…03`).

**2. Denominators are declared.** Utilization divides held appointments by available slots; attendance divides completed
exams by held appointments; conversion divides exam-linked purchasers by completed exams; on-time divides orders ready
on time by **orders placed** (a stated simplification — a production definition would likely use orders ready);
revenue per exam divides eyewear revenue by completed exams; recall-booking rate divides bookings by contacts.

**3. Every value carries a state.** No figure is shown without one of: `ok`, `red` (withheld for data quality),
`insufficient_history`, `low_volume`, `suppressed`, `not_applicable`. Zero, unavailable, suppressed and not-applicable
are four different things and never collapse into a blank or a dash.

**4. Nothing is invented.** No targets, no causes, no estimated savings, no stakeholder findings. Where the design needs
a decision that is not mine to make, it is recorded as an open question instead of being assumed away.

## Parameters

Every threshold is an illustrative proposal, declared in one place and quoted by the engine, the documents and the
prototype banner:

| Parameter | Value | Used for |
|---|---:|---|
| Peer floor | 5 | Minimum peers before a comparison is shown at all |
| Small count | 5 | Counts of 1–4 display as "<5" |
| Window | 4 weeks | Rolling measurement window |
| Minimum usable weeks | 3 | Below this: `insufficient_history` |
| Baseline | 8 weeks | Rule (b) comparison period (minimum 6 usable) |
| Rule (a) margin | 10% | Below peer P25 **and** at least this far below the peer median |
| Rule (b) change | 15% | Worsening against the store's own baseline |
| Rule (b) run | 3 weeks | Consecutive weeks before a flag is raised |
| Recall minimum contacts | 40 | Below this, recall rules do not apply |
| Ramp age range | 3–104 weeks | Eligible ages for a ramp index |
| Ramp threshold / run | 80 / 4 weeks | Index below 80 for four consecutive available weeks |

## Headline figures, week of 17 Aug 2026 (synthetic)

| Figure | Network | Atlantic region |
|---|---:|---:|
| Stores in scope | 30 | 6 |
| Completed exams | 3,496 | 545 |
| Appointment utilization | 82.4% | 81.0% |
| Attendance | 93.6% | 94.6% |
| Exam-to-purchase conversion | 57.0% | 55.8% |
| On-time fulfilment | 90.2% | 77.3% |
| Average order turnaround | 6.5 days | 9.1 days |
| Revenue per completed exam | $187 | — (role-restricted view) |
| Amber (provisional) store-weeks | 2 | 0 |

The regional column is the scope test: it is computed from the six Atlantic stores only, not filtered down from the
network figure afterwards. `PY_BASE_02` and `UI-RRM-01…03` assert these values, and the rendered-page test also asserts
that no out-of-region store name appears anywhere in the page.

## Peer statistics

```
peer group   = same cohort × same format, excluding the store itself and any Red store-week
fallback     = same cohort, all formats            (used when the first group has fewer than 5)
suppressed   = fewer than 5 peers after fallback
quantiles    = linear interpolation over the peer values
```

The prototype recomputes the peer group in JavaScript from the same raw values and is reconciled against the Python
engine for every store-week × KPI combination, including which basis was used and how many peers it held
(`JS-PEER-01`, `JS-PEER-02`).

## Exception flags

```
rule (a):  value worse than peer P25  AND  at least 10% worse than the peer median
rule (b):  4-week value at least 15% worse than the store's own 8-week baseline,
           for 3 consecutive weeks, with any unavailable week resetting the run
```

Direction is per KPI: for turnaround, "worse" means higher. Across the 26 synthetic weeks:

| Stage | Flags |
|---|---:|
| Fulfilment | 99 |
| Attendance | 43 |
| Recall | 41 |
| Conversion | 25 |
| Booking | 20 |
| **Total** | **228** |

That is 8.8 flags per week across 30 stores. By KPI, turnaround (96) and on-time (93) dominate, which is the seeded
regional turnaround pattern showing up exactly where it was planted — a check on the rules, not a finding about
fulfilment.

The stage grouping lists **every** KPI that triggered within a stage, and the run length is counted per KPI as well as
per stage (`PY_EXC_03`, `PY_EXC_04`, `UI-EXC-04`).

## Ramp index

```
ramp index = store 4-week exams per week ÷ median of same-age peers × 100
trigger    = index < 80 for 4 consecutive available weeks
```

36.5% of synthetic store-weeks have enough same-age peers for an index; the rest show why it is unavailable rather than
a blank. **No store in the synthetic data triggers the ramp prompt.** The trigger logic is covered by unit tests over
constructed frames (`PY_RAMP_01`, `PY_RAMP_02`) rather than by an example in the data.

## Suppression

| Outcome | Synthetic count |
|---|---:|
| Weekly recall counts of 1–4, shown as "<5" | 216 |
| Weekly recall counts of exactly 0, shown as 0 | 2 |
| Store-weeks where recall is not applicable | 42 |
| 4-week recall rates displayed | 606 |
| 4-week recall rates suppressed | 47 |
| 4-week recall rates with insufficient history | 62 |
| 4-week recall rates withheld (Red week) | 4 |

The five 4-week recall-rate states — displayed, suppressed, insufficient history, not applicable and withheld — sum to
761 store-weeks: every row is accounted for in exactly one state, and none is silently blank.

## How the figures were verified

**One engine.** The dashboard, the Power BI extract tables and the documents all read the same output file. There is no
second implementation of a rule that could drift.

**Python ↔ JavaScript reconciliation.** The prototype's aggregation and peer selection are recomputed in JavaScript and
compared with the Python engine for every store-week × KPI, not on a sample.

**Regression tests.** 30 Python tests over constructed frames and dataset baselines (windows, Red withholding,
suppression, peer fallback, both exception rules, run interruption, ramp persistence), 15 Node tests, and 83
rendered-page checks across four roles, three pages, five viewport widths and real key events.

**Document checks.** 21 automated checks assert that the phase documents, the deck and the README describe the
prototype as it actually behaves — versions, periods, security status, evidence wording — and that identifier families
are contiguous.

**Reproducibility.** The dataset regenerates byte-identically from seed 20260913, and the built page is compared against
its template, logic and data on every build.

The full result table, including what was **not** tested (Power BI, UAT, screen readers, real devices), is in
[`report/test-report.md`](report/test-report.md).

## Re-checking any figure yourself

1. Run `python build/validate_and_analyze.py` to rebuild `data/analysis_summary.json` from the CSV.
2. Find the figure in [`report/figures_trace.csv`](report/figures_trace.csv); the `source_key` column names the exact
   key in that file, and `guarded_by` names the test.
3. Run that test — for example `python -m unittest tests.test_calculations -k PY_BASE_02`.
4. Open `dashboard-mockup.html` and read the same figure on screen.
