import { AbsoluteFill, useCurrentFrame } from "remotion";

export const C = {
  ink: "#0E0705",
  ink2: "#1A0C08",
  plum: "#2A0F12",
  gold: "#E9C77E",
  goldDeep: "#B9863A",
  goldLight: "#F9E7BE",
  ivory: "#FFF6E7",
  muted: "rgba(255,246,231,0.62)",
  pink: "#FF3F6C",
  green: "#12B886",
  wine: "#4A0F1C",
};

export const F = {
  display: "Anton, Impact, sans-serif",
  serif: '"Playfair Display", Georgia, serif',
  ui: "Inter, system-ui, sans-serif",
};

export const goldGradient =
  "linear-gradient(180deg, #FFF3D2 0%, #F3D79A 32%, #DDB163 62%, #B9863A 100%)";

export const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

/** Gently drifting gold dust, used across scenes. */
export const GoldDust: React.FC<{ opacity?: number; speed?: number }> = ({
  opacity = 0.45,
  speed = 1,
}) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, mixBlendMode: "screen" }}>
      {new Array(18).fill(0).map((_, i) => {
        const seed = ((i * 37) % 23) / 23;
        const x = (i * 173.3) % 1040;
        const size = 2 + ((i * 7) % 5);
        const sp = (0.5 + ((i * 13) % 9) / 8) * speed;
        const y = 2100 - ((frame * sp + seed * 2300) % 2400);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: C.goldLight,
              filter: "blur(1.2px)",
              boxShadow: `0 0 ${5 + size}px ${C.gold}`,
              opacity: 0.2 + ((i * 17) % 10) / 26,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
