# Real Loss or Bad Data?

Validating wind underperformance before modelling it.

An independent analysis of public wind-farm SCADA data, built as a portfolio
project. **The full case study is complete: the data is audited, a transparent
baseline is built and validated, a pooled fleet-relative counterfactual and a
constrained machine-learning challenger have been benchmarked, and the results
are packaged in an interactive application, executive memo and slide deck.**

---

## The question

After validating public wind-farm SCADA data, how much apparent underperformance
remains, and does a carefully constrained machine-learning challenger identify
decision-relevant deviations better than a transparent power-curve baseline?

This is not a project about building the most accurate prediction model. It is
about establishing whether the data and the analytical output are trustworthy
enough to justify an operational investigation.

## Definition used throughout

> **Potential underperformance** means production materially below modelled
> expected production under comparable operating conditions. It is **not**
> confirmed recoverable energy, because operational logs, curtailment
> instructions and maintenance records are not available for this dataset.

## Independence statement

- Public data only.
- Independent personal project.
- No Clir Renewables data, software or proprietary methodology was used.
- Nothing here describes Clir, its platform, its methods or its customers.
- The site owner and turbine manufacturer are named only because the public
  dataset names them. No conclusion is drawn about either.

## Data

ENGIE La Haute Borne wind farm, Meuse, France. Four Senvion MM82 turbines,
2,050 kW each. Ten-minute records covering 2014-01-01 to 2015-12-31 (UTC).

Obtained from the OpenOA repository copy. See [`data/README.md`](data/README.md)
for the download command, licence and checksum. **The raw data is not committed
to this repository.**

## How to reproduce

```bash
# From the project root. Windows paths shown; use .venv/bin/python elsewhere.
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt

# Download the data first - see data/README.md

cd src
../.venv/Scripts/python.exe data_audit.py            # Phase 1: audit, changes nothing
../.venv/Scripts/python.exe timestamp_correction.py  # Phase 2A: timestamp hypothesis
../.venv/Scripts/python.exe prepare_data.py          # Phase 2B-D: processed dataset
../.venv/Scripts/python.exe baseline_model.py        # Phase 2E-H: baseline, sensitivity
../.venv/Scripts/python.exe ml_challenger.py         # Phase 3: pooled curve + challenger
```

Built and run on CPython 3.11.0, Windows. All package versions are pinned in
`requirements.txt`, including transitive dependencies.

Each script after Phase 1 writes its validation checks to a CSV in
`outputs/tables/`. A script cannot report a check as passed unless the check
actually ran: **84 of 85 pass** (9 timestamp, 11 data preparation, 9 baseline,
13 Phase 3, 7 decision register, 11 render verification, 25 application). The single failure is the wind-direction leakage check, which is a
finding rather than a defect — it fired as designed, and the diagnostic it
triggered showed the conclusion holds without the feature. Phase 1's audit
predates this framework and reports in `outputs/audit_log.txt` instead. The raw
files are read and never modified.

## What Phase 1 found

Full detail in [`docs/phase_1_findings.md`](docs/phase_1_findings.md). In short:

| Finding | Why it matters |
|---|---|
| **No status, event or alarm codes exist.** The file has 7 measurement columns. | Turbine states must be inferred from SCADA. Every loss category becomes an assumption, not a fact. |
| **The summer timestamps are wrong by one hour.** The timestamps look trustworthy — they carry `+01:00` and `+02:00` offsets — but two independent tests show the logger clock never moved for daylight saving and the summer offset was added afterwards. | Affects roughly **seven months of every year**, not the 96 clock-change records. The power curve is unaffected because wind and power share a row, but **any join to another time series — reanalysis, air density, time of day — would be an hour out.** |
| **The clock-change days are broken too.** Each spring date duplicates an hour; each autumn date drops one. 48 extra and 48 absent records. | Small in volume, and the clearest evidence of the bigger problem above. |
| **The meter series is synthetic**, derived from SCADA. Confirmed from the OpenOA loader source and by measurement (ratio 0.980, correlation 0.9997). | A meter reconciliation **cannot** validate the SCADA here. That check has to be dropped. |
| **`availability_kwh` and `curtailment_kwh` are estimates**, not measurements. | They cannot be used as ground truth for availability or curtailment. |
| **Missing values are clustered, not scattered.** Longest run 132.8 hours. 388 gaps are site-wide. | Filling gaps with zero would invent downtime the data does not show. |
| **3,824 records (0.91%) show no power in usable wind.** | This is the real analytical target, and its cause cannot be established without an event log. |

