"""
短剧生成 API 路由 —— 对标JD: 后端功能开发
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import json
import time
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional

try:
    from ..task_queue import get_task_queue
except ImportError:
    from backend.task_queue import get_task_queue

task_queue = get_task_queue()

router = APIRouter(prefix="/api/v1/drama", tags=["短剧生成"])

# ============================================================
# Request / Response Models
# ============================================================
VALID_SCENES = {"short_drama", "product_showcase", "knowledge_short", "cross_border"}
VALID_MODELS = {"deepseek", "doubao", "openai"}

class DramaRequest(BaseModel):
    script_text: str = Field(..., min_length=10, max_length=50000, description="剧本/文案全文 (10-50000字符)")
    scene_type: Optional[str] = Field("short_drama", description="场景类型: short_drama / product_showcase / knowledge_short / cross_border")
    model: Optional[str] = Field("deepseek", description="LLM模型: deepseek/doubao/openai")
    generate_images: bool = Field(False, description="是否生成图片")
    generate_videos: bool = Field(False, description="是否生成视频")

class DramaResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskResult(BaseModel):
    task_id: str
    status: str
    progress: int
    progress_msg: str = ""
    result: Optional[dict] = None
    error: Optional[str] = None

# ============================================================
# Routes
# ============================================================
@router.post("/generate", response_model=DramaResponse)
async def generate_drama(req: DramaRequest, background_tasks: BackgroundTasks):
    """提交短剧生成任务 —— 异步执行，立即返回 task_id"""
    if req.scene_type and req.scene_type not in VALID_SCENES:
        raise HTTPException(400, detail=f"无效场景类型: {req.scene_type}. 有效值: {VALID_SCENES}")
    if req.model and req.model not in VALID_MODELS:
        raise HTTPException(400, detail=f"无效模型: {req.model}. 有效值: {VALID_MODELS}")

    # 提交前对脚本进行内容安全预扫描
    try:
        from security import get_scanner
        scanner = get_scanner()
        scan_result = scanner.scan(req.script_text, "剧本")
        if not scan_result.passed:
            raise HTTPException(400, detail=f"内容安全扫描未通过: {scan_result.reason}")
    except ImportError:
        pass  # 安全模块可选, 不阻断服务

    task_id = task_queue.submit(
        _run_pipeline,
        script_text=req.script_text,
        model=req.model,
        generate_images=req.generate_images,
        generate_videos=req.generate_videos,
    )
    return DramaResponse(
        task_id=task_id,
        status="pending",
        message="任务已提交，使用 /api/v1/drama/task/{task_id} 查询进度",
    )

@router.get("/task/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    """查询任务状态和结果"""
    task = task_queue.get(task_id)
    if not task:
        raise HTTPException(404, detail=f"任务不存在: {task_id}")
    return TaskResult(**task)

@router.get("/tasks")
async def list_tasks(limit: int = 20):
    """列出最近的任务"""
    tasks = list(task_queue.tasks.values())
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return {"tasks": [t.to_dict() for t in tasks[:limit]]}


@router.get("/scenes")
async def list_scenes():
    """列出所有支持的视频场景类型"""
    try:
        from scenes import list_scenes as ls
        return {"scene_types": ls()}
    except ImportError:
        return {"scene_types": [
            {"id": "short_drama", "name": "短剧", "icon": "🎬",
             "description": "输入剧本 → 角色/场景/道具提取 → 专业分镜表 → AI 绘画/视频 Prompt"},
            {"id": "product_showcase", "name": "电商商品展示", "icon": "🛒",
             "description": "输入商品信息 → 自动拆解卖点 → 场景化分镜 → 带货短视频 Prompt"},
            {"id": "knowledge_short", "name": "知识口播", "icon": "📚",
             "description": "输入文章/观点 → 自动提炼核心信息 → 信息可视化分镜 → 科普短视频 Prompt"},
            {"id": "cross_border", "name": "跨境多语言", "icon": "🌍",
             "description": "输入商品 + 目标市场 → 多语言分镜 → 本地化视频 Prompt"},
        ]}


# ============================================================
# Pipeline Runner
# ============================================================
def _run_pipeline(script_text: str, model: str = "deepseek",
                  generate_images: bool = False, generate_videos: bool = False) -> dict:
    """执行短剧生成流水线 —— 在有API Key时真实运行，否则用Demo"""
    try:
        try:
            from ...tools.llm_client import LLMClient
            from ...agents.director import DirectorAgent
            from ...agents.analyst import AnalystAgent
            from ...agents.storyboarder import StoryboarderAgent
            from ...agents.prompt_engineer import PromptEngineerAgent
            from ...agents.reviewer import ReviewerAgent
        except ImportError:
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

        result = pipeline.run({"script_text": script_text})
        if not result.success:
            raise RuntimeError(result.error)

        return result.data

    except Exception as e:
        # Fallback: 使用本地Demo模式
        try:
            from ...scripts.demo import run_demo_pipeline
        except ImportError:
            from scripts.demo import run_demo_pipeline
        return run_demo_pipeline(script_text)
