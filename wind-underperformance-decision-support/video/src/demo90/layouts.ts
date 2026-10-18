import {scaleLinear} from 'd3-scale';
import {DATA, type SeriesPoint} from './data';
import type {Point, Rect} from './motion';
import {PLOT, type TurbineName} from './theme';

/**
 * Where every mark sits, in each state the film passes through.
 *
 * A layout turns repository values into geometry and nothing else. The scenes
 * then blend between two layouts, which is what makes a transition read as the
 * same evidence reorganising rather than as a cut to a different picture.
 *
 * Every layout returns marks in the same order for the same key, so blending
 * point i of a series always blends the same ten-minute record.
 */

const {neighbours, accounting, methods} = DATA;

// --- scales ----------------------------------------------------------------

export const xTime = scaleLinear()
  .domain([0, neighbours.totalMinutes])
  .range([PLOT.left, PLOT.left + PLOT.width]);

/** Power axis. The domain starts at zero because output cannot be negative. */
export const yPower = scaleLinear()
  .domain([0, Math.ceil(neighbours.maxPower / 250) * 250])
  .range([PLOT.top + PLOT.height, PLOT.top]);

/** Energy axis for the accounting column, in MWh. */
export const yEnergy = scaleLinear()
  .domain([0, Math.ceil(accounting.gross / 100) * 100])
  .range([PLOT.top + PLOT.height, PLOT.top]);

/** Shortfall axis for the method comparison, as a share of potential. */
export const yShortfall = scaleLinear()
  .domain([0, 7])
  .range([PLOT.top + PLOT.height, PLOT.top]);

// --- state 1: the compressed data band -------------------------------------

const BAND = {
  x: PLOT.left + PLOT.width / 2,
  halfWidth: 150,
  y: PLOT.top + PLOT.height / 2,
  gap: 11,
} as const;

/**
 * Every record of one series, squeezed into a narrow horizontal line.
 *
 * This is the film's resting state: all four turbines present, nothing yet
 * claimed about them.
 */
export const bandPoints = (turbine: TurbineName): (Point | null)[] => {
  const series = neighbours.series[turbine];
  const row = neighbours.turbines.indexOf(turbine) - (neighbours.turbines.length - 1) / 2;
  const y = BAND.y + row * BAND.gap;
  return series.map((point, i) => {
    const across = series.length === 1 ? 0.5 : i / (series.length - 1);
    return point.p === null
      ? null
      : {x: BAND.x - BAND.halfWidth + across * BAND.halfWidth * 2, y};
  });
};

// --- state 2: the neighbour comparison -------------------------------------

/**
 * One series at its true position in time and power.
 *
 * A record with no value becomes null, and the path generator leaves a gap
 * there rather than joining across it.
 */
export const neighbourPoints = (turbine: TurbineName): (Point | null)[] =>
  neighbours.series[turbine].map((point: SeriesPoint) =>
    point.p === null ? null : {x: xTime(point.t), y: yPower(point.p)});

/** The shaded interval the event covers, in plot coordinates. */
export const eventWindow = (): Rect => ({
  x: xTime(neighbours.eventStartMinutes),
  y: PLOT.top,
  width: xTime(neighbours.eventEndMinutes) - xTime(neighbours.eventStartMinutes),
  height: PLOT.height,
});

// --- state 3: records collecting into a column -----------------------------

export const COLUMN = {
  x: PLOT.left + PLOT.width / 2 - 120,
  width: 240,
} as const;

/**
 * The same records, packed as a grid inside the gross-energy column.
 *
 * The packing is a visual device for "these observations are what the total is
 * built from". It carries no per-mark quantity, and nothing is labelled until
 * the column has resolved and the published figure can be shown against it.
 */
export const columnPoints = (turbine: TurbineName): (Point | null)[] => {
  const series = neighbours.series[turbine];
  const index = neighbours.turbines.indexOf(turbine);
  const total = neighbours.turbines.length;
  const top = yEnergy(accounting.gross);
  const height = yEnergy(0) - top;
  const columns = 16;
  const rowsPerTurbine = Math.ceil(series.length / columns);
  const bandHeight = height / total;
  const cellX = COLUMN.width / columns;
  const cellY = bandHeight / rowsPerTurbine;
  return series.map((point, i) => {
    if (point.p === null) return null;
    const col = i % columns;
    const row = Math.floor(i / columns);
    return {
      x: COLUMN.x + cellX * (col + 0.5),
      y: top + index * bandHeight + cellY * (row + 0.5),
    };
  });
};

