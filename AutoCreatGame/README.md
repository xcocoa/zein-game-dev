# StoryForge — AI 互动叙事引擎

> 把小说变成可玩的视觉小说游戏，让每个有故事的人都能零成本做出自己的游戏。

---

## 这是什么

StoryForge 是一个 AI 驱动的内容转换工具：**输入一篇中文小说，自动输出一个可玩的视觉小说（Galgame）游戏**。

整个过程全自动——AI 负责提取角色、识别场景、分析对话、生成互动选择和多结局分支，最终输出完整的游戏项目。

**实际效果**：用芥川龙之介的《罗生门》（3000 字）做测试，全程自动完成。游戏包含 2 个角色、3 个章节、2 个互动选择点、4 个不同结局。

---

## 快速开始

### 环境要求

- Python 3.11+
- [Ollama](https://ollama.ai/)（本地 LLM 推理）

### 安装

```bash
cd AutoCreatGame
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 配置 Ollama 模型

```bash
# 安装并启动 Ollama
ollama pull huihui_ai/qwen3-abliterated

# 验证连接
storyforge check
```

### 一键转换

```bash
# 将小说转为可玩的 Ren'Py 游戏
storyforge convert your_novel.txt --title "你的游戏标题"

# 生成的游戏在 output/ 目录下，用 Ren'Py 打开即可运行
```

### 更多命令

```bash
storyforge parse novel.txt -o story.json    # 仅解析，输出 JSON
storyforge generate story.json               # 从 JSON 生成游戏（无需 LLM）
storyforge config --model other_model        # 切换模型
storyforge check                             # 检查 Ollama 连接状态
```

---

## 工作原理

### 6 阶段 LLM 编排管线

```
小说文本
  → Step 1: 角色提取（识别人物、性格、关系）
  → Step 2: 场景识别（地点、氛围、时间）
  → Step 3: 结构分析（对话/叙述/动作分类）
  → Step 4: 选择生成（互动决策点、变量效果）
  → Step 5: 结局设计（多结局、触发条件）
  → Step 6: 章节划分（节奏把控）
  → 结构化故事数据（JSON）
```

### 编译器级架构

```
Parser（LLM 解析器）→ AST（抽象语法树）→ Code Generator（代码生成器）
```

- **Parser 层**：LLM 将自然语言转为结构化数据（Pydantic 模型）
- **AST 层**：18 种节点类型表示游戏逻辑（对话、选择、条件、跳转……）
- **Generator 层**：AST → 目标代码（当前支持 Ren'Py，架构可扩展至 Web/Unity/Godot）

---

## 项目结构

```
AutoCreatGame/
├── storyforge/
│   ├── parser/          # LLM 解析管线
│   │   ├── llm_client.py    # Ollama API 客户端
│   │   ├── prompts.py       # 6 阶段中文优化 prompt
│   │   ├── story_parser.py  # 解析编排器
│   │   └── models.py        # Pydantic 数据模型
│   ├── ast/             # 抽象语法树
│   │   └── nodes.py         # 18 种 Ren'Py AST 节点
│   ├── generator/       # 代码生成器
│   │   └── renpy_generator.py
│   ├── project/         # 项目构建器
│   │   └── builder.py       # 生成完整 Ren'Py 项目
│   ├── cli.py           # CLI 入口
│   └── config.py        # 配置管理
├── tests/               # 104 个单元测试
├── examples/            # 示例小说
└── pyproject.toml
```

## 技术栈

| 层级 | 技术 |
|------|------|
| LLM 解析 | Ollama（本地）/ 云端 API（计划中） |
| 数据模型 | Python + Pydantic |
| AST 节点 | Python dataclass，18 种 Ren'Py 语句类型 |
| 代码生成 | 自研 Ren'Py 生成器 |
| 项目构建 | 自动生成完整可运行项目（含中文字体、GUI 屏幕） |
| 测试 | pytest，104 个用例 |
| CLI | Typer + Rich |

---

## Roadmap

**Phase 1 — Web 化（进行中）**
- [ ] 后端 API 服务（FastAPI）
- [ ] Web 视觉小说播放器（浏览器内直接玩）
- [ ] 云端 LLM 支持（DeepSeek / Qwen API）

**Phase 2 — 体验增强**
- [ ] AI 生成角色立绘和场景背景
- [ ] 可视化剧情编辑器
- [ ] 作品广场（发布、浏览、分享）

**Phase 3 — 更多可能**
- [ ] 多引擎输出（Unity / Godot）
- [ ] BGM / 语音合成
- [ ] 多语言支持

---

## 寻找队友

我们正在组建一个小团队，寻找以下方向的伙伴：

**AI 工程师** — LLM 管线优化、云端模型接入、AI 生图集成
- 有 LLM 应用开发经验，对 prompt engineering 有实践心得
- 这里有真实的技术挑战：从非结构化小说中抽取角色关系、情节分支、情感变量

**前端工程师** — Web 播放器、剧情可视化编辑器
- React/Vue 熟练，对游戏或互动体验感兴趣
- 对话动画系统、分支选择交互、节点图编辑器——游戏级的前端工程

**后端工程师** — API 服务、任务队列、部署运维
- Python（FastAPI）或 Go，有异步任务处理经验
- 从 0 到 1 搭建 AI SaaS 后端架构

不需要全职投入，业余时间参与也可以。关键是对 AI + 互动内容这个方向有兴趣。

---

## 联系方式

- GitHub: [项目地址]
- 微信: [你的微信号]
- 邮箱: [你的邮箱]

---

## License

MIT
