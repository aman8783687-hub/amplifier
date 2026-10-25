import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { C, F, goldGradient } from "../lib/theme";

export const Scrim: React.FC<{ strength?: number }> = ({ strength = 1 }) => (
  <>
    <AbsoluteFill
      style={{
        background: `linear-gradient(180deg, rgba(10,5,3,${0.55 * strength}) 0%, rgba(10,5,3,0) 24%, rgba(10,5,3,0) 52%, rgba(10,5,3,${0.55 * strength}) 76%, rgba(10,5,3,${0.94 * strength}) 100%)`,
      }}
    />
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.42) 100%)",
      }}
    />
  </>
);

export const Chip: React.FC<{
  children: React.ReactNode;
  color?: string;
  bg?: string;
  size?: number;
  style?: React.CSSProperties;
}> = ({ children, color = C.gold, bg = "rgba(20,10,6,0.55)", size = 26, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 12,
      padding: "12px 26px",
      borderRadius: 999,
      border: `1.5px solid ${color}66`,
      background: bg,
      color,
      fontFamily: F.ui,
      fontWeight: 700,
      fontSize: size,
      letterSpacing: 4,
      textTransform: "uppercase",
      backdropFilter: "blur(6px)",
      ...style,
    }}
  >
    {children}
  </div>
);

/** Rupee sign in Inter (reliable glyph) + digits in Anton. */
export const Price: React.FC<{
  amount: string;
  size: number;
  color?: string;
  gold?: boolean;
  style?: React.CSSProperties;
  signScale?: number;
}> = ({ amount, size, color = C.ivory, gold = false, style, signScale = 0.5 }) => (
  <div
    style={{
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "center",
      fontFamily: F.display,
      fontSize: size,
      lineHeight: 0.94,
      letterSpacing: -size * 0.012,
      ...style,
    }}
  >
    <span
      style={{
        fontFamily: F.ui,
        fontWeight: 800,
        fontSize: size * signScale,
        marginTop: size * 0.09,
        marginRight: size * 0.035,
        color: gold ? C.gold : color,
      }}
    >
      ₹
    </span>
    <span
      style={
        gold
          ? {
              backgroundImage: goldGradient,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }
          : { color }
      }
    >
      {amount}
    </span>
  </div>
);


/** Struck-through MRP, with a thin consistent strike line. */
export const StrikePrice: React.FC<{
  amount: string;
  size: number;
  style?: React.CSSProperties;
}> = ({ amount, size, style }) => (
  <div
    style={{
      position: "relative",
      display: "inline-block",
      fontFamily: F.ui,
      fontWeight: 600,
      fontSize: size,
      letterSpacing: 1,
      color: "#C9B49B",
      lineHeight: 1,
      ...style,
    }}
  >
    ₹{amount}
    <div
      style={{
        position: "absolute",
        left: "-3%",
        top: "54%",
        width: "106%",
        height: Math.max(2, Math.round(size * 0.055)),
        background: "rgba(201,180,155,0.7)",
        borderRadius: 2,
        transform: "translateY(-50%)",
        opacity: 0.9,
      }}
    />
  </div>
);

/** Full-bleed image with a slow Ken Burns move over the sequence. */
export const KenImg: React.FC<{
  src: string;
  scaleFrom?: number;
  scaleTo?: number;
  xFrom?: number;
  xTo?: number;
  yFrom?: number;
  yTo?: number;
  filter?: string;
  style?: React.CSSProperties;
}> = ({
  src,
  scaleFrom = 1.14,
  scaleTo = 1.02,
  xFrom = 0,
  xTo = 0,
  yFrom = 0,
  yTo = 0,
  filter,
  style,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = Math.min(1, frame / Math.max(1, durationInFrames - 1));
  const eased = p * p * (3 - 2 * p);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img
        src={staticFile(src)}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `translate(${xFrom + (xTo - xFrom) * eased}px, ${yFrom + (yTo - yFrom) * eased}px) scale(${scaleFrom + (scaleTo - scaleFrom) * eased})`,
          filter,
          ...style,
        }}
      />
    </AbsoluteFill>
  );
};
