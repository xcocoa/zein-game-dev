## ============================================================
## 吉他指板交互界面
## guitar_screen.rpy
##
## 布局（1280×720）：
##   上方：状态提示区（任务说明、当前反馈）
##   中间：可点击指板（6弦×5品 + 空弦列）
##   下方：扫弦按钮区 + 操作说明
## ============================================================

## ─────────────────────────────────────────────
## 运行时变量（每次进入 screen 前重置）
## ─────────────────────────────────────────────
default fret_pressed = {}        ## {(string, fret): True} 当前按住的品格
default last_played_note = ""    ## 最近一次弹奏的文字反馈
default strum_result = ""        ## 扫弦后的结果文字
default fret_feedback = ""       ## 点击品格后的小提示
default guitar_screen_task = ""  ## 本次 screen 的任务描述（外部传入）

## 音符名称表：(弦号1-6, 品格0-5) → 音名
## 弦序：1=最细高音弦(e), 6=最粗低音弦(E)
## 品格0=空弦
define GUITAR_NOTES = {
    ## 第1弦 e
    (1,0):"e",  (1,1):"F",  (1,2):"F#", (1,3):"G",  (1,4):"G#", (1,5):"A",
    ## 第2弦 B
    (2,0):"B",  (2,1):"C",  (2,2):"C#", (2,3):"D",  (2,4):"D#", (2,5):"E",
    ## 第3弦 G
    (3,0):"G",  (3,1):"G#", (3,2):"A",  (3,3):"A#", (3,4):"B",  (3,5):"C",
    ## 第4弦 D
    (4,0):"D",  (4,1):"D#", (4,2):"E",  (4,3):"F",  (4,4):"F#", (4,5):"G",
    ## 第5弦 A
    (5,0):"A",  (5,1):"A#", (5,2):"B",  (5,3):"C",  (5,4):"C#", (5,5):"D",
    ## 第6弦 E（低音）
    (6,0):"E",  (6,1):"F",  (6,2):"F#", (6,3):"G",  (6,4):"G#", (6,5):"A",
}

## 和弦定义：和弦名 → {弦号: 品格}（不在字典中的弦=不拨）
define CHORD_SHAPES = {
    "C":  {1:0, 2:1, 3:0, 4:2, 5:3},          ## 不拨第6弦
    "G":  {1:3, 2:0, 3:0, 4:0, 5:2, 6:3},
    "Am": {1:0, 2:1, 3:2, 4:2, 5:0},           ## 不拨第6弦
    "F":  {1:1, 2:1, 3:2, 4:3, 5:3, 6:1},      ## 封闭和弦
    "Em": {1:0, 2:0, 3:0, 4:2, 5:2, 6:0},
    "Dm": {1:1, 2:3, 3:2, 4:0},                 ## 仅1-4弦
}

## ─────────────────────────────────────────────
## 样式定义
## ─────────────────────────────────────────────
style fret_button:
    xysize (72, 52)
    background "#2a1a0a"
    hover_background "#5a3a18"
    selected_background "#c8860a"
    insensitive_background "#1a0f05"
    padding (0, 0, 0, 0)

style fret_button_text:
    size 13
    color "#c8a060"
    hover_color "#ffe097"
    selected_color "#fff0b0"
    xalign 0.5
    yalign 0.5

style open_string_button:
    xysize (52, 52)
    background "#1e3a1e"
    hover_background "#2e5a2e"
    selected_background "#3a8a3a"
    padding (0, 0, 0, 0)

style open_string_button_text:
    size 13
    color "#80c080"
    hover_color "#aaffaa"
    selected_color "#ccffcc"
    xalign 0.5
    yalign 0.5

style strum_button:
    xysize (160, 52)
    background "#1a2a4a"
    hover_background "#2a4a7a"
    padding (4, 4, 4, 4)

style strum_button_text:
    size 16
    color "#80aaff"
    hover_color "#aaccff"
    xalign 0.5
    yalign 0.5

style guitar_feedback_text:
    size 17
    color "#ffe097"
    xalign 0.5

style guitar_task_text:
    size 15
    color "#aaddaa"
    xalign 0.5

style guitar_note_label:
    size 12
    color "#666666"
    xalign 0.5
    yalign 0.5

