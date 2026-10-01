"""
Phase 2, Parts B, C and D: build an auditable processed dataset.

Nothing is thrown away. Every raw SCADA row survives into the processed file,
carrying flags that say what is wrong with it and whether it may be used to build
the reference power curve. A record is "excluded" by a label, never by deletion,
so any decision can be inspected, counted or reversed later.

Outputs
    data/processed/scada_processed.parquet
    outputs/tables/cleaning_reconciliation.csv
    outputs/tables/reference_subset_summary.csv
    outputs/tables/annual_resource_comparison.csv
    outputs/tables/operating_threshold_evidence.csv
    outputs/tables/phase2_partb_checks.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

from checks import CheckRecorder, EXPECTED_RAW_SCADA_ROWS, RATED_POWER_KW
from timestamp_correction import load_and_correct, seasonal_lag

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "outputs" / "tables"

ERA5_FILE = RAW / "era5_wind_la_haute_borne.csv"

MINUTES_PER_RECORD = 10

# --- Rule thresholds, each justified in docs/methodology_decisions.md ---
FROZEN_WIND_MIN_RECORDS = 6          # P-04 primary. Sensitivity at 3 and 12 runs later.
POWER_ABOVE_RATED_TOLERANCE = 1.10   # P-02
WIND_PLAUSIBLE_MAX = 30.0            # P-01
TEMPERATURE_MIN_VALID = -30.0        # P-08
PITCH_MIN_VALID, PITCH_MAX_VALID = -5.0, 95.0
REFERENCE_YEAR = 2014                # P-07
ASSESSMENT_YEAR = 2015


# ---------------------------------------------------------------------------
# Air density (P-09)
# ---------------------------------------------------------------------------

def add_air_density(scada):
    """
    Attach ERA5 air density to each ten-minute record and compute a
    density-corrected wind speed.

    Formula, following IEC 61400-12-1 as implemented in OpenOA's
    `air_density_adjusted_wind_speed`:

        corrected_wind = measured_wind * (density / reference_density) ** (1/3)

    Reference density is the mean of the density series itself, which is what
    OpenOA uses. That keeps corrected wind on the same scale as measured wind, so
    the power curve stays readable, and avoids importing a sea-level constant
    that does not suit a site at 411 m.

    Three caveats, all recorded in the methodology notes:
      - ERA5 is hourly; SCADA is every ten minutes.
      - ERA5 supplies density at 100 m; the turbine hub is at 80 m. No height
        adjustment is applied, because density changes very little over 20 m
        compared with the other uncertainties here.
      - Interpolation is linear in time, which reads the hour on either side of a
        record. That is acceptable because this is a retrospective study of what
        already happened, and density is an outside weather variable rather than
        anything derived from turbine output. Backward-fill was the alternative;
        it avoids reading ahead but turns a smooth physical variable into steps.
    """
    era5 = pd.read_csv(ERA5_FILE, usecols=["datetime", "dens_100m"])
    era5["timestamp_utc"] = pd.to_datetime(era5["datetime"], utc=True)
    density_hourly = era5.set_index("timestamp_utc")["dens_100m"].sort_index()

    # Put the hourly series onto the ten-minute grid, then interpolate between
    # the surrounding hours.
    ten_minute_grid = pd.date_range(scada["timestamp_corrected_utc"].min(),
                                    scada["timestamp_corrected_utc"].max(),
                                    freq=f"{MINUTES_PER_RECORD}min", tz="UTC")
    density_10min = (density_hourly.reindex(density_hourly.index.union(ten_minute_grid))
                                   .interpolate(method="time")
                                   .reindex(ten_minute_grid)
                                   .rename("air_density_kgm3"))

    scada = scada.merge(density_10min, left_on="timestamp_corrected_utc",
                        right_index=True, how="left")

    reference_density = scada["air_density_kgm3"].mean()
    scada["reference_density_kgm3"] = reference_density
    scada["wind_speed_density_corrected"] = (
        scada["Ws_avg"] * (scada["air_density_kgm3"] / reference_density) ** (1 / 3))

    print(f"  air density: mean {reference_density:.4f} kg/m3, "
          f"range {scada['air_density_kgm3'].min():.3f} to "
          f"{scada['air_density_kgm3'].max():.3f}")
    return scada


# ---------------------------------------------------------------------------
# Peer context (P-06)
# ---------------------------------------------------------------------------

def add_peer_context(scada):
    """
    For each record, summarise what the other three turbines were doing.

    This matters because a stopped turbine's own wind reading is the least
    reliable measurement on the site: the anemometer sits behind the rotor, and
    its calibration assumes the rotor is turning. Exactly when the reading is
    needed most, it should be trusted least. Peer readings give an independent
    view of whether wind was available.
    """
    grouped = scada.groupby("timestamp_corrected_utc")
    site = pd.DataFrame({
        "site_wind_sum": grouped["Ws_avg"].sum(min_count=1),
        "site_wind_count": grouped["Ws_avg"].count(),
        "site_producing_count": grouped["P_avg"].apply(lambda s: (s > 0).sum()),
        "site_reporting_count": grouped["P_avg"].count(),
    })
    scada = scada.merge(site, left_on="timestamp_corrected_utc", right_index=True, how="left")

    # Remove this turbine's own contribution to leave only its peers.
    own_wind = scada["Ws_avg"].fillna(0)
    own_counts = scada["Ws_avg"].notna().astype(int)
    peer_wind_count = scada["site_wind_count"] - own_counts
    scada["peer_wind_mean"] = np.where(peer_wind_count > 0,
                                       (scada["site_wind_sum"] - own_wind) / peer_wind_count,
                                       np.nan)
    scada["peer_turbines_producing"] = (scada["site_producing_count"]
                                        - (scada["P_avg"] > 0).astype(int))
    scada["peer_turbines_reporting"] = (scada["site_reporting_count"]
                                        - scada["P_avg"].notna().astype(int))
    return scada.drop(columns=["site_wind_sum", "site_wind_count",
                               "site_producing_count", "site_reporting_count"])


# ---------------------------------------------------------------------------
# Data-quality flags
# ---------------------------------------------------------------------------

def add_quality_flags(scada):
    """One boolean column per data-quality problem. No record is removed."""
    scada = scada.sort_values(["Wind_turbine_name", "timestamp_corrected_utc"]).reset_index(drop=True)

    scada["is_missing_power"] = scada["P_avg"].isna()
    scada["is_missing_wind"] = scada["Ws_avg"].isna()

    # Length of the run of identical consecutive wind readings this record sits in.
    # Storing the length rather than a yes/no lets the threshold be varied later
    # without recomputing anything.
    run_lengths = []
    for _, group in scada.groupby("Wind_turbine_name", observed=True, sort=False):
        speed = group["Ws_avg"]
        run_id = (speed != speed.shift()).cumsum()
        run_lengths.append(speed.groupby(run_id).transform("size").where(speed.notna()))
    scada["wind_run_length"] = pd.concat(run_lengths).sort_index()
    scada["is_frozen_wind"] = scada["wind_run_length"] >= FROZEN_WIND_MIN_RECORDS

    # -273.15 C is absolute zero, so a reading at or below it is a fault
    # placeholder the sensor wrote, not a measurement.
    scada["is_invalid_temperature"] = (scada["Ot_avg"] <= TEMPERATURE_MIN_VALID) | scada["Ot_avg"].isna()
    scada["is_invalid_pitch"] = ((scada["Ba_avg"] < PITCH_MIN_VALID)
                                 | (scada["Ba_avg"] > PITCH_MAX_VALID))

    scada["is_zero_power"] = scada["P_avg"] <= 0
    # Small negative power is the turbine running its own systems while idle. It
    # is a real observation, not an error, so it is a warning and not an exclusion.
    scada["is_auxiliary_consumption"] = (scada["P_avg"] < 0) & (scada["P_avg"] >= -50)
    scada["is_power_above_rated"] = scada["P_avg"] > RATED_POWER_KW * POWER_ABOVE_RATED_TOLERANCE
    scada["is_wind_out_of_range"] = (scada["Ws_avg"] < 0) | (scada["Ws_avg"] > WIND_PLAUSIBLE_MAX)
    return scada


def add_reasons_and_eligibility(scada):
    """
    Turn the flags into reason strings and a single eligibility decision.

    Reasons are stored as a sorted, pipe-separated string so that a record with
    several problems keeps all of them, in a form that is stable between runs and
    can be split apart again for counting.
    """
    exclusion_rules = [
        ("missing_power", scada["is_missing_power"]),
        ("missing_wind", scada["is_missing_wind"]),
        ("frozen_wind_sensor", scada["is_frozen_wind"]),
        ("invalid_temperature", scada["is_invalid_temperature"]),
        ("invalid_pitch", scada["is_invalid_pitch"]),
        ("zero_or_negative_power", scada["is_zero_power"]),
        ("power_above_rated_tolerance", scada["is_power_above_rated"]),
        ("wind_out_of_plausible_range", scada["is_wind_out_of_range"]),
    ]
    warning_rules = [
        ("auxiliary_consumption_observed", scada["is_auxiliary_consumption"]),
        ("timestamp_repaired_spring_collision", scada["spring_collision_moved"]),
        ("no_turbine_reporting_at_this_time", scada["peer_turbines_reporting"] == 0),
        ("peer_context_unavailable", scada["peer_wind_mean"].isna()),
    ]

    def combine(rules):
        parts = pd.Series([""] * len(scada), index=scada.index, dtype="object")
        for name, mask in rules:
            mask = mask.fillna(False)
            parts = parts.where(~mask, parts.where(parts == "", parts + "|") + name)
        return parts

    scada["exclusion_reason"] = combine(exclusion_rules)
    scada["warning_reason"] = combine(warning_rules)

    # Eligible for building the reference curve: no exclusion reason at all.
    # Note this is a data-quality judgement only. It does NOT mean the turbine was
    # operating correctly - without event logs that cannot be known, which is why
    # the term "reference-eligible" is used and "healthy" is not.
    scada["is_reference_eligible"] = scada["exclusion_reason"] == ""

    # Three confidence levels, driven by the reasons above.
    scada["data_quality_confidence"] = np.select(
        [scada["exclusion_reason"] != "", scada["warning_reason"] != ""],
        ["low", "medium"], default="high")
    return scada


# ---------------------------------------------------------------------------
# Part D: what is the real operating threshold?
# ---------------------------------------------------------------------------

def empirical_operating_threshold(scada):
    """
    Phase 1 used 4 m/s as the wind speed above which a turbine "should" produce.
    That was a conservative guess, not a measurement. This works it out from the
    data instead.

    For each 0.5 m/s bin: how often is power positive, and what is the median
    power? The threshold is taken where nearly every reporting turbine is
    producing, and it is deliberately set above the first bin that crosses the
    line, because a bin that is 90% producing is not evidence about the other 10%.
    """
    usable = scada[~scada["is_missing_power"] & ~scada["is_missing_wind"]
                   & ~scada["is_frozen_wind"]].copy()
    usable["wind_bin"] = (usable["Ws_avg"] / 0.5).apply(np.floor) * 0.5

    rows = []
    for (turbine, wind_bin), group in usable.groupby(["Wind_turbine_name", "wind_bin"],
                                                     observed=True):
        if len(group) < 20:            # Too few records to say anything.
            continue
        rows.append({
            "turbine": turbine,
            "wind_bin_ms": wind_bin,
            "records": len(group),
            "share_producing": round((group["P_avg"] > 0).mean(), 4),
            "median_power_kw": round(group["P_avg"].median(), 1),
            "p10_power_kw": round(group["P_avg"].quantile(0.10), 1),
        })
    evidence = pd.DataFrame(rows).sort_values(["turbine", "wind_bin_ms"])

    # Across all four turbines, find the lowest bin where at least 95% of records
    # show production, for every turbine.
    by_bin = evidence.groupby("wind_bin_ms")["share_producing"].min()
    qualifying = by_bin[by_bin >= 0.95]
    crossing_bin = qualifying.index.min() if len(qualifying) else np.nan

    # Step one bin higher for the working threshold, so the chosen value sits
    # inside the region where production is consistent rather than on its edge.
    threshold = crossing_bin + 0.5 if not np.isnan(crossing_bin) else 4.0

    print(f"  lowest wind bin where every turbine is >=95% producing: {crossing_bin} m/s")
    print(f"  working operating threshold (one bin higher): {threshold} m/s")
    spread = evidence[evidence["wind_bin_ms"] == crossing_bin]["share_producing"]
    if len(spread):
        print(f"  share producing in that bin, by turbine: "
              f"{spread.min():.3f} to {spread.max():.3f}")

    evidence.to_csv(TABLES / "operating_threshold_evidence.csv", index=False)
    return threshold, crossing_bin, evidence


# ---------------------------------------------------------------------------
# P-07: were 2014 and 2015 comparable wind years?
# ---------------------------------------------------------------------------

def compare_annual_resource(scada):
    """
    The plan is to build the reference on 2014 and assess 2015. That only makes
    sense if the two years are broadly comparable. Two independent views: ERA5
    reanalysis, which is unaffected by any turbine problem, and the site's own
    valid wind measurements.

    Different years do not automatically invalidate the split. The difference has
    to be measured and stated so that it can be weighed against the result.
    """
    era5 = pd.read_csv(ERA5_FILE, usecols=["datetime", "ws_100m", "dens_100m"])
    era5["timestamp_utc"] = pd.to_datetime(era5["datetime"], utc=True)
    era5 = era5[(era5["timestamp_utc"] >= "2014-01-01") & (era5["timestamp_utc"] < "2016-01-01")]
    era5["year"] = era5["timestamp_utc"].dt.year

    valid_wind = scada[~scada["is_missing_wind"] & ~scada["is_frozen_wind"]].copy()
    valid_wind["year"] = valid_wind["timestamp_corrected_utc"].dt.year

    measures = ["era5_mean_wind_ms", "era5_median_wind_ms", "era5_p90_wind_ms",
                "era5_mean_cubed_wind", "scada_mean_wind_ms", "scada_median_wind_ms"]

    rows = []
    for year in [REFERENCE_YEAR, ASSESSMENT_YEAR]:
        era_year = era5[era5["year"] == year]["ws_100m"]
        scada_year = valid_wind[valid_wind["year"] == year]["Ws_avg"]
        rows.append({
            # Kept as text so the percentage-change row can share the column.
            "year": str(year),
            "era5_mean_wind_ms": round(era_year.mean(), 3),
            "era5_median_wind_ms": round(era_year.median(), 3),
            "era5_p90_wind_ms": round(era_year.quantile(0.90), 3),
            # Energy in the wind goes with the cube of speed, so this tracks the
            # resource far better than the mean does.
            "era5_mean_cubed_wind": round((era_year ** 3).mean(), 1),
            "scada_mean_wind_ms": round(scada_year.mean(), 3),
            "scada_median_wind_ms": round(scada_year.median(), 3),
            "scada_records": len(scada_year),
        })

    change = {"year": "change_2015_vs_2014_pct", "scada_records": np.nan}
    for column in measures:
        first, second = rows[0][column], rows[1][column]
        change[column] = round(100 * (second - first) / first, 2)
    rows.append(change)

    comparison = pd.DataFrame(rows)

    # Seasonal view, since an annual average can hide offsetting seasons.
    era5["quarter"] = era5["timestamp_utc"].dt.quarter
    seasonal = era5.pivot_table(index="quarter", columns="year",
                                values="ws_100m", aggfunc="mean").round(3)
    seasonal["change_pct"] = (100 * (seasonal[ASSESSMENT_YEAR] - seasonal[REFERENCE_YEAR])
                              / seasonal[REFERENCE_YEAR]).round(2)
    print("\n  ERA5 mean wind speed by quarter (m/s):")
    print(seasonal.to_string())

    comparison.to_csv(TABLES / "annual_resource_comparison.csv", index=False)
    return comparison, seasonal


# ---------------------------------------------------------------------------
# Reconciliation tables
# ---------------------------------------------------------------------------

def build_reconciliation(scada):
    """Account for every raw record: eligible, excluded (and why), or warned."""
    rows = [{
        "category": "raw_records",
        "subcategory": "all",
        "records": len(scada),
        "share_of_raw_pct": 100.0,
    }, {
        "category": "reference_eligible",
        "subcategory": "no_exclusion_reason",
        "records": int(scada["is_reference_eligible"].sum()),
        "share_of_raw_pct": round(100 * scada["is_reference_eligible"].mean(), 3),
    }, {
        "category": "excluded",
        "subcategory": "any_reason",
        "records": int((~scada["is_reference_eligible"]).sum()),
        "share_of_raw_pct": round(100 * (~scada["is_reference_eligible"]).mean(), 3),
    }]

    # Each reason counted on its own. These overlap, so they do not add up to the
    # excluded total - the overlap rows below explain the difference.
    all_reasons = scada.loc[scada["exclusion_reason"] != "", "exclusion_reason"]
    for reason in sorted({r for entry in all_reasons for r in entry.split("|")}):
        count = int(all_reasons.str.split("|").apply(lambda parts: reason in parts).sum())
        rows.append({"category": "excluded_by_reason", "subcategory": reason,
                     "records": count, "share_of_raw_pct": round(100 * count / len(scada), 3)})

    # How many reasons each excluded record carries.
    reason_counts = all_reasons.str.count(r"\|") + 1
    for number, count in reason_counts.value_counts().sort_index().items():
        rows.append({"category": "exclusion_overlap", "subcategory": f"{number}_reason(s)",
                     "records": int(count), "share_of_raw_pct": round(100 * count / len(scada), 3)})

    warnings = scada.loc[scada["warning_reason"] != "", "warning_reason"]
    for reason in sorted({r for entry in warnings for r in entry.split("|")}):
        count = int(warnings.str.split("|").apply(lambda parts: reason in parts).sum())
        rows.append({"category": "warning_by_reason", "subcategory": reason,
                     "records": count, "share_of_raw_pct": round(100 * count / len(scada), 3)})

    for level in ["high", "medium", "low"]:
        count = int((scada["data_quality_confidence"] == level).sum())
        rows.append({"category": "confidence", "subcategory": level,
                     "records": count, "share_of_raw_pct": round(100 * count / len(scada), 3)})

    reconciliation = pd.DataFrame(rows)
    reconciliation.to_csv(TABLES / "cleaning_reconciliation.csv", index=False)
    return reconciliation


def build_reference_summary(scada):
    """Reference-eligible counts by turbine and year."""
    scada = scada.copy()
    scada["year"] = scada["timestamp_corrected_utc"].dt.year
    summary = scada.groupby(["Wind_turbine_name", "year"], observed=True).agg(
        records=("is_reference_eligible", "size"),
        reference_eligible=("is_reference_eligible", "sum"),
        excluded=("is_reference_eligible", lambda s: (~s).sum()),
        missing_power=("is_missing_power", "sum"),
        frozen_wind=("is_frozen_wind", "sum"),
        zero_or_negative_power=("is_zero_power", "sum"),
        invalid_temperature=("is_invalid_temperature", "sum"),
    ).reset_index()
    summary["eligible_pct"] = (100 * summary["reference_eligible"] / summary["records"]).round(2)
    summary.to_csv(TABLES / "reference_subset_summary.csv", index=False)
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    checker = CheckRecorder("phase2_part_b_prepare")

    print("=" * 78)
    print("PHASE 2 PARTS B, C, D - building the processed dataset")
    print("=" * 78)

    print("\nLoading raw SCADA and applying the approved timestamp correction...")
    scada, _ = load_and_correct()
    checker.require("raw_row_count_preserved_on_load",
                    len(scada) == EXPECTED_RAW_SCADA_ROWS,
                    f"{len(scada):,} rows")

    print("\nAttaching ERA5 air density (P-09, permitted because P-11 passed)...")
    scada = add_air_density(scada)

    print("\nAdding peer context...")
    scada = add_peer_context(scada)

    print("\nFlagging data-quality problems...")
    scada = add_quality_flags(scada)
    scada = add_reasons_and_eligibility(scada)

    print("\nPart D - empirical operating threshold:")
    threshold, crossing_bin, _ = empirical_operating_threshold(scada)
    scada["operating_threshold_ms"] = threshold
    # Two views of "idle when it should be producing": the turbine's own reading,
    # and the peers' reading. The peer view is the more trustworthy of the two
    # when the turbine is stopped.
    scada["idle_by_own_wind"] = scada["is_zero_power"] & (scada["Ws_avg"] >= threshold)
    scada["idle_by_peer_wind"] = scada["is_zero_power"] & (scada["peer_wind_mean"] >= threshold)

    print("\nP-07 - comparing 2014 and 2015 wind resource:")
    resource, _ = compare_annual_resource(scada)
    print(resource.to_string(index=False))

    print("\nBuilding reconciliation tables...")
    reconciliation = build_reconciliation(scada)
    summary = build_reference_summary(scada)

    # --- Validation -------------------------------------------------------
    print("\nValidating the processed dataset:")
    checker.require("every_raw_record_present_in_processed",
                    len(scada) == EXPECTED_RAW_SCADA_ROWS,
                    f"{len(scada):,} rows in, {EXPECTED_RAW_SCADA_ROWS:,} expected")
    checker.require("no_record_silently_dropped",
                    len(scada) == int(reconciliation.loc[
                        reconciliation["category"] == "raw_records", "records"].iloc[0]),
                    "reconciliation starts from the full raw count")

    eligible = int(scada["is_reference_eligible"].sum())
    excluded = int((~scada["is_reference_eligible"]).sum())
    checker.require("eligible_plus_excluded_equals_total",
                    eligible + excluded == len(scada),
                    f"{eligible:,} + {excluded:,} = {len(scada):,}")

    checker.require("every_exclusion_has_a_reason",
                    (scada.loc[~scada["is_reference_eligible"], "exclusion_reason"] != "").all(),
                    "no record is excluded without a recorded reason")
    checker.require("every_eligible_record_has_no_reason",
                    (scada.loc[scada["is_reference_eligible"], "exclusion_reason"] == "").all(),
                    "no eligible record carries an exclusion reason")

    # The rule that matters most: a gap must never become a zero.
    missing_now_zero = (scada["is_missing_power"] & (scada["P_avg"] == 0)).sum()
    checker.require("no_missing_observation_became_zero",
                    missing_now_zero == 0,
                    f"{missing_now_zero} missing power values turned into zeros")
    checker.require("missing_power_still_missing",
                    scada.loc[scada["is_missing_power"], "P_avg"].isna().all(),
                    "missing power values remain empty, not imputed")

    checker.record("reference_eligible_records_all_producing",
                   (scada.loc[scada["is_reference_eligible"], "P_avg"] > 0).all(),
                   "no zero or negative power in the reference subset")
    checker.record("density_attached_to_all_records",
                   scada["air_density_kgm3"].notna().all(),
                   f"{scada['air_density_kgm3'].isna().sum()} records without density")
    checker.record("confidence_levels_cover_all_records",
                   scada["data_quality_confidence"].notna().all()
                   and len(scada) == sum(int((scada["data_quality_confidence"] == lvl).sum())
                                         for lvl in ["high", "medium", "low"]),
                   "every record has exactly one confidence level")

    # --- Write ------------------------------------------------------------
    keep = [
        "Wind_turbine_name", "timestamp_raw", "timestamp_published_utc",
        "timestamp_corrected_utc", "utc_offset_written", "spring_collision_moved",
        "P_avg", "Ws_avg", "Ot_avg", "Ba_avg", "Ya_avg", "Wa_avg", "Va_avg",
        "air_density_kgm3", "reference_density_kgm3", "wind_speed_density_corrected",
        "peer_wind_mean", "peer_turbines_producing", "peer_turbines_reporting",
        "wind_run_length", "is_missing_power", "is_missing_wind", "is_frozen_wind",
        "is_invalid_temperature", "is_invalid_pitch", "is_zero_power",
        "is_auxiliary_consumption", "is_power_above_rated", "is_wind_out_of_range",
        "is_reference_eligible", "exclusion_reason", "warning_reason",
        "data_quality_confidence", "operating_threshold_ms",
        "idle_by_own_wind", "idle_by_peer_wind",
    ]
    output_path = PROCESSED / "scada_processed.parquet"
    scada[keep].to_parquet(output_path, index=False, compression="snappy")
    size_mb = output_path.stat().st_size / 1_048_576

    checker.save(TABLES / "phase2_partb_checks.csv")

    print(f"\nWrote {output_path.name} ({size_mb:.1f} MB, {len(scada):,} rows, {len(keep)} columns)")
    print("\nReference-eligible by turbine and year:")
    print(summary[["Wind_turbine_name", "year", "records", "reference_eligible",
                   "eligible_pct"]].to_string(index=False))
    print(f"\nOverall reference-eligible: {eligible:,} of {len(scada):,} "
          f"({100*eligible/len(scada):.2f}%)")
    return scada


if __name__ == "__main__":
    main()
