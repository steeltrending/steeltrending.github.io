#!/usr/bin/env python3
"""Temporary helper (branch tmp/commons-eaf-photos only).
pick.txt empty  -> search Commons for free-licensed EAF photos, save 480px thumbs + candidates.json
pick.txt filled -> download each listed File: title at 960px wide into out/ with meta.json
"""
import json, os, re, sys, time, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = "steeltrending-bot/1.0 (https://steeltrending.github.io; noreply@steeltrending.github.io)"
HERE = os.path.dirname(os.path.abspath(__file__))
FREE = re.compile(r"^(CC BY(-SA)? [0-9.]+|CC BY(-SA)?|CC0|Public domain|PD.*|Attribution)", re.I)

def get(params):
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        f.write(r.read())

def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()

def info(titles, width):
    out = []
    for i in range(0, len(titles), 40):
        d = get({"action": "query", "titles": "|".join(titles[i:i+40]), "prop": "imageinfo",
                 "iiprop": "url|size|mime|extmetadata", "iiurlwidth": width})
        for p in d["query"]["pages"]:
            if "imageinfo" not in p:
                continue
            ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
            v = lambda k: strip(m.get(k, {}).get("value", ""))
            out.append({"title": p["title"], "w": ii["width"], "h": ii["height"], "mime": ii["mime"],
                        "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"),
                        "license": v("LicenseShortName"), "license_url": v("LicenseUrl"),
                        "artist": v("Artist"), "credit": v("Credit"), "date": v("DateTimeOriginal"),
                        "desc": v("ImageDescription")[:400], "cats": v("Categories")[:300]})
        time.sleep(0.5)
    return out

def members(cat, kind):
    res, cont = [], {}
    while True:
        d = get(dict({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmtype": kind, "cmlimit": "500"}, **cont))
        res += [m["title"] for m in d["query"]["categorymembers"]]
        if "continue" not in d: return res
        cont = d["continue"]

def candidates():
    used = {urllib.parse.unquote(l.strip()).replace("_", " ") for l in open(os.path.join(HERE, "used.txt")) if l.strip()}
    titles = set()
    cats = ["Category:Electric arc furnaces"] + members("Category:Electric arc furnaces", "subcat")
    for c in cats:
        titles |= set(members(c, "file"))
    for q in ["electric arc furnace steel", "Elektrolichtbogenofen", "arc furnace tapping", "electric arc furnace electrodes"]:
        d = get({"action": "query", "list": "search", "srsearch": q + " filetype:bitmap", "srnamespace": "6", "srlimit": "50"})
        titles |= {s["title"] for s in d["query"]["search"]}
    titles = sorted(t for t in titles if t.replace("File:", "") not in used)
    items = [x for x in info(titles, 480) if x["mime"] in ("image/jpeg", "image/png")
             and x["w"] >= 900 and FREE.match(x["license"] or "")]
    os.makedirs(os.path.join(HERE, "cand"), exist_ok=True)
    keep = []
    for n, x in enumerate(items[:80]):
        fn = "c%02d.jpg" % n
        try:
            download(x["thumb"], os.path.join(HERE, "cand", fn)); x["file"] = fn; keep.append(x)
        except Exception as e:  # noqa
            print("skip", x["title"], e)
        time.sleep(0.3)
    json.dump({"searched": len(titles), "items": keep}, open(os.path.join(HERE, "candidates.json"), "w"), ensure_ascii=False, indent=1)
    print("candidates:", len(keep), "of", len(titles))

def fetch(picks):
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    items = info(picks, 960)
    for x in items:
        fn = re.sub(r"[^A-Za-z0-9._-]+", "_", x["title"].replace("File:", ""))[:80]
        if not fn.lower().endswith((".jpg", ".jpeg", ".png")): fn += ".jpg"
        download(x["thumb"], os.path.join(HERE, "out", fn)); x["file"] = fn
        time.sleep(0.5)
    json.dump(items, open(os.path.join(HERE, "out", "meta.json"), "w"), ensure_ascii=False, indent=1)
    print("downloaded", len(items))

if __name__ == "__main__":
    picks = [l.strip() for l in open(os.path.join(HERE, "pick.txt")) if l.strip()]
    fetch(picks) if picks else candidates()
