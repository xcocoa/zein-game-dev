## ============================================================
## 世界三：学吉他的那段日子
## 一个关于练习、挫折和最终弹出一首曲子的故事
## ============================================================

## 玩家进度变量
default guitar_chord_c = False
default guitar_chord_g = False
default guitar_chord_am = False
default guitar_chord_f = False
default guitar_strumming = False
default guitar_transition = False
default guitar_song_verse1 = False
default guitar_song_verse2 = False
default guitar_song_chorus = False
default guitar_tuned = False
default guitar_practice_days = 0


## ============================================================
## 入口
## ============================================================
label world_guitar:

    scene black with fade

    centered "{size=20}{color=#aaaaaa}正在进入这个世界...{/color}{/size}"
    pause 1.5
    centered "{size=16}{color=#666666}某个周末下午 · 一个决定学吉他的人的房间{/color}{/size}"
    pause 1.5

    scene bg_guitar_room with dissolve

    narrator "角落里靠着一把吉他。"
    narrator "是民谣吉他，木色，琴颈上贴着几张小标签纸，写着 C、G、Am、F。"
    narrator "旁边还放着一本《30天学会吉他》，封面有点皱。"

    inner "（第3天了。还没翻到第4页。）"

    narrator "窗外阳光不错，有点可惜——但也正是练琴的好时候。"

    jump guitar_room_main


## ============================================================
## 主房间菜单（可以反复回来）
## ============================================================
label guitar_room_main:

    scene bg_guitar_room with dissolve

    narrator "房间里有些东西可以互动。"

    menu:
        "🎸 拿起吉他，开始练习" if not (guitar_chord_c and guitar_chord_g and guitar_chord_am and guitar_chord_f and guitar_strumming and guitar_transition):
            jump guitar_pick_up

        "🎹 直接打开指板，自由弹奏":
            jump guitar_free_play

        "🎵 尝试弹一首曲子" if guitar_chord_c and guitar_chord_g and guitar_chord_am and guitar_chord_f and guitar_strumming and guitar_transition:
            jump guitar_play_song

        "📖 翻开教材" :
            jump guitar_book

        "🎧 听一遍目标曲子":
            jump guitar_listen

        "🪴 休息一下，望望窗外":
            jump guitar_rest

        "← 离开这个世界":
            jump guitar_leave


## ============================================================
## 拿起吉他
## ============================================================
label guitar_pick_up:

    scene bg_guitar_room with dissolve

    narrator "你把吉他从墙边拿起来，横放在腿上。"
    narrator "比想象中重一点，但也没有很重。"
    narrator "你拨了一下空弦——"

    inner "（有点跑调。）"

    if not guitar_tuned:
        narrator "音有些不对，需要先调弦。"
        menu:
            "用手机调音 App 调弦":
                jump guitar_tune
            "先不管，直接练":
                jump guitar_practice_menu
    else:
        narrator "弦已经调好了，可以开始练习。"
        jump guitar_practice_menu


## 调弦
label guitar_tune:

    scene bg_guitar_room with dissolve

    narrator "你打开手机上的调音器 App。"
    narrator "从第六弦开始，一根一根地调。"
    pause 0.8
    narrator "E 弦——拨一下，指针往右，慢慢拧紧……"
    pause 0.5
    narrator "A 弦——差了一点点，继续转……"
    pause 0.5
    narrator "D、G、B、e——"
    pause 1.0
    narrator "全部对齐了。"
    narrator "再拨一下，这次的声音干净多了。"

    $ guitar_tuned = True
    inner "（调好弦这件事，比想象中有成就感。）"

    jump guitar_practice_menu


