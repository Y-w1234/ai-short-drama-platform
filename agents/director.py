"""
导演 Agent —— 对标JD: 多Agent协作、工作流编排、任务拆解

Director Agent 是整个系统的总指挥:
1. 收到剧本 → 拆解任务 → 分发给子Agent
2. 协调 Analyst → Storyboarder → PromptEngineer → Reviewer 的工作流
3. 汇总各Agent结果，组装最终输出
"""
import sys, os
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from .base import BaseAgent, AgentResult
except ImportError:
    from agents.base import BaseAgent, AgentResult

DIRECTOR_SYSTEM_PROMPT = """# 角色
你是"AI短剧导演"，整个短剧制作流程的总指挥。

# 你的职责
1. **任务拆解**: 收到剧本后，将其拆解为"角色提取→场景提取→道具提取→分镜规划→Prompt生成→质量审核"6个子任务
2. **Agent调度**: 根据任务类型分发给对应的专业Agent
3. **质量把控**: 汇总各Agent输出，检查一致性和完整度
4. **最终交付**: 组装完整的短剧制作方案

# 调度规则
- 角色提取/场景提取/道具提取 → 交给 Analyst Agent (可并行)
- 分镜规划 → 交给 Storyboarder Agent
- Prompt生成 → 交给 PromptEngineer Agent
- 质量审核 → 交给 Reviewer Agent

# 任务拆解示例
用户输入剧本后，你应该这样拆解:
1. 先做预处理（清洗文本）
2. 并行执行角色、场景、道具提取
3. 合并结果后执行分镜规划
4. 基于分镜生成图片和视频Prompt
5. 最终质量审核
"""


class DirectorAgent(BaseAgent):
    """导演Agent —— 总指挥"""

    role = "短剧导演"
    system_prompt = DIRECTOR_SYSTEM_PROMPT

    def __init__(self, llm_client=None, tool_executor=None):
        super().__init__(llm_client, tool_executor)
        self.sub_agents = {}  # 注册的子Agent: {名称: Agent实例}

    def register_agent(self, name: str, agent: BaseAgent):
        """注册子Agent"""
        self.sub_agents[name] = agent

    def run(self, input_data: dict, context: dict = None) -> AgentResult:
        """导演执行完整流程 —— 协调所有子Agent"""
        script = input_data.get("script_text", "")

        if not script:
            return AgentResult(success=False, error="剧本为空")

        # Phase 1: 并行分析
        analyst = self.sub_agents.get("analyst")
        if analyst:
            char_result = analyst.run({"script_text": script, "task": "character"}, context)
            scene_result = analyst.run({"script_text": script, "task": "scene"}, context)
            props_result = analyst.run({"script_text": script, "task": "props"}, context)
        else:
            return AgentResult(success=False, error="Analyst Agent 未注册")

        # Phase 2: 分镜规划
        storyboarder = self.sub_agents.get("storyboarder")
        if storyboarder:
            board_result = storyboarder.run({
                "script_text": script,
                "characters": char_result.data,
                "scenes": scene_result.data,
                "props": props_result.data,
            }, context)
        else:
            return AgentResult(success=False, error="Storyboarder Agent 未注册")

        # Phase 3: Prompt生成
        prompt_engineer = self.sub_agents.get("prompt_engineer")
        img_prompts = {}
        vid_prompts = {}
        if prompt_engineer:
            img_result = prompt_engineer.run({
                "storyboard": board_result.data,
                "prompt_type": "image",
            }, context)
            vid_result = prompt_engineer.run({
                "storyboard": board_result.data,
                "prompt_type": "video",
            }, context)
            img_prompts = img_result.data
            vid_prompts = vid_result.data

        # Phase 4: 质量审核
        reviewer = self.sub_agents.get("reviewer")
        qc_report = {}
        if reviewer:
            qc_result = reviewer.run({
                "storyboard": board_result.data,
                "image_prompts": img_prompts,
                "video_prompts": vid_prompts,
            }, context)
            qc_report = qc_result.data

        # Phase 5: 组装最终结果
        final_output = {
            "project": board_result.data.get("project", {}),
            "characters": char_result.data,
            "scenes": scene_result.data,
            "props": props_result.data,
            "storyboard": board_result.data.get("storyboard", []),
            "image_prompts": img_prompts,
            "video_prompts": vid_prompts,
            "quality_report": qc_report,
            "total_shots": len(board_result.data.get("storyboard", [])),
        }

        return AgentResult(
            success=True,
            data=final_output,
            reasoning=f"导演完成调度: "
                       f"角色{char_result.data.get('total','?')}个, "
                       f"场景{scene_result.data.get('total','?')}个, "
                       f"分镜{final_output['total_shots']}个",
        )
