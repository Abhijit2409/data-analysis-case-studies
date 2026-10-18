/**
 * Visual constants.
 *
 * The turbine and method colours are the application's own palette, carried
 * across from app/content.py through the data export so that a machine keeps
 * the same colour in the tool, the static figures and this video.
 *
 * Type sizes are set for a phone-sized LinkedIn feed. At 1080x1350 displayed on
 * a ~390pt-wide screen the frame is roughly one third of its rendered size, so
 * body copy below ~34px becomes uncomfortable. Nothing here goes under that.
 */

export const COLOURS = {
  ink: '#14181d',
  body: '#4a5560',
  muted: '#8c8c8c',
  faint: '#c9c9c9',
  rule: '#e4e4e4',
  surface: '#ffffff',
  surfaceAlt: '#f6f7f9',
  accent: '#1f4e79',
  warn: '#b5651d',
  warnWash: 'rgba(181, 101, 29, 0.09)',
  good: '#2f6b4f',
} as const;

export const TURBINES = {
  R80711: '#1f4e79',
  R80721: '#6a8caf',
  R80736: '#8c8c8c',
  R80790: '#b5651d',
} as const;

export const TYPE = {
  hero: 78,
  headline: 60,
  subhead: 44,
  stat: 68,
  body: 36,
  caption: 30,
  micro: 26,
} as const;

export const LAYOUT = {
  width: 1080,
  height: 1350,
  margin: 86,
} as const;

export const FPS = 30;

/** Scene boundaries in seconds, matching the approved storyboard. */
export const SCENES = {
  hook: {from: 0, duration: 4},
  dataTrust: {from: 4, duration: 5},
  ranking: {from: 9, duration: 9},
  event: {from: 18, duration: 11},
  decision: {from: 29, duration: 7},
  close: {from: 36, duration: 4},
} as const;

export const toFrames = (seconds: number) => Math.round(seconds * FPS);
