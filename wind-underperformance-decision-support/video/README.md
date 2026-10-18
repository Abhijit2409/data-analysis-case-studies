# Video — Wind Underperformance Decision Support

The primary film is an **89-second data-native demo** for a hiring manager:
1920×1080, 30 fps, built with [Remotion](https://www.remotion.dev/).

Every analytical graphic in it is drawn as SVG from the project's published
tables. No chart is a screenshot, and no chart is a picture of a chart — bars,
lines, points, axes and labels are independently controllable marks bound to
repository values.

This folder is self-contained. It reads the project's published tables and
writes nothing back: no analytical script, dataset, output or document outside
`video/` is touched.

---

## The film

| | |
|---|---|
| Composition | `WindDemo90` |
| Entry point | `src/demo90/index.ts` |
| Output | `out/demo90/wind-underperformance-demo90.mp4` |
| Format | 1920×1080, 30 fps, H.264 |
| Duration | **exactly 89.000 s — 2670 frames** |
| Audio | synthesised ambient and transition design; a silent cut is produced for narration |
| Narration | `VOICEOVER_SCRIPT.md` — first-person script to exact timecodes |
| Verification | `DEMO90_VERIFICATION.md` |

It runs conclusion-first: the recommendation, its evidence and its limitation
are all on screen inside the first twelve seconds, and the rest of the film
shows the work behind them.

---

## Build

```bash
cd video
npm install
```

### 1. Export the data the film draws from

```bash
npm run demo:data
```

Reads `outputs/tables/*.csv` and writes `src/demo90/data/demo_data.json`. Every
mark in the film is bound to a value in that file, so a figure cannot drift
between the analysis and the animation.

### 2. Generate the soundtrack

```bash
npm run demo:audio
```

Writes `src/demo90/assets/soundtrack.wav`. **Every sample is synthesised by
arithmetic** — no recordings, no samples, no third-party material, nothing to
licence. The script reads the film's own `src/demo90/timeline.ts`, so the sound
cannot drift from the picture.

### 3. Verify

```bash
npm run demo:verify          # 61 data and construction checks
npm run demo:verify:render   # 10 checks on the rendered file
```

The first re-derives every displayed figure from the CSVs independently of the
export, and checks that no chart is a raster image, that marks are data-bound,
that the 279-observation context window is never confused with the
255-observation event, and that the unknown quantity carries no magnitude.

The second decodes the finished MP4 and measures it: label separation in every
frame of both bar scenes, blank frames, frozen stretches, frame-edge clipping.

### 4. Preview

```bash
npm run demo:preview
```

Opens Remotion Studio on the demo entry point.

### 5. Render

```bash
npm run demo:render          # master, with soundtrack
npm run demo:render:silent   # identical visuals, no audio stream
```

The silent cut is for recording narration over. Both share the same video
stream — it is copied, not re-encoded.

---

## How the charts are built

- **SVG only.** `<path>`, `<rect>` and `<text>`, positioned by d3 scales over
  the exported JSON.
- **Stable keys.** A series carries `key={turbine}` and a method bar
  `key={bar-${turbine}}`, so the same machine is the same element before and
  after a morph.
- **Gaps stay gaps.** `brokenPath` emits no geometry where a record has no
  value, so a line is never drawn across a missing observation.
- **Figures never tween.** Geometry interpolates; a published value appears at
  its verified figure, and where one value replaces another it does so while the
  text is invisible. No intermediate number is ever shown, because an
  intermediate would be a number the repository does not contain.
- **One continuous composition.** The same records travel between every chart,
  so a transition is the same evidence reorganising rather than a cut to a
  different picture.

---

## What the film claims, and what it does not

These boundaries are enforced by the verification, not just by intent:

- The shortfall is **potential shortfall against a statistical reference**. It is
  never described as confirmed loss or as recoverable energy.
- The missing-energy quantity is **unknown**. It is drawn as a detached,
  dashed placeholder beyond an axis break, at a fixed size that consults no
  scale, so its height cannot be read as an energy value.
- The timestamp correction removes the **seasonal inconsistency**. Both seasons
  still sit one hour behind ERA5 afterwards; the film never implies the absolute
  lag reaches zero, and does not attribute the remaining lag to any cause.
- The method comparison is **prioritisation, not diagnosis**. The application's
  real grouped chart is used; nothing re-sorts and no method control is invented.
- Neighbouring turbines producing through the interval is **corroborating
  evidence that wind was available**. It is not proof of a fault, of causation,
  or of identical conditions at each turbine.
- The challenger model's improved recovery is shown **with the alert burden it
  carries**, and the conclusion is that it was not deployable — not that it
  failed technically.
- **Cause: unknown.** No operational diagnosis is established anywhere.

Independent portfolio case study. Public ENGIE La Haute Borne data, Etalab Open
Licence 2.0, via OpenOA. Not Clir Renewables software, data or methodology.

---

## Legacy films

Two earlier cuts remain in the repository as legacy versions. They are kept for
reference and still build, but the 89-second demo above is the current film.

| Film | Composition | Entry point |
|---|---|---|
| 40-second silent LinkedIn cut, 1080×1350 | `WindDecisionSupport` | `src/index.ts` |
| 42-second product film, 1080×1350 | `WindDecisionFilmV2` | `src/v2/index.ts` |

```bash
npm run legacy:data              # v1 figures
npm run legacy:verify            # 41 v1 figure checks
npm run legacy:v2:capture        # re-capture the Streamlit screens v2 uses
npm run legacy:v2:verify         # 60 v2 claim checks
npm run legacy:render            # v1 render
npm run legacy:v2:render         # v2 render
```

The v2 film animates captures of the Streamlit application, which is why its
screen PNGs are tracked; `legacy:v2:capture` regenerates them from a running
app at `http://localhost:8515`.

---

## What is tracked

Rendered output is reproducible, so only the two published deliverables are
committed:

- `out/demo90/wind-underperformance-demo90.mp4`
- `out/demo90/contact-sheet.png`

Drafts, prototypes, duplicate masters, the silent cut, QA frame sequences,
generated WAV soundtracks and `node_modules/` are all ignored. Everything needed
to rebuild them from scratch is tracked.
