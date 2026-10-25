import asyncio, base64, os, sys
from playwright.async_api import async_playwright

OUTDIR = os.environ.get("PERCHANCE_OUTDIR", os.path.join(os.getcwd(), "perchance_output"))
os.makedirs(OUTDIR, exist_ok=True)

# Condensed prompts: keep scene essentials + master style keywords.
# Style dropdown = Watercolor, Shape = Landscape, so no need to repeat 2000 chars.
STYLE_SUFFIX = ", cinematic European hand-painted watercolor gouache, loose dark ink linework, visible brush strokes, textured paper, muted earthy palette warm beige dusty brown faded olive muted blue charcoal cream, soft natural light, atmospheric, vintage European animated film still, 16:9 widescreen, no photorealism no 3D no CGI no anime no vector"

SUBJECTS = [
  ("scene1-waking-up",
   "early morning 4:45 AM young airline pilot waking alone modest hotel room near airport, sitting on bed edge tired white undershirt dark trousers, uniform jacket on chair, glowing alarm clock, pale blue light through curtains, flight bag on floor, distant airport lights in mist"),
  ("scene2-walking-airport",
   "morning large international airport apron, same young airline pilot walking toward passenger airplane carrying flight bag, white pilot shirt epaulettes black tie, ground crew baggage carts service vehicles, terminal control tower pale cloudy sky, focused tired checking clipboard"),
  ("scene3-inside-cockpit",
   "inside commercial airplane cockpit before takeoff, same young pilot left seat white uniform black tie, older pilot beside him, analog instruments switches displays, soft morning sunlight, runway through windshield, pre-flight conversation, documentary feeling"),
  ("scene4-above-clouds",
   "commercial airplane high above vast clouds, same young pilot in cockpit seen from behind at controls, enormous white clouds horizon pale blue sky, dark cockpit interior instrument lights on hands uniform, calm contemplative, dark vs luminous contrast"),
  ("scene5-sudden-storm",
   "commercial airplane in powerful storm, same young pilot gripping controls both hands intensely focused, dark cockpit instrument lights, heavy rain windshield, dark clouds lightning distance, first officer instruments captain radio, tense dramatic hand-painted documentary"),
]

PICK_JS = """() => {
  try {
    const sels = Array.from(document.querySelectorAll('select'));
    const findSel = (pred) => sels.find(pred);
    const pick = (s, needle) => {
      if (!s) return 'NOSEL';
      const opts = Array.from(s.options);
      let o = opts.find(x => x.text.trim() === needle) || opts.find(x => x.text.indexOf(needle) >= 0);
      if (!o) return 'MISS';
      s.selectedIndex = opts.indexOf(o);
      s.dispatchEvent(new Event('input', {bubbles: true}));
      s.dispatchEvent(new Event('change', {bubbles: true}));
      return 'OK:' + o.text.trim();
    };
    const styleSel = findSel(s => Array.from(s.options).some(o => o.text.indexOf('Painted Anime') >= 0));
    const shapeSel = findSel(s => Array.from(s.options).some(o => o.text.trim() === 'Landscape'));
    const countSel = findSel(s => { const t = Array.from(s.options).map(o=>o.text.trim()); return t.includes('2') && t.length <= 8; });
    return [pick(styleSel, 'Watercolor'), pick(shapeSel, 'Landscape'), pick(countSel, '2')];
  } catch (e) { return ['ERR:' + e.message]; }
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
        for i in range(start, min(end, len(SUBJECTS))):
            name, subj = SUBJECTS[i]
            out = os.path.join(OUTDIR, name + '.jpg')
            if os.path.exists(out) and os.path.getsize(out) > 20000:
                print(f'[{i+1}/5] {name} SKIP exists', flush=True)
                continue
            prompt = subj + STYLE_SUFFIX
            await gen.evaluate("""(p) => {
              const tas = Array.from(document.querySelectorAll('textarea.paragraph-input'));
              const t = tas.find(x => (x.placeholder||'').indexOf('store prompts') < 0) || tas[tas.length-1];
              t.focus(); t.value = p;
              t.dispatchEvent(new Event('input', {bubbles: true}));
              t.dispatchEvent(new Event('change', {bubbles: true}));
            }""", prompt)
            data = await gen_one(pg, gen, prompt)
            if data:
                raw = base64.b64decode(data.split(',',1)[1])
                open(out,'wb').write(raw)
                print(f'[{i+1}/5] {name} OK {len(raw)}b', flush=True)
            else:
                print(f'[{i+1}/5] {name} FAIL timeout', flush=True)
        await b.close()

asyncio.run(main())
