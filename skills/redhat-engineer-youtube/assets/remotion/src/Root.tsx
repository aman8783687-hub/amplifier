import React from 'react';
import {Composition} from 'remotion';
import {Episode, EpisodeProps} from './Video';
import '@fontsource/anton/400.css';
import '@fontsource/inter/400.css';
import '@fontsource/inter/600.css';
import '@fontsource/inter/800.css';

const empty: EpisodeProps = {
  fps: 24,
  scenes: [],
  phrases: [],
  chapters: [],
  durationInFrames: 240,
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Episode"
      component={Episode}
      durationInFrames={empty.durationInFrames}
      fps={empty.fps}
      width={1920}
      height={1080}
      defaultProps={empty}
      calculateMetadata={({props}) => {
        const p = props as EpisodeProps;
        return {
          durationInFrames: Math.max(1, Math.round(p.durationInFrames)),
          fps: p.fps,
          props: p,
        };
      }}
    />
  );
};
