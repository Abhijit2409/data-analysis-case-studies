"""
Document and deck consistency checks (Phase 15, repair pass). Exits 1 on failure.

These complement the behaviour tests: they check that documents, the deck and the README describe the
prototype as it actually behaves (versions, periods, security status, evidence wording, access-test region),
and that identifier families are contiguous. Run: python build/consistency_scan.py
"""
import glob
import json
import os
import re
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
R = []


def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
        return fh.read()


def check(cid, name, ok, detail=""):
    R.append((cid, name, bool(ok), detail))


docs = {p: rd(p) for p in sorted(glob.glob("*.md", root_dir=ROOT))}
phases = {p: t for p, t in docs.items() if p.startswith("phase-")}
alltext = "\n".join(docs.values())
# The issue register and consistency report quote the defects they record, and correction notes quote replaced wording,
# so negative wording scans ignore those files and any line that states a correction or a negation.
CORRECTION = re.compile(r"\b(not|incorrect|earlier|previously|replaced|removed|correction|counting error|was wrong|instead of)\b", re.I)
claims_text = "\n".join(ln for p, t in docs.items() if p not in ("issue-register.md", "consistency-check.md")
                        for ln in t.splitlines() if not CORRECTION.search(ln))
tpl = rd("build/mockup_template.html")
deck_path = os.path.join(ROOT, "Specsavers-Canada-Case-Study-Deck.pptx")
z = zipfile.ZipFile(deck_path)
slide_names = sorted([n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)], key=lambda n: int(re.findall(r"\d+", n)[0]))
note_names = [n for n in z.namelist() if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)]
xml_text = lambda n: " ".join(re.findall(r"<a:t>([^<]*)</a:t>", z.read(n).decode("utf-8")))  # noqa: E731
slides = [xml_text(n) for n in slide_names]
deck_all = " ".join(slides) + " " + " ".join(xml_text(n) for n in note_names)
deck_all = deck_all.replace("&quot;", '"').replace("&amp;", "&").replace("&apos;", "'")


def absent(pattern, text, flags=re.I):
    return [m.group(0) for m in re.finditer(pattern, text, flags)]


# ------------------------------------------------------------------ DOC checks
check("DOC-01", "No document or deck claims the mockup demonstrates RLS/OLS; simulated role view stated",
      not absent(r"demonstrat\w*\s+(row-level security|RLS|OLS|object-level)", claims_text + " " + deck_all) and "Simulated role view" in tpl and "simulated" in deck_all.lower())
check("DOC-02", "Small-count rule v0.2 (suppressed numerator) documented in PR-04 and the KPI dictionary",
      "numerator is 1–4" in docs["phase-05-nfr-data-privacy-security.md"].replace("1-4", "1–4") and "count-based numerator" in docs["phase-06-kpi-dictionary.md"])
check("DOC-03", "KPI placement reconciled (Phase 11 KPI-07 not tooltip-only; recall and turnaround cards in prototype)",
      "— (tooltip)" not in docs["phase-11-mvp-definition.md"] and 'rate("recall_rate"' in tpl and 'rate("turnaround"' in tpl)
k11 = docs["phase-06-kpi-dictionary.md"].split("## KPI-11")[1].split("## KPI-12")[0]
check("DOC-04", "KPI-11 uses one method (equal-weighted mean) with a worked example; simulated values stated",
      "mean of per-source completeness" in k11 and "Worked example" in k11 and "simulated directly" in k11 and "Σ records received per source" not in k11)
check("DOC-05", "Finalised-snapshot assumption visible in the dictionary, dataset document and dashboard",
      "finalised snapshot" in docs["phase-06-kpi-dictionary.md"].lower() and "finalised snapshot" in docs["phase-12-synthetic-dataset.md"].lower()
      and "treated as final" in tpl)
p7 = docs["phase-07-data-model-and-flow.md"]
check("DOC-06", "FACT_SALES split into exam-week and transaction-week facts; TQ-06 resolved; converted stores logged (TQ-12)",
      "| **FACT_SALES** |" not in p7 and "FACT_EXAM_CONVERSION" in p7 and "FACT_SALES_REVENUE" in p7 and "Resolved (repair pass)" in p7 and "TQ-12" in p7)
p13 = docs["phase-13-power-bi-dashboard-design.md"]
check("DOC-07", "Power BI guidance: daily contiguous calendar, selector table, unexecuted label, correct OLS, Microsoft sources cited",
      "Mark as date table (weekly)" not in p13 and "**None** permission" not in p13 and "Contiguous daily dates" in p13 and "`KPISelector`" in p13
      and "unexecuted" in p13.lower() and "learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables" in p13
      and "object-level-security" in p13 and "no mechanism to secure a measure directly" in p13)
bad_v01 = [ln for ln in claims_text.splitlines() if re.search(r"v0\.1 parameter", ln)]
check("DOC-08", "Versions reconciled: recall parameter belongs to exception rule set v0.2 everywhere; banner shows three versions",
      not bad_v01 and "Exception rules ${VER.exception_rules}" in tpl, "; ".join(bad_v01)[:200])
