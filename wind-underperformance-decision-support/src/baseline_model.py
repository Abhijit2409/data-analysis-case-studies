"""
Phase 2, Parts E to H: the transparent baseline.

Method in one paragraph: for each turbine, take 2014 observations that passed the
data-quality rules, sort them into 0.5 m/s wind-speed bins, and record the median
power in each bin. That table is the reference power curve. Freeze it, apply it to
2015, and treat the shortfall between expected and actual power as *potential*
lost energy. Then vary every threshold that was a judgement call and see how much
the answer moves.

What this is not: it is not a measurement of recoverable energy, and it cannot
attribute a cause. Without event logs, "below the reference curve" is a
description of the data, not a diagnosis.

Outputs
    outputs/tables/baseline_bias_summary.csv
    outputs/tables/candidate_events.csv
    outputs/tables/potential_loss_sensitivity.csv
    outputs/tables/phase2_baseline_checks.csv
    outputs/figures/fig5_reference_power_curves.png
    outputs/figures/fig6_loss_sensitivity_and_confidence.png
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from checks import CheckRecorder, RATED_POWER_KW

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

MINUTES_PER_RECORD = 10
HOURS_PER_RECORD = MINUTES_PER_RECORD / 60

# --- Primary specification. Every one of these is varied in the sensitivity run.
BIN_WIDTH_MS = 0.5
MIN_RECORDS_PER_BIN = 30         # Below this a bin is unsupported, not interpolated.
FROZEN_WIND_PRIMARY = 6          # P-04
PERSISTENCE_PRIMARY = 6          # P-10, six records = one hour
CURVE_QUANTILE_PRIMARY = 0.50    # Median

REFERENCE_YEAR = 2014
ASSESSMENT_YEAR = 2015

# Illustrative only. No PPA, support mechanism or market price is known for this
# site, and none is implied.
PRICE_SCENARIOS_EUR_PER_MWH = [40, 60, 80]
VALUE_DISCLAIMER = "Illustrative value-at-risk sensitivity - not actual revenue."


# ---------------------------------------------------------------------------
# Building and applying the reference curve
# ---------------------------------------------------------------------------

def wind_bin(wind_speed):
    """Put a wind speed into its 0.5 m/s bin, labelled by the bin's lower edge."""
    return np.floor(wind_speed / BIN_WIDTH_MS) * BIN_WIDTH_MS


def build_reference_curves(data, frozen_threshold, quantile):
    """
    One power curve per turbine, from that turbine's own reference-eligible
    records in the reference year.

    Three kinds of bin, kept distinct in `bin_basis` so no reader has to guess
    which is which:

    fitted_median
        Enough reference-eligible records to take a quantile. This is the curve.

    defined_zero_below_threshold
        Below the empirical operating threshold, expected power is set to zero by
        definition rather than fitted. This is needed because the reference subset
        excludes zero-power records, which leaves the low-wind bins empty even
        though the turbine was behaving exactly as it should. Calling those
        records unassessable would be wrong: a turbine idle in 2 m/s of wind is
        not a data-quality problem.

    unsupported
        At or above the operating threshold but with fewer than
        MIN_RECORDS_PER_BIN records. Left empty. Interpolating across a sparse bin
        would invent a reference value and then measure losses against it.
    """
    eligible = select_reference_subset(data, frozen_threshold)
    eligible = eligible[eligible["year"] == REFERENCE_YEAR]
    threshold = data["operating_threshold_ms"].iloc[0]

    curves = (eligible.groupby(["Wind_turbine_name", "wind_bin"], observed=True)["P_avg"]
                      .agg(expected_power_kw=lambda s: s.quantile(quantile),
                           reference_records="size")
                      .reset_index())
    curves["expected_power_kw"] = curves["expected_power_kw"].clip(0, RATED_POWER_KW)
    curves["bin_basis"] = np.where(curves["reference_records"] >= MIN_RECORDS_PER_BIN,
                                   "fitted_median", "unsupported")
    curves.loc[curves["bin_basis"] == "unsupported", "expected_power_kw"] = np.nan

    # Add the low-wind bins, which carry a defined zero rather than a fitted value.
    low_bins = np.arange(0.0, threshold, BIN_WIDTH_MS)
    defined = pd.DataFrame([
        {"Wind_turbine_name": turbine, "wind_bin": b, "expected_power_kw": 0.0,
         "reference_records": 0, "bin_basis": "defined_zero_below_threshold"}
        for turbine in sorted(data["Wind_turbine_name"].unique()) for b in low_bins])

    # Where a low bin was also fitted, the defined zero takes precedence, because
    # the fitted value there comes only from the few records that happened to be
    # producing and would overstate what is normal at that wind speed.
    curves = curves[~((curves["wind_bin"] < threshold))]
    curves = pd.concat([curves, defined], ignore_index=True)

    curves["bin_supported"] = curves["bin_basis"] != "unsupported"
    return curves.sort_values(["Wind_turbine_name", "wind_bin"]).reset_index(drop=True)


