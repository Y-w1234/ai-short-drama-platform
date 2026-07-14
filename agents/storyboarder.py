"""
分镜规划 Agent —— 对标JD: 分镜规划、提示词生成
核心节点，将剧本转化为可执行的分镜表
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from .base import BaseAgent, AgentResult
except ImportError:
    from agents.base import BaseAgent, AgentResult

STORYBOARDER_PROMPT = """# 角色
你是资深短剧导演/分镜师，擅长短剧节奏把控。

# 分镜原则
- 每个情节转折至少1个分镜 | 对白用正反打 | 情绪高点用特写 | 环境建立用全景
- 1分钟短剧约8-15个分镜 | 同角色多分镜中外貌必须一致

# 对每个分镜输出
shot_id, scene_id, shot_type(远景/全景/中景/近景/特写/大特写),
camera_angle(平视/俯视/仰视/过肩/主观视角), camera_setup,
visual_description(100字+画面描述), character_actions({角色:动作表情}),
dialogue, duration_seconds(数字), camera_movement, transition, mood

输出JSON: {"project":{"title":"","genre":"","estimated_duration":""},"storyboard":[...]}"""


class StoryboarderAgent(BaseAgent):
    role = "分镜师"
    system_prompt = STORYBOARDER_PROMPT

    def think(self, input_data: dict) -> dict:
        script = input_data.get("script_text", "")
        chars = input_data.get("characters", {})
        return {
            "script_len": len(script),
            "char_count": chars.get("total", 0),
            "estimated_shots": max(8, min(20, len(script) // 40)),
        }

    def act(self, input_data: dict, plan: dict) -> dict:
        script = input_data.get("script_text", "")
        chars = input_data.get("characters", {})
        scenes = input_data.get("scenes", {})
        props = input_data.get("props", {})

        context = f"""角色列表: {chars}
场景列表: {scenes}
道具列表: {props}"""

        instruction = f"已提取的结构信息：\n{context}\n\n请根据以上信息和下面的剧本生成详细分镜表。"
        raw = self.call_llm_safe(
            instruction=instruction,
            user_content=script,
            content_label="剧本",
            json_mode=True,
        )
        return self.extract_json(raw)

    def respond(self, result: dict) -> AgentResult:
        return AgentResult(
            success=True,
            data=result,
            reasoning=f"分镜规划完成: {len(result.get('storyboard', []))} 个分镜"
        )
