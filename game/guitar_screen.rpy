## ============================================================
## 吉他指板交互界面
## guitar_screen.rpy
## ============================================================

## ─────────────────────────────────────────────
## 运行时变量
## ─────────────────────────────────────────────
default fret_pressed = {}
default last_played_note = ""
default strum_result = ""
default fret_feedback = ""
default guitar_screen_task = ""

## 音符名称表：(弦号1-6, 品格0-5) → 音名（显示用）
define GUITAR_NOTES = {
    (1,0):"e",  (1,1):"F",  (1,2):"F#", (1,3):"G",  (1,4):"G#", (1,5):"A",
    (2,0):"B",  (2,1):"C",  (2,2):"C#", (2,3):"D",  (2,4):"D#", (2,5):"E",
    (3,0):"G",  (3,1):"G#", (3,2):"A",  (3,3):"A#", (3,4):"B",  (3,5):"C",
    (4,0):"D",  (4,1):"D#", (4,2):"E",  (4,3):"F",  (4,4):"F#", (4,5):"G",
    (5,0):"A",  (5,1):"A#", (5,2):"B",  (5,3):"C",  (5,4):"C#", (5,5):"D",
    (6,0):"E",  (6,1):"F",  (6,2):"F#", (6,3):"G",  (6,4):"G#", (6,5):"A",
}

## 指板音符 → 音效文件名（含八度）
define FRET_SOUND_MAP = {
    (1,0):"E4",  (1,1):"F4",   (1,2):"F#4", (1,3):"G4",  (1,4):"G#4", (1,5):"A4",
    (2,0):"B3",  (2,1):"C4",   (2,2):"C#4", (2,3):"D4",  (2,4):"D#4", (2,5):"E4",
    (3,0):"G3",  (3,1):"G#3",  (3,2):"A3",  (3,3):"A#3", (3,4):"B3",  (3,5):"C4",
    (4,0):"D3",  (4,1):"D#3",  (4,2):"E3",  (4,3):"F3",  (4,4):"F#3", (4,5):"G3",
    (5,0):"A2",  (5,1):"A#2",  (5,2):"B2",  (5,3):"C3",  (5,4):"C#3", (5,5):"D3",
    (6,0):"E2",  (6,1):"F2",   (6,2):"F#2", (6,3):"G2",  (6,4):"G#2", (6,5):"A2",
}

## 和弦定义：和弦名 → {弦号: 品格}
define CHORD_SHAPES = {
    "C":  {1:0, 2:1, 3:0, 4:2, 5:3},
    "G":  {1:3, 2:0, 3:0, 4:0, 5:2, 6:3},
    "Am": {1:0, 2:1, 3:2, 4:2, 5:0},
    "F":  {1:1, 2:1, 3:2, 4:3, 5:3, 6:1},
    "Em": {1:0, 2:0, 3:0, 4:2, 5:2, 6:0},
    "Dm": {1:1, 2:3, 3:2, 4:0},
}

## ─────────────────────────────────────────────
## 样式
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

## 目标品格高亮（绿色提示）
style fret_button_target:
    xysize (72, 52)
    background "#1a3a1a"
    hover_background "#2a5a2a"
    selected_background "#3aaa3a"
    padding (0, 0, 0, 0)

style fret_button_target_text:
    size 13
    color "#88dd88"
    hover_color "#aaffaa"
    selected_color "#ccffcc"
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
## 工具函数
## ─────────────────────────────────────────────
init python:
    def check_chord_match(pressed, chord_name):
        shape = CHORD_SHAPES.get(chord_name, {})
        if not shape:
            return False, "未知和弦"
        errors = []
        for string_num, required_fret in shape.items():
            pressed_fret = 0
            for (s, f), v in pressed.items():
                if s == string_num and v:
                    pressed_fret = f
                    break
            if pressed_fret != required_fret:
                errors.append("第{}弦".format(string_num))
        if not errors:
            return True, "✓ {} 和弦正确！".format(chord_name)
        else:
            return False, "还差：" + "、".join(errors[:3]) + " 没按对"

    def get_pressed_notes(pressed):
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
        new_dict = dict(pressed_dict)
        for (s, f) in list(new_dict.keys()):
            if s == string_num:
                del new_dict[(s, f)]
        key = (string_num, fret_num)
        if not pressed_dict.get(key, False):
            new_dict[key] = True
        return new_dict

    def apply_chord_shape(chord_name):
        shape = CHORD_SHAPES.get(chord_name, {})
        new_dict = {}
        for string_num, fret_num in shape.items():
            if fret_num > 0:
                new_dict[(string_num, fret_num)] = True
        return new_dict

    def get_fret_sound(string_num, fret_num):
        """返回音效文件路径"""
        note = FRET_SOUND_MAP.get((string_num, fret_num), "E4")
        return "audio/note_{}.wav".format(note)

    def is_target_fret(string_num, fret_num, chord_name):
        """判断某个品格是否是目标和弦需要按的位置"""
        if not chord_name:
            return False
        shape = CHORD_SHAPES.get(chord_name, {})
        return shape.get(string_num, -1) == fret_num and fret_num > 0

    def is_target_open(string_num, chord_name):
        """判断某根弦是否是目标和弦的空弦位"""
        if not chord_name:
            return False
        shape = CHORD_SHAPES.get(chord_name, {})
        return shape.get(string_num, -1) == 0


