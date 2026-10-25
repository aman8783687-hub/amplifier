import React from "react";
import { Composition } from "remotion";
import { Reel } from "./Reel";
import { FPS, TOTAL_FRAMES } from "./lib/cues";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="DiwaliSareeReel"
      component={Reel}
      durationInFrames={TOTAL_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
    />
  );
};
