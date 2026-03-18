## ============================================================
## 《世界碎片》 World Fragments - Demo
## 核心体验：进入陌生人的世界，感受她某一天的生活
## ============================================================

define narrator = Character(None, what_style="narrator_text")
define you = Character("你", color="#c8c8ff")
define inner = Character(None, what_style="inner_voice")

## 样式定义
style narrator_text:
    size 22
    color "#e8e8e8"
    line_spacing 8

style inner_voice:
    size 20
    color "#aaddcc"
    italic True
    line_spacing 8

## ============================================================
## 主菜单入口
## ============================================================
label start:

    scene black with fade

    ## 片头字幕
    centered "{size=28}{color=#ffffff}每个人都活在自己的世界里{/color}{/size}"
    pause 2.0

    centered "{size=22}{color=#aaaaaa}但有时候，你可以悄悄走进去看看{/color}{/size}"
    pause 2.0

    scene black with fade
    pause 0.5

    jump world_select


## ============================================================
## 世界选择界面
## ============================================================
label world_select:

    scene black with dissolve

    centered "{size=30}{color=#ffffff}🌍  世界碎片{/color}{/size}\n\n{size=18}{color=#888888}World Fragments · Demo{/color}{/size}"

    pause 1.5

    narrator "你面前有一些被人遗落在这里的世界碎片。"
    narrator "它们的主人或许并不知道你会来。"
    narrator "你想进入哪一个？"

    menu:
        "📷  林晓的周五下午 · 一个摄影学生的房间":
            jump world_linxiao

        "📖  〔未解锁〕来自陌生城市的流水账":
            jump world_locked

        "🌙  〔未解锁〕失眠者的凌晨三点":
            jump world_locked

        "← 什么都不想看，离开":
            jump ending_leave


## ============================================================
## 世界一：林晓的周五下午
## ============================================================
label world_linxiao:

    scene black with fade

    ## 进入提示
    centered "{size=20}{color=#aaaaaa}正在进入林晓的世界...{/color}{/size}"
    pause 1.5
    centered "{size=16}{color=#666666}周五 · 下午 15:47 · 她的房间{/color}{/size}"
    pause 1.5

    ## 场景：房间，下午
    scene bg_room with dissolve

    narrator "下午三点四十七分。"
    narrator "光从百叶窗的缝隙里挤进来，在地板上切出几道细细的亮纹。"
    narrator "空气里有一点樟脑球的气味，还有什么——咖啡？不对，是泡面。"

    inner "（她刚才吃了泡面。）"

    narrator "桌上摊着一本笔记本，翻开的那页写着密密麻麻的字，看不清内容，但字很漂亮。"
    narrator "床边有一双拖鞋，一只正着，一只歪着。"
    narrator "窗台上有一盆仙人掌，很小，像是刚买来没多久的那种。"

    menu:
        "走近桌子，看看那本笔记本":
            jump linxiao_notebook
        "看向窗外":
            jump linxiao_window
        "拿起桌上的相机":
            jump linxiao_camera


## 笔记本
label linxiao_notebook:

    scene bg_room with dissolve

    narrator "你靠近了一点。"
    narrator "笔记本上写的是——课程表？不，是一张清单。"
    narrator ""
    narrator "  周五要做的事：\n  □ 交摄影作业\n  □ 给妈妈发消息\n  □ 买猫粮（！！）\n  □ 睡够八小时（上次写这个是一个月前）"

    inner "（她养猫。）"
    inner "（睡不够八小时。）"

    narrator "清单的边角画着一只很潦草的猫，猫的旁边写着「汤圆」。"

    menu:
        "继续在房间里逛逛":
            jump linxiao_room_continue
        "在访客本上留下一句话":
            jump linxiao_leave_message


