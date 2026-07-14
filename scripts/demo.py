"""
多场景快速演示脚本 —— 不依赖 API Key 也能展示全部 4 种视频场景
对标JD: 通过AI编程工具独立完成Agent Demo

用法:
    python -m scripts.demo                      # 默认：短剧
    python -m scripts.demo --scene product_showcase
    python -m scripts.demo --scene knowledge_short
    python -m scripts.demo --scene cross_border
    python -m scripts.demo --scene list         # 列出所有场景
"""
import json
import time
import sys
from pathlib import Path

# Windows 终端 emoji 兼容
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _preprocess(script: str) -> dict:
    lines = [l for l in script.split("\n") if l.strip()]
    chars = len(script.replace(" ", "").replace("\n", ""))
    return {"lines": len(lines), "chars": chars, "estimated_minutes": round(chars / 200, 1)}


def demo_short_drama():
    """场景1: 短剧 —— 求婚"""
    script = """【第一场】咖啡厅 - 下午

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
小红（擦泪，笑出来）：好。"""

    chars_data = _preprocess(script)
    print(f"\n  [Phase 1] 预处理: {chars_data['chars']}字符, {chars_data['lines']}行, 约{chars_data['estimated_minutes']}分钟")

    time.sleep(0.3)
    characters = {
        "characters": [
            {"id": "char_001", "name": "小红", "type": "主角", "gender": "女",
             "age_group": "青年", "personality": ["敏感", "执着", "浪漫"],
             "appearance": ["长发披肩", "素色连衣裙", "眼眶微红"],
             "first_line": "三个小时。我以为你不会来了。",
             "relationships": [{"to": "小明", "relation": "情侣"}]},
            {"id": "char_002", "name": "小明", "type": "主角", "gender": "男",
             "age_group": "青年", "personality": ["温柔", "细心", "浪漫"],
             "appearance": ["干净短发", "白衬衫", "手里拿咖啡"],
             "first_line": "你等了很久吗？",
             "relationships": [{"to": "小红", "relation": "情侣"}]},
        ], "total": 2,
    }
    print(f"  [Phase 2] 角色提取: {characters['total']}个角色 (小红/小明)")

    time.sleep(0.3)
    scenes = {
        "scenes": [
            {"id": "scene_001", "name": "街角咖啡厅", "location_type": "室内",
             "time_of_day": "下午", "description": "安静街角咖啡厅，暖黄灯光，靠窗双人座，角落书架和绿植，吧台咖啡机低鸣",
             "lighting": "柔和暖黄顶灯+窗外自然光", "atmosphere": "感动→惊喜→浪漫",
             "color_tone": "暖色调（黄+棕+米白）",
             "characters_present": ["小红", "小明"],
             "key_props": ["咖啡杯", "戒指盒", "手机"]},
        ], "total": 1,
    }
    print(f"  [Phase 3] 场景提取: {scenes['total']}个场景 (街角咖啡厅)")

    time.sleep(0.3)
    props = {
        "props": [
            {"id": "prop_001", "name": "戒指盒", "category": "手持", "priority": "A",
             "scenes": ["街角咖啡厅"], "used_by": ["小明"],
             "description": "深蓝色天鹅绒小方盒，金色边框，精致"},
            {"id": "prop_002", "name": "咖啡杯", "category": "手持", "priority": "B",
             "scenes": ["街角咖啡厅"], "used_by": ["小明", "小红"],
             "description": "白色陶瓷咖啡杯，杯壁有拉花痕迹"},
            {"id": "prop_003", "name": "手机", "category": "电子产品", "priority": "B",
             "scenes": ["街角咖啡厅"], "used_by": ["小红"],
             "description": "白色智能手机，屏幕亮着消息界面"},
        ], "total": 3,
    }
    print(f"  [Phase 4] 道具提取: {props['total']}个道具 (戒指盒★/咖啡杯/手机)")

    time.sleep(0.4)
    storyboard = {
        "project": {"title": "求婚", "genre": "都市情感", "estimated_duration": "100秒"},
        "storyboard": [
            {"shot_id": "shot_001", "scene_id": "scene_001", "shot_type": "全景",
             "camera_angle": "平视", "camera_setup": "咖啡厅门口视角",
             "visual_description": "咖啡厅全景，小红独自坐在角落靠窗的双人座，不停看手机。下午阳光透过落地窗投下暖黄色光斑。",
             "character_actions": {"小红": "坐在角落，反复看手机，表情焦虑"},
             "dialogue": "", "duration_seconds": 5, "camera_movement": "推", "transition": "硬切", "mood": "焦虑"},
            {"shot_id": "shot_002", "scene_id": "scene_001", "shot_type": "中景",
             "camera_angle": "平视", "camera_setup": "侧面",
             "visual_description": "小明端着两杯咖啡走入画面。小红抬起头，眼眶微红。小明在她对面坐下。",
             "character_actions": {"小明": "端咖啡走入", "小红": "抬头，眼眶微红"},
             "dialogue": "小明：你等了很久吗？", "duration_seconds": 4, "camera_movement": "固定", "transition": "硬切", "mood": "期待"},
            {"shot_id": "shot_003", "scene_id": "scene_001", "shot_type": "近景",
             "camera_angle": "平视", "camera_setup": "正面拍小红",
             "visual_description": "小红眼中泪光闪烁，睫毛上挂着将落未落的泪珠。声音有些颤抖。",
             "character_actions": {"小红": "眼眶更红，声音颤抖"},
             "dialogue": "小红：三个小时。我以为你不会来了。", "duration_seconds": 3, "camera_movement": "微推", "transition": "硬切", "mood": "委屈"},
            {"shot_id": "shot_004", "scene_id": "scene_001", "shot_type": "特写",
             "camera_angle": "俯视", "camera_setup": "俯拍桌面",
             "visual_description": "小明把咖啡推到小红面前，同时从口袋掏出深蓝色天鹅绒小方盒放在桌上。暖光下泛着微光。",
             "character_actions": {"小明": "推咖啡+掏戒指盒"},
             "dialogue": "小明：路上堵车...还有，我去买了这个。", "duration_seconds": 5, "camera_movement": "固定", "transition": "硬切", "mood": "转折"},
            {"shot_id": "shot_005", "scene_id": "scene_001", "shot_type": "大特写",
             "camera_angle": "平视", "camera_setup": "拍小红的脸",
             "visual_description": "小红看到戒指盒，整个人愣住。瞳孔微张，嘴唇微微张开。",
             "character_actions": {"小红": "愣住，瞳孔微张"},
             "dialogue": "小红：这是...？", "duration_seconds": 2, "camera_movement": "固定", "transition": "硬切", "mood": "震惊"},
            {"shot_id": "shot_006", "scene_id": "scene_001", "shot_type": "全景",
             "camera_angle": "平视", "camera_setup": "侧后方",
             "visual_description": "小明从沙发座起身，单膝跪地。小红捂住了嘴，眼泪终于滑落。周围客人纷纷转头。",
             "character_actions": {"小明": "单膝跪地", "小红": "捂嘴，眼泪滑落"},
             "dialogue": "小明：嫁给我，好吗？", "duration_seconds": 5, "camera_movement": "拉", "transition": "硬切", "mood": "浪漫"},
            {"shot_id": "shot_007", "scene_id": "scene_001", "shot_type": "全景",
             "camera_angle": "平视", "camera_setup": "正面拍两人",
             "visual_description": "小红擦掉眼泪，绽放灿烂笑容。整个咖啡厅客人起立鼓掌。阳光透过窗户洒在两人身上。",
             "character_actions": {"小红": "擦泪，灿烂笑", "小明": "期待抬头"},
             "dialogue": "小红：好。", "duration_seconds": 4, "camera_movement": "固定+微推", "transition": "淡出", "mood": "感动"},
        ],
    }
    print(f"  [Phase 5] 分镜规划: {len(storyboard['storyboard'])}个分镜, 预估{storyboard['project']['estimated_duration']}")

    time.sleep(0.3)
    image_prompts = {
        "prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt_cn": f"电影级画质，咖啡厅室内，{['全景浪漫求婚场景','年轻女性抬头含泪','近景女性眼中泪光','钻戒盒特写','大特写震惊表情','全景男子单膝跪地求婚','全景两人相拥阳光洒落'][i]}，8K超清，暖色调",
             "prompt_en": f"cinematic photorealistic 8k, {['wide shot cafe interior','medium shot woman looking up','closeup tearful eyes','extreme closeup ring box','extreme closeup shocked face','wide shot man proposing','wide shot couple embracing sunlight'][i]}, warm tones",
             "negative_prompt": "blur, deformed, extra fingers, text artifacts, anime",
             "style_tags": ["cinematic", "photorealistic", "professional lighting"],
             "aspect_ratio": "16:9"}
            for i in range(len(storyboard["storyboard"]))
        ],
    }
    video_prompts = {
        "video_prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt": f"Cinematic video, {['cafe interior','emotional conversation','tearful closeup','ring box reveal','shocked reaction','romantic proposal','happy ending'][i]}, smooth camera, 24fps",
             "motion_description": ["缓慢推近","小明走入自然","眼泪滚落","手部动作缓慢","表情细微变化","下跪动作流畅","自然微笑"][i],
             "camera_motion": ["推","固定","微推","固定","固定","拉","固定+微推"][i],
             "duration_seconds": [5,4,3,5,2,5,4][i]}
            for i in range(len(storyboard["storyboard"]))
        ],
    }
    print(f"  [Phase 6] Prompt生成: {len(image_prompts['prompts'])}图片, {len(video_prompts['video_prompts'])}视频")

    quality = {
        "scores": {
            "narrative_flow": {"score": 5, "reason": "7个分镜叙事流畅，起承转合完整"},
            "visual_consistency": {"score": 5, "reason": "角色外貌和场景在所有分镜中一致"},
            "pacing": {"score": 5, "reason": "从焦虑→期待→震惊→浪漫，节奏张弛有度"},
            "emotional_expression": {"score": 5, "reason": "景别精准服务情感变化"},
            "generatability": {"score": 5, "reason": "画面描述细节丰富，可直接用于AI生成"},
        },
        "overall_score": 5.0, "verdict": "通过",
        "suggestions": ["shot_003可增加0.5秒黑场强化情绪转折"],
    }

    return {
        "scene_type": "short_drama",
        "project": storyboard["project"],
        "characters": characters, "scenes": scenes, "props": props,
        "storyboard": storyboard["storyboard"],
        "image_prompts": image_prompts, "video_prompts": video_prompts,
        "quality_report": quality, "total_shots": len(storyboard["storyboard"]),
    }


