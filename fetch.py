import json, os, re, urllib.request, urllib.parse
UA = {"User-Agent": "SteelTrendingBot/1.0 (https://steeltrending.github.io; noreply@steeltrending.github.io)"}
API = "https://commons.wikimedia.org/w/api.php?"
def get(params):
    req = urllib.request.Request(API + urllib.parse.urlencode(params), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=60))
def dl(url, path):
    req = urllib.request.Request(url, headers=UA)
    open(path, "wb").write(urllib.request.urlopen(req, timeout=120).read())
q = json.load(open("queries.json"))
os.makedirs("out/thumbs", exist_ok=True); os.makedirs("out/full", exist_ok=True)
res = {}
for s in q.get("search", []):
    try:
        d = get({"action": "query", "format": "json", "generator": "search", "gsrsearch": s, "gsrnamespace": 6, "gsrlimit": 10,
                 "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 400})
    except Exception as e:
        res[s] = str(e); continue
    lst = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        g = lambda k: re.sub("<[^>]+>", "", m.get(k, {}).get("value", ""))[:200]
        fn = "%02d_%d.jpg" % (len(res), len(lst))
        try: dl(ii["thumburl"], "out/thumbs/" + fn)
        except Exception: fn = None
        lst.append({"title": p["title"], "thumb": fn, "w": ii.get("width"), "h": ii.get("height"), "license": g("LicenseShortName"),
                    "artist": g("Artist"), "date": g("DateTimeOriginal"), "desc": g("ImageDescription")})
    res[s] = lst
json.dump(res, open("out/search.json", "w"), ensure_ascii=False, indent=1)
for t, name in q.get("download", {}).items():
    d = get({"action": "query", "format": "json", "titles": t, "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 1280})
    p = list(d["query"]["pages"].values())[0]
    dl(p["imageinfo"][0]["thumburl"], "out/full/" + name)
