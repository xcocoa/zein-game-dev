"""核心数据模型 - 故事解析的结构化表示"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SegmentType(str, Enum):
    """段落类型"""
    NARRATION = "narration"   # 旁白/叙述
    DIALOGUE = "dialogue"     # 角色对话
    ACTION = "action"         # 动作描写


class EndingType(str, Enum):
    """结局类型"""
    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"
    TRUE = "true"


class VariableType(str, Enum):
    """变量类型"""
    INT = "int"
    BOOL = "bool"
    STRING = "string"


class Character(BaseModel):
    """角色定义"""
    name: str = Field(description="角色名称")
    var_name: str = Field(default="", description="Ren'Py 变量名（自动生成）")
    description: str = Field(default="", description="角色简介")
    color: str = Field(default="#ffffff", description="角色名称显示颜色")

    def model_post_init(self, __context) -> None:
        if not self.var_name:
            self.var_name = _sanitize_varname(self.name)


class Scene(BaseModel):
    """场景/地点定义"""
    name: str = Field(description="场景名称")
    bg_name: str = Field(default="", description="背景图标识名（自动生成）")
    description: str = Field(default="", description="场景描述")

    def model_post_init(self, __context) -> None:
        if not self.bg_name:
            self.bg_name = "bg_" + _sanitize_varname(self.name)


class Segment(BaseModel):
    """叙事段落"""
    type: SegmentType
    text: str
    character: Optional[str] = Field(default=None, description="对话时的角色名（仅 dialogue 类型）")


class ChoiceOption(BaseModel):
    """选择项"""
    text: str = Field(description="选项文字")
    branch_label: str = Field(default="", description="跳转的标签名")
    effects: list[str] = Field(default_factory=list, description="选择该项后的变量效果，如 'affection += 5'")


class Choice(BaseModel):
    """选择点"""
    prompt: str = Field(default="", description="选择提示语")
    options: list[ChoiceOption] = Field(default_factory=list)
    insert_after_segment: int = Field(default=-1, description="在第几个 segment 后插入此选择")


class Chapter(BaseModel):
    """章节"""
    number: int = Field(default=1)
    title: str = Field(default="")
    label_name: str = Field(default="", description="Ren'Py label 名")
    segments: list[Segment] = Field(default_factory=list)
    choices: list[Choice] = Field(default_factory=list)
    scene: Optional[str] = Field(default=None, description="章节的主要场景名")

    def model_post_init(self, __context) -> None:
        if not self.label_name:
            self.label_name = f"chapter_{self.number}"


class Ending(BaseModel):
    """结局"""
    label: str = Field(description="Ren'Py label 名，如 good_ending")
    type: EndingType = Field(default=EndingType.NEUTRAL)
    condition: str = Field(default="", description="触发条件表达式")
    text: str = Field(default="", description="结局文本")


class StoryVariable(BaseModel):
    """故事追踪变量"""
    name: str
    var_type: VariableType = Field(default=VariableType.INT)
    default_value: str = Field(default="0", description="默认值的字符串表示")
    description: str = Field(default="")


class StoryData(BaseModel):
    """故事的完整结构化数据 - 解析的最终产物"""
    title: str = Field(default="未命名故事")
    author: str = Field(default="")
    characters: list[Character] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)
    chapters: list[Chapter] = Field(default_factory=list)
    endings: list[Ending] = Field(default_factory=list)
    variables: list[StoryVariable] = Field(default_factory=list)


def _sanitize_varname(name: str) -> str:
    """将中文/英文名转为合法的 Ren'Py 变量名"""
    import re
    import unicodedata

    # 将每个字符转为合法的变量名片段
    result = []
    for ch in name:
        if ch.isascii() and (ch.isalnum() or ch == '_'):
            result.append(ch.lower())
        elif ch == ' ':
            result.append('_')
        else:
            # 中文字符用十六进制码点作为标识
            result.append(f"c{ord(ch):x}")

    varname = "".join(result)
    # 确保以字母开头
    if not varname or not varname[0].isalpha():
        varname = "v_" + varname
    # 去掉连续下划线
    varname = re.sub(r'_+', '_', varname).strip('_')
    return varname[:30]  # 限制长度
