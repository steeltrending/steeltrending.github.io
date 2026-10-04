#!/usr/bin/env python3
"""下載 21 檔鋼鐵代表股自 2026-01-01 起的每日收盤價，並更新最新報價。

由 GitHub Actions（.github/workflows/stock-history.yml）每天自動執行，也可手動跑：
  pip install yfinance requests
  python3 tools/fetch_history.py

輸出：
- data/history/<key>.json：{"key","name","ticker","currency","source","updated","points":[["YYYY-MM-DD", close], ...]}
  只新增或修正日期，不刪除既有資料點，所以「今日及以後」會逐日累積。
- data/stocks.json：以歷史資料最後兩筆更新 price / change / change_pct / asof
  （只在新交易日不早於現有 asof、且價格與現值差距合理時才覆寫）。
"""
import datetime as dt
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCKS = os.path.join(ROOT, "data", "stocks.json")
HIST = os.path.join(ROOT, "data", "history")
START = "2026-01-01"
TPE = dt.timezone(dt.timedelta(hours=8))

# stocks.json 的 key → Yahoo Finance 代號（HPG 不在 Yahoo，改用越南券商公開 API）
YAHOO = {
    "tw": "2002.TW", "tw2": "2014.TW", "tw3": "2007.TW",
    "cn": "600019.SS", "cn2": "000898.SZ", "cn3": "000932.SZ",
    "jpkr": "5401.T", "jpkr2": "5411.T", "jpkr3": "005490.KS",
    "us": "NUE", "us2": "STLD", "us3": "CLF",
    "eu": "MT", "eu2": "TKA.DE", "eu3": "VOE.VI",
    "sea2": "KRAS.JK", "sea3": "6556.KL",
    "in": "TATASTEEL.NS", "in2": "JSWSTEEL.NS", "in3": "SAIL.NS",
}
DEC = {"KRW": 0, "VND": 0, "IDR": 0, "MYR": 3}


def log(*a):
    print(*a, flush=True)


def fetch_yahoo(symbol):
    import yfinance as yf
    for attempt in range(3):
        try:
            df = yf.Ticker(symbol).history(start=START, interval="1d", auto_adjust=False, actions=False)
            if df is not None and len(df):
                out = []
                for idx, row in df.iterrows():
                    c = row.get("Close")
                    if c is None or c != c:  # NaN
                        continue
                    out.append([idx.strftime("%Y-%m-%d"), float(c)])
                return out
        except Exception as e:  # noqa: BLE001
            log(f"  {symbol} 第 {attempt + 1} 次失敗：{e}")
        time.sleep(3)
    return []


def fetch_hpg():
    import requests
    hdr = {"User-Agent": "Mozilla/5.0"}
    # 1) TCBS（價格單位：VND）
    try:
        to = int(time.time())
        r = requests.get(
            "https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars-long-term",
            params={"ticker": "HPG", "type": "stock", "resolution": "D", "countBack": 400, "to": to},
            headers=hdr, timeout=30)
        rows = r.json().get("data") or []
        out = [[x["tradingDate"][:10], float(x["close"])] for x in rows if x.get("close") is not None]
        out = [p for p in out if p[0] >= START]
        if out:
            return out, "TCBS"
    except Exception as e:  # noqa: BLE001
        log(f"  HPG TCBS 失敗：{e}")
    # 2) VNDirect（價格單位：千 VND → 乘 1000）
    try:
        r = requests.get(
            "https://finfo-api.vndirect.com.vn/v4/stock_prices",
            params={"sort": "date", "q": f"code:HPG~date:gte:{START}", "size": 400, "page": 1},
            headers=hdr, timeout=30)
        rows = r.json().get("data") or []
        out = sorted([[x["date"][:10], float(x["close"]) * 1000] for x in rows if x.get("close") is not None])
        if out:
            return out, "VNDirect"
    except Exception as e:  # noqa: BLE001
        log(f"  HPG VNDirect 失敗：{e}")
    return [], None


def rnd(v, cur):
    return round(v, DEC.get(cur, 2))


def main():
    os.makedirs(HIST, exist_ok=True)
    with open(STOCKS, encoding="utf-8") as f:
        stocks = json.load(f)
    now = dt.datetime.now(TPE).replace(microsecond=0).isoformat()
    touched_latest = False
    report = []

    for it in stocks["items"]:
        key, cur = it["key"], it["currency"]
        if key == "sea":
            pts, src = fetch_hpg()
        else:
            sym = YAHOO.get(key)
            pts, src = (fetch_yahoo(sym), "Yahoo Finance " + sym) if sym else ([], None)

        path = os.path.join(HIST, f"{key}.json")
        old = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = json.load(f)
        merged = {d: c for d, c in (old.get("points") or [])}
        for d, c in pts:
            merged[d] = rnd(c, cur)
        series = sorted(merged.items())

        if not pts:
            report.append(f"{it['name']}: 查無新資料，保留 {len(series)} 筆")
            if not old:
                continue
        hist = {
            "key": key, "name": it["name"], "ticker": it["ticker"], "currency": cur,
            "source": src or old.get("source"), "updated": now if pts else old.get("updated"),
            "points": [[d, c] for d, c in series],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

        if len(series) >= 2 and pts:
            (d1, c1), (d0, c0) = series[-1], series[-2]
            prev = it.get("price")
            sane = not isinstance(prev, (int, float)) or prev == 0 or 0.5 < c1 / prev < 2
            if (it.get("asof") or "") <= d1 and sane:
                it["price"] = rnd(c1, cur)
                it["change"] = rnd(c1 - c0, cur)
                it["change_pct"] = round((c1 - c0) / c0 * 100, 2) if c0 else None
                it["asof"] = d1
                touched_latest = True
            elif not sane:
                log(f"  ！{it['name']} 新價 {c1} 與現值 {prev} 差距過大，未覆寫最新報價")
        report.append(f"{it['name']}: {len(series)} 筆，最新 {series[-1][0] if series else '—'}（{src or '沿用'}）")

    if touched_latest:
        stocks["updated"] = now
        with open(STOCKS, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=1)
            f.write("\n")
    log("\n".join(report))
    ok = sum(1 for k in stocks["items"] if os.path.exists(os.path.join(HIST, k["key"] + ".json")))
    log(f"完成：{ok}/21 檔有歷史資料")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
