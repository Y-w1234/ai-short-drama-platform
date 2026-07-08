"""
PyCharm 一键启动脚本
右键此文件 → Run，即可启动 API 服务
"""
import sys, os

# Ensure project root is on path and set as working directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print(f"Project root: {PROJECT_ROOT}")
    print("Starting AI Short Drama Platform...")
    print("API docs: http://localhost:8000/docs")
    print("Health:   http://localhost:8000/health")
    print()
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[PROJECT_ROOT],
    )