// --- state 4: the energy accounting ----------------------------------------

export type NamedRect = {key: string; rect: Rect; fill: string; hatched?: boolean};

/** The gross column as one solid block. */
export const grossColumn = (): Rect => ({
  x: COLUMN.x,
  y: yEnergy(accounting.gross),
  width: COLUMN.width,
  height: yEnergy(0) - yEnergy(accounting.gross),
});

/**
 * The gross column separated into the parts that actually make it up.
 *
 * The two components sum exactly to the gross figure, which the export asserts,
 * so the split is arithmetic rather than illustration. The missing-data block
 * is hatched and has a FIXED token height that represents nothing: its quantity
 * is unknown and must never be drawn to scale.
 */
export const accountingParts = (): NamedRect[] => {
  const base = yEnergy(0);
  const reviewableHeight = base - yEnergy(accounting.reviewable);
  const nonPersistentHeight = base - yEnergy(accounting.nonPersistent);
  const gap = 300;
  const left = COLUMN.x - gap;
  const right = COLUMN.x + gap;
  return [
    {
      key: 'reviewable', fill: '#2f6ea8',
      rect: {x: left, y: base - reviewableHeight, width: COLUMN.width, height: reviewableHeight},
    },
    {
      key: 'nonPersistent', fill: '#55657a',
      rect: {x: COLUMN.x, y: base - nonPersistentHeight, width: COLUMN.width, height: nonPersistentHeight},
    },
    {
      key: 'missing', fill: 'transparent', hatched: true,
      rect: {x: right, y: base - 150, width: COLUMN.width, height: 150},
    },
  ];
};

// --- state 5: the method comparison ----------------------------------------

const BAR = {width: 150, gap: 130} as const;

/** One bar per turbine under one method, keyed by turbine so bars persist. */
export const methodBars = (method: 'A' | 'B' | 'C'): NamedRect[] => {
  const values = methods.byMethod[method];
  const list = methods.turbines;
  const span = list.length * BAR.width + (list.length - 1) * BAR.gap;
  const startX = PLOT.left + (PLOT.width - span) / 2;
  const base = yShortfall(0);
  return list.map((turbine, i) => {
    const y = yShortfall(values[turbine]);
    return {
      key: turbine,
      fill: '#2f6ea8',
      rect: {x: startX + i * (BAR.width + BAR.gap), y, width: BAR.width, height: base - y},
    };
  });
};

/** The same bars crushed to the baseline, keeping each turbine's slot. */
export const crushedBars = (method: 'A' | 'B' | 'C'): NamedRect[] =>
  methodBars(method).map((bar) => ({
    ...bar,
    rect: {...bar.rect, y: yShortfall(0) - 3, height: 3},
  }));

export const barCentre = (bar: NamedRect) => ({
  x: bar.rect.x + bar.rect.width / 2,
  y: bar.rect.y,
});

// --- the unknown quantity --------------------------------------------------

/**
 * The missing-energy placeholder.
 *
 * It is deliberately NOT a bar. It floats clear of the baseline, sits to the
 * right of a drawn axis break, and has a fixed size that encodes nothing, so
 * its height cannot be read against the energy axis. The quantity is unknown
 * and the drawing has to make that unreadable-as-a-value on purpose.
 */
export const unknownToken = () => {
  const width = 230;
  const height = 120;
  const x = COLUMN.x + 430;
  const y = PLOT.top + PLOT.height / 2 - height / 2 - 40;
  return {
    rect: {x, y, width, height},
    breakX: x - 80,
    breakTop: PLOT.top + 60,
    breakBottom: PLOT.top + PLOT.height,
  };
};

// --- seasonal timestamp alignment ------------------------------------------

/** Lag against ERA5, in hours. Negative, so the axis runs downward from zero. */
export const yLag = scaleLinear()
  .domain([-2.6, 0])
  .range([PLOT.top + PLOT.height - 80, PLOT.top + 120]);

const SEASON = {width: 190, gap: 260} as const;

/**
 * One bar per season, hanging from zero to its best-fit lag.
 *
 * `corrected` swaps summer from its published lag to the corrected one. Winter
 * does not move: the correction removes the DIFFERENCE between the seasons, and
 * both still sit a full hour behind afterwards.
 */
