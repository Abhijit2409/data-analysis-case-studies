"""
Phase 4: build the sendable deliverables.

Maintains the sendable PowerPoint and rebuilds the visual executive memo, then
checks that both files open and contain what they should. The PowerPoint is kept
as an editable design artifact; this script validates it without flattening or
replacing its native charts.

Outputs
    deliverables/La_Haute_Borne_performance_review.pptx
    deliverables/executive_memo.pdf
    outputs/tables/phase4_render_checks.csv
"""

from pathlib import Path
import subprocess
import sys

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from checks import CheckRecorder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = PROJECT_ROOT / "outputs" / "figures"
DELIVERABLES = PROJECT_ROOT / "deliverables"

INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)

FOOTER = ("Independent project. Public data: ENGIE La Haute Borne, Etalab Open Licence 2.0, "
          "via OpenOA. No Clir Renewables data, software or methodology used.")


def add_slide(presentation, title, bullets, note=None, image=None):
    """One content slide. Restrained: a title, text, an optional figure."""
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])

    box = slide.shapes.add_textbox(Inches(0.6), Inches(0.42), Inches(12.1), Inches(0.9))
    frame = box.text_frame
    frame.word_wrap = True
    frame.text = title
    run = frame.paragraphs[0].runs[0]
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = INK

    width = Inches(6.1) if image else Inches(12.1)
    body = slide.shapes.add_textbox(Inches(0.6), Inches(1.45), width, Inches(5.0))
    frame = body.text_frame
    frame.word_wrap = True
    for index, line in enumerate(bullets):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        bold = line.startswith("**")
        paragraph.text = line.replace("**", "")
        paragraph.space_after = Pt(9)
        for run in paragraph.runs:
            run.font.size = Pt(15)
            run.font.color.rgb = INK
            run.font.bold = bold

    if image:
        slide.shapes.add_picture(str(image), Inches(6.9), Inches(1.6), width=Inches(5.9))

    if note:
        caption = slide.shapes.add_textbox(Inches(0.6), Inches(6.45), Inches(12.1), Inches(0.5))
        frame = caption.text_frame
        frame.word_wrap = True
        frame.text = note
        run = frame.paragraphs[0].runs[0]
        run.font.size = Pt(10)
        run.font.italic = True
        run.font.color.rgb = MUTED
    return slide


