/**
 * Visual constants for the 90-second hiring-manager demo.
 *
 * Landscape 1920x1080, built to be read on a laptop rather than a phone, and
 * to be understood with the sound off.
 *
 * The turbine and method colours are the project's own, carried from
 * app/content.py, so a machine keeps one colour in the tool, the static
 * figures and every film.
 */

export const FPS = 30;

export const FRAME = {width: 1920, height: 1080} as const;

/** The restrained cinematic environment the charts sit in. */
export const ROOM = {
  base: '#0a0d12',
  rise: '#141c26',
  deep: '#05070a',
  grid: 'rgba(255, 255, 255, 0.07)',
  rule: 'rgba(255, 255, 255, 0.16)',
} as const;

export const INK = {
  bright: '#f2f6fa',
  body: '#b4c0cd',
  muted: '#7a8795',
  faint: '#4d5967',
  amber: '#e2a05d',
  good: '#59b089',
} as const;

/** Carried from app/content.py. */
export const TURBINES = {
  R80711: '#2f6ea8',
  R80721: '#6a8caf',
  R80736: '#8c8c8c',
  R80790: '#b5651d',
} as const;

/** Marks the bar under discussion. Deliberately not one of the method colours. */
export const HIGHLIGHT = '#d98a3d';

export const METHOD_COLOUR = {
  A: '#8c9aa8',
  B: '#2f6ea8',
  C: '#b5651d',
} as const;

export type TurbineName = keyof typeof TURBINES;

/**
 * The plotting area every chart is laid out in. Keeping one box across all
 * scenes is what lets a mark travel from one chart to the next without a cut.
 */
export const PLOT = {
  left: 230,
  top: 236,
  width: 1460,
  height: 620,
} as const;

/** The column to the right of the plot where evidence assembles. */
export const SIDE = {
  left: PLOT.left + PLOT.width + 90,
  width: 1920 - (PLOT.left + PLOT.width + 90) - 110,
} as const;

export const TYPE = {
  headline: 62,
  statement: 46,
  subhead: 32,
  label: 25,
  category: 22,
  value: 54,
  caption: 21,
  axis: 19,
} as const;

export const FONT =
  'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

export const MONO =
  '"SF Mono", "Cascadia Mono", "Roboto Mono", Consolas, monospace';
