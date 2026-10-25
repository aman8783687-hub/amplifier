"""Cinematic bed for the saree story: drone, heartbeat, sparse percussion, silence before the price."""
import json, math, os, subprocess, wave
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # reel/
AUD = os.path.join(BASE, "public/audio")
SR = 48000
rng = np.random.default_rng(11)

tl = json.load(open(os.path.join(BASE, "src/timeline.json")))
TOTAL = tl["totalSeconds"]
SEGS = tl["segments"]
S = [s["start"] for s in SEGS]
S1, S2, S3, S4, S5, S6 = S
END = TOTAL + 0.4
N = int(END * SR)
L = np.zeros(N)
R = np.zeros(N)
t = np.arange(N) / SR

def word_time(seg_idx, text):
    seg = SEGS[seg_idx]
    for w in seg["words"]:
        if w["text"].lower().strip(".,!?") == text.lower():
            return seg["start"] + w["start"]
    return seg["start"]

PRICE = word_time(3, "One")
FORTHIS = word_time(3, "For")
DIWALI = word_time(5, "Diwali")
GONE = word_time(5, "gone")

def add(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N:
        return
    n = min(len(sig), N - i)
    if pan <= 0:
        L[i:i+n] += sig[:n] * gain * (1 - max(0, -pan))
        R[i:i+n] += sig[:n] * gain * (1 - max(0, -pan)) * (1 + pan)
    else:
        L[i:i+n] += sig[:n] * gain * (1 - pan)
        R[i:i+n] += sig[:n] * gain

def pluck(freq, dur=5.0, bright=0.5):
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, period)
    buf = np.convolve(buf, [0.5, 0.5], mode="same") * bright + buf * (1 - bright)
    out = np.zeros(n)
    idx = 0
    for i in range(n):
        out[i] = buf[idx]
        nxt = (idx + 1) % period
        buf[idx] = 0.9962 * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt
    return out * np.linspace(1, 0, n) ** 0.6

def bell(freq, dur=3.2):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    mod = np.sin(2 * np.pi * freq * 3.01 * tt) * 0.55 * np.exp(-tt * 2)
    s = np.sin(2 * np.pi * freq * tt + mod) * np.exp(-tt * 2.0)
    s += 0.3 * np.sin(2 * np.pi * freq * 2.0 * tt) * np.exp(-tt * 3.2)
    return s

def noise(n):
    return rng.normal(0, 1, n)

def lowpass(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = a * acc + (1 - a) * v
        y[i] = acc
    return y

def highpass(x, cutoff):
    return x - lowpass(x, cutoff)

def whoosh(dur=0.7, peak=0.4):
    n = int(dur * SR)
    x = noise(n)
    loh = lowpass(x, 500)
    mid = lowpass(highpass(x, 500), 2200)
    hi = highpass(x, 2800)
    k = np.linspace(0, 1, n)
    y = loh * (1 - k) ** 2 + mid * 2 * k * (1 - k) + hi * k ** 2
    e = np.sin(np.linspace(0, math.pi, n)) ** 1.6
    return y * e * peak

def shaker(dur=0.045):
    n = int(dur * SR)
    x = highpass(noise(n), 5200)
    return x * np.exp(-np.linspace(0, 6, n)) * 0.45

def kick(dur=0.32):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = 50 * np.exp(-tt * 17) + 36
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * np.exp(-tt * 9)

def impact():
    n = int(1.8 * SR)
    tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (46 * np.exp(-tt * 2.8) + 32) * tt) * np.exp(-tt * 2.8)
    burst = lowpass(noise(n), 900) * np.exp(-tt * 6) * 0.45
    return boom + burst

def pad(freqs, dur, gain=1.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.0014, 0.0014):
            out += np.sin(2 * np.pi * f * (1 + det) * tt + rng.uniform(0, 6))
        out += 0.22 * np.sin(2 * np.pi * 2 * f * tt)
        out += 0.06 * np.sin(2 * np.pi * 3 * f * tt)
    lfo = 0.78 + 0.22 * np.sin(2 * np.pi * 0.06 * tt + rng.uniform(0, 6))
    a = np.clip(tt / 2.4, 0, 1) * np.clip((dur - tt) / 2.4, 0, 1)
    return out * lfo * a * gain

