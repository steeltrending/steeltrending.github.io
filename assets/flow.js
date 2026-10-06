/* 鋼鐵潮流首頁：01 每日速報、02 追蹤主題、03 關於 三個區域的捲動流動背景。
   捲動經過該區域時，背景的鋼胚方塊會隨捲動速度水平流入（往下捲由右往左流、往上捲反向），並微微加熱成橘色；
   停止捲動後方塊立即減速停住、回到暗灰色。只在區域進入畫面時運作，並尊重「減少動態效果」設定。 */
(function () {
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var IDS = ['daily', 'topics', 'about'];
  var DPR = Math.min(window.devicePixelRatio || 1, 2);
  var layers = [];

  function rnd(a, b) { return a + Math.random() * (b - a); }

  function makeLayer(sec, idx) {
    var cv = document.createElement('canvas');
    cv.setAttribute('aria-hidden', 'true');
    cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;z-index:-1;pointer-events:none;display:block';
    sec.style.position = 'relative';
    sec.style.isolation = 'isolate';
    sec.style.overflow = 'hidden';
    sec.insertBefore(cv, sec.firstChild);
    var L = { sec: sec, cv: cv, ctx: cv.getContext('2d'), w: 0, h: 0, blocks: [], vis: false, heat: 0, dir: idx % 2 ? 1 : -1 };
    layers.push(L);
    return L;
  }

  function seed(L) {
    var r = L.sec.getBoundingClientRect();
    L.w = Math.max(1, Math.round(r.width));
    L.h = Math.max(1, Math.round(r.height));
    L.cv.width = L.w * DPR;
    L.cv.height = L.h * DPR;
    L.ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    // 方塊數量依面積決定；細長鋼胚狀（寬約高的 2～4 倍），三種深度做出前後層次
    var n = Math.round(L.w * L.h / 9000);
    n = Math.max(40, Math.min(n, 220));
    L.blocks = [];
    for (var i = 0; i < n; i++) {
      var depth = [0.35, 0.65, 1][i % 3];
      var bh = rnd(3, 7) * (0.6 + depth * 0.6);
      L.blocks.push({
        x: rnd(0, L.w), y: rnd(0, L.h),
        h: bh, w: bh * rnd(2, 4.5),
        d: depth,
        hot: Math.random() < 0.18,     // 約兩成方塊受熱時會轉成橘色
        a: rnd(0.05, 0.11) * (0.5 + depth * 0.5)
      });
    }
    draw(L);
  }

  function draw(L) {
    var c = L.ctx, h = L.heat;
    c.clearRect(0, 0, L.w, L.h);
    for (var i = 0; i < L.blocks.length; i++) {
      var b = L.blocks[i];
      if (b.hot && h > 0.02) {
        // 由灰轉橘：#8A8F96 → #FF6A1A
        var t = Math.min(1, h);
        var R = Math.round(138 + (255 - 138) * t), G = Math.round(143 + (106 - 143) * t), B = Math.round(150 + (26 - 150) * t);
        c.fillStyle = 'rgba(' + R + ',' + G + ',' + B + ',' + (b.a + 0.16 * t * b.d).toFixed(3) + ')';
      } else {
        c.fillStyle = 'rgba(138,143,150,' + (b.a + 0.04 * Math.min(1, h)).toFixed(3) + ')';
      }
      c.fillRect(b.x, b.y, b.w, b.h);
    }
  }

  var lastY = window.scrollY, vel = 0, running = false;

  function step() {
    var any = false;
    for (var i = 0; i < layers.length; i++) {
      var L = layers[i];
      if (!L.vis) continue;
      var dx = vel * L.dir * 0.9;
      for (var j = 0; j < L.blocks.length; j++) {
        var b = L.blocks[j];
        b.x += dx * b.d;
        if (b.x > L.w + 4) b.x = -b.w - rnd(0, 40);
        else if (b.x + b.w < -4) b.x = L.w + rnd(0, 40);
      }
      var target = Math.min(1, Math.abs(vel) / 18);
      L.heat += (target - L.heat) * 0.25;
      if (L.heat < 0.01) L.heat = 0;
      draw(L);
      if (L.heat > 0) any = true;
    }
    vel *= 0.78;                 // 停止捲動後很快減速停住
    if (Math.abs(vel) < 0.05) vel = 0;
    if (vel !== 0 || any) requestAnimationFrame(step);
    else running = false;
  }

  function onScroll() {
    var y = window.scrollY, dy = y - lastY;
    lastY = y;
    vel += dy * 0.35;
    if (vel > 40) vel = 40; else if (vel < -40) vel = -40;
    if (!running) { running = true; requestAnimationFrame(step); }
  }

  function init() {
    IDS.forEach(function (id, i) {
      var s = document.getElementById(id);
      if (s) seed(makeLayer(s, i));
    });
    if (!layers.length) return;
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        layers.forEach(function (L) { if (L.sec === e.target) L.vis = e.isIntersecting; });
      });
    });
    layers.forEach(function (L) { io.observe(L.sec); });
    window.addEventListener('scroll', onScroll, { passive: true });
    var t;
    window.addEventListener('resize', function () {
      clearTimeout(t);
      t = setTimeout(function () { layers.forEach(seed); }, 200);
    });
    // 區域內容（文章清單、速報）載入後高度會變，重新配置方塊
    if (window.ResizeObserver) {
      var ro = new ResizeObserver(function (es) {
        es.forEach(function (e) {
          layers.forEach(function (L) {
            if (L.sec === e.target && Math.abs(e.target.getBoundingClientRect().height - L.h) > 40) seed(L);
          });
        });
      });
      layers.forEach(function (L) { ro.observe(L.sec); });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
