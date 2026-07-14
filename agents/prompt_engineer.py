"""
Prompt工程 Agent —— 对标JD: 设计和优化Prompt、提示词生成
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from .base import BaseAgent, AgentResult
except ImportError:
    from agents.base import BaseAgent, AgentResult

IMAGE_PROMPT_SYS = """你是AI绘画Prompt工程师。为每个分镜生成中英文Prompt。
结构: [主体+动作] + [场景] + [光线] + [视角] + [风格标签(cinematic,photorealistic,8k)]
负向: blur, deformed, extra fingers, text artifacts
输出JSON: {"prompts":[{"shot_id":"","prompt_cn":"","prompt_en":"","negative_prompt":"","style_tags":[],"aspect_ratio":"16:9"}]}"""

VIDEO_PROMPT_SYS = """你是AI视频生成专家。为每个分镜生成视频Prompt。
包含: 画面内容+角色动作(谁动/怎么动/速度)+摄像机运动+时长
输出JSON: {"video_prompts":[{"shot_id":"","prompt":"","motion_description":"","camera_motion":"","duration_seconds":数字}]}"""


class PromptEngineerAgent(BaseAgent):
    role = "Prompt工程师"
    system_prompt = IMAGE_PROMPT_SYS

    def think(self, input_data: dict) -> dict:
        ptype = input_data.get("prompt_type", "image")
        return {
            "prompt_type": ptype,
            "sys_prompt": IMAGE_PROMPT_SYS if ptype == "image" else VIDEO_PROMPT_SYS,
        }

    def act(self, input_data: dict, plan: dict) -> dict:
        board = input_data.get("storyboard", {})
        self.system_prompt = plan["sys_prompt"]  # 切换 System Prompt

        raw = self.call_llm_safe_with_scan(
            instruction=f"请为以下分镜生成{plan['prompt_type']} Prompt：",
            user_content=json.dumps(board, ensure_ascii=False),
            content_label="前置分镜数据",
            json_mode=True
        )
        return self.extract_json(raw)

    def respond(self, result: dict) -> AgentResult:
        key = "prompts" if "prompts" in result else "video_prompts"
        return AgentResult(
            success=True, data=result,
            reasoning=f"Prompt生成完成: {len(result.get(key, []))} 条"
        )