## ============================================================
## 练习菜单
## ============================================================
label guitar_practice_menu:

    scene bg_guitar_room with dissolve

    narrator "你看了一眼贴在琴颈上的标签。"
    narrator "C · G · Am · F —— 这四个和弦，是大多数流行歌曲的骨架。"

    menu:

        "🎸 【交互】 在指板上练 C 和弦" if not guitar_chord_c:
            jump guitar_interactive_c

        "🎸 【交互】 在指板上练 G 和弦" if not guitar_chord_g:
            jump guitar_interactive_g

        "🎸 【交互】 在指板上练 Am 和弦" if not guitar_chord_am:
            jump guitar_interactive_am

        "🎸 【交互】 在指板上练 F 和弦" if not guitar_chord_f:
            jump guitar_interactive_f

        "练扫弦节奏" if guitar_chord_c and guitar_chord_g and not guitar_strumming:
            jump guitar_practice_strumming

        "练和弦切换" if guitar_strumming and not guitar_transition:
            jump guitar_practice_transition

        "🎹 自由弹奏 · 随便按按":
            jump guitar_free_play

        "← 回到房间":
            jump guitar_room_main


## ============================================================
## 和弦练习：C
## ============================================================
label guitar_practice_c:

    scene bg_guitar_room with dissolve

    narrator "C 和弦。"
    narrator "中指按第二弦第一品，无名指按第四弦第二品，食指按第一弦第一品。"
    pause 0.8
    narrator "你把手指放上去——"

    inner "（手指有点短？还是琴颈有点宽？）"

    narrator "拨一下……"
    pause 0.5

    menu:
        "声音很闷，某根弦没有按实":
            jump guitar_c_retry
        "有点像了，继续重复":
            jump guitar_c_practice


label guitar_c_retry:

    narrator "你低头检查，食指稍微靠近了品格。"
    narrator "再试一次——"
    pause 0.5
    narrator "清脆多了。"
    inner "（原来差这么一点点。）"
    jump guitar_c_practice


label guitar_c_practice:

    narrator "你开始重复：按，拨，松，按，拨，松……"
    pause 0.8
    narrator "二十次。"
    pause 0.5
    narrator "五十次。"
    pause 0.5
    narrator "手指有点酸，按弦的地方开始有点发红。"

    menu:
        "继续练，不怕疼":
            jump guitar_c_done
        "先休息一下":
            jump guitar_c_rest_then_done


label guitar_c_rest_then_done:

    narrator "你把手放下来，甩了甩。"
    narrator "手指上出现了浅浅的弦痕。"
    inner "（这就是练琴留下的印记。）"
    pause 1.0
    jump guitar_c_done


label guitar_c_done:

    $ guitar_chord_c = True
    $ guitar_practice_days += 1

    narrator "C 和弦，算是摸到了。"
    narrator "不够稳，但已经有了形状。"

    inner "（每个吉他手的第一个和弦都是 C。）"

    jump guitar_practice_menu


## ============================================================
## 和弦练习：G
## ============================================================
label guitar_practice_g:

    scene bg_guitar_room with dissolve

    narrator "G 和弦。"
    narrator "三根手指要同时按住三根弦，分布在不同品格上。"
    narrator "食指按第五弦第二品，中指按第六弦第三品，无名指按第一弦第三品。"
    pause 0.8

    inner "（这个……有点费劲。）"

    narrator "你试着伸开手指——"
    pause 0.5
    narrator "拨弦……"

    menu:
        "有几根弦没有发声":
            jump guitar_g_fix
        "勉强发声了，继续重复":
            jump guitar_g_practice


label guitar_g_fix:

    narrator "你重新摆了摆手型，手指往指尖方向立了立。"
    narrator "再拨——"
    pause 0.5
    narrator "五根弦都响了。"
    inner "（原来按弦要立起来，不能塌着。）"
    jump guitar_g_practice


label guitar_g_practice:

    narrator "G 和弦有点大，虎口有一种微微被撑开的感觉。"
    narrator "但拨出来的声音……饱满，有共鸣。"
    pause 0.5
    narrator "你练了一会儿，手指开始适应这个张开的形状。"

    $ guitar_chord_g = True
    $ guitar_practice_days += 1

    inner "（G 和弦特别有吉他的感觉。）"

    jump guitar_practice_menu


