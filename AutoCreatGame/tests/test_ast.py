"""Ren'Py AST 节点单元测试"""

import pytest

from storyforge.ast.nodes import (
    BlankLine,
    CallNode,
    Comment,
    DefaultVar,
    DefineCharacter,
    HideStatement,
    IfBranch,
    IfNode,
    JumpNode,
    Label,
    MenuChoice,
    MenuNode,
    PlayMusic,
    PlaySound,
    PythonLine,
    ReturnNode,
    Say,
    SceneStatement,
    ShowStatement,
    StopMusic,
    Window,
    WithTransition,
    render_nodes,
)


class TestComment:
    def test_basic(self):
        node = Comment(text="这是注释")
        assert node.to_renpy() == "# 这是注释"

    def test_with_indent(self):
        node = Comment(text="缩进注释")
        assert node.to_renpy(indent=2) == "        # 缩进注释"


class TestBlankLine:
    def test_basic(self):
        assert BlankLine().to_renpy() == ""


class TestDefineCharacter:
    def test_basic(self):
        node = DefineCharacter(var_name="e", display_name="Eileen", color="#c8ffc8")
        assert node.to_renpy() == 'define e = Character("Eileen", who_color="#c8ffc8")'

    def test_chinese_name(self):
        node = DefineCharacter(var_name="lin_xue", display_name="林雪", color="#ffffff")
        assert node.to_renpy() == 'define lin_xue = Character("林雪", who_color="#ffffff")'

    def test_with_indent(self):
        node = DefineCharacter(var_name="e", display_name="Eileen", color="#fff")
        result = node.to_renpy(indent=1)
        assert result.startswith("    define")


class TestDefaultVar:
    def test_int(self):
        node = DefaultVar(var_name="affection", value="0")
        assert node.to_renpy() == "default affection = 0"

    def test_bool(self):
        node = DefaultVar(var_name="met_hero", value="False")
        assert node.to_renpy() == "default met_hero = False"

    def test_string(self):
        node = DefaultVar(var_name="name", value='"Player"')
        assert node.to_renpy() == 'default name = "Player"'


class TestLabel:
    def test_empty_body(self):
        node = Label(name="start")
        result = node.to_renpy()
        assert "label start:" in result
        assert "    pass" in result

    def test_with_body(self):
        node = Label(name="chapter_1", body=[
            Say(text="你好"),
            ReturnNode(),
        ])
        result = node.to_renpy()
        assert "label chapter_1:" in result
        assert '    "你好"' in result
        assert "    return" in result

    def test_nested_indent(self):
        node = Label(name="test", body=[Say(text="hello")])
        result = node.to_renpy(indent=1)
        assert result.startswith("    label test:")
        assert '        "hello"' in result


class TestSay:
    def test_narration(self):
        node = Say(text="这是旁白")
        assert node.to_renpy() == '"这是旁白"'

    def test_character_dialogue(self):
        node = Say(text="你好啊", character_var="lin_xue")
        assert node.to_renpy() == 'lin_xue "你好啊"'

    def test_quote_escape(self):
        node = Say(text='她说了"你好"')
        assert node.to_renpy() == '"她说了\\"你好\\""'

    def test_with_indent(self):
        node = Say(text="缩进对话", character_var="e")
        result = node.to_renpy(indent=1)
        assert result == '    e "缩进对话"'


class TestSceneStatement:
    def test_basic(self):
        node = SceneStatement(bg_name="bg_classroom")
        assert node.to_renpy() == "scene bg_classroom"

    def test_with_transition(self):
        node = SceneStatement(bg_name="bg_forest", transition="dissolve")
        assert node.to_renpy() == "scene bg_forest with dissolve"


class TestShowStatement:
    def test_basic(self):
        node = ShowStatement(name="eileen")
        assert node.to_renpy() == "show eileen"

    def test_with_expression(self):
        node = ShowStatement(name="eileen", expression="happy")
        assert node.to_renpy() == "show eileen happy"

    def test_with_position(self):
        node = ShowStatement(name="eileen", expression="happy", position="right")
        assert node.to_renpy() == "show eileen happy at right"

    def test_full(self):
        node = ShowStatement(name="eileen", expression="sad", position="left", transition="dissolve")
        assert node.to_renpy() == "show eileen sad at left with dissolve"


class TestHideStatement:
    def test_basic(self):
        node = HideStatement(name="eileen")
        assert node.to_renpy() == "hide eileen"

    def test_with_transition(self):
        node = HideStatement(name="eileen", transition="fadeout")
        assert node.to_renpy() == "hide eileen with fadeout"


