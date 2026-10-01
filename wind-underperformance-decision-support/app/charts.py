"""
Interactive charts.

House rules applied to every chart here:
  - a title that states what is being shown
  - units on every axis
  - hover text that answers the obvious follow-up question
  - fixed turbine and method colours from content.py
  - no decorative styling, no animation, no gradients

Each function returns a Plotly figure. Source notes are added by the page, next
to the chart, so the filename sits with the number.
"""

import pandas as pd
import plotly.graph_objects as go

from content import (ACCENT, ACCOUNTING_COLOURS, GRID, METHOD_COLOURS, METHOD_LABELS,
                     METHOD_SHORT, NEUTRAL, TURBINE_COLOURS, WARN)

FONT = dict(family="Segoe UI, Helvetica, Arial, sans-serif", size=12, color="#1a1a1a")


def _style(figure, title, x_title=None, y_title=None, height=400, legend=True):
    """One place for the shared layout, so every chart looks the same."""
    figure.update_layout(
        title=dict(text=title, font=dict(size=14, color="#1a1a1a")),
        font=FONT,
        height=height,
        # The legend sits on its own row between the title and the plot. Two
        # earlier placements both collided with something: beside the title it hit
        # these long sentence titles, and below the plot it hit the x-axis title.
        margin=dict(l=62, r=24, t=92 if legend else 56, b=58),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
                    font=dict(size=11)),
        hoverlabel=dict(font_size=12),
        title_x=0, title_xanchor="left", title_y=0.985, title_yanchor="top",
    )
    figure.update_xaxes(title_text=x_title, gridcolor=GRID, zeroline=False,
                        showline=True, linecolor="#c9c9c9")
    figure.update_yaxes(title_text=y_title, gridcolor=GRID, zeroline=False,
                        showline=True, linecolor="#c9c9c9")
    return figure


# ---------------------------------------------------------------------------
# Page 1
# ---------------------------------------------------------------------------

def energy_accounting(figures, price):
    """
    Where the 2015 shortfall sits.

    Missing energy is drawn as a hatched bar with no height value, because it is
    unknown rather than zero. Drawing it at zero would say something the data
    does not support.
    """
    events = figures["shortfall_in_persistent_candidate_events_mwh"]
    nonpersistent = figures["nonpersistent_shortfall_mwh"]

    figure = go.Figure()
    figure.add_bar(
        x=["Gross shortfall"], y=[events], name="In persistent reviewable events",
        marker_color=ACCOUNTING_COLOURS["In persistent reviewable events"],
        hovertemplate=(f"In reviewable events<br>%{{y:.1f}} MWh"
                       f"<br>~€{events * price:,.0f} at €{price}/MWh<extra></extra>"))
    figure.add_bar(
        x=["Gross shortfall"], y=[nonpersistent], name="Non-persistent shortfall",
        marker_color=ACCOUNTING_COLOURS["Non-persistent shortfall"],
        hovertemplate=(f"Short dips, below the one-hour rule<br>%{{y:.1f}} MWh"
                       f"<br>~€{nonpersistent * price:,.0f} at €{price}/MWh<extra></extra>"))
    # The unknown column: a marker, not a quantity.
    figure.add_bar(
        x=["Missing data"], y=[events + nonpersistent], name="Unknown (missing data)",
        marker=dict(color="rgba(0,0,0,0)", line=dict(color=NEUTRAL, width=1.4),
                    pattern=dict(shape="/", fgcolor=NEUTRAL, size=6, solidity=0.25)),
        text=["unknown"], textposition="inside", insidetextanchor="middle",
        hovertemplate=("Energy lost during missing data<br><b>unknown, not zero</b>"
                       "<br>2,074 ten-minute records<extra></extra>"))

    figure.update_layout(barmode="stack")
    _style(figure, "2015 energy accounting — potential shortfall, not recoverable energy",
           None, "Potential shortfall (MWh)", height=404)
    figure.add_annotation(x="Gross shortfall", y=events + nonpersistent,
                          text=f"<b>{events + nonpersistent:.1f} MWh</b>",
                          showarrow=False, yshift=14, font=dict(size=13))
    return figure


