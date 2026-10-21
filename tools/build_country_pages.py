#!/usr/bin/env python3
"""由 tools/plantmap.template.html 產生日本、南韓製鐵所地圖頁（jpmap.html、krmap.html）。

頁首與頁尾沿用 cnmap.html；各頁導覽「鋼鐵數字」選單的目前頁標記由此腳本設定。
資料檔：data/jpsteel.json、data/krsteel.json；地圖：assets/jpmap-geo.json、assets/krmap-geo.json。
用法：python3 tools/build_country_pages.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = {
    'jp': dict(file='jpmap.html', name='日本', label='日本鋼鐵地圖', en='JAPAN STEEL MAP', ws='JPN',
               desc='日本主要製鐵所分布地圖：標示日本製鐵、JFE、神戶製鋼各一貫製鐵所所在地與企業粗鋼排名，並附 1948 年起全國粗鋼歷史走勢。',
               intro='日本沒有公開都道府縣別的粗鋼產量，因此這張地圖以「製鐵所」為單位：圓點是已查證所在地的主要一貫製鐵所，顏色代表所屬企業。點圓點看廠區資料與企業排名，點縣市可看該地已列入的製鐵所。',
               tl='從有統計的 1948 年起看日本粗鋼產量：1973 年首度突破 1 億噸，之後長期在 1 億噸上下震盪，近年降到 8,000 萬噸出頭。'),
    'kr': dict(file='krmap.html', name='南韓', label='南韓鋼鐵地圖', en='SOUTH KOREA STEEL MAP', ws='KOR',
               desc='南韓主要製鐵所分布地圖：標示 POSCO 浦項、光陽與現代製鐵唐津等廠區所在地與企業粗鋼排名，並附全國粗鋼歷史走勢。',
               intro='南韓沒有公開各道的粗鋼產量，因此這張地圖以「製鐵所」為單位：圓點是已查證所在地的主要製鐵所，顏色代表所屬企業。點圓點看廠區資料與企業排名，點行政區可看該地已列入的製鐵所。',
               tl='從有紀錄的 1975 年起看南韓粗鋼產量：自約 250 萬噸一路成長，2018 年達到高峰 7,246 萬噸後回落。早期只有少數年份的記載值，缺口以虛線表示。'),
}


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


def main():
    cn = read('cnmap.html')
    header = re.search(r'<header.*?</header>', cn, re.S).group(0)
    footer = re.search(r'<footer.*?</footer>', cn, re.S).group(0)
    header = header.replace(' aria-current="page"', '')
    tpl = read('tools/plantmap.template.html')
    for key, c in PAGES.items():
        link = '<a href="%s">%s</a>' % (c['file'], c['label'])
        assert link in header, 'nav link missing for ' + key
        hd = header.replace(link, '<a href="%s" aria-current="page">%s</a>' % (c['file'], c['label']))
        cfg = json.dumps({'geo': 'assets/%smap-geo.json' % key, 'data': 'data/%ssteel.json' % key, 'wsKey': c['ws']}, ensure_ascii=False)
        s = tpl
        for k, v in (('@@NAME@@', c['name']), ('@@EN@@', c['en']), ('@@DESC@@', c['desc']), ('@@INTRO@@', c['intro']),
                     ('@@TLINTRO@@', c['tl']), ('@@HEADER@@', hd), ('@@FOOTER@@', footer), ('@@CFG@@', cfg)):
            s = s.replace(k, v)
        assert '@@' not in s
        open(os.path.join(ROOT, c['file']), 'w', encoding='utf-8').write(s)
        print(c['file'], len(s))


if __name__ == '__main__':
    main()
