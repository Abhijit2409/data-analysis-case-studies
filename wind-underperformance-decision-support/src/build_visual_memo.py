"""Build the visual executive memo without changing the analysis content."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "executive_memo.pdf"
FIG4 = ROOT / "outputs" / "figures" / "fig4_timestamp_validation.png"
PROJECT_URL = (
    "https://github.com/Abhijit2409/data-analysis-case-studies/tree/main/"
    "wind-underperformance-decision-support"
)

NAVY = colors.HexColor("#0B2638")
INK = colors.HexColor("#1B2C36")
MUTED = colors.HexColor("#64757F")
TEAL = colors.HexColor("#0B8F87")
ORANGE = colors.HexColor("#E28540")
RED = colors.HexColor("#C64949")
PALE = colors.HexColor("#F4F7F8")
GRID = colors.HexColor("#D7E0E4")


class EnergySplitChart(Flowable):
    def __init__(self, width=500, height=96):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        total = 671.6
        persistent = 380.8
        short = 290.8
        split = self.width * persistent / total
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(NAVY)
        c.drawString(0, 78, "Composition of gross positive residual shortfall")
        c.setFillColor(TEAL)
        c.rect(0, 40, split, 26, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.rect(split, 40, self.width - split, 26, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(split / 2, 49, "380.8 MWh | 57%")
        c.drawCentredString(split + (self.width - split) / 2, 49, "290.8 MWh | 43%")
        c.setFont("Helvetica", 8.5)
        c.setFillColor(TEAL)
        c.drawString(0, 22, "Persistent reviewable events")
        c.setFillColor(ORANGE)
        c.drawRightString(self.width, 22, "Non-persistent short dips")
        c.setFillColor(MUTED)
        c.drawString(0, 4, "Potential shortfall is not confirmed recoverable energy.")


class MethodComparisonChart(Flowable):
    def __init__(self, width=500, height=205):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        labels = ["R80711", "R80721", "R80736", "R80790"]
        series = [
            ("A: own history", [4.36, 4.22, 4.25, 6.15], colors.HexColor("#3B6EA8")),
            ("B: pooled transparent", [5.35, 4.49, 4.15, 5.10], ORANGE),
            ("C: pooled challenger", [4.72, 3.56, 3.23, 4.58], TEAL),
        ]
        left, bottom, chart_w, chart_h = 42, 42, self.width - 52, 128
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(NAVY)
        c.drawString(0, self.height - 16, "Gross shortfall by turbine and method (% of potential)")
        for tick in range(0, 8, 2):
            y = bottom + chart_h * tick / 7
            c.setStrokeColor(GRID)
            c.setLineWidth(0.5)
            c.line(left, y, left + chart_w, y)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 7.5)
            c.drawRightString(left - 6, y - 2, str(tick))
        group_w = chart_w / len(labels)
        bar_w = 17
        for g, label in enumerate(labels):
            x0 = left + g * group_w + 20
            for s, (_, vals, color) in enumerate(series):
                h = chart_h * vals[g] / 7
                c.setFillColor(color)
                c.rect(x0 + s * (bar_w + 3), bottom, bar_w, h, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("Helvetica", 8)
            c.drawCentredString(x0 + 28, bottom - 14, label)
        legend_x = 42
        for name, _, color in series:
            c.setFillColor(color)
            c.rect(legend_x, 8, 9, 9, fill=1, stroke=0)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 7.5)
            c.drawString(legend_x + 13, 9, name)
            legend_x += 145


def page_chrome(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 8 * mm, w, 8 * mm, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, h - 8 * mm, 46 * mm, 8 * mm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.4)
    canvas.drawString(15 * mm, 10 * mm, "Independent analysis | Public data | ENGIE La Haute Borne via OpenOA")
    canvas.drawRightString(w - 15 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
title = ParagraphStyle(
    "Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23,
    leading=27, textColor=NAVY, alignment=TA_LEFT, spaceAfter=6,
)
subtitle = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=9.2,
    leading=12, textColor=MUTED, spaceAfter=11,
)
h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16,
    leading=19, textColor=NAVY, spaceBefore=4, spaceAfter=7, keepWithNext=True,
)
h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.2,
    leading=14, textColor=TEAL, spaceBefore=5, spaceAfter=3, keepWithNext=True,
)
body = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2,
    leading=12.2, textColor=INK, spaceAfter=6,
)
small = ParagraphStyle(
    "Small", parent=body, fontSize=8, leading=10, textColor=MUTED, spaceAfter=4,
)
callout = ParagraphStyle(
    "Callout", parent=body, fontName="Helvetica-Bold", fontSize=10.5,
    leading=14, textColor=NAVY, spaceAfter=0,
)
quote = ParagraphStyle(
    "Quote", parent=body, fontName="Helvetica-Bold", fontSize=9.5,
    leading=12.5, textColor=RED, leftIndent=8, rightIndent=8, spaceAfter=0,
)


def p(text, style=body):
    return Paragraph(text, style)


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
    topMargin=16 * mm, bottomMargin=17 * mm,
    title="La Haute Borne performance review",
    author="Abhijit Mishra",
    subject="Independent wind-performance case study",
)

story = []

# Page 1: decision and accounting.
story += [
    p("Which issue should be investigated first?", title),
    p("<b>La Haute Borne wind farm, 2015 assessment year.</b> Independent analysis of public data. 30 September 2026.", subtitle),
    p("<b>Question.</b> After validating the data, which issue should be investigated first, what is the potential exposure, how confident are we, and what operational information is required before anyone acts?"),
]

decision = Table([
    [p("FIRST INVESTIGATION", small), p("DECISION EVIDENCE", small)],
    [p("R80711<br/><font size='15'><b>42.5 hours</b></font><br/>26 July 15:10 to 28 July 09:30 UTC", callout),
     p("Potential shortfall <b>36.8-37.6 MWh</b><br/>Illustrative exposure <b>EUR 1,842-4,513</b> at EUR 50-120/MWh<br/>All three analytical methods flag the event. Confidence is <b>medium</b> because no operational record exists.", body)],
], colWidths=[58 * mm, 112 * mm])
decision.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), PALE),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#DDF2EF")),
    ("BOX", (0, 0), (-1, -1), 0.7, GRID),
    ("INNERGRID", (0, 0), (-1, -1), 0.4, GRID),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
story += [decision, Spacer(1, 6), p("The next step is a request for event codes and work orders covering that interval.", callout)]

warning = Table([[p("Potential shortfall is not confirmed recoverable energy. It is the gap between observed output and a statistical reference built from the same machines' own past. No cause has been established.", quote)]], colWidths=[170 * mm])
warning.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FCEBE7")),
    ("LINEBEFORE", (0, 0), (0, -1), 4, RED),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]))
story += [Spacer(1, 8), warning, Spacer(1, 8), p("Validated energy accounting, 2015", h1), EnergySplitChart(170 * mm, 33 * mm)]

accounting = Table([
    [p("Quantity", small), p("Value", small)],
    [p("Gross positive residual shortfall"), p("<b>671.6 MWh</b>")],
    [p("Shortfall inside persistent reviewable events"), p("380.8 MWh")],
    [p("Non-persistent shortfall (short dips)"), p("290.8 MWh")],
    [p("Energy lost during missing data"), p("<b>unknown, not zero</b>")],
    [p("Records that cannot be assessed"), p("2,771")],
], colWidths=[125 * mm, 45 * mm])
accounting.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
    ("GRID", (0, 0), (-1, -1), 0.35, GRID),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story += [accounting, Spacer(1, 7), p("Only 57% of the gross figure sits inside reviewable events. Treating the headline as actionable would be the easiest mistake available here.", callout), PageBreak()]

# Page 2: validation.
story += [
    Spacer(1, 8 * mm),
    p("What changed after validation", title),
    p("Three things, none of which were visible in the raw data.", subtitle),
    p("The timestamps were confidently wrong", h2),
    p("They carry proper daylight-saving offsets, which makes them look reliable. Every local day held exactly 144 ten-minute records, including both clock-change days - which a daylight-saving logger cannot produce. The logger's clock never moved, so <b>every summer record sat one hour early</b>, about seven months of each year. Correcting it removed all 48 duplicate and all 48 absent intervals and closed a one-hour seasonal gap against independent reanalysis data."),
    p("The meter series is synthetic", h2),
    p("The data publisher derived it from SCADA. That removed the one external cross-check normally available, so every check here is internal. It is a real limitation, not a presentational one."),
    p("Comparing each turbine against itself was hiding the fleet picture", h2),
    p("R80711's own reference sits 11-19 kW below its neighbours, so judging it against its own history flattered it. Under a pooled fleet reference it moves from apparently well-behaved to the largest shortfall on the site. An earlier version of this analysis named R80790 as the turbine with the shallower curve. Measuring it directly showed the opposite, and the correction is recorded in the project history rather than edited away."),
    Spacer(1, 5),
    Image(str(FIG4), width=170 * mm, height=69 * mm, kind="proportional"),
    p("Timestamp validation evidence: the one-hour correction closes the seasonal alignment gap and removes holes in the ten-minute sequence.", small),
    PageBreak(),
]

# Page 3: investigation, method comparison, evidence request and limitations.
story += [
    p("Recommended first investigation", title),
    p("R80711 produced almost nothing for 42.5 hours - <b>97.6% of records at or below zero, against an expected 901 kW</b> - while all three neighbouring turbines produced continuously at 724-840 kW in the same 5-12 m/s wind. In the preceding 48 hours R80711 was operating in line with expectation."),
    p("It is ranked first because it is large, corroborated by all three methods, discrete enough to investigate, carries no data-quality qualifications, and <b>one record request can resolve it</b>."),
    p("An important qualification", h2),
    p("Removing this single event drops R80711 from 5.35% to 4.46% of potential, below R80790's 5.10%. R80711 leads the fleet-relative ranking largely because of this event, not because of a persistent pattern. R80790's more diffuse gap is a separate second line of enquiry."),
    MethodComparisonChart(170 * mm, 65 * mm),
    p("Required next evidence", h1),
    p("Turbine event and alarm codes for the interval; work orders and maintenance records; curtailment or grid instructions; operator logs. The site operations team normally holds the operating records, with curtailment records from the commercial team."),
    p("Five possible explanations fit the evidence equally well - planned maintenance, an unplanned fault stop, grid curtailment, a controller lockout awaiting manual reset, or a communications loss while the turbine was in fact running. <b>Nothing in this dataset can choose between them.</b> If the records show a planned outage, the item closes."),
    p("The three most important limitations", h1),
]

limits = Table([
    [p("01", callout), p("<b>No event codes, work orders or curtailment records exist.</b> Every operational explanation is a hypothesis. No finding reaches validated on the project's evidence hierarchy.")],
    [p("02", callout), p("<b>No independent meter validation.</b> The supplied meter series is synthetic, so all verification is internal.")],
    [p("03", callout), p("<b>Four turbines, and 2015 data.</b> A pooled reference built from four machines is weak, a site-wide problem affecting all of them would remain invisible, and nothing here describes the site today.")],
], colWidths=[14 * mm, 156 * mm])
limits.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PALE, colors.white]),
    ("LINEBELOW", (0, 0), (-1, -2), 0.4, GRID),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story += [
    limits,
    Spacer(1, 7),
    p(f'<a href="{PROJECT_URL}" color="#0B8F87"><u><b>Open the full analysis, source tables and application instructions</b></u></a>', body),
    p("Data: ENGIE La Haute Borne, Etalab Open Licence 2.0, via the OpenOA repository (NatLabRockies/OpenOA). Independent project. No Clir Renewables data, software or methodology was used, and nothing here describes Clir, its platform or its customers. Prices are illustrative; no tariff, PPA or market price is known for this site.", small),
]

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
print(OUT)