# ---------- tanpura drone ----------
D2, A2, D3, A3 = 73.42, 110.0, 146.83, 220.0
seq = [D2, D3, A2, D3, A3, D3, A2, D3]
tt = 0.0
k = 0
while tt < TOTAL + 0.5:
    f = seq[k % len(seq)]
    sig = pluck(f, dur=6.0, bright=0.5)
    add(sig, tt, pan=(-0.22 if k % 2 == 0 else 0.22), gain=0.085)
    tt += 0.66 if k % 2 else 0.5
    k += 1

# ---------- pads ----------
prog = [
    (0.0, S2, [146.83, 174.61], 0.022),
    (S2, S3, [146.83, 174.61, 220.0], 0.028),
    (S3, S4, [130.81, 174.61, 220.0, 261.63], 0.046),
    (S4, S5, [116.54, 146.83, 174.61], 0.026),
    (S5, S6, [146.83, 220.0, 293.66, 349.23], 0.032),
    (S6, END, [130.81, 164.81, 220.0], 0.034),
]
for a, b, fr, g in prog:
    p = pad(fr, b - a + 1.4, gain=g)
    add(p, a, gain=1.0)
    add(p, a + 0.005, gain=0.9)

# ---------- heartbeat (curiosity) ----------
hb = 0.62
tt = 0.55
while tt < S2 - 0.25:
    add(kick(0.3), tt, gain=0.105)
    add(kick(0.24), tt + 0.19, gain=0.055)
    tt += hb

# ---------- vinyl crackle ----------
crack = lowpass(noise(N), 5000)
mask = (rng.random(N) < 0.00035).astype(float)
mask = np.convolve(mask, np.ones(60) / 60, mode="same")
L += crack * mask * 0.36
R += crack * mask * 0.36

# ---------- low pulse (no shakers: score, not a library track) ----------
beat = 0.72
tt = S2
while tt < S3 - 0.2:
    add(kick(), tt, gain=0.045)
    tt += beat

tt = S6
while tt < END - 1.0:
    add(kick(0.28), tt, gain=0.05)
    tt += 0.6

# ---------- transitions ----------
for cue, g in ((S2, 0.07), (S3, 0.082), (S4, 0.062), (S5, 0.072), (S6, 0.078)):
    add(lowpass(whoosh(0.75, 0.45), 3200), cue - 0.5, pan=0.0, gain=g)

# ---------- silence before the price ----------
quiet_from = PRICE - 1.5
quiet_to = PRICE - 0.02
qi, qn = int(quiet_from * SR), int((quiet_to - quiet_from) * SR)
env = np.ones(N)
ramp = int(0.35 * SR)
env[qi:qi + qn] = 0.06
env[qi - ramp:qi] = np.linspace(1, 0.06, ramp)
env[qi + qn:qi + qn + ramp] = np.linspace(0.06, 1, ramp)
L *= env
R *= env

# ---------- price moment ----------
add(impact(), PRICE, gain=0.34)
add(bell(587.33, 3.0), PRICE + 0.06, pan=0.15, gain=0.028)

# ---------- fomo ----------
add(bell(587.33, 3.4), GONE + 0.4, pan=0.0, gain=0.026)

# ---------- air / space ----------
def make_ir(dur=2.2, decay=2.4, lp=3800):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    raw = rng.normal(0, 1, (n, 2))
    raw[:, 0] = lowpass(raw[:, 0], lp)
    raw[:, 1] = lowpass(raw[:, 1], lp)
    raw *= np.exp(-tt * decay)[:, None]
    pre = int(0.03 * SR)
    ir = np.vstack([np.zeros((pre, 2)), raw])
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    return ir

ir = make_ir()

def fftconv(x, h):
    n = len(x) + len(h) - 1
    nfft = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(h, nfft), nfft)[:len(x)]

