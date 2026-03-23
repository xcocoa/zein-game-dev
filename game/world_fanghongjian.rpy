## ============================================================
## 世界二：方鸿渐的某个下午
## 改编自钱钟书《围城》
## ============================================================

label world_fanghongjian:

    scene black with fade

    centered "{size=20}{color=#aaaaaa}正在进入方鸿渐的世界...{/color}{/size}"
    pause 1.5
    centered "{size=16}{color=#666666}1947年 · 梅雨季 · 上海 · 某个下午{/color}{/size}"
    pause 1.5

    scene bg_hongjian_room with dissolve

    narrator "雨下了三天了。"
    narrator "亭子间的窗玻璃蒙着一层水汽，外面的弄堂是模糊的灰。"
    narrator "房间里有一张旧书桌，一把吱呀作响的椅子，一床叠得不算整齐的被褥。"
    narrator "桌上摊着一张信纸，写了一半，墨迹还新。"

    inner "（他刚才在这里坐着。）"
    inner "（或许出去买烟了。）"

    narrator "窗外的雨声很均匀，像是有人在屋顶上轻轻踱步。"

    menu:
        "走近书桌，看那封信":
            jump hongjian_letter
        "看看书桌上的其他东西":
            jump hongjian_desk
        "走到窗边，看雨":
            jump hongjian_window


## 那封信
label hongjian_letter:

    scene bg_hongjian_room with dissolve

    narrator "你凑近看——"
    narrator "信纸上的字是毛笔写的，字迹工整，带着一点刻意的从容。"
    pause 0.8
    narrator "  「文纨，展信如晤。近日沪上梅雨连绵，……」"
    pause 1.0
    narrator "写到这里停了。"
    narrator "后面空着，笔搁在砚台边上，墨还没干透。"

    inner "（他不知道接下来写什么。）"
    inner "（或者说，他知道，但不想写。）"

    narrator "信纸的左下角，有一个被涂掉的名字。"
    narrator "涂了三层，彻底看不出来了。"
    narrator "但你猜得到。"

    inner "（不是苏文纨。）"

    menu:
        "翻看桌上的书":
            jump hongjian_desk
        "走到窗边，看雨":
            jump hongjian_window
        "在访客本上留下一句话":
            jump hongjian_leave_message


## 书桌上的东西
label hongjian_desk:

    scene bg_hongjian_room with dissolve

    narrator "书桌不大，但东西不少。"
    narrator "一摞书——几本英文原版，几本中文，书脊上有折痕，像是翻过很多次，又像是摆着好看的。"
    narrator "一个烟灰缸，里面有两个烟蒂。"
    narrator "一张照片，翻过去扣着，看不见正面。"

    inner "（他把照片翻过去了。）"

    narrator "你没有去翻它。"
    pause 0.8
    narrator "桌角还有一张折叠的报纸，是三天前的，头版是什么经济消息，没人在乎。"
    narrator "报纸边上压着一个文凭——是假的，你一眼就看出来了，烫金的字有点歪。"

    inner "（他自己也知道是假的。）"
    inner "（所以才压在报纸下面。）"

    menu:
        "看那封未写完的信":
            jump hongjian_letter
        "走到窗边，看雨":
            jump hongjian_window
        "在访客本上留下一句话":
            jump hongjian_leave_message


## 窗边看雨
label hongjian_window:

    scene bg_hongjian_window with dissolve

    narrator "雨顺着窗玻璃往下流，把弄堂里的一切都化成了水墨。"
    narrator "对面的墙壁，晾衣竿上一件蓝布衫，一个跑过去躲雨的小孩。"
    pause 1.0
    narrator "你站在这里，想象他每天下午都看着同一面墙。"

    inner "（他读过书，留过洋，回来之后——）"
    inner "（回来之后还是坐在这个亭子间里，看这面墙。）"

    narrator "雨声里有人在楼下打麻将，牌声啪啪的，很响。"
    narrator "还有人在争什么，声音很快就淹没在雨声里了。"

    narrator "这个城市对他来说太大，又太小。"
    narrator "大到装得下所有的可能性，小到哪里都是认识的人和说不清楚的事。"

    inner "（围城。）"
    inner "（城外的人想进来，城里的人想出去。）"

    menu:
        "看那封未写完的信":
            jump hongjian_letter
        "看看书桌上的其他东西":
            jump hongjian_desk
        "在访客本上留下一句话":
            jump hongjian_leave_message


## 留言
label hongjian_leave_message:

    scene bg_hongjian_room with dissolve

    narrator "访客本放在门背后，是个旧本子，封面有水渍。"
    narrator "你翻开，想写点什么。"

    menu:
        "「门是开着的。」":
            $ hongjian_message = "门是开着的。"
            jump hongjian_ending_message

        "「城里城外，都是人。」":
            $ hongjian_message = "城里城外，都是人。"
            jump hongjian_ending_message

        "「那封信，还是写完吧。」":
            $ hongjian_message = "那封信，还是写完吧。"
            jump hongjian_ending_message

        "什么都不写":
            jump hongjian_silent_leave


label hongjian_ending_message:

    scene bg_hongjian_room with dissolve

    narrator "你写下：「[hongjian_message]」"
    pause 0.8
    narrator "合上本子，放回原处。"

    inner "（他回来之后会看见吗？）"
    inner "（或者他根本不会注意到这个本子。）"

    jump hongjian_final


label hongjian_silent_leave:

    scene bg_hongjian_room with dissolve

    narrator "你什么都没写。"
    pause 0.5
    narrator "有些事不需要旁观者的评语。"

    jump hongjian_final


label hongjian_final:

    scene black with fade

    centered "{size=20}{color=#aaaaaa}你离开了方鸿渐的世界{/color}{/size}"
    pause 1.5
    centered "{size=16}{color=#666666}那封信最终没有寄出去\n三个月后他离开了上海\n{/color}{/size}"
    pause 1.0
    centered "{size=14}{color=#555555}改编自钱钟书《围城》{/color}{/size}"
    pause 2.0

    scene black with fade
    pause 0.5

    jump world_select
