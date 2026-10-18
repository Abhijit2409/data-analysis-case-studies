import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {
  Body,
  Eyebrow,
  Headline,
  Qualifier,
  Reveal,
  Stage,
} from '../components/Primitives';
import {COLOURS, TYPE} from '../theme';
import data from '../data/video_data.json';

/**
 * Scene 2 (4.0-9.0s) - Data trust.
 *
 * Three figures, each read from timestamp_correction_validation.csv via the data
 * export. They roll from their published value to their corrected value.
 *
 * The closing line is load-bearing: it states that this correction preceded the
 * performance work and is a separate matter from the shortfall. The brief
 * requires that the timestamp defect is not implied to have caused anything.
 */

const Figure: React.FC<{
  at: number;
  label: string;
  before: number;
  after: number;
  suffix?: string;
  signed?: boolean;
}> = ({at, label, before, after, suffix = '', signed = false}) => {
  const frame = useCurrentFrame();
  const settled = interpolate(frame, [at + 8, at + 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <Reveal at={at} shift={16}>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto',
          alignItems: 'baseline',
          gap: 24,
          padding: '22px 0',
          borderBottom: `1px solid ${COLOURS.rule}`,
        }}
      >
        <Body size={TYPE.body} tone={COLOURS.body}>
          {label}
        </Body>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 18}}>
          <span
            style={{
              fontSize: TYPE.subhead,
              fontWeight: 600,
              color: COLOURS.muted,
              textDecoration: 'line-through',
              textDecorationColor: COLOURS.warn,
              opacity: 1 - settled * 0.45,
            }}
          >
            {signed && before > 0 ? '+' : ''}
            {before}
            {suffix}
          </span>
          <span style={{fontSize: TYPE.body, color: COLOURS.faint}}>&#8594;</span>
          <span
            style={{
              fontSize: TYPE.stat,
              fontWeight: 720,
              color: COLOURS.good,
              letterSpacing: -1,
              opacity: settled,
            }}
          >
            {/* Faded in at its final value rather than rolled. A rolling counter
                would display intermediate numbers that are not published
                figures. */}
            {after}
            {suffix}
          </span>
        </div>
      </div>
    </Reveal>
  );
};

export const Scene2DataTrust: React.FC = () => {
  const {timestamps} = data;

  return (
    <Stage>
      <Reveal at={0} durationInFrames={0}>
        <Eyebrow>Step one &#183; Data trust</Eyebrow>
      </Reveal>

      <div style={{height: 22}} />

      <Reveal at={0} durationInFrames={0}>
        <Headline size={TYPE.headline}>First, the data
          <br />had to earn trust.</Headline>
      </Reveal>

      <div style={{height: 26}} />

      <Reveal at={14}>
        <Body size={TYPE.body}>
          Timestamps carried valid daylight-saving offsets.
          <br />
          They were still wrong.
        </Body>
      </Reveal>

      <div style={{height: 34}} />

      <Figure at={34} label="Duplicate intervals" before={timestamps.duplicates.before} after={timestamps.duplicates.after} />
      <Figure at={54} label="Absent intervals" before={timestamps.absent.before} after={timestamps.absent.after} />
      <Figure
        at={74}
        label="Seasonal lag vs ERA5"
        before={timestamps.lag.before}
        after={timestamps.lag.after}
        suffix=" h"
        signed
      />

      <div style={{flex: 1}} />

      <Qualifier at={104}>
        Corrected before any performance figure was computed &#8212; and a separate
        matter from the shortfall that follows.
      </Qualifier>
    </Stage>
  );
};
