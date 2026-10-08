#!/usr/bin/env python3
"""原料與鋼價看板：下載各期貨自 2026-01-01 起的每日價格，存成 data/futures/<key>.json。

由 GitHub Actions（.github/workflows/futures-history.yml）每天自動執行，也可手動跑：
  python3 tools/fetch_futures.py

資料來源：
- SGX 62% Fe 鐵礦砂期貨（近月）：新加坡交易所公開 API，逐月合約的每日結算價；
  每個交易日取「當月到期」那一口合約（即近月），串成連續序列。
- 大連鐵礦石、大連焦煤、上海熱軋卷板（主力）：新浪財經期貨主力連續日 K 線的收盤價
  （與首頁看板一致）。
- LME 廢鋼（近月）：LME 與各大報價網站不開放程式讀取，無法回補歷史；
  改為每天從首頁看板 data/latest.json 收進當日價格，逐日累積。

輸出格式：{"key","name","contract","unit","price_type","source","updated","points":[["YYYY-MM-DD", price], ...]}
只新增或修正日期，不刪除既有資料點；抓取失敗時保留既有檔案。

收盤後同步首頁看板（data/latest.json）：歷史資料若出現比看板更新的交易日，
就把看板該品項換成最新一筆，讓看板在收盤後自動更新，不必等隔天早上的排程任務。
- 大連／上海：price = 收盤價，change = 收盤價 − 前一交易日結算價（新浪 K 線的 s 欄；缺值時改用前一日收盤價）
- SGX：price = 官方每日結算價，change = 與前一交易日結算價之差
- LME 廢鋼無程式來源，不由此處更新。
"""
import datetime as dt
import json
import os
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "futures")
LATEST = os.path.join(ROOT, "data", "latest.json")
START = "2026-01-01"
TPE = dt.timezone(dt.timedelta(hours=8))
UA = {"User-Agent": "Mozilla/5.0 (compatible; SteelTrendingBot/1.0; +https://steeltrending.github.io)"}

META = {
    "sgx_iron_ore": {"name": "鐵礦砂", "contract": "SGX 62% Fe 鐵礦砂期貨 近月", "unit": "USD/t", "group": "原料",
                     "exchange": "新加坡交易所 SGX", "price_type": "每日結算價",
                     "source": "新加坡交易所（SGX）FEF 逐月合約每日結算價，取當月到期合約串接"},
    "dce_iron_ore": {"name": "鐵礦石", "contract": "大連商品交易所 鐵礦石期貨 主力", "unit": "CNY/t", "group": "原料",
                     "exchange": "大連商品交易所 DCE", "price_type": "收盤價", "sina": "I0",
                     "source": "新浪財經 大連鐵礦石期貨主力連續（I0）日 K 線收盤價"},
    "dce_coking_coal": {"name": "焦煤", "contract": "大連商品交易所 焦煤期貨 主力", "unit": "CNY/t", "group": "原料",
                        "exchange": "大連商品交易所 DCE", "price_type": "收盤價", "sina": "JM0",
                        "source": "新浪財經 大連焦煤期貨主力連續（JM0）日 K 線收盤價"},
    "lme_scrap": {"name": "廢鋼", "contract": "LME 廢鋼期貨（土耳其 HMS 1&2 80:20 CFR）近月", "unit": "USD/t", "group": "原料",
                  "exchange": "倫敦金屬交易所 LME", "price_type": "每日價格",
                  "source": "鋼鐵潮流每日看板紀錄（LME 不開放程式讀取歷史資料，自 2026-10-02 起逐日累積）"},
    "shfe_hrc": {"name": "熱軋卷板", "contract": "上海期貨交易所 熱軋卷板期貨 主力", "unit": "CNY/t", "group": "鋼材",
                 "exchange": "上海期貨交易所 SHFE", "price_type": "收盤價", "sina": "HC0",
                 "source": "新浪財經 上海熱軋卷板期貨主力連續（HC0）日 K 線收盤價"},
}
ORDER = ["sgx_iron_ore", "dce_iron_ore", "dce_coking_coal", "lme_scrap", "shfe_hrc"]
MONTH_CODE = "FGHJKMNQUVXZ"
SETTLE = {}  # 新浪 K 線的每日結算價，{symbol: {date: settle}}，供看板計算漲跌


def log(*a):
    print(*a, flush=True)


def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def sina(symbol):
    url = ("https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_{0}=/"
           "InnerFuturesNewService.getDailyKLine?symbol={0}").format(symbol)
    txt = get(url)
    rows = json.loads(txt[txt.index("(") + 1:txt.rindex(")")])
    rows = [r for r in rows if r["d"] >= START and float(r["c"]) > 0]
    SETTLE[symbol] = {r["d"]: round(float(r["s"]), 2) for r in rows if r.get("s") and float(r["s"]) > 0}
    return {r["d"]: round(float(r["c"]), 2) for r in rows}


def sgx_front_month(today):
    pts = {}
    y, m = 2026, 1
    while (y, m) <= (today.year, today.month):
        sym = "FEF%s%02d" % (MONTH_CODE[m - 1], y % 100)
        url = ("https://api.sgx.com/derivatives/v1.0/history/symbol/%s?days=1y&category=futures"
               "&params=base-date,total-volume,daily-settlement-price-abs" % sym)
        try:
            data = json.loads(get(url)).get("data") or []
        except Exception as e:  # noqa: BLE001
            log("  SGX %s 失敗：%s" % (sym, e))
            data = []
        n = 0
        for r in data:
            d = str(r.get("base-date", ""))
            p = r.get("daily-settlement-price-abs")
            if len(d) != 8 or not isinstance(p, (int, float)) or p <= 0:
                continue
            iso = "%s-%s-%s" % (d[:4], d[4:6], d[6:])
            # 近月：只取該合約到期月份內的交易日
            if iso[:7] == "%04d-%02d" % (y, m) and iso >= START:
                pts[iso] = round(float(p), 2)
                n += 1
        log("  SGX %s：%d 筆" % (sym, n))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return pts


