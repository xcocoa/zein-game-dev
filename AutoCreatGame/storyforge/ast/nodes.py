"""Ren'Py 抽象语法树节点定义

每个节点代表一条 Ren'Py 语句，实现 to_renpy() 方法输出对应的 .rpy 代码。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

INDENT = "    "  # Ren'Py 标准 4 空格缩进


@dataclass
class RenpyNode:
    """AST 节点基类"""

    def to_renpy(self, indent: int = 0) -> str:
        raise NotImplementedError

    def _pad(self, indent: int) -> str:
        return INDENT * indent


@dataclass
class Comment(RenpyNode):
    """注释 # text"""
    text: str

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}# {self.text}"


@dataclass
class BlankLine(RenpyNode):
    """空行"""

    def to_renpy(self, indent: int = 0) -> str:
        return ""


@dataclass
class DefineCharacter(RenpyNode):
    """define var = Character("Name", who_color="#xxx")"""
    var_name: str
    display_name: str
    color: str = "#ffffff"

    def to_renpy(self, indent: int = 0) -> str:
        return (
            f'{self._pad(indent)}define {self.var_name} = '
            f'Character("{self.display_name}", who_color="{self.color}")'
        )


@dataclass
class DefaultVar(RenpyNode):
    """default variable = value"""
    var_name: str
    value: str  # 字符串表示，如 "0", "False", '"hello"'

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}default {self.var_name} = {self.value}"


@dataclass
class Label(RenpyNode):
    """label name:
        body...
    """
    name: str
    body: list[RenpyNode] = field(default_factory=list)

    def to_renpy(self, indent: int = 0) -> str:
        lines = [f"{self._pad(indent)}label {self.name}:"]
        if not self.body:
            lines.append(f"{self._pad(indent + 1)}pass")
        else:
            for node in self.body:
                lines.append(node.to_renpy(indent + 1))
        return "\n".join(lines)


@dataclass
class Say(RenpyNode):
    """角色对话或旁白

    character "text" 或 "narration text"
    """
    text: str
    character_var: Optional[str] = None  # None 表示旁白

    def to_renpy(self, indent: int = 0) -> str:
        # 转义双引号
        escaped = self.text.replace('"', '\\"')
        if self.character_var:
            return f'{self._pad(indent)}{self.character_var} "{escaped}"'
        else:
            return f'{self._pad(indent)}"{escaped}"'


@dataclass
class SceneStatement(RenpyNode):
    """scene bg_name [with transition]"""
    bg_name: str
    transition: Optional[str] = None

    def to_renpy(self, indent: int = 0) -> str:
        line = f"{self._pad(indent)}scene {self.bg_name}"
        if self.transition:
            line += f" with {self.transition}"
        return line


@dataclass
class ShowStatement(RenpyNode):
    """show character [expression] [at position] [with transition]"""
    name: str
    expression: Optional[str] = None
    position: Optional[str] = None
    transition: Optional[str] = None

    def to_renpy(self, indent: int = 0) -> str:
        parts = [f"{self._pad(indent)}show {self.name}"]
        if self.expression:
            parts[0] += f" {self.expression}"
        if self.position:
            parts[0] += f" at {self.position}"
        if self.transition:
            parts[0] += f" with {self.transition}"
        return parts[0]


@dataclass
class HideStatement(RenpyNode):
    """hide character [with transition]"""
    name: str
    transition: Optional[str] = None

    def to_renpy(self, indent: int = 0) -> str:
        line = f"{self._pad(indent)}hide {self.name}"
        if self.transition:
            line += f" with {self.transition}"
        return line


@dataclass
class MenuChoice(RenpyNode):
    """menu 内的一个选择项及其子分支"""
    text: str
    body: list[RenpyNode] = field(default_factory=list)
    condition: Optional[str] = None  # if condition

    def to_renpy(self, indent: int = 0) -> str:
        line = f'{self._pad(indent)}"{self.text}"'
        if self.condition:
            line += f" if {self.condition}"
        line += ":"
        lines = [line]
        if not self.body:
            lines.append(f"{self._pad(indent + 1)}pass")
        else:
            for node in self.body:
                lines.append(node.to_renpy(indent + 1))
        return "\n".join(lines)


