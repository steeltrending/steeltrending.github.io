#!/usr/bin/env python3
"""台灣車市月報產生器（下游需求觀察）。

讀取 data/carmarket/<YYYY-MM>.json，產生：
  - articles/carmarket-<YYYY-MM>.html（月報頁面，含歷月趨勢）
  - data/articles.json 中 id = carmarket-<YYYY-MM> 的條目（category = demand）
  - index.html「下游需求觀察」卡片的靜態連結（只保留最新一期月報）

用法：python3 tools/build_car_market.py [YYYY-MM]   （省略時處理最新一個月）
資料格式請參考 data/carmarket/2026-09.json。
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "carmarket")
HERO = "assets/articles/carmarket-hero.jpg"
HERO_CREDIT = ('照片：Benlisquare，2025 年攝，<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>，經 '
               '<a href="https://commons.wikimedia.org/wiki/File:Traffic_on_Nanjing_West_Road_in_Taipei_at_night.jpg">Wikimedia Commons</a>')

E = html.escape


def n(v):
    return f"{v:,}"


def pct(v, sign=True):
    s = f"{v:+.1f}%" if sign else f"{v:.1f}%"
    return s.replace("+", "+").replace("-", "−")


def load_all():
    out = {}
    for f in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        out[d["month"]] = d
    return out


def ym_label(ym):
    y, m = ym.split("-")
    return f"{int(y)} 年 {int(m)} 月"


def bars(rows, unit="", highlight=None, color="#FF6A1A", mx=None):
    """水平長條圖；同一張圖分次呼叫時務必傳入相同的 mx，長條長度才可比較。"""
    mx = mx or max(v for _, v in rows) or 1
    out = []
    for name, v in rows:
        hi = " hi" if highlight and name == highlight else ""
        out.append(f'<div class="bar{hi}" title="{E(name)}：{n(v)}{unit}"><span>{E(name)}</span>'
                   f'<span class="tr"><span class="fi" style="display:block;width:{v / mx * 100:.1f}%;background:{color}"></span></span>'
                   f'<span class="v">{n(v)}</span></div>')
    return "".join(out)


ICON = {
    "car": '<path d="M5 17h14v-5l-2-5H7l-2 5z"/><circle cx="8" cy="17" r="1.6"/><circle cx="16" cy="17" r="1.6"/><path d="M5 12h14"/>',
    "up": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "ship": '<path d="M3 17h18l-2 4H5z"/><path d="M6 17V9h12v8"/><path d="M9 9V5h6v4"/>',
    "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/>',
    "sum": '<path d="M18 4H6l6 8-6 8h12"/>',
}


def card(icon, label, value, sub):
    return (f'<div class="fact"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" '
            f'stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{ICON[icon]}</svg></span>'
            f'<div><span class="fl">{E(label)}</span><span class="fv">{E(value)}</span><span class="fs">{E(sub)}</span></div></div>')


def li_pairs(pairs):
    return "".join(f"<li><b>{E(a)}</b> {E(b)}</li>" for a, b in pairs)


def trend_section(all_data, upto):
    months = [m for m in sorted(all_data) if m <= upto][-12:]
    if len(months) < 2:
        return ('<h2>歷月趨勢</h2><p>本專欄自 2026 年 9 月起每月更新，累積兩個月以上資料後，'
                '將在此呈現掛牌量與進口車占比的月度趨勢。</p>')
    rows_total = [(ym_label(m), all_data[m]["kpis"]["total"]) for m in months]
    rows_share = [(ym_label(m), all_data[m]["kpis"]["import_share"]) for m in months]
    mx = max(v for _, v in rows_share)
    share_html = "".join(
        f'<div class="bar" title="{E(k)}：{v:.1f}%"><span>{E(k)}</span><span class="tr"><span class="fi" '
        f'style="display:block;width:{v / max(mx, 1) * 100:.1f}%;background:#8DB4D6"></span></span><span class="v">{v:.1f}%</span></div>'
        for k, v in rows_share)
    return (f'<h2>歷月趨勢</h2>'
            f'<div class="bars" role="img" aria-label="近 {len(months)} 個月新車掛牌量"><p class="bt">新車掛牌量（輛）</p>'
            f'{bars(rows_total, " 輛", highlight=ym_label(upto))}</div>'
            f'<div class="bars" role="img" aria-label="近 {len(months)} 個月進口車占比"><p class="bt">進口車占比</p>{share_html}</div>')


def build(ym):
    all_data = load_all()
    d = all_data[ym]
    k = d["kpis"]
    label = ym_label(ym)
    title = f"{label}台灣車市：{d['headline']}"
    slug = f"carmarket-{ym}"

    cards = "".join([
        card("car", "新車掛牌", f"{n(k['total'])} 輛", f"年增 {pct(k['yoy'])}、月增 {pct(k['mom'])}"),
        card("ship", "進口車", f"{n(k['imported'])} 輛", f"占 {k['import_share']:.1f}%"),
        card("home", "國產車", f"{n(k['domestic'])} 輛", f"占 {100 - k['import_share']:.1f}%"),
        card("bolt", "電動車", f"{n(k['ev'])} 輛", f"約占 {k['ev'] / k['total'] * 100:.0f}%"),
        card("sum", "今年累計", f"{n(k['ytd'])} 輛", f"年增 {pct(k['ytd_yoy'])}"),
        card("up", "累計進口占比", f"{k['ytd_import_share']:.1f}%", "1 月起累計"),
    ])

    split = (f'<div class="bars" role="img" aria-label="國產車 {n(k["domestic"])} 輛、進口車 {n(k["imported"])} 輛">'
             f'<p class="bt">國產與進口（輛）</p>'
             f'{bars([("國產車", k["domestic"])], color="#8A8F96", mx=max(k["domestic"], k["imported"]))}'
             f'{bars([("進口車", k["imported"])], mx=max(k["domestic"], k["imported"]))}'
             f'<p class="bn">進口車占 {k["import_share"]:.1f}%。</p></div>')

    brand_html = (f'<div class="bars" role="img" aria-label="品牌掛牌前 {len(d["brands"])} 名">'
                  f'<p class="bt">品牌掛牌前 {len(d["brands"])} 名（輛）</p>{bars(d["brands"])}</div>')

    model_rows = "".join(f'<tr><td class="num">{i}</td><td>{E(m)}</td><td>{E(o)}</td><td class="num">{n(v)}</td></tr>'
                         for i, (m, v, o) in enumerate(d["models"], 1))
    models = (f'<div class="tbl"><table><caption style="position:absolute;left:-9999px">車型掛牌排行</caption>'
              f'<thead><tr><th scope="col">#</th><th scope="col">車型</th><th scope="col">國產／進口</th><th scope="col">掛牌數</th></tr></thead>'
              f'<tbody>{model_rows}</tbody></table></div>')

    sources = "".join(f'<li><a href="{E(u)}">{E(t)}</a>（{E(p)}）</li>' for t, u, p in d["sources"])
    watch = "".join(f"<li>{E(w)}</li>" for w in d["watch"])
    drivers = "".join(f"<li>{E(x)}</li>" for x in d["drivers"])

    body = f'''<main class="wrap" style="padding-top:40px;padding-bottom:96px">
<nav aria-label="導覽路徑" style="font-size:14px;color:#9AA0A6"><a href="../#topics" style="text-decoration:none">關注主題</a> <span aria-hidden="true">›</span> 下游需求觀察 <span aria-hidden="true">›</span> 台灣車市月報</nav>

<article>
<p class="mono" style="margin:28px 0 0;font-size:13px;letter-spacing:.24em;color:#FF6A1A">DOWNSTREAM DEMAND · TAIWAN AUTO · {ym.replace("-", ".")}</p>
<h1 style="margin:12px 0 10px;font-size:clamp(30px,5vw,46px);font-weight:900;line-height:1.25">{E(title)}</h1>
<p style="font-size:14px;color:#9AA0A6">鋼鐵潮流工作室 · 台灣車市月報 · 發布 {d["published"].replace("-", ".")}</p>

<figure>
<img src="../{HERO}" alt="台北夜間街頭，汽車與機車在路口等候通行，兩旁是燈火通明的商店" width="960" height="640">
<figcaption>台北南京西路夜間車流。台灣車市月報每月追蹤新車掛牌、國產與進口消長，以及對汽車用鋼的意涵。<small>{HERO_CREDIT}</small></figcaption>
</figure>

<h2>本期重點</h2>
<p class="lead">{E(d["lead"])}</p>
<ul>{li_pairs(d["highlights"])}</ul>

<h2>關鍵數字</h2>
<div class="facts">{cards}</div>
{split}

<h2>品牌與車型</h2>
{brand_html}
{models}

<h2>成長動能</h2>
<ul>{drivers}</ul>

<h2>本刊解讀</h2>
<ul>{li_pairs(d["analysis"])}</ul>

<h2>對鋼鐵業的意義</h2>
<ul>{li_pairs(d["steel"])}</ul>

{trend_section(all_data, ym)}

<h2>展望與觀察重點</h2>
<p>{E(d["outlook"])}</p>
<ul class="watch">{watch}</ul>

<h2>資料來源</h2>
<ul class="sources">{sources}</ul>
<p style="font-size:13px;color:#9AA0A6;margin-top:32px">掛牌數為監理機關數據交換資料，各媒體統計口徑可能略有差異。內容僅供產業資訊參考，不構成投資建議。新聞版權屬原出處所有。</p>
</article>

<p style="margin-top:48px"><a href="../#topics" style="display:inline-flex;align-items:center;border:1px solid #4A5058;color:#E8E6E1;text-decoration:none;padding:12px 20px">← 回到下游需求觀察</a></p>
'''
    head = open(os.path.join(ROOT, "tools/templates/article_head.html"), encoding="utf-8").read()
    foot = open(os.path.join(ROOT, "tools/templates/article_foot.html"), encoding="utf-8").read()
    head = head.replace("{{TITLE}}", E(title)).replace("{{DESC}}", E(d["summary"]))
    open(os.path.join(ROOT, "articles", slug + ".html"), "w", encoding="utf-8").write(head + body + foot)

    # articles.json
    p = os.path.join(ROOT, "data", "articles.json")
    arts = json.load(open(p, encoding="utf-8"))
    arts["items"] = [a for a in arts["items"] if a.get("id") != slug]
    arts["items"].insert(0, {
        "id": slug, "category": "demand", "series": "carmarket", "title": title, "period": ym, "published": d["published"],
        "summary": d["summary"], "tags": ["台灣車市", "新車掛牌", "進口車", "電動車", "汽車用鋼"],
        "image": HERO, "url": f"articles/{slug}.html"})
    json.dump(arts, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(p, "a", encoding="utf-8").write("\n")

    # index.html 靜態連結：只保留最新一期月報
    ip = os.path.join(ROOT, "index.html")
    h = open(ip, encoding="utf-8").read()
    box = '<div data-articles="demand" style="display: flex; flex-direction: column; margin-top: 6px; border-top: 1px solid #2A2F35">'
    if box in h:
        h = re.sub(r'<a href="articles/carmarket-[^"]+\.html"[^>]*>.*?</a>', "", h)
        link = (f'<a href="articles/{slug}.html" style="display: flex; justify-content: space-between; align-items: center; gap: 12px; '
                f'padding: 12px 0; color: #E8E6E1; text-decoration: none; font-size: 15px; font-weight: 700; border-bottom: 1px solid #22262B">'
                f'{E(title)}<span aria-hidden="true" style="color: #FF6A1A">→</span></a>')
        h = h.replace(box, box + link, 1)
        open(ip, "w", encoding="utf-8").write(h)
    print(f"已產生 articles/{slug}.html：{title}")


if __name__ == "__main__":
    data = load_all()
    ym = sys.argv[1] if len(sys.argv) > 1 else max(data)
    build(ym)
