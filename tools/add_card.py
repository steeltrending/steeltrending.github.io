#!/usr/bin/env python3
"""把一天的速報圖卡（與完整版 PDF）加入「過去詳情」。

用法：
  python3 tools/add_card.py <圖卡.jpg> <YYYY-MM-DD> [完整報告.pdf]
  python3 tools/add_card.py --pdf <完整報告.pdf> <YYYY-MM-DD>   # 只補 PDF
  python3 tools/add_card.py                                       # 只重建清單

- 圖卡 → data/archive/<日期>.jpg，縮圖 data/archive/thumb/<日期>.jpg（寬 480px）
- PDF  → data/report/<日期>/report.pdf，各頁圖 p1.jpg…（寬約 1240px），文字版 text.txt
- 依現有檔案重建 data/archive.json（新到舊）
同一日期重跑會覆蓋，不會重複。需要 Pillow 與 poppler-utils（pdftoppm、pdftotext）。
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "data", "archive")
THUMB = os.path.join(ARCH, "thumb")
REPORT = os.path.join(ROOT, "data", "report")
INDEX = os.path.join(ROOT, "data", "archive.json")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def check_date(date):
    if not DATE_RE.match(date):
        sys.exit("日期格式須為 YYYY-MM-DD")


def add_card(src, date):
    os.makedirs(THUMB, exist_ok=True)
    dst = os.path.join(ARCH, date + ".jpg")
    shutil.copyfile(src, dst)
    im = Image.open(dst).convert("RGB")
    im.thumbnail((480, 10000), Image.LANCZOS)
    im.save(os.path.join(THUMB, date + ".jpg"), "JPEG", quality=80, optimize=True, progressive=True)


def add_pdf(src, date):
    out = os.path.join(REPORT, date)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    pdf = os.path.join(out, "report.pdf")
    shutil.copyfile(src, pdf)
    # 依頁寬換算 DPI，讓每頁輸出寬度約 1240px
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
    m = re.search(r"Page size:\s+([\d.]+) x", info)
    width_pt = float(m.group(1)) if m else 595.0
    dpi = max(60, min(220, round(1240 / (width_pt / 72))))
    subprocess.run(["pdftoppm", "-r", str(dpi), "-jpeg", "-jpegopt", "quality=82,progressive=y",
                    pdf, os.path.join(out, "p")], check=True)
    # pdftoppm 會輸出 p-1.jpg 或 p-01.jpg，統一改名為 p1.jpg
    for f in glob.glob(os.path.join(out, "p-*.jpg")):
        n = int(re.search(r"p-(\d+)\.jpg$", f).group(1))
        os.rename(f, os.path.join(out, "p%d.jpg" % n))
    txt = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True, text=True).stdout
    with open(os.path.join(out, "text.txt"), "w", encoding="utf-8") as f:
        f.write(txt.replace("\f", "\n").strip() + "\n")


def rebuild():
    dates = set()
    for name in os.listdir(ARCH):
        stem, ext = os.path.splitext(name)
        if ext.lower() == ".jpg" and DATE_RE.match(stem):
            dates.add(stem)
    if os.path.isdir(REPORT):
        dates.update(d for d in os.listdir(REPORT) if DATE_RE.match(d))
    items = []
    for d in sorted(dates, reverse=True):
        it = {"date": d}
        card = os.path.join(ARCH, d + ".jpg")
        if os.path.exists(card):
            with Image.open(card) as im:
                it["w"], it["h"] = im.size
        pages = sorted(glob.glob(os.path.join(REPORT, d, "p*.jpg")),
                       key=lambda p: int(re.search(r"p(\d+)\.jpg$", p).group(1)))
        it["pages"] = len(pages)
        if pages:
            with Image.open(pages[0]) as im:
                it["pw"], it["ph"] = im.size
                # 沒有圖卡的日子，以報告第一頁當縮圖
                th = os.path.join(THUMB, d + ".jpg")
                if not os.path.exists(card) and not os.path.exists(th):
                    os.makedirs(THUMB, exist_ok=True)
                    t = im.convert("RGB"); t.thumbnail((480, 10000), Image.LANCZOS)
                    t.save(th, "JPEG", quality=80, optimize=True, progressive=True)
        items.append(it)
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write('{"items": [\n' + ",\n".join(json.dumps(i, ensure_ascii=False) for i in items) + "\n]}\n")
    return items


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--pdf" and len(a) == 3:
        check_date(a[2]); add_pdf(a[1], a[2])
    elif len(a) in (2, 3):
        check_date(a[1]); add_card(a[0], a[1])
        if len(a) == 3:
            add_pdf(a[2], a[1])
    elif a:
        sys.exit(__doc__)
    items = rebuild()
    print("archive.json 共 %d 天，其中 %d 天有完整報告" % (len(items), sum(1 for i in items if i["pages"])))
