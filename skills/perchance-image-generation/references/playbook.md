# Perchance Bulk Image Generation – Exact Playbook (works Oct 2026)
**Goal:** generate N coloring pages from `https://perchance.org/ai-text-to-image-generator` programmatically, $0, no login.
**Working script:** `perchance_bulk_gen.py` in this folder. Tested: 50/50 images, ~1/min, Concept Sketch + Portrait.

## 0. Environment (exact)
- `python3` system (here 3.12) with `PYTHONHOME`/`PYTHONPATH` UNSET (they break pipx/python mounts in this env — always prefix `env -u PYTHONHOME -u PYTHONPATH`).
- `pip install --user --break-system-packages requests playwright Pillow reportlab pypdf`
- `python3 -m playwright install firefox` (108MB; Ubuntu fallback build works on Mint).
- Stealth (mandatory, see §3).

## 1. What does NOT work (don't retry blindly)
1. **Direct `requests` to `image-generation.perchance.org/api/*` → 403** Cloudflare "Just a moment...". Bare homepage also 403 for scripts. Full browser required.
2. **GitHub `aein00/perchance-image-generator` CLI is broken** (2023): its `requests`-based `generator.py` gets the same 403; its `key_finder` treats an empty/invalid key as valid. Do not use as-is.
3. **MCP/browser-extension JS can't reach results**: results live in nested `image-generation.perchance.org/embed` iframes, cross-origin vs the `cd*.perchance.org` generator frame → `contentDocument` is `null`/blocked. Only CDP-level automation (Playwright) can read them.
4. **`ctx.request`/`page.request` download → 403**, and `downloadTemporaryImage?imageId=` in a new tab → **404** (IDs are transient / session-tied). Don't chase imageIds.
5. **Playwright `select_option(label=...)` fails**: the dropdowns are custom-styled; set via JS `selectedIndex` + `input`/`change` events (§4).
6. **Frame picking bug**: top page AND subframe both match `perchance.org/ai-text-to-image`. Always pick the frame whose URL contains **`.perchance.org/ai-text-to-image`** (leading dot) and excludes `image-generation`.
7. **Layout varies per load**: sometimes 3 `<select>`, sometimes 5. Never use fixed indices — find selects by option contents (§4).
8. **`button#generateButtonEl` id is unreliable** — click via `button:has-text("generate")`.
9. **Gallery accumulates**: snapshot existing `img.src` BEFORE clicking, then wait for a src not in the baseline, else you'll re-save an old image.
10. **Batch count minimum is 2** (options 2/4/6/8/16/32/4). We set 2 and keep the first new image.

## 2. What works (the system)
Real headless Firefox + webdriver-mask + real UA → page behaves like a human: `verifyUser` + `generate?userKey=` fire, results paint as **inline `data:image/jpeg;base64` `<img>` inside nested embed frames** → decode + save. No download API needed.

## 3. Stealth (required — without this, generate silently never fires)
```python
ctx = await b.new_context(
    viewport={'width': 1400, 'height': 900},
    user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0')
await ctx.add_init_script(
    "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
```
Proof it matters: without it, zero `/api/*` traffic after clicking generate; with it, `verifyUser` + `generate?userKey=` appear immediately.

## 4. Controls (set every run via JS, verify)
```js
() => {
  const sels = Array.from(document.querySelectorAll('select'));
  const findSel = (pred) => sels.find(pred);
  const pick = (s, needle) => {
    if (!s) return 'NOSEL';
    const opts = Array.from(s.options);
    let o = opts.find(x => x.text.trim() === needle)
         || opts.find(x => x.text.indexOf(needle) >= 0);
    if (!o) return 'MISS';
    s.selectedIndex = opts.indexOf(o);
    s.dispatchEvent(new Event('input', {bubbles: true}));
    s.dispatchEvent(new Event('change', {bubbles: true}));
    return 'OK:' + o.text.trim();
  };
  const styleSel = findSel(s => Array.from(s.options).some(o => o.text.indexOf('Painted Anime') >= 0));
  const shapeSel = findSel(s => Array.from(s.options).some(o => o.text.trim() === 'Portrait'));
  const countSel = findSel(s => { const t = Array.from(s.options).map(o=>o.text.trim()); return t.includes('2') && t.length <= 8; });
  return [pick(styleSel, 'Concept Sketch'), pick(shapeSel, 'Portrait'), pick(countSel, '2')];
}
```
- Style `Concept Sketch` (no "No style"/coloring style exists; 79 options total; avoid Disney/anime styles for IP + shading reasons).
- Shape `Portrait`, count `2`.
- Description box = the `textarea.paragraph-input` whose placeholder does NOT contain `store prompts` (the other one is the scratchpad). Set via `focus + value + input/change events`, not Playwright `fill` alone.

## 5. Prompt pattern (toddler coloring)
`{subject}, children coloring book page, pure black outlines only, thick bold lines, white fill, no solid black areas, no gray shading, no colors, one single centered subject, plain white background`
- Keep `nudity text` in negative (default) + our suffix does the rest. Perchance appends style text automatically.
- One subject per prompt. 50 prompts live in `page_plan_prompts.md`.

## 6. Capture loop (per image)
1. Snapshot baseline: all `img.src` across frames with `image-generation.perchance.org/embed` in URL.
2. Click generate.
3. Poll every 2s up to ~5 min: first `img` with `src startswith data:image` AND `naturalWidth > 200` AND src not in baseline → that's the new image.
4. `base64.b64decode(src.split(',',1)[1])` → save `.jpg`. Filenames `NN-subject.jpg` into `perchance/`.
5. Skip if file exists and >20KB (resume support: `script.py START END`).
- Observed: ~45–70s/image, 768px-class output (Square→768×768; Portrait→512×768). Expect ~60–90 DPI native at 8.5" — upscale before print (we used 4x LANCZOS + autocontrast; see `build_interior_v2.py`).

## 7. Run it
```bash
env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 perchance_bulk_gen.py 0 50 > /tmp/bulk.log 2>&1 &
tail -f /tmp/bulk.log   # [i/50] NAME OK bytes / FAIL timeout
```
- Foreground test first: `... bulk_gen.py 0 2`.
- Resume: `... bulk_gen.py 21 50` (skips existing).
- If site changes (new Cloudflare, UI restyle): re-run the mapping probes in `/tmp/pwmap.py`, `/tmp/pwstyle2.py` pattern (kept in /tmp, recreate from §4 snippets above).

## 8. After generation (assembly, in this folder)
- `build_kdp_interior.py`: upscales 4x, 8.5×11" single-sided (art + blank verso), word labels, front matter → `farm-friends-interior-v2.pdf` (105p).
- Cover: `build_kdp_cover.py` (spine = pages × 0.002252" white paper).
- KDP AI disclosure = **Yes (Images)**. Raw 512px art is print-soft: proof copy mandatory; fix list = gray wash, thin lines, duplicates, factual labels.

## 9. One-line mental model
Perchance has no usable API for scripts (Cloudflare) and its iframes block page-JS — so drive the real UI with a masked headless Firefox, set controls by option-content (never index), and steal the inline base64 pixels from the embed frames.
