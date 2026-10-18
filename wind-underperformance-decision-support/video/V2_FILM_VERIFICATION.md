# Wind Underperformance Decision Support — v2 product film

Verification report. Nothing is committed, pushed or merged. v1 and the approved
v2 prototype are untouched and still render from their own entry points.

---

## 1. Deliverables

| File | Size | Audio |
|---|---|---|
| `out/v2/wind-decision-support-v2.mp4` | 28,502,168 bytes (27.2 MiB) | AAC-LC 48 kHz stereo |
| `out/v2/wind-decision-support-v2-silent.mp4` | 27,631,052 bytes (26.3 MiB) | **no audio stream at all** |
| `out/v2/contact-sheet.png` | 1920x1512 | 84 frames, one every 0.5 s |
| `out/v2/stills/*.png` | 1080x1350 each | ten stills, every scene |

**Both: 1080 x 1350, 30 fps, exactly 42.000 s, 1260 frames, H.264 High profile.**

The two files share **the same video stream, copied not re-encoded** — the
per-frame packet sizes hash identically (`472ff420…`), so the visuals are
bit-identical. The contact sheet and every still are generated from the final
encoded MP4, not from a draft.

---

## 2. Sequence

| Scene | Frames | Time | Application shown |
|---|---|---|---|
| 1 Cinematic opening | 0–119 | 0.0–4.0 | Executive cockpit, whole page |
| 2 Data trust | 120–299 | 4.0–10.0 | Data trust: ERA5 alignment chart, then the timestamp expander opened by a real click |
| 3 Scope the shortfall | 300–479 | 10.0–16.0 | Executive cockpit, 2015 energy accounting |
| 4 Challenge the method | 480–719 | 16.0–24.0 | Executive cockpit, shortfall-per-turbine chart |
| 5 Investigate the event | 720–989 | 24.0–33.0 | Investigation explorer, neighbour comparison and event evidence |
| 6 Decision support | 990–1139 | 33.0–38.0 | Investigation explorer, operational evidence |
| 7 Montage and close | 1140–1259 | 38.0–42.0 | Twelve regions of the four real pages |

---

## 3. The accuracy decisions you set

1. **671.6 MWh, never 672.** The overlay says 671.6 and the application renders
   671.6 in the same frame.
2. **No invented method control.** Nothing re-sorts. Scene 4 dollies into the
   real grouped chart and uses light and callouts to move attention from
   `Method A · R80790 · 6.15%` to `Method B · R80711 · 5.35%`. Both bars are
   present in the chart the whole time. Each callout is anchored to the exact
   rectangle the browser drew for that bar, measured during capture.
3. **The timestamp result is stated as it is.** The chart on screen shows winter
   −1 h and summer −2 h before correction and both at −1 h after. The callout
   reads `48 → 0 duplicate · 48 → 0 absent`, pointing at the paragraph of the
   application that says exactly that. The lower third says the *seasonal
   difference* is gone. **Nothing in the film says or implies the lag became
   zero.**
4. **The placeholder is gone.** "The basis is a choice, not a given" does not
   appear. Scene 3 uses "Missing is unknown — not zero", with the accounting
   figures as its qualification.
5. **Nothing is fabricated.** Every panel is a photograph of the running
   application; the only two clicks are clicks that were really performed.

---

## 4. Verification

### Numerical

- **60/60 v2 claim checks pass** (`scripts/v2/verify_v2_claims.py`).
- **41/41 v1 figure checks still pass** — v1 untouched.
- Every figure that reaches the screen as overlay copy, a callout or a figure
  strip is found by **scanning the film's own source** and re-derived from the
  repository:

| On screen | Source |
|---|---|
| 671.6 | `energy_accounting.csv` gross positive residual shortfall |
| 380.8 | `energy_accounting.csv` shortfall in persistent candidate events |
| 290.8 | `energy_accounting.csv` non-persistent shortfall |
| 2,074 | `energy_accounting.csv` basis for unmeasured energy |
| 48 → 0 | `timestamp_correction_validation.csv` details |
| 6.15 | `phase3_turbine_comparison.csv`, method A / R80790 |
| 5.35 | `phase3_turbine_comparison.csv`, method B / R80711 |
| 42.5 | `decision_event_register.csv` duration_hours |
| 255 | records inside the event, `presentation_event_neighbour_comparison.csv` |
| 97.65 | share of host records at or below zero, same table |
| 100 | lowest share of records with output across the three neighbours, same table |
| 2015 / 26 / 28 | event year and start/end days from the register |

- **No value is ever tweened.** Nothing counts up; a figure appears at its final
  value or not at all.
- Turbine names shown (R80711, R80790) are checked against the analysis.
- Forbidden assertions ("lost revenue", "root cause", "confirmed loss",
  "recoverable energy of") are absent. The approved qualification
  *"not confirmed loss"* is allowed, and the check distinguishes the negation
  from the assertion.

### Frame-by-frame, all 1,260 frames of the final encode

- no blank frame
- no near-empty frame (every frame is at least 12% lit application content)
- no frozen stretch of 1.5 s or more
- every scene cut lands on a populated frame
- every scene's first frame holds application content, frame 0 included: the
  opening frame shows the whole cockpit, receded in depth, at 40% lit area
- the closing montage never touches a frame edge
- no duplicated panels from overlapping sequences
- audio and video durations match to 0 ms

### Cursor

The pointer press is checked against the measured control: it lands at
(401, 1893) inside the expander header measured at x 417, y 1889, w 281, h 22
— the header box extends left of its text to take in the chevron.

### Panels

Every single-panel scene draws its panel 1050 × 1194 px, which is **86% of the
frame at rest** and more during each push-in. The montage is twelve tiles on a
1006 × 930 grid.

### Type at phone size

A 1080-wide frame shows at roughly 390 pt on a phone:

| Element | px | on a phone |
|---|---|---|
| Primary statement | 62 | 22.4 pt |
| Closing title | 52 | 18.8 pt |
| Figure value | 50 | 18.1 pt |
| Qualification line | 32 | 11.6 pt |
| Closing spine | 29 | 10.5 pt |
| Page label | 27 | 9.8 pt |
| Figure label | 27 | 9.8 pt |
| Closing attribution | 22 | 7.9 pt |

Nothing falls below a 9.5 pt floor except the attribution credit, which is held
to its own 7.5 pt floor. The figure strip is laid out two by two so every label
gets a full line.

### Application chrome

Streamlit's toolbar, deploy button and status widget are hidden by injected CSS
before capture. No browser chrome, development control or loading state appears.

---

## 5. Audio

**Origin: every sample is synthesised by `scripts/v2/make_audio.py`.** There are
no recordings, no samples, no loops and no third-party material, so there is
nothing to licence. The script is in the repository and the file can be rebuilt
from it at any time.

| Element | How it is made |
|---|---|
| Ambient bed | two sine drones a fifth apart (55 Hz and 82.5 Hz) with a 0.045 Hz tremolo, plus low-passed noise |
| Transition whooshes | low-passed noise with a downward sweep, one per scene change, starting 0.28 s before the cut |
| Interface click | two decaying sines at 1.85 and 2.7 kHz, at the one cursor press |
| Emphasis tones | a single soft tone with harmonics and a long tail, at the two method callouts and the event reveal |

Peak −14 dBFS, RMS −25.7 dBFS. No alarms, no risers to a drop, no disaster
effects. **The film is built to be understood muted**; the sound only supports
the motion.

---

## 6. Known limitations

- Scene 4's push-in crops the ranking chart's axis label while it is at its
  closest. The axis title and both callouts stay legible.
- The film shows one event, the top-ranked one. The register holds more.
