# v2 — product film: art direction for approval

Status: **style frames and motion prototype only.** No full render, no commit.
v1 is untouched and still passes its 41 figure checks.

---

## 1. The reference — what I actually saw

I did watch it. `WebFetch` returned only the post text, so I opened the post in
the in-app browser, dismissed the sign-in prompt (I did **not** sign in), and
stepped the player through its timeline. The video is **46.5 s, 960×720**.

What is actually on screen:

| Time | Shot |
|---|---|
| 0:02 | A **dark-themed** dashboard panel at a steep angle in a near-black room, raked by a warm amber light from the left. Barely legible — it is a mood shot, not an information shot. |
| 0:09 | "Incident propagation": an isometric node diagram inside a dark navy dashboard, **flat-on, filling the frame**, teal accents. |
| 0:18 | "Lasso": a **light-themed** dashboard, flat-on, full frame, green scatter plot, a large `480` KPI. |
| 0:25 | A light dashboard with an isometric floor-plan visual, flat-on, full frame. |
| 0:33 | **Three or four light panels overlapping at a shallow angle**, floating on near-black with a soft glow behind them. |
| 0:44 | The ending: a **4×3 wall of twelve small dashboards**, lit from behind by a warm amber wash. |

Five things I got wrong before looking, and have now corrected in the build:

1. **Panels fill far more of the frame than I had them** — flat-on shots are
   essentially edge to edge. My first pass was ~50%. Now 87%.
2. **Angles are shallow.** The steep rake is used once, for the opening mood
   shot. Information shots are flat-on or within a few degrees.
3. **The ending is a dense wall of many small screens**, not four large ones.
   Rebuilt as twelve tiles.
4. **The light behind the panels is a warm amber pool**, which is the signature
   of the look. Added.
5. **There is almost no overlay text anywhere in the reference.** Your own
   sequence does call for short overlay statements, so I have kept them — but
   this is a real divergence from the reference and you should know it is
   deliberate, not an oversight.

The reference mixes dark-themed and light-themed products. Ours is light-themed,
which matches the 0:18 and 0:25 shots.

### The rule that keeps v2 honest

v1 drew its own numbers, so each had to be re-derived from a CSV. v2 inverts it:
**overlay copy carries no figures**, except two that are traced to source. Every
other number on screen is part of a photograph of the running application. To
change what the film claims, you would have to change what the product shows.

---

## 2. Two beats have no real interface behind them — please decide

### (a) The method switch, 16–24 s

Your sequence asks for a visible interaction that switches Method A → B and
re-ranks the bars. **No control in the application does this:**

- The cockpit's **"Method view"** selectbox changes one sentence
  (`app/app.py:234`) and nothing else.
- `charts.turbine_comparison` always draws **all three methods as grouped bars
  sorted by turbine name**. It never re-sorts.
- The lab's selectbox is **"Method for the recovery heatmap"** — it drives the
  heatmap, not the ranking.

v1 could show a re-ranking because it drew its own bars. A product film showing
a toggle that reorders the chart would be showing an interaction that does not
exist — the same class of error as inventing a metric.

**What I built** (style frame 4): the camera pushes into the real grouped-bar
chart, which already contains the finding. Under A, R80790 is tallest (6.15%);
under B, R80711 is (5.35%). Both in one real chart, whose own title reads
*"the priority changes with the method."*

- **(a1) Keep the real chart.** Honest; the chart makes the point itself. *Recommended.*
- **(a2) Add the control to the application**, then re-capture. Better product,
  but it changes `app/` — outside the "only touch `video/`" boundary.
- **(a3) Draw the re-ranking as an explicit annotation** over the real chart,
  labelled as a graphic rather than as the product responding.

### (b) The timestamp figures, 4–10 s

Your sequence asks to reveal *48 duplicates → 0, 48 absent → 0, seasonal lag
−1 h → 0*. On the real Data trust page:

- The **48 → 0** counts appear **only as prose inside a collapsed expander**
  ("Why the summer timestamps were an hour early"). I have captured the real
  click that opens it (`datatrust_expander.png`) but have not used it yet.
