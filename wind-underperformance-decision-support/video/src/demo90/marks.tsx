import React from 'react';
import {AbsoluteFill} from 'remotion';
import {brokenPath, type Point, type Rect} from './motion';
import {FONT, FRAME, INK, MONO, PLOT, ROOM, TYPE} from './theme';

/**
 * The drawing primitives.
 *
 * Everything the viewer reads as a chart is SVG built from data: a path from
 * records, a rect from a published value, a tick from a scale. No chart here is
 * a picture of a chart.
 */

// --- environment -----------------------------------------------------------

export const Backdrop: React.FC<{children: React.ReactNode}> = ({children}) => (
  <AbsoluteFill style={{
    background: `radial-gradient(120% 95% at 50% 10%, ${ROOM.rise} 0%, ${ROOM.base} 55%, ${ROOM.deep} 100%)`,
    fontFamily: FONT,
  }}>
    {children}
    <AbsoluteFill style={{
      pointerEvents: 'none',
      background: 'radial-gradient(115% 80% at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.5) 100%)',
    }} />
  </AbsoluteFill>
);

export const Stage: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width={FRAME.width} height={FRAME.height}
    style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
    <defs>
      {/* Used for the unknown quantity: visibly present, deliberately not to scale. */}
      <pattern id="unknown" width={12} height={12} patternUnits="userSpaceOnUse"
        patternTransform="rotate(45)">
        <rect width={12} height={12} fill="rgba(226,160,93,0.07)" />
        <line x1={0} y1={0} x2={0} y2={12} stroke="rgba(226,160,93,0.5)" strokeWidth={2.5} />
      </pattern>
    </defs>
    {children}
  </svg>
);

// --- data marks ------------------------------------------------------------

/**
 * One series as a single path, broken wherever a record has no value.
 *
 * `clipWidth` reveals the line left to right without altering the data: the
 * whole series is always in the path, only how much is uncovered changes.
 */
export const SeriesPath: React.FC<{
  id: string;
  points: (Point | null)[];
  colour: string;
  width?: number;
  opacity?: number;
  clipWidth?: number;
}> = ({id, points, colour, width = 3, opacity = 1, clipWidth}) => {
  const d = brokenPath(points);
  const clipId = `reveal-${id}`;
  return (
    <g opacity={opacity}>
      {clipWidth === undefined ? null : (
        <clipPath id={clipId}>
          <rect x={PLOT.left - 40} y={0} width={clipWidth + 40} height={FRAME.height} />
        </clipPath>
      )}
      <path
        d={d}
        fill="none"
        stroke={colour}
        strokeWidth={width}
        strokeLinejoin="round"
        strokeLinecap="round"
        clipPath={clipWidth === undefined ? undefined : `url(#${clipId})`}
      />
    </g>
  );
};

/** The same records drawn as individual marks, for the compressed states. */
export const SeriesDots: React.FC<{
  points: (Point | null)[];
  colour: string;
  radius?: number;
  opacity?: number;
}> = ({points, colour, radius = 2.2, opacity = 1}) => (
  <g opacity={opacity} fill={colour}>
    {points.map((point, i) =>
      point === null ? null : (
        <circle key={i} cx={point.x} cy={point.y} r={radius} />
      ))}
  </g>
);

export const BarRect: React.FC<{
  rect: Rect; fill: string; opacity?: number; hatched?: boolean; radius?: number;
}> = ({rect, fill, opacity = 1, hatched = false, radius = 3}) => (
  <rect
    x={rect.x} y={rect.y} width={rect.width} height={Math.max(0, rect.height)}
    rx={radius}
    fill={hatched ? 'url(#unknown)' : fill}
    stroke={hatched ? 'rgba(226,160,93,0.65)' : 'none'}
    strokeWidth={hatched ? 2 : 0}
    opacity={opacity}
  />
);

// --- axes ------------------------------------------------------------------