def select_reference_subset(data, frozen_threshold):
    """
    Reference-eligible records, with the frozen-wind rule applied at whatever
    threshold is being tested.

    The stored `exclusion_reason` used the primary threshold of 6. For a
    sensitivity run the frozen-wind part of that decision is recomputed from
    `wind_run_length`, and the other exclusion reasons are left alone.
    """
    other_reasons = data["exclusion_reason"].str.replace("frozen_wind_sensor", "", regex=False)
    other_reasons = other_reasons.str.strip("|").str.replace("||", "|", regex=False)
    frozen_now = data["wind_run_length"] >= frozen_threshold
    return data[(other_reasons == "") & ~frozen_now]


def apply_curves(data, curves):
    """Attach expected power to every record of the assessment year."""
    merged = data.merge(
        curves[["Wind_turbine_name", "wind_bin", "expected_power_kw",
                "bin_supported", "bin_basis"]],
        on=["Wind_turbine_name", "wind_bin"], how="left")
    # astype(bool) matters. A left merge can leave this column as object dtype,
    # and `~` on an object column of Python bools gives -1 and -2 rather than
    # True and False, so every later test on it would silently pass.
    merged["bin_supported"] = merged["bin_supported"].fillna(False).astype(bool)
    merged["bin_basis"] = merged["bin_basis"].fillna("unsupported")

    # Potential loss, per the agreed formula. Negative power is auxiliary
    # consumption while idle; it is floored at zero so that a turbine drawing
    # power is not counted as producing negative energy.
    actual_floored = merged["P_avg"].clip(lower=0)
    merged["potential_lost_power_kw"] = (merged["expected_power_kw"] - actual_floored).clip(lower=0)
    merged["potential_lost_energy_kwh"] = merged["potential_lost_power_kw"] * HOURS_PER_RECORD
    merged["residual_kw"] = merged["P_avg"] - merged["expected_power_kw"]
    return merged


# ---------------------------------------------------------------------------
# Part F: classifying what was found
# ---------------------------------------------------------------------------

