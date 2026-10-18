# Wind Underperformance Decision Support — 89-second demo

Verification report. Nothing committed, pushed or merged. The 42-second product
film, its prototype and v1 are untouched and still pass their own checks.

---

## 1. Deliverables

| File | Size | Audio |
|---|---|---|
| `out/demo90/wind-underperformance-demo90.mp4` | 10,622,851 bytes (10.1 MiB) | synthesised ambient + transition design |
| `out/demo90/wind-underperformance-demo90-silent.mp4` | 8,776,059 bytes (8.4 MiB) | **no audio stream at all** |
| `out/demo90/contact-sheet.png` | 1940×1107 | 89 frames, one per second |
| `out/demo90/frames/*.png` | 1920×1080 | 16 stills, every scene |
| `VOICEOVER_SCRIPT.md` | — | first-person narration to exact timecodes |

**Both: 1920×1080, 30 fps, exactly 89.000 s, 2670 frames, H.264.** The two files
share the same video stream, copied not re-encoded — per-frame packet sizes hash
identically (`d37e2da1…`).

---

## 2. The two factual corrections

### The display window is not the event

The export now carries both counts separately and the film uses only the second:

| | |
|---|---|
| Plotted across the displayed context window | **279** observations per turbine |
| Inside the highlighted 42.5-hour event | **255** observations per turbine |

Five automated assertions cover this:

- context counts per turbine re-derived from the table and compared;
- event counts per turbine re-derived from `inside_event` and compared;
- **the two counts are required to be disjoint** — if they ever became the same
  number the check fails;
- every event observation is required to lie inside the event window, and the
  event set must be strictly smaller than the window set (1,020 of 1,116 rows);
- **`279` is required to appear nowhere in the film as a displayed figure**, and
  the displayed event figure is required to come from `recordsInsideEvent`.

The film additionally *shows* the distinction: in scene 1 the event interval
wipes in across the wider plotted window, so the viewer sees the highlighted
part is a subset of what is drawn.

Displayed event evidence: 42.5 hours · 255 consecutive event records · 97.65% of
R80711 event observations at or below zero · all three neighbours producing
throughout.

### The unknown quantity has no magnitude

The missing-energy placeholder is **not a bar**. It is a dashed, hatched token
that:

- floats vertically centred in the plot and never touches the baseline;
- sits to the right of a **drawn axis break** with a break glyph;
- has a fixed 230 × 120 size that consults no scale — six checks confirm the
  layout function contains no `yEnergy` and no `scale` call;
- is labelled `unknown`, `Quantity unknown` and `not plotted to scale`.

Its height cannot be read against the energy axis, because it is not on that
axis.

---

## 3. Construction

- **No raster chart anywhere.** A check greps every `.ts`/`.tsx` under
  `src/demo90/` for `<img>`, `<Img>` or a `.png` import. There are none.
- Charts are `<path>`, `<rect>` and `<text>` from d3 scales over the exported
  JSON.
- Stable keys: series carry `key={turbine}`, method bars `key={bar-${turbine}}`,
  so a machine is the same element before and after a morph.
- `brokenPath` leaves a gap where a record has no value, so a missing
  observation produces no geometry.
- **No figure is typed into the film.** A check scans the composition for
  numeric literals and fails on any that is not an axis tick.

### Source tables

`energy_accounting.csv` · `phase3_turbine_comparison.csv` ·
`presentation_event_neighbour_comparison.csv` · `decision_event_register.csv` ·
`timestamp_alignment_test.csv` · `timestamp_correction_validation.csv` ·
`phase3_synthetic_injection.csv`. `app/content.py` supplies the palette only.

---

## 3b. The label-collision correction

The reported collision in `s5-11-method-B.png` — `R80721` and `R80736` running
together — **is not present in the rendered film.** Measured from the delivered
still: each label is 86 px wide with **194 px of clear space between adjacent
labels**, in Method A, during the baseline crush and in settled Method B. The
same holds at every display width from 1920 px down to 192 px. The most likely
explanation is the image being viewed scaled down somewhere between here and
your screen.

The corrections were applied regardless, because more separation costs nothing:

- category labels dropped from 25 px to **22 px** (`TYPE.category`), which
  widens the gap further and is one of the options you listed;
- labels nudged 2 px further below the baseline.

Settled gaps are now **204–205 px** against **75–76 px** labels.

