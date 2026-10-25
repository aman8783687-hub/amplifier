import asyncio, base64, os, sys
from playwright.async_api import async_playwright

OUTDIR = os.environ.get("WILD_THINKING_IMAGES", os.path.join(os.getcwd(), "images"))
os.makedirs(OUTDIR, exist_ok=True)

STYLE_SUFFIX = ", cinematic European hand-painted watercolor gouache, loose dark ink linework, visible brush strokes, textured paper, muted earthy palette warm beige dusty brown faded olive muted blue charcoal cream, soft natural light, atmospheric, vintage European animated film still, 16:9 widescreen, no photorealism no 3D no CGI no anime no vector"

SUBJECTS = [
  ("scene1-candle-cave", "black cave interior single flickering candle light, ancient human figure standing over a still body on stone floor, torches on walls, shadows, solemn mood, prehistoric"),
  ("scene2-atapuerca-shaft", "deep vertical cave shaft pit of bones, archaeologists lowering ancient human skeletons into darkness, limestone cave walls, dramatic overhead light, prehistoric burial site"),
  ("scene3-burying-body", "ancient family digging grave in earth at dusk, body wrapped in animal hide, scavenging animals watching in background, torches, solemn cooperative effort"),
  ("scene4-shanidar-flowers", "Neanderthal skeleton in cave grave surrounded by scattered wildflowers yarrow cornflower, red ochre dust, ancient burial, tender grief, soft cave light"),
  ("scene5-sungir-beads", "two ancient children buried head to head, thousands of ivory beads covering bodies, mammoth tusk spears, fox tooth pendants, Upper Paleolithic grave, shimmering"),
  ("scene6-neanderthal-elder", "elderly Neanderthal man with heavy brow arthritic joints, lying in simple grave, community members standing around with care, La Chapelle cave, compassionate burial"),
  ("scene7-cave-art-spirit", "cave wall paintings of animals and handprints, ghostly spirit figure rising from a grave walking into painted animals, Lascaux, mystical ancient belief"),
  ("scene8-mourning-globe", "globe of earth with mourning rituals, Tibetan sky burial vultures, Egyptian mummy, Aboriginal Dreamtime landscape, ancient funeral scenes around world, warm light"),
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
                print(f'[{i+1}/{len(SUBJECTS)}] {name} SKIP exists', flush=True)
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
                print(f'[{i+1}/{len(SUBJECTS)}] {name} OK {len(raw)}b', flush=True)
            else:
                print(f'[{i+1}/{len(SUBJECTS)}] {name} FAIL timeout', flush=True)
        await b.close()

asyncio.run(main())
PY