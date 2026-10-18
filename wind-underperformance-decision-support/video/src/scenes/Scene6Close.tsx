import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Body, Headline, Reveal, Stage} from '../components/Primitives';
import {COLOURS, TYPE} from '../theme';
import data from '../data/video_data.json';

/**
 * Scene 6 (36.0-40.0s) - Close.
 *
 * The four-step spine, the independence line, and the attribution the public
 * data licence requires.
 */

const STEPS = ['Validate', 'Compare', 'Investigate', 'Act'];

export const Scene6Close: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <Stage>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
        <Reveal at={0} durationInFrames={0}>
          <Headline size={66}>
            Wind Underperformance
            <br />
            Decision Support
          </Headline>
        </Reveal>

        <div style={{height: 54}} />

        {/* The spine arrives one step at a time, left to right. */}
        <div style={{display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap'}}>
          {STEPS.map((step, index) => {
            const at = 20 + index * 11;
            const progress = interpolate(frame, [at, at + 12], [0, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            });
            return (
              <React.Fragment key={step}>
                <div
                  style={{
                    fontSize: 40,
                    fontWeight: 700,
                    color: index === STEPS.length - 1 ? COLOURS.warn : COLOURS.accent,
                    opacity: progress,
                    transform: `translateY(${(1 - progress) * 10}px)`,
                  }}
                >
                  {step}
                </div>
                {index < STEPS.length - 1 ? (
                  <div style={{fontSize: 34, color: COLOURS.faint, opacity: progress}}>
                    &#8594;
                  </div>
                ) : null}
              </React.Fragment>
            );
          })}
        </div>

        <div style={{height: 46}} />

        <Reveal at={66}>
          <div style={{height: 1, background: COLOURS.rule}} />
        </Reveal>

        <div style={{height: 26}} />

        <Reveal at={70}>
          <Body size={TYPE.caption} tone={COLOURS.body}>
            {data.validation.passed} of {data.validation.total} automated checks pass,
            with one documented diagnostic failure retained.
          </Body>
        </Reveal>
      </div>

      <Reveal at={82}>
        <Body size={TYPE.micro} tone={COLOURS.muted} style={{lineHeight: 1.5}}>
          Independent portfolio case study &#8212; not Clir Renewables software,
          data or methodology.
          <br />
          Public data: ENGIE La Haute Borne, Etalab Open Licence 2.0, via OpenOA.
        </Body>
      </Reveal>
    </Stage>
  );
};
