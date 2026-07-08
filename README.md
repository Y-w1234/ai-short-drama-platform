# 🎬 AI 短剧生成平台

AI 驱动的短剧自动生成系统 —— 从剧本到分镜 Prompt，全链路自动化。

> 对标岗位：AI应用开发工程师（AI短剧方向）| 长沙 | 2026

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 快速体验（无需 API Key）
python -m scripts.demo

# 3. 启动 API 服务
cp .env.example .env          # 编辑填入你的 API Key
uvicorn backend.main:app --reload

# 4. 访问 Swagger 文档
open http://localhost:8000/docs
```

## 项目结构

```
ai-short-drama-platform/
├── backend/               # FastAPI 后端服务
│   ├── main.py           # 应用入口 + 路由注册
│   ├── task_queue.py     # 异步任务队列 + 失败重试
│   └── routes/drama.py   # 短剧生成 API
│
├── agents/                # 多 Agent 协作系统
│   ├── base.py           # Agent 基类 (React 模式)
│   ├── director.py       # 导演 Agent (总调度)
│   ├── analyst.py        # 剧本分析 Agent
│   ├── storyboarder.py   # 分镜规划 Agent
│   ├── prompt_engineer.py # Prompt 工程 Agent
│   └── reviewer.py       # 质量审核 Agent
│
├── tools/                 # 工具层
│   ├── llm_client.py     # LLM 统一调用 (重试+记录)
│   ├── function_calling.py # Function Calling 实现
│   └── image_gen.py      # 图片/视频生成封装
│
├── prompts/               # Prompt 模板库
│   └── library.py        # 8 组验证过的 Prompt + A/B 对比
│
├── scripts/
│   └── demo.py           # 一键演示 (无需 API Key)
│
├── config.py              # 统一配置管理
├── models.py              # 数据库模型 (调用记录+任务管理)
├── requirements.txt
├── .env.example
└── README.md
```

## 工作流架构

```
用户提交剧本
    ↓
┌─────────────────────────────────────────┐
│ Director Agent (总调度)                   │
│   ├─ Analyst Agent ×3 (并行)              │
│   │   ├ 角色提取                         │
│   │   ├ 场景提取                         │
│   │   └ 道具提取                         │
│   ├─ Storyboarder Agent                  │
│   │   └ 分镜表 (11维)                    │
│   ├─ PromptEngineer Agent ×2 (并行)       │
│   │   ├ 图片 Prompt (中英双语)            │
│   │   └ 视频 Prompt                      │
│   └─ Reviewer Agent                      │
│       └ 5维质量评分                       │
└─────────────────────────────────────────┘
    ↓
JSON 输出: 分镜表 + Prompt + 质量报告
```

## 对标 JD 清单

| JD 要求 | 实现位置 | 状态 |
|---------|---------|------|
| Agent 应用能力 (意图识别/任务拆解/工作流编排/多轮对话/工具调用) | `agents/` 全部 | ✅ |
| AI 短剧创作 (剧本解析/角色/场景/道具/分镜/Prompt) | `agents/analyst.py` `agents/storyboarder.py` | ✅ |
| 接入大模型/图片/视频生成模型 | `tools/llm_client.py` `tools/image_gen.py` | ✅ |
| 设计和优化 Prompt/工作流/异常处理 | `prompts/library.py` `agents/base.py` | ✅ |
| 使用 Claude Code/Cursor 快速开发 | 本项目的开发过程 | ✅ |
| 后端功能 (任务队列/调用记录/结果管理/失败重试) | `backend/task_queue.py` `models.py` | ✅ |
| 跟进模型效果，优化生成质量 | `tools/llm_client.py` stats() `prompts/library.py` prompt_compare() | ✅ |
| Coze/Dify/LangChain 经验 | Coze 工作流 + `agents/base.py` (自研框架) | ✅ |
| Function Calling | `tools/function_calling.py` | ✅ |
| RAG/知识库/意图识别 | Agent 知识库 + `agents/base.py` think() | ✅ |
| 多 Agent 协作 | `agents/director.py` + 全部 Agent | ✅ |

## 技术亮点

- **React 模式 Agent**: 每个 Agent 遵循 think()→act()→observe()→respond() 生命周期
- **Function Calling**: 5 个专业工具，LLM 自动选择并生成参数
- **多 Agent 协作**: Director 调度 4 类专业 Agent，Parallel + Pipeline 混合编排
- **任务队列**: 异步执行 + 自动重试 + 状态追踪 + TTL 过期
- **调用记录**: 完整记录每次 LLM 调用的 Token、耗时、状态
- **Prompt 版本管理**: 8 组 Prompt 模板，支持 A/B 对比测试
- **API First**: FastAPI + Swagger 文档，可直接集成到前端

## API 示例

```bash
# 提交短剧生成任务
curl -X POST http://localhost:8000/api/v1/drama/generate \
  -H "Content-Type: application/json" \
  -d '{"script_text": "【第一场】办公室 - 下午\n张三：李总，不好了！\n李总：什么？！"}'

# 查询任务结果
curl http://localhost:8000/api/v1/drama/task/{task_id}

# 查看最近任务列表
curl http://localhost:8000/api/v1/drama/tasks
```

## License

MIT — 本项目的 Prompt 模板和架构设计可自由使用和修改。
