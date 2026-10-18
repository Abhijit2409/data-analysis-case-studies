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
    presentation_event_neighbour_comparison.csv  all four turbines over event 1
    presentation_validation_summary.csv    every validation check in one place

and one static figure for use outside the application:

    outputs/figures/fig9_event_neighbour_comparison.png   1080x1350
"""

import glob
from pathlib import Path

import pandas as pd

from baseline_model import (build_reference_curves, FROZEN_WIND_PRIMARY,
                            CURVE_QUANTILE_PRIMARY, ASSESSMENT_YEAR, HOURS_PER_RECORD)
from ml_challenger import load_data, fit_pooled_curve

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"


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


def source_check_files():
    """
    The authoritative validation files, as a {filename: frame} mapping.

    A file counts as authoritative if it carries both a `check` and a `result`
    column. This module's own outputs are skipped: the summary itself has those
    columns, so including it would fold a previous run's rows back in and
    double-count every check.
    """
    found = {}
    for path in sorted(glob.glob(str(TABLES / "*.csv"))):
        name = Path(path).name
        if name.startswith("presentation_"):
            continue
        frame = pd.read_csv(path)
        if "result" not in frame.columns or "check" not in frame.columns:
            continue
        found[name] = frame
    return found


def export_validation_summary():
    """
    Every validation check from every phase, in one table.

    The summary is derived, so it can silently fall behind its sources: it did,
    when the deliverable render checks grew from 11 to 14 and nothing regenerated
    it. The reconciliation below makes that failure loud instead of silent — the
    function refuses to return a summary that disagrees with the files it was
    built from.
    """
    sources = source_check_files()
    pieces = []
    for name, frame in sources.items():
        frame = frame.copy()
        frame["source_file"] = name
        pieces.append(frame[["stage", "check", "result", "detail", "source_file"]])
    summary = pd.concat(pieces, ignore_index=True)

    reconcile_summary(summary, sources)
    summary.to_csv(TABLES / "presentation_validation_summary.csv", index=False)
    return summary


def reconcile_summary(summary, sources=None):
    """
    Confirm a combined summary matches the files it claims to summarise.

    Raises on any mismatch. Returns a short report so callers can print it.
    """
    sources = source_check_files() if sources is None else sources
    expected_rows = sum(len(frame) for frame in sources.values())
    expected_pass = sum(int((frame["result"] == "PASS").sum()) for frame in sources.values())

    problems = []
    if len(summary) != expected_rows:
        problems.append(f"row count {len(summary)} != {expected_rows} across source files")
    actual_pass = int((summary["result"] == "PASS").sum())
    if actual_pass != expected_pass:
        problems.append(f"PASS count {actual_pass} != {expected_pass}")

    missing = set(sources) - set(summary["source_file"].unique())
    if missing:
        problems.append(f"source files absent from the summary: {sorted(missing)}")

    # Per-file counts, so a file that is present but truncated is also caught.
    for name, frame in sources.items():
        in_summary = int((summary["source_file"] == name).sum())
        if in_summary != len(frame):
            problems.append(f"{name}: {in_summary} rows in summary, {len(frame)} in file")

    if problems:
        raise AssertionError(
            "Validation summary does not reconcile with its source files:\n  - "
            + "\n  - ".join(problems)
            + "\nRe-run src/export_presentation_tables.py to regenerate it.")

    return {"rows": expected_rows, "passed": expected_pass,
            "failed": expected_rows - expected_pass, "files": len(sources)}


def export_event_neighbour_comparison(data, priority_rank=1):
    """
    Side-by-side output of all four turbines across one event window.

    The existing event timeline answers "how far below its own expected output
    was this turbine?". This answers a different question: "what were the other
    three machines doing at the same moment?" Both are needed, and neither
    replaces the other.

    Every value is read from the processed dataset. Missing observations stay
    missing — they are never filled, and the chart that consumes this must not
    draw a line across them.
    """
    register = pd.read_csv(TABLES / "decision_event_register.csv",
                           parse_dates=["start_utc", "end_utc"])
    event = register[register["priority_rank"] == priority_rank].iloc[0]

    # Same two hours of lead-in and lead-out as the existing timeline export, so
    # the two charts line up when read side by side.
    pad = pd.Timedelta(hours=2)
    window = data[(data["timestamp_corrected_utc"] >= event["start_utc"] - pad)
                  & (data["timestamp_corrected_utc"] <= event["end_utc"] + pad)].copy()

    frame = window[["Wind_turbine_name", "timestamp_corrected_utc", "P_avg",
                    "Ws_avg", "is_missing_power"]].copy()
    frame["priority_rank"] = priority_rank
    frame["event_turbine"] = event["turbine"]
    frame["event_start_utc"] = event["start_utc"]
    frame["event_end_utc"] = event["end_utc"]
    frame["inside_event"] = ((frame["timestamp_corrected_utc"] >= event["start_utc"])
                             & (frame["timestamp_corrected_utc"] <= event["end_utc"]))
    frame = frame.sort_values(["Wind_turbine_name", "timestamp_corrected_utc"])
    frame.to_csv(TABLES / "presentation_event_neighbour_comparison.csv", index=False)

    inside = frame[frame["inside_event"]]
    stats = (inside.groupby("Wind_turbine_name")
                   .agg(records=("P_avg", "size"),
                        mean_kw=("P_avg", "mean"),
                        producing_pct=("P_avg", lambda s: 100 * (s > 0).mean()),
                        at_or_below_zero_pct=("P_avg", lambda s: 100 * (s <= 0).mean()),
                        missing=("is_missing_power", "sum"))
                   .round(2).reset_index())
    return frame, event, stats


def render_event_neighbour_figure(frame, event, stats):
    """
    Static 1080x1350 rendering of the neighbour comparison, for use as a video or
    social asset.

    Matplotlib rather than Plotly, matching how every other file in
    outputs/figures/ is produced, and avoiding a static-image dependency.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    host = event["turbine"]
    # Same palette the application uses, so the still and the app agree.
    colours = {"R80711": "#1f4e79", "R80721": "#6a8caf",
               "R80736": "#8c8c8c", "R80790": "#b5651d"}

    # 10.8 x 13.5 inches at 100 dpi is exactly 1080 x 1350 px.
    figure = plt.figure(figsize=(10.8, 13.5), dpi=100, facecolor="white")
    # Vertical bands are set explicitly rather than by tight_layout: the figure
    # carries a title block, a stats block and a qualification block as well as
    # the axes, and they must not run into one another.
    axis = figure.add_axes([0.11, 0.37, 0.84, 0.43])

    for turbine, group in frame.groupby("Wind_turbine_name"):
        group = group.sort_values("timestamp_corrected_utc")
        is_host = turbine == host
        # P_avg stays NaN where the record is missing, and matplotlib leaves a
        # gap at a NaN. That is deliberate: a missing record is not zero output.
        axis.plot(group["timestamp_corrected_utc"], group["P_avg"],
                  color=colours.get(turbine, "#8c8c8c"),
                  linewidth=2.6 if is_host else 1.3,
                  alpha=1.0 if is_host else 0.75,
                  zorder=3 if is_host else 2,
                  label=f"{turbine}  (event turbine)" if is_host else turbine)

    axis.axvspan(event["start_utc"], event["end_utc"], color="#b5651d",
                 alpha=0.10, zorder=1, lw=0)
    axis.axhline(0, color="#1a1a1a", linewidth=0.9, zorder=2)

    axis.set_ylabel("Active power (kW)", fontsize=13, labelpad=10)
    axis.set_xlabel("Time (UTC)", fontsize=13, labelpad=10)
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    axis.xaxis.set_major_locator(mdates.HourLocator(interval=8))
    axis.tick_params(labelsize=11)
    axis.grid(color="#e4e4e4", linewidth=0.8)
    for side in ("top", "right"):
        axis.spines[side].set_visible(False)
    axis.legend(loc="upper left", fontsize=11, frameon=False, ncol=2)

    window_label = (f"{event['start_utc']:%d %B %Y %H:%M} to "
                    f"{event['end_utc']:%d %B %H:%M} UTC  ·  "
                    f"{event['duration_hours']:.1f} hours")
    figure.text(0.08, 0.955, f"{host} near zero while neighbouring\nturbines continued producing",
                fontsize=27, fontweight="bold", color="#1a1a1a", va="top", linespacing=1.25)
    figure.text(0.08, 0.868, window_label, fontsize=13.5, color="#5a5a5a", va="top")

    lookup = stats.set_index("Wind_turbine_name")
    lines = []
    for turbine in sorted(lookup.index):
        row = lookup.loc[turbine]
        mark = "   <-- event turbine" if turbine == host else ""
        lines.append(f"{turbine}    mean {row['mean_kw']:>6.1f} kW    "
                     f"producing {row['producing_pct']:>5.1f}% of records{mark}")
    figure.text(0.08, 0.288, "Inside the event window", fontsize=14,
                fontweight="bold", color="#1a1a1a", va="top")
    figure.text(0.08, 0.256, "\n".join(lines), fontsize=12.5, color="#1a1a1a",
                va="top", family="DejaVu Sans Mono", linespacing=1.8)

    figure.text(0.08, 0.148,
                "Observation, not a diagnosed fault. No event codes, work orders or\n"
                "curtailment records exist for this interval, so the cause cannot be\n"
                "established. Neighbouring output shows wind was available; it does not\n"
                "establish causation and does not make the shortfall recoverable energy.",
                fontsize=11.5, color="#5a5a5a", va="top", linespacing=1.6)
    figure.text(0.08, 0.032,
                "Independent analysis of public data: ENGIE La Haute Borne, "
                "Etalab Open Licence 2.0, via OpenOA.",
                fontsize=10, color="#8c8c8c", va="top")

    path = FIGURES / "fig9_event_neighbour_comparison.png"
    figure.savefig(path, dpi=100, facecolor="white")
    plt.close(figure)
    return path


