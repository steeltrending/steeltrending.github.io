/* 鋼鐵潮流 文章語音朗讀（瀏覽器內建語音，Web Speech API）
 * - 在文章標題與署名下方加入朗讀列：播放／暫停、停止、語速、語音選擇
 * - 依段落朗讀標題、內文、清單與表格以外的文字；略過圖表、表格、「延伸閱讀」與「資料來源」
 * - 長段落切成短句逐句朗讀（避開 Chrome 長句中斷問題），正在朗讀的段落會標示
 * - 讀者選的語速與語音記在本機瀏覽器
 * 由 tools/article_tts.py 自動加到每篇文章（</body> 前），新文章不必手動處理。
 */
(function () {
  'use strict';
  var synth = window.speechSynthesis;
  var article = document.querySelector('article');
  if (!synth || !window.SpeechSynthesisUtterance || !article) return;

  // ---- 念法修正：讓單位、符號念得自然 ----
  var FIXES = [
    [/US\$\s*/g, '美元'],
    [/NT\$\s*/g, '新台幣'],
    [/USD\s*\/\s*(t|MT|噸)\b/gi, '美元每噸'],
    [/CNY\s*\/\s*(t|MT|噸)\b/gi, '人民幣每噸'],
    [/RMB\s*\/\s*(t|MT|噸)\b/gi, '人民幣每噸'],
    [/EUR\s*\/\s*(t|MT|噸)\b/gi, '歐元每噸'],
    [/元\s*\/\s*(公噸|噸|t)\b/g, '元每噸'],
    [/\/\s*(公噸|噸)/g, '每噸'],
    [/\s*\/\s*(年|月|日|季|週|小時)/g, '每$1'],
    [/(\d)\s*萬\s*t\b/g, '$1萬噸'],
    [/(\d)\s*(Mt|百萬噸)\b/g, '$1百萬噸'],
    [/(\d)\s*kt\b/g, '$1千噸'],
    [/(\d)\s*t\b/g, '$1噸'],
    [/(\d)\s*kg\b/gi, '$1公斤'],
    [/(\d)\s*GWh\b/g, '$1百萬度'],
    [/(\d)\s*MW\b/g, '$1百萬瓦'],
    [/62%\s*Fe/g, '62%品位'],
    [/\bHMS\s*1\s*&\s*2\b/g, 'HMS一號及二號'],
    [/\b(\d{1,3})\s*:\s*(\d{1,3})\b(?!\s*[:：]?\d)(?=\s*(?:CFR|比|配比|$|[，,。）)]))/g, '$1比$2'],
    [/\bCFR\b/g, '到岸價'],
    [/\bFOB\b/g, '離岸價'],
    [/\bYoY\b/gi, '年增'],
    [/\bMoM\b/gi, '月增'],
    [/\bQoQ\b/gi, '季增'],
    [/\bQ([1-4])\b/g, '第$1季'],
    [/([1-4])Q(\d{2})\b/g, '20$2年第$1季'],
    [/\bH([12])\b/g, function (m, n) { return n === '1' ? '上半年' : '下半年'; }],
    [/(\d)\s*[~～–—]\s*(\d)/g, '$1至$2'],
    [/\s*&\s*/g, '和'],
    [/[▲△]\s*/g, '上漲'],
    [/[▼▽]\s*/g, '下跌'],
    [/[「」『』《》〈〉【】]/g, ''],
    [/[（(]\s*[)）]/g, ''],
    [/\s*·\s*/g, '，'],
    [/\s*\/\s*/g, '，']
  ];
  function normalize(s) {
    s = s.replace(/\s+/g, ' ').trim();
    for (var i = 0; i < FIXES.length; i++) s = s.replace(FIXES[i][0], FIXES[i][1]);
    return s;
  }

  // ---- 收集要朗讀的段落 ----
  var SKIP_IN = 'figure,table,.tbl,.facts,.tl,.tlfig,.flow,.flowkey,.bars,.diag,.pies,.note,nav,script,style,.tts-bar';
  var STOP_HEADINGS = /^(延伸閱讀|資料來源|參考資料|來源)/;
  function collect() {
    var nodes = article.querySelectorAll('h1,h2,h3,p,li');
    var out = [], stop = false, h1 = article.querySelector('h1');
    for (var i = 0; i < nodes.length && !stop; i++) {
      var el = nodes[i];
      // 標題上方的欄目標籤（例如 CARBON NEUTRALITY · EU CBAM）不念
      if (h1 && el !== h1 && (h1.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_PRECEDING)) continue;
      if (el.closest(SKIP_IN)) continue;
      if (el.tagName === 'LI' && el.querySelector('p')) continue; // 由內層 p 朗讀
      var text = (el.innerText || el.textContent || '').trim();
      if (!text) continue;
      if (/^H[23]$/.test(el.tagName) && STOP_HEADINGS.test(text)) { stop = true; break; }
      if (el.tagName === 'P' && /^鋼鐵潮流工作室\s*·\s*發布/.test(text)) continue; // 署名
      out.push({ el: el, text: normalize(text) });
    }
    return out;
  }

  // 長段落切成短句；每句不超過約 120 字
  function splitSentences(text) {
    var parts = text.match(/[^。！？；!?;]+[。！？；!?;」』）)]*|[^。！？；!?;]+$/g) || [text];
    var out = [];
    parts.forEach(function (p) {
      p = p.trim();
      while (p.length > 120) {
        var cut = Math.max(p.lastIndexOf('，', 120), p.lastIndexOf('、', 120), p.lastIndexOf(',', 120));
        if (cut < 30) cut = 120;
        out.push(p.slice(0, cut + 1));
        p = p.slice(cut + 1).trim();
      }
      if (p) out.push(p);
    });
    return out;
  }

  // ---- 偏好設定（本機） ----
  function load(k, d) { try { var v = localStorage.getItem('tts-' + k); return v === null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem('tts-' + k, v); } catch (e) { /* 無痕模式等 */ } }

  // ---- 語音挑選：台灣國語優先 ----
  var voices = [];
  function score(v) {
    var s = 0, n = (v.name + ' ' + v.lang).toLowerCase();
    if (/zh[-_]tw|taiwan|國語（臺灣）|國語\(臺灣\)/.test(n)) s += 100;
    else if (/zh[-_]hk|cantonese|粵/.test(n)) s += 10;
    else if (/^zh|chinese|mandarin|普通话|中文/.test(n)) s += 40;
    if (/natural|online|neural|premium|enhanced|google/.test(n)) s += 20;
    if (/hsiaochen|hsiaoyu|meijia|美佳|yunjhe/.test(n)) s += 15;
    if (v.localService === false) s += 2;
    return s;
  }
  function refreshVoices() {
    voices = synth.getVoices().filter(function (v) { return /^zh|chinese|mandarin/i.test(v.lang + ' ' + v.name); })
      .sort(function (a, b) { return score(b) - score(a); });
    var sel = bar && bar.querySelector('.tts-voice');
    if (!sel) return;
    var want = load('voice', '');
    sel.innerHTML = '';
    voices.forEach(function (v, i) {
      var o = document.createElement('option');
      o.value = v.name; o.textContent = v.name.replace(/Microsoft |Google |\(.*?\)|Online|Natural/g, '').replace(/\s+-\s+.*$/, '').trim() + '（' + v.lang + '）';
      if (v.name === want || (!want && i === 0)) o.selected = true;
      sel.appendChild(o);
    });
    sel.parentElement.style.display = voices.length > 1 ? '' : 'none';
  }
  function currentVoice() {
    var sel = bar.querySelector('.tts-voice');
    var name = sel && sel.value;
    for (var i = 0; i < voices.length; i++) if (voices[i].name === name) return voices[i];
    return voices[0] || null;
  }

  // ---- 介面 ----
  var css = document.createElement('style');
  css.textContent =
    '.tts-bar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:14px 0 4px;padding:10px 12px;background:#15181B;border:1px solid #2A2F35;border-left:3px solid #FF6A1A;font-size:14px;color:#C9CDD2}' +
    '.tts-bar button{font:inherit;cursor:pointer;border:1px solid #3A3F46;background:#1C2024;color:#E8E6E1;padding:8px 14px;min-height:40px;display:inline-flex;align-items:center;gap:6px}' +
    '.tts-bar button:hover{border-color:#FF6A1A;color:#FF8A47}' +
    '.tts-bar button:focus-visible,.tts-bar select:focus-visible{outline:2px solid #FF6A1A;outline-offset:2px}' +
    '.tts-bar .tts-play{background:#FF6A1A;border-color:#FF6A1A;color:#0F1113;font-weight:700}' +
    '.tts-bar .tts-play:hover{background:#FF8A47;color:#0F1113}' +
    '.tts-bar .tts-stop[disabled]{opacity:.4;cursor:default}' +
    '.tts-bar label{display:inline-flex;align-items:center;gap:6px;color:#9AA0A6;font-size:13px}' +
    '.tts-bar select{font:inherit;font-size:13px;background:#1C2024;color:#E8E6E1;border:1px solid #3A3F46;padding:7px 8px;min-height:38px;max-width:180px}' +
    '.tts-bar .tts-st{margin-left:auto;font-family:"IBM Plex Mono",monospace;font-size:12px;color:#9AA0A6;white-space:nowrap}' +
    '.tts-on{background:rgba(255,106,26,.10);box-shadow:-10px 0 0 rgba(255,106,26,.10),10px 0 0 rgba(255,106,26,.10);border-radius:2px;transition:background .2s}' +
    'h2.tts-on{color:#FF8A47}' +
    '@media (max-width:640px){.tts-bar{gap:8px}.tts-bar .tts-st{margin-left:0;width:100%}.tts-bar select{max-width:140px}}' +
    '@media print{.tts-bar{display:none}}';
  document.head.appendChild(css);

  var blocks = collect();
  if (!blocks.length) return;
  var totalChars = blocks.reduce(function (n, b) { return n + b.text.length; }, 0);

  var bar = document.createElement('div');
  bar.className = 'tts-bar';
  bar.setAttribute('role', 'region');
  bar.setAttribute('aria-label', '語音朗讀');
  bar.innerHTML =
    '<button type="button" class="tts-play" aria-label="朗讀本文"><span aria-hidden="true">▶</span><span class="tts-lbl">朗讀本文</span></button>' +
    '<button type="button" class="tts-stop" disabled aria-label="停止朗讀"><span aria-hidden="true">■</span>停止</button>' +
    '<label>語速<select class="tts-rate"><option value="0.8">0.8×</option><option value="1">1.0×</option><option value="1.2">1.2×</option><option value="1.4">1.4×</option><option value="1.7">1.7×</option></select></label>' +
    '<label>語音<select class="tts-voice"></select></label>' +
    '<span class="tts-st" aria-live="polite"></span>';

  // 放在標題與署名下方
  var h1 = article.querySelector('h1');
  var anchor = h1 && h1.nextElementSibling && h1.nextElementSibling.tagName === 'P' ? h1.nextElementSibling : h1;
  if (anchor) anchor.insertAdjacentElement('afterend', bar); else article.insertBefore(bar, article.firstChild);

  var btnPlay = bar.querySelector('.tts-play'), lbl = bar.querySelector('.tts-lbl'), icon = btnPlay.firstChild;
  var btnStop = bar.querySelector('.tts-stop'), selRate = bar.querySelector('.tts-rate'), st = bar.querySelector('.tts-st');
  selRate.value = load('rate', '1');
  if (!selRate.value) selRate.value = '1';

  function minutes() { return Math.max(1, Math.round(totalChars / (260 * parseFloat(selRate.value || '1')))); }
  function idleStatus() { st.textContent = '約 ' + minutes() + ' 分鐘'; }
  idleStatus();

  refreshVoices();
  if (typeof synth.onvoiceschanged !== 'undefined') synth.addEventListener('voiceschanged', refreshVoices);

  // ---- 播放控制：以「段落 + 句」為位置，暫停時記住位置 ----
  var state = 'idle', bi = 0, si = 0, sentences = [], token = 0;
  function mark(i) {
    blocks.forEach(function (b, j) { b.el.classList.toggle('tts-on', j === i); });
    if (i >= 0) {
      var r = blocks[i].el.getBoundingClientRect();
      if (r.top < 70 || r.bottom > window.innerHeight - 20) blocks[i].el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }
  }
  function setUI() {
    var playing = state === 'playing';
    icon.textContent = playing ? '❚❚' : '▶';
    lbl.textContent = playing ? '暫停' : (state === 'paused' ? '繼續朗讀' : '朗讀本文');
    btnPlay.setAttribute('aria-label', lbl.textContent);
    btnStop.disabled = state === 'idle';
    if (state === 'idle') idleStatus();
    else st.textContent = '第 ' + (bi + 1) + ' / ' + blocks.length + ' 段';
  }
  function speakNext(my) {
    if (my !== token || state !== 'playing') return;
    if (si >= sentences.length) {
      bi++; si = 0;
      if (bi >= blocks.length) { stop(); st.textContent = '朗讀完畢'; return; }
      sentences = splitSentences(blocks[bi].text);
    }
    mark(bi); setUI();
    var u = new SpeechSynthesisUtterance(sentences[si]);
    var v = currentVoice();
    if (v) { u.voice = v; u.lang = v.lang; } else u.lang = 'zh-TW';
    u.rate = parseFloat(selRate.value || '1');
    var done = false;
    u.onend = function () { if (done) return; done = true; si++; speakNext(my); };
    u.onerror = function (e) {
      if (done) return; done = true;
      if (e && (e.error === 'interrupted' || e.error === 'canceled')) return;
      si++; speakNext(my); // 單句失敗就跳過，不中斷整篇
    };
    synth.speak(u);
  }
  function play() {
    if (state === 'idle') { bi = 0; si = 0; sentences = splitSentences(blocks[0].text); }
    state = 'playing'; token++;
    synth.cancel();
    setUI();
    speakNext(token);
  }
  function pause() { state = 'paused'; token++; synth.cancel(); setUI(); }
  function stop() { state = 'idle'; token++; synth.cancel(); bi = 0; si = 0; mark(-1); setUI(); }

  btnPlay.addEventListener('click', function () { state === 'playing' ? pause() : play(); });
  btnStop.addEventListener('click', stop);
  selRate.addEventListener('change', function () {
    save('rate', selRate.value);
    if (state === 'playing') play(); else if (state === 'idle') idleStatus();
  });
  bar.querySelector('.tts-voice').addEventListener('change', function () {
    save('voice', this.value);
    if (state === 'playing') play();
  });
  // 點段落可從該段開始（朗讀中或暫停時）
  blocks.forEach(function (b, j) {
    b.el.addEventListener('dblclick', function () {
      if (state === 'idle') return;
      bi = j; si = 0; sentences = splitSentences(b.text); play();
    });
  });
  window.addEventListener('pagehide', function () { token++; synth.cancel(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && state !== 'idle') stop();
  });
})();
