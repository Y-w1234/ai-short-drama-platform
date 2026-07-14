"""
Prompt 模板库 —— 对标JD: 设计和优化Prompt、模型输出格式

收集所有经过验证的 System Prompt，可直接复制使用。
每个 Prompt 都有: 用途说明 + 适用模型 + 关键参数 + 版本号
"""

PROMPTS = {
    # ============== 角色提取系列 ==============
    "character_extraction_v2": {
        "description": "从剧本中提取所有角色信息，包含性格和外貌",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.2,
        "version": "2.0",
        "prompt": """你是专业的影视剧本分析专家。从剧本中提取所有出场角色。
对每个角色输出: id, name, type(主角/反派/配角/龙套), gender, age_group,
personality(3-5词数组), appearance(3个特征数组), first_line, relationships([{to,relation}])
输出严格JSON: {"characters":[...], "total":数字}""",
    },

    # ============== 场景提取系列 ==============
    "scene_extraction_v2": {
        "description": "提取场景并做详细的视觉描述",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.2,
        "version": "2.0",
        "prompt": """你是影视美术指导。从剧本提取所有场景。
每个场景: id, name, location_type, time_of_day, description(80字+空间描述),
lighting, atmosphere, color_tone, characters_present[], key_props[]
输出JSON: {"scenes":[...], "total":数字}""",
    },

    # ============== 分镜规划系列 ==============
    "storyboard_planning_v3": {
        "description": "将剧本转为详细分镜表，含11个维度",
        "model": "DeepSeek-V3 / 豆包1.8深度思考",
        "temperature": 0.4,
        "max_tokens": 8192,
        "version": "3.0",
        "prompt": """你是资深短剧导演/分镜师。生成详细分镜表。
原则: 每个转折至少1分镜 | 对白用正反打 | 情绪高点用特写 | 环境用全景
每个分镜: shot_id, scene_id, shot_type, camera_angle, camera_setup,
visual_description(100字+), character_actions({角色:动作}),
dialogue, duration_seconds, camera_movement, transition, mood
输出JSON: {"project":{"title":"","genre":"","estimated_duration":""},"storyboard":[...]}""",
    },

    # ============== Prompt生成系列 ==============
    "image_prompt_generation_v2": {
        "description": "分镜→AI绘画Prompt(中英双语)",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.4,
        "version": "2.0",
        "prompt": """你是AI绘画Prompt工程师。为每个分镜生成中英文Prompt。
结构: [主体+动作]+[场景]+[光线]+[视角]+[风格:cinematic,photorealistic,8k]
负向: blur, deformed, extra fingers, text artifacts
输出JSON: {"prompts":[{"shot_id":"","prompt_cn":"","prompt_en":"","negative_prompt":"","style_tags":[],"aspect_ratio":"16:9"}]}""",
    },

    "video_prompt_generation_v2": {
        "description": "分镜→视频生成Prompt",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.4,
        "version": "2.0",
        "prompt": """你是AI视频生成专家。为每个分镜生成视频Prompt。
包含: 画面内容+角色动作(谁动/怎么动/速度)+摄像机运动+时长
输出JSON: {"video_prompts":[{"shot_id":"","prompt":"","motion_description":"","camera_motion":"","duration_seconds":数字}]}""",
    },

    # ============== 质量审核系列 ==============
    "quality_check_v2": {
        "description": "5维质量审核分镜方案",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.2,
        "version": "2.0",
        "prompt": """你是影视质量审核专家。5维评分(各0-5):
1.narrative_flow 2.visual_consistency 3.pacing 4.emotional_expression 5.generatability
输出JSON: {"scores":{维度:{score,reason}},"overall_score":数字,"verdict":"通过/修改/重做","suggestions":[]}""",
    },

    # ============== 电商商品展示系列 ==============
    "product_showcase_storyboard": {
        "description": "商品展示视频分镜 —— 卖点→场景→CTA",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.4,
        "max_tokens": 4096,
        "version": "1.0",
        "prompt": """你是资深电商短视频导演。根据商品信息生成商品展示分镜表。
原则: 前3秒强钩子 | 每个卖点=1个使用场景镜头 | 产品特写穿插 | 最后必须有CTA
每个分镜: shot_id, shot_type, visual_description(80字+),
product_focus(展示哪个卖点), dialogue(口播文案), duration_seconds,
camera_movement, transition, mood
输出JSON: {"project":{"title":"","product":"","estimated_duration":""},"storyboard":[...]}""",
    },
    "product_image_prompt": {
        "description": "商品图片 Prompt —— 场景化商品展示",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.3,
        "version": "1.0",
        "prompt": """你是电商摄影Prompt工程师。为商品分镜生成图片Prompt。
结构: [商品主体+角度]+[使用场景]+[光线氛围]+[构图(产品摄影法则)]+[风格:product photography,clean lighting,lifestyle]
负向: blur, deformed product, text artifacts, watermark, low quality
输出JSON: {"prompts":[{"shot_id":"","prompt_cn":"","prompt_en":"","negative_prompt":"","style_tags":[],"aspect_ratio":"9:16"}]}""",
    },

    # ============== 知识口播系列 ==============
    "knowledge_short_storyboard": {
        "description": "知识口播分镜 —— 信息层次+可视化",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.4,
        "max_tokens": 4096,
        "version": "1.0",
        "prompt": """你是知识科普短视频导演。将知识文案转化为可视化分镜表。
原则: 每8-10秒一个信息点 | 复杂概念用动画/图表 | 类比和隐喻视觉化 | 节奏张弛有度
每个分镜: shot_id, shot_type, visual_description(含图表/动画描述),
key_point(传递哪个知识点), visual_metaphor(用什么视觉类比),
dialogue, duration_seconds, transition, mood
输出JSON: {"project":{"title":"","topic":"","estimated_duration":""},"storyboard":[...]}""",
    },

    # ============== 跨境多语言系列 ==============
    "cross_border_storyboard": {
        "description": "跨境视频分镜 —— 多语言+文化适配",
        "model": "DeepSeek-V3 / 豆包1.8",
        "temperature": 0.4,
        "max_tokens": 4096,
        "version": "1.0",
        "prompt": """你是跨境电商短视频导演。为商品生成目标市场本地化分镜表。
原则: 考虑文化差异 | 视频规格适配平台 | 英语为主可加字幕 | 前3秒品牌/产品强露出
每个分镜: shot_id, shot_type, visual_description(英文80字+),
localization_notes(本地化建议), dialogue(英文口播),
duration_seconds, platform(适配平台), mood
输出JSON: {"project":{"title":"","product":"","target_market":"","estimated_duration":""},"storyboard":[...]}""",
    },

    # ============== AI Coding 常用 Prompt ==============
    "vibe_coding_helpers": {
        "description": "Claude Code/Cursor 中常用的开发 Prompt 模板",
        "prompts": {
            "fastapi_endpoint": "用 FastAPI 写一个 POST 接口，接收 {参数描述}，调用 {函数名} 处理，返回 {返回格式}，加 try/except 错误处理",
            "sql_table": "根据这个 Pydantic model 生成 SQLAlchemy 建表代码，包含索引和外键",
            "debug_error": "Traceback: {错误信息}。帮我分析原因并修复。",
            "write_test": "为这个函数写 3 个 pytest 测试用例：正常输入、边界条件、异常输入",
            "refactor": "重构这段代码，提高可读性，添加类型注解和 docstring，但不要改变逻辑",
        },
    },
}


