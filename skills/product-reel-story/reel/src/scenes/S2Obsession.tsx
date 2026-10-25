import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { C, F } from "../lib/theme";
import { cue, local } from "../lib/cues";
import { Kicker } from "../components/Film";
import { Scrim } from "../components/UI";

/** One detail, pushed in slowly, over its own sequence. */
const Shot: React.FC<{
  src: string;
  pos: string;
  sf: number;
  st: number;
}> = ({ src, pos, sf, st }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const p = frame / Math.max(1, durationInFrames - 1);
  const e = p * p * (3 - 2 * p);
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
          objectPosition: pos,
          transform: `scale(${sf + (st - sf) * e})`,
          filter: "brightness(0.84) contrast(1.1) saturate(1.06)",
        }}
      />
    </AbsoluteFill>
  );
};

/**
 * OBSESSION — four details, each one closer than the last.
 * The zoom counter and the film-strip dots make the looking itself the story.
 */
export const S2Obsession: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const mirrorAt = local(cue("s2", "Mirror"), start);
  const seqAt = local(cue("s2", "Sequins"), start);
  const goldAt = local(cue("s2", "Gold"), start);

  const shots = [
    {
      at: 0,
      end: mirrorAt,
      img: "images/04.jpg",
      pos: "38% 20%",
      sf: 1.72,
      st: 1.98,
      label: "",
      hud: "\u00d72.4",
    },
    {
      at: mirrorAt,
      end: seqAt,
      img: "images/02.jpg",
      pos: "72% 44%",
      sf: 1.45,
      st: 1.62,
      label: "mirror work",
      hud: "\u00d73.6",
    },
    {
      at: seqAt,
      end: goldAt,
      img: "images/06.jpg",
      pos: "50% 38%",
      sf: 1.3,
      st: 1.48,
      label: "sequins",
      hud: "\u00d75.0",
    },
    {
      at: goldAt,
      end: durationInFrames,
      img: "images/01.jpg",
      pos: "50% 30%",
      sf: 1.0,
      st: 1.06,
      label: "gold thread",
      hud: "\u00d78.0",
    },
  ];

  const activeIdx = Math.max(
    0,
    shots.findIndex((s) => frame >= s.at && frame < s.end)
  );
  const active = shots[activeIdx];

  const fadeIn = interpolate(frame, [0, 4], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [durationInFrames - 8, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const labelIn = spring({
    frame: frame - active.at,
    fps,
    config: { damping: 20, mass: 0.7, stiffness: 95 },
  });

  // a short bright tick on each cut, like a film splice
  const flash = shots.reduce((m, s) => {
    if (s.at === 0) return m;
    const t = Math.min(1, Math.max(0, 1 - (frame - s.at) / 3));
    return Math.max(m, 0.13 * t);
  }, 0);

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink, opacity: fadeIn * fadeOut }}>
      {shots.map((s, i) => (
        <Sequence key={i} from={s.at} durationInFrames={Math.max(1, s.end - s.at)}>
          <Shot src={s.img} pos={s.pos} sf={s.sf} st={s.st} />
        </Sequence>
      ))}

      <Scrim strength={0.85} />

      {/* zoom HUD */}
      <div
        style={{
          position: "absolute",
          top: 146,
          right: 74,
          display: "flex",
          alignItems: "baseline",
          gap: 14,
          color: C.ivory,
        }}
      >
        <span
          style={{
            fontFamily: F.ui,
            fontWeight: 600,
            fontSize: 17,
            letterSpacing: 6,
            opacity: 0.55,
          }}
        >
          ZOOM
        </span>
        <span
          style={{
            fontFamily: F.display,
            fontSize: 36,
            letterSpacing: 1,
            textShadow: "0 2px 18px rgba(0,0,0,0.8)",
          }}
        >
          {active.hud}
        </span>
      </div>

      {/* film-strip progress */}
      <div
        style={{
          position: "absolute",
          right: 46,
          top: 820,
          display: "flex",
          flexDirection: "column",
          gap: 20,
          alignItems: "center",
        }}
      >
        {shots.map((s, i) => {
          const on = i === activeIdx;
          return (
            <div
              key={i}
              style={{
                width: on ? 11 : 6,
                height: on ? 11 : 6,
                borderRadius: 8,
                background: on ? C.gold : "rgba(255,246,231,0.32)",
                boxShadow: on ? `0 0 14px ${C.gold}` : "none",
              }}
            />
          );
        })}
      </div>

      {/* annotation */}
      {active.label ? (
        <div
          style={{
            position: "absolute",
            left: 76,
            bottom: 470,
            opacity: labelIn,
            transform: `translateY(${(1 - labelIn) * 18}px)`,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ width: 44, height: 1, background: C.gold, opacity: 0.85 }} />
            <Kicker size={25} dot={false} color={C.goldLight}>
              {active.label}
            </Kicker>
          </div>
        </div>
      ) : null}

      <AbsoluteFill style={{ backgroundColor: "#FFF6E7", opacity: flash }} />
    </AbsoluteFill>
  );
};
