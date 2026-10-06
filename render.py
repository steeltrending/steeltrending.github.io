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
                if r.request.resource_type in ("xhr", "fetch") or "json" in ct or "csv" in ct:
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

# 在頁面同源環境中呼叫 API（需瀏覽器 cookie / referer）
if q.get("api"):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(q["api"]["page"], wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(4000)
        os.makedirs("out/api", exist_ok=True)
        for name, url in q["api"]["urls"].items():
            try:
                txt = pg.evaluate("u => fetch(u, {credentials:'include'}).then(r => r.text())", url)
            except Exception as e:
                txt = "ERR " + str(e)
            open("out/api/" + name, "w").write(txt)
        b.close()
