# 🎬 AI 短剧生成平台 — Demo 视频录制方案书

> **目标时长**：2 分钟 | **工具**：Win + G（Windows 游戏栏）| **分辨率**：1920×1080  
> **上传平台**：B 站 | **标题**：`AI短剧生成平台 Demo | 多Agent协作 | FastAPI`  
> **标签**：AI Agent、短剧生成、大模型应用、Python、FastAPI

---

## 🎯 视频章节划分（2 分钟）

```
[0:00-0:10]  第 1 幕：GitHub README + 架构图封面
[0:10-0:30]  第 2 幕：终端运行 Demo（7 阶段全流程）
[0:30-0:50]  第 3 幕：输出 JSON 结果（分镜表 + Prompt）
[0:50-1:15]  第 4 幕：CLI 工具集展示
[1:15-1:40]  第 5 幕：FastAPI + Swagger 在线调试
[1:40-2:00]  第 6 幕：代码亮点 + 总结
```

---

## 📹 第 1 幕：封面页（0:00-0:10）

### 录制位置

```
网址栏：https://github.com/Y-w1234/ai-short-drama-platform
```

### 操作步骤

| 时间 | 操作 | 屏幕显示 |
|------|------|---------|
| 0:00 | 打开浏览器，输入 GitHub 地址 | README 页面从上往下慢慢滚动 |
| 0:03 | 滚到架构图位置 | ASCII 架构图（7 个 Agent 流程图） |
| 0:06 | 滚到技术亮点位置 | 看到「React 模式」「Function Calling」「A/B Prompt」 |
| 0:08 | 滚到底部 | 项目结构树 |

### 🎤 台词

> "AI 短剧生成平台——7 个 Agent 协作，从剧本到完整分镜表全链路自动化。这个视频 2 分钟带你跑通全流程。"

---

## 📹 第 2 幕：终端 Demo 运行（0:10-0:30）

### 录制位置

```
终端：D:\claude\ai-short-drama-platform\>
```

### ⚠️ 录前准备（必须提前做好！）

```bash
# 1. 先进入项目目录
cd D:\claude\ai-short-drama-platform

# 2. 确认 Demo 能跑通（预演一次）
python -m scripts.demo

# 3. 清屏，等待录制
cls
```

### 操作步骤

| 时间 | 操作 | 屏幕显示 |
|------|------|---------|
| 0:10 | 输入命令 `python -m scripts.demo` 回车 | 终端开始输出 |
| 0:12 | Phase 1 输出 | `预处理: 210字符, 12行, 约1.0分钟` |
| 0:14 | Phase 2-4 输出 | `角色提取: 2个角色` `场景提取: 1个场景` `道具提取: 3个道具` |
| 0:17 | Phase 5 输出 | `分镜规划: 8个分镜, 预估100秒` |
| 0:19 | Phase 6 输出 | `Prompt生成: 8图片, 8视频` |
| 0:21 | Phase 7 输出 | `质量审核: 5.0/5 (通过)` |
| 0:23 | 总耗时行 | `总耗时: 1.7秒` |
| 0:25 | 指向最后一行 | `结果已保存: output/demo_result.json` |

### 🎤 台词

> "一行命令，无需任何 API Key。7 个阶段全自动：预处理→角色→场景→道具→分镜规划→Prompt 生成→质量审核。8 个分镜 1.7 秒跑完，全部满分通过。"

---

## 📹 第 3 幕：JSON 输出结果（0:30-0:50）

### 录制位置 3A：VS Code 打开 JSON 文件

```
文件路径：D:\claude\ai-short-drama-platform\output\demo_result.json
```

### 操作步骤

| 时间 | 操作 | 屏幕显示 |
|------|------|---------|
| 0:30 | 在 VS Code 中打开 `output/demo_result.json` | 左侧文件树高亮该文件 |
| 0:32 | 折叠/展开 JSON 结构 | 看到顶层字段：`project` `characters` `scenes` `storyboard` `quality_report` 等 |
| 0:35 | 展开 `characters` | 看到 2 个角色（小红/小明），各有 personality、appearance、relationships |
| 0:38 | 展开 `storyboard[0]` | 看到第 1 个分镜：`shot_001`，全景、推镜头、焦虑氛围 |
| 0:41 | 往下滚到 `storyboard[4]` | 看到第 5 个分镜（戒指盒特写），大特写 shot_type |
| 0:44 | 展开 `image_prompts` | 看到中英双语 Prompt，如 `cinematic photorealistic 8k, ...` |
| 0:47 | 展开 `quality_report` | 看到 5 维评分，每项 5 分 |

### 🎤 台词

> "输出的 JSON 结构完整：角色带性格外貌关系、分镜表含 11 个维度——shot_type、camera_angle、visual_description 100 字以上的画面描述。每个分镜还生成中英双语 AI 绘画 Prompt，附带负向提示词。最后是 5 维质量审核报告。"

---

## 📹 第 4 幕：CLI 工具集（0:50-1:15）

### 录制位置

```
终端：D:\claude\ai-short-drama-platform\>
```

### 操作步骤

| 时间 | 操作 | 屏幕显示 |
|------|------|---------|
| 0:50 | `cls` 清屏 | 干净的终端 |
| 0:52 | `python -m scripts.cli help` | 7 个命令列表：demo, run, tools, prompts, serve, test |
| 0:55 | `python -m scripts.cli tools` | 5 个 Function Calling 工具，每个带参数和说明 |
| 1:00 | `python -m scripts.cli prompts` | 8 组 Prompt 模板（格式清晰的列表） |
| 1:05 | `python -m scripts.cli test` | pytest 开始跑，7 个测试类快速输出绿点 |
| 1:10 | 测试结果 | `xx passed` 全部绿色 |