def demo_product_showcase():
    """场景2: 电商商品展示 —— ProPods X1 蓝牙耳机"""
    script = "ProPods X1 真无线降噪耳机 | 42dB ANC | 36h续航 | BT5.4 | IPX5防水 | ¥299"

    chars_data = _preprocess(script)
    print(f"\n  [Phase 1] 商品信息解析: {chars_data['chars']}字符, 5个核心卖点")

    time.sleep(0.3)
    # 商品展示没有"角色"，而是"卖点拆解"
    product_info = {
        "product_name": "ProPods X1 真无线降噪耳机",
        "price": 299, "currency": "CNY",
        "selling_points": [
            {"id": "sp_001", "name": "42dB主动降噪", "category": "核心功能", "priority": "A",
             "scene": "地铁/通勤", "visual": "嘈杂车厢→开启降噪→瞬间安静"},
            {"id": "sp_002", "name": "36小时超长续航", "category": "核心功能", "priority": "A",
             "scene": "长途旅行/图书馆", "visual": "电量从早到晚不焦虑"},
            {"id": "sp_003", "name": "蓝牙5.4超低延迟", "category": "性能", "priority": "B",
             "scene": "打游戏/看视频", "visual": "音画同步，枪声和画面零延迟"},
            {"id": "sp_004", "name": "IPX5防水", "category": "品质", "priority": "B",
             "scene": "健身房/雨天", "visual": "汗水雨水都不怕"},
            {"id": "sp_005", "name": "仅售¥299", "category": "价格", "priority": "A",
             "scene": "对比竞品", "visual": "同等配置半价"},
        ],
    }
    print(f"  [Phase 2] 卖点拆解: {len(product_info['selling_points'])}个卖点 (降噪★/续航★/低延迟/防水/性价比★)")

    time.sleep(0.3)
    use_scenes = {
        "scenes": [
            {"id": "scene_001", "name": "地铁车厢", "type": "室内公共交通",
             "description": "高峰期地铁车厢，人挤人，环境嘈杂。主角戴耳机闭眼享受音乐，周围噪音与他无关。",
             "mood": "嘈杂→宁静", "selling_point": "42dB降噪"},
            {"id": "scene_002", "name": "现代化健身房", "type": "室内运动",
             "description": "明亮健身房，主角正在跑步机上挥汗如雨。耳机稳稳戴着，防水性能尽显。",
             "mood": "活力", "selling_point": "IPX5防水"},
            {"id": "scene_003", "name": "电竞桌面", "type": "室内",
             "description": "RGB灯效电竞桌面，主角戴着耳机打FPS游戏。画面与枪声完美同步。",
             "mood": "酷炫", "selling_point": "蓝牙5.4低延迟"},
            {"id": "scene_004", "name": "纯色产品展示台", "type": "影棚",
             "description": "白色背景产品摄影，耳机360°旋转展示，每圈展示一个颜色。价格大字叠加。",
             "mood": "专业", "selling_point": "¥299性价比"},
        ], "total": 4,
    }
    print(f"  [Phase 3] 使用场景: {use_scenes['total']}个场景 (地铁/健身房/电竞桌/产品台)")

    time.sleep(0.4)
    storyboard = {
        "project": {"title": "通勤党的降噪神器", "product": "ProPods X1", "estimated_duration": "15秒"},
        "storyboard": [
            {"shot_id": "shot_001", "scene_id": "scene_001", "shot_type": "中景",
             "camera_angle": "平视",
             "visual_description": "地铁车厢人挤人，画面带轻微抖动。屏幕中央大字弹出：'受够了通勤噪音？'周围人声嘈杂。主角戴上耳机。",
             "product_focus": "钩子/痛点",
             "dialogue": "受够了通勤噪音？", "duration_seconds": 3,
             "camera_movement": "手持微晃→稳定", "transition": "硬切", "mood": "共鸣"},
            {"shot_id": "shot_002", "scene_id": "scene_001", "shot_type": "特写",
             "camera_angle": "微距俯视",
             "visual_description": "手指轻触耳机，LED灯亮起蓝色。世界瞬间安静。主角表情从烦躁变为放松。屏幕弹出：'42dB主动降噪'。",
             "product_focus": "42dB降噪",
             "dialogue": "42dB主动降噪，世界立刻安静。", "duration_seconds": 3,
             "camera_movement": "推→特写", "transition": "硬切", "mood": "惊喜"},
            {"shot_id": "shot_003", "scene_id": "scene_002", "shot_type": "中景",
             "camera_angle": "平视",
             "visual_description": "健身房，主角跑步大汗淋漓，耳机稳稳在耳。水珠从耳机表面滑落。弹出：'IPX5防水，汗水雨水都不怕'。",
             "product_focus": "IPX5防水",
             "dialogue": "IPX5防水，随便造。", "duration_seconds": 2.5,
             "camera_movement": "跟", "transition": "硬切", "mood": "活力"},
            {"shot_id": "shot_004", "scene_id": "scene_003", "shot_type": "特写",
             "camera_angle": "正面",
             "visual_description": "屏幕分屏：左边游戏画面火光四射，右边耳机特写。字幕弹出：'蓝牙5.4，40ms超低延迟，音画同步'。",
             "product_focus": "低延迟",
             "dialogue": "蓝牙5.4，40毫秒超低延迟，听声辨位。", "duration_seconds": 2.5,
             "camera_movement": "固定", "transition": "硬切", "mood": "酷炫"},
            {"shot_id": "shot_005", "scene_id": "scene_004", "shot_type": "全景→特写",
             "camera_angle": "平视→微距",
             "visual_description": "白色背景，耳机360°旋转。价格大字砸入：'¥299'。下方小字：'同等配置，一半价格'。屏幕底部弹出购买链接。",
             "product_focus": "性价比+CTA",
             "dialogue": "只要299，点击下方链接立即购买！", "duration_seconds": 4,
             "camera_movement": "推→特写", "transition": "硬切", "mood": "紧迫"},
        ],
    }
    print(f"  [Phase 5] 分镜规划: {len(storyboard['storyboard'])}个分镜, 预估{storyboard['project']['estimated_duration']}")

    time.sleep(0.3)
    image_prompts = {
        "prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt_cn": f"电商产品摄影，{['地铁车厢拥挤场景','手指触摸耳机LED亮蓝光特写','健身房跑步大汗淋漓','游戏画面和耳机分屏对比','无线耳机产品白底360度展示价格299'][i]}，干净布光，生活方式风格",
             "prompt_en": f"product photography, {['crowded subway car commuter','closeup finger touching earbud LED blue light','gym treadmill sweat','split screen gaming vs earbuds','wireless earbuds 360 rotation white background price 299'][i]}, clean lighting, lifestyle commercial",
             "negative_prompt": "blur, deformed product, watermark, text in image, low quality",
             "style_tags": ["product photography", "clean lighting", "lifestyle", "commercial"],
             "aspect_ratio": "9:16"}
            for i in range(len(storyboard["storyboard"]))
        ],
    }
    print(f"  [Phase 6] Prompt生成: {len(image_prompts['prompts'])}个商品场景Prompt")

    quality = {
        "scores": {
            "hook_strength": {"score": 5, "reason": "前3秒痛点共鸣钩子精准"},
            "product_visibility": {"score": 5, "reason": "每个镜头都有产品露出"},
            "selling_point_flow": {"score": 5, "reason": "降噪→防水→低延迟→价格，卖点递进清晰"},
            "cta_clarity": {"score": 5, "reason": "最后3秒明确购买引导"},
            "generatability": {"score": 5, "reason": "Prompt适合即梦/通义万相产品摄影风格"},
        },
        "overall_score": 5.0, "verdict": "通过",
        "suggestions": ["shot_004分屏可考虑加音效同步波形图强化视觉效果"],
    }

    return {
        "scene_type": "product_showcase",
        "project": storyboard["project"],
        "product_info": product_info,
        "scenes": use_scenes,
        "storyboard": storyboard["storyboard"],
        "image_prompts": image_prompts,
        "quality_report": quality,
        "total_shots": len(storyboard["storyboard"]),
    }


