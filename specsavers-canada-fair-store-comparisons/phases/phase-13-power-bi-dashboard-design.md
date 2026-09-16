# Phase 13 — Power BI Dashboard Design

**Status:** Design drafted by the author · Prototype **implemented as an HTML mockup on synthetic data** and covered by automated tests · **Power BI build not done; DAX below is unexecuted guidance** · **Prepared:** 2026-09-13 · **Revised:** repair pass (see "Corrections" at the end) · **Builds on:** Phases 1–12

> **Outside-in disclaimer.** This is a **prototype design using synthetic data** (Phase 12). Every value in the mockup and the "synthetic insights" section is fictional and **unrelated to actual Specsavers performance**. KPI definitions (dictionary v0.2), peer rules, exception rules (rule set v0.2), prompts (library v0.2) and thresholds are illustrative proposals.

**Deliverables**
- This design specification.
- **Interactive HTML mockup:** `dashboard-mockup.html`, generated from `build/mockup_template.html`, `build/dashboard_logic.js` and `data/analysis_summary.json`. It renders the three pages with reporting-week, region, province, format, banner, cohort and data-quality filters, drill-through with Back, KPI definitions and data tables.
- **Simulated role view.** The mockup embeds the full synthetic dataset. Its "View as role" selector shows what each role *would* see (scope, anonymous peers, restricted revenue). It is **not** authentication, row-level security (RLS) or object-level security (OLS). Production security is specified in Phase 5 (SR-01 to SR-08) and in §5.5 below.
- Essential Power BI model and DAX guidance (§5), **not executed in Power BI Desktop**.
- Power BI-ready synthetic tables written by the build: `data/powerbi/store_week_kpi.csv`, `store_week_revenue.csv`, `ramp_index.csv` (store-level KPI values, states, peer statistics and flags computed once by `build/kpi_engine.py`).

The mockup is a design artefact, not a Power BI file. It lets the design be reviewed without a Power BI licence.

---

## 1. Report-wide design standards

| Area | Standard |
|---|---|
| Canvas | 16:9, 1280 × 720 in Power BI; the HTML mockup is responsive (tested at 375–1440 px, NFR-08) |
| Theme | Deep teal (favourable) and burnt orange (attention); grey for peers. Never colour alone: data quality uses ● Green, ▲ Amber, ■ Red **with the words "Data quality"** (NFR-04). Text colours meet 4.5:1 on white and on the page background (test JS-CONTRAST-01) |
| Header on every page | Selected week · **"Data as at"** · Green/Amber/Red counts **for the stores in view** · KPI dictionary, exception rule set and prompt library versions · peer floor and small-count rule · finalised-snapshot note · **SYNTHETIC DATA** label |
| Numbers | Rates to 1 decimal place; counts with thousands separators; revenue in CAD with no decimals; distinct states for **n/a (low volume)**, **Suppressed (<5)**, **Not applicable**, **Insufficient history**, **Data check required (Red)** and **Restricted** |
| Periods | Every visual states its period: *selected week*, *4 calendar weeks ending the selected week*, *weekly values across 26 weeks* or *weeks since opening* |
| Language | Triage vocabulary: "warrants attention", "area to investigate", "typical follow-up". Prohibited: "caused by", "because", "due to", "driver", "root cause" (UAT-21; tests JS-TEXT-01, UI-TEXT-01) |
| Help | ⓘ on KPIs opens a definition (formula, units, period, exclusions, proposed owner, version, limitations) from the dictionary; "How to read this page" on every page (FR-07) |
| Security | **Production:** RLS on DimStore via an access mapping; table-level OLS on a separate revenue table; peer statistics precomputed so partners never need peer rows (§5.5). **Prototype:** simulated only |
| Performance | ≤ 8 visuals per view excluding cards; aggregated tables; no bidirectional filters (NFR-01) |

---

## 2. Page 1 — Network Overview (Regional Overview for a regional manager)

