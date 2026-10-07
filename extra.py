import io, zipfile, urllib.request, csv, os, json
os.makedirs("out/raw", exist_ok=True)
url = "https://serv.gcis.nat.gov.tw/RDownLoad/Data/statistical/%E7%94%9F%E7%94%A2%E4%B8%AD%E5%B7%A5%E5%BB%A0%E6%B8%85%E5%86%8A.zip"
data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=600).read()
z = zipfile.ZipFile(io.BytesIO(data))
info = {"zip_bytes": len(data), "files": [(i.filename, i.file_size) for i in z.infolist()]}
out = []
for i in z.infolist():
    raw = z.read(i)
    for enc in ("utf-8-sig", "big5", "cp950"):
        try:
            txt = raw.decode(enc); break
        except Exception:
            txt = None
    if txt is None:
        continue
    rows = list(csv.reader(io.StringIO(txt)))
    info.setdefault("headers", {})[i.filename] = rows[:3]
    hdr = rows[0]
    for r in rows[1:]:
        line = ",".join(r)
        if any(k in line for k in ("鋼鐵", "鋼品", "241", "242", "243")):
            out.append([i.filename] + r)
    info.setdefault("rows", {})[i.filename] = len(rows)
json.dump(info, open("out/raw/factories_info.json", "w"), ensure_ascii=False, indent=1)
with open("out/raw/factories_steel.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerows(out)
print(info["files"], len(out))
