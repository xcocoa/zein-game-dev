# Zein Game Dev

用 AI 让每个人都能做自己的游戏。

---

## 项目全景

本仓库包含两个项目，它们代表了同一个目标的两个阶段：

```
Phase 1 — 手工制作              Phase 2 — AI 自动化
┌─────────────────────┐        ┌─────────────────────────┐
│   世界碎片            │  启发   │     StoryForge           │
│  (World Fragments)   │ ─────→ │   AI 互动叙事引擎         │
│                     │        │                         │
│  手写 Ren'Py 脚本    │        │  小说 → AI 解析 → 游戏    │
│  3 个互动世界         │        │  全自动，零手写代码        │
│  探索叙事游戏的可能性  │        │  把手工经验产品化         │
└─────────────────────┘        └─────────────────────────┘
       game/                      AutoCreatGame/
```

**为什么会有两个项目？**

「世界碎片」是我们手工制作的第一个 Ren'Py 互动叙事游戏。在制作过程中我们发现：写故事的人很多，但能把故事变成可玩游戏的人很少——瓶颈不在创意，而在技术门槛。

于是我们开始做 StoryForge：用 AI 自动完成从小说到游戏的全部技术工作。手工制作游戏时积累的经验（屏幕设计、GUI 布局、中文排版、选择分支逻辑）直接输入到了 StoryForge 的代码生成器中。

**一句话总结**：世界碎片证明了「小说可以变成好玩的游戏」，StoryForge 让这件事可以自动化、规模化。

---

## StoryForge — AI 互动叙事引擎

> 输入一篇中文小说，自动输出一个可玩的视觉小说游戏。

### 它能做什么

用芥川龙之介《罗生门》（3000 字）测试，全程自动：

```
输入：一篇小说 .txt 文件
输出：完整的 Ren'Py 游戏项目
      ├── 2 个角色（自动提取）
      ├── 3 个章节（自动划分）
      ├── 2 个互动选择点（AI 生成）
      └── 4 个不同结局（多分支）
```

用 Ren'Py 打开即可运行，不需要写一行代码。

### 快速开始

```bash
cd AutoCreatGame
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# 安装 Ollama 并拉取模型
ollama pull huihui_ai/qwen3-abliterated

# 一键转换
storyforge convert your_novel.txt --title "你的游戏"
```

生成的游戏在 `output/` 目录下，用 [Ren'Py](https://www.renpy.org/) 打开即可运行。

### 工作原理

采用编译器级三层架构，将非结构化小说文本转为可执行的游戏代码：

```
                 6 阶段 LLM 管线
小说文本 ──→ ┌──────────────────────────┐ ──→ 结构化数据（JSON）
             │ 角色提取 → 场景识别       │
             │ 结构分析 → 选择生成       │
             │ 结局设计 → 章节划分       │
             └──────────────────────────┘
                         │
                  AST 中间表示（18 种节点类型）
                         │
                   Code Generator
                         │
                   ┌─────┴─────┐
                 Ren'Py    Web/Unity
                （已实现）  （计划中）
```

- **Parser 层**：LLM 将自然语言转为结构化数据（Pydantic 模型验证）
- **AST 层**：18 种节点类型表示游戏逻辑（对话、选择、条件、跳转……）
- **Generator 层**：AST → 目标引擎代码，当前输出 Ren'Py，架构可扩展

### 技术栈

| 模块 | 技术 |
|------|------|
| LLM | Ollama 本地推理 / 云端 API（计划中） |
| 数据模型 | Pydantic |
| AST | Python dataclass，18 种语句节点 |
| 生成器 | Ren'Py .rpy 代码生成 |
| 构建器 | 完整游戏项目（含中文字体、GUI 屏幕） |
| CLI | Typer + Rich |
| 测试 | 104 个单元测试 |

### 命令一览

```bash
storyforge convert novel.txt --title "标题"   # 小说 → 游戏（完整流程）
storyforge parse novel.txt -o story.json       # 仅 AI 解析，输出 JSON
storyforge generate story.json                  # JSON → 游戏（无需 LLM）
storyforge config --model your_model            # 切换模型
storyforge check                                # 检查连接状态
```

### 项目结构

```
AutoCreatGame/
├── storyforge/
│   ├── parser/            # LLM 解析管线（6 阶段 prompt 编排）
│   ├── ast/               # 抽象语法树（18 种 Ren'Py 节点）
│   ├── generator/         # 代码生成器
│   ├── project/           # 项目构建器（字体、GUI、配置）
│   ├── cli.py             # 命令行入口
│   └── config.py          # 配置管理
├── tests/                 # 104 个单元测试
├── examples/              # 示例小说（罗生门、天台上的约定）
└── pyproject.toml
```

---

## 世界碎片 (World Fragments)

> StoryForge 的灵感来源——一个手工制作的 Ren'Py 互动叙事游戏 Demo。

玩家扮演一个「世界访客」，进入陌生人留下的生活碎片，通过文字和选择感受不同的故事。

包含三个世界：
- **世界一**：林晓的周五下午（探索路线 + 留言 + 多结局）
- **世界二**：方鸿渐的某个下午（改编自《围城》）
- **世界三**：学吉他的那段日子（含吉他练习互动界面）

这个项目让我们积累了 Ren'Py 开发经验——屏幕布局、中文字体适配、分支叙事设计、GUI 交互等。这些经验后来成为 StoryForge 代码生成器的核心知识。

### 运行方法

1. 下载 [Ren'Py SDK](https://www.renpy.org/latest.html)
2. 打开 Ren'Py Launcher → 添加项目 → 选择本仓库根目录
3. 启动项目

---

## 两个项目的关系

| | 世界碎片 (game/) | StoryForge (AutoCreatGame/) |
|---|---|---|
| **定位** | 手工制作的游戏 Demo | AI 自动化转换工具 |
| **输入** | 开发者手写 .rpy 脚本 | 任意小说 .txt 文件 |
| **输出** | 3 个固定世界 | 无限多的游戏 |
| **技术门槛** | 需要会写 Ren'Py | 不需要任何代码能力 |
| **角色** | 验证了叙事游戏的可能性 | 将手工经验产品化 |
| **状态** | 已完成 Demo | 核心功能已完成，持续迭代 |

---

## Roadmap

- [x] CLI 工具 + Ren'Py 输出
- [x] 中文字体自动集成
- [x] 多结局 + 互动选择生成
- [ ] Web 平台（浏览器内上传、生成、在线玩）
- [ ] AI 生成角色立绘和场景背景
- [ ] 可视化剧情编辑器
- [ ] 云端 LLM 支持（DeepSeek / Qwen API）
- [ ] 多引擎输出（Web / Unity / Godot）

---

## 参与贡献

欢迎提交 Issue 和 PR。如果你对以下方向感兴趣，特别欢迎参与：

- **AI / NLP**：LLM 管线优化、prompt 工程、AI 生图集成
- **前端**：Web 视觉小说播放器、可视化剧情编辑器
- **后端**：API 服务、异步任务队列、SaaS 架构
- **游戏开发**：Ren'Py 高级特效、多引擎适配

---

## License

MIT
