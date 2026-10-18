import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {loadFont} from '@remotion/google-fonts/Inter';
import {Scene1Hook} from './scenes/Scene1Hook';
import {Scene2DataTrust} from './scenes/Scene2DataTrust';
import {Scene3Ranking} from './scenes/Scene3Ranking';
import {Scene4Event} from './scenes/Scene4Event';
import {Scene5Decision} from './scenes/Scene5Decision';
import {Scene6Close} from './scenes/Scene6Close';
import {COLOURS, SCENES, toFrames} from './theme';

// Inter via @remotion/google-fonts: a pinned, licence-safe dependency (Inter is
// SIL Open Font License 1.1). The font is bundled at build time, so rendering
// does not depend on a network fetch or on a locally installed typeface.
const {fontFamily} = loadFont();

/**
 * The 40-second cut. Scene boundaries live in theme.ts so the storyboard timing
 * and the composition cannot drift apart.
 *
 * Silent by design: every message is on screen, and the video is intended to
 * work in a muted feed. See README for where to mount an audio track.
 */
export const WindDecisionSupport: React.FC = () => (
  <AbsoluteFill style={{background: COLOURS.surface, fontFamily}}>
    {Object.entries({
      hook: Scene1Hook,
      dataTrust: Scene2DataTrust,
      ranking: Scene3Ranking,
      event: Scene4Event,
      decision: Scene5Decision,
      close: Scene6Close,
    }).map(([key, Component]) => {
      const {from, duration} = SCENES[key as keyof typeof SCENES];
      return (
        <Sequence key={key} from={toFrames(from)} durationInFrames={toFrames(duration)}>
          <Component />
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