| Element | Specification (✓ = implemented in the prototype) |
|---|---|
| **Primary user** | Retail Operations lead (SH-04); Regional Retail Managers (SH-03, own region) |
| **Decision supported** | Is the network, or my region, moving as expected? Which stores and stages warrant attention this week (MD-1, MD-2)? |
| **Visuals** | 1. ✓ **KPI cards (10), selected week, stores in view:** active stores · completed exams (weekly total) · appointment utilization · attendance · conversion · recall-booking rate · revenue per completed exam *(restricted, context only)* · on-time fulfilment · average turnaround · data-quality counts. Each rate compares with the **pooled rate over the 4 weeks before the selected week** (same stores, Red excluded); exams compare with the prior 4-week weekly average. *Sparklines: specified only.* <br>2. ✓ **Province tile map** (4 calendar weeks ending the selected week): value labels; states "No synthetic stores", "Outside your scope", "Filtered out"; tiles are buttons that set the province filter; data-table alternative. <br>3. ✓ **Weekly trend** (weekly pooled values, 26 weeks): ■ markers for weeks with Red store-weeks excluded; selected-week line; for a regional manager (or any filtered view) a dashed **network reference** line labelled as a comparison population, not the user's scope. <br>4. ✓ **Region table** (4 weeks ending the selected week): stores, utilization, attendance, conversion, on-time, turnaround, stores with a fulfilment flag this week. Network roles see all regions; a regional manager sees only their region plus a labelled **network reference** row (U-38 demonstration assumption). <br>5. ✓ **Stores warranting attention** (selected week): one row per store and journey stage, listing **every** triggering KPI with its 4-week value, the reference used (peer median for rule a, own baseline for rule b), consecutive weeks and data quality; Red store-weeks listed as data checks; a coverage line counts stores with a triggered rule, with no triggered rule, with some comparisons unavailable, and data checks. |
| **Filters** | ✓ Reporting week (single) · Region · Province · Store format · Host banner · Maturity cohort (as at the selected week) · Data-quality status. Role scope is applied first; options outside the scope never appear; filter summary line and Reset. *Week range: not implemented (trends show 26 weeks).* |
| **Drill-through** | ✓ Exception row → Page 3 (same store, week and filters) with Back · ✓ Region name → region filter · ✓ Province tile → province filter |
| **Tooltips** | Card definitions via ⓘ; tile title shows value, stores and Red exclusions; exception rows state rule and reference in the table text |
| **Accessibility** | Keyboard-operable tabs (arrow keys, Home/End), visible focus, chart titles and descriptions, "Show data table" for every chart, header scopes on tables. Tested with automated checks and real key events (UI-A11Y-01…03, UI-KEY-01…05); **no screen-reader test or formal audit** |
| **Data-quality treatment** | Banner counts for the stores in view; Red store-weeks excluded from every rate with a count; Amber shown as provisional on store views; ■ markers on the trend |
| **Business action supported** | Choose which stores and stages to review; decide whether a pattern is local (store conversation) or shared (one conversation with a central team, e.g., Supply Chain) |

**Wireframe (Page 1, synthetic week of 17 Aug 2026)**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Simulated role view note · View as role ▾                                   │
│ Week ▾  Region ▾  Province ▾  Format ▾  Banner ▾  Cohort ▾  Data quality ▾ [Reset] │
│ Data as at week of Aug 17, 2026 · ● 28 Green ▲ 2 Amber ■ 0 Red · versions    │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────────┤
│Stores│Exams │Util %│Att % │Conv %│Recall│Rev/ex│OnTime│TAT d │ DQ ●28 ▲2 ■0  │
│  30  │3,496 │82.4% │93.6% │57.0% │17.7% │(role)│90.2% │ 6.5  │               │
├───────────────────────────────────────┬──────────────────────────────────────┤
│ Weekly trend [KPI▾] ── scope -- ref ■ │ Province tiles [KPI▾] (4 weeks)      │
├───────────────────────────────────────┼──────────────────────────────────────┤
│ Region table (4 weeks)                │ Stores warranting attention (stage)  │
│ Region│Stores│Util│Att│Conv│OnT│TAT   │ Store│Cohort│Stage│KPIs (rule)│Wks│DQ │
└───────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Page 2 — Store and Cohort Benchmarking

| Element | Specification (✓ = implemented in the prototype) |
|---|---|
| **Primary user** | Regional Retail Managers (SH-03); Retail Partners (SH-01) for their own store; Business Development (SH-15) for ramp-up |
| **Decision supported** | Is this store performing, and ramping up, in line with comparable stores? Which KPIs differ most (MD-1, MD-3)? |
| **Visuals** | 1. ✓ **Store header:** format, province, region, banner, cohort **as at the selected week**, week N since opening, data quality, ramp index with basis and n. <br>2. ✓ **Store vs peer median table** (week of selection; 4-week values): completed exams per week, utilization, attendance, conversion, on-time, turnaround, recall-booking rate, revenue per exam (restricted) · peer median · variance (absolute and %) · position (below P25 / P25–P75 / above P75) · peer basis text · exception rule status ("rule (a) peer", "rule (b) own trend", "no triggered rule", "peer rule unavailable; own-trend rule only", "not eligible", "comparison unavailable"). <br>3. ✓ **Peer distribution** (selected KPI and week): dots for peers with a reportable value, P25/median/P75 lines, selected store; the **comparison population** is stated (e.g., "7 Developing · Grocery-hosted stores across all regions (2 in Atlantic)"). Names: network role sees names; regional manager sees names **only for peers inside the region**, other peers labelled "Peer store outside Atlantic"; partners see anonymous peers. <br>4. ✓ **Ramp-up by weeks since opening** — the **same chart for every store with weeks 0–104 in the sample**: store completed exams per week (4-week average) vs peer median at the same age with IQR band split at gaps; New → Developing marker; gap reasons with actual ranges; ramp-trigger status; data table with peer n by age. Mature-only stores show "Not applicable". <br>5. ✓ **Variance from peer median over time** (26 weeks): red dots for weeks with a triggered rule (explained: rule b can flag when the peer variance is small), ■ Red weeks, gap reasons. <br>6. ✓ **Warnings:** Red selected week; small peer group (fallback, with format and cohort n); peer comparison not available (own values remain visible). |
| **Filters** | ✓ Store (within role scope and page filters) · KPI · reporting week and the global filters |
| **Drill-through** | ✓ In from Page 1 · ✓ "Open Store Diagnostic" (same store and week) · Back |
| **Tooltips** | Dot: peer label per role and value · Basis text in the table · ⓘ definitions |
| **Accessibility** | The comparison table is the primary accessible view; distribution and charts have data tables |
| **Data-quality treatment** | Red selected week: values, peer comparisons and flags withheld; peer statistics use only other stores' reportable values (Red store-weeks excluded); Amber shown as provisional |
| **Small-peer-group treatment** | Fewer than 5 cohort × format peers → whole cohort with ▲ warning stating both n; fewer than 5 cohort peers → "Peer comparison not available"; ramp ages with fewer than 5 same-age peers → gap with reason (FR-16, PR-03) |
| **Business action supported** | Set realistic expectations for new stores; decide whether a gap is large and persistent enough for a support conversation; brief partners with anonymous, like-for-like context |

