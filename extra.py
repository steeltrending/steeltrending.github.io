import io, zipfile, urllib.request, urllib.parse, csv, os, json, time
os.makedirs("out/raw", exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}
url = "https://serv.gcis.nat.gov.tw/RDownLoad/Data/statistical/%E7%94%9F%E7%94%A2%E4%B8%AD%E5%B7%A5%E5%BB%A0%E6%B8%85%E5%86%8A.zip"
z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600).read()))
name = z.infolist()[0].filename
rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
hdr = rows[0]
st = [r for r in rows[1:] if "241鋼鐵" in r[12].replace(" ", "")]
with open("out/raw/steel_factories.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(hdr + ["source_file"]); [w.writerow(r + [name]) for r in st]
ids = sorted({r[6] for r in st if r[6].strip()})
API = "https://data.gcis.nat.gov.tw/od/data/api/{}?$format=json&$filter=Business_Accounting_NO eq {}&$skip=0&$top=50"
COMP = "5F64D864-61CB-4D0D-8AD9-492047CC1EA6"
BIZ = "7E6AFA72-AD6A-46D3-8681-ED77951D912D"
res = {}
for i, tid in enumerate(ids):
    rec = None
    for api in (COMP, BIZ):
        u = API.format(api, tid).replace(" ", "%20")
        for t in range(3):
            try:
                txt = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8")
                break
            except Exception as e:
                txt = ""; time.sleep(2)
        if txt.strip():
            try:
                d = json.loads(txt)
                if d:
                    rec = {"api": api, "data": d[0]}; break
            except Exception:
                pass
    res[tid] = rec
    time.sleep(0.15)
json.dump(res, open("out/raw/steel_caps.json", "w"), ensure_ascii=False)
print(len(st), len(ids), sum(1 for v in res.values() if v))
