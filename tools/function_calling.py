"""
Function Calling 工具定义与执行 —— 对标JD: 工具调用模块

完整的 Function Calling 实现:
1. 定义工具 Schema（OpenAI 兼容格式）
2. LLM 自动选择工具并生成参数
3. 代码解析 tool_call 并执行
4. 结果返回给 LLM 继续处理
"""
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ============================================================
# 工具 Schema 定义
# ============================================================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_character_info",
            "description": "搜索角色在剧本中的所有出场信息，包括台词、动作、情绪变化",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string", "description": "角色名称"},
                },
                "required": ["character_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_scene_atmosphere",
            "description": "深度分析指定场景的氛围、光线、情绪走向，用于辅助分镜师做决定",
            "parameters": {
                "type": "object",
                "properties": {
                    "scene_id": {"type": "string", "description": "场景ID，如 scene_001"},
                },
                "required": ["scene_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_shot_composition",
            "description": "根据角色数量、对白密度、情绪强度，建议最合适的景别和机位",
            "parameters": {
                "type": "object",
                "properties": {
                    "character_count": {"type": "integer", "description": "出场角色数"},
                    "has_dialogue": {"type": "boolean", "description": "是否有对白"},
                    "emotion_intensity": {"type": "string", "description": "情绪强度: low/medium/high", "enum": ["low", "medium", "high"]},
                },
                "required": ["character_count", "has_dialogue", "emotion_intensity"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_shot_duration",
            "description": "根据台词字数、动作复杂度估算分镜时长",
            "parameters": {
                "type": "object",
                "properties": {
                    "dialogue_chars": {"type": "integer", "description": "台词字数"},
                    "action_count": {"type": "integer", "description": "动作数量"},
                },
                "required": ["dialogue_chars", "action_count"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_image_prompt",
            "description": "为指定分镜生成高质量的AI绘画Prompt",
            "parameters": {
                "type": "object",
                "properties": {
                    "shot_description": {"type": "string", "description": "分镜画面描述"},
                    "style": {"type": "string", "description": "画风: realistic/anime/ink", "enum": ["realistic", "anime", "ink"]},
                },
                "required": ["shot_description"],
            },
        },
    },
]


# ============================================================
# 工具执行器
# ============================================================
class ToolExecutor:
    """执行 Function Calling 返回的工具调用"""

    def __init__(self, script_text: str = "", parsed_data: dict = None):
        self.script = script_text
        self.parsed = parsed_data or {}
        self.execution_log: list[dict] = []  # 执行记录

    def execute(self, tool_name: str, arguments: dict) -> dict:
        """分发执行具体工具"""
        method = getattr(self, f"_tool_{tool_name}", None)
        if not method:
            return {"error": f"未知工具: {tool_name}"}

        result = method(**arguments)
        self.execution_log.append({
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
        })
        return result

    def _tool_search_character_info(self, character_name: str) -> dict:
        """搜索角色信息"""
        characters = self.parsed.get("characters", [])
        matched = [c for c in characters if c.get("name") == character_name]
        if not matched:
            return {"found": False, "name": character_name, "info": {}}

        char = matched[0]
        # 在剧本中统计出场次数
        lines = [l for l in self.script.split("\n") if character_name in l]
        return {
            "found": True,
            "name": character_name,
            "id": char.get("id", ""),
            "type": char.get("type", ""),
            "personality": char.get("personality", []),
            "appearance": char.get("appearance", []),
            "appearances_in_script": len(lines),
            "first_line": char.get("first_line", ""),
            "relationships": char.get("relationships", []),
        }

    def _tool_analyze_scene_atmosphere(self, scene_id: str) -> dict:
        """分析场景氛围"""
        scenes = self.parsed.get("scenes", [])
        matched = [s for s in scenes if s.get("id") == scene_id]
        if not matched:
            return {"found": False}

        scene = matched[0]
        return {
            "found": True,
            "name": scene.get("name"),
            "atmosphere": scene.get("atmosphere"),
            "lighting": scene.get("lighting"),
            "color_tone": scene.get("color_tone"),
            "characters_count": len(scene.get("characters_present", [])),
            "props_count": len(scene.get("key_props", [])),
        }

    def _tool_suggest_shot_composition(self, character_count: int,
                                        has_dialogue: bool,
                                        emotion_intensity: str) -> dict:
        """建议分镜构图 —— 基于影视专业规则"""
        # 1人 → 近景/特写, 多人 → 全景/中景
        if character_count == 1:
            if emotion_intensity == "high":
                suggestion = {"shot_type": "大特写", "angle": "正面", "reason": "单人情绪高点，用大特写强调微表情"}
            else:
                suggestion = {"shot_type": "近景", "angle": "平视", "reason": "单人中低情绪，近景展现状态"}
        elif character_count == 2:
            if has_dialogue:
                suggestion = {"shot_type": "中景", "angle": "过肩", "reason": "双人对白，正反打过肩拍"}
            else:
                suggestion = {"shot_type": "中景", "angle": "平视", "reason": "双人无声，中景展现关系"}
        else:
            suggestion = {"shot_type": "全景", "angle": "平视", "reason": "多人场景用全景建立空间关系"}

        suggestion["estimated_duration"] = 4 if has_dialogue else 3
        return suggestion

    def _tool_estimate_shot_duration(self, dialogue_chars: int, action_count: int) -> dict:
        """估算分镜时长"""
        # 平均语速约 4 字/秒
        speaking_time = dialogue_chars / 4
        # 每个动作约 1 秒
        action_time = action_count * 1
        total = max(2, round(speaking_time + action_time))
        return {
            "speaking_time_s": round(speaking_time, 1),
            "action_time_s": action_time,
            "total_duration_s": total,
        }

    def _tool_generate_image_prompt(self, shot_description: str, style: str = "realistic") -> dict:
        """生成图片Prompt —— 基于分镜描述"""
        style_tags = {
            "realistic": "cinematic, photorealistic, 8k, professional lighting, film grain",
            "anime": "anime style, studio ghibli, vibrant colors, clean lines",
            "ink": "traditional chinese ink painting, wash painting, elegant brushwork",
        }
        return {
            "prompt_en": f"{shot_description} | {style_tags.get(style, style_tags['realistic'])}",
            "prompt_cn": f"影视级{shot_description}，电影质感，{style}风格",
            "negative_prompt": "blur, deformed, extra fingers, text artifacts, ugly, low quality",
            "suggested_size": "16:9" if len(shot_description) > 50 else "1:1",
        }
