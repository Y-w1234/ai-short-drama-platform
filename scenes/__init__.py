"""
场景类型注册表 —— AI 原生视频生产管线的场景层

每种场景定义了:
- 专门的 System Prompt 变体
- 默认参数（时长、画幅、风格）
- 内置 Demo 数据
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class SceneType(str, Enum):
    SHORT_DRAMA = "short_drama"           # 短剧
    PRODUCT_SHOWCASE = "product_showcase"  # 电商商品展示
    KNOWLEDGE_SHORT = "knowledge_short"    # 知识口播
    CROSS_BORDER = "cross_border"          # 跨境多语言


@dataclass
class SceneDefinition:
    """场景定义 —— 一套完整的场景配置"""
    scene_type: SceneType
    name: str                          # 中文名
    description: str                   # 一句话描述
    icon: str                          # emoji 图标
    default_aspect_ratio: str          # 默认画幅
    target_duration_range: str         # 目标时长范围
    style_tags: list[str] = field(default_factory=list)  # 风格标签
    input_description: str = ""        # 输入内容说明
    output_description: str = ""       # 输出内容说明
    demo_script: str = ""              # 内置 Demo 剧本/文案
    demo_title: str = ""               # Demo 标题
    storyboard_prompt_extra: str = ""  # 分镜 Prompt 场景专属补充


# ═══════════════════════════════════════
# 场景定义
# ═══════════════════════════════════════

SHORT_DRAMA = SceneDefinition(
    scene_type=SceneType.SHORT_DRAMA,
    name="短剧",
    description="输入剧本 → 角色/场景/道具提取 → 专业分镜表 → AI 绘画/视频 Prompt",
    icon="🎬",
    default_aspect_ratio="16:9",
    target_duration_range="60-180秒",
    style_tags=["cinematic", "photorealistic", "professional lighting"],
    input_description="短剧剧本（中文，含场景标记和对话）",
    output_description="完整分镜表（11维）+ 中英双语图片Prompt + 视频Prompt + 质量审核报告",
    demo_title="求婚",
    demo_script="""【第一场】咖啡厅 - 下午

[小红坐在角落，不停看手机]
小明（走过来）：你等了很久吗？
小红（抬头，眼眶微红）：三个小时。我以为你不会来了。
小明（坐下，推过去一杯咖啡）：路上堵车...还有，我去买了这个。
[他从口袋里掏出一个小盒子，放在桌上]
小红（愣住）：这是...？
小明（微笑）：打开看看。
[小红颤抖着打开盒子，里面是一枚戒指]
小红（眼泪掉下来）：你...
小明（单膝跪地）：嫁给我，好吗？
[整个咖啡厅的人都看过来，鼓掌]
小红（擦泪，笑出来）：好。""",
    storyboard_prompt_extra="短剧强调角色情感弧线，每个情绪转折点至少1个分镜。对白密集处用正反打。",
)

PRODUCT_SHOWCASE = SceneDefinition(
    scene_type=SceneType.PRODUCT_SHOWCASE,
    name="电商商品展示",
    description="输入商品信息 → 自动拆解卖点 → 场景化分镜 → 带货短视频 Prompt",
    icon="🛒",
    default_aspect_ratio="9:16",
    target_duration_range="15-45秒",
    style_tags=["product photography", "clean lighting", "commercial", "lifestyle"],
    input_description="商品名称 + 核心卖点（3-5个）+ 目标人群 + 风格偏好",
    output_description="场景化分镜表 + 图片Prompt（含商品特写/使用场景/对比展示）+ 口播文案",
    demo_title="ProPods X1 真无线耳机",
    demo_script="""【商品】ProPods X1 真无线降噪耳机
【卖点】42dB主动降噪 | 36小时续航 | 蓝牙5.4超低延迟 | IPX5防水 | ¥299
【目标人群】18-30岁，通勤族/学生/健身爱好者
【风格】科技感 + 生活方式

