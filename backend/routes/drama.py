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
class DramaRequest(BaseModel):
    script_text: str = Field(..., min_length=10, description="短剧剧本全文")
    model: Optional[str] = Field("deepseek", description="LLM模型: deepseek/doubao")
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