def main():
    print("Exporting presentation-only tables (no analytical result is changed)...")
    data = load_data()

    curves = export_reference_curves(data)
    monthly = export_monthly_completeness(data)
    runs = export_missing_runs(data)
    funnel = export_data_funnel(data)
    neighbours, event, neighbour_stats = export_event_neighbour_comparison(data)
    figure_path = render_event_neighbour_figure(neighbours, event, neighbour_stats)
    summary = export_validation_summary()

    print(f"  reference curves      {len(curves):>6} rows")
    print(f"  monthly completeness  {len(monthly):>6} rows")
    print(f"  missing runs          {len(runs):>6} rows "
          f"(longest {runs['hours'].max():.1f} h)")
    print(f"  data funnel           {len(funnel):>6} stages")
    print(f"  neighbour comparison  {len(neighbours):>6} rows "
          f"({neighbours['Wind_turbine_name'].nunique()} turbines, event rank 1)")
    print(f"  static figure         {figure_path.name}")
    print(f"  validation summary    {len(summary):>6} checks "
          f"({int((summary['result'] == 'PASS').sum())} pass, "
          f"{int((summary['result'] == 'FAIL').sum())} fail) "
          f"- reconciled against {summary['source_file'].nunique()} source files")
    print("\n  Inside the event window:")
    print(neighbour_stats.to_string(index=False))


if __name__ == "__main__":
    main()
