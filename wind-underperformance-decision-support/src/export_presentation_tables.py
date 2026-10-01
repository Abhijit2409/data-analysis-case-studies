"""
Phase 4B: presentation-only tables for the application.

These tables exist so the application can draw interactive charts without
recomputing anything. **No analytical result is produced or changed here.** Every
figure is a reshaping of data the pipeline already wrote, or a straight count off
the processed dataset. Classifications, thresholds and model outputs are read, not
recalculated.

Outputs, all prefixed `presentation_` so they are never confused with analytical
tables:
    presentation_reference_curves.csv      method A and B expected power by bin
    presentation_monthly_completeness.csv  records and missing values by month
    presentation_missing_runs.csv          every run of missing power, with length
    presentation_data_funnel.csv           raw to assessable, as funnel stages
    presentation_validation_summary.csv    every validation check in one place
"""

import glob
from pathlib import Path

import pandas as pd

from baseline_model import (build_reference_curves, FROZEN_WIND_PRIMARY,
                            CURVE_QUANTILE_PRIMARY, ASSESSMENT_YEAR, HOURS_PER_RECORD)
from ml_challenger import load_data, fit_pooled_curve

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES = PROJECT_ROOT / "outputs" / "tables"


def export_reference_curves(data):
    """Method A's per-turbine curves and method B's pooled curve, in one table."""
    turbine_curves = build_reference_curves(data, FROZEN_WIND_PRIMARY, CURVE_QUANTILE_PRIMARY)
    pooled = fit_pooled_curve(data)

    rows = turbine_curves[["Wind_turbine_name", "wind_bin", "expected_power_kw",
                           "reference_records", "bin_basis"]].copy()
    rows["method"] = "A_turbine_specific"
    rows = rows.rename(columns={"Wind_turbine_name": "series"})

    pooled_rows = pooled[["wind_bin", "expected_power_kw", "reference_records",
                          "bin_basis"]].copy()
    pooled_rows["series"] = "Fleet (pooled)"
    pooled_rows["method"] = "B_pooled_transparent"

    combined = pd.concat([rows, pooled_rows], ignore_index=True)

    # The difference between each turbine's own curve and the fleet curve is what
    # the pooling argument rests on, so it is precomputed for the chart.
    fleet = pooled_rows.set_index("wind_bin")["expected_power_kw"]
    combined["fleet_expected_power_kw"] = combined["wind_bin"].map(fleet)
    combined["own_minus_fleet_kw"] = (combined["expected_power_kw"]
                                      - combined["fleet_expected_power_kw"]).round(2)
    combined.to_csv(TABLES / "presentation_reference_curves.csv", index=False)
    return combined


def export_monthly_completeness(data):
    """Record counts and missing values by turbine and month, for a heatmap."""
    frame = data.copy()
    frame["month"] = frame["timestamp_corrected_utc"].dt.tz_localize(None).dt.to_period("M")
    monthly = frame.groupby(["Wind_turbine_name", "month"], observed=True).agg(
        records=("P_avg", "size"),
        missing_power=("is_missing_power", "sum"),
        reference_eligible=("is_reference_eligible", "sum"),
    ).reset_index()
    monthly["month"] = monthly["month"].astype(str)
    monthly["completeness_pct"] = (100 * (1 - monthly["missing_power"] / monthly["records"])).round(2)
    monthly["eligible_pct"] = (100 * monthly["reference_eligible"] / monthly["records"]).round(2)
    monthly.to_csv(TABLES / "presentation_monthly_completeness.csv", index=False)
    return monthly


