# Phase 3 method — locked before any model was trained

Written and committed **before** the challenger was fitted, so the evaluation
rules cannot be adjusted after seeing results. Commit this file on its own; the
model code arrives in a later commit.

---

## 1. The question

> Can a fleet-relative counterfactual detect persistent turbine underperformance
> that a self-referencing baseline may normalise away, and does machine learning
> add useful detection capability beyond a transparent pooled baseline?

This is not a question about prediction error. A model that predicts degraded
operation accurately is a **worse** detector, not a better one. Phase 2 found the
specific weakness this phase is built to probe: R80790's reference curve is
visibly shallower than the other three, and because each turbine is judged against
its own history, that shallowness produces no flagged loss at all.

## 2. The three methods

| | Method | Fitted on | Why it is here |
|---|---|---|---|
| **A** | Turbine-specific median-binned reference curve | Each turbine's own 2014 reference-eligible records | The Phase 2 baseline. The incumbent. |
| **B** | **Pooled** median-binned reference curve | All four turbines' 2014 reference-eligible records, combined | Isolates the effect of **pooling alone**. Same transparent method as A, only the population changes. |
| **C** | Pooled constrained tree-based regressor | Same pooled 2014 subset as B | Isolates the effect of **model flexibility and extra features**, over and above pooling. |

**B is the control that makes this experiment meaningful.** Without it, any
difference between A and C could be attributed to machine learning when it
actually came from comparing turbines against the fleet. A minus B is the pooling
effect; C minus B is the machine-learning effect.

## 3. Rules that apply identically to all three

1. Fit only on the 2014 reference-eligible subset defined in Phase 2 (166,726
   records). No method sees any 2015 record during fitting.
2. All methods are frozen before being applied to 2015.
3. Identical eligibility, assessment and event rules for all three.
4. Expected power is clipped to [0, 2050] kW for all three.
5. Below the operating threshold (4.5 m/s), expected power is zero by definition
   for all three, exactly as in Phase 2.
6. `potential_lost_energy_kwh = max(expected_kw − max(actual_kw, 0), 0) × (10/60)`
   for all three.

## 4. Features for C, and the leakage review

**Permitted:** density-corrected wind speed, air density, and wind direction as
`sin`/`cos` pair.

**Excluded, with reasons:**

| Excluded | Reason |
|---|---|
| Turbine identity | Would let the model learn R80790's shallower curve as normal — the exact failure this phase exists to expose. |
| Hour of day, month, any calendar variable | Power should depend on wind, not the clock. Would absorb operational patterns into "expected". |
| Actual power, residuals | The target. Direct leakage. |
| Pitch angle (`Ba_avg`) | A control-system output. A pitched-out blade is a *consequence* of the turbine's operating state, so it would let the model predict the shortfall from the evidence of the shortfall. |
| Generator speed, nacelle position | Same reason: control outputs, not conditions. |
| Rolling or forward-looking windows | Would read the outcome. |

**Leakage review of wind direction, which is a genuine borderline case.** `Wa_avg`
(absolute wind direction) is derived from nacelle position plus vane angle. Both
reflect the turbine's own control state. For a stopped or yawed turbine, the
nacelle may not track the wind, so the reading could partly encode operating state
rather than weather.

The decision, and it is a judgement: **include it, and test it.** Direction has a
legitimate physical role at this site — the four turbines sit in a line running
roughly north-east, so wake interference is direction-dependent, and a pooled
curve that ignores direction will systematically misjudge waked turbines. Before
using the feature, `src/ml_challenger.py` runs a check comparing direction
distributions between producing and non-producing records. **If the distributions
differ materially, the concern is reported in the findings and the result is
qualified.** The check runs regardless of outcome and is recorded in the Phase 3
validation CSV.

## 5. The model

One model, fixed, no search:

- `HistGradientBoostingRegressor` from scikit-learn
- `max_depth=4`, `max_iter=200`, `learning_rate=0.05`, `min_samples_leaf=200`,
  `l2_regularization=1.0`, `random_state=42`
- Target: `P_avg`
- No grid search, no AutoML, no neural network, no feature selection loop, no
  leaderboard of variants

Constrained on purpose. The aim is to see whether *any* reasonable flexible model
adds detection capability, not to find the best one.

