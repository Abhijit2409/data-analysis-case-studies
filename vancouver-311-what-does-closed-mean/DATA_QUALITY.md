# Data-quality log

Nineteen checks were run on the published data before any finding was written. Each one records what was found, the
rule applied, and how it changed the analysis. The full log lives on the `Data_Quality_Log` sheet of the workbook; this
is the same content in readable form.

Percentages below use the cohort total of 272,580 records.

---

## The principle

Every issue here is handled by **stating a rule and applying it visibly** — not by silently cleaning the data. Nothing
is imputed, deleted or recoded to make a finding stronger. Where a limit can't be fixed, it becomes a stated limitation
of the study instead of a hidden assumption.

## Cohort and time

| ID | Check | Found | Rule applied | Effect |
|---|---|---|---|---|
| DQ01 | Row count and cohort | 272,580 records opened on a 2025 Vancouver-local date. The UTC-year count is 272,562: the local cohort adds 138 records opened the evening of 31 Dec 2025 local and removes 120 from the evening of 31 Dec 2024 local. | Filter on local opening date after converting UTC → `America/Vancouver`. | All analysis uses the local-date cohort. |
| DQ02 | Time zone of opening timestamp | All values carry `+00:00`. Converted to local time, 70% of requests open between 09:00 and 16:59 and 2.7% between midnight and 06:59 — consistent with true UTC. | Convert to local before deriving any date. | Local dates used consistently. |
| DQ03 | Close-date calendar | Date only, no time. For 2,411 evening (17:00+) auto-closed cases, the close date equals the local opening date 86.6% of the time and the UTC date 1.9%. | Treat as a local calendar date; report "recorded calendar days to closure". | Durations are whole calendar days, not elapsed time. |
| DQ18 | Coverage | All 12 months present; 365 distinct local opening dates. Monthly volume ranges 19,517–26,742. | None required. | One year only, so no seasonal claims. |
| DQ19 | Source refresh and censoring | The portal refreshes records daily, so values can change. Latest close date in the extract: 2026-09-04. 2025 cases had 8–20 months to close before extraction. | Analysis is tied to the saved extract and its date. | Right-censoring of durations is small but not zero. |

## Status, closure reasons and durations

| ID | Check | Found | Rule applied | Effect |
|---|---|---|---|---|
| DQ04 | Close date before local opening date | 10 closed cases (0.004%) close one day before they open. All are "Referred to another service group", opened 06:00–07:59 local. | **Not** replaced with zero. Excluded from duration statistics, kept in counts. | Negligible effect on percentiles. |
| DQ05 | Open cases (no close date) | 2,782 (1.0%), all opened in 2025, aged 253–616 days at extraction (median 389). | Reported separately; excluded from closed-case durations. | Closed-case durations do not describe these cases. |
| DQ06 | Closed without a close date | 0 records. | None required. | None. |
| DQ07 | Status and closure-reason combinations | "N/A" appears only on open cases (2,749). 33 open cases carry a closure reason such as "Referred to another service group". | Outcome shares use closed cases only; open cases with a reason are flagged, not recoded. | Small; flagged as an exception type for the proposed report. |
| DQ08 | Closed cases recorded as "N/A" | None — "N/A" behaves as the placeholder for open cases in 2025. | Grouped with "Unknown" as an unclear outcome. | None for closed-case shares. |
| DQ09 | "Unknown" closure reason | 15,971 closures (5.9% of closed cases). 99.4% sit in two request types: Garbage Bin Request and Parking Enforcement Transfer. Almost all are recorded on the day the case opened. | Kept as "Unknown or N/A" and reported by request type, not as a citywide rate alone. | The citywide unclear share is driven by two intake paths. |

## Fields that are incomplete by design

| ID | Check | Found | Rule applied | Effect |
|---|---|---|---|---|
| DQ10 | Missing local area | 59,527 (21.8%), mainly request types without a street location: feedback cases, bin requests, transfer cases. | Labelled "(Not recorded)". Not imputed. | Area summaries describe located requests only. |
| DQ11 | Missing coordinates | 178,672 (65.5%). City metadata notes some addresses are withheld and some do not geocode. | Coordinates not used; local-area names used instead. | No point-level mapping — also a privacy choice. |
| DQ12 | Missing address | 179,097 (65.7%), withheld for some request types by design. | Presence flag only; address values removed from every output. | None. |

## Identity, duplicates and labels

| ID | Check | Found | Rule applied | Effect |
|---|---|---|---|---|
| DQ13 | Obsolete "ZZ OLD" labels | 59 records in three obsolete request types still received records in 2025. | Kept with their original labels. | Negligible. |
| DQ15 | No stable case identifier | No published field uniquely identifies a case. | Referrals, reopenings and true duplicates cannot be linked. | Limits process tracing and duplicate detection — and is why the report proposes linking completion back to the case. |
| DQ16 | Exact duplicate rows | 0 across all published fields. | None required. | None. |
| DQ17 | Duplicate-looking rows | 2,465 records in 1,219 groups, mostly Garbage Bin and Green Bin Request cases. 48% of opening timestamps end in `:00` seconds, so coincidences are plausible. | Flagged only, never removed. | Demand counts may include multi-item or repeat requests. |

## The sensitivity flag

| ID | Check | Found | Rule applied | Effect |
|---|---|---|---|---|
| DQ14 | Administrative/internal-sounding types | Rule: request-type name contains (case-insensitive) "internal", "audit", "tracking", or the phrase "transfer case". Four types flagged, 12,033 records (4.4%). "Disposal Facility – Transfer Station Inquiry Case" is deliberately **not** flagged, because "Transfer" there names a facility. | Sensitivity analysis: all records against records excluding flagged types. | Flagged types hold 42% of "Unknown" closures and 37% of auto-closed cases. |

This is the check that most affects how the headline reads, so the report shows both versions side by side rather than
picking one. Excluding the flagged types moves "Service provided" from 57.5% to 60.2% of closed cases and "Unknown"
from 5.9% to 3.6%. The finding holds either way.

The flag is **my name-based rule, not a City classification.** Whether those request types are resident-initiated is
one of the questions to settle with City staff.