def turbine_comparison(turbine_table, metric="shortfall_pct_of_potential"):
    """
    Shortfall per turbine under each method.

    The point of the chart is that the apparent priority changes between
    self-reference (A) and fleet-relative comparison (B and C).
    """
    labels = {"shortfall_pct_of_potential": "Gross shortfall (% of potential)",
              "gross_shortfall_mwh": "Gross shortfall (MWh)",
              "produced_mwh": "Produced energy (MWh)",
              "persistent_hours": "Hours in persistent events"}
    figure = go.Figure()
    for method in ["A_turbine_specific", "B_pooled_transparent", "C_pooled_challenger"]:
        subset = turbine_table[turbine_table["method"] == method].sort_values("turbine")
        figure.add_bar(
            x=subset["turbine"], y=subset[metric], name=METHOD_LABELS[method],
            marker_color=METHOD_COLOURS[method],
            customdata=subset[["produced_mwh", "gross_shortfall_mwh", "persistent_events"]],
            hovertemplate=("%{x} · " + METHOD_SHORT[method]
                           + "<br>" + labels[metric] + ": %{y:.2f}"
                           + "<br>Produced: %{customdata[0]:,.0f} MWh"
                           + "<br>Shortfall: %{customdata[1]:,.1f} MWh"
                           + "<br>Events: %{customdata[2]}<extra></extra>"))
    figure.update_layout(barmode="group")
    _style(figure, "Shortfall per turbine — the priority changes with the method",
           None, labels[metric], height=404)
    return figure


def event_scatter(events, price, highlight_rank=None):
    """
    Every event by duration and energy.

    Colour is the turbine, symbol is how many methods agree. Both are carried
    consistently from the rest of the application.
    """
    symbols = {3: "circle", 2: "diamond", 1: "x", 0: "x-thin"}
    figure = go.Figure()
    if len(events) == 0:
        _style(figure, "No events match the current filters",
               "Duration (hours)", "Potential shortfall (MWh)", height=444)
        figure.add_annotation(text="No events match the current filters.<br>"
                                   "Widen a filter to see results.",
                              showarrow=False, font=dict(size=13, color=NEUTRAL))
        return figure

    for turbine, group in events.groupby("turbine"):
        figure.add_trace(go.Scatter(
            x=group["duration_hours"], y=group["mwh_min_across_methods"],
            mode="markers", name=turbine,
            marker=dict(size=13, color=TURBINE_COLOURS.get(turbine, NEUTRAL),
                        symbol=[symbols.get(n, "x") for n in group["method_agreement_count"]],
                        line=dict(width=1, color="white"), opacity=0.9),
            customdata=group[["priority_rank", "start_utc", "candidate_class",
                              "evidence_confidence", "methods_agreeing",
                              "mwh_max_across_methods"]],
            # Illustrative value is precomputed per point rather than built into
            # the template string, which keeps the template readable.
            text=[f"€{v * price:,.0f}" for v in group["mwh_min_across_methods"]],
            hovertemplate=(
                f"<b>{turbine} · rank %{{customdata[0]}}</b>"
                "<br>%{customdata[1]|%d %b %Y %H:%M} UTC"
                "<br>Duration: %{x:.1f} h"
                "<br>Potential: %{y:.1f}–%{customdata[5]:.1f} MWh"
                f"<br>Illustrative at €{price}/MWh: %{{text}}"
                "<br>Class: %{customdata[2]}"
                "<br>Confidence: %{customdata[3]}"
                "<br>Methods agreeing: %{customdata[4]}<extra></extra>")))

    if highlight_rank is not None and (events["priority_rank"] == highlight_rank).any():
        chosen = events[events["priority_rank"] == highlight_rank]
        figure.add_trace(go.Scatter(
            x=chosen["duration_hours"], y=chosen["mwh_min_across_methods"],
            mode="markers", name="Selected", showlegend=False,
            marker=dict(size=26, color="rgba(0,0,0,0)",
                        line=dict(width=2.2, color=ACCENT)),
            hoverinfo="skip"))

    _style(figure, "Events by duration and potential energy "
                   "(circle = all three methods agree, diamond = two, cross = one)",
           "Duration (hours)", "Potential shortfall, conservative end (MWh)", height=444)
    return figure