## ─────────────────────────────────────────────
## 工具函数：判断当前按弦是否匹配指定和弦
## ─────────────────────────────────────────────
init python:
    def check_chord_match(pressed, chord_name):
        """
        检查 pressed（{(string,fret): True}）是否与和弦定义一致。
        返回 (bool, str)：是否匹配，以及反馈文字
        """
        shape = CHORD_SHAPES.get(chord_name, {})
        if not shape:
            return False, "未知和弦"

        errors = []
        for string_num, required_fret in shape.items():
            # 找到这根弦上按的品格（可能是0即空弦，或某品格）
            pressed_fret = None
            for (s, f), v in pressed.items():
                if s == string_num and v:
                    pressed_fret = f
                    break
            if pressed_fret is None:
                pressed_fret = 0  # 没按=空弦

            if pressed_fret != required_fret:
                errors.append("第{}弦应按{}品".format(string_num, required_fret if required_fret > 0 else "空弦"))

        if not errors:
            return True, "✓ {} 和弦，手型正确！".format(chord_name)
        else:
            return False, "差一点：" + "、".join(errors[:2])

    def get_pressed_notes(pressed):
        """获取当前按弦状态下的音名列表（按弦6→1顺序）"""
        notes = []
        for s in range(6, 0, -1):
            fret = 0
            for (st, f), v in pressed.items():
                if st == s and v:
                    fret = f
                    break
            note = GUITAR_NOTES.get((s, fret), "?")
            notes.append(note)
        return notes

    def toggle_fret(pressed_dict, string_num, fret_num):
        """切换某品格的按压状态，同一弦上同时只能按一个品"""
        new_dict = dict(pressed_dict)
        # 清除同一弦上的其他品格
        for (s, f) in list(new_dict.keys()):
            if s == string_num:
                del new_dict[(s, f)]
        # 如果原来就是这个位置，则松开（不写入=松开）
        key = (string_num, fret_num)
        old_val = pressed_dict.get(key, False)
        if not old_val:
            new_dict[key] = True
        return new_dict

    def apply_chord_shape(chord_name):
        """直接应用整个和弦手型，返回新的 pressed 字典"""
        shape = CHORD_SHAPES.get(chord_name, {})
        new_dict = {}
        for string_num, fret_num in shape.items():
            if fret_num > 0:
                new_dict[(string_num, fret_num)] = True
        return new_dict


