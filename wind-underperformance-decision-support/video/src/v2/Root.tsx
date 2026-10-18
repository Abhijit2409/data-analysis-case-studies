import React from 'react';
import {Composition} from 'remotion';
import {FILM_FRAMES, WindDecisionFilmV2} from './Film40';
import {PROTOTYPE_FRAMES, V2Prototype} from './Prototype';
import {STYLE_FRAMES} from './StyleFrames';
import {FPS, LAYOUT} from './theme';

/**
 * v2 compositions, registered from their own entry point so the approved v1
 * film in src/Root.tsx is never touched.
 */
export const V2Root: React.FC = () => (
  <>
    {STYLE_FRAMES.map(({id, component}) => (
      <Composition
        key={id}
        id={id}
        component={component}
        durationInFrames={1}
        fps={FPS}
        width={LAYOUT.width}
        height={LAYOUT.height}
      />
    ))}
    <Composition
      id="WindDecisionFilmV2"
      component={WindDecisionFilmV2}
      durationInFrames={FILM_FRAMES}
      fps={FPS}
      width={LAYOUT.width}
      height={LAYOUT.height}
    />
    <Composition
      id="V2Prototype"
      component={V2Prototype}
      durationInFrames={PROTOTYPE_FRAMES}
      fps={FPS}
      width={LAYOUT.width}
      height={LAYOUT.height}
    />
  </>
);
