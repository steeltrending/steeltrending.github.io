/* 鋼鐵潮流 亮色／暗色主題切換
 *
 * - 全站預設暗色；右上角（訂閱頻道按鈕下方）的浮動圓鈕可切換成亮色，再按一次恢復暗色。
 * - 作法：亮色主題 = 整頁反相並轉回色相（深底變暖白、淺字變深字、橘色仍是橘色），
 *   圖片、影片、嵌入的 YouTube 與有背景照片的區塊再反相一次，維持原樣。
 *   全站顏色大多寫在各頁的 inline style，用這個方式不必逐頁改色，新頁面自動適用。
 * - 選擇記在讀者瀏覽器（localStorage），換頁、重開、分頁之間都會保持；沒有記錄時一律是暗色。
 * - 這支檔案放在 <head> 內同步載入（不加 defer），才能在畫面第一次繪製前套上主題，避免閃一下暗色。
 * 由 tools/page_theme.py 自動加到每個頁面（</head> 前），新頁面不必手動處理。
 */
(function () {
  'use strict';
  var KEY = 'st-theme';
  var root = document.documentElement;
  var theme = 'dark';
  var btn = null;

  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v) { try { localStorage.setItem(KEY, v); } catch (e) { /* 無痕模式等：本頁仍可切換，只是不記住 */ } }

  // ---- 樣式 ----
  var FLIP = 'invert(1) hue-rotate(180deg)';
  var L = 'html[data-theme=light]';
  var ORANGE_FILLS = [
    'a[style*="background:#FF6A1A" i]', 'a[style*="background: #FF6A1A" i]', 'a[style*="background: rgb(255, 106, 26)"]',
    'button[style*="background:#FF6A1A" i]', 'button[style*="background: rgb(255, 106, 26)"]',
    '.chip[aria-pressed="true"]', '.chip[aria-current="true"]', '.chip[aria-selected="true"]', '.tab[aria-selected="true"]',
    '.btn.primary', '.tts-bar .tts-play'
  ];
  var css =
    L + '{filter:' + FLIP + '}' +
    // 圖片、影片、嵌入內容：再反相一次，回到原樣
    L + ' img,' + L + ' video,' + L + ' iframe,' + L + ' .st-keep{filter:' + FLIP + '}' +
    // 已還原的區塊裡面不要再重複還原
    L + ' .st-keep img,' + L + ' .st-keep video,' + L + ' .st-keep iframe{filter:none}' +
    // 橘底的按鈕與選中的分頁：反相後深字配橘底對比不足（約 2.7:1），把底色加深到約 4.5:1 以上。
    // inline style 的寫法有 #FF6A1A 與 rgb(255, 106, 26) 兩種（hover.js 載入後會被瀏覽器改寫成 rgb）。
    ORANGE_FILLS.map(function (x) { return L + ' ' + x; }).join(',') + '{background:#FF8F5A !important}' +
    // 浮動按鈕
    '.st-theme-btn{position:fixed;z-index:60;top:88px;right:16px;width:44px;height:44px;box-sizing:border-box;padding:0;' +
    'display:flex;align-items:center;justify-content:center;border-radius:50%;border:1px solid #3A3F46;background:#1C2024;color:#FF8A47;' +
    'cursor:pointer;box-shadow:0 4px 14px rgba(0,0,0,.45);-webkit-tap-highlight-color:transparent;touch-action:manipulation}' +
    '.st-theme-btn:hover{border-color:#FF6A1A;color:#FFB07F}' +
    '.st-theme-btn:focus-visible{outline:2px solid #FF6A1A;outline-offset:3px}' +
    '.st-theme-btn svg{width:22px;height:22px;display:block;pointer-events:none}' +
    '.st-theme-btn[hidden]{display:none}' +
    '@media print{.st-theme-btn{display:none}}';
  var style = document.createElement('style');
  style.id = 'st-theme-css';
  style.textContent = css;
  (document.head || root).appendChild(style);

  // ---- 套用主題 ----
  var SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';

  function syncMeta() {
    var m = document.querySelector('meta[name="theme-color"]');
    if (!m && document.head) { m = document.createElement('meta'); m.name = 'theme-color'; document.head.appendChild(m); }
    if (m) m.content = theme === 'light' ? '#EDEFF1' : '#0F1113';
  }
  function syncButton() {
    if (!btn) return;
    var light = theme === 'light';
    btn.innerHTML = light ? MOON : SUN; // 顯示「按下去會變成」的樣子
    btn.setAttribute('aria-pressed', light ? 'true' : 'false');
    btn.title = light ? '切換為暗色主題' : '切換為亮色主題';
  }
  function apply(t) {
    theme = t === 'light' ? 'light' : 'dark';
    if (theme === 'light') root.setAttribute('data-theme', 'light'); else root.removeAttribute('data-theme');
    syncMeta();
    syncButton();
  }
  apply(read()); // 立刻套用，早於第一次繪製

  // ---- 按鈕位置：右上角、在「訂閱頻道」按鈕正下方；手機版頁首排不下時改放最右上角 ----
  function place() {
    if (!btn) return;
    var vw = root.clientWidth, top = null, right = null;
    var link = document.querySelector('header a[href*="youtube.com/@steeltrending"]');
    if (link) {
      var r = link.getBoundingClientRect();
      var absTop = r.top + (window.pageYOffset || 0);
      if (r.width > 0 && absTop < 120) { top = Math.round(absTop + r.height + 12); right = Math.max(12, Math.round(vw - r.right)); }
    }
    if (top === null) {
      if (vw >= 900) { top = 88; right = Math.max(16, Math.round((vw - 1200) / 2 + 24)); }
      else { top = 12; right = 12; }
    }
    btn.style.top = top + 'px';
    btn.style.right = right + 'px';
  }

  function init() {
    // 有背景照片的區塊：整塊維持原樣
    var withBg = document.querySelectorAll('[style*="url("]');
    for (var i = 0; i < withBg.length; i++) withBg[i].classList.add('st-keep');

    btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'st-theme-btn';
    btn.setAttribute('aria-label', '亮色主題');
    btn.addEventListener('click', function () {
      var next = theme === 'light' ? 'dark' : 'light';
      write(next);
      apply(next);
    });
    document.body.appendChild(btn);
    syncButton();
    syncMeta();
    place();

    var raf = 0;
    function later() { if (raf) return; raf = requestAnimationFrame(function () { raf = 0; place(); }); }
    window.addEventListener('resize', later);
    window.addEventListener('load', later);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(later);
    var header = document.querySelector('header');
    if (header && window.ResizeObserver) new ResizeObserver(later).observe(header);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  // 其他分頁、上一頁（bfcache）切換後保持一致
  window.addEventListener('storage', function (e) { if (e.key === KEY) apply(e.newValue); });
  window.addEventListener('pageshow', function (e) { if (e.persisted) apply(read()); });
})();
