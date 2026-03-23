"""StoryForge CLI - 命令行入口"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from storyforge import __version__

app = typer.Typer(
    name="storyforge",
    help="StoryForge - 中文小说转 Ren'Py 游戏脚本自动转换工具",
    no_args_is_help=True,
)
console = Console()


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="输入的小说文件路径 (.txt)"),
    output: Path = typer.Option("./output", "-o", "--output", help="输出目录"),
    title: str = typer.Option("", "-t", "--title", help="游戏标题（默认使用文件名）"),
    model: str = typer.Option("", "-m", "--model", help="指定 Ollama 模型（默认读取配置）"),
):
    """将小说文件转换为 Ren'Py 游戏项目（一键全流程）"""
    _print_banner()

    if not input_file.exists():
        console.print(f"[red]错误: 文件不存在: {input_file}[/red]")
        raise typer.Exit(1)

    text = input_file.read_text(encoding="utf-8")
    if len(text.strip()) < 50:
        console.print("[red]错误: 文本内容太短（至少需要 50 个字符）[/red]")
        raise typer.Exit(1)

    if not title:
        title = input_file.stem

    console.print(f"[bold]输入文件:[/bold] {input_file}")
    console.print(f"[bold]文本长度:[/bold] {len(text)} 字符")
    console.print(f"[bold]游戏标题:[/bold] {title}")
    console.print(f"[bold]输出目录:[/bold] {output}")
    console.print()

    # 检查 Ollama
    from storyforge.parser.llm_client import LLMClient
    if model:
        from storyforge.config import update_config
        update_config(model_name=model)

    llm = LLMClient()
    if not llm.check_connection():
        console.print("[red]错误: 无法连接到 Ollama 服务[/red]")
        console.print("[dim]请确保 Ollama 正在运行: ollama serve[/dim]")
        console.print("[dim]下载模型: ollama pull qwen2.5[/dim]")
        raise typer.Exit(1)

    console.print("[green]Ollama 连接成功[/green]")
    console.print()

    # 解析
    from storyforge.parser.story_parser import StoryParser
    parser = StoryParser(llm=llm)
    story_data = parser.parse(text, title=title)

    # 显示解析结果摘要
    _print_summary(story_data)

    # 生成项目
    console.print("\n[bold]正在生成 Ren'Py 项目...[/bold]\n")
    from storyforge.project.builder import ProjectBuilder
    builder = ProjectBuilder(story_data, output / title)
    project_path = builder.build()

    console.print(f"\n[bold green]完成！[/bold green] 使用 Ren'Py 打开 [bold]{project_path}[/bold] 即可运行游戏。")


@app.command()
def parse(
    input_file: Path = typer.Argument(..., help="输入的小说文件路径 (.txt)"),
    output: Path = typer.Option("", "-o", "--output", help="输出 JSON 文件路径（默认输出到终端）"),
    title: str = typer.Option("", "-t", "--title", help="故事标题"),
    model: str = typer.Option("", "-m", "--model", help="指定 Ollama 模型"),
):
    """仅解析小说，输出结构化 JSON（不生成 Ren'Py 代码）"""
    _print_banner()

    if not input_file.exists():
        console.print(f"[red]错误: 文件不存在: {input_file}[/red]")
        raise typer.Exit(1)

    text = input_file.read_text(encoding="utf-8")
    if not title:
        title = input_file.stem

    from storyforge.parser.llm_client import LLMClient
    if model:
        from storyforge.config import update_config
        update_config(model_name=model)

    llm = LLMClient()
    if not llm.check_connection():
        console.print("[red]错误: 无法连接到 Ollama 服务[/red]")
        raise typer.Exit(1)

    from storyforge.parser.story_parser import StoryParser
    parser = StoryParser(llm=llm)
    story_data = parser.parse(text, title=title)

    json_str = story_data.model_dump_json(indent=2, ensure_ascii=False)

    if output:
        Path(output).write_text(json_str, encoding="utf-8")
        console.print(f"[green]JSON 已保存: {output}[/green]")
    else:
        console.print(json_str)