class TestMenuNode:
    def test_basic_menu(self):
        node = MenuNode(
            prompt="你要怎么做？",
            choices=[
                MenuChoice(text="选项A", body=[Say(text="选了A")]),
                MenuChoice(text="选项B", body=[Say(text="选了B")]),
            ],
        )
        result = node.to_renpy()
        assert "menu:" in result
        assert '"你要怎么做？"' in result
        assert '"选项A":' in result
        assert '"选项B":' in result
        assert '"选了A"' in result
        assert '"选了B"' in result

    def test_menu_no_prompt(self):
        node = MenuNode(choices=[
            MenuChoice(text="是", body=[Say(text="好的")]),
            MenuChoice(text="否", body=[Say(text="不好")]),
        ])
        result = node.to_renpy()
        assert "menu:" in result
        assert '"是":' in result

    def test_choice_with_condition(self):
        node = MenuNode(choices=[
            MenuChoice(text="特殊选项", body=[Say(text="wow")], condition="has_key"),
        ])
        result = node.to_renpy()
        assert '"特殊选项" if has_key:' in result

    def test_empty_choice_body(self):
        node = MenuNode(choices=[
            MenuChoice(text="空选项"),
        ])
        result = node.to_renpy()
        assert "pass" in result

    def test_menu_with_effects(self):
        node = MenuNode(
            prompt="如何回应？",
            choices=[
                MenuChoice(text="友好", body=[
                    PythonLine(code="affection += 5"),
                    Say(text="你微笑着回应"),
                ]),
                MenuChoice(text="冷淡", body=[
                    PythonLine(code="affection -= 3"),
                    Say(text="你冷冷地转过头"),
                ]),
            ],
        )
        result = node.to_renpy()
        assert "$ affection += 5" in result
        assert "$ affection -= 3" in result


class TestIfNode:
    def test_simple_if(self):
        node = IfNode(branches=[
            IfBranch(condition="affection >= 10", body=[Say(text="好结局")]),
        ])
        result = node.to_renpy()
        assert "if affection >= 10:" in result
        assert '"好结局"' in result

    def test_if_else(self):
        node = IfNode(branches=[
            IfBranch(condition="affection >= 10", body=[JumpNode(target="good_end")]),
            IfBranch(condition=None, body=[JumpNode(target="bad_end")]),
        ])
        result = node.to_renpy()
        assert "if affection >= 10:" in result
        assert "else:" in result
        assert "jump good_end" in result
        assert "jump bad_end" in result

    def test_if_elif_else(self):
        node = IfNode(branches=[
            IfBranch(condition="score >= 90", body=[Say(text="优秀")]),
            IfBranch(condition="score >= 60", body=[Say(text="及格")]),
            IfBranch(condition=None, body=[Say(text="不及格")]),
        ])
        result = node.to_renpy()
        assert "if score >= 90:" in result
        assert "elif score >= 60:" in result
        assert "else:" in result

    def test_empty_branch(self):
        node = IfNode(branches=[
            IfBranch(condition="True", body=[]),
        ])
        result = node.to_renpy()
        assert "pass" in result


class TestSimpleNodes:
    def test_jump(self):
        assert JumpNode(target="chapter_2").to_renpy() == "jump chapter_2"

    def test_jump_indent(self):
        assert JumpNode(target="end").to_renpy(indent=2) == "        jump end"

    def test_call(self):
        assert CallNode(target="chapter_1").to_renpy() == "call chapter_1"

    def test_return(self):
        assert ReturnNode().to_renpy() == "return"

    def test_python_line(self):
        assert PythonLine(code="affection += 5").to_renpy() == "$ affection += 5"

    def test_python_line_indent(self):
        assert PythonLine(code="x = 1").to_renpy(indent=1) == "    $ x = 1"


class TestAudioNodes:
    def test_play_music(self):
        node = PlayMusic(filename="bgm/theme.ogg")
        assert node.to_renpy() == 'play music "bgm/theme.ogg"'

    def test_play_music_with_fade(self):
        node = PlayMusic(filename="bgm/sad.ogg", fadein=2.0, fadeout=1.0)
        assert node.to_renpy() == 'play music "bgm/sad.ogg" fadeout 1.0 fadein 2.0'

    def test_stop_music(self):
        assert StopMusic().to_renpy() == "stop music"

    def test_stop_music_fadeout(self):
        assert StopMusic(fadeout=2.0).to_renpy() == "stop music fadeout 2.0"

    def test_play_sound(self):
        assert PlaySound(filename="sfx/click.ogg").to_renpy() == 'play sound "sfx/click.ogg"'


class TestOtherNodes:
    def test_with_transition(self):
        assert WithTransition(transition="dissolve").to_renpy() == "with dissolve"

    def test_window_show(self):
        assert Window(action="show").to_renpy() == "window show"

    def test_window_hide(self):
        assert Window(action="hide").to_renpy() == "window hide"


class TestRenderNodes:
    def test_multiple_nodes(self):
        nodes = [
            Comment(text="角色定义"),
            DefineCharacter(var_name="e", display_name="Eileen", color="#c8ffc8"),
            BlankLine(),
            DefaultVar(var_name="score", value="0"),
        ]
        result = render_nodes(nodes)
        lines = result.strip().split("\n")
        assert lines[0] == "# 角色定义"
        assert 'define e = Character("Eileen"' in lines[1]
        assert lines[2] == ""
        assert "default score = 0" in lines[3]

    def test_empty_nodes(self):
        result = render_nodes([])
        assert result == "\n"

    def test_render_with_indent(self):
        nodes = [Say(text="hello"), Say(text="world")]
        result = render_nodes(nodes, indent=1)
        lines = result.rstrip("\n").split("\n")
        for line in lines:
            assert line.startswith("    ")
