import React, {useMemo} from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from 'remotion';

export type Scene = {
  from: number;
  to: number;
  image: string;
  motion: 'in' | 'out';
  kicker?: string | null;
  overlay?: {text: string; accent?: string} | null;
};

export type Phrase = {
  start: number; // seconds
  end: number;
  words: {text: string; start: number; end: number}[];
};

export type Chapter = {text: string; from: number; to: number};

export type EpisodeProps = {
  fps: number;
  scenes: Scene[];
  phrases: Phrase[];
  chapters: Chapter[];
  durationInFrames: number;
};

const RED = '#E5332A';
const CREAM = '#F7EFE0';

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)',
      pointerEvents: 'none',
    }}
  />
);

const SceneLayer: React.FC<{scene: Scene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const duration = Math.max(1, scene.to - scene.from);
  const t = Math.min(1, Math.max(0, frame / duration));
  const ease = Easing.inOut(Easing.ease);
  const p = ease(t);

  const scale = scene.motion === 'in' ? interpolate(p, [0, 1], [1.0, 1.075]) : interpolate(p, [0, 1], [1.075, 1.0]);
  const drift = interpolate(p, [0, 1], [0, scene.motion === 'in' ? -10 : 10]);
  const fadeIn = interpolate(frame, [0, Math.min(8, duration)], [0, 1], {extrapolateRight: 'clamp'});
  const fadeOut = interpolate(duration - frame, [0, Math.min(7, duration)], [0, 1], {extrapolateLeft: 'clamp'});

  return (
    <AbsoluteFill style={{opacity: Math.min(fadeIn, fadeOut), backgroundColor: '#050506'}}>
      <AbsoluteFill style={{transform: `scale(${scale}) translateY(${drift}px)`}}>
        <Img
          src={staticFile(scene.image)}
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Overlay: React.FC<{text: string; from: number; to: number}> = ({text, from, to}) => {
  const frame = useCurrentFrame();
  const local = frame - from;
  const dur = Math.min(to - from, 74);
  const enter = interpolate(local, [2, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const exit = interpolate(dur - local, [0, 12], [0, 1], {extrapolateLeft: 'clamp'});
  const lift = interpolate(enter, [0, 1], [26, 0]);

  const words = text.split(' ');
  const last = words.length > 1 ? words.pop() : '';

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 0,
        height: 196,
        backgroundColor: 'rgba(5,5,6,0.94)',
        borderTop: `3px solid ${RED}`,
        display: 'flex',
        alignItems: 'center',
        padding: '0 76px',
        opacity: Math.min(enter, exit),
        transform: `translateY(${lift}px)`,
      }}
    >
      <div
        style={{
          fontFamily: 'Anton',
          fontSize: 96,
          lineHeight: 1,
          color: CREAM,
          letterSpacing: 1,
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}
      >
        {words.join(' ')}{' '}
        {last ? <span style={{color: RED}}>{last}</span> : null}
      </div>
    </div>
  );
};

const Captions: React.FC<{phrases: Phrase[]; hidden: {start: number; end: number}[]}> = ({phrases, hidden}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const now = frame / fps;

  const idx = useMemo(() => {
    let lo = 0;
    let hi = phrases.length - 1;
    let best = -1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (phrases[mid].start <= now) {
        best = mid;
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }
    return best;
  }, [now, phrases]);

  if (idx < 0) return null;
  const phrase = phrases[idx];
  if (now > phrase.end + 0.12) return null;
  if (hidden.some((h) => now >= h.start - 0.05 && now <= h.end)) return null;

  const appear = Math.min(1, (now - phrase.start) / 0.1);

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 78,
        display: 'flex',
        justifyContent: 'center',
        opacity: appear,
      }}
    >
      <div
        style={{
          maxWidth: 1560,
          textAlign: 'center',
          fontFamily: 'Anton',
          fontSize: 62,
          lineHeight: 1.12,
          letterSpacing: 1.2,
          textTransform: 'uppercase',
          color: '#FFFFFF',
          WebkitTextStroke: '5px #000000',
          paintOrder: 'stroke fill',
          textShadow: '0 6px 18px rgba(0,0,0,0.9)',
        }}
      >
        {phrase.words.map((w, i) => {
          const active = now >= w.start - 0.02 && now <= w.end + 0.02;
          return (
            <span
              key={i}
              style={{
                color: active ? RED : '#FFFFFF',
                display: 'inline-block',
                transform: active ? 'translateY(-3px)' : 'none',
              }}
            >
              {w.text}
              {i < phrase.words.length - 1 ? '\u00A0' : ''}
            </span>
          );
        })}
      </div>
    </div>
  );
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = frame / Math.max(1, durationInFrames - 1);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 5, backgroundColor: 'rgba(255,255,255,0.08)'}}>
      <div style={{width: `${p * 100}%`, height: '100%', backgroundColor: RED}} />
    </div>
  );
};

const ChapterLabel: React.FC<{chapter: Chapter}> = ({chapter}) => {
  const frame = useCurrentFrame();
  const dur = chapter.to - chapter.from;
  const inP = interpolate(frame, [0, 14], [0, 1], {extrapolateRight: 'clamp'});
  const outP = interpolate(dur - frame, [0, 14], [0, 1], {extrapolateLeft: 'clamp'});
  const opacity = Math.min(inP, outP);
  return (
    <div
      style={{
        position: 'absolute',
        top: 54,
        left: 76,
        display: 'flex',
        alignItems: 'center',
        gap: 14,
        opacity,
        transform: `translateY(${(1 - inP) * -10}px)`,
      }}
    >
      <div style={{width: 12, height: 12, borderRadius: 6, backgroundColor: RED}} />
      <div style={{fontFamily: 'Anton', fontSize: 27, letterSpacing: 3.5, color: CREAM, opacity: 0.9}}>
        {chapter.text}
      </div>
    </div>
  );
};

export const Episode: React.FC<EpisodeProps> = ({scenes, phrases, chapters}) => {
  const overlayRanges = scenes
    .filter((s) => s.overlay)
    .map((s) => ({start: s.from / 24, end: (s.from + 74) / 24}));
  return (
    <AbsoluteFill style={{backgroundColor: '#050506'}}>
      {scenes.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={Math.max(1, s.to - s.from)} name={`scene-${i + 1}`}>
          <SceneLayer scene={s} />
          {s.overlay ? <Overlay text={s.overlay.text} from={0} to={s.to - s.from} /> : null}
        </Sequence>
      ))}
      {chapters.map((c, i) => (
        <Sequence key={`ch-${i}`} from={c.from} durationInFrames={Math.max(1, c.to - c.from)} name={`chapter-${c.text}`}>
          <ChapterLabel chapter={c} />
        </Sequence>
      ))}
      <Captions phrases={phrases} hidden={overlayRanges} />
      <Progress />
      <Audio src={staticFile('audio/vo_master.wav')} />
    </AbsoluteFill>
  );
};
