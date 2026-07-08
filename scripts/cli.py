"""
命令行入口 —— 对标JD: 调试脚本、测试用例

用法:
    # 脱机演示
    python -m scripts.cli demo

    # 分析剧本文件
    python -m scripts.cli run sample.txt

    # Function Calling 演示
    python -m scripts.cli tools

    # 查看 Prompt 模板库
    python -m scripts.cli prompts

    # 启动 API 服务
    python -m scripts.cli serve

    # 跑测试
    python -m scripts.cli test
"""
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def cmd_demo():
    """脱机演示整个流水线"""
    from scripts.demo import run_demo_pipeline
    result = run_demo_pipeline()

    output = PROJECT_ROOT / "output" / "demo_result.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[Done] 结果已保存: {output}")


def cmd_run(script_path: str):
    """分析指定剧本文件"""
    script = Path(script_path).read_text(encoding="utf-8")
    from scripts.demo import run_demo_pipeline
    result = run_demo_pipeline(script)

    output = PROJECT_ROOT / "output" / f"{Path(script_path).stem}_result.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[Done] 结果已保存: {output}")


def cmd_tools():
    """Function Calling 工具演示"""
    print("=" * 60)
    print("  Function Calling 工具列表")
    print("=" * 60)
    from tools.function_calling import TOOLS, ToolExecutor

    for tool in TOOLS:
        func = tool["function"]
        params = func["parameters"]["properties"]
        required = func["parameters"].get("required", [])
        print(f"\n  [{func['name']}]")
        print(f"    {func['description']}")
        for pname, pinfo in params.items():
            req_mark = " *" if pname in required else ""
            print(f"    - {pname}: {pinfo['type']}{req_mark} — {pinfo.get('description','')}")

    print(f"\n  {len(TOOLS)} 个工具已注册，可在 Function Calling 中使用")
    print(f"  查看代码: tools/function_calling.py")


def cmd_prompts():
    """Prompt 模板库"""
    from prompts.library import list_prompts
    prompts = list_prompts()
    print("=" * 60)
    print("  Prompt 模板库")
    print("=" * 60)
    for p in prompts:
        if "version" in p:
            print(f"\n  [{p['name']}] v{p['version']}")
            print(f"    模型: {p['model']}")
            print(f"    描述: {p['description']}")
        else:
            print(f"  [{p['category']}] {p['name']}")
    print(f"\n  {len(prompts)} 个 Prompt 模板")
    print(f"  查看代码: prompts/library.py")


def cmd_serve():
    """启动 API 服务"""
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)


def cmd_test():
    """运行测试"""
    import pytest
    test_dir = PROJECT_ROOT / "tests"
    if not test_dir.exists():
        print("[Skip] tests/ 目录不存在，运行 Demo 验证")
        cmd_demo()
        return
    pytest.main([str(test_dir), "-v"])


HELP = """AI 短剧生成平台 CLI

用法: python -m scripts.cli <命令>

命令:
  demo          脱机演示 (无需 API Key)
  run <文件>    分析剧本文件
  tools         查看 Function Calling 工具列表
  prompts       查看 Prompt 模板库
  serve         启动 API 服务 (uvicorn)
  test          运行测试
  help          显示帮助
"""


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "-h", "--help"):
        print(HELP)
        return

    cmd_handlers = {
        "demo": lambda: cmd_demo(),
        "run": lambda: cmd_run(args[1]) if len(args) > 1 else print("请指定剧本文件路径"),
        "tools": cmd_tools,
        "prompts": cmd_prompts,
        "serve": cmd_serve,
        "test": cmd_test,
    }

    handler = cmd_handlers.get(args[0])
    if handler:
        handler()
    else:
        print(f"未知命令: {args[0]}\n{HELP}")


if __name__ == "__main__":
    main()
