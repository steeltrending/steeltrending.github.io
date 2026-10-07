import subprocess, sys, json, os, urllib.request
os.makedirs("out/tr", exist_ok=True)
log = {}
U = "https://trends.google.com/trends/embed/explore/TIMESERIES?req=%7B%22comparisonItem%22%3A%5B%7B%22keyword%22%3A%22%E9%8B%BC%E5%83%B9%22%2C%22geo%22%3A%22TW%22%2C%22time%22%3A%22today%2012-m%22%7D%5D%2C%22category%22%3A0%2C%22property%22%3A%22%22%7D&tz=-480&hl=zh-TW"
try:
    r = urllib.request.urlopen(urllib.request.Request(U, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"}), timeout=60)
    log["direct"] = {"status": r.status, "headers": dict(r.headers), "body": r.read().decode("utf-8", "replace")[:3000]}
except Exception as e:
    log["direct"] = {"err": repr(e), "body": getattr(e, "read", lambda: b"")().decode("utf-8", "replace")[:3000] if hasattr(e, "read") else ""}
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"], check=True)
subprocess.run([sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"], check=True, stdout=subprocess.DEVNULL)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(viewport={"width": 1400, "height": 1000}, locale="zh-TW", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36")
    pg = ctx.new_page()
    net = []
    pg.on("response", lambda r: net.append([r.status, r.request.resource_type, r.url[:300]]) if "google" in r.url else None)
    cons = []
    pg.on("console", lambda m: cons.append(m.type + ": " + m.text[:300]))
    pg.goto("https://steeltrending.github.io/trends.html", wait_until="load", timeout=90000)
    pg.mouse.wheel(0, 600); pg.wait_for_timeout(4000); pg.mouse.wheel(0, 1200); pg.wait_for_timeout(12000)
    pg.screenshot(path="out/tr/page.png", full_page=True)
    frames = []
    for f in pg.frames[1:]:
        try: frames.append({"url": f.url[:200], "text": f.inner_text("body")[:800]})
        except Exception as e: frames.append({"url": f.url[:200], "err": str(e)[:200]})
    log["net"] = net; log["console"] = cons; log["frames"] = frames
    # direct embed page in browser
    pg2 = ctx.new_page(); net2 = []
    pg2.on("response", lambda r: net2.append([r.status, r.request.resource_type, r.url[:200]]))
    pg2.goto(U, wait_until="load", timeout=90000); pg2.wait_for_timeout(10000)
    pg2.screenshot(path="out/tr/embed.png")
    log["embed_net"] = net2[:60]
    try: log["embed_text"] = pg2.inner_text("body")[:1500]
    except Exception as e: log["embed_text"] = str(e)
    b.close()
json.dump(log, open("out/tr/log.json", "w"), ensure_ascii=False, indent=1)