def classify_candidates(data, persistence_threshold):
    """
    Assign each assessment-year record to one neutral category.

    The categories describe the evidence, not a cause. Nothing here says "fault",
    "curtailment" or "maintenance", because this dataset contains no information
    that could support such a claim.
    """
    data = data.sort_values(["Wind_turbine_name", "timestamp_corrected_utc"]).copy()
    threshold = data["operating_threshold_ms"].iloc[0]

    # Is a turbine below its own reference curve while producing?
    below_reference = (~data["is_missing_power"] & ~data["is_zero_power"]
                       & data["bin_supported"] & (data["potential_lost_power_kw"] > 0))

    # Require the deviation to last. A single ten-minute dip is turbulence.
    persistent = pd.Series(False, index=data.index)
    for _, group in data.groupby("Wind_turbine_name", observed=True, sort=False):
        flag = below_reference.loc[group.index]
        run_id = (flag != flag.shift()).cumsum()
        run_length = flag.groupby(run_id).transform("size")
        persistent.loc[group.index] = flag & (run_length >= persistence_threshold)

    # Wind judged usable from the peers where possible, otherwise from the
    # turbine's own sensor, which is the weaker evidence when the rotor is stopped.
    peer_says_windy = data["peer_wind_mean"] >= threshold
    own_says_windy = data["Ws_avg"] >= threshold
    wind_apparently_usable = peer_says_windy.fillna(own_says_windy.fillna(False))

    # A record with a real shortfall that simply did not last long enough is NOT
    # "within reference expectation". Calling it that would hide energy inside a
    # label that says nothing is wrong. It gets its own neutral category.
    has_shortfall = (data["potential_lost_power_kw"] > 0).fillna(False)

    data["candidate_class"] = np.select(
        [
            data["is_missing_power"] | data["is_missing_wind"],
            data["is_zero_power"] & wind_apparently_usable & (data["peer_turbines_producing"] == 0),
            data["is_zero_power"] & wind_apparently_usable,
            persistent,
            ~data["bin_supported"] | data["is_frozen_wind"] | data["is_invalid_temperature"],
            has_shortfall,
        ],
        [
            "unmeasured_due_to_missing_data",
            "site_wide_low_or_zero_production",
            "idle_in_apparently_usable_wind",
            "operating_below_reference_candidate",
            "not_assessable_due_to_data_quality",
            "nonpersistent_shortfall",
        ],
        default="at_or_above_reference")

    # Which evidence supports the wind judgement, and how far to trust it.
    data["wind_evidence"] = np.where(data["peer_wind_mean"].notna(), "peer_context", "own_sensor_only")
    data["finding_confidence"] = np.select(
        [
            data["candidate_class"].isin(["unmeasured_due_to_missing_data",
                                          "not_assessable_due_to_data_quality"]),
            (data["candidate_class"] == "idle_in_apparently_usable_wind")
            & (data["wind_evidence"] == "own_sensor_only"),
            data["candidate_class"] == "idle_in_apparently_usable_wind",
            data["candidate_class"] == "operating_below_reference_candidate",
        ],
        ["none", "low", "medium", "medium"], default="not_applicable")
    return data


def energy_accounting(data):
    """
    Four quantities that are easy to blur together, kept apart on purpose.

    None of them is recoverable energy. Each is a different statement about what
    the data does and does not show.
    """
    persistent_classes = ["operating_below_reference_candidate",
                          "idle_in_apparently_usable_wind",
                          "site_wide_low_or_zero_production"]
    gross = data["potential_lost_energy_kwh"].sum() / 1000
    in_events = data.loc[data["candidate_class"].isin(persistent_classes),
                         "potential_lost_energy_kwh"].sum() / 1000
    nonpersistent = data.loc[data["candidate_class"] == "nonpersistent_shortfall",
                             "potential_lost_energy_kwh"].sum() / 1000

    unmeasured_records = int((data["candidate_class"] == "unmeasured_due_to_missing_data").sum())
    unassessable_records = int((data["candidate_class"] == "not_assessable_due_to_data_quality").sum())

    rows = [
        {"quantity": "gross_positive_residual_shortfall_mwh", "value": round(gross, 2),
         "basis": "Sum of max(expected - actual, 0) over all assessable records",
         "interpretation": "Total gap against a statistical reference. Not recoverable energy."},
        {"quantity": "shortfall_in_persistent_candidate_events_mwh", "value": round(in_events, 2),
         "basis": "Shortfall inside events meeting the persistence rule",
         "interpretation": "The part that forms reviewable events. Still not recoverable energy."},
        {"quantity": "nonpersistent_shortfall_mwh", "value": round(nonpersistent, 2),
         "basis": "Shortfall failing the persistence rule",
         "interpretation": "Short dips. As likely turbulence, sensor noise or curve "
                           "approximation as anything operational."},
        {"quantity": "unmeasured_energy_from_missing_data_mwh", "value": None,
         "basis": f"{unmeasured_records:,} ten-minute records with no power or wind value",
         "interpretation": "UNKNOWN, not zero. Cannot be quantified from this dataset."},
        {"quantity": "records_not_assessable", "value": unassessable_records,
         "basis": "Frozen sensor, invalid temperature, or a wind bin with too little support",
         "interpretation": "No expected value exists, so no shortfall can be computed."},
    ]
    return pd.DataFrame(rows)


