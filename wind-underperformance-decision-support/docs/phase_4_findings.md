# Phase 4 findings

Decision and communication. Completed 30 September 2026.

Phase 4 added no model, tuned no threshold and changed no analytical result. It
reads the methods frozen in Phases 2 and 3 and turns them into a decision. The
pre-registration at `2b310b9` and the Phase 3 results at `500f42d` are untouched.

---

## 1. Restoring the original question

The project drifted toward model comparison. Phases 2 and 3 asked which method
detects better; the question an analyst is actually asked is which issue to look
at first. Phase 4 puts that back at the front and demotes the model comparison to
supporting evidence, visible on one page of the application and one slide of six.

**The decision method is B, the pooled transparent curve.** A is shown beside it
so the effect of self-reference stays visible. **C is a qualified second opinion**
and is never described as operationally accepted.

## 2. The correction that mattered most

Phase 3 reported that the challenger "passed the pre-specified acceptance rule".
That was true and it was misleading, because the rule was incomplete.

> The rule required C to improve injected-event recovery over B **without
> increasing apparent alert burden by more than 10% relative to B**. It said
> nothing about the absolute burden. A method can satisfy "no more than 10% worse
> than the alternative" while both alternatives are unusable — which is what
> happened. A 37.9%, B 39.9% and C 40.8% of untouched control windows trigger an
> alert.

The corrected wording, used everywhere now: **the challenger passed the registered
experimental benchmark, but its approximately 41% apparent alert burden means it
is not ready for automated operational alerting.** Neither is A or B.

A better rule would have set an absolute ceiling alongside the relative one,
fixed before any result was seen. It is recorded as a methodological lesson rather
than repaired after the fact, because rewriting a pre-registration once results
are known would destroy the thing that made the Phase 3 result worth reporting.

Two other pieces of wording were tightened for the same reason:

- **R80790 is the preliminary turbine-specific result** (method A: 6.15%).
- **R80711 is the fleet-relative result** produced by the pooled methods (B:
  5.35%, C: 4.72%).
- **Neither turbine is called faulty or confirmed underperforming anywhere.**

The wind-direction leakage failure remains visible in the findings, the
application and the validation CSV. The no-direction refit remains labelled a
post-hoc diagnostic outside the registered comparison. The validation result is
reported as **41 of 42**, not rounded up.

## 3. How the decision register ranks events

Built by `src/decision_register.py` from the frozen methods. Events are defined by
method B, then cross-checked against A and C over the same interval.

The ranking is a transparent tier, not a weighted score. Every input stays in its
own column so a reader can disagree and see exactly why:

| Tier | Rule |
|---|---|
| 1 | Flagged by all three methods, at least one hour long, no blocking data-quality note, and a named operational record could test it |
| 2 | Flagged by at least two methods, discrete, and testable |
| 3 | Everything else |

Within a tier, events sort by the **conservative** end of their energy range —
the smallest figure any applicable method gives, not the largest.

**On prices.** The €50, €80 and €120/MWh scenarios are flat multipliers. They
scale exposure and **cannot reorder events by MWh**. An unchanged ranking across
them is arithmetic, not an independent robustness result, and is not presented as
one.

**On confidence.** No event is graded high. The ceiling is medium, because no
operational record exists for any interval in this dataset.

## 4. The recommended first investigation

**R80711, 26 July 2015 15:10 to 28 July 09:30 UTC, 42.5 hours.**

| | |
|---|---|
| Potential shortfall | 36.8–37.6 MWh across methods |
| Illustrative value | €1,842–1,880 at €50 · €2,947–3,008 at €80 · €4,421–4,513 at €120 |
| Methods flagging it | **A + B + C** |
| Confidence | Medium |
| Data-quality qualifications | None |

**Directly observed.** 255 consecutive ten-minute records. 97.6% at or below zero
power against an expected 901 kW under method B. All three neighbouring turbines
produced continuously through the same interval, averaging 724–840 kW in 5–12 m/s
wind. In the preceding 48 hours R80711 tracked expectation closely (647 kW actual
against 673 kW expected, 1.92 MWh shortfall over two days).

**Where the methods agree.** All three flag it, and their energy estimates fall
within 0.8 MWh of one another. This is the strongest agreement in the register.

**Where they disagree.** Method A places the event at 47.2 hours starting 09:30;
method B at 42.5 hours starting 15:10. The boundaries differ because the methods
disagree about the marginal records at each end. The energy is nearly identical,
so the disagreement does not affect the decision.