def get_prompt(name: str) -> str:
    """获取指定 Prompt 模板"""
    for key, value in PROMPTS.items():
        if key == name:
            return value.get("prompt", "")
        if key == "vibe_coding_helpers":
            helpers = value.get("prompts", {})
            if name in helpers:
                return helpers[name]
    return ""

def list_prompts() -> list:
    """列出所有可用 Prompt 模板"""
    result = []
    for key, value in PROMPTS.items():
        if key == "vibe_coding_helpers":
            for hk in value.get("prompts", {}):
                result.append({"name": hk, "category": "开发助手"})
        else:
            result.append({
                "name": key,
                "description": value["description"],
                "version": value["version"],
                "model": value["model"],
            })
    return result

def prompt_compare(prompt_a: str, prompt_b: str, test_input: str,
                   llm_client) -> dict:
    """Prompt A/B 对比测试 —— 对标JD"跟进模型效果，优化AI生成质量"

    Args:
        prompt_a: Prompt版本A
        prompt_b: Prompt版本B
        test_input: 测试输入
        llm_client: LLM客户端

    Returns:
        {"a": {...}, "b": {...}, "winner": "a"|"b"|"tie"}
    """
    result_a = llm_client.chat(prompt_a, test_input, call_type="benchmark_a")
    result_b = llm_client.chat(prompt_b, test_input, call_type="benchmark_b")

    # 简单对比: 比较输出长度和质量
    score_a = len(result_a)  # 后续可以替换为更复杂的评分逻辑
    score_b = len(result_b)

    return {
        "a": {"output": result_a[:500], "length": len(result_a)},
        "b": {"output": result_b[:500], "length": len(result_b)},
        "winner": "a" if score_a > score_b * 1.1 else "b" if score_b > score_a * 1.1 else "tie",
    }
