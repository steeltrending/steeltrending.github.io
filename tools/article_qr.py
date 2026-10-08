#!/usr/bin/env python3
"""在每篇文章文末加上「本文連結」QR Code（中央為吉祥物）。

- 每篇 articles/<名稱>.html 產生 assets/qr/<名稱>.png，連到 https://steeltrending.github.io/articles/<名稱>.html
- QR 用最高容錯（H 級），中央放圓形吉祥物，產生後會實際解碼驗證，掃不出來就停止。
- 「中鋼新聞專區」的文章（返回連結為「回到中鋼新聞專區」）不加。
- 區塊插在 </article> 之後；已有區塊的文章會更新成最新版本，重複執行不會重複插入。
- 由 GitHub Actions（.github/workflows/sitemap.yml）在文章有異動時自動執行，新文章不必手動處理。

用法：python3 tools/article_qr.py
"""
import glob
import os
import re

import segno
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://steeltrending.github.io/articles/"
MASCOT = os.path.join(ROOT, "assets", "mascot.jpg")
OUT_DIR = os.path.join(ROOT, "assets", "qr")
EXCLUDE = "回到中鋼新聞專區"
SIZE = 600            # 輸出 PNG 邊長（px）
LOGO_RATIO = 0.30     # 吉祥物（含白邊）直徑佔整張圖的比例
ORANGE = (255, 106, 26)

BLOCK_RE = re.compile(r"\n?<!-- article-qr -->.*?<!-- /article-qr -->\n?", re.S)


def make_png(url, path):
    qr = segno.make(url, error="h")
    modules = qr.symbol_size(border=4)[0]
    scale = max(1, SIZE // modules)
    img = Image.new("RGB", (modules * scale,) * 2, "white")
    d = ImageDraw.Draw(img)
    for y, row in enumerate(qr.matrix_iter(border=4)):
        for x, dark in enumerate(row):
            if dark:
                d.rectangle([x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1], fill="black")
    w = img.size[0]

    # 中央吉祥物：白色底圈 + 橘色細框 + 圓形頭像
    outer = int(w * LOGO_RATIO)
    ring = max(2, outer // 30)
    pad = max(4, outer // 12)
    cx = cy = w // 2
    d.ellipse([cx - outer // 2, cy - outer // 2, cx + outer // 2, cy + outer // 2], fill="white")
    inner = outer - 2 * pad
    d.ellipse([cx - inner // 2, cy - inner // 2, cx + inner // 2, cy + inner // 2], fill=ORANGE)
    face = inner - 2 * ring
    m = Image.open(MASCOT).convert("RGB").resize((face, face), Image.LANCZOS)
    mask = Image.new("L", (face, face), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, face - 1, face - 1], fill=255)
    img.paste(m, (cx - face // 2, cy - face // 2), mask)
    img.save(path, optimize=True)
    return img


def verify(img, url):
    try:
        import zxingcpp
    except ImportError:
        return  # 驗證工具不在時略過（GitHub Actions 會安裝）
    got = [r.text for r in zxingcpp.read_barcodes(img)]
    if url not in got:
        raise SystemExit(f"QR 解碼失敗：{url} → {got}")


def block(name):
    url = BASE + name
    return f"""<!-- article-qr -->
<aside aria-label="本文連結 QR Code" style="max-width:760px;box-sizing:border-box;margin-top:48px;border:1px solid #2A2F35;background:#15181B;padding:20px;display:flex;align-items:center;gap:20px;flex-wrap:wrap">
<img src="../assets/qr/{name[:-5]}.png" alt="本文連結 QR Code" width="132" height="132" loading="lazy" style="display:block;width:132px;height:132px;background:#FFFFFF;flex:none">
<div style="display:flex;flex-direction:column;gap:6px;min-width:0;flex:1 1 220px">
<p style="margin:0;font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.2em;color:#FF6A1A">SHARE</p>
<p style="margin:0;font-size:17px;font-weight:900;color:#E8E6E1">掃描 QR Code 開啟本文</p>
<p style="margin:0;font-size:13px;line-height:1.7;color:#9AA0A6;word-break:break-all">{url}</p>
<a href="../assets/qr/{name[:-5]}.png" download="steeltrending-{name[:-5]}-qr.png" style="align-self:flex-start;margin-top:4px;font-size:14px;color:#FF8A47;text-decoration:none">下載 QR Code ↓</a>
</div>
</aside>
<!-- /article-qr -->
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    done = skipped = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*.html"))):
        name = os.path.basename(path)
        html = open(path, encoding="utf-8").read()
        new = BLOCK_RE.sub("\n", html)
        png = os.path.join(OUT_DIR, name[:-5] + ".png")
        if EXCLUDE in html:
            if os.path.exists(png):
                os.remove(png)
            skipped += 1
        else:
            if "</article>" not in new:
                print("找不到 </article>，略過：", name)
                continue
            if not os.path.exists(png):
                verify(make_png(BASE + name, png), BASE + name)
            new = new.replace("</article>", "</article>\n" + block(name).rstrip("\n"), 1)
            done += 1
        if new != html:
            open(path, "w", encoding="utf-8").write(new)
    print(f"已加上 QR：{done} 篇；中鋼新聞專區略過：{skipped} 篇")


if __name__ == "__main__":
    main()
