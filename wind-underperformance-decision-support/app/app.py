"""
Decision-support application for the La Haute Borne wind performance review.

This application READS the tables the analysis pipeline produced. It does not fit,
train or tune anything at runtime. The interactive controls explore the evidence;
they never overwrite the official pre-registered results, which are fixed in
content.OFFICIAL_FINDINGS.

Run it with the commands in RUN_APP.md.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import assistant
import charts
import content
import data

st.set_page_config(page_title="La Haute Borne performance review", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.9rem; max-width: 1320px;}
  h1 {font-size: 1.6rem; font-weight: 600; margin-bottom: 0.2rem;}
  h2 {font-size: 1.15rem; font-weight: 600; margin-top: 1.1rem;}
  h3 {font-size: 1rem; font-weight: 600;}
  .caveat {border-left: 3px solid #b5651d; padding: 0.5rem 0.85rem;
           background: rgba(181,101,29,0.06); margin: 0.5rem 0; font-size: 0.9rem;}
  .src {color: #6b6b6b; font-size: 0.78rem; margin: -0.5rem 0 0.9rem 0;}
  [data-testid="stMetricValue"] {font-size: 1.25rem;}
  [data-testid="stMetricLabel"] {font-size: 0.78rem;}
  .stPlotlyChart {border: 1px solid #ececec; border-radius: 3px;
                  padding: 2px; overflow: hidden;}
</style>
""", unsafe_allow_html=True)

PLOTLY = {"displayModeBar": False, "responsive": True}


def caveat(text):
    """A bordered note. Streamlit does not parse markdown inside raw HTML, so
    emphasis markers are converted first or they appear as literal asterisks."""
    for mark, tag in (("**", "strong"), ("*", "em")):
        parts = text.split(mark)
        text = "".join(f"<{tag}>{p}</{tag}>" if i % 2 else p for i, p in enumerate(parts))
    st.markdown(f"<div class='caveat'>{text}</div>", unsafe_allow_html=True)


def source(*files):
    st.markdown(f"<div class='src'>{content.SOURCE_PREFIX} {', '.join(files)}</div>",
                unsafe_allow_html=True)


PAGES = ["Executive cockpit", "Investigation explorer", "Method and scenario lab",
         "Data trust", "Ask the analysis"]

st.sidebar.markdown("### Performance review")
st.sidebar.caption("La Haute Borne wind farm · 2015 assessment year")
page = st.sidebar.radio("Section", PAGES, label_visibility="collapsed",
                        key="nav")
st.sidebar.divider()

with st.sidebar.expander("About this analysis"):
    st.caption(content.INDEPENDENCE)
    st.caption(content.ATTRIBUTION)
    st.markdown("**Evidence hierarchy**")
    for level, test, where in content.EVIDENCE_HIERARCHY:
        st.caption(f"**{level}** — {test}. _{where}_")
    st.markdown("**Primary method**")
    st.caption("B, the pooled transparent curve. A is shown alongside so the effect "
               "of self-reference stays visible. C is experimental supporting "
               "evidence, never the decision method.")

with st.sidebar.expander("Limitations"):
    st.caption(
        "- No event codes, work orders or curtailment records exist\n"
        "- No independent meter validation; the supplied meter is synthetic\n"
        "- Four turbines only; a site-wide problem stays invisible\n"
        "- 2015 data; nothing describes the site today\n"
        "- The synthetic benchmark is an upper bound on real detection\n"
        "- No finding reaches 'validated finding' on the project's own hierarchy")

with st.sidebar.expander("Transfer to solar"):
    st.caption("A transfer of analytical discipline, not a claim of solar expertise.")
    st.dataframe(pd.DataFrame(content.SOLAR_TRANSFER,
                              columns=["Check", "Here", "Solar equivalent"]),
                 hide_index=True, width="stretch")