@app.command()
def generate(
    input_json: Path = typer.Argument(..., help="结构化 JSON 文件路径"),
    output: Path = typer.Option("./output", "-o", "--output", help="输出目录"),
):
    """从结构化 JSON 生成 Ren'Py 项目（跳过 AI 解析步骤）"""
    _print_banner()

    if not input_json.exists():
        console.print(f"[red]错误: 文件不存在: {input_json}[/red]")
        raise typer.Exit(1)

    from storyforge.parser.models import StoryData
    raw = json.loads(input_json.read_text(encoding="utf-8"))
    story_data = StoryData.model_validate(raw)

    _print_summary(story_data)

    from storyforge.project.builder import ProjectBuilder
    builder = ProjectBuilder(story_data, output / story_data.title)
    project_path = builder.build()

    console.print(f"\n[bold green]完成！[/bold green] 项目路径: [bold]{project_path}[/bold]")


@app.command()
def config(
    ollama_url: str = typer.Option("", "--url", help="Ollama 服务地址"),
    model_name: str = typer.Option("", "--model", help="默认模型名称"),
    show: bool = typer.Option(False, "--show", help="显示当前配置"),
):
    """查看或修改配置"""
    from storyforge.config import get_config, update_config

    if show:
        cfg = get_config()
        table = Table(title="StoryForge 配置")
        table.add_column("配置项", style="bold")
        table.add_column("值")
        table.add_row("Ollama URL", cfg.ollama_url)
        table.add_row("模型名称", cfg.model_name)
        table.add_row("默认输出目录", cfg.default_output_dir)
        table.add_row("章节最大行数", str(cfg.max_chapter_lines))
        console.print(table)
        return

    kwargs = {}
    if ollama_url:
        kwargs["ollama_url"] = ollama_url
    if model_name:
        kwargs["model_name"] = model_name

    if kwargs:
        cfg = update_config(**kwargs)
        console.print("[green]配置已更新[/green]")
        for k, v in kwargs.items():
            console.print(f"  {k} = {v}")
    else:
        console.print("[dim]使用 --show 查看配置，或传入参数修改配置[/dim]")


@app.command()
def check():
    """检查 Ollama 连接和可用模型"""
    _print_banner()
    from storyforge.parser.llm_client import LLMClient

    llm = LLMClient()
    console.print(f"[bold]Ollama URL:[/bold] {llm.base_url}")
    console.print(f"[bold]目标模型:[/bold] {llm.model}")
    console.print()

    if llm.check_connection():
        console.print("[green]Ollama 连接成功[/green]")
        models = llm.list_models()
        if models:
            console.print(f"\n可用模型 ({len(models)}):")
            for m in models:
                marker = " [green]<-- 当前[/green]" if m == llm.model or m.startswith(llm.model + ":") else ""
                console.print(f"  - {m}{marker}")
        else:
            console.print("[yellow]暂无已下载的模型[/yellow]")
            console.print(f"[dim]运行: ollama pull {llm.model}[/dim]")
    else:
        console.print("[red]Ollama 连接失败[/red]")
        console.print("[dim]请确保 Ollama 正在运行: ollama serve[/dim]")


def _print_banner():
    console.print(Panel.fit(
        f"[bold cyan]StoryForge[/bold cyan] v{__version__}\n"
        "[dim]中文小说 → Ren'Py 游戏 自动转换工具[/dim]",
        border_style="cyan",
    ))
    console.print()


def _print_summary(story_data):
    """打印解析结果摘要"""
    table = Table(title="解析结果摘要")
    table.add_column("项目", style="bold")
    table.add_column("内容")
    table.add_row("标题", story_data.title)
    table.add_row("角色数", str(len(story_data.characters)))
    table.add_row("角色", ", ".join(c.name for c in story_data.characters))
    table.add_row("场景数", str(len(story_data.scenes)))
    table.add_row("场景", ", ".join(s.name for s in story_data.scenes))
    table.add_row("章节数", str(len(story_data.chapters)))
    total_segments = sum(len(ch.segments) for ch in story_data.chapters)
    table.add_row("总段落数", str(total_segments))
    total_choices = sum(len(ch.choices) for ch in story_data.chapters)
    table.add_row("选择点数", str(total_choices))
    table.add_row("结局数", str(len(story_data.endings)))
    table.add_row("变量数", str(len(story_data.variables)))
    console.print(table)


if __name__ == "__main__":
    app()