**Wireframe (Page 2)**
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Store: SYN-014 · Northstar Mews ▾   KPI: Conversion ▾   [Open Store Diagnostic] │
│ Grocery-hosted · MB · Prairies · Developing as at Aug 17, 2026 · week 31 ·      │
│ Data quality ● Green · Ramp index 102 (same-format peers, n = 7)              │
│ (▲ small-peer-group warning shown here when a fallback applies, e.g. SYN-029) │
├───────────────────────────────────────┬──────────────────────────────────────┤
│ Store vs peer median table            │ Peer distribution (population stated)│
├───────────────────────────────────────┼──────────────────────────────────────┤
│ Ramp-up by weeks since opening        │ Variance from peer median over time  │
└───────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 4. Page 3 — Store Diagnostic and Data Quality

| Element | Specification (✓ = implemented in the prototype) |
|---|---|
| **Primary user** | Retail Partners and Optometry Partners (landing page, own store); Regional Retail Managers |
| **Decision supported** | Which journey stage should be investigated first, who typically follows up, and is the data fit to act on (MD-4, MD-5)? |
| **Visuals** | 1. ✓ **Funnel table** (4 calendar weeks ending the selected week; usable weeks stated): available slots → held appointments (*booked minus cancelled; includes attended, no-shows and statuses not recorded*) → completed exams → exam-linked purchasing customers; separate cells for label, bar, count and stage rate with peer median; statuses not recorded shown (suppressed if 1–4); revenue per exam as context (restricted for Optometry Partners). <br>2. ✓ **Investigation areas** (selected week): for each flagged stage, a rule-specific explanation — rule (a) cites the peer P25 and median with the peer basis; rule (b) cites the store's own 8-week baseline and consecutive weeks — then the prompt and typical follow-up team. Ramp prompt only when the index is below 80 for 4 consecutive weeks. If nothing triggered: a compact statement with the count of earlier flagged weeks, comparisons unavailable this week, and "this does not show that every area is performing well". <br>3. ✓ **Six trend cards** (weekly points of 4-week values, 26 weeks): utilization, attendance, conversion, on-time, turnaround, recall-booking rate · store vs dashed peer median · flag dots · ▲ Amber / ■ Red markers · selected-week line · store-line and peer-line gap reasons · data tables. <br>4. ✓ **Weekly recall bookings** as a text strip ("<5", "0", "n/a", "Withheld"), so small counts have no plotted position. <br>5. ✓ **Data-quality panel**, labelled as not a performance measure: 26 week cells (buttons that select the week), legend, and a table of non-Green weeks with completeness, refresh, statuses not recorded and treatment. |
| **Filters** | ✓ Store (partners locked to own store) · reporting week and global filters |
| **Drill-through** | ✓ In from Pages 1 and 2 · ✓ "Open benchmarking" · ✓ data-quality cell → that week |
| **Tooltips** | Chart points and flags titled with the week; definitions via ⓘ |
| **Accessibility** | Funnel is a semantic table that restacks on narrow screens; trends have titles, descriptions and data tables |
| **Data-quality treatment** | Red selected week → funnel withheld, only the data prompt shown, no performance rules; Amber → provisional note; statuses not recorded shown explicitly; recall "not applicable" distinct from zero |
| **Business action supported** | Partner and manager agree 1–2 areas to investigate, the follow-up team, and whether to wait for data correction (manual follow-up log in the pilot, EO-04) |

### Investigation prompt library v0.2 (illustrative, FR-15)

| Stage | Trigger | Explanation shown (template) | Prompt | Typical follow-up |
|---|---|---|---|---|
| Booking | Utilization flagged | Rule text per rule (below) | Review booking visibility (online and in-store), the appointment availability pattern and local awareness activity. | Store team with Regional Retail Manager; Marketing if the pattern is regional |
| Attendance | Attendance flagged | ″ | Check the reminder and confirmation process, booking lead times and no-show follow-up. | Store team with Regional Retail Manager |
| Conversion | Conversion flagged | ″ | Review the exam-to-eyewear hand-off, frame and lens availability, and how pricing and coverage options are explained. | Retail and Optometry Partners with Regional Retail Manager |
| Fulfilment | On-time and/or turnaround flagged (all listed) | ″ | Review order routing, lab turnaround and remakes; check whether nearby stores show the same pattern. | Supply Chain with store team |
| Recall | Recall-booking rate flagged | ″ | Review recall list quality, contact channel mix and booking follow-up. | Marketing with store team |
| Ramp | Ramp index < 80 for 4 consecutive weeks with an available index | "Ramp index N: below 80 for K consecutive weeks against same-age peers." | Discuss local launch activity, booking visibility and the capacity plan. | Regional Retail Manager with Business Development |
| Data | Data quality Red in the selected week | "Data quality Red (x% complete, refresh s). No performance rules are evaluated for this week." | Review data completeness with the data team before discussing performance for this store-week. | Data team |