# ===========================================================================
# Page 1 — Executive cockpit
# ===========================================================================
if page == PAGES[0]:
    register = data.register()
    figures = data.accounting()
    turbine_table = data.table("phase3_turbine_comparison.csv")
    timelines = data.timelines()

    st.title("Which issue should be investigated first?")

    controls = st.columns([1.5, 1.3, 1.2, 1.4])
    price = controls[0].slider("Electricity value (€/MWh)", 30, 150, 80, 5,
                               help="Illustrative only. A uniform price is a flat "
                                    "multiplier: it scales exposure but cannot change "
                                    "the ranking of events by energy.")
    method_choice = controls[1].selectbox(
        "Method view", list(content.METHOD_LABELS),
        index=1, format_func=lambda m: content.METHOD_LABELS[m],
        help="B is the decision method. A and C are shown for comparison only.")
    turbine_filter = controls[2].multiselect(
        "Turbines", sorted(register["turbine"].unique()),
        default=sorted(register["turbine"].unique()))
    basis = controls[3].radio("Energy basis",
                              ["Persistent reviewable events", "Gross residual shortfall"],
                              help="Gross includes short dips that fail the one-hour "
                                   "persistence rule.")

    shown = register[register["turbine"].isin(turbine_filter)] if turbine_filter else register
    top = register.iloc[0]

    st.markdown("### Recommendation")
    # The metrics sit in their own full-width row rather than nested in a narrow
    # column: at smaller window widths a nested metric truncates its own label.
    metric_row = st.columns([1.15, 0.85, 1.0, 1.4])
    with st.container():
        st.markdown(
            f"**Turbine {top['turbine']} · "
            f"{top['start_utc']:%d %B %Y %H:%M} to {top['end_utc']:%d %B %H:%M} UTC "
            f"· {top['duration_hours']:.1f} hours**")
        st.markdown(
            "Produced almost nothing for 42 hours while all three neighbouring "
            "turbines produced normally in the same wind. It had been operating in "
            "line with expectation for the preceding two days.")
        st.markdown(f"**Next operational record required** — {top['operational_records_required']}")
    if True:
        a, b = metric_row[0], metric_row[1]
        c_col, d_col = metric_row[2], metric_row[3]
        a.metric("Potential MWh",
                 f"{top['mwh_min_across_methods']:.1f}–{top['mwh_max_across_methods']:.1f}",
                 help="Potential shortfall range across the applicable methods. "
                      "Not confirmed recoverable energy.")
        b.metric("Methods", top["methods_agreeing"],
                 help="Which of the three methods flag this interval.")
        c_col.metric("Confidence", top["evidence_confidence"],
                 help="Medium is the ceiling: no operational record exists.")
        d_col.metric(f"At €{price}/MWh",
                 f"€{data.value_at_price(top['mwh_min_across_methods'], price):,.0f}"
                 f"–{data.value_at_price(top['mwh_max_across_methods'], price):,.0f}",
                 help="Illustrative sensitivity only, not actual revenue.")

    caveat(f"**{content.NOT_RECOVERABLE}**")

    st.markdown("### 2015 energy accounting")
    columns = st.columns(4)
    columns[0].metric("Gross shortfall",
                      f"{figures['gross_positive_residual_shortfall_mwh']:.1f} MWh",
                      help="Total gap against a statistical reference.")
    columns[1].metric("In reviewable events",
                      f"{figures['shortfall_in_persistent_candidate_events_mwh']:.1f} MWh",
                      help="The part that forms reviewable events.")
    columns[2].metric("Non-persistent",
                      f"{figures['nonpersistent_shortfall_mwh']:.1f} MWh",
                      help="Short dips failing the one-hour rule.")
    columns[3].metric("Missing energy", "unknown",
                      help=f"{content.OFFICIAL_FINDINGS['missing_records']:,} records "
                           "with no power or wind value. Unknown, not zero.")

    headline = (figures["shortfall_in_persistent_candidate_events_mwh"]
                if basis.startswith("Persistent")
                else figures["gross_positive_residual_shortfall_mwh"])
    st.caption(f"At €{price}/MWh, {basis.lower()} of {headline:.1f} MWh is an "
               f"illustrative **€{headline * price:,.0f}**. {content.PRICE_CAVEAT}")

    one, two = st.columns(2)
    with one:
        st.plotly_chart(charts.energy_accounting(figures, price),
                        width="stretch", config=PLOTLY)
        source("energy_accounting.csv")
    with two:
        metric = ("shortfall_pct_of_potential" if basis.startswith("Persistent")
                  else "gross_shortfall_mwh")
        st.plotly_chart(charts.turbine_comparison(turbine_table, metric),
                        width="stretch", config=PLOTLY)
        source("phase3_turbine_comparison.csv")
        st.caption("Method A judges R80711 against a bar 11–19 kW below its "
                   "neighbours. Pooling moves it from apparently best-behaved to "
                   "largest shortfall — the apparent priority depends on the method.")

    st.markdown("### Leading events")
    st.plotly_chart(charts.event_scatter(shown, price, highlight_rank=top["priority_rank"]),
                    width="stretch", config=PLOTLY)
    source("decision_event_register.csv")

    detail = timelines[timelines["priority_rank"] == top["priority_rank"]]
    if len(detail):
        st.plotly_chart(
            charts.event_timeline(detail, top["start_utc"], top["end_utc"]),
            width="stretch", config=PLOTLY)
        source("decision_event_timelines.csv")

    with st.expander("How this was calculated"):
        st.markdown(
            "Expected power comes from a binned-median reference curve fitted on "
            "2014 records that passed the data-quality rules, then frozen and "
            "applied to 2015. Potential shortfall is "
            "`max(expected − max(actual, 0), 0) × (10/60)` per ten-minute record. "
            "Events are runs of at least six consecutive shortfall records (one "
            "hour). Ranking is a transparent tier — corroboration first, then the "
            "conservative end of the energy range — with every input visible as a "
            "column in the register. No event is graded high confidence, because "
            "no operational record exists for any interval.\n\n"
            f"Selected method view: **{content.METHOD_LABELS[method_choice]}**. "
            "The official figures above are method B and do not change with this "
            "control.")
        source("decision_event_register.csv", "energy_accounting.csv",
               "phase3_turbine_comparison.csv")


