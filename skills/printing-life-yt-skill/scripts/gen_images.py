#!/usr/bin/env python3
"""Generate the scene plates for an episode with Perchance (free, no API key).

The script's `IMG:` line is the subject. The style suffix below is the channel
lock: flat 2D cartoon, thick ink outlines, muted historical palette, no text.
Perchance renders 768x512 landscape; prep_frames.py cover-crops to 1920x1080.

Perchance's headless-browser check blocks plain Playwright Firefox, so this
drives Camoufox (fingerprint-spoofed Firefox). If Camoufox is unavailable it
falls back to Playwright with the navigator.webdriver mask.

Outputs:
    images2/s01.jpg        chosen plate (first of the batch)
    images2/alt/s01_b.jpg  second option for picking later
    images2/prompts.json   exact prompts used (reproducibility)

Usage:
    env -u PYTHONPATH python3 gen_images.py script.md --workdir .
    ... --only s03 s04
    ... --style comic
    ... --force
    ... --start 0 --end 5
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plib import parse_script  # noqa: E402

# ---------------------------------------------------------------------------
# Style presets. `tintin` is the default: clear line, flat fill, period detail.
# Keep the "no text" clause in every preset; lettering is a separate layer.
# ---------------------------------------------------------------------------
STYLES = {
    "tintin": (
        "flat 2D cartoon illustration, clean-line comic style, thick uniform dark ink outlines "
        "of even weight, solid flat colour fills with no shading and no texture, clean simplified "
        "shapes, chibi characters with oversized heads and small blocky bodies, tiny black dot "
        "eyes, thick expressive eyebrows, no noses, muted historical palette of parchment cream, "
        "brick red, navy, mustard yellow and olive green, plain flat parchment background, "
        "stage-play composition, deadpan comedic historical explainer, 16:9 widescreen"
    ),
    "comic": (
        "flat 2D comic-book cartoon, bold black outlines, flat saturated colours, simple shapes, "
        "chibi characters with oversized heads, dot eyes and huge eyebrows, vintage print texture, "
        "muted red navy gold cream palette, comedic historical illustration, 16:9 widescreen"
    ),
    "flat": (
        "minimal flat vector cartoon, thick uniform dark outlines, solid flat colours, no shading, "
        "geometric simplified chibi characters with oversized heads and dot eyes, muted cream red "
        "navy gold palette, clean parchment background, comedic historical explainer, 16:9 widescreen"
    ),
}

NEGATIVE = (
    "no text, no letters, no numbers, no words, no captions, no logos, no watermark, "
    "no photorealism, no photograph, no 3D render, no CGI, no anime, no manga, "
    "no realistic faces, no detailed shading, no gradients, no glossy highlights, "
    "no crosshatching, no pencil texture, no sketch lines, "
    "no extra limbs, no deformed hands, no modern clothing unless the scene asks for it"
)

# Pure map plates get their own style: the shared preset mentions "chibi
# characters", which made the image model drop groups of children onto every
# map. Maps must stay cartography only; arrows and labels are overlay layers.
MAP_STYLE = (
    "flat 2D cartoon illustration, clean-line comic style, thick uniform dark ink outlines "
    "of even weight, solid flat colour fills with no shading and no texture, clean simplified "
    "shapes, antique parchment map seen from directly above, cartography only, completely "
    "uninhabited, no people, no characters, no figures, no faces, no portraits, no crowds, "
    "no armies, no ships, no compass rose, no labels, no lettering, no numbers, "
    "muted historical palette of parchment cream, brick red, navy, mustard yellow and olive "
    "green, flat parchment background, deadpan comedic historical explainer, 16:9 widescreen"
)

MAP_NEGATIVE = (
    "no text, no letters, no numbers, no words, no captions, no labels, no place names, "
    "no logos, no watermark, no people, no characters, no figures, no faces, no children, "
    "no crowds, no soldiers, no ships, no arrows, no map pins, no compass rose, "
    "no photorealism, no photograph, no 3D render, no CGI, no anime, no manga, "
    "no realistic faces, no detailed shading, no gradients, no glossy highlights, "
    "no crosshatching, no pencil texture, no sketch lines, no extra limbs"
)

PICK_JS = """(want) => {
  try {
    const sels = Array.from(document.querySelectorAll('select'));
    const findSel = (pred) => sels.find(pred);
    const pick = (s, needle) => {
      if (!s) return 'NOSEL';
      const opts = Array.from(s.options);
      let o = opts.find(x => x.text.trim() === needle)
           || opts.find(x => x.text.toLowerCase().includes(needle.toLowerCase()));
      if (!o) return 'MISS';
      s.selectedIndex = opts.indexOf(o);
      s.dispatchEvent(new Event('input', {bubbles: true}));
      s.dispatchEvent(new Event('change', {bubbles: true}));
      return 'OK:' + o.text.trim();
    };
    const styleSel = findSel(s => Array.from(s.options).some(o => o.text.includes('Painted Anime')));
    const shapeSel = findSel(s => Array.from(s.options).some(o => o.text.trim() === 'Landscape'));
    const countSel = findSel(s => {
      const t = Array.from(s.options).map(o => o.text.trim());
      return t.includes('2') && t.length <= 8;
    });
    let style = pick(styleSel, want);
    if (style === 'MISS' || style === 'NOSEL') style = pick(styleSel, 'Tintin Comic');
    if (style === 'MISS' || style === 'NOSEL') style = pick(styleSel, 'Franco-Belgian Comic');
    if (style === 'MISS' || style === 'NOSEL') style = pick(styleSel, 'Vintage Comic');
    return [style, pick(shapeSel, 'Landscape'), pick(countSel, '2')];
  } catch (e) { return ['ERR:' + e.message]; }
}"""

SET_PROMPT_JS = """(p) => {
  const tas = Array.from(document.querySelectorAll('textarea.paragraph-input'));
  const t = tas.find(x => (x.placeholder || '').indexOf('store prompts') < 0)
         || tas[tas.length - 1];
  if (!t) return false;
  t.focus(); t.value = p;
  t.dispatchEvent(new Event('input', {bubbles: true}));
  t.dispatchEvent(new Event('change', {bubbles: true}));
  return true;
}"""


async def gallery_srcs(page) -> set[str]:
    """All image srcs currently on screen, from every frame."""
    out: set[str] = set()
    for frame in page.frames:
        try:
            srcs = await frame.evaluate(
                "() => Array.from(document.querySelectorAll('img')).map(i => i.src)"
            )
        except Exception:
            continue
        out.update(srcs)
    return out


async def blocked(page) -> bool:
    for frame in page.frames:
        try:
            txt = await frame.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception:
            continue
        if "Anti-bot verification failed" in txt:
            return True
    return False


async def generate_batch(app, page, want: int, baseline: set[str],
                         timeout_s: int = 300) -> list[str]:
    """Click generate in the app frame and collect fresh data-URL images."""
    btn = await app.query_selector("#generateButtonEl")
    if btn is None:
        btn = await app.query_selector('button:has-text("generate")')
    if btn is None:
        raise RuntimeError("Perchance generate button not found")
    await btn.click()

    found: list[str] = []
    waited = 0
    while waited < timeout_s:
        await page.wait_for_timeout(2000)
        waited += 2
        for frame in page.frames:
            try:
                imgs = await frame.evaluate(
                    "() => Array.from(document.querySelectorAll('img'))"
                    ".map(i => ({src: i.src, w: i.naturalWidth}))"
                )
            except Exception:
                continue
            for img in imgs:
                src = img["src"]
                if (
                    src.startswith("data:image")
                    and img["w"] > 200
                    and src not in baseline
                    and src not in found
                ):
                    found.append(src)
        if len(found) >= want:
            return found
        if found and waited > 12:
            # The site sometimes returns fewer than requested; take what came.
            return found
    return found


def save_data_url(src: str, path: Path) -> int:
    raw = base64.b64decode(src.split(",", 1)[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return len(raw)


async def open_app(page) -> tuple:
    await page.goto("https://perchance.org/ai-text-to-image-generator", timeout=90000)
    await page.wait_for_timeout(7000)
    try:
        app = [
            f for f in page.frames
            if ".perchance.org/ai-text-to-image" in f.url and "image-generation" not in f.url
        ][0]
    except IndexError:
        raise SystemExit("could not find the generator frame on the page")
    return app


async def run_session(browser, ep, targets, outdir, alt_dir, log_path, prompts_log,
                      style_key, style_text, style_want, args) -> None:
    page = await browser.new_page()
    app = await open_app(page)
    print("controls:", await app.evaluate(PICK_JS, style_want), flush=True)

    for n, scene in enumerate(targets, 1):
        dest = outdir / f"{scene.id}.jpg"
        if dest.is_file() and dest.stat().st_size > 20000 and not args.force:
            print(f"[{n}/{len(targets)}] {scene.id} skip (exists)", flush=True)
            continue

        if n % max(1, args.reload_every) == 1 and n > 1:
            page = await browser.new_page()
            app = await open_app(page)
            await app.evaluate(PICK_JS, style_want)

        subject = scene.prompt
        for name, desc in ep.cast.items():
            subject = subject.replace("{" + name + "}", desc)
        is_map = "aged parchment map" in subject.lower()
        prompt = f"{subject}. {MAP_STYLE if is_map else style_text}. {MAP_NEGATIVE if is_map else NEGATIVE}"
        prompts_log[scene.id] = {"prompt": prompt,
                                 "style": f"{style_key}-map" if is_map else style_key}
        log_path.write_text(json.dumps(prompts_log, indent=2))

        ok = False
        for attempt in range(1, args.retries + 1):
            if await blocked(page):
                print(f"[{n}/{len(targets)}] {scene.id} anti-bot, reloading", flush=True)
                page = await browser.new_page()
                app = await open_app(page)
                await app.evaluate(PICK_JS, style_want)

            if not await app.evaluate(SET_PROMPT_JS, prompt):
                print(f"[{n}/{len(targets)}] {scene.id} prompt box missing", flush=True)
            baseline = await gallery_srcs(page)
            try:
                batch = await generate_batch(app, page, getattr(args, "variants", 2),
                                             baseline)
            except Exception as exc:
                print(f"[{n}/{len(targets)}] {scene.id} FAIL {exc}", flush=True)
                batch = []
            if not batch:
                print(f"[{n}/{len(targets)}] {scene.id} retry {attempt}/{args.retries}",
                      flush=True)
                await page.wait_for_timeout(4000)
                continue
            size = save_data_url(batch[0], dest)
            for k, extra in enumerate(batch[1:], start=2):
                save_data_url(extra, alt_dir / f"{scene.id}_{chr(96 + k)}.jpg")
            print(f"[{n}/{len(targets)}] {scene.id} ok {size // 1024}KB "
                  f"({len(batch)} options)", flush=True)
            ok = True
            break
        if not ok:
            print(f"[{n}/{len(targets)}] {scene.id} GAVE UP", flush=True)


async def main_async(args) -> int:
    from playwright.async_api import async_playwright

    script_path = Path(args.script).expanduser().resolve()
    ep = parse_script(script_path)
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else script_path.parent
    outdir = (workdir / args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    alt_dir = outdir / "alt"

    style_key = (args.style or ep.style or "tintin").lower()
    if style_key not in STYLES:
        print(f"Unknown style {style_key!r}; using tintin. Known: {list(STYLES)}")
        style_key = "tintin"
    style_text = STYLES[style_key]
    style_want = {"tintin": "Tintin Comic", "comic": "Vintage Comic",
                  "flat": "2D Disney"}.get(style_key, "Tintin Comic")

    targets = []
    for i, scene in enumerate(ep.scenes):
        if args.only and scene.id not in set(args.only):
            continue
        if args.start is not None and i < args.start:
            continue
        if args.end is not None and i >= args.end:
            continue
        if not scene.prompt:
            continue
        targets.append(scene)
    if not targets:
        print("No scenes with an IMG: prompt in range.")
        return 0

    prompts_log = {}
    log_path = outdir / "prompts.json"
    if log_path.is_file():
        prompts_log = json.loads(log_path.read_text())

    common = (ep, targets, outdir, alt_dir, log_path, prompts_log,
              style_key, style_text, style_want, args)

    try:
        from camoufox.async_api import AsyncCamoufox

        async with AsyncCamoufox(headless=True, humanize=True, geoip=False) as browser:
            print("engine: camoufox", flush=True)
            await run_session(browser, *common)
    except ImportError:
        print("camoufox not installed; using playwright firefox", flush=True)
        async with async_playwright() as p:
            browser = await p.firefox.launch(headless=True)
            ctx = await browser.new_context(
                viewport={"width": 1400, "height": 900},
                user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
            )
            await ctx.add_init_script(
                "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});"
            )
            await run_session(browser, *common)
            await browser.close()

    print(f"\nPlates -> {outdir}")
    print(f"Prompts -> {log_path}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Perchance scene generator for Printing Life")
    ap.add_argument("script")
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--outdir", default="images2")
    ap.add_argument("--style", default=None, choices=sorted(STYLES))
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--start", type=int, default=None)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--variants", type=int, default=2, choices=[1, 2])
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--reload-every", type=int, default=20)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