**Rule text templates.** Rule (a): *"Rule (a), peer comparison: 4-week value X is beyond the peer 25th percentile (P25) and at least 10% below the peer median M (basis, n)."* Rule (b): *"Rule (b), own trend: 4-week value X is N% below this store's own baseline B (the 8 weeks before the window), for K consecutive weeks (rule needs 3)."* (For turnaround, "above" replaces "below".) **Change from v0.1:** v0.1 used one sentence for every flag ("Flags show where this store differs from comparable stores"), which was wrong for rule (b).

### Exception rule set v0.2 (illustrative; owner SH-04; separate from the KPI dictionary)

| Parameter | v0.2 value | Status vs v0.1 |
|---|---|---|
| Rule (a) | 4-week value below peer P25 **and** at least 10% worse than the peer median (turnaround: above P75 and at least 10% higher). Needs a peer group of 5 or more | Unchanged |
| Rule (b) | 4-week value at least 15% worse than the pooled 8 calendar weeks immediately before the window (minimum 6 usable weeks), for 3 consecutive weeks | Wording clarified in RTM-17; unchanged meaning |
| Consecutive weeks | Counted per KPI over calendar weeks; any week where the KPI is unavailable (Red, insufficient history, suppressed) resets the run; a stage shows the longest current run of its KPIs | **New** (was undefined) |
| Recall eligibility | Recall exceptions only for Developing and Mature stores with **40 or more contacts** in the 4-week window | **New in v0.2.** Earlier documents called this a "v0.1 parameter"; it changes which stores can be flagged, so it is a versioned change |
| Red selected week | No rule is evaluated; the store-week is excluded from others' peer groups | Clarified |
| Revenue per exam | Never an exception driver | Unchanged |
| Ramp trigger | Index below 80 for 4 consecutive weeks with an available index (KPI-10 guidance) | **New as a rule** (the v0.1 prototype checked only the latest week) |
| Stage grouping | One row per store-week-stage listing every triggering KPI | **Changed** (v0.1 kept only the first KPI) |

---

## 5. Essential Power BI model and DAX (unexecuted guidance)

> **Not tested in Power BI.** The DAX below is written to mirror `build/kpi_engine.py` and `build/dashboard_logic.js`, but it has not been run in Power BI Desktop. Treat it as a specification for the Visualization Analyst, to be validated with the reconciliation tests in Phase 14.

**Design principle.** Store-level 4-week values, states, peer statistics, exception flags and the ramp index are **computed once upstream** (in the prototype by `kpi_engine.py`; in production by the data pipeline) and loaded as tables. DAX then (1) reads those store-level values for store pages and (2) aggregates the selected week's store-week counts for network and regional cards. This keeps one implementation of the rules and works under RLS, because a partner's row already carries its peer statistics.

### 5.1 Model tables

| Table | Grain / content | Source |
|---|---|---|
| `StoreWeek` | Store × week counts (slots, booked, cancelled, no-shows, completed, purchasers, orders, on-time, turnaround, recall), completeness, refresh | `data/synthetic_store_weekly.csv` |
| `StoreWeekKPI` | Store × week × KPI: value (4-week), state, peer median/P25/P75, peer n, basis, rule (a), rule (b), flag, consecutive weeks, 8-week baseline, change, exception state | `data/powerbi/store_week_kpi.csv` |
| `StoreWeekRevenue` | Store × week: eyewear revenue and revenue per exam (value, state, peer statistics). **Separate table so OLS can secure it** | `data/powerbi/store_week_revenue.csv` |
| `RampIndex` | Store × week: weeks since opening, ramp index, state, peer median/P25/P75 at that age, peer n, basis, run length, trigger | `data/powerbi/ramp_index.csv` |
| `DimStore` | One row per store (prototype); effective-dated in production (Phase 7) | Distinct store attributes |
| `DimCalendar` | **Contiguous daily dates** from 2026-02-23 to 2026-08-23 with `WeekStart` (Monday), `WeekEnd`, `WeekLabel`, `WeekIndex`, `IsLatestWeek`. Marked as the date table on `Date` | Generated in Power Query or DAX (`CALENDAR`) |
| `KPISelector` | One row per KPI key: `kpi_key`, label, unit, sort order, higher-is-better | Static table |
| `KPIDictionary`, `PromptLibrary` | Governed reference content (Phase 6 v0.2, §4 library v0.2) | Static tables |
| `AccessMap` | `user_upn`, `role`, `store_id` or `region` | Access governance (SR-02); hidden; no relationships |

