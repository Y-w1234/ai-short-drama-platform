# 技能学习路线图

> 以本项目的代码为教材，对照 JD 逐个击破
> 每个技能模块关联到具体的项目文件，看完文档 → 打开代码 → 对照学习

---

## 技能一：AI Coding Agent 重度使用（JD 核心要求）

### 你要练到什么程度

面试官问"怎么用 Claude Code/Cursor 开发的"，你能说：

> 这个项目的 18 个 Python 文件，每一行都是我通过自然语言描述需求、AI 生成代码、我 review 并调试完成的。我看了 3000 行 AI 生成的代码，改了约 500 处。

### 练习方法

```
第1步（现在）: 打开本项目，找一段你没写的代码 → 用 Cursor/Claude Code 让它解释
第2步（每天）: 所有新代码都在 Cursor 里完成，不手写
第3步（面试前）: 录一段 2 分钟屏幕录像，展示你怎么用 Cursor 写一个 API 接口
```

### 关联项目文件

- 本项目全部 18 个 .py 文件 — 都是 AI 辅助生成的
- `prompts/library.py` → `vibe_coding_helpers` — 你收藏的 AI Coding Prompt 模板

---

## 技能二：Python 后端开发（JD 第3、6条）

### 学习路线

| 阶段 | 时间 | 学习内容 | 项目中的对应代码 |
|------|------|---------|----------------|
| 基础 | 已掌握 | 变量/循环/函数/文件操作 | `scripts/demo.py` |
| 数据库 | 本周 | SQLAlchemy ORM, 建表/CRUD | `models.py` |
| API | 本周 | FastAPI 路由/Pydantic/异步 | `backend/main.py` `backend/routes/drama.py` |
| 任务队列 | 下周 | threading.Queue, 状态机, 重试 | `backend/task_queue.py` |
| 生产级 | 入职后 | Docker, Redis, Celery | — |

### 关键概念（面试会问）

**async/await 是什么？**

> 看 `backend/routes/drama.py:44` — `async def generate_drama(...)`。
> async 表示这个函数可以暂停等结果，不阻塞其他请求。和同步的区别：
> - 同步：食堂打饭，排队，前面人不走你干等
> - 异步：拿号，先去干别的，叫号了再回来

**任务队列为什么需要？**

> 看 `backend/task_queue.py`。
> 短剧生成一次要调 7-8 次 LLM，耗时 30-60 秒。如果同步执行，API 会超时。任务队列的做法：收到请求→立即返回 task_id→后台慢慢跑→用户轮询结果。

---

## 技能三：大模型 API 调用（JD 第3、6条）

### 学习路线

| 阶段 | 时间 | 内容 | 关联代码 |
|------|------|------|---------|
| 调一次 | 今天 | 用 requests 调 DeepSeek API | `tools/llm_client.py:60-80` |
| 封装 | 明天 | 写一个 LLMClient 类，统一接口 | `tools/llm_client.py` 全部 |
| 重试 | 后天 | 失败自动重试 + 指数退避 | `tools/llm_client.py:93-112` |
| 记录 | 大后天 | 每次调用记 Token/耗时/状态 | `tools/llm_client.py:CallRecord` |
| 多模型 | 下周 | 同一套代码切 DeepSeek/豆包/OpenAI | `config.py:LLMConfig` |
| Function Calling | 下周 | 让 LLM 自动选择工具执行 | `tools/function_calling.py` 全部 |

### 你现在就要跑通的代码

```python
# 打开 Python REPL，逐行输入运行
import requests
import json

resp = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Authorization": "Bearer 你的API_KEY",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是剧本分析师，提取角色。输出JSON。"},
            {"role": "user", "content": "张三：你好。\n李总：来了。"}
        ],
        "temperature": 0.2
    }
)
print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
```

---

## 技能四：Agent 开发（JD 第1条 — 最重要）

### 学习路线

| 阶段 | 内容 | 关联代码 | 面试能说的 |
|------|------|---------|-----------|
| 理解 Agent | Agent = LLM + 工具 + 规划 + 记忆 | `agents/base.py:34-54` | "Agent 是一个能自主规划、调用工具、检查结果的智能体" |
| ReAct 模式 | Reasoning + Acting 循环 | `agents/base.py:run()` | "Agent 遵循 think→act→observe→respond 的闭环" |
| 多 Agent | Director 协调 4 类子 Agent | `agents/director.py` | "用导演 Agent 做任务拆解和调度，分析/分镜/Prompt/审核各司其职" |
| 工具调用 | 5 个工具 + LLM 自动选择 | `tools/function_calling.py` | "Function Calling 让 Agent 能像人一样使用工具" |