## ============================================================
## 和弦练习：Am
## ============================================================
label guitar_practice_am:

    scene bg_guitar_room with dissolve

    narrator "Am 和弦。"
    narrator "中指按第三弦第二品，无名指按第四弦第二品，食指按第二弦第一品。"
    pause 0.8
    narrator "形状和 C 有点像，但手指的位置整体下移了一根弦。"
    pause 0.5

    narrator "拨出来——"
    pause 0.5

    inner "（有一种淡淡的忧郁感。）"

    narrator "Am 是小调，声音比 C 和 G 暗一点，柔一点。"
    narrator "你反复拨了几遍，觉得自己喜欢这个和弦的音色。"

    $ guitar_chord_am = True
    $ guitar_practice_days += 1

    inner "（难怪很多民谣里都有 Am。）"

    jump guitar_practice_menu


## ============================================================
## 和弦练习：F（最难的）
## ============================================================
label guitar_practice_f:

    scene bg_guitar_room with dissolve

    narrator "F 和弦。"
    narrator "食指需要横按第一到第二弦的第一品——也就是所谓的「封闭和弦」。"
    pause 0.8

    inner "（所有人第一次学 F 都会卡住。）"

    narrator "你按下去，拨弦……"
    pause 0.5
    narrator "闷的。"
    pause 0.3
    narrator "再试……"
    pause 0.5
    narrator "还是闷的。"
    pause 0.3

    inner "（食指不够直？还是力气不够？）"

    menu:
        "调整食指位置，重新来":
            jump guitar_f_retry1
        "加大力气，硬按":
            jump guitar_f_retry2
        "先放弃，回来再练":
            jump guitar_f_give_up


label guitar_f_retry1:

    narrator "你把食指移到更靠近品丝的位置，稍微旋转了一下。"
    narrator "再按，再拨——"
    pause 0.5
    narrator "第一弦和第二弦都响了！"
    narrator "但力气还不够稳，需要继续练。"
    jump guitar_f_training


label guitar_f_retry2:

    narrator "你咬着牙用力按。"
    narrator "手指有点疼，但……"
    pause 0.5
    narrator "有几根弦开始发声了。"
    inner "（原来需要这么大力气。）"
    jump guitar_f_training


label guitar_f_give_up:

    narrator "F 和弦不是一天练成的。"
    narrator "你放下手，决定明天再试。"
    inner "（几乎所有人都在 F 上卡过。）"
    narrator "但你知道，只要坚持，一定能按实。"

    $ guitar_chord_f = True  # 即使艰难，也算经历了
    jump guitar_practice_menu


label guitar_f_training:

    narrator "你盯着手指练了很久。"
    narrator "从五分钟，到十五分钟。"
    narrator "手指开始有点麻，但 F 和弦的声音渐渐干净起来。"
    pause 1.0
    narrator "最后一次拨弦——"
    pause 0.5
    narrator "六根弦，全部响了。"
    pause 0.8

    $ guitar_chord_f = True
    $ guitar_practice_days += 1

    inner "（F 和弦，拿下了。）"
    narrator "这一刻，比之前任何一个和弦都有成就感。"

    jump guitar_practice_menu


## ============================================================
## 扫弦节奏练习
## ============================================================
label guitar_practice_strumming:

    scene bg_guitar_room with dissolve

    narrator "学会按和弦只是第一步，还要学会扫弦的节奏。"
    narrator "最基本的节奏型：下 下 上 下 上 上 下——"
    pause 0.8

    narrator "你先用 C 和弦练节奏，不求速度，先求稳。"

    menu:
        "跟着拍子：下下上下上上下":
            jump guitar_strum_practice
        "先用拇指慢慢感受节拍":
            jump guitar_strum_slow


label guitar_strum_slow:

    narrator "你用拇指一下一下地扫，数着拍子。"
    narrator "1、2、3、4——"
    pause 0.8
    narrator "越来越有感觉了。"
    inner "（节拍，是音乐的骨架。）"
    jump guitar_strum_practice