# ===========================================================================
# Page 2 — Investigation explorer
# ===========================================================================
elif page == PAGES[1]:
    register = data.register()
    timelines = data.timelines()

    st.title("Investigation explorer")

    with st.expander("Filters", expanded=True):
        one, two, three = st.columns(3)
        turbines = one.multiselect("Turbine", sorted(register["turbine"].unique()),
                                   default=sorted(register["turbine"].unique()))
        classes = two.multiselect("Classification",
                                  sorted(register["candidate_class"].unique()),
                                  default=sorted(register["candidate_class"].unique()))
        confidences = three.multiselect("Confidence",
                                        sorted(register["evidence_confidence"].unique()),
                                        default=sorted(register["evidence_confidence"].unique()))
        four, five, six = st.columns(3)
        agreements = four.multiselect("Methods agreeing",
                                      sorted(register["methods_agreeing"].unique()),
                                      default=sorted(register["methods_agreeing"].unique()))
        min_hours = five.slider("Minimum duration (hours)", 0.0,
                                float(register["duration_hours"].max()), 0.0, 0.5)
        min_mwh = six.slider("Minimum potential (MWh)", 0.0,
                             float(register["mwh_min_across_methods"].max()), 0.0, 0.5)
        seven, eight = st.columns([2, 1])
        earliest = register["start_date"].min()
        latest = register["start_date"].max()
        date_range = seven.date_input("Event start date range", (earliest, latest),
                                      min_value=earliest, max_value=latest)
        price = eight.slider("Electricity value (€/MWh)", 30, 150, 80, 5, key="explorer_price")

    chosen_range = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else None
    filtered = data.filter_register(register, turbines, classes, confidences,
                                    agreements, min_hours, min_mwh, chosen_range)

    one, two = st.columns([3, 2])
    with one:
        st.plotly_chart(charts.event_scatter(filtered, price),
                        width="stretch", config=PLOTLY)
    with two:
        if len(filtered):
            grid = (filtered.pivot_table(index="turbine", columns="month",
                                         values="mwh_min_across_methods", aggfunc="sum")
                    .fillna(0))
            import plotly.graph_objects as go
            heat = go.Figure(go.Heatmap(
                z=grid.values, x=grid.columns, y=grid.index, colorscale="Blues",
                colorbar=dict(title="MWh"),
                hovertemplate="%{y} · %{x}<br>%{z:.1f} MWh in events<extra></extra>"))
            heat.update_layout(title=dict(text="Event energy by turbine and month (MWh)",
                                          font=dict(size=14)),
                               height=420, margin=dict(l=70, r=24, t=52, b=52),
                               plot_bgcolor="white", paper_bgcolor="white",
                               font=charts.FONT)
            st.plotly_chart(heat, width="stretch", config=PLOTLY)
        else:
            st.info("No events match the current filters.")
    source("decision_event_register.csv")

    empty_filters = [name for name, values in
                     [("turbine", turbines), ("classification", classes),
                      ("confidence", confidences), ("methods agreeing", agreements)]
                     if not values]
    note = (f" An empty selection counts as no filter, so {', '.join(empty_filters)} "
            "is not narrowing the list." if empty_filters else "")
    st.caption(f"{len(filtered)} of {len(register)} events shown.{note}")

    if len(filtered) == 0:
        st.warning("No events match the current filters. Widen a filter to continue.")
    else:
        display = filtered[["priority_rank", "priority_tier", "turbine", "start_utc",
                            "duration_hours", "candidate_class",
                            "mwh_min_across_methods", "mwh_max_across_methods",
                            "methods_agreeing", "evidence_confidence"]].copy()
        display[f"illustrative_eur_at_{price}"] = (
            display["mwh_min_across_methods"] * price).round(0)
        st.dataframe(display, hide_index=True, width="stretch", height=260)

        st.markdown("## Event detail")
        chosen = st.selectbox(
            "Event", filtered["priority_rank"].tolist(),
            format_func=lambda r: (
                f"#{r} · {register.loc[register.priority_rank == r, 'turbine'].iloc[0]}"
                f" · {register.loc[register.priority_rank == r, 'start_utc'].iloc[0]:%d %b %Y %H:%M}"
                f" · {register.loc[register.priority_rank == r, 'mwh_min_across_methods'].iloc[0]:.1f} MWh"))
        event = register[register["priority_rank"] == chosen].iloc[0]

        detail = timelines[timelines["priority_rank"] == chosen]
        if len(detail):
            st.plotly_chart(charts.event_timeline(detail, event["start_utc"],
                                                  event["end_utc"]),
                            width="stretch", config=PLOTLY)
            source("decision_event_timelines.csv")
        else:
            st.info("Ten-minute detail is exported for the eight leading events only. "
                    "The register row below still applies.")

        metrics = st.columns(5)
        metrics[0].metric("Potential",
                          f"{event['mwh_min_across_methods']:.1f}–"
                          f"{event['mwh_max_across_methods']:.1f} MWh")
        metrics[1].metric("Duration", f"{event['duration_hours']:.1f} h")
        metrics[2].metric("Confidence", event["evidence_confidence"])
        metrics[3].metric("Methods", event["methods_agreeing"])
        metrics[4].metric(f"At €{price}/MWh",
                          f"€{event['mwh_min_across_methods'] * price:,.0f}–"
                          f"{event['mwh_max_across_methods'] * price:,.0f}")
        st.caption(content.PRICE_CAVEAT)

        left, right = st.columns(2)
        with left:
            st.markdown("**Observed facts**")
            st.markdown(
                f"- Wind at the turbine: {event['mean_wind_ms']:.1f} m/s\n"
                f"- Wind at neighbouring turbines: {event['mean_peer_wind_ms']:.1f} m/s\n"
                f"- Shortfall by method — A {event['shortfall_mwh_method_a']:.2f}, "
                f"B {event['shortfall_mwh_method_b']:.2f}, "
                f"C {event['shortfall_mwh_method_c']:.2f} MWh\n"
                f"- Data-quality notes: {event['data_quality_qualifications']}")
            st.markdown("**Possible explanations — hypotheses, none confirmed**")
            for item in str(event["possible_explanations_hypotheses_only"]).split(" | "):
                st.markdown(f"- {item}")
        with right:
            st.markdown("**Operational records required**")
            st.markdown(event["operational_records_required"])
            st.markdown("**Recommended next action**")
            st.markdown(event["recommended_next_action"])
            st.markdown("**Escalate if**")
            st.markdown("Event codes show an unplanned fault stop with no corresponding "
                        "work order, or there is no record of the outage at all.")
            st.markdown("**Close if**")
            st.markdown("Records show a planned service visit or a documented grid "
                        "instruction covering the interval.")
        caveat("No cause is shown for any event. Nothing in this dataset distinguishes "
               "a fault from maintenance, curtailment, a grid instruction or a "
               "communications failure.")


