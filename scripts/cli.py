"""
命令行入口 —— 对标JD: 调试脚本、测试用例

用法:
    # 脱机演示（默认短剧）
    python -m scripts.cli demo
    python -m scripts.cli demo --scene product_showcase

    # 列出所有场景
    python -m scripts.cli scenes

    # 分析剧本文件
    python -m scripts.cli run sample.txt --scene short_drama

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
import os
from pathlib import Path

# Windows 终端 emoji 兼容
_IS_WIN = sys.platform == "win32"
if _IS_WIN:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent


def cmd_demo(scene: str = "short_drama"):
    """脱机演示整个流水线"""
    from scripts.demo import run_demo_pipeline
    result = run_demo_pipeline(scene=scene)

    output = PROJECT_ROOT / "output" / f"demo_{scene}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[Done] 结果已保存: {output}")


def cmd_run(script_path: str, scene: str = "short_drama"):
    """分析指定剧本文件"""
    script = Path(script_path).read_text(encoding="utf-8")
    from scripts.demo import run_demo_pipeline
    result = run_demo_pipeline(script, scene=scene)

    output = PROJECT_ROOT / "output" / f"{Path(script_path).stem}_{scene}.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[Done] 结果已保存: {output}")


def cmd_scenes():
    """列出所有可用场景"""
    try:
        from scenes import list_scenes, SCENES
    except ImportError:
        _project_root_insert()
        from scenes import list_scenes, SCENES

    print("=" * 60)
    print("  AI 原生视频生产管线 — 可用场景")
    print("=" * 60)
    for s in list_scenes():
        print(f"\n  {s['icon']} {s['name']:12s}  ({s['id']})")
        print(f"     {s['description']}")
        print(f"     画幅: {s['aspect_ratio']}  |  时长: {s['duration']}")
        print(f"     输入: {s['input']}")
        print(f"     运行: python -m scripts.cli demo --scene {s['id']}")
    print(f"\n  {len(SCENES)} 个场景可用")
    print("=" * 60)


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


HELP = """AI 原生视频生产管线 CLI

用法: python -m scripts.cli <命令> [选项]

命令:
  demo                 脱机演示 (默认短剧场景)
    --scene <场景>      指定场景: short_drama / product_showcase / knowledge_short / cross_border
  run <文件>           分析剧本/文案文件
    --scene <场景>      指定场景类型
  scenes               列出所有可用场景
  tools                查看 Function Calling 工具列表
  prompts              查看 Prompt 模板库
  serve                启动 API 服务 (uvicorn)
  test                 运行测试
  help                 显示帮助

示例:
  python -m scripts.cli demo --scene product_showcase
  python -m scripts.cli demo --scene knowledge_short
  python -m scripts.cli scenes
"""


def _project_root_insert():
    """兼容性：确保项目根目录在 sys.path 中"""
    _pr = str(Path(__file__).parent.parent)
    if _pr not in sys.path:
        sys.path.insert(0, _pr)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "-h", "--help"):
        print(HELP)
        return

    # 解析 --scene 参数
    scene = "short_drama"
    remaining = []
    i = 0
    while i < len(args):
        if args[i] == "--scene" and i + 1 < len(args):
            scene = args[i + 1]
            i += 2
        else:
            remaining.append(args[i])
            i += 1

    cmd = remaining[0] if remaining else ""

    if cmd == "scenes":
        cmd_scenes()
        return

    cmd_handlers = {
        "demo": lambda: cmd_demo(scene),
        "run": lambda: cmd_run(remaining[1], scene) if len(remaining) > 1 else print("请指定剧本文件路径"),
        "tools": cmd_tools,
        "prompts": cmd_prompts,
        "serve": cmd_serve,
        "test": cmd_test,
    }

    handler = cmd_handlers.get(cmd)
    if handler:
        handler()
    else:
        print(f"未知命令: {cmd}\n{HELP}")


if __name__ == "__main__":
    main()
