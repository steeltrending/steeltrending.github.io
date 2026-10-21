#!/usr/bin/env python3
"""歐洲國家地圖：由 Natural Earth 1:50m admin-0 國界（公有領域）產生 Albers 等積圓錐投影的 SVG 路徑。

用法：python3 tools/build_eu_geo.py <ne_50m_admin_0_countries.geojson> [輸出路徑，預設 assets/eumap-geo.json]
產出：{"W","H","proj","provs":[{"id"(ISO 3 碼),"n","en","g","d","cx","cy"}...]}
- g：EU27＝歐盟 27 國；OTH＝其他歐洲（worldsteel 定義：英國、挪威、瑞士、土耳其、塞爾維亞等）；
  CTX＝範圍外的底圖（俄羅斯、烏克蘭、白俄羅斯、摩爾多瓦），灰色、不可點選。
- 以經度 -25～45、緯度 34～72 的範圍裁切（範圍外底圖另在平面座標裁成範圍內各國的外框），海外領地（法屬圭亞那、加那利群島、斯瓦巴等）不入圖。
- 一次性產生，不在排程中執行。需要 shapely。
"""
import json, math, os, sys
from shapely.geometry import shape, box, MultiPolygon, Polygon
from shapely.ops import transform

EU = {'AUT': '奧地利', 'BEL': '比利時', 'BGR': '保加利亞', 'HRV': '克羅埃西亞', 'CYP': '賽普勒斯', 'CZE': '捷克', 'DNK': '丹麥',
      'EST': '愛沙尼亞', 'FIN': '芬蘭', 'FRA': '法國', 'DEU': '德國', 'GRC': '希臘', 'HUN': '匈牙利', 'IRL': '愛爾蘭', 'ITA': '義大利',
      'LVA': '拉脫維亞', 'LTU': '立陶宛', 'LUX': '盧森堡', 'MLT': '馬爾他', 'NLD': '荷蘭', 'POL': '波蘭', 'PRT': '葡萄牙',
      'ROU': '羅馬尼亞', 'SVK': '斯洛伐克', 'SVN': '斯洛維尼亞', 'ESP': '西班牙', 'SWE': '瑞典'}
OTH = {'GBR': '英國', 'NOR': '挪威', 'CHE': '瑞士', 'ISL': '冰島', 'SRB': '塞爾維亞', 'BIH': '波士尼亞', 'MKD': '北馬其頓',
       'ALB': '阿爾巴尼亞', 'MNE': '蒙特內哥羅', 'KOS': '科索沃', 'TUR': '土耳其'}
CTX = {'RUS': '俄羅斯', 'UKR': '烏克蘭', 'BLR': '白俄羅斯', 'MDA': '摩爾多瓦'}
P1, P2, L0, F0 = 38, 62, 14, 50
WIN = box(-25, 34, 45, 72)
WIN_CTX = box(-25, 34, 90, 80)  # 範圍外底圖先取寬一點，之後在平面座標裁成直線邊界
W = 860
MIN_AREA, TOL = 0.02, 0.03


def make_proj():
    p1, p2, l0, f0 = map(math.radians, (P1, P2, L0, F0))
    n = (math.sin(p1) + math.sin(p2)) / 2
    C = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    r0 = math.sqrt(C - 2 * n * math.sin(f0)) / n

    def proj(lon, lat):
        l, f = math.radians(lon), math.radians(lat)
        r = math.sqrt(C - 2 * n * math.sin(f)) / n
        t = n * (l - l0)
        return r * math.sin(t), -(r0 - r * math.cos(t))
    return proj


def polys_of(g):
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [x for x in getattr(g, 'geoms', []) if isinstance(x, (Polygon, MultiPolygon))] and sum([polys_of(x) for x in g.geoms], [])


def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else 'assets/eumap-geo.json'
    gj = json.load(open(src, encoding='utf-8'))
    proj = make_proj()
    items = []
    for f in gj['features']:
        p = f['properties']
        iso = p['ADM0_A3']
        if iso == 'KOS' or p.get('NAME') == 'Kosovo':
            iso = 'KOS'
        grp = 'EU27' if iso in EU else 'OTH' if iso in OTH else 'CTX' if iso in CTX else None
        if not grp:
            continue
        name = {**EU, **OTH, **CTX}[iso]
        g = shape(f['geometry']).buffer(0).intersection(WIN_CTX if grp == 'CTX' else WIN)
        ps = [q.simplify(TOL, preserve_topology=True) for q in polys_of(g) if q.area >= MIN_AREA]
        if ps:
            items.append((iso, name, p['NAME'], grp, ps))
    have = {i[0] for i in items}
    miss = (set(EU) | set(OTH) | set(CTX)) - have
    if miss:
        print('missing', sorted(miss))
    # 先投影成平面座標；範圍外底圖再裁成範圍內各國的外框，邊界才會是乾淨的直線
    pj = lambda xs, ys: tuple(zip(*[proj(a, b) for a, b in zip(xs, ys)]))
    items = [(iso, name, en, grp, [transform(pj, q) for q in ps]) for iso, name, en, grp, ps in items]
    sc = [q.bounds for _, _, _, grp, ps in items if grp != 'CTX' for q in ps]
    bx = box(min(b[0] for b in sc), min(b[1] for b in sc), max(b[2] for b in sc), max(b[3] for b in sc))
    clipped = []
    for iso, name, en, grp, ps in items:
        if grp == 'CTX':
            ps = [r for q in ps for r in polys_of(q.intersection(bx)) if r.area > 1e-6]
        clipped.append((iso, name, en, grp, ps))
    items = clipped
    pts = [(x, y) for _, _, _, _, ps in items for q in ps for x, y in q.exterior.coords]
    x0, x1 = min(a[0] for a in pts), max(a[0] for a in pts)
    y0, y1 = min(a[1] for a in pts), max(a[1] for a in pts)
    k = (W - 20) / (x1 - x0)
    H = round((y1 - y0) * k + 20)
    tx = lambda x, y: ((x - x0) * k + 10, (y - y0) * k + 10)
    provs = []
    for iso, name, en, grp, ps in sorted(items):
        d, best, ba = [], None, 0
        for q in ps:
            for ring in [q.exterior] + list(q.interiors):
                pp = [tx(x, y) for x, y in ring.coords][:-1]
                if len(pp) >= 3:
                    d.append('M' + 'L'.join('%.1f,%.1f' % a for a in pp) + 'Z')
            if q.area > ba:
                ba, best = q.area, q.representative_point()
        cx, cy = tx(best.x, best.y)
        provs.append({'id': iso, 'n': name, 'en': en, 'g': grp, 'd': ''.join(d), 'cx': round(cx, 1), 'cy': round(cy, 1)})
    out = {'W': W, 'H': H, 'proj': {'p1': P1, 'p2': P2, 'l0': L0, 'f0': F0, 'x0': x0, 'y0': y0, 'k': k}, 'provs': provs}
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(len(provs), 'countries', W, H, os.path.getsize(dst), 'bytes')


if __name__ == '__main__':
    main()