# ===========================================================================
# Page 3 — Method and scenario lab
# ===========================================================================
elif page == PAGES[2]:
    benchmark = data.table("phase3_synthetic_injection.csv")
    overlap = data.table("phase3_event_overlap.csv")
    turbine_table = data.table("phase3_turbine_comparison.csv")
    curves = data.table("presentation_reference_curves.csv")

    st.title("Method and scenario lab")
    st.caption("Exploratory controls. They change what is displayed; they never "
               "overwrite the official pre-registered results.")

    controls = st.columns(4)
    turbines = controls[0].multiselect("Turbines",
                                       sorted(turbine_table["turbine"].unique()),
                                       default=sorted(turbine_table["turbine"].unique()))
    method = controls[1].selectbox("Method for the recovery heatmap",
                                   list(content.METHOD_LABELS), index=2,
                                   format_func=lambda m: content.METHOD_LABELS[m])
    severity = controls[2].multiselect("Injected severity (%)",
                                       sorted(benchmark["severity_pct"].unique()),
                                       default=sorted(benchmark["severity_pct"].unique()))
    duration = controls[3].multiselect("Injected duration (minutes)",
                                       sorted(benchmark["duration_minutes"].unique()),
                                       default=sorted(benchmark["duration_minutes"].unique()))

    scoped = benchmark[benchmark["severity_pct"].isin(severity)
                       & benchmark["duration_minutes"].isin(duration)]

    summary = st.columns(4)
    summary[0].metric("Pooling contributed",
                      f"+{content.OFFICIAL_FINDINGS['pooling_recovery_points']} pts",
                      help="A → B, injected-event recovery.")
    summary[1].metric("Model flexibility contributed",
                      f"+{content.OFFICIAL_FINDINGS['model_recovery_points']} pts",
                      help="B → C, injected-event recovery.")
    summary[2].metric("C agrees with B on",
                      f"{content.OFFICIAL_FINDINGS['b_c_agreement_pct']}%",
                      help="Of flagged ten-minute records. A and B agree on 71.8%.")
    summary[3].metric("Alert burden A / B / C",
                      f"{100*content.OFFICIAL_FINDINGS['burden_a']:.0f} / "
                      f"{100*content.OFFICIAL_FINDINGS['burden_b']:.0f} / "
                      f"{100*content.OFFICIAL_FINDINGS['burden_c']:.0f}%",
                      help="Share of untouched control windows that trigger an alert. "
                           "Not a false-positive rate.")

    caveat(f"**{content.ALERTING_CAVEAT}**")

    one, two = st.columns(2)
    with one:
        scoped_turbines = turbine_table[turbine_table["turbine"].isin(turbines)] \
            if turbines else turbine_table
        st.plotly_chart(charts.turbine_comparison(scoped_turbines),
                        width="stretch", config=PLOTLY)
        source("phase3_turbine_comparison.csv")
    with two:
        if len(scoped):
            st.plotly_chart(charts.recovery_vs_burden(scoped),
                            width="stretch", config=PLOTLY)
            source("phase3_synthetic_injection.csv")
        else:
            st.info("Select at least one severity and one duration.")

    one, two = st.columns(2)
    with one:
        if len(scoped):
            st.plotly_chart(charts.recovery_heatmap(benchmark, method),
                            width="stretch", config=PLOTLY)
            source("phase3_synthetic_injection.csv")
    with two:
        st.plotly_chart(charts.method_overlap(overlap),
                        width="stretch", config=PLOTLY)
        source("phase3_event_overlap.csv")

    st.plotly_chart(charts.reference_curve_difference(curves, turbines or
                                                      sorted(turbine_table["turbine"].unique())),
                    width="stretch", config=PLOTLY)
    source("presentation_reference_curves.csv")

    caveat(content.NO_LABELS_CAVEAT)

    with st.expander("The failed leakage check, and the post-hoc diagnostic"):
        st.markdown(
            "One pre-registered check **failed**: the wind-direction feature is "
            "partly state-dependent, with a largest sector difference of 0.082 "
            "against a 0.05 limit. Direction here is derived from nacelle position "
            "and vane angle, both of which reflect the turbine's own control state.\n\n"
            "**A post-hoc diagnostic — explicitly not part of the pre-registered "
            "comparison —** refitted the model without the feature: recovery 0.8167 "
            "against 0.8183 with it, still above B's 0.7713. The conclusion does not "
            "rest on the suspect feature. The failure stays on the record.")
        source("phase3_checks.csv", "phase3_posthoc_no_direction.csv")

    with st.expander("How the synthetic benchmark works"):
        st.markdown(
            "Real 2015 data has no verified labels, so detection capability cannot "
            "be measured on it. Known power reductions of 5%, 10% and 20% lasting "
            "30, 60 and 120 minutes were injected into clean 2015 windows, leaving "
            "every input feature untouched, so no method can see the injection in "
            "its inputs. Each injected window has an untouched control drawn the "
            "same way. A window counts as recovered when at least three consecutive "
            "records inside it are flagged. The rule and the acceptance criterion "
            "were fixed and committed before any model was trained.")
        source("phase3_method.md", "phase3_synthetic_injection.csv")