label guitar_strum_practice:

    narrator "你开始用拨片模拟扫弦。"
    narrator "下——下——上——下——上——上——下——"
    pause 0.8
    narrator "第一遍，手腕有点僵。"
    pause 0.5
    narrator "第五遍，节奏开始稳了一点。"
    pause 0.5
    narrator "第二十遍——"
    pause 0.5
    narrator "手腕放松了，扫弦声音也更圆润了。"
    pause 0.8

    inner "（对！就是这种感觉！）"

    $ guitar_strumming = True

    narrator "扫弦，有了。"
    jump guitar_practice_menu


## ============================================================
## 和弦切换练习
## ============================================================
label guitar_practice_transition:

    scene bg_guitar_room with dissolve

    narrator "最后一关：和弦切换。"
    narrator "一首歌里，和弦是要不停切换的，这才是最考验流畅度的地方。"
    pause 0.8

    narrator "目标：C → G → Am → F，每个和弦各四拍，循环练习。"

    menu:
        "开始慢速练习（每个和弦停留够久再换）":
            jump guitar_transition_slow
        "直接尝试正常速度":
            jump guitar_transition_normal


label guitar_transition_slow:

    narrator "你放慢速度，给自己足够时间摆手型。"
    narrator "C……（数四拍）……G……（数四拍）……Am……（数四拍）……F——"
    pause 1.5
    narrator "有时候换 F 的时候会慢一拍，食指没摆好。"
    narrator "但你没有停，继续转下去。"
    inner "（不要停，出错了也继续走。）"
    pause 0.5
    narrator "循环了五遍，已经能跟上节拍了。"
    jump guitar_transition_done


label guitar_transition_normal:

    narrator "你深呼一口气，按上 C 和弦，开始扫弦——"
    pause 0.5
    narrator "C → G，有一点卡顿——"
    pause 0.5
    narrator "G → Am，还行——"
    pause 0.5
    narrator "Am → F，食指慢了——"
    pause 0.5
    narrator "但你没有停下来，继续扫，继续走。"
    inner "（第一遍没关系，继续。）"
    narrator "第三遍，明显顺了很多。"
    jump guitar_transition_done


label guitar_transition_done:

    $ guitar_transition = True
    $ guitar_practice_days += 1

    narrator "C → G → Am → F，这四个和弦的循环，你终于能连起来了。"
    pause 0.8
    narrator "不完美，有几次切换还会慢。"
    narrator "但有了这个底子，就可以弹一首真正的歌了。"
    pause 0.8

    inner "（所有准备，都是为了那一刻。）"

    narrator "你决定去试试。"
    jump guitar_room_main


## ============================================================
## 教材
## ============================================================
label guitar_book:

    scene bg_guitar_room with dissolve

    narrator "你翻开那本《30天学会吉他》。"
    narrator "第1页：认识吉他各部件。"
    narrator "第2页：调弦方法。"
    narrator "第3页：如何持琴、如何拨弦。"
    narrator "第4页：C 和弦图解。"
    pause 0.5

    narrator "页边有你自己写的笔记——「食指要立起来」「按完马上检查发音」。"
    narrator "有几页还折了角。"

    inner "（看起来确实读进去了一点。）"

    menu:
        "看和弦指法图":
            jump guitar_book_chords
        "看节奏型说明":
            jump guitar_book_rhythm
        "合上，去练琴":
            jump guitar_room_main


label guitar_book_chords:

    narrator "书上画着手指的位置，旁边标着数字。"
    narrator "C：2-1，4-2，1-1（弦号-品格号）"
    narrator "G：5-2，6-3，1-3"
    narrator "Am：3-2，4-2，2-1"
    narrator "F：1~6-1（封闭），3-2，4-3"
    pause 0.5
    inner "（看懂了，但手指不一定能做到。）"
    narrator "理论和实践之间，差的就是那几百次的重复。"
    jump guitar_room_main


label guitar_book_rhythm:

    narrator "「基础节奏型：四四拍，下下上下上上下」"
    narrator "书上还画了箭头，↓↓↑↓↑↑↓"
    narrator "旁边注着：「手腕放松，用小臂带动」"
    pause 0.5
    inner "（所以不是靠手腕使劲？）"
    narrator "原来一直用手腕在扫，难怪容易累。"
    jump guitar_room_main


