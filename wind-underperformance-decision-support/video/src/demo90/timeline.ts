/**
 * Every timing in the film, in one place.
 *
 * Two rules are enforced by how these windows are written, and checked by
 * scripts/demo90/verify_demo_claims.py:
 *
 *   * a label only appears after the chart it describes has finished moving;
 *   * method A reaches the baseline completely before method B begins to rise.
 *
 * Frames, at 30fps.
 */

export const SCENES = {
  conclusion: {from: 0, to: 360},      //  0.0 - 12.0
  context: {from: 360, to: 690},       // 12.0 - 23.0
  dataTrust: {from: 690, to: 1080},    // 23.0 - 36.0
  scope: {from: 1080, to: 1470},       // 36.0 - 49.0
  method: {from: 1470, to: 1890},      // 49.0 - 63.0
  model: {from: 1890, to: 2190},       // 63.0 - 73.0
  evidence: {from: 2190, to: 2490},    // 73.0 - 83.0
  decision: {from: 2490, to: 2670},    // 83.0 - 89.0
} as const;

export const FILM_FRAMES = SCENES.decision.to; // 2670 = 89.0s

/** Geometry moves. Each pair is [start, end]. */
export const MOVE = {
  // Scene 1 - the conclusion
  expand: [14, 110],
  markEvent: [238, 322],          // the event interval is marked inside the window
  // Scene 2 - context
  crush: [368, 432],
  collect: [428, 488],
  solidify: [484, 518],
  // Scene 3 - data trust
  disperse: [664, 726],          // column marks -> timestamp strip
  seasonsIn: [734, 792],         // season bars rise
  correctSummer: [862, 922],     // summer lag moves to match winter
  intervalsIn: [920, 968],      // 48 + 48 interval marks appear
  intervalsClear: [976, 1028],  // and leave, one at a time
  // Scene 4 - scope
  seasonsOut: [1088, 1134],      // season bars crush away
  regather: [1130, 1196],        // strip -> gross column
  split: [1262, 1322],           // gross -> its two components
  unknownIn: [1330, 1364],       // the unscaled placeholder arrives
  // Scene 5 - method
  toBaseline: [1480, 1526],      // components flatten onto the baseline
  riseA: [1522, 1576],
  crushA: [1656, 1700],          // completes before riseB begins
  riseB: [1714, 1768],
  // Scene 6 - model
  toBenchmark: [1900, 1958],
  burdenIn: [2054, 2096],
  // Scene 7 - back to the event
  toSignals: [2198, 2244],
  rebuildChart: [2240, 2306],
  drawLines: [2306, 2396],
  // Scene 8 - decision
  toCards: [2498, 2556],
} as const;

/** Copy and value timings. Each is [in, out] or [in] for "stays". */
export const COPY = {
  eyebrow: [2, 2660],
  conclusion: [128, 334],
  evidenceRow: [158, 334],
  action: [232, 340],

  grossLabel: [528, 656],
  question: [580, 656],

  publishedLags: [798, 856],
  summerSnap: 892,
  correctedLags: [926, 1040],
  intervalLabels: [972, 1058],
  trustCaption: [984, 1072],

  grossAgain: [1200, 1262],
  partsLabel: [1336, 1452],
  scopeCaption: [1352, 1456],

  methodALabel: [1588, 1652],
  methodBLabel: [1776, 1872],
  methodCaption: [1792, 1876],
  julyNote: [1812, 1876],

  recoveryLabels: [1968, 2172],
  burdenLabel: [2102, 2176],
  modelCaption: [1998, 2048],
  modelVerdict: [2110, 2180],

  eventStats: [2404, 2476],
  eventCaption: [2342, 2400],
  causeUnknown: [2412, 2478],

  cards: [2560, 2616],
  closing: [2600, 2668],
} as const;
