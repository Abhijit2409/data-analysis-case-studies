import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {Body, Eyebrow, Headline, Qualifier, Reveal, Stage} from '../components/Primitives';
import {COLOURS, TURBINES, TYPE} from '../theme';
import data from '../data/video_data.json';

/**
 * Scene 3 (9.0-18.0s) - The conclusion changes. The longest scene, because the
 * ranking reversal is the analytical core of the case study.
 *
 * Bars are sorted highest-first under each method and physically reorder when
 * the method switches, so the reversal is carried by movement rather than by a
 * caption. Values come from phase3_turbine_comparison.csv.
 *
 * The axis label says "gross potential shortfall", never "loss".
 */

// Method A holds, fades out, and method B fades in. The short gap between them
// is what prevents the two orderings from ghosting through each other.
const FADE_OUT_AT = 118;
const FADE_IN_AT = 126;
const BAR_HEIGHT = 74;
const BAR_GAP = 26;
const MAX_WIDTH = 640;

type Row = {turbine: string; value: number};

const ranked = (rows: Row[]) => [...rows].sort((a, b) => b.value - a.value);

export const Scene3Ranking: React.FC = () => {
  const frame = useCurrentFrame();
  const {ranking} = data;

  const rowsA = ranked(ranking.A);
  const rowsB = ranked(ranking.B);

  // The label swaps on the same ramps as the bars: A clears before B arrives,
  // so the two never overlap and the label always matches the bars below it.
  const labelA = interpolate(frame, [FADE_OUT_AT, FADE_OUT_AT + 8], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const labelB = interpolate(frame, [FADE_IN_AT, FADE_IN_AT + 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const scaleMax = Math.max(...rowsA.map((r) => r.value), ...rowsB.map((r) => r.value));

  const introduce = interpolate(frame, [12, 34], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <Stage>
      <Reveal at={0} durationInFrames={0}>
        <Eyebrow>Step two &#183; Compare</Eyebrow>
      </Reveal>

      <div style={{height: 20}} />

      {/* The method label swaps in place; only one is visible at a time. */}
      <div style={{position: 'relative', height: 132}}>
        <div style={{position: 'absolute', inset: 0, opacity: labelA}}>
          <Headline size={TYPE.subhead}>
            Method A
            <span style={{color: COLOURS.muted, fontWeight: 500}}>
              {' '}&#8212; each turbine
              <br />
              against its own history
            </span>
          </Headline>
        </div>
        <div style={{position: 'absolute', inset: 0, opacity: labelB}}>
          <Headline size={TYPE.subhead}>
            Method B
            <span style={{color: COLOURS.muted, fontWeight: 500}}>
              {' '}&#8212; each turbine
              <br />
              against the fleet
            </span>
          </Headline>
        </div>
      </div>

      <div style={{height: 20}} />

      {/* Each method's ranking is drawn as its own sorted list. Interpolating
          the rows between the two orders made labels cross through one another
          and become unreadable mid-move, so method A fades out, the list is
          rebuilt in the new order, and method B fades in. */}
      <div style={{position: 'relative', height: (BAR_HEIGHT + BAR_GAP) * 4}}>
        {([['A', rowsA], ['B', rowsB]] as const).map(([key, rows]) => {
          const visible =
            key === 'A'
              ? interpolate(frame, [FADE_OUT_AT, FADE_OUT_AT + 8], [1, 0], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                })
              : interpolate(frame, [FADE_IN_AT, FADE_IN_AT + 8], [0, 1], {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                });
          if (visible === 0) return null;
          return (
            <div key={key} style={{position: 'absolute', inset: 0, opacity: visible}}>
              {rows.map((row, slot) => {
                const turbine = row.turbine as keyof typeof TURBINES;
                const isLeader = slot === 0;
                const grow = key === 'A' ? introduce : 1;
                return (
                  <div
                    key={row.turbine}
                    style={{
                      position: 'absolute',
                      top: slot * (BAR_HEIGHT + BAR_GAP),
                      left: 0,
                      right: 0,
                      height: BAR_HEIGHT,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 22,
                    }}
                  >
                    <div
                      style={{
                        width: 168,
                        fontSize: TYPE.body,
                        fontWeight: isLeader ? 700 : 500,
                        color: isLeader ? COLOURS.ink : COLOURS.body,
                        fontVariantNumeric: 'tabular-nums',
                      }}
                    >
                      {row.turbine}
                    </div>
                    <div
                      style={{
                        width: (row.value / scaleMax) * MAX_WIDTH * grow,
                        height: BAR_HEIGHT,
                        background: TURBINES[turbine],
                        opacity: isLeader ? 1 : 0.42,
                        borderRadius: 3,
                      }}
                    />
                    <div
                      style={{
                        fontSize: TYPE.subhead,
                        fontWeight: isLeader ? 760 : 560,
                        color: isLeader ? COLOURS.ink : COLOURS.muted,
                        fontVariantNumeric: 'tabular-nums',
                      }}
                    >
                      {row.value.toFixed(2)}%
                    </div>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>

      <Reveal at={18} shift={8}>
        <Body size={TYPE.micro} tone={COLOURS.muted}>
          Gross potential shortfall (% of potential production)
        </Body>
      </Reveal>

      <div style={{flex: 1}} />

      {/* The explanation arrives only after the bars have reordered. */}
      <div style={{opacity: interpolate(frame, [FADE_IN_AT + 14, FADE_IN_AT + 30], [0, 1], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })}}>
        <Body size={TYPE.body} tone={COLOURS.ink} style={{fontWeight: 600}}>
          R80711&#8217;s own reference sits 11&#8211;19 kW below its
          neighbours&#8217;.
        </Body>
        <div style={{height: 12}} />
        <Body size={TYPE.body}>
          Measured only against itself, its potential shortfall
          was understated.
        </Body>
      </div>

      <div style={{height: 26}} />

      <Qualifier at={FADE_IN_AT + 40}>
        Prioritisation, not diagnosis. No cause is established by either method.
      </Qualifier>
    </Stage>
  );
};