## What Phase 2 found

Full detail in [`docs/phase_2_findings.md`](docs/phase_2_findings.md).

| Finding | Detail |
|---|---|
| **The timestamp correction passed all 9 checks.** | Absent intervals 48 → **0**, duplicates 48 → **0**, seasonal lag difference −1 h → **0 h**, energy conserved exactly. The corrected sequence is complete: 105,120 records per turbine, no gap, no duplicate. |
| **80.13% of records are reference-eligible.** | 336,928 of 420,480. The largest exclusion is zero-power (18.4%), kept in full as investigation candidates. |
| **The operating threshold is 4.5 m/s**, measured. | Every turbine first reaches 95% producing in the 4.0 m/s bin; the threshold sits one bin above. |
| **2014 and 2015 are not closely comparable.** | Mean cubed wind +13.3% in 2015. The split stays valid because the curve is conditioned on wind speed, but raw annual energy must never be compared between years. |
| **672 MWh potential lost energy in 2015**, 4.77% of potential. | Range **538–834 MWh** across specifications. Illustrative value €21,500–66,700 at €40–80/MWh. *Illustrative sensitivity — not actual revenue.* |
| **Only 57% of that is attributable to identified events.** | 291 MWh is diffuse sub-threshold noise. Reporting the headline as if it were all actionable would be the easiest mistake here. |
| **R80790 stands out.** | 6.15% lost against 4.2–4.4% for the other three. |
| **The reference quantile is the assumption that matters** (±22%). | The frozen-wind threshold, flagged as a worry in Phase 1, moves the answer by 0.03 MWh. |
| **2.30% of 2015 cannot be judged.** | Unmeasured is reported as unknown, never as zero. |

No cause is assigned to anything. Without event logs, "below the reference curve"
is a description of the data, not a diagnosis.

## What Phase 3 found

Full detail in [`docs/phase_3_findings.md`](docs/phase_3_findings.md). Method and
acceptance rule were locked in [`docs/phase_3_method.md`](docs/phase_3_method.md)
and committed **before** any model was trained.

Three methods, all fitted on the same 2014 subset and frozen before touching 2015:
**A** each turbine against its own history, **B** the same transparent method
pooled across the fleet, **C** a constrained pooled gradient-boosted challenger.
B is the control that separates the effect of pooling from the effect of the model.

| Finding | Detail |
|---|---|
| **The challenger passed the registered experimental benchmark, but is not ready for automated operational alerting.** | Recovery 0.771 → **0.818**, burden up 2.3% against a 10% limit. But its ~41% absolute alert burden (A 37.9%, B 39.9%) makes none of the three fit for automated alerting. The rule constrained only the *relative* increase, not the absolute level — an incomplete rule, recorded rather than patched. |
| **Two thirds of the gain is the model, one third is pooling.** | A→B +2.5 points of recovery, B→C +4.7. Without B in the design, all of it would have been credited to machine learning. |
| **Pooling reversed which turbine looks worst — and corrected a Phase 2 error.** | A says R80790 (6.15%). B and C say **R80711** (5.35%, 4.72%). R80711's own curve sits 11–19 kW *below* the fleet, so judging it against itself flatters it. |
| **The wind-direction leakage check failed, and it did not matter.** | Sector difference 0.082 against a 0.05 limit. A post-hoc refit without the feature: recovery 0.8167 against 0.8183. The advantage survives. |
| **All three methods flag ~40% of untouched control windows.** | Structural, since a median reference puts half of all records below it. None of these is a precision instrument at this setting. |
| **Recommended primary method: B**, with A shown beside it and C as a second opinion. | C detects better but agrees with B on only 44.7% of flagged records. For a tool whose value is a number someone can interrogate, transparency leads. |

