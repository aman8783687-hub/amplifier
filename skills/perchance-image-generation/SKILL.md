---
name: perchance-image-generation
description: Generate images totally free and unlimited via Perchance AI text-to-image with masked headless Firefox + Playwright. Use whenever user mentions Perchance, perchance.org, ai-text-to-image-generator, free image generation, bulk images, coloring pages, KDP interiors, cinematic stills, or needs $0 no-login no-API-key image gen. Always use this skill for Perchance tasks even if user just says generate image free.
---

# Perchance Free Unlimited Image Generation

Perchance has no usable API for scripts. Drive its real website with masked headless Firefox and steal inline base64 pixels. $0, no login, no API key. Tested 50/50 ~1/min zero failures (Oct 2026).

## When NOT to use
- Direct `requests` to `image-generation.perchance.org/api/*` = 403 Cloudflare. Don't retry.
- `page.request` download / `downloadTemporaryImage?imageId=` in new tab = 403/404. Don't chase imageIds.
- MCP / browser-extension JS can't read results (cross-origin nested `image-generation.perchance.org/embed` iframes, `contentDocument` null). Must use Playwright CDP-level automation.
- GitHub `aein00/perchance-image-generator` CLI is broken (2023, same 403). Don't use.

## 0. Environment
```bash
env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 -c "import playwright; print('ok')"
# if missing:
pip install --user --break-system-packages requests playwright Pillow
env -u PYTHONHOME -u PYTHONPATH python3 -m playwright install firefox
```
Always prefix python with `env -u PYTHONHOME -u PYTHONPATH` in this env (mount breaks otherwise).

## 1. Stealth launch (REQUIRED - without this Generate silently does nothing)
```python
b = await p.firefox.launch(headless=True)
ctx = await b.new_context(
    viewport={'width':1400,'height':900},
    user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0')
await ctx.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
pg = await ctx.new_page()
await pg.goto('https://perchance.org/ai-text-to-image-generator', timeout=60000)
await pg.wait_for_timeout(6000)
```
Proof: without mask zero `/api/*` traffic after click. With mask `verifyUser` + `generate?userKey=` fire immediately.

## 2. Pick correct frame (trap: top page AND subframe both match URL)
```python
gen = [f for f in pg.frames if '.perchance.org/ai-text-to-image' in f.url and 'image-generation' not in f.url][0]
```
Must contain `.perchance.org/ai-text-to-image` with leading dot, exclude `image-generation`.

## 3. Set controls by option TEXT, never index (layout changes per load: 3 or 5 selects)
See `scripts/generate.py` PICK_JS. Pattern:
- Find style select = select containing `Painted Anime` option, then pick by text: `Concept Sketch` for coloring pages, `Watercolor` / `Painterly` / `Cinematic` / `Tintin Comic` for cinematic work
- Find shape select = select containing `Portrait` option, pick `Portrait` / `Landscape` / `Square`
- Find count select = options include `2` and len<=8, pick `2` (minimum, keep first new image)
- Set via JS `selectedIndex` + `input` + `change` events. `select_option(label=)` fails (custom-styled).
- Description box = `textarea.paragraph-input` whose placeholder does NOT contain `store prompts` (other is scratchpad). Set via focus + value + input/change, not `fill` alone.

Available styles probed Oct 2026 (79): Painted Anime | Casual Photo | Cinematic | Digital Painting | Concept Art | No style | 3D Disney | 2D Disney | Disney Sketch | Concept Sketch | Painterly | Oil Painting | Watercolor | Franco-Belgian Comic | Tintin Comic | Vintage Comic | ... Shapes: Square | Portrait | Landscape. Counts: 4|6|8|16|32|2.

## 4. Prompt patterns
- Toddler coloring: `{subject}, children coloring book page, pure black outlines only, thick bold lines, white fill, no solid black areas, no gray shading, no colors, one single centered subject, plain white background`
- Cinematic watercolor: `{scene}, cinematic European hand-painted watercolor gouache, loose dark ink linework, visible brush strokes, textured paper, muted earthy palette warm beige dusty brown faded olive muted blue charcoal cream, soft natural light, atmospheric, vintage European animated film still, 16:9 widescreen, no photorealism no 3D no CGI no anime no vector`

## 5. Capture loop (per image, ~45-70s)
1. Snapshot baseline: all `img.src` across `image-generation.perchance.org/embed` frames BEFORE click
2. Click `button:has-text("generate")`
3. Poll every 2s up to ~5min: first `img` with `src startswith data:image` AND `naturalWidth > 200` AND src not in baseline = new image
4. `base64.b64decode(src.split(',',1)[1])` -> save `.jpg`
5. Skip if exists >20KB (resume: `script.py START END`)

Landscape output = 768x512. Portrait = 512x768.

## 6. Run
```bash
env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 scripts/generate.py 0 2 > /tmp/bulk.log 2>&1 &
tail -f /tmp/bulk.log
# 0 2 = test, 0 50 = full, 21 50 = resume
```

## Bundled resources
- `scripts/generate.py` - generic bulk generator (edit SUBJECTS + STYLE_SUFFIX + PICK_JS for task)
- `references/playbook.md` - full playbook + every dead end (Oct 2026)
- `references/examples.md` - coloring-page vs cinematic presets

Full details: read `references/playbook.md` before debugging site changes.
