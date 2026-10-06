/* 鋼鐵潮流：全站超連結滑鼠移入效果——文字放大並變橘色。
   - 一般文字連結：變橘色（#FF6A1A）並放大。
   - 有底色的按鈕或色塊（訂閱鈕、熱力圖磚塊等）與圖片連結：只放大，不改文字顏色，避免橘字疊在橘底上看不見。
   - 跨行的長連結：只變色不放大，避免折行文字變形。
   - 只在有滑鼠的裝置生效（觸控螢幕不受影響），並尊重「減少動態效果」設定。 */
(function () {
  var css =
    '@media (hover:hover){' +
    'a.lk,a.lkb{transition:color .18s ease,transform .18s ease;transform-origin:center}' +
    'a.lk.row{transform-origin:left center}' +
    'a.lk:hover{color:#FF6A1A !important}' +
    'a.lk.sc:hover,a.lkb:hover,a.lk.row:hover{transform:scale(var(--hs,1.06))}' +
    '}' +
    '@media (prefers-reduced-motion:reduce){a.lk:hover,a.lkb:hover{transform:none !important}}';
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  // 放大幅度隨連結寬度遞減：短連結放大約 6%，長連結兩側各最多外擴約 6px，避免蓋到旁邊文字
  function setScale(a, cap) {
    var w = a.getBoundingClientRect().width || 1;
    var k = Math.min(cap || 0.06, 12 / w);
    a.style.setProperty('--hs', (1 + Math.max(k, 0.015)).toFixed(3));
  }

  function tag(a) {
    if (a.dataset.hov) return;
    a.dataset.hov = '1';
    var cs = getComputedStyle(a);
    var bg = cs.backgroundColor;
    var hasBg = bg && bg !== 'transparent' && !/rgba\(0, 0, 0, 0\)/.test(bg);
    var hasImg = !!a.querySelector('img');
    if (hasBg || hasImg) {
      a.classList.add('lkb');
      if (cs.display === 'inline') a.style.display = 'inline-block';
      setScale(a);
      return;
    }
    a.classList.add('lk');
    if (cs.display === 'inline') {
      // 單行的行內連結改為 inline-block 才能放大；跨行的長連結只變色
      if (a.getClientRects().length === 1) {
        a.style.display = 'inline-block';
        a.classList.add('sc');
        setScale(a);
      }
    } else {
      // 區塊或整列連結（文章清單、導覽列等）：寬度大的放大幅度小一點
      var w = a.getBoundingClientRect().width;
      a.classList.add(w > 360 ? 'row' : 'sc');
      setScale(a, w > 360 ? 0.025 : 0.06);
    }
  }

  function scan(root) {
    if (root.tagName === 'A') tag(root);
    if (root.querySelectorAll) root.querySelectorAll('a[href]').forEach(tag);
  }

  function init() {
    scan(document.body);
    new MutationObserver(function (ms) {
      ms.forEach(function (m) {
        m.addedNodes.forEach(function (n) { if (n.nodeType === 1) scan(n); });
      });
    }).observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