## ============================================================
## 听目标曲子
## ============================================================
label guitar_listen:

    scene bg_guitar_room with dissolve

    narrator "你戴上耳机，搜出那首你想弹的歌。"
    pause 0.5
    narrator "《等你下课》。"
    pause 0.5
    narrator "前奏响起来，吉他声很清晰，像是有人坐在旁边弹给你听。"
    pause 0.8
    narrator "C → G → Am → F……"
    pause 0.5
    inner "（就是这四个和弦，循环下去，就是一首歌。）"
    narrator "你一边听，一边在腿上比画手型。"
    narrator "闭上眼睛，感受那个节奏。"
    pause 1.0
    inner "（总有一天，我能弹出这个声音。）"
    jump guitar_room_main


## ============================================================
## 休息
## ============================================================
label guitar_rest:

    scene bg_guitar_room with dissolve

    narrator "你把吉他放回去，走到窗边。"
    pause 0.5
    narrator "外面的树在风里动着，阳光把影子切碎了投在地板上。"
    pause 0.8

    if guitar_practice_days == 0:
        narrator "你刚开始学，什么都陌生。但每一件陌生的事，都会有变熟悉的那天。"
    elif guitar_practice_days <= 2:
        narrator "练了几天了。手指有点酸，但也开始有点感觉了。"
        inner "（身体也在学习。）"
    elif guitar_practice_days <= 4:
        narrator "一点点在进步。那些和弦，正在从「需要思考」变成「下意识」。"
        inner "（这就是练习的意义。）"
    else:
        narrator "你已经练了不少天了。"
        narrator "手指上有了薄薄的茧，按弦不再那么疼了。"
        inner "（茧是身体记住吉他的方式。）"

    pause 1.0
    jump guitar_room_main


## ============================================================
## 弹一首曲子（需要全部解锁）
## ============================================================
label guitar_play_song:

    scene bg_guitar_room with dissolve

    narrator "你拿起吉他，深吸一口气。"
    narrator "《等你下课》。"
    narrator "C → G → Am → F，就是这四个和弦，循环四次，就是一首歌。"
    pause 1.0

    narrator "你摆好 C 和弦，开始扫弦——"

    jump guitar_song_part1


## 第一段：主歌
label guitar_song_part1:

    scene bg_guitar_room with dissolve

    narrator "C 和弦，四拍——"
    pause 0.8
    narrator "换 G——"
    pause 0.5

    menu:
        "顺利切换过去了":
            jump guitar_song_p1_good
        "换慢了，重新来":
            jump guitar_song_p1_retry


label guitar_song_p1_retry:

    narrator "你停下来，从头再来。"
    inner "（不急，再来一遍。）"
    pause 0.5
    narrator "这次慢一点——"
    pause 0.5
    narrator "C……G……Am……F……"
    pause 1.0
    narrator "顺了很多。"
    jump guitar_song_p1_good


label guitar_song_p1_good:

    $ guitar_song_verse1 = True
    narrator "第一段，走完了。"
    narrator "不完美，但完整。"
    inner "（继续。）"
    jump guitar_song_part2


## 第二段：主歌重复
label guitar_song_part2:

    scene bg_guitar_room with dissolve

    narrator "第二遍主歌——"
    narrator "手指开始熟悉这个路线了。"
    narrator "C → G → Am → F，像一个你越走越顺的小径。"
    pause 1.0

    narrator "扫弦的节奏稳了很多，手腕也没有那么僵了。"
    pause 0.5

    inner "（有点感觉了！）"

    $ guitar_song_verse2 = True
    jump guitar_song_chorus


## 副歌
label guitar_song_chorus:

    scene bg_guitar_room with dissolve

    narrator "副歌——节奏要稍微快一点。"
    pause 0.5
    narrator "你加快扫弦速度，换弦的间隔缩短了——"
    pause 0.8

    menu:
        "跟上节奏，顺利弹完":
            jump guitar_song_end_good
        "F 和弦卡了一下，但撑过去了":
            jump guitar_song_end_struggle


