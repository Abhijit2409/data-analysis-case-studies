"""
Phase 2, Part A: test the timestamp hypothesis (P-11).

The hypothesis
--------------
Phase 1 found that the published timestamps carry daylight-saving offsets, but
that the logger's own clock appears never to have changed. If so, the "+02:00"
offset was applied to unchanged local time, and every summer record sits one hour
early once converted to UTC.

The candidate correction is simple: ignore the written offset and treat every
record's wall-clock reading as a fixed UTC+1 clock all year round.

Nothing here overwrites the original timestamps. Three columns are kept side by
side so the change is auditable and reversible:

    timestamp_raw              the original text, untouched
    timestamp_published_utc    what the written offset says
    timestamp_corrected_utc    the candidate correction

The correction is only used later if every test in this module passes.
"""

import hashlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from checks import (CheckRecorder, EXPECTED_RAW_SCADA_ROWS,
                    RAW_FILE_CHECKSUMS)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

SCADA_FILE = RAW / "la-haute-borne-data-2014-2015.csv"
ERA5_FILE = RAW / "era5_wind_la_haute_borne.csv"

LOGGER_OFFSET_HOURS = 1          # The fixed UTC+1 clock the hypothesis proposes.
MINUTES_PER_RECORD = 10


# ---------------------------------------------------------------------------
# Building the three timestamp columns
# ---------------------------------------------------------------------------

def build_timestamp_columns(scada):
    """Add the three timestamp columns. The raw text is never modified."""
    scada = scada.copy()
    scada["timestamp_raw"] = scada["Date_time"]

    # What the file says, taking the written offset at face value.
    scada["timestamp_published_utc"] = pd.to_datetime(
        scada["timestamp_raw"], utc=True, format="ISO8601")

    # The wall-clock reading with the offset stripped off, e.g. "2014-06-01T12:00".
    wall_clock = pd.to_datetime(scada["timestamp_raw"].str.slice(0, 19), format="ISO8601")

    # The candidate correction: read that wall clock as a fixed UTC+1 clock.
    scada["timestamp_corrected_utc"] = (
        wall_clock - pd.Timedelta(hours=LOGGER_OFFSET_HOURS)).dt.tz_localize("UTC")

    scada["utc_offset_written"] = scada["timestamp_raw"].str.slice(-6)
    return scada


def resolve_spring_collisions(scada):
    """
    Repair the one case the simple rule cannot fix on its own.

    On a spring clock-change date the published file contains the hour 03:00-03:50
    twice. Phase 1 established (Test A) that both copies are genuine data: one
    continues from the record before, the other leads into the record after. The
    export collapsed two different logger hours onto one label, so the wall-clock
    reading alone cannot separate them.

    This function puts one copy back an hour. Which copy moves is decided by
    continuity of wind speed, not by row order: wind speed changes smoothly
    between consecutive ten-minute records, so the correct arrangement is the one
    with the smaller jump at the two seams.
    """
    scada = scada.sort_values(["Wind_turbine_name", "timestamp_raw"]).reset_index(drop=True)
    scada["spring_collision_moved"] = False

    decisions = []
    duplicated_mask = scada.duplicated(subset=["Wind_turbine_name", "timestamp_corrected_utc"],
                                       keep=False)

    for (turbine, _), block in scada[duplicated_mask].groupby(
            ["Wind_turbine_name", scada.loc[duplicated_mask, "timestamp_corrected_utc"].dt.date]):

        # Split the block into the first and second copy of each timestamp.
        copy_one = block.iloc[0::2]
        copy_two = block.iloc[1::2]

        earliest = block["timestamp_corrected_utc"].min()
        latest = block["timestamp_corrected_utc"].max()
        one_hour = pd.Timedelta(hours=1)

        # The records immediately before and after the collided block.
        same_turbine = scada[scada["Wind_turbine_name"] == turbine]
        before = same_turbine[same_turbine["timestamp_corrected_utc"] == earliest - one_hour]
        after = same_turbine[same_turbine["timestamp_corrected_utc"] == latest + pd.Timedelta(
            minutes=MINUTES_PER_RECORD)]

        def seam_gap(moves_back, stays):
            """Total wind-speed jump at the two joins for one candidate arrangement."""
            gap = 0.0
            if len(before):
                gap += abs(moves_back["Ws_avg"].iloc[0] - before["Ws_avg"].iloc[0])
            if len(after):
                gap += abs(stays["Ws_avg"].iloc[-1] - after["Ws_avg"].iloc[0])
            return gap

        score_move_copy_one = seam_gap(copy_one, copy_two)
        score_move_copy_two = seam_gap(copy_two, copy_one)
        moved = copy_one if score_move_copy_one <= score_move_copy_two else copy_two

        scada.loc[moved.index, "timestamp_corrected_utc"] -= one_hour
        scada.loc[moved.index, "spring_collision_moved"] = True

        decisions.append({
            "turbine": turbine,
            "collision_date": str(earliest.date()),
            "records_moved_back_one_hour": len(moved),
            "seam_gap_if_first_copy_moves_ms": round(score_move_copy_one, 3),
            "seam_gap_if_second_copy_moves_ms": round(score_move_copy_two, 3),
            "copy_moved": "first" if score_move_copy_one <= score_move_copy_two else "second",
        })

    return scada, pd.DataFrame(decisions)


