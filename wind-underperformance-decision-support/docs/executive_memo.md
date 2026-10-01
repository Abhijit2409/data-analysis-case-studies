# Which issue should be investigated first?

**La Haute Borne wind farm, 2015 assessment year.** Independent analysis of public
data. 30 September 2026.

---

**Question.** After validating the data, which issue should be investigated first,
what is the potential exposure, how confident are we, and what operational
information is required before anyone acts?

**Answer.** Turbine **R80711**, **26 July 2015 15:10 to 28 July 09:30 UTC (42.5
hours)**. Potential shortfall **36.8–37.6 MWh**, illustratively **€1,842–4,513**
at €50–120/MWh. All three analytical methods flag it. Confidence is **medium** —
the ceiling, because no operational record exists. The next step is a request for
event codes and work orders covering that interval.

> **Potential shortfall is not confirmed recoverable energy.** It is the gap
> between observed output and a statistical reference built from the same
> machines' own past. No cause has been established.

## What changed after validation

Three things, none of which were visible in the raw data.

**The timestamps were confidently wrong.** They carry proper daylight-saving
offsets, which makes them look reliable. Every local day held exactly 144
ten-minute records, including both clock-change days — which a daylight-saving
logger cannot produce. The logger's clock never moved, so **every summer record
sat one hour early**, about seven months of each year. Correcting it removed all
48 duplicate and all 48 absent intervals and closed a one-hour seasonal gap
against independent reanalysis data.

**The meter series is synthetic**, derived from SCADA by the data publisher. That
removed the one external cross-check normally available, so every check here is
internal. It is a real limitation, not a presentational one.

**Comparing each turbine against itself was hiding the fleet picture.** R80711's
own reference sits 11–19 kW below its neighbours', so judging it against its own
history flattered it. Under a pooled fleet reference it moves from apparently
well-behaved to the largest shortfall on the site. An earlier version of this
analysis named R80790 as the turbine with the shallower curve; measuring it
directly showed the opposite, and the correction is recorded in the project
history rather than edited away.

## Validated energy accounting, 2015

| Quantity | Value |
|---|---|
| Gross positive residual shortfall | 671.6 MWh |
| Shortfall inside persistent reviewable events | 380.8 MWh |
| Non-persistent shortfall (short dips) | 290.8 MWh |
| Energy lost during missing data | **unknown**, not zero |
| Records that cannot be assessed | 2,771 |

Only 57% of the gross figure sits inside reviewable events. Treating the headline
as actionable would be the easiest mistake available here.

## Recommended first investigation

R80711 produced almost nothing for 42.5 hours — **97.6% of records at or below
zero, against an expected 901 kW** — while all three neighbouring turbines
produced continuously at 724–840 kW in the same 5–12 m/s wind. In the preceding 48
hours R80711 was operating in line with expectation.

It is ranked first because it is large, corroborated by all three methods,
discrete enough to investigate, carries no data-quality qualifications, and **one
record request can resolve it**.

**An important qualification.** Removing this single event drops R80711 from 5.35%
to 4.46% of potential, below R80790's 5.10%. R80711 leads the fleet-relative
ranking largely *because of* this event, not because of a persistent pattern.
R80790's more diffuse gap is a separate second line of enquiry.

## Required next evidence

Turbine event and alarm codes for the interval; work orders and maintenance
records; curtailment or grid instructions; operator logs. Normally held by the
site operations team, with curtailment records from the commercial team.

Five possible explanations fit the evidence equally well — planned maintenance, an
unplanned fault stop, grid curtailment, a controller lockout awaiting manual
reset, or a communications loss while the turbine was in fact running. **Nothing
in this dataset can choose between them.** If the records show a planned outage,
the item closes.

## The three most important limitations

1. **No event codes, work orders or curtailment records exist.** Every operational
   explanation in this project is a hypothesis. No finding anywhere reaches
   "validated" on the project's own evidence hierarchy.
2. **No independent meter validation**, because the supplied meter series is
   synthetic. All verification is internal.
3. **Four turbines, and 2015 data.** A pooled fleet reference built from four
   machines is weak, a site-wide problem affecting all of them would be invisible
   to every method used, and nothing here describes the site today.

*Data: ENGIE La Haute Borne, Etalab Open Licence 2.0, via the OpenOA repository
(NatLabRockies/OpenOA). Independent project. No Clir Renewables data, software or
methodology was used, and nothing here describes Clir, its platform or its
customers. Prices are illustrative; no tariff, PPA or market price is known for
this site.*
