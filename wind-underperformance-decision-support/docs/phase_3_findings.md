# Phase 3 findings

Pooled counterfactual and constrained challenger. Completed 30 September 2026.

Method and acceptance rule were fixed in `docs/phase_3_method.md` and committed at
`2b310b9`, before any model was trained. Every number below traces to a table in
`outputs/tables/`. No Streamlit, slides, memo or outreach material exists yet.

---

## Summary

| | A: turbine-specific | B: pooled transparent | C: pooled challenger |
|---|---|---|---|
| Assessable share of 2015 | 98.55% | 98.83% | 98.83% |
| Gross shortfall | 671.6 MWh | 678.1 MWh | 569.5 MWh |
| Persistent events | 2,302 | 2,435 | 2,637 |
| Injected-event recovery | 0.7459 | 0.7713 | **0.8183** |
| Apparent alert burden | 0.3789 | 0.3993 | 0.4083 |
| Recovery minus burden | 0.367 | 0.372 | **0.410** |

**The challenger passed the registered experimental benchmark**: recovery improved
from 0.7713 to 0.8183, and alert burden rose 2.27%, inside the 10% limit. I
expected it to fail. Two other expectations were also wrong, and one of them
corrects a statement in the Phase 2 findings.

> **Corrected in Phase 4 — read this before quoting the result.** Passing the
> registered benchmark is not the same as being fit for use. **The challenger's
> approximately 41% apparent alert burden means it is not ready for automated
> operational alerting**, and neither is A at 37.9% or B at 39.9%.
>
> The acceptance rule was **incomplete**. It constrained only the *relative*
> increase in burden against method B, and said nothing about the *absolute*
> level. A method can satisfy "no more than 10% worse than the alternative" while
> both alternatives are unusable. That is a flaw in the rule I wrote, recorded
> here as a methodological lesson rather than quietly repaired. A better rule
> would have set an absolute ceiling on burden as well as a relative one, fixed
> before any result was seen.
>
> Nothing about the measured results changes. The wording does: the challenger is
> **a qualified second opinion**, never "operationally accepted".

---

## 1. How much of the difference comes from pooling?

**Less than half of it.** This is what method B exists to establish.

| Step | Recovery change | Gross shortfall change |
|---|---|---|
| A → B (pooling alone, same transparent method) | **+2.5 points** (0.7459 → 0.7713) | +6.5 MWh |
| B → C (model flexibility and extra features) | **+4.7 points** (0.7713 → 0.8183) | −108.6 MWh |

So roughly one third of the total detection gain comes from comparing turbines
with the fleet, and two thirds from the model. Without B in the design, all 7.2
points would have been credited to machine learning.

The gross-shortfall figures move in opposite directions and are worth separating.
Pooling barely changes the total energy (+6.5 MWh). The model **reduces** it by
108.6 MWh while flagging **more** events (2,637 against 2,435). That is the
expected consequence of a better fit: residuals shrink, so each flagged record
carries less energy. **A method that reports less energy is not thereby finding
less.** It is a reminder that gross shortfall measures fit as much as it measures
performance.

## 2. Does pooling expose a fleet-relative gap for R80790?

**No. It does the opposite, and it corrects a Phase 2 error.**

| Turbine | A | B | C |
|---|---|---|---|
| R80711 | 4.36% | **5.35%** | **4.72%** |
| R80721 | 4.22% | 4.49% | 3.56% |
| R80736 | 4.25% | 4.15% | 3.23% |
| R80790 | **6.15%** | 5.10% | 4.58% |

Phase 2 flagged R80790 as the turbine to investigate first, at 6.15% against
4.2–4.4% for the others, and reasoned that its own curve looked shallower on
Figure 5, so a self-referencing method might be hiding worse behaviour.

**That reasoning was wrong.** Figure 7 measures each turbine's own curve against
the pooled curve directly, rather than reading it off a scatter plot:

| Turbine | Own curve minus pooled, mean | At 8 m/s | At 11 m/s |
|---|---|---|---|
| R80711 | **−11.2 kW** | −18.4 | −19.2 |
| R80721 | −8.3 kW | −1.0 | −0.2 |
| R80736 | +14.1 kW | +5.4 | +27.6 |
| R80790 | +6.0 kW | +17.6 | −16.9 |

**R80711 is the turbine whose own reference sits lowest relative to the fleet**,
not R80790. Under method A, R80711 is judged against a bar roughly 11–19 kW below
its neighbours, which flatters it. Correct that by pooling and R80711 becomes the
worst turbine on the site under both B and C.

R80790's own curve sits *above* the fleet at mid wind speeds, so method A judges
it against a stricter bar than its neighbours face. Its 6.15% is partly an
artefact of that, and pooling reduces it to 5.10%.

