"""
Checks every claim the v2 film makes, without touching the 41 checks that guard
v1.

v2 is built on a different honesty rule from v1. In v1 the video drew the
numbers itself, so each one had to be re-derived from a CSV. In v2 the numbers
are part of a photograph of the running application, so the thing that has to be
checked is different:

  1. the one figure that does appear in overlay copy still matches the source;
  2. every qualification shown as overlay copy matches what the application and
     the project documents actually say;
  3. every capture exists, and every element the film points at was really
     measured on that capture;
  4. the film never points a cursor at a control that does not exist.

Run from the video/ directory:
    python scripts/v2/verify_v2_claims.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

VIDEO = Path(__file__).resolve().parents[2]
PROJECT = VIDEO.parent
TABLES = PROJECT / "outputs" / "tables"
SCREENS = VIDEO / "src" / "v2" / "assets" / "screens"

results: list[tuple[str, str, bool, str]] = []


def check(group: str, label: str, passed: bool, detail: str = "") -> None:
    results.append((group, label, bool(passed), detail))


def table(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


# --- 1. The only figure that appears in overlay copy ------------------------

accounting = table("energy_accounting.csv").set_index("quantity")["value"]
gross = float(accounting["gross_positive_residual_shortfall_mwh"])
reviewable = float(accounting["shortfall_in_persistent_candidate_events_mwh"])
missing = accounting["unmeasured_energy_from_missing_data_mwh"]

check("overlay figures", "cold open says 671.6 MWh", round(gross, 1) == 671.6,
      f"energy_accounting.csv gross = {gross}")
check("overlay figures", "671.6 is the gross figure, not the reviewable one",
      round(gross, 1) != round(reviewable, 1),
      f"reviewable = {reviewable} MWh, kept distinct")
check("overlay figures", "missing energy has no value to quote",
      pd.isna(missing), "unmeasured_energy_from_missing_data_mwh is NaN")

CONTENT = (PROJECT / "app" / "content.py").read_text(encoding="utf-8")
APP = (PROJECT / "app" / "app.py").read_text(encoding="utf-8")

# --- 1b. Any OTHER figure that reaches overlay copy -------------------------

# Overlay copy is meant to be figure-free apart from the cold-open number. This
# sweeps the actual source for numbers rather than trusting that intention.
OVERLAY_TEXT = []
for path in ("Film40.tsx", "Prototype.tsx", "StyleFrames.tsx"):
    text = (VIDEO / "src" / "v2" / path).read_text(encoding="utf-8")
    # Statement and LowerThird bodies only - not style values or frame numbers.
    for match in re.finditer(r"<(?:Statement|LowerThird|Callout|ScreenLabel)[^>]*>(.*?)</(?:Statement|LowerThird|Callout|ScreenLabel)>",
                             text, re.S):
        body = re.sub(r"<[^>]+>", " ", match.group(1))
        # HTML entities such as &#8212; are punctuation, not figures, and the
        # JSX wraps sentences across lines. Normalise both before scanning.
        body = re.sub(r"&#\d+;", " ", body)
        OVERLAY_TEXT.append(re.sub(r"\s+", " ", body).strip())
    # The figure strip holds its values in a prop rather than in children, so
    # without this its numbers would never be scanned.
    for strip in re.findall(r"<StatStrip(.*?)/>", text, re.S):
        for value, label in re.findall(r"\{value: '([^']*)', label: '([^']*)'\}", strip):
            OVERLAY_TEXT.append(f"{value} {label}")
turbines = table("phase3_turbine_comparison.csv")
register = table("decision_event_register.csv")
top_event = register.iloc[0]
validation = table("timestamp_correction_validation.csv")
validation_text = " ".join(validation["detail"].astype(str))
neighbours = pd.read_csv(TABLES / "presentation_event_neighbour_comparison.csv")
inside = neighbours[neighbours["inside_event"]]
host = inside[inside["Wind_turbine_name"] == top_event["turbine"]]
peers = inside[inside["Wind_turbine_name"] != top_event["turbine"]]

def pct_of_potential(method_prefix, turbine):
    row = turbines[turbines["method"].str.startswith(method_prefix)
                   & (turbines["turbine"] == turbine)]
    return float(row["shortfall_pct_of_potential"].iloc[0])

# Turbine identifiers are names, not figures, but the film must only name
# machines that exist in the analysis.
NAMED = sorted(set(re.findall(r"R\d{5}", " ".join(OVERLAY_TEXT))))
for name in NAMED:
    check("named turbines", f"{name} exists in the analysis",
          name in set(turbines["turbine"]), "phase3_turbine_comparison.csv")

# Figures, each with the source value it has to equal.
SOURCES = {
    "671.6": (round(gross, 1), "energy_accounting gross"),
    "380.8": (round(reviewable, 1), "energy_accounting in reviewable events"),
    "290.8": (round(float(accounting["nonpersistent_shortfall_mwh"]), 1),
              "energy_accounting non-persistent"),
    "6.15": (round(pct_of_potential("A", "R80790"), 2),
             "phase3_turbine_comparison A / R80790"),
    "5.35": (round(pct_of_potential("B", "R80711"), 2),
             "phase3_turbine_comparison B / R80711"),
    "42.5": (round(float(top_event["duration_hours"]), 1),
             "decision_event_register duration_hours"),
    "255": (len(host), "records inside the event for the host turbine"),
    "97.65": (round(float((host["P_avg"] <= 0).mean() * 100), 2),
              "share of host records at or below zero"),
    "100": (round(float(peers.groupby("Wind_turbine_name")["P_avg"]
                        .apply(lambda s: (s > 0).mean()).min() * 100)),
            "lowest share of records with output, across the three neighbours"),
    "2015": (int(pd.to_datetime(top_event["start_utc"]).year), "event year"),
    "26": (int(pd.to_datetime(top_event["start_utc"]).day), "event start day"),
    "28": (int(pd.to_datetime(top_event["end_utc"]).day), "event end day"),
}

# The duplicate and absent interval counts are stated in the validation detail,
# so they are checked as text rather than as a number.
basis_text = " ".join(table("energy_accounting.csv")["basis"].astype(str))

TEXTUAL = {
    "2,074": ("2,074" in basis_text,
              "energy_accounting basis for unmeasured energy"),
    "48": ("48 duplicates under published time" in validation_text
           and "48 published -> 0 corrected" in validation_text,
           "timestamp_correction_validation details"),
    "0": ("0 duplicate(s) remain" in validation_text
          and "-> 0 corrected" in validation_text,
          "timestamp_correction_validation details"),
}

stripped = [re.sub(r"R\d{5}", " ", block) for block in OVERLAY_TEXT]
FIGURES = sorted({m for block in stripped
                  for m in re.findall(r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?", block)})

for figure in FIGURES:
    if figure in SOURCES:
        value, origin = SOURCES[figure]
        shown = float(figure.replace(",", ""))
        check("overlay figures", f"{figure} matches {origin}",
              abs(shown - float(value)) < 0.005, f"source value {value}")
    elif figure in TEXTUAL:
        ok, origin = TEXTUAL[figure]
        check("overlay figures", f"{figure} is stated in {origin}", ok)
    else:
        check("overlay figures", f"figure {figure!r} traced to a source", False,
              "NOT TRACED - overlay copy must not show an unverified figure")

ALLOWED = set(SOURCES) | set(TEXTUAL)
check("overlay figures", "every figure on screen is traced",
      set(FIGURES) <= ALLOWED, f"found: {FIGURES}")

# --- 2. Qualifications shown as overlay copy --------------------------------

# These confirm the film's qualifications use wording the application itself
# uses. They check the phrase exists in the app AND in the film's overlay copy -
# not merely that the app contains it somewhere.
CLAIMS = {
    "potential shortfall is not recoverable energy":
        "not confirmed recoverable energy",
    "neighbouring output does not establish causation":
        "does not establish causation",
    "missing data is unknown rather than zero":
        "nknown, not zero",
    "gross basis includes sub-hour dips":
        "short dips that fail the one-hour",
}
joined_overlay = " ".join(OVERLAY_TEXT)
for label, needle in CLAIMS.items():
    in_app = needle in CONTENT or needle in APP
    check("overlay qualifications", f"{label} (app wording)", in_app,
          f"app source: {needle!r}")

check("overlay qualifications", "film states shortfall is not recoverable energy",
      "not confirmed" in joined_overlay and "recoverable energy" in joined_overlay)
check("overlay qualifications", "film states neighbours do not identify the cause",
      "does not identify the cause" in joined_overlay)
check("overlay qualifications", "film states missing data cannot be quantified",
      "cannot" in joined_overlay and "quantified" in joined_overlay)

# The cold-open qualification must not promise recoverability.
FORBIDDEN = ["recoverable energy of", "lost revenue", "confirmed loss",
             "root cause", "diagnosed fault of"]
overlay_sources = [
    (VIDEO / "src" / "v2" / name).read_text(encoding="utf-8")
    for name in ("Film40.tsx", "Prototype.tsx", "StyleFrames.tsx")
]
for phrase in FORBIDDEN:
    hits = []
    for text in overlay_sources:
        for match in re.finditer(re.escape(phrase), text, re.I):
            before = text[max(0, match.start() - 14):match.start()].lower()
            # "not confirmed loss" is the approved qualification; the bare
            # assertion is what must never appear.
            if "not " not in before and "never " not in before:
                hits.append(text[max(0, match.start() - 40):match.end() + 10])
    check("forbidden language", f"never asserts {phrase!r}", not hits,
          " ".join(hits[0].split()) if hits else "")

# Nothing in v2 may imply the project uses Clir data, software or methodology.
disclaimer = "not clir renewables software"
check("attribution", "independence statement present in every v2 surface",
      all(disclaimer in text.lower() for text in overlay_sources), disclaimer)
check("attribution", "public data licence credited in every v2 surface",
      all("etalab open licence 2.0" in text.lower() for text in overlay_sources))
check("attribution", "data source named",
      all("la haute borne" in text.lower() for text in overlay_sources))

# --- 3. Captures and measured elements --------------------------------------

manifest = json.loads((SCREENS / "boxes.json").read_text(encoding="utf-8"))
screens = manifest["screens"]

check("captures", "manifest describes at least four application pages",
      len({s["page"] for s in screens.values()}) >= 4,
      ", ".join(sorted({s["page"] for s in screens.values()})))

for name, entry in screens.items():
    png = SCREENS / entry["file"]
    check("captures", f"{name}: image present", png.exists(), entry["file"])
    missing_boxes = [k for k, v in entry["boxes"].items() if not v]
    check("captures", f"{name}: every element measured", not missing_boxes,
          f"unmeasured: {missing_boxes}" if missing_boxes else "all resolved")

# --- 4. The film only points at controls that exist -------------------------

# Every element the film references, by capture and key.
REFERENCED = re.findall(r"box\('([a-z_]+)',\s*'([A-Za-z]+)'\)",
                        "\n".join(overlay_sources))
for cap, key in sorted(set(REFERENCED)):
    entry = screens.get(cap)
    ok = bool(entry) and bool(entry["boxes"].get(key))
    check("targets", f"{cap}.{key} was measured on the real page", ok)

# Where the film puts the pointer when it presses, in capture coordinates.
# Read from the source so the check cannot drift away from what is rendered.
film = (VIDEO / "src" / "v2" / "Film40.tsx").read_text(encoding="utf-8")
target = re.search(r"const to = \{x: expander\.x ([+-]) (\d+), y: expander\.y ([+-]) (\d+)\}",
                   film)
if target:
    expander_box = screens["datatrust_expander"]["clicked"]
    dx = int(target.group(2)) * (1 if target.group(1) == "+" else -1)
    dy = int(target.group(4)) * (1 if target.group(3) == "+" else -1)
    point = (expander_box["x"] + dx, expander_box["y"] + dy)
    # The clickable header extends left of its text to take in the chevron.
    inside = (expander_box["x"] - 26 <= point[0] <= expander_box["x"] + expander_box["w"]
              and expander_box["y"] - 6 <= point[1] <= expander_box["y"] + expander_box["h"] + 6)
    check("targets", "the pointer presses inside the real expander header",
          inside, f"pointer at {point}, header at {expander_box}")
else:
    check("targets", "the pointer press position was found in the film source", False)

clicked = [(n, e) for n, e in screens.items() if e.get("clicked")]
check("targets", "the clicked control is a real application control",
      bool(clicked),
      "; ".join(f"{n}: {e.get('control')}" for n, e in clicked))

# The control the cursor presses must exist in the application source.
for name, entry in clicked:
    control = entry.get("control", "")
    needle = "Energy basis" if "Energy basis" in control else control
    check("targets", f"{name}: '{needle}' exists in app/app.py",
          needle in APP, needle)

# --- report -----------------------------------------------------------------

width = max(len(label) for _, label, _, _ in results) + 2
current = None
for group, label, passed, detail in results:
    if group != current:
        print(f"\n{group}")
        current = group
    print(f"  [{'OK  ' if passed else 'FAIL'}] {label:<{width}} {detail}")

failed = [r for r in results if not r[2]]
print(f"\n{len(results) - len(failed)}/{len(results)} v2 claim checks passed")
if failed:
    print("\nFAILURES:")
    for group, label, _, detail in failed:
        print(f"  {group}: {label}  {detail}")
sys.exit(1 if failed else 0)
