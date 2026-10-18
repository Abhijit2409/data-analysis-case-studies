import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {COLOURS, LAYOUT, TYPE} from '../theme';

/**
 * Shared building blocks.
 *
 * Motion here is restrained on purpose: short fades and small vertical moves,
 * nothing that spins, bounces or draws attention to itself. The brief asks for
 * purposeful animation, which in practice means the movement should carry the
 * reading order and then stop.
 */

/** Fade and lift a block into place, then hold it still. */
export const Reveal: React.FC<{
  at: number;
  children: React.ReactNode;
  shift?: number;
  durationInFrames?: number;
  style?: React.CSSProperties;
}> = ({at, children, shift = 22, durationInFrames = 14, style}) => {
  const frame = useCurrentFrame();
  const progress =
    durationInFrames <= 0
      ? Number(frame >= at)
      : interpolate(frame, [at, at + durationInFrames], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
  return (
    <div
      style={{
        opacity: progress,
        transform: `translateY(${(1 - progress) * shift}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Fade a block out again, so a scene can retire one message before the next. */
export const FadeOut: React.FC<{
  at: number;
  children: React.ReactNode;
  durationInFrames?: number;
}> = ({at, children, durationInFrames = 10}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [at, at + durationInFrames], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return <div style={{opacity}}>{children}</div>;
};

/** Count a number up to its final value. Used only for figures from the data. */
export const CountUp: React.FC<{
  at: number;
  to: number;
  from?: number;
  decimals?: number;
  durationInFrames?: number;
  suffix?: string;
  style?: React.CSSProperties;
}> = ({at, to, from = 0, decimals = 0, durationInFrames = 20, suffix = '', style}) => {
  const frame = useCurrentFrame();
  const value = interpolate(frame, [at, at + durationInFrames], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <span style={style}>
      {value.toFixed(decimals)}
      {suffix}
    </span>
  );
};

/** The scene surface. Every scene sits on the same white field. */
export const Stage: React.FC<{children: React.ReactNode; padded?: boolean}> = ({
  children,
  padded = true,
}) => (
  <div
    style={{
      position: 'absolute',
      inset: 0,
      background: COLOURS.surface,
      padding: padded ? LAYOUT.margin : 0,
      display: 'flex',
      flexDirection: 'column',
      fontFamily: 'Inter, system-ui, sans-serif',
      color: COLOURS.ink,
    }}
  >
    {children}
  </div>
);

/** Small uppercase label that names what a scene is doing. */
export const Eyebrow: React.FC<{children: React.ReactNode; tone?: string}> = ({
  children,
  tone = COLOURS.accent,
}) => (
  <div
    style={{
      fontSize: TYPE.micro,
      letterSpacing: 3.4,
      textTransform: 'uppercase',
      fontWeight: 650,
      color: tone,
    }}
  >
    {children}
  </div>
);

export const Headline: React.FC<{
  children: React.ReactNode;
  size?: number;
  style?: React.CSSProperties;
}> = ({children, size = TYPE.headline, style}) => (
  <div
    style={{
      fontSize: size,
      lineHeight: 1.16,
      fontWeight: 700,
      letterSpacing: -0.9,
      color: COLOURS.ink,
      ...style,
    }}
  >
    {children}
  </div>
);

export const Body: React.FC<{
  children: React.ReactNode;
  size?: number;
  tone?: string;
  style?: React.CSSProperties;
}> = ({children, size = TYPE.body, tone = COLOURS.body, style}) => (
  <div style={{fontSize: size, lineHeight: 1.44, color: tone, fontWeight: 450, ...style}}>
    {children}
  </div>
);

/**
 * The qualification strip.
 *
 * Every scene that shows a figure also carries the sentence that bounds what the
 * figure means. It is deliberately the same treatment each time so a viewer
 * learns to look for it.
 */
export const Qualifier: React.FC<{at: number; children: React.ReactNode}> = ({
  at,
  children,
}) => (
  <Reveal at={at} shift={12}>
    <div
      style={{
        borderLeft: `4px solid ${COLOURS.warn}`,
        background: COLOURS.warnWash,
        padding: '20px 26px',
        fontSize: TYPE.caption,
        lineHeight: 1.42,
        color: COLOURS.body,
        fontWeight: 450,
      }}
    >
      {children}
    </div>
  </Reveal>
);

/** A spring that settles quickly, for bars that move to a new position. */
export const useSettle = (at: number) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({
    frame: frame - at,
    fps,
    config: {damping: 200, mass: 0.7},
  });
};
