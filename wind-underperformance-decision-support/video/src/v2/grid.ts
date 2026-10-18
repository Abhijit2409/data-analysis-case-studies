import type {Framing} from './components/Film';

/**
 * The closing montage.
 *
 * Twelve tiles, three from each of the four application pages, so the pull-back
 * lands on a wall of product rather than four large screenshots. Every tile is
 * a different region of a real capture - nothing here is a mock-up or a repeat.
 */
export const MONTAGE: {frame: Framing; label: string}[] = [
  {frame: {screen: 'cockpit', x: 0, w: 1440, y: 0, h: 980}, label: 'Executive cockpit'},
  {frame: {screen: 'cockpit', x: 0, w: 1440, y: 600, h: 980}, label: 'Energy accounting'},
  {frame: {screen: 'cockpit', x: 0, w: 1440, y: 1340, h: 980}, label: 'Leading events'},

  {frame: {screen: 'datatrust', x: 0, w: 1440, y: 0, h: 980}, label: 'Data trust'},
  {frame: {screen: 'datatrust', x: 0, w: 1440, y: 660, h: 980}, label: 'Completeness'},
  {frame: {screen: 'datatrust', x: 0, w: 1440, y: 1180, h: 980}, label: 'Validation'},

  {frame: {screen: 'lab', x: 0, w: 1440, y: 0, h: 980}, label: 'Method lab'},
  {frame: {screen: 'lab', x: 0, w: 1440, y: 400, h: 980}, label: 'Benchmark'},
  {frame: {screen: 'lab', x: 0, w: 1440, y: 1120, h: 980}, label: 'Method overlap'},

  {frame: {screen: 'explorer', x: 0, w: 1440, y: 0, h: 980}, label: 'Investigation'},
  {frame: {screen: 'explorer', x: 0, w: 1440, y: 1380, h: 980}, label: 'Event timeline'},
  {frame: {screen: 'explorer', x: 0, w: 1440, y: 1800, h: 980}, label: 'Neighbours'},
];

/** Tile geometry, sized so the montage fills most of a 1080-wide frame. */
export const TILE = {width: 340, gap: 14, columns: 3} as const;
