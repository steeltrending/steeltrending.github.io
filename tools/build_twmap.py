#!/usr/bin/env python3
"""台灣鋼鐵地圖：每年元旦由 GitHub Actions（.github/workflows/twmap.yml）自動重建 data/twsteelmap.json。

1. 下載經濟部「登記工廠名錄」（生產中工廠清冊，https://data.gov.tw/dataset/6569），篩出主要產品含「241 鋼鐵」的工廠。
2. 依統一編號查詢經濟部商工登記公示資料（公司登記基本資料-應用一）的資本額。
3. 以 data/twmap-centroids.json（村里、鄉鎮區中心點，已投影為地圖座標）定位，輸出工廠點與鄉鎮區聚落彙總。
鋼鐵本業：主要產品第一項為 241 鋼鐵；其餘為非鋼鐵本業。
抓取失敗或資料筆數異常（少於既有的一半）時保留既有檔案。
手動執行：python3 tools/build_twmap.py
"""
import csv, collections, datetime as dt, io, json, os, re, sys, time, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "twsteelmap.json")
CENT = os.path.join(ROOT, "data", "twmap-centroids.json")
UA = {"User-Agent": "Mozilla/5.0 (compatible; SteelTrendingBot/1.0; +https://steeltrending.github.io)"}
LIST = "https://www.ida.gov.tw/opendata/02/SDD6569.csv"
ZIP = "https://serv.gcis.nat.gov.tw/RDownLoad/Data/statistical/%E7%94%9F%E7%94%A2%E4%B8%AD%E5%B7%A5%E5%BB%A0%E6%B8%85%E5%86%8A.zip"
API = "https://data.gcis.nat.gov.tw/od/data/api/5F64D864-61CB-4D0D-8AD9-492047CC1EA6?$format=json&$filter=Business_Accounting_NO%20eq%20{}&$skip=0&$top=50"
TPE = dt.timezone(dt.timedelta(hours=8))


