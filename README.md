# 🤖 AI 短剧生成平台 (AI Short Drama Platform)

> 多 Agent 协作的 AI 短剧自动生成系统  
> 输入剧本 → 7 个 Agent 协作 → 输出完整分镜表 + 图片/视频 Prompt

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎬 Demo

📺 **[2 分钟演示视频](https://www.bilibili.com/video/BV1NeMi6NENu/)** — B 站在线观看

**一行命令，无需 API Key：**

```bash
python -m scripts.demo
```

输入「求婚」短剧剧本 → 7 个阶段自动运行 → 输出 8 镜分镜表 + 中英双语 Prompt + 质量报告

<details>
<summary>📺 点击展开 Demo 输出预览</summary>

```
============================================================
  AI 短剧生成平台 — Demo 模式
  (无需 API Key，使用内置示例数据)
============================================================

  [Phase 1] 预处理: 210字符, 12行, 约1.0分钟
  [Phase 2] 角色提取: 2个角色 (小红/小明)
  [Phase 3] 场景提取: 1个场景 (街角咖啡厅)
  [Phase 4] 道具提取: 3个道具 (戒指盒/咖啡杯/手机)
  [Phase 5] 分镜规划: 8个分镜, 预估100秒
  [Phase 6] Prompt生成: 8图片, 8视频
  [Phase 7] 质量审核: 5.0/5 (通过)

  总耗时: 1.7秒
  项目: 求婚
```

</details>

## 🏗️ Agent 架构

```
                     ┌──────────────┐
   剧本输入 ────────→│  Director     │
                     │  Agent (调度器)│
                     └──────┬───────┘
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ 角色提取   │    │ 场景提取   │    │ 道具提取   │  ← 3 Agent 并行
    │ Analyst   │    │ Analyst   │    │ Analyst   │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         └───────────────┼───────────────┘
                         ▼
                  ┌──────────────┐
                  │ Storyboarder │  ← 主 Agent：11 维分镜表
                  │ Agent        │
                  └──────┬───────┘
           ┌─────────────┴─────────────┐
           ▼                           ▼
    ┌──────────────┐           ┌──────────────┐
    │ 图片 Prompt   │           │ 视频 Prompt   │  ← 2 Agent 并行
    │ Engineer     │           │ Engineer     │
    └──────┬───────┘           └──────┬───────┘
           └──────────┬───────────────┘
                      ▼
               ┌──────────────┐
               │  Reviewer     │  ← 5 维评分 (叙事/视觉/节奏/情感/可生成性)
               │  Agent        │
               └──────┬───────┘
                      ▼
                 📦 JSON 输出
```

## 🔧 Agent 核心设计

### React 模式（think → act → observe → respond）

每个 Agent 遵循标准的思考-行动-观察-响应循环，自主决定下一步做什么。

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
| `search_character_info` | 查询角色特征库（性格/外貌/关系） |
| `analyze_scene_atmosphere` | 分析场景氛围、光线、色调 |
| `suggest_shot_composition` | 根据角色数/对白/情绪推荐景别机位 |
| `estimate_shot_duration` | 根据台词字数+动作数估算时长 |
| `generate_image_prompt` | 生成中英双语 AI 绘画 Prompt |

### 技术亮点

- **LLM 统一客户端**：DeepSeek / 豆包 / OpenAI 三接口，自动重试（指数退避）+ 调用日志 + Token 统计
- **异步任务队列**：支持并发请求，失败自动重试 + TTL 过期
- **A/B Prompt 测试**：8 组 Prompt 支持版本对比，可量化评估效果
- **多模态集成**：对接即梦 + 通义万相图片/视频生成 API

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Y-w1234/ai-short-drama-platform.git
cd ai-short-drama-platform
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 离线 Demo（不调 API 也能跑）

```bash
python -m scripts.demo
```

### 4. 使用真实 API

```bash
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 启动 API 服务
python run.py
# → http://localhost:8000/docs
```

## 📡 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 |
| `/api/v1/drama/generate` | POST | 提交剧本，启动完整分析流水线 |
| `/api/v1/drama/task/{task_id}` | GET | 查询分析任务状态与结果 |
| `/api/v1/drama/tasks` | GET | 获取最近任务列表 |

**使用示例：**

```bash
# 提交短剧生成任务
curl -X POST http://localhost:8000/api/v1/drama/generate \
  -H "Content-Type: application/json" \
  -d '{"script_text": "【第一场】办公室 - 下午\n张三：李总，不好了！\n李总：什么？！"}'

# 查询任务结果
curl http://localhost:8000/api/v1/drama/task/{task_id}
```

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| **Agent 框架** | 自研 React 模式 |
| **LLM** | DeepSeek / 豆包 / OpenAI |
| **后端** | FastAPI + Uvicorn |
| **数据库** | SQLite + SQLAlchemy |
| **任务队列** | asyncio + 自研重试机制 |
| **多模态** | 即梦 API + 通义万相 API |

## 📂 项目结构

```
ai-short-drama-platform/
├── agents/                  # 多 Agent 协作系统
│   ├── base.py             # Agent 基类（React 模式）
│   ├── director.py         # 导演 Agent（总调度）
│   ├── analyst.py          # 剧本分析 Agent（角色/场景/道具）
│   ├── storyboarder.py     # 分镜规划 Agent（11 维分镜表）
│   ├── prompt_engineer.py  # Prompt 工程 Agent（图片/视频）
│   └── reviewer.py         # 质量审核 Agent（5 维评分）
├── tools/                   # 工具层
│   ├── llm_client.py       # LLM 统一客户端（重试+记录）
│   ├── function_calling.py # 5 个 Tool Schema + 执行器
│   └── image_gen.py        # 图片/视频生成 API 封装
├── prompts/
│   └── library.py          # 8 组验证过的 Prompt + A/B 对比
├── backend/                 # FastAPI 后端
│   ├── main.py             # 应用入口
│   ├── routes/drama.py     # 短剧生成 API 路由
│   └── task_queue.py       # 异步任务队列
├── scripts/
│   ├── demo.py             # 离线演示（无需 API Key）
│   └── cli.py              # 命令行工具
├── tests/
│   └── test_pipeline.py    # 流水线测试
├── config.py               # 统一配置管理
├── models.py               # 数据库模型
├── run.py                  # 一键启动脚本
└── requirements.txt
```

## 📝 License

MIT

---

## 🔗 相关项目

| 项目 | 说明 |
|------|------|
| [📚 RAG 问答系统](https://github.com/Y-w1234/my-rag-project) | FastAPI + LangChain + ChromaDB 私有知识库问答 |
| [🎬 短剧流水线（单文件版）](https://github.com/Y-w1234/ai-short-drama-pipeline) | 纯 Python 单文件实现，快速理解核心流程 |
