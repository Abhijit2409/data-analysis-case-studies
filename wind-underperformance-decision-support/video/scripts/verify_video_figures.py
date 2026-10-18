"""
Check every figure the video displays against the project's published tables.

The video renders from src/data/video_data.json. That file is generated, but a
generated file can still drift if the export is edited. This reads the JSON back
and re-derives each value independently from outputs/tables/, so a number on
screen cannot disagree with the repository without this failing.

It also checks the claims that are written as prose in the scene components, by
asserting the values those sentences rest on.

Run from the video/ folder:
    python scripts/verify_video_figures.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

VIDEO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = VIDEO_ROOT.parent
TABLES = PROJECT_ROOT / "outputs" / "tables"

checks = []


def check(label, shown, expected, note=""):
    ok = shown == expected
    checks.append(ok)
    status = "OK  " if ok else "FAIL"
    detail = f"shown {shown!r} vs source {expected!r}"
    print(f"  [{status}] {label:<46} {detail}" + (f"  {note}" if note else ""))


def main():
    shown = json.loads((VIDEO_ROOT / "src" / "data" / "video_data.json").read_text())

    print("Scene 2 - timestamp correction (timestamp_correction_validation.csv)")
    ts = pd.read_csv(TABLES / "timestamp_correction_validation.csv")
    check("duplicate intervals after correction", shown["timestamps"]["duplicates"]["after"], 0)
    check("absent intervals after correction", shown["timestamps"]["absent"]["after"], 0)
    check("seasonal lag after correction (h)", shown["timestamps"]["lag"]["after"], 0)
    check("all correction checks passed", shown["timestamps"]["all_passed"],
          bool((ts["result"] == "PASS").all()))
    # The "48" figures are quoted in the detail strings of the checks themselves.
    for key, check_name in [("duplicates", "spring_duplicates_resolved_without_discarding"),
                            ("absent", "autumn_gaps_removed_by_correction")]:
        detail = ts.loc[ts["check"] == check_name, "detail"].iloc[0]
        check(f"{key}: 48 appears in the source detail",
              "48" in detail, True, f"<- {detail[:52]}")

    print("\nScene 3 - ranking reversal (phase3_turbine_comparison.csv)")
    turbines = pd.read_csv(TABLES / "phase3_turbine_comparison.csv")
    pivot = turbines.pivot(index="turbine", columns="method",
                           values="shortfall_pct_of_potential").round(2)
    for row in shown["ranking"]["A"]:
        check(f"method A {row['turbine']}", row["value"],
              float(pivot.loc[row["turbine"], "A_turbine_specific"]))
    for row in shown["ranking"]["B"]:
        check(f"method B {row['turbine']}", row["value"],
              float(pivot.loc[row["turbine"], "B_pooled_transparent"]))
    # The reversal the scene asserts.
    check("A ranks R80790 highest",
          max(shown["ranking"]["A"], key=lambda r: r["value"])["turbine"], "R80790")
    check("B ranks R80711 highest",
          max(shown["ranking"]["B"], key=lambda r: r["value"])["turbine"], "R80711")

    print("\nScene 4 - priority event (presentation_event_neighbour_comparison.csv)")
    neighbours = pd.read_csv(TABLES / "presentation_event_neighbour_comparison.csv")
    inside = neighbours[neighbours["inside_event"]]
    for turbine, group in inside.groupby("Wind_turbine_name"):
        stats = shown["neighbours"]["stats"][turbine]
        check(f"{turbine} records", stats["records"], int(len(group)))
        check(f"{turbine} mean kW", stats["mean_kw"], round(float(group["P_avg"].mean()), 1))
        check(f"{turbine} producing %", stats["producing_pct"],
              round(float(100 * (group["P_avg"] > 0).mean()), 2))
        check(f"{turbine} at or below zero %", stats["at_or_below_zero_pct"],
              round(float(100 * (group["P_avg"] <= 0).mean()), 2))

    register = pd.read_csv(TABLES / "decision_event_register.csv")
    top = register.iloc[0]
    check("event duration (h)", shown["recommendation"]["durationHours"],
          float(top["duration_hours"]))
    check("event turbine", shown["neighbours"]["eventTurbine"], str(top["turbine"]))

    # Missing observations must survive as nulls, never as zeros.
    nulls = sum(1 for line in shown["neighbours"]["series"]
                for point in line["points"] if point["p"] is None)
    source_missing = int(neighbours["P_avg"].isna().sum())
    check("missing observations kept as null", nulls, source_missing,
          "(never converted to zero)")

    print("\nScene 5 - recommendation (decision_event_register.csv)")
    check("methods agreeing", shown["recommendation"]["methodsAgreeing"],
          str(top["methods_agreeing"]))
    source_records = [p.strip() for p in
                      str(top["operational_records_required"]).split(";") if p.strip()]
    check("required records list", shown["recommendation"]["requiredRecords"], source_records)
    check("operator logs is a repository string",
          any("operator logs" in r.lower() for r in source_records), True)

    print("\nScene 6 - validation tally (presentation_validation_summary.csv)")
    summary = pd.read_csv(TABLES / "presentation_validation_summary.csv")
    check("checks passed", shown["validation"]["passed"],
          int((summary["result"] == "PASS").sum()))
    check("checks total", shown["validation"]["total"], int(len(summary)))
    check("documented failure retained", shown["validation"]["documentedFailure"],
          str(summary.loc[summary["result"] == "FAIL", "check"].iloc[0]))

    passed = sum(checks)
    print(f"\n{passed}/{len(checks)} figure checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