def demo_knowledge_short():
    """场景3: 知识口播 —— AI 为什么能理解人类语言"""
    script = "AI 为什么能理解人类语言？用通俗类比解释大语言模型的原理。"

    chars_data = _preprocess(script)
    print(f"\n  [Phase 1] 文案解析: {chars_data['chars']}字符, 5个核心信息点")

    time.sleep(0.3)
    info_points = {
        "topic": "大语言模型原理科普",
        "target_audience": "非技术背景，对 AI 好奇的普通人",
        "key_points": [
            {"id": "kp_001", "point": "大模型本质是'超级完形填空'——根据前文预测下一个词",
             "metaphor": "像一个读了整个图书馆的人，看到'今天天气真___'就知道填'好'"},
            {"id": "kp_002", "point": "训练过程 = 阅读了互联网上几乎所有公开文本",
             "metaphor": "不是'学会'了语言，而是'统计'了所有词语的排列规律"},
            {"id": "kp_003", "point": "模型不真正'理解'语言，只学会了词语间的统计模式",
             "metaphor": "鹦鹉能说'恭喜发财'，但它不知道什么是过年"},
            {"id": "kp_004", "point": "这就是为什么大模型会'一本正经地胡说八道'（幻觉）",
             "metaphor": "当它遇到训练数据里没见过的问题，就开始'合理编造'"},
            {"id": "kp_005", "point": "未来方向：从'预测下一个词'进化到'真正理解语义'",
             "metaphor": "从鹦鹉 → 到真正的对话者"},
        ],
    }
    print(f"  [Phase 2] 信息拆解: {len(info_points['key_points'])}个核心知识点")

    time.sleep(0.4)
    storyboard = {
        "project": {"title": "AI 为什么能理解人类语言？", "topic": "大语言模型原理",
                     "estimated_duration": "60秒"},
        "storyboard": [
            {"shot_id": "shot_001", "shot_type": "中景",
             "camera_angle": "平视", "camera_movement": "固定",
             "visual_description": "主持人面对镜头。背后大屏幕显示一句话被遮住最后一个词：'今天天气真___'。文字动效：最后一个空位闪烁。",
             "key_point": "钩子：提出问题",
             "visual_metaphor": "填空题——正是大模型的运作方式",
             "dialogue": "你有没有想过，AI为什么能跟你对话？其实原理比你想象的简单。",
             "duration_seconds": 5, "transition": "硬切", "mood": "好奇"},
            {"shot_id": "shot_002", "shot_type": "动画",
             "camera_angle": "平视", "camera_movement": "推",
             "visual_description": "全屏动画：一个巨大的图书馆，无数书本自动翻开、文字从书页中飞出、汇聚成一个大脑的形状。弹出字幕：'大模型 = 读完整个互联网'。",
             "key_point": "训练数据规模",
             "visual_metaphor": "图书馆→大脑 = 阅读→理解",
             "dialogue": "大模型本质上是一个读了整个互联网所有公开文本的超级读者。",
             "duration_seconds": 8, "transition": "叠化", "mood": "震撼"},
            {"shot_id": "shot_003", "shot_type": "动画",
             "camera_angle": "正面", "camera_movement": "固定",
             "visual_description": "文字动效：'今天天气真___' → 空格处依次闪现候选词（好/热/冷/差）及概率百分比。最后'好'被高亮选中。弹出：'不是理解，是统计'。",
             "key_point": "完形填空本质",
             "visual_metaphor": "带概率的填空题 = 统计规律",
             "dialogue": "但它并不是真正'理解'了语言。它只是在统计：看到'今天天气真'这几个字后面，出现'好'的概率最高。",
             "duration_seconds": 10, "transition": "硬切", "mood": "顿悟"},
            {"shot_id": "shot_004", "shot_type": "分屏动画",
             "camera_angle": "平视", "camera_movement": "固定",
             "visual_description": "左边：一只鹦鹉在说话泡里说'恭喜发财'，背景是春节。右边：一个小朋友在说话泡里说'恭喜发财'，手里拿着红包。弹出：'鹦鹉 vs 理解'。左边鹦鹉上打❌，右边小朋友上打✅。",
             "key_point": "鹦鹉比喻——能说但不懂",
             "visual_metaphor": "鹦鹉 = 统计模仿，小朋友 = 真正理解",
             "dialogue": "这就好比一只鹦鹉，它学会了说'恭喜发财'，但它不知道什么叫过年。",
             "duration_seconds": 8, "transition": "硬切", "mood": "幽默"},
            {"shot_id": "shot_005", "shot_type": "动画",
             "camera_angle": "平视", "camera_movement": "微推",
             "visual_description": "AI机器人认真地在纸上写字，突然表情一变，开始在纸上乱画。纸上的文字从'地球绕太阳转一圈是365天'变成了'地球绕太阳转一圈大概是...嗯...200天？'。弹出红色警报：'⚠️ 幻觉'。",
             "key_point": "幻觉现象的来源",
             "visual_metaphor": "遇到没见过的题→开始合理编造",
             "dialogue": "这就是为什么AI有时候会一本正经地胡说八道。我们管这叫'幻觉'。",
             "duration_seconds": 7, "transition": "硬切", "mood": "警示"},
            {"shot_id": "shot_006", "shot_type": "动画+口播",
             "camera_angle": "平视", "camera_movement": "拉",
             "visual_description": "画面从混乱涂鸦中升起，鹦鹉飞走，一个发光的人脑图标出现。字幕：'从预测下一个词 → 到真正理解意义'。底部淡入一句话：'这条路刚刚开始。'",
             "key_point": "未来展望",
             "visual_metaphor": "鹦鹉飞走 = 超越统计，发光大脑 = 真正的理解",
             "dialogue": "AI的未来，不再只是猜下一个词，而是真正理解你在说什么。这条路，才刚刚开始。",
             "duration_seconds": 7, "transition": "淡出", "mood": "启发"},
        ],
    }
    print(f"  [Phase 5] 信息可视化分镜: {len(storyboard['storyboard'])}个分镜, 预估{storyboard['project']['estimated_duration']}")

    time.sleep(0.3)
    shot_count = len(storyboard["storyboard"])
    image_prompts = {
        "prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt_cn": f"科普动画风格，{['主持人面对镜头背后大屏幕填空题闪烁','巨大图书馆书本飞出汇聚大脑形状','文字动效填空格候选项概率百分比','分屏鹦鹉说恭喜发财vs小朋友拿红包','AI机器人乱画幻觉红色警报','鹦鹉飞走发光人脑图标未来展望'][i]}，干净现代设计，教育风格",
             "prompt_en": f"educational animation style, {['host facing camera with big screen fill-in-the-blank','giant library books flying forming brain shape','text animation fill blank with probability percentages','split screen parrot vs child understanding concept','AI robot scribbling hallucination red alert','parrot flying away glowing brain icon future'][i]}, clean modern design, motion graphics friendly",
             "negative_prompt": "blur, deformed, text artifacts, cluttered, low quality",
             "style_tags": ["educational", "clean", "modern", "motion graphics"],
             "aspect_ratio": "9:16"}
            for i in range(shot_count)
        ],
    }
    print(f"  [Phase 6] Prompt生成: {len(image_prompts['prompts'])}个知识可视化Prompt")

    quality = {
        "scores": {
            "information_clarity": {"score": 5, "reason": "完形填空→训练数据→统计规律→幻觉→未来，递进清晰"},
            "visual_metaphor_quality": {"score": 5, "reason": "图书馆/填空题/鹦鹉三个核心比喻贯穿始终"},
            "pacing": {"score": 5, "reason": "5s钩子→8s震撼→10s顿悟→8s幽默→7s警示→7s启发，节奏弧线完整"},
            "audience_engagement": {"score": 5, "reason": "非技术观众全程可理解，每个概念都有视觉锚点"},
            "generatability": {"score": 4, "reason": "动画镜头需Motion Graphics工具，Prompt应侧重画面描述而非动画逻辑"},
        },
        "overall_score": 4.8, "verdict": "通过",
        "suggestions": ["shot_003统计动画可简化为静态图表以降低制作难度"],
    }

    return {
        "scene_type": "knowledge_short",
        "project": storyboard["project"],
        "info_points": info_points,
        "storyboard": storyboard["storyboard"],
        "image_prompts": image_prompts,
        "quality_report": quality,
        "total_shots": len(storyboard["storyboard"]),
    }


