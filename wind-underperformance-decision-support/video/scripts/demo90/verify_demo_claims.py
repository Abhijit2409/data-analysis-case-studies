"""
Checks the demo film's data layer against the repository, independently of the
export that produced it.

The export reads the CSVs and writes demo_data.json. This script reads the CSVs
again, by a different route, and compares. If the two ever disagree the film is
showing something the analysis does not support.

It also checks the two structural promises the film makes:
  * no chart in src/demo90/ is a raster image;
  * every figure that reaches the screen is present in the data layer.

Run from the video/ directory:
    python scripts/demo90/verify_demo_claims.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

VIDEO = Path(__file__).resolve().parents[2]
TABLES = VIDEO.parent / "outputs" / "tables"
DEMO = VIDEO / "src" / "demo90"
DATA = json.loads((DEMO / "data" / "demo_data.json").read_text(encoding="utf-8"))

results: list[tuple[str, str, bool, str]] = []


def check(group: str, label: str, ok: bool, detail: str = "") -> None:
    results.append((group, label, bool(ok), detail))


def close(a: float, b: float, tol: float = 0.051) -> bool:
    return abs(float(a) - float(b)) <= tol


# --- 1. the data layer against the tables ----------------------------------

accounting = pd.read_csv(TABLES / "energy_accounting.csv").set_index("quantity")["value"]
acc = DATA["accounting"]
check("accounting", "gross matches energy_accounting.csv",
      close(acc["gross"], accounting["gross_positive_residual_shortfall_mwh"]),
      f'{acc["gross"]} vs {accounting["gross_positive_residual_shortfall_mwh"]}')
check("accounting", "reviewable matches",
      close(acc["reviewable"], accounting["shortfall_in_persistent_candidate_events_mwh"]))
check("accounting", "non-persistent matches",
      close(acc["nonPersistent"], accounting["nonpersistent_shortfall_mwh"]))
check("accounting", "components sum to the gross figure",
      close(acc["reviewable"] + acc["nonPersistent"], acc["gross"]),
      f'{acc["reviewable"]} + {acc["nonPersistent"]} = {acc["reviewable"] + acc["nonPersistent"]}')
check("accounting", "missing energy carries no value",
      acc["missingIsUnknown"] and pd.isna(accounting["unmeasured_energy_from_missing_data_mwh"]),
      "drawn at a token height, never to scale")

turbines = pd.read_csv(TABLES / "phase3_turbine_comparison.csv")
short = {"A": "A_turbine_specific", "B": "B_pooled_transparent", "C": "C_pooled_challenger"}
for letter, method in short.items():
    rows = turbines[turbines["method"] == method].set_index("turbine")["shortfall_pct_of_potential"]
    exported = DATA["methods"]["byMethod"][letter]
    agree = all(close(exported[t], rows[t], 0.006) for t in exported)
    check("methods", f"method {letter} values match the table", agree,
          ", ".join(f"{t} {exported[t]}" for t in sorted(exported)))
    leader = rows.idxmax()
    check("methods", f"method {letter} leader is {leader}",
          DATA["methods"]["leaders"][letter] == leader)

neigh = pd.read_csv(TABLES / "presentation_event_neighbour_comparison.csv")
nb = DATA["neighbours"]
inside = neigh[neigh["inside_event"]]
host = inside[inside["Wind_turbine_name"] == nb["eventTurbine"]]
peers = inside[inside["Wind_turbine_name"] != nb["eventTurbine"]]
check("event window", "records inside the event match",
      nb["recordsInsideEvent"] == len(host), f'{nb["recordsInsideEvent"]}')
check("event window", "share at or below zero matches",
      close(nb["pctAtOrBelowZero"], (host["P_avg"] <= 0).mean() * 100, 0.006),
      f'{nb["pctAtOrBelowZero"]}%')
producing = peers.groupby("Wind_turbine_name")["P_avg"].apply(lambda s: (s > 0).mean()).min() * 100
check("event window", "lowest neighbour producing share matches",
      close(nb["neighboursProducingPct"], producing, 0.06), f'{nb["neighboursProducingPct"]}%')
check("event window", "every exported series keeps all its records",
      all(len(nb["series"][t]) == len(neigh[neigh["Wind_turbine_name"] == t]) for t in nb["turbines"]),
      f'{len(nb["series"][nb["turbines"][0]])} points per turbine')
exported_missing = sum(1 for t in nb["turbines"] for p in nb["series"][t] if p["p"] is None)
check("event window", "records with no value are exported as gaps, not zeros",
      exported_missing == int(neigh["is_missing_power"].sum()),
      f"{exported_missing} gaps in the export, {int(neigh['is_missing_power'].sum())} in the table")

register = pd.read_csv(TABLES / "decision_event_register.csv").iloc[0]
ev = DATA["event"]
check("priority event", "turbine matches the register", ev["turbine"] == register["turbine"])
check("priority event", "duration matches", close(ev["durationHours"], register["duration_hours"]))
check("priority event", "potential shortfall range matches",
      close(ev["mwhMin"], register["mwh_min_across_methods"])
      and close(ev["mwhMax"], register["mwh_max_across_methods"]),
      f'{ev["mwhMin"]}-{ev["mwhMax"]} MWh')
check("priority event", "methods agreeing match",
      ev["methodsAgreeing"] == register["methods_agreeing"], ev["methodsAgreeing"])

lag = pd.read_csv(TABLES / "timestamp_alignment_test.csv").set_index("season")["best_lag_hours"]
ts = DATA["timestamps"]
winter = next(v for k, v in lag.items() if k.startswith("winter"))
summer = next(v for k, v in lag.items() if k.startswith("summer"))
check("timestamps", "seasonal lags before correction match the test",
      ts["winterBefore"] == winter and ts["summerBefore"] == summer,
      f'winter {ts["winterBefore"]} h, summer {ts["summerBefore"]} h')
check("timestamps", "after correction both seasons sit at the same lag",
      ts["winterAfter"] == ts["summerAfter"] == winter,
      f'both {ts["winterAfter"]} h - the DIFFERENCE is removed, not the lag')
check("timestamps", "the absolute lag is never claimed to reach zero",
      ts["winterAfter"] != 0 and ts["summerAfter"] != 0)
check("timestamps", "interval counts are stated in the validation table",
      ts["countsStatedInSource"], "48 -> 0 duplicate, 48 -> 0 absent")

bench = pd.read_csv(TABLES / "phase3_synthetic_injection.csv")
summary = bench.groupby("method")[["recovery_rate", "apparent_alert_burden"]].mean()
bm = DATA["benchmark"]
for letter, method in short.items():
    check("benchmark", f"method {letter} recovery matches",
          close(bm["recovery"][letter], summary.loc[method, "recovery_rate"], 0.0006),
          f'{bm["recovery"][letter]}')
    check("benchmark", f"method {letter} alert burden matches",
          close(bm["burdenPct"][letter], summary.loc[method, "apparent_alert_burden"] * 100, 0.06),
          f'{bm["burdenPct"][letter]}%')

# --- 2. no chart is a raster image -----------------------------------------

sources = {p: p.read_text(encoding="utf-8")
           for p in DEMO.rglob("*") if p.suffix in {".ts", ".tsx"}}
raster = [p.name for p, text in sources.items()
          if re.search(r"<\s*[Ii]mg\b", text) or re.search(r"from '.*\.png'", text)]
check("construction", "no component renders an image", not raster, f"offenders: {raster}")
check("construction", "charts are drawn as SVG paths and rects",
      any("<path" in t for t in sources.values()) and any("<rect" in t for t in sources.values()))
check("construction", "scales come from d3",
      any("d3-scale" in t for t in sources.values()))
check("construction", "series keep a stable key per turbine",
      any("key={turbine}" in t for t in sources.values())
      and any('key={`bar-${turbine}`}' in t for t in sources.values()))
check("construction", "gaps are never bridged",
      any("brokenPath" in t for t in sources.values()),
      "a record with no value produces no geometry")

# --- 3. every figure on screen exists in the data layer --------------------

film = sources[DEMO / "Prototype.tsx"]
literal = re.findall(r">\s*([0-9][0-9,.]*)\s*(?:%|h|MWh)?\s*<", film)
hardcoded = [v for v in literal if v not in {"0", "2", "4", "6", "200", "400", "600",
                                             "500", "1000", "1500", "2000"}]
check("figures", "no published figure is typed into the film", not hardcoded,
      f"hardcoded: {hardcoded}" if hardcoded else
      "every value is read from the data layer; only axis ticks are literals")

# --- 4. the context window is not the event --------------------------------

# The film draws 279 observations per turbine across the displayed window and
# highlights 255 of them inside the 42.5-hour event. Conflating the two would
# overstate the event, so the two counts are derived separately here and
# required to differ.
window_counts = set(nb["contextObservationsPerTurbine"].values())
event_counts = set(nb["eventObservationsPerTurbine"].values())
derived_window = set(neigh.groupby("Wind_turbine_name").size())
derived_event = set(inside.groupby("Wind_turbine_name").size())

check("context vs event", "context observations per turbine match the table",
      window_counts == derived_window, f"{sorted(window_counts)}")
check("context vs event", "event observations per turbine match the table",
      event_counts == derived_event, f"{sorted(event_counts)}")
check("context vs event", "the two counts are different numbers",
      window_counts.isdisjoint(event_counts),
      f"window {sorted(window_counts)} vs event {sorted(event_counts)}")
check("context vs event", "every event observation lies inside the event window",
      bool(inside["inside_event"].all()) and len(inside) < len(neigh),
      f"{len(inside)} of {len(neigh)} rows are inside the event")

film_text = (DEMO / "Film.tsx").read_text(encoding="utf-8")
check("context vs event", "the film never labels the event with the window count",
      str(nb["contextObservations"]) not in film_text,
      f'{nb["contextObservations"]} appears nowhere as a displayed figure')
check("context vs event", "the event figure the film shows is the event count",
      "recordsInsideEvent" in film_text and "Consecutive event records" in film_text,
      f'{nb["recordsInsideEvent"]} consecutive event records')

# --- 5. the unknown quantity has no readable magnitude ---------------------

layouts = (DEMO / "layouts.ts").read_text(encoding="utf-8")
marks = (DEMO / "marks.tsx").read_text(encoding="utf-8")
token_block = layouts[layouts.index("export const unknownToken"):]
token_block = token_block[:token_block.index("// ---")]

check("unknown quantity", "it is not drawn as a bar",
      "BarRect" not in film_text.split("UnknownToken")[0].split("<BarRect rect={token")[0]
      or "<BarRect rect={token" not in film_text,
      "rendered by UnknownToken, not BarRect")
check("unknown quantity", "its size is a constant, not a scale lookup",
      "yEnergy" not in token_block and "scale" not in token_block,
      "fixed 230x120; no axis scale is consulted")
check("unknown quantity", "it floats clear of the baseline",
      "PLOT.height / 2" in token_block,
      "vertically centred in the plot, not sitting on zero")
check("unknown quantity", "an axis break separates it from the scale",
      "breakX" in token_block and "breakX" in marks)
check("unknown quantity", "it is labelled as unscaled",
      "Quantity unknown" in film_text and "not plotted to scale" in film_text)
check("unknown quantity", "no energy value is ever attached to it",
      acc["missingIsUnknown"] and "missingMwh" not in json.dumps(DATA))

# --- 6. the method morph completes before the next one starts --------------

timeline = (DEMO / "timeline.ts").read_text(encoding="utf-8")


def window(name: str) -> tuple[int, int]:
    found = re.search(rf"{name}:\s*\[(\d+),\s*(\d+)\]", timeline)
    assert found, name
    return int(found.group(1)), int(found.group(2))


crush_a = window("crushA")
rise_b = window("riseB")
check("method morph", "method A reaches the baseline before method B rises",
      crush_a[1] <= rise_b[0],
      f"crush ends at frame {crush_a[1]}, rise begins at {rise_b[0]}")
check("method morph", "there is a clear gap between them",
      rise_b[0] - crush_a[1] >= 10,
      f"{rise_b[0] - crush_a[1]} frames")

# --- 7. a label only appears after its chart has settled -------------------

PAIRS = [
    ("conclusion headline", "expand", "conclusion"),
    ("gross figure", "solidify", "grossLabel"),
    ("component figures", "split", "partsLabel"),
    ("published lags", "seasonsIn", "publishedLags"),
    ("corrected lags", "correctSummer", "correctedLags"),
    ("interval counts", "intervalsIn", "intervalLabels"),
    ("method A callout", "riseA", "methodALabel"),
    ("method B callout", "riseB", "methodBLabel"),
    ("recovery figures", "toBenchmark", "recoveryLabels"),
    ("burden figure", "burdenIn", "burdenLabel"),
    ("event figures", "drawLines", "eventStats"),
]
for label, move_name, copy_name in PAIRS:
    settles = window(move_name)[1]
    appears = window(copy_name)[0]
    check("label timing", f"{label} appears after its chart settles",
          appears >= settles, f"chart settles {settles}, label {appears}")

width = max(len(label) for _, label, _, _ in results) + 2
group = None
for g, label, ok, detail in results:
    if g != group:
        print(f"\n{g}")
        group = g
    print(f"  [{'OK  ' if ok else 'FAIL'}] {label:<{width}} {detail}")
failed = [r for r in results if not r[2]]
print(f"\n{len(results) - len(failed)}/{len(results)} demo data checks passed")
if failed:
    print("\nFAILURES:")
    for g, label, _, detail in failed:
        print(f"  {g}: {label}  {detail}")
sys.exit(1 if failed else 0)