def get(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def zip_url():
    try:
        rows = list(csv.reader(io.StringIO(get(LIST).decode("utf-8-sig"))))
        for r in rows[1:]:
            if r and r[-1].startswith("http") and r[-1].lower().endswith(".zip"):
                return r[-1]
    except Exception as e:  # noqa: BLE001
        print("清冊索引讀取失敗，改用預設網址：", e)
    return ZIP


def main():
    z = zipfile.ZipFile(io.BytesIO(get(zip_url(), 600)))
    info = z.infolist()[0]
    rows = list(csv.DictReader(io.StringIO(z.read(info.filename).decode("utf-8-sig"))))
    rows = [r for r in rows if "241鋼鐵" in (r.get("主要產品") or "").replace(" ", "")]
    print("鋼鐵工廠", len(rows), "（清冊檔案", info.filename, "）")
    caps = {}
    for tid in sorted({r["統一編號"].strip() for r in rows if r["統一編號"].strip()}):
        rec = None
        for t in range(3):
            try:
                d = json.loads(get(API.format(tid), 30).decode("utf-8") or "[]")
                rec = {"data": d[0]} if d else None
                break
            except Exception:  # noqa: BLE001
                time.sleep(2)
        caps[tid] = rec
        time.sleep(0.1)
    print("查得資本額", sum(1 for v in caps.values() if v), "/", len(caps))
    C = json.load(open(CENT, encoding="utf-8"))
    data = build(rows, caps, C)
    data["asof"] = re.sub(r"\D", "", info.filename)[:5]  # 例如 11508 = 民國 115 年 8 月
    data["updated"] = dt.datetime.now(TPE).replace(microsecond=0).isoformat()
    try:
        old = json.load(open(OUT, encoding="utf-8"))
        if len(data["factories"]) < len(old.get("factories", [])) * 0.5:
            print("！工廠數異常減少，保留既有檔案"); return 1
    except Exception:  # noqa: BLE001
        pass
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("完成", data["summary"])
    return 0


def build(rows, caps, C):
    norm = lambda s: (s or "").replace("台", "臺").strip()
    
    
    def cap_of(tid):
        rec = caps.get(tid)
        if not rec:
            return None, None, None
        d = rec["data"]
        def num(k):
            try:
                return float(str(d.get(k, "")).replace(",", "") or 0)
            except ValueError:
                return 0.0
        paid = num("Paid_In_Capital_Amount")
        total = num("Capital_Stock_Amount")
        name = d.get("Company_Name") or d.get("Business_Name")
        status = d.get("Company_Status_Desc") or d.get("Business_Current_Status_Desc")
        v = paid if paid > 0 else total
        return (v or None), name, status
    
    
    def split_loc(loc):
        # 「高雄市小港區山明里」→ 縣市、鄉鎮區、村里；鄉鎮區以底圖的行政區名稱比對（避免「平鎮區」「新市區」被切錯）
        loc = norm(loc)
        county = loc[:3]
        towns = [k[3:] for k in C["town"] if k.startswith(county) and loc.startswith(k)]
        if not towns:
            m = re.match(r"^(.{2}[縣市])(.+?[鄉鎮市區])(.*[村里])?$", loc)
            return (m.group(1), m.group(2), m.group(3) or "") if m else (None, None, None)
        town = max(towns, key=len)
        return county, town, loc[3 + len(town):]


    facs, miss = [], 0
    for r in rows:
        county, town, vill = split_loc(r["工廠市鎮鄉村里"])
        xy = None; prec = None
        if county:
            xy = C["vil"].get(county + town + vill); prec = "村里"
            if not xy:
                xy = C["town"].get(county + town); prec = "鄉鎮區"
        if not xy:
            miss += 1
            continue
        cap, cname, status = cap_of(r["統一編號"].strip())
        prods = [p.strip() for p in re.split(r"[、,]", r["主要產品"]) if p.strip()]
        facs.append({
            "n": r["工廠名稱"].strip(), "tid": r["統一編號"].strip(), "a": norm(r["工廠地址"]),
            "c": county, "t": town, "x": xy[0], "y": xy[1], "p": prec,
            "org": r["工廠組織型態"].strip(), "cap": cap, "co": cname, "st": status,
            "prod": prods, "reg": r["工廠登記核准日期"].strip(),
            # 鋼鐵本業：主要產品第一項為 241 鋼鐵；其餘（第一項為其他產品、241 鋼鐵列為兼營）為非鋼鐵本業
            "core": bool(prods) and prods[0].replace(" ", "").startswith("241"),
        })
    
    # 鄉鎮區聚落彙總：工廠數、資本額（同一公司只計一次）
    agg = collections.defaultdict(lambda: {"n": 0, "nc": 0, "cos": {}, "xs": [], "ys": []})
    for f in facs:
        a = agg[(f["c"], f["t"])]
        a["n"] += 1; a["nc"] += 1 if f["core"] else 0; a["xs"].append(f["x"]); a["ys"].append(f["y"])
        if f["cap"]:
            a["cos"][f["tid"]] = (f["co"] or f["n"], f["cap"])
    towns = []
    for (c, t), a in agg.items():
        top = sorted(a["cos"].values(), key=lambda v: -v[1])[:3]
        tx, ty = C["town"].get(c + t, [sum(a["xs"]) / len(a["xs"]), sum(a["ys"]) / len(a["ys"])])
        towns.append({"c": c, "t": t, "n": a["n"], "nc": a["nc"], "cap": sum(v[1] for v in a["cos"].values()),
                      "x": tx, "y": ty, "top": [v[0] for v in top]})
    towns.sort(key=lambda v: (-v["n"], -v["cap"]))
    counties = collections.Counter(f["c"] for f in facs)
    cos = {f["tid"]: f["cap"] for f in facs if f["cap"]}
    data = {"source": "經濟部工廠登記（生產中工廠清冊）、經濟部商工登記公示資料（資本額）",
            "asof": "", "factories": facs, "towns": towns,
            "summary": {"factories": len(facs), "companies": len({f["tid"] for f in facs}),
                        "counties": len(counties), "capital": sum(cos.values()),
                        "with_cap": sum(1 for f in facs if f["cap"]), "unlocated": miss,
                        "core": sum(1 for f in facs if f["core"])}}
    return data
    


if __name__ == "__main__":
    sys.exit(main())
