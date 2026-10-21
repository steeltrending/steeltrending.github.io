#!/usr/bin/env python3
"""在每個頁面加上亮色／暗色主題切換（assets/theme.js）。

- 在 *.html 與 articles/*.html 的 </head> 前插入 <script src="/assets/theme.js"></script>
  （同步載入，才能在第一次繪製前套上讀者選的主題）。
- 已有的頁面不會重複插入；Google 網站驗證檔（google*.html）略過。
- 由 GitHub Actions（.github/workflows/sitemap.yml）在頁面異動時自動執行，新頁面不必手動處理。

用法：python3 tools/page_theme.py
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = '<script src="/assets/theme.js"></script>'


def main():
    paths = sorted(glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "articles", "*.html")))
    n = 0
    for path in paths:
        if os.path.basename(path).startswith("google"):
            continue
        html = open(path, encoding="utf-8").read()
        if "assets/theme.js" in html or "</head>" not in html:
            continue
        html = html.replace("</head>", TAG + "\n</head>", 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        n += 1
    print("加入主題切換：%d 頁" % n)


if __name__ == "__main__":
    main()
