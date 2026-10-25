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
import { Price, StrikePrice } from "../components/UI";

/**
 * FOMO — a film poster, not a sale banner.
 * Big portrait, a stacked date, then the line, the price and a quiet link.
 */
export const S6Fomo: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const eighthAt = local(cue("s6", "eighth"), start);
  const wishAt = local(cue("s6", "wish"), start);
  const linkAt = local(cue("s6", "pinned"), start);
  const goAt = local(cue("s6", "Go"), start);

  const dateIn = spring({ frame: frame - eighthAt, fps, config: { damping: 22, mass: 0.9, stiffness: 75 } });
  const wishIn = spring({ frame: frame - wishAt, fps, config: { damping: 22, mass: 0.9, stiffness: 70 } });
  const priceIn = interpolate(frame, [wishAt + 14, wishAt + 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const linkIn = spring({ frame: frame - linkAt, fps, config: { damping: 20, mass: 0.8, stiffness: 85 } });
  const pulse = frame > goAt ? 1 + 0.018 * Math.sin(((frame - goAt) / fps) * 6.5) : 1;

  const p = interpolate(frame, [0, durationInFrames], [0, 1]);
  const fadeOut = interpolate(frame, [durationInFrames - 46, durationInFrames - 2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      {/* hero portrait */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 1150, overflow: "hidden" }}>
        <Img
          src={staticFile("images/01.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "50% 0%",
            transform: `scale(${1.02 - 0.02 * p})`,
            filter: "brightness(0.56) contrast(1.05) saturate(1.03)",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(180deg, rgba(10,5,3,0.55) 0%, rgba(10,5,3,0.06) 26%, rgba(10,5,3,0.12) 52%, rgba(14,7,5,0.86) 86%, rgba(14,7,5,1) 100%)",
          }}
        />
      </div>

      {/* stacked date */}
      <div
        style={{
          position: "absolute",
          left: 82,
          top: 158,
          opacity: dateIn,
          transform: `translateY(${(1 - dateIn) * 18}px)`,
        }}
      >
        <Kicker size={21}>diwali</Kicker>
        <div
          style={{
            fontFamily: F.display,
            fontSize: 176,
            lineHeight: 0.84,
            color: C.ivory,
            marginTop: 18,
            textShadow: "0 10px 50px rgba(0,0,0,0.55)",
          }}
        >
          8
        </div>
        <div
          style={{
            fontFamily: F.ui,
            fontWeight: 600,
            fontSize: 27,
            letterSpacing: 13,
            color: "rgba(255,246,231,0.72)",
            marginTop: 10,
          }}
        >
          NOVEMBER
        </div>
      </div>

      {/* the close */}
      <div style={{ position: "absolute", left: 82, right: 82, top: 1186 }}>
        <div
          style={{
            opacity: wishIn,
            transform: `translateY(${(1 - wishIn) * 22}px)`,
          }}
        >
          <Quote size={56} align="left">
            the one you&rsquo;ll
            <br />
            <span style={{ color: C.goldLight }}>wish you&rsquo;d bought.</span>
          </Quote>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 26, opacity: priceIn }}>
          <Price amount="1,345" size={62} color={C.ivory} />
          <StrikePrice amount="6,999" size={28} style={{ marginBottom: 6 }} />
        </div>

        <div
          style={{
            marginTop: 24,
            opacity: linkIn,
            transform: `translateY(${(1 - linkIn) * 16}px) scale(${(0.97 + 0.03 * linkIn) * pulse})`,
            transformOrigin: "left center",
          }}
        >
          <div
            style={{
              display: "inline-block",
              fontFamily: F.ui,
              fontWeight: 700,
              fontSize: 40,
              letterSpacing: 0.2,
              color: C.ivory,
              paddingBottom: 9,
              borderBottom: `2px solid ${C.gold}`,
            }}
          >
            link in the pinned comment <span style={{ color: C.gold }}>&#8599;</span>
          </div>
        </div>

        <div
          style={{
            marginTop: 26,
            fontFamily: F.ui,
            fontWeight: 500,
            fontSize: 19,
            letterSpacing: 6,
            color: "rgba(255,246,231,0.42)",
            opacity: linkIn,
          }}
        >
          ANOUK &middot; MYNTRA &middot; 41573047
        </div>
      </div>

      <AbsoluteFill style={{ backgroundColor: "#000", opacity: fadeOut }} />
    </AbsoluteFill>
  );
};
