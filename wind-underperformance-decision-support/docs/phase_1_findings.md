# Phase 1 findings

Data audit of the La Haute Borne SCADA dataset. Completed 30 September 2026.

Every number below comes from `src/data_audit.py`. The full console output is in
`outputs/audit_log.txt`, and the tables are in `outputs/tables/`. Nothing was
cleaned, filled in or removed.

---

## 1. What the dataset actually contains

| Property | Measured value |
|---|---|
| Archive | 36,762,939 bytes, sha256 `be5ea66a…df6138` |
| SCADA rows | 420,480 |
| Turbines | R80711, R80721, R80736, R80790 |
| Turbine specification | Senvion MM82, 2,050 kW, 80 m hub, 82 m rotor, 411 m elevation — all four identical |
| Period | 2014-01-01 00:00 to 2015-12-31 23:50 UTC (2 full years) |
| Interval | 10 minutes, confirmed from the data, not assumed |
| Expected timestamps per turbine | 105,120 |
| Coverage | 99.99% for all four turbines |
| Data columns | **7**: `Ba_avg` `P_avg` `Ws_avg` `Va_avg` `Ot_avg` `Ya_avg` `Wa_avg` |
| Status / event / alarm columns | **None** |
| Timestamp format | Timezone-aware ISO 8601, offsets `+01:00` and `+02:00` |

Units come from `SCADA_data_description.csv`: power in kW, wind speed in m/s,
temperature in °C, angles in degrees. Power ranges −17.92 to 2,051.87 kW against
a 2,050 kW rating, which confirms kW.

The description file lists nine variables, including `Rm` (torque) and `Ds`
(generator speed). **Neither column exists in the SCADA file.** The description
therefore describes a fuller export than the one supplied.

---

## 2. Assumptions from the background report that were CORRECT

| Assumption | Verdict |
|---|---|
| The example subset is 2014–2015, not the full 2013–2016 range | **Correct.** The file is named `la-haute-borne-data-2014-2015.csv` and covers exactly two years. |
| The ENGIE portal link is dead; the OpenOA copy works | **Correct.** `opendata-renewables.engie.com` does not resolve. The repository zip downloaded cleanly. |
| There would probably be no status or event codes | **Correct**, and it is the most consequential finding in the audit. |
| Four turbines make a weak peer group | **Correct**, and worse than expected: a peer estimate rests on three machines. |
| `plant_data.csv` contains meter and curtailment fields | **Correct** on contents, **wrong** on what they are worth — see §3. |
| Power is in kW | **Correct**, now confirmed from values rather than inferred from loader code. |
| Air-density normalisation would need thought | **Correct.** SCADA has temperature but no pressure. |

---

## 3. Assumptions that were WRONG or unsupported

### 3.1 "Timestamps may be naive; the loader treats them as UTC"
**Wrong on the surface, and the surface is misleading.** The raw timestamps *are*
timezone-aware and carry explicit `+01:00` and `+02:00` offsets, which looks
better than assumed. It is not. See 3.2.

### 3.2 "Daylight saving should show as 138-record and 150-record local days"
**Wrong, and chasing why exposed the most important finding in the audit.**

Neither pattern appears. **Every local day has exactly 144 records, including both
clock-change days.** A logger that followed daylight saving could not do that. That
observation led to a hypothesis: the logger clock never changed, and the summer
offset was written on afterwards. Two independent tests were run.

**Test A — continuity across a spring clock change.** On 2014-03-30 the hour
03:00–03:50 `+02:00` appears twice, with different values. If one copy were a
faulty duplicate it would join on to nothing. Instead both sequences are
continuous with real data:

| Record | Power (kW) | Wind (m/s) |
|---|---|---|
| 01:50, last before the gap | 163.6 | 5.51 |
| sequence B | 172.6 → 207.4 → 247.4 → 259.4 → 241.9 → 254.2 | continues smoothly from 01:50 |
| sequence A | 202.3 → 138.1 → 119.9 → 33.7 → 51.2 → 26.9 | declines into the 04:00 record |
| 04:00, first after the gap | 34.2 | 3.81 |

Both are genuine. The logger kept counting through an hour that the export then
relabelled.

**Test B — SCADA temperature against ERA5 reanalysis.** ERA5 is stored in UTC and
was produced without reference to this logger. Comparing the daily temperature
cycle, season by season:

| Season | Records | Best lag | Correlation |
|---|---|---|---|
| Winter (Nov–Feb) | 5,751 | −1 h | 0.746 |
| Summer (May–Aug) | 5,868 | −2 h | 0.887 |

**The difference is exactly one hour.** A nacelle sensor can lag the outside air in
any season, and that is harmless. A one-hour *seasonal* difference is not.

**Conclusion, supported by both tests:** the logger clock did not follow daylight
saving. The `+02:00` offset was applied to unchanged local time. **Every summer
record therefore lands one hour early once converted to UTC** — roughly late March
to late October, about **seven months of each year**, not 96 records.

**What this does and does not break:**

