"""
统一LLM调用客户端 —— 对标JD: 接入大语言模型、接口封装、失败重试、调用记录

功能：
1. 统一封装 DeepSeek / 豆包 / OpenAI 等模型调用
2. 自动重试(失败重试 + 指数退避)
3. 记录每次调用的耗时、Token消耗、状态
4. 支持 Function Calling / JSON Mode
"""
import time
import json
import logging
from datetime import datetime
from typing import Optional, Callable
from dataclasses import dataclass, field

import requests

try:
    from ..config import config
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config

logger = logging.getLogger(__name__)

# ============================================================
# Call logging callback（对标JD: 模型调用记录）
# ============================================================
@dataclass
class CallRecord:
    """单次调用记录"""
    model_name: str
    provider: str
    call_type: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    status: str = "success"
    retry_count: int = 0
    error_message: str = ""


class LLMClient:
    """大模型统一调用客户端

    对标JD要求:
    - "接入大语言模型、图片生成模型、视频生成模型等能力"
    - "完成接口封装和调用逻辑开发"
    - "失败重试"机制
    - "模型调用记录"
    """

    def __init__(self, call_logger: Optional[Callable] = None):
        self.cfg = config.llm
        self.records: list[CallRecord] = []
        self.call_logger = call_logger

    def chat(self, system: str, user: str, *,
             temperature: float = None,
             max_tokens: int = None,
             call_type: str = "chat",
             json_mode: bool = True) -> str:
        """对话补全 —— 带重试机制"""
        temp = temperature if temperature is not None else self.cfg.temperature
        maxtok = max_tokens if max_tokens is not None else self.cfg.max_tokens

        body = {
            "model": self.cfg.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temp,
            "max_tokens": maxtok,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        return self._request(body, call_type)

    def function_call(self, system: str, user: str,
                      tools: list[dict],
                      tool_choice: str = "auto") -> dict:
        """Function Calling —— 对标JD: 工具调用模块

        Args:
            system: 系统提示
            user: 用户输入
            tools: 工具定义列表 [{"name":"","description":"","parameters":{}}]
            tool_choice: "auto" 或 "required"

        Returns:
            {"name": "函数名", "arguments": {...}} 或 {"content": "纯文本回复"}
        """
        body = {
            "model": self.cfg.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "tools": tools,
            "tool_choice": tool_choice,
        }
        raw = self._request(body, "function_call")
        data = json.loads(raw) if isinstance(raw, str) else raw

        # 解析 tool_calls
        if "tool_calls" in data and data["tool_calls"]:
            tc = data["tool_calls"][0]
            return {
                "type": "tool_call",
                "name": tc["function"]["name"],
                "arguments": json.loads(tc["function"]["arguments"])
                if isinstance(tc["function"]["arguments"], str)
                else tc["function"]["arguments"],
            }
        return {"type": "text", "content": data.get("content", raw)}

    # ---- 内部 ----
    def _request(self, body: dict, call_type: str) -> str:
        """发送请求，带重试"""
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        }

        record = CallRecord(
            model_name=self.cfg.model,
            provider=self.cfg.provider,
            call_type=call_type,
        )

        for attempt in range(self.cfg.max_retries + 1):
            t0 = time.time()
            try:
                resp = requests.post(
                    f"{self.cfg.base_url}/chat/completions",
                    headers=headers,
                    json=body,
                    timeout=self.cfg.timeout,
                )
                elapsed = int((time.time() - t0) * 1000)
                resp.raise_for_status()
                data = resp.json()

                usage = data.get("usage", {})
                record.prompt_tokens = usage.get("prompt_tokens", 0)
                record.completion_tokens = usage.get("completion_tokens", 0)
                record.latency_ms = elapsed
                record.status = "success"
                record.retry_count = attempt
                self._save(record)

                return data["choices"][0]["message"]["content"]

            except Exception as e:
                elapsed = int((time.time() - t0) * 1000)
                record.status = "failed" if attempt == self.cfg.max_retries else "retry"
                record.latency_ms = elapsed
                record.retry_count = attempt
                record.error_message = str(e)

                if attempt < self.cfg.max_retries:
                    logger.warning(f"[{call_type}] 第{attempt+1}次调用失败，{self.cfg.retry_delay}s后重试: {e}")
                    time.sleep(self.cfg.retry_delay * (attempt + 1))  # 指数退避
                else:
                    logger.error(f"[{call_type}] 所有重试均失败: {e}")
                    self._save(record)
                    raise

    def _save(self, record: CallRecord):
        self.records.append(record)
        if self.call_logger:
            self.call_logger(record)

    def stats(self) -> dict:
        """统计信息 —— 对标JD: 跟进模型效果"""
        if not self.records:
            return {"total_calls": 0}
        success = [r for r in self.records if r.status == "success"]
        return {
            "total_calls": len(self.records),
            "success_rate": len(success) / len(self.records) if self.records else 0,
            "avg_latency_ms": sum(r.latency_ms for r in success) / len(success) if success else 0,
            "total_prompt_tokens": sum(r.prompt_tokens for r in self.records),
            "total_completion_tokens": sum(r.completion_tokens for r in self.records),
            "by_type": {
                t: {
                    "count": len([r for r in self.records if r.call_type == t]),
                    "avg_latency_ms": sum(r.latency_ms for r in self.records if r.call_type == t) / max(len([r for r in self.records if r.call_type == t]), 1),
                }
                for t in set(r.call_type for r in self.records)
            }
        }
