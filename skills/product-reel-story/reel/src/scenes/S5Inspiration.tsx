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
import { C, F } from "../lib/theme";
import { cue, local } from "../lib/cues";
import { Kicker, Quote } from "../components/Film";

const PanelLabel: React.FC<{ kicker: string; sub: string; style?: React.CSSProperties }> = ({
  kicker,
  sub,
  style,
}) => (
  <div style={{ position: "absolute", ...style }}>
    <Kicker size={25}>{kicker}</Kicker>
    <div
      style={{
        fontFamily: F.serif,
        fontStyle: "italic",
        fontSize: 38,
        color: "rgba(255,246,231,0.72)",
        marginTop: 6,
        textShadow: "0 2px 18px rgba(0,0,0,0.9)",
      }}
    >
      {sub}
    </div>
  </div>
);

/**
 * INSPIRATION — the same six yards, two completely different women.
 * The split is the argument: you don't have to choose.
 */
export const S5Inspiration: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const poojaAt = local(cue("s5", "pooja"), start);
  const partyAt = local(cue("s5", "party"), start);
  const sameAt = local(cue("s5", "Same"), start);

  const p = interpolate(frame, [0, durationInFrames], [0, 1]);

  const topIn = spring({ frame: frame - poojaAt, fps, config: { damping: 22, mass: 0.8, stiffness: 80 } });
  const botIn = spring({ frame: frame - partyAt, fps, config: { damping: 22, mass: 0.8, stiffness: 80 } });
  const sameIn = spring({ frame: frame - sameAt, fps, config: { damping: 24, mass: 0.9, stiffness: 70 } });
  const fadeOut = interpolate(frame, [durationInFrames - 10, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, opacity: fadeOut }}>
      {/* morning / puja */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 820, overflow: "hidden" }}>
        <Img
          src={staticFile("images/01.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 0%",
            transform: `scale(${1.0 + 0.04 * p})`,
            filter: "brightness(0.95) contrast(1.03) saturate(1.04) sepia(0.06)",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(40,14,4,0.4) 0%, rgba(40,14,4,0.02) 38%, rgba(12,6,3,0.6) 100%)",
          }}
        />
      </div>

      {/* night / party */}
      <div style={{ position: "absolute", top: 820, left: 0, right: 0, height: 1100, overflow: "hidden" }}>
        <Img
          src={staticFile("images/02.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 0%",
            transform: `scale(${1.0 + 0.035 * p})`,
            filter: "brightness(0.62) contrast(1.08) saturate(1.02)",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(10,5,3,0.55) 0%, rgba(12,6,20,0.18) 30%, rgba(8,4,10,0.62) 100%)",
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          top: 819,
          left: 0,
          right: 0,
          height: 2,
          background: `linear-gradient(90deg, rgba(233,199,126,0), ${C.gold}, rgba(233,199,126,0))`,
          opacity: 0.7,
          zIndex: 3,
        }}
      />

      <PanelLabel
        kicker="puja"
        sub="morning"
        style={{
          left: 86,
          top: 96,
          opacity: topIn * interpolate(frame, [sameAt, sameAt + 8], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `translateY(${(1 - topIn) * 16}px)`,
        }}
      />
      <PanelLabel
        kicker="party"
        sub="night"
        style={{
          left: 86,
          top: 900,
          opacity: botIn * interpolate(frame, [sameAt, sameAt + 8], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          transform: `translateY(${(1 - botIn) * 16}px)`,
        }}
      />

      <AbsoluteFill style={{ backgroundColor: "rgba(10,5,3,0.58)", opacity: sameIn }} />

      <div
        style={{
          position: "absolute",
          top: 750,
          left: 0,
          right: 0,
          padding: "48px 0 52px",
          background:
            "linear-gradient(90deg, rgba(10,5,3,0) 0%, rgba(10,5,3,0.86) 16%, rgba(10,5,3,0.86) 84%, rgba(10,5,3,0) 100%)",
          opacity: sameIn,
          transform: `scaleY(${0.92 + 0.08 * sameIn})`,
          WebkitMaskImage:
            "linear-gradient(180deg, rgba(0,0,0,0) 0%, #000 15%, #000 85%, rgba(0,0,0,0) 100%)",
          maskImage:
            "linear-gradient(180deg, rgba(0,0,0,0) 0%, #000 15%, #000 85%, rgba(0,0,0,0) 100%)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Kicker size={20}>one saree</Kicker>
        </div>
        <div style={{ marginTop: 18 }}>
          <Quote size={92}>same six yards.</Quote>
        </div>
      </div>
    </AbsoluteFill>
  );
};