@dataclass
class MenuNode(RenpyNode):
    """menu:
        "prompt"
        "choice 1":
            ...
        "choice 2":
            ...
    """
    prompt: Optional[str] = None
    choices: list[MenuChoice] = field(default_factory=list)

    def to_renpy(self, indent: int = 0) -> str:
        lines = [f"{self._pad(indent)}menu:"]
        if self.prompt:
            escaped = self.prompt.replace('"', '\\"')
            lines.append(f'{self._pad(indent + 1)}"{escaped}"')
        lines.append("")  # 空行分隔
        for choice in self.choices:
            lines.append(choice.to_renpy(indent + 1))
            lines.append("")
        return "\n".join(lines)


@dataclass
class IfBranch:
    """if/elif/else 中的一个分支"""
    condition: Optional[str]  # None 表示 else
    body: list[RenpyNode] = field(default_factory=list)


@dataclass
class IfNode(RenpyNode):
    """if/elif/else 条件语句"""
    branches: list[IfBranch] = field(default_factory=list)

    def to_renpy(self, indent: int = 0) -> str:
        lines = []
        for i, branch in enumerate(self.branches):
            if i == 0:
                lines.append(f"{self._pad(indent)}if {branch.condition}:")
            elif branch.condition is not None:
                lines.append(f"{self._pad(indent)}elif {branch.condition}:")
            else:
                lines.append(f"{self._pad(indent)}else:")

            if not branch.body:
                lines.append(f"{self._pad(indent + 1)}pass")
            else:
                for node in branch.body:
                    lines.append(node.to_renpy(indent + 1))
        return "\n".join(lines)


@dataclass
class JumpNode(RenpyNode):
    """jump label_name"""
    target: str

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}jump {self.target}"


@dataclass
class CallNode(RenpyNode):
    """call label_name"""
    target: str

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}call {self.target}"


@dataclass
class ReturnNode(RenpyNode):
    """return"""

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}return"


@dataclass
class PythonLine(RenpyNode):
    """$ python_expression"""
    code: str

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}$ {self.code}"


@dataclass
class PlayMusic(RenpyNode):
    """play music "file" [fadein X] [fadeout X]"""
    filename: str
    fadein: Optional[float] = None
    fadeout: Optional[float] = None

    def to_renpy(self, indent: int = 0) -> str:
        line = f'{self._pad(indent)}play music "{self.filename}"'
        if self.fadeout is not None:
            line += f" fadeout {self.fadeout}"
        if self.fadein is not None:
            line += f" fadein {self.fadein}"
        return line


@dataclass
class StopMusic(RenpyNode):
    """stop music [fadeout X]"""
    fadeout: Optional[float] = None

    def to_renpy(self, indent: int = 0) -> str:
        line = f"{self._pad(indent)}stop music"
        if self.fadeout is not None:
            line += f" fadeout {self.fadeout}"
        return line


@dataclass
class PlaySound(RenpyNode):
    """play sound "file" """
    filename: str

    def to_renpy(self, indent: int = 0) -> str:
        return f'{self._pad(indent)}play sound "{self.filename}"'


@dataclass
class WithTransition(RenpyNode):
    """with dissolve/fade/etc"""
    transition: str

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}with {self.transition}"


@dataclass
class Window(RenpyNode):
    """window show/hide"""
    action: str = "show"  # "show" or "hide"

    def to_renpy(self, indent: int = 0) -> str:
        return f"{self._pad(indent)}window {self.action}"


def render_nodes(nodes: list[RenpyNode], indent: int = 0) -> str:
    """将节点列表渲染为完整的 .rpy 代码文本"""
    lines = []
    for node in nodes:
        lines.append(node.to_renpy(indent))
    return "\n".join(lines) + "\n"