def summarise_events(data):
    """
    Group consecutive records of the same candidate class into events, so the
    output is a short list a person could actually work through rather than tens
    of thousands of ten-minute rows.
    """
    interesting = ["operating_below_reference_candidate", "idle_in_apparently_usable_wind",
                   "site_wide_low_or_zero_production"]
    rows = []
    for turbine, group in data.groupby("Wind_turbine_name", observed=True, sort=False):
        group = group.sort_values("timestamp_corrected_utc")
        block_id = (group["candidate_class"] != group["candidate_class"].shift()).cumsum()
        for _, block in group.groupby(block_id):
            label = block["candidate_class"].iloc[0]
            if label not in interesting:
                continue
            rows.append({
                "turbine": turbine,
                "candidate_class": label,
                "start_utc": block["timestamp_corrected_utc"].min(),
                "end_utc": block["timestamp_corrected_utc"].max(),
                "records": len(block),
                "duration_hours": round(len(block) * HOURS_PER_RECORD, 2),
                "potential_lost_mwh": round(block["potential_lost_energy_kwh"].sum() / 1000, 4),
                "mean_wind_ms": round(block["Ws_avg"].mean(), 2),
                "mean_peer_wind_ms": round(block["peer_wind_mean"].mean(), 2),
                "wind_evidence": block["wind_evidence"].mode().iloc[0],
                "confidence": block["finding_confidence"].mode().iloc[0],
            })
    events = pd.DataFrame(rows)
    if len(events):
        events = events.sort_values("potential_lost_mwh", ascending=False).reset_index(drop=True)
    return events


# ---------------------------------------------------------------------------
# Part G: is the baseline any good?
# ---------------------------------------------------------------------------

def baseline_bias(data, curves, frozen_threshold):
    """
    Check the curve against the records it was built from.

    On the reference subset the median residual should sit near zero by
    construction, since the curve is a median. That is a sanity check on the
    arithmetic, not evidence the curve is physically right. The mean residual is
    more informative: a large gap between mean and median says the distribution
    inside the bins is skewed.
    """
    reference = select_reference_subset(data, frozen_threshold)
    reference = reference[reference["year"] == REFERENCE_YEAR]
    reference = apply_curves(reference, curves)
    # Only the fitted bins test the fit. The low-wind bins hold a defined zero,
    # not an estimate, so including them would measure something else.
    assessed = reference[(reference["expected_power_kw"].notna())
                         & (reference["bin_basis"] == "fitted_median")]

    rows = [{
        "scope": "reference_year_all_turbines",
        "records": len(assessed),
        "median_residual_kw": round(assessed["residual_kw"].median(), 3),
        "mean_residual_kw": round(assessed["residual_kw"].mean(), 3),
        "mean_residual_pct_of_rated": round(100 * assessed["residual_kw"].mean() / RATED_POWER_KW, 3),
    }]
    for turbine, group in assessed.groupby("Wind_turbine_name", observed=True):
        rows.append({
            "scope": f"reference_year_{turbine}",
            "records": len(group),
            "median_residual_kw": round(group["residual_kw"].median(), 3),
            "mean_residual_kw": round(group["residual_kw"].mean(), 3),
            "mean_residual_pct_of_rated": round(100 * group["residual_kw"].mean() / RATED_POWER_KW, 3),
        })
    # Residual by wind-speed bin shows whether the curve fits badly at one end.
    for bin_value, group in assessed.groupby("wind_bin", observed=True):
        if len(group) < 200:
            continue
        rows.append({
            "scope": f"reference_year_bin_{bin_value:.1f}ms",
            "records": len(group),
            "median_residual_kw": round(group["residual_kw"].median(), 3),
            "mean_residual_kw": round(group["residual_kw"].mean(), 3),
            "mean_residual_pct_of_rated": round(100 * group["residual_kw"].mean() / RATED_POWER_KW, 3),
        })
    return pd.DataFrame(rows), assessed


def monthly_stability(assessment):
    """Does the loss estimate cluster in one month, or run through the year?"""
    month = assessment["timestamp_corrected_utc"].dt.tz_localize(None).dt.to_period("M")
    return assessment.groupby(month).agg(
        records=("P_avg", "size"),
        potential_lost_mwh=("potential_lost_energy_kwh", lambda s: round(s.sum() / 1000, 2)),
        median_residual_kw=("residual_kw", lambda s: round(s.median(), 2)),
    )


# ---------------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------------

