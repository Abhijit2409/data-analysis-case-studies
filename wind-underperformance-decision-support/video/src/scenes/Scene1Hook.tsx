import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Body, Headline, Reveal, Stage} from '../components/Primitives';
import {COLOURS, TURBINES, TYPE} from '../theme';

/**
 * Scene 1 (0.0-4.0s) - Hook.
 *
 * Four power curves drawn faintly; one resolves into the project's R80711 blue.
 * The curves are illustrative of shape only - no figure is quoted here, so no
 * value needs sourcing. Every number in this video appears from Scene 2 onward,
 * and each of those is read from the exported data.
 */

const curvePath = (offset: number) => {
  // A sigmoid-ish power curve shape. Decorative background only.
  const points: string[] = [];
  for (let i = 0; i <= 60; i += 1) {
    const x = i / 60;
    const y = 1 / (1 + Math.exp(-(x * 12 - 6 - offset * 0.5)));
    points.push(`${(x * 880).toFixed(1)},${(300 - y * 270).toFixed(1)}`);
  }
  return `M ${points.join(' L ')}`;
};

export const Scene1Hook: React.FC = () => {
  const frame = useCurrentFrame();

  // The curves draw on together, then three recede and one holds.
  const draw = interpolate(frame, [6, 46], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const isolate = interpolate(frame, [46, 64], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const turbines = Object.keys(TURBINES) as (keyof typeof TURBINES)[];

  return (
    <Stage>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
        <Reveal at={0} durationInFrames={0}>
          <Headline size={TYPE.hero}>
            A turbine can look
            <br />
            acceptable against
            <br />
            its own history.
          </Headline>
        </Reveal>

        <div style={{height: 56}} />

        <svg width={908} height={310} style={{overflow: 'visible'}}>
          {turbines.map((turbine, index) => {
            const isFocus = turbine === 'R80711';
            const length = 1400;
            return (
              <path
                key={turbine}
                d={curvePath(index)}
                fill="none"
                stroke={isFocus ? TURBINES.R80711 : COLOURS.faint}
                strokeWidth={isFocus ? 3 + isolate * 2.5 : 2.4}
                strokeDasharray={length}
                strokeDashoffset={length * (1 - draw)}
                opacity={isFocus ? 0.45 + isolate * 0.55 : 0.5 - isolate * 0.32}
              />
            );
          })}
        </svg>

        <div style={{height: 50}} />

        <Reveal at={57} shift={18} durationInFrames={12}>
          <Headline size={TYPE.hero} style={{color: COLOURS.warn}}>
            And still be the
            <br />
            wrong priority.
          </Headline>
        </Reveal>
      </div>

      <Reveal at={92} shift={10}>
        <Body size={TYPE.caption} tone={COLOURS.muted}>
          A wind performance case study
        </Body>
      </Reveal>
    </Stage>
  );
};
