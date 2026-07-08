"""
快速演示脚本 —— 不依赖API Key也能跑通全流程
对标JD: 通过AI编程工具独立完成Agent Demo

用法: python -m scripts.demo
"""
import json
import time
from pathlib import Path

# 测试剧本
SAMPLE_SCRIPT = """【第一场】咖啡厅 - 下午

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
小红（擦泪，笑出来）：好。
"""

def run_demo_pipeline(script_text: str = None) -> dict:
    """Demo模式运行完整流水线"""
    script = script_text or SAMPLE_SCRIPT
    print("=" * 60)
    print("  AI 短剧生成平台 — Demo 模式")
    print("  (无需 API Key，使用内置示例数据)")
    print("=" * 60)

    # Phase 1: 预处理
    t0 = time.time()
    lines = [l for l in script.split("\n") if l.strip()]
    chars = len(script.replace(" ", "").replace("\n", ""))
    print(f"\n  [Phase 1] 预处理: {chars}字符, {len(lines)}行, 约{round(chars/200,1)}分钟")

    # Phase 2: 角色
    time.sleep(0.3)
    characters = {
        "characters": [
            {"id": "char_001", "name": "小红", "type": "主角", "gender": "女",
             "age_group": "青年", "personality": ["敏感", "执着", "浪漫"],
             "appearance": ["长发披肩", "素色连衣裙", "眼眶微红"],
             "first_line": "你等了很久吗？",
             "relationships": [{"to": "小明", "relation": "情侣"}]},
            {"id": "char_002", "name": "小明", "type": "主角", "gender": "男",
             "age_group": "青年", "personality": ["温柔", "细心地", "浪漫"],
             "appearance": ["干净短发", "白衬衫", "手里拿咖啡"],
             "first_line": "路上堵车...",
             "relationships": [{"to": "小红", "relation": "情侣"}]},
        ],
        "total": 2,
    }
    print(f"  [Phase 2] 角色提取: {characters['total']}个角色")

    # Phase 3: 场景
    time.sleep(0.3)
    scenes = {
        "scenes": [
            {"id": "scene_001", "name": "街角咖啡厅", "location_type": "室内",
             "time_of_day": "下午", "description": "安静的街角咖啡厅，暖黄色灯光，靠窗位置有两人沙发座，角落书架和绿植，吧台咖啡机低鸣",
             "lighting": "柔和的暖黄顶灯+窗外自然光", "atmosphere": "感动→惊喜→浪漫",
             "color_tone": "暖色调（黄+棕+米白）",
             "characters_present": ["小红", "小明"],
             "key_props": ["咖啡杯", "戒指盒", "手机", "沙发座", "吧台"]},
        ],
        "total": 1,
    }
    print(f"  [Phase 3] 场景提取: {scenes['total']}个场景")

    # Phase 4: 道具
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
        ],
        "total": 3,
    }
    print(f"  [Phase 4] 道具提取: {props['total']}个道具")

    # Phase 5: 分镜规划
    time.sleep(0.5)
    storyboard = {
        "project": {"title": "求婚", "genre": "都市情感", "estimated_duration": "100秒"},
        "storyboard": [
            {"shot_id": "shot_001", "scene_id": "scene_001", "shot_type": "全景",
             "camera_angle": "平视", "camera_setup": "咖啡厅门口视角",
             "visual_description": "咖啡厅全景，小红独自坐在角落靠窗的双人座，不停看手机。周围零星坐着几桌客人，吧台咖啡机冒着蒸汽。下午阳光透过落地窗投下暖黄色光斑。",
             "character_actions": {"小红": "坐在角落，反复看手机，表情焦虑"},
             "dialogue": "", "duration_seconds": 5, "camera_movement": "推", "transition": "硬切", "mood": "焦虑"},
            {"shot_id": "shot_002", "scene_id": "scene_001", "shot_type": "中景",
             "camera_angle": "平视", "camera_setup": "侧面，拍小红抬头",
             "visual_description": "小明从门口走进来，手里端着两杯咖啡。小红抬起头，眼眶微红。小明在她对面坐下。",
             "character_actions": {"小明": "端着两杯咖啡走入场", "小红": "抬头，眼眶微红"},
             "dialogue": "小明：你等了很久吗？", "duration_seconds": 4, "camera_movement": "固定", "transition": "硬切", "mood": "期待"},
            {"shot_id": "shot_003", "scene_id": "scene_001", "shot_type": "近景",
             "camera_angle": "平视", "camera_setup": "正面拍小红",
             "visual_description": "小红眼中的泪光闪烁，声音有些颤抖。睫毛上挂着将落未落的泪珠。",
             "character_actions": {"小红": "眼眶更红，声音颤抖"},
             "dialogue": "小红：三个小时。我以为你不会来了。", "duration_seconds": 3, "camera_movement": "微推", "transition": "硬切", "mood": "委屈"},
            {"shot_id": "shot_004", "scene_id": "scene_001", "shot_type": "特写",
             "camera_angle": "俯视", "camera_setup": "俯拍桌面",
             "visual_description": "小明把咖啡推到小红面前，手指在同一瞬间从口袋里掏出一个小方盒放在桌上。深蓝色天鹅绒在暖光下泛着微光。",
             "character_actions": {"小明": "推咖啡+掏戒指盒放桌上"},
             "dialogue": "小明：路上堵车...还有，我去买了这个。", "duration_seconds": 5, "camera_movement": "固定", "transition": "硬切", "mood": "转折"},
            {"shot_id": "shot_005", "scene_id": "scene_001", "shot_type": "大特写",
             "camera_angle": "平视", "camera_setup": "拍小红的表情",
             "visual_description": "小红看到戒指盒，整个人愣住了。瞳孔微张，嘴唇微微张开。",
             "character_actions": {"小红": "愣住，瞳孔微张"},
             "dialogue": "小红：这是...？", "duration_seconds": 3, "camera_movement": "固定", "transition": "硬切", "mood": "震惊"},
            {"shot_id": "shot_006", "scene_id": "scene_001", "shot_type": "特写",
             "camera_angle": "平视", "camera_setup": "拍小红的手",
             "visual_description": "小红的手指颤抖着打开盒子。盒盖翻开的瞬间，一枚钻戒在咖啡厅暖光下折射出细碎的光芒。",
             "character_actions": {"小红": "颤抖着打开盒子"},
             "dialogue": "", "duration_seconds": 3, "camera_movement": "固定", "transition": "硬切", "mood": "惊喜"},
            {"shot_id": "shot_007", "scene_id": "scene_001", "shot_type": "全景",
             "camera_angle": "平视", "camera_setup": "侧后方",
             "visual_description": "小明从沙发座上起身，单膝跪地。小红捂住了嘴，眼泪终于滑落。周围桌的客人纷纷转头看过来。",
             "character_actions": {"小明": "单膝跪地", "小红": "捂嘴，眼泪滑落"},
             "dialogue": "小明：嫁给我，好吗？", "duration_seconds": 5, "camera_movement": "拉", "transition": "硬切", "mood": "浪漫"},
            {"shot_id": "shot_008", "scene_id": "scene_001", "shot_type": "全景",
             "camera_angle": "平视", "camera_setup": "正面拍两人",
             "visual_description": "小红擦掉眼泪，绽放出灿烂的笑容。整个咖啡厅的客人都站起来鼓掌。阳光透过窗户洒在两人身上。",
             "character_actions": {"小红": "擦泪，灿烂笑", "小明": "期待地抬头"},
             "dialogue": "小红：好。", "duration_seconds": 4, "camera_movement": "固定+微推", "transition": "淡出", "mood": "感动"},
        ],
    }
    shot_count = len(storyboard["storyboard"])
    print(f"  [Phase 5] 分镜规划: {shot_count}个分镜, 预估{storyboard['project']['estimated_duration']}")

    # Phase 6: Prompt生成
    time.sleep(0.3)
    image_prompts = {
        "prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt_cn": f"电影级画质，咖啡厅室内，{['全景浪漫求婚场景','年轻女性抬头含泪','近景女性眼中泪光','钻戒盒特写','大特写震惊表情','手打开戒指盒特写','全景男子单膝跪地求婚','全景两人相拥阳光洒落'][i]}，8K超清，暖色调",
             "prompt_en": f"cinematic photorealistic 8k, {['wide shot cafe interior','medium shot couple talking','closeup woman tearful eyes','extreme closeup diamond ring box on table','extreme closeup shocked face','closeup hands opening box','wide shot man proposing on one knee','wide shot couple embracing'][i]}, warm tones, professional lighting",
             "negative_prompt": "blur, deformed, extra fingers, text artifacts, anime",
             "style_tags": ["cinematic", "photorealistic", "professional lighting"],
             "aspect_ratio": "16:9"}
            for i in range(shot_count)
        ],
    }
    video_prompts = {
        "video_prompts": [
            {"shot_id": f"shot_{i+1:03d}",
             "prompt": f"Cinematic video, {['cafe interior','closeup emotional conversation','tearful closeup','ring box reveal','shocked reaction','opening box','romantic proposal','happy ending'][i]}, smooth camera, 24fps",
             "motion_description": ["缓慢推近", "小明走入自然", "眼泪滚落", "手部动作缓慢", "表情细微变化", "手指颤抖", "下跪动作流畅", "自然微笑"][i],
             "camera_motion": ["推","固定","微推","固定","固定","固定","拉","固定+微推"][i],
             "duration_seconds": [5,4,3,5,3,3,5,4][i]}
            for i in range(shot_count)
        ],
    }
    print(f"  [Phase 6] Prompt生成: {len(image_prompts['prompts'])}图片, {len(video_prompts['video_prompts'])}视频")

    # Phase 7: 质量审核
    time.sleep(0.3)
    quality = {
        "scores": {
            "narrative_flow": {"score": 5, "reason": "8个分镜叙事流畅，起承转合完整，从焦虑到惊喜再到浪漫高潮"},
            "visual_consistency": {"score": 5, "reason": "小红和小明的外貌在所有分镜中保持一致，咖啡厅环境统一"},
            "pacing": {"score": 5, "reason": "分镜节奏从慢(焦虑建立)→快(戒指转折)→慢(浪漫高潮)，张弛有度"},
            "emotional_expression": {"score": 5, "reason": "景别精准服务情感:全景建立→近景委屈→特写震惊→全景浪漫"},
            "generatability": {"score": 5, "reason": "每个分镜的画面描述都在100字以上，细节丰富，可直接用于AI生成"},
        },
        "overall_score": 5.0,
        "verdict": "通过",
        "suggestions": ["如需增强情绪张力，shot_005可加入0.5秒黑场过渡"],
    }
    print(f"  [Phase 7] 质量审核: {quality['overall_score']}/5 ({quality['verdict']})")

    elapsed = time.time() - t0
    print(f"\n  总耗时: {elapsed:.1f}秒")
    print(f"  项目: {storyboard['project']['title']}")
    print(f"  分镜数: {shot_count}")
    print(f"  角色: {characters['total']} | 场景: {scenes['total']} | 道具: {props['total']}")
    print("=" * 60)

    return {
        "project": storyboard["project"],
        "characters": characters,
        "scenes": scenes,
        "props": props,
        "storyboard": storyboard["storyboard"],
        "image_prompts": image_prompts,
        "video_prompts": video_prompts,
        "quality_report": quality,
        "total_shots": shot_count,
    }

if __name__ == "__main__":
    result = run_demo_pipeline()

    # 保存结果
    output = Path("output/demo_result.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n结果已保存: {output}")