| Unaffected | Broken |
|---|---|
| The power curve, and anything else comparing columns **within** a row — wind and power share a timestamp, so both move together | **Any join to another time series**: reanalysis wind, air density, temperature |
| Monthly and annual energy totals (a one-hour shift does not change a sum) | **Any reasoning by time of day**, such as diurnal patterns or night-time operation |
| | Cross-checks against `plant_data`, which cannot settle the question because it was built from the same timestamps |

The clock-change days themselves are the visible symptom: **48 duplicated and 48
absent records** across all four turbines (0.0228% of rows). The duplicated pairs
disagree by a median of 127 kW and by up to 828 kW.

### 3.3 "A meter reconciliation will be the strongest credibility check"
**Wrong, and this removes a planned pillar of the project.** The OpenOA loader
states in its own source that the meter series was *"generated by adding
artificial electrical loss and uncertaitny to SCADA data"* (typo original). The
audit confirms it: the meter-to-turbine-sum ratio averages **0.980** with a
standard deviation of **0.008**, and the two series correlate at **0.9997**.

That is a fixed ~2% loss factor with noise added, not an independent measurement.
**The reconciliation must be dropped from the project.**

### 3.4 "Availability and curtailment fields could provide labels"
**Wrong.** Both were estimated from SCADA. `availability_kwh` is non-zero in 3,842
intervals, and 3,074 of those (80%) coincide with a turbine sitting idle in usable
wind — it tracks a SCADA-derived rule. `curtailment_kwh` is non-zero in just 40
intervals (0.04%). Using either as a label would be circular.

### 3.5 "Roughly 136 columns, with min/max/std for each variable"
**Wrong.** That describes the full ENGIE export. This subset has 7 data columns,
averages only. There is **no wind-speed standard deviation** (so turbulence
intensity cannot be computed), no second anemometer for a cross-check, no rotor
speed and no torque.

---

## 4. The three most important data-quality risks

### Risk 1 — No event data, so every loss category is an assumption
3,824 records (0.91% of rows) show no power while wind was at 4 m/s or above.
That is the analytical target of the project, and **nothing in this dataset can
say why**. Peer comparison narrows it only partially:

| Other turbines producing | Records | What it narrows to |
|---|---|---|
| 3 | 2,869 | Specific to this turbine |
| 2 | 621 | Specific to this turbine |
| 1 | 136 | Specific to this turbine |
| 0 | 198 | Site-wide cause, or a shared data outage |

So 3,626 records are turbine-specific and 198 are site-wide. That is the limit of
what the data supports. **Fault, scheduled maintenance, curtailment and grid
outage remain indistinguishable**, which is why every output must say "period
requiring investigation" and never name a cause.

By turbine: R80790 accounts for the most at 1,533 records (255.5 hours), then
R80711 at 944 (157.3 h), R80721 at 694 (115.7 h) and R80736 at 653 (108.8 h).

### Risk 2 — Missing data is clustered, so a careless fill would invent downtime
2,569 power values are absent, in 65 runs. The longest is **132.8 hours on
R80721** — more than five days. **388 gaps are moments when no turbine reported at
all**, which points at the data link rather than the machines.

Filling these with zero would manufacture almost a week of false outage on a
single turbine. Excluding them is correct, but it means any loss during a data
outage is **unmeasured, not zero**, and the final figure must state that.

### Risk 3 — R80721 shows a cluster of instrumentation problems
One turbine carries a disproportionate share of the defects:

| Measure | R80711 | R80721 | R80736 | R80790 |
|---|---|---|---|---|
| Missing power values | 475 | **1,209** | 435 | 450 |
| Longest gap (hours) | 34.3 | **132.8** | 34.2 | 34.3 |
| Gaps unique to this turbine | 87 | **821** | 47 | 62 |
| Temperature at absolute zero | 0 | **33** | 0 | 0 |

The 33 readings of −273.2 °C are at absolute zero, so they are a sensor fault
placeholder, not a measurement. **All of them are on R80721.** Averaging them into
a temperature series would corrupt any air-density calculation for that turbine.

Whether this is one instrumentation problem or several is an open question.

**Smaller issues, quantified and not yet treated:** 43 pitch records outside −5°
to 95°; 18.4% of records show small negative power, which is normal idle
consumption and **not** an error.

Wind-speed readings frozen for an hour or more account for 0.9%–1.4% of each
turbine's records, the longest freeze being 7 hours. A cross-check shows what kind
of fault these are: of 4,609 frozen records, **4,608 have power still moving while
only the wind reading is stuck**, and just 1 has both frozen. So these are stuck
anemometers with the turbine still responding, not the logger republishing an old
row. That matters, because a stuck wind reading corrupts the x-axis of the power
curve while the turbine behaves normally.

---

## 5. Is the planned baseline analysis still feasible?

**Yes, with one pillar removed and one caveat added.**

