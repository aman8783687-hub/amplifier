import json, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myntra_41573047")
info = json.load(open(os.path.join(BASE, "product_info.json")))
imgs = sorted(os.listdir(os.path.join(BASE, "images")))
vids = [f for f in sorted(os.listdir(os.path.join(BASE, "video"))) if f.endswith(".mp4")]

cards = "\n".join(
    f'<figure><a href="images/{f}" target="_blank"><img src="images/{f}" loading="lazy" alt="Saree image {i}"></a>'
    f'<figcaption><span>Image {i:02d}</span> 1620×2160 <a href="images/{f}" download>Download</a></figcaption></figure>'
    for i, f in enumerate(imgs, 1)
)
vcards = "\n".join(
    f'<figure class="v"><video src="video/{v}" poster="video/rampwalk_poster.jpg" controls preload="metadata"></video>'
    f'<figcaption><span>{v}</span> <a href="video/{v}" download>Download</a></figcaption></figure>'
    for v in vids
)

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{info['name']} — Myntra assets</title>
<style>
  :root {{ --pink:#ff3f6c; --ink:#282c3f; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,"Segoe UI",Roboto,Arial,sans-serif; background:#f5f5f6; color:var(--ink); }}
  header {{ padding:28px 24px 20px; background:#fff; border-bottom:1px solid #eaeaec; }}
  .brand {{ color:var(--pink); font-weight:800; letter-spacing:.14em; font-size:12px; text-transform:uppercase; }}
  h1 {{ font-size:24px; margin:8px 0 10px; line-height:1.25; max-width:900px; }}
  .meta {{ display:flex; gap:16px; flex-wrap:wrap; align-items:center; font-size:14px; color:#535766; }}
  .price {{ font-size:20px; font-weight:700; color:var(--ink); }}
  .price s {{ font-weight:400; color:#94969f; font-size:14px; margin-left:6px; }}
  .off {{ color:#03a685; font-weight:700; }}
  main {{ padding:24px; max-width:1400px; margin:0 auto; }}
  h2 {{ font-size:13px; letter-spacing:.12em; text-transform:uppercase; color:#94969f; margin:8px 0 14px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px; }}
  figure {{ margin:0; background:#fff; border-radius:10px; overflow:hidden; box-shadow:0 1px 2px rgba(40,44,63,.08); }}
  figure img, figure video {{ display:block; width:100%; aspect-ratio:3/4; object-fit:cover; background:#eee; }}
  figcaption {{ display:flex; justify-content:space-between; gap:8px; padding:10px 12px; font-size:12px; color:#94969f; }}
  figcaption span {{ color:var(--ink); font-weight:600; }}
  figcaption a {{ color:var(--pink); text-decoration:none; font-weight:600; }}
  .row {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:16px; margin-bottom:30px; }}
  .note {{ font-size:12px; color:#94969f; margin-top:26px; }}
  a.src {{ color:#535766; }}
</style>
</head>
<body>
<header>
  <div class="brand">Myntra · {info['brand']}</div>
  <h1>{info['name']}</h1>
  <div class="meta">
    <span class="price">₹{info['price']['discounted']:,} <s>₹{info['price']['mrp']:,}</s></span>
    <span class="off">{round((1 - info['price']['discounted']/info['price']['mrp'])*100)}% OFF</span>
    <span>Product ID {info['productId']}</span>
    <a class="src" href="{info['url']}" target="_blank">View on Myntra ↗</a>
  </div>
</header>
<main>
  <h2>Video · {len(vids)} files</h2>
  <div class="row">
{vcards}
  </div>
  <h2>Images · {len(imgs)} files (1620 × 2160)</h2>
  <div class="grid">
{cards}
  </div>
  <p class="note">Files are stored locally in <code>images/</code> (1620×2160), <code>images_1080/</code> (1080×1440) and <code>video/</code>.
  Downloaded from the live product page; assets belong to Myntra / Anouk.</p>
</main>
</body>
</html>"""

open(os.path.join(BASE, "gallery.html"), "w").write(html)
print("gallery written")
