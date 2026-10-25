import timeline from "../timeline.json";

export type Word = { text: string; start: number; dur: number };
export type Segment = {
  id: string;
  text: string;
  file: string;
  start: number;
  duration: number;
  startFrame: number;
  frames: number;
  words: Word[];
};

export const FPS = timeline.fps;
export const SEGMENTS = timeline.segments as Segment[];
export const SEG: Record<string, Segment> = Object.fromEntries(
  SEGMENTS.map((s) => [s.id, s])
);
export const AUDIO_END = timeline.totalSeconds;
export const TOTAL_FRAMES = timeline.totalFrames;

/** Absolute time (seconds) of the n-th occurrence of a spoken word. */
export const cue = (id: string, word: string, occurrence = 0): number => {
  const seg = SEG[id];
  if (!seg) return 0;
  const target = word.toLowerCase().replace(/[^a-z0-9-]/g, "");
  let seen = 0;
  for (const w of seg.words) {
    const clean = w.text.toLowerCase().replace(/[^a-z0-9-]/g, "");
    if (clean === target) {
      if (seen === occurrence) return seg.start + w.start;
      seen++;
    }
  }
  return seg.start;
};

export const sceneStart = (id: string): number => SEG[id]?.start ?? 0;
export const sceneFrames = (id: string): number => SEG[id]?.frames ?? 0;

/** Local frame for an absolute cue, given the scene's absolute start. */
export const local = (absSec: number, sceneStartSec: number): number =>
  Math.round((absSec - sceneStartSec) * FPS);
