/*
 * Capture "after" screenshots of the repaired dashboard (evidence/screenshots/after) and cropped images for the deck
 * (build/deck_images). Uses headless Microsoft Edge through tests/cdp.js. SYNTHETIC data only.
 * Run: node build/capture_screenshots.js   (after python build/build_mockup.py)
 */
const path = require("path");
const fs = require("fs");
const { launch, fileUrl, sleep } = require("../tests/cdp");

const ROOT = path.join(__dirname, "..");
const PAGE = path.join(ROOT, "dashboard-mockup.html");
const AFTER = path.join(ROOT, "evidence", "screenshots", "after");
const DECK = path.join(__dirname, "deck_images");

const SHOTS = [
  // name, width, height, hash, { fullPage | clipSelector }
  ["p1-1440", 1440, 1000, "role=ROL&page=p1", { fullPage: true }],
  ["p1-375-mobile", 375, 812, "role=ROL&page=p1", { fullPage: true }],
  ["p1-rrm-atlantic-1440", 1440, 1000, "role=RRM&page=p1", { fullPage: true }],
  ["p3-SYN-014-funnel-1440", 1440, 1000, "role=ROL&page=p3&store=SYN-014", { fullPage: true }],
  ["p3-SYN-012-1440", 1440, 1000, "role=ROL&page=p3&store=SYN-012", { fullPage: true }],
  ["p2-SYN-029-1440", 1440, 1000, "role=ROL&page=p2&store=SYN-029", { fullPage: true }],
  ["p3-SYN-022-red-week-1440", 1440, 1000, "role=ROL&page=p3&store=SYN-022&week=2026-05-25", { fullPage: true }],
  ["p3-SYN-005-rule-b-1440", 1440, 1000, "role=ROL&page=p3&store=SYN-005&week=2026-05-25", { fullPage: true }],
  ["p3-SYN-014-375-mobile", 375, 812, "role=OP&page=p3&store=SYN-014", { fullPage: true }],
  ["p2-640-zoom200", 640, 800, "role=RRM&page=p2&store=SYN-027", { fullPage: true }],
];
const DECK_SHOTS = [
  ["deck-p1-cards", 1280, 900, "role=ROL&page=p1", "#kpiCards"],
  ["deck-p1-exceptions", 1280, 900, "role=ROL&page=p1", "#excTable"],
  ["deck-p2-ramp", 1280, 900, "role=ROL&page=p2&store=SYN-014", "#ramp"],
  ["deck-p3-funnel", 1280, 900, "role=ROL&page=p3&store=SYN-014", ".grid.two.wide"],
  ["deck-p3-funnel-card", 1280, 900, "role=ROL&page=p3&store=SYN-014", ".grid.two.wide > .card:first-child"],
  ["deck-p3-rule-b", 1280, 900, "role=ROL&page=p3&store=SYN-005&week=2026-05-25", "#prompts"],
  ["deck-rrm-cards", 1280, 900, "role=RRM&page=p1", "#kpiCards"],
];

(async () => {
  const browser = await launch();
  try {
    for (const [name, w, h, hash, opt] of SHOTS) {
      const page = await browser.newPage();
      await page.viewport(w, h, 1);
      await page.goto(fileUrl(PAGE, hash));
      await sleep(300);
      await page.screenshot(path.join(AFTER, name + ".png"), Object.assign({ width: w }, opt));
      page.close();
      console.log("after:", name);
    }
    for (const [name, w, h, hash, sel] of DECK_SHOTS) {
      const page = await browser.newPage();
      await page.viewport(w, h, 2);
      await page.goto(fileUrl(PAGE, hash));
      await sleep(300);
      await page.eval("document.querySelectorAll('details').forEach((d) => { d.open = false; })");
      await page.screenshot(path.join(DECK, name + ".png"), { clipSelector: sel, width: w, scale: 2 });
      page.close();
      console.log("deck:", name);
    }
  } finally { await browser.close(); }
  console.log("Screenshots written to", path.relative(ROOT, AFTER), "and", path.relative(ROOT, DECK));
})().catch((e) => { console.error(e); process.exit(1); });