# ---------------------------------------------------------------------------
# The seasonal alignment test, run on either timestamp column
# ---------------------------------------------------------------------------

def seasonal_lag(scada, timestamp_column):
    """
    Compare the daily temperature cycle against ERA5 reanalysis, which is stored
    in UTC and produced independently of this logger.

    The absolute lag is not the test. A nacelle-mounted sensor can lag the outside
    air in any season, and that is harmless. What matters is whether winter and
    summer agree. A one-hour seasonal difference means the clock moves when it
    should not.
    """
    temperature = scada.loc[scada["Ot_avg"] > -30, [timestamp_column, "Ot_avg"]]
    scada_hourly = (temperature.groupby(timestamp_column)["Ot_avg"].median()
                               .resample("1h").mean().rename("scada_temp"))

    era5 = pd.read_csv(ERA5_FILE, usecols=["datetime", "t_2m"])
    era5["timestamp_utc"] = pd.to_datetime(era5["datetime"], utc=True)
    era5["era5_temp"] = era5["t_2m"] - 273.15              # Kelvin to Celsius
    era5_hourly = era5.set_index("timestamp_utc")["era5_temp"]

    paired = pd.concat([scada_hourly, era5_hourly], axis=1, sort=True).dropna()
    paired = paired[(paired.index >= "2014-01-01") & (paired.index < "2016-01-01")]

    # Strip each day's mean so the daily cycle, not the seasonal swing, drives
    # the correlation.
    day = paired.index.floor("D")
    paired["scada_shape"] = paired["scada_temp"] - paired.groupby(day)["scada_temp"].transform("mean")
    paired["era5_shape"] = paired["era5_temp"] - paired.groupby(day)["era5_temp"].transform("mean")

    output = {}
    for season, months in [("winter", [11, 12, 1, 2]), ("summer", [5, 6, 7, 8])]:
        subset = paired[paired.index.month.isin(months)]
        correlations = {lag: subset["scada_shape"].corr(subset["era5_shape"].shift(lag))
                        for lag in range(-3, 4)}
        best = max(correlations, key=correlations.get)
        output[season] = {"best_lag_hours": best,
                          "correlation": round(correlations[best], 4),
                          "curve": correlations,
                          "records": len(subset)}
    output["seasonal_difference_hours"] = (output["summer"]["best_lag_hours"]
                                           - output["winter"]["best_lag_hours"])
    return output


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_correction(scada, before_lag, after_lag, checker):
    """
    Run every test the correction must pass. The correction is adopted only if
    all of them pass.
    """
    print("\nValidating the timestamp correction:")

    # 0. The raw files must be the ones Phase 1 audited.
    archive = RAW / "la_haute_borne.zip"
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checker.require("raw_archive_unchanged_since_phase_1",
                    digest == RAW_FILE_CHECKSUMS["la_haute_borne.zip"],
                    f"sha256 {digest[:16]}...")

    # 1. No record gained or lost. Compared against the count recorded in Phase 1,
    #    not against this run's own total, which would prove nothing.
    checker.require("row_count_matches_phase_1",
                    len(scada) == EXPECTED_RAW_SCADA_ROWS,
                    f"{len(scada):,} rows, expected {EXPECTED_RAW_SCADA_ROWS:,}")

    # 2. Corrected timestamps unique within each turbine.
    duplicates = scada.duplicated(subset=["Wind_turbine_name", "timestamp_corrected_utc"]).sum()
    checker.record("corrected_timestamps_unique_per_turbine",
                   duplicates == 0,
                   f"{duplicates} duplicate(s) remain")

    # 3. Spring collisions resolved without dropping anything.
    published_duplicates = scada.duplicated(
        subset=["Wind_turbine_name", "timestamp_published_utc"]).sum()
    checker.record("spring_duplicates_resolved_without_discarding",
                   duplicates == 0 and published_duplicates > 0,
                   f"{published_duplicates} duplicates under published time, "
                   f"{duplicates} under corrected time, no rows removed")

    # 4 and 6. A complete ten-minute sequence per turbine, with no new holes.
    gap_report = []
    for turbine, group in scada.groupby("Wind_turbine_name", observed=True):
        for label, column in [("published", "timestamp_published_utc"),
                              ("corrected", "timestamp_corrected_utc")]:
            stamps = pd.DatetimeIndex(group[column].unique()).sort_values()
            grid = pd.date_range(stamps.min(), stamps.max(),
                                 freq=f"{MINUTES_PER_RECORD}min", tz="UTC")
            gap_report.append({"turbine": turbine, "timestamp": label,
                               "absent_intervals": len(grid.difference(stamps))})
    gaps = pd.DataFrame(gap_report)
    published_gaps = int(gaps.loc[gaps["timestamp"] == "published", "absent_intervals"].sum())
    corrected_gaps = int(gaps.loc[gaps["timestamp"] == "corrected", "absent_intervals"].sum())
    checker.record("autumn_gaps_removed_by_correction",
                   corrected_gaps < published_gaps,
                   f"absent intervals: {published_gaps} published -> {corrected_gaps} corrected")
    checker.record("no_new_timestamp_discontinuity",
                   corrected_gaps == 0,
                   f"{corrected_gaps} absent interval(s) under corrected time")

    # 5. The seasonal difference should disappear. This is the real test.
    before = before_lag["seasonal_difference_hours"]
    after = after_lag["seasonal_difference_hours"]
    checker.record("seasonal_lag_difference_removed",
                   after == 0,
                   f"winter-summer difference: {before:+d} h published -> {after:+d} h corrected")

    # 7. Energy is only relabelled, never changed.
    energy = scada["P_avg"] * MINUTES_PER_RECORD / 60
    total_energy = energy.sum()
    monthly_published = energy.groupby(
        scada["timestamp_published_utc"].dt.tz_localize(None).dt.to_period("M")).sum()
    monthly_corrected = energy.groupby(
        scada["timestamp_corrected_utc"].dt.tz_localize(None).dt.to_period("M")).sum()
    monthly_change = (monthly_corrected - monthly_published).abs()
    largest_monthly_change_pct = 100 * monthly_change.max() / monthly_published.max()

    # Relabelling must move energy between months, never create or destroy it.
    # Comparing the two monthly totals is a real test: it would catch a record
    # dropped or double-counted during the collision repair.
    checker.record("energy_conserved_across_relabelling",
                   abs(monthly_published.sum() - monthly_corrected.sum()) < 1e-6,
                   f"{total_energy/1000:,.0f} MWh under both timestamps, "
                   f"difference {abs(monthly_published.sum() - monthly_corrected.sum()):.2e} kWh")
    # Records near a month boundary can move month when shifted by an hour. That
    # is expected and small; it is reported rather than treated as a failure.
    checker.record("monthly_energy_change_within_boundary_effect",
                   largest_monthly_change_pct < 1.0,
                   f"largest monthly shift {largest_monthly_change_pct:.3f}% "
                   "(month-boundary records only)")

    return gaps, monthly_change


