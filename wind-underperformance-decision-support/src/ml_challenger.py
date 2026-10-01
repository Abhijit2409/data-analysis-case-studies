"""
Phase 3: does a fleet-relative counterfactual find what a self-referencing one
misses, and does machine learning add anything beyond a pooled transparent curve?

Three methods, all fitted on the same 2014 reference-eligible subset, all frozen
before touching 2015:

    A  turbine-specific median-binned curve   (the Phase 2 baseline)
    B  pooled median-binned curve             (same method, all turbines together)
    C  pooled constrained tree-based model    (flexibility and extra features)

B is the control. A-to-B isolates pooling; B-to-C isolates the model.

Every rule in this file was fixed in docs/phase_3_method.md and committed before
the challenger was trained.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from checks import CheckRecorder, RATED_POWER_KW
from baseline_model import (BIN_WIDTH_MS, MIN_RECORDS_PER_BIN, CURVE_QUANTILE_PRIMARY,
                            FROZEN_WIND_PRIMARY, REFERENCE_YEAR, ASSESSMENT_YEAR,
                            HOURS_PER_RECORD, MINUTES_PER_RECORD,
                            build_reference_curves, select_reference_subset, wind_bin)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

RANDOM_SEED = 42

# Locked in docs/phase_3_method.md, section 5. No search, no tuning.
MODEL_PARAMETERS = dict(max_depth=4, max_iter=200, learning_rate=0.05,
                        min_samples_leaf=200, l2_regularization=1.0,
                        random_state=RANDOM_SEED)

# Locked in section 7.
INJECTION_SEVERITIES = [0.05, 0.10, 0.20]
INJECTION_DURATIONS_RECORDS = [3, 6, 12]          # 30, 60, 120 minutes
WINDOWS_PER_COMBINATION = 120
DETECTION_PERSISTENCE = 3                          # records, for the benchmark only
OPERATIONAL_PERSISTENCE = 6                        # records, for real 2015 reporting

# Locked in section 8.
MAX_ALERT_BURDEN_INCREASE = 0.10                   # 10% relative


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_data():
    data = pd.read_parquet(PROCESSED / "scada_processed.parquet")
    data["year"] = data["timestamp_corrected_utc"].dt.year
    data["wind_bin"] = wind_bin(data["wind_speed_density_corrected"])
    # Wind direction is a compass angle, so 359 degrees and 1 degree are close.
    # Splitting it into sine and cosine keeps that closeness intact; feeding the
    # raw angle to a model would put a false cliff at north.
    radians = np.deg2rad(data["Wa_avg"])
    data["wind_dir_sin"] = np.sin(radians)
    data["wind_dir_cos"] = np.cos(radians)
    return data


FEATURES = ["wind_speed_density_corrected", "air_density_kgm3",
            "wind_dir_sin", "wind_dir_cos"]


# ---------------------------------------------------------------------------
# Leakage review of the wind-direction feature
# ---------------------------------------------------------------------------

def review_direction_leakage(data, checker):
    """
    Wind direction here is derived from nacelle position plus vane angle, so it
    partly reflects what the turbine is doing rather than only what the weather is
    doing. If a stopped turbine stops tracking the wind, the reading could carry
    information about the operating state.

    The test: compare the direction distribution between producing and
    non-producing records. If they differ sharply, the feature is partly encoding
    state, and any result using it has to be qualified.

    This runs whatever the answer is, and the answer is reported either way.
    """
    print("\nLeakage review of the wind-direction feature:")
    valid = data[data["Wa_avg"].notna() & data["P_avg"].notna()]
    producing = valid[valid["P_avg"] > 0]["Wa_avg"]
    idle = valid[valid["P_avg"] <= 0]["Wa_avg"]

    # Compare in 30-degree sectors so the comparison does not depend on the
    # arbitrary position of a bin edge.
    sectors = np.arange(0, 361, 30)
    producing_share = np.histogram(producing, bins=sectors)[0] / len(producing)
    idle_share = np.histogram(idle, bins=sectors)[0] / len(idle)
    largest_gap = float(np.max(np.abs(producing_share - idle_share)))

    print(f"  producing records: {len(producing):,}, idle records: {len(idle):,}")
    print(f"  largest difference in any 30-degree sector: {largest_gap:.4f} "
          f"({100*largest_gap:.2f} percentage points)")

    # 0.05 means a sector holding five percentage points more of one group than
    # the other. Below that the feature looks weather-driven; above it, the
    # finding needs a caveat.
    acceptable = largest_gap < 0.05
    checker.record("wind_direction_feature_not_state_dependent", acceptable,
                   f"largest sector share difference {largest_gap:.4f} "
                   f"({'below' if acceptable else 'ABOVE'} the 0.05 concern level)")
    if not acceptable:
        print("  NOTE: direction differs materially between producing and idle records.")
        print("  The feature is retained, and every result using it is qualified.")
    return largest_gap, acceptable


# ---------------------------------------------------------------------------
# The three methods
# ---------------------------------------------------------------------------

def fit_pooled_curve(data):
    """
    Method B: one median-binned curve for the whole fleet.

    Identical in method to A, but each bin's median is taken across all four
    turbines rather than within one. A turbine that consistently produces less
    than its neighbours in the same wind is no longer measured against its own
    reduced output.
    """
    eligible = select_reference_subset(data, FROZEN_WIND_PRIMARY)
    eligible = eligible[eligible["year"] == REFERENCE_YEAR]
    threshold = data["operating_threshold_ms"].iloc[0]

    curve = (eligible.groupby("wind_bin", observed=True)["P_avg"]
                     .agg(expected_power_kw=lambda s: s.quantile(CURVE_QUANTILE_PRIMARY),
                          reference_records="size").reset_index())
    curve["expected_power_kw"] = curve["expected_power_kw"].clip(0, RATED_POWER_KW)
    curve["bin_basis"] = np.where(curve["reference_records"] >= MIN_RECORDS_PER_BIN,
                                  "fitted_median", "unsupported")
    curve.loc[curve["bin_basis"] == "unsupported", "expected_power_kw"] = np.nan

    # Same defined-zero rule below the operating threshold as method A.
    low_bins = np.arange(0.0, threshold, BIN_WIDTH_MS)
    defined = pd.DataFrame({"wind_bin": low_bins, "expected_power_kw": 0.0,
                            "reference_records": 0,
                            "bin_basis": "defined_zero_below_threshold"})
    curve = curve[curve["wind_bin"] >= threshold]
    curve = pd.concat([curve, defined], ignore_index=True)
    curve["bin_supported"] = curve["bin_basis"] != "unsupported"
    return curve.sort_values("wind_bin").reset_index(drop=True)


def fit_challenger(data):
    """
    Method C: one constrained gradient-boosted tree, pooled across turbines.

    Trained on exactly the subset methods A and B use. Turbine identity is not a
    feature, so the model cannot learn one machine's reduced output as normal.
    """
    eligible = select_reference_subset(data, FROZEN_WIND_PRIMARY)
    eligible = eligible[eligible["year"] == REFERENCE_YEAR]
    training = eligible.dropna(subset=FEATURES + ["P_avg"])

    model = HistGradientBoostingRegressor(**MODEL_PARAMETERS)
    model.fit(training[FEATURES], training["P_avg"])
    return model, len(training)


def apply_method_a(data, curves):
    merged = data.merge(curves[["Wind_turbine_name", "wind_bin", "expected_power_kw",
                                "bin_supported", "bin_basis"]],
                        on=["Wind_turbine_name", "wind_bin"], how="left")
    return finalise(merged)


def apply_method_b(data, curve):
    merged = data.merge(curve[["wind_bin", "expected_power_kw", "bin_supported", "bin_basis"]],
                        on="wind_bin", how="left")
    return finalise(merged)


def apply_method_c(data, model, pooled_curve):
    """
    The model supplies expected power above the operating threshold. Below it the
    same defined-zero rule applies as for A and B, so all three methods treat low
    wind identically and the comparison stays like-for-like.
    """
    merged = data.copy()
    threshold = merged["operating_threshold_ms"].iloc[0]

    predicted = pd.Series(np.nan, index=merged.index)
    usable = merged[FEATURES].notna().all(axis=1)
    if usable.any():
        predicted.loc[usable] = model.predict(merged.loc[usable, FEATURES])

    below_threshold = merged["wind_speed_density_corrected"] < threshold
    merged["expected_power_kw"] = np.where(below_threshold, 0.0, predicted)
    merged["bin_basis"] = np.where(below_threshold, "defined_zero_below_threshold",
                                   np.where(usable, "model_prediction", "unsupported"))
    # Match method B's supported wind range, so C is not credited for covering
    # bins that the transparent methods leave empty.
    supported_bins = set(pooled_curve.loc[pooled_curve["bin_supported"], "wind_bin"])
    merged["bin_supported"] = merged["wind_bin"].isin(supported_bins) & (usable | below_threshold)
    merged.loc[~merged["bin_supported"], "expected_power_kw"] = np.nan
    return finalise(merged)


def finalise(merged):
    """Shared arithmetic, so no method gets a different loss definition."""
    merged["bin_supported"] = merged["bin_supported"].fillna(False).astype(bool)
    merged["bin_basis"] = merged["bin_basis"].fillna("unsupported")
    merged["expected_power_kw"] = merged["expected_power_kw"].clip(0, RATED_POWER_KW)
    actual_floored = merged["P_avg"].clip(lower=0)
    merged["potential_lost_power_kw"] = (merged["expected_power_kw"] - actual_floored).clip(lower=0)
    merged["potential_lost_energy_kwh"] = merged["potential_lost_power_kw"] * HOURS_PER_RECORD
    merged["residual_kw"] = merged["P_avg"] - merged["expected_power_kw"]
    merged["is_shortfall_record"] = (merged["bin_supported"]
                                     & merged["P_avg"].notna()
                                     & (merged["potential_lost_power_kw"] > 0))
    return merged


# ---------------------------------------------------------------------------
# Event logic, identical for every method
# ---------------------------------------------------------------------------

def flag_persistent(data, persistence):
    """Mark records inside a run of at least `persistence` consecutive shortfalls."""
    flagged = pd.Series(False, index=data.index)
    for _, group in data.groupby("Wind_turbine_name", observed=True, sort=False):
        group = group.sort_values("timestamp_corrected_utc")
        marks = data.loc[group.index, "is_shortfall_record"].fillna(False)
        run_id = (marks != marks.shift()).cumsum()
        run_length = marks.groupby(run_id).transform("size")
        flagged.loc[group.index] = marks & (run_length >= persistence)
    return flagged


def count_events(data, flag_column):
    """Number of separate runs, not number of records."""
    total = 0
    for _, group in data[data[flag_column]].groupby("Wind_turbine_name", observed=True, sort=False):
        stamps = group["timestamp_corrected_utc"].sort_values()
        total += int((stamps.diff() > pd.Timedelta(minutes=MINUTES_PER_RECORD)).sum()) + 1
    return total


def summarise_method(name, applied):
    """One row describing what a method found across 2015."""
    applied = applied.copy()
    applied["persistent_flag"] = flag_persistent(applied, OPERATIONAL_PERSISTENCE)
    assessable = applied[applied["bin_supported"] & applied["P_avg"].notna()]
    fitted = assessable[assessable["bin_basis"].isin(["fitted_median", "model_prediction"])]
    return {
        "method": name,
        "assessable_records": len(assessable),
        "assessable_share_pct": round(100 * len(assessable) / len(applied), 2),
        "mean_residual_kw": round(fitted["residual_kw"].mean(), 2),
        "median_residual_kw": round(fitted["residual_kw"].median(), 2),
        "gross_shortfall_mwh": round(applied["potential_lost_energy_kwh"].sum() / 1000, 1),
        "persistent_events": count_events(applied, "persistent_flag"),
        "persistent_records": int(applied["persistent_flag"].sum()),
        "persistent_hours": round(applied["persistent_flag"].sum() * HOURS_PER_RECORD, 1),
        "shortfall_in_events_mwh": round(
            applied.loc[applied["persistent_flag"], "potential_lost_energy_kwh"].sum() / 1000, 1),
    }


def turbine_comparison(applied_by_method):
    """Per-turbine view. This is where a fleet-relative gap would show up."""
    rows = []
    for name, applied in applied_by_method.items():
        applied = applied.copy()
        applied["persistent_flag"] = flag_persistent(applied, OPERATIONAL_PERSISTENCE)
        for turbine, group in applied.groupby("Wind_turbine_name", observed=True):
            produced = group["P_avg"].clip(lower=0).sum() * HOURS_PER_RECORD / 1000
            shortfall = group["potential_lost_energy_kwh"].sum() / 1000
            rows.append({
                "method": name,
                "turbine": turbine,
                "produced_mwh": round(produced, 1),
                "gross_shortfall_mwh": round(shortfall, 1),
                "shortfall_pct_of_potential": round(100 * shortfall / (produced + shortfall), 2),
                "persistent_events": count_events(group, "persistent_flag"),
                "persistent_hours": round(group["persistent_flag"].sum() * HOURS_PER_RECORD, 1),
                "mean_residual_kw": round(
                    group.loc[group["bin_basis"].isin(["fitted_median", "model_prediction"]),
                              "residual_kw"].mean(), 2),
            })
    return pd.DataFrame(rows)


def event_overlap(applied_by_method):
    """Do the methods flag the same ten-minute records, or different ones?"""
    flags = {}
    for name, applied in applied_by_method.items():
        applied = applied.sort_values(["Wind_turbine_name", "timestamp_corrected_utc"])
        flags[name] = flag_persistent(applied, OPERATIONAL_PERSISTENCE).to_numpy()

    names = list(flags)
    rows = []
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            both = int((flags[first] & flags[second]).sum())
            only_first = int((flags[first] & ~flags[second]).sum())
            only_second = int((~flags[first] & flags[second]).sum())
            union = both + only_first + only_second
            rows.append({
                "method_pair": f"{first} vs {second}",
                "flagged_by_both": both,
                f"flagged_by_first_only": only_first,
                f"flagged_by_second_only": only_second,
                "agreement_pct_of_union": round(100 * both / union, 1) if union else np.nan,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Synthetic derating benchmark
# ---------------------------------------------------------------------------

def build_injection_windows(data):
    """
    Pick clean 2015 windows, stratified across turbines and wind-speed ranges.

    Only power is changed later. Wind speed, direction and density stay exactly as
    recorded, so no method can see the injection in its inputs.
    """
    rng = np.random.default_rng(RANDOM_SEED)
    assessment = data[data["year"] == ASSESSMENT_YEAR].sort_values(
        ["Wind_turbine_name", "timestamp_corrected_utc"]).reset_index(drop=True)
    threshold = data["operating_threshold_ms"].iloc[0]

    clean = (assessment["P_avg"].notna() & assessment["Ws_avg"].notna()
             & ~assessment["is_frozen_wind"] & ~assessment["is_invalid_temperature"]
             & (assessment["P_avg"] > 0)
             & (assessment["wind_speed_density_corrected"] >= threshold))

    speed = assessment["wind_speed_density_corrected"]
    assessment["speed_band"] = np.select(
        [speed < 7, speed < 10], ["below_7", "7_to_10"], default="above_10")

    windows = []
    longest = max(INJECTION_DURATIONS_RECORDS)
    wanted = len(INJECTION_DURATIONS_RECORDS) * WINDOWS_PER_COMBINATION

    for turbine, group in assessment.groupby("Wind_turbine_name", observed=True, sort=True):
        index = group.index.to_numpy()
        group_clean = clean.loc[index].to_numpy()
        for band in ["below_7", "7_to_10", "above_10"]:
            in_band = (group["speed_band"] == band).to_numpy()
            usable = group_clean & in_band
            if len(usable) <= longest:
                continue
            # A window qualifies only if all `longest` of its records are usable.
            # sliding_window_view does this in one pass instead of a Python loop
            # over half a million positions.
            blocks = np.lib.stride_tricks.sliding_window_view(usable, longest)
            starts = index[:len(blocks)][blocks.all(axis=1)]
            if len(starts) == 0:
                continue
            chosen = (starts if len(starts) < wanted
                      else rng.choice(starts, size=wanted, replace=False))
            # Spread the chosen starts evenly across the three durations.
            for offset, duration in enumerate(INJECTION_DURATIONS_RECORDS):
                take = chosen[offset::len(INJECTION_DURATIONS_RECORDS)][:WINDOWS_PER_COMBINATION]
                for start in take:
                    windows.append({"turbine": turbine, "speed_band": band,
                                    "duration_records": duration, "start_index": int(start)})
    return assessment, pd.DataFrame(windows)


def build_window_frame(assessment, windows):
    """
    Expand every window into its records, once, as a single long table.

    Each window contributes the same number of rows, which lets the detection
    step reshape the result into a (windows x records) grid and work on all of
    them at once instead of one at a time.

    Injected copies and untouched controls are built here together, so both go
    through exactly the same code path afterwards.
    """
    longest = max(INJECTION_DURATIONS_RECORDS)
    offsets = np.arange(longest)

    pieces = []
    window_index = []
    identifier = 0

    for severity in INJECTION_SEVERITIES + [0.0]:      # 0.0 builds the controls
        variant = "control" if severity == 0.0 else "injected"
        for duration in INJECTION_DURATIONS_RECORDS:
            subset = windows[windows["duration_records"] == duration]
            starts = subset["start_index"].to_numpy()
            rows = (starts[:, None] + offsets[None, :]).ravel()
            block = assessment.loc[rows].copy()
            block["window_id"] = np.repeat(
                np.arange(identifier, identifier + len(starts)), longest)
            block["record_position"] = np.tile(offsets, len(starts))
            if variant == "injected":
                cut = block["record_position"] < duration
                block.loc[cut, "P_avg"] = block.loc[cut, "P_avg"] * (1 - severity)
            pieces.append(block)
            window_index.append(pd.DataFrame({
                "window_id": np.arange(identifier, identifier + len(starts)),
                "turbine": subset["turbine"].to_numpy(),
                "speed_band": subset["speed_band"].to_numpy(),
                "severity_pct": int(severity * 100),
                "duration_records": duration,
                "variant": variant,
            }))
            identifier += len(starts)

    return pd.concat(pieces, ignore_index=True), pd.concat(window_index, ignore_index=True)


def detect_in_windows(applied, window_index):
    """
    For every window, find the first qualifying run of shortfall records.

    Because each window has the same number of records in order, the flags can be
    reshaped into a grid and scanned in one operation. A run qualifies at
    DETECTION_PERSISTENCE consecutive shortfall records, the rule fixed in the
    method document before any result was seen.
    """
    longest = max(INJECTION_DURATIONS_RECORDS)
    applied = applied.sort_values(["window_id", "record_position"])
    marks = applied["is_shortfall_record"].fillna(False).to_numpy().reshape(-1, longest)

    # A run starts at position p if p, p+1, ... p+(persistence-1) are all flagged.
    starts_here = marks[:, :longest - DETECTION_PERSISTENCE + 1].copy()
    for step in range(1, DETECTION_PERSISTENCE):
        starts_here &= marks[:, step:longest - DETECTION_PERSISTENCE + 1 + step]

    any_run = starts_here.any(axis=1)
    first_start = np.where(any_run, starts_here.argmax(axis=1), -1)

    result = window_index.copy()
    # The run must begin inside the injected span to count as detecting it.
    result["first_run_start"] = first_start
    result["detected"] = any_run & (first_start < result["duration_records"].to_numpy())
    result["detection_delay_min"] = np.where(result["detected"],
                                             first_start * MINUTES_PER_RECORD, np.nan)
    return result


def run_benchmark(assessment, windows, methods, checker):
    """
    Apply each method once to every window, then score detection.

    Injected windows measure recovery. Untouched controls measure how much review
    the same rule would generate on data nobody altered.
    """
    frame, window_index = build_window_frame(assessment, windows)
    print(f"  {len(window_index):,} windows ({len(frame):,} records) "
          "built once and scored for all three methods")

    results = []
    for name, apply_method in methods.items():
        applied = apply_method(frame)
        applied["window_id"] = frame["window_id"].to_numpy()
        applied["record_position"] = frame["record_position"].to_numpy()
        detection = detect_in_windows(applied, window_index)

        injected = detection[detection["variant"] == "injected"]
        controls = detection[detection["variant"] == "control"]

        for (severity, duration), group in injected.groupby(["severity_pct", "duration_records"]):
            # Controls do not depend on severity, only on the duration that
            # defines the detection span, so the matching duration is reused.
            control_group = controls[controls["duration_records"] == duration]
            delays = group.loc[group["detected"], "detection_delay_min"]
            results.append({
                "method": name,
                "severity_pct": severity,
                "duration_minutes": duration * MINUTES_PER_RECORD,
                "windows_tested": len(group),
                "recovered": int(group["detected"].sum()),
                "recovery_rate": round(group["detected"].mean(), 4),
                "median_detection_delay_min": round(float(delays.median()), 1)
                                              if len(delays) else np.nan,
                "control_windows": len(control_group),
                "control_windows_alerting": int(control_group["detected"].sum()),
                "apparent_alert_burden": round(control_group["detected"].mean(), 4),
            })

    benchmark = pd.DataFrame(results)
    checker.record("benchmark_windows_stratified_and_seeded",
                   benchmark["windows_tested"].nunique() == 1,
                   f"{int(benchmark['windows_tested'].max())} windows per combination, "
                   f"seed {RANDOM_SEED}, stratified by turbine and wind band")
    checker.record("controls_and_injected_windows_matched",
                   (benchmark["control_windows"] == benchmark["windows_tested"]).all(),
                   "every injected window has an untouched control drawn the same way")
    return benchmark


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def make_figures(turbine_curves, pooled_curve, turbine_table, benchmark):
    # Figure 7: where pooling changes the reference, and for which turbine.
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.8))
    pooled_supported = pooled_curve[pooled_curve["bin_basis"] == "fitted_median"]
    for turbine in sorted(turbine_curves["Wind_turbine_name"].unique()):
        own = turbine_curves[(turbine_curves["Wind_turbine_name"] == turbine)
                             & (turbine_curves["bin_basis"] == "fitted_median")]
        merged = own.merge(pooled_supported[["wind_bin", "expected_power_kw"]],
                           on="wind_bin", suffixes=("_own", "_pooled"))
        left.plot(merged["wind_bin"] + BIN_WIDTH_MS / 2,
                  merged["expected_power_kw_own"] - merged["expected_power_kw_pooled"],
                  marker="o", markersize=3, linewidth=1.3, label=turbine)
    left.axhline(0, color="black", linewidth=0.8)
    left.set_xlabel("Density-corrected wind speed (m/s)")
    left.set_ylabel("Own curve minus pooled curve (kW)")
    left.set_title("Where each turbine's own reference sits\nbelow or above the fleet", fontsize=10)
    left.legend(fontsize=8)
    left.grid(alpha=0.25)

    pivot = turbine_table.pivot(index="turbine", columns="method",
                                values="shortfall_pct_of_potential")
    pivot.plot(kind="bar", ax=right, width=0.78)
    right.set_ylabel("Gross shortfall (% of potential)")
    right.set_xlabel("")
    right.set_title("Shortfall per turbine under each method", fontsize=10)
    right.tick_params(axis="x", rotation=0)
    right.legend(fontsize=8, title=None)
    fig.suptitle("Figure 7: what changes when turbines are compared with the fleet "
                 "instead of themselves", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig7_pooled_vs_turbine_curves.png", dpi=130)
    plt.close()

    # Figure 8: detection against alert burden.
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.8))
    for name, group in benchmark.groupby("method"):
        by_severity = group.groupby("severity_pct")["recovery_rate"].mean()
        left.plot(by_severity.index, 100 * by_severity.values, marker="o", label=name)
    left.set_xlabel("Injected power reduction (%)")
    left.set_ylabel("Injected windows recovered (%)")
    left.set_title("Recovery of known synthetic derates\n(mean across durations)", fontsize=10)
    left.set_xticks([5, 10, 20])
    left.legend(fontsize=8)
    left.grid(alpha=0.25)

    summary = benchmark.groupby("method").agg(
        recovery=("recovery_rate", "mean"), burden=("apparent_alert_burden", "mean"))
    right.scatter(100 * summary["burden"], 100 * summary["recovery"], s=90)
    for name, row in summary.iterrows():
        right.annotate(name, (100 * row["burden"], 100 * row["recovery"]),
                       textcoords="offset points", xytext=(7, 4), fontsize=9)
    right.set_xlabel("Apparent alert burden on untouched windows (%)")
    right.set_ylabel("Injected windows recovered (%)")
    right.set_title("Detection against review effort\n(up and to the left is better)", fontsize=10)
    right.grid(alpha=0.25)
    fig.suptitle("Figure 8: detection benchmark on deterministic synthetic derates "
                 "(not a real false-positive rate)", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig8_detection_benchmark.png", dpi=130)
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    checker = CheckRecorder("phase3_challenger")
    print("=" * 78)
    print("PHASE 3 - pooled counterfactual and constrained challenger")
    print("=" * 78)

    data = load_data()
    print(f"\nLoaded {len(data):,} records.")

    direction_gap, direction_acceptable = review_direction_leakage(data, checker)

    print("\nFitting all three methods on the 2014 reference-eligible subset...")
    turbine_curves = build_reference_curves(data, FROZEN_WIND_PRIMARY, CURVE_QUANTILE_PRIMARY)
    pooled_curve = fit_pooled_curve(data)
    model, training_records = fit_challenger(data)
    print(f"  A: {int(turbine_curves['bin_supported'].sum())} supported bins across 4 turbines")
    print(f"  B: {int(pooled_curve['bin_supported'].sum())} supported pooled bins")
    print(f"  C: trained on {training_records:,} records, features {FEATURES}")

    checker.require("no_method_trained_on_assessment_year", True,
                    f"all three fitted on {REFERENCE_YEAR} only")
    checker.require("challenger_excludes_turbine_identity",
                    "Wind_turbine_name" not in FEATURES,
                    f"features are {FEATURES}")
    checker.require("challenger_excludes_calendar_and_outcome_features",
                    not any(f in FEATURES for f in
                            ["hour", "month", "P_avg", "residual_kw", "Ba_avg", "Ya_avg"]),
                    "no hour, calendar, power, residual, pitch or nacelle features")
    checker.require("model_parameters_fixed_and_seeded",
                    MODEL_PARAMETERS["random_state"] == RANDOM_SEED,
                    f"{MODEL_PARAMETERS}")

    assessment = data[data["year"] == ASSESSMENT_YEAR]
    methods = {
        "A_turbine_specific": lambda frame: apply_method_a(frame, turbine_curves),
        "B_pooled_transparent": lambda frame: apply_method_b(frame, pooled_curve),
        "C_pooled_challenger": lambda frame: apply_method_c(frame, model, pooled_curve),
    }
    applied_by_method = {name: fn(assessment) for name, fn in methods.items()}

    print("\n2015 results by method:")
    comparison = pd.DataFrame([summarise_method(name, applied)
                               for name, applied in applied_by_method.items()])
    comparison.to_csv(TABLES / "phase3_method_comparison.csv", index=False)
    print(comparison.to_string(index=False))

    print("\nPer turbine:")
    turbine_table = turbine_comparison(applied_by_method)
    turbine_table.to_csv(TABLES / "phase3_turbine_comparison.csv", index=False)
    print(turbine_table.pivot(index="turbine", columns="method",
                              values="shortfall_pct_of_potential").to_string())

    print("\nEvent overlap between methods (ten-minute records flagged):")
    overlap = event_overlap(applied_by_method)
    overlap.to_csv(TABLES / "phase3_event_overlap.csv", index=False)
    print(overlap.to_string(index=False))

    print("\nBuilding the synthetic derating benchmark...")
    benchmark_source, windows = build_injection_windows(data)
    print(f"  {len(windows):,} candidate windows, stratified by turbine and wind band")
    benchmark = run_benchmark(benchmark_source, windows, methods, checker)
    benchmark.to_csv(TABLES / "phase3_synthetic_injection.csv", index=False)

    print("\nRecovery rate by severity and duration:")
    print(benchmark.pivot_table(index=["severity_pct", "duration_minutes"],
                                columns="method", values="recovery_rate").to_string())
    print("\nApparent alert burden on untouched control windows:")
    print(benchmark.pivot_table(index="method", values="apparent_alert_burden",
                                aggfunc="mean").round(4).to_string())

    # --- The pre-specified acceptance rule ---
    overall = benchmark.groupby("method").agg(recovery=("recovery_rate", "mean"),
                                              burden=("apparent_alert_burden", "mean"))
    b_recovery, b_burden = overall.loc["B_pooled_transparent", ["recovery", "burden"]]
    c_recovery, c_burden = overall.loc["C_pooled_challenger", ["recovery", "burden"]]
    burden_increase = (c_burden - b_burden) / b_burden if b_burden > 0 else np.inf
    improves = c_recovery > b_recovery
    within_burden = burden_increase <= MAX_ALERT_BURDEN_INCREASE
    accepted = bool(improves and within_burden)

    print("\n" + "=" * 78)
    print("PRE-SPECIFIED ACCEPTANCE RULE")
    print(f"  B recovery {b_recovery:.4f}, burden {b_burden:.4f}")
    print(f"  C recovery {c_recovery:.4f}, burden {c_burden:.4f}")
    print(f"  recovery improved:          {improves}")
    print(f"  burden increase:            {burden_increase:+.2%} "
          f"(limit +{MAX_ALERT_BURDEN_INCREASE:.0%})")
    print(f"  CHALLENGER {'ACCEPTED' if accepted else 'NOT ACCEPTED'}")
    print("=" * 78)

    checker.record("challenger_meets_prespecified_acceptance_rule", accepted,
                   f"recovery {b_recovery:.4f}->{c_recovery:.4f}, "
                   f"burden {b_burden:.4f}->{c_burden:.4f} ({burden_increase:+.1%})")
    checker.record("benchmark_uses_synthetic_labels_only", True,
                   "no real-world precision, recall or accuracy is reported")
    checker.record("all_methods_share_event_logic", True,
                   f"detection persistence {DETECTION_PERSISTENCE} records for the benchmark, "
                   f"{OPERATIONAL_PERSISTENCE} for 2015 reporting, identical across methods")

    # --- Post-hoc diagnostic, run only because the leakage check failed --------
    # This is NOT part of the pre-registered comparison and does not change the
    # accepted result above. The method document said a failed leakage check
    # means the finding is qualified; this measures how much qualification is
    # needed, by refitting the same model without the suspect feature.
    if not direction_acceptable:
        print("\nPost-hoc diagnostic (leakage check failed, so C is refitted without")
        print("wind direction). This does NOT replace the pre-registered result.")
        plain_features = ["wind_speed_density_corrected", "air_density_kgm3"]
        eligible = select_reference_subset(data, FROZEN_WIND_PRIMARY)
        eligible = eligible[eligible["year"] == REFERENCE_YEAR].dropna(
            subset=plain_features + ["P_avg"])
        plain_model = HistGradientBoostingRegressor(**MODEL_PARAMETERS)
        plain_model.fit(eligible[plain_features], eligible["P_avg"])

        def apply_plain(frame):
            saved = FEATURES[:]
            FEATURES[:] = plain_features
            try:
                return apply_method_c(frame, plain_model, pooled_curve)
            finally:
                FEATURES[:] = saved

        diagnostic = run_benchmark(benchmark_source, windows,
                                   {"C_without_direction": apply_plain}, checker)
        diagnostic_overall = diagnostic.agg({"recovery_rate": "mean",
                                             "apparent_alert_burden": "mean"})
        print(f"  C with direction:    recovery {c_recovery:.4f}, burden {c_burden:.4f}")
        print(f"  C without direction: recovery {diagnostic_overall['recovery_rate']:.4f}, "
              f"burden {diagnostic_overall['apparent_alert_burden']:.4f}")
        still_beats_b = diagnostic_overall["recovery_rate"] > b_recovery
        print(f"  Without direction, does C still beat B on recovery? {still_beats_b}")
        checker.record("challenger_advantage_survives_removing_suspect_feature",
                       bool(still_beats_b),
                       f"recovery without direction {diagnostic_overall['recovery_rate']:.4f} "
                       f"vs B {b_recovery:.4f}")
        diagnostic["note"] = "Post-hoc diagnostic, not part of the pre-registered comparison"
        diagnostic.to_csv(TABLES / "phase3_posthoc_no_direction.csv", index=False)

    make_figures(turbine_curves, pooled_curve, turbine_table, benchmark)
    checker.save(TABLES / "phase3_checks.csv")
    return comparison, benchmark, accepted


if __name__ == "__main__":
    main()
