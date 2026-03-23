"""Ren'Py 项目构建器 - 生成完整可运行的 Ren'Py 游戏项目目录"""

from __future__ import annotations

import platform
import re
import shutil
from pathlib import Path

from rich.console import Console

from storyforge.generator.renpy_generator import RenpyGenerator
from storyforge.parser.models import StoryData

console = Console()

# macOS 系统中文字体路径
_CHINESE_FONT_CANDIDATES = [
    Path("/System/Library/Fonts/PingFang.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/STHeiti Light.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    # Linux
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc"),
    # Windows
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simsun.ttc"),
]

_FONT_FILENAME = "PingFang.ttc"


def _find_chinese_font() -> Path | None:
    """查找系统中可用的中文字体文件"""
    for p in _CHINESE_FONT_CANDIDATES:
        if p.exists():
            return p
    return None


class ProjectBuilder:
    """构建完整的 Ren'Py 项目目录"""

    def __init__(self, story: StoryData, output_dir: str | Path):
        self.story = story
        self.output_dir = Path(output_dir)
        self.game_dir = self.output_dir / "game"

    def build(self) -> Path:
        """构建项目并返回项目根目录路径"""
        self.game_dir.mkdir(parents=True, exist_ok=True)

        generator = RenpyGenerator(self.story)
        files = generator.generate_all()

        for filename, content in files.items():
            filepath = self.game_dir / filename
            filepath.write_text(content, encoding="utf-8")
            console.print(f"  [dim]写入: {filepath}[/dim]")

        self._copy_font()
        self._write_gui()
        self._write_screens()
        self._write_options()

        total = len(files) + 4  # +4: font, gui, screens, options
        console.print(f"\n[bold green]项目已生成: {self.output_dir}[/bold green]")
        console.print(f"[dim]共 {total} 个文件[/dim]")
        return self.output_dir

    def _copy_font(self):
        """复制中文字体到游戏目录"""
        font_src = _find_chinese_font()
        if font_src:
            dst = self.game_dir / _FONT_FILENAME
            shutil.copy(font_src, dst)
            console.print(f"  [dim]写入: {dst}[/dim]")
        else:
            console.print("  [yellow]警告: 未找到系统中文字体，中文可能显示为方块[/yellow]")

    def _write_gui(self):
        """生成 gui.rpy - 纯变量定义"""
        content = f'''\
# gui.rpy - 由 StoryForge 自动生成

init offset = -1

define gui.accent_color = '#0099ff'
define gui.idle_color = '#aaaaaa'
define gui.hover_color = '#ffffff'
define gui.selected_color = '#ffffff'
define gui.insensitive_color = '#555555'
define gui.text_color = '#ffffff'
define gui.interface_text_color = '#ffffff'

define gui.default_font = "{_FONT_FILENAME}"

define gui.text_size = 30
define gui.name_text_size = 36
define gui.button_text_size = 30
define gui.choice_button_text_size = 26

define gui.textbox_height = 220
define gui.textbox_yalign = 1.0

define gui.text_xpos = 50
define gui.text_ypos = 15
define gui.text_width = 1180
define gui.name_xpos = 50
define gui.name_ypos = 0

define gui.choice_button_width = 800
'''
        filepath = self.game_dir / "gui.rpy"
        filepath.write_text(content, encoding="utf-8")
        console.print(f"  [dim]写入: {filepath}[/dim]")

    def _write_screens(self):
        """生成 screens.rpy - 所有屏幕和样式定义"""
        title = self.story.title.replace('"', '\\"')
        font = _FONT_FILENAME
        content = f'''\
# screens.rpy - 由 StoryForge 自动生成

init python:
    style.default.font = "{font}"

################################################################################
# Say 对话框
################################################################################

screen say(who, what):
    window:
        id "window"
        style "say_window"

        if who is not None:
            window:
                id "namebox"
                style "say_namebox"
                text who id "who" style "say_label"

        text what id "what" style "say_dialogue"

style say_window:
    xalign 0.5
    xfill True
    yalign 1.0
    ysize 220
    background Solid("#000000dd")
    padding (30, 20, 30, 20)

style say_namebox:
    xpos 30
    ypos 0
    xsize 300
    ysize 50
    background None
    padding (5, 5, 5, 5)

style say_label:
    font "{font}"
    xalign 0.0
    yalign 0.5
    size 32
    color "#0099ff"
    bold True
    outlines [(2, "#000000", 0, 0)]

style say_dialogue:
    font "{font}"
    xpos 30
    ypos 70
    xsize 720
    yalign 0.0
    size 28
    color "#ffffff"
    outlines [(2, "#000000", 0, 0)]

################################################################################
# Choice 选择菜单
################################################################################

screen choice(items):
    style_prefix "choice"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 10

        for i in items:
            textbutton i.caption action i.action

style choice_vbox:
    xalign 0.5
    yalign 0.5
    spacing 10

style choice_button:
    xalign 0.5
    xsize gui.choice_button_width
    yminimum 55
    background Solid("#333333cc")
    hover_background Solid("#0066cccc")
    padding (20, 10, 20, 10)

style choice_button_text:
    font "{font}"
    xalign 0.5
    size gui.choice_button_text_size
    color "#cccccc"
    hover_color "#ffffff"
    outlines [(1, "#000000", 0, 0)]

################################################################################
# 主菜单
################################################################################

screen main_menu():
    tag menu
    add Solid("#1a1a2e")

    vbox:
        xalign 0.5
        yalign 0.4
        spacing 10

        text "{title}" size 56 color "#ffffff" xalign 0.5 font "{font}"
        text "由 StoryForge 生成" size 18 color "#666666" xalign 0.5 font "{font}"

    vbox:
        style_prefix "main_menu"
        xalign 0.5
        yalign 0.75
        spacing 12

        textbutton _("开始游戏") action Start()
        textbutton _("退出") action Quit(confirm=False)

style main_menu_button:
    xalign 0.5
    xsize 300
    yminimum 50
    background Solid("#333333aa")
    hover_background Solid("#0066cccc")
    padding (20, 8, 20, 8)

style main_menu_button_text:
    font "{font}"
    xalign 0.5
    size 28
    color "#aaaaaa"
    hover_color "#ffffff"

################################################################################
# 确认对话框
################################################################################

screen confirm(message, yes_action, no_action):
    modal True
    zorder 200
    style_prefix "confirm"

    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        ysize 250
        background Solid("#222222ee")
        padding (40, 40, 40, 40)

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 30

            text _(message) xalign 0.5 size 24 color "#ffffff" text_align 0.5 font "{font}"

            hbox:
                xalign 0.5
                spacing 40

                textbutton _("确认") action yes_action
                textbutton _("取消") action no_action

style confirm_button:
    xsize 160
    yminimum 44
    background Solid("#444444cc")
    hover_background Solid("#0066cccc")
    padding (10, 6, 10, 6)

style confirm_button_text:
    font "{font}"
    xalign 0.5
    size 22
    color "#cccccc"
    hover_color "#ffffff"

################################################################################
# Skip indicator
################################################################################

screen skip_indicator():
    zorder 100

    frame:
        background Solid("#00000088")
        xalign 1.0
        yalign 0.0
        padding (10, 5, 10, 5)

        text _("快进中...") size 16 color "#ffffff" font "{font}"

screen game_menu_selector():
    pass
'''
        filepath = self.game_dir / "screens.rpy"
        filepath.write_text(content, encoding="utf-8")
        console.print(f"  [dim]写入: {filepath}[/dim]")

    def _write_options(self):
        """生成 options.rpy"""
        title = self.story.title.replace('"', '\\"')
        safe_name = _safe_filename(self.story.title)
        content = f'''\
# options.rpy - 由 StoryForge 自动生成

define config.name = _("{title}")
define config.version = "1.0"
define build.name = "{safe_name}"

define config.has_sound = False
define config.has_music = False
define config.has_voice = False
define config.main_menu_music = None

define config.window = "auto"
'''
        filepath = self.game_dir / "options.rpy"
        filepath.write_text(content, encoding="utf-8")
        console.print(f"  [dim]写入: {filepath}[/dim]")


def _safe_filename(name: str) -> str:
    """将中文名转为安全的文件名"""
    safe = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)
    return safe[:50] or "game"
