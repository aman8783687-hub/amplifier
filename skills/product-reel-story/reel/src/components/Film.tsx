import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame } from "remotion";
import { C, F } from "../lib/theme";

/** Moving film grain. Keeps the frame from looking like a clean product render. */
export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.06 }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("textures/grain.png")})`,
        backgroundRepeat: "repeat",
        backgroundPosition: `${(frame * 11) % 256}px ${(frame * 17) % 256}px`,
        opacity,
        mixBlendMode: "overlay",
        pointerEvents: "none",
        zIndex: 60,
      }}
    />
  );
};

/** Warm halation on the highlights, then a vignette. */
export const Halation: React.FC = () => (
  <>
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(90% 55% at 50% 14%, rgba(255,199,126,0.13) 0%, rgba(255,150,70,0.045) 46%, rgba(0,0,0,0) 74%)",
        mixBlendMode: "screen",
        pointerEvents: "none",
        zIndex: 61,
      }}
    />
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(125% 88% at 50% 46%, rgba(0,0,0,0) 44%, rgba(0,0,0,0.48) 100%)",
        pointerEvents: "none",
        zIndex: 62,
      }}
    />
  </>
);

export const Kicker: React.FC<{
  children: React.ReactNode;
  color?: string;
  dot?: boolean;
  size?: number;
  style?: React.CSSProperties;
}> = ({ children, color = "rgba(255,246,231,0.75)", dot = true, size = 23, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 14,
      fontFamily: F.ui,
      fontWeight: 600,
      fontSize: size,
      letterSpacing: 9,
      textTransform: "uppercase",
      color,
      textShadow: "0 2px 18px rgba(0,0,0,0.7)",
      ...style,
    }}
  >
    {dot ? (
      <span
        style={{
          width: 7,
          height: 7,
          borderRadius: 4,
          background: C.gold,
          boxShadow: `0 0 10px ${C.gold}`,
          flexShrink: 0,
        }}
      />
    ) : null}
    {children}
  </div>
);

export const Quote: React.FC<{
  children: React.ReactNode;
  size?: number;
  color?: string;
  align?: "left" | "center" | "right";
  style?: React.CSSProperties;
}> = ({ children, size = 84, color = C.ivory, align = "center", style }) => (
  <div
    style={{
      fontFamily: F.serif,
      fontStyle: "italic",
      fontWeight: 500,
      fontSize: size,
      lineHeight: 1.12,
      letterSpacing: -size * 0.012,
      color,
      textAlign: align,
      textShadow: "0 8px 44px rgba(0,0,0,0.85)",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Rule: React.FC<{ width?: number | string; style?: React.CSSProperties }> = ({
  width = 110,
  style,
}) => (
  <div
    style={{
      width,
      height: 2,
      background: `linear-gradient(90deg, rgba(233,199,126,0), ${C.gold}, rgba(233,199,126,0))`,
      ...style,
    }}
  />
);
