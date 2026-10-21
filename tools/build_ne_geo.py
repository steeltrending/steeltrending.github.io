#!/usr/bin/env python3
"""日本、南韓行政區地圖：由 Natural Earth 1:10m admin-1（公有領域）產生 Albers 投影的 SVG 路徑。

用法：python3 tools/build_ne_geo.py <ne_10m_admin_1_states_provinces.geojson> [輸出資料夾，預設 assets] [jp kr us ...]
產出：assets/jpmap-geo.json、assets/krmap-geo.json、assets/usmap-geo.json（可只指定其中幾個）
  {"W","H","proj":{p1,p2,l0,f0,x0,y0,k},"provs":[{"id","n","en","d","cx","cy"}...]}
- 頁面以 proj 把廠區經緯度投影到同一座標系，所以資料檔只存經緯度。
- 日本：遠離本土的小島（小笠原等）略去；沖繩縣以示意位置放在左下角（inset=true），不代表實際相對位置。
- 南韓：略去面積極小的島嶼。
- 美國：只畫本土 48 州＋華盛頓特區（阿拉斯加、夏威夷無鋼廠，略去）。
- 一次性產生，不在排程中執行。需要 shapely。
"""
import json, math, sys, os
from shapely.geometry import shape, Polygon, MultiPolygon, box
from shapely.affinity import translate

CFG = {
    'jp': dict(admin='Japan', p1=30, p2=45, l0=137, f0=36, W=720, min_area=0.004, tol=0.012,
               keep=lambda lon, lat, name: 30 <= lat <= 46 and lon <= 146.5),
    'kr': dict(admin='South Korea', p1=33, p2=38, l0=127.5, f0=36, W=520, min_area=0.002, tol=0.006,
               keep=lambda lon, lat, name: True),
    'us': dict(admin='United States of America', p1=29.5, p2=45.5, l0=-96, f0=37.5, W=900, min_area=0.02, tol=0.02,
               keep=lambda lon, lat, name: 24 <= lat <= 50 and -126 <= lon <= -66),
}
US_TC = {'Alabama': '阿拉巴馬州', 'Arizona': '亞利桑那州', 'Arkansas': '阿肯色州', 'California': '加利福尼亞州', 'Colorado': '科羅拉多州',
         'Connecticut': '康乃狄克州', 'Delaware': '德拉瓦州', 'District of Columbia': '華盛頓特區', 'Florida': '佛羅里達州', 'Georgia': '喬治亞州',
         'Idaho': '愛達荷州', 'Illinois': '伊利諾州', 'Indiana': '印第安納州', 'Iowa': '愛荷華州', 'Kansas': '堪薩斯州', 'Kentucky': '肯塔基州',
         'Louisiana': '路易斯安那州', 'Maine': '緬因州', 'Maryland': '馬里蘭州', 'Massachusetts': '麻薩諸塞州', 'Michigan': '密西根州',
         'Minnesota': '明尼蘇達州', 'Mississippi': '密西西比州', 'Missouri': '密蘇里州', 'Montana': '蒙大拿州', 'Nebraska': '內布拉斯加州',
         'Nevada': '內華達州', 'New Hampshire': '新罕布夏州', 'New Jersey': '紐澤西州', 'New Mexico': '新墨西哥州', 'New York': '紐約州',
         'North Carolina': '北卡羅來納州', 'North Dakota': '北達科他州', 'Ohio': '俄亥俄州', 'Oklahoma': '奧克拉荷馬州', 'Oregon': '奧勒岡州',
         'Pennsylvania': '賓夕法尼亞州', 'Rhode Island': '羅德島州', 'South Carolina': '南卡羅來納州', 'South Dakota': '南達科他州',
         'Tennessee': '田納西州', 'Texas': '德克薩斯州', 'Utah': '猶他州', 'Vermont': '佛蒙特州', 'Virginia': '維吉尼亞州',
         'Washington': '華盛頓州', 'West Virginia': '西維吉尼亞州', 'Wisconsin': '威斯康辛州', 'Wyoming': '懷俄明州'}
