"""Ren'Py 代码生成器单元测试"""

import pytest

from storyforge.parser.models import (
    Chapter,
    Character,
    Choice,
    ChoiceOption,
    Ending,
    EndingType,
    Scene,
    Segment,
    SegmentType,
    StoryData,
    StoryVariable,
    VariableType,
    _sanitize_varname,
)
from storyforge.generator.renpy_generator import RenpyGenerator


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def full_story() -> StoryData:
    """完整的测试故事数据"""
    return StoryData(
        title="天台上的约定",
        author="测试",
        characters=[
            Character(name="林雪", description="女主角"),
            Character(name="陈默", description="男主角"),
        ],
        scenes=[
            Scene(name="天台", description="学院教学楼天台"),
            Scene(name="教室", description="早晨的教室"),
        ],
        chapters=[
            Chapter(
                number=1,
                title="重逢",
                scene="天台",
                segments=[
                    Segment(type=SegmentType.NARRATION, text="夜色深沉，月光洒满了天台。"),
                    Segment(type=SegmentType.DIALOGUE, text="你又来这里了。", character="陈默"),
                    Segment(type=SegmentType.DIALOGUE, text="嗯，我喜欢这里。", character="林雪"),
                    Segment(type=SegmentType.NARRATION, text="两人并肩坐下，望着远处的灯火。"),
                ],
                choices=[
                    Choice(
                        prompt="你想说什么？",
                        insert_after_segment=2,
                        options=[
                            ChoiceOption(text="谈谈未来", effects=["affection_chenmo += 5"]),
                            ChoiceOption(text="保持沉默", effects=["affection_chenmo -= 2"]),
                        ],
                    ),
                ],
            ),
        ],
        endings=[
            Ending(label="good_ending", type=EndingType.GOOD, condition="affection_chenmo >= 10", text="他们一起走向了未来。"),
            Ending(label="bad_ending", type=EndingType.BAD, condition="", text="各自走上了不同的道路。"),
        ],
        variables=[
            StoryVariable(name="affection_chenmo", var_type=VariableType.INT, default_value="0", description="与陈默的好感度"),
        ],
    )


@pytest.fixture
def minimal_story() -> StoryData:
    """最简故事数据"""
    return StoryData(
        title="最简故事",
        characters=[Character(name="主角")],
        chapters=[
            Chapter(
                number=1,
                title="正文",
                segments=[
                    Segment(type=SegmentType.NARRATION, text="故事开始了。"),
                    Segment(type=SegmentType.NARRATION, text="故事结束了。"),
                ],
            ),
        ],
    )


# ============================================================
# _sanitize_varname 测试
# ============================================================

class TestSanitizeVarname:
    def test_english_name(self):
        result = _sanitize_varname("Eileen")
        assert result.isidentifier()
        assert result == "eileen"

    def test_chinese_name(self):
        result = _sanitize_varname("林雪")
        assert result.isidentifier()
        assert len(result) > 0

    def test_mixed_name(self):
        result = _sanitize_varname("Hero 1")
        assert result.isidentifier()

    def test_empty_string(self):
        result = _sanitize_varname("")
        assert result.startswith("v_") or result.isidentifier()

    def test_special_chars(self):
        result = _sanitize_varname("test@#$")
        assert result.isidentifier()

    def test_max_length(self):
        result = _sanitize_varname("a" * 100)
        assert len(result) <= 30


# ============================================================
# RenpyGenerator 测试
# ============================================================

class TestGenerateAll:
    def test_returns_all_files(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        assert "characters.rpy" in files
        assert "variables.rpy" in files
        assert "script.rpy" in files
        assert "chapter_1.rpy" in files
        assert "endings.rpy" in files

    def test_minimal_story_files(self, minimal_story):
        gen = RenpyGenerator(minimal_story)
        files = gen.generate_all()
        assert "characters.rpy" in files
        assert "variables.rpy" in files
        assert "script.rpy" in files
        assert "chapter_1.rpy" in files
        # 无结局时不生成 endings.rpy
        assert "endings.rpy" not in files


class TestCharactersRpy:
    def test_contains_define(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["characters.rpy"]
        assert "define" in content
        assert "Character(" in content
        assert "林雪" in content
        assert "陈默" in content

    def test_auto_color(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["characters.rpy"]
        # 默认颜色 #ffffff 应被替换为调色板颜色
        assert "who_color=" in content


class TestVariablesRpy:
    def test_contains_default(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["variables.rpy"]
        assert "default affection_chenmo = 0" in content

    def test_empty_variables(self, minimal_story):
        gen = RenpyGenerator(minimal_story)
        files = gen.generate_all()
        content = files["variables.rpy"]
        assert "暂无变量" in content


class TestScriptRpy:
    def test_has_label_start(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["script.rpy"]
        assert "label start:" in content

    def test_calls_chapters(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["script.rpy"]
        assert "call chapter_1" in content

    def test_has_ending_jumps(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["script.rpy"]
        assert "jump good_ending" in content
        assert "jump bad_ending" in content

    def test_no_endings_has_return(self, minimal_story):
        gen = RenpyGenerator(minimal_story)
        files = gen.generate_all()
        content = files["script.rpy"]
        assert "return" in content


class TestChapterRpy:
    def test_has_label(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "label chapter_1:" in content

    def test_contains_dialogue(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "你又来这里了" in content
        assert "我喜欢这里" in content

    def test_contains_narration(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "夜色深沉" in content

    def test_contains_menu(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "menu:" in content
        assert "谈谈未来" in content
        assert "保持沉默" in content

    def test_contains_scene(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "scene expression Solid(" in content

    def test_has_return(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "return" in content


class TestEndingsRpy:
    def test_has_ending_labels(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["endings.rpy"]
        assert "label good_ending:" in content
        assert "label bad_ending:" in content

    def test_ending_text(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["endings.rpy"]
        assert "一起走向了未来" in content
        assert "不同的道路" in content

    def test_ending_type_titles(self, full_story):
        gen = RenpyGenerator(full_story)
        files = gen.generate_all()
        content = files["endings.rpy"]
        assert "GOOD ENDING" in content
        assert "BAD ENDING" in content


class TestEdgeCases:
    def test_empty_characters(self):
        story = StoryData(
            title="空角色",
            chapters=[Chapter(number=1, segments=[
                Segment(type=SegmentType.NARRATION, text="空故事"),
            ])],
        )
        gen = RenpyGenerator(story)
        files = gen.generate_all()
        assert "characters.rpy" in files

    def test_no_choices(self):
        story = StoryData(
            title="无选择",
            characters=[Character(name="主角")],
            chapters=[Chapter(number=1, segments=[
                Segment(type=SegmentType.DIALOGUE, text="你好", character="主角"),
            ])],
        )
        gen = RenpyGenerator(story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        assert "menu:" not in content

    def test_dialogue_without_known_character(self):
        """对话角色不在 characters 列表中时，character_var 应为 None"""
        story = StoryData(
            title="未知角色",
            chapters=[Chapter(number=1, segments=[
                Segment(type=SegmentType.DIALOGUE, text="你好", character="路人"),
            ])],
        )
        gen = RenpyGenerator(story)
        files = gen.generate_all()
        content = files["chapter_1.rpy"]
        # 路人不在 _char_map 中，应作为旁白输出（character_var=None）
        assert "你好" in content
