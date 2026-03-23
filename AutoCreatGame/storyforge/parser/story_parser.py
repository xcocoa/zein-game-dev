"""核心故事解析器 - 编排多步 LLM 调用，将小说文本转换为 StoryData"""

from __future__ import annotations

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from storyforge.parser.llm_client import LLMClient
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
)
from storyforge.parser import prompts

console = Console()


class StoryParser:
    """将小说文本解析为结构化的 StoryData"""

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def parse(self, text: str, title: str = "") -> StoryData:
        """完整解析流程"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Step 1: 提取角色
            task = progress.add_task("正在提取角色...", total=None)
            characters = self._extract_characters(text)
            progress.update(task, description=f"[green]已提取 {len(characters)} 个角色")
            progress.remove_task(task)

            # Step 2: 提取场景
            task = progress.add_task("正在提取场景...", total=None)
            scenes = self._extract_scenes(text)
            progress.update(task, description=f"[green]已提取 {len(scenes)} 个场景")
            progress.remove_task(task)

            # Step 3: 解析段落结构
            task = progress.add_task("正在解析叙事结构...", total=None)
            segments = self._parse_structure(text, characters)
            progress.update(task, description=f"[green]已解析 {len(segments)} 个段落")
            progress.remove_task(task)

            # Step 4: 生成选择点
            task = progress.add_task("正在生成选择点...", total=None)
            choices, variables = self._generate_choices(characters, segments)
            progress.update(task, description=f"[green]已生成 {len(choices)} 个选择点")
            progress.remove_task(task)

            # Step 5: 划分章节
            task = progress.add_task("正在划分章节...", total=None)
            chapters = self._split_chapters(segments, scenes, choices)
            progress.update(task, description=f"[green]已划分 {len(chapters)} 个章节")
            progress.remove_task(task)

            # Step 6: 生成结局
            task = progress.add_task("正在设计结局...", total=None)
            summary = self._summarize(text)
            endings = self._generate_endings(title, characters, variables, summary)
            progress.update(task, description=f"[green]已设计 {len(endings)} 个结局")
            progress.remove_task(task)

        return StoryData(
            title=title or "未命名故事",
            characters=characters,
            scenes=scenes,
            chapters=chapters,
            endings=endings,
            variables=variables,
        )

    def _extract_characters(self, text: str) -> list[Character]:
        """调用 LLM 提取角色"""
        result = self.llm.chat_json(
            prompts.CHARACTER_EXTRACTION_SYSTEM,
            prompts.CHARACTER_EXTRACTION_USER.format(text=_truncate(text, 6000)),
        )
        chars = []
        for item in result.get("characters", []):
            chars.append(Character(
                name=item["name"],
                description=item.get("description", ""),
            ))
        return chars

    def _extract_scenes(self, text: str) -> list[Scene]:
        """调用 LLM 提取场景"""
        result = self.llm.chat_json(
            prompts.SCENE_EXTRACTION_SYSTEM,
            prompts.SCENE_EXTRACTION_USER.format(text=_truncate(text, 6000)),
        )
        scenes = []
        for item in result.get("scenes", []):
            scenes.append(Scene(
                name=item["name"],
                description=item.get("description", ""),
            ))
        return scenes

    def _parse_structure(self, text: str, characters: list[Character]) -> list[Segment]:
        """调用 LLM 解析文本结构"""
        char_names = ", ".join(c.name for c in characters)

        # 对长文本分块处理
        chunks = _split_text(text, max_chars=3000)
        all_segments = []

        for chunk in chunks:
            result = self.llm.chat_json(
                prompts.STRUCTURE_PARSE_SYSTEM,
                prompts.STRUCTURE_PARSE_USER.format(
                    characters=char_names,
                    text=chunk,
                ),
            )
            for item in result.get("segments", []):
                seg_type = item.get("type", "narration")
                try:
                    seg_type_enum = SegmentType(seg_type)
                except ValueError:
                    seg_type_enum = SegmentType.NARRATION

                all_segments.append(Segment(
                    type=seg_type_enum,
                    text=item.get("text", ""),
                    character=item.get("character"),
                ))

        return all_segments

    def _generate_choices(
        self, characters: list[Character], segments: list[Segment]
    ) -> tuple[list[Choice], list[StoryVariable]]:
        """调用 LLM 生成选择点"""
        char_names = ", ".join(c.name for c in characters)
        summaries = "\n".join(
            f"[{i}] ({seg.type.value}) {seg.text[:30]}..."
            for i, seg in enumerate(segments)
        )

        result = self.llm.chat_json(
            prompts.CHOICE_GENERATION_SYSTEM,
            prompts.CHOICE_GENERATION_USER.format(
                characters=char_names,
                segment_count=len(segments),
                segment_summaries=summaries[:4000],
            ),
        )

        choices = []
        for item in result.get("choices", []):
            options = []
            for opt in item.get("options", []):
                options.append(ChoiceOption(
                    text=opt.get("text", ""),
                    effects=opt.get("effects", []),
                    branch_label=opt.get("branch_label", ""),
                ))
            choices.append(Choice(
                prompt=item.get("prompt", ""),
                options=options,
                insert_after_segment=item.get("insert_after_segment", -1),
            ))

        variables = []
        for item in result.get("variables", []):
            var_type_str = item.get("var_type", "int")
            try:
                var_type = VariableType(var_type_str)
            except ValueError:
                var_type = VariableType.INT
            variables.append(StoryVariable(
                name=item.get("name", ""),
                var_type=var_type,
                default_value=item.get("default_value", "0"),
                description=item.get("description", ""),
            ))

        return choices, variables

    def _split_chapters(
        self,
        segments: list[Segment],
        scenes: list[Scene],
        choices: list[Choice],
    ) -> list[Chapter]:
        """将段落划分为章节"""
        scene_names = ", ".join(s.name for s in scenes)
        summaries = "\n".join(
            f"[{i}] ({seg.type.value}) {seg.text[:30]}..."
            for i, seg in enumerate(segments)
        )

        result = self.llm.chat_json(
            prompts.CHAPTER_SPLIT_SYSTEM,
            prompts.CHAPTER_SPLIT_USER.format(
                scenes=scene_names,
                segment_count=len(segments),
                segment_summaries=summaries[:4000],
            ),
        )

        chapters = []
        raw_chapters = result.get("chapters", [])

        if not raw_chapters:
            # 如果 LLM 没返回有效数据，整个故事作为一章
            raw_chapters = [{
                "number": 1,
                "title": "正文",
                "start_line": 0,
                "end_line": len(segments),
                "scene": scenes[0].name if scenes else None,
            }]

        # 构建 choice 索引: segment_index → list[Choice]
        choice_map: dict[int, list[Choice]] = {}
        for choice in choices:
            idx = choice.insert_after_segment
            choice_map.setdefault(idx, []).append(choice)

        for ch_data in raw_chapters:
            start = ch_data.get("start_line", 0)
            end = ch_data.get("end_line", len(segments))
            # 安全边界
            start = max(0, min(start, len(segments)))
            end = max(start, min(end, len(segments)))

            ch_segments = segments[start:end]
            # 收集属于该章节的选择
            ch_choices = []
            for idx in range(start, end):
                if idx in choice_map:
                    for choice in choice_map[idx]:
                        # 调整 insert_after_segment 为章节内偏移
                        adjusted = Choice(
                            prompt=choice.prompt,
                            options=choice.options,
                            insert_after_segment=idx - start,
                        )
                        ch_choices.append(adjusted)

            chapters.append(Chapter(
                number=ch_data.get("number", len(chapters) + 1),
                title=ch_data.get("title", ""),
                segments=ch_segments,
                choices=ch_choices,
                scene=ch_data.get("scene"),
            ))

        return chapters

    def _summarize(self, text: str) -> str:
        """生成故事摘要"""
        return self.llm.chat(
            prompts.STORY_SUMMARY_SYSTEM,
            prompts.STORY_SUMMARY_USER.format(text=_truncate(text, 4000)),
        )

    def _generate_endings(
        self,
        title: str,
        characters: list[Character],
        variables: list[StoryVariable],
        summary: str,
    ) -> list[Ending]:
        """调用 LLM 生成结局"""
        char_names = ", ".join(c.name for c in characters)
        var_info = ", ".join(f"{v.name}({v.description})" for v in variables) or "暂无"

        result = self.llm.chat_json(
            prompts.ENDING_ANALYSIS_SYSTEM,
            prompts.ENDING_ANALYSIS_USER.format(
                title=title or "未命名故事",
                characters=char_names,
                variables=var_info,
                summary=summary,
            ),
        )

        endings = []
        for item in result.get("endings", []):
            end_type_str = item.get("type", "neutral")
            try:
                end_type = EndingType(end_type_str)
            except ValueError:
                end_type = EndingType.NEUTRAL
            endings.append(Ending(
                label=item.get("label", f"ending_{len(endings) + 1}"),
                type=end_type,
                condition=item.get("condition", ""),
                text=item.get("text", ""),
            ))

        # 确保至少有一个结局
        if not endings:
            endings.append(Ending(
                label="default_ending",
                type=EndingType.NEUTRAL,
                condition="",
                text="故事结束了。",
            ))

        return endings


def _truncate(text: str, max_chars: int) -> str:
    """截断文本"""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n...(文本已截断)..."


def _split_text(text: str, max_chars: int = 3000) -> list[str]:
    """将长文本按段落分块"""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n")
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) + 1 > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(para) + 1

    if current:
        chunks.append("\n".join(current))

    return chunks
