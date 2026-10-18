import {interpolate} from 'remotion';

/**
 * The film's motion grammar: compress, reorganise, resolve.
 *
 * A scene does not cut to the next one. Its marks compress toward a neutral
 * shape, travel to where the next chart needs them, and resolve into it. The
 * same evidence is being examined a different way, so the same marks are
 * reused and only their positions change.
 *
 * Nothing here interpolates a NUMBER that a viewer reads. Geometry
 * interpolates; published values only ever fade or snap between verified
 * states. That rule lives in the Value component, and this module never
 * produces a number for display.
 */

/** Slow in, slow out. Every camera and layout move uses this. */
export const ease = (t: number): number =>
  t < 0.5 ? 4 * t * t * t : 1 - (-2 * t + 2) ** 3 / 2;

/** A softer ease for marks settling into place. */
export const easeOut = (t: number): number => 1 - (1 - t) ** 3;

/** Eased 0..1 progress across a frame range. */
export const phase = (frame: number, from: number, to: number): number =>
  ease(interpolate(frame, [from, to], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));

/** Linear 0..1 progress, for opacity where easing would look sluggish. */
export const fade = (frame: number, at: number, length = 12): number =>
  interpolate(frame, [at, at + length], [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/** Appears, holds, then leaves before the next thing arrives. */
export const hold = (frame: number, inAt: number, outAt: number, length = 12): number =>
  Math.min(fade(frame, inAt, length), 1 - fade(frame, outAt, 10));

/** Straight-line blend between two numbers. */
export const mix = (a: number, b: number, t: number): number => a + (b - a) * t;

/**
 * Staggers a group of marks so they do not all move at once.
 *
 * `index` of `count`, spread over `spread` of the available progress. The
 * result is each mark's own 0..1 progress, eased.
 */
export const stagger = (
  t: number, index: number, count: number, spread = 0.45,
): number => {
  if (count <= 1) return easeOut(t);
  const step = spread / (count - 1);
  const start = index * step;
  const local = (t - start) / (1 - spread);
  return easeOut(Math.max(0, Math.min(1, local)));
};

export type Point = {x: number; y: number};

/** Blends two point lists of equal length - the core of a chart morph. */
export const mixPoints = (a: Point[], b: Point[], t: number): Point[] =>
  a.map((pa, i) => {
    const pb = b[i] ?? pa;
    return {x: mix(pa.x, pb.x, t), y: mix(pa.y, pb.y, t)};
  });

export type Rect = {x: number; y: number; width: number; height: number};

/** Blends two rectangles - the core of a bar morph. */
export const mixRect = (a: Rect, b: Rect, t: number): Rect => ({
  x: mix(a.x, b.x, t),
  y: mix(a.y, b.y, t),
  width: mix(a.width, b.width, t),
  height: mix(a.height, b.height, t),
});

/**
 * An SVG path through points, broken wherever a point is absent.
 *
 * This is the load-bearing piece of the neighbour chart: a record with no value
 * is an absence of evidence, and a line drawn across it would invent data. Each
 * unbroken run becomes its own subpath, so a gap has no geometry at all.
 */
export const brokenPath = (points: (Point | null)[]): string => {
  const parts: string[] = [];
  let run: Point[] = [];
  const flush = () => {
    if (run.length === 1) {
      parts.push(`M ${run[0].x.toFixed(2)} ${run[0].y.toFixed(2)} l 0.01 0`);
    } else if (run.length > 1) {
      parts.push('M ' + run.map((p) => `${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(' L '));
    }
    run = [];
  };
  for (const point of points) {
    if (point === null) flush();
    else run.push(point);
  }
  flush();
  return parts.join(' ');
};

/**
 * Reveals a path from left to right by clipping, rather than by trimming the
 * data. The line is always the whole series; only how much of it is uncovered
 * changes, so a partially drawn line never implies a shorter record.
 */
export const revealWidth = (progress: number, width: number): number =>
  Math.max(0, Math.min(1, progress)) * width;
