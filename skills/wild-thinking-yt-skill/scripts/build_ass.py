import re, os, glob

BASE=os.environ.get("WILD_THINKING_DIR", os.getcwd())

IMPORTANT = set("""death died dead burial bury buried grave afterlife spirit soul Neanderthal neanderthal ochre beads beads Sungir Shanidar Qafzeh Atapuerca bones bone funeral mourn mourning ritual rituals Egypt Egyptian Tibetan sky vultures mummification Dreamtime Aboriginal ancestor ancestors worship offerings temple temples cave art fire flowers tools stone axe scavengers predators hygiene disease transition human humans Homo sapiens evolution extinction species La Chapelle arthritis compassion grief love children child boy girl ivory mammoth fox tooth pendants weeks hand drilled Qafzeh Israel Russia France Spain Iraq Kalahari Ju hoansi Field Reeds landscape song memory rest peace""".split())

def parse_srt(path):
    txt=open(path).read()
    cues=[]
    for block in re.split(r'\n\s*\n', txt.strip()):
        lines=block.strip().splitlines()
        if len(lines)<3: continue
        # find timing line
        m=re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})', lines[1])
        if not m: 
            # maybe lines[0] is index, lines[1] timing
            m=re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})', lines[1] if len(lines)>1 else '')
        if not m: continue
        def to_sec(a,b,c,d): return int(a)*3600+int(b)*60+int(c)+int(d)/1000.0
        start=to_sec(m.group(1),m.group(2),m.group(3),m.group(4))
        end=to_sec(m.group(5),m.group(6),m.group(7),m.group(8))
        text=" ".join(lines[2:]).strip()
        cues.append((start,end,text))
    return cues

def fmt(t):
    h=int(t//3600); t%=3600
    m=int(t//60); s=t%60
    cs=int(round((s-int(s))*100))
    s=int(s)
    if cs>=100: cs=99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def is_important(w):
    w2=w.strip(".,?!:;\"'()").lower()
    if any(ch.isdigit() for ch in w): return True
    return w2 in {x.lower() for x in IMPORTANT}

def weight(words):
    # char-length weights
    ws=[max(1,len(w)) for w in words]
    total=sum(ws)
    return ws,total

def build_ass(seg):
    srt_path=f"{BASE}/audio/{seg}.srt"
    cues=parse_srt(srt_path)
    out=[]
    out.append("[Script Info]")
    out.append("Title: Wild Thinking")
    out.append("ScriptType: v4.00+")
    out.append("WrapStyle: 0")
    out.append("PlayResX: 1920")
    out.append("PlayResY: 1080")
    out.append("ScaledBorderAndShadow: yes")
    out.append("")
    out.append("[V4+ Styles]")
    out.append("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding")
    out.append("Style: Default,DejaVu Sans,56,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,70,1")
    out.append("")
    out.append("[Events]")
    out.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
    for (start,end,text) in cues:
        words=text.split()
        if not words: continue
        ws,tot=weight(words)
        # compute word start times within [start,end]
        cur=start
        wstarts=[]
        for w,wt in zip(words,ws):
            dur=(end-start)*(wt/tot)
            wstarts.append((cur, cur+dur, w))
            cur+=dur
        # fix last end
        if wstarts:
            wstarts[-1]=(wstarts[-1][0], end, wstarts[-1][2])
        # build events for each word index
        for k,(ws_k,we_k,wk) in enumerate(wstarts):
            # accumulated text words 0..k
            accum=words[:k+1]
            # build text with tags
            parts=[]
            for i,w in enumerate(accum):
                imp=is_important(w)
                if i==k:
                    # current word: pop/zoom + yellow if important
                    if imp:
                        tag="{\\c&H0000FFFF&\\t(0,180,\\fscx118\\fscy118)\\t(180,360,\\fscx100\\fscy100)}"
                    else:
                        tag="{\\c&H00FFFFFF&\\t(0,180,\\fscx108\\fscy108)\\t(180,360,\\fscx100\\fscy100)}"
                    parts.append(tag+w+"{\\r}")
                else:
                    if imp:
                        parts.append("{\\c&H0000FFFF&}"+w+"{\\r}")
                    else:
                        parts.append(w)
            line=" ".join(parts)
            # fade-in + upward movement only on first word of phrase
            if k==0:
                ev_start=fmt(start)
                ev_text="{\\fad(180,0)\\move(960,1000,960,980,0,180)}"+line
            else:
                ev_start=fmt(ws_k)
                ev_text=line
            ev_end=fmt(wstarts[k+1][0] if k+1<len(wstarts) else end)
            # ensure ev_end > ev_start
            if ev_end<=ev_start: 
                ev_end=fmt(min(end, ws_k+0.3))
            out.append(f"Dialogue: 0,{ev_start},{ev_end},Default,,0,0,0,,{ev_text}")
    with open(f"{BASE}/audio/{seg}.ass","w") as f:
        f.write("\n".join(out)+"\n")

for srt in sorted(glob.glob(f"{BASE}/audio/seg*.srt")):
    seg=os.path.basename(srt).replace(".srt","")
    build_ass(seg)
    print("built", seg)
print("done")