## 6. Event logic — identical for all three methods

A record is a **shortfall record** if it is assessable and
`potential_lost_power_kw > 0`.

An **event** is a run of consecutive shortfall records. The operational
persistence rule stays at **6 records (1 hour)**, unchanged from Phase 2, for
reporting candidate events on real 2015 data.

## 7. Synthetic derating benchmark

Real 2015 data has no verified labels, so detection capability cannot be measured
on it. The benchmark creates cases where the answer is known by construction.

**Construction:**
- Select windows from 2015 that are clean and assessable throughout: no missing
  data, no frozen sensor, producing, in a supported bin.
- **Preserve every feature.** Only `P_avg` is reduced. Wind speed, direction and
  density are untouched, so no method can see the injection in its inputs.
- Severities: **5%, 10%, 20%** reduction.
- Durations: **30, 60, 120 minutes** (3, 6, 12 records).
- `random_state=42`, stratified across the four turbines and across wind-speed
  ranges (below 7 m/s, 7–10 m/s, above 10 m/s).
- Every injected window has an **untouched control copy**, drawn the same way.

**Detection rule, pre-specified.** A window counts as **recovered** if at least
**3 consecutive records** inside it are shortfall records under that method.

Three records is chosen because it equals the shortest injected duration, so all
three durations are detectable in principle. Note the consequence, stated now
rather than discovered later: **under the operational 6-record rule, a 30-minute
injection could never be recovered by any method.** That is a property of the
rule, not of the methods, which is why the benchmark uses 3.

**Metrics:**
- **Event recovery rate**: share of injected windows recovered, by severity and
  duration.
- **Detection delay**: minutes from injection start to the first record of the
  first qualifying run.
- **Apparent alert burden**: share of *untouched control* windows that trigger the
  same rule.

**Apparent alert burden is not a false-positive rate.** An untouched window may
contain genuine underperformance that nobody has labelled. The figure measures how
much review each method would generate, not how often it is wrong.

Synthetic labels are used only for injected-event recovery. **No real-world
precision, recall or accuracy is reported anywhere**, because no real labels exist.

## 8. Acceptance rule for the challenger — fixed in advance

> **C is operationally useful only if it improves injected-event recovery over B,
> without increasing apparent alert burden on untouched windows by more than 10%
> relative to B.**

Applied to the overall recovery rate across all severity and duration
combinations. If C fails, the findings will say so plainly. **A negative result is
an acceptable and publishable outcome**, and is the more likely one given that B's
mean residual is already about 0.04% of rated power.

Thresholds are not adjusted after seeing 2015 results. If something in the results
suggests a different rule would be better, that observation goes in the findings as
a recommendation for future work — it does not change this rule.

## 9. What Phase 3 cannot settle

- No cause, for anything. There are still no event codes, work orders or
  curtailment records.
- No recoverable energy, production uplift or revenue.
- No external validation: the meter series is synthetic, so every check remains
  internal.
- Whether a flagged fleet-relative gap on any turbine reflects a fault, a
  different control configuration, a siting or wake effect, or a sensor
  calibration difference. All four would look identical here.
- A synthetic benchmark measures response to a clean artificial step. Real
  degradation is gradual, noisy and often correlated with conditions, so recovery
  rates here are an **upper bound** on real-world detection.

## 10. Outputs

| File | Contents |
|---|---|
| `src/ml_challenger.py` | All Phase 3 code |
| `outputs/tables/phase3_method_comparison.csv` | A, B, C on 2015 |
| `outputs/tables/phase3_synthetic_injection.csv` | Recovery and delay by severity and duration |
| `outputs/tables/phase3_turbine_comparison.csv` | Per-turbine, all three methods |
| `outputs/tables/phase3_event_overlap.csv` | Which methods flag the same events |
| `outputs/tables/phase3_checks.csv` | Validation checks |
| `outputs/figures/fig7_pooled_vs_turbine_curves.png` | Where pooling changes the reference |
| `outputs/figures/fig8_detection_benchmark.png` | Recovery against alert burden |
| `docs/phase_3_findings.md` | Results against the questions above |

No Streamlit, slides, memo or outreach material in this phase.