- The **lag chart shows something different from the brief**: best lag is
  **winter −1 h, summer −2 h before correction, and both −1 h after**. So what
  goes to zero is the **seasonal difference between them**, not a lag of −1 h.
  The chart's own caption says: *"Published: winter and summer differ by one
  hour. Corrected: they agree."*

The full film must not animate "−1 h → 0" as if the chart showed it. My proposal
is the **expander + chart treatment**: cursor opens the expander (a real click I
already have), camera pans to the lag chart. Please approve or redirect.

### (c) One wording change I made on your behalf

Your brief says *"672 MWh of apparent underperformance."* The application
renders **671.6 MWh** in the same frame, so an overlay reading 672 would
contradict the screen behind it. I used **671.6**. Say the word and I will
change it back.

### (d) One line of placeholder copy

*"The basis is a choice, not a given."* is **not from your sequence** — it is
placeholder copy for the prototype's interaction beat, and maps to your
**10–16 s "Scope the exposure"** beat. It needs your wording or approval.

---

## 3. What was built

```
video/
  scripts/v2/capture_app.mjs        drives headless Chrome, captures the app
  scripts/v2/verify_v2_claims.py    39 checks on everything v2 asserts
  src/v2/theme.ts                   the dark room
  src/v2/screens.ts                 typed access to captures + measured boxes
  src/v2/grid.ts                    the twelve-tile closing montage
  src/v2/components/Film.tsx        Environment, Camera, ScreenPanel, Spotlight,
                                    Ring, Cursor, Scrim, overlay copy
  src/v2/StyleFrames.tsx            the six frames below
  src/v2/Prototype.tsx              the 11.6 s prototype
  src/v2/Root.tsx, index.ts         separate entry point — v1's Root is untouched
  src/v2/assets/screens/            6 captures + boxes.json
  out/v2/style/                     six 1080x1350 PNGs
  out/v2/prototype-11s.mp4          540x674, 11.65 s
  out/v2/comparison/                v1 beside v2, two matched beats
```

v1 and v2 render from different entry points:

```bash
npx remotion render src/index.ts    WindDecisionSupport out/wind-decision-support-40s.mp4
npx remotion render src/v2/index.ts V2Prototype         out/v2/prototype-11s.mp4
```

### The six style frames

| # | Beat | What is on screen |
|---|---|---|
| 1 | Product cold open | Whole cockpit incl. sidebar; ring on the 2015 accounting row |
| 2 | Data trust | The real ERA5 seasonal-alignment chart, published vs corrected |
| 3 | Scope the exposure | Accounting row with **Missing energy / unknown** spotlit |
| 4 | Challenge the method | The real grouped-bar ranking chart, A/B/C per turbine |
| 5 | Investigation | The neighbour chart **plus** the event's own evidence block — observed facts, hypotheses, required records, escalation criteria |
| 6 | Product reveal | Twelve-tile montage, warm backlight, title, attribution |

**Panel coverage: 87% of frame in every style frame** (measured as the panel
bounding box over frame area), inside your 70–90% target. The prototype runs at
a median of 83%, dipping to 36% only during the closing pull-back, which is the
point of a pull-back.

### The prototype — 11.65 s, 348 frames

| Frames | Beat | Contains |
|---|---|---|
| 0–95 | Cold open | Panel arrives out of depth; push-in to the accounting row |
| 96–191 | Real interaction | Cursor travels to **Energy basis**, clicks *Gross residual shortfall*; panel swaps to the post-click capture; camera pulls back |
| 192–287 | **Screen-to-screen travel** | Camera dollies from the cockpit to the Investigation explorer **with both pages on screen while it travels**, then pushes into the neighbour chart |
| 288–347 | Product reveal | Pull back into the twelve-tile montage |

The click is real. Before it the caption reads *"persistent reviewable events of
380.8 MWh is an illustrative €30,466"*; after it, *"gross residual shortfall of
671.6 MWh is an illustrative €53,731"*, and the ranking chart's metric changes
from % of potential to MWh. The four headline metrics are **identical** in both
states (671.6 / 380.8 / 290.8 / unknown) — I verified that rather than assuming
it, because an apparently-changing headline number would have been a real defect.

---

## 4. Screens and repository assets used

