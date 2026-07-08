"""
单元测试 —— 对标JD: 测试用例、调试脚本

用法: pytest tests/ -v
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestPreprocessing:
    """文本预处理测试"""

    def test_clean_text(self):
        script = "\n\n\n张三：你好。\n\n\n\n李总：来了。\n\n"
        lines = [l for l in script.split("\n") if l.strip()]
        chars = len(script.replace(" ", "").replace("\n", ""))
        assert len(lines) == 2
        assert chars > 0

    def test_empty_input(self):
        script = ""
        lines = [l for l in script.split("\n") if l.strip()]
        assert len(lines) == 0


class TestJSONParsing:
    """JSON 容错解析测试 —— 对标JD: 异常处理机制"""

    def extract(self, text: str) -> dict:
        """模拟 agents/base.py 的 extract_json"""
        for fence in ["```json", "```"]:
            if fence in text:
                parts = text.split(fence)
                text = parts[1] if len(parts) >= 2 else text
                if "```" in text:
                    text = text.split("```")[0]
                break
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start:end + 1])
            return {"parse_error": True}

    def test_plain_json(self):
        result = self.extract('{"a": 1, "b": "test"}')
        assert result == {"a": 1, "b": "test"}

    def test_markdown_wrapped(self):
        result = self.extract('```json\n{"name": "张三"}\n```')
        assert result == {"name": "张三"}

    def test_json_with_text_before(self):
        result = self.extract('这是分析结果: {"total": 3}')
        assert result == {"total": 3}

    def test_broken_json(self):
        result = self.extract('这是分析结果，无法解析')
        assert "parse_error" in result


class TestDemoPipeline:
    """完整流水线集成测试"""

    def test_demo_runs(self):
        from scripts.demo import run_demo_pipeline
        result = run_demo_pipeline()
        assert result["total_shots"] > 0
        assert result["characters"]["total"] > 0
        assert result["scenes"]["total"] > 0
        assert result["quality_report"]["overall_score"] >= 3.0

    def test_output_format(self):
        """验证输出结构完整性"""
        from scripts.demo import run_demo_pipeline
        result = run_demo_pipeline()
        # 检查所有必要字段
        required_keys = [
            "project", "characters", "scenes", "props",
            "storyboard", "image_prompts", "video_prompts", "quality_report"
        ]
        for key in required_keys:
            assert key in result, f"缺少字段: {key}"

    def test_storyboard_structure(self):
        """分镜表结构验证"""
        from scripts.demo import run_demo_pipeline
        result = run_demo_pipeline()
        shots = result["storyboard"]
        for shot in shots:
            assert "shot_id" in shot
            assert "shot_type" in shot
            assert "visual_description" in shot
            assert "duration_seconds" in shot
            assert shot["duration_seconds"] >= 1


class TestFunctionCalling:
    """Function Calling 工具测试"""

    def test_tools_defined(self):
        from tools.function_calling import TOOLS
        assert len(TOOLS) >= 3

    def test_search_character(self):
        from tools.function_calling import ToolExecutor
        executor = ToolExecutor(
            script_text="张三：你好。\n李总：你好。\n张三：再见。",
            parsed_data={
                "characters": [
                    {"id": "char_001", "name": "张三", "type": "主角",
                     "personality": ["冲动"], "appearance": ["短发"],
                     "first_line": "你好。", "relationships": [{"to": "李总", "relation": "上下级"}]},
                ]
            }
        )
        result = executor.execute("search_character_info", {"character_name": "张三"})
        assert result["found"] is True
        assert result["name"] == "张三"
        assert result["appearances_in_script"] >= 2

    def test_suggest_shot_composition(self):
        from tools.function_calling import ToolExecutor
        executor = ToolExecutor()
        result = executor.execute("suggest_shot_composition", {
            "character_count": 2, "has_dialogue": True, "emotion_intensity": "high"
        })
        assert "shot_type" in result
        assert result["shot_type"] in ["大特写", "特写", "近景", "中景", "全景", "远景"]

    def test_estimate_duration(self):
        from tools.function_calling import ToolExecutor
        executor = ToolExecutor()
        result = executor.execute("estimate_shot_duration", {
            "dialogue_chars": 20, "action_count": 2
        })
        assert result["total_duration_s"] >= 2
        assert result["speaking_time_s"] > 0


class TestAgentBase:
    """Agent 基类测试"""

    def test_agent_result(self):
        from agents.base import AgentResult
        r = AgentResult(success=True, data={"test": 123})
        assert r.success is True
        assert r.data["test"] == 123

    def test_agent_result_failure(self):
        from agents.base import AgentResult
        r = AgentResult(success=False, error="测试错误")
        assert r.success is False
        assert r.error == "测试错误"


class TestTaskQueue:
    """任务队列测试"""

    def test_submit_and_retrieve(self):
        from backend.task_queue import TaskQueue
        q = TaskQueue(max_concurrent=1)
        q.start()

        def dummy_task(x):
            return {"result": x * 2}

        task_id = q.submit(dummy_task, 21)
        import time
        time.sleep(0.5)  # 等待执行完成

        task = q.get(task_id)
        assert task is not None
        assert task["status"] in ["completed", "running"]
        q.stop()

    def test_task_retry(self):
        from backend.task_queue import TaskQueue
        q = TaskQueue(max_concurrent=1)
        q.start()

        call_count = [0]

        def failing_task():
            call_count[0] += 1
            if call_count[0] < 3:
                raise RuntimeError("模拟失败")

        task_id = q.submit(failing_task)
        import time
        time.sleep(5)  # 等待重试

        task = q.get(task_id)
        assert task is not None
        assert call_count[0] >= 2  # 至少重试了
        q.stop()


class TestPromptLibrary:
    """Prompt 模板库测试"""

    def test_list_prompts(self):
        from prompts.library import list_prompts, get_prompt
        prompts = list_prompts()
        assert len(prompts) > 5

    def test_get_character_prompt(self):
        from prompts.library import get_prompt
        prompt = get_prompt("character_extraction_v2")
        assert len(prompt) > 100

    def test_get_vibe_coding_prompt(self):
        from prompts.library import get_prompt
        prompt = get_prompt("fastapi_endpoint")
        assert "FastAPI" in prompt
