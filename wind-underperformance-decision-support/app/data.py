"""
Cached loading of the tables the pipeline produced.

Every function here reads a CSV that already exists on disk. **Nothing in this
module fits, trains, tunes or recalculates an analytical result.** Where a value
is derived (an illustrative price multiplied by an energy figure, for example),
it is a presentation transformation of a number the pipeline already wrote.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"
DOCS = PROJECT_ROOT / "docs"


@st.cache_data(show_spinner=False)
def table(name, **kwargs):
    """Read one generated table. Cached so switching pages does not re-read disk."""
    return pd.read_csv(TABLES / name, **kwargs)


def available(name):
    return (TABLES / name).exists()


# --- Core tables ---------------------------------------------------------------

@st.cache_data(show_spinner=False)
def register():
    """The decision event register, with timestamps parsed."""
    frame = pd.read_csv(TABLES / "decision_event_register.csv",
                        parse_dates=["start_utc", "end_utc"])
    frame["start_date"] = frame["start_utc"].dt.date
    frame["month"] = frame["start_utc"].dt.tz_localize(None).dt.to_period("M").astype(str)
    return frame


@st.cache_data(show_spinner=False)
def timelines():
    return pd.read_csv(TABLES / "decision_event_timelines.csv",
                       parse_dates=["timestamp_corrected_utc", "event_start_utc",
                                    "event_end_utc"])


@st.cache_data(show_spinner=False)
def accounting():
    """Energy accounting as a plain dictionary."""
    frame = pd.read_csv(TABLES / "energy_accounting.csv")
    return {row["quantity"]: row["value"] for _, row in frame.iterrows()}


@st.cache_data(show_spinner=False)
def validation_summary():
    if available("presentation_validation_summary.csv"):
        return pd.read_csv(TABLES / "presentation_validation_summary.csv")
    return pd.DataFrame(columns=["stage", "check", "result", "detail", "source_file"])


# --- Presentation helpers ------------------------------------------------------

def value_at_price(energy_mwh, price_eur_per_mwh):
    """
    Illustrative exposure at a chosen price.

    A flat multiplier. It scales every event by the same factor, so it can change
    the size of the number but never the order of the events.
    """
    return energy_mwh * price_eur_per_mwh


def filter_register(frame, turbines=None, classes=None, confidences=None,
                    agreements=None, min_hours=0.0, min_mwh=0.0, date_range=None):
    """Apply the explorer filters. Returns an empty frame rather than failing."""
    result = frame
    if turbines:
        result = result[result["turbine"].isin(turbines)]
    if classes:
        result = result[result["candidate_class"].isin(classes)]
    if confidences:
        result = result[result["evidence_confidence"].isin(confidences)]
    if agreements:
        result = result[result["methods_agreeing"].isin(agreements)]
    if min_hours:
        result = result[result["duration_hours"] >= min_hours]
    if min_mwh:
        result = result[result["mwh_min_across_methods"] >= min_mwh]
    if date_range and len(date_range) == 2:
        start, end = date_range
        result = result[(result["start_date"] >= start) & (result["start_date"] <= end)]
    return result


@st.cache_data(show_spinner=False)
def evidence_documents():
    """
    The documents the assistant retrieves from, as {filename: text}.

    Only project files. Nothing from the raw dataset and nothing from the web.
    """
    wanted = [
        PROJECT_ROOT / "README.md",
        DOCS / "phase_1_findings.md",
        DOCS / "phase_2_findings.md",
        DOCS / "phase_3_method.md",
        DOCS / "phase_3_findings.md",
        DOCS / "phase_4_findings.md",
        DOCS / "methodology_decisions.md",
        DOCS / "executive_memo.md",
    ]
    documents = {}
    for path in wanted:
        if path.exists():
            documents[path.name] = path.read_text(encoding="utf-8", errors="replace")
    return documents


@st.cache_data(show_spinner=False)
def evidence_tables():
    """
    Small CSVs rendered as text, so the assistant can quote exact figures.

    Large tables are summarised rather than dumped: the raw dataset is never sent
    anywhere, and a long table would crowd out the documents.
    """
    summaries = {}
    for path in sorted(TABLES.glob("*.csv")):
        try:
            frame = pd.read_csv(path)
        except Exception:
            continue
        if len(frame) <= 40:
            text = frame.to_csv(index=False)
        else:
            text = (f"[{len(frame)} rows; first 25 shown]\n"
                    + frame.head(25).to_csv(index=False))
        summaries[path.name] = text
    return summaries
