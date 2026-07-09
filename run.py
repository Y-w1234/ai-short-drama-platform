"""
AI 短剧生成平台 — 开发环境一键启动脚本
用法: 右键此文件 → Run，或 `python run.py`

注意事项:
- host="0.0.0.0" 允许局域网内其他设备访问（如手机测试）
- reload=True 仅在开发时使用，生产环境应去掉，改用 uvicorn 命令行
- reload_dirs 指定了项目根目录，修改任何代码后自动重启
"""
import sys, os

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print(f"项目根目录: {PROJECT_ROOT}")
    print("启动 AI 短剧生成平台...")
    print("Swagger 文档: http://localhost:8000/docs")
    print("健康检查:     http://localhost:8000/health")
    print()
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # 开发模式热重载（生产环境应设为 False）
        reload_dirs=[PROJECT_ROOT],
    )
