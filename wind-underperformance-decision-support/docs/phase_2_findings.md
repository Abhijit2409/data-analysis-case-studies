# Phase 2 findings

Transparent baseline. Completed 30 September 2026.

Every number comes from a script in `src/` and a table in `outputs/tables/`. The
machine-learning challenger has not been built. No memo, slides or application
has been written.

**Phase 2 question:** what potential underperformance remains after applying
transparent data-quality rules, and how sensitive is the result to the
assumptions an event-code-free dataset forces on you?

---

## 1. Did P-11 pass?

**Yes. All nine checks passed** (`timestamp_correction_validation.csv`).

The hypothesis was that the logger's clock never followed daylight saving, and
that the `+02:00` summer offset was written on afterwards. The correction reads
every wall-clock value as a fixed UTC+1 clock.

| Check | Result |
|---|---|
| Raw archive unchanged since Phase 1 (sha256) | PASS |
| Row count still 420,480 | PASS |
| Corrected timestamps unique per turbine | PASS — 0 duplicates, was 48 |
| Spring duplicates resolved without discarding anything | PASS |
| Autumn gaps removed | PASS — 48 absent intervals became 0 |
| No new discontinuity | PASS — **0 absent intervals; the sequence is now complete** |
| Seasonal lag difference removed | PASS — **−1 h became 0 h** |
| Energy conserved across relabelling | PASS — 24,630 MWh, difference 0.00 kWh |
| Monthly energy change within the month-boundary effect | PASS — largest shift 0.339% |

Two results are worth more than the pass marks:

- **The corrected sequence is perfect.** Every turbine now has exactly 105,120
  ten-minute records with no duplicate and no hole. Under the published
  timestamps each turbine had 12 duplicates and 12 gaps. Nothing was added or
  removed to achieve this; only the labels changed.
- **Summer correlation against ERA5 improved on its own** (0.887 → 0.903). That
  was not a target of the correction, which makes it useful corroboration.

**The spring collision repair.** The simple rule cannot separate the two copies of
the collided hour, because both carry the same wall-clock text. Each pair is split
by continuity of wind speed: whichever copy joins more smoothly onto the preceding
hour is moved back. The decision table shows the first copy moved in 3 cases and
the second in 5, so **file order would have been the wrong rule** — a useful check
on an assumption that would have been easy to make.

Two of those eight decisions are close (seam gaps 1.33 vs 1.04, and 0.38 vs 0.16
m/s). A wrong choice there misplaces six records by one hour inside a two-hour
window and changes no energy total, so the residual risk is small.

## 2. What timestamp is used, and why?

`timestamp_corrected_utc`, for everything.

All three columns are kept in the processed file — `timestamp_raw`,
`timestamp_published_utc`, `timestamp_corrected_utc` — so the correction can be
inspected or undone. Because P-11 passed, ERA5 air density could be joined to
SCADA (P-09). Under the published timestamps that join would have been an hour out
for roughly seven months of each year.

## 3. How many observations are reference-eligible?

**336,928 of 420,480 (80.13%).** By turbine and year, eligibility runs from 77.7%
to 83.3% — no turbine is an outlier on availability of usable data.

"Reference-eligible" means only that a record passed the data-quality rules. It
does **not** mean the turbine was operating correctly. Without event logs that
cannot be known, which is why this document never uses the word "healthy".

## 4. What was excluded, and why?

From `cleaning_reconciliation.csv`. Reasons overlap, so they do not sum to the
total.

| Exclusion reason | Records | Share of raw |
|---|---|---|
| Zero or negative power | 80,983 | 19.26% |
| Frozen wind sensor (6+ identical readings) | 4,609 | 1.10% |
| Missing power | 2,569 | 0.61% |
| Missing wind | 2,569 | 0.61% |
| Invalid temperature | 2,569 | 0.61% |
| Invalid pitch | 43 | 0.01% |
| Power above rated +10% | 0 | 0.00% |
| Wind outside 0–30 m/s | 0 | 0.00% |