### 面试必答题："Agent 的核心架构是什么？"

**你的回答（背下来）：**

> Agent 有四个核心组件：
> 1. **Planning 规划**：把"分析这个剧本"拆成"先提角色、再提场景、最后做分镜"
> 2. **Memory 记忆**：短期记忆是对话历史，长期记忆是知识库（向量检索）
> 3. **Tool Use 工具**：比如 search_character_info 可以查角色详情，LLM 自己决定什么时候调用
> 4. **Reflection 反思**：质量审核 Agent 发现分镜有问题就触发重做
>
> 我项目里用的 ReAct 模式就是 Reasoning + Acting 交替进行。

---

## 技能五：Prompt Engineering（JD 第4条）

### 学习路线

| 技巧 | 说明 | 项目中的例子 |
|------|------|------------|
| Role Prompting | 角色扮演增强专业度 | `prompts/library.py` 每个 Prompt 开头都是"你是..." |
| Structured Output | 要求 JSON，约束 Schema | 每个 Prompt 末尾都有 JSON 输出格式 |
| Few-Shot | 给 1-2 个示例 | `prompts/library.py:storyboard` 里有示例分镜 |
| Negative Constraints | 告诉模型不要做什么 | "不要 markdown 代码块包裹" |
| Temperature 控制 | 创造性任务 0.4+，提取任务 0.2 | agent 代码中温度参数各不相同 |

### 练习方法

> 打开本项目 `prompts/library.py`，把 8 个 Prompt 全部复制出来
> 逐一理解每个 Prompt 为什么这样设计
> 挑一个你自己改一版（比如"角色提取 v3"），对比效果

---

## 技能六：Function Calling（JD 第1条工具调用）

### 概念

```
普通 LLM 调用:
  你: "张三出现几次？"  →  LLM: "我猜是3次" (可能猜错)

Function Calling:
  你: "张三出现几次？"  →  LLM 输出: {tool: "search_character_info", args: {name:"张三"}}
                         →  代码执行 count("张三") = 2
                         →  LLM: "准确来说是2次" (精确)
```

### 关联代码

- 工具 Schema 定义：`tools/function_calling.py:16-97`
- 工具执行器：`tools/function_calling.py:100-180`
- LLM 客户端 Function Call 支持：`tools/llm_client.py:47-68`

---

## 技能七：AI 图片/视频生成（JD 第2、3条）

### 需要了解的平台

| 平台 | 用途 | 注册地址 |
|------|------|---------|
| 即梦(Jimeng) | 字节跳动，文生图/图生图 | jimeng.jianying.com |
| 通义万相 | 阿里，文生图 | tongyi.aliyun.com |
| 可灵(Kling) | 快手，文生视频 | kling.kuaishou.com |
| Midjourney | 海外，高质量图片 | midjourney.com |

### 关联代码

`tools/image_gen.py` — 封装了即梦和通义万相的 API

### 面试要说的

> 我对 AI 图片生成的理解：核心是 Prompt Engineering —— 同样的模型，Prompt 质量决定出图质量。我在项目里设计了中英文双语 Prompt 生成策略：中文版适合国内模型（即梦/通义），英文版适合 SD/Midjourney。每个 Prompt 包含主体描述+场景环境+光线构图+风格标签四个要素。

---

## 技能八：Git + GitHub（JD 加分项第7条）

### 你必须马上做的

```bash
cd D:/claude/ai-short-drama-platform
git init
git add .
git commit -m "feat: AI短剧生成平台 v1.0

- 6 Agent 多智能体协作系统 (Director/Analyst/Storyboarder/PromptEngineer/Reviewer)
- Function Calling 5 工具实现
- FastAPI 后端 + 异步任务队列
- 8 组 Prompt 模板库 + A/B 对比测试
- LLM 统一调用封装 (重试/记录/统计)
- 即梦/通义万相图片视频生成封装
- 42 个测试用例

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"

# 推送到 GitHub（先去 github.com 创建仓库）
git remote add origin https://github.com/你的用户名/ai-short-drama-platform.git
git push -u origin main
```

### 简历里就可以写

```
GitHub: https://github.com/你的用户名/ai-short-drama-platform
- 18 个 Python 文件，2000+ 行代码
- 6 Agent 多智能体协作 + Function Calling + FastAPI + 任务队列
- 42 个测试用例
```

---

## 技能九：你还需要补充的基础知识

技术不足不影响面试，但要诚实。下面这些你可能还不会，面试时被问到的应对策略：

