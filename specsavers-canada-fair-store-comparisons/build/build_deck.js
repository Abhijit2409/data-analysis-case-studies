/* Phase 15 deck builder — outside-in case study. All quantitative results are SYNTHETIC. Rebuilt in the repair pass. */
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "analysis_summary.json"), "utf8"));
const OUT = path.join(ROOT, "Specsavers-Canada-Case-Study-Deck.pptx");
const IMG = path.join(__dirname, "deck_images");

/* ---------------------------------------------------------------- test evidence (from the last run of build/run_tests.py) */
const TR = fs.existsSync(path.join(ROOT, "evidence", "test-results.md")) ? fs.readFileSync(path.join(ROOT, "evidence", "test-results.md"), "utf8") : "";
const grab = (re, fallback) => { const m = TR.match(re); return m ? m[1] : fallback; };
const TESTS = {
  checks: grab(/Checks passed: (\d+\/\d+)/, "32/32"),
  py: grab(/Ran (\d+) tests/, "30"),
  js: grab(/pass (\d+), fail 0/, "15"),
  ui: grab(/UI checks passed: (\d+\/\d+)/, "83/83"),
  overall: /\*\*Overall:\*\* PASS/.test(TR),
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "Fair Comparisons for a Fast-Growing Network — Outside-In Case Study";
pres.subject = "Data Business Analyst case study (public information + synthetic data)";

const C = {
  teal: "0B5D57", teal2: "1F8A80", tealDark: "08423E", tealCard: "0F6E67", tealLight: "E3EFED",
  ink: "1D2A33", muted: "56656F", line: "D9E1E6", orange: "C4581B", orangeText: "A84A14", orangeLight: "FBEAE0",
  bg: "F4F7F8", white: "FFFFFF", amber: "8A5300", red: "B3261E", green: "2E7D32", grey: "6B7B85", purple: "5E4B8B",
};
const HF = "Cambria", BF = "Calibri";
const pctf = (v, d = 1) => (v == null ? "n/a" : (v * 100).toFixed(d) + "%");

function T(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, fontFace: BF, color: C.ink, margin: 0, valign: "top" }, o));
}
function header(slide, n, kicker, title, dark = false) {
  T(slide, kicker.toUpperCase(), { x: 0.5, y: 0.32, w: 10, h: 0.28, fontSize: 11, bold: true, color: dark ? "A9D6D0" : C.teal, charSpacing: 1.5 });
  T(slide, title, { x: 0.5, y: 0.6, w: 12.3, h: 0.7, fontSize: 28, fontFace: HF, bold: true, color: dark ? C.white : C.ink });
  if (n) T(slide, String(n), { x: 12.3, y: 0.32, w: 0.55, h: 0.28, fontSize: 11, color: dark ? "A9D6D0" : C.muted, align: "right" });
}
const TAGS = { FACT: C.teal, INFERENCE: C.purple, ASSUMPTION: C.amber, SYNTHETIC: C.orangeText, ILLUSTRATIVE: C.grey, "COMMISSIONED SURVEY": C.grey, "NOT EXECUTED": C.red };
function tag(slide, x, y, label) {
  slide.addText(label, { isTextBox: true, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x, y, w: label.length * 0.082 + 0.3, h: 0.25,
    fontSize: 9, bold: true, color: C.white, fill: { color: TAGS[label] }, align: "center", valign: "middle", margin: 0, fontFace: BF, charSpacing: 0.5 });
}
function source(slide, text, dark = false) {
  T(slide, text, { x: 0.5, y: 7.02, w: 12.3, h: 0.32, fontSize: 9, color: dark ? "A9D6D0" : C.muted });
}
function card(slide, x, y, w, h, fill = C.bg, line = null) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: line ? { color: line, width: 0.75 } : { type: "none" } });
}
function circleNum(slide, x, y, n, fill = C.teal) {
  slide.addText(String(n), { isTextBox: true, shape: pres.shapes.OVAL, x, y, w: 0.4, h: 0.4, fill: { color: fill }, color: C.white, bold: true, fontSize: 13, align: "center", valign: "middle", margin: 0, fontFace: BF });
}
function bullets(items, o = {}) {
  return items.map((t, i) => {
    const base = { bullet: o.bullet === false ? false : { indent: 12 }, breakLine: i < items.length - 1, paraSpaceAfter: o.space || 4 };
    if (typeof t === "string") return { text: t, options: base };
    return { text: t.text, options: Object.assign(base, t.options || {}) };
  });
}
function table(slide, rows, o) {
  const head = rows[0].map((h) => ({ text: h, options: { bold: true, color: C.white, fill: { color: C.teal } } }));
  const body = rows.slice(1).map((r, i) => r.map((c) => (typeof c === "object" && c !== null ? c : { text: String(c), options: { fill: { color: i % 2 ? "F7FAFA" : C.white } } })));
  slide.addTable([head, ...body], Object.assign({ fontFace: BF, fontSize: 9, color: C.ink, border: { type: "solid", pt: 0.5, color: C.line }, margin: 0.04, valign: "middle" }, o));
}
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}
function image(slide, name, x, y, maxW, maxH) {
  const file = path.join(IMG, name);
  if (!fs.existsSync(file)) throw new Error("Missing deck image " + file + " — run node build/capture_screenshots.js");
  const s = pngSize(file);
  let w = maxW, h = (maxW * s.h) / s.w;
  if (h > maxH) { h = maxH; w = (maxH * s.w) / s.h; }
  slide.addShape(pres.shapes.RECTANGLE, { x: x - 0.02, y: y - 0.02, w: w + 0.04, h: h + 0.04, fill: { color: C.white }, line: { color: C.line, width: 0.75 } });
  slide.addImage({ path: file, x, y, w, h, altText: "Screenshot of the synthetic-data prototype: " + name.replace(/[-_]/g, " ").replace(".png", "") });
  return { w, h };
}

const NW = D.network_week_latest, ATW = D.region_week_latest.Atlantic, R4 = D.region_last4, CK = D.cohort_kpis, P = D.patterns;
const otherTurn = ["Ontario", "Prairies", "West"].map((r) => R4[r].turnaround);
const sw = D.store_weekly;
const lastRec = (sid) => sw[sid][sw[sid].length - 1];
const syn014 = lastRec("SYN-014");

/* =========================================================== SLIDE 1 — Title */
{
  const s = pres.addSlide();
  s.background = { color: C.teal };
  T(s, "OUTSIDE-IN DATA BUSINESS ANALYSIS CASE STUDY", { x: 0.7, y: 0.7, w: 9, h: 0.3, fontSize: 12, bold: true, color: "A9D6D0", charSpacing: 2 });
  T(s, "Fair Comparisons for a\nFast-Growing Network", { x: 0.7, y: 1.1, w: 7.6, h: 1.9, fontSize: 44, fontFace: HF, bold: true, color: C.white });
  T(s, "Store ramp-up and partner performance intelligence — a proposed reporting product for Specsavers Canada", { x: 0.7, y: 3.05, w: 7.2, h: 0.8, fontSize: 18, color: "DDEFEC" });
  T(s, [
    { text: "What I did  ", options: { bold: true, color: C.white } },
    { text: "Researched public evidence, analysed stakeholders, wrote requirements and KPI rules, designed the data model, generated a synthetic dataset, built and tested a three-page prototype, and planned UAT.", options: { color: "DDEFEC" } },
  ], { x: 0.7, y: 4.05, w: 7.2, h: 1.1, fontSize: 13.5 });
  T(s, "Portfolio case study for the Data Business Analyst role · Specsavers Canada, Burnaby, BC · September 2026", { x: 0.7, y: 6.55, w: 8, h: 0.35, fontSize: 11, color: "A9D6D0" });

  card(s, 8.55, 0.7, 4.1, 5.95, C.tealDark);
  T(s, "Outside-in disclaimer", { x: 8.85, y: 0.95, w: 3.6, h: 0.35, fontSize: 15, bold: true, color: C.white, fontFace: HF });
  T(s, bullets([
    "Built only from public information and synthetic data.",
    "Does not claim that Specsavers' reporting is inadequate or that any stakeholder reviewed this work.",
    "Every number in the prototype is fictional.",
    "Targets, thresholds and definitions are illustrative proposals.",
    "No patient-identifiable data, diagnoses or individual performance.",
  ], { space: 8 }), { x: 8.85, y: 1.4, w: 3.55, h: 3.6, fontSize: 12.5, color: "DDEFEC" });
  T(s, "Evidence labels used throughout", { x: 8.85, y: 5.2, w: 3.6, h: 0.3, fontSize: 11, bold: true, color: C.white });
  tag(s, 8.85, 5.6, "FACT"); tag(s, 9.65, 5.6, "INFERENCE"); tag(s, 10.93, 5.6, "ASSUMPTION");
  tag(s, 8.85, 5.97, "SYNTHETIC"); tag(s, 10.07, 5.97, "ILLUSTRATIVE");
  s.addNotes("This is an outside-in portfolio case study for the Data Business Analyst role. My contribution is the whole chain: public research with an evidence log, stakeholder analysis, business and functional requirements, a KPI dictionary with explicit calculation rules, a conceptual data model, user stories, traceability, risks, an MVP, a synthetic dataset I generated and validated, a three-page prototype I built and tested, and a UAT plan. Nothing here claims internal knowledge, and no Specsavers stakeholder has reviewed it. The coloured labels show the evidence status of each claim.");
}