请生成一个15秒的短视频分镜：开场抓注意力 → 痛点展示 → 产品特写 → 使用场景 → CTA""",
    storyboard_prompt_extra="商品视频强调视觉冲击力和产品质感。前3秒必须有强钩子。每个卖点对应一个使用场景镜头。最后必须有明确的CTA（立即下单/点击链接）。",
)

KNOWLEDGE_SHORT = SceneDefinition(
    scene_type=SceneType.KNOWLEDGE_SHORT,
    name="知识口播",
    description="输入文章/观点 → 自动提炼核心信息 → 信息可视化分镜 → 科普短视频 Prompt",
    icon="📚",
    default_aspect_ratio="9:16",
    target_duration_range="45-90秒",
    style_tags=["clean", "modern", "educational", "motion graphics friendly"],
    input_description="科普文章/知识文案（500-2000字）",
    output_description="信息层次化分镜表 + 关键概念可视化Prompt + 口播/字幕同步方案",
    demo_title="AI 为什么能理解人类语言？",
    demo_script="""【主题】AI 为什么能理解人类语言？——大语言模型的原理科普
【目标观众】非技术背景，对 AI 好奇的普通人
【时长】60秒
【风格】轻松易懂，类比法解释

核心信息点：
1. 大模型本质上是一个"超级完形填空"——根据前文预测下一个词
2. 训练过程 = 读了整个互联网的书
3. 但模型并不"理解"语言，它只是学会了词语之间的统计规律
4. 这就是为什么它会"一本正经地胡说八道"（幻觉）
5. 未来方向：从"预测下一个词"到"真正理解意义" """,
    storyboard_prompt_extra="知识类视频强调信息层次和可视化。复杂概念必须用动画/图表辅助理解。节奏：每8-10秒一个信息点。善用类比和隐喻的视觉化表达。",
)

CROSS_BORDER = SceneDefinition(
    scene_type=SceneType.CROSS_BORDER,
    name="跨境多语言",
    description="输入商品信息 + 目标市场 → 多语言分镜 → 本地化视频 Prompt",
    icon="🌍",
    default_aspect_ratio="1:1",
    target_duration_range="15-30秒",
    style_tags=["lifestyle", "clean", "international", "brand safe"],
    input_description="商品信息 + 目标市场（国家/语言）+ 投放平台（TikTok/Instagram/YouTube Shorts）",
    output_description="多语言分镜表 + 本地化Prompt（含文化适配建议）+ 多语言配音文案",
    demo_title="蓝牙耳机 × 美国市场",
    demo_script="""【Product】ProPods X1 True Wireless Earbuds
【Key Features】42dB ANC | 36hr Battery | BT 5.4 | IPX5 | $39.99
【Target Market】US, 18-35, TikTok/Instagram Reels
【Style】Trendy, lifestyle, Gen-Z aesthetic
【Language】English (primary) + Spanish subtitles option

Generate a 15-second product showcase video storyboard.""",
    storyboard_prompt_extra="跨境视频需考虑目标市场文化差异。避免使用可能在当地有负面含义的视觉元素。考虑不同平台的视频规格（TikTok 9:16, Instagram 1:1 或 4:5）。Prompt 以英文为主，保留关键卖点术语。",
)

# ═══════════════════════════════════════
# 注册表
# ═══════════════════════════════════════

SCENES: dict[SceneType, SceneDefinition] = {
    SceneType.SHORT_DRAMA: SHORT_DRAMA,
    SceneType.PRODUCT_SHOWCASE: PRODUCT_SHOWCASE,
    SceneType.KNOWLEDGE_SHORT: KNOWLEDGE_SHORT,
    SceneType.CROSS_BORDER: CROSS_BORDER,
}

SCENE_CHOICES = [s.value for s in SceneType]


def get_scene(scene_type: str) -> SceneDefinition:
    """根据字符串获取场景定义"""
    st = SceneType(scene_type)
    return SCENES.get(st, SHORT_DRAMA)


def list_scenes() -> list[dict]:
    """列出所有可用场景"""
    return [
        {
            "id": s.scene_type.value,
            "name": s.name,
            "icon": s.icon,
            "description": s.description,
            "aspect_ratio": s.default_aspect_ratio,
            "duration": s.target_duration_range,
            "input": s.input_description,
        }
        for s in SCENES.values()
    ]
