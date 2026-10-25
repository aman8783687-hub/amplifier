# Presets - coloring vs cinematic

## A. Toddler coloring pages (KDP, 50/50 tested)
- Style: `Concept Sketch`
- Shape: `Portrait` (512x768)
- Count: `2`
- Suffix: `, children coloring book page, pure black outlines only, thick bold lines, white fill, no solid black areas, no gray shading, no colors, one single centered subject, plain white background`
- Example subject: `cute smiling baby cow standing side view, big oval body with spots`
- Full file: ad-hoc script from the original run (not bundled) — same pattern as `scripts/generate.py`
- After: upscale 4x LANCZOS + autocontrast, assemble with `build_kdp_interior.py` -> 105-page PDF. KDP AI disclosure = Yes (Images).

## B. Cinematic European watercolor (pilot test, 5/5 tested Oct 2026)
- Style: `Watercolor` (alternatives: `Painterly`, `Cinematic`, `Tintin Comic`, `Franco-Belgian Comic`)
- Shape: `Landscape` (768x512, crop to 768x432 for exact 16:9)
- Count: `2`
- Suffix: `, cinematic European hand-painted watercolor gouache, loose dark ink linework, visible brush strokes, textured paper, muted earthy palette warm beige dusty brown faded olive muted blue charcoal cream, soft natural light, atmospheric, vintage European animated film still, 16:9 widescreen, no photorealism no 3D no CGI no anime no vector`
- Example subjects: 5 scenes — see `SUBJECTS` in `scripts/generate.py`
- Outputs: `<OUTDIR>/scene*.jpg` — see `OUTDIR` in `scripts/generate.py`

## Switching
Edit in `scripts/generate.py`:
1. `SUBJECTS = [(name, prompt-without-suffix), ...]`
2. `STYLE_SUFFIX = ...`
3. `PICK_JS` needles: `pick(styleSel, 'Concept Sketch'|'Watercolor'|...)`, `pick(shapeSel, 'Portrait'|'Landscape')`
4. `OUTDIR = ...`
Run: `env -u PYTHONHOME -u PYTHONPATH /usr/bin/python3 scripts/generate.py 0 2` test, then full.
