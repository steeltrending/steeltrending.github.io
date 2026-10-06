#!/usr/bin/env python3
"""世界鋼鐵數據：從世界鋼鐵協會（worldsteel，WSA）官網的數據檢視器取得各國公布數據，整理成 data/worldsteel.json。

由 GitHub Actions（.github/workflows/worldsteel.yml）每週自動執行；worldsteel 每月下旬公布前一個月的粗鋼產量，
年度數據則於每年年中《World Steel in Figures》／統計年鑑發布時更新。也可手動跑：
  pip install playwright opencc-python-reimplemented && python3 -m playwright install chromium
  python3 tools/fetch_worldsteel.py
  python3 tools/fetch_worldsteel.py --from <資料夾>   # 改用已下載的 API 回應檔（檔名為 <指標代碼>.json、meta_zh.json）

worldsteel 的數據 API 只接受從其網頁發出的請求，因此用無頭瀏覽器開啟數據頁後，在同一頁面內呼叫 API。
抓取失敗或資料異常時保留既有的 data/worldsteel.json，不覆寫。
"""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "worldsteel.json")
PAGE = "https://worldsteel.org/data/annual-production-steel-data/?ind=P1_crude_steel_total_pub/CHN/IND"
API = "https://worldsteel.org/mappingworld-api/?values={}&lang=EN"
META = "https://worldsteel.org/mappingworld-api/?lang=ZH&meta&geoitems&indicators&datasets"
TPE = dt.timezone(dt.timedelta(hours=8))

# 本站使用的指標：鍵為輸出名稱，值為 worldsteel 指標代碼與中文說明
ANNUAL = {
    "crude": ("P1_crude_steel_total", "粗鋼產量", "千噸"),
    "bof": ("P1_crude_steel_BOF", "轉爐鋼產量", "千噸"),
    "eaf": ("P1_crude_steel_EF", "電爐鋼產量", "千噸"),
    "pig": ("P3_pig_iron", "生鐵產量", "千噸"),
    "dri": ("P3_dri", "直接還原鐵產量", "千噸"),
    "exp": ("T_exports_sf_f_total_pub", "鋼材出口（半成品＋成品）", "千噸"),
    "imp": ("T_imports_sf_f_total_pub", "鋼材進口（半成品＋成品）", "千噸"),
    "asu": ("C_asu_fsp_pub", "表觀鋼材消費（成品）", "千噸"),
    "asupc": ("C_asu_per_capita_fsp_pub", "人均表觀鋼材消費（成品）", "公斤"),
}
MONTHLY = {
    "crude": ("MCSP_crude_steel_monthly", "粗鋼月產量", "千噸"),
    "pig": ("MPIP_pig_iron_monthly", "生鐵月產量", "千噸"),
}
EXTRA = {"regions_ytd": "CSP-NUMBERS"}

# 名稱覆寫（其餘由 worldsteel 簡體中文名稱轉為台灣用語）
NAME_FIX = {"TWN": "台灣", "KOR": "南韓", "WORLD_ALL": "全球", "WORLD": "全球", "OTHER": "其他",
            "PRK": "北韓", "ASOC": "亞洲與大洋洲", "EU27": "歐盟 27 國", "EUROTHER1": "其他歐洲國家",
            "NOAM1": "北美", "CIS": "獨立國協", "SAM": "南美", "MDEAST": "中東", "AFR": "非洲",
            "CHN": "中國", "USA": "美國", "RUS": "俄羅斯", "IRN": "伊朗", "VNM": "越南",
            "ARE": "阿聯", "AUS": "澳洲", "BGD": "孟加拉", "BIH": "波士尼亞", "CZE": "捷克", "IDN": "印尼",
            "KGZ": "吉爾吉斯", "MKD": "北馬其頓", "MNE": "蒙特內哥羅", "MLT": "馬爾他", "DOM": "多明尼加",
            "BELLUX": "比利時－盧森堡", "SAU": "沙烏地", "TTO": "千里達"}


def log(*a):
    print(*a, flush=True)