/* =========================================================== SLIDE 2 — Public evidence */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 2, "Specsavers Canada context — public evidence, dated", "Rapid, geographically diverse growth");
  const stats = [
    ["111", "in-grocery locations announced in Jul 2025 and reported open during 2025 (release of 22 Jun 2026)", "FACT", "EV-01, EV-17"],
    ["270+", "locations across nine provinces and one territory, as reported in Mar and Jun 2026", "FACT", "EV-02, EV-17"],
    ["≈ half", "of the network opened in 2025: 130+ openings of 270+ stores (Mar 2026) — my arithmetic on lower bounds", "INFERENCE", "EV-02"],
    ["20%", "of stores were open under six months at the 100-store milestone (Feb 2024)", "FACT", "EV-06"],
  ];
  stats.forEach(([big, lab, t, ev], i) => {
    const x = 0.5 + (i % 2) * 3.2, y = 1.55 + Math.floor(i / 2) * 2.7;
    card(s, x, y, 3.0, 2.5, C.bg);
    T(s, big, { x: x + 0.22, y: y + 0.15, w: 2.6, h: 0.8, fontSize: 38, bold: true, color: t === "FACT" ? C.teal : C.purple, fontFace: HF });
    T(s, lab, { x: x + 0.22, y: y + 0.95, w: 2.6, h: 1.05, fontSize: 12.5 });
    tag(s, x + 0.22, y + 2.08, t);
    T(s, ev, { x: x + 1.55, y: y + 2.1, w: 1.3, h: 0.24, fontSize: 9.5, color: C.muted, align: "right" });
  });

  T(s, "Partnership operating model", { x: 7.1, y: 1.5, w: 4.3, h: 0.32, fontSize: 15, bold: true, fontFace: HF });
  tag(s, 11.95, 1.54, "FACT");
  card(s, 7.1, 1.95, 2.75, 1.2, C.tealLight);
  T(s, [{ text: "Optometry Partner", options: { bold: true, breakLine: true } }, { text: "Independent optometry corporation · clinical leader", options: { fontSize: 11.5, color: C.muted } }], { x: 7.25, y: 2.08, w: 2.5, h: 1.0, fontSize: 13 });
  card(s, 10.05, 1.95, 2.75, 1.2, C.tealLight);
  T(s, [{ text: "Retail Partner", options: { bold: true, breakLine: true } }, { text: "Specsavers retail corporation · store leader", options: { fontSize: 11.5, color: C.muted } }], { x: 10.2, y: 2.08, w: 2.5, h: 1.0, fontSize: 13 });
  card(s, 7.1, 3.3, 5.7, 1.45, C.teal);
  T(s, [{ text: "Central support services", options: { bold: true, breakLine: true } },
        { text: "Procurement · supply chain · marketing and patient recall · IT and patient-record systems · training · finance · business development", options: { fontSize: 11.5 } }],
    { x: 7.28, y: 3.42, w: 5.35, h: 1.25, fontSize: 13, color: C.white });
  T(s, "Each business is owned \"in accordance with provincial regulations\" (prospectus, EV-04)", { x: 7.1, y: 4.85, w: 5.7, h: 0.3, fontSize: 11, italic: true, color: C.muted });

  card(s, 7.1, 5.3, 5.7, 1.55, C.orangeLight);
  T(s, "Access challenge (Specsavers-commissioned survey, n = 2,022, Feb 2025)", { x: 7.28, y: 5.4, w: 5.4, h: 0.3, fontSize: 11.5, bold: true });
  T(s, [
    { text: "1 in 3 ", options: { bold: true, color: C.orangeText } }, { text: "adults overdue for an eye exam · ", options: {} },
    { text: "51% ", options: { bold: true, color: C.orangeText } }, { text: "cite cost · ", options: {} },
    { text: "61% ", options: { bold: true, color: C.orangeText } }, { text: "of people who qualify for provincial coverage don't think they are covered", options: {} },
  ], { x: 7.28, y: 5.75, w: 5.4, h: 0.7, fontSize: 12.5 });
  tag(s, 7.28, 6.5, "COMMISSIONED SURVEY");
  source(s, "Sources: Loblaw releases (30 Jul 2025; 22 Jun 2026); Specsavers releases via Newswire (7 Feb 2024; 9 Oct 2025; 11 Mar 2026); partnership prospectus (Oct 2025). Links: Appendix A1.");
  s.addNotes("Four public figures frame the opportunity, each with its date. The July 2025 Loblaw announcement said 111 Specsavers locations would open inside Loblaw grocery stores; the June 2026 PC Optimum release confirms those 111 opened during 2025. Specsavers reported more than 270 stores in March 2026, and the June 2026 release repeats more than 270 locations across nine provinces and one territory. The 'roughly half' figure is my own arithmetic — more than 130 openings in 2025 out of more than 270 stores — so it is an inference on two lower bounds, not a company statement. Specsavers itself tracked the share of stores under six months old in 2024. The ownership model has two partner corporations plus central support services. The access survey was commissioned by Specsavers, so I treat it as context, not independent research. Full links are in Appendix A1.");
}

/* =========================================================== SLIDE 3 — Decision and hypothesis */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 3, "Business decision and hypothesis", "Unadjusted store comparisons could mislead in a network like this");
  card(s, 0.5, 1.5, 12.33, 1.3, C.tealLight);
  T(s, [
    { text: "Decision the product supports: ", options: { bold: true, color: C.teal } },
    { text: "“Which stores warrant attention relative to comparable stores, which candidate factors should be investigated, and which business team should follow up?”", options: { italic: true, breakLine: true } },
    { text: "Hypothesis: ", options: { bold: true } },
    { text: "partners and support-office teams may benefit from a consistent, fair way to monitor ramp-up and compare like-for-like stores.", options: {} },
  ], { x: 0.75, y: 1.62, w: 11.2, h: 1.1, fontSize: 14 });
  tag(s, 11.35, 2.45, "INFERENCE");

  const mech = [
    ["Maturity mix", "Many stores are young; volume grows with age."],
    ["Structural diversity", "Province, regulation and host format differ."],
    ["Two entities", "Clinical and retail activity may sit in different systems."],
    ["Many owners", "Supply chain, marketing and finance each own part of the picture."],
  ];
  mech.forEach(([h, b], i) => {
    const x = 0.5 + i * 3.1;
    card(s, x, 3.0, 2.95, 1.55, C.bg);
    circleNum(s, x + 0.18, 3.13, i + 1);
    T(s, h, { x: x + 0.7, y: 3.17, w: 2.15, h: 0.35, fontSize: 14, bold: true });
    T(s, b, { x: x + 0.2, y: 3.65, w: 2.6, h: 0.85, fontSize: 12.5 });
  });

  T(s, "Why now", { x: 0.5, y: 4.8, w: 5, h: 0.35, fontSize: 16, bold: true, fontFace: HF });
  T(s, bullets([
    "A large 2025 opening cohort is ramping up through 2026",
    "New provinces with little historical baseline",
    "PC Optimum earning from Jun 2026: a future data stream, outside the MVP",
    "Burnaby data hiring shows investment — not proof of a reporting gap",
  ], { space: 5 }), { x: 0.5, y: 5.2, w: 6.3, h: 1.7, fontSize: 13 });

  card(s, 7.05, 4.8, 5.78, 2.1, C.orangeLight);
  T(s, "What the evidence does not show", { x: 7.25, y: 4.9, w: 5.4, h: 0.3, fontSize: 14, bold: true, color: C.orangeText });
  T(s, "No public evidence says current reporting is inadequate. Discovery would start with what exists today.", { x: 7.25, y: 5.25, w: 5.4, h: 0.6, fontSize: 12.5 });
  T(s, [
    { text: "Synthetic illustration (all 26 weeks): ", options: { bold: true } },
    { text: `New stores average ${CK.New.exams_per_store_week.toFixed(0)} exams per store-week vs ${CK.Mature.exams_per_store_week.toFixed(0)} for Mature — an unadjusted comparison mixes store age with performance.`, options: {} },
  ], { x: 7.25, y: 5.9, w: 4.1, h: 0.95, fontSize: 12 });
  tag(s, 11.55, 6.55, "SYNTHETIC");
  source(s, "Sources: EV-01, EV-02, EV-08, EV-09, EV-17 (Appendix A2). Illustration: synthetic dataset (Appendix A8).");
  s.addNotes("The hypothesis rests on four mechanisms, each an inference from public facts rather than a known problem: a young network, structural diversity, two ownership entities whose data may sit in different systems, and many central functions. I reframed the decision in triage language — which stores warrant attention and what to investigate — so the product never implies it can explain causes. The synthetic illustration shows why age matters: in my fictional data New stores average far fewer exams than Mature stores, so any unadjusted comparison mixes age with performance. I have no evidence that current reporting is poor; that is the first thing discovery would test.");
}