### Streamlit screens captured (`src/v2/assets/screens/`)

| Capture | Page | State | Size |
|---|---|---|---|
| `cockpit.png` | Executive cockpit | default controls | 2880×6190 |
| `cockpit_gross.png` | Executive cockpit | after a real click on *Gross residual shortfall* | 2880×6270 |
| `datatrust.png` | Data trust | default | 2880×4352 |
| `datatrust_expander.png` | Data trust | after a real click opening *"Why the summer timestamps were an hour early"* | 2880×5066 |
| `lab.png` | Method and scenario lab | default | 2880×4326 |
| `explorer.png` | Investigation explorer | default, event detail visible | 2880×6406 |

`boxes.json` holds the browser's own measurement of 30 named elements. The
cursor and every highlight are positioned from those numbers, so they land on
real controls.

### Repository assets the captures depend on

The application reads `outputs/tables/*.csv` only. Visible in the film:

`energy_accounting.csv` · `phase3_turbine_comparison.csv` ·
`decision_event_register.csv` · `decision_event_timelines.csv` ·
`presentation_event_neighbour_comparison.csv` · `timestamp_alignment_test.csv` ·
`presentation_data_funnel.csv` · `cleaning_reconciliation.csv` ·
`presentation_monthly_completeness.csv` · `presentation_missing_runs.csv` ·
`presentation_validation_summary.csv` · `phase3_synthetic_injection.csv` ·
`phase3_event_overlap.csv` · `presentation_reference_curves.csv`

Palette carried from `app/content.py` via `src/v2/theme.ts`. Type: Inter
(SIL OFL 1.1). **No raw or processed site data is in `video/`.**

---

## 5. Verification

- **41/41** v1 figure checks still pass — v1 is untouched.
- **39/39** v2 claim checks pass (`scripts/v2/verify_v2_claims.py`). What they
  actually prove:
  - every number appearing in overlay copy is **found by scanning the source**
    and traced to a table — currently only `671.6` and `2,074`, both from
    `energy_accounting.csv`;
  - the film's qualification lines **are present in the film's own copy**, and
    the wording they use **also appears in `app/content.py` or `app/app.py`**;
  - forbidden language ("lost revenue", "root cause", "confirmed loss", …) is
    absent; independence and licence attribution are present;
  - all six captures exist, all 30 measured elements resolve, and the clicked
    control exists in `app/app.py`.
- Prototype QA: 348 frames, 30 fps, no frozen stretch ≥ 2 s, panel coverage
  median 83%.
- `git status` outside `video/` is clean. Nothing committed.

### Defects found and fixed during this build

1. **Every panel rendered twice.** Inside the camera's 3D context
   `overflow: hidden` did not clip the image, so a clipped panel and an
   unclipped copy drew over each other. Fixed with `clipPath`.
2. **Scenes never unmounted.** I passed `duration` where Remotion expects
   `durationInFrames`, so all four scenes stacked up.
3. **White overlay copy over white interface.** Added a top/bottom scrim.
4. **Blank frames at cuts** — the same class of bug caught in v1. Every scene
   now opens with the product already on screen.
5. **A verification check that could never fail.** A shell heredoc turned a
   regex escape into a literal backspace byte, so the overlay scan matched
   nothing and passed on an empty set. Once fixed it immediately caught two real
   problems (an HTML entity being read as a figure, and a line-wrapped
   qualification the check could not see).

---

## 6. Open items for the full build

- **§2 (a), (b), (c), (d)** all need your decision.
- **Sound.** Not built, and not in the prototype list. The full film needs either
  procedural interface sounds (a soft click on the cursor press, a low riser into
  each push-in) or a licensed track you supply. I will not fetch music. LinkedIn
  autoplays muted, so it must still work silent.
- **Streamlit chrome.** The *Deploy* button and ⋮ menu are visible top-right in
  wide shots. They are honestly part of the app; I can crop them if you prefer.
- **Overlay text load.** The reference uses almost none. Yours asks for a
  statement per beat. If you want to move further toward the reference, the
  statements could drop to three or four across the whole film.
- **Duration.** The prototype is 11.65 s. The full sequence is 40–42 s.
