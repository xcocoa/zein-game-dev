"""故事解析器和 LLM 客户端单元测试（全部 mock，不依赖 Ollama）"""

import pytest
from unittest.mock import MagicMock, patch

from storyforge.parser.llm_client import LLMClient
from storyforge.parser.story_parser import StoryParser, _truncate, _split_text
from storyforge.parser.models import (
    Character,
    Scene,
    Segment,
    SegmentType,
    StoryData,
)


# ============================================================
# LLMClient._extract_json 测试
# ============================================================

class TestExtractJson:
    def test_pure_json_object(self):
        result = LLMClient._extract_json('{"name": "test", "value": 42}')
        assert result == {"name": "test", "value": 42}

    def test_pure_json_array(self):
        result = LLMClient._extract_json('[1, 2, 3]')
        assert result == [1, 2, 3]

    def test_markdown_code_block(self):
        text = '```json\n{"characters": ["林雪", "陈默"]}\n```'
        result = LLMClient._extract_json(text)
        assert result == {"characters": ["林雪", "陈默"]}

    def test_markdown_code_block_no_lang(self):
        text = '```\n{"key": "value"}\n```'
        result = LLMClient._extract_json(text)
        assert result == {"key": "value"}

    def test_json_with_prefix_text(self):
        text = '以下是提取结果：\n{"characters": [{"name": "林雪"}]}'
        result = LLMClient._extract_json(text)
        assert result["characters"][0]["name"] == "林雪"

    def test_json_with_surrounding_text(self):
        text = '分析完成，结果如下：\n{"result": true}\n以上就是分析结果。'
        result = LLMClient._extract_json(text)
        assert result == {"result": True}

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="无法从 LLM 回复中提取有效 JSON"):
            LLMClient._extract_json("这不是JSON内容")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            LLMClient._extract_json("")

    def test_nested_json(self):
        text = '{"chapters": [{"number": 1, "segments": [{"type": "dialogue"}]}]}'
        result = LLMClient._extract_json(text)
        assert result["chapters"][0]["number"] == 1

    def test_chinese_content_json(self):
        text = '{"title": "天台上的约定", "characters": ["林雪", "陈默"]}'
        result = LLMClient._extract_json(text)
        assert result["title"] == "天台上的约定"


# ============================================================
# 辅助函数测试
# ============================================================

class TestTruncate:
    def test_short_text(self):
        text = "短文本"
        assert _truncate(text, 100) == "短文本"

    def test_long_text(self):
        text = "a" * 200
        result = _truncate(text, 100)
        assert len(result) < 200
        assert "截断" in result

    def test_exact_length(self):
        text = "a" * 100
        assert _truncate(text, 100) == text


class TestSplitText:
    def test_short_text_single_chunk(self):
        text = "短文本"
        chunks = _split_text(text, max_chars=100)
        assert len(chunks) == 1
        assert chunks[0] == "短文本"

    def test_long_text_multiple_chunks(self):
        paragraphs = ["段落" * 50 + "\n"] * 10
        text = "\n".join(paragraphs)
        chunks = _split_text(text, max_chars=300)
        assert len(chunks) > 1
        # 所有文本都应被保留
        reconstructed = "\n".join(chunks)
        # 不丢失内容（大致检查长度）
        assert len(reconstructed) >= len(text) * 0.9

    def test_empty_text(self):
        chunks = _split_text("", max_chars=100)
        assert len(chunks) == 1


# ============================================================
# StoryParser 测试（mock LLM）
# ============================================================

def _make_mock_llm():
    """创建 mock 的 LLMClient"""
    mock = MagicMock(spec=LLMClient)
    mock.check_connection.return_value = True
    return mock