## ─────────────────────────────────────────────
## 主 Screen：guitar_fretboard
## ─────────────────────────────────────────────
screen guitar_fretboard(task_text="自由弹奏", target_chord="", exit_label="guitar_room_main"):

    modal True
    add "#000000cc"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14

        ## ── 任务说明 ──
        frame:
            xalign 0.5
            xsize 820
            ysize 44
            background "#00000088"
            padding (12, 6, 12, 6)
            text task_text style "guitar_task_text"

        ## ── 反馈区 ──
        frame:
            xalign 0.5
            xsize 820
            ysize 40
            background "#00000066"
            padding (12, 4, 12, 4)
            text "[fret_feedback]" style "guitar_feedback_text"

        ## ── 指板 ──
        frame:
            xalign 0.5
            background "#1a0d05ee"
            padding (16, 12, 16, 12)

            vbox:
                spacing 0

                ## 标题行
                hbox:
                    spacing 0
                    frame:
                        xysize (36, 24)
                        background "#00000000"
                        text "" size 12 xalign 0.5
                    frame:
                        xysize (52, 24)
                        background "#00000000"
                        text "空弦" style "guitar_note_label"
                    for fret_num in [1, 2, 3, 4, 5]:
                        frame:
                            xysize (72, 24)
                            background "#00000000"
                            text "{}品".format(fret_num) style "guitar_note_label"

                ## 6根弦
                for string_num in [1, 2, 3, 4, 5, 6]:
                    hbox:
                        spacing 0

                        ## 弦名
                        frame:
                            xysize (36, 52)
                            background "#0f0804"
                            text ["e","B","G","D","A","E"][string_num-1]:
                                size 14
                                color "#aa8844"
                                xalign 0.5
                                yalign 0.5

                        ## 空弦按钮
                        python:
                            _open_is_target = is_target_open(string_num, target_chord)
                            _open_note = GUITAR_NOTES.get((string_num, 0), "?")
                            _open_sound = get_fret_sound(string_num, 0)
                        button:
                            style "open_string_button"
                            selected fret_pressed.get((string_num, 0), False)
                            action [
                                Play("sound", _open_sound),
                                SetVariable("fret_pressed", toggle_fret(fret_pressed, string_num, 0)),
                                SetVariable("fret_feedback", "第{}弦 空弦".format(string_num)),
                                SetVariable("strum_result", ""),
                            ]
                            if _open_is_target:
                                text "✓" style "open_string_button_text"
                            else:
                                text _open_note style "open_string_button_text"

                        ## 品格 1-5
                        for fret_num in [1, 2, 3, 4, 5]:
                            python:
                                _is_pressed = fret_pressed.get((string_num, fret_num), False)
                                _note_name = GUITAR_NOTES.get((string_num, fret_num), "?")
                                _is_target = is_target_fret(string_num, fret_num, target_chord)
                                _sound_file = get_fret_sound(string_num, fret_num)
                            if _is_target:
                                button:
                                    style "fret_button_target"
                                    selected _is_pressed
                                    action [
                                        Play("sound", _sound_file),
                                        SetVariable("fret_pressed", toggle_fret(fret_pressed, string_num, fret_num)),
                                        SetVariable("fret_feedback", "第{}弦 {}品".format(string_num, fret_num)),
                                        SetVariable("strum_result", ""),
                                    ]
                                    text "●" style "fret_button_target_text"
                            else:
                                button:
                                    style "fret_button"
                                    selected _is_pressed
                                    action [
                                        Play("sound", _sound_file),
                                        SetVariable("fret_pressed", toggle_fret(fret_pressed, string_num, fret_num)),
                                        SetVariable("fret_feedback", "第{}弦 {}品".format(string_num, fret_num)),
                                        SetVariable("strum_result", ""),
                                    ]
                                    text _note_name style "fret_button_text"

        ## ── 提示说明（有目标和弦时显示） ──
        if target_chord:
            frame:
                xalign 0.5
                xsize 820
                ysize 36
                background "#001a0088"
                padding (12, 4, 12, 4)
                text "绿色 ● = 需要按的位置  ·  ✓ = 空弦直接拨  ·  按好后点「扫弦」听听看":
                    size 13
                    color "#88cc88"
                    xalign 0.5
                    yalign 0.5

        ## ── 扫弦 + 操作按钮 ──
        hbox:
            xalign 0.5
            spacing 16

            button:
                style "strum_button"
                action [
                    Play("sound", "audio/strum_down.wav"),
                    SetVariable("strum_result", "↓ " + " ".join(get_pressed_notes(fret_pressed))),
                    SetVariable("fret_feedback", "↓ 扫弦"),
                ]
                text "↓ 扫弦" style "strum_button_text"

            button:
                style "strum_button"
                action [
                    Play("sound", "audio/strum_up.wav"),
                    SetVariable("strum_result", "↑ " + " ".join(list(reversed(get_pressed_notes(fret_pressed))))),
                    SetVariable("fret_feedback", "↑ 扫弦"),
                ]
                text "↑ 扫弦" style "strum_button_text"

            if target_chord:
                button:
                    style "strum_button"
                    background "#2a1a3a"
                    hover_background "#4a2a6a"
                    action [
                        SetVariable("fret_feedback",
                            check_chord_match(fret_pressed, target_chord)[1]
                        ),
                        Play("sound",
                            "audio/chord_correct.wav" if check_chord_match(fret_pressed, target_chord)[0]
                            else "audio/chord_wrong.wav"
                        ),
                    ]
                    text "检查手型" style "strum_button_text"

            button:
                style "strum_button"
                background "#2a1a1a"
                hover_background "#4a2a2a"
                action [
                    Play("sound", "audio/chord_wrong.wav"),
                    SetVariable("fret_pressed", {}),
                    SetVariable("fret_feedback", "松开了所有弦"),
                    SetVariable("strum_result", ""),
                ]
                text "✕ 松弦" style "strum_button_text"

        ## ── 完成/退出 ──
        hbox:
            xalign 0.5
            spacing 24

            if target_chord:
                button:
                    xysize (220, 48)
                    background "#1a3a1a"
                    hover_background "#2a5a2a"
                    padding (8, 8, 8, 8)
                    sensitive check_chord_match(fret_pressed, target_chord)[0]
                    action [
                        Play("sound", "audio/chord_correct.wav"),
                        Hide("guitar_fretboard"),
                        Jump(exit_label),
                    ]
                    text "✓ 弹对了，继续" xalign 0.5 yalign 0.5 size 15 color "#88dd88" hover_color "#aaffaa"

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

        ## ── 底部说明 ──
        frame:
            xalign 0.5
            xsize 820
            ysize 34
            background "#00000055"
            padding (12, 4, 12, 4)
            text "点击格子按弦发声（再次点击松开）· 同一弦只能按一个品格":
                size 12
                color "#555555"
                xalign 0.5
                yalign 0.5


