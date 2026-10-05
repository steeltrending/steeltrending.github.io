#!/usr/bin/env python3
"""台股鋼鐵產業鏈：抓取上中下游九大類代表上市股的收盤價，計算當日、近 5 日、近 20 日與今年以來漲跌幅。

由 GitHub Actions（.github/workflows/tw-chain.yml）每天 07:20、16:20、18:40（台北）自動執行，也可手動跑：
  pip install yfinance
  python3 tools/fetch_tw_chain.py

更新邏輯與全球鋼鐵股（tools/fetch_history.py）一致：
- 台北時間 13:55 前視為尚未收盤，略過當日盤中資料，沿用前一交易日收盤價；已收盤則用當日收盤價。
- data/twhistory/<代號>.json 逐日累積收盤價，只新增或修正日期，不刪除既有資料點。
- data/twchain.json 的最新報價只在新交易日不早於現有 asof、且價格與現值差距合理（0.5～2 倍）時才覆寫；
  抓不到新資料時沿用最近一次可取得的資料，不留空。
- 漲跌幅由累積的歷史序列計算：當日、近 5 日、近 20 日、今年以來（以 2025 年最後一個交易日為基準）。
"""
import datetime as dt
import json
import os
import sys
import time

import yfinance as yf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "twchain.json")
HIST = os.path.join(ROOT, "data", "twhistory")
TPE = dt.timezone(dt.timedelta(hours=8))
START = "2025-12-15"          # 抓到 2025 年最後一個交易日，作為今年以來的基準
YEAR_BASE = "2026-01-01"
CLOSE_HHMM = (13, 55)         # 台股收盤後約 25 分鐘才採用當日收盤價

# 分類依網站「下游需求觀察」主題：AI、能源、營建、汽車、造船、家電、機械，前面加上游與鋼鐵本業
# 產業別為證交所上市產業分類（2026-10-05 對照）
GROUPS = [
    ("upstream", "上游與周邊", "上游", "鐵礦砂、煤炭海運；焦油、爐石、鋼渣資源化", [
        ("2606", "裕民", "航運業"), ("2605", "新興", "航運業"), ("2637", "慧洋-KY", "航運業"),
        ("1723", "中碳", "化學工業"), ("9930", "中聯資源", "綠能環保"), ("6581", "鋼聯", "綠能環保")]),
    ("steel", "鋼鐵本業", "中游", "煉鋼、軋延、加工", [
        ("2002", "中鋼", "鋼鐵工業"), ("2014", "中鴻", "鋼鐵工業"), ("2013", "中鋼構", "鋼鐵工業"),
        ("2015", "豐興", "鋼鐵工業"), ("2006", "東和鋼鐵", "鋼鐵工業"), ("2028", "威致", "鋼鐵工業"),
        ("2027", "大成鋼", "鋼鐵工業"), ("2023", "燁輝", "鋼鐵工業"), ("2029", "盛餘", "鋼鐵工業"),
        ("2012", "春雨", "鋼鐵工業"), ("9958", "世紀鋼", "鋼鐵工業")]),
    ("ai", "AI", "下游", "伺服器機殼、機櫃、滑軌用鋼板", [
        ("8210", "勤誠", "電腦及週邊設備業"), ("3013", "晟銘電", "電腦及週邊設備業"),
        ("6117", "迎廣", "電腦及週邊設備業"), ("2059", "川湖", "電子零組件業"),
        ("3017", "奇鋐", "電腦及週邊設備業")]),
    ("energy", "能源", "下游", "變壓器電磁鋼片、電纜、離岸風電厚板", [
        ("1519", "華城", "電機機械"), ("1503", "士電", "電機機械"), ("1513", "中興電", "電機機械"),
        ("1514", "亞力", "電機機械"), ("1605", "華新", "電器電纜"), ("1609", "大亞", "電器電纜"),
        ("2072", "世紀風電", "綠能環保")]),
    ("construction", "營建", "下游", "鋼筋、H 型鋼、鋼構厚板", [
        ("2597", "潤弘", "建材營造業"), ("2515", "中工", "建材營造業"), ("2542", "興富發", "建材營造業"),
        ("2548", "華固", "建材營造業"), ("5522", "遠雄", "建材營造業"), ("2504", "國產", "建材營造業"),
        ("1101", "台泥", "水泥工業"), ("1102", "亞泥", "水泥工業"), ("9933", "中鼎", "其他業")]),
    ("auto", "汽車", "下游", "汽車鋼板、高強度鋼、馬達電磁鋼片", [
        ("2201", "裕隆", "汽車工業"), ("2204", "中華", "汽車工業"), ("2207", "和泰車", "汽車工業"),
        ("2206", "三陽工業", "汽車工業"), ("2258", "鴻華先進", "汽車工業"), ("1319", "東陽", "汽車工業"),
        ("1522", "堤維西", "汽車工業"), ("9921", "巨大", "運動休閒"), ("9914", "美利達", "運動休閒")]),
    ("ship", "造船", "下游", "船用厚板", [
        ("2208", "台船", "航運業"), ("6753", "龍德造船", "航運業")]),
    ("appliance", "家電", "下游", "冷軋、彩塗鋼板、不銹鋼、壓縮機電磁鋼片", [
        ("1604", "聲寶", "電器電纜"), ("1614", "三洋電", "電器電纜"), ("5283", "禾聯碩", "電器電纜"),
        ("2371", "大同", "電機機械"), ("4532", "瑞智", "電機機械"), ("9911", "櫻花", "居家生活")]),
    ("machinery", "機械", "下游", "合金鋼棒線、軸承鋼、結構鋼板", [
        ("2049", "上銀", "電機機械"), ("1590", "亞德客-KY", "電機機械"), ("4526", "東台", "電機機械"),
        ("1583", "程泰", "電機機械"), ("1736", "喬山", "運動休閒")]),
]


