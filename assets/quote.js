/* 鋼語：首頁標題旁每次載入隨機一則與鋼鐵、冶煉、鍛造、工藝相關的詩句、格言與俗諺（不收聖經）。
   每次重新整理隨機換一則（不與上一次重複）；新增條目直接加在 Q 陣列即可。
   t：中文（外文則為譯文）；o：外文原文（可省略）；by：出處（詩句須含作品與作者） */
(function () {
  var Q = [
    // —— 西方詩文 ——
    { t: '有所嘗試，有所完成，便換得一夜安眠。', o: 'Something attempted, something done, / Has earned a night’s repose.', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '我們的命運，正是在生命熊熊的鍛爐上鍛成；每個熾熱的行動與念頭，都在鳴響的鐵砧上成形。', o: 'Thus at the flaming forge of life / Our fortunes must be wrought; / Thus on its sounding anvil shaped / Each burning deed and thought!', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '在枝葉繁茂的栗樹下，矗立著村裡的鐵匠鋪；鐵匠是個魁梧的漢子，有一雙粗大結實的手。', o: 'Under a spreading chestnut-tree / The village smithy stands; / The smith, a mighty man is he, / With large and sinewy hands.', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '他的額頭沾滿誠實的汗水，憑本事賺取所得。', o: 'His brow is wet with honest sweat, / He earns whate’er he can.', by: '朗費羅〈鄉村鐵匠〉（The Village Blacksmith）' },
    { t: '是什麼樣的鐵鎚？什麼樣的鎖鏈？你的頭腦在哪座熔爐裡鍛成？', o: 'What the hammer? what the chain? / In what furnace was thy brain?', by: '布萊克〈老虎〉（The Tyger）' },
    { t: '石牆築不成牢獄，鐵欄也圍不成籠。', o: 'Stone walls do not a prison make, / Nor iron bars a cage.', by: '洛夫萊斯〈獄中致艾西亞〉（To Althea, from Prison）' },
    { t: '石砌的高塔、黃銅的城牆、不透氣的地牢、堅固的鐵鍊，都困不住堅強的精神。', o: 'Nor stony tower, nor walls of beaten brass, / Nor airless dungeon, nor strong links of iron, / Can be retentive to the strength of spirit.', by: '莎士比亞《凱撒大帝》第一幕第三景' },
    { t: '你所交的朋友，若已經過考驗，就用鋼箍把他們緊緊扣在心上。', o: 'Those friends thou hast, and their adoption tried, / Grapple them unto thy soul with hoops of steel.', by: '莎士比亞《哈姆雷特》第一幕第三景' },
    { t: '堅不可摧的岩石不夠堅固，鋼鐵的城門也不夠牢靠，終究都會被時間侵蝕。', o: 'When rocks impregnable are not so stout, / Nor gates of steel so strong, but Time decays?', by: '莎士比亞《十四行詩》第 65 首' },
    { t: '除非我的神經是黃銅或鍛打過的鋼，否則只能在自己的過錯面前低頭。', o: 'Needs must I under my transgression bow, / Unless my nerves were brass or hammer’d steel.', by: '莎士比亞《十四行詩》第 120 首' },
    { t: '理直者有三重盔甲；良心不正的人，即使全身包在鋼裡，也形同赤裸。', o: 'Thrice is he arm’d that hath his quarrel just, / And he but naked, though lock’d up in steel, / Whose conscience with injustice is corrupted.', by: '莎士比亞《亨利六世》中篇 第三幕第二景' },
    { t: '燧石裡的火，不敲擊就不會顯現。', o: 'The fire i’ the flint / Shows not till it be struck.', by: '莎士比亞《雅典的泰門》第一幕第一景' },
    { t: '別為敵人把熔爐燒得太熱，以免燙傷了自己。', o: 'Heat not a furnace for your foe so hot / That it do singe yourself.', by: '莎士比亞《亨利八世》第一幕第一景' },
    { t: '別驚訝財富生長在地獄；那片土壤最配得上這珍貴的禍根。', o: 'Let none admire / That riches grow in Hell; that soil may best / Deserve the precious bane.', by: '米爾頓《失樂園》第一卷' },
    { t: '你必須……做鐵砧，或做鐵鎚。', o: 'Du mußt … Amboß oder Hammer sein.', by: '歌德〈科普特之歌〉（Kophtisches Lied）' },
    { t: '牢牢砌在土裡，立著燒成的泥模；今天，鐘必須鑄成。', o: 'Fest gemauert in der Erden / Steht die Form, aus Lehm gebrannt. / Heute muß die Glocke werden.', by: '席勒〈大鐘之歌〉（Das Lied von der Glocke）' },
    { t: '然而鐵——冰冷的鐵——才是萬物之主。', o: 'But Iron—Cold Iron—is master of them all.', by: '吉卜林〈冷鐵〉（Cold Iron）' },
    { t: '金子給女主人，銀子給女僕，銅給精於手藝的工匠。', o: 'Gold is for the mistress—silver for the maid— / Copper for the craftsman cunning at his trade.', by: '吉卜林〈冷鐵〉（Cold Iron）' },
    { t: '我們從礦床與礦坑裡被取出，在熔爐與坩堝中熔化；我們被鑄造、鍛打，依設計成形。', o: 'We were taken from the ore-bed and the mine, / We were melted in the furnace and the pit— / We were cast and wrought and hammered to design.', by: '吉卜林〈機器的祕密〉（The Secret of the Machines）' },
    { t: '千百年來，承受衝擊、緩和震盪，始終是他們的職責。', o: 'It is their care in all the ages to take the buffet and cushion the shock.', by: '吉卜林〈瑪大的兒子們〉（The Sons of Martha），獻給工程師的詩' },
    { t: '如鋼一般真，如刃一般直，偉大的工匠造就了我的伴侶。', o: 'Steel-true and blade-straight, / The great artificer / Made my mate.', by: '史蒂文生〈我的妻子〉（My Wife）' },
    { t: '腳下穿著鋼，我們在光滑的冰面上嘶嘶滑行。', o: 'All shod with steel, / We hiss’d along the polish’d ice.', by: '華茲華斯《序曲》第一卷（The Prelude）' },
    { t: '讓偉大的世界沿著變革那鏗鏘的軌道，永遠向前飛轉。', o: 'Let the great world spin for ever down the ringing grooves of change.', by: '丁尼生〈洛克斯利廳〉（Locksley Hall）' },
    { t: '形狀優美、赤裸、蒼白的利器，斧頭從大地母親的腹中取出。', o: 'Weapon shapely, naked, wan, / Head from the mother’s bowels drawn.', by: '惠特曼〈闊斧之歌〉（Song of the Broad-Axe）' },
    { t: '現代的典型——動力與運動的象徵——大陸的脈搏。', o: 'Type of the modern—emblem of motion and power—pulse of the continent.', by: '惠特曼〈冬日的火車頭〉（To a Locomotive in Winter）' },
    { t: '世界的屠豬場，工具製造者，小麥堆疊者，鐵路的玩家。', o: 'Hog Butcher for the World, / Tool Maker, Stacker of Wheat, / Player with Railroads.', by: '桑德堡〈芝加哥〉（Chicago）' },
    { t: '一根鋼條——它的核心只是煙，煙和一個人的血。', o: 'A bar of steel—it is only / Smoke at the heart of it, smoke and the blood of a man.', by: '桑德堡〈煙與鋼〉（Smoke and Steel）' },
    { t: '如今真正是黑鐵的世代，人們白日不得停歇於勞苦與憂患。', o: 'For now truly is a race of iron, and men never rest from labour and sorrow by day.', by: '赫西俄德《工作與時日》' },
    { t: '我已建成一座比青銅更持久的紀念碑。', o: 'Exegi monumentum aere perennius.', by: '賀拉斯《頌歌集》第三卷第 30 首' },
    { t: '水滴石穿。', o: 'Gutta cavat lapidem.', by: '奧維德《黑海書簡》' },
    // —— 西方名言 ——
    { t: '相信你自己：每一顆心都隨著那根鐵弦震動。', o: 'Trust thyself: every heart vibrates to that iron string.', by: '愛默生〈自立〉（Self-Reliance）' },
    { t: '人是使用工具的動物……沒有工具，他一無所是；有了工具，他無所不能。', o: 'Man is a Tool-using Animal… Without Tools he is nothing, with Tools he is all.', by: '卡萊爾《衣裳哲學》（Sartor Resartus）' },
    { t: '找到自己工作的人是有福的，他不必再求別的福分。', o: 'Blessed is he who has found his work; let him ask no other blessedness.', by: '卡萊爾《過去與現在》（Past and Present）' },
    { t: '看哪！人已經成為自己工具的工具。', o: 'But lo! men have become the tools of their tools.', by: '梭羅《湖濱散記》（Walden）' },
    { t: '當代的重大問題，不是靠演說與多數決來解決……而是靠鐵與血。', o: 'Nicht durch Reden und Majoritätsbeschlüsse werden die großen Fragen der Zeit entschieden … sondern durch Eisen und Blut.', by: '俾斯麥，1862 年普魯士下議院預算委員會演說' },
    { t: '如此富有而死的人，死得可恥。', o: 'The man who dies thus rich dies disgraced.', by: '鋼鐵大王卡內基《財富的福音》（The Gospel of Wealth）' },
    { t: '懶惰像鐵鏽，比勞動磨損得更快；常用的鑰匙總是發亮。', o: 'Sloth, like rust, consumes faster than labour wears, while the used key is always bright.', by: '富蘭克林《窮理查年鑑》' },
    { t: '少了一根釘子，掉了一隻馬蹄鐵；少了一隻馬蹄鐵，失了一匹馬。', o: 'For want of a nail the shoe was lost; for want of a shoe the horse was lost.', by: '西方諺語，富蘭克林《窮理查年鑑》收錄' },
    { t: '做得好勝過說得好。', o: 'Well done is better than well said.', by: '富蘭克林《窮理查年鑑》' },
    { t: '鐵不用會生鏽，水不流會腐臭；人的心智不活動，也會失去活力。', o: 'Iron rusts from disuse; stagnant water loses its purity… even so does inaction sap the vigor of the mind.', by: '達文西筆記' },
    { t: '天才是百分之一的靈感，加上百分之九十九的汗水。', o: 'Genius is one percent inspiration, ninety-nine percent perspiration.', by: '愛迪生' },
    { t: '給我一個支點，我就能撬動地球。', o: 'Δός μοι πᾶ στῶ καὶ τὰν γᾶν κινάσω.', by: '阿基米德（據帕普斯記載）' },
    { t: '如果說我看得比別人更遠，那是因為我站在巨人的肩膀上。', o: 'If I have seen further it is by standing on the shoulders of Giants.', by: '牛頓，1676 年致虎克書信' },
    { t: '接下來要談的是鐵，它在人類手中，既是最有用、也是最致命的工具。', o: 'Iron, at the same time the most useful and the most fatal instrument in the hand of mankind.', by: '老普林尼《博物誌》第 34 卷' },
    { t: '陛下，若有人帶著比您更好的鐵來，這些黃金就全歸他了。', o: 'If any other come that hath better iron than you, he will be master of all this gold.', by: '梭倫對克羅伊斯語（馬基維利《論李維》第二卷第十章引述）' },
    { t: '每個人都是自己命運的鐵匠。', o: 'Faber est suae quisque fortunae.', by: '阿庇烏斯・克勞狄烏斯・凱庫斯' },
    { t: '烈火試煉黃金，苦難試煉勇者。', o: 'Ignis aurum probat, miseria fortes viros.', by: '塞內卡《論天意》' },
    // —— 各國俗諺 ——
    { t: '趁熱打鐵。', o: 'Strike while the iron is hot.', by: '英語諺語' },
    { t: '像鋼一樣真。（形容忠誠可靠）', o: 'True as steel.', by: '英語俗語' },
    { t: '火裡的鐵太多。（同時做太多事，反而顧不周全）', o: 'Too many irons in the fire.', by: '英語諺語' },
    { t: '百工百藝，全靠鐵鎚與雙手。', o: 'By hammer and hand all arts do stand.', by: '英國鐵匠行會格言' },
    { t: '拙匠總怪工具差。', o: 'A bad workman blames his tools.', by: '英語諺語' },
    { t: '量兩次，切一次。', o: 'Measure twice, cut once.', by: '英語諺語' },
    { t: '一條鏈子的強度，取決於最弱的那一環。', o: 'A chain is no stronger than its weakest link.', by: '英語諺語' },
    { t: '會吱吱叫的輪子才有油上。', o: 'The squeaky wheel gets the grease.', by: '美國諺語' },
    { t: '鐵砧不怕鎚打。', o: 'The anvil fears no blows.', by: '西方諺語' },
    { t: '打鐵才能成為鐵匠。（熟能生巧）', o: 'C’est en forgeant qu’on devient forgeron.', by: '法國諺語' },
    { t: '鐵匠家裡用木刀。', o: 'En casa de herrero, cuchillo de palo.', by: '西班牙諺語' },
    { t: '練習造就大師。', o: 'Übung macht den Meister.', by: '德國諺語' },
    { t: '耐心加勞動，什麼都能磨成。', o: 'Терпение и труд всё перетрут.', by: '俄羅斯諺語' },
    { t: '千日之練為鍛，萬日之練為鍊。', o: '千日の稽古を鍛とし、万日の稽古を錬とす。', by: '宮本武藏《五輪書》水之卷' },
    // —— 中國詩詞典籍 ——
    { t: '爐火照天地，紅星亂紫煙。赧郎明月夜，歌曲動寒川。', by: '李白〈秋浦歌〉其十四' },
    { t: '趙客縵胡纓，吳鉤霜雪明。', by: '李白〈俠客行〉' },
    { t: '何意百煉剛，化為繞指柔。', by: '劉琨〈重贈盧諶〉' },
    { t: '十年磨一劍，霜刃未曾試。今日把示君，誰有不平事？', by: '賈島〈劍客〉' },
    { t: '試玉要燒三日滿，辨材須待七年期。', by: '白居易〈放言五首〉其三' },
    { t: '千錘萬鑿出深山，烈火焚燒若等閒。粉骨碎身渾不怕，要留清白在人間。', by: '于謙〈石灰吟〉' },
    { t: '金戈鐵馬，氣吞萬里如虎。', by: '辛棄疾〈永遇樂・京口北固亭懷古〉' },
    { t: '夜闌臥聽風吹雨，鐵馬冰河入夢來。', by: '陸游〈十一月四日風雨大作〉其二' },
    { t: '男兒何不帶吳鉤，收取關山五十州。', by: '李賀〈南園十三首〉其五' },
    { t: '黃沙百戰穿金甲，不破樓蘭終不還。', by: '王昌齡〈從軍行〉其四' },
    { t: '欲將輕騎逐，大雪滿弓刀。', by: '盧綸〈塞下曲〉其三' },
    { t: '折戟沉沙鐵未銷，自將磨洗認前朝。', by: '杜牧〈赤壁〉' },
    { t: '將軍角弓不得控，都護鐵衣冷難著。', by: '岑參〈白雪歌送武判官歸京〉' },
    { t: '朔氣傳金柝，寒光照鐵衣。', by: '〈木蘭詩〉（北朝民歌）' },
    { t: '千淘萬漉雖辛苦，吹盡狂沙始到金。', by: '劉禹錫〈浪淘沙〉其八' },
    { t: '千磨萬擊還堅勁，任爾東西南北風。', by: '鄭板橋〈竹石〉' },
    { t: '不惜千金買寶刀，貂裘換酒也堪豪。', by: '秋瑾〈對酒〉' },
    { t: '工欲善其事，必先利其器。', by: '孔子《論語・衛靈公》' },
    { t: '如切如磋，如琢如磨。', by: '《詩經・衛風・淇奧》' },
    { t: '玉不琢，不成器；人不學，不知道。', by: '《禮記・學記》' },
    { t: '今臣之刀十九年矣，所解數千牛矣，而刀刃若新發於硎。', by: '莊子《莊子・養生主》' },
    { t: '吾楯之堅，物莫能陷也；吾矛之利，於物無不陷也。', by: '韓非《韓非子・難一》' },
    { t: '故木受繩則直，金就礪則利。', by: '荀子《荀子・勸學》' },
    { t: '鍥而舍之，朽木不折；鍥而不舍，金石可鏤。', by: '荀子《荀子・勸學》' },
    { t: '天有時，地有氣，材有美，工有巧，合此四者，然後可以為良。', by: '《周禮・考工記》' },
    { t: '精誠所加，金石為開。', by: '范曄《後漢書・廣陵思王荊傳》' },
    { t: '繩鋸木斷，水滴石穿。', by: '羅大經《鶴林玉露》' },
    { t: '寶劍鋒從磨礪出，梅花香自苦寒來。', by: '《警世賢文》' },
    { t: '鐵肩擔道義，辣手著文章。', by: '楊繼盛（明代諫臣）' },
    // —— 中文俗諺與成語 ——
    { t: '百鍊成鋼。', by: '成語' },
    { t: '恨鐵不成鋼。', by: '俗語' },
    { t: '真金不怕火煉。', by: '俗諺' },
    { t: '打鐵還需自身硬。', by: '俗諺' },
    { t: '只要功夫深，鐵杵磨成針。', by: '俗諺' },
    { t: '好鋼用在刀刃上。', by: '俗諺' },
    { t: '鐵打的營盤，流水的兵。', by: '俗諺' },
    { t: '磨刀不誤砍柴工。', by: '俗諺' },
    { t: '斬釘截鐵。', by: '成語' },
    { t: '削鐵如泥。', by: '成語' }

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
