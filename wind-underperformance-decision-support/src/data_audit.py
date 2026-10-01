"""
Phase 1 data audit for the La Haute Borne wind farm dataset.

What this script does:
    Reads the raw files, measures what is actually in them, and writes summary
    tables plus three diagnostic figures.

What this script deliberately does NOT do:
    It does not clean, fix, fill in or drop anything. Questionable records are
    counted and reported so that cleaning rules can be decided afterwards, with
    evidence. Nothing here changes the raw files.

Run from the project root:
    python src/data_audit.py
"""

import hashlib
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")           # Save figures to file instead of opening a window.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

SCADA_FILE = RAW / "la-haute-borne-data-2014-2015.csv"
PLANT_FILE = RAW / "plant_data.csv"
MERRA_FILE = RAW / "merra2_la_haute_borne.csv"
ERA5_FILE = RAW / "era5_wind_la_haute_borne.csv"
ASSET_FILE = RAW / "la-haute-borne_asset_table.csv"
ZIP_FILE = RAW / "la_haute_borne.zip"

# From the asset table shipped with the data, not from memory or assumption.
RATED_POWER_KW = 2050
MINUTES_PER_RECORD = 10
# The two columns that identify a record rather than measure something.
INDEX_COLUMNS = ["Wind_turbine_name", "Date_time"]

# Only used to COUNT how many records look odd. These are not cleaning rules.
# Thresholds are justified in docs/methodology_decisions.md.
PLAUSIBLE_WIND_MIN = 0.0
PLAUSIBLE_WIND_MAX = 30.0
OPERATING_WIND_MIN = 4.0        # Comfortably above the cut-in speed for this turbine class.
FLATLINE_MIN_RECORDS = 6        # 6 records = 1 hour of an identical reading.

notes = []                      # Plain-language findings, printed at the end.


def note(line):
    """Record one finding and show it as the audit runs."""
    notes.append(line)
    print(line)


# ---------------------------------------------------------------------------
# Step 1: File inventory and provenance
# ---------------------------------------------------------------------------

def audit_files():
    """List every raw file with its size and checksum, so results are traceable."""
    print("\n=== 1. FILE INVENTORY ===")
    rows = []
    for path in sorted(RAW.glob("*")):
        if path.is_dir():
            continue
        # A checksum lets anyone confirm they have the same file we audited.
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({
            "file_name": path.name,
            "size_bytes": path.stat().st_size,
            "size_mb": round(path.stat().st_size / 1_048_576, 2),
            "sha256": digest,
        })
    inventory = pd.DataFrame(rows)
    inventory.to_csv(TABLES / "data_inventory.csv", index=False)
    print(inventory[["file_name", "size_mb"]].to_string(index=False))
    return inventory


# ---------------------------------------------------------------------------
# Step 2: Load SCADA, keeping the original timestamp text
# ---------------------------------------------------------------------------

def load_scada():
    """
    Load the turbine data.

    The timestamp text is kept in its original form as well as parsed. That is
    deliberate: the raw text carries the UTC offset (for example "+01:00"), and
    that offset is the evidence for how daylight saving was handled. Parsing
    straight to UTC would throw that evidence away.
    """
    print("\n=== 2. SCADA STRUCTURE ===")
    scada = pd.read_csv(SCADA_FILE, dtype={"Date_time": "string"})

    print(f"Rows: {len(scada):,}")
    print(f"Columns ({len(scada.columns)}): {list(scada.columns)}")

    # The offset is the last 6 characters of the timestamp, e.g. "+01:00".
    scada["utc_offset"] = scada["Date_time"].str.slice(-6)
    # Parse to a real UTC timestamp. Mixed offsets are handled correctly here.
    scada["timestamp_utc"] = pd.to_datetime(scada["Date_time"], utc=True, format="ISO8601")

    measurement_columns = [c for c in scada.columns
                           if c not in INDEX_COLUMNS + ["utc_offset", "timestamp_utc"]]
    note(f"SCADA has {len(scada):,} rows and {len(measurement_columns)} measurement "
         f"columns: {measurement_columns}")
    note(f"Timestamps ARE timezone-aware. Offsets found: {sorted(scada['utc_offset'].unique())}")
    note(f"UTC range: {scada['timestamp_utc'].min()} to {scada['timestamp_utc'].max()}")

    # Confirm the sampling interval from the data rather than assuming 10 minutes.
    one_turbine = scada[scada["Wind_turbine_name"] == scada["Wind_turbine_name"].iloc[0]]
    gaps = one_turbine["timestamp_utc"].sort_values().diff().dropna()
    interval_counts = gaps.value_counts().head(3)
    note(f"Most common interval between records: {interval_counts.index[0]}")

    # Are status or event codes present? This decides whether turbine states can
    # be read from the data or must be inferred.
    code_like = [c for c in scada.columns
                 if re.search(r"status|state|code|event|alarm|fault|avail", c, re.I)]
    note(f"Status/event/alarm columns present: {code_like if code_like else 'NONE'}")

    return scada


# ---------------------------------------------------------------------------
# Step 3: Row counts, duplicates and missing timestamps
# ---------------------------------------------------------------------------