A permanent check was added — `scripts/demo90/verify_render.py` — which measures
ink in the label band of the rendered frames and requires at least 40 px of
clear space between adjacent labels in **every frame of both bar scenes**,
during the morph as well as at rest. Building it surfaced two measurement traps
worth recording, because either would have produced a false result:

1. The y-axis tick shares that band. Scanning the full width counted `0%` as a
   category label. The scan now starts at the plot's left edge.
2. While labels fade in, one or two antialiased pixels cross the ink threshold
   and read as separate "labels" 38 px apart. Runs narrower than 25 px are now
   discarded as fragments rather than measured as labels.

The check reports the tightest gap it found, so a future regression shows up as
a number rather than as a pass.

## 4. Checks

**61/61 data and construction checks pass** (`scripts/demo90/verify_demo_claims.py`),
covering: every displayed figure re-derived independently from the CSVs; the
context/event distinction; the unknown placeholder; vector construction; the
method morph ordering; and label timing.

Two of those deserve naming, because they were required and both initially failed:

- **Method A reaches the baseline before method B rises.** The crush ends at
  frame 1700 and the rise begins at 1714 — a 14-frame gap, asserted.
- **A label appears only after its chart settles.** Eleven chart/label pairs are
  checked. The interval counts originally appeared 34 frames early, while their
  marks were still arriving; the check caught it and the timing was corrected.

**10/10 render checks pass** (`scripts/demo90/verify_render.py`), over all 2,670
frames at full resolution:

- 2670 frames at 1920×1080
- method comparison: adjacent labels keep a clear gap — tightest **204 px**
- detection benchmark: adjacent labels keep a clear gap — tightest **67 px**
- method A settled: four separate turbine labels, gaps 204/205/204 px
- method B settled: four separate turbine labels, gaps 205/205/205 px
- no blank frame
- no frozen stretch of 2 s or more
- no frame renders before its content is ready
- nothing touches the frame edge — no axis, unit or label is clipped
- the first frame carries data marks

`git status` outside `video/` is clean.

### Defects found and fixed during this build

1. The flattened accounting slabs were never hidden and sat on the baseline for
   the rest of the film.
2. The gross figure was held across scene 3, where its column is not on screen.
3. The interval counts were labelled before their marks had arrived.
4. The event figures collided with the caption.
5. The film opened on eight identical frames; the signals now converge into the
   band from frame zero.
6. Scene 2 held still for 2.5 s; a measuring line now travels the column while
   the question is on screen, carrying no value of its own.
7. Scene 7 reformed the chart in full and then clipped it back to nothing before
   drawing on, which read as a reset. The records now travel into place as
   marks, and the line draws across them once they have settled.

### Corrections in this pass

- Category-label typography reduced and separation verified (§3b).
- The voiceover line attributing the remaining one-hour lag to the sensor was
  replaced. The project establishes that the seasons disagreed and that the
  correction removes the disagreement; it does **not** establish what causes the
  constant one-hour relationship that remains. The script now says only that the
  seasonal inconsistency was the clock problem, and the recording notes say why.
  The on-screen wording was already correct and is unchanged.
- Evidence-card labels put into sentence case. Only the leading character
  changed — the register's own wording is otherwise intact, so the scope of each
  request is preserved. Card one therefore still reads "Turbine event and alarm
  codes for the interval" rather than being shortened.

---

## 5. Audio

**Origin: every sample is synthesised by `scripts/demo90/make_audio.py`.** No
recordings, no samples, no loops, no third-party material — nothing to licence.
The script reads the film's own `timeline.ts`, so the sound cannot drift from
the picture.

| Element | How it is made |
|---|---|
| Ambient bed | two sine drones a fifth apart (55 Hz, 82.5 Hz), 0.035 Hz tremolo, low-passed noise |
| Transitions | low-passed noise with a downward sweep, one per scene change, starting 0.3 s before the cut |
| Data marks | a soft tone with harmonics at the method A leader, the method B leader, and the alert burden |
| Closing settle | a low two-tone arrival under the title |

Peak −14.0 dBFS, RMS −26.2 dBFS, 89.000 s — exactly matching 2670 frames at
30 fps. No alarms, no risers. **The film is built to be understood with the
sound off.**

The silent version carries no audio stream at all, ready for the narration in
`VOICEOVER_SCRIPT.md`. No synthetic narrator voice was generated.
