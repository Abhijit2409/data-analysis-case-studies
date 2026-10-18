# Voiceover script — Wind Underperformance Decision Support

For `video/out/demo90/wind-underperformance-demo90-silent.mp4`
(1920×1080, 30 fps, 89.0 s, 2670 frames).

**How to use this.** Timecodes are where each line should *start*. Every line is
written to be said slowly, with the gaps left in deliberately — the film carries
its own captions, so silence over a chart is not dead air. Total spoken content
is about 215 words across 89 seconds, which is a relaxed pace with room to
breathe.

Read it as yourself explaining a decision to a colleague. Nothing here is a
sales line, and nothing claims more than the analysis supports.

---

## Scene 1 — Conclusion first · 0:00–0:12

> **0:02** — Four turbines, one wind farm, one year of ten-minute records.
>
> **0:05** — This is the one I'd look at first. R80711.
>
> **0:08** — Forty-two and a half hours. Thirty-seven megawatt-hours of
> potential shortfall. Three independent methods agree on the interval.
>
> *(pause)*
>
> **0:10** — But I'd ask for the operational records before calling it a fault.

---

## Scene 2 — Context · 0:12–0:23

> **0:14** — Here's the number that gets you in the room.
>
> **0:17** — Six hundred and seventy-one point six megawatt-hours of apparent
> shortfall across the year.
>
> *(pause)*
>
> **0:20** — The useful question isn't how big it is. It's how much of it I can
> actually trust, and act on.

---

## Scene 3 — Data trust · 0:23–0:36

> **0:25** — Before any of that, the timestamps had to earn their place.
>
> **0:28** — They carried valid daylight-saving offsets. They looked fine.
>
> **0:31** — But winter sat an hour behind the reanalysis and summer sat two.
> That gap shouldn't exist.
>
> **0:34** — Correcting it lines the seasons up, and clears forty-eight
> duplicate and forty-eight absent intervals. After correction, both seasons
> share the same one-hour relationship to ERA5. The seasonal inconsistency — not
> the absolute lag — was the clock problem.

---

## Scene 4 — Scope the shortfall · 0:36–0:49

> **0:38** — So, how much of the six-seven-one is reviewable?
>
> **0:41** — Three hundred and eighty inside events long enough to investigate.
> Two hundred and ninety in short dips that fail the persistence rule.
>
> *(pause)*
>
> **0:45** — And a block of records with no value at all. That quantity is
> unknown. I've drawn it off the scale on purpose, because filling it in with
> zero would invent days of outage that may never have happened.

---

## Scene 5 — Challenge the method · 0:49–1:03

> **0:51** — Now the part that changed my mind.
>
> **0:54** — Judge each turbine against its own history, and R80790 looks like
> the problem.
>
> *(pause)*
>
> **0:58** — Pool the fleet and compare like for like, and R80711 moves to the
> top instead.
>
> **1:01** — Same data. Different reference. Different priority. Worth knowing
> that one event is doing most of the work.

---

## Scene 6 — Reject the model · 1:03–1:13

> **1:05** — I tested a more flexible model against injected events.
>
> **1:07** — Recovery went from 0.771 to 0.818. On its own, that reads as a win.
>
> *(pause)*
>
> **1:10** — Then look at what it costs. Around two in five untouched windows
> would still raise an alert. The model improved — and I still wouldn't put it
> in front of an operations team.

---

## Scene 7 — The event evidence · 1:13–1:23

> **1:15** — Back to the interval the three methods agreed on.
>
> **1:18** — Two hundred and fifty-five consecutive records. R80711 at or below
> zero for ninety-seven and a half percent of them, while all three neighbours
> produced throughout.
>
> *(pause)*
>
> **1:21** — That tells me wind was available. It does not tell me the cause.

---

## Scene 8 — Decision · 1:23–1:29

> **1:24** — So the recommendation is narrow on purpose.
>
> **1:26** — Investigate this one first. Pull the alarm codes, the work orders,
> the curtailment instructions and the operator logs.
>
> **1:28** — Diagnose when the evidence is in. Not before.

---

## Notes for recording

- **Pace.** Around 145 words per minute. If you run short, lengthen the pauses
  rather than speeding up — every pause is placed where the picture is doing
  the explaining.
- **Numbers.** Say them as written. "Six hundred and seventy-one point six" and
  "0.771" are the figures the screen shows; rounding them in the read would put
  the voice and the caption out of step.
- **Tone.** Flat and specific beats enthusiastic. The two lines carrying the most
  weight — *"I still wouldn't put it in front of an operations team"* and *"it
  does not tell me the cause"* — land hardest when they are said plainly.
- **What not to add.** Don't say "loss", "wasted energy" or "root cause". The
  analysis does not support any of them, and the captions are careful about it.
- **The one-hour lag.** Say only that the seasonal inconsistency was the clock
  problem. The project establishes that the seasons disagreed and that the
  correction removes the disagreement. It does **not** establish what causes the
  remaining constant one-hour relationship to ERA5, so the read must not
  attribute it to a sensor, a logger or anything else.