/* =========================================================== SLIDE 4 — Stakeholders */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 4, "Stakeholders, decisions and discovery approach", "Eighteen stakeholder groups, four core decisions");
  const qx = 0.85, qy = 1.55, qw = 5.6, qh = 4.7;
  const quads = [
    ["Keep satisfied", "Finance · Privacy / Governance · Partnership Advisory Committee · Executive leadership", 0, 0, "F3F6F7"],
    ["Manage closely", "Retail Operations (sponsor, assumed) · Product Owner · Retail and Optometry Partners · Regional Retail Managers (title TBC) · Data Delivery Manager", 1, 0, C.tealLight],
    ["Monitor", "Source-system owners (until data access is needed)", 0, 1, "F7F9FA"],
    ["Keep informed and involved", "Marketing · Supply Chain · Business Development · Clinical Services · Data engineers and analysts", 1, 1, "F3F6F7"],
  ];
  quads.forEach(([t, b, cx, cy, fill]) => {
    const x = qx + cx * (qw / 2), y = qy + cy * (qh / 2);
    card(s, x + 0.04, y + 0.04, qw / 2 - 0.08, qh / 2 - 0.08, fill);
    T(s, t, { x: x + 0.18, y: y + 0.15, w: qw / 2 - 0.35, h: 0.3, fontSize: 13, bold: true, color: t === "Manage closely" ? C.teal : C.ink });
    T(s, b, { x: x + 0.18, y: y + 0.52, w: qw / 2 - 0.35, h: qh / 2 - 0.7, fontSize: 11.5 });
  });
  T(s, "Influence ↑", { x: 0.1, y: 3.6, w: 0.8, h: 0.3, fontSize: 10.5, color: C.muted, rotate: 270 });
  T(s, "Interest →", { x: qx, y: qy + qh + 0.05, w: qw, h: 0.25, fontSize: 10.5, color: C.muted, align: "center" });
  tag(s, qx, 6.6, "FACT"); T(s, "Partner roles, Privacy Officer, data roles", { x: qx + 0.75, y: 6.62, w: 2.9, h: 0.24, fontSize: 10, color: C.muted });
  tag(s, qx + 3.3, 6.6, "ASSUMPTION"); T(s, "Other titles", { x: qx + 4.5, y: 6.62, w: 1.3, h: 0.24, fontSize: 10, color: C.muted });

  table(s, [
    ["Who", "Decision the product must support"],
    ["Regional Retail Manager", "Which stores do I contact this week, and about what?"],
    ["Retail and Optometry Partners", "Where should my team focus? Are we ramping like similar stores?"],
    ["Retail Operations lead", "Where to direct support; approve peer and cohort rules"],
    ["Privacy Officer", "What may be shown, to whom, at what aggregation?"],
  ], { x: 6.85, y: 1.55, w: 5.98, colW: [2.15, 3.83], fontSize: 11.5, rowH: 0.42 });

  T(s, "Discovery approach", { x: 6.85, y: 3.85, w: 4, h: 0.32, fontSize: 14, bold: true, fontFace: HF });
  ["Validate problem", "KPI workshops", "Data & privacy", "Prototype tests", "Endorse"].forEach((st, i) => {
    s.addText(st, { isTextBox: true, shape: pres.shapes.CHEVRON, x: 6.85 + i * 1.2, y: 4.25, w: 1.25, h: 0.6, fill: { color: i === 4 ? C.orangeText : C.teal }, color: C.white, fontSize: 10, bold: true, align: "center", valign: "middle", margin: 0, fontFace: BF });
  });
  T(s, "Sample stores across maturity, province and format · hear Retail and Optometry Partners separately · 35 discovery questions (Appendix A3)", { x: 6.85, y: 4.97, w: 5.98, h: 0.55, fontSize: 11.5, color: C.muted });
  card(s, 6.85, 5.6, 5.98, 1.3, C.orangeLight);
  T(s, "Tensions to surface early", { x: 7.05, y: 5.68, w: 5.6, h: 0.3, fontSize: 13, bold: true, color: C.orangeText });
  T(s, bullets(["Peer visibility vs partner commercial confidentiality", "Conversion framed as sales pressure on clinical care", "Point-of-sale revenue vs finance ledger as the source of truth"], { space: 2 }), { x: 7.05, y: 6.0, w: 5.6, h: 0.85, fontSize: 12 });
  source(s, "Stakeholder IDs SH-01 to SH-18, RACI and engagement plan: Appendix A3. Titles are proposals, not confirmed Specsavers positions; none of these groups has reviewed the work.");
  s.addNotes("I evaluated thirteen proposed groups and added five, including the Partnership Advisory Committee, which the partnership site confirms exists, and Business Development, the likely owner of store opening dates — the field the whole maturity concept depends on. I found no public evidence for a 'Retail Performance Manager' title, so I used Regional Retail Manager, title to be validated. Partners are consulted rather than approvers, with endorsement through the advisory committee. Three tensions stand out, and I would surface them in the first workshops rather than at UAT.");
}

/* =========================================================== SLIDE 5 — Requirements and BA judgments */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 5, "Requirements, KPI rules and trade-offs", "Five judgments that make comparisons fair and safe");
  const chain = [["7", "Business\nobjectives"], ["12", "Business\nrequirements"], ["18", "Functional\nrequirements"], ["34", "NFR · data ·\nprivacy · security"], ["12", "Governed\nKPIs"], ["10", "User\nstories"], ["24", "UAT\nscenarios"]];
  chain.forEach(([n, l], i) => {
    const x = 0.5 + i * 1.77;
    s.addShape(pres.shapes.CHEVRON, { x, y: 1.45, w: 1.82, h: 1.0, fill: { color: i % 2 ? C.teal2 : C.teal }, line: { type: "none" } });
    T(s, n, { x: x + 0.35, y: 1.49, w: 1.1, h: 0.45, fontSize: 22, bold: true, color: C.white, align: "center", fontFace: HF });
    T(s, l, { x: x + 0.3, y: 1.93, w: 1.2, h: 0.5, fontSize: 10, color: C.white, align: "center" });
  });
  const J = [
    ["Compare like with like", "Peers share maturity cohort (as at each week) and format; fall back to the whole cohort; hide below 5 stores.", "Fairness vs small groups: some young stores get no peer comparison."],
    ["Flag areas, not causes", "Rule (a): below comparable stores. Rule (b): worse than the store's own 8-week baseline for 3 weeks. Prompts name a follow-up team.", "Explainable flags vs subtle signals; thresholds need pilot tuning."],
    ["Withhold rather than guess", "Red data quality: no values, no flags, excluded from peers. Amber: provisional.", "Gaps in trends vs unfair conversations."],
    ["Protect small numbers", "Counts 1–4 shown as \"<5\"; rates hidden when the numerator is 1–4 or the denominator under 5.", "Less detail for young stores; complementary suppression still open (U-39)."],
    ["Separate clinical and commercial", "Revenue per exam is restricted context, never a flag. Conversion for Optometry Partners stays an open decision (U-41).", "Partner transparency vs clinical independence."],
  ];
  J.forEach(([h, choice, trade], i) => {
    const x = 0.5 + i * 2.49, y = 2.7;
    card(s, x, y, 2.37, 4.15, i % 2 ? C.bg : C.tealLight);
    circleNum(s, x + 0.15, y + 0.15, i + 1);
    T(s, h, { x: x + 0.65, y: y + 0.13, w: 1.62, h: 0.62, fontSize: 13.5, bold: true, fontFace: HF, valign: "middle" });
    T(s, [{ text: "Choice", options: { bold: true, color: C.teal, breakLine: true } }, { text: choice, options: {} }], { x: x + 0.15, y: y + 0.9, w: 2.08, h: 1.95, fontSize: 12 });
    T(s, [{ text: "Trade-off", options: { bold: true, color: C.orangeText, breakLine: true } }, { text: trade, options: {} }], { x: x + 0.15, y: y + 2.85, w: 2.08, h: 1.2, fontSize: 11.5 });
  });
  tag(s, 10.9, 0.36, "ILLUSTRATIVE");
  source(s, "Rules: KPI dictionary v0.2 and exception rule set v0.2 (Phases 6 and 13), all illustrative. Full catalogue, dictionary and traceability: Appendix A4, A5, A7.");
  s.addNotes("The requirements chain is traceable from seven objectives to twenty-four UAT scenarios. Rather than list them, here are the five judgments that do most of the work. First, compare like with like — same maturity cohort and format as at each week — and accept that some young stores will have no peer comparison rather than an unfair one. Second, flags are areas to investigate: rule (a) compares with peers, rule (b) with the store's own recent history, and the text says which. Third, when data quality is Red the product withholds values and flags instead of guessing. Fourth, small counts are protected: a count from one to four shows as less than five, and a rate is hidden if it would reveal that count. Fifth, clinical and commercial views stay separate: revenue is restricted context, and whether Optometry Partners see conversion is an open decision, not something I have decided for Specsavers.");
}