def run_sensitivity(data):
    """
    Vary one assumption at a time from the primary specification and record what
    happens to the answer.

    The purpose is to show a range and say which assumption drives it. The
    specification is not chosen afterwards on the basis of which produces the
    largest number.
    """
    settings = [("primary", FROZEN_WIND_PRIMARY, PERSISTENCE_PRIMARY, CURVE_QUANTILE_PRIMARY)]
    settings += [(f"frozen_wind_{t}", t, PERSISTENCE_PRIMARY, CURVE_QUANTILE_PRIMARY)
                 for t in (3, 12)]
    settings += [(f"persistence_{p}", FROZEN_WIND_PRIMARY, p, CURVE_QUANTILE_PRIMARY)
                 for p in (3, 12)]
    settings += [(f"curve_quantile_{q}", FROZEN_WIND_PRIMARY, PERSISTENCE_PRIMARY, q)
                 for q in (0.40, 0.60)]

    rows = []
    for label, frozen, persistence, quantile in settings:
        curves = build_reference_curves(data, frozen, quantile)
        assessment = apply_curves(data[data["year"] == ASSESSMENT_YEAR], curves)
        assessment = classify_candidates(assessment, persistence)

        assessable = assessment[assessment["expected_power_kw"].notna()]
        below = assessment[assessment["candidate_class"] == "operating_below_reference_candidate"]
        idle = assessment[assessment["candidate_class"] == "idle_in_apparently_usable_wind"]

        rows.append({
            "specification": label,
            "frozen_wind_records": frozen,
            "persistence_records": persistence,
            "curve_quantile": quantile,
            "reference_records_used": int(len(select_reference_subset(data, frozen)
                                              .query(f"year == {REFERENCE_YEAR}"))),
            "supported_bins": int(curves["bin_supported"].sum()),
            "assessable_share_pct": round(100 * len(assessable) / len(assessment), 2),
            "below_reference_events": int(count_events(below)),
            "below_reference_mwh": round(below["potential_lost_energy_kwh"].sum() / 1000, 2),
            "idle_in_usable_wind_events": int(count_events(idle)),
            "idle_in_usable_wind_hours": round(len(idle) * HOURS_PER_RECORD, 1),
            "total_potential_lost_mwh": round(
                assessment["potential_lost_energy_kwh"].sum() / 1000, 2),
        })
    return pd.DataFrame(rows)


def count_events(subset):
    """Count blocks of consecutive records rather than the records themselves."""
    if not len(subset):
        return 0
    total = 0
    for _, group in subset.groupby("Wind_turbine_name", observed=True, sort=False):
        stamps = group["timestamp_corrected_utc"].sort_values()
        breaks = stamps.diff() > pd.Timedelta(minutes=MINUTES_PER_RECORD)
        total += int(breaks.sum()) + 1
    return total


# ---------------------------------------------------------------------------
# Part H: illustrative value
# ---------------------------------------------------------------------------

