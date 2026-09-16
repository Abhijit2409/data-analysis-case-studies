# Methodology

How the cohort, the outcome groups and the duration measure were built — and the judgement calls behind each one.

Everything here is an outside-in reading of public data. Where I made an interpretation, it is labelled as mine, and
the original published values are always preserved alongside it.

---

## 1. Source and extraction

| | |
|---|---|
| Dataset | City of Vancouver Open Data Portal, "3-1-1 service requests" |
| Licence | Open Government Licence – Vancouver |
| Extracted | 2026-09-11 02:59 UTC (dataset last modified 2026-09-10 14:08 UTC per portal metadata) |
| API filter | `service_request_open_timestamp >= "2024-12-31T00:00:00+00:00"` and `< "2026-01-02T00:00:00+00:00"`, timezone UTC |
| Records in cohort | 272,580 |

The API filter takes a **buffered window** — a day either side of 2025 in UTC — because the portal filters in UTC while
the cohort is defined in local time. The exact cohort is then cut locally, so no request near either year boundary is
lost or wrongly included.

**Privacy.** Address, latitude, longitude and geometry fields were dropped before any file in this package was created.
Only yes/no presence flags (`has_address`, `has_coordinates`) and local-area names were kept. No individual address
appears in the report, the workbook, or the data files here.

## 2. Cohort definition

> **Requests whose opening timestamp, converted from UTC to `America/Vancouver`, falls on a 2025 local date.**

272,580 records. This is a **cohort of requests opened in 2025**, not of activity during 2025: a case opened in
December 2025 and closed in January 2026 stays in, and a case opened in 2024 and closed in 2025 stays out. That keeps
each case's opening and closure in the same population, which is what makes closure shares meaningful.

The opening field is a UTC timestamp. 75.7% of records carry a UTC hour between 14:00 and 23:00, which is daytime in
Vancouver — consistent with the timestamps being UTC rather than local, and with requests arriving during business
hours (69.7% fall in local hours 09:00–16:00).

**The close field is a date, not a timestamp,** so it has no timezone of its own. To work out which calendar it uses, I
took the 2,411 cases closed automatically in the local evening — where the local and UTC dates differ — and compared:

| The close date equals… | Share of those cases |
|---|---:|
| The **local** opening date | 86.6% |
| The UTC opening date | 1.9% |

So the close date behaves like a local calendar date, and durations are calculated against the **local** opening date.

## 3. Outcome groups: my interpretation, the City's values

The published `closure_reason` field has 17 distinct values. Reporting all 17 separately buries the point; collapsing
them into "done / not done" overstates what the data says. So I mapped all 17 to six groups, kept every original value,
and wrote down both a rationale and the question I would ask City staff to confirm each one. The full mapping with
rationales and validation questions is in [`data/closure_outcome_mapping.csv`](data/closure_outcome_mapping.csv).

| Group | Closure reasons (original values) | Closed cases 2025 |
|---|---|---:|
| **1. Service recorded as provided** | Service provided | 155,210 |
| **2. Work assigned, referred or continuing** | Further action has been planned (23,220); Closed automatically and sent to service group (14,236); Assigned to inspector (14,185); Referred to another service group (10,368); Dispatched to Crew (3,117) | 65,126 |
| **3. No service or no action recorded** | Reviewed and no action planned (14,931); Issue not found or inaccessible (8,021); Not a city provided service / jurisdiction (3,726); Outside of Parameters (Sanitation) (133); Contaminated (Sanitation) (60) | 26,871 |
| **4. Insufficient information / could not proceed** | Insufficient info (4,608); Customer unreachable (390) | 4,998 |
| **5. Unknown or N/A** | Unknown (15,971); N/A (0 closed — it appears on 2,749 **open** cases) | 15,971 |
| **6. Other – requires review** | Alternate Service Required (1,616); Information received (6) | 1,622 |

Three decisions inside this mapping are worth stating plainly:

- **Group 2 is not "unfinished work".** The wording records a handoff or planned work. Whether it was completed is not
  published, so the group is labelled "handed off or planned" in the report and never counted as failure.
- **Group 3 is an outcome, not a gap.** "Reviewed and no action planned" and "Not a city provided service" are
  decisions. Treating every non-"Service provided" closure as incomplete would be wrong, and the report says so.
- **Ambiguous values go to group 6, not to a convenient group.** "Alternate Service Required" and "Information received"
  could each be read two ways, so they sit in a review group rather than being forced into a story.

In the report, groups 4 and 6 are shown together as "Other outcomes" (6,620 cases, 2.5% of closed cases) for legibility.
Both the six analyst groups and the 17 original values are printed in the appendix, so nothing is hidden by that merge.

## 4. Denominators

Mixing denominators is the easiest way to mislead with this dataset, so the rules are fixed:

| Measure | Denominator |
|---|---|
| Outcome shares | **Closed cases** (269,798), with open cases reported separately |
| Department and request-type shares | **That group's own closed cases** |
| Demand counts (monthly, by department) | **All records** (272,580) |
| Duration percentiles | **Eligible closed cases** (269,788) |

