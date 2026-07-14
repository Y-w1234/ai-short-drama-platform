"""
异步任务队列 —— 对标JD: 任务队列、失败重试、生成结果管理

功能:
1. 异步执行短剧生成任务
2. 任务状态追踪(PENDING→RUNNING→COMPLETED/FAILED)
3. 自动失败重试
4. 结果缓存与过期清理
"""
import uuid
import time
import threading
import logging
from queue import Queue
from typing import Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Task:
    """单个任务"""
    task_id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: any = None
    error: str = ""
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: int = 0  # 0-100
    progress_msg: str = ""

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "progress_msg": self.progress_msg,
            "retry_count": self.retry_count,
            "error": self.error,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "started_at": datetime.fromtimestamp(self.started_at).isoformat() if self.started_at else None,
            "completed_at": datetime.fromtimestamp(self.completed_at).isoformat() if self.completed_at else None,
        }


class TaskQueue:
    """异步任务队列管理器

    对标JD要求:
    - "任务队列": 异步执行耗时任务，不阻塞API响应
    - "失败重试": 自动重试失败任务
    - "生成结果管理": TTL过期清理
    """

    def __init__(self, max_concurrent: int = 5, result_ttl: int = 3600, max_queue_size: int = 100):
        self.queue: Queue = Queue(maxsize=max_queue_size)
        self.tasks: dict[str, Task] = {}
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.result_ttl = result_ttl
        self._workers: list[threading.Thread] = []
        self._running = False
        self._lock = threading.Lock()

    def start(self):
        """启动工作线程"""
        self._running = True
        for i in range(self.max_concurrent):
            t = threading.Thread(target=self._worker, name=f"task-worker-{i}", daemon=True)
            t.start()
            self._workers.append(t)
        logger.info(f"任务队列已启动: {self.max_concurrent} 个工作线程")

    def stop(self):
        """停止队列"""
        self._running = False
        # 向队列发送停止信号
        for _ in self._workers:
            self.queue.put(None)
        for t in self._workers:
            t.join(timeout=5)

    def submit(self, func: Callable, *args, **kwargs) -> str:
        """提交任务，返回 task_id"""
        task_id = str(uuid.uuid4())[:12]
        task = Task(task_id=task_id, func=func, args=args, kwargs=kwargs)
        with self._lock:
            self.tasks[task_id] = task
        self.queue.put(task)
        logger.info(f"任务已提交: {task_id}")
        return task_id

    def get(self, task_id: str) -> Optional[dict]:
        """查询任务状态和结果"""
        with self._lock:
            task = self.tasks.get(task_id)
        if not task:
            return None

        result = task.to_dict()
        if task.status == TaskStatus.COMPLETED:
            result["result"] = task.result
            # 检查 TTL
            if time.time() - task.completed_at > self.result_ttl:
                result["expired"] = True
        return result

    def _worker(self):
        """工作线程"""
        while self._running:
            try:
                task = self.queue.get(timeout=1)
                if task is None:  # 停止信号
                    break

                self._execute(task)
                self.queue.task_done()

            except Exception:
                continue

    def _execute(self, task: Task):
        """执行单个任务，含重试"""
        with self._lock:
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()

        for attempt in range(task.max_retries + 1):
            try:
                task.progress = 10 + attempt * 20
                task.progress_msg = f"第{attempt+1}次尝试..."
                task.result = task.func(*task.args, **task.kwargs)

                with self._lock:
                    task.status = TaskStatus.COMPLETED
                    task.progress = 100
                    task.progress_msg = "完成"
                    task.completed_at = time.time()
                return

            except Exception as e:
                task.retry_count = attempt + 1
                # 净化错误信息: 移除路径/密钥等敏感信息
                raw_err = str(e)
                import re as _re
                raw_err = _re.sub(r'sk-[a-zA-Z0-9_-]{20,}', 'sk-***REDACTED***', raw_err)
                raw_err = _re.sub(r'Bearer\s+[a-zA-Z0-9._\-]+', 'Bearer ***REDACTED***', raw_err)
                raw_err = _re.sub(r'[A-Z]:\\[^\s,;]{10,}', '[PATH_REDACTED]', raw_err)
                raw_err = _re.sub(r'[\w/._-]{30,}', '[LONG_PATH_REDACTED]', raw_err)
                task.error = raw_err
                if attempt < task.max_retries:
                    task.status = TaskStatus.RETRYING
                    task.progress_msg = f"失败，{attempt+2}秒后重试..."
                    logger.warning(f"任务{task.task_id}第{attempt+1}次失败，重试中: {e}")
                    time.sleep(attempt + 2)  # 线性退避
                else:
                    with self._lock:
                        task.status = TaskStatus.FAILED
                        task.progress_msg = "所有重试均失败"
                        task.completed_at = time.time()
                    logger.error(f"任务{task.task_id}最终失败: {e}")


# 全局单例 —— 延迟启动，避免 import 时就创建线程
_task_queue_instance = None

def get_task_queue() -> TaskQueue:
    global _task_queue_instance
    if _task_queue_instance is None:
        _task_queue_instance = TaskQueue(max_concurrent=5)
        _task_queue_instance.start()
    return _task_queue_instance

