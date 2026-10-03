#!/usr/bin/env python3
"""把一張每日速報圖卡加入歷史圖卡庫。

用法：python3 tools/add_card.py <圖檔路徑> <YYYY-MM-DD>

- 複製原圖到 data/archive/<日期>.jpg
- 產生縮圖 data/archive/thumb/<日期>.jpg（寬 480px）
- 依 data/archive/ 內所有圖檔重建 data/archive.json（新到舊）
同一日期重跑會覆蓋，不會重複。
"""
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "data", "archive")
THUMB = os.path.join(ARCH, "thumb")
INDEX = os.path.join(ROOT, "data", "archive.json")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def add(src, date):
    if not DATE_RE.match(date):
        sys.exit("日期格式須為 YYYY-MM-DD")
    os.makedirs(THUMB, exist_ok=True)
    dst = os.path.join(ARCH, date + ".jpg")
    shutil.copyfile(src, dst)
    im = Image.open(dst).convert("RGB")
    im.thumbnail((480, 10000), Image.LANCZOS)
    im.save(os.path.join(THUMB, date + ".jpg"), "JPEG", quality=80, optimize=True, progressive=True)


def rebuild():
    items = []
    for name in os.listdir(ARCH):
        stem, ext = os.path.splitext(name)
        if ext.lower() != ".jpg" or not DATE_RE.match(stem):
            continue
        with Image.open(os.path.join(ARCH, name)) as im:
            w, h = im.size
        items.append({"date": stem, "w": w, "h": h})
    items.sort(key=lambda x: x["date"], reverse=True)
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return len(items)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        add(sys.argv[1], sys.argv[2])
    elif len(sys.argv) != 1:
        sys.exit(__doc__)
    print("archive.json 共", rebuild(), "張")