## ─────────────────────────────────────────────
## 自由弹奏
## ─────────────────────────────────────────────
label guitar_free_play:
    $ fret_pressed = {}
    $ fret_feedback = "随便点格子，听听每个音"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="🎸 自由弹奏 · 随便探索，没有对错",
        target_chord="",
        exit_label="guitar_room_main"
    )
    pause
    return


## ─────────────────────────────────────────────
## 和弦练习
## ─────────────────────────────────────────────
label guitar_interactive_c:
    $ fret_pressed = apply_chord_shape("C")
    $ fret_feedback = "绿色的位置就是要按的地方，试着扫一下弦"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="练习 C 和弦 · 按住绿色位置，扫弦，再「检查手型」",
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
    $ fret_pressed = apply_chord_shape("G")
    $ fret_feedback = "绿色的位置就是要按的地方，试着扫一下弦"
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
    $ fret_pressed = apply_chord_shape("Am")
    $ fret_feedback = "绿色的位置就是要按的地方，试着扫一下弦"
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
    $ fret_pressed = apply_chord_shape("F")
    $ fret_feedback = "F 是封闭和弦，6根弦都要按——绿色位置都按住后扫弦"
    $ strum_result = ""
    show screen guitar_fretboard(
        task_text="练习 F 和弦（封闭和弦）· 最难的一关",
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