### 🎤 台词

> "CLI 工具提供 7 个命令。tools 列出 5 个 Function Calling 工具——搜索角色、分析场景、建议构图、估算时长、生成 Prompt。prompts 展示 8 组经过验证的 Prompt 模板。test 跑一遍完整的测试套件——全部通过。"

---

## 📹 第 5 幕：FastAPI + Swagger（1:15-1:40）

### 录制位置

```
终端 + 浏览器双窗口切换
```

### ⚠️ 录前准备

```bash
# 确保 8000 端口没有被占用
# 如果已经启动过，先 Ctrl+C 关掉
```

### 操作步骤

| 时间 | 操作 | 屏幕显示 |
|------|------|---------|
| 1:15 | 终端：`python run.py` | 输出 `Starting AI Short Drama Platform...` 和 `API docs: http://localhost:8000/docs` |
| 1:18 | 浏览器打开 `http://localhost:8000/docs` | Swagger UI 页面 |
| 1:20 | 点击 `GET /` | 返回 service info JSON |
| 1:22 | 点击 `GET /health` → Try it out → Execute | 返回 `{"status":"ok"}` |
| 1:25 | 展开 `POST /api/v1/drama/generate` → Try it out | 在 Request body 填入短剧剧本 JSON |
| 1:28 | 点击 Execute | 返回 `{"task_id":"xxx","status":"pending","message":"任务已提交"}` |
| 1:30 | 复制 task_id，粘贴到 `GET /api/v1/drama/task/{task_id}` | 返回任务进度和最终结果 |
| 1:35 | 点击 `GET /api/v1/drama/tasks` | 返回最近任务列表 |

### 🎤 台词

> "`python run.py` 一键启动 FastAPI 服务。Swagger 文档自动生成，3 个接口可以直接在线调试。提交剧本→拿到 task_id→查询进度和结果→任务列表。异步任务队列支持并发和失败重试。"

---

## 📹 第 6 幕：代码亮点 + 总结（1:40-2:00）

### 录制位置 6A：VS Code 代码浏览

```
打开以下 3 个文件，每个停留 5 秒
```

| 时间 | 文件 | 展示重点 |
|------|------|---------|
| 1:40 | `agents/base.py` | `run()` 方法：think→act→observe→respond 四步循环，光标指向第 46 行 |
| 1:45 | `tools/llm_client.py` | `_request()` 方法：for 循环重试、指数退避、Token 统计、调用记录 |
| 1:50 | `tools/function_calling.py` | 5 个 Tool Schema 定义（`TOOLS` 列表），执行器 `ToolExecutor` 类 |

### 录制位置 6B：回到 GitHub README 底部

| 时间 | 操作 | 屏幕显示 |
|------|------|---------|
| 1:55 | 浏览器切回 GitHub README | 技术栈 badges 和 License |
| 1:57 | 滚到「相关项目」部分 | 看到 RAG 项目的链接 |
| 1:59 | 定格 | GitHub 仓库主页全貌 |

### 🎤 台词

> "技术上，Agent 基类实现了 React 模式——think→act→observe→respond，不理想自动重试。LLM 客户端封装了 DeepSeek/豆包/OpenAI 三接口，带自动重试和调用统计。5 个 Function Calling 工具，LLM 自动选择并生成参数。项目 MIT 开源，欢迎 Star 和 PR！"

---

## ✅ 录制前检查清单

### 环境准备
- [ ] 关闭所有无关窗口（微信、QQ、通知弹窗）
- [ ] 浏览器只保留 1 个标签页
- [ ] 终端字体调大（建议 14pt+），背景深色
- [ ] VS Code 关闭侧边栏无关文件夹，只留本项目
- [ ] 桌面壁纸换成纯色（避免分散注意力）

### 内容准备
- [ ] 在终端预演一次 `python -m scripts.demo`，确认正常
- [ ] 在终端预演一次 `python -m scripts.cli help` / `tools` / `prompts`
- [ ] 确认 `python -m scripts.cli test` 能通过
- [ ] 在终端预演一次 `python run.py`，确认服务启动
- [ ] 浏览器确认 `http://localhost:8000/docs` 能打开
- [ ] VS Code 打开 `output/demo_result.json` 确认文件存在

### 录制技巧
- [ ] 鼠标移动不要太快（观众跟不上）
- [ ] 点击之前停顿 0.5 秒（给观众反应时间）
- [ ] 每幕之间有 1-2 秒黑屏/定格过渡
- [ ] 如果念错台词，停下来重新录这一段（后期可以剪）

---

## 🎬 后期处理建议

| 处理 | 工具 | 说明 |
|------|------|------|
| 剪辑 | CapCut / 剪映 | 去掉卡顿、口误、多余等待 |
| 字幕 | 剪映自动识别 | 自动生成后手动修正 |
| 缩放强调 | 剪映关键帧 | JSON 字段太小可放大展示 |
| 背景音乐 | 剪映素材库 | 轻量科技感纯音乐，音量 20% |

---

## 📤 上传 B 站配置

```
标题：AI短剧生成平台 Demo | 多Agent协作 | FastAPI | 2分钟跑通全流程
类型：科技 → 软件应用
标签：AI Agent、短剧生成、大模型应用、Python、FastAPI、开源
简介：
  GitHub: https://github.com/Y-w1234/ai-short-drama-platform
  7 个 AI Agent 协作，从剧本输入到完整分镜表 + 图片/视频 Prompt 全自动生成。
  支持离线 Demo（无需 API Key），一行命令体验完整流程。
```
