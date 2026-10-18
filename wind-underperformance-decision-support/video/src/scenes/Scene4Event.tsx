import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Body, Eyebrow, Headline, Qualifier, Reveal, Stage} from '../components/Primitives';
import {COLOURS, TYPE} from '../theme';
import data from '../data/video_data.json';

/**
 * Scene 4 (18.0-29.0s) - The priority event.
 *
 * Opens on the event-driven qualification so the previous scene's ranking
 * reversal cannot read as the sole reason this event was prioritised, then
 * states that all three methods flag the same interval - which is the actual
 * reason it ranks first.
 *
 * The chart is drawn from presentation_event_neighbour_comparison.csv. A null
 * power value produces a break in the path: the line is never bridged across a
 * missing record, and a missing record is never drawn as zero.
 */

// 1080 wide minus the stage's 86px margins leaves exactly 908px of content.
// The chart fills it; there is no y-axis gutter because there are no y labels.
const CHART = {width: 908, height: 352, left: 0, top: 16};

type Point = {t: number; p: number | null};

/**
 * Build one path per unbroken run of observations.
 *
 * Returning several short paths rather than one long one is what keeps the gaps
 * honest - there is simply no geometry where the data is missing.
 */
const segmentPaths = (
  points: Point[],
  totalMinutes: number,
  maxPower: number,
  revealMinutes: number,
): string[] => {
  const x = (t: number) => CHART.left + (t / totalMinutes) * CHART.width;
  const y = (p: number) => CHART.top + CHART.height - (p / maxPower) * CHART.height;

  const paths: string[] = [];
  let current: string[] = [];

  for (const point of points) {
    if (point.p === null || point.t > revealMinutes) {
      if (current.length > 1) paths.push(`M ${current.join(' L ')}`);
      current = [];
      continue;
    }
    current.push(`${x(point.t).toFixed(1)},${y(point.p).toFixed(1)}`);
  }
  if (current.length > 1) paths.push(`M ${current.join(' L ')}`);
  return paths;
};

const StatChip: React.FC<{at: number; value: string; label: string}> = ({at, value, label}) => (
  <Reveal at={at} shift={14}>
    <div>
      <div
        style={{
          fontSize: 54,
          fontWeight: 740,
          color: COLOURS.ink,
          letterSpacing: -1,
          fontVariantNumeric: 'tabular-nums',
          lineHeight: 1.08,
        }}
      >
        {value}
      </div>
      <div style={{fontSize: TYPE.micro, color: COLOURS.body, lineHeight: 1.3, marginTop: 4}}>
        {label}
      </div>
    </div>
  </Reveal>
);

