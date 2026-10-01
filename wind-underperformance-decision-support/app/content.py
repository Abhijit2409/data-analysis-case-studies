"""
Shared labels, colours, caveats and official findings.

Everything the application says more than once lives here, so the wording and the
colours stay consistent across pages and a correction only has to be made once.

The OFFICIAL_FINDINGS values are the analytical results from Phases 2 and 3. The
application's interactive controls explore the evidence; they never overwrite
these.
"""

# --- Colour. One palette, used everywhere. -------------------------------------
# Turbines keep the same colour on every chart so a reader can follow one machine
# across pages without re-reading a legend.
TURBINE_COLOURS = {
    "R80711": "#1f4e79",      # deep blue
    "R80721": "#6a8caf",      # muted blue
    "R80736": "#8c8c8c",      # grey
    "R80790": "#b5651d",      # ochre, the second turbine of interest
}

# Methods also keep fixed colours. B is the decision method and carries the
# strongest colour; C is deliberately muted because it is supporting evidence.
METHOD_COLOURS = {
    "A_turbine_specific": "#9aa7b1",
    "B_pooled_transparent": "#1f4e79",
    "C_pooled_challenger": "#b5651d",
}
METHOD_LABELS = {
    "A_turbine_specific": "A · turbine-specific",
    "B_pooled_transparent": "B · pooled (decision method)",
    "C_pooled_challenger": "C · challenger (experimental)",
}
METHOD_SHORT = {"A_turbine_specific": "A", "B_pooled_transparent": "B",
                "C_pooled_challenger": "C"}

ACCENT = "#1f4e79"
WARN = "#b5651d"
NEUTRAL = "#8c8c8c"
GRID = "#e4e4e4"

# Energy-accounting categories keep their own fixed colours.
ACCOUNTING_COLOURS = {
    "In persistent reviewable events": "#1f4e79",
    "Non-persistent shortfall": "#9aa7b1",
    "Unknown (missing data)": "#c9c9c9",
}


# --- Official findings. Read-only. ---------------------------------------------
OFFICIAL_FINDINGS = {
    "gross_shortfall_mwh": 671.6,
    "events_shortfall_mwh": 380.8,
    "nonpersistent_mwh": 290.8,
    "missing_energy": "unknown",
    "missing_records": 2074,
    "unassessable_records": 2771,
    "primary_method": "B_pooled_transparent",
    "experimental_method": "C_pooled_challenger",
    "pooling_recovery_points": 2.5,
    "model_recovery_points": 4.7,
    "burden_a": 0.379,
    "burden_b": 0.399,
    "burden_c": 0.408,
    "b_c_agreement_pct": 44.7,
    "a_b_agreement_pct": 71.8,
}


# --- Wording used repeatedly ---------------------------------------------------
NOT_RECOVERABLE = (
    "Potential shortfall is not confirmed recoverable energy. It is the gap between "
    "observed output and a statistical reference built from the same machines' own "
    "past. No cause has been established for any of it.")

PRICE_CAVEAT = (
    "Illustrative sensitivity only — not actual revenue. No tariff, PPA or market "
    "price is known for this site. A uniform price is a flat multiplier: it changes "
    "exposure but cannot change the ranking of events by energy.")

ALERTING_CAVEAT = (
    "The challenger passed the registered experimental benchmark, but its "
    "approximately 41% apparent alert burden means it is not ready for automated "
    "operational alerting. Neither is A at 37.9% or B at 39.9%. The pre-registered "
    "acceptance rule constrained only the relative increase in burden against B, not "
    "the absolute level — an incomplete rule, recorded rather than repaired.")

NO_LABELS_CAVEAT = (
    "No method has a real-world precision or recall figure, because the real data "
    "has no labels. Apparent alert burden measures review effort generated, not "
    "error: an untouched window may contain genuine underperformance nobody labelled.")

INDEPENDENCE = (
    "Independent project using public data. No Clir Renewables data, software or "
    "methodology is used, and nothing here describes Clir, its platform, its methods "
    "or its customers.")

ATTRIBUTION = (
    "Data: ENGIE La Haute Borne wind farm, Etalab Open Licence 2.0, obtained via the "
    "OpenOA repository (NatLabRockies/OpenOA). Air-density correction follows "
    "IEC 61400-12-1 as implemented in OpenOA.")

EVIDENCE_HIERARCHY = [
    ("Observation", "Reproducible directly from the supplied data",
     "The 42.5-hour R80711 stop; every energy figure"),
    ("Hypothesis", "A possible cause that predicts something checkable",
     "Every operational explanation in the register"),
    ("Validated finding", "Supported by independent or operational evidence",
     "None. No operational record exists."),
]

SOLAR_TRANSFER = [
    ("Timestamp alignment",
     "Logger clock did not follow daylight saving; summer records sat one hour early",
     "Same problem, plus aligning irradiance and power timestamps and night-time zeros"),
    ("Missing data vs downtime",
     "Gaps clustered in runs up to 132.8 h; never converted to zero",
     "Same rule, harder: inverter dropouts vs genuine outages vs night"),
    ("Sensor quality",
     "Nacelle anemometer least reliable when the rotor is stopped",
     "Plane-of-array irradiance soiling and drift — the reference signal degrades"),
    ("Unit standardisation",
     "Power labelled kWh but behaving as kW; temperature placeholders at absolute zero",
     "Inverter power in W vs kW; irradiance in W/m²; DC vs AC conventions"),
    ("Peer comparison",
     "Pooled fleet reference exposed a gap that self-reference hid",
     "Inverter-to-inverter within the same string configuration and orientation"),
    ("Event taxonomy",
     "No event codes at all, so every category is an assumption",
     "Worse: more inverter makes, string vs inverter granularity, tracker faults"),
    ("Curtailment vs clipping",
     "Curtailment could not be separated from other stops",
     "Clipping is normal design behaviour and must be separated from both"),
    ("Confidence grading",
     "Observation / hypothesis / validated finding; nothing graded high",
     "Identical discipline; matters more where the device population is larger"),
]

SOURCE_PREFIX = "Source:"
