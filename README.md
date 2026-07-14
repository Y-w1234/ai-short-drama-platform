# 🎬 AI 原生视频生产管线 (AI Native Video Production Pipeline)

> **Agent 驱动的多场景视频自动生成系统**  
> 短剧 · 电商带货 · 知识口播 · 跨境内容 — 一套 Agent 架构，覆盖全部视频生产场景

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688)](https://fastapi.tiangolo.com)
[![Multi-Scene](https://img.shields.io/badge/scenes-4-orange)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Demo](https://img.shields.io/badge/Demo-Offline%20Mode-brightgreen)](#快速开始)

---

## 一句话介绍

**输入任何形式的内容（剧本/商品文案/知识文章/跨境产品信息），多 Agent 协作系统自动完成：理解内容 → 拆解要素 → 规划分镜 → 生成 Prompt → 质量审核 → 输出可执行的视频制作方案。**

同一套 Agent 管线，换一套 Prompt 模板，就能从"做短剧"切换到"做带货视频"。

---

## 🎯 支持场景

| 场景 | 输入 | 输出 | 一行命令 |
|------|------|------|----------|
| 🎬 **短剧** | 中文剧本 | 角色/场景/道具提取 + 11维分镜表 + 中英双语Prompt | `python -m scripts.cli demo` |
| 🛒 **电商商品展示** | 商品名+卖点 | 卖点拆解 + 场景化分镜 + 产品摄影Prompt + 口播文案 | `--scene product_showcase` |
| 📚 **知识口播** | 科普文章/观点 | 信息层次拆解 + 可视化分镜（含动画/图表描述） | `--scene knowledge_short` |
| 🌍 **跨境多语言** | 商品+目标市场 | 本地化分镜 + 文化适配建议 + 多语言Prompt | `--scene cross_border` |

**4 个场景 = 同一套 Agent 管线 + 不同 Prompt 模板。** 换场景不换架构。

---

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────┐
│                    场景层 (Scene Layer)                   │
│  🎬短剧    🛒电商    📚口播    🌍跨境                     │
│  每个场景定义了自己的 Prompt 模板、默认参数、Demo 数据      │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   Agent 编排层 (Director)                 │
│  任务拆解 → Agent 调度 → 结果汇总 → 最终交付               │
└────────────────────────┬────────────────────────────────┘
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Analyst  │  │ Analyst  │  │ Analyst  │  ← 3 Agent 并行
    │ (角色提取)│  │ (场景提取)│  │ (道具/卖点)│
    └────┬─────┘  └────┬─────┘  └────┬─────┘
         └──────────────┼──────────────┘
                        ▼
                 ┌──────────────┐
                 │ Storyboarder │  ← 核心：多维度分镜表
                 └──────┬───────┘
          ┌─────────────┴─────────────┐
          ▼                           ▼
   ┌──────────────┐           ┌──────────────┐
   │ 图片 Prompt   │           │ 视频 Prompt   │  ← 2 Agent 并行
   └──────┬───────┘           └──────┬───────┘
          └──────────┬───────────────┘
                     ▼
              ┌──────────────┐
              │  Reviewer     │  ← 多维度质量评分
              └──────┬───────┘
                     ▼
                📦 输出结果
```

### Agent 核心设计

每个 Agent 遵循 **React 模式**（think → act → observe → respond），自主决策下一步：

```python
class BaseAgent:
    def run(self, input_data, context):
        plan = self.think(input_data)        # 意图识别 + 任务拆解
        result = self.act(input_data, plan)  # 执行业务逻辑
        if not self.observe(result):         # 结果检查
            result = self.act(input_data, plan)  # 不理想则重试
        return self.respond(result)          # 格式化输出
```

### Function Calling（5 个 Tool Schema）

| Tool | 功能 |
|------|------|
| `search_character_info` | 查询角色特征库 |
| `analyze_scene_atmosphere` | 分析场景氛围、光线、色调 |
| `suggest_shot_composition` | 根据参数推荐景别机位 |
| `estimate_shot_duration` | 根据台词+动作估算时长 |
| `generate_image_prompt` | 生成中英双语 AI 绘画 Prompt |

---

## 🚀 快速开始

### 1. 克隆 & 安装

```bash
git clone https://github.com/Y-w1234/ai-short-drama-platform.git
cd ai-short-drama-platform
pip install -r requirements.txt
```

### 2. 30 秒体验（无需 API Key）

```bash
# 短剧场景
python -m scripts.cli demo

# 电商商品展示
python -m scripts.cli demo --scene product_showcase

# 知识口播
python -m scripts.cli demo --scene knowledge_short

# 跨境多语言
python -m scripts.cli demo --scene cross_border

# 列出所有场景
python -m scripts.cli scenes
```

### 3. 使用真实 API

```bash
cp .env.example .env
# 编辑 .env → 填入 DEEPSEEK_API_KEY
python run.py
# → http://localhost:8000/docs
```

---

## Demo 输出预览

### 🛒 电商商品展示 — ProPods X1 蓝牙耳机 (15秒)

```
[Phase 1] 商品信息解析: 5个核心卖点
[Phase 2] 卖点拆解: 5个卖点 (降噪★/续航★/低延迟/防水/性价比★)
[Phase 3] 使用场景: 4个场景 (地铁/健身房/电竞桌/产品台)
[Phase 5] 分镜规划: 5个分镜, 预估15秒

shot_001: 地铁车厢痛点钩子 "受够了通勤噪音？"
shot_002: 手指触控→42dB降噪→世界安静
shot_003: 健身房IPX5防水→随便造
shot_004: 游戏分屏→40ms低延迟→听声辨位
shot_005: 360°产品展示→¥299→CTA购买链接

[Quality] 5.0/5 (通过)
```

### 📚 知识口播 — AI 为什么能理解人类语言？(60秒)

```
[Phase 2] 信息拆解: 5个核心知识点
[Phase 5] 信息可视化分镜: 6个分镜, 预估60秒

shot_001: "填空题"钩子 → 大模型就是超级完形填空
shot_002: 图书馆动画 → 读了整个互联网
shot_003: 概率填空动画 → 不是理解，是统计
shot_004: 鹦鹉 vs 小朋友 → 能说≠懂
shot_005: AI乱画 → 一本正经胡说八道 = 幻觉
shot_006: 鹦鹉飞走→发光大脑 → 从预测到理解

[Quality] 4.8/5 (通过)
```

---

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 管线信息 + 支持的场景类型 |
| `/health` | GET | 健康检查 |
| `/api/v1/drama/generate` | POST | 提交内容，启动完整分析流水线 |
| `/api/v1/drama/task/{task_id}` | GET | 查询任务状态与结果 |
| `/api/v1/drama/tasks` | GET | 获取最近任务列表 |
| `/api/v1/drama/scenes` | GET | 列出所有视频场景类型 |

**请求示例：**

```bash
# 短剧
curl -X POST http://localhost:8000/api/v1/drama/generate \
  -H "Content-Type: application/json" \
  -d '{"script_text": "【第一场】...", "scene_type": "short_drama"}'

# 电商商品展示
curl -X POST http://localhost:8000/api/v1/drama/generate \
  -H "Content-Type: application/json" \
  -d '{"script_text": "ProPods X1 | 42dB ANC | ¥299", "scene_type": "product_showcase"}'
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **Agent 框架** | 自研 React 模式 (think→act→observe→respond) | 对标: 意图识别、任务拆解、多Agent协作 |
| **LLM 客户端** | DeepSeek / 豆包 / OpenAI 三接口统一封装 | 自动重试 + 指数退避 + Token 统计 + 调用记录 |
| **Function Calling** | 5 个 Tool Schema (OpenAI 兼容格式) | LLM 决策 → 代码执行 → 结果返回 |
| **后端** | FastAPI + Uvicorn | RESTful API + Swagger 文档 |
| **数据库** | SQLite + SQLAlchemy | 模型调用日志 + 任务记录 |
| **任务队列** | asyncio + 自研多线程队列 | 异步执行 + 失败重试 + TTL 过期 |
| **多模态** | 即梦 API + 通义万相 API | 图片/视频生成接口封装 |
| **Prompt 管理** | 版本化 Prompt 模板库 (10+组) | A/B 对比测试 + 场景专属变体 |

---

## 📂 项目结构

```
ai-short-drama-platform/
├── scenes/                  # 场景层（NEW v2.0）
│   └── __init__.py         # 场景注册表 + 4个场景定义
├── agents/                  # Agent 协作系统
│   ├── base.py             # Agent 基类（React 模式）
│   ├── director.py         # 导演 Agent（总调度）
│   ├── analyst.py          # 分析 Agent（角色/场景/道具/卖点）
│   ├── storyboarder.py     # 分镜 Agent（多维度分镜表）
│   ├── prompt_engineer.py  # Prompt 工程 Agent
│   └── reviewer.py         # 质量审核 Agent（多维度评分）
├── tools/                   # 工具层
│   ├── llm_client.py       # LLM 统一客户端
│   ├── function_calling.py # Function Calling 工具
│   └── image_gen.py        # 图片/视频生成 API 封装
├── prompts/
│   └── library.py          # 10+ 组版本化 Prompt + 场景变体
├── backend/                 # API 服务
│   ├── main.py             # FastAPI 应用入口
│   ├── routes/drama.py     # 管线 API 路由
│   └── task_queue.py       # 异步任务队列
├── scripts/
│   ├── demo.py             # 多场景离线演示
│   └── cli.py              # 命令行工具
├── tests/                   # 测试
├── config.py               # 统一配置管理
├── models.py               # 数据库模型
└── run.py                  # 一键启动
```

---

## 🧪 测试

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## 🔮 路线图

- [x] 多场景支持（短剧/电商/口播/跨境）
- [x] 场景注册表 + 场景专属 Prompt
- [x] React 模式 Agent 框架
- [x] Function Calling 完整实现
- [ ] 对接即梦/通义万相 API 实际生成图片
- [ ] LangGraph 可视化工作流迁移
- [ ] Web UI (Streamlit)
- [ ] Docker 一键部署
- [ ] 视频自动合成 (Remotion 集成)

---

## 🎤 面试叙事

> "我做的是一个 **Agent 驱动的视频生产管线**，不是只能做短剧的工具。
>
> 同一个 Agent 架构（7 个 Agent，React 模式，Function Calling，任务队列），换一套 Prompt 模板就能从做短剧切换到做电商带货视频、知识科普视频、跨境多语言内容。
>
> 我验证了 4 个场景，每个场景都有完整的内置 Demo 数据。这套管线的核心价值在于：**AI 视频生成模型（即梦/Sora/可灵）越来越强，但没有人做'用 Agent 串联从内容理解到视频制作全流程'这件事**。这就是我在做的。"

---

## 📝 License

MIT

---

> 🤖 本项目为 AI 辅助开发作品。Agent 架构、Prompt 工程、多场景设计由作者主导；代码实现由 Claude Code 辅助生成。
