import asyncio, base64, os, sys
from playwright.async_api import async_playwright

OUTDIR = os.environ.get("IMAGES_DIR", os.path.join(os.getcwd(), "images2"))
os.makedirs(OUTDIR, exist_ok=True)

STYLE_PRESETS = {
    # Default: the channel's signature marker stickman.
    "boss": ", hand-drawn black marker stickman on a clean white whiteboard, thick confident marker strokes, the stickman wears a black fedora with a gold band, a thin black outline suit jacket and a small solid gold tie, exactly two black dot eyes and NO mouth, calm neutral face, thin single-line stick limbs, no text, no letters, no numbers, one or two simple hand-drawn marker props only, money props drawn in gold, no arrows, lots of empty white space, only black, white and gold colors, no red, whiteboard explainer animation look",
    # Sparse editorial ink: adapted from hi-nikola/hand-drawn-explainer-video-nikola
    # ("Xiaohei" preset, credited to helloianneo/ian-xiaohei-illustrations).
    # The Boss keeps his fedora and gold tie; upstream red/orange/blue -> gold.
    "xiaohei": ", minimalist hand-drawn editorial illustration on a pure white background, one small black creature with tiny white dot eyes wearing a black fedora with a gold band and a small solid gold tie, no mouth, sparse slightly wobbly black ink lines, flat solid black shapes, large clean negative space, at least thirty-five percent empty white area, only black, white and gold annotation accents, gold arrows and gold circles, low line density, one absurd but clearly explanatory core action, no pencil noise, no hatching, no shading, no gradients, no long text, no pseudo-writing, no numbers, no letters, no logos, no photorealism, no glossy 3d, no dense texture, 16:9 widescreen",
    # Natural-skin Q-version people, still cartoon (never a real person's likeness).
    "qhuman": ", soft hand-drawn Q-version cartoon illustration on a clean white background, natural skin tone, simple rounded shapes with clear age and outfit anchors, thin black ink outline, flat limited colours, clothing in black white and gold, no red no orange no blue, calm friendly expression, large clean empty space, one or two simple props only, no text, no letters, no numbers, no logos, no pseudo-writing, no photorealism, no 3d, no shading, no gradients, 16:9 widescreen",
}

COMPOSITIONS = {
    "single": ", one complete action filling a 16:9 frame, the bottom eighteen percent of the image left clean and empty for captions",
    "islands": ", two independent but narratively connected scene islands on one white sheet, left island and right island of similar size, a clean empty vertical gutter of six to ten percent of the image width between them, no ground line, no wire, no table edge, no shadow and no arrow crossing the gutter, the bottom eighteen percent of the image left clean and empty for captions",
}

STYLE_PRESET = os.environ.get("STYLE_PRESET", "boss")
COMPOSITION = os.environ.get("COMPOSITION", "single")

if STYLE_PRESET not in STYLE_PRESETS:
    sys.exit(f"Unknown STYLE_PRESET {STYLE_PRESET!r}; choose from {sorted(STYLE_PRESETS)}")
if COMPOSITION not in COMPOSITIONS:
    sys.exit(f"Unknown COMPOSITION {COMPOSITION!r}; choose from {sorted(COMPOSITIONS)}")

STYLE_SUFFIX = STYLE_PRESETS[STYLE_PRESET] + COMPOSITIONS[COMPOSITION]

NEGATIVE = "color photo, photorealistic, 3d render, shading, gradients, text, letters, numbers, watermark, mouth, red, extra colors"

SUBJECTS = [
  # One subject per beat (7-10 s of narration). Edit per episode.
  # Example: "चाय वाला असल में कितना कमाता है?"
  ("scene1-chai-hook", "the boss stickman in a black fedora and gold tie standing in front of a small Indian chai stall, one steaming kettle and a row of tiny clay cups, gold coins floating in the air, curious pose"),
  ("scene2-ramesh-stall", "a plain stickman with an apron standing proudly beside his small chai stall on a busy Indian street, one wooden bench, a kettle on a stove, morning light"),
  ("scene3-money-in", "the boss stickman counting gold coins into a small cash box on a wooden counter, one clay cup of chai beside it, calm knowing pose"),
  ("scene4-costs", "the boss stickman pointing at a small stack of gold coins split into three small piles on a whiteboard, a milk can, a gas cylinder and a rent paper as simple marker props"),
  ("scene5-customers", "three plain stickman customers standing in a short queue at a chai stall, the chai wala stickman pouring tea, one kettle and clay cups, busy morning"),
  ("scene6-smart-move", "the boss stickman tipping his fedora beside a chai stall with a small snack plate and a stack of gold notes, one folding stool, clever satisfied pose"),
  ("scene7-start-small", "a plain stickman setting up a tiny chai cart with one kettle, a stove and a folded umbrella, a few gold coins on the cart, hopeful morning street"),
  ("scene8-respect", "the boss stickman raising a clay cup of chai in respect toward a hardworking chai wala stickman, a small gold coin on the counter, warm calm mood"),
]

