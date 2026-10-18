/**
 * Typed access to the captured application screens.
 *
 * Every image here is a photograph of the running Streamlit application, taken
 * by scripts/v2/capture_app.mjs. Every box is the browser's own measurement of
 * a real element, in the capture's CSS pixel space. Placing a cursor or a
 * spotlight from these numbers puts it on the actual control, which is the
 * whole point: the film must not point at interface that does not exist.
 */
import manifest from './assets/screens/boxes.json';

import cockpit from './assets/screens/cockpit.png';
import cockpitGross from './assets/screens/cockpit_gross.png';
import datatrust from './assets/screens/datatrust.png';
import datatrustExpander from './assets/screens/datatrust_expander.png';
import lab from './assets/screens/lab.png';
import explorer from './assets/screens/explorer.png';

export type Box = {x: number; y: number; w: number; h: number};
export type ScreenName = keyof typeof IMAGES;

const IMAGES = {
  cockpit,
  cockpit_gross: cockpitGross,
  datatrust,
  datatrust_expander: datatrustExpander,
  lab,
  explorer,
} as const;

/** Width of every capture, in its own CSS pixels. The sidebar occupies 0-312. */
export const CAPTURE_WIDTH = manifest.viewport.width;

/** The application's content column, excluding the sidebar and the right gutter. */
export const CONTENT = {x: 360, w: 1020} as const;

export const screen = (name: ScreenName) => {
  const entry = (manifest.screens as Record<string, {
    cssWidth: number; cssHeight: number; page: string; state: string;
    boxes: Record<string, Box | null>; clicked?: Box; control?: string;
  }>)[name];
  if (!entry) throw new Error(`no capture named ${name}`);
  return {...entry, src: IMAGES[name]};
};

/** A measured element, or a clear failure rather than a silently wrong position. */
export const box = (name: ScreenName, key: string): Box => {
  const found = screen(name).boxes[key];
  if (!found) throw new Error(`capture ${name} has no box for ${key}`);
  return found;
};

/** Where a real click was made to produce this capture. */
export const clicked = (name: ScreenName): Box => {
  const found = screen(name).clicked;
  if (!found) throw new Error(`capture ${name} records no click`);
  return found;
};

/** Grows a box outward, so a spotlight has breathing room around its subject. */
export const pad = (b: Box, by: number, byY = by): Box => ({
  x: b.x - by, y: b.y - byY, w: b.w + by * 2, h: b.h + byY * 2,
});

/** The smallest box containing all of them - used to frame a row of metrics. */
export const union = (...boxes: Box[]): Box => {
  const x = Math.min(...boxes.map((b) => b.x));
  const y = Math.min(...boxes.map((b) => b.y));
  return {
    x, y,
    w: Math.max(...boxes.map((b) => b.x + b.w)) - x,
    h: Math.max(...boxes.map((b) => b.y + b.h)) - y,
  };
};

export const SCREEN_LIST = Object.keys(IMAGES) as ScreenName[];

/**
 * One bar of the grouped method-comparison chart, by method and turbine.
 *
 * The capture records where the browser actually drew each rectangle, so a
 * callout naming "Method A, R80790" points at that bar and no other.
 */
export const bar = (name: ScreenName, method: 'A' | 'B' | 'C', turbine: string): Box => {
  const entry = screen(name) as unknown as {
    bars?: Box[][];
    barOrder?: {traces: string[]; points: string[]};
  };
  if (!entry.bars || !entry.barOrder) throw new Error(`capture ${name} has no bar measurements`);
  const traceIndex = entry.barOrder.traces.findIndex((t) => t.startsWith(method + '_'));
  const pointIndex = entry.barOrder.points.indexOf(turbine);
  if (traceIndex < 0 || pointIndex < 0) throw new Error(`no bar for ${method}/${turbine}`);
  return entry.bars[traceIndex][pointIndex];
};

/**
 * The crop height that makes a panel fill `coverage` of a 1080x1350 frame when
 * drawn at `width`. Keeps every scene at the same visual weight without
 * hand-tuning each one.
 */
export const fitHeight = (cropWidth: number, width = 1050, coverage = 0.86) =>
  Math.round((coverage * cropWidth * 1080 * 1350) / (width * width));