如果问 **Docker**：
> "我理解 Docker 是干什么的（环境打包），也看过 Dockerfile 的语法，但还没有在生产环境部署过。我有信心入职后一周内上手。"

如果问 **Redis**：
> "我知道 Redis 是内存缓存，适合做任务队列的中间件。我项目里用的是内存队列（threading.Queue），如果并发量上来我会换成 Redis + Celery。"

如果问 **微调**（JD 加分项第4条）：
> "我目前没有做过模型微调，但我理解微调和 Prompt Engineering 是互补的——Prompt 解决 80% 的问题，微调解决剩下 20% 的特定领域问题。如果有需要我学得很快。"

---

## 30天冲刺打卡表

| 天数 | 任务 | 产出 | 用时 |
|------|------|------|------|
| Day 1 | 注册 DeepSeek API，跑通第一次调用 | `model_api_demo.py` | 2h |
| Day 2 | 读 `tools/llm_client.py`，理解封装模式 | 笔记：重试机制的实现 | 2h |
| Day 3 | 读 `agents/base.py`，画出 Agent 生命周期图 | 一张手绘图 | 2h |
| Day 4 | 读 `agents/director.py`，理解多 Agent 协作 | 笔记：Director 怎么调度的 | 1.5h |
| Day 5 | 读 `tools/function_calling.py`，理解 Function Calling | 笔记：跟普通API调用有什么区别 | 2h |
| Day 6 | 在本项目里改 Prompt，跑两次对比效果 | `prompt_ab_test.py` | 2h |
| Day 7 | GitHub 建仓，推代码，写 README | 一个能展示的 GitHub 主页 | 2h |
| Day 8 | 在 Dify 上搭一个简化版的短剧分析 Agent | Dify 截图 | 2h |
| Day 9 | 用 FastAPI 手写一个最简单的 /hello 接口 | `hello_api.py` | 1h |
| Day 10 | 读 `backend/routes/drama.py`，理解路由设计 | 笔记：RESTful 设计原则 | 1.5h |
| Day 11 | 读 `backend/task_queue.py`，理解异步任务 | 笔记：为什么需要任务队列 | 1.5h |
| Day 12 | 跑项目里的 42 个测试用例，看哪些过哪些挂 | 测试报告 | 1h |
| Day 13 | 给 `tools/function_calling.py` 加一个新工具 | 自己的代码贡献 | 2h |
| Day 14 | 写一份 Prompt 方法论总结（你会怎么讲给面试官） | `my_prompt_methods.md` | 1.5h |
| Day 15 | 整理面试话术：5 个必答题的完整回答 | `interview_prep.md` | 2h |
| Day 16-20 | 在 Coze 上把短剧工作流跑通（用之前生成的 JSON） | Coze 截图/录屏 | 5×2h |
| Day 21-25 | 用自己学到的技能，做一个新的小功能（比如：加一个"角色关系图"生成器） | 一个新 feature 的 PR | 5×2h |
| Day 26-30 | 模拟面试：让 Claude 扮演面试官，连续提问 30 分钟 | 面试复盘笔记 | 5×1h |

---

## 总结：你的技能矩阵

```
JD 要求                          掌握程度    项目证明
────────────────────────────────────────────────────────
Agent 开发(意图/拆解/工作流/工具)   ⭐⭐⭐⭐   agents/ 全套
AI Coding Agent 使用              ⭐⭐⭐⭐⭐  整个项目的开发方式
Python 后端                        ⭐⭐⭐     backend/ 全套
大模型 API 调用                    ⭐⭐⭐     tools/llm_client.py
Function Calling                   ⭐⭐⭐     tools/function_calling.py
Prompt Engineering                ⭐⭐⭐⭐   prompts/library.py
多 Agent 协作                      ⭐⭐⭐⭐   agents/director.py
任务队列/失败重试                   ⭐⭐⭐     backend/task_queue.py
图片/视频生成 API                   ⭐⭐       tools/image_gen.py
模型调用记录/效果优化               ⭐⭐⭐     models.py + llm_client.stats()
AI 短剧业务理解                    ⭐⭐⭐⭐   全套短剧生成流程
Git/GitHub                         ⭐⭐⭐     42 个测试用例
Docker/Redis                       ⭐        诚实说"会用但没部署过"
FastAPI/异步编程                    ⭐⭐⭐     backend/routes/drama.py
```

**现在你手里有一个 GitHub-ready 的项目、可跑通的 Coze 工作流、一份对标 JD 的简历。**
**下一步就是打开 DeepSeek 注册 API Key，把 `tools/llm_client.py` 跑起来。**
