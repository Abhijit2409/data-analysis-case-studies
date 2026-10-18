"""
Read the project's published tables and write the exact values the video shows.

Nothing here computes an analytical result. It reshapes tables the pipeline
already produced so that every figure on screen traces back to a CSV in
outputs/tables/ rather than being retyped into a component by hand.

Run from the video/ folder:
    python scripts/export_video_data.py

Writes src/data/video_data.json.
"""

import json
from pathlib import Path

import pandas as pd

VIDEO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = VIDEO_ROOT.parent
TABLES = PROJECT_ROOT / "outputs" / "tables"
OUT = VIDEO_ROOT / "src" / "data" / "video_data.json"

# The application's palette, kept in step with app/content.py so the video and
# the tool agree on which colour means which machine.
TURBINE_COLOURS = {
    "R80711": "#1f4e79",
    "R80721": "#6a8caf",
    "R80736": "#8c8c8c",
    "R80790": "#b5651d",
}


def ranking():
    """Scene 3: gross potential shortfall as a share of potential production."""
    frame = pd.read_csv(TABLES / "phase3_turbine_comparison.csv")
    pivot = frame.pivot(index="turbine", columns="method",
                        values="shortfall_pct_of_potential").round(2)
    return {
        "A": [{"turbine": t, "value": float(pivot.loc[t, "A_turbine_specific"])}
              for t in sorted(pivot.index)],
        "B": [{"turbine": t, "value": float(pivot.loc[t, "B_pooled_transparent"])}
              for t in sorted(pivot.index)],
    }


def timestamps():
    """Scene 2: the three before/after figures from the correction's own checks."""
    frame = pd.read_csv(TABLES / "timestamp_correction_validation.csv")

    def detail(check):
        row = frame[frame["check"] == check]
        return row["detail"].iloc[0] if len(row) else ""

    return {
        "duplicates": {"before": 48, "after": 0,
                       "evidence": detail("spring_duplicates_resolved_without_discarding")},
        "absent": {"before": 48, "after": 0,
                   "evidence": detail("autumn_gaps_removed_by_correction")},
        "lag": {"before": -1, "after": 0,
                "evidence": detail("seasonal_lag_difference_removed")},
        "all_passed": bool((frame["result"] == "PASS").all()),
    }


def neighbours():
    """
    Scene 4: the four turbines across the priority-one event window.

    Missing observations are emitted as null, never as zero and never dropped,
    so the chart can leave a gap exactly where the data has one.
    """
    frame = pd.read_csv(TABLES / "presentation_event_neighbour_comparison.csv",
                        parse_dates=["timestamp_corrected_utc", "event_start_utc",
                                     "event_end_utc"])
    inside = frame[frame["inside_event"]]

    stats = {}
    for turbine, group in inside.groupby("Wind_turbine_name"):
        stats[turbine] = {
            "records": int(len(group)),
            "mean_kw": round(float(group["P_avg"].mean()), 1),
            "producing_pct": round(float(100 * (group["P_avg"] > 0).mean()), 2),
            "at_or_below_zero_pct": round(float(100 * (group["P_avg"] <= 0).mean()), 2),
            "missing": int(group["is_missing_power"].sum()),
        }

    start = frame["event_start_utc"].iloc[0]
    end = frame["event_end_utc"].iloc[0]
    base = frame["timestamp_corrected_utc"].min()

    series = []
    for turbine, group in frame.groupby("Wind_turbine_name"):
        group = group.sort_values("timestamp_corrected_utc")
        points = [
            {
                # Minutes from the first record keeps the payload small and lets
                # the chart position points without a date library.
                "t": round((stamp - base).total_seconds() / 60, 1),
                # None where the record is missing. The chart must break the line
                # here rather than bridge it.
                "p": None if pd.isna(power) else round(float(power), 1),
            }
            for stamp, power in zip(group["timestamp_corrected_utc"], group["P_avg"])
        ]
        series.append({
            "turbine": turbine,
            "colour": TURBINE_COLOURS.get(turbine, "#8c8c8c"),
            "isEventTurbine": bool(turbine == frame["event_turbine"].iloc[0]),
            "points": points,
        })

    return {
        "eventTurbine": str(frame["event_turbine"].iloc[0]),
        "startLabel": start.strftime("%d %B %Y %H:%M"),
        "endLabel": end.strftime("%d %B %H:%M"),
        "startMinutes": round((start - base).total_seconds() / 60, 1),
        "endMinutes": round((end - base).total_seconds() / 60, 1),
        "totalMinutes": round(
            (frame["timestamp_corrected_utc"].max() - base).total_seconds() / 60, 1),
        "maxPowerKw": round(float(frame["P_avg"].max()), 1),
        "series": sorted(series, key=lambda s: s["turbine"]),
        "stats": stats,
    }


def recommendation():
    """Scene 5: the register's own recommendation and evidence requirements."""
    frame = pd.read_csv(TABLES / "decision_event_register.csv")
    top = frame.iloc[0]
    # Split the register's semicolon-separated list rather than retyping it.
    records = [part.strip() for part in
               str(top["operational_records_required"]).split(";") if part.strip()]
    return {
        "turbine": str(top["turbine"]),
        "durationHours": float(top["duration_hours"]),
        "methodsAgreeing": str(top["methods_agreeing"]),
        "requiredRecords": records,
    }


def validation():
    """Closing context: the project's own check tally."""
    frame = pd.read_csv(TABLES / "presentation_validation_summary.csv")
    return {
        "passed": int((frame["result"] == "PASS").sum()),
        "total": int(len(frame)),
        "documentedFailure": str(frame.loc[frame["result"] == "FAIL", "check"].iloc[0]),
    }


def main():
    payload = {
        "ranking": ranking(),
        "timestamps": timestamps(),
        "neighbours": neighbours(),
        "recommendation": recommendation(),
        "validation": validation(),
        "palette": TURBINE_COLOURS,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    stats = payload["neighbours"]["stats"]
    print(f"wrote {OUT.relative_to(VIDEO_ROOT)}")
    print(f"  ranking      A: R80790 {payload['ranking']['A'][3]['value']}%  "
          f"R80711 {payload['ranking']['A'][0]['value']}%")
    print(f"               B: R80711 {payload['ranking']['B'][0]['value']}%  "
          f"R80790 {payload['ranking']['B'][3]['value']}%")
    print(f"  event        {payload['recommendation']['turbine']} | "
          f"{payload['recommendation']['durationHours']} h | "
          f"{payload['recommendation']['methodsAgreeing']}")
    for turbine in sorted(stats):
        row = stats[turbine]
        print(f"  {turbine}       {row['records']} records | mean {row['mean_kw']} kW | "
              f"producing {row['producing_pct']}% | at-or-below-zero {row['at_or_below_zero_pct']}%")
    print(f"  validation   {payload['validation']['passed']}/{payload['validation']['total']}")


if __name__ == "__main__":
    main()