**Excluded in total: 83,552 records (19.87%).** The overwhelming majority is
zero-or-negative power, which is deliberate: those records are excluded from
*fitting* the curve and kept in full as investigation candidates.

**Correction (made in Phase 3 reconciliation).** An earlier version of this table
gave 77,431 for zero-or-negative power. That figure is the **auxiliary-consumption
warning** count — records between −50 and 0 kW, where an idle turbine draws power
for its own systems. The exclusion count is **80,983**: 77,431 negative plus 3,552
at exactly zero. Source: `cleaning_reconciliation.csv`.

Nothing was deleted. Every one of the 420,480 raw rows is in
`data/processed/scada_processed.parquet` with its reasons attached. Ten validation
checks confirm this, including that **no missing observation was turned into a
zero** — the rule that would most easily manufacture false downtime.

## 5. What operating threshold was selected?

**4.5 m/s**, from evidence rather than convention.

Every turbine first reaches at least 95% of records producing in the **4.0 m/s**
bin (range across turbines 0.966 to 0.984). The working threshold is set one bin
higher so it sits inside the region where production is consistent rather than on
its edge.

Phase 1 used 4.0 m/s as a guess. The measured answer is close to it, which is
reassuring but was not knowable in advance.

## 6. Are 2014 and 2015 comparable?

**No, not closely — and this is the most important caveat in Phase 2.**

| Measure | 2014 | 2015 | Change |
|---|---|---|---|
| ERA5 mean wind | 5.780 m/s | 6.042 m/s | **+4.53%** |
| ERA5 mean cubed wind | 324.2 | 367.4 | **+13.33%** |
| ERA5 90th percentile | 9.265 m/s | 9.758 m/s | +5.32% |
| SCADA mean wind (valid records) | 5.357 m/s | 5.660 m/s | +5.66% |

By quarter the difference is uneven: Q1 was 4.2% *weaker* in 2015, while Q3 was
15.3% stronger and Q4 8.8% stronger.

**Does this invalidate the split? No, but it constrains what may be claimed.** The
reference curve maps wind speed to expected power, so it is conditioned on wind:
a windier year produces more energy and more expected energy together. What would
be invalid is comparing raw annual energy between the years and calling the
difference performance. This analysis does not do that.

The real residual risk is subtler. 2015 spent more time in high-wind bins, where
the 2014 curve has fewer reference records, so the estimate leans harder on the
thinnest part of the curve.

## 7. How well does the baseline reproduce reference observations?

From `baseline_bias_summary.csv`, on fitted bins only (the defined-zero low-wind
bins are not a fit and would measure something else):

| Scope | Records | Median residual | Mean residual | Mean as % of rated |
|---|---|---|---|---|
| All turbines | 140,417 | 0.00 kW | +0.75 kW | 0.037% |
| R80711 | 42,699 | 0.00 kW | +1.10 kW | 0.054% |
| R80721 | 40,796 | 0.00 kW | +0.29 kW | 0.014% |
| R80736 | 41,154 | 0.00 kW | +1.12 kW | 0.055% |
| R80790 | 41,792 | 0.00 kW | +0.49 kW | 0.024% |

**Why 140,417 and not 166,726.** Those are three different populations, and the
distinction matters:

| Population | Records |
|---|---|
| Reference-eligible 2014 records | 166,726 |
| ...in `fitted_median` bins — **the only ones that test the fit** | **140,417** |
| ...in `defined_zero_below_threshold` bins (a definition, not a fit) | 26,136 |
| ...in `unsupported` bins (no curve value exists) | 173 |

140,417 + 26,136 + 173 = 166,726. The bias check uses only the fitted bins,
because including bins whose value was defined as zero rather than estimated would
measure the definition, not the fit. An earlier version of this table reported
166,441, which came from a run before that filter was added.