| Component | Status |
|---|---|
| Binned power-curve baseline | **Feasible.** Two years of clean wind-and-power pairs at 99.99% coverage. |
| Expected power and lost energy | **Feasible**, but every category is inferred, never observed. |
| Peer-based expected power when stopped | **Feasible but weak.** Three peers. Report it as a sensitivity, not as the headline method. |
| Meter reconciliation | **Not feasible. Removed** — the meter is synthetic (§3.3). |
| Time-based vs energy-based availability | **Feasible internally**, but it cannot be compared with any contractual or reported figure, because none exists here. |
| Air-density normalisation | **Feasible, but blocked until the summer timestamps are corrected** (§3.2). Joining reanalysis to uncorrected SCADA would be an hour out for seven months a year. |
| Value-at-risk ranking | **Feasible** as a labelled sensitivity across several €/MWh scenarios. No real price is available. |

**The most important consequence:** losing the meter reconciliation removes the
only external check that was available. The project's credibility now rests
entirely on internal checks — residual bias on the reference subset, sensitivity
across thresholds, and agreement between the two methods. This must be stated in
the final write-up as a limitation, not omitted.

---

## 6. Is the ML comparison still methodologically defensible?

**Yes, but only under conditions that must be fixed before any model is trained.**

**What makes it defensible**
- Enough data: 420,480 records over two full years.
- A clean chronological split is available (2014 train, 2015 test) with good
  coverage on both sides.
- Genuine candidate features exist: wind speed, wind direction, temperature.

**What would make it indefensible**
1. **Scoring on prediction error across all data.** A model that predicts degraded
   and stopped operation accurately is a **worse** underperformance detector, not
   a better one. Lower error would mean the model had learned the very behaviour
   it is meant to flag. The scoring rule must be agreed before training.
2. **Training the challenger on data the baseline excludes.** Both must use the
   same healthy-reference subset, or the comparison is meaningless.
3. **Giving the challenger temperature while the baseline gets only wind speed.**
   That hands the model extra information and then calls the result a fair win.
   Either both get air density or neither does (P-09).
4. **Including turbine identity as a feature.** With four turbines and a strong
   suspicion that R80721 behaves differently, turbine ID would let the model
   learn that turbine's underperformance as normal, and it would then never flag
   it.
5. **Including hour of day.** Power should depend on wind, not the clock. If
   hour-of-day helps, it is absorbing an operational pattern into "expected".
6. **Reporting precision, recall or detection accuracy.** There are **no labels**
   (§3.4). Any such figure would be invented.

**Conclusion:** the comparison stays in, framed as a controlled experiment about
whether extra model flexibility helps or hides the thing being looked for. It
does not stay in as a leaderboard.

---

## 7. Questions to resolve before modelling

0. **Is the P-11 re-timing rule approved, and does it pass its own test?** After correction, the seasonal lag difference against ERA5 should fall to zero. If it does not, the rule is wrong. This gates every cross-series join.
1. Does air density go to **both** models or **neither**? (blocks P-09, and now depends on question 0)
2. Were 2014 and 2015 comparable wind years? Reanalysis can answer this, and it
   validates or breaks the 2014/2015 split.
3. What is the **empirical** cut-in speed? The 4 m/s currently used is a
   conservative choice, not a measurement.
4. Is the R80721 cluster one instrumentation problem or several?
5. What is the agreed scoring rule for the challenger, given there are no labels?
6. Should the 96 clock-change records be excluded outright, or kept in a
   quarantine table and reported? (Current proposal: exclude and report.)

---

## 8. Proposed Phase 2 scope

Deliberately narrow, and it stops before the model.

1. Apply and **validate** the P-11 re-timing rule: re-run the seasonal lag test on
   the corrected timestamps and confirm the difference falls to zero. If it does
   not, withdraw the rule and drop every analysis that needs a cross-series join.
2. Apply the other approved cleaning rules from `methodology_decisions.md` and
   write a `data/processed/` dataset with an exclusion reason recorded for every
   dropped record.
3. Settle open questions 2 and 3 using reanalysis and the observed data.
4. Build the binned power-curve baseline on the 2014 reference subset: 0.5 m/s
   bins, median power, minimum sample count per bin.
5. Check the baseline for bias — the mean residual on healthy records should be
   near zero. Report the figure whatever it is.
6. Produce lost-energy estimates for 2015 by category, with a range from
   sensitivity runs across the P-04, P-06 and P-10 thresholds.
7. **Stop.** Review before the challenger is trained.

Phase 2 deliberately excludes the ML model, the Streamlit app, the slides and the
memo. If the baseline cannot be made trustworthy, a model comparison built on top
of it would not be worth presenting.

---

## 9. Honest assessment of what this data can support

This dataset can support a careful study of **how much apparent underperformance
survives validation, and how confident anyone can be about it.**

It cannot support: a claim about recoverable energy, any root cause, a
contractual availability figure, a revenue number, or a statement about how the
site is operated today. The data is ten years old, has no event log, and its
meter and availability fields are synthetic.

That is not a weakness in the project. **It is the project.** A result that says
"most of this cannot be attributed without operational data, and here is exactly
how much and why" is a more honest and more useful answer than a confident loss
figure built on assumptions.