## 窗外
label linxiao_window:

    scene bg_window with dissolve

    narrator "你走到窗边。"
    narrator "外面是一条普通的街道，一棵不知名的树，两辆停着的电动车。"
    narrator "没什么特别的。"
    narrator "但光很好。"
    narrator "那种下午快四点的光，有点懒，有点金，照在任何东西上都显得有点不真实。"

    inner "（她每天下午都看这个。）"
    inner "（或许正是这个光让她喜欢摄影的。）"

    narrator "窗台上的仙人掌刚好挡住了一辆车，构成一个意外的小景。"
    narrator "你忽然觉得，这个人的眼睛一定不错。"

    menu:
        "继续在房间里逛逛":
            jump linxiao_room_continue
        "在访客本上留下一句话":
            jump linxiao_leave_message


## 相机
label linxiao_camera:

    scene bg_camera with dissolve

    narrator "相机是一台旧的胶片机，表面有几道划痕，背带上绑着一个小吊坠——是个橡皮鸭。"
    narrator "你没有动它，只是凑近看了看。"
    narrator "取景框里还有上一次构图留下的影子。"

    inner "（相机的快门按了很多次了。）"
    inner "（划痕不是摔的，是用旧的。）"

    narrator "你想象她举起这台相机的样子。"
    narrator "大概是半蹲着，或者踮起脚，眯起一只眼睛。"

    menu:
        "继续在房间里逛逛":
            jump linxiao_room_continue
        "在访客本上留下一句话":
            jump linxiao_leave_message


## 房间继续探索
label linxiao_room_continue:

    scene bg_room with dissolve

    narrator "你在房间里又站了一会儿。"
    narrator "没有什么特别的事情发生。"
    narrator "但你说不清楚为什么，感觉自己好像真的来过这里。"

    pause 1.0

    narrator "角落里有一只猫窝，毛茸茸的，空的。"
    narrator "汤圆现在不知道在哪儿。"

    inner "（可能在床底下。）"

    menu:
        "在访客本上留下一句话":
            jump linxiao_leave_message
        "悄悄离开，不打扰":
            jump linxiao_silent_leave


## 留言
label linxiao_leave_message:

    scene bg_room with dissolve

    narrator "访客本放在门边的小架子上，已经有几行字了。"
    narrator "你拿起笔，想了想，写下一句话。"

    menu:
        "「汤圆应该很好玩。」":
            $ player_message = "汤圆应该很好玩。"
            jump linxiao_ending_message

        "「那盆仙人掌的位置很好。」":
            $ player_message = "那盆仙人掌的位置很好。"
            jump linxiao_ending_message

        "「谢谢你的光。」":
            $ player_message = "谢谢你的光。"
            jump linxiao_ending_message

        "什么都不写，合上本子":
            jump linxiao_silent_leave


label linxiao_ending_message:

    scene bg_room with dissolve

    narrator "你写下了：「[player_message]」"
    pause 0.8
    narrator "然后把笔放回去。"

    inner "（她不一定会看。）"
    inner "（但你留下了。）"

    jump linxiao_final


label linxiao_silent_leave:

    scene bg_room with dissolve

    narrator "你没有留下任何东西。"
    narrator "就像你从来没来过一样。"
    narrator "但你来过。"

    jump linxiao_final


label linxiao_final:

    scene black with fade

    centered "{size=20}{color=#aaaaaa}你离开了林晓的世界{/color}{/size}"
    pause 1.5
    centered "{size=16}{color=#666666}她今天下午 18:23 完成了摄影作业\n还忘了给妈妈发消息{/color}{/size}"
    pause 2.5

    scene black with fade
    pause 0.5

    jump world_select


## ============================================================
## 未解锁世界
## ============================================================
label world_locked:

    narrator "这个世界还没有准备好迎接访客。"
    narrator "或许它的主人还没决定是否愿意被人看见。"
    pause 1.0
    jump world_select


## ============================================================
## 离开结局
## ============================================================
label ending_leave:

    scene black with fade

    narrator "你没有走进任何人的世界。"
    pause 1.0
    narrator "这也是一种选择。"
    pause 1.5

    centered "{size=24}{color=#888888}《世界碎片》 Demo{/color}{/size}\n\n{size=16}{color=#555555}真正的游戏里，这些世界都是真实的人留下的{/color}{/size}"

    pause 2.0

    return
