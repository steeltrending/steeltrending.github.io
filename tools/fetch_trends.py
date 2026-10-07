#!/usr/bin/env python3
"""關鍵字熱度：以瀏覽器開啟 Google Trends 圖表頁，攔截其資料 API，存成 data/trends.json。

Google 會擋嵌在第三方網站的趨勢圖表（回應 429），但直接開啟圖表頁可正常取得數據；
因此由 GitHub Actions（.github/workflows/trends.yml）每天抓一次預設主題，網站自行繪圖。
抓不到的組合保留前一次的資料。需要：pip install playwright && python -m playwright install --with-deps chromium
"""
import datetime as dt
import json
import os
import random
import re
import time
import urllib.parse

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "trends.json")
TPE = dt.timezone(dt.timedelta(hours=8))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"

PRESETS = [
    {"id": "tw-steel", "name": "台灣鋼鐵", "geo": "TW", "kw": ["鋼價", "鋼筋", "中鋼", "廢鋼", "鐵礦砂"]},
    {"id": "tw-build", "name": "台灣營建與房市", "geo": "TW", "kw": ["鋼筋", "房價", "建照", "營建", "缺工"]},
    {"id": "tw-down", "name": "台灣下游產業", "geo": "TW", "kw": ["電動車", "資料中心", "離岸風電", "造船", "工具機"]},
    {"id": "gl-raw", "name": "全球原料（英文）", "geo": "", "kw": ["steel price", "iron ore", "scrap metal", "coking coal"]},
    {"id": "gl-issue", "name": "全球鋼鐵議題（英文）", "geo": "", "kw": ["green steel", "steel tariffs", "CBAM", "hydrogen steel"]},
]
PERIODS = ["today 3-m", "today 12-m", "today 5-y"]
GEOS = ["TW", ""]


def log(*a):
    print(*a, flush=True)


def embed(kind, kws, geo, period):
    req = {"comparisonItem": [{"keyword": k, "geo": geo, "time": period} for k in kws], "category": 0, "property": ""}
    return ("https://trends.google.com/trends/embed/explore/%s?req=%s&tz=-480&hl=zh-TW"
            % (kind, urllib.parse.quote(json.dumps(req, ensure_ascii=False, separators=(",", ":")))))


def parse(body):
    i = body.find("{")
    return json.loads(body[i:]) if i >= 0 else None


def grab(page, kind, kws, geo, period, api):
    """開啟圖表頁並攔截 widgetdata/<api> 的回應。"""
    got = {}

    def on_resp(r):
        if "/trends/api/widgetdata/" + api in r.url and r.status == 200:
            try:
                got["d"] = parse(r.text())
            except Exception as e:  # noqa: BLE001
                got["err"] = str(e)

    page.on("response", on_resp)
    try:
        resp = page.goto(embed(kind, kws, geo, period), wait_until="domcontentloaded", timeout=60000)
        status = resp.status if resp else 0
        for _ in range(30):
            if "d" in got:
                break
            page.wait_for_timeout(500)
    finally:
        page.remove_listener("response", on_resp)
    return status, got.get("d")


def ts_rows(d):
    rows = []
    for p in (d or {}).get("default", {}).get("timelineData", []):
        rows.append([dt.datetime.fromtimestamp(int(p["time"]), dt.timezone.utc).strftime("%Y-%m-%d"),
                     # hasData=false 為搜尋量過低，Google 圖表顯示為 0
                     [int(v) for v in p["value"]],
                     1 if p.get("isPartial") else 0])
    return rows


def geo_rows(d):
    out = []
    for p in (d or {}).get("default", {}).get("geoMapData", []):
        if p.get("hasData", [False])[0]:
            out.append([p.get("geoName"), p["value"][0]])
    return sorted(out, key=lambda x: -x[1])


CJK = re.compile(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])")


def cjk(q):
    """Google 會把中文搜尋詞斷成「中 鋼 股價」，去掉中文字之間的空白。"""
    return CJK.sub("", q)


def rq_rows(d):
    lists = (d or {}).get("default", {}).get("rankedList", [])
    pick = lambda i: [[cjk(k["query"]), k.get("formattedValue", str(k.get("value")))] for k in (lists[i]["rankedKeyword"] if len(lists) > i else [])][:15]
    return {"top": pick(0), "rising": pick(1)}


def empty(v):
    if isinstance(v, dict):
        return not v.get("top") and not v.get("rising")
    if v and isinstance(v[0], list) and len(v[0]) == 3 and isinstance(v[0][1], list):
        return not any(x for r in v for x in r[1])
    return not v


def main():
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        old = {}
    oldsets = old.get("sets", {})
    sets, ok, fail = {}, 0, 0
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(locale="zh-TW", user_agent=UA, viewport={"width": 1200, "height": 900})
        page = ctx.new_page()
        page.goto("https://trends.google.com/trends/?geo=TW&hl=zh-TW", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        for pr in PRESETS:
            for geo in GEOS:
                for per in PERIODS:
                    key = "%s|%s|%s" % (pr["id"], geo or "WW", per)
                    rec = {"kw": pr["kw"], "geo": geo, "period": per}
                    parts = 0
                    for kind, api, kws, fn, field in (("TIMESERIES", "multiline", pr["kw"], ts_rows, "ts"),
                                                      ("GEO_MAP", "comparedgeo", pr["kw"][:1], geo_rows, "geomap"),
                                                      ("RELATED_QUERIES", "relatedsearches", pr["kw"][:1], rq_rows, "related")):
                        val, prev = None, oldsets.get(key, {}).get(field)
                        for attempt in range(3):
                            try:
                                st, d = grab(page, kind, kws, geo, per, api)
                            except Exception as e:  # noqa: BLE001
                                st, d = "ERR " + str(e)[:80], None
                            val = fn(d) if d else None
                            # Google 偶爾回傳空的清單；前一次有資料時視為失敗重試
                            if val is not None and not (empty(val) and prev and not empty(prev)):
                                break
                            log("  %s %s 第 %d 次失敗（%s）" % (key, kind, attempt + 1, st if not d else "空資料"))
                            time.sleep(15 * (attempt + 1))
                        if val is not None and not (empty(val) and prev and not empty(prev)):
                            rec[field] = val; parts += 1
                        elif prev is not None:
                            rec[field] = prev; rec.setdefault("stale", []).append(field)
                        time.sleep(random.uniform(2.5, 4.5))
                    rec["fetched"] = dt.datetime.now(TPE).replace(microsecond=0).isoformat() if parts == 3 else oldsets.get(key, {}).get("fetched")
                    sets[key] = rec
                    ok += parts; fail += 3 - parts
                    log("%s：%d/3%s" % (key, parts, "" if parts == 3 else "（沿用舊資料：%s）" % ",".join(rec.get("stale", []))))
        b.close()
    if ok == 0:
        log("全部失敗，不更新檔案"); return
    out = {"updated": dt.datetime.now(TPE).replace(microsecond=0).isoformat(), "presets": PRESETS, "periods": PERIODS,
           "source": "Google Trends（每日由鋼鐵潮流抓取，數值為相對熱度，期間內最高點 = 100）", "sets": sets, "ok": ok, "fail": fail}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    log("完成：成功 %d、失敗 %d" % (ok, fail))


if __name__ == "__main__":
    main()