export const AxisBase: React.FC<{y: number; opacity?: number}> = ({y, opacity = 1}) => (
  <line x1={PLOT.left} y1={y} x2={PLOT.left + PLOT.width} y2={y}
    stroke={ROOM.rule} strokeWidth={1.5} opacity={opacity} />
);

export const AxisY: React.FC<{
  ticks: number[]; scale: (v: number) => number; format: (v: number) => string;
  opacity?: number; unit?: string;
}> = ({ticks, scale, format, opacity = 1, unit}) => (
  <g opacity={opacity}>
    {ticks.map((value) => (
      <g key={value}>
        <line x1={PLOT.left} y1={scale(value)} x2={PLOT.left + PLOT.width} y2={scale(value)}
          stroke={ROOM.grid} strokeWidth={1} />
        <text x={PLOT.left - 18} y={scale(value) + 6} textAnchor="end"
          fill={INK.muted} fontSize={TYPE.axis} fontFamily={MONO}>
          {format(value)}
        </text>
      </g>
    ))}
    {unit ? (
      <text x={PLOT.left} y={PLOT.top - 28} textAnchor="start"
        fill={INK.faint} fontSize={TYPE.axis} fontFamily={FONT}>
        {unit}
      </text>
    ) : null}
  </g>
);

export const AxisCategories: React.FC<{
  items: {key: string; x: number; label: string; colour?: string}[];
  y: number; opacity?: number;
}> = ({items, y, opacity = 1}) => (
  <g opacity={opacity}>
    {items.map((item) => (
      <text key={item.key} x={item.x} y={y + 40} textAnchor="middle"
        fill={item.colour ?? INK.body} fontSize={TYPE.category} fontFamily={MONO}>
        {item.label}
      </text>
    ))}
  </g>
);

// --- published values ------------------------------------------------------

/**
 * A published figure.
 *
 * It only ever fades or snaps. There is no counting, no rolling and no
 * intermediate state, because an intermediate would be a number that appears
 * nowhere in the repository.
 */
export const Value: React.FC<{
  x: number; y: number; text: string; opacity: number;
  size?: number; colour?: string; anchor?: 'start' | 'middle' | 'end'; weight?: number;
}> = ({x, y, text, opacity, size = TYPE.value, colour = INK.bright,
       anchor = 'middle', weight = 700}) => (
  <text x={x} y={y} textAnchor={anchor} opacity={opacity}
    fill={colour} fontSize={size} fontWeight={weight} fontFamily={FONT}
    style={{letterSpacing: -0.5}}>
    {text}
  </text>
);

export const Label: React.FC<{
  x: number; y: number; text: string; opacity: number;
  size?: number; colour?: string; anchor?: 'start' | 'middle' | 'end';
}> = ({x, y, text, opacity, size = TYPE.label, colour = INK.muted, anchor = 'middle'}) => (
  <text x={x} y={y} textAnchor={anchor} opacity={opacity}
    fill={colour} fontSize={size} fontWeight={520} fontFamily={FONT}>
    {text}
  </text>
);

// --- screen copy -----------------------------------------------------------

export const Headline: React.FC<{
  children: React.ReactNode; opacity: number; lift?: number; top?: number;
}> = ({children, opacity, lift = 0, top = 92}) => (
  <div style={{
    position: 'absolute', left: PLOT.left, right: 110, top,
    opacity, transform: `translateY(${lift}px)`,
    fontSize: TYPE.headline, fontWeight: 700, lineHeight: 1.1,
    letterSpacing: -1.6, color: INK.bright, fontFamily: FONT,
  }}>
    {children}
  </div>
);

/** The caption track. Always present when something is being claimed. */
export const Caption: React.FC<{
  children: React.ReactNode; opacity: number; tone?: string;
}> = ({children, opacity, tone = INK.body}) => (
  <div style={{
    position: 'absolute', left: PLOT.left, right: 110, bottom: 74,
    opacity, fontSize: TYPE.statement, fontWeight: 600, lineHeight: 1.22,
    letterSpacing: -0.8, color: tone, fontFamily: FONT,
  }}>
    {children}
  </div>
);

