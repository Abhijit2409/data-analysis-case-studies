# Methodology

How the peer groups, the measurement window, the exception rules and the synthetic dataset were designed — and the
judgement calls behind each one.

Everything here is an outside-in design built on public information. Where I made an interpretation or picked a
threshold, it is labelled as mine. No figure in this package describes actual Specsavers performance.

---

## 1. Evidence and what it supports

| | |
|---|---|
| Sources | Company and partner press releases, the corporate site, publicly posted job advertisements, provincial regulatory pages |
| Access checked | Each source re-read and its HTTP status recorded on 2026-09-13 |
| Logged in | [`phases/evidence-log.md`](phases/evidence-log.md) — 17 evidence items, each with date, status and what it does not support |
| Not used | No internal documents, systems, data or conversations |

Three rules govern how that evidence is used:

- **Company statements are dated, never presented as "today".** "More than 270 locations" is reported as of March 2026
  and again in June 2026, not as a current network size.
- **My arithmetic is labelled as mine.** "Roughly half the network was under about fifteen months old" is an inference
  from two published lower bounds, not a company statement.
- **An announcement is not an outcome.** The July 2025 announcement of 111 in-grocery locations is kept separate from
  the June 2026 statement that they opened.

## 2. The hypothesis, stated as a hypothesis

> A geographically diverse, partner-owned network with a wide spread of store ages **may** need a consistent and fair way
> to compare each store with genuinely comparable stores, rather than with the network average.

It rests on four mechanisms that the public record makes plausible — a wide maturity mix, structural diversity across
provinces and host formats, separate clinical and retail entities at each location, and measures that span both domains.
Every one of them would need internal validation. Nothing in this study shows that current reporting has a problem.

## 3. Maturity cohorts: the core design choice

A store is banded by its age in weeks **as at the reporting week**, so a store moves between cohorts as it matures:

| Cohort | Weeks since opening |
|---|---|
| New | 0–26 |
| Developing | 27–104 |
| Mature | 105+ |

Bands, not a continuous age adjustment, because a band is explainable to a store partner in one sentence and does not
imply a fitted model of how stores should grow. The 26/104 boundaries are illustrative proposals; the phase documents
carry them as an open question for stakeholders, and the prototype recomputes everything if they change.

## 4. Peer groups, and what happens when there aren't enough peers

```
peers = other stores in the same maturity cohort AND the same store format, with a reportable value this week
```

- If fewer than 5 such peers exist, fall back to the **whole cohort across formats** — and say so on screen with the
  peer count.
- If the fallback still has fewer than 5, **suppress the comparison** rather than show a thin one, and leave the store's
  own values visible.
- Peer quantiles use linear interpolation, and a store is never its own peer.
- Red (unusable) store-weeks are excluded from every peer group.

The floor of 5 is both a statistical judgement and a privacy one: with a small group, a store partner could infer a
named competitor's numbers from the median.

## 5. The measurement window

> **Four calendar weeks ending at the selected reporting week, requiring at least three usable weeks, with the selected
> week itself usable.**

- The window is built from a contiguous weekly calendar, not from "the last four rows that exist", so a missing week is
  a gap rather than a silent substitution.
- "Usable" means present and not Red.
- Rates are a **ratio of sums** over the window (total numerator ÷ total denominator), never a mean of weekly rates —
  the two differ whenever weekly volumes differ, and the mean of rates over-weights quiet weeks.
- Fewer than three usable weeks produces `insufficient_history`, not a partial average.

## 6. Exception rules: two rules, both explained on screen

| Rule | Fires when | What it means |
|---|---|---|
| **(a) Against peers** | The 4-week value is below the peer 25th percentile **and** at least 10% worse than the peer median | This store sits low in its own comparison group |
| **(b) Against itself** | The 4-week value is 15% or more worse than the store's own 8-week baseline (the 8 weeks before the window, at least 6 usable) for **3 consecutive weeks** | This store has moved away from its own recent normal |

Design decisions worth stating plainly:

- **Rule (b) exists so that a store can be flagged without a peer group at all.** A store with too few peers is not
  invisible; it is compared with itself.
- **A run must be unbroken.** Any week where the comparison is unavailable resets the run to zero, so "flagged 3
  consecutive weeks" always means three weeks that could actually be measured.
- **Recall rules are skipped for New stores and for stores with fewer than 40 contacts in the window**, because a recall
  programme is not meaningful in either case.
- **"No flag" and "comparison unavailable" are different states** and are displayed differently. The earlier draft
  showed both as "no exceptions", which reads as reassurance the data cannot support.