def fetch_live():
    from playwright.sync_api import sync_playwright
    raw = {}
    codes = [v[0] for v in ANNUAL.values()] + [v[0] for v in MONTHLY.values()] + list(EXTRA.values())
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(PAGE, wait_until="networkidle", timeout=120000)
        pg.wait_for_timeout(3000)
        get = "u => fetch(u, {credentials: 'include'}).then(r => r.text())"
        for c in codes:
            try:
                raw[c] = pg.evaluate(get, API.format(c))
            except Exception as e:  # noqa: BLE001
                log(f"  {c} 失敗：{e}")
        try:
            raw["meta_zh"] = pg.evaluate(get, META)
        except Exception as e:  # noqa: BLE001
            log(f"  meta 失敗：{e}")
        b.close()
    return raw


def load_dir(d):
    raw = {}
    for f in os.listdir(d):
        if f.endswith(".json"):
            raw[f[:-5]] = open(os.path.join(d, f), encoding="utf-8").read()
    return raw


def values(raw, code):
    try:
        j = json.loads(raw[code])
        return j["indicators"][code]["values"]
    except Exception:  # noqa: BLE001
        log(f"  ！{code} 無法解析")
        return None


def clean(series):
    out = {}
    for geo, ys in series.items():
        if not isinstance(ys, dict):
            continue
        row = {y: round(float(v), 1) for y, v in ys.items() if isinstance(v, (int, float))}
        if any(row.values()):
            out[geo] = dict(sorted(row.items()))
    return out


def names(raw, geos):
    try:
        from opencc import OpenCC
        cc = OpenCC("s2twp").convert
    except Exception:  # noqa: BLE001
        cc = lambda s: s  # noqa: E731
    zh = {}
    try:
        g = json.loads(raw["meta_zh"])["geoitems"]
        for k, v in g.items():
            if v.get("label"):
                zh[k] = cc(v["label"])
    except Exception:  # noqa: BLE001
        pass
    zh.update(NAME_FIX)
    return {k: zh.get(k, k) for k in sorted(geos)}


def main():
    src = None
    if "--from" in sys.argv:
        src = sys.argv[sys.argv.index("--from") + 1]
    raw = load_dir(src) if src else fetch_live()

    data = {"source": "World Steel Association（worldsteel）", "source_url": PAGE,
            "updated": dt.datetime.now(TPE).replace(microsecond=0).isoformat(),
            "indicators": {}, "annual": {}, "monthly": {}}
    geos = set()
    for key, (code, label, unit) in ANNUAL.items():
        v = values(raw, code)
        if v is None:
            continue
        data["annual"][key] = clean(v)
        data["indicators"]["a_" + key] = {"label": label, "unit": unit, "code": code}
        geos |= set(data["annual"][key])
    for key, (code, label, unit) in MONTHLY.items():
        v = values(raw, code)
        if v is None:
            continue
        data["monthly"][key] = clean(v)
        data["indicators"]["m_" + key] = {"label": label, "unit": unit, "code": code}
        geos |= set(data["monthly"][key])
    v = values(raw, EXTRA["regions_ytd"])
    if v:
        data["regions_ytd"] = clean(v)   # 單位：百萬噸；鍵為 YYYY（年初至今）與 YYYYMM（單月）
        geos |= set(data["regions_ytd"])
    data["names"] = names(raw, geos)

    # 基本檢查：粗鋼年產量須涵蓋中國且有全球合計，否則不覆寫
    crude = data["annual"].get("crude", {})
    if "CHN" not in crude or "WORLD_ALL" not in crude:
        log("！粗鋼年產量資料不完整，保留既有檔案")
        return 1
    data["asof"] = {
        "annual": max(crude["WORLD_ALL"]),
        "monthly": max((max(s) for s in data["monthly"].get("crude", {}).values()), default=None),
    }
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
            if old.get("asof", {}).get("annual", "") > data["asof"]["annual"]:
                log("！新資料年份早於既有檔案，保留既有檔案")
                return 1
            # 數值完全沒變時保留原擷取時間，避免產生無意義的提交
            if {k: v for k, v in old.items() if k != "updated"} == {k: v for k, v in data.items() if k != "updated"}:
                log("數值與既有檔案相同，未更新")
                return 0
        except Exception:  # noqa: BLE001
            pass
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    log(f"完成：年度至 {data['asof']['annual']}、月度至 {data['asof']['monthly']}，{len(data['names'])} 個國家／地區")
    return 0


if __name__ == "__main__":
    sys.exit(main())