class TestExtractCharacters:
    def test_basic(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "characters": [
                {"name": "林雪", "description": "女主角"},
                {"name": "陈默", "description": "男主角"},
            ]
        }
        parser = StoryParser(llm=mock_llm)
        chars = parser._extract_characters("示例文本")
        assert len(chars) == 2
        assert chars[0].name == "林雪"
        assert chars[1].name == "陈默"
        assert isinstance(chars[0], Character)

    def test_empty_result(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {"characters": []}
        parser = StoryParser(llm=mock_llm)
        chars = parser._extract_characters("文本")
        assert len(chars) == 0


class TestExtractScenes:
    def test_basic(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "scenes": [
                {"name": "天台", "description": "学校天台"},
                {"name": "教室", "description": "早晨教室"},
            ]
        }
        parser = StoryParser(llm=mock_llm)
        scenes = parser._extract_scenes("示例文本")
        assert len(scenes) == 2
        assert scenes[0].name == "天台"
        assert isinstance(scenes[0], Scene)


class TestParseStructure:
    def test_basic(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "segments": [
                {"type": "narration", "text": "夜色如墨。", "character": None},
                {"type": "dialogue", "text": "你好。", "character": "林雪"},
                {"type": "action", "text": "她转过身。", "character": "林雪"},
            ]
        }
        parser = StoryParser(llm=mock_llm)
        chars = [Character(name="林雪")]
        segments = parser._parse_structure("短文本", chars)
        assert len(segments) == 3
        assert segments[0].type == SegmentType.NARRATION
        assert segments[1].type == SegmentType.DIALOGUE
        assert segments[1].character == "林雪"
        assert segments[2].type == SegmentType.ACTION

    def test_invalid_type_defaults_to_narration(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "segments": [
                {"type": "unknown_type", "text": "测试", "character": None},
            ]
        }
        parser = StoryParser(llm=mock_llm)
        segments = parser._parse_structure("文本", [])
        assert segments[0].type == SegmentType.NARRATION


class TestGenerateChoices:
    def test_basic(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "choices": [
                {
                    "insert_after_segment": 3,
                    "prompt": "你要怎么做？",
                    "options": [
                        {"text": "安慰她", "effects": ["affection += 5"], "branch_label": ""},
                        {"text": "转身离开", "effects": ["affection -= 3"], "branch_label": ""},
                    ],
                }
            ],
            "variables": [
                {"name": "affection", "var_type": "int", "default_value": "0", "description": "好感度"},
            ],
        }
        parser = StoryParser(llm=mock_llm)
        chars = [Character(name="林雪")]
        segments = [
            Segment(type=SegmentType.NARRATION, text=f"段落{i}")
            for i in range(5)
        ]
        choices, variables = parser._generate_choices(chars, segments)
        assert len(choices) == 1
        assert choices[0].prompt == "你要怎么做？"
        assert len(choices[0].options) == 2
        assert len(variables) == 1
        assert variables[0].name == "affection"


class TestSplitChapters:
    def test_basic(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "chapters": [
                {"number": 1, "title": "开始", "start_line": 0, "end_line": 3, "scene": "天台"},
                {"number": 2, "title": "发展", "start_line": 3, "end_line": 5, "scene": "教室"},
            ]
        }
        parser = StoryParser(llm=mock_llm)
        segments = [
            Segment(type=SegmentType.NARRATION, text=f"段落{i}")
            for i in range(5)
        ]
        scenes = [Scene(name="天台"), Scene(name="教室")]
        chapters = parser._split_chapters(segments, scenes, [])
        assert len(chapters) == 2
        assert chapters[0].title == "开始"
        assert len(chapters[0].segments) == 3
        assert len(chapters[1].segments) == 2

    def test_fallback_single_chapter(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {"chapters": []}
        parser = StoryParser(llm=mock_llm)
        segments = [
            Segment(type=SegmentType.NARRATION, text=f"段落{i}")
            for i in range(3)
        ]
        chapters = parser._split_chapters(segments, [], [])
        assert len(chapters) == 1
        assert len(chapters[0].segments) == 3


class TestGenerateEndings:
    def test_basic(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {
            "endings": [
                {"label": "good_ending", "type": "good", "condition": "affection >= 10", "text": "好结局文本"},
                {"label": "bad_ending", "type": "bad", "condition": "", "text": "坏结局文本"},
            ]
        }
        parser = StoryParser(llm=mock_llm)
        endings = parser._generate_endings("测试", [Character(name="林雪")], [], "摘要")
        assert len(endings) == 2
        assert endings[0].label == "good_ending"
        assert endings[1].label == "bad_ending"

    def test_fallback_default_ending(self):
        mock_llm = _make_mock_llm()
        mock_llm.chat_json.return_value = {"endings": []}
        parser = StoryParser(llm=mock_llm)
        endings = parser._generate_endings("测试", [], [], "摘要")
        assert len(endings) == 1
        assert endings[0].label == "default_ending"