# ===========================================================================
# Page 4 — Data trust
# ===========================================================================
elif page == PAGES[3]:
    st.title("Data trust")
    st.caption("What had to be established before any performance number meant anything.")

    funnel = data.table("presentation_data_funnel.csv")
    reconciliation = data.table("cleaning_reconciliation.csv")
    monthly = data.table("presentation_monthly_completeness.csv")
    runs = data.table("presentation_missing_runs.csv", parse_dates=["start_utc", "end_utc"])
    lag = data.table("timestamp_alignment_test.csv")
    validation = data.validation_summary()

    columns = st.columns(4)
    columns[0].metric("Raw records", "420,480")
    columns[1].metric("Reference-eligible", "336,928", "80.13%", delta_color="off")
    columns[2].metric("Longest data gap", f"{runs['hours'].max():.1f} h",
                      help="On R80721. Filling it with zero would invent five days "
                           "of false outage.")
    columns[3].metric("Validation checks",
                      f"{int((validation['result'] == 'PASS').sum())} / {len(validation)}",
                      help="The single failure is the wind-direction leakage check, "
                           "which fired as designed.")

    one, two = st.columns(2)
    with one:
        st.plotly_chart(charts.data_funnel(funnel), width="stretch", config=PLOTLY)
        source("presentation_data_funnel.csv")
    with two:
        st.plotly_chart(charts.exclusion_reasons(reconciliation),
                        width="stretch", config=PLOTLY)
        source("cleaning_reconciliation.csv")
        st.caption("The largest exclusion is zero-or-negative power. That is "
                   "deliberate: those records are excluded from *fitting* the curve "
                   "and kept in full as investigation candidates.")

    one, two = st.columns([1.3, 1])
    with one:
        st.plotly_chart(charts.completeness_heatmap(monthly),
                        width="stretch", config=PLOTLY)
        source("presentation_monthly_completeness.csv")
    with two:
        st.plotly_chart(charts.timestamp_before_after(lag),
                        width="stretch", config=PLOTLY)
        source("timestamp_alignment_test.csv")

    st.plotly_chart(charts.missing_runs(runs), width="stretch", config=PLOTLY)
    source("presentation_missing_runs.csv")

    st.plotly_chart(charts.validation_overview(validation),
                    width="stretch", config=PLOTLY)
    source("presentation_validation_summary.csv")

    notes = st.columns(2)
    with notes[0]:
        with st.expander("Why the summer timestamps were an hour early"):
            st.markdown(
                "The published timestamps carry proper `+01:00` and `+02:00` offsets, "
                "which makes them look reliable. Every local day held exactly 144 "
                "ten-minute records, **including both clock-change days** — which a "
                "daylight-saving-aware logger cannot produce.\n\n"
                "Two independent tests showed the logger's clock never moved and the "
                "summer offset was applied afterwards, putting every summer record "
                "one hour early for about seven months a year. Correcting it removed "
                "all 48 duplicate and all 48 absent intervals and closed the seasonal "
                "gap against ERA5. It affects any join to another time series, "
                "including air density. It does not affect the power curve, because "
                "wind and power share a row.")
            source("phase_2_findings.md", "timestamp_correction_validation.csv")
        with st.expander("Why missing data cannot become zero production"):
            st.markdown(
                f"2,569 power values are absent, clustered in {len(runs)} runs. The "
                f"longest is {runs['hours'].max():.1f} hours, and 388 gaps are moments "
                "when no turbine reported at all, which points at the data link rather "
                "than the machines.\n\n"
                "A record showing 0 kW is an observation: the turbine was there and "
                "produced nothing. A record with no value is an absence of evidence. "
                "Filling the second with zero would manufacture days of false outage.")
            source("presentation_missing_runs.csv", "phase_1_findings.md")
    with notes[1]:
        with st.expander("Why the synthetic meter could not validate SCADA"):
            st.markdown(
                "The OpenOA loader states in its own source that the meter series was "
                "generated by adding artificial electrical loss and uncertainty to "
                "SCADA data. Measured directly: the meter-to-turbine ratio averages "
                "0.980 with a standard deviation of 0.008, and the two correlate at "
                "0.9997 — a fixed loss factor with noise, not an independent "
                "measurement.\n\n"
                "**This removes the one external cross-check that would normally "
                "exist.** Every check in this project is internal, and that is stated "
                "wherever a number is presented.")
            source("phase_2_findings.md", "data/README.md")
        with st.expander("Why the 2014 / 2015 resource difference matters"):
            st.markdown(
                "The reference curve is fitted on 2014 and applied to 2015, but the "
                "years are not closely comparable: ERA5 mean wind is 4.53% higher in "
                "2015 and **mean cubed wind 13.3% higher**, ranging from −4.2% to "
                "+15.3% by quarter.\n\n"
                "This does not invalidate the split, because the curve is conditioned "
                "on wind speed. It does mean raw annual energy must never be compared "
                "between years and called performance. The residual risk is that 2015 "
                "leans harder on the thin high-wind end of the 2014 curve.")
            source("annual_resource_comparison.csv", "phase_2_findings.md")


