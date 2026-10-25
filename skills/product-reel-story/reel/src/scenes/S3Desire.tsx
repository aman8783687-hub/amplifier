import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C } from "../lib/theme";
import { cue, local } from "../lib/cues";
import { Quote } from "../components/Film";
import { Scrim } from "../components/UI";

/**
 * DESIRE — the only moving shot in the film, slowed down.
 * Two lines, no labels, no numbers.
 */
export const S3Desire: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const fallsAt = local(cue("s3", "falls"), start);
  const kindAt = local(cue("s3", "kind"), start);

  const fadeIn = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 12, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const p = interpolate(frame, [0, durationInFrames], [0, 1]);

  const q1 = spring({ frame: frame - fallsAt, fps, config: { damping: 22, mass: 0.9, stiffness: 70 } });
  const q2 = spring({ frame: frame - kindAt, fps, config: { damping: 22, mass: 0.9, stiffness: 70 } });
  const q1Out = interpolate(frame, [kindAt, kindAt + 10], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const leakX = 78 - 10 * Math.sin(frame / 46);

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, opacity: fadeIn * fadeOut }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <OffthreadVideo
          src={staticFile("video/rampwalk_1440.mp4")}
          startFrom={30}
          playbackRate={0.72}
          muted
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${1.08 - 0.08 * p})`,
            filter: "brightness(1.0) contrast(1.07) saturate(1.03)",
          }}
        />
      </AbsoluteFill>

      {/* warm film grade + drifting window light */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(255,170,90,0.10) 0%, rgba(90,25,20,0.10) 55%, rgba(30,8,6,0.28) 100%)",
          mixBlendMode: "soft-light",
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(36% 26% at ${leakX}% 20%, rgba(255,190,120,0.22), rgba(0,0,0,0) 70%)`,
          mixBlendMode: "screen",
        }}
      />

      <Scrim strength={0.9} />

      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          bottom: 560,
          opacity: q1 * q1Out,
          transform: `translateY(${(1 - q1) * 26}px)`,
        }}
      >
        <Quote size={94}>
          falls like
          <br />
          <span style={{ color: C.goldLight }}>water.</span>
        </Quote>
      </div>

      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          bottom: 560,
          opacity: q2,
          transform: `translateY(${(1 - q2) * 26}px)`,
        }}
      >
        <Quote size={86}>
          makes you
          <br />
          <span style={{ color: C.goldLight }}>stand taller.</span>
        </Quote>
      </div>
    </AbsoluteFill>
  );
};