def log(*a):
    print(*a, flush=True)


def drop_unclosed(pts):
    """台北今天尚未收盤時，移除今天（及以後）的資料點；已收盤則保留當日收盤價。"""
    now = dt.datetime.now(TPE)
    today = now.strftime("%Y-%m-%d")
    closed = (now.hour, now.minute) >= CLOSE_HHMM
    return [p for p in pts if p[0] < today or (p[0] == today and closed)]


def fetch_yahoo(code):
    for attempt in range(3):
        try:
            df = yf.Ticker(code + ".TW").history(start=START, interval="1d", auto_adjust=False, actions=False)
            if df is not None and len(df):
                out = []
                for idx, row in df.iterrows():
                    c = row.get("Close")
                    if c is None or c != c:  # NaN
                        continue
                    out.append([idx.strftime("%Y-%m-%d"), round(float(c), 2)])
                return out
        except Exception as e:  # noqa: BLE001
            log(f"  {code} 第 {attempt + 1} 次失敗：{e}")
        time.sleep(3)
    return []


def pct(a, b):
    return round((a - b) / b * 100, 2) if a is not None and b else None


def returns(series):
    """由歷史序列計算當日、近 5 日、近 20 日、今年以來漲跌幅。"""
    c = [v for _, v in series]
    base = [v for d, v in series if d < YEAR_BASE]
    return {
        "d1": pct(c[-1], c[-2]) if len(c) > 1 else None,
        "d5": pct(c[-1], c[-6]) if len(c) > 5 else None,
        "d20": pct(c[-1], c[-21]) if len(c) > 20 else None,
        "ytd": pct(c[-1], base[-1]) if base else None,
    }


def main():
    os.makedirs(HIST, exist_ok=True)
    now = dt.datetime.now(TPE).replace(microsecond=0).isoformat()
    old = {}
    if os.path.exists(OUT):
        try:
            for g in json.load(open(OUT, encoding="utf-8")).get("groups", []):
                for it in g.get("items", []):
                    old[it["code"]] = it
        except Exception:  # noqa: BLE001
            pass
    errors, report, groups, latest = [], [], [], ""
    for key, name, role, steel, items in GROUPS:
        out = []
        for code, nm, industry in items:
            it = {"code": code, "name": nm, "industry": industry}
            prev = old.get(code, {})
            pts = drop_unclosed(fetch_yahoo(code))

            # 歷史檔只新增或修正日期，不刪除既有資料點；舊檔若留有今天的盤中值且仍未收盤，一併移除
            path = os.path.join(HIST, f"{code}.json")
            oldh = {}
            if os.path.exists(path):
                try:
                    oldh = json.load(open(path, encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    oldh = {}
            merged = {d: c for d, c in drop_unclosed(oldh.get("points") or [])}
            for d, c in pts:
                merged[d] = c
            series = sorted(merged.items())
            if series:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"code": code, "name": nm, "ticker": code + ".TW", "currency": "TWD",
                               "source": "Yahoo Finance " + code + ".TW",
                               "updated": now if pts else oldh.get("updated"),
                               "points": [[d, c] for d, c in series]},
                              f, ensure_ascii=False, separators=(",", ":"))
                    f.write("\n")

            # 最新報價：新交易日不早於現有 asof、且價格與現值差距合理時才覆寫；否則沿用最近一次可取得的資料
            use_new = False
            if series:
                d1, c1 = series[-1]
                pc = prev.get("close")
                sane = not isinstance(pc, (int, float)) or pc == 0 or 0.5 < c1 / pc < 2
                use_new = (prev.get("asof") or "") <= d1 and sane
                if not sane:
                    log(f"  ！{nm} 新價 {c1} 與現值 {pc} 差距過大，未覆寫最新報價")
            if use_new:
                it.update({"close": series[-1][1], "asof": series[-1][0]})
                it.update(returns(series))
            elif prev:
                it.update({k: prev.get(k) for k in ("close", "asof", "d1", "d5", "d20", "ytd")})
            if not pts:
                errors.append(f"{code} {nm}: 查無新資料，沿用 {it.get('asof') or '—'}")
            if it.get("asof"):
                latest = max(latest, it["asof"])
            report.append(f"{nm} {code}: {len(series)} 筆，最新 {it.get('asof') or '—'}")
            out.append(it)
            time.sleep(0.4)
        groups.append({"key": key, "name": name, "role": role, "steel": steel, "items": out})
    data = {"updated": now, "asof": latest, "groups": groups, "errors": errors}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with open(os.path.join(HIST, "_status.json"), "w", encoding="utf-8") as f:
        json.dump({"updated": now, "report": report, "errors": errors}, f, ensure_ascii=False, indent=1)
    log("\n".join(report))
    n = sum(len(g["items"]) for g in groups)
    log(f"完成：{n} 檔，最新交易日 {latest}，查無新資料 {len(errors)} 檔")
    return 0 if latest else 1


if __name__ == "__main__":
    sys.exit(main())