Every percentage in the report names its denominator next to it.

## 5. Recorded calendar days to closure

The measure is deliberately named **recorded calendar days to closure**, not resolution time:

```
recorded calendar days to closure = close date − local opening date
```

- **Eligible:** 269,788 closed cases.
- **Excluded:** 2,782 open cases (no close date), and 10 cases with a close date before the local opening date. The 10
  are **excluded, not set to zero** — a negative duration is a data question, and zeroing it would quietly pull the
  median down. All 10 fall in the "handed off or planned" group, which is why its duration count (65,116) is 10 lower
  than its case count (65,126).
- **Percentiles are nearest-rank:** the p-th percentile is the smallest number of days within which at least p% of
  eligible closed cases closed. Percentiles are only reported for groups with at least 30 eligible cases.

Because the close field is a date, a case opened and closed the same day measures 0 days. That is a limit of the
published data, not a service-speed claim.

Citywide, the medians differ enough that a combined figure describes none of them:

| Outcome | Eligible n | Median days | 90th percentile |
|---|---:|---:|---:|
| Service provided | 155,210 | 4 | 18 |
| Handed off or planned | 65,116 | 1 | 9 |
| No service or no action | 26,871 | 3 | 17 |
| Unknown | 15,971 | 0 | 0 |
| **All outcomes combined** | **269,788** | **2** | **16** |

The combined median of 2 days sits between a handoff (1) and recorded service (4). That is the reporting problem in one
row: a single number that describes no actual group.

## 6. Administrative-sounding request types: a rule, then a test

Some request types read like internal workflow rather than resident requests. Rather than assume, I wrote a
transparent name-based rule and tested what happens if those types are excluded:

> Request-type name contains (case-insensitive) "internal", "audit", "tracking", or the phrase "transfer case".

"Transfer case" is matched as a phrase so that a facility name like "Disposal Facility – Transfer Station Inquiry Case"
is **not** flagged. The rule flags four request types, 12,033 records (4.4% of the cohort). Excluding them:

| Share of closed cases | All records | Excluding flagged types |
|---|---:|---:|
| Service provided | 57.5% | 60.2% |
| Handed off or planned | 24.1% | 23.2% |
| No service or no action | 10.0% | 10.4% |
| Unknown | 5.9% | 3.6% |

The finding survives the test: the "Service provided" share moves by under 3 points and stays well below the closure
rate. The flag is my rule, not a City classification, and whether those types are resident-initiated is a question for
City staff.

## 7. Choosing one service family for the deep dive

Seven candidate families were scored against four evidence tests: volume, several outcome groups above 5%, a low
unclear share, and comparable request types within the family.

**Street and sidewalk repair** (Pothole, Street Repair, Sidewalk Repair — 7,650 records) met all four, and among the
families that did, it had the highest share of handoff or planned closures (30.1%, against 10.7% for street lights and
signs). That makes it the family where clarified definitions would change most, which is why the pilot is proposed
there.

## 8. Options analysis

Four options were scored against seven criteria (decision benefit, evidence, effort, risk, data needs, stakeholder
impact, scalability), each 1–5 with 5 the favourable end:

| Option | Score (of 35) |
|---|---:|
| Keep the current interpretation | 18 |
| **Clarify outcome definitions in reporting** | **31** |
| Improve intake guidance for repairs | 17 |
| Add a recurring exception-review report | 25 |

**These scores are judgement, not measurement** — my preliminary outside-in assessment, labelled as such in the report
and in the numbers trace. With stakeholders, effort and risk in particular would be re-scored by the people who carry
them.

## 9. Tooling

| Stage | Tool |
|---|---|
| Extract, profile, analyse | Python 3.13 (pandas) — `scripts/01_download.py`, `02_profile.py`, `03_analyze.py` |
| Workbook | Excel with Power Query (`scripts/pq_source_data.m`, `pq_source_durations.m`); analysis sheets are formulas, not pasted values |
| Reconciliation | `scripts/07_reconcile.py` compares workbook figures against the independent Python calculation |
| Report | HTML/CSS rendered to PDF; charts drawn at final printed size so no text is scaled down |

## 10. Corrections made during the redesign

The report was rebuilt from the workbook after an earlier draft, and three claims did not survive that check. They are
recorded here because how you handle a figure that doesn't reconcile matters more than never having written it:

- **Department range.** An earlier draft said "Service provided" ranged from 1.8% to 98.8% across 30 departments. The
  workbook holds the 12 largest departments only, so 98.8% could not be verified against the saved figures. The range
  now reads 1.8% to 86.7% across those 12, with the coverage (79.6% of closed cases) stated.
- **Overstated wording.** An earlier draft called a closed case "often a handoff, not a finished job". The public data
  does not show the work was left undone; the wording now says the record shows a handoff or planned work and that
  completion is not published.
- **Figures without a source.** A count of "insufficient info" repair closures, a same-day "Unknown" count, open-case
  ages, and a channel split of "Unknown" were all removed because the workbook holds no figure to support them.
