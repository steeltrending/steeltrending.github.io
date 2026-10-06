import json, os, sys
from playwright.sync_api import sync_playwright
q = json.load(open("queries.json"))
os.makedirs("out/render", exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, url in q.get("render", {}).items():
        pg = b.new_page(viewport={"width": 1400, "height": 1000})
        caps = []
        def on_resp(r):
            try:
                ct = r.headers.get("content-type", "")
                if "json" in ct or r.url.endswith(".json") or "csv" in ct:
                    caps.append({"url": r.url, "status": r.status, "body": r.text()[:400000]})
            except Exception as e:
                pass
        pg.on("response", on_resp)
        try:
            pg.goto(url, wait_until="networkidle", timeout=90000)
            pg.wait_for_timeout(6000)
        except Exception as e:
            open(f"out/render/{name}.err", "w").write(str(e))
        open(f"out/render/{name}.html", "w").write(pg.content())
        open(f"out/render/{name}.txt", "w").write(pg.inner_text("body"))
        pg.screenshot(path=f"out/render/{name}.png", full_page=True)
        json.dump(caps, open(f"out/render/{name}.net.json", "w"), ensure_ascii=False)
    b.close()
