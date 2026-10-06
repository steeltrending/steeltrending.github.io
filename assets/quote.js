/* 鋼語：首頁標題旁每次載入隨機一則與鋼鐵、冶煉、鍛造相關的詩句或格言。
   每次重新整理隨機換一則（不與上一次重複）；新增條目直接加在 Q 陣列即可。
   t：中文（外文則為譯文）；o：外文原文（可省略）；by：出處（詩句須含作品與作者） */
(function () {
  var Q = [
    { t: '鐵從地裡挖出，銅從石中熔化。', by: '《聖經・約伯記》28:2（和合本）' },
    { t: '那地的石頭是鐵，山內可以挖銅。', by: '《聖經・申命記》8:9（和合本）' },
    { t: '鐵器鈍了，若不將刃磨快，就必多費氣力；但得智慧指教，便有益處。', by: '《聖經・傳道書》10:10（和合本）' },
    { t: '他們要將刀打成犁頭，把槍打成鐮刀。', by: '《聖經・以賽亞書》2:4（和合本）' },
    { t: '鐵磨鐵，磨出刃來；朋友相感，也是如此。', by: '《聖經・箴言》27:17（和合本）' },
    { t: '有所嘗試，有所完成，便換得一夜安眠。', o: 'Something attempted, something done, / Has earned a night’s repose.', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '我們的命運，正是在生命熊熊的鍛爐上鍛成；每個熾熱的行動與念頭，都在鳴響的鐵砧上成形。', o: 'Thus at the flaming forge of life / Our fortunes must be wrought; / Thus on its sounding anvil shaped / Each burning deed and thought!', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '是什麼樣的鐵鎚？什麼樣的鎖鏈？你的頭腦在哪座熔爐裡鍛成？', o: 'What the hammer? what the chain? / In what furnace was thy brain?', by: '布萊克〈老虎〉（The Tyger）' },
    { t: '石牆築不成牢獄，鐵欄也圍不成籠。', o: 'Stone walls do not a prison make, / Nor iron bars a cage.', by: '洛夫萊斯〈獄中致艾西亞〉（To Althea, from Prison）' },
    { t: '石砌的高塔、黃銅的城牆、不透氣的地牢、堅固的鐵鍊，都困不住堅強的精神。', o: 'Nor stony tower, nor walls of beaten brass, / Nor airless dungeon, nor strong links of iron, / Can be retentive to the strength of spirit.', by: '莎士比亞《凱撒大帝》第一幕第三景' },
    { t: '你所交的朋友，若已經過考驗，就用鋼箍把他們緊緊扣在心上。', o: 'Those friends thou hast, and their adoption tried, / Grapple them unto thy soul with hoops of steel.', by: '莎士比亞《哈姆雷特》第一幕第三景' },
    { t: '你必須……做鐵砧，或做鐵鎚。', o: 'Du mußt … Amboß oder Hammer sein.', by: '歌德〈科普特之歌〉（Kophtisches Lied）' },
    { t: '然而鐵——冰冷的鐵——才是萬物之主。', o: 'But Iron—Cold Iron—is master of them all.', by: '吉卜林〈冷鐵〉（Cold Iron）' },
    { t: '相信你自己：每一顆心都隨著那根鐵弦震動。', o: 'Trust thyself: every heart vibrates to that iron string.', by: '愛默生〈自立〉（Self-Reliance）' },
    { t: '人是使用工具的動物……沒有工具，他一無所是；有了工具，他無所不能。', o: 'Man is a Tool-using Animal… Without Tools he is nothing, with Tools he is all.', by: '卡萊爾《衣裳哲學》（Sartor Resartus）' },
    { t: '堅不可摧的岩石不夠堅固，鋼鐵的城門也不夠牢靠，終究都會被時間侵蝕。', o: 'When rocks impregnable are not so stout, / Nor gates of steel so strong, but Time decays?', by: '莎士比亞《十四行詩》第 65 首' },
    { t: '除非我的神經是黃銅或鍛打過的鋼，否則只能在自己的過錯面前低頭。', o: 'Needs must I under my transgression bow, / Unless my nerves were brass or hammer’d steel.', by: '莎士比亞《十四行詩》第 120 首' },
    { t: '理直者有三重盔甲；良心不正的人，即使全身包在鋼裡，也形同赤裸。', o: 'Thrice is he arm’d that hath his quarrel just, / And he but naked, though lock’d up in steel, / Whose conscience with injustice is corrupted.', by: '莎士比亞《亨利六世》中篇 第三幕第二景' },
    { t: '如鋼一般真，如刃一般直，偉大的工匠造就了我的伴侶。', o: 'Steel-true and blade-straight, / The great artificer / Made my mate.', by: '史蒂文生〈我的妻子〉（My Wife）' },
    { t: '我們從礦床與礦坑裡被取出，在熔爐與坩堝中熔化；我們被鑄造、鍛打，依設計成形。', o: 'We were taken from the ore-bed and the mine, / We were melted in the furnace and the pit— / We were cast and wrought and hammered to design.', by: '吉卜林〈機器的祕密〉（The Secret of the Machines）' },
    { t: '腳下穿著鋼，我們在光滑的冰面上嘶嘶滑行。', o: 'All shod with steel, / We hiss’d along the polish’d ice.', by: '華茲華斯《序曲》第一卷（The Prelude）' },
    { t: '像鋼一樣真。（形容忠誠可靠）', o: 'True as steel.', by: '英語俗語' },
    { t: '當代的重大問題，不是靠演說與多數決來解決……而是靠鐵與血。', o: 'Nicht durch Reden und Majoritätsbeschlüsse werden die großen Fragen der Zeit entschieden … sondern durch Eisen und Blut.', by: '俾斯麥，1862 年普魯士下議院預算委員會演說' },
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