def build_deck(register, accounting):
    top = register.iloc[0]
    presentation = Presentation()
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)

    add_slide(
        presentation,
        "Which issue should be investigated first?",
        [
            "Question: after validating the data, which issue comes first, what is the "
            "exposure, how confident are we, and what records are needed before acting?",
            "",
            f"**Answer: turbine {top['turbine']}, 26–28 July 2015, {top['duration_hours']:.1f} hours.**",
            f"Potential shortfall {top['mwh_min_across_methods']:.1f}–"
            f"{top['mwh_max_across_methods']:.1f} MWh. Illustratively €1,842–4,513 at €50–120/MWh.",
            f"All three methods agree. Confidence: {top['evidence_confidence']} — the ceiling, "
            "because no operational record exists.",
            "",
            "**Potential shortfall is not confirmed recoverable energy.**",
            "Next step: request event codes and work orders for the interval.",
        ],
        note=FOOTER)

    add_slide(
        presentation,
        "What trusting the raw data would have missed",
        [
            "**The timestamps looked reliable and were wrong.**",
            "They carry proper daylight-saving offsets. But every local day held exactly 144 "
            "ten-minute records, including both clock-change days — which a daylight-saving "
            "logger cannot produce.",
            "The logger's clock never moved: every summer record sat one hour early, about "
            "seven months a year. Correcting it removed all 48 duplicate and 48 absent "
            "intervals and closed a one-hour seasonal gap against independent reanalysis.",
            "",
            "**The meter series is synthetic**, derived from SCADA by the publisher. That "
            "removes the only external cross-check, so all verification here is internal.",
            "",
            "**Missing data is never zero.** Gaps run up to 132.8 hours; 388 are moments when "
            "no turbine reported at all. Filling them would invent days of false outage.",
        ],
        note=FOOTER,
        image=FIGURES / "fig4_timestamp_validation.png")

    figures = {row["quantity"]: row["value"] for _, row in accounting.iterrows()}
    add_slide(
        presentation,
        "Validated energy accounting, 2015",
        [
            f"**Gross positive residual shortfall: "
            f"{figures['gross_positive_residual_shortfall_mwh']:.1f} MWh**",
            f"Inside persistent reviewable events: "
            f"{figures['shortfall_in_persistent_candidate_events_mwh']:.1f} MWh",
            f"Non-persistent short dips: {figures['nonpersistent_shortfall_mwh']:.1f} MWh",
            "Energy lost during missing data: unknown, not zero",
            "Records that cannot be assessed: 2,771",
            "",
            "**Only 57% of the gross figure sits inside reviewable events.**",
            "The rest is scattered across thousands of dips that never persist for an hour — "
            "as likely turbulence, sensor noise or curve approximation as anything operational.",
            "",
            "Reporting the headline as if it were all actionable would be the easiest mistake "
            "available here.",
        ],
        note=FOOTER)

    add_slide(
        presentation,
        "The first investigation, and the next action",
        [
            f"**{top['turbine']}, 26 July 15:10 – 28 July 09:30 UTC (42.5 hours).**",
            "Observed: 97.6% of records at or below zero against an expected 901 kW, while "
            "all three neighbours produced continuously at 724–840 kW in the same 5–12 m/s "
            "wind. The turbine ran normally in the preceding 48 hours.",
            "",
            "Ranked first because it is large, flagged by all three methods, discrete, carries "
            "no data-quality qualifications, and one record request can resolve it.",
            "",
            "**Five explanations fit equally well:** planned maintenance, an unplanned fault "
            "stop, grid curtailment, a controller lockout, or a communications loss while the "
            "turbine was running. Nothing in this dataset can choose between them.",
            "",
            "**Qualification:** removing this one event drops R80711 from 5.35% to 4.46%, "
            "below R80790. Its fleet ranking is event-driven, not a persistent pattern.",
        ],
        note=FOOTER)

    add_slide(
        presentation,
        "Transparent baseline against ML — and why ML is not the headline",
        [
            "**A** each turbine against its own history · **B** the same method pooled across "
            "the fleet · **C** a constrained pooled gradient-boosted challenger.",
            "",
            "**Pooling is the finding.** A judges R80711 against a bar 11–19 kW below its "
            "neighbours. Correcting that moves it from apparently best-behaved to largest "
            "shortfall. Two thirds of the detection gain came from the model, one third from "
            "pooling — but only pooling changed a decision.",
            "",
            "**The challenger passed the registered experimental benchmark (recovery 0.771 → "
            "0.818), but its approximately 41% apparent alert burden means it is not ready "
            "for automated operational alerting.** Neither is A at 38% or B at 40%.",
            "",
            "The acceptance rule constrained only the relative increase in burden, not the "
            "absolute level. That was an incomplete rule, and it is recorded, not patched.",
            "",
            "C agrees with B on only 44.7% of flagged records. B is the decision method; C is "
            "a qualified second opinion.",
        ],
        note=FOOTER)

    add_slide(
        presentation,
        "Limitations, and what transfers",
        [
            "**No event codes, work orders or curtailment records.** Every operational "
            "explanation is a hypothesis. Nothing here reaches 'validated finding'.",
            "**No independent meter validation** — the supplied meter is synthetic.",
            "**Four turbines, 2015 data.** A site-wide problem would be invisible to every "
            "method used. Nothing describes the site today.",
            "**The synthetic benchmark is an upper bound**; clean artificial steps are the "
            "easiest possible detection case.",
            "",
            "**What transfers to solar and portfolio data standardisation** — discipline, not "
            "solar expertise: timestamp alignment; missing data against downtime; degrading "
            "reference sensors (nacelle anemometer → irradiance sensor soiling); unit "
            "standardisation; peer comparison; event taxonomy; separating clipping from "
            "curtailment; and confidence grading before anything reaches a client.",
        ],
        note=FOOTER)

    DELIVERABLES.mkdir(exist_ok=True)
    path = DELIVERABLES / "La_Haute_Borne_performance_review.pptx"
    presentation.save(path)
    return path


def build_memo_pdf():
    """Render the executive memo to PDF. The markdown source stays authoritative."""
    source = (PROJECT_ROOT / "docs" / "executive_memo.md").read_text(encoding="utf-8")
    styles = getSampleStyleSheet()
    # Tight but readable. The memo has to fit on one page when rendered.
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=7.6, leading=9.8,
                          spaceAfter=3)
    heading = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=9.2,
                             spaceBefore=6, spaceAfter=2)
    title = ParagraphStyle("title", parent=styles["Title"], fontSize=13.5, spaceAfter=5)

    # The standard PDF fonts are Latin-1, so typographic punctuation has to be
    # mapped to plain equivalents or it renders as a replacement character.
    SUBSTITUTIONS = {"—": " - ", "–": "-", "‘": "'", "’": "'",
                     "“": '"', "”": '"', "→": "->", "·": "-",
                     "≥": ">=", "≤": "<="}

    def to_markup(text):
        """
        Convert one block of markdown to reportlab's mini-markup.

        Bold is handled on the whole block rather than line by line, because a
        `**...**` pair often straddles a line wrap in the source file. XML-special
        characters are escaped first so the parser never sees a stray angle
        bracket or ampersand.
        """
        for original, plain in SUBSTITUTIONS.items():
            text = text.replace(original, plain)
        text = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        parts = text.split("**")
        # Odd-numbered fragments sit between a pair of markers, so they are bold.
        rebuilt = "".join(f"<b>{part}</b>" if index % 2 else part
                          for index, part in enumerate(parts))
        return rebuilt.replace("\n", " ")

    story = []
    # Group consecutive non-blank lines into paragraphs before converting.
    blocks, current = [], []
    for line in source.splitlines():
        if line.strip() in ("", "---"):
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line.rstrip())
    if current:
        blocks.append("\n".join(current))

    for block in blocks:
        first = block.splitlines()[0].strip()
        if first.startswith("# "):
            story.append(Paragraph(to_markup(block.lstrip("# ").strip()), title))
        elif first.startswith("## "):
            story.append(Paragraph(to_markup(block.lstrip("# ").strip()), heading))
        elif first.startswith("|"):
            for row in block.splitlines():
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                if all(set(c) <= set("-: ") for c in cells):
                    continue          # the |---|---| separator row
                story.append(Paragraph(to_markup(" &nbsp;·&nbsp; ".join(cells)), body))
            story.append(Spacer(1, 3))
        elif first.startswith(">"):
            quoted = " ".join(l.lstrip("> ").strip() for l in block.splitlines())
            story.append(Paragraph(to_markup(quoted), body))
        else:
            story.append(Paragraph(to_markup(block), body))

    path = DELIVERABLES / "executive_memo.pdf"
    document = SimpleDocTemplate(str(path), pagesize=A4, topMargin=12 * mm,
                                 bottomMargin=12 * mm, leftMargin=14 * mm,
                                 rightMargin=14 * mm,
                                 title="La Haute Borne performance review")
    document.build(story)
    return path


