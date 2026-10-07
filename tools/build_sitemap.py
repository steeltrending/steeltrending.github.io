#!/usr/bin/env python3
"""產生 sitemap.xml 與 robots.txt，供搜尋引擎收錄。

列入根目錄的各頁（day.html、stock.html、future.html 等需帶參數的詳情頁除外）與 data/articles.json 的文章。
由 .github/workflows/sitemap.yml 在頁面或文章清單變動時自動執行。
"""
import datetime as dt
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://steeltrending.github.io/"
SKIP = {"day.html", "stock.html", "future.html"}  # 需帶參數的詳情頁
PRIORITY = {"index.html": "1.0", "sitemap.html": "0.6"}


def lastmod(path):
    """以 git 最後修改日期為準，沒有紀錄時用今天。"""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if out:
            return out
    except Exception:  # noqa: BLE001
        pass
    return dt.date.today().isoformat()


def main():
    urls = []
    for f in sorted(os.listdir(ROOT)):
        if f.endswith(".html") and f not in SKIP:
            loc = BASE if f == "index.html" else BASE + f
            urls.append((loc, lastmod(f), PRIORITY.get(f, "0.8")))
    try:
        items = json.load(open(os.path.join(ROOT, "data", "articles.json"), encoding="utf-8")).get("items", [])
    except Exception:  # noqa: BLE001
        items = []
    for a in items:
        u = a.get("url")
        if u and os.path.exists(os.path.join(ROOT, u)):
            urls.append((BASE + u, lastmod(u), "0.7"))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           # 瀏覽器開啟時套用樣式（XML + CSS；Chrome 將移除 XSLT，故不用 XSL）
           '<?xml-stylesheet type="text/css" href="/assets/sitemap.css"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, pr in urls:
        xml.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (loc, mod, pr))
    xml.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(xml) + "\n")
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write("User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % BASE)
    print("sitemap.xml：%d 個網址" % len(urls))


if __name__ == "__main__":
    main()