/* =========================================================== SLIDE 6 — Data architecture */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 6, "Assumed data architecture, governance and quality", "Aggregate before reporting: a privacy boundary by design");
  tag(s, 10.5, 0.36, "ASSUMPTION");
  const srcs = ["Store master", "Scheduling", "PMS / EMR", "Point of sale", "Order management", "Marketing / recall", "Finance"];
  srcs.forEach((t, i) => {
    card(s, 0.5, 1.55 + i * 0.5, 1.9, 0.42, C.tealLight);
    T(s, t, { x: 0.5, y: 1.6 + i * 0.5, w: 1.9, h: 0.32, fontSize: 11.5, align: "center", valign: "middle" });
  });
  T(s, "Generic source categories", { x: 0.5, y: 5.08, w: 1.9, h: 0.25, fontSize: 10, color: C.muted, align: "center" });
  [[2.7, "Raw landing", "Immutable extracts and load metadata · restricted"], [4.75, "Standardise and link", "Conform store_id · pseudonymise · exam↔purchase linkage · restricted"]].forEach(([x, h, b]) => {
    card(s, x, 2.1, 1.85, 1.9, C.bg, C.line);
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: b, options: { fontSize: 11, color: C.muted } }], { x: x + 0.12, y: 2.22, w: 1.62, h: 1.7, fontSize: 12.5 });
  });
  s.addShape(pres.shapes.LINE, { x: 6.85, y: 1.5, w: 0, h: 3.1, line: { color: C.orange, width: 2.5, dashType: "dash" } });
  T(s, "PRIVACY BOUNDARY\nstore-week aggregates only", { x: 5.95, y: 4.66, w: 1.8, h: 0.5, fontSize: 10, bold: true, color: C.orangeText, align: "center" });
  [[7.05, "Aggregated zone", "Store-week facts · store-level KPI, peer and flag tables computed once"], [9.05, "Semantic model", "Selected-week aggregates · RLS · OLS on a revenue table"], [11.05, "3 report pages", "Network · Benchmarking · Diagnostic and data quality"]].forEach(([x, h, b], i) => {
    card(s, x, 2.1, 1.78, 1.9, i === 2 ? C.teal : C.tealLight);
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: b, options: { fontSize: 11, color: i === 2 ? "DDEFEC" : C.muted } }], { x: x + 0.12, y: 2.22, w: 1.55, h: 1.7, fontSize: 12.5, color: i === 2 ? C.white : C.ink });
  });
  [2.45, 4.6, 8.85, 10.85].forEach((x) => s.addShape(pres.shapes.RIGHT_ARROW, { x, y: 2.9, w: 0.24, h: 0.3, fill: { color: C.grey }, line: { type: "none" } }));
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.63, y: 2.9, w: 0.4, h: 0.3, fill: { color: C.orange }, line: { type: "none" } });

  const cols = [
    ["Data-quality checkpoints", ["Completeness and freshness per source", "Opening-date and store-code checks", "Arithmetic invariants", "Privacy scan blocks publishing"]],
    ["Master data and ownership", ["Opening date → Business Development (to confirm)", "Converted or relocated stores flagged (open, TQ-12)", "Effective-dated region and format", "User-to-store access mapping"]],
    ["Governance and privacy", ["No identifiers, diagnoses or individual performance", "Revenue in a separate table secured with OLS", "Anonymous peers; minimum group of 5", "Versioned KPIs, rules and prompts"]],
  ];
  cols.forEach(([h, items], i) => {
    const x = 0.5 + i * 4.15;
    card(s, x, 5.35, 4.0, 1.57, C.bg);
    T(s, h, { x: x + 0.15, y: 5.43, w: 3.7, h: 0.3, fontSize: 12.5, bold: true, color: C.teal });
    T(s, bullets(items, { space: 1 }), { x: x + 0.15, y: 5.76, w: 3.75, h: 1.12, fontSize: 11 });
  });
  card(s, 2.7, 4.15, 3.1, 1.05, C.orangeLight);
  T(s, [{ text: "Prototype lesson: ", options: { bold: true, color: C.orangeText } }, { text: "compute windows, peers and flags once upstream; the report only aggregates, so one rule set also works under RLS.", options: {} }], { x: 2.85, y: 4.22, w: 2.85, h: 0.95, fontSize: 11 });
  source(s, "No Specsavers platforms or schemas are asserted; postings reference PMS/EMR, POS, ERP, Power BI, SQL and Databricks as categories (EV-09). Model detail: Appendix A6.");
  s.addNotes("This is an assumed, generic architecture — I have not named any Specsavers platform. The key choice is a privacy boundary: patient-level linkage, such as connecting an exam to an eyewear purchase, happens only in restricted upstream zones, and only store-week aggregates reach reporting. Building the prototype taught me a second principle: calculate rolling windows, peer groups and exception flags once, upstream, and let the report only aggregate. That keeps one implementation of the rules — my Python engine and the dashboard logic are reconciled by tests — and it works under row-level security, because each store's row already carries its peer statistics. Revenue sits in its own table so object-level security can hide it from roles that should not see it. Converted or relocated stores are an open master-data question.");
}

/* =========================================================== SLIDE 7 — Demonstration */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 7, "Demonstration on synthetic data", "What a regional manager would see this week");
  tag(s, 9.9, 0.36, "SYNTHETIC");
  T(s, "Regional Overview · Atlantic (simulated role view) · week of 17 Aug 2026", { x: 0.5, y: 1.38, w: 7.9, h: 0.28, fontSize: 12, bold: true, color: C.teal });
  const a = image(s, "deck-rrm-cards.png", 0.5, 1.72, 7.9, 1.9);
  const y2 = 1.72 + a.h + 0.28;
  const hAvail = 6.88 - (y2 + 0.32);
  T(s, "Funnel · SYN-014 · 4 weeks ending 17 Aug 2026", { x: 0.5, y: y2, w: 4.2, h: 0.28, fontSize: 12, bold: true, color: C.teal });
  const f = image(s, "deck-p3-funnel-card.png", 0.5, y2 + 0.32, 4.2, hAvail);
  const x3 = 0.5 + f.w + 0.3;
  T(s, "Rule (b) explanation · SYN-005 · week of 25 May 2026", { x: x3, y: y2, w: 8.4 - x3, h: 0.28, fontSize: 12, bold: true, color: C.teal });
  image(s, "deck-p3-rule-b.png", x3, y2 + 0.32, 8.4 - x3, hAvail);

  card(s, 8.7, 1.38, 4.13, 5.5, C.bg);
  T(s, "Walkthrough", { x: 8.9, y: 1.48, w: 3.7, h: 0.35, fontSize: 16, bold: true, fontFace: HF });
  const steps = [
    ["Scope first", `The Atlantic manager sees ${ATW.stores} stores and ${ATW.completed_exams} exams; the banner shows ${ATW.amber_store_weeks} Amber because both Amber stores are elsewhere.`],
    ["One shared pattern", `SYN-025 to SYN-028 are flagged on on-time and turnaround. Atlantic turnaround ${R4.Atlantic.turnaround.toFixed(1)} days vs ${Math.min(...otherTurn).toFixed(1)}–${Math.max(...otherTurn).toFixed(1)} elsewhere (last 4 weeks) → one Supply Chain conversation.`],
    ["Fair for young stores", `SYN-014 has ramp index ${Math.round(syn014.ramp.i)} against ${syn014.ramp.n} same-age peers: on track despite low volume.`],
    ["Trust gate", "SYN-022's Red week (25 May 2026) shows no values and no flags, only a data-quality prompt."],
    ["Own-trend rule", "SYN-005's conversion is 15%+ below its own baseline (11 May – 8 Jun 2026) — an area to investigate, not a cause."],
  ];
  steps.forEach(([h, b], i) => {
    const y = 1.95 + i * 0.98;
    circleNum(s, 8.9, y, i + 1, i === 3 ? C.red : C.teal);
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: b, options: {} }], { x: 9.42, y: y - 0.04, w: 3.3, h: 0.95, fontSize: 11 });
  });
  source(s, "SYNTHETIC DATA: 30 fictional stores × 26 weeks; unrelated to Specsavers results. Screens from dashboard-mockup.html. Roles are simulated, not secured. Periods as labelled.");
  s.addNotes(`This is the prototype, running on my synthetic data, as a regional manager in the Atlantic region would see it in the week of 17 August 2026. Step one: scope comes first — every card, chart and the data-quality banner count only the ${ATW.stores} Atlantic stores; the network's two Amber stores are outside the region, so the banner shows zero. Step two: four Atlantic stores are flagged on both on-time and turnaround against comparable stores, and the region's turnaround is ${R4.Atlantic.turnaround.toFixed(1)} days over the last four weeks against about six elsewhere, so the right action is one conversation with Supply Chain rather than four store conversations. Step three: SYN-014, a young grocery-hosted store, looks small on volume but its ramp index is about 100 against stores at the same age. Step four: for a week with Red data quality the product shows no values and no flags. Step five: SYN-005 is flagged by the own-trend rule, and the explanation says so rather than implying a peer difference. The role switch is a simulated view; the page embeds all synthetic data and is not security.`);
}

/* =========================================================== SLIDE 8 — MVP, UAT and testing */
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  header(s, 8, "MVP plan, UAT and what was actually tested", "A three-page pilot, and a prototype tested before any user sees it");
  card(s, 0.5, 1.5, 12.33, 0.95, C.tealLight);
  T(s, [{ text: "MVP: ", options: { bold: true, color: C.teal } },
        { text: "three pages · store-week aggregates · 12 governed KPIs · like-for-like peers · non-causal prompts · visible data quality · role-based access. Pilot: 2–3 Regional Retail Managers and 12–16 opt-in stores in two regions. Excludes patient-level data, profitability, forecasting and PC Optimum analytics.", options: {} }],
    { x: 0.7, y: 1.58, w: 11.95, h: 0.82, fontSize: 12.5 });
  const tl = [["Sprint 0", 1, C.grey], ["Sprints 1–3 build", 6, C.teal2], ["UAT", 1, C.orangeText], ["4-week pilot → evaluate", 4, C.teal]];
  let wk = 0; const unit = 6.0 / 12;
  T(s, "Illustrative 12-week build-to-pilot plan", { x: 0.5, y: 2.65, w: 6, h: 0.3, fontSize: 13, bold: true, fontFace: HF });
  tl.forEach(([lab, len, col]) => {
    s.addText(lab, { isTextBox: true, shape: pres.shapes.RECTANGLE, x: 0.5 + wk * unit, y: 3.0, w: len * unit - 0.03, h: 0.55, fill: { color: col }, color: C.white, fontSize: len > 2 ? 11 : 9, bold: true, align: "center", valign: "middle", margin: 0, fontFace: BF });
    wk += len;
  });
  tag(s, 4.75, 2.68, "ILLUSTRATIVE");
  T(s, bullets(["10 user stories with Given/When/Then and negative scenarios", "24 UAT scenarios · 7 reconciliation · 10 access · 8 accessibility checks", "Sign-off order: privacy → reconciliation → stories → business → release"], { space: 5 }), { x: 0.5, y: 3.75, w: 6.0, h: 1.3, fontSize: 12.5 });
  card(s, 0.5, 5.2, 6.0, 1.7, C.orangeLight);
  tag(s, 0.7, 5.32, "NOT EXECUTED");
  T(s, "UAT with business users, reconciliation to control totals, security testing, usability and accessibility audits have not happened. They are the plan for an internal team, not results.", { x: 0.7, y: 5.68, w: 5.6, h: 1.15, fontSize: 12.5 });

  card(s, 6.85, 2.65, 5.98, 4.25, C.bg);
  T(s, "What I built and tested (prototype, synthetic data)", { x: 7.05, y: 2.75, w: 5.6, h: 0.35, fontSize: 14, bold: true, fontFace: HF });
  const facts = [[TESTS.checks, "structural and seeded-pattern data checks"], [TESTS.py, "calculation regression tests (Python)"], [TESTS.js, "logic tests, incl. Python ↔ JavaScript reconciliation"], [TESTS.ui, "rendered-page checks: 4 roles, 3 pages, 5 widths, keyboard"]];
  facts.forEach(([n, l], i) => {
    const x = 7.05 + (i % 2) * 2.85, y = 3.2 + Math.floor(i / 2) * 1.3;
    card(s, x, y, 2.7, 1.18, C.white, C.line);
    T(s, n, { x: x + 0.1, y: y + 0.08, w: 2.5, h: 0.5, fontSize: 24, bold: true, color: C.teal, align: "center", fontFace: HF });
    T(s, l, { x: x + 0.12, y: y + 0.6, w: 2.46, h: 0.55, fontSize: 10.5, align: "center" });
  });
  T(s, bullets([`Fixed before sign-off: regional scope, Red-week values, suppression via chart positions, dropped flag reasons (issue register: 45 items)`, "Automated checks on synthetic data and simulated roles — not UAT, not Power BI, not an accessibility audit"], { space: 4 }), { x: 7.05, y: 5.85, w: 5.6, h: 1.0, fontSize: 11.5 });
  source(s, "Timeline, pilot size and thresholds are illustrative proposals. Plans: Phase 11 and Appendix A9. Test evidence: evidence/test-report.md and evidence/test-results.md.");
  s.addNotes(`The MVP is deliberately small: three pages, store-week aggregates and twelve governed KPIs, piloted with two or three regional managers and twelve to sixteen opt-in stores within an illustrative twelve weeks. On the left is the plan for an internal team — stories, twenty-four UAT scenarios and a sign-off order with privacy first. None of that has been executed, and I label it that way. On the right is what I actually did: ${TESTS.checks} data checks, ${TESTS.py} calculation tests, ${TESTS.js} logic tests that reconcile the dashboard's JavaScript against the Python engine, and ${TESTS.ui} rendered-page checks across simulated roles, pages, screen widths and real key presses. Testing found real defects in my first prototype — the regional view used network figures, Red weeks still showed values, and a chart revealed suppressed counts — and I fixed and regression-tested them. These are prototype checks on synthetic data, not user acceptance.`);
}

