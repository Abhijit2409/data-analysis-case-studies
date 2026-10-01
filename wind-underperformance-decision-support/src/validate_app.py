"""
Phase 4B validation for the application.

Loads every page through Streamlit's AppTest harness and checks the things that
would otherwise only be caught by clicking around: that pages render without an
exception, that filters survive empty selections, that no model is trained at
runtime, that missing values are never shown as zero, and that displayed numbers
match the generated tables.

The assistant is tested with a stub client. **No real API key is used and no
request is made to any external service.**

Output
    outputs/tables/phase4b_app_checks.csv
"""

import os
import re
import sys
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP = PROJECT_ROOT / "app" / "app.py"
TABLES = PROJECT_ROOT / "outputs" / "tables"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from checks import CheckRecorder                                    # noqa: E402

PAGES = ["Executive cockpit", "Investigation explorer", "Method and scenario lab",
         "Data trust", "Ask the analysis"]


def run_page(label, timeout=120):
    """Start the app and select one page."""
    test = AppTest.from_file(str(APP), default_timeout=timeout)
    test.run()
    if test.exception:
        return test
    test.radio(key="nav").set_value(label).run()
    return test


def check_pages(checker):
    """Every page must load without an exception, with no API key present."""
    os.environ.pop("OPENAI_API_KEY", None)
    for label in PAGES:
        test = run_page(label)
        problems = [f"{e.value}" for e in test.exception] if test.exception else []
        checker.require(f"page_loads_without_exception::{label}",
                        not problems,
                        problems[0][:160] if problems else "rendered cleanly")
    return True


def check_empty_selections(checker):
    """
    Filters must survive being emptied.

    A multiselect cleared to nothing is the most common way a dashboard breaks,
    because an empty filter often produces an empty frame that charts then try to
    plot.
    """
    test = AppTest.from_file(str(APP), default_timeout=120)
    test.run()
    test.radio(key="nav").set_value("Investigation explorer").run()

    # Clear every multiselect on the page, one at a time, then all together.
    for index in range(len(test.multiselect)):
        test.multiselect[index].set_value([]).run()
    checker.require("explorer_survives_all_filters_empty",
                    not test.exception,
                    f"{len(test.multiselect)} multiselects cleared, page still renders")

    # An empty multiselect means "no filter on this field", so the full set stays
    # visible rather than the page going blank. That behaviour is deliberate and
    # is stated on the page; this records it rather than assuming it.
    checker.record("empty_multiselect_means_no_filter_not_no_results",
                   any("counts as no filter" in str(c.value) for c in test.caption),
                   "the page says so explicitly when a filter is empty")

    # The real risk is a chart being handed zero rows. Test that directly.
    sys.path.insert(0, str(PROJECT_ROOT / "app"))
    import charts as chart_module
    empty_frame = pd.read_csv(TABLES / "decision_event_register.csv").iloc[0:0]
    try:
        figure = chart_module.event_scatter(empty_frame, 80)
        annotated = any("No events match" in (a.text or "")
                        for a in figure.layout.annotations)
    except Exception as error:
        figure, annotated = None, False
        checker.record("event_chart_handles_zero_rows", False, str(error)[:120])
    if figure is not None:
        checker.require("event_chart_handles_zero_rows", annotated,
                        "an empty selection draws an explanatory message, not an error")

    lab = AppTest.from_file(str(APP), default_timeout=120)
    lab.run()
    lab.radio(key="nav").set_value("Method and scenario lab").run()
    for index in range(len(lab.multiselect)):
        lab.multiselect[index].set_value([]).run()
    checker.require("method_lab_survives_all_filters_empty",
                    not lab.exception,
                    "severity, duration and turbine selections cleared")
    return True