def event_timeline(detail, event_start, event_end):
    """
    Actual against expected power for one event.

    Gaps in the actual line are records with no value. They are left as gaps on
    purpose: joining across them would imply a measurement that does not exist.
    """
    figure = go.Figure()
    figure.add_trace(go.Scatter(
        x=detail["timestamp_corrected_utc"], y=detail["P_avg"],
        name="Actual power", mode="lines",
        line=dict(color="#1a1a1a", width=2),
        connectgaps=False,
        hovertemplate="%{x|%d %b %H:%M} UTC<br>Actual: %{y:.0f} kW<extra></extra>"))
    for method, dash in [("A", "dot"), ("B", "solid"), ("C", "dash")]:
        column = f"expected_kw_{method}"
        if column not in detail:
            continue
        key = {"A": "A_turbine_specific", "B": "B_pooled_transparent",
               "C": "C_pooled_challenger"}[method]
        figure.add_trace(go.Scatter(
            x=detail["timestamp_corrected_utc"], y=detail[column],
            name=f"Expected · {method}", mode="lines",
            line=dict(color=METHOD_COLOURS[key], width=1.8, dash=dash),
            connectgaps=False,
            hovertemplate=f"%{{x|%d %b %H:%M}} UTC<br>Expected ({method}): "
                          "%{y:.0f} kW<extra></extra>"))

    figure.add_vrect(x0=event_start, x1=event_end, fillcolor=WARN, opacity=0.09,
                     line_width=0, annotation_text="event", annotation_position="top left",
                     annotation_font_size=11)
    _style(figure, "Actual against expected power — gaps are records with no value, not zeros",
           "Time (UTC)", "Power (kW)", height=384)
    return figure


# ---------------------------------------------------------------------------
# Page 3
# ---------------------------------------------------------------------------

def recovery_vs_burden(benchmark, metric="recovery_rate"):
    """Detection against the review effort it generates."""
    summary = benchmark.groupby("method").agg(
        recovery=("recovery_rate", "mean"),
        burden=("apparent_alert_burden", "mean")).reset_index()
    summary["lift"] = summary["recovery"] - summary["burden"]

    figure = go.Figure()
    for _, row in summary.iterrows():
        figure.add_trace(go.Scatter(
            x=[100 * row["burden"]], y=[100 * row["recovery"]],
            mode="markers+text", name=METHOD_LABELS[row["method"]],
            text=[METHOD_SHORT[row["method"]]], textposition="top center",
            textfont=dict(size=13),
            marker=dict(size=20, color=METHOD_COLOURS[row["method"]],
                        line=dict(width=1, color="white")),
            hovertemplate=(METHOD_LABELS[row["method"]]
                           + f"<br>Recovery: {100*row['recovery']:.1f}%"
                           + f"<br>Apparent alert burden: {100*row['burden']:.1f}%"
                           + f"<br>Recovery minus burden: {100*row['lift']:.1f}"
                             " points<extra></extra>")))
    _style(figure, "Detection against review effort — up and to the left is better",
           "Apparent alert burden on untouched windows (%)",
           "Injected windows recovered (%)", height=424)
    return figure


def recovery_heatmap(benchmark, method):
    """Recovery by injected severity and duration, for one method."""
    subset = benchmark[benchmark["method"] == method]
    grid = subset.pivot(index="severity_pct", columns="duration_minutes",
                        values="recovery_rate") * 100
    figure = go.Figure(go.Heatmap(
        z=grid.values, x=[f"{c} min" for c in grid.columns],
        y=[f"{i}%" for i in grid.index],
        colorscale="Blues", zmin=40, zmax=100,
        colorbar=dict(title="Recovered (%)", ticksuffix="%"),
        text=[[f"{v:.1f}%" for v in row] for row in grid.values],
        texttemplate="%{text}", textfont=dict(size=12),
        hovertemplate="Severity %{y}<br>Duration %{x}<br>Recovered "
                      "%{z:.1f}% of injected windows<extra></extra>"))
    _style(figure, f"Synthetic derate recovery — {METHOD_LABELS[method]}",
           "Injected duration", "Injected power reduction", height=320, legend=False)
    return figure