def export_missing_runs(data):
    """
    Every unbroken run of missing power values, with its length.

    The Phase 1 audit reported run statistics; this writes the individual runs so
    the application can show that gaps are clustered rather than scattered, which
    is the reason a gap must never be filled with zero.
    """
    rows = []
    for turbine, group in data.groupby("Wind_turbine_name", observed=True):
        group = group.sort_values("timestamp_corrected_utc")
        missing = group["is_missing_power"].to_numpy()
        stamps = group["timestamp_corrected_utc"].to_numpy()
        start = None
        for position, flag in enumerate(missing):
            if flag and start is None:
                start = position
            elif not flag and start is not None:
                rows.append({"turbine": turbine, "start_utc": stamps[start],
                             "end_utc": stamps[position - 1], "records": position - start})
                start = None
        if start is not None:
            rows.append({"turbine": turbine, "start_utc": stamps[start],
                         "end_utc": stamps[-1], "records": len(missing) - start})

    runs = pd.DataFrame(rows)
    runs["hours"] = (runs["records"] * HOURS_PER_RECORD).round(2)
    runs = runs.sort_values("records", ascending=False).reset_index(drop=True)
    runs.to_csv(TABLES / "presentation_missing_runs.csv", index=False)
    return runs


def export_data_funnel(data):
    """Raw records down to assessable 2015 records, as funnel stages."""
    assessment = data[data["year"] == ASSESSMENT_YEAR]
    register = pd.read_csv(TABLES / "decision_event_register.csv")

    # Assessable 2015 records: taken from the method comparison the pipeline wrote,
    # so this stage matches the analytical result rather than re-deriving it.
    comparison = pd.read_csv(TABLES / "phase3_method_comparison.csv")
    assessable = int(comparison.loc[
        comparison["method"] == "B_pooled_transparent", "assessable_records"].iloc[0])

    stages = [
        {"stage": "Raw SCADA records", "records": len(data),
         "note": "Every row in the published file. None deleted at any point."},
        {"stage": "Reference-eligible", "records": int(data["is_reference_eligible"].sum()),
         "note": "Passed the data-quality rules. Not a claim that the turbine ran correctly."},
        {"stage": "Excluded from fitting",
         "records": int((~data["is_reference_eligible"]).sum()),
         "note": "Kept in the dataset with reasons attached, mostly zero-power records."},
        {"stage": "2015 assessment year", "records": len(assessment),
         "note": "The year the frozen reference curves were applied to."},
        {"stage": "Assessable in 2015 (method B)", "records": assessable,
         "note": "Had an expected-power value, so a shortfall could be computed."},
        {"stage": "In persistent reviewable events", "records": int(register["duration_hours"].sum() * 6),
         "note": "Approximate record count behind the 25 leading events."},
    ]
    funnel = pd.DataFrame(stages)
    funnel.to_csv(TABLES / "presentation_data_funnel.csv", index=False)
    return funnel


def export_validation_summary():
    """Every validation check from every phase, in one table."""
    pieces = []
    for path in sorted(glob.glob(str(TABLES / "*.csv"))):
        name = Path(path).name
        # Skip this module's own outputs. The summary itself has stage/check/result
        # columns, so including it would fold a previous run's rows back in and
        # double-count every check.
        if name.startswith("presentation_"):
            continue
        frame = pd.read_csv(path)
        if "result" not in frame.columns or "check" not in frame.columns:
            continue
        frame["source_file"] = name
        pieces.append(frame[["stage", "check", "result", "detail", "source_file"]])
    summary = pd.concat(pieces, ignore_index=True)
    summary.to_csv(TABLES / "presentation_validation_summary.csv", index=False)
    return summary


def main():
    print("Exporting presentation-only tables (no analytical result is changed)...")
    data = load_data()

    curves = export_reference_curves(data)
    monthly = export_monthly_completeness(data)
    runs = export_missing_runs(data)
    funnel = export_data_funnel(data)
    summary = export_validation_summary()

    print(f"  reference curves      {len(curves):>6} rows")
    print(f"  monthly completeness  {len(monthly):>6} rows")
    print(f"  missing runs          {len(runs):>6} rows "
          f"(longest {runs['hours'].max():.1f} h)")
    print(f"  data funnel           {len(funnel):>6} stages")
    print(f"  validation summary    {len(summary):>6} checks "
          f"({int((summary['result'] == 'PASS').sum())} pass, "
          f"{int((summary['result'] == 'FAIL').sum())} fail)")


if __name__ == "__main__":
    main()