**Why a daily calendar.** Power BI validates a marked date table for unique, non-blank and **contiguous** date values ([Microsoft Learn: Set and use date tables in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-date-tables)). A table of Monday week-starts has six-day gaps, so it should not be described as a conventional marked date table. Week-level facts relate to the daily calendar through their week-start date; visuals slice on `DimCalendar[WeekStart]`.

**Relationships (all many-to-one, single direction, dimension → fact)**

| From (many) | To (one) |
|---|---|
| `StoreWeek[store_id]`, `StoreWeekKPI[store_id]`, `StoreWeekRevenue[store_id]`, `RampIndex[store_id]` | `DimStore[store_id]` |
| `StoreWeek[week_start]`, `StoreWeekKPI[week_start]`, `StoreWeekRevenue[week_start]`, `RampIndex[week_start]` | `DimCalendar[Date]` |
| `StoreWeekKPI[kpi_key]` | `KPISelector[kpi_key]` |
| `KPIDictionary[kpi_key]` | `KPISelector[kpi_key]` (one-to-one) |

`StoreWeekRevenue` is a leaf table, so securing it with table-level OLS does not break a relationship chain.

### 5.2 Calculated columns (`StoreWeek`)

```DAX
Held Appointments = StoreWeek[booked_appointments] - StoreWeek[cancelled_appointments]

Unresolved Statuses =
    StoreWeek[booked_appointments] - StoreWeek[completed_exams]
        - StoreWeek[cancelled_appointments] - StoreWeek[no_show_appointments]

DQ Status =
    SWITCH ( TRUE (),
        StoreWeek[data_completeness_pct] < 90 || StoreWeek[data_refresh_status] = "Stale", "Red",
        StoreWeek[data_completeness_pct] < 98 || StoreWeek[data_refresh_status] = "Delayed", "Amber",
        "Green" )

Is Usable = StoreWeek[DQ Status] <> "Red"

-- KPI-07 synthetic simplification: all placed orders reached "ready"
Turnaround x Orders = StoreWeek[average_turnaround_days] * StoreWeek[orders_placed]
```

### 5.3 Selected-week aggregates for network and regional cards (mirrors `aggregate()` in `dashboard_logic.js`)

```DAX
Min Count = 5    -- PR-04 demonstration rule v0.2 and peer floor (illustrative)

Selected Week = MAX ( DimCalendar[WeekStart] )     -- single-select week slicer

Store-Weeks = COUNTROWS ( StoreWeek )
Red Store-Weeks   = CALCULATE ( COUNTROWS ( StoreWeek ), StoreWeek[DQ Status] = "Red" )
Amber Store-Weeks = CALCULATE ( COUNTROWS ( StoreWeek ), StoreWeek[DQ Status] = "Amber" )

Slots (usable)      = CALCULATE ( SUM ( StoreWeek[available_appointment_slots] ), StoreWeek[Is Usable] = TRUE () )
Held (usable)       = CALCULATE ( SUM ( StoreWeek[Held Appointments] ),           StoreWeek[Is Usable] = TRUE () )
Exams (usable)      = CALCULATE ( SUM ( StoreWeek[completed_exams] ),             StoreWeek[Is Usable] = TRUE () )
Purchasers (usable) = CALCULATE ( SUM ( StoreWeek[purchasing_customers] ),        StoreWeek[Is Usable] = TRUE () )
Orders (usable)     = CALCULATE ( SUM ( StoreWeek[orders_placed] ),               StoreWeek[Is Usable] = TRUE () )
On Time (usable)    = CALCULATE ( SUM ( StoreWeek[orders_ready_on_time] ),        StoreWeek[Is Usable] = TRUE () )

-- Reusable rule: show a count-based rate only if denominator >= 5 and numerator is not 1-4
Utilization % =
VAR n = [Held (usable)]
VAR d = [Slots (usable)]
RETURN IF ( d >= [Min Count] && NOT ( n >= 1 && n < [Min Count] ), DIVIDE ( n, d ) )

Attendance % =
VAR n = [Exams (usable)]  VAR d = [Held (usable)]
RETURN IF ( d >= [Min Count] && NOT ( n >= 1 && n < [Min Count] ), DIVIDE ( n, d ) )

Conversion % =
VAR n = [Purchasers (usable)]  VAR d = [Exams (usable)]
RETURN IF ( d >= [Min Count] && NOT ( n >= 1 && n < [Min Count] ), DIVIDE ( n, d ) )

On-time % =
VAR n = [On Time (usable)]  VAR d = [Orders (usable)]
RETURN IF ( d >= [Min Count] && NOT ( n >= 1 && n < [Min Count] ), DIVIDE ( n, d ) )

Avg Turnaround Days =      -- not count-based: no numerator suppression
VAR d = [Orders (usable)]
RETURN IF ( d >= [Min Count], DIVIDE ( CALCULATE ( SUM ( StoreWeek[Turnaround x Orders] ), StoreWeek[Is Usable] = TRUE () ), d ) )

Recall Booking % =
VAR c = CALCULATE ( SUM ( StoreWeek[recall_contacts] ), StoreWeek[Is Usable] = TRUE (), NOT ISBLANK ( StoreWeek[recall_contacts] ) )
VAR b = CALCULATE ( SUM ( StoreWeek[recall_bookings] ), StoreWeek[Is Usable] = TRUE (), NOT ISBLANK ( StoreWeek[recall_contacts] ) )
RETURN IF ( NOT ISBLANK ( c ) && c >= [Min Count] && NOT ( b >= 1 && b < [Min Count] ), DIVIDE ( b, c ) )

Conversion Display =       -- same pattern for each rate card
VAR d = [Exams (usable)]
VAR v = [Conversion %]
RETURN SWITCH ( TRUE (),
    [Store-Weeks] = 0, "No stores match",
    ISBLANK ( d ) && [Red Store-Weeks] > 0, "Data check required",
    ISBLANK ( d ) || d < [Min Count], "n/a (low volume)",
    ISBLANK ( v ), "Suppressed (<5)",
    FORMAT ( v, "0.0%" ) )

Recall Bookings Display =
VAR b = CALCULATE ( SUM ( StoreWeek[recall_bookings] ), StoreWeek[Is Usable] = TRUE () )
RETURN SWITCH ( TRUE (),
    ISBLANK ( b ), "n/a (no programme)",
    b = 0, "0",
    b < [Min Count], "<5",
    FORMAT ( b, "#,0" ) )

-- "vs prior 4 weeks": pooled rate over the 4 weeks before the selected week (not an average of weekly rates)
Conversion % (prior 4 weeks pooled) =
VAR wk = [Selected Week]
RETURN CALCULATE ( [Conversion %], REMOVEFILTERS ( DimCalendar ), DATESBETWEEN ( DimCalendar[Date], wk - 28, wk - 7 ) )

Conversion Change (pts) =
VAR cur = [Conversion %]  VAR prv = [Conversion % (prior 4 weeks pooled)]
RETURN IF ( NOT ISBLANK ( cur ) && NOT ISBLANK ( prv ), ( cur - prv ) * 100 )

Data As At Banner =
"Data as at week of " & FORMAT ( [Selected Week], "mmm d, yyyy" )
    & "  ·  ● " & ( [Store-Weeks] - [Amber Store-Weeks] - [Red Store-Weeks] ) & " Green"
    & "  ·  ▲ " & ( [Amber Store-Weeks] + 0 ) & " Amber  ·  ■ " & ( [Red Store-Weeks] + 0 ) & " Red"
```