## The application

An interactive decision tool, not a report. `streamlit run app/app.py` — full
instructions and optional AI setup in [`RUN_APP.md`](RUN_APP.md).

| Page | What it answers |
|---|---|
| **Executive cockpit** | Which issue first, what is the exposure, how confident, what record is needed. Price slider, method selector, turbine filter, energy-basis toggle. |
| **Investigation explorer** | The event register as a scatter and heatmap, filterable, with per-event timelines, hypotheses and escalation criteria. |
| **Method and scenario lab** | Why A, B and C disagree, and the synthetic detection benchmark. Model performance appears here and nowhere else. |
| **Data trust** | The audit trail: funnel, exclusions, completeness heatmap, timestamp test, missing-gap chart. |
| **Ask the analysis** | Grounded question answering over the project's own documents and tables. |

The application reads generated tables and **never trains a model at runtime**.
Its controls explore the evidence; they do not overwrite the official results.
The assistant is optional: without an API key the page returns the retrieved
passages from the project's own files, clearly labelled as project text rather
than an AI-generated answer.

## Project layout

```
clir_wind_case/
├── data/
│   ├── raw/            # Downloaded data, never edited, not in git
│   └── processed/      # Cleaned outputs (Phase 2)
├── app/                        # Decision-support application (reads outputs only)
│   ├── app.py                  # Navigation and the five pages
│   ├── charts.py               # Plotly charts and the shared colour palette
│   ├── data.py                 # Cached table loading
│   ├── assistant.py            # Local retrieval + optional OpenAI answers
│   └── content.py              # Shared labels, caveats, official findings
├── src/
│   ├── checks.py               # Validation recorder used by every script
│   ├── data_audit.py           # Phase 1: audit
│   ├── timestamp_correction.py # Phase 2A: the P-11 hypothesis and its tests
│   ├── prepare_data.py         # Phase 2B-D: processed dataset, thresholds
│   ├── baseline_model.py       # Phase 2E-H: curves, candidates, sensitivity
│   ├── ml_challenger.py        # Phase 3: pooled curve, challenger, benchmark
│   ├── decision_register.py    # Phase 4: decision register
│   ├── build_deliverables.py   # Phase 4: deck and memo PDF
│   ├── export_presentation_tables.py  # Phase 4B: chart tables (no new analysis)
│   └── validate_app.py         # Phase 4B: application validation
├── outputs/
│   ├── tables/         # CSV results, including every validation check
│   ├── figures/        # Eight figures
│   └── audit_log.txt   # Phase 1 console output
├── docs/
│   ├── phase_1_findings.md
│   ├── phase_2_findings.md
│   ├── phase_3_method.md       # Locked and committed BEFORE modelling
│   ├── phase_3_findings.md
│   └── methodology_decisions.md
└── notebooks/          # (unused so far)
```

## Status

| Phase | Scope | Status |
|---|---|---|
| 1 | Data audit | **Complete** |
| 2 | Timestamp validation, cleaning rules, reference subset, baseline, sensitivity | **Complete** |
| 3 | Pooled counterfactual, constrained challenger, synthetic detection benchmark | **Complete** |
| 4 | Decision register, memo, slides, application | **Complete** |
| 4B | Interactive decision tool and grounded assistant | **Complete** |

Phase 3 recommends method B as the primary display, with A alongside and C as an
optional second opinion — see
[`docs/phase_3_findings.md`](docs/phase_3_findings.md) §5.

## Author

[Abhijit Mishra](https://github.com/Abhijit2409) ·
[Portfolio](https://abhijitmishraportfolio.netlify.app/) ·
[LinkedIn](https://www.linkedin.com/in/mishraabhijit)