wet = np.stack([fftconv(L, ir[:, 0]), fftconv(R, ir[:, 1])], axis=1)
bed = np.stack([L, R], axis=1) + 0.16 * wet

# ---------- fade edges ----------
fade = np.ones(N)
fi = int(0.8 * SR)
fade[:fi] = np.linspace(0, 1, fi) ** 1.4
fo = int(1.8 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.2
bed *= fade[:, None]

def loudnorm_json(path, af="loudnorm=I=-14:TP=-1.5:LRA=11"):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          af + ":print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return json.loads(out[out.rindex("{"):out.rindex("}") + 1])

def write_wav(path, x):
    with wave.open(path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())

def read_wav(path):
    with wave.open(path) as w:
        return (np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
                .astype(np.float32).reshape(-1, 2) / 32768)

# Bed sits well under the voice: ~11.5 LU down at rest, ~15 LU down while she speaks.
BED_LUFS = -27.5
bed_raw = os.path.join(AUD, "bed_raw.wav")
bed_eq = os.path.join(AUD, "bed_eq.wav")
write_wav(bed_raw, bed / max(1e-9, np.abs(bed).max()) * 0.9)
# Small-speaker translation: warm mids forward, sub rumble trimmed, soft on top.
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", bed_raw, "-af",
                "lowshelf=f=110:g=-2.5,highshelf=f=380:g=3.5,lowpass=f=7000", bed_eq], check=True)
bed = read_wav(bed_eq)
bed *= 10 ** ((BED_LUFS - float(loudnorm_json(bed_eq)["input_i"])) / 20)
write_wav(os.path.join(AUD, "bed.wav"), bed)
print("bed written", len(bed) / SR, "s")

# ---------- voice assembly ----------
vo = np.zeros((N, 2), dtype=np.float32)
for seg in SEGS:
    path = os.path.join(BASE, "public", seg["file"])
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
                                   "-ac", "2", "-ar", str(SR), "-"])
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    i = int(seg["start"] * SR)
    n = min(len(x), N - i)
    vo[i:i+n] += x[:n]

VOICE_LUFS = -16.0
vo = vo / max(1e-9, np.abs(vo).max()) * 0.9
write_wav(os.path.join(AUD, "voice_raw.wav"), vo)
vo *= 10 ** ((VOICE_LUFS - float(loudnorm_json(os.path.join(AUD, "voice_raw.wav"))["input_i"])) / 20)
write_wav(os.path.join(AUD, "voice.wav"), vo)

vmono = np.abs(vo).mean(axis=1)
win = int(0.45 * SR)
sm = np.convolve(vmono, np.ones(win) / win, mode="same")
# Soft, smoothed duck (-3.1 dB under speech): fast attack, slow release, no pumping.
fps = 100
step = SR // fps
sm_ds = sm[::step]
gate = np.clip((sm_ds - 0.006) / 0.018, 0.0, 1.0)
a_att, a_rel = math.exp(-1 / (0.12 * fps)), math.exp(-1 / (0.55 * fps))
env = np.empty_like(gate)
prev = 1.0
for i, g in enumerate(gate):
    target = 1.0 - 0.32 * g
    a = a_att if target < prev else a_rel
    prev = a * prev + (1 - a) * target
    env[i] = prev
duck = np.interp(np.arange(N), np.arange(len(env)) * step, env)
mix = bed * duck[:, None] + vo
mix = np.tanh(mix * 1.0) * 0.97
write_wav(os.path.join(AUD, "voice_bed_mix.wav"), mix)
print("mix written", len(mix) / SR, "s")

m = loudnorm_json(os.path.join(AUD, "voice_bed_mix.wav"))
af = ("loudnorm=I=-14:TP=-1.5:LRA=11"
      f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
      f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
      f":offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(AUD, "voice_bed_mix.wav"),
                "-af", af, "-ar", "48000", "-b:a", "192k",
                os.path.join(AUD, "soundtrack.mp3")], check=True)
print("soundtrack done")