**The honest conclusion is uncomfortable: which turbine is "worst" depends on the
method.** A says R80790; B and C say R80711. That is a direct challenge to the
Phase 2 recommendation, and it is the strongest argument in this whole project for
not relying on a self-referencing baseline alone. It is also a reason to be
cautious about any single ranking: with four turbines and no event data, neither
answer can be confirmed.

## 3. Does the model improve detection beyond the pooled curve?

**Yes, consistently, and by more than pooling did.** From
`phase3_synthetic_injection.csv`:

| Severity | Duration | A | B | C |
|---|---|---|---|---|
| 5% | 30 min | 0.4597 | 0.4924 | **0.5417** |
| 5% | 60 min | 0.6049 | 0.6326 | **0.6868** |
| 5% | 120 min | 0.7083 | 0.7458 | **0.7861** |
| 10% | 30 min | 0.6132 | 0.6319 | **0.7257** |
| 10% | 60 min | 0.7715 | 0.7938 | **0.8451** |
| 10% | 120 min | 0.8653 | 0.8736 | **0.9194** |
| 20% | 30 min | 0.8222 | 0.8597 | **0.9153** |
| 20% | 60 min | 0.9139 | 0.9417 | **0.9632** |
| 20% | 120 min | 0.9542 | 0.9701 | **0.9812** |

C is ahead in all nine cells. The ordering A < B < C holds throughout, which makes
the pattern harder to dismiss as noise. The gain is largest where detection is
hardest — at 10% severity and 30 minutes, C recovers 72.6% against B's 63.2%.

**The failed leakage check, and what it turned out to mean.** The pre-specified
check on wind direction **failed**: the largest difference in any 30-degree sector
between producing and idle records was 0.0818, above the 0.05 concern level. The
feature does partly encode operating state.

The method document said a failure means the result is qualified. To quantify the
qualification, C was refitted without direction as a **post-hoc diagnostic,
clearly not part of the pre-registered comparison**:

| | Recovery | Burden |
|---|---|---|
| C with direction (pre-registered) | 0.8183 | 0.4083 |
| C without direction (diagnostic) | 0.8167 | 0.4067 |
| B pooled transparent | 0.7713 | 0.3993 |

**C's advantage does not depend on the suspect feature.** Removing it costs 0.0016
of recovery. The gain comes from the model's flexibility in the wind-speed and
density relationship, not from direction. The leakage concern is real and stands
on the record, but it does not change the conclusion.

## 4. What alert burden does each method create?

| Method | Apparent alert burden | Recovery | Recovery minus burden |
|---|---|---|---|
| A | 0.3789 | 0.7459 | 0.367 |
| B | 0.3993 | 0.7713 | 0.372 |
| C | 0.4083 | 0.8183 | **0.410** |

**All three methods flag roughly 40% of untouched control windows.** That is high,
and it is mostly structural: the reference is a median, so about half of all
records sit below it by construction, and a rule needing three consecutive
shortfall records is met often by chance. The detection rule was fixed in advance
and applied identically, so the comparison is fair — but none of these methods is
a precision instrument at this setting.

The honest reading is that C detects more while asking for proportionally little
extra review. It is not that C is accurate in absolute terms.

**This is not a false-positive rate.** An untouched window may well contain
genuine underperformance that nobody has labelled. The figure measures review
effort generated, not error.

**A design flaw to report.** Median detection delay came out at 0 minutes for
every method and every severity, because each injection begins at the first record
of its window, leaving no clean lead-in to measure a lag against. The metric is
reported for completeness but **cannot discriminate between methods**. A future
version should pad each window with clean records before the injection starts.

## 5. Which method should be primary in the eventual application?

**B, the pooled transparent curve, with A shown alongside and C available as a
second opinion.**

The reasoning, including the part that argues against this choice:

**For C:** it passed the pre-specified acceptance rule. It detects better in all
nine benchmark cells, and its advantage survives removing the suspect feature.
On the evidence, it is the better detector.

**For B as primary anyway:**
- The gain is modest in context. C recovers 4.7 points more than B, on a benchmark
  where both are around 40% burden. That is an improvement, not a step change.
- **C agrees with B on only 44.7% of flagged records** (`phase3_event_overlap.csv`;
  A and B agree on 71.8%). The methods are not interchangeable, and a tool whose
  purpose is a number someone can interrogate should not lead with the one that is
  hardest to explain and most different from the others.
- The single most valuable finding in Phase 3 — the R80711/R80790 reversal — comes
  from **pooling**, which B delivers with a method that fits on one slide.
- A synthetic benchmark measures response to a clean artificial step. Real
  degradation is gradual and correlated with conditions, so C's margin here is an
  upper bound on any real advantage.

**Recommended layout:** B as the headline, A shown next to it so the effect of
self-reference is visible rather than hidden, and C offered as a second opinion
that can be turned on. Where B and C disagree, say so rather than resolving it
silently — a disagreement between two defensible methods is information.