/* =========================================================== SLIDE 9 — Limitations and next steps */
{
  const s = pres.addSlide();
  s.background = { color: C.teal };
  header(s, 9, "Limitations, validation needed and next steps", "Honest limits, and what I would ask first", true);
  const top = [
    ["Value to test (not monetised)", ["Pilot users rate comparisons as fair", "Stores needing attention found sooner", "Flags get a named follow-up owner", "Data quality visible before action"]],
    ["Limitations", ["Public, largely company-authored sources", "Synthetic data; roles simulated, not secured", "No Power BI build; DAX unexecuted", "No UAT, usability study or accessibility audit"]],
    ["Open decisions I did not make", ["U-38: can managers see other regions?", "U-39: is complementary suppression needed?", "U-41: should Optometry Partners see conversion?", "Opening dates for converted or relocated stores"]],
  ];
  top.forEach(([h, items], i) => {
    const x = 0.5 + i * 4.15;
    card(s, x, 1.5, 4.0, 2.75, C.tealCard);
    T(s, h, { x: x + 0.18, y: 1.6, w: 3.7, h: 0.35, fontSize: 14, bold: true, color: C.white, fontFace: HF });
    T(s, bullets(items, { space: 4 }), { x: x + 0.18, y: 2.02, w: 3.7, h: 2.15, fontSize: 12.5, color: "E4F2F0" });
  });

  card(s, 0.5, 4.4, 4.9, 2.5, C.tealDark);
  T(s, "First steps inside the business", { x: 0.7, y: 4.5, w: 4.5, h: 0.35, fontSize: 14, bold: true, color: C.white, fontFace: HF });
  T(s, bullets(["1. Review today's reports; interview managers and partners", "2. Agree KPI definitions, owners and peer rules", "3. Confirm data access, store crosswalk and linkage custody", "4. Privacy review; test the prototype with 5+ users"], { bullet: false, space: 5 }), { x: 0.7, y: 4.9, w: 4.55, h: 1.95, fontSize: 12.5, color: "E4F2F0" });

  card(s, 5.55, 4.4, 7.28, 2.5, C.white);
  T(s, "Questions for Specsavers", { x: 5.75, y: 4.5, w: 6.9, h: 0.35, fontSize: 14, bold: true, color: C.teal, fontFace: HF });
  T(s, bullets([
    "How do teams judge today whether a new store is on track?",
    "Which event defines a store's opening date, and who owns it?",
    "How, and under whose custody, are exams and purchases connected?",
    "What peer-comparison principles would partners support?",
  ], { space: 5 }), { x: 5.75, y: 4.9, w: 6.9, h: 1.95, fontSize: 13 });
  source(s, "No financial ROI is claimed. Measures and thresholds are illustrative and need baselines and internal validation. Registers: Appendix A10; status of every feature: feature-status-matrix.md.", true);
  s.addNotes("I have not claimed any financial ROI. The value I would test is fairness, speed of finding stores that need attention, follow-up ownership and visible data quality. The limitations are real: public sources, synthetic data, simulated roles rather than security, no Power BI build, and no user testing or accessibility audit. Three policy decisions are deliberately left open because they belong to Specsavers — regional visibility, complementary suppression and whether Optometry Partners see conversion — and the prototype labels its assumptions for each. My first steps would be to validate that the problem exists, agree definitions and rules, confirm data access and privacy, and put the prototype in front of users.");
}

/* =========================================================== APPENDIX */
function appx(n, title) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  T(s, `APPENDIX ${n}`, { x: 0.5, y: 0.3, w: 5, h: 0.28, fontSize: 11, bold: true, color: C.teal, charSpacing: 1.5 });
  T(s, title, { x: 0.5, y: 0.56, w: 12.3, h: 0.6, fontSize: 24, fontFace: HF, bold: true });
  return s;
}
const link = (text, url) => ({ text: [{ text, options: { hyperlink: { url, tooltip: url }, color: C.teal, underline: { style: "sng" } } }], options: {} });

/* A1 Sources */
const SOURCES = [
  ["EV-01", "Loblaw — Specsavers to open 111 new optical locations in Loblaw grocery stores", "30 Jul 2025", "https://www.loblaw.ca/en/specsavers-to-open-111-new-optical-locations-in-loblaw-grocery-stores-across-canada/", "Read"],
  ["EV-02", "Specsavers appoints Jane Hoban as Managing Director (Newswire copy)", "11 Mar 2026", "https://www.newswire.ca/news-releases/specsavers-appoints-jane-hoban-as-managing-director-to-lead-next-phase-of-canadian-expansion-873853796.html", "Canonical specsavers.ca page returned 403"],
  ["EV-03–05, 10, 11, 16", "Specsavers Canada partnership prospectus (PDF)", "Oct 2025", "https://specsaverspartnership.ca/wp-content/uploads/2025/10/vx250312_03_Specsavers-Canada-Prospectus_8-2677x5-8268_EN_x1a-trim-6.pdf", "Read (text extracted)"],
  ["EV-03, 15", "Specsavers partnership — Retail partnership page", "Accessed 13 Sep 2026", "https://specsaverspartnership.ca/retail-partnership/", "Read"],
  ["EV-06", "Specsavers surpasses 100-store milestone in Canada (Newswire copy)", "7 Feb 2024", "https://www.newswire.ca/news-releases/specsavers-surpasses-100-store-milestone-in-canada-805965501.html", "Canonical page 403"],
  ["EV-07", "Canada Eyecare Report 2025 — national vision gap (Newswire copy)", "9 Oct 2025", "https://www.newswire.ca/news-releases/specsavers-canada-highlights-national-vision-gap-one-third-of-canadians-are-overdue-for-an-eye-exam-848439853.html", "Commissioned survey"],
  ["EV-08, 17", "Loblaw — Specsavers joins PC Optimum program", "22 Jun 2026", "https://www.loblaw.ca/en/specsavers-joins-pc-optimum-program/", "Re-read 13 Sep 2026"],
  ["EV-09a", "Data Business Analyst, Burnaby (jid-13707)", "Live at access", "https://join.specsavers.com/ca/job/data-business-analyst-in-burnaby-british-columbia-canada-jid-13707", "Hiring evidence"],
  ["EV-09b", "Data Analyst, Burnaby (jid-13749)", "Live at access", "https://join.specsavers.com/ca/job/data-analyst-in-burnaby-british-columbia-canada-jid-13749", "Hiring evidence"],
  ["EV-09c", "Data Delivery Manager, Burnaby (jid-13764)", "Live at access", "https://join.specsavers.com/ca/job/data-delivery-manager-in-burnaby-british-columbia-canada-jid-13764", "Hiring evidence"],
  ["EV-09d", "Product Owner — PMS/EMR application, Burnaby (jid-13803)", "Live at access", "https://join.specsavers.com/ca/job/product-owner-in-burnaby-british-columbia-canada-jid-13803", "Hiring evidence"],
  ["EV-12", "Specsavers Canada candidate privacy policy", "Accessed 13 Sep 2026", "https://join.specsavers.com/ca/candidate-privacy-policy/", "Read"],
  ["EV-13", "Retail Regional Manager, Burnaby (jid-8803)", "Closed posting", "https://join.specsavers.com/ca/job/retail-regional-manager-in-burnaby-british-columbia-canada-jid-8803", "HTTP 404; snippet only"],
  ["EV-14", "Regional Training Manager, Burnaby (jid-3691)", "Closed posting", "https://join.specsavers.com/ca/job/regional-training-manager-in-burnaby-british-columbia-canada-jid-3691", "HTTP 404; snippet only"],
  ["Power BI", "Microsoft Learn — Set and use date tables in Power BI Desktop", "Accessed 13 Sep 2026", "https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables", "Design reference"],
  ["Power BI", "Microsoft Learn — Tabular model object-level security", "Accessed 13 Sep 2026", "https://learn.microsoft.com/en-us/analysis-services/tabular-models/object-level-security?view=sql-analysis-services-2025", "Design reference"],
];
{
  const s = appx("A1", "Sources (accessed 13 September 2026) — titles are links");
  table(s, [["Evidence", "Source (select to open)", "Date", "Access note"], ...SOURCES.map(([id, t, d, u, note]) => [id, link(t, u), d, note])],
    { x: 0.5, y: 1.3, w: 12.33, colW: [1.45, 6.9, 1.7, 2.28], fontSize: 9.5, rowH: 0.33 });
  s.addNotes("Full source references:\n" + SOURCES.map(([id, t, d, u, note]) => `${id} — ${t} (${d}). ${u} — ${note}.`).join("\n") +
    "\nWhere specsavers.ca pages blocked automated access, I verified the same releases on Newswire or Loblaw and recorded both URLs in evidence-log.md.");
}