def method_overlap(overlap):
    """How often each pair of methods flags the same ten-minute record."""
    figure = go.Figure()
    labels = overlap["method_pair"].str.replace("_pooled_transparent", "", regex=False) \
        .str.replace("_turbine_specific", "", regex=False) \
        .str.replace("_pooled_challenger", "", regex=False)
    figure.add_bar(x=labels, y=overlap["flagged_by_both"], name="Flagged by both",
                   marker_color=ACCENT,
                   hovertemplate="%{x}<br>Both: %{y:,} records<extra></extra>")
    figure.add_bar(x=labels, y=overlap["flagged_by_first_only"], name="First only",
                   marker_color="#9aa7b1",
                   hovertemplate="%{x}<br>First only: %{y:,} records<extra></extra>")
    figure.add_bar(x=labels, y=overlap["flagged_by_second_only"], name="Second only",
                   marker_color=WARN,
                   hovertemplate="%{x}<br>Second only: %{y:,} records<extra></extra>")
    figure.update_layout(barmode="stack")
    _style(figure, "Do the methods flag the same records? (ten-minute records, 2015)",
           None, "Records flagged", height=384)
    for index, row in overlap.iterrows():
        figure.add_annotation(x=labels.iloc[index],
                              y=row["flagged_by_both"] + row["flagged_by_first_only"]
                              + row["flagged_by_second_only"],
                              text=f"{row['agreement_pct_of_union']:.1f}% agree",
                              showarrow=False, yshift=12, font=dict(size=11))
    return figure


def reference_curve_difference(curves, turbines):
    """
    How far each turbine's own reference sits from the fleet reference.

    This is the chart behind the pooling argument: a turbine whose own curve sits
    below the fleet is judged against a lower bar when compared with itself.
    """
    figure = go.Figure()
    own = curves[(curves["method"] == "A_turbine_specific")
                 & (curves["bin_basis"] == "fitted_median")]
    for turbine in sorted(turbines):
        subset = own[own["series"] == turbine].sort_values("wind_bin")
        subset = subset[subset["own_minus_fleet_kw"].notna()]
        figure.add_trace(go.Scatter(
            x=subset["wind_bin"] + 0.25, y=subset["own_minus_fleet_kw"],
            name=turbine, mode="lines+markers",
            line=dict(color=TURBINE_COLOURS.get(turbine, NEUTRAL), width=2),
            marker=dict(size=6),
            hovertemplate=(f"<b>{turbine}</b><br>Wind: %{{x:.2f}} m/s"
                           "<br>Own curve minus fleet: %{y:+.1f} kW<extra></extra>")))
    figure.add_hline(y=0, line_color="#1a1a1a", line_width=1.2)
    _style(figure, "Own reference minus fleet reference "
                   "(below zero = judged against a lower bar when compared with itself)",
           "Density-corrected wind speed (m/s)", "Difference (kW)", height=424)
    return figure


# ---------------------------------------------------------------------------
# Page 4
# ---------------------------------------------------------------------------

def data_funnel(funnel):
    """Raw records down to what could actually be assessed."""
    figure = go.Figure(go.Funnel(
        y=funnel["stage"], x=funnel["records"],
        textinfo="value+percent initial",
        marker=dict(color=[ACCENT, "#2f6396", "#9aa7b1", "#6a8caf", "#8fa6bd", WARN]),
        hovertemplate="<b>%{y}</b><br>%{x:,} records<br>%{percentInitial} of raw"
                      "<extra></extra>"))
    _style(figure, "From raw records to what could be assessed",
           "Ten-minute records", None, height=380, legend=False)
    return figure


def exclusion_reasons(reconciliation):
    """Why records were excluded from fitting. Reasons overlap."""
    subset = reconciliation[reconciliation["category"] == "excluded_by_reason"] \
        .sort_values("records")
    figure = go.Figure(go.Bar(
        x=subset["records"], y=subset["subcategory"].str.replace("_", " "),
        orientation="h", marker_color=ACCENT,
        hovertemplate="%{y}<br>%{x:,} records<extra></extra>"))
    _style(figure, "Why records were excluded from curve fitting "
                   "(reasons overlap, so they do not sum to the total)",
           "Records", None, height=340, legend=False)
    return figure


