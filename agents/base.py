"""
Agent 基类 —— 对标JD: 意图识别、任务拆解、多Agent协作

每个 Agent 都有: 角色定义(System Prompt) + 工具集(Function Calling) + 执行方法
"""
import json
import sys, os
from typing import Optional, Any
from dataclasses import dataclass, field

# Make project root importable when run directly
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

@dataclass
class AgentResult:
    """Agent执行结果"""
    success: bool = True
    data: dict = field(default_factory=dict)
    reasoning: str = ""         # 推理过程 —— 对标JD"意图识别"
    tool_calls: list = field(default_factory=list)  # 工具调用记录
    error: str = ""

class BaseAgent:
    """AI Agent 基类 —— 对标JD: Agent应用能力建设

    每个 Agent 的生命周期:
    1. think()     —— 意图识别 & 任务拆解
    2. act()       —— 调用工具 / 调用LLM / 执行业务逻辑
    3. observe()   —— 检查结果，决定是否重试
    4. respond()   —— 格式化输出
    """

    # 子类需要覆写的属性
    role: str = ""           # 角色名称
    system_prompt: str = ""  # System Prompt
    tools: list[dict] = []   # 可调用的工具列表

    def __init__(self, llm_client=None, tool_executor=None):
        self.llm = llm_client
        self.tools_executor = tool_executor
        self.context: dict = {}      # Agent 上下文(共享记忆)
        self.history: list[dict] = []  # 对话历史

    def run(self, input_data: dict, context: dict = None) -> AgentResult:
        """Agent 主执行流程 —— React 模式"""
        if context:
            self.context = context

        try:
            # Step 1: 意图识别 + 任务拆解
            plan = self.think(input_data)

            # Step 2: 执行 (可能包含多轮 tool call)
            result = self.act(input_data, plan)

            # Step 3: 结果检查
            if not self.observe(result):
                # 结果不理想，重试一次
                result = self.act(input_data, plan)

            # Step 4: 格式化输出
            return self.respond(result)

        except Exception as e:
            return AgentResult(success=False, error=str(e))

    def think(self, input_data: dict) -> dict:
        """意图识别 + 任务拆解 —— 确定要做什么、怎么做"""
        return {"task": self.role, "input_summary": str(input_data)[:200]}

    def act(self, input_data: dict, plan: dict) -> Any:
        """执行业务逻辑 —— 子类覆写"""
        raise NotImplementedError

    def observe(self, result: Any) -> bool:
        """检查结果质量 —— 返回 True 表示满意"""
        return True

    def respond(self, result: Any) -> AgentResult:
        """格式化输出"""
        return AgentResult(success=True, data=result if isinstance(result, dict) else {})

    def call_llm(self, user_message: str, json_mode: bool = True) -> str:
        """调用 LLM"""
        if self.llm:
            return self.llm.chat(self.system_prompt, user_message, json_mode=json_mode)
        return "{}"

    def extract_json(self, raw: str) -> dict:
        """从 LLM 输出中提取 JSON —— 对标JD"异常处理机制" """
        text = raw.strip()
        for fence in ["```json", "```"]:
            if fence in text:
                parts = text.split(fence)
                text = parts[1] if len(parts) >= 2 else text
                if "```" in text:
                    text = text.split("```")[0]
                break
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass
            return {"raw": raw, "parse_error": True}
