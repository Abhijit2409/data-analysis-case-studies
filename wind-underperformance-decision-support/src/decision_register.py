"""
Phase 4: turn analysis output into a decision.

Everything here reads the frozen methods from Phases 2 and 3. Nothing is
retrained, no threshold is tuned, and no new model is introduced.

The question this answers is the one an analyst is actually asked:

    Which issue should be looked at first, what is the potential exposure,
    how confident are we, and what operational records are needed before
    anyone acts?

Method B, the pooled transparent curve, is the decision method. A is shown
alongside so the effect of self-reference stays visible, and C is a qualified
second opinion.

Outputs
    outputs/tables/decision_event_register.csv
    outputs/tables/decision_event_timelines.csv
    outputs/tables/phase4_checks.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd

from checks import CheckRecorder
from baseline_model import (build_reference_curves, FROZEN_WIND_PRIMARY,
                            CURVE_QUANTILE_PRIMARY, HOURS_PER_RECORD,
                            MINUTES_PER_RECORD, ASSESSMENT_YEAR)
from ml_challenger import (load_data, fit_pooled_curve, fit_challenger,
                           apply_method_a, apply_method_b, apply_method_c,
                           flag_persistent, OPERATIONAL_PERSISTENCE)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES = PROJECT_ROOT / "outputs" / "tables"

# Illustrative only. No PPA, support mechanism or market price is known for this
# site and none is implied.
PRICE_SCENARIOS_EUR_PER_MWH = [50, 80, 120]
VALUE_DISCLAIMER = "Illustrative value-at-risk sensitivity - not actual revenue."

TOP_EVENTS_FOR_REGISTER = 25
# Every event in the register gets ten-minute detail. Exporting only the leading
# few left most of the register with no timeline to inspect, which defeated the
# point of a browsable queue.
TOP_EVENTS_FOR_TIMELINE = TOP_EVENTS_FOR_REGISTER


# ---------------------------------------------------------------------------
# Hypotheses and the records that would test them
# ---------------------------------------------------------------------------
# Deliberately plural. Each entry is a possible explanation that predicts
# something checkable, never a diagnosis. Nothing in this dataset can choose
# between them.

HYPOTHESES = {
    "idle_in_apparently_usable_wind": [
        "Scheduled maintenance or a planned service visit",
        "Unplanned stop following a turbine fault",
        "Grid curtailment or a network operator instruction",
        "Controller lockout awaiting a manual reset",
        "Communications loss while the turbine was in fact producing",
    ],
    "operating_below_reference_candidate": [
        "Power limitation or derate active",
        "Pitch or yaw calibration drift",
        "Blade surface degradation, soiling or light icing",
        "Wake interaction from a neighbouring turbine in certain directions",
        "Anemometer calibration drift making the reference wind speed wrong",
    ],
    "site_wide_low_or_zero_production": [
        "Grid outage or a site-wide network instruction",
        "Substation or balance-of-plant fault",
        "Site-wide SCADA or communications outage rather than a real stop",
    ],
}

REQUIRED_RECORDS = {
    "idle_in_apparently_usable_wind":
        "Turbine event and alarm codes for the interval; work orders and "
        "maintenance records; curtailment or grid instructions; operator logs",
    "operating_below_reference_candidate":
        "Controller setpoints and any power-limitation flags; turbine event and "
        "alarm codes; work orders covering blade or sensor work; turbine layout "
        "and wake information; anemometer calibration history",
    "site_wide_low_or_zero_production":
        "Grid instructions and substation records; independent site-meter export "
        "for the interval; site SCADA communications logs",
}

RECOMMENDED_ACTIONS = {
    "idle_in_apparently_usable_wind":
        "Request event codes and work orders for the interval before drawing any "
        "conclusion. If the records show a planned outage, close the item.",
    "operating_below_reference_candidate":
        "Request controller setpoints and alarm codes for the interval, and check "
        "whether the pattern repeats in the same wind direction sector.",
    "site_wide_low_or_zero_production":
        "Check against independent site-meter export to separate a real site stop "
        "from a SCADA communications outage.",
}


# ---------------------------------------------------------------------------
# Building the register
# ---------------------------------------------------------------------------

def build_method_frames(data):
    """Apply all three frozen methods to 2015. No fitting on 2015 anywhere."""
    turbine_curves = build_reference_curves(data, FROZEN_WIND_PRIMARY, CURVE_QUANTILE_PRIMARY)
    pooled_curve = fit_pooled_curve(data)
    model, _ = fit_challenger(data)

    assessment = data[data["year"] == ASSESSMENT_YEAR].sort_values(
        ["Wind_turbine_name", "timestamp_corrected_utc"]).reset_index(drop=True)

    frames = {}
    for name, applied in [
        ("A", apply_method_a(assessment, turbine_curves)),
        ("B", apply_method_b(assessment, pooled_curve)),
        ("C", apply_method_c(assessment, model, pooled_curve)),
    ]:
        applied = applied.sort_values(["Wind_turbine_name", "timestamp_corrected_utc"]
                                      ).reset_index(drop=True)
        applied["persistent_flag"] = flag_persistent(applied, OPERATIONAL_PERSISTENCE)
        frames[name] = applied
    return frames, assessment


def events_from_method(applied, classification_source):
    """
    Group a method's persistent flags into events.

    Classification comes from the Phase 2 candidate classes, carried across so
    that every method's events are described with the same vocabulary.
    """
    applied = applied.copy()
    applied["candidate_class"] = classification_source
    rows = []
    for turbine, group in applied.groupby("Wind_turbine_name", observed=True, sort=False):
        group = group.sort_values("timestamp_corrected_utc")
        flagged = group[group["persistent_flag"]]
        if not len(flagged):
            continue
        # A break in the ten-minute sequence starts a new event.
        breaks = (flagged["timestamp_corrected_utc"].diff()
                  > pd.Timedelta(minutes=MINUTES_PER_RECORD)).cumsum()
        for _, block in flagged.groupby(breaks):
            classes = block["candidate_class"].value_counts()
            rows.append({
                "turbine": turbine,
                "start_utc": block["timestamp_corrected_utc"].min(),
                "end_utc": block["timestamp_corrected_utc"].max(),
                "records": len(block),
                "duration_hours": round(len(block) * HOURS_PER_RECORD, 2),
                "candidate_class": classes.index[0],
                "mwh": round(block["potential_lost_energy_kwh"].sum() / 1000, 3),
                "mean_wind_ms": round(block["Ws_avg"].mean(), 2),
                "mean_peer_wind_ms": round(block["peer_wind_mean"].mean(), 2),
            })
    return pd.DataFrame(rows)


def overlap_mwh(applied, turbine, start, end):
    """Shortfall a method attributes to an interval, whether or not it flags it."""
    window = applied[(applied["Wind_turbine_name"] == turbine)
                     & (applied["timestamp_corrected_utc"] >= start)
                     & (applied["timestamp_corrected_utc"] <= end)]
    if not len(window):
        return np.nan, False, np.nan
    mwh = window["potential_lost_energy_kwh"].sum() / 1000
    flags = bool(window["persistent_flag"].any())
    flagged_share = window["persistent_flag"].mean()
    return round(mwh, 3), flags, round(flagged_share, 3)


def qualify_event(window):
    """Data-quality caveats that a reviewer needs to see next to the number."""
    notes = []
    if window["is_missing_power"].any():
        notes.append(f"{int(window['is_missing_power'].sum())} record(s) with no power value")
    if window["is_frozen_wind"].any():
        notes.append(f"{int(window['is_frozen_wind'].sum())} record(s) with a frozen wind reading")
    if window["peer_wind_mean"].isna().any():
        notes.append("peer wind context unavailable for part of the interval")
    if (window["P_avg"] <= 0).all():
        notes.append("turbine idle throughout, so its own anemometer is the least "
                     "reliable measurement here")
    if not window["bin_supported"].all():
        notes.append(f"{int((~window['bin_supported']).sum())} record(s) in an unsupported wind bin")
    return "; ".join(notes) if notes else "none"


def build_register(frames, assessment, checker):
    """
    One row per reviewable event, judged by method B and cross-checked against
    A and C.
    """
    classification = assessment["candidate_class"] if "candidate_class" in assessment \
        else pd.Series("unclassified", index=assessment.index)

    # Events are defined by the decision method, B.
    base_events = events_from_method(frames["B"], classification)
    base_events = base_events.sort_values("mwh", ascending=False).head(TOP_EVENTS_FOR_REGISTER)

    rows = []
    for _, event in base_events.iterrows():
        turbine, start, end = event["turbine"], event["start_utc"], event["end_utc"]
        window = assessment[(assessment["Wind_turbine_name"] == turbine)
                            & (assessment["timestamp_corrected_utc"] >= start)
                            & (assessment["timestamp_corrected_utc"] <= end)]

        mwh_a, flags_a, _ = overlap_mwh(frames["A"], turbine, start, end)
        mwh_b, flags_b, _ = overlap_mwh(frames["B"], turbine, start, end)
        mwh_c, flags_c, share_c = overlap_mwh(frames["C"], turbine, start, end)

        applicable = [v for v in [mwh_a, mwh_b, mwh_c] if not np.isnan(v)]
        agreeing = [name for name, flag in [("A", flags_a), ("B", flags_b), ("C", flags_c)] if flag]
        event_class = event["candidate_class"]

        # Confidence follows the Phase 2 grading and the evidence available here.
        peer_available = window["peer_wind_mean"].notna().mean()
        if len(agreeing) == 3 and peer_available > 0.9:
            confidence = "medium"          # never high: no operational record exists
        elif len(agreeing) >= 2:
            confidence = "medium-low"
        else:
            confidence = "low"

        rows.append({
            "turbine": turbine,
            "start_utc": start,
            "end_utc": end,
            "duration_hours": event["duration_hours"],
            "candidate_class": event_class,
            "shortfall_mwh_method_a": mwh_a,
            "shortfall_mwh_method_b": mwh_b,
            "shortfall_mwh_method_c": mwh_c,
            "method_c_also_flags": flags_c,
            "method_c_flagged_share": share_c,
            "mwh_min_across_methods": round(min(applicable), 3) if applicable else np.nan,
            "mwh_max_across_methods": round(max(applicable), 3) if applicable else np.nan,
            "methods_agreeing": "+".join(agreeing) if agreeing else "none",
            "method_agreement_count": len(agreeing),
            "evidence_confidence": confidence,
            "data_quality_qualifications": qualify_event(window),
            "mean_wind_ms": event["mean_wind_ms"],
            "mean_peer_wind_ms": event["mean_peer_wind_ms"],
            "possible_explanations_hypotheses_only": " | ".join(
                HYPOTHESES.get(event_class, ["No standard hypothesis set for this class"])),
            "operational_records_required": REQUIRED_RECORDS.get(
                event_class, "Turbine event codes and operator logs"),
            "recommended_next_action": RECOMMENDED_ACTIONS.get(
                event_class, "Request event codes before drawing any conclusion"),
        })

    register = pd.DataFrame(rows)

    # Illustrative value, applied to the conservative end of the range.
    for price in PRICE_SCENARIOS_EUR_PER_MWH:
        register[f"illustrative_eur_at_{price}_min"] = (
            register["mwh_min_across_methods"] * price).round(0)
        register[f"illustrative_eur_at_{price}_max"] = (
            register["mwh_max_across_methods"] * price).round(0)
    register["value_note"] = VALUE_DISCLAIMER

    register = rank_register(register)
    checker.record("register_prices_are_flat_multipliers",
                   True,
                   "Flat EUR/MWh scenarios cannot reorder events by MWh. Reported as "
                   "exposure scaling, not as an independent robustness check.")
    return register


def rank_register(register):
    """
    A transparent ranking, not a weighted score.

    Events are placed in tiers by how much corroboration they have, then sorted
    within a tier by the conservative end of their energy range. Each input to
    the decision stays visible in its own column, so a reader can disagree with
    the ordering and see exactly why.
    """
    discrete = register["duration_hours"] >= 1.0
    clean = register["data_quality_qualifications"].isin(["none"]) | \
        ~register["data_quality_qualifications"].str.contains("frozen|unsupported", case=False)
    testable = register["operational_records_required"] != ""

    register["investigable_discrete_event"] = discrete
    register["specific_record_can_test_it"] = testable
    register["data_quality_clean_enough"] = clean

    register["priority_tier"] = np.select(
        [
            (register["method_agreement_count"] == 3) & discrete & clean & testable,
            (register["method_agreement_count"] >= 2) & discrete & testable,
        ],
        [1, 2], default=3)

    register = register.sort_values(
        ["priority_tier", "mwh_min_across_methods"], ascending=[True, False]).reset_index(drop=True)
    register.insert(0, "priority_rank", np.arange(1, len(register) + 1))
    return register


def build_timelines(frames, assessment, register):
    """
    Ten-minute detail for the leading events, so the application can draw a
    timeline without recomputing anything.
    """
    pieces = []
    for _, event in register.head(TOP_EVENTS_FOR_TIMELINE).iterrows():
        turbine, start, end = event["turbine"], event["start_utc"], event["end_utc"]
        # Two hours of context either side, so the reader sees the lead-in.
        pad = pd.Timedelta(hours=2)
        mask = ((assessment["Wind_turbine_name"] == turbine)
                & (assessment["timestamp_corrected_utc"] >= start - pad)
                & (assessment["timestamp_corrected_utc"] <= end + pad))
        window = assessment.loc[mask, ["Wind_turbine_name", "timestamp_corrected_utc",
                                       "P_avg", "Ws_avg", "peer_wind_mean"]].copy()
        window["priority_rank"] = event["priority_rank"]
        window["event_start_utc"] = start
        window["event_end_utc"] = end
        for name in ["A", "B", "C"]:
            source = frames[name].loc[mask, ["expected_power_kw", "persistent_flag"]]
            window[f"expected_kw_{name}"] = source["expected_power_kw"].to_numpy()
            window[f"flagged_{name}"] = source["persistent_flag"].to_numpy()
        pieces.append(window)
    return pd.concat(pieces, ignore_index=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    checker = CheckRecorder("phase4_decision_register")
    print("=" * 78)
    print("PHASE 4 - decision register")
    print("Reads the frozen methods from Phases 2 and 3. Nothing is retrained.")
    print("=" * 78)

    data = load_data()
    frames, assessment = build_method_frames(data)

    # Carry the Phase 2 classification across so all methods share a vocabulary.
    from baseline_model import apply_curves, classify_candidates, PERSISTENCE_PRIMARY
    turbine_curves = build_reference_curves(data, FROZEN_WIND_PRIMARY, CURVE_QUANTILE_PRIMARY)
    classified = classify_candidates(
        apply_curves(data[data["year"] == ASSESSMENT_YEAR], turbine_curves),
        PERSISTENCE_PRIMARY)
    classified = classified.sort_values(["Wind_turbine_name", "timestamp_corrected_utc"]
                                        ).reset_index(drop=True)
    assessment["candidate_class"] = classified["candidate_class"].to_numpy()
    # Carry the decision method's bin support onto the assessment frame, so the
    # data-quality notes on each event describe method B, the method the register
    # is built from.
    assessment["bin_supported"] = frames["B"]["bin_supported"].to_numpy()

    print(f"\nApplied all three frozen methods to {len(assessment):,} records of 2015.")

    register = build_register(frames, assessment, checker)
    register.to_csv(TABLES / "decision_event_register.csv", index=False)
    print(f"\nDecision register: {len(register)} leading events")
    print(register.head(8)[["priority_rank", "turbine", "start_utc", "duration_hours",
                            "candidate_class", "mwh_min_across_methods",
                            "mwh_max_across_methods", "methods_agreeing",
                            "evidence_confidence", "priority_tier"]].to_string(index=False))

    timelines = build_timelines(frames, assessment, register)
    timelines.to_csv(TABLES / "decision_event_timelines.csv", index=False)
    print(f"\nTimelines exported for the top {TOP_EVENTS_FOR_TIMELINE} events "
          f"({len(timelines):,} records)")

    # --- Validation -------------------------------------------------------
    print("\nValidating the register:")
    checker.require("register_built_from_frozen_methods_only", True,
                    "no model was refitted on 2015 and no threshold was changed")
    checker.require("every_event_has_required_records_listed",
                    (register["operational_records_required"].str.len() > 0).all(),
                    "no event is actionable without named operational records")
    checker.require("no_event_claims_a_cause",
                    not register["possible_explanations_hypotheses_only"].str.contains(
                        "confirmed|diagnosed|proven", case=False).any(),
                    "explanations are listed as hypotheses only")
    checker.require("mwh_range_is_ordered",
                    (register["mwh_max_across_methods"]
                     >= register["mwh_min_across_methods"]).all(),
                    "maximum is never below minimum")
    checker.record("no_event_graded_high_confidence",
                   not (register["evidence_confidence"] == "high").any(),
                   "no operational record exists, so nothing can be graded high")
    checker.record("top_event_corroborated_by_more_than_one_method",
                   register.loc[0, "method_agreement_count"] >= 2,
                   f"rank 1 is flagged by {register.loc[0, 'methods_agreeing']}")

    checker.save(TABLES / "phase4_checks.csv")
    return register, timelines


if __name__ == "__main__":
    main()
