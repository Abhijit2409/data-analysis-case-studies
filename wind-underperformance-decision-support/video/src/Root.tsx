import React from 'react';
import {Composition} from 'remotion';
import {WindDecisionSupport} from './Video';
import {FPS, LAYOUT} from './theme';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="WindDecisionSupport"
      component={WindDecisionSupport}
      durationInFrames={FPS * 40}
      fps={FPS}
      width={LAYOUT.width}
      height={LAYOUT.height}
    />
  </>
);
