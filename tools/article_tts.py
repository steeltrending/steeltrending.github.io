#!/usr/bin/env python3
"""在每篇文章加上語音朗讀功能（assets/tts.js，使用讀者瀏覽器內建的中文語音）。

- 在 articles/*.html 的 </body> 前插入 <script src="../assets/tts.js" defer></script>
- 已有的文章不會重複插入；由 GitHub Actions（.github/workflows/sitemap.yml）在文章異動時自動執行。

用法：python3 tools/article_tts.py
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = '<script src="../assets/tts.js" defer></script>'


def main():
    n = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "articles", "*.html"))):
        html = open(path, encoding="utf-8").read()
        if "assets/tts.js" in html or "</body>" not in html or "<article" not in html:
            continue
        html = html.replace("</body>", TAG + "\n</body>", 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        n += 1
    print("加入語音朗讀：%d 篇" % n)


if __name__ == "__main__":
    main()