KR_TC = {'江原道': '江原道', '京畿道': '京畿道', '忠清南道': '忠清南道', '仁川広域市': '仁川廣域市', '全羅北道': '全羅北道', '全羅南道': '全羅南道', '慶尚南道': '慶尚南道', '釜山広域市': '釜山廣域市', '蔚山広域市': '蔚山廣域市', '慶尚北道': '慶尚北道', '済州特別自治道': '濟州特別自治道', 'ソウル特別市': '首爾特別市', '大田広域市': '大田廣域市', '世宗特別自治市': '世宗特別自治市', '忠清北道': '忠清北道', '光州広域市': '光州廣域市', '大邱広域市': '大邱廣域市'}  # 南韓行政區改用繁體中文漢字名
OKINAWA_SHIFT = (14.5, 6.5)  # 度：把沖繩移到本州東南方的太平洋空白處，作為示意 inset（僅限日本）


def make_proj(p1, p2, l0, f0):
    p1, p2, l0, f0 = map(math.radians, (p1, p2, l0, f0))
    n = (math.sin(p1) + math.sin(p2)) / 2
    C = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    r0 = math.sqrt(C - 2 * n * math.sin(f0)) / n

    def proj(lon, lat):
        l, f = math.radians(lon), math.radians(lat)
        r = math.sqrt(C - 2 * n * math.sin(f)) / n
        t = n * (l - l0)
        return r * math.sin(t), -(r0 - r * math.cos(t))
    return proj


def polys_of(geom):
    return list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]


def build(key, feats, out):
    c = CFG[key]
    proj = make_proj(c['p1'], c['p2'], c['l0'], c['f0'])
    items = []
    for f in feats:
        p = f['properties']
        if key == 'us' and p['name'] in ('Alaska', 'Hawaii'):
            continue
        name = p['name'] if key == 'us' else (p.get('name_ja') or p.get('name_ko') or p['name'])
        name = US_TC[name] if key == 'us' else KR_TC.get(name, name)
        g = shape(f['geometry'])
        ps = []
        for poly in polys_of(g):
            cen = poly.representative_point()
            okinawa = key == 'jp' and p['name'] == 'Okinawa'
            if not okinawa and not c['keep'](cen.x, cen.y, p['name']):
                continue
            if poly.area < c['min_area'] and not okinawa:
                continue
            if okinawa:
                if poly.area < 0.003:
                    continue
                poly = translate(poly, xoff=OKINAWA_SHIFT[0], yoff=OKINAWA_SHIFT[1])
            ps.append(poly.simplify(c['tol'], preserve_topology=True))
        if not ps:
            continue
        items.append((name, p['name'], ps))
    pts = [proj(x, y) for _, _, ps in items for poly in ps for x, y in poly.exterior.coords]
    x0, x1 = min(q[0] for q in pts), max(q[0] for q in pts)
    y0, y1 = min(q[1] for q in pts), max(q[1] for q in pts)
    k = (c['W'] - 20) / (x1 - x0)
    H = round((y1 - y0) * k + 20)
    tx = lambda lon, lat: ((proj(lon, lat)[0] - x0) * k + 10, (proj(lon, lat)[1] - y0) * k + 10)
    provs = []
    for name, en, ps in items:
        d, best, ba = [], None, 0
        for poly in ps:
            for ring in [poly.exterior] + list(poly.interiors):
                pp = [tx(x, y) for x, y in ring.coords][:-1]
                if len(pp) >= 3:
                    d.append('M' + 'L'.join('%.1f,%.1f' % q for q in pp) + 'Z')
            if poly.area > ba:
                ba, best = poly.area, poly.representative_point()
        cx, cy = tx(best.x, best.y)
        provs.append({'id': name, 'n': name, 'en': en, 'd': ''.join(d), 'cx': round(cx, 1), 'cy': round(cy, 1)})
    data = {'W': c['W'], 'H': H, 'proj': {'p1': c['p1'], 'p2': c['p2'], 'l0': c['l0'], 'f0': c['f0'], 'x0': x0, 'y0': y0, 'k': k},
            'provs': provs, 'inset': 'Okinawa' if key == 'jp' else None}
    json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(key, len(provs), 'regions', c['W'], H, os.path.getsize(out), 'bytes')


def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else 'assets'
    keys = sys.argv[3:] or list(CFG)
    g = json.load(open(src, encoding='utf-8'))
    for key in keys:
        feats = [f for f in g['features'] if f['properties'].get('admin') == CFG[key]['admin']]
        build(key, feats, os.path.join(dst, key + 'map-geo.json'))


if __name__ == '__main__':
    main()
