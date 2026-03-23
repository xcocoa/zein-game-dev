# Zein Game Dev

用 AI 让每个人都能做自己的游戏。本仓库包含两个项目：一个手工制作的 Ren'Py 互动叙事游戏，和一个 AI 驱动的小说转游戏自动化工具。

---

## StoryForge — AI 互动叙事引擎

> 输入一篇中文小说，自动输出一个可玩的视觉小说游戏。

StoryForge 是一个开源的 AI 内容转换工具。通过 6 阶段 LLM 管线，自动从小说中提取角色、识别场景、分析对话、生成互动选择和多结局分支，最终输出完整的 [Ren'Py](https://www.renpy.org/) 游戏项目。

### 效果演示

用芥川龙之介《罗生门》（3000 字）测试，全程自动：

```
输入：一篇小说文本
输出：包含 2 个角色、3 个章节、2 个互动选择点、4 个结局的完整游戏
```

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

生成的游戏在 `output/` 目录下，用 Ren'Py 打开即可运行。

### 工作原理

采用编译器级三层架构：

```
              6 阶段 LLM 管线
小说文本 ──→ ┌─────────────────────────┐ ──→ 结构化数据（JSON）
             │ 角色提取 → 场景识别     │
             │ 结构分析 → 选择生成     │
             │ 结局设计 → 章节划分     │
             └─────────────────────────┘
                        │
                   AST 中间表示
                  （18 种节点类型）
                        │
                  Code Generator
                        │
                  ┌─────┴─────┐
                Ren'Py    Web/Unity
               （已实现）  （计划中）
```

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

### Roadmap

- [x] CLI 工具 + Ren'Py 输出
- [x] 中文字体自动集成
- [x] 多结局 + 互动选择生成
- [ ] Web 平台（浏览器内上传、生成、在线玩）
- [ ] AI 生成角色立绘和场景背景
- [ ] 可视化剧情编辑器
- [ ] 云端 LLM 支持（DeepSeek / Qwen API）
- [ ] 多引擎输出（Web / Unity / Godot）

---

## 世界碎片 (World Fragments)

基于 Ren'Py 手工制作的互动叙事游戏 Demo。玩家扮演一个「世界访客」，进入陌生人留下的生活碎片，通过文字和选择感受不同的故事。

包含三个世界：
- 世界一：林晓的周五下午（探索路线 + 留言 + 多结局）
- 世界二：方鸿渐的某个下午（改编自《围城》）
- 世界三：学吉他的那段日子（含吉他练习互动界面）

### 运行方法

1. 下载 [Ren'Py SDK](https://www.renpy.org/latest.html)
2. 打开 Ren'Py Launcher → 添加项目 → 选择本仓库根目录
3. 启动项目

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