Because RLS filters `DimStore`, these measures return the **user's scope** automatically: a regional manager's banner and cards count only their region (the prototype defect ISS-01/ISS-02 cannot occur in a correctly secured model). A network reference for a regional manager needs a separate, approved aggregate table (for example `AggNetworkWeek`) outside the RLS filter, and should only be added if U-38 allows it.

### 5.4 Store-level values, peers and flags (read from precomputed tables)

```DAX
Selected KPI = SELECTEDVALUE ( KPISelector[kpi_key], "conversion" )

KPI State = SELECTEDVALUE ( StoreWeekKPI[state] )     -- ok · red · insufficient_history · low_volume · suppressed · not_applicable

KPI Value (4 weeks) = IF ( [KPI State] = "ok", SELECTEDVALUE ( StoreWeekKPI[value] ) )

KPI State Text =
SWITCH ( [KPI State],
    "red", "Data check required",
    "insufficient_history", "Insufficient history",
    "low_volume", "n/a (low volume)",
    "suppressed", "Suppressed (<5)",
    "not_applicable", "Not applicable",
    BLANK () )

Peer Median = IF ( [KPI State] <> "red", SELECTEDVALUE ( StoreWeekKPI[peer_median] ) )

Variance vs Peer =
VAR s = [KPI Value (4 weeks)]  VAR p = [Peer Median]
RETURN IF ( NOT ISBLANK ( s ) && NOT ISBLANK ( p ), s - p )

Peer Basis Text =
VAR b = SELECTEDVALUE ( StoreWeekKPI[peer_basis] )
VAR n = SELECTEDVALUE ( StoreWeekKPI[peer_n] )
VAR c = SELECTEDVALUE ( StoreWeek[maturity_cohort] )
RETURN SWITCH ( TRUE (),
    [KPI State] = "red", BLANK (),
    b = "cohort x format", c & " · " & SELECTEDVALUE ( DimStore[store_format] ) & " · n = " & n,
    b = "cohort (fallback)", "▲ Small peer group: all " & c & " stores (n = " & n & ")",
    "Peer comparison not available (fewer than 5 peers)" )

Exception Text =
VAR a = SELECTEDVALUE ( StoreWeekKPI[rule_a] )
VAR b = SELECTEDVALUE ( StoreWeekKPI[rule_b] )
RETURN SWITCH ( TRUE (),
    [KPI State] = "red", "Withheld (data quality Red)",
    a && b, "Flag: rules (a) peer and (b) own trend",
    a, "Flag: rule (a) peer comparison",
    b, "Flag: rule (b) own trend",
    SELECTEDVALUE ( StoreWeekKPI[exception_state] ) = "not_eligible", "Not eligible",
    SELECTEDVALUE ( StoreWeekKPI[exception_state] ) = "unavailable", "Comparison unavailable",
    SELECTEDVALUE ( StoreWeekKPI[exception_state] ) = "no_flag_own_baseline_only", "No triggered rule (own-trend rule only)",
    "No triggered rule" )

Ramp Index = IF ( SELECTEDVALUE ( RampIndex[ramp_state] ) = "ok", SELECTEDVALUE ( RampIndex[ramp_index] ) )
```