This is a judgement, not a result. Someone weighing detection above
explainability could reasonably choose C, and the evidence would support them.

## 6. What cannot be concluded without event codes, work orders, curtailment records and an independent meter?

- **Any cause.** Nothing here distinguishes a fault from scheduled maintenance,
  curtailment, a grid restriction, a different control configuration or a sensor
  calibration difference. The R80711 fleet-relative gap could be any of those, or
  a wake or siting effect.
- **Whether any of it is recoverable.** None of these figures is recoverable
  energy, and none should be presented as revenue.
- **Which method is right.** The benchmark measures response to synthetic steps.
  It cannot say which method is correct about the real 2015 data, because the real
  data has no labels. This is why no real-world precision, recall or accuracy is
  reported anywhere in this project.
- **Whether the ~40% alert burden is error.** Without labels, an alert on an
  untouched window cannot be called wrong.
- **Whether R80711 or R80790 deserves attention first.** A and B disagree, and
  nothing available can break the tie.
- **Anything about the site today.** The data is from 2015.

## What changed my expectation

**I expected the challenger to fail the acceptance rule. It passed.** In the
Phase 2 findings I wrote that the most likely outcome was "the challenger fits
slightly better and flags slightly less" and that the comparison's value would be
in explaining why. The first half was right — gross shortfall fell by 108.6 MWh —
but the detection benchmark went the other way, consistently, in all nine cells.
Having pre-registered the rule before seeing any of it is the only reason I can
report that without it looking like a story fitted to the result.

**I expected pooling to expose R80790. It exonerated it.** The Phase 2 hypothesis
was that R80790's self-reference was hiding worse behaviour. The opposite is true:
its own curve sits above the fleet, so method A was judging it more harshly than
its neighbours, and pooling reduced its shortfall from 6.15% to 5.10%.

**A Phase 2 statement was wrong and is corrected here.** Phase 2 said R80790's
curve was "noticeably shallower than the others", read off the Figure 5 scatter.
Measuring it directly shows R80711's curve is the one sitting below the fleet, by
11–19 kW across the mid range. The lesson is narrow and worth keeping: a visual
impression from four overlaid scatter plots is not a measurement, and I should
have measured it in Phase 2 rather than asserting it.

**The pooling effect was smaller than the model effect**, at +2.5 against +4.7
points of recovery. I had assumed pooling would dominate, on the reasoning that
fleet-relative comparison addresses a structural blind spot while a model only
adds flexibility. Pooling does address the blind spot — question 2 is the proof —
but it contributes less to detecting a step change.

## Validation

**12 of 13 checks passed** (`phase3_checks.csv`). The one failure is the
wind-direction leakage check, which is a finding rather than a defect: it fired
exactly as designed, and the post-hoc diagnostic it triggered showed the
conclusion holds without the feature.

| Check | Result |
|---|---|
| No method trained on the assessment year | PASS |
| Challenger excludes turbine identity | PASS |
| Challenger excludes calendar and outcome features | PASS |
| Model parameters fixed and seeded | PASS |
| Wind-direction feature not state-dependent | **FAIL** — 0.0818 against a 0.05 limit |
| Benchmark windows stratified and seeded | PASS — 1,440 per combination |
| Controls and injected windows matched | PASS |
| Challenger meets the pre-specified acceptance rule | PASS |
| Benchmark uses synthetic labels only | PASS |
| All methods share event logic | PASS |
| Challenger advantage survives removing the suspect feature | PASS |

## Remaining limitations

1. **No external validation.** The meter is synthetic, so every check remains
   internal. Unchanged from Phase 2 and unfixable with this dataset.
2. **Four turbines.** A pooled curve built from four machines is a weak fleet
   reference. With one turbine contributing a quarter of the pooled median, a
   genuinely degraded machine still pulls the bar toward itself.
3. **A site-wide problem remains invisible.** Pooling fixes turbine-versus-turbine
   blindness, not fleet-versus-truth blindness. If all four degraded together, no
   method here would see it.
4. **The synthetic benchmark is an upper bound.** Clean artificial steps are the
   easiest possible case.
5. **Detection delay is unmeasurable** in the current window design (see §4).
6. **The ~40% alert burden** means none of these methods is precise enough to
   drive an alerting workflow as configured. A higher persistence threshold or a
   deadband would reduce it, but both were fixed in advance and changing them now
   would be tuning on the result.
7. **The leakage check failed.** Quantified and shown not to matter here, but the
   feature remains partly state-dependent.
8. **Everything from Phase 2 still applies**: no event codes, an inferred
   timestamp correction, 2014/2015 resource differing by 13.3% in mean cubed wind,
   and the reference quantile driving the total by ±22%.