def from_latest(key):
    try:
        d = json.load(open(LATEST, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    for it in d.get("items", []):
        if it.get("key") == key and isinstance(it.get("price"), (int, float)) and it.get("asof"):
            return {str(it["asof"])[:10]: float(it["price"])}
    return {}


def load(key):
    p = os.path.join(OUT, key + ".json")
    try:
        return {d: v for d, v in json.load(open(p, encoding="utf-8")).get("points", [])}
    except Exception:  # noqa: BLE001
        return {}


def save(key, pts):
    m = META[key]
    out = {"key": key, "name": m["name"], "contract": m["contract"], "unit": m["unit"], "group": m["group"],
           "exchange": m["exchange"], "price_type": m["price_type"], "source": m["source"],
           "updated": dt.datetime.now(TPE).replace(microsecond=0).isoformat(),
           "points": [[d, pts[d]] for d in sorted(pts) if d >= START]}
    p = os.path.join(OUT, key + ".json")
    try:
        old = json.load(open(p, encoding="utf-8"))
        if old.get("points") == out["points"] and {k: v for k, v in old.items() if k not in ("updated", "points")} == \
                {k: v for k, v in out.items() if k not in ("updated", "points")}:
            log("  %s 無變動" % key)
            return
    except Exception:  # noqa: BLE001
        pass
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    log("  %s：%d 筆，最後 %s" % (key, len(out["points"]), out["points"][-1] if out["points"] else "—"))


def num(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


def board_json(board):
    """沿用 latest.json 原本的排版：每個品項一行。"""
    lines = ["{", '  "updated": %s,' % json.dumps(board.get("updated")),
             '  "social": %s,' % json.dumps(board.get("social", {}), ensure_ascii=False, separators=(", ", ": ")).replace("{", "{ ").replace("}", " }"),
             '  "items": [']
    items = board.get("items", [])
    for i, it in enumerate(items):
        it = {k: num(v) for k, v in it.items()}
        body = json.dumps(it, ensure_ascii=False, separators=(", ", ": "))
        lines.append("    { " + body[1:-1] + " }" + ("," if i < len(items) - 1 else ""))
    lines += ["  ]", "}"]
    extra = {k: v for k, v in board.items() if k not in ("updated", "social", "items")}
    if extra:  # 若日後新增欄位，退回一般格式以免遺失
        return json.dumps(board, ensure_ascii=False, indent=2) + "\n"
    return "\n".join(lines) + "\n"


def sync_board(series):
    """把歷史資料中比看板更新的交易日寫回 data/latest.json（只動 price／change／asof 與 updated）。"""
    try:
        board = json.load(open(LATEST, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        log("  看板讀取失敗，略過同步：%s" % e)
        return
    changed = []
    for it in board.get("items", []):
        key = it.get("key")
        pts = series.get(key)
        if key == "lme_scrap" or not pts:
            continue
        dates = sorted(pts)
        last = dates[-1]
        if it.get("asof") and str(it["asof"])[:10] >= last:
            continue
        price = pts[last]
        prev = dates[-2] if len(dates) > 1 else None
        change = None
        if prev:
            sym = META[key].get("sina")
            base = SETTLE.get(sym, {}).get(prev) if sym else None
            change = round(price - (base if base else pts[prev]), 2)
        it.update(price=price, change=change, asof=last)
        changed.append("%s %s %s" % (key, last, price))
    if not changed:
        log("  看板無需更新")
        return
    board["updated"] = dt.datetime.now(TPE).replace(microsecond=0).isoformat()
    with open(LATEST, "w", encoding="utf-8") as f:
        f.write(board_json(board))
    log("  看板已更新：" + "；".join(changed))


def main():
    os.makedirs(OUT, exist_ok=True)
    series = {}
    today = dt.datetime.now(TPE).date()
    for key in ORDER:
        m = META[key]
        pts = load(key)
        try:
            if key == "sgx_iron_ore":
                new = sgx_front_month(today)
            elif m.get("sina"):
                new = sina(m["sina"])
            else:
                new = {}
        except Exception as e:  # noqa: BLE001
            log("  %s 抓取失敗：%s" % (key, e))
            new = {}
        # 看板當日價格作為補充（官方來源沒有的日期才補進）
        for d, v in from_latest(key).items():
            if d >= START and d not in new and d not in pts:
                new[d] = v
        # 合理性檢查：新值與既有值差距超過 30% 視為異常，不覆寫
        for d, v in new.items():
            if d in pts and pts[d] and abs(v - pts[d]) / pts[d] > 0.3:
                log("  %s %s 新值 %s 與既有 %s 差距過大，略過" % (key, d, v, pts[d]))
                continue
            pts[d] = v
        save(key, pts)
        series[key] = pts
    # 索引：品項順序與中繼資料，供列表頁使用
    idx = {"updated": dt.datetime.now(TPE).replace(microsecond=0).isoformat(),
           "items": [dict(key=k, **{x: META[k][x] for x in ("name", "contract", "unit", "group", "exchange", "price_type")})
                     for k in ORDER]}
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
        f.write("\n")
    sync_board(series)


if __name__ == "__main__":
    main()
