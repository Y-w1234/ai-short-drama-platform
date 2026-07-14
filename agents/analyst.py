"""
剧本分析 Agent —— 对标JD: 剧本解析、角色提取、场景提取、道具提取
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from .base import BaseAgent, AgentResult
except ImportError:
    from agents.base import BaseAgent, AgentResult

ANALYST_SYSTEM_PROMPT = """你是专业影视剧本分析师。根据任务类型完成对应提取工作:
- character: 提取角色(名称/类型/性格/外貌/关系)
- scene: 提取场景(地点/时间/光线/氛围/道具)
- props: 提取道具(名称/类别/级别/描述)
输出严格JSON。"""

CHARACTER_PROMPT = """请分析以下剧本，提取所有角色。对每个角色输出:
id(char_001格式), name, type(主角/反派/配角/龙套), gender, age_group,
personality(3-5词数组), appearance(3个特征数组), first_line, relationships([{to,relation}])
输出JSON: {"characters":[...], "total":数字}"""

SCENE_PROMPT = """请分析以下剧本，提取所有场景。对每个场景输出:
id, name, location_type, time_of_day, description(80字+), lighting,
atmosphere, color_tone, characters_present(数组), key_props(数组)
输出JSON: {"scenes":[...], "total":数字}"""

PROPS_PROMPT = """请分析以下剧本，提取所有道具。对每个道具输出:
id, name, category, priority(A/B/C), scenes(数组), used_by(数组), description
输出JSON: {"props":[...], "total":数字}"""

TASK_MAP = {
    "character": (CHARACTER_PROMPT, "角色提取"),
    "scene": (SCENE_PROMPT, "场景提取"),
    "props": (PROPS_PROMPT, "道具提取"),
}

class AnalystAgent(BaseAgent):
    role = "剧本分析师"
    system_prompt = ANALYST_SYSTEM_PROMPT

    def think(self, input_data: dict) -> dict:
        task = input_data.get("task", "character")
        task_info = TASK_MAP.get(task, TASK_MAP["character"])
        return {"task_type": task, "task_name": task_info[1], "prompt": task_info[0]}

    def act(self, input_data: dict, plan: dict) -> dict:
        script = input_data.get("script_text", "")
        raw = self.call_llm_safe(
            instruction=plan['prompt'],
            user_content=script,
            content_label="剧本",
        )
        return self.extract_json(raw)

    def respond(self, result: dict) -> AgentResult:
        # 统一返回格式
        key = "characters" if "characters" in result else "scenes" if "scenes" in result else "props"
        return AgentResult(
            success=True,
            data=result,
            reasoning=f"提取完成: {result.get('total', 0)} 个{key}"
        )
