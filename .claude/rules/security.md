# AI 短剧平台 — 专属安全规则

继承全局规则（`D:\claude\.claude\rules\security.md`），在此基础上增加本项目的特殊规则：

## 全局规则的补充
本文件的所有规则附加到全局安全规则之上，不替代。

## 本项目专属规则

### LLM API 调用安全
- `DEEPSEEK_API_KEY` / `DOUBAO_API_KEY` 必须在 `.env` 中，禁止出现在任何 `.py` 文件里
- 你的 `.env.example` 文件已经只有占位符，保持这样
- 每次 API 调用不要记录完整的 prompt/output 到日志（可能含用户数据）

### 文件上传安全（生成结果存储）
- 生成的 JSON 结果文件禁止包含原始 API Key
- `output/` 目录下的结果文件要限制大小（单个文件不超过 50MB）
- 用户上传的剧本文件大小限制 1MB

### 用户数据处理
- 剧本内容属于用户创作内容，不在日志中明文记录
- 生成结果（分镜/Prompt）属于用户数据，禁止未经授权分享

### 依赖检查
- 本项目依赖：fastapi、uvicorn、requests、sqlalchemy、pydantic
- 这些包都已验证在 PyPI 存在且为最新稳定版
- 新增依赖前，先确认包名在 pypi.org 真实存在