PICK_JS = """() => {
  try {
    const sels = Array.from(document.querySelectorAll('select'));
    const findSel = (pred) => sels.find(pred);
    const pick = (s, needle) => {
      if (!s) return 'NOSEL';
      const opts = Array.from(s.options);
      const o = opts.find(x => x.text.trim() === needle) || opts.find(x => x.text.indexOf(needle) >= 0);
      if (!o) return 'MISS';
      s.selectedIndex = opts.indexOf(o);
      s.dispatchEvent(new Event('input', {bubbles: true}));
      s.dispatchEvent(new Event('change', {bubbles: true}));
      return 'OK:' + o.text.trim();
    };
    // Do NOT touch the style select. Selecting "No style" (unicode 𝗡𝗼 𝘀𝘁𝘆𝗹𝗲 in
    // current Perchance) silently breaks generation: the button clicks but no
    // image ever appears. The default style plus the prompt's own style suffix
    // produced every usable frame, so only shape and count are set here.
    const shapeSel = findSel(s => Array.from(s.options).some(o => o.text.trim() === 'Landscape'));
    const countSel = findSel(s => { const t = Array.from(s.options).map(o=>o.text.trim()); return t.includes('2') && t.length <= 8; });
    return [pick(shapeSel, 'Landscape'), pick(countSel, '2')];
  } catch (e) { return ['ERR:' + e.message]; }
}"""

SET_PROMPT = """(p) => {
  const tas = Array.from(document.querySelectorAll('textarea.paragraph-input'));
  const t = tas.find(x => (x.placeholder||'').indexOf('store prompts') < 0) || tas[tas.length-1];
  t.focus(); t.value = p;
  t.dispatchEvent(new Event('input', {bubbles: true}));
  t.dispatchEvent(new Event('change', {bubbles: true}));
  t.blur();
  return t.value;
}"""

async def gallery_srcs(pg):
    out = set()
    for f in pg.frames:
        if 'image-generation.perchance.org/embed' not in f.url:
            continue
        try:
            srcs = await f.evaluate("() => Array.from(document.querySelectorAll('img')).map(i=>i.src)")
        except Exception:
            continue
        out.update(srcs)
    return out

async def gen_one(pg, gen, prompt):
    baseline = await gallery_srcs(pg)
    btn = await gen.query_selector('button:has-text("generate")')
    await btn.click()
    data = None
    for _ in range(150):
        await pg.wait_for_timeout(2000)
        for f in pg.frames:
            if 'image-generation.perchance.org/embed' not in f.url:
                continue
            try:
                srcs = await f.evaluate("() => Array.from(document.querySelectorAll('img')).map(i=>({s:i.src.slice(0,30), w:i.naturalWidth, full:i.src}))")
            except Exception:
                continue
            for s in srcs:
                if s['s'].startswith('data:image') and s['w'] > 200 and s['full'] not in baseline:
                    data = s['full']
                    break
            if data: break
        if data: break
    return data

async def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(SUBJECTS)
    async with async_playwright() as p:
        b = await p.firefox.launch(headless=True)
        ctx = await b.new_context(viewport={'width':1400,'height':900},
            user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0')
        await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        pg = await ctx.new_page()
        await pg.goto('https://perchance.org/ai-text-to-image-generator', timeout=60000)
        await pg.wait_for_timeout(6000)
        gen = [f for f in pg.frames if '.perchance.org/ai-text-to-image' in f.url and 'image-generation' not in f.url][0]
        print('controls:', await gen.evaluate(PICK_JS), flush=True)
        await pg.wait_for_timeout(3000)  # let the shape change re-render
        for i in range(start, min(end, len(SUBJECTS))):
            name, subj = SUBJECTS[i]
            out = os.path.join(OUTDIR, name + '.jpg')
            if os.path.exists(out) and os.path.getsize(out) > 20000:
                print(f'[{i+1}/{len(SUBJECTS)}] {name} SKIP exists', flush=True)
                continue
            prompt = subj + STYLE_SUFFIX
            # Perchance silently generates a random image if the prompt textarea
            # did not take the text. Verify the value before clicking.
            saved = False
            for attempt in range(3):
                got = await gen.evaluate(SET_PROMPT, prompt)
                if not got.startswith(prompt[:50]):
                    await pg.wait_for_timeout(800)
                    continue
                await pg.wait_for_timeout(400)
                data = await gen_one(pg, gen, prompt)
                if data:
                    raw = base64.b64decode(data.split(',',1)[1])
                    open(out,'wb').write(raw)
                    print(f'[{i+1}/{len(SUBJECTS)}] {name} OK {len(raw)}b', flush=True)
                    saved = True
                    break
                print(f'[{i+1}] {name} attempt {attempt+1} produced nothing', flush=True)
            if not saved:
                print(f'[{i+1}/{len(SUBJECTS)}] {name} FAIL', flush=True)
        await b.close()

asyncio.run(main())
