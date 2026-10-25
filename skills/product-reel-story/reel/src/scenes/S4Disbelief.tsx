import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, F } from "../lib/theme";
import { cue, local } from "../lib/cues";
import { Kicker, Quote, Rule } from "../components/Film";
import { KenImg, Price, Scrim, StrikePrice } from "../components/UI";

/**
 * DISBELIEF — the price arrives quietly, almost apologetically.
 * No badge, no starburst, no "you save". The restraint is the point.
 */
export const S4Disbelief: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const priceAt = local(cue("s4", "price"), start);
  const oneAt = local(cue("s4", "One"), start);
  const forAt = local(cue("s4", "For"), start);

  const open = interpolate(frame, [0, 9], [1, 0], { extrapolateRight: "clamp" });
  const reveal = spring({ frame: frame - oneAt, fps, config: { damping: 30, mass: 1.1, stiffness: 55 } });
  const moved = spring({ frame: frame - forAt, fps, config: { damping: 26, mass: 0.9, stiffness: 70 } });
  const labelIn = interpolate(frame, [priceAt, priceAt + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const bright = interpolate(frame, [forAt, forAt + 22], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, opacity: fadeOut }}>
      <KenImg
        src="images/01.jpg"
        scaleFrom={1.06}
        scaleTo={1.0}
        filter={`brightness(${0.42 + 0.24 * bright}) contrast(1.1) saturate(0.98)`}
      />
      <Scrim strength={1.1} />

      <div
        style={{
          position: "absolute",
          top: 604,
          left: 0,
          right: 0,
          transform: `translateY(${-92 * moved}px)`,
        }}
      >
        <div style={{ display: "flex", justifyContent: "center", opacity: labelIn }}>
          <Kicker size={22} dot={false} color="rgba(255,246,231,0.5)">
            the price
          </Kicker>
        </div>
        <div
          style={{
            marginTop: 22,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            opacity: reveal,
            transform: `scale(${(1 - 0.2 * moved) * (1.05 - 0.05 * reveal)})`,
            transformOrigin: "50% 0%",
          }}
        >
          <Rule width={90} style={{ margin: "0 auto 20px", opacity: 0.55 }} />
          <Price amount="1,345" size={160} color={C.ivory} />
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 18 }}>
            <span
              style={{
                fontFamily: F.ui,
                fontWeight: 500,
                fontSize: 20,
                letterSpacing: 4,
                color: "rgba(255,246,231,0.38)",
              }}
            >
              MRP
            </span>
            <StrikePrice amount="6,999" size={32} />
          </div>
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          top: 1010,
          left: 0,
          right: 0,
          textAlign: "center",
          opacity: moved,
          transform: `translateY(${(1 - moved) * 26}px)`,
        }}
      >
        <Quote size={106} color={C.goldLight}>
          for this.
        </Quote>
      </div>

      <AbsoluteFill style={{ backgroundColor: "#000", opacity: open }} />
    </AbsoluteFill>
  );
};
