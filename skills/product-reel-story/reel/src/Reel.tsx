import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  continueRender,
  delayRender,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { SEGMENTS, TOTAL_FRAMES } from "./lib/cues";
import { C } from "./lib/theme";
import { S1Curiosity } from "./scenes/S1Curiosity";
import { S2Obsession } from "./scenes/S2Obsession";
import { S3Desire } from "./scenes/S3Desire";
import { S4Disbelief } from "./scenes/S4Disbelief";
import { S5Inspiration } from "./scenes/S5Inspiration";
import { S6Fomo } from "./scenes/S6Fomo";
import { Grain, Halation } from "./components/Film";

/** A hairline, not a loading bar. */
const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const p = Math.min(1, frame / (TOTAL_FRAMES - 1));
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 2,
        background: "rgba(255,246,231,0.08)",
        zIndex: 50,
      }}
    >
      <div
        style={{
          width: `${p * 100}%`,
          height: "100%",
          background: "linear-gradient(90deg, rgba(185,134,58,0.5), rgba(243,215,154,0.85))",
        }}
      />
    </div>
  );
};

const SCENES: Record<string, React.FC<{ start: number }>> = {
  s1: S1Curiosity,
  s2: S2Obsession,
  s3: S3Desire,
  s4: S4Disbelief,
  s5: S5Inspiration,
  s6: S6Fomo,
};

export const Reel: React.FC = () => {
  const [handle] = useState(() => delayRender("Waiting for fonts"));
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        await Promise.all([
          document.fonts.load("400 100px Anton"),
          document.fonts.load('italic 600 100px "Playfair Display"'),
          document.fonts.load("800 100px Inter"),
          document.fonts.load("600 40px Inter"),
          document.fonts.load("500 40px Inter"),
        ]);
        await document.fonts.ready;
      } catch {
        // fall through: render with system fallbacks rather than hanging
      }
      setReady(true);
      continueRender(handle);
    };
    load();
  }, [handle]);

  const fontCss = `
    @font-face { font-family: "Anton"; src: url("${staticFile("fonts/Anton-Regular.ttf")}") format("truetype"); font-weight: 400; font-display: block; }
    @font-face { font-family: "Playfair Display"; src: url("${staticFile("fonts/PlayfairDisplay-Italic.ttf")}") format("truetype"); font-weight: 400 900; font-style: italic; font-display: block; }
    @font-face { font-family: "Inter"; src: url("${staticFile("fonts/Inter.ttf")}") format("truetype"); font-weight: 100 900; font-display: block; }
  `;

  return (
    <AbsoluteFill style={{ backgroundColor: C.ink }}>
      <style dangerouslySetInnerHTML={{ __html: fontCss }} />
      <Audio src={staticFile("audio/soundtrack.mp3")} />

      {SEGMENTS.map((seg, i) => {
        const next = SEGMENTS[i + 1];
        const dur = (next ? next.startFrame : TOTAL_FRAMES) - seg.startFrame;
        const Comp = SCENES[seg.id];
        if (!Comp) return null;
        return (
          <Sequence key={seg.id} from={seg.startFrame} durationInFrames={dur} name={seg.id}>
            <Comp start={seg.start} />
          </Sequence>
        );
      })}

      {/* a whisper of a bottom scrim, for the platform UI */}
      <AbsoluteFill
        style={{
          background:
            "linear-gradient(180deg, rgba(8,4,3,0) 76%, rgba(8,4,3,0.22) 88%, rgba(8,4,3,0.5) 100%)",
          pointerEvents: "none",
        }}
      />

      {ready ? (
        <>
          <Halation />
          <Grain />
        </>
      ) : null}
      <Progress />
    </AbsoluteFill>
  );
};