## ─────────────────────────────────────────────
## 主 Screen：guitar_fretboard
## 参数：
##   task_text  — 顶部任务说明
##   target_chord — 目标和弦名（""=自由弹奏模式）
##   exit_label — 完成/退出后跳转的 label
## ─────────────────────────────────────────────
screen guitar_fretboard(task_text="自由弹奏", target_chord="", exit_label="guitar_room_main"):

    ## 防止点击穿透到对话层
    modal True

    ## ── 背景遮罩 ──
    add "#000000cc"

    ## ── 整体容器，垂直居中 ──
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

        ## ── 任务说明 ──
        frame:
            xalign 0.5
            xsize 780
            ysize 44
            background "#00000088"
            padding (12, 6, 12, 6)
            text task_text style "guitar_task_text"

        ## ── 反馈区 ──
        frame:
            xalign 0.5
            xsize 780
            ysize 40
            background "#00000066"
            padding (12, 4, 12, 4)
            text "[fret_feedback]" style "guitar_feedback_text"

        ## ── 指板主体 ──
        frame:
            xalign 0.5
            background "#1a0d05ee"
            padding (16, 12, 16, 12)

            vbox:
                spacing 0

                ## 品格标题行
                hbox:
                    spacing 0
                    ## 弦名列占位
                    frame:
                        xysize (36, 24)
                        background "#00000000"
                        text "" size 12 xalign 0.5

                    ## 空弦列标题
                    frame:
                        xysize (52, 24)
                        background "#00000000"
                        text "空弦" style "guitar_note_label"

                    ## 品格号标题
                    for fret_num in [1, 2, 3, 4, 5]:
                        frame:
                            xysize (72, 24)
                            background "#00000000"
                            text "{}品".format(fret_num) style "guitar_note_label"

                ## 6根弦（从1弦到6弦，1弦在上）
                for string_num in [1, 2, 3, 4, 5, 6]:
                    hbox:
                        spacing 0

                        ## 弦名标签
                        frame:
                            xysize (36, 52)
                            background "#0f0804"
                            text ["e","B","G","D","A","E"][string_num-1]:
                                size 14
                                color "#aa8844"
                                xalign 0.5
                                yalign 0.5

                        ## 空弦按钮（品格0）
                        button:
                            style "open_string_button"
                            selected fret_pressed.get((string_num, 0), False)
                            action [
                                SetVariable("fret_pressed", toggle_fret(fret_pressed, string_num, 0)),
                                SetVariable("fret_feedback", "第{}弦 空弦 → {}".format(
                                    string_num,
                                    GUITAR_NOTES.get((string_num, 0), "?")
                                )),
                                SetVariable("strum_result", ""),
                            ]
                            text GUITAR_NOTES.get((string_num, 0), "?") style "open_string_button_text"

                        ## 品格1-5
                        for fret_num in [1, 2, 3, 4, 5]:
                            python:
                                _is_pressed = fret_pressed.get((string_num, fret_num), False)
                                _note_name = GUITAR_NOTES.get((string_num, fret_num), "?")
                            button:
                                style "fret_button"
                                selected _is_pressed
                                action [
                                    SetVariable("fret_pressed", toggle_fret(fret_pressed, string_num, fret_num)),
                                    SetVariable("fret_feedback", "第{}弦 {}品 → {}".format(
                                        string_num, fret_num, _note_name
                                    )),
                                    SetVariable("strum_result", ""),
                                ]
                                text _note_name style "fret_button_text"

        ## ── 扫弦 + 和弦检测区 ──
        hbox:
            xalign 0.5
            spacing 16

            ## 向下扫弦
            button:
                style "strum_button"
                action [
                    SetVariable("strum_result", "↓ " + " ".join(get_pressed_notes(fret_pressed))),
                    SetVariable("fret_feedback", "↓ 扫弦：" + "  ".join(get_pressed_notes(fret_pressed))),
                ]
                text "↓ 扫弦" style "strum_button_text"

            ## 向上扫弦
            button:
                style "strum_button"
                action [
                    SetVariable("strum_result", "↑ " + " ".join(reversed(get_pressed_notes(fret_pressed)))),
                    SetVariable("fret_feedback", "↑ 扫弦：" + "  ".join(reversed(get_pressed_notes(fret_pressed)))),
                ]
                text "↑ 扫弦" style "strum_button_text"

            ## 检查和弦（有目标和弦时才显示）
            if target_chord:
                button:
                    style "strum_button"
                    background "#2a1a3a"
                    hover_background "#4a2a6a"
                    action [
                        SetVariable("fret_feedback",
                            check_chord_match(fret_pressed, target_chord)[1]
                        ),
                    ]
                    text "检查 {} 和弦".format(target_chord) style "strum_button_text"

                ## 显示标准手型（提示）
                button:
                    style "strum_button"
                    background "#1a2a1a"
                    hover_background "#2a4a2a"
                    action [
                        SetVariable("fret_pressed", apply_chord_shape(target_chord)),
                        SetVariable("fret_feedback", "已显示 {} 标准手型，试试扫弦听听效果".format(target_chord)),
                        SetVariable("strum_result", ""),
                    ]
                    text "查看手型提示" style "strum_button_text"

            ## 清空
            button:
                style "strum_button"
                background "#2a1a1a"
                hover_background "#4a2a2a"
                action [
                    SetVariable("fret_pressed", {}),
                    SetVariable("fret_feedback", "清空了所有按弦"),
                    SetVariable("strum_result", ""),
                ]
                text "✕ 松开所有弦" style "strum_button_text"

        ## ── 底部：完成/退出按钮 ──
        hbox:
            xalign 0.5
            spacing 24

            if target_chord:
                ## 确认完成（要通过检查才能完成）
                button:
                    xysize (200, 48)
                    background "#1a3a1a"
                    hover_background "#2a5a2a"
                    padding (8, 8, 8, 8)
                    sensitive check_chord_match(fret_pressed, target_chord)[0]
                    action [
                        Hide("guitar_fretboard"),
                        Jump(exit_label),
                    ]
                    text "✓ 弹对了，继续" xalign 0.5 yalign 0.5 size 15 color "#88dd88" hover_color "#aaffaa"

            ## 不带目标时的完成按钮
            if not target_chord:
                button:
                    xysize (200, 48)
                    background "#1a3a1a"
                    hover_background "#2a5a2a"
                    padding (8, 8, 8, 8)
                    action [
                        Hide("guitar_fretboard"),
                        Jump(exit_label),
                    ]
                    text "完成练习" xalign 0.5 yalign 0.5 size 15 color "#88dd88"

            ## 退出不保存
            button:
                xysize (160, 48)
                background "#3a1a1a"
                hover_background "#5a2a2a"
                padding (8, 8, 8, 8)
                action [
                    Hide("guitar_fretboard"),
                    Jump("guitar_room_main"),
                ]
                text "先不练了" xalign 0.5 yalign 0.5 size 15 color "#dd8888"

        ## ── 操作说明 ──
        frame:
            xalign 0.5
            xsize 780
            ysize 34
            background "#00000055"
            padding (12, 4, 12, 4)
            text "点击格子按弦（再次点击松开）· 同一弦只能按一个品 · 空弦格=不按品格直接拨":
                size 12
                color "#555555"
                xalign 0.5
                yalign 0.5


