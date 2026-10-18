import React from 'react';
import {Composition} from 'remotion';
import {FILM_FRAMES, WindDemo90} from './Film';
import {MotionPrototype, PROTOTYPE_FRAMES} from './Prototype';
import {FPS, FRAME} from './theme';

/**
 * The demo compositions, on their own entry point so the approved 42-second
 * product film and its prototype are never touched.
 */
export const Demo90Root: React.FC = () => (
  <>
    <Composition
      id="WindDemo90"
      component={WindDemo90}
      durationInFrames={FILM_FRAMES}
      fps={FPS}
      width={FRAME.width}
      height={FRAME.height}
    />
    <Composition
      id="Demo90Prototype"
      component={MotionPrototype}
      durationInFrames={PROTOTYPE_FRAMES}
      fps={FPS}
      width={FRAME.width}
      height={FRAME.height}
    />
  </>
);