def completeness_heatmap(monthly):
    """Data completeness by turbine and month."""
    grid = monthly.pivot(index="Wind_turbine_name", columns="month",
                         values="completeness_pct")
    figure = go.Figure(go.Heatmap(
        z=grid.values, x=grid.columns, y=grid.index,
        colorscale="Blues", zmin=90, zmax=100,
        colorbar=dict(title="Complete (%)", ticksuffix="%"),
        hovertemplate="%{y} · %{x}<br>Power values present: %{z:.2f}%<extra></extra>"))
    _style(figure, "Data completeness by turbine and month (% of records with a power value)",
           "Month (UTC)", None, height=300, legend=False)
    return figure


def missing_runs(runs):
    """Every gap, by length. The point is that gaps cluster."""
    figure = go.Figure()
    for turbine, group in runs.groupby("turbine"):
        figure.add_trace(go.Scatter(
            x=group["start_utc"], y=group["hours"], mode="markers", name=turbine,
            marker=dict(size=9, color=TURBINE_COLOURS.get(turbine, NEUTRAL), opacity=0.85,
                        line=dict(width=0.8, color="white")),
            hovertemplate=(f"<b>{turbine}</b><br>%{{x|%d %b %Y %H:%M}} UTC"
                           "<br>Gap length: %{y:.1f} hours<extra></extra>")))
    _style(figure, "Every run of missing power values — gaps cluster, they are not scattered",
           "Start of gap (UTC)", "Gap length (hours)", height=364)
    longest = runs.iloc[0]
    figure.add_annotation(x=longest["start_utc"], y=longest["hours"],
                          text=f"longest: {longest['hours']:.1f} h on {longest['turbine']}",
                          showarrow=True, arrowhead=0, ax=-70, ay=-26, font=dict(size=11))
    return figure


def timestamp_before_after(lag_table):
    """
    The decisive timestamp test.

    If the logger clock were right, winter and summer would agree. A one-hour
    seasonal difference says the clock moves when it should not.
    """
    figure = go.Figure()
    figure.add_bar(x=["Winter (Nov–Feb)", "Summer (May–Aug)"],
                   y=lag_table["best_lag_hours"], name="Published timestamps",
                   marker_color=WARN, width=0.32, offset=-0.33,
                   hovertemplate="%{x}<br>Best lag: %{y:+d} h<extra></extra>")
    figure.add_bar(x=["Winter (Nov–Feb)", "Summer (May–Aug)"], y=[-1, -1],
                   name="After correction", marker_color=ACCENT, width=0.32, offset=0.01,
                   hovertemplate="%{x}<br>Best lag after correction: %{y:+d} h<extra></extra>")
    _style(figure, "Seasonal alignment against independent ERA5 reanalysis",
           None, "Best lag (hours)", height=354)
    figure.add_annotation(x=0.5, y=-2.45, xref="paper", yref="y",
                          text="Published: winter and summer differ by one hour. "
                               "Corrected: they agree.",
                          showarrow=False, font=dict(size=11, color="#5a5a5a"))
    return figure


def validation_overview(summary):
    """Passes and failures by phase."""
    counts = summary.groupby(["stage", "result"]).size().unstack(fill_value=0)
    if "PASS" not in counts:
        counts["PASS"] = 0
    if "FAIL" not in counts:
        counts["FAIL"] = 0
    figure = go.Figure()
    figure.add_bar(x=counts.index, y=counts["PASS"], name="Passed", marker_color=ACCENT,
                   hovertemplate="%{x}<br>Passed: %{y}<extra></extra>")
    figure.add_bar(x=counts.index, y=counts["FAIL"], name="Failed", marker_color=WARN,
                   hovertemplate="%{x}<br>Failed: %{y}<extra></extra>")
    figure.update_layout(barmode="stack")
    _style(figure, "Validation checks by phase — a check cannot be reported as passed "
                   "unless it ran", None, "Checks", height=320)
    return figure