def demo_cross_border():
    """场景4: 跨境多语言 —— 蓝牙耳机 × 美国市场"""
    script = "ProPods X1 | 42dB ANC | 36hr Battery | $39.99 | Target: US TikTok"

    chars_data = _preprocess(script)
    print(f"\n  [Phase 1] 市场解析: 美国, TikTok/Reels, 英语主+西语字幕")

    time.sleep(0.3)
    print(f"  [Phase 2] 本地化分析: 目标人群18-35岁, Gen-Z审美, 快节奏剪辑")

    time.sleep(0.4)
    storyboard = {
        "project": {"title": "The $40 ANC Earbuds Taking Over TikTok",
                     "product": "ProPods X1", "target_market": "US",
                     "estimated_duration": "15秒"},
        "storyboard": [
            {"shot_id": "shot_001", "shot_type": "中景",
             "camera_angle": "平视", "camera_movement": "固定",
             "visual_description": "NYC subway, guy puts on earbuds. Split screen: left side chaotic noise, right side complete silence with ProPods X1. Text slam: '42dB ANC. SILENCE.'",
             "localization_notes": "US context: NYC subway = universal commuter pain. No Chinese text.",
             "dialogue": "Your commute just got silent.", "duration_seconds": 3,
             "platform": "TikTok", "transition": "硬切", "mood": "relatable"},
            {"shot_id": "shot_002", "shot_type": "特写",
             "camera_angle": "微距", "camera_movement": "固定",
             "visual_description": "Close-up of earbuds in charging case. Battery icon animates from 10% to 100% in seconds. Text overlay: '36 HOURS. NO BS.'",
             "localization_notes": "US audience responds to bold claims with proof. 'NO BS' = casual confidence.",
             "dialogue": "36 hours. No cap.", "duration_seconds": 2.5,
             "platform": "TikTok", "transition": "硬切", "mood": "bold"},
            {"shot_id": "shot_003", "shot_type": "分屏",
             "camera_angle": "正面", "camera_movement": "固定",
             "visual_description": "Split: left side shows $79.99 AirPods-style buds with ❌, right shows ProPods X1 $39.99 with ✅. Quick zoom into price.",
             "localization_notes": "Price comparison is universal. Dollar signs, not yuan.",
             "dialogue": "Same features. Half the price.", "duration_seconds": 3,
             "platform": "TikTok / Reels", "transition": "硬切", "mood": "deal"},
            {"shot_id": "shot_004", "shot_type": "中景",
             "camera_angle": "平视", "camera_movement": "跟",
             "visual_description": "Montage: gym (sweating), gaming (intense face), coffee shop (chill). Earbuds stay in every shot. Text: 'WORKS EVERYWHERE.'",
             "localization_notes": "Lifestyle montage = universal format. Show diversity of users.",
             "dialogue": "Gym. Game. Grind. These stay in.", "duration_seconds": 3.5,
             "platform": "TikTok / Reels", "transition": "硬切", "mood": "energetic"},
            {"shot_id": "shot_005", "shot_type": "产品特写+CTA",
             "camera_angle": "平视→微距", "camera_movement": "推→特写",
             "visual_description": "Earbuds 360 spin on white. Price tag $39.99 slams center. Arrow pointing to link in bio. Optional: 'Tambien disponible en espanol' subtitle.",
             "localization_notes": "CTA = 'Link in bio' (TikTok standard). Spanish option = growing US demographic.",
             "dialogue": "Link in bio. You're welcome.", "duration_seconds": 3,
             "platform": "TikTok", "transition": "硬切", "mood": "confident"},
        ],
    }
    print(f"  [Phase 5] 跨境分镜: {len(storyboard['storyboard'])}个分镜, 预估{storyboard['project']['estimated_duration']}")

    time.sleep(0.3)
    shot_count = len(storyboard["storyboard"])
    image_prompts = {
        "prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt_cn": f"跨境电商产品摄影，{['纽约地铁分屏降噪对比','充电仓电池续航动画','价格对比AirPods风格','健身房游戏厅咖啡厅蒙太奇','耳机360度白色背景价格标签'][i]}，干净布光，生活方式风格",
             "prompt_en": f"e-commerce product photography, {['NYC subway split screen ANC comparison','charging case battery animation','price comparison AirPods style','gym gaming cafe lifestyle montage','earbuds 360 white background price tag'][i]}, clean lighting, lifestyle commercial, 9:16 vertical",
             "negative_prompt": "blur, deformed product, watermark, text in image, Chinese text, low quality",
             "style_tags": ["product photography", "clean lighting", "lifestyle", "commercial"],
             "aspect_ratio": "9:16"}
            for i in range(shot_count)
        ],
    }
    print(f"  [Phase 6] Prompt生成: {len(image_prompts['prompts'])}个跨境场景Prompt")

    quality = {
        "scores": {
            "cultural_adaptation": {"score": 5, "reason": "NYC地铁/美式自信语气/美元定价，完全本地化"},
            "platform_fit": {"score": 5, "reason": "9:16竖屏，快节奏剪辑(平均3秒/镜)，符合TikTok"},
            "language_quality": {"score": 5, "reason": "口语化英语('no cap', 'you're welcome')，有西语扩展"},
            "hook_strength": {"score": 5, "reason": "前3秒分屏对比抓眼球"},
            "generatability": {"score": 5, "reason": "产品摄影+生活方式场景，AI生成友好"},
        },
        "overall_score": 5.0, "verdict": "通过",
        "suggestions": ["可增加阿拉伯语字幕版本覆盖中东TikTok市场"],
    }

    return {
        "scene_type": "cross_border",
        "project": storyboard["project"],
        "storyboard": storyboard["storyboard"],
        "image_prompts": image_prompts,
        "quality_report": quality,
        "total_shots": len(storyboard["storyboard"]),
    }