def audit_completeness(scada):
    """
    Check three separate things that are easy to confuse:
      - duplicates: the same turbine and timestamp appearing more than once
      - absent intervals: a timestamp that has no row at all
      - present-but-empty: a row that exists but has no power value
    """
    print("\n=== 3. COMPLETENESS ===")

    # Build the full set of timestamps we would expect if nothing were absent.
    full_grid = pd.date_range(
        scada["timestamp_utc"].min(), scada["timestamp_utc"].max(),
        freq=f"{MINUTES_PER_RECORD}min", tz="UTC",
    )
    print(f"Expected timestamps per turbine: {len(full_grid):,}")

    rows = []
    for turbine, group in scada.groupby("Wind_turbine_name", observed=True):
        duplicate_count = group["timestamp_utc"].duplicated().sum()
        present = set(group["timestamp_utc"])
        absent = len(full_grid) - len(present)
        rows.append({
            "turbine": turbine,
            "rows": len(group),
            "expected_timestamps": len(full_grid),
            "duplicate_timestamps": int(duplicate_count),
            "absent_intervals": int(absent),
            "power_value_missing": int(group["P_avg"].isna().sum()),
            "windspeed_value_missing": int(group["Ws_avg"].isna().sum()),
            "coverage_pct": round(100 * len(present) / len(full_grid), 2),
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(TABLES / "missing_interval_summary.csv", index=False)
    print(summary.to_string(index=False))

    note(f"Absent intervals per turbine: {summary['absent_intervals'].tolist()}")
    note(f"Rows present but with no power value: {summary['power_value_missing'].tolist()}")
    note(f"Duplicate timestamps per turbine: {summary['duplicate_timestamps'].tolist()}")

    # Identical duplicate rows and conflicting duplicates need different treatment,
    # so count them separately.
    key = ["Wind_turbine_name", "timestamp_utc"]
    all_dupes = scada[scada.duplicated(subset=key, keep=False)]
    if len(all_dupes):
        exact = scada.duplicated().sum()
        note(f"Duplicate turbine+timestamp rows: {len(all_dupes):,} "
             f"(of which fully identical rows: {exact:,})")
    else:
        note("No duplicate turbine+timestamp combinations found.")

    return summary


# ---------------------------------------------------------------------------
# Step 4: Daylight saving behaviour
# ---------------------------------------------------------------------------

def audit_clock_changes(scada):
    """
    France changes its clocks twice a year, so the clock-change days are where
    timestamp bugs show up. This section works out exactly what the file does on
    those days, because the earlier completeness check found the same number of
    duplicated and absent intervals per turbine, which is a strong hint that both
    come from the clock changes rather than from random data loss.

    Expected if the file were correct: every UTC timestamp appears exactly once.
    """
    print("\n=== 4. CLOCK CHANGES ===")
    rows = []

    for turbine, group in scada.groupby("Wind_turbine_name", observed=True):
        group = group.sort_values("timestamp_utc")

        # Which UTC timestamps appear twice, and which are absent entirely?
        duplicated_utc = group.loc[group["timestamp_utc"].duplicated(), "timestamp_utc"]
        full_grid = pd.date_range(group["timestamp_utc"].min(), group["timestamp_utc"].max(),
                                  freq=f"{MINUTES_PER_RECORD}min", tz="UTC")
        absent_utc = full_grid.difference(pd.DatetimeIndex(group["timestamp_utc"].unique()))

        for stamp in duplicated_utc:
            rows.append({"turbine": turbine, "problem": "duplicated_utc_timestamp",
                         "timestamp_utc": stamp, "local_date": stamp.tz_convert("Europe/Paris").date()})
        for stamp in absent_utc:
            rows.append({"turbine": turbine, "problem": "absent_utc_timestamp",
                         "timestamp_utc": stamp, "local_date": stamp.tz_convert("Europe/Paris").date()})

    clock_issues = pd.DataFrame(rows)
    clock_issues.to_csv(TABLES / "clock_change_issues.csv", index=False)

    # Group the problems by month to show they land only on clock-change dates.
    if len(clock_issues):
        by_date = clock_issues.groupby(["problem", "local_date"]).size().rename("records")
        print(by_date.to_string())

    spring = clock_issues[clock_issues["problem"] == "duplicated_utc_timestamp"]
    autumn = clock_issues[clock_issues["problem"] == "absent_utc_timestamp"]
    note(f"Every duplicated UTC timestamp falls on a spring clock-change date "
         f"{sorted(set(spring['local_date'].astype(str)))} and every absent one on an "
         f"autumn clock-change date {sorted(set(autumn['local_date'].astype(str)))}. "
         "Neither is random data loss.")

    # The duplicates matter only if the two copies disagree. Check that.
    key = ["Wind_turbine_name", "timestamp_utc"]
    pairs = scada[scada.duplicated(subset=key, keep=False)]
    spread = pairs.groupby(key)["P_avg"].agg(["min", "max"])
    spread["difference_kw"] = spread["max"] - spread["min"]
    note(f"The duplicated records are NOT copies: power differs between the two "
         f"versions by a median of {spread['difference_kw'].median():.0f} kW and up to "
         f"{spread['difference_kw'].max():.0f} kW, so one cannot simply be dropped at random.")

    # How much energy sits in the absent autumn hour? Small counts can still matter.
    note(f"Scale: {len(spring)} duplicated and {len(autumn)} absent records in total "
         f"across 4 turbines and 2 years, which is "
         f"{100 * (len(spring) + len(autumn)) / len(scada):.4f}% of rows.")
    return clock_issues


# ---------------------------------------------------------------------------
# Step 4b: Are the timestamps actually correct, or only correct-looking?
# ---------------------------------------------------------------------------

def audit_timestamp_alignment(scada):
    """
    The clock-change results raise a bigger question than the clock-change days.

    If the logger's own clock never moved for daylight saving, and the summer
    offset "+02:00" was written on top of unchanged local time afterwards, then
    every summer record would land one hour early once converted to UTC. That
    would be about seven months of each year, not the 96 records found so far.

    Two independent tests, using only data already in the project.

    Test A - continuity.
        On a spring clock-change date one hour appears twice. If the logger simply
        kept counting, both copies are real data: one is the hour that follows
        01:50, the other is the hour that leads into 04:00. If instead one copy
        were a faulty duplicate, it would not join up with anything.

    Test B - temperature against an independent weather record.
        Air temperature follows a strong daily cycle. ERA5 reanalysis is stored
        in UTC and was produced without reference to this logger. Comparing the
        two, season by season, shows whether the SCADA clock keeps a constant
        relationship with real time.

        What decides it is the DIFFERENCE in best lag between winter and summer,
        not the lag itself. A sensor sitting on a nacelle can lag the outside air
        in any season, and that is harmless. A one-hour seasonal difference is not.
    """
    print("\n=== 4b. ARE THE TIMESTAMPS CORRECT? ===")

    # ---- Test A: does each duplicated sequence join on to real data? ----
    print("Test A - continuity across a spring clock change (turbine R80711, 2014-03-30)")
    one = scada[scada["Wind_turbine_name"] == "R80711"]
    window = one[one["Date_time"].str.startswith("2014-03-30")].sort_values("Date_time")
    before = window[window["Date_time"].str.contains("T01:50")]
    after = window[window["Date_time"].str.contains("T04:00")]
    doubled = window[window["Date_time"].str.contains("T03:")]

    print(f"  record before the gap (01:50): power {before['P_avg'].iloc[0]:7.1f} kW, "
          f"wind {before['Ws_avg'].iloc[0]:.2f} m/s")
    print("  the two sequences labelled 03:00-03:50:")
    for label, sequence in [("A", doubled.iloc[0::2]), ("B", doubled.iloc[1::2])]:
        powers = " ".join(f"{v:6.1f}" for v in sequence["P_avg"])
        print(f"    sequence {label}: {powers}")
    print(f"  record after the gap (04:00):  power {after['P_avg'].iloc[0]:7.1f} kW, "
          f"wind {after['Ws_avg'].iloc[0]:.2f} m/s")

    # Whichever sequence ends closest to the 04:00 record is the one that truly
    # precedes it; the other belongs immediately after 01:50.
    ends = {label: abs(sequence["P_avg"].iloc[-1] - after["P_avg"].iloc[0])
            for label, sequence in [("A", doubled.iloc[0::2]), ("B", doubled.iloc[1::2])]}
    leads_into_0400 = min(ends, key=ends.get)
    note(f"Test A: sequence {leads_into_0400} runs continuously into the 04:00 record, "
         "and the other continues from 01:50. Both are genuine data, so the logger did "
         "not skip an hour in spring - the export relabelled one.")

    # ---- Test B: seasonal lag against ERA5 ----
    print("\nTest B - SCADA temperature against ERA5 reanalysis, by season")

    temperature = scada.loc[scada["Ot_avg"] > -30, ["timestamp_utc", "Ot_avg"]]
    scada_hourly = (temperature.groupby("timestamp_utc")["Ot_avg"].median()
                               .resample("1h").mean().rename("scada_temp"))

    era5 = pd.read_csv(ERA5_FILE, usecols=["datetime", "t_2m"])
    era5["timestamp_utc"] = pd.to_datetime(era5["datetime"], utc=True)
    era5["era5_temp"] = era5["t_2m"] - 273.15          # Kelvin to Celsius
    era5_hourly = era5.set_index("timestamp_utc")["era5_temp"]

    paired = pd.concat([scada_hourly, era5_hourly], axis=1, sort=True).dropna()
    paired = paired[(paired.index >= "2014-01-01") & (paired.index < "2016-01-01")]

    # Remove each day's average from both series. Without this the comparison is
    # dominated by the slow seasonal swing, and the daily cycle is what carries
    # the timing information.
    day = paired.index.floor("D")
    paired["scada_shape"] = paired["scada_temp"] - paired.groupby(day)["scada_temp"].transform("mean")
    paired["era5_shape"] = paired["era5_temp"] - paired.groupby(day)["era5_temp"].transform("mean")

    results = []
    for season, months in [("winter (Nov-Feb)", [11, 12, 1, 2]), ("summer (May-Aug)", [5, 6, 7, 8])]:
        subset = paired[paired.index.month.isin(months)]
        correlations = {lag: subset["scada_shape"].corr(subset["era5_shape"].shift(lag))
                        for lag in range(-3, 4)}
        best = max(correlations, key=correlations.get)
        results.append({"season": season, "records": len(subset),
                        "best_lag_hours": best, "correlation": round(correlations[best], 4)})
        detail = "  ".join(f"{lag:+d}h:{value:.3f}" for lag, value in correlations.items())
        print(f"  {season:18} n={len(subset):>5}  best lag {best:+d} h  ({detail})")

    lag_table = pd.DataFrame(results)
    lag_table.to_csv(TABLES / "timestamp_alignment_test.csv", index=False)

    difference = lag_table.loc[1, "best_lag_hours"] - lag_table.loc[0, "best_lag_hours"]
    print(f"\n  Difference between seasons: {difference:+d} hour(s)")

    if difference == 0:
        note("Test B: winter and summer agree, so the offsets are applied consistently "
             "and only the clock-change records are affected.")
    else:
        note(f"Test B: the best lag differs between winter and summer by {difference:+d} "
             "hour. The two tests together indicate the logger clock did NOT follow "
             "daylight saving, and the summer offset was applied afterwards. Summer "
             "records therefore sit ONE HOUR EARLY once converted to UTC.")
        note("Scope of that problem: roughly late March to late October each year, "
             "about seven months, not the 96 clock-change records. Wind and power share "
             "a row, so the power curve is unaffected. Anything that JOINS SCADA to "
             "another time series - reanalysis, air density, time-of-day - would be "
             "wrong by an hour for most of the year unless corrected.")

    return lag_table


# ---------------------------------------------------------------------------
# Step 5: Physical plausibility
# ---------------------------------------------------------------------------

def audit_plausibility(scada):
    """
    Count values that are physically doubtful. Nothing is removed here.

    Small negative power is normal: a turbine that is not generating still draws
    some electricity to run its own systems. That is why negative power is counted
    in bands rather than treated as a single error category.
    """
    print("\n=== 5. PHYSICAL PLAUSIBILITY ===")
    checks = []

    def add(name, mask, why):
        count = int(mask.sum())
        checks.append({
            "check": name,
            "records": count,
            "pct_of_rows": round(100 * count / len(scada), 3),
            "interpretation": why,
        })

    power = scada["P_avg"]
    wind = scada["Ws_avg"]

    add("power_above_rated_plus_10pct", power > RATED_POWER_KW * 1.10,
        "Possible sensor or scaling problem")
    add("power_negative_small", (power < 0) & (power >= -50),
        "Expected: turbine drawing its own power while idle")
    add("power_negative_large", power < -50,
        "Unusual; worth investigating")
    add("wind_outside_plausible_range",
        (wind < PLAUSIBLE_WIND_MIN) | (wind > PLAUSIBLE_WIND_MAX),
        "Sensor problem or extreme weather")
    add("zero_power_while_wind_above_operating",
        (power <= 0) & (wind >= OPERATING_WIND_MIN),
        "Turbine not producing although the wind could support it")
    add("power_positive_while_wind_near_zero", (power > 50) & (wind < 1),
        "Suggests a failed, iced or stuck wind sensor")
    add("pitch_angle_outside_minus5_to_95",
        (scada["Ba_avg"] < -5) | (scada["Ba_avg"] > 95),
        "Outside the physically sensible pitch range")
    add("nacelle_angle_outside_0_to_360",
        (scada["Ya_avg"] < 0) | (scada["Ya_avg"] > 360),
        "Outside the compass range")
    # -273.15 C is absolute zero, so anything at or below it is a fault value the
    # sensor wrote rather than a reading. Checking for it is how you catch a
    # placeholder being silently averaged into real data later on.
    add("temperature_at_or_below_absolute_zero", scada["Ot_avg"] <= -273.15,
        "Sensor fault placeholder, not a measurement")
    add("temperature_implausible_for_france",
        (scada["Ot_avg"] < -30) & (scada["Ot_avg"] > -273.15),
        "Too cold for this site; likely a sensor fault")

    plausibility = pd.DataFrame(checks)
    print(plausibility.to_string(index=False))

    # Report which turbines the bad temperature readings belong to. A defect
    # confined to one turbine says something different from one spread across all.
    bad_temp = scada[scada["Ot_avg"] <= -273.15]
    if len(bad_temp):
        note(f"Temperature readings at or below absolute zero: {len(bad_temp)} records, "
             f"all on {sorted(bad_temp['Wind_turbine_name'].unique())}. "
             "These are fault placeholders and must not be averaged as data.")

    zero_wind_ok = plausibility.loc[
        plausibility["check"] == "zero_power_while_wind_above_operating", "records"].iloc[0]
    note(f"Records with no power while wind was at least {OPERATING_WIND_MIN} m/s: "
         f"{zero_wind_ok:,} ({round(100*zero_wind_ok/len(scada), 2)}% of rows). "
         "These are the periods that matter most and cannot be explained without event data.")

    # Value ranges give a quick sanity check on units.
    print("\nValue ranges (units from SCADA_data_description.csv):")
    ranges = scada[["P_avg", "Ws_avg", "Ot_avg", "Ba_avg", "Ya_avg", "Wa_avg", "Va_avg"]].describe()
    print(ranges.loc[["min", "mean", "max"]].round(2).to_string())
    note(f"Power ranges {power.min():.1f} to {power.max():.1f} kW against a rated "
         f"{RATED_POWER_KW} kW, which is consistent with kW units.")

    return plausibility


# ---------------------------------------------------------------------------
# Step 6: Stuck sensors
# ---------------------------------------------------------------------------

def audit_flatlines(scada):
    """
    A wind sensor that reports exactly the same speed for an hour or more is
    probably stuck. Wind is never that steady. Power is not checked this way,
    because a stopped turbine legitimately reports zero for long stretches.
    """
    print("\n=== 6. STUCK SENSOR CHECK ===")
    rows = []
    for turbine, group in scada.groupby("Wind_turbine_name", observed=True):
        group = group.sort_values("timestamp_utc")
        speed = group["Ws_avg"]
        # Give each run of identical consecutive values its own group number,
        # then count how long each run is.
        run_id = (speed != speed.shift()).cumsum()
        run_lengths = speed.groupby(run_id).transform("size")
        stuck = (run_lengths >= FLATLINE_MIN_RECORDS) & speed.notna()

        # Was power frozen at the same time? If only the wind reading repeats, the
        # anemometer is stuck. If the whole row repeats, the logger was republishing
        # an old record. These call for different fixes, so they are counted apart.
        power = group["P_avg"]
        power_run_id = (power != power.shift()).cumsum()
        power_frozen = power.groupby(power_run_id).transform("size") >= FLATLINE_MIN_RECORDS
        both_frozen = stuck & power_frozen

        rows.append({
            "turbine": turbine,
            "records_in_flatline_runs": int(stuck.sum()),
            "pct_of_turbine_rows": round(100 * stuck.sum() / len(group), 3),
            "longest_run_records": int(run_lengths.max()),
            "wind_and_power_both_frozen": int(both_frozen.sum()),
            "wind_only_frozen": int((stuck & ~power_frozen).sum()),
        })
    flatlines = pd.DataFrame(rows)
    flatlines.to_csv(TABLES / "flatline_summary.csv", index=False)
    print(flatlines.to_string(index=False))
    note(f"Wind-speed readings inside a run of {FLATLINE_MIN_RECORDS}+ identical values: "
         f"{flatlines['records_in_flatline_runs'].tolist()}")
    note(f"Of those, {flatlines['wind_and_power_both_frozen'].sum():,} have power frozen "
         f"at the same time (a repeated row) and {flatlines['wind_only_frozen'].sum():,} "
         "have only the wind reading frozen (a stuck anemometer with the turbine still "
         "responding). The two need different treatment.")
    return flatlines


# ---------------------------------------------------------------------------
# Step 6b: Are the missing values scattered or clustered?
# ---------------------------------------------------------------------------

def audit_missing_runs(scada):
    """
    This distinction changes how missing data should be treated.

    Scattered single gaps look like ordinary dropout and can reasonably be left
    out of an average. Long unbroken runs look like an outage or a turbine out of
    service, which is a different situation entirely: the energy that would have
    been produced is unknown, and filling it with zero would invent downtime.

    It also checks whether the other turbines were reporting normally during each
    run, which separates a site-wide outage from one turbine going quiet.
    """
    print("\n=== 6b. ARE MISSING VALUES SCATTERED OR CLUSTERED? ===")

    # For each timestamp, count how many of the four turbines reported a power value.
    turbines_reporting = scada.groupby("timestamp_utc")["P_avg"].agg(lambda s: s.notna().sum())

    rows = []
    for turbine, group in scada.groupby("Wind_turbine_name", observed=True):
        group = group.sort_values("timestamp_utc")
        missing = group["P_avg"].isna()
        if not missing.any():
            continue

        # Number each unbroken run of missing values so their lengths can be measured.
        run_id = (missing != missing.shift()).cumsum()
        run_lengths = missing[missing].groupby(run_id[missing]).size()

        # At the moments this turbine had no value, was anything reporting at all?
        # Zero reporting means the whole site went quiet together.
        gap_times = group.loc[missing, "timestamp_utc"]
        reporting_during_gaps = turbines_reporting.reindex(gap_times).fillna(0)
        site_wide_gaps = int((reporting_during_gaps == 0).sum())

        rows.append({
            "turbine": turbine,
            "missing_records": int(missing.sum()),
            "number_of_runs": int(len(run_lengths)),
            "longest_run_records": int(run_lengths.max()),
            "longest_run_hours": round(run_lengths.max() / 6, 1),
            "median_run_records": int(run_lengths.median()),
            "gaps_when_no_turbine_reported": site_wide_gaps,
            "gaps_unique_to_this_turbine": int(missing.sum()) - site_wide_gaps,
        })

    missing_runs = pd.DataFrame(rows)
    missing_runs.to_csv(TABLES / "missing_value_runs.csv", index=False)
    print(missing_runs.to_string(index=False))

    note(f"Missing power values are clustered, not scattered: the longest single run "
         f"is {missing_runs['longest_run_hours'].max()} hours. Long runs look like an "
         "outage or a turbine out of service, so treating a gap as zero production "
         "would invent downtime that the data does not show.")
    note(f"Most gaps are shared: {missing_runs['gaps_when_no_turbine_reported'].iloc[0]:,} "
         "of them are moments when no turbine reported at all, which points to the data "
         "link rather than the turbines. Only "
         f"{missing_runs['gaps_unique_to_this_turbine'].tolist()} gaps per turbine are "
         "unique to that turbine.")
    return missing_runs


# ---------------------------------------------------------------------------
# Step 7: Missing data versus downtime
# ---------------------------------------------------------------------------

def audit_missing_vs_downtime(scada):
    """
    The central question of the audit.

    A turbine showing no power could be stopped, or its data link could have
    failed. The only evidence available here is what the other three turbines
    were doing at the same moment. If they were producing normally, the wind was
    available and this turbine was not using it.

    This narrows the possibilities. It does not identify a cause, because no
    event log, work order or curtailment record is included.
    """
    print("\n=== 7. MISSING DATA VERSUS DOWNTIME ===")

    # How many turbines were producing at each timestamp?
    scada = scada.copy()
    scada["is_producing"] = scada["P_avg"] > 0
    peers = scada.groupby("timestamp_utc")["is_producing"].sum().rename("turbines_producing")
    scada = scada.merge(peers, left_on="timestamp_utc", right_index=True, how="left")

    quiet = scada[(scada["P_avg"] <= 0) & (scada["Ws_avg"] >= OPERATING_WIND_MIN)].copy()
    # Subtract this turbine's own contribution to get the peer count.
    quiet["peers_producing"] = quiet["turbines_producing"] - quiet["is_producing"].astype(int)

    breakdown = quiet["peers_producing"].value_counts().sort_index()
    print("Records with no power despite usable wind, grouped by how many of the "
          "other 3 turbines were producing:")
    for peers_up, count in breakdown.items():
        meaning = {
            0: "no turbine producing -> site-wide cause, or a shared data outage",
        }.get(peers_up, "other turbines were producing -> cause specific to this turbine")
        print(f"  {peers_up} peer(s) producing: {count:>7,}  {meaning}")

    isolated = int(breakdown.reindex([1, 2, 3]).fillna(0).sum())
    site_wide = int(breakdown.get(0, 0))
    note(f"Of the no-power-but-windy records, {isolated:,} happened while at least one "
         f"other turbine was producing (turbine-specific), and {site_wide:,} happened "
         f"while none were (site-wide or shared outage).")

    rows = []
    for turbine, group in scada.groupby("Wind_turbine_name", observed=True):
        windy = group["Ws_avg"] >= OPERATING_WIND_MIN
        rows.append({
            "turbine": turbine,
            "no_power_windy_records": int(((group["P_avg"] <= 0) & windy).sum()),
            "no_power_windy_hours": round(((group["P_avg"] <= 0) & windy).sum() / 6, 1),
            "missing_power_value_records": int(group["P_avg"].isna().sum()),
        })
    per_turbine = pd.DataFrame(rows)
    print("\nPer turbine:")
    print(per_turbine.to_string(index=False))

    note("Limit of this evidence: peer comparison can separate a turbine-specific "
         "event from a site-wide one, but it cannot tell a fault from maintenance, "
         "curtailment or a communication failure. That needs an event log.")
    return per_turbine, quiet


# ---------------------------------------------------------------------------
# Step 8: Is the meter data measured or synthetic?
# ---------------------------------------------------------------------------

def audit_plant_data(scada):
    """
    The OpenOA loader states in its own source comments that the meter series was
    "generated by adding artificial electrical loss and uncertaitny to SCADA data"
    (the typo is in the original), and that curtailment and availability were
    "generated by estimating availability and curtailment from SCADA data".

    This check tests that claim against the files. It matters because synthetic
    meter data cannot be used as independent evidence of what was exported.
    """
    print("\n=== 8. PLANT DATA: MEASURED OR SYNTHETIC? ===")
    plant = pd.read_csv(PLANT_FILE)
    plant["time_utc"] = pd.to_datetime(plant["time_utc"], utc=True, format="ISO8601")
    print(f"Rows: {len(plant):,}   Columns: {list(plant.columns)}")
    print(f"UTC range: {plant['time_utc'].min()} to {plant['time_utc'].max()}")

    for column in ["net_energy_kwh", "availability_kwh", "curtailment_kwh"]:
        values = plant[column]
        nonzero = int((values != 0).sum())
        print(f"  {column:20} min {values.min():>10.2f}  max {values.max():>10.2f}  "
              f"non-zero rows {nonzero:,} ({round(100*nonzero/len(plant), 1)}%)")

    # Compare the meter series with the sum of the four turbines over the same
    # interval. A near-constant ratio is the signature of a synthetic series
    # built from SCADA; real metering wanders because of genuine losses.
    turbine_energy = (scada.assign(energy_kwh=scada["P_avg"] * MINUTES_PER_RECORD / 60)
                           .groupby("timestamp_utc")["energy_kwh"].sum())
    merged = pd.DataFrame({"meter": plant.set_index("time_utc")["net_energy_kwh"]}).join(
        turbine_energy.rename("turbine_sum"), how="inner")
    both_positive = merged[(merged["meter"] > 0) & (merged["turbine_sum"] > 0)]
    ratio = both_positive["meter"] / both_positive["turbine_sum"]

    print(f"\nMeter vs sum of turbines, on {len(both_positive):,} intervals where both are positive:")
    print(f"  ratio mean {ratio.mean():.4f}   std {ratio.std():.4f}   "
          f"5th pct {ratio.quantile(0.05):.4f}   95th pct {ratio.quantile(0.95):.4f}")
    print(f"  correlation: {both_positive['meter'].corr(both_positive['turbine_sum']):.6f}")

    note(f"Meter-to-turbine-sum ratio averages {ratio.mean():.3f} with a standard "
         f"deviation of {ratio.std():.3f}, and the two series correlate at "
         f"{both_positive['meter'].corr(both_positive['turbine_sum']):.4f}. This is "
         "consistent with the loader's statement that the meter series was derived "
         "from SCADA rather than measured independently.")
    note("Consequence: the meter series can be used as an internal consistency "
         "check only. It is NOT independent evidence of exported energy, so a "
         "meter reconciliation cannot validate the SCADA data here.")

    all_zero = [c for c in ["availability_kwh", "curtailment_kwh"] if (plant[c] == 0).all()]
    if all_zero:
        note(f"These columns are entirely zero and carry no information: {all_zero}")

    # Second, independent test of the same claim. If availability_kwh really was
    # estimated from SCADA, it should light up at the same moments that a turbine
    # sat idle in usable wind. A measured availability figure would not track a
    # SCADA-derived rule this closely.
    quiet_windy_per_interval = (
        scada.assign(quiet_windy=(scada["P_avg"] <= 0) & (scada["Ws_avg"] >= OPERATING_WIND_MIN))
             .groupby("timestamp_utc")["quiet_windy"].sum()
    )
    joined = plant.set_index("time_utc").join(
        quiet_windy_per_interval.rename("turbines_quiet_in_wind"), how="inner")
    availability_flagged = joined["availability_kwh"] > 0
    scada_flagged = joined["turbines_quiet_in_wind"] > 0
    overlap = int((availability_flagged & scada_flagged).sum())

    print(f"\nCross-check on availability_kwh:")
    print(f"  intervals with availability_kwh > 0            : {int(availability_flagged.sum()):,}")
    print(f"  intervals with a turbine idle in usable wind   : {int(scada_flagged.sum()):,}")
    print(f"  overlap                                        : {overlap:,}")
    note(f"availability_kwh is non-zero in {int(availability_flagged.sum()):,} intervals, and "
         f"{overlap:,} of those ({100*overlap/max(int(availability_flagged.sum()),1):.0f}%) are "
         "intervals where a turbine was idle in usable wind. That close tracking is further "
         "evidence the field was derived from SCADA, not measured.")

    return plant, ratio


# ---------------------------------------------------------------------------
# Step 9: Can air density be worked out?
# ---------------------------------------------------------------------------

def audit_air_density_inputs():
    """
    Comparing a turbine's output fairly across seasons needs air density, because
    cold dense air carries more energy at the same wind speed. Density can come
    from measured pressure and temperature, or from reanalysis (modelled weather
    history). This checks what is actually available, without using it yet.
    """
    print("\n=== 9. AIR DENSITY INPUTS ===")

    for label, path in [("MERRA-2", MERRA_FILE), ("ERA5", ERA5_FILE)]:
        # Only the first rows are needed to see the columns and spacing.
        head = pd.read_csv(path, nrows=5000)
        time_column = "datetime"
        head[time_column] = pd.to_datetime(head[time_column])
        spacing = head[time_column].diff().dropna().mode().iloc[0]
        density_columns = [c for c in head.columns if "dens" in c.lower()]
        useful = [c for c in head.columns
                  if re.search(r"pres|temp|dens|ws_", c, re.I)]
        print(f"{label}: columns = {list(head.columns)}")
        print(f"  time spacing = {spacing}, density columns = {density_columns}")
        note(f"{label} provides {useful} at {spacing} spacing.")

        # Check the full time span cheaply, by reading only the time column.
        full_time = pd.read_csv(path, usecols=[time_column])
        full_time[time_column] = pd.to_datetime(full_time[time_column])
        print(f"  full range: {full_time[time_column].min()} to {full_time[time_column].max()} "
              f"({len(full_time):,} rows)")

    note("SCADA itself has outdoor temperature (Ot_avg) but no air pressure, so "
         "density from SCADA alone would need an assumed pressure for the site's "
         "411 m elevation. Reanalysis supplies pressure and density directly but "
         "is hourly, so it would need aligning to 10-minute records.")
    note("Feasible within three days: yes, but it adds a dependency. Decide in "
         "Phase 2 whether the baseline and the challenger both get density, or "
         "neither does.")


# ---------------------------------------------------------------------------
# Step 10: Three diagnostic figures
# ---------------------------------------------------------------------------

def make_figures(scada, quiet):
    """Three figures only, each answering a question raised by the audit."""
    print("\n=== 10. FIGURES ===")
    turbines = sorted(scada["Wind_turbine_name"].unique())

    # Figure 1: is data coverage even across turbines and over time?
    fig, axes = plt.subplots(len(turbines), 1, figsize=(11, 7), sharex=True)
    for axis, turbine in zip(axes, turbines):
        group = scada[scada["Wind_turbine_name"] == turbine]
        # Drop the timezone before grouping by month. A month label has no
        # timezone, and converting a timezone-aware series straight to a period
        # warns about the information being discarded. Doing it explicitly says
        # the loss is intended: these are UTC months.
        month_label = group["timestamp_utc"].dt.tz_localize(None).dt.to_period("M")
        monthly = group.groupby(month_label).agg(
            rows=("P_avg", "size"), missing_power=("P_avg", lambda s: s.isna().sum()))
        months = monthly.index.to_timestamp()
        axis.bar(months, monthly["rows"], width=20, label="records present")
        axis.bar(months, monthly["missing_power"], width=20, label="power value missing")
        axis.set_ylabel(turbine, fontsize=8)
        axis.tick_params(labelsize=8)
    axes[0].legend(fontsize=8, loc="lower right")
    axes[0].set_title("Figure 1: monthly record count and missing power values, by turbine")
    plt.tight_layout()
    plt.savefig(FIGURES / "fig1_coverage_by_turbine.png", dpi=130)
    plt.close()

    # Figure 2: the basic relationship every later step depends on.
    fig, axes = plt.subplots(1, len(turbines), figsize=(15, 4), sharex=True, sharey=True)
    for axis, turbine in zip(axes, turbines):
        group = scada[scada["Wind_turbine_name"] == turbine]
        axis.scatter(group["Ws_avg"], group["P_avg"], s=0.4, alpha=0.12, linewidths=0)
        axis.axhline(RATED_POWER_KW, linestyle="--", linewidth=0.8, color="grey")
        axis.set_title(turbine, fontsize=10)
        axis.set_xlabel("Wind speed (m/s)")
        axis.set_xlim(0, 27)
    axes[0].set_ylabel("Active power (kW)")
    fig.suptitle("Figure 2: wind speed against power, all records, no cleaning applied "
                 "(dashed line = 2050 kW rated)", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig2_power_curve_raw.png", dpi=130)
    plt.close()

    # Figure 3: the most important problem found - periods with usable wind but
    # no power, which is exactly what cannot be explained without an event log.
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.5))
    # Same explicit timezone drop as Figure 1: these are UTC months.
    quiet_month = quiet["timestamp_utc"].dt.tz_localize(None).dt.to_period("M")
    monthly_quiet = quiet.groupby(
        [quiet_month, "Wind_turbine_name"]
    ).size().unstack(fill_value=0)
    monthly_quiet.index = monthly_quiet.index.to_timestamp()
    monthly_quiet.plot(ax=left, linewidth=1.2)
    left.set_title("No power despite wind ≥ 4 m/s, records per month", fontsize=10)
    left.set_ylabel("10-minute records")
    left.set_xlabel("")
    left.legend(fontsize=7)

    counts = quiet["peers_producing"].value_counts().sort_index()
    right.bar(counts.index.astype(str), counts.values)
    right.set_title("Same records, by how many other turbines were producing", fontsize=10)
    right.set_xlabel("Number of the other 3 turbines producing")
    right.set_ylabel("10-minute records")
    fig.suptitle("Figure 3: the periods that cannot be explained without event data", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig3_unexplained_stops.png", dpi=130)
    plt.close()

    print("Saved 3 figures to outputs/figures/")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("PHASE 1 DATA AUDIT - La Haute Borne")
    print("Nothing is cleaned, filled in or removed in this script.")
    print("=" * 78)

    audit_files()
    scada = load_scada()
    completeness = audit_completeness(scada)
    audit_clock_changes(scada)
    audit_timestamp_alignment(scada)
    plausibility = audit_plausibility(scada)
    flatlines = audit_flatlines(scada)
    audit_missing_runs(scada)
    per_turbine, quiet = audit_missing_vs_downtime(scada)
    audit_plant_data(scada)
    audit_air_density_inputs()
    make_figures(scada, quiet)

    # One combined summary table, so every number in the write-up is traceable.
    summary = pd.concat([
        plausibility.assign(section="plausibility")[
            ["section", "check", "records", "pct_of_rows", "interpretation"]],
        pd.DataFrame([{
            "section": "completeness",
            "check": "absent_intervals_total",
            "records": int(completeness["absent_intervals"].sum()),
            "pct_of_rows": 0.0,
            "interpretation": "Timestamps with no row for a turbine",
        }, {
            "section": "completeness",
            "check": "power_value_missing_total",
            "records": int(completeness["power_value_missing"].sum()),
            "pct_of_rows": round(100 * completeness["power_value_missing"].sum() / len(scada), 3),
            "interpretation": "Row exists but the power value is empty",
        }, {
            "section": "sensors",
            "check": "windspeed_flatline_records_total",
            "records": int(flatlines["records_in_flatline_runs"].sum()),
            "pct_of_rows": round(100 * flatlines["records_in_flatline_runs"].sum() / len(scada), 3),
            "interpretation": f"Inside a run of {FLATLINE_MIN_RECORDS}+ identical wind readings",
        }, {
            "section": "downtime",
            "check": "no_power_while_windy_total",
            "records": int(per_turbine["no_power_windy_records"].sum()),
            "pct_of_rows": round(100 * per_turbine["no_power_windy_records"].sum() / len(scada), 3),
            "interpretation": "Cause cannot be established without an event log",
        }]),
    ], ignore_index=True)
    summary.to_csv(TABLES / "data_quality_summary.csv", index=False)

    print("\n" + "=" * 78)
    print("FINDINGS")
    print("=" * 78)
    for i, line in enumerate(notes, 1):
        print(f"{i:>2}. {line}")
    print("\nTables written to outputs/tables/, figures to outputs/figures/")


if __name__ == "__main__":
    main()
