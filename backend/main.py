"""
FastAPI 主应用 —— 对标JD: AI应用后端功能开发

启动: uvicorn backend.main:app --reload
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from .routes import drama
except ImportError:
    from backend.routes import drama

app = FastAPI(
    title="AI 短剧生成平台",
    description="AI驱动的短剧自动生成服务 —— 剧本→角色提取→分镜→Prompt→质量审核",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drama.router)

@app.get("/")
def root():
    return {
        "service": "AI Short Drama Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate": "POST /api/v1/drama/generate",
            "task_status": "GET /api/v1/drama/task/{task_id}",
            "list_tasks": "GET /api/v1/drama/tasks",
            "health": "GET /health",
        },
    }

@app.get("/health")
def health():
    return {"status": "ok", "uptime": time.process_time()}