export const seasonBars = (corrected: boolean): NamedRect[] => {
  const t = DATA.timestamps;
  const values: [string, number][] = [
    ['winter', corrected ? t.winterAfter : t.winterBefore],
    ['summer', corrected ? t.summerAfter : t.summerBefore],
  ];
  const span = values.length * SEASON.width + (values.length - 1) * SEASON.gap;
  const startX = PLOT.left + (PLOT.width - span) / 2 - 170;
  const zero = yLag(0);
  return values.map(([key, value], i) => ({
    key,
    fill: key === 'summer' ? '#b5651d' : '#2f6ea8',
    rect: {
      x: startX + i * (SEASON.width + SEASON.gap),
      y: zero,
      width: SEASON.width,
      height: yLag(value) - zero,
    },
  }));
};

/**
 * The duplicate and absent intervals, one mark per interval.
 *
 * Forty-eight marks are drawn because the validation table records forty-eight
 * of each. They leave one at a time, so the count going to zero is something
 * the viewer watches happen rather than reads.
 */
export const intervalMarks = (row: 0 | 1) => {
  const count = row === 0
    ? DATA.timestamps.duplicatesBefore
    : DATA.timestamps.absentBefore;
  const columns = 24;
  const cell = 19;
  const x0 = PLOT.left + PLOT.width - 560;
  const y0 = PLOT.top + 150 + row * 190;
  return Array.from({length: count}, (_, i) => ({
    key: `${row}-${i}`,
    index: i,
    x: x0 + (i % columns) * cell,
    y: y0 + Math.floor(i / columns) * cell,
    size: cell - 6,
  }));
};

// --- detection benchmark ---------------------------------------------------

export const yRecovery = scaleLinear()
  .domain([0, 1])
  .range([PLOT.top + PLOT.height, PLOT.top + 70]);

const BENCH = {width: 200, gap: 230} as const;

/** Recovery for the decision method and the challenger, as published. */
export const benchmarkBars = (): NamedRect[] => {
  const recovery = DATA.benchmark.recovery;
  const entries: ['B' | 'C', number][] = [['B', recovery.B], ['C', recovery.C]];
  const span = entries.length * BENCH.width + (entries.length - 1) * BENCH.gap;
  const startX = PLOT.left + (PLOT.width - span) / 2 - 150;
  const base = yRecovery(0);
  return entries.map(([key, value], i) => ({
    key,
    fill: key === 'C' ? '#b5651d' : '#2f6ea8',
    rect: {
      x: startX + i * (BENCH.width + BENCH.gap),
      y: yRecovery(value),
      width: BENCH.width,
      height: base - yRecovery(value),
    },
  }));
};

/** The share of untouched control windows that still raise an alert. */
export const burdenBand = () => {
  const burden = DATA.benchmark.burdenPct.C / 100;
  const bars = benchmarkBars();
  const left = bars[0].rect.x - 70;
  const right = bars[bars.length - 1].rect.x + bars[bars.length - 1].rect.width + 70;
  return {
    x: left,
    width: right - left,
    y: yRecovery(burden),
    height: yRecovery(0) - yRecovery(burden),
  };
};

// --- operational evidence --------------------------------------------------

/** One card per record the register says is required before a diagnosis. */
export const evidenceCards = () => {
  // Sentence case for consistency. The register's wording is otherwise
  // untouched, so the scope of each request is preserved.
  const items = DATA.event.recordsRequired.map(
    (label) => label.charAt(0).toUpperCase() + label.slice(1));
  const width = 330;
  const gap = 36;
  const span = items.length * width + (items.length - 1) * gap;
  const startX = PLOT.left + (PLOT.width - span) / 2;
  return items.map((label, i) => ({
    key: `card-${i}`,
    label,
    rect: {x: startX + i * (width + gap), y: PLOT.top + 150, width, height: 210},
  }));
};

/**
 * The records spread along a timeline, as timestamp observations rather than
 * as power readings. Used where the film turns from how much energy to when
 * the records say it happened.
 */
export const stripPoints = (turbine: TurbineName): (Point | null)[] => {
  const series = neighbours.series[turbine];
  const row = neighbours.turbines.indexOf(turbine) - (neighbours.turbines.length - 1) / 2;
  const y = PLOT.top + 90 + row * 13;
  const left = PLOT.left + 40;
  const span = PLOT.width - 80;
  return series.map((point, i) => {
    const across = series.length === 1 ? 0.5 : i / (series.length - 1);
    return point.p === null ? null : {x: left + across * span, y};
  });
};