/* A2 Evidence log */
{
  const s = appx("A2", "Evidence log — facts, inferences and corrections");
  table(s, [
    ["ID", "Verified claim (summary, dated)", "Class", "Correction / note"],
    ["EV-01", "30 Jul 2025: 111 in-grocery locations announced; network projected above 260; six new provinces or territories", "Fact", "Announcement and projection, not outcome"],
    ["EV-02", "11 Mar 2026: more than 270 stores; more than 130 opened in 2025; \"number one\" ambition", "Company statement", "Cite as \"reported Mar 2026\""],
    ["EV-17", "22 Jun 2026: the 111 in-grocery locations opened in 2025; 270+ locations, nine provinces and one territory", "Fact", "Added in repair pass; completes EV-01"],
    ["Inference", "≈ half of stores opened in 2025 (130+ of 270+)", "Inference", "Author's arithmetic on lower bounds"],
    ["EV-03/04", "Optometry and retail corporations; owned per provincial regulations", "Fact / statement", "Prospectus is the citation"],
    ["EV-05", "Nine support services incl. patient recall and patient-record systems", "Fact", "Training and recruitment separate"],
    ["EV-06", "7 Feb 2024: 100th store; 20% under six months old", "Historical", "Revenue figures not verified"],
    ["EV-07", "1 in 3 overdue; 51% cost; 61% coverage misunderstanding", "Commissioned research", "\"or never\" wording removed"],
    ["EV-08", "PC Optimum at all locations, 10 points per $1 (22 Jun 2026)", "Fact", "Excluded from MVP"],
    ["EV-09", "Data postings: Power BI, SQL, Databricks; PMS/EMR product owner", "Hiring evidence", "Shows categories, not architecture"],
    ["EV-11", "Prospectus shows 151 Canadian stores (2024/25)", "Historical", "Stale — model only"],
    ["EV-12", "Named Privacy Officer; PIPA/PIPEDA referenced", "Fact", "Team structure unknown"],
    ["EV-13/14", "Retail Regional Manager; Regional Training Manager (closed)", "Indirect", "Low confidence"],
    ["EV-15/16", "Partnership Advisory Committee; support-office roles", "Company statement", "Remit unknown"],
  ], { x: 0.5, y: 1.3, w: 12.33, colW: [1.0, 6.3, 1.85, 3.18], fontSize: 9.5, rowH: 0.37 });
  s.addNotes("The evidence log separates facts, company statements, commissioned research, hiring evidence and my own inferences. The repair pass added EV-17, which confirms that the 111 in-grocery locations announced in July 2025 opened during 2025, and it dates every network count.");
}

/* A3 Stakeholders */
{
  const s = appx("A3", "Stakeholder analysis — evidence status, influence and roles");
  table(s, [
    ["ID", "Stakeholder", "Evidence", "Infl.", "Int.", "Requirements, approval and UAT role (proposed)"],
    ["SH-01", "Retail Partners", "Confirmed", "High*", "High", "Store needs · endorsement via SH-14 · pilot testers"],
    ["SH-02", "Optometry Partners", "Confirmed", "High", "Med–High", "Clinical wording and privacy · consulted · clinic view tests"],
    ["SH-03", "Regional Retail Managers (title TBC)", "Assumed / indirect", "Med–High", "High", "Exception and workflow needs · core UAT testers"],
    ["SH-04", "Retail Operations leadership", "Function confirmed", "High", "High", "Sponsor (assumed) · peer rules · business sign-off"],
    ["SH-05", "Marketing", "Function confirmed", "Medium", "Medium", "Recall KPI owner · recall reconciliation"],
    ["SH-06", "Supply Chain", "Function confirmed", "Medium", "Medium", "Fulfilment KPI owner · fulfilment reconciliation"],
    ["SH-07", "Finance", "Function confirmed", "High", "Medium", "Revenue definitions · revenue reconciliation"],
    ["SH-08", "Product Owner (data)", "Role type confirmed", "High", "High", "Backlog and story acceptance · co-signs UAT"],
    ["SH-09", "Data Business Analyst", "Confirmed", "Medium", "High", "Elicitation, requirements, mapping, RTM · UAT lead"],
    ["SH-10/11", "Data Engineers · Visualization Analysts", "Confirmed", "Med–High", "High", "Feasibility, model, report build · defect fixes"],
    ["SH-12", "Data Delivery Manager", "Confirmed", "High", "High", "Release readiness · UAT gates"],
    ["SH-13", "Governance / Privacy / Security", "Privacy Officer confirmed", "High", "Med–High", "Privacy and access approval · witnesses access tests"],
    ["SH-14", "Partnership Advisory Committee", "Confirmed exists", "High", "Medium", "Comparison principles · endorsement"],
    ["SH-15", "Business Development / openings", "Function confirmed", "Medium", "High", "Opening-date master data owner (TBC)"],
    ["SH-16/17/18", "Clinical Services · System owners · Executive", "Indirect / confirmed", "Varies", "Varies", "Clinical wording · data access · informed"],
  ], { x: 0.5, y: 1.3, w: 12.33, colW: [1.0, 2.9, 2.05, 0.9, 0.9, 4.58], fontSize: 9.5, rowH: 0.33 });
  T(s, "*Collectively. RACI (19 activities) and the 8-stage engagement plan: phase-02-stakeholders.md. All roles are proposals; no stakeholder has reviewed them.", { x: 0.5, y: 6.85, w: 12.3, h: 0.4, fontSize: 9.5, color: C.muted });
  s.addNotes("Stakeholder evidence status is explicit — for example, the Privacy Officer role is publicly confirmed but a dedicated governance team is not.");
}