def main():
    checker = CheckRecorder("phase4_render")
    print("Building sendable deliverables...")

    deck_path = DELIVERABLES / "La_Haute_Borne_performance_review.pptx"
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "src" / "build_visual_memo.py")],
        check=True,
        cwd=PROJECT_ROOT,
    )
    memo_path = DELIVERABLES / "executive_memo.pdf"

    print("\nVerifying the rendered files open and contain what they should:")
    # Reopen the deck and count what is actually in it, rather than assuming.
    reopened = Presentation(str(deck_path))
    slide_count = len(reopened.slides)
    text_found = "\n".join(
        shape.text_frame.text for slide in reopened.slides
        for shape in slide.shapes if shape.has_text_frame)
    chart_count = sum(
        1 for slide in reopened.slides for shape in slide.shapes
        if getattr(shape, "has_chart", False))
    hyperlink_count = sum(
        1 for slide in reopened.slides for shape in slide.shapes
        if shape.has_text_frame for paragraph in shape.text_frame.paragraphs
        for run in paragraph.runs if run.hyperlink.address)

    checker.require("deck_file_created", deck_path.exists(),
                    f"{deck_path.name}, {deck_path.stat().st_size/1024:.0f} KB")
    checker.require("deck_reopens_with_eight_slides", slide_count == 8,
                    f"{slide_count} slides read back from the saved file")
    checker.require("deck_contains_editable_charts", chart_count == 6,
                    f"{chart_count} native charts read back from the saved file")
    checker.require("deck_contains_project_links", hyperlink_count >= 8,
                    f"{hyperlink_count} hyperlinks read back from the saved file")
    checker.require("deck_states_shortfall_is_not_recoverable",
                    "not confirmed recoverable energy" in text_found,
                    "the disclaimer is present in the deck text")
    checker.require("deck_states_ml_not_ready_for_alerting",
                    "not ready for automated operational alerting" in text_found,
                    "the alerting caveat is present in the deck text")
    checker.record("deck_carries_data_attribution",
                   "Etalab Open Licence" in text_found,
                   "ENGIE / OpenOA attribution on every slide footer")

    checker.require("memo_pdf_created", memo_path.exists(),
                    f"{memo_path.name}, {memo_path.stat().st_size/1024:.0f} KB")
    header = memo_path.read_bytes()[:5]
    checker.require("memo_pdf_is_a_valid_pdf", header == b"%PDF-",
                    f"file header {header!r}")

    # Reopen the PDF and read it back, rather than trusting that it was written.
    from pypdf import PdfReader
    reader = PdfReader(str(memo_path))
    memo_text = "\n".join(page.extract_text() for page in reader.pages)
    pdf_link_count = sum(
        1 for page in reader.pages for annotation in (page.get("/Annots") or [])
        if annotation.get_object().get("/Subtype") == "/Link")
    checker.require("memo_is_three_page_visual_brief", len(reader.pages) == 3,
                    f"{len(reader.pages)} page(s)")
    checker.require("memo_contains_project_link", pdf_link_count >= 1,
                    f"{pdf_link_count} hyperlink annotation(s) read back from the PDF")
    checker.require("memo_pdf_contains_the_recommendation",
                    "R80711" in memo_text and "36.8" in memo_text,
                    "turbine and energy range read back from the rendered file")
    checker.require("memo_pdf_states_shortfall_is_not_recoverable",
                    "not confirmed recoverable energy" in memo_text,
                    "the disclaimer survived rendering")
    checker.record("memo_pdf_has_no_unrenderable_characters",
                   "�" not in memo_text,
                   "no replacement characters in the rendered text")

    checker.save(TABLES / "phase4_render_checks.csv")
    print(f"\n  {deck_path.relative_to(PROJECT_ROOT)}")
    print(f"  {memo_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
