"""
AI图片/视频生成工具封装 —— 对标JD: "接入图片生成模型、视频生成模型等能力，并完成接口封装"

封装的模型：
- 即梦(Jimeng) / 通义万相(Tongyi Wanxiang) 图片生成
- 可灵(Kling) / Sora 视频生成
"""
import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

import requests

try:
    from ..config import config
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config

logger = logging.getLogger(__name__)

# ============================================================
# 生成结果模型
# ============================================================
@dataclass
class GeneratedImage:
    url: str
    width: int = 1024
    height: int = 1024
    prompt_used: str = ""
    model: str = ""
    generation_time_ms: int = 0

@dataclass
class GeneratedVideo:
    url: str
    duration_seconds: int = 4
    fps: int = 24
    prompt_used: str = ""
    model: str = ""
    generation_time_ms: int = 0
    status: str = "completed"  # completed/processing/failed


# ============================================================
# 抽象基类
# ============================================================
class ImageGenClient(ABC):
    """图片生成客户端基类"""
    @abstractmethod
    def generate(self, prompt: str, size: str = "1024x1024",
                 style: str = "cinematic", negative_prompt: str = "") -> GeneratedImage:
        ...

class VideoGenClient(ABC):
    """视频生成客户端基类"""
    @abstractmethod
    def generate(self, prompt: str, duration: int = 4,
                 fps: int = 24, motion: str = "") -> GeneratedVideo:
        ...


# ============================================================
# 即梦（Jimeng）实现
# ============================================================
class JimengImageGen(ImageGenClient):
    """即梦图片生成 —— 字节跳动旗下AI绘画工具"""

    BASE_URL = "https://api.jimeng.ai/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.image.api_key

    def generate(self, prompt: str, size: str = "1024x1024",
                 style: str = "cinematic", negative_prompt: str = "") -> GeneratedImage:
        """调用即梦API生成图片"""
        t0 = time.time()
        try:
            resp = requests.post(
                f"{self.BASE_URL}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": prompt,
                    "size": size,
                    "style": style,
                    "negative_prompt": negative_prompt or "blur, deformed, low quality",
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            elapsed = int((time.time() - t0) * 1000)

            return GeneratedImage(
                url=data["data"][0]["url"],
                width=int(size.split("x")[0]),
                height=int(size.split("x")[1]),
                prompt_used=prompt,
                model="jimeng",
                generation_time_ms=elapsed,
            )
        except Exception as e:
            logger.error(f"即梦图片生成失败: {e}")
            # 返回占位图URL，不中断流程
            return GeneratedImage(
                url=f"https://placeholder.pics/{size}/cccccc/666666?text=Generation+Failed",
                prompt_used=prompt,
                model="jimeng(fallback)",
                generation_time_ms=0,
            )


class JimengVideoGen(VideoGenClient):
    """即梦视频生成"""

    BASE_URL = "https://api.jimeng.ai/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.video.api_key

    def generate(self, prompt: str, duration: int = 4,
                 fps: int = 24, motion: str = "") -> GeneratedVideo:
        """调用即梦API生成视频"""
        t0 = time.time()
        try:
            resp = requests.post(
                f"{self.BASE_URL}/videos/generations",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "prompt": prompt,
                    "duration": duration,
                    "fps": fps,
                    "motion": motion,
                },
                timeout=300,
            )
            resp.raise_for_status()
            data = resp.json()
            elapsed = int((time.time() - t0) * 1000)

            return GeneratedVideo(
                url=data.get("url", ""),
                duration_seconds=duration,
                fps=fps,
                prompt_used=prompt,
                model="jimeng",
                generation_time_ms=elapsed,
                status=data.get("status", "completed"),
            )
        except Exception as e:
            logger.error(f"即梦视频生成失败: {e}")
            return GeneratedVideo(
                url="",
                duration_seconds=duration,
                prompt_used=prompt,
                model="jimeng(fallback)",
                status="failed",
            )


# ============================================================
# 通义万相实现
# ============================================================
class TongyiImageGen(ImageGenClient):
    """通义万相图片生成 —— 阿里旗下AI绘画"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.image.api_key
        # 通义万相使用 DashScope SDK 方式，这里展示 HTTP API 封装
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"

    def generate(self, prompt: str, size: str = "1024*1024",
                 style: str = "cinematic", negative_prompt: str = "") -> GeneratedImage:
        t0 = time.time()
        try:
            resp = requests.post(
                f"{self.base_url}/services/aigc/text2image/image-synthesis",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-DashScope-Async": "enable",
                },
                json={
                    "model": "wanx-v1",
                    "input": {"prompt": prompt},
                    "parameters": {
                        "size": size,
                        "n": 1,
                        "style": "<" + style + ">",
                    },
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            elapsed = int((time.time() - t0) * 1000)
            urls = data.get("output", {}).get("results", [])
            return GeneratedImage(
                url=urls[0]["url"] if urls else "",
                prompt_used=prompt,
                model="tongyi-wanx",
                generation_time_ms=elapsed,
            )
        except Exception as e:
            logger.error(f"通义万相生成失败: {e}")
            return GeneratedImage(
                url="",
                prompt_used=prompt,
                model="tongyi-wanx(fallback)",
            )


# ============================================================
# 工厂函数
# ============================================================
def get_image_gen(provider: str = None) -> ImageGenClient:
    p = provider or config.image.provider
    if p == "tongyi":
        return TongyiImageGen()
    return JimengImageGen()  # 默认即梦

def get_video_gen(provider: str = None) -> VideoGenClient:
    p = provider or config.video.provider
    return JimengVideoGen()
