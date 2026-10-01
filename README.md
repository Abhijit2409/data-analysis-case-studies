# Data Analysis Case Studies

Business analysis case studies built end to end: question, data, method, findings, recommendation.

Created by [Abhijit Mishra](https://github.com/Abhijit2409)

| Project | Question | Data | Tools |
|---|---|---|---|
| [What Does "Closed" Mean?](vancouver-311-what-does-closed-mean/) | Can a closed Vancouver 3-1-1 case be read as a completed service? | 272,580 public service requests opened in 2025 | Python (pandas), Excel, Power Query |
| [Fair Comparisons for a Fast-Growing Network](specsavers-canada-fair-store-comparisons/) | How do you show which stores warrant attention without ranking a three-month-old store against a ten-year-old one? | Public company statements, plus a synthetic dataset of 30 fictional stores over 26 weeks | Python (pandas), JavaScript, Power BI design |
| [Real Loss or Bad Data?](wind-underperformance-decision-support/) | How much apparent wind-turbine underperformance remains after validating the data, and which cases warrant investigation? | Public SCADA data from four turbines at ENGIE La Haute Borne, 2014–2015 | Python, Streamlit, Plotly, scikit-learn |

## Start here

- **Vancouver 311** — [read the report (PDF)](vancouver-311-what-does-closed-mean/report/Vancouver311_What_Does_Closed_Mean.pdf) · [project README](vancouver-311-what-does-closed-mean/README.md)
- **Specsavers Canada** — [project README](specsavers-canada-fair-store-comparisons/README.md) · [case study deck (PPTX)](specsavers-canada-fair-store-comparisons/report/Specsavers-Canada-Case-Study-Deck.pptx)
- **Wind underperformance decision support** — [project README](wind-underperformance-decision-support/README.md) · [executive memo (PDF)](wind-underperformance-decision-support/deliverables/executive_memo.pdf) · [case study deck (PPTX)](wind-underperformance-decision-support/deliverables/La_Haute_Borne_performance_review.pptx)

Each project folder contains the analysis code, reports, workbooks and interactive prototypes behind it, and documentation
of the method, the calculations and the data-quality checks.

These use **public sources**. Where a project needs transaction-level data that is not public, it says so and runs on
clearly labelled **synthetic** data instead — no figure from a synthetic dataset describes a real organisation's
performance. None of these projects is affiliated with or endorsed by the organisations whose data or public
information they use.