label guitar_song_end_struggle:

    narrator "F 卡了一下，但你没有停。"
    narrator "扫弦继续走，差了那么一点点，但整首歌没有断。"
    inner "（真正演奏的时候，出错了也要继续。）"
    jump guitar_song_end_good


label guitar_song_end_good:

    $ guitar_song_chorus = True

    scene bg_guitar_room with dissolve

    narrator "最后一个 F 和弦——"
    pause 0.8
    narrator "扫下去——"
    pause 1.5

    centered "{size=28}{color=#ffe97f}🎸  弹完了{/color}{/size}"
    pause 2.0

    scene bg_guitar_room with dissolve

    narrator "琴弦的余音在房间里散开。"
    pause 1.0
    narrator "不完美。"
    narrator "有几次切换慢了，有一个 F 卡了一下。"
    pause 0.8
    narrator "但那是一首完整的歌。"
    narrator "从头，到尾。"
    pause 1.0

    inner "（是你弹出来的。）"

    pause 1.5

    menu:
        "再弹一遍，这次更好":
            jump guitar_play_song
        "放下吉他，在访客本上留点什么":
            jump guitar_leave_message
        "就这样，悄悄离开":
            jump guitar_silent_leave


## ============================================================
## 留言
## ============================================================
label guitar_leave_message:

    scene bg_guitar_room with dissolve

    narrator "你找到一张便利贴，想写点什么。"

    menu:
        "「第[guitar_practice_days]天，弹完了一首歌。」":
            $ guitar_note = "第" + str(guitar_practice_days) + "天，弹完了一首歌。"
            jump guitar_ending_with_note

        "「F 和弦，没有想象中那么难。」":
            $ guitar_note = "F 和弦，没有想象中那么难。"
            jump guitar_ending_with_note

        "「开始之前总以为很难，开始之后才知道只要坚持。」":
            $ guitar_note = "开始之前总以为很难，开始之后才知道只要坚持。"
            jump guitar_ending_with_note

        "什么都不写":
            jump guitar_silent_leave


label guitar_ending_with_note:

    scene bg_guitar_room with dissolve

    narrator "你把便利贴贴在吉他盒上。"
    narrator "「[guitar_note]」"
    pause 1.0

    inner "（留给下次练琴的自己看。）"

    jump guitar_final


label guitar_silent_leave:

    scene bg_guitar_room with dissolve

    narrator "你把吉他放回墙角。"
    narrator "房间里还留着扫弦的余韵。"
    pause 1.0

    jump guitar_final


## ============================================================
## 结局
## ============================================================
label guitar_final:

    scene black with fade

    centered "{size=20}{color=#aaaaaa}你离开了这个练琴的房间{/color}{/size}"
    pause 1.5

    if guitar_song_chorus:
        centered "{size=16}{color=#ffe97f}🎸  弹完了一首歌{/color}{/size}"
        pause 1.0
        centered "{size=14}{color=#666666}C → G → Am → F\n那是学吉他第[guitar_practice_days]天{/color}{/size}"
    elif guitar_chord_f:
        centered "{size=16}{color=#666666}四个和弦都学了\n离弹完一首歌，只差练习的时间{/color}{/size}"
    else:
        centered "{size=16}{color=#666666}开始了。\n这已经是最难的一步了。{/color}{/size}"

    pause 2.0
    scene black with fade
    pause 0.5

    jump world_select


## ============================================================
## 未完成时直接离开
## ============================================================
label guitar_leave:

    scene bg_guitar_room with dissolve

    if not guitar_chord_c:
        narrator "吉他还靠在墙边，没有动过。"
        inner "（随时可以回来。）"
    elif guitar_song_chorus:
        narrator "吉他靠在墙边，已经弹出了一首曲子。"
        inner "（还会再来的。）"
    else:
        narrator "还有些和弦没有练完。"
        narrator "但今天到这里也不错了。"
        inner "（明天继续。）"

    jump guitar_final
