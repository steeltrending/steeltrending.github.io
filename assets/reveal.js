/* 鋼鐵潮流首頁：01 每日速報、02 追蹤主題、03 關於 三個區域的區塊捲動流入。
   區塊的位置與透明度直接由捲動位置決定（不是計時動畫）：捲動時區塊由下方斜向流入定位，
   停止捲動就停在當下的位置；往回捲則反向退出。尊重「減少動態效果」設定。 */
(function () {
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var items = [];

  function collect() {
    var daily = document.getElementById('daily');
    var topics = document.getElementById('topics');
    var about = document.getElementById('about');
    function add(el, i, side) { if (el) items.push({ el: el, i: i, side: side }); }
    if (daily) {
      var dk = daily.children;                       // 標題、圖卡＋價格欄、按鈕列
      add(dk[0], 0, 0);
      var grid = dk[1];
      if (grid) for (var a = 0; a < grid.children.length; a++) add(grid.children[a], a, a % 2 ? 1 : -1);
      add(dk[2], 0, 0);
    }
    if (topics) {
      var tk = topics.children;
      add(tk[0], 0, 0);
      var tg = tk[1];
      if (tg) for (var b = 0; b < tg.children.length; b++) add(tg.children[b], b, 0);
    }
    if (about) {
      var inner = about.firstElementChild;
      if (inner) for (var c = 0; c < inner.children.length; c++) add(inner.children[c], c, c % 2 ? 1 : -1);
    }
    items.forEach(function (it) { it.el.style.willChange = 'transform, opacity'; });
  }

  function ease(t) { return 1 - Math.pow(1 - t, 3); }

  function update() {
    var vh = window.innerHeight;
    var range = vh * 0.45;                            // 區塊頂端從畫面底部上移這段距離內完成流入
    for (var k = 0; k < items.length; k++) {
      var it = items[k], el = it.el;
      // 先移除位移再量測，避免位移影響判斷
      var top = el.getBoundingClientRect().top - (it.dy || 0);
      // 同一列的方塊依欄位錯開，形成一塊接一塊流入的節奏
      var col = 0;
      if (it.side === 0 && it.i > 0) {
        var w = el.offsetWidth || 1, pw = el.parentElement ? el.parentElement.clientWidth : w;
        var cols = Math.max(1, Math.round(pw / w));
        col = it.i % cols;
      }
      var start = vh - col * vh * 0.06;
      var p = Math.max(0, Math.min(1, (start - top) / range));
      var e = ease(p);
      var dy = (1 - e) * 70;
      var dx = (1 - e) * 40 * it.side;
      it.dy = dy;
      el.style.transform = p >= 1 ? '' : 'translate(' + dx.toFixed(1) + 'px,' + dy.toFixed(1) + 'px)';
      el.style.opacity = p >= 1 ? '' : (0.08 + 0.92 * e).toFixed(3);
    }
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { ticking = false; update(); });
  }

  function init() {
    collect();
    if (!items.length) return;
    // 斜向流入時不讓區塊撐出橫向捲軸
    ['daily', 'topics', 'about'].forEach(function (id) {
      var s = document.getElementById(id);
      if (s) s.style.overflowX = 'clip';
    });
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