### 5.5 Security (production design; not built)

**Row-level security** (role table filters on `DimStore`):
```DAX
-- Role: Partner (Retail or Optometry) — own store(s)
DimStore[store_id] IN CALCULATETABLE ( VALUES ( AccessMap[store_id] ), AccessMap[user_upn] = USERPRINCIPALNAME () )

-- Role: Regional Retail Manager — assigned region(s)
DimStore[region] IN CALCULATETABLE ( VALUES ( AccessMap[region] ), AccessMap[user_upn] = USERPRINCIPALNAME () )
```
`StoreWeekKPI` carries each store's peer statistics on its own row, so partners see peer medians without seeing peer rows (PR-07). The peer **distribution** with named dots needs a peer-membership table (store × week × KPI × peer value, with the peer's region); load it only for roles allowed to see it, and label out-of-region peers anonymously for regional managers.

**Object-level security** (per [Microsoft Learn: Tabular model object-level security](https://learn.microsoft.com/en-us/analysis-services/tabular-models/object-level-security?view=sql-analysis-services-2025)):
- OLS secures **tables and columns**: set `metadataPermission` to `none` on the `tablePermissions` (or `columnPermissions`) of a role, using Tabular Editor, TMSL or TOM.
- There is **no mechanism to secure a measure directly**. Measures that reference a secured table or column are restricted automatically for that role. So secure the **`StoreWeekRevenue` table** for the Optometry Partner, Supply Chain and Marketing roles; revenue measures that reference it become unavailable to them. *Correction:* the earlier draft said to set the `Revenue per Exam` measure to "None", which is not possible.
- Table-level OLS cannot secure a table in the middle of a relationship chain; `StoreWeekRevenue` is a leaf table.
- RLS and OLS **cannot be combined from different roles** for the same user; give each persona one role that carries both its row filter and its object permissions.
- Visuals that use a secured object show an error-like message rather than an empty value; Q&A, quick insights, smart narrative and the Excel data types gallery are not supported with OLS. Design role-specific pages or bookmarks accordingly and test for leakage (Phase 14, ACC tests).

---

## 6. Synthetic insights demonstrated by the prototype

> **All figures below are synthetic.** They show how the design surfaces patterns. They are **not** findings about Specsavers. Each figure states its period.

**Week of 17 Aug 2026 (latest week), synthetic network of 30 stores:** 3,496 completed exams · utilization 82.4% · attendance 93.6% · conversion 57.0% (▼ 0.8 pts vs the pooled 4 weeks before) · recall-booking rate 17.7% · on-time 90.2% · turnaround 6.5 days · data quality 28 Green, 2 Amber, 0 Red.

| # | What the prototype surfaces (period) | Why simple reporting could miss it | Suggested area to investigate (not a cause) |
|---|---|---|---|
| SI-1 | **Cohort gap** (all 26 weeks, pooled by as-at-week cohort): New stores average 66 completed exams per store-week vs 150 for Mature; conversion 51.2% vs 59.2% | An unadjusted comparison mixes store age with performance, so young stores tend to look weak on volume whatever their ramp-up progress | Compare young stores with same-age peers, not the whole network |
| SI-2 | **SYN-014 is on track** (week of 17 Aug 2026): 82 exams per week (4-week average), ramp index **102** against 7 same-format peers observed at week 31 since opening | Absolute volume looks low | No action; continue monitoring |
| SI-3 | **SYN-030 (index 86, n = 6) and SYN-020 (89, n = 5)** (week of 17 Aug 2026) are below same-age peers but above the illustrative threshold of 80. **No store in the synthetic sample meets the ramp trigger** (below 80 for 4 consecutive weeks); the trigger is verified with unit tests instead (PY-RAMP-01) | Easy to over-react to new-store numbers | Watch; discuss with Business Development only if the trigger is met |
| SI-4 | **Regional fulfilment pattern.** Atlantic turnaround **8.9 days** in the 4 weeks ending 17 Aug 2026 vs 6.0–6.1 in other regions; on-time 78.5% vs 92.3–92.5%. (Latest week alone: 9.1 days and 77.3%. All 26 weeks: 8.7 vs 6.0 days.) SYN-025 to SYN-028 are flagged on **both** on-time and turnaround in the latest week | Four store conversations could hide one shared issue | One regional review with Supply Chain (order routing, lab turnaround) |
| SI-5 | **An unavailable peer comparison can hide a store-level signal.** SYN-030 shows the same slow turnaround but is not flagged: its New · Grocery-hosted and New-cohort peer groups are under 5 stores, so rule (a) cannot be evaluated; its own values remain visible and only the own-trend rule applies | Store-only exception lists miss it | Keep the region comparison on Page 1 alongside store flags |
| SI-6 | **High demand, low attendance** (all 26 weeks): SYN-012 and SYN-019 run at about 94% utilization but about 84% attendance, against 94% attendance in the rest of the network. Attendance is flagged in 22 and 21 of 26 weeks | A utilization-only view suggests a capacity shortage | Reminders, confirmation and no-show follow-up before adding capacity |
| SI-7 | **Mature store conversion decline.** SYN-005 fell from 62.9% (weeks 1–6 pooled) to 42.9% (last 8 weeks pooled) while exams held at about 157 per week. Rule (a) flags from the week of 27 Apr 2026; rule (b), against its own baseline, flags 11 May to 8 Jun 2026 | Exam totals and revenue trends can mask a hand-off issue | Exam-to-eyewear hand-off, product availability, and how pricing and coverage are explained |
| SI-8 | **Data-quality protection.** SYN-022's three Red weeks (25 May – 8 Jun 2026; 78.5–88% complete) would understate its exams by up to about 21%. Values are withheld, no rule is evaluated, the weeks are excluded from peers, and the following funnel windows state how many weeks were usable (1 of 4 in the week of 15 Jun). SYN-009's unrecorded statuses show as Amber | Incomplete data could trigger an unfair conversation | Fix the data before discussing performance |
| SI-9 | **Alert volume and ramp coverage** (all 26 weeks): 228 stage flags (8.8 per week across 30 stores); the ramp index is available for 36% of store-weeks aged 3–104 weeks in a 30-store sample | Rules that look fine on paper may create noise or blind spots | Tune thresholds in the pilot (R-18); expect better ramp coverage in a larger network (R-03) |
| SI-10 | **Format and maturity overlap.** Most grocery-hosted stores are young, so format-level averages mix the two effects | Format comparisons alone could mislead | Keep cohort × format peers; treat format differences as context, not cause |

**Demonstration route (about five minutes).** Open `dashboard-mockup.html`:
1. **Page 1, Retail Operations lead:** read the banner and the 10 cards; note SYN-025 to SYN-028 in "Stores warranting attention" with both fulfilment KPIs.
2. **Switch role to Regional Retail Manager (Atlantic):** cards change to 6 stores and 545 exams; the banner shows 0 Amber; other regions disappear and a labelled network reference remains.
3. **Back to Retail Operations lead → Page 2, SYN-014:** ramp index 102 with same-age peers; then **SYN-029** for the small-peer-group fallback and **SYN-030** for an unavailable peer comparison.
4. **Page 3, SYN-014:** funnel 460 → 350 → 326 → 187; weekly recall bookings shown as "<5".
5. **Set the week to 25 May 2026 and open SYN-022:** values withheld, only the data prompt. Select the 6 Jul cell for **SYN-027** to see the stale week.
6. **Week of 25 May, SYN-005:** rule (b) explanation against its own baseline; press Back to return with filters kept.

---

## Phase 13 close

### Decisions made
1. Three pages specified with user, decision, visuals, filters, drill-through, tooltips, accessibility, data-quality treatment and business action; the prototype implements them on synthetic data (see `feature-status-matrix.md`).
2. **Store-level values, peer statistics, flags and the ramp index are computed once upstream** and loaded as tables; DAX aggregates the selected week and reads store-level values (§5).
3. Exceptions grouped by journey stage listing every triggering KPI; exception rule set **v0.2** holds the recall eligibility parameter, run definitions and the ramp trigger.
4. Province **tile map** chosen over a filled map for accessibility, performance and no external map dependency.
5. The HTML mockup's role selector is a **simulated role view**; production RLS and OLS are specified in §5.5 and Phase 5 and remain untested.

### Assumptions introduced
| ID | Assumption |
|---|---|
| A-41 | Precomputed store-level and peer tables are acceptable to governance (aggregates only, suppression applied before load). |
| A-42 | Users accept 4-week values as the default comparison basis. |

### Questions requiring validation
- Is a tile map acceptable to leadership, or is a geographic map expected?
- Is the stage-grouped exception list the right unit of work for Regional Retail Managers?

### Corrections
1. **Phase 7:** AGG_PEER_BENCHMARK and AGG_EXCEPTION_FLAG added. *Applied (Phase 13 addition).* The prototype's `store_week_kpi.csv` is the synthetic equivalent of both.
2. **Versions reconciled (repair pass).** The recall ≥ 40-contact parameter belongs to **exception rule set v0.2** (§4). KPI dictionary **v0.2** adds only an interpretation note to KPI-09. The earlier statement that it was a "rule set v0.1 parameter" was incorrect.
3. **Security claims corrected (repair pass).** The mockup simulates role views; it does not demonstrate RLS or OLS.
4. **Power BI guidance corrected (repair pass).** Daily contiguous calendar instead of a Monday-only "date table"; selector table and relationships defined; DAX aligned with the prototype's rules (usable weeks, Red withholding, numerator suppression, pooled prior-4-week comparison); OLS instructions follow Microsoft's documented behaviour; DAX labelled unexecuted.
5. **Synthetic insights (repair pass):** periods stated for every figure; "a national ranking would put every young store at the bottom" and "one New store is hidden" replaced with precise wording; ramp coverage 36% and 228 flags reflect the corrected Red-week and suppression rules (previously 40% and 227).