## ─────────────────────────────────────────────
## 自由弹奏模式（无任务，随便探索）
## ─────────────────────────────────────────────
label guitar_free_play:
    $ fret_pressed = {}
    $ fret_feedback = "点击格子按弦，然后扫弦听听效果"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="🎸 自由弹奏 · 随便探索，没有对错",
        target_chord="",
        exit_label="guitar_room_main"
    )
    pause  ## 等待 screen 内的 Jump 触发
    return


## ─────────────────────────────────────────────
## 指定和弦练习（带检查）
## ─────────────────────────────────────────────
label guitar_interactive_c:
    $ fret_pressed = {}
    $ fret_feedback = "试着按出 C 和弦：食指1弦1品，中指2弦1品，无名指4弦2品，小指5弦3品（可查看手型提示）"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="练习 C 和弦 · 按对手型后扫弦，再点「弹对了，继续」",
        target_chord="C",
        exit_label="guitar_c_interactive_done"
    )
    pause
    return

label guitar_c_interactive_done:
    $ guitar_chord_c = True
    $ guitar_practice_days += 1
    narrator "C 和弦——你自己按出来了。"
    inner "（不只是知道怎么按，而是真的按到了。）"
    jump guitar_practice_menu


label guitar_interactive_g:
    $ fret_pressed = {}
    $ fret_feedback = "试着按出 G 和弦：中指6弦3品，食指5弦2品，无名指1弦3品（可查看手型提示）"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="练习 G 和弦 · 手指要撑开，按对后扫弦确认",
        target_chord="G",
        exit_label="guitar_g_interactive_done"
    )
    pause
    return

label guitar_g_interactive_done:
    $ guitar_chord_g = True
    $ guitar_practice_days += 1
    narrator "G 和弦，拿下了。"
    inner "（虎口要撑开那种感觉——）"
    jump guitar_practice_menu


label guitar_interactive_am:
    $ fret_pressed = {}
    $ fret_feedback = "试着按出 Am 和弦：食指2弦1品，中指3弦2品，无名指4弦2品（可查看手型提示）"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="练习 Am 和弦 · 有点忧郁感的小调",
        target_chord="Am",
        exit_label="guitar_am_interactive_done"
    )
    pause
    return

label guitar_am_interactive_done:
    $ guitar_chord_am = True
    $ guitar_practice_days += 1
    narrator "Am，很有感觉。"
    inner "（小调总是带着点什么。）"
    jump guitar_practice_menu


label guitar_interactive_f:
    $ fret_pressed = {}
    $ fret_feedback = "F 和弦最难：食指横按1-6弦1品（封闭），中指3弦2品，无名指4弦3品，小指5弦3品"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="练习 F 和弦（封闭和弦）· 最难的一关，可以先看手型提示",
        target_chord="F",
        exit_label="guitar_f_interactive_done"
    )
    pause
    return

label guitar_f_interactive_done:
    $ guitar_chord_f = True
    $ guitar_practice_days += 1
    narrator "F 和弦，按实了。"
    pause 0.5
    narrator "这一下，是真的过了。"
    inner "（封闭和弦——所有人的第一道坎。）"
    jump guitar_practice_menu


## 自由弹奏进入的和弦试弹（用于演奏环节）
label guitar_interactive_free_song:
    $ fret_pressed = {}
    $ fret_feedback = "按出你想要的和弦，然后扫弦感受一下"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="🎵 演奏《等你下课》· 按顺序弹出 C → G → Am → F",
        target_chord="",
        exit_label="guitar_song_free_continue"
    )
    pause
    return

label guitar_song_free_continue:
    jump guitar_play_song