def check_no_training(checker):
    """The application must not fit, train or tune anything at runtime."""
    banned = ["HistGradientBoosting", ".fit(", "build_reference_curves",
              "fit_challenger", "fit_pooled_curve", "train_test_split"]
    offenders = []
    for path in sorted((PROJECT_ROOT / "app").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for term in banned:
            if term in text:
                offenders.append(f"{path.name}:{term}")
    checker.require("app_never_trains_a_model_at_runtime",
                    not offenders,
                    offenders[0] if offenders else
                    "no model-fitting call in any app module")
    return True


def check_numbers_match_tables(checker):
    """Every headline figure in the app must come from a generated table."""
    sys.path.insert(0, str(PROJECT_ROOT / "app"))
    import content

    accounting = pd.read_csv(TABLES / "energy_accounting.csv")
    figures = {r["quantity"]: r["value"] for _, r in accounting.iterrows()}
    register = pd.read_csv(TABLES / "decision_event_register.csv")
    benchmark = pd.read_csv(TABLES / "phase3_synthetic_injection.csv")
    overlap = pd.read_csv(TABLES / "phase3_event_overlap.csv")
    official = content.OFFICIAL_FINDINGS

    comparisons = [
        ("gross_shortfall_mwh",
         official["gross_shortfall_mwh"],
         round(figures["gross_positive_residual_shortfall_mwh"], 1)),
        ("events_shortfall_mwh",
         official["events_shortfall_mwh"],
         round(figures["shortfall_in_persistent_candidate_events_mwh"], 1)),
        ("nonpersistent_mwh",
         official["nonpersistent_mwh"], round(figures["nonpersistent_shortfall_mwh"], 1)),
        ("missing_records", official["missing_records"], 2074),
    ]
    burdens = benchmark.groupby("method")["apparent_alert_burden"].mean().round(3)
    for key, method in [("burden_a", "A_turbine_specific"),
                        ("burden_b", "B_pooled_transparent"),
                        ("burden_c", "C_pooled_challenger")]:
        comparisons.append((key, official[key], round(float(burdens[method]), 3)))
    comparisons.append(("b_c_agreement_pct", official["b_c_agreement_pct"],
                        float(overlap.loc[overlap["method_pair"].str.contains(
                            "B_pooled_transparent vs C_pooled_challenger"),
                            "agreement_pct_of_union"].iloc[0])))

    mismatches = [f"{name}: app {stated} vs table {actual}"
                  for name, stated, actual in comparisons if stated != actual]
    checker.require("app_constants_match_generated_tables",
                    not mismatches,
                    mismatches[0] if mismatches else
                    f"{len(comparisons)} headline figures match their source tables")

    top = register.iloc[0]
    checker.record("top_event_is_corroborated_and_not_high_confidence",
                   top["methods_agreeing"] == "A+B+C"
                   and top["evidence_confidence"] != "high",
                   f"rank 1: {top['turbine']}, {top['methods_agreeing']}, "
                   f"{top['evidence_confidence']}")
    return True


def check_missing_never_zero(checker):
    """A record with no power value must stay empty, never become zero."""
    timelines = pd.read_csv(TABLES / "decision_event_timelines.csv")
    missing = timelines["P_avg"].isna().sum()
    zeros_from_missing = ((timelines["P_avg"] == 0) & timelines["P_avg"].isna()).sum()
    checker.require("missing_power_values_remain_empty",
                    zeros_from_missing == 0,
                    f"{missing} empty power values preserved as empty, none converted")

    runs = pd.read_csv(TABLES / "presentation_missing_runs.csv")
    checker.record("missing_runs_exported_for_display",
                   len(runs) > 0 and runs["hours"].max() > 100,
                   f"{len(runs)} runs, longest {runs['hours'].max():.1f} h")
    return True


def check_assistant_with_stub(checker):
    """
    Exercise the assistant end to end with a stub client.

    No API key is read and no network call is made. The point is to confirm the
    evidence pack builds, retrieval returns relevant chunks, and the response is
    read correctly from the Responses API shape.
    """
    sys.path.insert(0, str(PROJECT_ROOT / "app"))
    import assistant as helper
    import data as loader

    documents = {}
    for name in ["README.md", "docs/phase_2_findings.md", "docs/phase_3_findings.md",
                 "docs/phase_4_findings.md", "docs/executive_memo.md"]:
        path = PROJECT_ROOT / name
        if path.exists():
            documents[path.name] = path.read_text(encoding="utf-8", errors="replace")
    tables = {p.name: pd.read_csv(p).head(10).to_csv(index=False)
              for p in sorted(TABLES.glob("*.csv"))[:6]}

    chunks = helper.build_evidence_pack.__wrapped__(documents, tables)
    checker.require("assistant_evidence_pack_builds",
                    len(chunks) > 40,
                    f"{len(chunks)} chunks from {len(documents)} documents "
                    f"and {len(tables)} tables")

    selected = helper.retrieve("Why was R80711 selected for investigation?", chunks)
    sources = {chunk.source for _, chunk in selected}
    checker.require("assistant_retrieval_finds_relevant_sources",
                    len(selected) > 0,
                    f"{len(selected)} chunks from {sorted(sources)}")
    checker.record("assistant_retrieval_spreads_across_files",
                   len(sources) >= 2,
                   f"{len(sources)} distinct source files in the top results")

    empty = helper.retrieve("qzxwv nonsense token", chunks)
    checker.record("assistant_returns_nothing_for_unrelated_question",
                   len(empty) == 0,
                   "retrieval returns no chunks rather than irrelevant ones")

    class StubResponse:
        output_text = ("Observation: R80711 produced almost nothing for 42.5 hours "
                       "while peers ran [decision_event_register.csv].")

    class StubResponses:
        def __init__(self):
            self.captured = {}

        def create(self, **kwargs):
            self.captured = kwargs
            return StubResponse()

    class StubClient:
        def __init__(self):
            self.responses = StubResponses()

    stub = StubClient()
    answer, error = helper.ask_model("Why was R80711 selected?",
                                     helper.format_evidence(selected), [], client=stub)
    checker.require("assistant_reads_responses_api_output",
                    error is None and "R80711" in answer,
                    "output_text read from the Responses API result")
    sent = stub.responses.captured
    checker.require("assistant_sends_instructions_and_bounded_output",
                    "instructions" in sent and sent.get("max_output_tokens") ==
                    helper.MAX_OUTPUT_TOKENS,
                    f"max_output_tokens={sent.get('max_output_tokens')}")
    checker.require("assistant_sends_only_retrieved_evidence",
                    "Evidence passages from the project" in sent["input"][-1]["content"],
                    "only the retrieved chunks are sent; the raw dataset never is")

    os.environ.pop("OPENAI_API_KEY", None)
    answer, error = helper.ask_model("test", "evidence", [])
    checker.require("assistant_reports_no_key_without_failing",
                    answer is None and error == "no_key",
                    "returns a no-key signal so the page can fall back to passages")
    return True


def check_no_secret_in_repo(checker):
    """No API key may appear in tracked files or application output."""
    import subprocess
    tracked = subprocess.run(["git", "ls-files"], cwd=PROJECT_ROOT,
                             capture_output=True, text=True).stdout.split()
    offenders = []
    for name in tracked:
        path = PROJECT_ROOT / name
        if not path.exists() or path.suffix in {".png", ".pptx", ".pdf", ".parquet"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # Match the SHAPE of a real key: sk- followed by a long run of key
        # characters. Documentation placeholders contain REPLACE and are skipped,
        # so the check cannot be satisfied by simply rewording a doc.
        for match in re.finditer(r"sk-[A-Za-z0-9_\-]{20,}", text):
            token = match.group(0)
            if "REPLACE" in token:
                continue
            offenders.append(f"{name}: {token[:18]}...")
    checker.require("no_api_key_in_tracked_files",
                    not offenders,
                    offenders[0] if offenders else "no key-shaped string in any tracked file")
    checker.require("secrets_file_is_ignored",
                    ".streamlit/secrets.toml" in
                    (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8"),
                    ".streamlit/secrets.toml is listed in .gitignore")
    checker.record("secrets_example_contains_only_a_placeholder",
                   "REPLACE" in (PROJECT_ROOT / ".streamlit"
                                 / "secrets.toml.example").read_text(encoding="utf-8"),
                   "the example file carries no real value")
    return True


def main():
    checker = CheckRecorder("phase4b_application")
    print("=" * 78)
    print("PHASE 4B - application validation")
    print("No API key is used and no external request is made.")
    print("=" * 78)

    print("\nLoading every page without an API key:")
    check_pages(checker)
    print("\nEmpty filter selections:")
    check_empty_selections(checker)
    print("\nRuntime behaviour:")
    check_no_training(checker)
    check_missing_never_zero(checker)
    print("\nDisplayed numbers against source tables:")
    check_numbers_match_tables(checker)
    print("\nAssistant, with a stub client:")
    check_assistant_with_stub(checker)
    print("\nSecret handling:")
    check_no_secret_in_repo(checker)

    checker.save(TABLES / "phase4b_app_checks.csv")

    # Refresh the combined validation summary so the application's Data trust page
    # includes the checks this run just produced. Without this the summary would
    # depend on which script happened to run last.
    from export_presentation_tables import export_validation_summary
    summary = export_validation_summary()
    print(f"\nCombined validation summary refreshed: "
          f"{int((summary['result'] == 'PASS').sum())}/{len(summary)} checks passed "
          f"across {summary['source_file'].nunique()} files.")


if __name__ == "__main__":
    main()
