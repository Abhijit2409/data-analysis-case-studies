# Calculations and verification

Every number in the report comes from a cell in the workbook, and every one of those cells is a formula over the
Power Query output — not a pasted value. This file explains how the figures are calculated and how they were checked.
For the figure-by-figure list, see [`report/numbers_trace.csv`](report/numbers_trace.csv).

---

## The rules behind the arithmetic

**1. Denominators are declared, never assumed.** Outcome shares use closed cases (269,798). Demand counts use all
records (272,580). Department and request-type shares use that group's own closed cases. Duration percentiles use
eligible closed cases (269,788). Each percentage in the report carries its denominator next to it.

**2. Original values are preserved.** The 17 published closure reasons are never overwritten. The outcome group is an
added column, and both are printed in the report's appendix.

**3. Nothing is invented.** No service targets, no causal explanations, no estimated savings, no stakeholder findings.
Where the data cannot answer a question, the report says so and lists it as something to confirm with City staff.

**4. Excluded records are counted, not dropped quietly.** Open cases and negative durations are reported with their
counts wherever they affect a figure.

## Headline counts

| Figure | How it is calculated | Value |
|---|---|---:|
| Cohort | Records whose UTC opening timestamp converts to a 2025 `America/Vancouver` date | 272,580 |
| Closed | Cohort records with status closed at extraction | 269,798 |
| Open | Cohort − closed | 2,782 |
| Closed share | 269,798 ÷ 272,580 | 99.0% |

The workbook checks that closed + open equals the cohort, and that the cohort total equals the independent Python
figure. Both read TRUE on the Analysis sheet.

## Outcome shares

```
share of closed cases = closed cases in outcome group ÷ 269,798
```

| Group | Closed cases | Share |
|---|---:|---:|
| Service provided | 155,210 | 57.5% |
| Handed off or planned | 65,126 | 24.1% |
| No service or no action | 26,871 | 10.0% |
| Unknown | 15,971 | 5.9% |
| Insufficient info / could not proceed | 4,998 | 1.9% |
| Other – requires review | 1,622 | 0.6% |

The six groups are checked to sum back to 269,798.

## Department and request-type shares

Each department's outcome shares use **its own** closed cases as the denominator, so the rows are comparable as
profiles even though the departments differ hugely in size:

```
department outcome share = that department's closed cases in the group ÷ that department's closed cases
```

The report covers the 12 largest departments by closed cases, which together hold 79.6% of all closed cases. Across
them, "Service provided" runs from 1.8% (Property Use Inspections, 10,456 closed) to 86.7% (Services Centre, 22,552
closed).

The street and sidewalk repair family works the same way, per request type:

| Request type | Closed | Service provided | Handed off or planned | No service or no action |
|---|---:|---:|---:|---:|
| Pothole | 3,820 | 77.0% | 18.5% | 3.7% |
| Street repair | 1,808 | 38.1% | 43.9% | 17.3% |
| Sidewalk repair | 1,882 | 48.0% | 40.4% | 10.9% |
| **All three types** | **7,510** | **60.4%** | **30.1%** | **8.8%** |

140 open cases in this family are excluded from these shares and reported separately.

## Durations

```
recorded calendar days to closure = close date − local opening date
```

Eligible: 269,788 closed cases. Excluded: 2,782 open cases, and 10 cases whose close date precedes the local opening
date — excluded rather than zeroed, so the median isn't quietly pulled down. All 10 sit in the "handed off or planned"
group, so that group's duration count is 65,116 against 65,126 cases.

**Percentiles are nearest-rank:** the p-th percentile is the smallest number of days within which at least p% of
eligible cases closed. They are computed from a days-to-closure frequency table
([`data/duration_frequency_2025.csv`](data/duration_frequency_2025.csv)) rather than from row-level data, which is what
lets the workbook reproduce them without holding 270,000 rows.

Within sidewalk repair:

| Outcome | Eligible n | Median days |
|---|---:|---:|
| Service provided | 904 | 5 |
| Of which "Further action has been planned" | 551 | 9 |

Subgroups this size are reported with their `n` beside them, because 551 cases inside one request type is a much
weaker base than a citywide figure and shouldn't be read as if it were the same.

## Where "Unknown" comes from

```
share of all "Unknown" = that type's "Unknown" closures ÷ 15,971
rate within type       = that type's "Unknown" closures ÷ that type's closed cases
```

| Request type | "Unknown" closures | Closed cases of this type | Rate within type | Share of all "Unknown" |
|---|---:|---:|---:|---:|
| Garbage Bin Request | 9,203 | 17,225 | 53.4% | 57.6% |
| Parking Enforcement Transfer | 6,680 | 6,740 | 99.1% | 41.8% |
| Every other request type combined | 88 | — | — | 0.6% |

Two types account for 99.4% of all "Unknown" closures. The report states this as a concentration and leaves the cause
open: whether "Unknown" is a system default on certain intake paths is a question for City staff, and the public data
doesn't answer it.

## How the figures were verified

**Cell-level traceability.** Each figure in the report is read from a named workbook cell, and the trace file records
figure → cell for all 205 of them. Nothing is typed into the report by hand.

**Label-asserted reads.** The report build doesn't just read `Analysis!C16`; it first asserts that the label in the
neighbouring cell still says what it expects (for example that `A16` reads "1. Service recorded as provided"). If a row
were ever inserted into the workbook, the build fails instead of silently publishing a wrong number.

**Independent recalculation.** The workbook figures were reconciled against a separate Python calculation over the
row-level extract (`scripts/07_reconcile.py`), and the report's headline counts are cross-checked again at build time.
The workbook's own reconciliation rows on the Analysis sheet are shaded green and should all read TRUE.

**Privacy scan.** Before publication, the report HTML and the extracted PDF text were checked against an address
pattern and against all 40,421 distinct address strings in the published dataset. Zero matches in both.

**Page-level review.** Every page of the report was rendered to an image and inspected for clipped labels, overlapping
text and legibility at printed size.

## Re-checking any figure yourself

1. Open `report/Vancouver311_Closure_Outcomes_Workbook.xlsx` and go to the **Analysis** sheet.
2. Find the figure in [`report/numbers_trace.csv`](report/numbers_trace.csv); the `source` column names the exact cell.
3. Click that cell to see the formula and the Power Query output it reads.
4. The green-shaded rows on the same sheet are the reconciliation checks; all should read TRUE.

Figures labelled as judgement in the trace — the options scores — are not workbook calculations, and are marked that way
in both the report and the trace.
