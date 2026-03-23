"""Ren'Py 代码生成器 - 将 StoryData 转换为 .rpy 脚本文件

流程: StoryData → AST 节点列表 → .rpy 代码文本
"""

from __future__ import annotations

from storyforge.ast.nodes import (
    BlankLine,
    CallNode,
    Comment,
    DefaultVar,
    DefineCharacter,
    IfBranch,
    IfNode,
    JumpNode,
    Label,
    MenuChoice,
    MenuNode,
    PythonLine,
    RenpyNode,
    ReturnNode,
    Say,
    SceneStatement,
    render_nodes,
)
from storyforge.parser.models import (
    Chapter,
    EndingType,
    SegmentType,
    StoryData,
    VariableType,
)


# 为角色分配不同颜色
_COLOR_PALETTE = [
    "#c8ffc8",  # 浅绿
    "#ffc8c8",  # 浅红
    "#c8c8ff",  # 浅蓝
    "#ffffc8",  # 浅黄
    "#ffc8ff",  # 浅紫
    "#c8ffff",  # 浅青
    "#ffddaa",  # 浅橙
    "#ddaaff",  # 浅紫罗兰
]

# 场景背景色（MVP 无图片资源时使用 Solid 纯色）
_SCENE_BG_COLORS = [
    "#1a1a2e",  # 深蓝夜色
    "#2a2a3e",  # 蓝灰
    "#2e3a50",  # 深灰蓝
    "#3a4a60",  # 灰蓝
    "#1e3d2f",  # 深绿
    "#3a2e50",  # 深紫
    "#4a3a2e",  # 深棕
    "#2e2e2e",  # 深灰
]