- **A flag names the rule and the follow-up team, and never a cause.** "Below peers on turnaround" is an area to
  investigate; the prototype's wording is tested against a prohibited-phrase list so that no screen says a store is
  underperforming *because* of anything.

## 7. Ramp index for young stores

```
ramp index = store's 4-week exams per week ÷ median for stores of the same age, × 100
```

Same-age peers are taken at the same weeks-since-opening: first within the same format, then across all formats, with
the same floor of 5. Eligible ages are 3–104 weeks. An index below 80 for **four consecutive available weeks** raises a
ramp prompt.

Four weeks, not one, because a single quiet week in a young store is noise. In the synthetic data the index can be
computed for 36.5% of store-weeks — the rest have too few same-age peers — and **no store meets the trigger**. Both
facts are reported rather than smoothed away.

## 8. Small counts and data quality are treated as design, not cleanup

| Situation | Treatment |
|---|---|
| Count of 1–4 | Displayed as "<5"; any rate built on it is hidden too, so the count cannot be recovered |
| Count of 0 | Displayed as 0 — a real zero is information |
| Programme not active | "Not applicable" — never zero |
| Data completeness under 90% or a stale refresh (Red) | Every KPI for that store-week is withheld; excluded from peers, ramp and flags |
| Late but usable (Amber) | Value shown, marked provisional |

Turnaround and revenue are not count-based, so they are suppressed on their denominator only. The rule is documented
once and applied by the same engine everywhere, so a chart cannot quietly disagree with a card.

**This is a demonstration of a suppression rule, not a production privacy control.** Complementary suppression — making
sure a suppressed cell cannot be derived from a total — is *not* implemented, and is recorded as an open decision.

## 9. Role scope

Four simulated roles: network lead, regional manager, retail partner, optometry partner. Scope is applied **before**
any filter and before every visual, and peers outside a regional manager's own region are anonymous. Revenue is
restricted from the optometry partner view.

This demonstrates the *reporting* design of row- and object-level security. It is not security: the page contains the
whole synthetic dataset, and the role switch is a dropdown.

## 10. The synthetic dataset

30 fictional stores × 26 weeks (23 Feb – 17 Aug 2026) = 761 store-weeks, 24 columns, seed 20260913, regenerating
byte-identically. Stores span 4 regions, 8 provinces and 3 formats, with opening dates spread so that all three cohorts
are populated.

Six patterns were deliberately seeded so the reporting rules have something to find: improving new stores, a region with
elevated turnaround, a store with a conversion decline, small recall counts, Red and Amber data-quality weeks, and a
store with too few peers. The patterns exist to exercise the rules — they are not claims about how any real network
behaves. `build/validate_and_analyze.py` checks all 32 structural and pattern properties on every build.

## 11. Snapshot simplification

The synthetic snapshot is treated as **final**: no provisional attribution windows, no restatements. A production
implementation would need a provisional period for conversion and recall, which is recorded as a stated simplification
rather than left implicit. The prototype's banner says so on screen.

## 12. Tooling

| Stage | Tool |
|---|---|
| Generate and validate the dataset | Python 3.11 (pandas) — `build/generate_synthetic.py`, `build/validate_and_analyze.py` |
| Calculations | One engine, `build/kpi_engine.py` — windows, peers, suppression, exception rules, ramp index |
| Prototype | Hand-written HTML/CSS/JavaScript with no dependencies; `build/build_mockup.py` injects the logic and data into the template |
| Tests | Python `unittest`, Node's built-in test runner, and rendered-page tests driving headless Microsoft Edge over the DevTools protocol |
| Deck | `pptxgenjs`, validated and rendered slide by slide |
| Power BI | Designed only. Never built or executed |

## 13. Corrections made during the repair pass

The prototype was rebuilt after an earlier draft, and four reporting defects only became visible when the rendered page
was tested rather than described. They are recorded because how a defect is caught matters more than never having
written it — the document-level consistency check passed while all four were live:

- **Regional scope was cosmetic.** The role switch filtered the selectors but left the cards, trend, map and banner on
  network figures. Scope is now applied before every visual, and a regression test asserts the regional totals.
- **Red weeks still produced values.** A withheld week inherited the previous week's 4-week value and entered peer
  groups. The engine now withholds at the Red week and excludes it from peers and ramp.
- **Suppressed counts were recoverable.** Counts of 1–4 were captioned "<5" but plotted at their true height. They are
  now text only, and the rates built on them are hidden.
- **Stage grouping dropped a flag reason.** Only the first triggering KPI in a stage was listed. Every triggering KPI is
  now shown.

The full list of 45 issues, with the test that now guards each, is in [`phases/issue-register.md`](phases/issue-register.md)
and [`phases/consistency-check.md`](phases/consistency-check.md).
