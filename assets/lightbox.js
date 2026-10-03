/* 鋼鐵潮流 圖卡放大檢視（首頁與歷史圖卡共用）
   window.SteelLightbox.open(list, index)
   list: [{ src: 原圖網址, title: 標題文字 }] */
(function () {
  var css = '' +
    '.lb{position:fixed;inset:0;z-index:1000;background:rgba(8,9,11,.94);display:flex;flex-direction:column;color:#E8E6E1;font-family:"Noto Sans TC","PingFang TC",sans-serif}' +
    '.lb[hidden]{display:none}' +
    '.lb-bar{display:flex;align-items:center;gap:8px;padding:8px 12px;border-bottom:1px solid #2A2F35;background:#0F1113;flex-wrap:wrap}' +
    '.lb-title{flex:1;min-width:0;font-family:"IBM Plex Mono",monospace;font-size:13px;letter-spacing:.14em;color:#C9CDD2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' +
    '.lb-btn{background:transparent;border:1px solid #3A3F46;color:#E8E6E1;font:inherit;font-size:14px;min-height:40px;min-width:40px;padding:0 12px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}' +
    '.lb-btn:hover{border-color:#FF6A1A;color:#FFB07F}' +
    '.lb-btn[disabled]{opacity:.35;cursor:default}' +
    '.lb-btn[hidden]{display:none}' +
    '.lb-stage{flex:1;overflow:auto;display:flex;align-items:center;justify-content:center;-webkit-overflow-scrolling:touch}' +
    '.lb-stage img{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;cursor:zoom-in}' +
    '.lb.zoom .lb-stage{display:block}' +
    '.lb.zoom .lb-stage img{max-width:none;max-height:none;margin:0 auto;cursor:zoom-out}' +
    '.lb-hint{padding:6px 12px;font-size:12px;color:#9AA0A6;text-align:center;border-top:1px solid #2A2F35;background:#0F1113}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  var root = document.createElement('div');
  root.className = 'lb'; root.hidden = true;
  root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', '圖卡放大檢視');
  root.innerHTML =
    '<div class="lb-bar">' +
      '<span class="lb-title"></span>' +
      '<button type="button" class="lb-btn lb-prev" aria-label="上一張（較新）">‹</button>' +
      '<button type="button" class="lb-btn lb-next" aria-label="下一張（較舊）">›</button>' +
      '<button type="button" class="lb-btn lb-zoom">放大</button>' +
      '<a class="lb-btn lb-open" target="_blank" rel="noopener">原圖</a>' +
      '<button type="button" class="lb-btn lb-close" aria-label="關閉">✕</button>' +
    '</div>' +
    '<div class="lb-stage"><img alt=""></div>' +
    '<div class="lb-hint">點圖片切換放大／縮小　·　Esc 關閉　·　← → 切換圖卡</div>';
  document.body.appendChild(root);

  var img = root.querySelector('img');
  var stage = root.querySelector('.lb-stage');
  var title = root.querySelector('.lb-title');
  var prev = root.querySelector('.lb-prev');
  var next = root.querySelector('.lb-next');
  var zoomBtn = root.querySelector('.lb-zoom');
  var openA = root.querySelector('.lb-open');
  var list = [], idx = 0, lastFocus = null;

  function setZoom(on, cx, cy) {
    var fx = 0.5, fy = 0;
    if (on && cx != null) {
      var r = img.getBoundingClientRect();
      fx = (cx - r.left) / r.width; fy = (cy - r.top) / r.height;
    }
    root.classList.toggle('zoom', on);
    zoomBtn.textContent = on ? '縮小' : '放大';
    if (on) {
      stage.scrollLeft = Math.max(0, img.offsetWidth * fx - stage.clientWidth / 2);
      stage.scrollTop = Math.max(0, img.offsetHeight * fy - stage.clientHeight / 2);
    }
  }
  function show(i) {
    idx = i;
    var it = list[i];
    setZoom(false);
    img.src = it.src; img.alt = it.title || '速報圖卡';
    title.textContent = it.title || '';
    openA.href = it.src;
    var multi = list.length > 1;
    prev.hidden = next.hidden = !multi;
    prev.disabled = i <= 0; next.disabled = i >= list.length - 1;
  }
  function close() {
    root.hidden = true; document.body.style.overflow = '';
    img.removeAttribute('src');
    if (lastFocus) lastFocus.focus();
  }

  img.addEventListener('click', function (e) { setZoom(!root.classList.contains('zoom'), e.clientX, e.clientY); });
  zoomBtn.addEventListener('click', function () { setZoom(!root.classList.contains('zoom')); });
  prev.addEventListener('click', function () { if (idx > 0) show(idx - 1); });
  next.addEventListener('click', function () { if (idx < list.length - 1) show(idx + 1); });
  root.querySelector('.lb-close').addEventListener('click', close);
  stage.addEventListener('click', function (e) { if (e.target === stage) close(); });
  document.addEventListener('keydown', function (e) {
    if (root.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft' && idx > 0) show(idx - 1);
    else if (e.key === 'ArrowRight' && idx < list.length - 1) show(idx + 1);
  });

  window.SteelLightbox = {
    open: function (l, i) {
      list = l; lastFocus = document.activeElement;
      root.hidden = false; document.body.style.overflow = 'hidden';
      show(i || 0);
      root.querySelector('.lb-close').focus();
    }
  };
})();