/* A4 Requirements catalogue */
{
  const s = appx("A4", "Requirements catalogue (summary)");
  T(s, "Business objectives", { x: 0.5, y: 1.3, w: 6, h: 0.3, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets(["BO-01 Fair like-for-like assessment (Must)", "BO-02 Surface stores earlier, esp. ramp-up (Must)", "BO-03 Trusted, governed KPIs (Must)", "BO-04 Better-targeted follow-up (Must)", "BO-05 Balanced access and commercial view (Should)", "BO-06 Privacy and confidentiality by design (Must)", "BO-07 Reduce manual effort — if validated (Could)"], { space: 2 }), { x: 0.5, y: 1.62, w: 6, h: 2.1, fontSize: 11.5 });
  T(s, "Business requirements", { x: 0.5, y: 3.75, w: 6, h: 0.3, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets(["BR-01 Network monitoring (M) · BR-02 Maturity-aware comparison (M)", "BR-03 Candidate factors to investigate (S) · BR-04 Governed KPIs (M)", "BR-05 Visible data quality (M) · BR-06 Partner information (M)", "BR-07 Regional patterns (S) · BR-08 Protect sensitive information (M)", "BR-09 Support action (M) · BR-10 → constraint CON-01", "BR-11 Access indicators (S) · BR-12 Reduce manual compilation (C)"], { space: 3 }), { x: 0.5, y: 4.07, w: 6, h: 2.4, fontSize: 11.5 });
  T(s, "Functional requirements", { x: 6.8, y: 1.3, w: 6, h: 0.3, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets(["MVP: FR-01 overview · FR-02 filters · FR-03 maturity · FR-04 peers · FR-05 drill-through · FR-06 exceptions · FR-07 definitions · FR-08 data quality · FR-10 access · FR-13 ramp-up · FR-14 funnel · FR-15 prompts · FR-16 small groups", "If low effort: FR-09 landing views · FR-11 exports · FR-12 persistent filters", "Deferred: FR-17 annotations · FR-18 action log", "Prototype status of each: feature-status-matrix.md (FR-10 simulated; FR-11 deferred)"], { space: 4 }), { x: 6.8, y: 1.62, w: 6.0, h: 2.45, fontSize: 11 });
  T(s, "Non-functional, data, privacy and security (targets illustrative)", { x: 6.8, y: 4.1, w: 6, h: 0.3, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets(["NFR-01–08: ≤5 s interactions · weekly refresh · 99% availability · WCAG 2.1 AA target · SUS ≥70 · 400-store scale · supportability · mobile", "DR-01–10: lineage · versioning · retention · completeness · freshness · store-week grain · store master · reconciliation · null vs zero · as-at-week cohort", "PR-01–08: no identifiers or diagnoses · peer floor 5 · small-count rule v0.2 · no individual performance · privacy review · partner confidentiality · synthetic non-production", "SR-01–08: least privilege · RLS · OLS · audit · export limits · recertification · SSO/MFA · environments (specified, not built)"], { space: 4 }), { x: 6.8, y: 4.42, w: 6.0, h: 2.5, fontSize: 10.5 });
  s.addNotes("Full statements, rationale, owners, measures and validation questions are in the Phase 3, 4 and 5 documents. The feature-status matrix shows which are implemented in the prototype, simulated, specified only or deferred.");
}

/* A5 KPI dictionary */
{
  const s = appx("A5", "KPI dictionary v0.2 (proposed definitions — not Specsavers definitions)");
  table(s, [
    ["ID", "KPI", "Formula (store-week; re-aggregated from sums)", "Proposed owner", "Key rule"],
    ["KPI-01", "Available capacity", "Σ bookable exam slots", "Retail Ops", "Excludes blocked or closed slots; null ≠ 0"],
    ["KPI-02", "Appointment utilization", "(Booked − cancelled) ÷ slots", "Retail Ops", "No-shows count as held"],
    ["KPI-03", "Attendance rate", "Completed ÷ (booked − cancelled)", "Retail Ops", "Unrecorded statuses shown, not hidden"],
    ["KPI-04", "Completed examinations", "Count of completed exam appointments", "Clinical Services", "No clinician dimension"],
    ["KPI-05", "Exam-to-purchase conversion", "Distinct exam-linked purchasers (≤30 days) ÷ completed", "Retail Ops", "Customers, not transactions; linkage upstream"],
    ["KPI-06", "Revenue per completed exam", "Net eligible eyewear revenue ÷ completed", "Finance", "Context only; restricted; negative weeks valid"],
    ["KPI-07", "Average order turnaround", "Σ (ready − placed days) ÷ orders ready", "Supply Chain", "Prototype assumes all placed orders ready"],
    ["KPI-08", "On-time fulfilment", "Ready by promised date ÷ orders placed", "Supply Chain", "Excludes cancelled orders"],
    ["KPI-09", "Recall-booking rate", "Recall bookings (≤30 days) ÷ recall contacts", "Marketing", "n/a before programme; 1–4 shown as <5"],
    ["KPI-10", "Store ramp index", "100 × store 4-week exams ÷ median of peers at same weeks since opening", "Retail Ops", "≥5 peers; trigger <80 for 4 weeks"],
    ["KPI-11", "Data completeness", "Mean of per-source received ÷ expected (equal weight)", "Governance", "≥98 Green · 90–98 Amber · <90 Red"],
    ["KPI-12", "Data freshness", "Current / Delayed / Stale by load age", "Data team", "Worst source wins; Stale withholds"],
  ], { x: 0.5, y: 1.3, w: 12.33, colW: [0.85, 2.15, 4.4, 1.55, 3.38], fontSize: 9.8, rowH: 0.42 });
  source(s, "All rates: 4 calendar weeks ending the selected week, ≥3 usable weeks, unavailable if the selected week is Red. Cohorts: New 0–26 · Developing 27–104 · Mature 105+ weeks. Change log: phase-06-kpi-dictionary.md.");
  s.addNotes("Each KPI has fifteen documented fields in the full dictionary. Version 0.2 clarifies the rolling window and Red-week rule, extends small-count suppression to rates with a small numerator, chooses one completeness method, and states two synthetic simplifications. No KPI IDs changed.");
}

/* A6 Data model */
{
  const s = appx("A6", "Conceptual data model — star schema with as-at-week cohort");
  tag(s, 11.3, 0.36, "ASSUMPTION");
  const dims = [["DIM_STORE", "store_id · format · host banner · opening date and type · effective dates", 0.5, 1.4], ["DIM_DATE", "contiguous daily calendar · week start · published flag", 9.33, 1.4], ["DIM_GEOGRAPHY", "province · region (effective-dated)", 0.5, 5.45], ["DIM_MATURITY_COHORT", "New / Developing / Mature / Unclassified · version", 9.33, 5.45]];
  dims.forEach(([h, b, x, y]) => {
    card(s, x, y, 3.5, 1.1, C.tealLight);
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: b, options: { fontSize: 10.5, color: C.muted } }], { x: x + 0.15, y: y + 0.1, w: 3.2, h: 0.95, fontSize: 12 });
  });
  const facts = [["FACT_APPOINTMENT", "store × week"], ["FACT_EXAMINATION", "store × week"], ["FACT_EXAM_CONVERSION", "store × exam week"], ["FACT_SALES_REVENUE", "store × transaction week"], ["FACT_ORDER_FULFILMENT", "store × placed week"], ["FACT_RECALL_CAMPAIGN", "store × contact week"], ["FACT_DATA_QUALITY", "store × week × source"]];
  facts.forEach(([h, g], i) => {
    const x = 4.3 + (i % 2) * 2.4, y = 2.55 + Math.floor(i / 2) * 0.72;
    card(s, x, y, 2.3, 0.64, C.teal);
    T(s, [{ text: h, options: { bold: true, breakLine: true } }, { text: g, options: { fontSize: 10 } }], { x: x + 0.1, y: y + 0.06, w: 2.1, h: 0.54, fontSize: 10.5, color: C.white });
  });
  T(s, "Cohort and geography are resolved as at each fact week, so a store can move from New to Developing mid-period. Conversion (exam week) and revenue (transaction week) are separate facts.", { x: 4.15, y: 1.45, w: 5.0, h: 1.0, fontSize: 11.5, italic: true, align: "center" });
  T(s, "Supporting: store-level KPI, peer and exception tables · ramp index · KPI dictionary · rule and prompt tables · user-store access (security only)", { x: 0.5, y: 6.7, w: 12.3, h: 0.35, fontSize: 11, color: C.muted, align: "center" });
  s.addNotes("Separate facts load and reconcile independently; the prototype flattens them into one store-week CSV. The repair pass split the earlier FACT_SALES into exam-week conversion and transaction-week revenue, because two independent weekly aggregates cannot share a row without defining its meaning. Source-to-target mapping (23 rows), checkpoints and master-data responsibilities are in phase-07-data-model-and-flow.md.");
}

/* A7 Traceability */
{
  const s = appx("A7", "Traceability matrix (summary) and gap findings");
  table(s, [
    ["BR", "FR", "KPI", "User stories", "UAT", "Release"],
    ["BR-01 Network monitoring", "FR-01, 02, 05, 09", "KPI-01–09", "US-01, US-02", "01, 02, 05, 14–16, 23", "MVP"],
    ["BR-02 Maturity comparison", "FR-03, 04, 13, 16", "KPI-04, 10", "US-03, US-10", "03, 04, 18, 22", "MVP"],
    ["BR-03 Candidate factors", "FR-04, 14, 15, (17)", "KPI-02, 03, 05, 07–09", "US-04", "06, 21, 24", "MVP"],
    ["BR-04 Governed KPIs", "FR-07", "KPI-01–12", "US-05", "07, 15–17", "MVP"],
    ["BR-05 Data quality", "FR-08", "KPI-11, 12", "US-06", "08, 15", "MVP"],
    ["BR-06 Partner information", "FR-04, 09, 10, 12", "KPI-02–06, 10", "US-03, 04, 07", "09, 19, 23, 24", "MVP"],
    ["BR-07 Regional patterns", "FR-02, 05, 06", "KPI-02, 05, 07, 08", "US-02", "02, 05, 17", "MVP (Should)"],
    ["BR-08 Protect information", "FR-10, 11, 16", "KPI-06, 09", "US-07, 08, 10", "09–12, 18", "MVP"],
    ["BR-09 Support action", "FR-06, 15, (18)", "KPI-02, 03, 05, 07, 10", "US-04", "06, 21", "MVP"],
    ["BR-10 → CON-01", "— by design", "—", "US-09", "20", "Constraint"],
    ["BR-11 Access indicators", "FR-01, 14", "KPI-03, 04, 09", "US-01, 04", "01, 06", "MVP"],
    ["BR-12 Manual compilation", "FR-11", "—", "US-08", "12", "Could"],
  ], { x: 0.5, y: 1.3, w: 7.9, colW: [2.1, 1.5, 1.45, 1.15, 1.0, 0.7], fontSize: 9.5, rowH: 0.42 });
  card(s, 8.6, 1.3, 4.23, 5.6, C.bg);
  T(s, "Gap findings (25 logged)", { x: 8.8, y: 1.4, w: 3.9, h: 0.32, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets([
    "BO-07 weakly supported: no Must-level requirement or baseline",
    "FR-12, FR-17, FR-18 have no user story",
    "KPI-01 and KPI-06 weakly tied to a decision",
    "US-02, US-10 not Ready until U-38 and U-39 are decided",
    "KPI-05 visibility for Optometry Partners open (U-41)",
    "Repair pass (RTM-18–25): the first prototype did not meet several traced requirements — scope, Red weeks, suppression, flag reasons — until fixed and tested",
  ], { space: 5 }), { x: 8.8, y: 1.8, w: 3.9, h: 5.0, fontSize: 11 });
  s.addNotes("I reported gaps rather than engineering a perfect matrix. The repair pass added a lesson: an ID-level traceability matrix can be complete while the product still fails the requirement, so behaviour tests are linked back to the requirement IDs.");
}

/* A8 Synthetic methodology */
{
  const s = appx("A8", "Synthetic-data methodology and validation");
  tag(s, 11.35, 0.36, "SYNTHETIC");
  card(s, 0.5, 1.3, 4.0, 5.6, C.bg);
  T(s, "Generation", { x: 0.7, y: 1.4, w: 3.6, h: 0.32, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets(["30 fictional stores (SYN-001–030), 26 weeks from 23 Feb 2026; 761 rows, 24 columns", "8 provinces, 4 synthetic regions, 3 formats; generic host banners", "Cohort as at each week; 3 stores open mid-window", "Ramp-up curve drives capacity, utilization and conversion", "Reproducible: seed 20260913 (byte-identical rerun tested)", "Simplifications: snapshot treated as final; all orders reach ready; completeness simulated; no converted stores"], { space: 4 }), { x: 0.7, y: 1.78, w: 3.65, h: 5.0, fontSize: 11 });
  card(s, 4.65, 1.3, 3.2, 5.6, C.tealLight);
  T(s, "Validation and tests", { x: 4.85, y: 1.4, w: 2.9, h: 0.32, fontSize: 13, bold: true, color: C.teal });
  T(s, TESTS.checks, { x: 4.85, y: 1.8, w: 2.9, h: 0.7, fontSize: 34, bold: true, color: C.teal, fontFace: HF });
  T(s, bullets(["Structure, keys, arithmetic, null semantics", "Each deliberate pattern tested", `${TESTS.py} calculation tests: windows, Red weeks, peers, suppression, rules, ramp`, `${TESTS.js} logic tests reconcile JavaScript with Python`, `${TESTS.ui} rendered-page checks`], { space: 3 }), { x: 4.85, y: 2.55, w: 2.9, h: 3.2, fontSize: 11 });
  T(s, "Issues fixed: 3 in the data, 4 in the calculation engine (repair pass)", { x: 4.85, y: 5.9, w: 2.85, h: 0.9, fontSize: 10.5, italic: true, color: C.muted });
  const p2 = P.P2_atlantic_turnaround;
  table(s, [
    ["Pattern", "Synthetic evidence (period)"],
    ["P1 New stores improve", `All ${P.P1_new_stores_improving.length} New-at-start stores improve utilization and exams (first vs last 4 weeks)`],
    ["P2 Regional turnaround", `Atlantic ${p2.atlantic_turnaround.toFixed(1)} vs ${p2.other_turnaround.toFixed(1)} days (all weeks); ${p2.atlantic_stores_above_network_store_median} of 6 above median`],
    ["P3 High demand, low attendance", `SYN-012 / SYN-019 ≈ ${pctf(P.P3_high_demand_low_attendance.stores["SYN-012"].utilization, 0)} utilization, ≈ ${pctf(P.P3_high_demand_low_attendance.stores["SYN-012"].attendance, 0)} attendance (all weeks)`],
    ["P4 Mature conversion decline", `SYN-005 ${pctf(P.P4_mature_declining_conversion.conv_weeks1_6)} → ${pctf(P.P4_mature_declining_conversion.conv_last8)} (weeks 1–6 vs last 8); exams flat`],
    ["P5 Data-quality warnings", "5 Amber and 4 Red store-weeks; Red weeks withheld, no flags"],
    ["P6 Cohort differences", `Exams per store-week ${Math.round(CK.New.exams_per_store_week)} / ${Math.round(CK.Developing.exams_per_store_week)} / ${Math.round(CK.Mature.exams_per_store_week)} (all weeks)`],
    ["Rule coverage", `${D.stage_flags_total} stage flags (${D.stage_flags_per_week_avg.toFixed(1)}/week); ramp index available ${Math.round(D.ramp_index_coverage * 100)}%; ${D.suppression.weekly_recall_bookings_1_to_4} weekly counts shown as <5`],
  ], { x: 8.0, y: 1.3, w: 4.83, colW: [1.7, 3.13], fontSize: 9.5, rowH: 0.66 });
  source(s, "Fictional data, unrelated to Specsavers stores, partners, patients or results. Files: data/synthetic_store_weekly.csv · data/validation-results.md · build/*.py · tests/");
  s.addNotes("The dataset is designed to test the rules — small peer groups, suppression, null versus zero, Red data weeks — not just to produce nice charts. The repair pass found four defects in my own calculation engine, fixed them in the engine rather than the outputs, and added regression tests for each.");
}

/* A9 UAT plan */
{
  const s = appx("A9", "UAT plan (summary) — a plan, not results");
  tag(s, 10.9, 0.36, "NOT EXECUTED");
  table(s, [
    ["Area", "Scenarios", "Expected results (synthetic test data)"],
    ["Core pages", "UAT-01–06, 22, 23", "Default latest week; ratio of sums; SYN-014 changes cohort 20 Jul 2026; SYN-025–028 flagged on on-time and turnaround"],
    ["Definitions and data quality", "UAT-07, 08", "Dictionary version shown; SYN-022 Red weeks withheld in the week itself, no flags, excluded from peers"],
    ["Security and privacy", "UAT-09–12, 18", "Partner sees only SYN-014; Atlantic manager sees 6 stores, 545 exams, no out-of-region names; <5 rule"],
    ["Reconciliation", "UAT-15–17", "Exams ±0.5% · revenue ±1.0% · orders ±0.5% vs control totals (illustrative)"],
    ["Quality attributes", "UAT-13, 14, 19, 24", "WCAG checks; ≤5 s interactions; persistent filters; 80% complete triage task ≤3 min"],
    ["Interpretation and sign-off", "UAT-20, 21", "0 prohibited causal terms; ≥80% comprehension; sign-off order recorded"],
  ], { x: 0.5, y: 1.3, w: 8.0, colW: [1.8, 1.5, 4.7], fontSize: 10, rowH: 0.66 });
  table(s, [
    ["Level", "Status"],
    ["Data and pattern checks", `Executed (${TESTS.checks})`],
    ["Calculation and reconciliation", `Executed (${TESTS.py} + ${TESTS.js})`],
    ["Rendered-page regression", `Executed (${TESTS.ui})`],
    ["Power BI (DAX, RLS, OLS)", "Not executed"],
    ["UAT with business users", "Not executed"],
  ], { x: 8.7, y: 1.3, w: 4.13, colW: [2.2, 1.93], fontSize: 10, rowH: 0.45 });
  card(s, 8.7, 4.2, 4.13, 2.7, C.bg);
  T(s, "Entry and exit", { x: 8.9, y: 4.3, w: 3.8, h: 0.32, fontSize: 13, bold: true, color: C.teal });
  T(s, bullets(["Entry: stories done · test environment · role accounts · privacy review · no Sev 1", "Exit: 100% Must scenarios run · ≥95% pass · 0 Sev 1–2 · access tests witnessed", "Pilot: 4 weeks · office hours · pulse surveys · evaluation workshop"], { space: 5 }), { x: 8.9, y: 4.68, w: 3.8, h: 2.15, fontSize: 11 });
  s.addNotes("Expected results reference deterministic synthetic test cases, so every scenario is reproducible. The status table separates what I executed on the prototype from what only an internal team can execute.");
}

/* A10 Risks and assumptions */
{
  const s = appx("A10", "Risk and assumption registers (highlights)");
  table(s, [
    ["ID", "Risk", "P×I", "Mitigation", "Early warning"],
    ["R-01", "Conflicting KPI definitions", "16 High", "Domain workshops; governed dictionary", "Two or more definitions surface"],
    ["R-02", "Unfair store comparisons", "15 High", "Cohort × format peers; comprehension tests", "Fairness score <80%"],
    ["R-04", "Missing or delayed data", "16 High", "Checkpoints; withholding; publish gate", "Red store-weeks >5%"],
    ["R-11", "Incorrect causal interpretation", "16 High", "Rule-specific text; UAT-21; training", "Flags quoted as causes"],
    ["R-14", "Source-system integration", "16 High", "Sprint 0 access; ready sources first", "No access by end of Sprint 0"],
    ["R-15", "Master-data inconsistency", "16 High", "Crosswalk; opening-date owner", "Unmapped store codes"],
    ["R-05", "Privacy exposure", "10 (critical)", "Privacy boundary; PR-01–04; review", "Identifier-like fields in scan"],
    ["R-22", "Prototype mistaken for secured or production-ready", "9 Medium", "Simulated-role note; status matrix", "Prototype called \"secured\" or \"tested with users\""],
  ], { x: 0.5, y: 1.3, w: 7.7, colW: [0.6, 2.0, 0.95, 2.35, 1.8], fontSize: 9.5, rowH: 0.52 });
  card(s, 8.4, 1.3, 4.43, 5.6, C.bg);
  T(s, "Lowest-confidence assumptions", { x: 8.6, y: 1.4, w: 4.1, h: 0.32, fontSize: 13, bold: true, color: C.amber });
  T(s, bullets([
    "A-06 Aggregated exam counts can be shown to retail users",
    "A-17 Partnership Advisory Committee suits endorsement",
    "A-19 Manual compilation exists today",
    "A-26 Finance can provide weekly control totals",
    "A-31 / A-33 Exam↔purchase linkage without exposing identifiers",
    "A-46 Optometry Partners see conversion (demonstration only, U-41)",
  ], { space: 5 }), { x: 8.6, y: 1.8, w: 4.1, h: 3.4, fontSize: 11 });
  T(s, "Registers: 22 risks · 47 assumptions · 9 constraints · 12 dependencies · 42 open questions (phase-10-raid-registers.md).", { x: 8.6, y: 5.4, w: 4.1, h: 1.3, fontSize: 11, color: C.muted });
  s.addNotes("Six risks rate High. The lowest-confidence assumptions are the ones I would test first in discovery. The repair pass added R-22: a polished prototype can be mistaken for a secured or user-tested product, so every page and document states its status.");
}

pres.writeFile({ fileName: OUT }).then((f) => console.log("Wrote " + f + (TESTS.overall ? "" : " (warning: last test run not recorded as PASS)")));
