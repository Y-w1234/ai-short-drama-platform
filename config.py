"""
配置文件 —— 统一管理所有环境变量和参数
对应JD：模型接口封装、Prompt调优、异常处理
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

PROJECT_ROOT = Path(__file__).parent

@dataclass
class LLMConfig:
    """大模型配置"""
    provider: str = os.getenv("LLM_PROVIDER", "deepseek")  # deepseek / doubao / openai
    model: str = os.getenv("LLM_MODEL", "deepseek-chat")
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 180
    max_retries: int = 3  # 失败重试次数 —— 对标JD"失败重试"要求
    retry_delay: float = 1.0  # 重试间隔(秒)

@dataclass
class ImageGenConfig:
    """图片生成模型配置 —— 对标JD"接入图片生成模型" """
    provider: str = os.getenv("IMAGE_PROVIDER", "jimeng")  # jimeng(即梦) / tongyi(通义万相)
    api_key: str = os.getenv("IMAGE_API_KEY", "")
    default_size: str = "1024x1024"
    default_style: str = "cinematic"

@dataclass
class VideoGenConfig:
    """视频生成模型配置 —— 对标JD"接入视频生成模型" """
    provider: str = os.getenv("VIDEO_PROVIDER", "jimeng")
    api_key: str = os.getenv("VIDEO_API_KEY", "")
    default_duration: int = 4  # 默认4秒
    default_fps: int = 24

@dataclass
class DatabaseConfig:
    """数据库配置 —— 对标JD"模型调用记录" """
    url: str = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/data/drama.db")

@dataclass
class TaskQueueConfig:
    """任务队列配置 —— 对标JD"任务队列" """
    max_concurrent: int = 5
    default_timeout: int = 300
    result_ttl: int = 3600  # 结果保留时间(秒)

@dataclass
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    image: ImageGenConfig = field(default_factory=ImageGenConfig)
    video: VideoGenConfig = field(default_factory=VideoGenConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    task_queue: TaskQueueConfig = field(default_factory=TaskQueueConfig)
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

config = AppConfig()
