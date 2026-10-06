/* 鋼語：首頁標題旁每次載入隨機一則與鋼鐵、冶煉、鍛造相關的詩句或格言。
   每次重新整理隨機換一則（不與上一次重複）；新增條目直接加在 Q 陣列即可。
   t：中文（外文則為譯文）；o：外文原文（可省略）；by：出處（詩句須含作品與作者） */
(function () {
  var Q = [
    { t: '爐火照天地，紅星亂紫煙。赧郎明月夜，歌曲動寒川。', by: '李白〈秋浦歌〉其十四' },
    { t: '何意百煉剛，化為繞指柔。', by: '劉琨〈重贈盧諶〉' },
    { t: '十年磨一劍，霜刃未曾試。今日把示君，誰有不平事？', by: '賈島〈劍客〉' },
    { t: '試玉要燒三日滿，辨材須待七年期。', by: '白居易〈放言五首〉其三' },
    { t: '千錘萬鑿出深山，烈火焚燒若等閒。粉骨碎身渾不怕，要留清白在人間。', by: '于謙〈石灰吟〉' },
    { t: '金戈鐵馬，氣吞萬里如虎。', by: '辛棄疾〈永遇樂・京口北固亭懷古〉' },
    { t: '夜闌臥聽風吹雨，鐵馬冰河入夢來。', by: '陸游〈十一月四日風雨大作〉其二' },
    { t: '男兒何不帶吳鉤，收取關山五十州。', by: '李賀〈南園十三首〉其五' },
    { t: '故木受繩則直，金就礪則利。', by: '荀子《荀子・勸學》' },
    { t: '鍥而舍之，朽木不折；鍥而不舍，金石可鏤。', by: '荀子《荀子・勸學》' },
    { t: '天有時，地有氣，材有美，工有巧，合此四者，然後可以為良。', by: '《周禮・考工記》' },
    { t: '精誠所加，金石為開。', by: '范曄《後漢書・廣陵思王荊傳》' },
    { t: '寶劍鋒從磨礪出，梅花香自苦寒來。', by: '《警世賢文》' },
    { t: '鐵肩擔道義，辣手著文章。', by: '楊繼盛（明代諫臣）' },
    { t: '他們要將刀打成犁頭，把槍打成鐮刀。', by: '《聖經・以賽亞書》2:4（和合本）' },
    { t: '鐵磨鐵，磨出刃來；朋友相感，也是如此。', by: '《聖經・箴言》27:17（和合本）' },
    { t: '當代的重大問題，不是靠演說與多數決來解決……而是靠鐵與血。', o: 'Nicht durch Reden und Majoritätsbeschlüsse werden die großen Fragen der Zeit entschieden … sondern durch Eisen und Blut.', by: '俾斯麥，1862 年普魯士下議院預算委員會演說' },
    { t: '你所交的朋友，若已經過考驗，就用鋼箍把他們緊緊扣在心上。', o: 'Those friends thou hast, and their adoption tried, / Grapple them unto thy soul with hoops of steel.', by: '莎士比亞《哈姆雷特》第一幕第三景' },
    { t: '有所嘗試，有所完成，便換得一夜安眠。', o: 'Something attempted, something done, / Has earned a night’s repose.', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '然而鐵——冰冷的鐵——才是萬物之主。', o: 'But Iron—Cold Iron—is master of them all.', by: '吉卜林〈冷鐵〉（Cold Iron）' },
    { t: '如此富有而死的人，死得可恥。', o: 'The man who dies thus rich dies disgraced.', by: '鋼鐵大王卡內基《財富的福音》（The Gospel of Wealth）' },
    { t: '趁熱打鐵。', o: 'Strike while the iron is hot.', by: '英語諺語' }
  ];
  var el = document.getElementById('steel-quote');
  if (!el) return;
  // 每次載入隨機挑一則，並避開上一次看到的那則
  var last = -1;
  try { last = parseInt(sessionStorage.getItem('sq-last'), 10); } catch (e) {}
  var i = Math.floor(Math.random() * Q.length);
  if (Q.length > 1 && i === last) i = (i + 1 + Math.floor(Math.random() * (Q.length - 1))) % Q.length;
  try { sessionStorage.setItem('sq-last', String(i)); } catch (e) {}
  var q = Q[i];
  el.querySelector('.sq-t').textContent = '「' + q.t + '」';
  var o = el.querySelector('.sq-o');
  if (q.o) { o.textContent = q.o; o.hidden = false; } else { o.hidden = true; }
  el.querySelector('.sq-by').textContent = '— ' + q.by;
  el.hidden = false;
})();