**It was checked before being selected.** The largest event is not automatically
the right first investigation. Two things were verified:

1. **Is it corroborated?** Yes — all three frozen methods, with no data-quality
   qualifications.
2. **Does it explain R80711's fleet-relative ranking, or is it separate?**
   **Removing this one event drops R80711 from 5.35% to 4.46% of potential, below
   R80790's 5.10%.** R80711 leads the pooled ranking largely *because of* this
   event, not because of a persistent pattern.

That second answer changes how the recommendation should be read. It is a
recommendation to investigate **a discrete outage**, not a verdict that R80711 is
the worst-performing turbine. R80790's more diffuse gap, which survives the
removal of any single event, is a separate and slower second line of enquiry.

**What cannot be concluded.** Five explanations fit the evidence equally well:
planned maintenance, an unplanned fault stop, grid curtailment, a controller
lockout awaiting a manual reset, or a communications loss while the turbine was
in fact producing. Nothing in this dataset distinguishes them. Nothing here
establishes that the energy was recoverable by anyone.

**First data request.** Turbine event and alarm codes for 26–28 July 2015; work
orders and maintenance records covering the interval; curtailment or grid
instructions; operator logs. Normally held by the site operations team, with
curtailment records from the commercial team.

**Review point.** Five business days after the records are received.

**What would escalate it.** Event codes showing an unplanned fault stop with no
corresponding work order, or no record of the outage at all — the latter would
raise a data-completeness question as well as an operational one.

**What would close it.** Records showing a planned service visit or a documented
grid instruction covering the interval. That outcome is entirely plausible, and a
42-hour stop in late July is consistent with scheduled summer maintenance.

## 5. Inconsistencies found during Phase 4

| Found | Resolution |
|---|---|
| "Passed the acceptance rule" read as operational readiness | Reworded everywhere; the rule's incompleteness documented in §2 |
| `bin_supported` missing from the assessment frame when building event qualifications | Method B's bin support is now attached explicitly, so data-quality notes describe the decision method |
| Method A and method B disagree on event boundaries for the leading event | Reported in §4 rather than silently resolved; both energy figures appear in the register |
| The register's initial event list came from method A's classification | Classification vocabulary is carried across all methods, so every event is described consistently |

No numerical result from Phases 1 to 3 changed.

## 6. What changed from the Phase 3 interpretation

**Phase 3 framed the challenger's pass as the headline result.** Phase 4 reframes
it as supporting evidence with a material caveat. The measured numbers are
identical; the claim attached to them is narrower.

**Phase 3 left "which turbine is worst" as an open disagreement between methods.**
Phase 4 resolves the practical question without resolving the analytical one:
investigate the discrete, corroborated, testable **event**, and treat the turbine
ranking as unsettled. That is a better answer than picking a turbine, because one
record request can close the event, and no available evidence can close the
ranking.

**Phase 3 did not test whether R80711's ranking was event-driven.** It is, and
that materially qualifies the fleet-relative finding. This is the single most
useful thing Phase 4 added, and it took one calculation that should have been run
in Phase 3.

## 7. Deliverables

| File | What it is |
|---|---|
| `outputs/tables/decision_event_register.csv` | 25 leading events, fully attributed |
| `outputs/tables/decision_event_timelines.csv` | Ten-minute detail for the top 8 events |
| `app/app.py` | Five-section decision-support application, reads generated tables only |
| `docs/executive_memo.md` | One-page memo (source) |
| `deliverables/executive_memo.pdf` | Rendered, verified as one page by reading it back |
| `deliverables/La_Haute_Borne_performance_review.pptx` | Six slides, verified by reopening the saved file |
| `RUN_APP.md` | Exact commands |

**Render verification was done by reading the files back**, not by assuming they
were written: the deck reopens with six slides and contains both required
disclaimers; the PDF reopens as a single page containing the recommendation, the
energy range and the not-recoverable statement, with no unrenderable characters.

## 8. Limitations, unchanged

Everything from Phases 1 to 3 still applies, and Phase 4 adds nothing that
weakens them: no event codes or work orders, no independent meter validation
(the supplied meter is synthetic), four turbines, 2015 data, a synthetic benchmark
that is an upper bound, and site-wide problems that would remain invisible to
every method used.

**No finding in this project reaches "validated finding" on its own evidence
hierarchy.** Everything operational is a hypothesis, and the deliverables say so
on every page that carries a number.