# ═══════════════════════════════════════
# Demo Runner
# ═══════════════════════════════════════

DEMO_MAP = {
    "short_drama": ("🎬 短剧", demo_short_drama),
    "product_showcase": ("🛒 电商商品展示", demo_product_showcase),
    "knowledge_short": ("📚 知识口播", demo_knowledge_short),
    "cross_border": ("🌍 跨境多语言", demo_cross_border),
}


def run_demo_pipeline(script_text: str = None, scene: str = "short_drama") -> dict:
    """
    运行 Demo 流水线 —— 兼容旧接口

    Args:
        script_text: 剧本/文案（Demo模式下不使用，保留兼容性）
        scene: 场景类型

    Returns:
        完整的结果 dict
    """
    import sys as _sys

    demo_func = DEMO_MAP.get(scene, DEMO_MAP["short_drama"])[1]

    t0 = time.time()
    print("=" * 60)
    print(f"  AI 原生视频生产管线 — Demo 模式")
    print(f"  场景: {DEMO_MAP.get(scene, DEMO_MAP['short_drama'])[0]}")
    print(f"  (无需 API Key，使用内置示例数据)")
    print("=" * 60)

    result = demo_func()

    elapsed = time.time() - t0
    print(f"\n  总耗时: {elapsed:.1f}秒")
    print(f"  场景: {DEMO_MAP.get(scene, ('?','?'))[0]}")
    print(f"  分镜数: {result['total_shots']}")
    print(f"  质量评分: {result['quality_report']['overall_score']}/5 ({result['quality_report']['verdict']})")
    print("=" * 60)

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI 原生视频生产管线 — Demo")
    parser.add_argument("--scene", type=str, default="short_drama",
                        choices=["short_drama", "product_showcase", "knowledge_short", "cross_border", "list"],
                        help="场景类型 (list=列出所有)")
    args = parser.parse_args()

    if args.scene == "list":
        print("=" * 60)
        print("  可用场景列表")
        print("=" * 60)
        for sid, (label, _) in DEMO_MAP.items():
            print(f"  {label:20s}  →  python -m scripts.demo --scene {sid}")
        print()
        return

    result = run_demo_pipeline(scene=args.scene)

    # 保存结果
    output = Path(__file__).parent / "output" / f"demo_{args.scene}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n结果已保存: {output}")


if __name__ == "__main__":
    main()
