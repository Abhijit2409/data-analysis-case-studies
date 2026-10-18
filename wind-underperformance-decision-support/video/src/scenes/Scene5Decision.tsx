import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Body, Eyebrow, Headline, Qualifier, Reveal, Stage} from '../components/Primitives';
import {COLOURS, TYPE} from '../theme';
import data from '../data/video_data.json';

/**
 * Scene 5 (29.0-36.0s) - Decision support.
 *
 * The required records are rendered as a short visual checklist rather than a
 * paragraph. They come from the decision register's own
 * operational_records_required field, split on its semicolons - including
 * "operator logs", which is present in that field.
 *
 * No confidence classification appears here: the gloss around it is not a
 * repository string, and the evidence gap below already carries the limitation.
 */

const shortLabels: Record<string, string> = {
  'Turbine event and alarm codes for the interval': 'Event and alarm codes',
  'work orders and maintenance records': 'Work orders and maintenance records',
  'curtailment or grid instructions': 'Curtailment or grid instructions',
  'operator logs': 'Operator logs',
};

const RecordRow: React.FC<{at: number; label: string}> = ({at, label}) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [at, at + 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        padding: '18px 0',
        borderBottom: `1px solid ${COLOURS.rule}`,
        opacity: progress,
        transform: `translateX(${(1 - progress) * 14}px)`,
      }}
    >
      {/* An empty box: the record is required, not held. */}
      <div
        style={{
          width: 26,
          height: 26,
          border: `2.5px solid ${COLOURS.warn}`,
          borderRadius: 4,
          flexShrink: 0,
        }}
      />
      <div style={{fontSize: TYPE.body, color: COLOURS.ink, fontWeight: 500}}>{label}</div>
    </div>
  );
};

export const Scene5Decision: React.FC = () => {
  const {recommendation} = data;
  const labels = recommendation.requiredRecords.map(
    (raw) => shortLabels[raw] ?? raw.charAt(0).toUpperCase() + raw.slice(1),
  );

  return (
    <Stage>
      <Reveal at={0} durationInFrames={0}>
        <Eyebrow>Step four &#183; Act</Eyebrow>
      </Reveal>

      <div style={{height: 22}} />

      <Reveal at={0} durationInFrames={0}>
        <Headline size={TYPE.hero}>
          Investigate
          <br />
          {recommendation.turbine} first.
        </Headline>
      </Reveal>

      <div style={{height: 18}} />

      <Reveal at={20}>
        <Body size={TYPE.body} tone={COLOURS.muted}>
          Flagged by all three methods &#183; {recommendation.methodsAgreeing}
        </Body>
      </Reveal>

      <div style={{height: 46}} />

      <Reveal at={36}>
        <Body size={TYPE.body} tone={COLOURS.ink} style={{fontWeight: 650}}>
          Required before any diagnosis:
        </Body>
      </Reveal>

      <div style={{height: 8}} />

      {/* An unticked box could be misread as a task list. This says plainly that
          the boxes mark evidence the project does not hold. */}
      <Reveal at={42} shift={8}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 10,
            border: `1.5px solid ${COLOURS.warn}`,
            borderRadius: 4,
            padding: '8px 14px',
            fontSize: TYPE.micro,
            fontWeight: 620,
            letterSpacing: 0.4,
            color: COLOURS.warn,
            textTransform: 'uppercase',
          }}
        >
          Operational evidence required &#8212; not available
        </div>
      </Reveal>

      <div style={{height: 14}} />

      {labels.map((label, index) => (
        <RecordRow key={label} at={56 + index * 12} label={label} />
      ))}

      <div style={{flex: 1}} />

      <Qualifier at={112}>
        Potential shortfall is not confirmed recoverable energy. No cause has been
        established.
      </Qualifier>
    </Stage>
  );
};