**A median residual of exactly zero proves almost nothing.** The curve is a median
of each bin, so the median residual must be near zero — this is an arithmetic
check that the code does what it says, not evidence the curve is physically
right. The mean residual is the more informative figure: at under 0.06% of rated
power it shows the distribution inside each bin is close to symmetric, with no
large skew being hidden.

The curve covers **75 fitted bins**, plus 36 defined-zero bins below the operating
threshold, with **22 bins left unsupported** and deliberately empty rather than
interpolated.

## 8. How much potential lost energy in 2015?

**672 MWh**, against 13,410 MWh produced — **4.77%** of the two combined.

But the single figure is the least useful part of the answer:

**Four quantities, kept separate** (`energy_accounting.csv`). None is recoverable
energy:

| Quantity | Value | What it means |
|---|---|---|
| Gross positive residual shortfall | **671.6 MWh** | Total gap against a statistical reference |
| Shortfall inside persistent candidate events | **380.8 MWh** | The part that forms reviewable events |
| Non-persistent shortfall | **290.8 MWh** | Short dips failing the one-hour rule |
| Unmeasured energy from missing data | **unknown** | 2,074 records. Unknown, not zero. |
| Records not assessable | 2,771 records | No expected value exists |

**Only 381 MWh (57%) sits inside identifiable candidate events.** The other 291 MWh
is scattered across thousands of short dips. That residue is as likely to be
turbulence, sensor noise and curve approximation as anything operational.

**Correction (Phase 3 reconciliation): the label was wrong.** That 291 MWh was
originally filed under `within_reference_expectation`, which was misleading —
these records have a genuine positive shortfall and simply failed the persistence
test. Calling them "within expectation" hid energy inside a label saying nothing
was wrong. The category is now split:

| Category | Records | Share of 2015 |
|---|---|---|
| `at_or_above_reference` | 136,842 | 65.09% |
| `nonpersistent_shortfall` | 45,439 | **21.61%** |
| `operating_below_reference_candidate` | 20,515 | 9.76% |
| `not_assessable_due_to_data_quality` | 2,771 | 1.32% |
| `idle_in_apparently_usable_wind` | 2,575 | 1.22% |
| `unmeasured_due_to_missing_data` | 2,074 | 0.99% |
| `site_wide_low_or_zero_production` | 24 | 0.01% |

**Complete candidate-event breakdown — 2,688 events:**

| Class | Events | Records | Hours | Potential MWh |
|---|---|---|---|---|
| `operating_below_reference_candidate` | 2,239 | 20,515 | 3,419.9 | 223.4 |
| `idle_in_apparently_usable_wind` | 434 | 2,575 | 429.8 | 156.4 |
| `site_wide_low_or_zero_production` | 15 | 24 | 4.0 | 1.1 |
| **Total** | **2,688** | **23,114** | **3,853.7** | **380.8** |

An earlier version omitted the site-wide row.

## 9. What range comes from the sensitivities?

From `potential_loss_sensitivity.csv`:

| Specification | Total potential lost (MWh) | Below-reference attributed (MWh) |
|---|---|---|
| Curve quantile 0.40 | **538** | 138 |
| Frozen-wind 3 records | 672 | 223 |
| **Primary** (frozen 6, persistence 6, median) | **672** | **223** |
| Frozen-wind 12 records | 672 | 223 |
| Persistence 3 records | 672 | 374 |
| Persistence 12 records | 672 | 89 |
| Curve quantile 0.60 | **834** | 353 |

**Range: 538 to 834 MWh.** Illustrative value at €40–80/MWh: **€21,500 to
€66,700**. *Illustrative value-at-risk sensitivity — not actual revenue.*

Which assumption drives what:

- **The curve quantile drives the total.** Moving from the 40th to the 60th
  percentile changes the answer by ±22%. This is the choice that matters, and it
  is unavoidably a judgement: there is no measurement that says which percentile
  represents expected behaviour.