# ===========================================================================
# Page 5 — Ask the analysis
# ===========================================================================
else:
    st.title("Ask this analysis")
    st.caption("Answers are generated from the project evidence pack. The cited "
               "source files remain authoritative.")

    documents = data.evidence_documents()
    tables = data.evidence_tables()
    chunks = assistant.build_evidence_pack(documents, tables)

    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "asked" not in st.session_state:
        st.session_state.asked = 0

    key_present = assistant.api_key_available()
    if key_present:
        st.caption(f"Model: `{assistant.configured_model()}` · "
                   f"{assistant.MAX_QUESTIONS_PER_SESSION - st.session_state.asked} "
                   "questions left this session · API use may incur charges.")
    else:
        st.warning("AI assistant unavailable until a server-side API key is "
                   "configured. The suggested questions below still work: they return "
                   "the matching passages from the project's own files.")
        with st.expander("How to enable written answers", expanded=False):
            st.markdown(
                "You need an OpenAI API key. The rest of the application does not, "
                "and nothing else changes if you skip this.\n\n"
                "**1.** Create a key at `platform.openai.com` → API keys, and add "
                "billing to that account. **API use is charged to it.**\n\n"
                "**2.** Give the key to the app, by either route:")
            st.code("# Option A - environment variable, this terminal session only\n"
                    "set OPENAI_API_KEY=sk-...your-key...\n"
                    "\n"
                    "# then start the app from the project root\n"
                    ".venv\\Scripts\\python.exe -m streamlit run app/app.py",
                    language="bat")
            st.markdown("**Option B — a secrets file**, which persists between runs. "
                        "Create `.streamlit/secrets.toml` next to this project's "
                        "`.streamlit/secrets.toml.example`:")
            st.code('OPENAI_API_KEY = "sk-...your-key..."\n'
                    '# Optional. Defaults to gpt-6-luna.\n'
                    '# OPENAI_MODEL = "gpt-6-luna"', language="toml")
            st.markdown(
                f"**3.** Restart the app. This page will then show written answers "
                f"grounded in the same passages, capped at "
                f"{assistant.MAX_QUESTIONS_PER_SESSION} questions per session.\n\n"
                "`.streamlit/secrets.toml` is git-ignored — **never commit a real "
                "key.** On Streamlit Community Cloud, use Settings → Secrets instead "
                "of a file. Full detail is in `RUN_APP.md`.")

    st.markdown("**Suggested questions**")
    chosen_question = None
    for row_start in range(0, len(assistant.SUGGESTED_QUESTIONS), 2):
        for column, question in zip(
                st.columns(2), assistant.SUGGESTED_QUESTIONS[row_start:row_start + 2]):
            if column.button(question, key=f"suggest_{question}",
                             width="stretch"):
                chosen_question = question

    typed = st.chat_input("Ask about the data, methods, events or limitations")
    question = typed or chosen_question

    for earlier_question, earlier_answer in st.session_state.chat:
        with st.chat_message("user"):
            st.markdown(earlier_question)
        with st.chat_message("assistant"):
            st.markdown(earlier_answer)

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        selected = assistant.retrieve(question, chunks)

        with st.chat_message("assistant"):
            if not selected:
                answer = ("The project does not contain enough evidence to answer "
                          "that. Try one of the suggested questions, or ask about the "
                          "dataset, the timestamp correction, the methods, the "
                          "candidate events or the limitations.")
                st.markdown(answer)
                st.session_state.chat.append((question, answer))
            elif not key_present:
                st.markdown("**Retrieved passages** — this is project text, not an "
                            "AI-generated answer.")
                for score, chunk in selected[:4]:
                    with st.expander(f"[{chunk.source}]"
                                     + (f" — {chunk.heading}" if chunk.heading else "")):
                        st.markdown(chunk.text)
                st.caption("Configure an API key to get a written answer grounded in "
                           "these passages.")
            elif st.session_state.asked >= assistant.MAX_QUESTIONS_PER_SESSION:
                st.info(f"Session limit of {assistant.MAX_QUESTIONS_PER_SESSION} "
                        "questions reached. Reload the page to start a new session. "
                        "The limit exists to avoid unintended API cost.")
            else:
                with st.spinner("Reading the evidence pack..."):
                    answer, error = assistant.ask_model(
                        question, assistant.format_evidence(selected),
                        st.session_state.chat)
                if error:
                    st.error(error)
                else:
                    st.session_state.asked += 1
                    st.markdown(answer)
                    st.session_state.chat.append((question, answer))
                    with st.expander("Evidence used"):
                        for score, chunk in selected:
                            st.caption(f"**[{chunk.source}]**"
                                       + (f" — {chunk.heading}" if chunk.heading else "")
                                       + f" · term overlap {score:.1f}")

    with st.expander("What the assistant can and cannot do"):
        st.markdown(
            "**Retrieval is local and transparent.** The project's documents and "
            "small tables are split into chunks, and chunks are scored by how many "
            "of the question's terms they contain. No embeddings: the evidence pack "
            "is small, term overlap works, and a reader can check why a passage was "
            "selected. Only the selected passages are sent to the model — **the raw "
            "dataset is never sent anywhere.**\n\n"
            "**It will not** diagnose a fault, claim recoverable energy or revenue, "
            "invent event codes or work orders, make claims about Clir's platform or "
            "customers, present a hypothesis as an observation, treat synthetic "
            "benchmark results as real-world accuracy, browse the web, or change any "
            "data.\n\n"
            "Files it retrieves from: `README.md`, `docs/phase_1_findings.md`, "
            "`docs/phase_2_findings.md`, `docs/phase_3_method.md`, "
            "`docs/phase_3_findings.md`, `docs/phase_4_findings.md`, "
            "`docs/methodology_decisions.md`, `docs/executive_memo.md`, and the CSVs "
            "in `outputs/tables/`.")