/** The qualification line, under the caption. */
export const Note: React.FC<{children: React.ReactNode; opacity: number}> = ({
  children, opacity,
}) => (
  <div style={{
    position: 'absolute', left: PLOT.left, right: 110, bottom: 36,
    opacity, fontSize: TYPE.caption, lineHeight: 1.4, color: INK.muted,
    fontFamily: FONT,
  }}>
    {children}
  </div>
);

export const Eyebrow: React.FC<{children: React.ReactNode; opacity: number}> = ({
  children, opacity,
}) => (
  <div style={{
    position: 'absolute', left: PLOT.left, top: 56, opacity,
    fontSize: TYPE.caption, fontWeight: 650, letterSpacing: 2.6,
    textTransform: 'uppercase', color: INK.faint, fontFamily: FONT,
  }}>
    {children}
  </div>
);

/**
 * A published figure that changes to a different published figure.
 *
 * It fades out, swaps, and fades back in. There is deliberately no counting
 * between the two: every intermediate would be a number the repository does not
 * contain. The swap happens while the text is invisible.
 */
export const SnapValue: React.FC<{
  x: number; y: number; before: string; after: string;
  switchAt: number; frame: number; opacity: number;
  size?: number; colour?: string; anchor?: 'start' | 'middle' | 'end';
}> = ({x, y, before, after, switchAt, frame, opacity, size = TYPE.value,
       colour = INK.bright, anchor = 'middle'}) => {
  const blink = Math.min(
    Math.abs(frame - switchAt) / 7,
    1,
  );
  return (
    <Value
      x={x} y={y}
      text={frame >= switchAt ? after : before}
      opacity={opacity * blink}
      size={size} colour={colour} anchor={anchor}
    />
  );
};

/** A dashed, detached placeholder for a quantity that is not known. */
export const UnknownToken: React.FC<{
  rect: Rect; opacity: number; breakX: number; breakTop: number; breakBottom: number;
}> = ({rect, opacity, breakX, breakTop, breakBottom}) => (
  <g opacity={opacity}>
    {/* An explicit axis break: everything to the right of it is off the scale. */}
    <path
      d={`M ${breakX} ${breakTop} L ${breakX} ${breakBottom}`}
      stroke={INK.faint} strokeWidth={1.5} strokeDasharray="7 9" fill="none"
    />
    <path
      d={`M ${breakX - 13} ${breakBottom - 26} l 13 -13 l 0 26 l 13 -13`}
      stroke={INK.faint} strokeWidth={2} fill="none" strokeLinejoin="round"
    />
    {/* Floating clear of the baseline, with a size that encodes nothing. */}
    <rect
      x={rect.x} y={rect.y} width={rect.width} height={rect.height}
      rx={10} fill="url(#unknown)"
      stroke={INK.amber} strokeWidth={2} strokeDasharray="10 7"
    />
  </g>
);

/** A labelled card, used for the operational records the decision needs. */
export const EvidenceCard: React.FC<{
  rect: Rect; label: string; opacity: number; lift?: number;
}> = ({rect, label, opacity, lift = 0}) => (
  <g opacity={opacity} transform={`translate(0 ${lift})`}>
    <rect x={rect.x} y={rect.y} width={rect.width} height={rect.height} rx={12}
      fill="rgba(255,255,255,0.035)" stroke={ROOM.rule} strokeWidth={1.5} />
    <rect x={rect.x} y={rect.y} width={5} height={rect.height}
      rx={2.5} fill={INK.amber} />
    <foreignObject x={rect.x + 26} y={rect.y + 26}
      width={rect.width - 52} height={rect.height - 52}>
      <div style={{
        fontFamily: FONT, fontSize: 25, lineHeight: 1.3, color: INK.bright,
        fontWeight: 560,
      }}>
        {label}
      </div>
    </foreignObject>
  </g>
);