- **Persistence drives attribution, not the total.** At 3 records, 374 MWh is
  attributed to below-reference events; at 12 records, 89 MWh. The total never
  moves, because persistence only decides which records get named as candidates.
- **The frozen-wind threshold barely matters at all.** Between 3 and 12 records
  the total moves by 0.03 MWh. Phase 1 flagged this as a judgement needing a
  sensitivity test; the test shows it does not matter here.

## 10. Which turbine and period first?

**R80790.**

| Turbine | Actual MWh | Potential lost MWh | Lost as % of potential |
|---|---|---|---|
| R80711 | 3,803 | 173 | 4.36% |
| R80721 | 2,955 | 130 | 4.22% |
| R80736 | 3,210 | 143 | 4.25% |
| **R80790** | 3,442 | **226** | **6.15%** |

Three turbines sit within 4.2–4.4%. R80790 is at 6.15%, and leads on both
components: most below-reference energy (90 MWh) and most idle-in-wind energy (57
MWh over 173 hours).

The two largest single events are elsewhere, and both are long idle periods:

| Turbine | Start (UTC) | Duration | Potential MWh | Evidence | Confidence |
|---|---|---|---|---|---|
| R80711 | 2015-07-26 09:30 | 47.2 h | 37.5 | Peer context | Medium |
| R80790 | 2015-02-07 11:00 | 40.0 h | 29.7 | Peer context | Medium |

Both are consistent with a turbine being out of service for around two days while
the others ran. **That is a description, not a diagnosis.** A scheduled service
visit, a fault and a grid restriction would all look like this.

**Recommended first investigation:** R80790's below-reference pattern, because it
is persistent rather than a single outage and it is the only turbine standing
apart from its peers. The evidence needed to take it further — event logs, work
orders, curtailment records — does not exist in this dataset.

> **Superseded by Phase 3.** Under a fleet-pooled reference, R80790's shortfall
> falls to 5.10% and **R80711 becomes the highest at 5.35%**. The ranking depends
> on the method: the self-referencing curve judges R80790 against a stricter bar
> than its neighbours and R80711 against a more lenient one. Neither answer can be
> confirmed without event data. See `phase_3_findings.md` §2.

## 11. How much of the period cannot be judged?

**2.30% of 2015 records** — 0.99% unmeasured (missing data) and 1.32% not
assessable (frozen sensor, invalid temperature, or a wind bin with too little
reference support).

That is a low figure, and it is low partly because of a decision: records below
4.5 m/s get a defined expected power of zero rather than being called
unassessable. Without that, 88% of the year would have been marked unassessable,
which would have been an artefact of the method rather than a fact about the data.

**Unmeasured is not zero.** Any energy lost during those 2,074 missing records is
unknown, not absent. The 672 MWh estimate covers observed time only.

## 12. Which assumptions contribute most to uncertainty?

In order:

1. **The reference quantile** (±22% on the total). No measurement settles it.
2. **Self-referencing curves.** Each turbine is compared with its own history, so
   a fault present throughout 2014 is invisible in 2015. With four turbines the
   peer comparison that would catch this is weak.

   > **Corrected in Phase 3.** This section originally said Figure 5 showed
   > R80790's curve was "noticeably shallower than the others". That was a visual
   > impression from overlaid scatter plots, and measuring it directly
   > ([Figure 7](../outputs/figures/fig7_pooled_vs_turbine_curves.png)) shows the
   > opposite: **R80711** has the curve sitting lowest against the fleet, by 11–19
   > kW across the mid range, while R80790's sits *above* the fleet at mid wind
   > speeds. The structural concern about self-reference was sound; the turbine I
   > attached it to was wrong. See `phase_3_findings.md` §2.
