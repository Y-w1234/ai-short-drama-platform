"""
数据库模型 —— 对标JD"模型调用记录、生成结果管理"
"""
import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import declarative_base, sessionmaker
import enum

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class ModelCallLog(Base):
    """模型调用记录 —— 对标JD"模型调用记录"
    记录每次大模型API调用的完整信息：模型、耗时、Token数、状态
    """
    __tablename__ = "model_call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), index=True)
    model_name = Column(String(128))           # 使用的模型名称
    provider = Column(String(32))               # 提供商(deepseek/doubao)
    call_type = Column(String(32))              # 调用类型(character/scene/storyboard/prompt/qc)
    prompt_tokens = Column(Integer, default=0)  # Prompt Token数
    completion_tokens = Column(Integer, default=0)  # 输出 Token数
    latency_ms = Column(Integer, default=0)    # 延迟(毫秒)
    status = Column(String(16), default="success")  # success/failed/retry
    retry_count = Column(Integer, default=0)   # 重试次数
    error_message = Column(Text, nullable=True)  # 错误信息
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class GenerationTask(Base):
    """生成任务 —— 对标JD"生成结果管理"
    完整的短剧生成任务记录：输入剧本、输出结果、状态流转
    """
    __tablename__ = "generation_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, index=True)
    status = Column(String(16), default=TaskStatus.PENDING.value)
    script_text = Column(Text)
    script_char_count = Column(Integer, default=0)

    # 各阶段结果(JSON字符串)
    characters_json = Column(Text, nullable=True)
    scenes_json = Column(Text, nullable=True)
    props_json = Column(Text, nullable=True)
    storyboard_json = Column(Text, nullable=True)
    image_prompts_json = Column(Text, nullable=True)
    video_prompts_json = Column(Text, nullable=True)
    quality_report_json = Column(Text, nullable=True)

    # 质量指标
    overall_score = Column(Float, nullable=True)
    total_shots = Column(Integer, nullable=True)

    # 时间记录
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 耗时统计
    total_latency_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

# 初始化数据库
try:
    from .config import config as app_config
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import config as app_config
engine = create_engine(app_config.database.url, echo=app_config.debug)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
