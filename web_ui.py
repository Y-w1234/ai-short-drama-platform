"""
AI 原生视频生产管线 — Streamlit Web 界面
面向普通用户的浏览器交互版本，无需命令行

启动: streamlit run web_ui.py
"""
import streamlit as st
import sys
from pathlib import Path

# 确保项目根目录可导入
sys.path.insert(0, str(Path(__file__).parent))

from scripts.demo import DEMO_MAP, run_demo_pipeline
from scenes import list_scenes, SCENES
from security import get_scanner

st.set_page_config(
    page_title="AI 视频生产管线",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 样式 ──
st.markdown("""
<style>
.main-title { font-size: 2.5rem; font-weight: 900; margin-bottom: 0; }
.subtitle { color: #888; font-size: 1.1rem; margin-bottom: 2rem; }
.shot-card {
    background: #1a1a2e; border-radius: 12px; padding: 20px;
    margin: 10px 0; border-left: 4px solid #ff6b35;
}
.shot-card h4 { color: #ff6b35; margin-top: 0; }
.metric-box {
    text-align: center; padding: 20px; background: #0d1117;
    border-radius: 12px; margin: 5px;
}
.metric-box .num { font-size: 2rem; font-weight: 900; color: #ff6b35; }
.metric-box .label { font-size: 0.9rem; color: #888; }
.quality-pass { color: #00c864; font-weight: 700; }
.quality-warn { color: #ff6b35; font-weight: 700; }
.prompt-box {
    background: #0d1117; border-radius: 8px; padding: 15px;
    margin: 8px 0; font-family: monospace; font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ── 侧边栏 ──
with st.sidebar:
    st.markdown("## 🎬 场景选择")
    scene_id = st.selectbox(
        "选择视频场景类型",
        options=[s.value for s in SCENES],
        format_func=lambda x: {
            "short_drama": "🎬 短剧",
            "product_showcase": "🛒 电商商品展示",
            "knowledge_short": "📚 知识口播",
            "cross_border": "🌍 跨境多语言",
        }.get(x, x),
    )

    scene_def = SCENES[scene_id]
    st.markdown(f"**输入**: {scene_def.input_description}")
    st.markdown(f"**输出**: {scene_def.output_description}")
    st.markdown(f"**画幅**: {scene_def.default_aspect_ratio}")
    st.markdown(f"**时长**: {scene_def.target_duration_range}")

    st.markdown("---")
    st.markdown("## 🔒 安全检查")
    enable_safety = st.toggle("启用内容安全扫描", value=True)
    show_safety_report = st.checkbox("显示安全扫描详情", value=False)

    st.markdown("---")
    st.markdown("### 关于")
    st.markdown(
        "**AI 原生视频生产管线 v2.0**\n\n"
        "7个Agent协作，支持短剧/电商/口播/跨境4种场景。"
        "88项安全探测，53种攻击防御。\n\n"
        "[GitHub](https://github.com/Y-w1234/ai-short-drama-platform)"
    )

# ── 主页面 ──
st.markdown(f'<p class="main-title">🎬 AI 原生视频生产管线</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="subtitle">当前场景: {scene_def.icon} {scene_def.name} — {scene_def.description}</p>',
    unsafe_allow_html=True,
)

# ── 输入区 ──
col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_area(
        "输入你的内容",
        value=scene_def.demo_script[:500] if scene_def.demo_script else "",
        height=200,
        placeholder=f"在此粘贴你的{scene_def.input_description}...",
        key="user_input",
    )
with col2:
    st.markdown("### 快捷操作")
    if st.button("🚀 使用Demo数据运行", use_container_width=True):
        user_input = scene_def.demo_script
        st.session_state.user_input = user_input

    st.markdown("---")
    st.markdown("### 设置")
    run_real = st.checkbox("连接真实API (需要Key)", value=False)
    if run_real:
        st.warning("⚠️ 将消耗API额度")

    st.markdown("---")
    st.markdown("### 统计")
    st.markdown(f"输入字符: **{len(user_input)}**")

run_clicked = st.button("🎬 生成视频方案", type="primary", use_container_width=True)

# ── 执行 ──
if run_clicked and user_input:
    # 安全检查
    if enable_safety:
        scanner = get_scanner()
        scan_result = scanner.scan(user_input, scene_def.name)
        if not scan_result.passed:
            st.error(f"🚨 内容安全扫描未通过: {scan_result.reason}")
            if show_safety_report:
                with st.expander("安全扫描详情"):
                    for p in scan_result.blocked_patterns:
                        st.error(p)
                    for w in scan_result.warnings:
                        st.warning(w)
            st.stop()
        elif show_safety_report:
            with st.expander("✅ 安全扫描通过"):
                st.success(scan_result.reason)
                for w in scan_result.warnings:
                    st.info(w)

    # 运行管线
    with st.spinner(f"正在生成 {scene_def.name} 方案... 7个Agent协作中"):
        try:
            if run_real:
                # 真实API模式（需要配置环境变量）
                from tools.llm_client import LLMClient
                from agents.director import DirectorAgent
                from agents.analyst import AnalystAgent
                from agents.storyboarder import StoryboarderAgent
                from agents.prompt_engineer import PromptEngineerAgent
                from agents.reviewer import ReviewerAgent

                llm = LLMClient()
                pipeline = DirectorAgent(llm)
                pipeline.register_agent("analyst", AnalystAgent(llm))
                pipeline.register_agent("storyboarder", StoryboarderAgent(llm))
                pipeline.register_agent("prompt_engineer", PromptEngineerAgent(llm))
                pipeline.register_agent("reviewer", ReviewerAgent(llm))
                result = pipeline.run({"script_text": user_input})
                result = result.data if result.success else None
            else:
                result = run_demo_pipeline(user_input, scene=scene_id)
        except Exception as e:
            st.error(f"执行失败: {e}")
            st.stop()

    if not result:
        st.error("生成失败")
        st.stop()

    st.success(f"✅ 生成完成！")

    # ── 结果展示 ──
    project = result.get("project", {})
    qr = result.get("quality_report", {})
    storyboard = result.get("storyboard", [])
    image_prompts = result.get("image_prompts", {}).get("prompts", [])

    # 指标卡片
    metrics = st.columns(5)
    metrics[0].markdown(
        f'<div class="metric-box"><div class="num">{result["total_shots"]}</div><div class="label">分镜数</div></div>',
        unsafe_allow_html=True,
    )
    metrics[1].markdown(
        f'<div class="metric-box"><div class="num">{qr.get("overall_score", "?")}/5</div><div class="label">质量评分</div></div>',
        unsafe_allow_html=True,
    )
    characters = result.get("characters", {})
    char_count = characters.get("total", 0) if isinstance(characters, dict) else 0
    metrics[2].markdown(
        f'<div class="metric-box"><div class="num">{char_count}</div><div class="label">角色数</div></div>',
        unsafe_allow_html=True,
    )
    scenes = result.get("scenes", {})
    scene_count = scenes.get("total", 0) if isinstance(scenes, dict) else 0
    metrics[3].markdown(
        f'<div class="metric-box"><div class="num">{scene_count}</div><div class="label">场景数</div></div>',
        unsafe_allow_html=True,
    )
    metrics[4].markdown(
        f'<div class="metric-box"><div class="num">{len(image_prompts)}</div><div class="label">AI Prompt</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 分镜表
    tab1, tab2, tab3 = st.tabs(["📋 分镜表", "🎨 AI绘画Prompt", "📊 质量报告"])

    with tab1:
        if storyboard:
            for shot in storyboard:
                shot_type = shot.get("shot_type", "")
                mood = shot.get("mood", "")
                desc = shot.get("visual_description", "")
                dialogue = shot.get("dialogue", "")
                duration = shot.get("duration_seconds", 0)
                camera = shot.get("camera_movement", "")
                transition = shot.get("transition", "")

                st.markdown(f"""
                <div class="shot-card">
                    <h4>🎥 {shot.get('shot_id', '?')} — {shot_type} ({duration}秒)</h4>
                    <p><strong>画面:</strong> {desc}</p>
                    <p><strong>运镜:</strong> {camera} | <strong>转场:</strong> {transition} | <strong>情绪:</strong> {mood}</p>
                </div>
                """, unsafe_allow_html=True)
                if dialogue:
                    st.markdown(f"*💬 {dialogue}*")
        else:
            st.info("暂无分镜数据")

    with tab2:
        if image_prompts:
            for prompt in image_prompts:
                st.markdown(f"""
                <div class="prompt-box">
                    <strong>📸 {prompt.get('shot_id', '?')}</strong><br>
                    <strong>CN:</strong> {prompt.get('prompt_cn', '')}<br>
                    <strong>EN:</strong> {prompt.get('prompt_en', '')}<br>
                    <strong>Negative:</strong> {prompt.get('negative_prompt', '')}<br>
                    <strong>风格:</strong> {', '.join(prompt.get('style_tags', []))} | <strong>画幅:</strong> {prompt.get('aspect_ratio', '16:9')}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("暂无 Prompt 数据")

    with tab3:
        if qr:
            st.markdown(f"### 综合评分: {qr.get('overall_score', '?')}/5 — {qr.get('verdict', '?')}")
            scores = qr.get("scores", {})
            if scores:
                for dim, info in scores.items():
                    score = info.get("score", 0) if isinstance(info, dict) else info
                    reason = info.get("reason", "") if isinstance(info, dict) else ""
                    bar = "█" * int(score) + "░" * (5 - int(score))
                    st.markdown(f"**{dim}**: {bar} ({score}/5)")
                    if reason:
                        st.caption(f"  {reason}")

            suggestions = qr.get("suggestions", [])
            if suggestions:
                st.markdown("### 改进建议")
                for s in suggestions:
                    st.info(s)

            integrity = qr.get("integrity_warning")
            if integrity:
                st.warning(f"⚠️ {integrity}")

# ── 空状态 ──
if not run_clicked:
    st.info("👆 输入内容后点击「生成视频方案」按钮开始")

    # 展示场景对比
    st.markdown("---")
    st.markdown("### 🎯 四种视频场景，一键切换")
    cols = st.columns(4)
    scene_info = {
        "short_drama": ("🎬 短剧", "剧本 → 分镜", "16:9", "60-180秒"),
        "product_showcase": ("🛒 电商", "卖点 → 带货视频", "9:16", "15-45秒"),
        "knowledge_short": ("📚 口播", "文章 → 科普视频", "9:16", "45-90秒"),
        "cross_border": ("🌍 跨境", "商品 → 多语言视频", "1:1", "15-30秒"),
    }
    for i, (sid, (icon_name, flow, ratio, dur)) in enumerate(scene_info.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center; padding:15px; background:#0d1117; border-radius:12px;">
                <div style="font-size:2rem;">{icon_name.split()[0]}</div>
                <div style="font-weight:700;">{icon_name.split()[1]}</div>
                <div style="font-size:0.8rem; color:#888;">{flow}</div>
                <div style="font-size:0.8rem; color:#888;">{ratio} | {dur}</div>
            </div>
            """, unsafe_allow_html=True)