export const Scene4Event: React.FC = () => {
  const frame = useCurrentFrame();
  const {neighbours, recommendation} = data;

  // The chart draws left to right over ~3.5s, so the eye follows the interval.
  const revealMinutes = interpolate(
    frame,
    [70, 175],
    [0, neighbours.totalMinutes],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  const x = (t: number) => CHART.left + (t / neighbours.totalMinutes) * CHART.width;
  const shadeFrom = x(neighbours.startMinutes);
  const shadeTo = x(neighbours.endMinutes);
  const shadeOpacity = interpolate(frame, [58, 76], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const eventTurbine = neighbours.eventTurbine;
  const hostStats = neighbours.stats[eventTurbine as keyof typeof neighbours.stats];

  return (
    <Stage>
      <Reveal at={0} durationInFrames={0}>
        <Eyebrow tone={COLOURS.warn}>Step three &#183; Investigate</Eyebrow>
      </Reveal>

      <div style={{height: 18}} />

      {/* The event-driven caveat first, then the real reason for prioritising. */}
      <Reveal at={0} durationInFrames={0}>
        <Body size={TYPE.body} tone={COLOURS.body}>
          The ranking is event-driven. Remove this event
          and R80711 falls below R80790.
        </Body>
      </Reveal>

      <div style={{height: 18}} />

      <Reveal at={26}>
        <Headline size={TYPE.subhead}>
          All three methods flag the
          <br />
          same 42.5-hour interval.
        </Headline>
      </Reveal>

      <div style={{height: 14}} />

      <Reveal at={44} shift={10}>
        <Body size={TYPE.caption} tone={COLOURS.muted}>
          {eventTurbine} &#183; {neighbours.startLabel} to {neighbours.endLabel} UTC
        </Body>
      </Reveal>

      <div style={{height: 16}} />

      <svg width={CHART.width} height={CHART.height + CHART.top + 44}>
        {/* Event window */}
        <rect
          x={shadeFrom}
          y={CHART.top}
          width={shadeTo - shadeFrom}
          height={CHART.height}
          fill={COLOURS.warn}
          opacity={0.09 * shadeOpacity}
        />
        {/* Window boundaries, so the shaded band reads as a bounded interval */}
        {[shadeFrom, shadeTo].map((xPos) => (
          <line
            key={xPos}
            x1={xPos}
            x2={xPos}
            y1={CHART.top}
            y2={CHART.top + CHART.height}
            stroke={COLOURS.warn}
            strokeWidth={1.6}
            opacity={0.5 * shadeOpacity}
          />
        ))}
        {/* Zero line */}
        <line
          x1={CHART.left}
          x2={CHART.left + CHART.width}
          y1={CHART.top + CHART.height}
          y2={CHART.top + CHART.height}
          stroke={COLOURS.ink}
          strokeWidth={1.4}
        />
        {/* Neighbours first, event turbine last so it sits on top */}
        {[...neighbours.series]
          .sort((a, b) => Number(a.isEventTurbine) - Number(b.isEventTurbine))
          .map((line) => {
            const paths = segmentPaths(
              line.points as Point[],
              neighbours.totalMinutes,
              neighbours.maxPowerKw,
              revealMinutes,
            );
            return (
              <g key={line.turbine}>
                {paths.map((d, index) => (
                  <path
                    key={index}
                    d={d}
                    fill="none"
                    stroke={line.colour}
                    strokeWidth={line.isEventTurbine ? 4.4 : 2}
                    opacity={line.isEventTurbine ? 1 : 0.72}
                    strokeLinejoin="round"
                  />
                ))}
              </g>
            );
          })}
        {/* Neighbour means as small annotations, not a text block */}
        {[...neighbours.series]
          .filter((line) => !line.isEventTurbine)
          .map((line, index) => {
            const stats = neighbours.stats[line.turbine as keyof typeof neighbours.stats];
            const appear = interpolate(frame, [186 + index * 7, 198 + index * 7], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            return (
              <text
                key={line.turbine}
                x={CHART.left + CHART.width}
                y={CHART.top + 24 + index * 32}
                textAnchor="end"
                fontSize={25}
                fontWeight={620}
                fill={line.colour}
                opacity={appear}
              >
                {line.turbine} &#183; mean {stats.mean_kw} kW
              </text>
            );
          })}
        {/* The event turbine's own annotation, at the zero line */}
        <text
          x={CHART.left + 6}
          y={CHART.top + CHART.height - 18}
          fontSize={25}
          fontWeight={700}
          fill={COLOURS.accent}
          opacity={interpolate(frame, [186, 198], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          })}
        >
          {eventTurbine} &#183; mean {hostStats.mean_kw} kW
        </text>
        <text
          x={CHART.left}
          y={CHART.top + CHART.height + 34}
          fontSize={24}
          fill={COLOURS.muted}
        >
          Active power (kW) &#183; time in UTC
        </text>
      </svg>

      <div style={{height: 10}} />

      {/* Four priority figures only, revealed progressively. */}
      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '22px 30px'}}>
        <StatChip at={204} value={`${recommendation.durationHours} h`} label="Continuous interval" />
        <StatChip at={214} value={`${hostStats.records}`} label="Consecutive records" />
        <StatChip
          at={224}
          value={`${hostStats.at_or_below_zero_pct}%`}
          label={`${eventTurbine} at or below zero`}
        />
        <StatChip at={234} value="100%" label="All three neighbours producing" />
      </div>

      <div style={{flex: 1}} />

      <Qualifier at={252}>
        Neighbouring production confirms simultaneous peer operation; it does not
        identify the cause. Gaps are records with no value &#8212; never zero.
      </Qualifier>
    </Stage>
  );
};