class RenpyGenerator:
    """将 StoryData 转换为多个 .rpy 文件的内容"""

    def __init__(self, story: StoryData):
        self.story = story
        # 角色名 → 变量名 的映射
        self._char_map: dict[str, str] = {}
        for char in story.characters:
            self._char_map[char.name] = char.var_name

    def generate_all(self) -> dict[str, str]:
        """生成所有 .rpy 文件，返回 {文件名: 内容}"""
        files: dict[str, str] = {}

        files["characters.rpy"] = self._gen_characters()
        files["variables.rpy"] = self._gen_variables()
        files["script.rpy"] = self._gen_main_script()

        for chapter in self.story.chapters:
            fname = f"chapter_{chapter.number}.rpy"
            files[fname] = self._gen_chapter(chapter)

        for ending in self.story.endings:
            # 所有结局放在一个文件中
            pass
        if self.story.endings:
            files["endings.rpy"] = self._gen_endings()

        return files

    def _gen_characters(self) -> str:
        """生成 characters.rpy"""
        nodes: list[RenpyNode] = [
            Comment("角色定义 - 由 StoryForge 自动生成"),
            BlankLine(),
        ]
        for i, char in enumerate(self.story.characters):
            color = char.color
            if color == "#ffffff":
                color = _COLOR_PALETTE[i % len(_COLOR_PALETTE)]
            nodes.append(DefineCharacter(
                var_name=char.var_name,
                display_name=char.name,
                color=color,
            ))
        nodes.append(BlankLine())
        return render_nodes(nodes)

    def _gen_variables(self) -> str:
        """生成 variables.rpy"""
        nodes: list[RenpyNode] = [
            Comment("故事变量 - 由 StoryForge 自动生成"),
            BlankLine(),
        ]
        for var in self.story.variables:
            if var.var_type == VariableType.BOOL:
                val = var.default_value if var.default_value in ("True", "False") else "False"
            elif var.var_type == VariableType.STRING:
                val = f'"{var.default_value}"' if not var.default_value.startswith('"') else var.default_value
            else:
                val = var.default_value or "0"
            nodes.append(DefaultVar(var_name=var.name, value=val))
        if not self.story.variables:
            nodes.append(Comment("（暂无变量）"))
        nodes.append(BlankLine())
        return render_nodes(nodes)

    def _gen_main_script(self) -> str:
        """生成 script.rpy - 主入口和流程控制"""
        nodes: list[RenpyNode] = [
            Comment("主脚本 - 由 StoryForge 自动生成"),
            BlankLine(),
        ]

        # label start
        body: list[RenpyNode] = []

        # 按章节顺序 call 每个 chapter
        for chapter in self.story.chapters:
            body.append(CallNode(target=chapter.label_name))

        # 结局判定
        if self.story.endings:
            body.append(BlankLine())
            body.append(Comment("结局判定"))
            branches = []
            for i, ending in enumerate(self.story.endings):
                if ending.condition:
                    cond = ending.condition if i < len(self.story.endings) - 1 or i == 0 else None
                    branches.append(IfBranch(
                        condition=cond,
                        body=[JumpNode(target=ending.label)],
                    ))
                else:
                    branches.append(IfBranch(
                        condition=None,
                        body=[JumpNode(target=ending.label)],
                    ))
            if branches:
                # 确保最后一个是 else
                if branches[-1].condition is not None:
                    # 添加默认结局
                    branches.append(IfBranch(
                        condition=None,
                        body=[JumpNode(target=self.story.endings[-1].label)],
                    ))
                body.append(IfNode(branches=branches))
        else:
            body.append(BlankLine())
            body.append(Say(text="故事结束。"))
            body.append(ReturnNode())

        nodes.append(Label(name="start", body=body))
        nodes.append(BlankLine())
        return render_nodes(nodes)

    def _gen_chapter(self, chapter: Chapter) -> str:
        """生成单个章节的 .rpy 文件"""
        nodes: list[RenpyNode] = [
            Comment(f"第 {chapter.number} 章: {chapter.title}" if chapter.title else f"第 {chapter.number} 章"),
            BlankLine(),
        ]

        body: list[RenpyNode] = []

        # 场景设置（MVP 使用 Solid 纯色背景）
        color = _SCENE_BG_COLORS[(chapter.number - 1) % len(_SCENE_BG_COLORS)]
        body.append(SceneStatement(
            bg_name=f'expression Solid("{color}")',
            transition="dissolve",
        ))
        body.append(BlankLine())

        # 建立选择点索引：segment_index → Choice
        choice_map: dict[int, list] = {}
        for choice in chapter.choices:
            idx = choice.insert_after_segment
            choice_map.setdefault(idx, []).append(choice)

        # 遍历段落生成对话/叙述
        for seg_idx, segment in enumerate(chapter.segments):
            if segment.type == SegmentType.DIALOGUE:
                char_var = self._char_map.get(segment.character, None)
                body.append(Say(text=segment.text, character_var=char_var))
            elif segment.type == SegmentType.NARRATION:
                body.append(Say(text=segment.text))
            elif segment.type == SegmentType.ACTION:
                body.append(Say(text=segment.text))

            # 在此 segment 后插入选择
            if seg_idx in choice_map:
                for choice in choice_map[seg_idx]:
                    body.append(BlankLine())
                    body.append(self._build_menu(choice))
                    body.append(BlankLine())

        body.append(BlankLine())
        body.append(ReturnNode())

        nodes.append(Label(name=chapter.label_name, body=body))
        nodes.append(BlankLine())
        return render_nodes(nodes)

    def _gen_endings(self) -> str:
        """生成 endings.rpy"""
        nodes: list[RenpyNode] = [
            Comment("结局 - 由 StoryForge 自动生成"),
            BlankLine(),
        ]

        for ending in self.story.endings:
            body: list[RenpyNode] = []

            # 结局类型标题
            type_names = {
                EndingType.GOOD: "GOOD ENDING",
                EndingType.BAD: "BAD ENDING",
                EndingType.NEUTRAL: "NORMAL ENDING",
                EndingType.TRUE: "TRUE ENDING",
            }
            title = type_names.get(ending.type, "ENDING")
            body.append(Say(text=f"--- {title} ---"))
            body.append(BlankLine())

            if ending.text:
                body.append(Say(text=ending.text))

            body.append(BlankLine())
            body.append(ReturnNode())

            nodes.append(Label(name=ending.label, body=body))
            nodes.append(BlankLine())

        return render_nodes(nodes)

    def _build_menu(self, choice) -> MenuNode:
        """将 Choice 数据模型转为 MenuNode AST 节点"""
        menu_choices = []
        for option in choice.options:
            option_body: list[RenpyNode] = []
            for effect in option.effects:
                option_body.append(PythonLine(code=effect))
            if option.branch_label:
                option_body.append(JumpNode(target=option.branch_label))
            if not option_body:
                option_body.append(Say(text="……"))
            menu_choices.append(MenuChoice(text=option.text, body=option_body))

        return MenuNode(prompt=choice.prompt or None, choices=menu_choices)

    def _find_scene(self, name: str):
        """按名称查找场景"""
        for scene in self.story.scenes:
            if scene.name == name:
                return scene
        return None
