import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C } from "../lib/theme";
import { cue, local } from "../lib/cues";
import { Kicker, Quote, Rule } from "../components/Film";
import { Scrim } from "../components/UI";

/**
 * CURIOSITY — an overheard sentence, not a pitch.
 * The product stays half-hidden until the second line.
 */
export const S1Curiosity: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const stopAt = local(cue("s1", "stop"), start);
  const notAt = local(cue("s1", "Not"), start);

  const fadeIn = interpolate(frame, [0, 16], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const p = interpolate(frame, [0, durationInFrames], [0, 1]);
  const cut = interpolate(frame, [notAt, notAt + 9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const q1 = spring({ frame: frame - stopAt, fps, config: { damping: 22, mass: 0.9, stiffness: 70 } });
  const q2 = spring({ frame: frame - notAt, fps, config: { damping: 22, mass: 0.9, stiffness: 70 } });
  const kick = interpolate(frame, [12, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rule = interpolate(frame, [stopAt + 4, stopAt + 24], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const drift = interpolate(frame, [0, durationInFrames], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, opacity: fadeIn * fadeOut }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img
          src={staticFile("images/06.jpg")}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "52% 38%",
            transform: `scale(${1.46 - 0.2 * p})`,
            filter: "brightness(0.66) contrast(1.1) saturate(1.02)",
          }}
        />
      </AbsoluteFill>

      <AbsoluteFill style={{ overflow: "hidden", opacity: cut }}>
        <Img
          src={staticFile("images/04.jpg")}
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "44% 22%",
            transform: `scale(${1.08 + 0.08 * ((frame - notAt) / Math.max(1, durationInFrames - notAt))})`,
            filter: "brightness(0.7) contrast(1.08) saturate(1.04)",
          }}
        />
      </AbsoluteFill>

      <Scrim strength={1.05} />

      {/* a slow warm leak, like light through a window */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(40% 30% at ${76 + 6 * drift}% ${20 + 4 * drift}%, rgba(255,184,110,0.16), rgba(0,0,0,0) 70%)`,
          mixBlendMode: "screen",
        }}
      />

      <div
        style={{
          position: "absolute",
          top: 148,
          width: "100%",
          display: "flex",
          justifyContent: "center",
          opacity: kick * (1 - cut),
          transform: `translateY(${(1 - kick) * 10}px)`,
        }}
      >
        <Kicker size={22}>a saree story</Kicker>
      </div>

      <div
        style={{
          position: "absolute",
          left: 90,
          right: 90,
          bottom: 560,
          opacity: q1 * (1 - cut),
          transform: `translateY(${(1 - q1) * 26}px)`,
        }}
      >
        <Rule width={rule * 120} style={{ margin: "0 auto 30px" }} />
        <Quote size={82}>
          makes people
          <br />
          <span style={{ color: C.goldLight }}>stop mid-sentence.</span>
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
        <Rule width={120} style={{ margin: "0 auto 30px" }} />
        <Quote size={82}>
          <span style={{ color: C.goldLight }}>not</span> the one
          <br />
          you&rsquo;re thinking of.
        </Quote>
      </div>
    </AbsoluteFill>
  );
};
