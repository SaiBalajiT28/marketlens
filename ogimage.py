"""Draws docs/og.png: the preview picture shown when the site link is shared."""
import json, os, re, time
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
IST = timezone(timedelta(hours=5, minutes=30))

def _font(size, bold=True):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def inr(n):
    s = str(int(round(n))); 
    if len(s) <= 3: return "₹" + s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2: parts.insert(0, head[-2:]); head = head[:-2]
    if head: parts.insert(0, head)
    return "₹" + ",".join(parts) + "," + tail

def _arrow(v):
    l = v["label"]
    return ("▲ likely to rise", (30, 127, 85)) if l == "lean buy" else ("▼ likely to fall", (184, 57, 43)) if l == "lean sell" else ("• could go either way", (107, 116, 131))

def make(latest_path="docs/latest.json", out="docs/og.png"):
    L = json.load(open(latest_path))
    img = Image.new("RGB", (W, H), (243, 244, 246))
    d = ImageDraw.Draw(img)
    # soft metallic wash
    for i in range(H):
        t = i / H
        d.line([(0, i), (W, i)], fill=(int(243 - 8 * t), int(244 - 10 * t), int(246 - 6 * t)))
    d.ellipse([700, -250, 1400, 350], fill=(236, 226, 190))
    d.ellipse([-300, 350, 500, 900], fill=(226, 229, 236))
    # brand
    d.rounded_rectangle([60, 56, 92, 88], 8, fill=(201, 162, 74))
    d.text((106, 52), "MarketLens", font=_font(34), fill=(23, 26, 33))
    ts = datetime.fromtimestamp(L["run_time"], IST).strftime("%d %b %Y, %I:%M %p IST")
    d.text((W - 60, 62), ts, font=_font(22, False), fill=(95, 103, 117), anchor="ra")

    def card(x, key, title, sub):
        a = L["assets"].get(key)
        d.rounded_rectangle([x, 150, x + 520, 540], 24, fill=(255, 255, 255), outline=(214, 196, 140) if key == "GOLD" else (205, 211, 220), width=3)
        d.ellipse([x + 32, 184, x + 72, 224], fill=(216, 183, 90) if key == "GOLD" else (205, 211, 220))
        d.text((x + 88, 186), title, font=_font(30), fill=(23, 26, 33))
        d.text((x + 32, 240), sub, font=_font(20, False), fill=(95, 103, 117))
        if not a: d.text((x + 32, 300), "not available", font=_font(28), fill=(107, 116, 131)); return
        r = a["rates"]
        d.text((x + 32, 285), inr(r["inr_india_est"]), font=_font(68), fill=(23, 26, 33))
        d.text((x + 32, 372), f"per {r['unit']}", font=_font(22, False), fill=(95, 103, 117))
        ch = a.get("change_1d_pct")
        if ch is not None:
            col = (30, 127, 85) if ch > 0 else (184, 57, 43) if ch < 0 else (107, 116, 131)
            d.text((x + 32, 420), f"{'+' if ch > 0 else ''}{ch:.2f}% today", font=_font(26), fill=col)
        t, col = _arrow(a["horizons"]["1d"])
        d.text((x + 32, 470), "Tomorrow: " + t, font=_font(24, False), fill=col)
    card(60, "GOLD", "Gold 24K", "India price, incl. duty & GST")
    card(620, "SILVER", "Silver 999", "India price, incl. duty & GST")
    d.text((60, 572), "Gold, silver and Indian stock outlook, in plain words. Updated every hour. Not advice.", font=_font(20, False), fill=(95, 103, 117))
    img.save(out, "PNG", optimize=True)
    return out

def stamp_html(path="docs/index.html", latest_path="docs/latest.json"):
    """Point the page's preview tags at the fresh image and current prices."""
    L = json.load(open(latest_path)); s = open(path).read()
    v = int(L["run_time"])
    s = re.sub(r"og\.png\?v=\d+", f"og.png?v={v}", s)
    g, sv = L["assets"].get("GOLD"), L["assets"].get("SILVER")
    desc = "Gold, silver and Indian stock outlook in plain words, updated hourly."
    if g and sv: desc = f"Gold 24K {inr(g['rates']['inr_india_est'])}/10 g · Silver {inr(sv['rates']['inr_india_est'])}/kg · updated " + datetime.fromtimestamp(L["run_time"], IST).strftime("%d %b %I:%M %p IST")
    s = re.sub(r'(<meta (?:property="og:description"|name="twitter:description"|name="description") content=")[^"]*(")', lambda m: m.group(1) + desc + m.group(2), s)
    open(path, "w").write(s)

if __name__ == "__main__":
    make(); stamp_html()
