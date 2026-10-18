/**
 * v2 visual constants - the cinematic product film.
 *
 * v1 put typography on white cards. v2 puts the running application in a dark
 * room and moves a camera around it. So the palette here describes the ROOM,
 * not the product: the application keeps its own light theme, exactly as a
 * viewer would see it on their screen.
 *
 * The illumination colours are the project's own accents (app/content.py)
 * pushed to the brightness a dark environment needs. Nothing new is invented.
 */

export const FPS = 30;

export const LAYOUT = {
  width: 1080,
  height: 1350,
  // Overlay copy stays inside this margin. Panels deliberately do not - they
  // are meant to fill most of the frame and bleed past the edges.
  safe: 72,
} as const;

/** The room. */
export const ROOM = {
  base: '#0b0e13',
  rise: '#1a2330',
  deep: '#06080b',
  panelEdge: 'rgba(255, 255, 255, 0.10)',
  panelEdgeLit: 'rgba(255, 255, 255, 0.22)',
  scrim: 'rgba(7, 9, 13, 0.74)',
} as const;

/** Illumination, derived from the application palette. */
export const LIGHT = {
  blue: '#2f6ea8',
  teal: '#2f8a86',
  amber: '#b5651d',
  amberLit: '#e08a33',
} as const;

/** Text on the dark environment. */
export const TEXT = {
  bright: '#f4f7fa',
  body: '#b9c4d0',
  muted: '#7d8a99',
  amber: '#e2a05d',
} as const;

/** Carried across from app/content.py so a turbine keeps one colour. */
export const TURBINES = {
  R80711: '#1f4e79',
  R80721: '#6a8caf',
  R80736: '#8c8c8c',
  R80790: '#b5651d',
} as const;

/**
 * Overlay type. Larger than v1's: there is far less of it, it sits over a
 * moving image, and it must read at a thumb's distance in the feed.
 */
export const TYPE = {
  statement: 62,
  secondary: 38,
  lower: 32,
  micro: 27,
  title: 66,
} as const;

export const FONT_STACK =
  'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
