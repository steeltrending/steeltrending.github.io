#!/usr/bin/env python3
"""把 echarts 4.9 的 china.json（UTF8 差分編碼）解碼，轉成 Albers 等積圓錐投影的 SVG 路徑。

用法：python3 tools/build_cnmap_geo.py <china.json> [輸出路徑，預設 assets/cnmap-geo.json]
產出：{"W":..,"H":..,"provs":[{"id","n","en","d","cx","cy"}...]}
- 不含台灣（本站另有「台灣鋼鐵地圖」）；香港、澳門保留為無統計區塊。
- 一次性產生，不在排程中執行。
"""
import json, math, sys

TC = {  # 簡體 → 繁體省名（與 data/cnsteel.json 的 id 對應）
    '北京': ('北京市', 'Beijing'), '天津': ('天津市', 'Tianjin'), '河北': ('河北省', 'Hebei'),
    '山西': ('山西省', 'Shanxi'), '内蒙古': ('內蒙古', 'Inner Mongolia'), '辽宁': ('遼寧省', 'Liaoning'),
    '吉林': ('吉林省', 'Jilin'), '黑龙江': ('黑龍江省', 'Heilongjiang'), '上海': ('上海市', 'Shanghai'),
    '江苏': ('江蘇省', 'Jiangsu'), '浙江': ('浙江省', 'Zhejiang'), '安徽': ('安徽省', 'Anhui'),
    '福建': ('福建省', 'Fujian'), '江西': ('江西省', 'Jiangxi'), '山东': ('山東省', 'Shandong'),
    '河南': ('河南省', 'Henan'), '湖北': ('湖北省', 'Hubei'), '湖南': ('湖南省', 'Hunan'),
    '广东': ('廣東省', 'Guangdong'), '广西': ('廣西', 'Guangxi'), '海南': ('海南省', 'Hainan'),
    '重庆': ('重慶市', 'Chongqing'), '四川': ('四川省', 'Sichuan'), '贵州': ('貴州省', 'Guizhou'),
    '云南': ('雲南省', 'Yunnan'), '西藏': ('西藏', 'Tibet'), '陕西': ('陝西省', 'Shaanxi'),
    '甘肃': ('甘肅省', 'Gansu'), '青海': ('青海省', 'Qinghai'), '宁夏': ('寧夏', 'Ningxia'),
    '新疆': ('新疆', 'Xinjiang'), '香港': ('香港', 'Hong Kong'), '澳门': ('澳門', 'Macao'),
}


def dec_ring(s, off):
    out, px, py = [], off[0], off[1]
    for i in range(0, len(s), 2):
        x = ord(s[i]) - 64
        y = ord(s[i + 1]) - 64
        x = (x >> 1) ^ (-(x & 1))
        y = (y >> 1) ^ (-(y & 1))
        px += x
        py += y
        out.append((px / 1024.0, py / 1024.0))
    return out


def polys(geom):
    co, eo = geom['coordinates'], geom['encodeOffsets']
    if geom['type'] == 'Polygon':
        return [[dec_ring(r, eo[i]) for i, r in enumerate(co)]]
    return [[dec_ring(r, eo[k][i]) for i, r in enumerate(poly)] for k, poly in enumerate(co)]


# Albers equal-area conic（中國常用：標準緯線 25°N / 47°N，中央經線 105°E）
P1, P2, L0, F0 = map(math.radians, (25, 47, 105, 0))
n = (math.sin(P1) + math.sin(P2)) / 2
C = math.cos(P1) ** 2 + 2 * n * math.sin(P1)
R0 = math.sqrt(C - 2 * n * math.sin(F0)) / n


def proj(lon, lat):
    l, f = math.radians(lon), math.radians(lat)
    r = math.sqrt(C - 2 * n * math.sin(f)) / n
    t = n * (l - L0)
    return r * math.sin(t), -(R0 - r * math.cos(t))


def area_centroid(ring):
    a = cx = cy = 0.0
    for i in range(len(ring)):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % len(ring)]
        k = x0 * y1 - x1 * y0
        a += k
        cx += (x0 + x1) * k
        cy += (y0 + y1) * k
    a /= 2
    return (a, cx / (6 * a), cy / (6 * a)) if a else (0, ring[0][0], ring[0][1])


def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else 'assets/cnmap-geo.json'
    g = json.load(open(src, encoding='utf-8'))
    items = []
    for f in g['features']:
        name = f['properties']['name']
        if name == '台湾':
            continue
        pj = [[[proj(*pt) for pt in ring] for ring in poly] for poly in polys(f['geometry'])]
        items.append((name, pj))
    xs = [p[0] for _, pj in items for poly in pj for ring in poly for p in ring]
    ys = [p[1] for _, pj in items for poly in pj for ring in poly for p in ring]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    W = 800.0
    k = (W - 20) / (x1 - x0)
    H = round((y1 - y0) * k + 20)
    tx = lambda p: ((p[0] - x0) * k + 10, (p[1] - y0) * k + 10)
    provs = []
    for name, pj in items:
        d, best = [], (0, 0, 0)
        for poly in pj:
            for ring in poly:
                pts = [tx(p) for p in ring]
                d.append('M' + 'L'.join('%.1f,%.1f' % p for p in pts) + 'Z')
            a, cx, cy = area_centroid([tx(p) for p in poly[0]])
            if abs(a) > abs(best[0]):
                best = (a, cx, cy)
        tc, en = TC[name]
        provs.append({'id': tc, 'n': tc, 'en': en, 'd': ''.join(d), 'cx': round(best[1], 1), 'cy': round(best[2], 1)})
    json.dump({'W': int(W), 'H': H, 'provs': provs}, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('provs', len(provs), 'size', W, H)


if __name__ == '__main__':
    main()