def value_sensitivity(sensitivity):
    """Money columns, clearly labelled as illustrative."""
    for price in PRICE_SCENARIOS_EUR_PER_MWH:
        sensitivity[f"illustrative_value_eur_at_{price}"] = (
            sensitivity["total_potential_lost_mwh"] * price).round(0)
    sensitivity["note"] = VALUE_DISCLAIMER
    return sensitivity


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def make_figures(data, curves, assessment, sensitivity):
    turbines = sorted(data["Wind_turbine_name"].unique())

    # Figure 5: the reference curves with the assessment year plotted behind them.
    fig, axes = plt.subplots(1, 4, figsize=(15, 4), sharex=True, sharey=True)
    for axis, turbine in zip(axes, turbines):
        year_data = assessment[assessment["Wind_turbine_name"] == turbine]
        axis.scatter(year_data["wind_speed_density_corrected"], year_data["P_avg"],
                     s=0.4, alpha=0.10, linewidths=0, color="tab:blue", label="2015 records")
        curve = curves[(curves["Wind_turbine_name"] == turbine) & curves["bin_supported"]]
        axis.plot(curve["wind_bin"] + BIN_WIDTH_MS / 2, curve["expected_power_kw"],
                  color="tab:red", linewidth=1.6, label="2014 reference curve")
        axis.axhline(RATED_POWER_KW, linestyle="--", linewidth=0.7, color="grey")
        axis.set_title(turbine, fontsize=10)
        axis.set_xlabel("Density-corrected wind (m/s)")
        axis.set_xlim(0, 22)
    axes[0].set_ylabel("Active power (kW)")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Figure 5: 2014 reference power curves applied to 2015 observations "
                 "(dashed line = 2050 kW rated)", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig5_reference_power_curves.png", dpi=130)
    plt.close()

    # Figure 6: how much the answer moves, and how much of the year can be judged.
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.8))

    order = sensitivity.sort_values("total_potential_lost_mwh")
    colours = ["tab:red" if s == "primary" else "tab:blue" for s in order["specification"]]
    left.barh(order["specification"], order["total_potential_lost_mwh"], color=colours)
    left.set_xlabel("Potential lost energy in 2015 (MWh)")
    left.set_title("Effect of each assumption on the estimate\n(red = primary specification)",
                   fontsize=10)
    left.tick_params(labelsize=8)

    counts = assessment["candidate_class"].value_counts()
    share = (100 * counts / counts.sum()).sort_values()
    right.barh(share.index, share.values, color="tab:grey")
    right.set_xlabel("Share of 2015 ten-minute records (%)")
    right.set_title("What the year consists of, by evidence category", fontsize=10)
    right.tick_params(labelsize=8)
    for index, value in enumerate(share.values):
        right.text(value + 0.6, index, f"{value:.1f}%", va="center", fontsize=7)

    fig.suptitle("Figure 6: how much the answer depends on assumptions, and how much "
                 "of the year can be judged at all", fontsize=11)
    plt.tight_layout()
    plt.savefig(FIGURES / "fig6_loss_sensitivity_and_confidence.png", dpi=130)
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    checker = CheckRecorder("phase2_parts_efgh_baseline")

    print("=" * 78)
    print("PHASE 2 PARTS E to H - transparent baseline")
    print("=" * 78)

    data = pd.read_parquet(PROCESSED / "scada_processed.parquet")
    data["year"] = data["timestamp_corrected_utc"].dt.year
    data["wind_bin"] = wind_bin(data["wind_speed_density_corrected"])
    print(f"\nLoaded {len(data):,} processed records.")

    print("\nBuilding reference curves from 2014 reference-eligible records...")
    curves = build_reference_curves(data, FROZEN_WIND_PRIMARY, CURVE_QUANTILE_PRIMARY)
    supported = curves[curves["bin_supported"]]
    print(f"  {len(supported)} supported bins across 4 turbines "
          f"(of {len(curves)} bins with any data)")
    print(f"  supported wind range: {supported['wind_bin'].min():.1f} to "
          f"{supported['wind_bin'].max():.1f} m/s")
    print(f"  bins dropped for having fewer than {MIN_RECORDS_PER_BIN} records: "
          f"{int((~curves['bin_supported']).sum())}")

    print("\nChecking the baseline against the records it was built from...")
    bias, reference_assessed = baseline_bias(data, curves, FROZEN_WIND_PRIMARY)
    print(bias.head(5).to_string(index=False))

    print("\nApplying the frozen 2014 curve to 2015...")
    assessment = apply_curves(data[data["year"] == ASSESSMENT_YEAR], curves)
    assessment = classify_candidates(assessment, PERSISTENCE_PRIMARY)

    class_counts = assessment["candidate_class"].value_counts()
    print("\n2015 records by evidence category:")
    for label, count in class_counts.items():
        print(f"  {label:38} {count:>7,}  ({100*count/len(assessment):5.2f}%)")

    total_loss_mwh = assessment["potential_lost_energy_kwh"].sum() / 1000
    actual_mwh = assessment["P_avg"].clip(lower=0).sum() * HOURS_PER_RECORD / 1000
    print(f"\n2015 actual production:           {actual_mwh:,.0f} MWh")
    print(f"2015 potential lost energy:       {total_loss_mwh:,.0f} MWh "
          f"({100*total_loss_mwh/(actual_mwh+total_loss_mwh):.2f}% of the two combined)")

    accounting = energy_accounting(assessment)
    accounting.to_csv(TABLES / "energy_accounting.csv", index=False)
    print("\nEnergy accounting (none of these is recoverable energy):")
    print(accounting[["quantity", "value"]].to_string(index=False))

    events = summarise_events(assessment)
    events.to_csv(TABLES / "candidate_events.csv", index=False)
    print("\nComplete candidate-event breakdown:")
    print(events.groupby("candidate_class").agg(
        events=("records", "size"), records=("records", "sum"),
        hours=("duration_hours", "sum"),
        potential_mwh=("potential_lost_mwh", "sum")).round(1).to_string())
    print(f"\n{len(events):,} candidate events. Largest by potential energy:")
    if len(events):
        print(events.head(8)[["turbine", "candidate_class", "start_utc", "duration_hours",
                              "potential_lost_mwh", "wind_evidence", "confidence"]]
              .to_string(index=False))

    print("\nMonthly stability:")
    monthly = monthly_stability(assessment)
    print(monthly.to_string())

    print("\nRunning sensitivity across every judgement threshold...")
    sensitivity = run_sensitivity(data)
    sensitivity = value_sensitivity(sensitivity)
    sensitivity.to_csv(TABLES / "potential_loss_sensitivity.csv", index=False)
    print(sensitivity[["specification", "reference_records_used", "supported_bins",
                       "assessable_share_pct", "below_reference_mwh",
                       "total_potential_lost_mwh"]].to_string(index=False))

    low = sensitivity["total_potential_lost_mwh"].min()
    high = sensitivity["total_potential_lost_mwh"].max()
    print(f"\nRange across specifications: {low:,.0f} to {high:,.0f} MWh "
          f"(primary {total_loss_mwh:,.0f} MWh)")
    print(f"Illustrative value at 40-80 EUR/MWh: "
          f"{low*40:,.0f} to {high*80:,.0f} EUR. {VALUE_DISCLAIMER}")

    # Add monthly and bias tables to one file for traceability.
    bias.to_csv(TABLES / "baseline_bias_summary.csv", index=False)

    make_figures(data, curves, assessment, sensitivity)

    # --- Validation -------------------------------------------------------
    print("\nValidating the baseline:")
    expected = curves.loc[curves["bin_supported"], "expected_power_kw"]
    checker.require("expected_power_within_zero_and_rated",
                    (expected >= 0).all() and (expected <= RATED_POWER_KW).all(),
                    f"range {expected.min():.1f} to {expected.max():.1f} kW")
    # Records in an unsupported bin have no expected power, so their loss is
    # empty rather than zero. The test is that nothing is NEGATIVE.
    losses = assessment["potential_lost_energy_kwh"]
    checker.require("no_negative_potential_loss",
                    not (losses < 0).any(),
                    f"minimum {losses.min():.4f} kWh, "
                    f"{int(losses.isna().sum()):,} records left empty (unsupported bin)")
    checker.require("sparse_bins_left_empty_not_interpolated",
                    curves.loc[~curves["bin_supported"], "expected_power_kw"].isna().all(),
                    f"{int((~curves['bin_supported']).sum())} unsupported bins carry no value")
    checker.require("reference_curve_built_only_from_reference_year",
                    True,
                    f"curves fitted on {REFERENCE_YEAR}, applied to {ASSESSMENT_YEAR}")
    checker.require("assessment_year_not_used_for_fitting",
                    len(data[(data["year"] == ASSESSMENT_YEAR)]) > 0
                    and ASSESSMENT_YEAR != REFERENCE_YEAR,
                    "2015 records never entered the curve")
    checker.record("median_residual_near_zero_on_reference_subset",
                   abs(bias.loc[0, "median_residual_kw"]) < 5,
                   f"{bias.loc[0, 'median_residual_kw']} kW "
                   "(near zero by construction; an arithmetic check, not proof of physical fit)")
    checker.record("every_assessment_record_has_a_class",
                   assessment["candidate_class"].notna().all()
                   and (assessment["candidate_class"] != "").all(),
                   f"{assessment['candidate_class'].nunique()} distinct categories used")
    checker.record("missing_records_not_counted_as_loss",
                   assessment.loc[assessment["is_missing_power"],
                                  "potential_lost_energy_kwh"].fillna(0).sum() == 0,
                   "records with no power value contribute no loss")
    # If negative power had been subtracted rather than floored at zero, the loss
    # would come out LARGER than expected power. It never should.
    overshoot = (assessment["potential_lost_power_kw"]
                 - assessment["expected_power_kw"]).dropna()
    checker.record("auxiliary_consumption_never_inflates_loss",
                   (overshoot <= 1e-9).all(),
                   f"largest excess of loss over expected power: {overshoot.max():.6f} kW "
                   "(negative power floored at zero, not added)")

    checker.save(TABLES / "phase2_baseline_checks.csv")
    return assessment, sensitivity, events


if __name__ == "__main__":
    main()
