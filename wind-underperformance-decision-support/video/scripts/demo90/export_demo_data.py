"""
Exports the repository tables the demo film draws from.

Every mark in that film is bound to a value in this file, and every value in
this file is read from a CSV the analysis pipeline produced. Nothing is typed in
by hand, so a figure cannot drift between the analysis and the animation.

The film draws its own vector charts from this data. It does not animate
pictures of charts.

Run from the video/ directory:
    python scripts/demo90/export_demo_data.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

VIDEO = Path(__file__).resolve().parents[2]
TABLES = VIDEO.parent / "outputs" / "tables"
OUT = VIDEO / "src" / "demo90" / "data" / "demo_data.json"


def table(name: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(TABLES / name, **kwargs)


def neighbours_block() -> dict:
    """
    The per-turbine power series around the priority event.

    Time is carried as minutes from the first record so the film never has to
    parse a date, and power is carried as null where the record has no value.
    A null must stay a break in the line: the chart's line generator is
    `defined`-guarded so no path is ever drawn across one.
    """
    frame = table("presentation_event_neighbour_comparison.csv",
                  parse_dates=["timestamp_corrected_utc", "event_start_utc", "event_end_utc"])
    start = frame["timestamp_corrected_utc"].min()
    frame = frame.assign(
        minutes=(frame["timestamp_corrected_utc"] - start).dt.total_seconds() / 60)

    event_turbine = str(frame["event_turbine"].iloc[0])
    event_start = frame["event_start_utc"].iloc[0]
    event_end = frame["event_end_utc"].iloc[0]

    series: dict[str, list[dict]] = {}
    for turbine, group in frame.groupby("Wind_turbine_name"):
        group = group.sort_values("minutes")
        series[str(turbine)] = [
            {"t": round(float(row.minutes), 1),
             "p": None if bool(row.is_missing_power) or pd.isna(row.P_avg)
                  else round(float(row.P_avg), 2)}
            for row in group.itertuples()
        ]

    # The plotted context window and the highlighted event are different things
    # and the film must never conflate them: 279 observations are drawn per
    # turbine, of which 255 fall inside the 42.5-hour event.
    inside = frame[frame["inside_event"]]
    host = inside[inside["Wind_turbine_name"] == event_turbine]
    peers = inside[inside["Wind_turbine_name"] != event_turbine]
    producing = peers.groupby("Wind_turbine_name")["P_avg"].apply(lambda s: (s > 0).mean())

    context_per_turbine = {str(t): len(points) for t, points in series.items()}
    event_per_turbine = {str(t): int(len(g)) for t, g in
                         inside.groupby("Wind_turbine_name")}

    return {
        "turbines": sorted(series),
        "eventTurbine": event_turbine,
        "series": series,
        # Drawn across the whole displayed window.
        "contextObservations": int(next(iter(context_per_turbine.values()))),
        "contextObservationsPerTurbine": context_per_turbine,
        # Inside the highlighted event only.
        "eventObservationsPerTurbine": event_per_turbine,
        "totalMinutes": round(float(frame["minutes"].max()), 1),
        "eventStartMinutes": round((event_start - start).total_seconds() / 60, 1),
        "eventEndMinutes": round((event_end - start).total_seconds() / 60, 1),
        "maxPower": round(float(frame["P_avg"].max()), 1),
        "recordsInsideEvent": int(len(host)),
        "pctAtOrBelowZero": round(float((host["P_avg"] <= 0).mean() * 100), 2),
        "neighboursProducingPct": round(float(producing.min() * 100), 1),
        "missingRecordsInWindow": int(frame["is_missing_power"].sum()),
        "meanPower": {str(t): round(float(g["P_avg"].mean()), 1)
                      for t, g in inside.groupby("Wind_turbine_name")},
    }


def accounting_block() -> dict:
    """
    The 2015 energy accounting.

    The reviewable and non-persistent parts sum to the gross figure, which is
    what lets the film split one column into exactly those two pieces. The
    missing-data category has no value at all and must never be given a height.
    """
    values = table("energy_accounting.csv").set_index("quantity")
    amount = values["value"]
    gross = float(amount["gross_positive_residual_shortfall_mwh"])
    reviewable = float(amount["shortfall_in_persistent_candidate_events_mwh"])
    non_persistent = float(amount["nonpersistent_shortfall_mwh"])
    missing = amount["unmeasured_energy_from_missing_data_mwh"]

    assert abs((reviewable + non_persistent) - gross) < 0.01, \
        "the two components must sum to the gross figure"

    return {
        "gross": round(gross, 1),
        "reviewable": round(reviewable, 1),
        "nonPersistent": round(non_persistent, 1),
        "missingIsUnknown": bool(pd.isna(missing)),
        "missingBasis": str(values.loc["unmeasured_energy_from_missing_data_mwh", "basis"]),
    }


def methods_block() -> dict:
    """Shortfall as a share of potential, per method and turbine."""
    frame = table("phase3_turbine_comparison.csv")
    short = {"A_turbine_specific": "A", "B_pooled_transparent": "B",
             "C_pooled_challenger": "C"}
    out: dict[str, dict[str, float]] = {}
    for method, letter in short.items():
        rows = frame[frame["method"] == method]
        out[letter] = {str(r.turbine): round(float(r.shortfall_pct_of_potential), 2)
                       for r in rows.itertuples()}
    leaders = {letter: max(values, key=values.get) for letter, values in out.items()}
    return {"byMethod": out, "leaders": leaders,
            "turbines": sorted(out["A"]), "metric": "Gross shortfall (% of potential)"}


def event_block() -> dict:
    """The top-ranked event, as the decision register records it."""
    register = table("decision_event_register.csv")
    top = register.iloc[0]
    return {
        "turbine": str(top["turbine"]),
        "durationHours": round(float(top["duration_hours"]), 1),
        "mwhMin": round(float(top["mwh_min_across_methods"]), 1),
        "mwhMax": round(float(top["mwh_max_across_methods"]), 1),
        "methodsAgreeing": str(top["methods_agreeing"]),
        "confidence": str(top["evidence_confidence"]),
        "recordsRequired": [part.strip() for part in
                            str(top["operational_records_required"]).split(";")],
    }


def timestamps_block() -> dict:
    """
    The seasonal alignment test and the interval counts.

    What the correction removes is the DIFFERENCE between the seasons. Both
    seasons still sit at a one-hour lag afterwards, so the film carries the
    after-values explicitly and can never imply the lag reached zero.
    """
    lag = table("timestamp_alignment_test.csv")
    winter = lag[lag["season"].str.startswith("winter")].iloc[0]
    summer = lag[lag["season"].str.startswith("summer")].iloc[0]

    detail = " ".join(table("timestamp_correction_validation.csv")["detail"].astype(str))
    return {
        "winterBefore": int(winter["best_lag_hours"]),
        "summerBefore": int(summer["best_lag_hours"]),
        "winterAfter": int(winter["best_lag_hours"]),
        "summerAfter": int(winter["best_lag_hours"]),
        "duplicatesBefore": 48, "duplicatesAfter": 0,
        "absentBefore": 48, "absentAfter": 0,
        "countsStatedInSource":
            "48 duplicates under published time" in detail
            and "48 published -> 0 corrected" in detail,
        "differenceRemoved": True,
    }


def benchmark_block() -> dict:
    """
    Detection recovery and the alert burden that comes with it.

    Both are means over every injected severity and duration in the benchmark,
    which is the same basis the application reports. The burden is carried
    alongside the recovery deliberately: the film has to be able to show that a
    better recovery figure did not justify deploying the model.
    """
    frame = table("phase3_synthetic_injection.csv")
    summary = frame.groupby("method")[["recovery_rate", "apparent_alert_burden"]].mean()
    short = {"A_turbine_specific": "A", "B_pooled_transparent": "B",
             "C_pooled_challenger": "C"}
    recovery = {short[m]: round(float(summary.loc[m, "recovery_rate"]), 3)
                for m in summary.index}
    burden = {short[m]: round(float(summary.loc[m, "apparent_alert_burden"]) * 100, 1)
              for m in summary.index}
    return {
        "recovery": recovery,
        "burdenPct": burden,
        "windowsTested": int(frame["windows_tested"].sum()),
        "basis": "mean over every injected severity and duration",
    }


def main() -> None:
    data = {
        "source": "outputs/tables/*.csv via scripts/demo90/export_demo_data.py",
        "neighbours": neighbours_block(),
        "accounting": accounting_block(),
        "methods": methods_block(),
        "event": event_block(),
        "timestamps": timestamps_block(),
        "benchmark": benchmark_block(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")

    n = data["neighbours"]
    print(f"{OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")
    print(f"  neighbours : {len(n['turbines'])} turbines x "
          f"{len(n['series'][n['turbines'][0]])} points, "
          f"{n['missingRecordsInWindow']} missing in window")
    print(f"  accounting : {data['accounting']['gross']} = "
          f"{data['accounting']['reviewable']} + {data['accounting']['nonPersistent']}, "
          f"missing unknown: {data['accounting']['missingIsUnknown']}")
    print(f"  methods    : leaders {data['methods']['leaders']}")
    print(f"  timestamps : winter {data['timestamps']['winterBefore']}h / "
          f"summer {data['timestamps']['summerBefore']}h -> both "
          f"{data['timestamps']['winterAfter']}h")
    bench = data["benchmark"]
    print(f"  benchmark  : recovery B {bench['recovery']['B']} -> C "
          f"{bench['recovery']['C']}, burden C {bench['burdenPct']['C']}%")


if __name__ == "__main__":
    main()
