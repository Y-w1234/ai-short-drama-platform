"""
FastAPI 主应用 —— 对标JD: AI应用后端功能开发

启动: uvicorn backend.main:app --reload
"""
import sys, os, time
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

try:
    from .routes import drama
except ImportError:
    from backend.routes import drama

# ── CORS 配置 ──
# 生产环境必须替换为具体域名。开发环境允许 localhost。
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000").split(",")

app = FastAPI(
    title="AI 原生视频生产管线",
    description="Agent 驱动的多场景视频自动生成系统",
    version="2.0.0",
    docs_url="/docs" if os.getenv("DISABLE_DOCS", "").lower() != "true" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True,
    max_age=3600,
)


# ── 安全响应头中间件 ──
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if not os.getenv("DEBUG", "").lower() == "true":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

app.add_middleware(SecurityHeadersMiddleware)


# ── 简易速率限制 (内存, 单进程) ──
_rate_store: dict[str, list[float]] = {}
_RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
_RATE_WINDOW = 60

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = _rate_store.setdefault(client_ip, [])
        # 清理过期记录
        bucket[:] = [t for t in bucket if now - t < _RATE_WINDOW]
        if len(bucket) >= _RATE_LIMIT:
            return Response(
                content='{"detail":"速率限制: 每分钟最多%d个请求"}' % _RATE_LIMIT,
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(_RATE_WINDOW)},
            )
        bucket.append(now)
        return await call_next(request)

app.add_middleware(RateLimitMiddleware)

app.include_router(drama.router)


@app.get("/")
def root():
    return {
        "service": "AI Native Video Production Pipeline",
        "version": "2.0.0",
    }


@app.get("/health")
def health():
    return {"status": "ok", "uptime": time.process_time()}