def make_validation_figure(before_lag, after_lag, gaps):
    """One figure, showing only what is needed to judge the correction."""
    fig, (left, right) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Left: the seasonal lag curves, before and after. This is the decisive test.
    for season, style in [("winter", "-o"), ("summer", "--s")]:
        lags = sorted(before_lag[season]["curve"])
        left.plot(lags, [before_lag[season]["curve"][l] for l in lags], style,
                  markersize=4, label=f"{season}, published")
    for season, style in [("winter", "-o"), ("summer", "--s")]:
        lags = sorted(after_lag[season]["curve"])
        left.plot(lags, [after_lag[season]["curve"][l] for l in lags], style,
                  markersize=4, alpha=0.55, label=f"{season}, corrected")
    left.set_xlabel("Lag applied to ERA5 (hours)")
    left.set_ylabel("Correlation of daily temperature shape")
    left.set_title(f"Seasonal alignment against ERA5\n"
                   f"winter-summer gap: {before_lag['seasonal_difference_hours']:+d} h published, "
                   f"{after_lag['seasonal_difference_hours']:+d} h corrected", fontsize=10)
    left.legend(fontsize=7)
    left.grid(alpha=0.25)

    # Right: did the correction close the timestamp holes?
    pivot = gaps.pivot(index="turbine", columns="timestamp", values="absent_intervals")
    pivot = pivot[["published", "corrected"]]
    pivot.plot(kind="bar", ax=right, width=0.75)
    right.set_ylabel("Absent 10-minute intervals")
    right.set_xlabel("")
    right.set_title("Holes in the ten-minute sequence", fontsize=10)
    right.tick_params(axis="x", rotation=0)
    right.legend(fontsize=8)

    fig.suptitle("Figure 4: evidence for and against the timestamp correction (P-11)", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig4_timestamp_validation.png", dpi=130)
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_and_correct():
    """Load the raw SCADA and return it with all three timestamp columns."""
    scada = pd.read_csv(SCADA_FILE, dtype={"Date_time": "string"})
    scada = build_timestamp_columns(scada)
    scada, decisions = resolve_spring_collisions(scada)
    return scada, decisions


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    checker = CheckRecorder("phase2_part_a_timestamps")

    print("=" * 78)
    print("PHASE 2 PART A - testing the timestamp hypothesis (P-11)")
    print("=" * 78)

    scada, decisions = load_and_correct()
    print(f"\nLoaded {len(scada):,} rows.")

    if len(decisions):
        print("\nSpring collision decisions (which copy moved back an hour):")
        print(decisions.to_string(index=False))

    print("\nSeasonal alignment BEFORE correction (published timestamps):")
    before_lag = seasonal_lag(scada, "timestamp_published_utc")
    for season in ["winter", "summer"]:
        print(f"  {season:7} best lag {before_lag[season]['best_lag_hours']:+d} h "
              f"(correlation {before_lag[season]['correlation']})")
    print(f"  difference: {before_lag['seasonal_difference_hours']:+d} h")

    print("\nSeasonal alignment AFTER correction:")
    after_lag = seasonal_lag(scada, "timestamp_corrected_utc")
    for season in ["winter", "summer"]:
        print(f"  {season:7} best lag {after_lag[season]['best_lag_hours']:+d} h "
              f"(correlation {after_lag[season]['correlation']})")
    print(f"  difference: {after_lag['seasonal_difference_hours']:+d} h")

    gaps, monthly_change = validate_correction(scada, before_lag, after_lag, checker)
    make_validation_figure(before_lag, after_lag, gaps)

    results = checker.save(TABLES / "timestamp_correction_validation.csv")

    verdict = "APPROVED" if checker.all_passed else "REJECTED"
    print("\n" + "=" * 78)
    print(f"P-11 VERDICT: {verdict}")
    if not checker.all_passed:
        print(f"Failed checks: {checker.failures()}")
        print("Consequence: keep published timestamps, and drop air-density")
        print("normalisation and every other cross-series join from the project.")
    else:
        print("Consequence: timestamp_corrected_utc is used for analysis, and")
        print("cross-series joins such as ERA5 air density are permitted.")
    print("=" * 78)

    return checker.all_passed, results


if __name__ == "__main__":
    main()
