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

# 各市場當地時區與收盤時間（含約 20 分鐘緩衝，等收盤價定案）。
# 當地「今天」尚未收盤時，丟掉今天的盤中 K 棒，只用最近一個已收盤交易日的收盤價；
# 當地已收盤，就用當日收盤價。
_TW = ("Asia/Taipei", "13:55")
_CN = ("Asia/Shanghai", "15:20")
_JP = ("Asia/Tokyo", "15:50")
_KR = ("Asia/Seoul", "15:50")
_US = ("America/New_York", "16:20")
_DE = ("Europe/Berlin", "17:55")
_AT = ("Europe/Vienna", "17:55")
_VN = ("Asia/Ho_Chi_Minh", "15:05")
_ID = ("Asia/Jakarta", "16:35")
_MY = ("Asia/Kuala_Lumpur", "17:20")
_IN = ("Asia/Kolkata", "15:50")
MARKET_CLOSE = {
    "tw": _TW, "tw2": _TW, "tw3": _TW,
    "cn": _CN, "cn2": _CN, "cn3": _CN,
    "jpkr": _JP, "jpkr2": _JP, "jpkr3": _KR,
    "us": _US, "us2": _US, "us3": _US,
    "eu": _US, "eu2": _DE, "eu3": _AT,  # ArcelorMittal 用 NYSE 的 MT
    "sea": _VN, "sea2": _ID, "sea3": _MY,
    "in": _IN, "in2": _IN, "in3": _IN,
}


def drop_unclosed(key, pts, quiet=False):
    """當地今天尚未收盤時，移除今天（及以後）的資料點。"""
    from zoneinfo import ZoneInfo
    tz, hm = MARKET_CLOSE.get(key, ("Asia/Taipei", "23:59"))
    now = dt.datetime.now(ZoneInfo(tz))
    today = now.strftime("%Y-%m-%d")
    closed = now.strftime("%H:%M") >= hm
    keep = [p for p in pts if p[0] < today or (p[0] == today and closed)]
    if len(keep) != len(pts) and not quiet:
        log(f"  {key}: 當地 {today} 尚未收盤，略過盤中資料")
    return keep


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


def _vnd(out):
    """部分來源以「千 VND」計價，統一換成 VND。"""
    if out:
        mid = sorted(c for _, c in out)[len(out) // 2]
        if mid < 1000:
            out = [[d, c * 1000] for d, c in out]
    return sorted(p for p in out if p[0] >= START)


def fetch_hpg():
    import requests
    hdr = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    now = int(time.time())
    errs = []
    # 1) Vietcap（VCI）
    try:
        r = requests.post(
            "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart",
            json={"timeFrame": "ONE_DAY", "symbols": ["HPG"], "to": now, "countBack": 400},
            headers={**hdr, "Referer": "https://trading.vietcap.com.vn/", "Origin": "https://trading.vietcap.com.vn"},
            timeout=30)
        j = r.json()
        j = j[0] if isinstance(j, list) else j
        ts, cs = j.get("t") or [], j.get("c") or []
        out = [[dt.datetime.fromtimestamp(int(t), TPE).strftime("%Y-%m-%d"), float(c)] for t, c in zip(ts, cs) if c is not None]
        out = _vnd(out)
        if out:
            return out, "Vietcap", errs
    except Exception as e:  # noqa: BLE001
        errs.append(f"Vietcap: {e}")
    # 2) TCBS
    try:
        r = requests.get(
            "https://apipubaws.tcbs.com.vn/stock-insight/v2/stock/bars-long-term",
            params={"ticker": "HPG", "type": "stock", "resolution": "D", "countBack": 400, "to": now},
            headers=hdr, timeout=30)
        rows = r.json().get("data") or []
        out = _vnd([[x["tradingDate"][:10], float(x["close"])] for x in rows if x.get("close") is not None])
        if out:
            return out, "TCBS", errs
    except Exception as e:  # noqa: BLE001
        errs.append(f"TCBS: {e}")
    # 3) KB Securities
    try:
        end = dt.datetime.now(TPE).strftime("%d-%m-%Y")
        r = requests.get(
            "https://kbbuddywts.kbsec.com.vn/iis-server/investment/stocks/HPG/data_day",
            params={"sdate": "01-01-2026", "edate": end}, headers=hdr, timeout=30)
        rows = r.json().get("data_day") or []
        out = _vnd([[str(x.get("t"))[:10], float(x["c"])] for x in rows if x.get("c") is not None])
        if out:
            return out, "KB Securities", errs
    except Exception as e:  # noqa: BLE001
        errs.append(f"KBS: {e}")
    # 4) VNDirect
    try:
        r = requests.get(
            "https://finfo-api.vndirect.com.vn/v4/stock_prices",
            params={"sort": "date", "q": f"code:HPG~date:gte:{START}", "size": 400, "page": 1},
            headers=hdr, timeout=30)
        rows = r.json().get("data") or []
        out = _vnd([[x["date"][:10], float(x["close"])] for x in rows if x.get("close") is not None])
        if out:
            return out, "VNDirect", errs
    except Exception as e:  # noqa: BLE001
        errs.append(f"VNDirect: {e}")
    return [], None, errs


def rnd(v, cur):
    return round(v, DEC.get(cur, 2))


def main():
    os.makedirs(HIST, exist_ok=True)
    with open(STOCKS, encoding="utf-8") as f:
        stocks = json.load(f)
    now = dt.datetime.now(TPE).replace(microsecond=0).isoformat()
    touched_latest = False
    report = []
    status = {"updated": now}

    for it in stocks["items"]:
        key, cur = it["key"], it["currency"]
        if key == "sea":
            pts, src, errs = fetch_hpg()
            status["sea_errors"] = errs
        else:
            sym = YAHOO.get(key)
            pts, src = (fetch_yahoo(sym), "Yahoo Finance " + sym) if sym else ([], None)

        pts = drop_unclosed(key, pts)

        path = os.path.join(HIST, f"{key}.json")
        old = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = json.load(f)
        # 舊檔若留有當地今天的盤中值且現在仍未收盤，一併移除
        merged = {d: c for d, c in drop_unclosed(key, old.get("points") or [], quiet=True)}
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
    status["report"] = report
    with open(os.path.join(HIST, "_status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=1)
    ok = sum(1 for k in stocks["items"] if os.path.exists(os.path.join(HIST, k["key"] + ".json")))
    log(f"完成：{ok}/21 檔有歷史資料")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
