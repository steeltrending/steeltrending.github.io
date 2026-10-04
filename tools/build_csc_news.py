#!/usr/bin/env python3
"""從每日完整報告（data/report/<日期>/text.txt）彙整「中鋼」相關新聞，輸出 data/csc_news.json。

- 每則新聞取自報告中的單一條目（・／•／1. 開頭），只要提到「中鋼」即收錄；
  「中鋼協」（中國鋼鐵工業協會）不算。
- 內容相近的重複報導只保留最早出現的那一天，並記下後續被重複報導的次數。
- 由 GitHub Actions（.github/workflows/csc-news.yml）在每日報告更新後自動執行。

用法：python3 tools/build_csc_news.py
"""
import datetime as dt
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "csc_news.json")
TPE = dt.timezone(dt.timedelta(hours=8))

BULLET = re.compile(r"\s*(?:[・•]|(?<![\d.])\d{1,2}\.\s)\s*")
SOURCE = re.compile(r"[（(]\s*(?:來源[:：]\s*)?([^（）()]{2,40})[）)]\s*[。.]?\s*$")
REGION = re.compile(r"【[^】]+】")
NOISE = re.compile(r"鋼鐵潮流工作室.*$")


HEADER = re.compile(r"全球鋼鐵產經速報|STEEL MARKET DAILY|完整版報告請見官方頻道|^\s*Sources\s*$")
ENDS = re.compile(r"[）)]\s*[。.]?\s*$")


def items_of(text):
    """把報告切成一則一則：條目符號開頭、或上一行以（來源）收尾時，視為新條目。"""
    text = text.split("\nSources")[0]
    items, cur = [], ""
    for line in text.splitlines():
        if HEADER.search(line):
            continue
        line = REGION.sub(" ", line).strip()
        if not line:
            continue
        starts = re.match(r"^(?:[・•⚠]|\d{1,2}\.\s)", line)
        if cur and (starts or ENDS.search(cur)):
            items.append(cur)
            cur = ""
        cur += (" " if cur else "") + line
    if cur:
        items.append(cur)
    out = []
    for p in items:
        p = re.sub(r"^(?:[・•⚠]|\d{1,2}\.\s)\s*", "", p)
        p = NOISE.sub("", p).strip()
        p = re.sub(r"\s+", " ", p)
        # pdftotext 斷行會在中文字間留空白，去掉中日韓字元之間的空白
        p = re.sub(r"(?<=[\u3000-\u9fff\uff00-\uffef]) (?=[\u3000-\u9fff\uff00-\uffef0-9])", "", p)
        p = re.sub(r"(?<=[0-9]) (?=[\u3000-\u9fff\uff00-\uffef])", "", p)
        if len(p) >= 20:
            out.append(p)
    return out


def mentions_csc(s):
    """中鋼要是這則新聞的主角：出現在前 30 個字內（不含「中鋼協」）。"""
    if s.startswith(("重大關稅", "⚠")) or "：" in s[:12]:
        return False
    return re.search(r"(?<!其)中鋼(?!協|材|鐵)", s[:30]) is not None


MONTH = r"(1[0-2]|[1-9])"

# 手動排除：內容含任一字串的條目不收錄（例如來源資料有誤時）
EXCLUDE = [
]


def implausible(body, date, event):
    """營收要到隔月才公布：報告日期還在該月（含）之前出現的「X 月營收」視為資料有誤。"""
    if event and event.startswith("revenue-"):
        month = int(event.split("-")[1])
        m = int(date[5:7])
        # 同月或更早（相差半年內）就出現 → 不合理；跨年的情況（如 1 月報 12 月營收）相差 ≥ 6，不受影響
        if 0 <= month - m < 6:
            return True
    return any(x in body for x in EXCLUDE)


def event_key(s):
    """同一事件的不同報導歸成同一組：X 月盤價、X 月營收、X 月出貨。"""
    m = re.search(MONTH + r"月(?!\d)(?:份)?[^，。；\d]{0,10}?盤", s)
    if m:
        n = m.group(1)
        if re.search(r"看漲|預估|傳出|傳看", s):
            return "price-forecast-" + n
        return "price-" + n
    m = re.search(MONTH + r"月(?:合併)?營收", s)
    if m:
        return "revenue-" + m.group(1)
    m = re.search(MONTH + r"月(?:集團)?出貨", s)
    if m:
        return "shipment-" + m.group(1)
    if "出口許可證" in s or "出口管制" in s:
        return "cn-export-license"
    return None


def norm(s):
    s = SOURCE.sub("", s)
    return re.sub(r"[\s，。、；：「」（）()0-9０-９,.%]", "", s)


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "report", "*", "text.txt"))):
        date = os.path.basename(os.path.dirname(f))
        try:
            text = open(f, encoding="utf-8").read()
        except OSError:
            continue
        for it in items_of(text):
            if not mentions_csc(it):
                continue
            m = SOURCE.search(it)
            src = m.group(1).strip() if m else ""
            body = SOURCE.sub("", it).strip(" ，。") + "。"
            ev = event_key(body)
            if implausible(body, date, ev):
                continue
            rows.append({"date": date, "text": body, "source": src, "key": norm(body), "event": ev})

    def grams(k):
        return {k[i:i + 2] for i in range(len(k) - 1)}

    def days(a, b):
        return abs((dt.date.fromisoformat(a) - dt.date.fromisoformat(b)).days)

    kept = []
    for r in rows:  # 由舊到新：三週內內容相近的報導只留第一次出現
        g = grams(r["key"])
        dup = None
        for k in kept:
            if days(r["date"], k["date"]) > 35:
                continue
            if r["event"] and r["event"] == k["event"]:
                dup = k
                break
            kg = k["grams"]
            sim = len(g & kg) / max(1, min(len(g), len(kg)))
            if sim > 0.5:
                dup = k
                break
        if dup:
            dup["repeats"] = dup.get("repeats", 0) + 1
            dup["last_seen"] = r["date"]
            continue
        r["grams"] = g
        kept.append(r)

    items = []
    for k in reversed(kept):
        items.append({
            "date": k["date"], "text": k["text"], "source": k["source"],
            "repeats": k.get("repeats", 0), "last_seen": k.get("last_seen"),
            "report": f"day.html?d={k['date']}",
        })
    data = {"updated": dt.datetime.now(TPE).replace(microsecond=0).isoformat(), "count": len(items), "items": items}
    old = None
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT, encoding="utf-8"))
        except ValueError:
            pass
    if old and old.get("items") == items:
        print(f"沒有變化（{len(items)} 則）")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"中鋼新聞 {len(items)} 則（原始 {len(rows)} 則，合併重複 {len(rows) - len(items)} 則）")


if __name__ == "__main__":
    main()