3. **Nacelle anemometry.** The wind reading sits behind the rotor, and its
   calibration assumes the rotor is turning — so it is least reliable exactly when
   a turbine is stopped. Peer wind is used wherever available, which is why
   idle-in-wind findings are graded medium and never high.
4. **Resource difference between the years** (+13.3% in mean cubed wind), which
   pushes 2015 into the thinner high-wind part of the 2014 curve.
5. **The spring collision repair**, affecting 48 records with two marginal calls.
6. **The timestamp correction itself.** It passed nine checks, but it rests on an
   inferred mechanism, not on documentation from the data publisher.

## 13. What this does not prove

- **Not recoverable energy.** "Potential lost energy" is the gap between observed
  power and a statistical reference built from the same machine's past. Some of it
  may not be recoverable by anyone.
- **No cause, for anything.** There are no event codes, no work orders, no
  curtailment records. Words like fault, maintenance, curtailment and grid outage
  appear nowhere in the outputs, and could not be justified if they did.
- **A low residual does not mean the curve is physically correct.** It means the
  arithmetic is consistent.
- **Nothing about the site today.** The data is from 2015.
- **Nothing validated externally.** The meter series is synthetic, so the one
  independent cross-check that would normally exist is unavailable. Every check
  here is internal.

## What changed my mind

Three things.

**The biggest: I was wrong about the scale of the timestamp defect.** In Phase 1 I
first wrote it up as a 96-record clock-change bug and moved on. Testing it
properly showed it affects roughly seven months of every year. The clue I nearly
walked past was that every local day had exactly 144 records, including both
clock-change days — which a daylight-saving-aware logger cannot produce. The
lesson I take from it: a defect that looks small at a boundary is often a symptom,
and timezone-aware timestamps can be confidently wrong.

**Second, a bug that would have produced a plausible-looking wrong answer.** My
first classification run put 88% of 2015 in "not assessable". Two separate causes:
a merge left a boolean column as object dtype, where Python's `~True` is `-2`
rather than `False`, so a test that looked right passed everything through; and
low-wind records had no reference value because zero-power records are excluded
from fitting, so a turbine correctly idle in 2 m/s of wind was being called a data
problem. Neither would have raised an error. Both would have been invisible if I
had not checked whether the category shares made physical sense.

**Third, the frozen-wind threshold did not matter.** In Phase 1 I listed the
6-record rule as a judgement needing a sensitivity test, expecting it to move the
answer. Between 3 and 12 records the total changes by 0.03 MWh. The assumption I
worried about was not the one that mattered — the curve quantile was, and I had
not flagged it in Phase 1 at all.

## 14. Should the ML challenger go ahead?

**Yes, but with the scoring rule fixed in advance and expectations lowered.**

**The case for:** the data supports it. There are 166,726 reference-eligible 2014
records, a clean chronological split, a validated timestamp, and real candidate
features in wind speed, direction and density.

**The case against, which is stronger than it looked in Phase 1:** the baseline's
mean residual is already 0.037% of rated power. A challenger will not beat that
meaningfully on prediction error, and **prediction error is the wrong target
anyway.** A model that predicts degraded operation accurately is a worse detector,
not a better one. The real uncertainty is not in the fit — it is in the reference
quantile (±22%) and in self-reference, and **no model can fix either**, because
both come from having no event data.

**Conditions before training:**

1. The scoring rule is agreed first, and it is detection behaviour, not RMSE.
2. Both methods use the same reference-eligible subset.
3. Both get density, or neither does. The baseline already has it, so the
   challenger must too.
4. Turbine identity and hour of day stay out — the first would let the model learn
   R80790's shallower curve as normal, which is precisely the failure the baseline
   already has.
5. No precision, recall or detection accuracy is reported. There are no labels.

**The honest expectation:** the most likely outcome is that the challenger fits
slightly better and flags slightly less, and that the comparison's value is in
explaining *why* rather than in declaring a winner. That is a legitimate result
and worth showing. It is not a leaderboard.