p14, p8 = docs["phase-14-uat-and-implementation.md"], docs["phase-08-user-stories.md"]
check("DOC-09", "Access tests use the Atlantic manager demonstrated in the prototype (ACC-03, UAT-10, US-07 AC2)",
      "Regional Retail Manager – Atlantic" in p14 and "RRM (Atlantic)" in p14 and "RRM (Prairies)" not in p14 and "mapped to the Atlantic region" in p8)
stale = absent(r"awaiting approval|stopping here|need your approval|\(for approval\)|pending approval|Status:\*\* Approved|Status:\*\* Complete", "\n".join(phases.values()))
check("DOC-10", "No stale approval or completion language in phase documents", not stale, ", ".join(stale))
fsm = docs.get("feature-status-matrix.md", "")
check("DOC-11", "Feature-status matrix exists with implemented, simulated, specified-only and deferred statuses",
      all(s in fsm for s in ["Implemented (prototype)", "Simulated", "Specified only", "Deferred"]))
p12 = docs["phase-12-synthetic-dataset.md"]
check("DOC-12", "Phase 12 column count correct (23 requested + weeks_since_opening = 24)",
      not [ln for ln in p12.splitlines() if "22 requested" in ln and not CORRECTION.search(ln)] and "24 columns" in p12)
check("DOC-13", "Evidence wording: dated counts, EV-17 completion statement, 'roughly half' labelled inference",
      "EV-17" in docs["evidence-log.md"] and "Inference, not fact" in docs["evidence-log.md"] and "INFERENCE" in slides[1] and "≈ half" in slides[1])
check("DOC-14", "Deck removes unsupported claims ('today's network', 'rank every young store', 'hidden by peer suppression')",
      not absent(r"today.s network|rank every young store|every young store at the bottom|hidden by peer suppression|New store is hidden", deck_all + " " + claims_text))
check("DOC-15", "Slide 7 shows the repaired dashboard (images) with a synthetic walkthrough",
      z.read(slide_names[6]).decode().count("<p:pic>") >= 1 and "Walkthrough" in slides[6] and "SYNTHETIC" in slides[6])
rels = z.read("ppt/slides/_rels/slide10.xml.rels").decode()
links = re.findall(r'Target="(https?://[^"]+)"', rels)
ev_urls = set(re.findall(r"\((https?://[^)\s]+)\)", docs["evidence-log.md"]))
unknown = [u for u in links if u not in ev_urls and "learn.microsoft.com" not in u and u.replace("&amp;", "&") not in ev_urls]
check("DOC-16", "Appendix A1: complete hyperlinks (no ellipses) that match the evidence log",
      len(links) >= 14 and "…" not in slides[9] and "..." not in slides[9] and not unknown, f"{len(links)} links; unmatched: {unknown[:3]}")
pkg = json.loads(rd("build/package.json"))
readme = docs["README.md"]
check("DOC-17", "README has launch, demonstration route, reproduction, tests and limitations; npm test is real",
      all(s in readme for s in ["Open the dashboard", "demonstration route", "run_tests.py", "Honest limitations"]) and "no test specified" not in pkg["scripts"]["test"])
cc = docs.get("consistency-check.md", "")
check("DOC-18", "Consistency report distinguishes seeded-pattern checks, reconciliation, UI regression and proposed UAT",
      all(s in cc for s in ["Seeded-pattern", "reconciliation", "UI regression", "internal UAT"]))
causal = absent(r"caused by|due to|root cause|\bdriver of\b", " ".join(slides))
check("DOC-19", "No prohibited causal wording on deck slides", not causal, ", ".join(causal))
ui = rd("evidence/ui-test-results.json") if os.path.exists(os.path.join(ROOT, "evidence/ui-test-results.json")) else "{}"
check("DOC-20", "Open internal-policy questions U-38, U-39, U-41 remain visible as unresolved",
      all(u in docs["phase-10-raid-registers.md"] for u in ["U-38", "U-39", "U-41"]) and "Still open after the repair pass" in docs["phase-10-raid-registers.md"])

# ------------------------------------------------------------------ identifier families
families = {"BO": 7, "BR": 12, "FR": 18, "NFR": 8, "DR": 10, "PR": 8, "SR": 8, "KPI": 12, "US": 10, "UAT": 24, "SH": 18, "EV": 17,
            "A": 47, "U": 42, "DQ": 35, "TQ": 12, "CP": 9, "MDM": 9, "R": 22, "CON": 9, "DEP": 12, "RTM": 25, "EO": 7, "SI": 10, "ISS": 45}
gaps = []
for fam, expected in families.items():
    found = {int(n) for n in re.findall(rf"(?<![A-Za-z-]){fam}-(\d{{1,2}})(?!\d)", alltext)}
    missing = [i for i in range(1, expected + 1) if i not in found]
    if missing:
        gaps.append(f"{fam}: missing {missing[:6]}")
check("ID-01", "Identifier families contiguous (BO…ISS, including repair-pass additions)", not gaps, "; ".join(gaps))

width = max(len(n) for _, n, _, _ in R)
for cid, name, ok, detail in R:
    print(f"{'PASS' if ok else 'FAIL'}  {cid:<7} {name}{'' if ok or not detail else ' — ' + detail}")
failed = [r for r in R if not r[2]]
print(f"\nDocument checks passed: {len(R) - len(failed)}/{len(R)}")
sys.exit(1 if failed else 0)
