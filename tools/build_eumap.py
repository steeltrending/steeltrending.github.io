#!/usr/bin/env python3
"""由 tools/eumap.template.html 產生歐洲鋼鐵地圖頁（eumap.html）。

樣式、頁首與頁尾沿用 cnmap.html；「鋼鐵數字」選單的目前頁標記由此腳本設定。
資料：data/eusteel.json（鋼企與範圍）、data/worldsteel.json（各國粗鋼）、assets/eumap-geo.json（地圖）。
用法：python3 tools/build_eumap.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


def main():
    cn = read('cnmap.html')
    style = re.search(r'<style>\n(.*?)</style>', cn, re.S).group(1)
    header = re.search(r'<header.*?</header>', cn, re.S).group(0).replace(' aria-current="page"', '')
    footer = re.search(r'<footer.*?</footer>', cn, re.S).group(0)
    link = '<a href="eumap.html">歐洲鋼鐵地圖</a>'
    assert link in header, 'nav link missing'
    header = header.replace(link, '<a href="eumap.html" aria-current="page">歐洲鋼鐵地圖</a>')
    s = read('tools/eumap.template.html').replace('@@STYLE@@', style.rstrip('\n')).replace('@@HEADER@@', header).replace('@@FOOTER@@', footer)
    assert '@@' not in s
    open(os.path.join(ROOT, 'eumap.html'), 'w', encoding='utf-8').write(s)
    print('eumap.html', len(s))


if __name__ == '__main__':
    main()
