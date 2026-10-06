/* 鋼語：首頁標題旁每次載入隨機一則與「鋼、鐵」相關的西方詩文、名言與俗諺（不收聖經與東方典籍）。
   每次重新整理隨機換一則（不與上一次重複）；新增條目直接加在 Q 陣列即可。
   t：中文（外文則為譯文）；o：外文原文（可省略）；by：出處（詩句須含作品與作者） */
(function () {
  var Q = [
    // —— 古希臘、羅馬 ——
    { t: '如今真正是黑鐵的世代，人們白日不得停歇於勞苦與憂患。', o: 'For now truly is a race of iron, and men never rest from labour and sorrow by day.', by: '赫西俄德《工作與時日》' },
    { t: '就像鐵匠把斧頭浸入冷水淬火——鐵的強度正是由此而來——發出巨大的嘶聲。', o: 'As a blacksmith plunges an axe or hatchet into cold water to temper it—for it is this that gives strength to the iron—and it makes a great hiss as he does so.', by: '荷馬《奧德賽》第九卷' },
    { t: '鐵自會把人吸引過去。', o: 'αὐτὸς γὰρ ἐφέλκεται ἄνδρα σίδηρος.', by: '荷馬《奧德賽》第十六卷' },
    { t: '贏得這塊生鐵的人，五年都用不完；他的牧人和農夫不必再進城買鐵。', o: 'He who wins it will have a store of iron that will last him five years… his shepherd or ploughman will not have to make a journey to buy iron.', by: '荷馬《伊利亞德》第二十三卷' },
    { t: '兩股風是風箱，打擊與反擊是鐵鎚與鐵砧，禍上加禍是被鍛打的鐵——因為鐵的發現，本是人類的禍害。', o: 'The two winds were the bellows, the stroke and counter-stroke the hammer and the anvil, and the woe upon woe the iron being hammered.', by: '希羅多德《歷史》第一卷' },
    { t: '開俄斯的格勞科斯，是世上唯一發明鐵焊接的人。', o: 'Glaucus of Chios, who alone of all men invented the welding of iron.', by: '希羅多德《歷史》第一卷' },
    { t: '我原本如此剛強，像淬過火的鐵一樣。', o: 'I, who erewhile was so wondrous firm,—yea, as iron hardened in the dipping.', by: '索福克勒斯《埃阿斯》' },
    { t: '神在統治者身上摻入黃金，在輔助者身上摻入白銀，在農夫與工匠身上摻入鐵與銅。', o: 'He has mingled gold… but in the helpers silver, and iron and brass in the husbandmen and craftsmen.', by: '柏拉圖《理想國》第三卷' },
    { t: '藥治不好的，鐵（刀）能治；鐵治不好的，火能治；火也治不好的，就是不治之症。', o: 'Those diseases which medicines do not cure, iron cures; those which iron cannot cure, fire cures.', by: '希波克拉底《格言》' },
    { t: '他廢除金幣與銀幣的流通，規定只准使用鐵錢。', o: 'He withdrew all gold and silver money from currency, and ordained the use of iron money only.', by: '普魯塔克《希臘羅馬名人傳・萊克格斯傳》' },
    { t: '最後一個世代，是堅硬的鐵。', o: 'De duro est ultima ferro.', by: '奧維德《變形記》第一卷' },
    { t: '有害的鐵已經出現，而比鐵更有害的黃金也隨之而來。', o: 'Iamque nocens ferrum ferroque nocentius aurum prodierat.', by: '奧維德《變形記》第一卷' },
    { t: '人類最早的武器是手、指甲與牙齒……後來才發現了鐵與銅的力量。', o: 'Arma antiqua manus ungues dentesque fuerunt… Posterius ferri vis est aerisque reperta.', by: '盧克萊修《物性論》第五卷' },
    { t: '然後有了鐵的剛硬，與鋸子尖響的鋼片。', o: 'Tum ferri rigor atque argutae lammina serrae.', by: '維吉爾《農事詩》第一卷' },
    { t: '他們連鐵都不多，這從他們的武器就看得出來。', o: 'Ne ferrum quidem superest, sicut ex genere telorum colligitur.', by: '塔西佗《日耳曼尼亞志》' },
    { t: '他們用銅幣、金幣，或按重量計值的鐵條當作貨幣。', o: 'Utuntur aut aere aut nummo aureo aut taleis ferreis ad certum pondus examinatis pro nummo.', by: '凱撒《高盧戰記》第五卷' },
    { t: '要用鐵，而不是用黃金，來收復祖國。', o: 'Ferro, non auro, recuperare patriam.', by: '卡米盧斯語，李維《羅馬史》第五卷' },
    { t: '戰敗者有禍了！（布倫努斯把鐵劍擲上秤盤時所說）', o: 'Vae victis!', by: '李維《羅馬史》第五卷' },
    { t: '鐵在人類手中，既是最有用、也是最致命的工具。', o: 'Iron, at the same time the most useful and the most fatal instrument in the hand of mankind.', by: '老普林尼《博物誌》第 34 卷' },
    { t: '陛下，若有人帶著比您更好的鐵來，這些黃金就全歸他了。', o: 'If any other come that hath better iron than you, he will be master of all this gold.', by: '梭倫對克羅伊斯語（馬基維利《論李維》引述）' },
    { t: '每個人都是自己命運的鐵匠。', o: 'Faber est suae quisque fortunae.', by: '阿庇烏斯・克勞狄烏斯・凱庫斯' },
    { t: '畢達哥拉斯路過鐵匠鋪，從鐵鎚敲擊的聲響中，找出了音程的比例。', by: '尼科馬庫斯《和聲學手冊》所載' },
    { t: '毒蛇去咬一把銼刀，銼刀說：「我向來只咬別人，不被別人咬。」', by: '伊索寓言〈毒蛇與銼刀〉' },
    // —— 中世紀至近代文學 ——
    { t: '凡能從這石中鐵砧拔出此劍者，即為全英格蘭天生的君王。', o: 'Whoso pulleth out this sword of this stone and anvil, is rightwise king born of all England.', by: '馬洛禮《亞瑟之死》' },
    { t: '他名叫塔路斯，是用鐵鑄成的人。', o: 'His name was Talus, made of yron mould.', by: '史賓賽《仙后》第五卷' },
    { t: '另一處，有人在鍛爐前勞作，熔化了兩大塊鐵與銅。', o: 'In other part stood one who at the Forge / Labouring, two massie clods of Iron and Brass / Had melted.', by: '米爾頓《失樂園》第十一卷' },
    { t: '鐵罐與陶罐結伴同行……我們只該與地位相當的人結交。', o: 'Ne nous associons qu’avecque nos égaux.', by: '拉封丹〈陶罐與鐵罐〉' },
    { t: '石牆築不成牢獄，鐵欄也圍不成籠。', o: 'Stone walls do not a prison make, / Nor iron bars a cage.', by: '洛夫萊斯〈獄中致艾西亞〉' },
    { t: '石砌的高塔、黃銅的城牆、不透氣的地牢、堅固的鐵鍊，都困不住堅強的精神。', o: 'Nor stony tower, nor walls of beaten brass, / Nor airless dungeon, nor strong links of iron, / Can be retentive to the strength of spirit.', by: '莎士比亞《凱撒大帝》第一幕第三景' },
    { t: '你所交的朋友，若已經過考驗，就用鋼箍把他們緊緊扣在心上。', o: 'Those friends thou hast, and their adoption tried, / Grapple them unto thy soul with hoops of steel.', by: '莎士比亞《哈姆雷特》第一幕第三景' },
    { t: '堅不可摧的岩石不夠堅固，鋼鐵的城門也不夠牢靠，終究都會被時間侵蝕。', o: 'When rocks impregnable are not so stout, / Nor gates of steel so strong, but Time decays?', by: '莎士比亞《十四行詩》第 65 首' },
    { t: '除非我的神經是黃銅或鍛打過的鋼，否則只能在自己的過錯面前低頭。', o: 'Needs must I under my transgression bow, / Unless my nerves were brass or hammer’d steel.', by: '莎士比亞《十四行詩》第 120 首' },
    { t: '理直者有三重盔甲；良心不正的人，即使全身包在鋼裡，也形同赤裸。', o: 'Thrice is he arm’d that hath his quarrel just, / And he but naked, though lock’d up in steel.', by: '莎士比亞《亨利六世》中篇 第三幕第二景' },
    { t: '別為敵人把熔爐燒得太熱，以免燙傷了自己。', o: 'Heat not a furnace for your foe so hot / That it do singe yourself.', by: '莎士比亞《亨利八世》第一幕第一景' },
    { t: '你吸引我，你這鐵石心腸的磁石；可你吸的不是鐵，因為我的心真得像鋼。', o: 'You draw me, you hard-hearted adamant; / But yet you draw not iron, for my heart / Is true as steel.', by: '莎士比亞《仲夏夜之夢》第二幕第一景' },
    { t: '真得像鋼，像月亮之於草木。', o: 'As true as steel, as plantage to the moon.', by: '莎士比亞《特洛伊羅斯與克瑞西達》第三幕第二景' },
    { t: '習慣這個暴君，已讓戰場上燧石與鋼鐵般的床鋪，成了我最柔軟的羽絨床。', o: 'The tyrant custom… / Hath made the flinty and steel couch of war / My thrice-driven bed of down.', by: '莎士比亞《奧賽羅》第一幕第三景' },
    { t: '英勇的馬克白，不顧命運，揮舞著他的鋼刃。', o: 'For brave Macbeth—well he deserves that name— / Disdaining fortune, with his brandish’d steel.', by: '莎士比亞《馬克白》第一幕第二景' },
    { t: '把這些鐵條給我燒紅。', o: 'Heat me these irons hot.', by: '莎士比亞《約翰王》第四幕第一景' },
    // —— 18、19 世紀詩文 ——
    { t: '是什麼樣的鐵鎚？什麼樣的鎖鏈？你的頭腦在哪座熔爐裡鍛成？', o: 'What the hammer? what the chain? / In what furnace was thy brain?', by: '布萊克〈老虎〉' },
    { t: '是什麼樣的鐵砧？什麼樣可怕的手勁，竟敢緊握那致命的恐怖？', o: 'What the anvil? what dread grasp, / Dare its deadly terrors clasp!', by: '布萊克〈老虎〉' },
    { t: '腳下穿著鋼，我們在光滑的冰面上嘶嘶滑行。', o: 'All shod with steel, / We hiss’d along the polish’d ice.', by: '華茲華斯《序曲》第一卷' },
    { t: '你必須……做鐵砧，或做鐵鎚。', o: 'Du mußt … Amboß oder Hammer sein.', by: '歌德〈科普特之歌〉' },
    { t: '讓鐵生長的上帝，不要奴隸。', o: 'Der Gott, der Eisen wachsen ließ, / Der wollte keine Knechte.', by: '阿恩特〈祖國之歌〉' },
    { t: '我獻出黃金，換回鐵。', o: 'Gold gab ich für Eisen.', by: '1813 年普魯士解放戰爭募捐口號' },
    { t: '在枝葉繁茂的栗樹下，矗立著村裡的鐵匠鋪；鐵匠是個魁梧的漢子，有一雙粗大結實的手。', o: 'Under a spreading chestnut-tree / The village smithy stands; / The smith, a mighty man is he, / With large and sinewy hands.', by: '朗費羅〈鄉村鐵匠〉' },
    { t: '他的額頭沾滿誠實的汗水，憑本事賺取所得。', o: 'His brow is wet with honest sweat, / He earns whate’er he can.', by: '朗費羅〈鄉村鐵匠〉' },
    { t: '日復一日，從早到晚，你聽得見他的風箱鼓動，聽得見他揮動沉重的大鎚，節奏穩重而緩慢。', o: 'Week in, week out, from morn till night, / You can hear his bellows blow; / You can hear him swing his heavy sledge, / With measured beat and slow.', by: '朗費羅〈鄉村鐵匠〉' },
    { t: '放學回家的孩子們，從敞開的門往裡看；他們愛看熊熊的鍛爐，愛聽風箱的呼嘯。', o: 'And children coming home from school / Look in at the open door; / They love to see the flaming forge, / And hear the bellows roar.', by: '朗費羅〈鄉村鐵匠〉' },
    { t: '有所嘗試，有所完成，便換得一夜安眠。', o: 'Something attempted, something done, / Has earned a night’s repose.', by: '朗費羅〈鄉村鐵匠〉' },
    { t: '我們的命運，正是在生命熊熊的鍛爐上鍛成；每個熾熱的行動與念頭，都在鳴響的鐵砧上成形。', o: 'Thus at the flaming forge of life / Our fortunes must be wrought; / Thus on its sounding anvil shaped / Each burning deed and thought!', by: '朗費羅〈鄉村鐵匠〉' },
    { t: '這就是兵工廠。從地板到天花板，擦亮的兵器像一架巨大的管風琴般排列而上。', o: 'This is the Arsenal. From floor to ceiling, / Like a huge organ, rise the burnished arms.', by: '朗費羅〈斯普林菲爾德兵工廠〉' },
    { t: '聽那鐘聲的敲響——鐵的鐘聲！', o: 'Hear the tolling of the bells— / Iron Bells!', by: '愛倫・坡〈鐘〉' },
    { t: '扯下她破爛的旗幟吧！它在高處飄揚已久。', o: 'Ay, tear her tattered ensign down! / Long has it waved on high.', by: '霍姆斯〈老鐵甲〉（Old Ironsides）' },
    { t: '人生不是無用的礦石，而是從深處掘出的鐵，在燃燒的恐懼中燒熱，在嘶響的淚水中淬火，在命運的衝擊下鍛打，終於成形、成器。', o: 'That life is not as idle ore, / But iron dug from central gloom, / And heated hot with burning fears, / And dipt in baths of hissing tears, / And batter’d with the shocks of doom / To shape and use.', by: '丁尼生《悼念集》第 118 首' },
    { t: '人生是由許許多多的離別焊接而成的。有人是鐵匠，有人是白鐵匠，有人是金匠，有人是銅匠。', o: 'Life is made of ever so many partings welded together… and one man’s a blacksmith, and one’s a whitesmith, and one’s a goldsmith, and one’s a coppersmith.', by: '狄更斯《遠大前程》，鐵匠喬・葛吉瑞' },
    { t: '我戴著生前親手鍛造的鎖鏈，一環一環、一碼一碼地打成。', o: 'I wear the chain I forged in life. I made it link by link, and yard by yard.', by: '狄更斯《小氣財神》，馬里的鬼魂' },
    { t: '形狀優美、赤裸、蒼白的利器，斧頭從大地母親的腹中取出，木的肉身、金屬的骨。', o: 'Weapon shapely, naked, wan, / Head from the mother’s bowels drawn, / Wooded flesh and metal bone.', by: '惠特曼〈闊斧之歌〉' },
    { t: '你在粗獷的鍛爐前，在同伴中顯得強壯，為那匹灰色大馱馬打造明亮而鏗鏘的蹄鐵。', o: 'When thou at the random grim forge, powerful amidst peers, / Didst fettle for the great grey drayhorse his bright and battering sandal!', by: '霍普金斯〈菲力克斯・蘭德爾〉（鐵蹄匠）' },
    { t: '如鋼一般真，如刃一般直，偉大的工匠造就了我的伴侶。', o: 'Steel-true and blade-straight, / The great artificer / Made my mate.', by: '史蒂文生〈我的妻子〉' },
    { t: '相信你自己：每一顆心都隨著那根鐵弦震動。', o: 'Trust thyself: every heart vibrates to that iron string.', by: '愛默生〈自立〉' },
    { t: '大地堅硬如鐵，河水凍結如石。', o: 'Earth stood hard as iron, / Water like a stone.', by: '克莉絲蒂娜・羅塞蒂〈在荒涼的隆冬〉' },
    { t: '諾東！諾東！令人豔羨的劍！', o: 'Nothung! Nothung! Neidliches Schwert!', by: '華格納《齊格菲》第一幕鍛劍之歌' },
    // —— 20 世紀初詩文 ——
    { t: '然而鐵——冰冷的鐵——才是萬物之主。', o: 'But Iron—Cold Iron—is master of them all.', by: '吉卜林〈冷鐵〉' },
    { t: '鐵——冰冷的鐵——終將主宰你們所有人！', o: 'Iron—Cold Iron—shall be master of you all!', by: '吉卜林〈冷鐵〉' },
    { t: '我們從礦床與礦坑裡被取出，在熔爐與坩堝中熔化；我們被鑄造、鍛打，依設計成形。', o: 'We were taken from the ore-bed and the mine, / We were melted in the furnace and the pit— / We were cast and wrought and hammered to design.', by: '吉卜林〈機器的祕密〉' },
    { t: '鋼鐵的艙室，曾是她火蜥蜴般烈焰的焚爐，如今冰冷的洋流穿行其中，化為潮汐的豎琴。', o: 'Steel chambers, late the pyres / Of her salamandrine fires, / Cold currents thrid, and turn to rhythmic tidal lyres.', by: '哈代〈兩者的交會〉（悼鐵達尼號）' },
    { t: '神啊，把我放在鐵砧上，把我敲打、鎚煉成一根撬棍。', o: 'Lay me on an anvil, O God. / Beat me and hammer me into a crowbar.', by: '桑德堡〈鋼的禱詞〉' },
    { t: '神啊，把我放在鐵砧上，把我敲打、鎚煉成一根鋼釘。', o: 'Lay me on an anvil, O God. / Beat me and hammer me into a steel spike.', by: '桑德堡〈鋼的禱詞〉' },
    { t: '一根鋼條——它的核心只是煙，煙和一個人的血。', o: 'A bar of steel—it is only / Smoke at the heart of it, smoke and the blood of a man.', by: '桑德堡〈煙與鋼〉' },
    { t: '春天田野的煙是一種，秋天落葉的煙是另一種；鋼廠屋頂的煙，又是另一種。', o: 'Smoke of the fields in spring is one, / Smoke of the leaves in autumn another. / Smoke of a steel-mill roof or a battleship funnel.', by: '桑德堡〈煙與鋼〉' },
    // —— 名言與歷史 ——
    { t: '當代的重大問題，不是靠演說與多數決來解決……而是靠鐵與血。', o: 'Nicht durch Reden und Majoritätsbeschlüsse werden die großen Fragen der Zeit entschieden … sondern durch Eisen und Blut.', by: '俾斯麥，1862 年普魯士下議院預算委員會演說' },
    { t: '從波羅的海的斯德丁到亞得里亞海的的里雅斯特，一道鐵幕已經降下，橫亙歐洲大陸。', o: 'From Stettin in the Baltic to Trieste in the Adriatic, an iron curtain has descended across the Continent.', by: '邱吉爾，1946 年富爾頓演說' },
    { t: '工資的鐵律。', o: 'Das eherne Lohngesetz.', by: '拉薩爾，1863 年' },
    { t: '我相信，這座鐵塔將有它自己的美。', o: 'Je crois bien que la tour aura sa beauté propre.', by: '艾菲爾，1887 年回應藝術家抗議' },
    { t: '這座無用而怪誕的艾菲爾鐵塔。', o: 'Cette inutile et monstrueuse tour Eiffel.', by: '1887 年巴黎藝術家抗議書' },
    { t: '匹茲堡是掀了蓋子的地獄。', o: 'Hell with the lid taken off.', by: '帕頓，1868 年《大西洋月刊》描寫鋼鐵城匹茲堡' },
    { t: '如此富有而死的人，死得可恥。', o: 'The man who dies thus rich dies disgraced.', by: '鋼鐵大王卡內基《財富的福音》' },
    { t: '這裡長眠著一個懂得讓比自己更聰明的人圍繞在身邊的人。', o: 'Here lies one who knew how to get around him men who were cleverer than himself.', by: '鋼鐵大王卡內基自擬墓誌銘（相傳）' },
    { t: '懶惰像鐵鏽，比勞動磨損得更快；常用的鑰匙總是發亮。', o: 'Sloth, like rust, consumes faster than labour wears, while the used key is always bright.', by: '富蘭克林《窮理查年鑑》' },
    { t: '少了一根釘子，掉了一隻馬蹄鐵；少了一隻馬蹄鐵，失了一匹馬。', o: 'For want of a nail the shoe was lost; for want of a shoe the horse was lost.', by: '富蘭克林《窮理查年鑑》收錄的諺語' },
    { t: '鐵不用會生鏽，水不流會腐臭；人的心智不活動，也會失去活力。', o: 'Iron rusts from disuse; stagnant water loses its purity… even so does inaction sap the vigor of the mind.', by: '達文西筆記' },
    // —— 西方俗諺與成語 ——
    { t: '趁熱打鐵。', o: 'Strike while the iron is hot.', by: '英語諺語' },
    { t: '鐵要趁熱鍛。', o: 'Man muss das Eisen schmieden, solange es heiß ist.', by: '德國諺語' },
    { t: '鐵燒紅時就該鍛打。', o: 'Ferrum, dum in igni candet, cudendum est.', by: '拉丁諺語' },
    { t: '像鋼一樣真。（形容忠誠可靠）', o: 'True as steel.', by: '英語俗語' },
    { t: '火裡的鐵太多。（同時做太多事，反而顧不周全）', o: 'Too many irons in the fire.', by: '英語諺語' },
    { t: '百工百藝，全靠鐵鎚與雙手。', o: 'By hammer and hand all arts do stand.', by: '英國鐵匠行會格言' },
    { t: '鐵砧不怕鎚打。', o: 'The anvil fears no blows.', by: '西方諺語' },
    { t: '鐵砧比鐵鎚更耐久。', o: 'Dura più l’incudine che il martello.', by: '義大利諺語' },
    { t: '夾在鐵鎚與鐵砧之間。（兩面受壓）', o: 'Zwischen Hammer und Amboss.', by: '德語成語' },
    { t: '打鐵才能成為鐵匠。（熟能生巧）', o: 'C’est en forgeant qu’on devient forgeron.', by: '法國諺語' },
    { t: '鐵匠家裡用木刀。', o: 'En casa de herrero, cuchillo de palo.', by: '西班牙諺語' },
    { t: '天鵝絨手套裡的鐵拳。（外柔內剛）', o: 'An iron hand in a velvet glove.', by: '西方俗語' },
    { t: '鋼鐵般的神經。（臨危不亂）', o: 'Nerves of steel.', by: '英語俗語' },
    { t: '把自己鍛成鋼。（硬起心腸，做好準備）', o: 'Steel yourself.', by: '英語俗語' },
    { t: '硬得像釘子。（意志堅強、不易屈服）', o: 'As hard as nails.', by: '英語俗語' },
    { t: '一鎚敲在釘頭上。（說中要害）', o: 'Hit the nail on the head.', by: '英語俗語' },
    { t: '用鐵與火。（以刀兵與烈火）', o: 'Ferro ignique.', by: '拉丁成語' },
    { t: '用鐵和鋼把它蓋起來，鐵和鋼，鐵和鋼。', o: 'Build it up with iron and steel, / Iron and steel, iron and steel.', by: '英國童謠〈倫敦鐵橋垮下來〉' }

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
