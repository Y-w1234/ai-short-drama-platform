"""
质量审核 Agent —— 对标JD: 跟进模型效果、优化AI生成质量
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from .base import BaseAgent, AgentResult
except ImportError:
    from agents.base import BaseAgent, AgentResult

REVIEWER_PROMPT = """你是影视质量审核专家。审核分镜方案，5维度每项0-5分:
1. narrative_flow 叙事连贯性  2. visual_consistency 视觉一致性
3. pacing 节奏把控  4. emotional_expression 情感表达
5. generatability Prompt可生成性

输出JSON: {"scores":{维度名:{score:数字,reason:""}},"overall_score":数字,"verdict":"通过/修改/重做","suggestions":[]}"""


class ReviewerAgent(BaseAgent):
    role = "质量审核员"
    system_prompt = REVIEWER_PROMPT

    def act(self, input_data: dict, plan: dict) -> dict:
        storyboard = input_data.get("storyboard", {})
        img = input_data.get("image_prompts", {})
        vid = input_data.get("video_prompts", {})

        raw = self.call_llm(
            f"分镜方案：{storyboard}\n图片Prompt：{img}\n视频Prompt：{vid}",
            json_mode=True
        )
        return self.extract_json(raw)

    def observe(self, result: dict) -> bool:
        # 评分低于3分则不满意，触发重试
        return result.get("overall_score", 0) >= 3.0

    def respond(self, result: dict) -> AgentResult:
        return AgentResult(
            success=result.get("overall_score", 0) >= 3.0,
            data=result,
            reasoning=f"质量评分: {result.get('overall_score', '?')}/5 ({result.get('verdict', '?')})"
        )
