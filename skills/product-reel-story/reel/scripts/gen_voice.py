import asyncio, json, os, subprocess
import edge_tts

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # reel/
AUD = os.path.join(BASE, "public/audio")
os.makedirs(AUD, exist_ok=True)
VOICE = "en-IN-NeerjaExpressiveNeural"
RATE = "+9%"
PITCH = "-2Hz"
TEMPO = 1.03
GAP = 0.34
FPS = 30

# Emotional arc: curiosity -> obsession -> desire -> disbelief -> inspiration -> FOMO
SEGS = [
    ("s1", "There's a saree that makes people stop mid-sentence. Not the one you're thinking of."),
    ("s2", "I zoomed in on the border for ten minutes. Mirror. Sequins. Gold thread that catches the light."),
    ("s3", "Then I saw it move. Satin that falls like water. The kind of drape that makes you stand taller."),
    ("s4", "So I checked the price. One thousand three hundred forty-five. For this."),
    ("s5", "Morning pooja, one way. Night party, a completely different woman. Same six yards."),
    ("s6", "Diwali is on the eighth. The one you'll wish you'd bought when it's gone. The link's in the pinned comment. Go."),
]

def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", path])
    return float(out.strip())

async def synth(name, text):
    raw = os.path.join(AUD, f"{name}_raw.mp3")
    c = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, boundary="WordBoundary")
    words = []
    with open(raw, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"text": ch["text"], "start": ch["offset"] / 1e7, "dur": ch["duration"] / 1e7})
    out = os.path.join(AUD, f"{name}.mp3")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw,
                    "-af", f"atempo={TEMPO},loudnorm=I=-16:TP=-1.5:LRA=7",
                    "-ar", "48000", "-b:a", "192k", out], check=True)
    os.remove(raw)
    for w in words:
        w["start"] = round(w["start"] / TEMPO, 3)
        w["dur"] = round(w["dur"] / TEMPO, 3)
    return out, words

async def main():
    timeline = []
    t = 0.0
    for name, text in SEGS:
        mp3, words = await synth(name, text)
        d = dur(mp3)
        timeline.append({
            "id": name, "text": text, "file": f"audio/{name}.mp3",
            "start": round(t, 3), "duration": round(d, 3),
            "startFrame": round(t * FPS), "frames": round(d * FPS),
            "words": words,
        })
        print(f"{name}: {d:.2f}s words={len(words)} start={t:.2f}s frame={round(t*FPS)}")
        t += d + GAP

    total = t - GAP + 1.0
    data = {"fps": FPS, "voice": VOICE, "tempo": TEMPO,
            "totalSeconds": round(total, 3), "totalFrames": round(total * FPS),
            "segments": timeline}
    open(os.path.join(BASE, "src/timeline.json"), "w").write(json.dumps(data, indent=2))
    print("TOTAL", data["totalSeconds"], "s", data["totalFrames"], "frames")

asyncio.run(main())
