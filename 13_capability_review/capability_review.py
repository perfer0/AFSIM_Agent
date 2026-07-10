import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"


CAPABILITIES = [
    {
        "id": "json_to_afsim",
        "name": "JSON 到 AFSIM 脚本",
        "evidence": ["01_json_to_afsim_main/afsim_ai.py", "01_json_to_afsim_main/build/eoir_demo_generated.txt"],
        "meaning": "能把结构化 JSON 转为 AFSIM 主控脚本，理解最小生成链路。",
    },
    {
        "id": "platform_generation",
        "name": "平台实例生成",
        "evidence": ["02_generate_platform_instances/build/scenario_generated.txt"],
        "meaning": "能生成平台实例、航线、执行脚本，并理解 AFSIM 平台展开。",
    },
    {
        "id": "component_library",
        "name": "组件库建模",
        "evidence": [
            "03_component_library/components/platform_types/uav_eoir.json",
            "03_component_library/components/target_sets/eoir_short_long_targets.json",
        ],
        "meaning": "能把平台类型、目标集、事件输出抽象成可复用组件。",
    },
    {
        "id": "local_llm",
        "name": "本地模型生成 JSON",
        "evidence": ["06_local_model_deployment/examples/local_model_drafted_scenario.json"],
        "json_checks": [{"path": "06_local_model_deployment/examples/local_model_drafted_scenario.json", "key": "draft_provider", "expected": "ollama"}],
        "meaning": "能用本地 Ollama 模型生成想定 JSON，并保留工程校验。",
    },
    {
        "id": "rag",
        "name": "本地 RAG 知识检索",
        "evidence": ["05_rag_knowledge_base/knowledge/afsim_snippets/eoir_platform_instance.md"],
        "meaning": "能把 AFSIM 模板知识放入本地知识库并用于生成上下文。",
    },
    {
        "id": "agent_loop",
        "name": "Agent 闭环",
        "evidence": ["07_agent_loop/build/agent_trace.json", "07_agent_loop/examples/agent_generated_scenario.json"],
        "json_checks": [
            {"path": "07_agent_loop/examples/agent_generated_scenario.json", "key": "draft_provider", "expected": "ollama"},
            {"path": "07_agent_loop/build/agent_trace.json", "event_step": "run", "event_data_key": "exit_code", "expected": 0},
        ],
        "meaning": "能完成 plan/retrieve/draft/validate/generate/run 的自动闭环。",
    },
    {
        "id": "mcp",
        "name": "MCP 工具封装",
        "evidence": ["08_mcp_tools/mcp_server.py", "08_mcp_tools/build/mcp_test_result.json"],
        "meaning": "能把本地 Agent 暴露为标准 MCP 工具，供外部客户端调用。",
    },
    {
        "id": "skill",
        "name": "定制 Skill",
        "evidence": ["09_custom_skills/afsim-scenario-agent/SKILL.md", "09_custom_skills/afsim-scenario-agent/references/workflow.md"],
        "meaning": "能把项目经验固化为 AI 可复用的专业操作手册。",
    },
    {
        "id": "orchestration",
        "name": "总控编排审计",
        "evidence": ["10_agent_orchestration/build/orchestration_audit.json"],
        "json_checks": [{"path": "10_agent_orchestration/build/orchestration_audit.json", "key": "passed", "expected": True}],
        "meaning": "能跨 Skill、MCP、Agent、AFSIM 做端到端审计。",
    },
    {
        "id": "project_integration",
        "name": "项目级入口",
        "evidence": ["11_project_integration/afsim_project.py", "11_project_integration/build/project_run_report.json"],
        "json_checks": [{"path": "11_project_integration/build/project_run_report.json", "key_path": ["quality_gates", "passed"], "expected": True}],
        "meaning": "能用一个项目入口统一查看状态、运行编排、生成报告。",
    },
    {
        "id": "offline_packaging",
        "name": "离线打包交付",
        "evidence": ["12_offline_packaging/build/package_manifest.json", "12_offline_packaging/build/package_verify.json"],
        "json_checks": [{"path": "12_offline_packaging/build/package_verify.json", "key": "passed", "expected": True}],
        "meaning": "能生成离线源码包、校验清单和恢复说明，并排除模型 blob。",
    },
]


NEXT_CAPABILITIES = [
    {
        "name": "扩展想定类型",
        "why": "当前主要是 EOIR 侦察 demo，下一步需要扩展到雷达、通信、武器、电子战或多平台协同。",
    },
    {
        "name": "更强本地模型",
        "why": "qwen2.5:0.5b 适合验证链路，但复杂想定需要 7B/14B 级模型和更强 JSON 修复能力。",
    },
    {
        "name": "真实 AFSIM 组件映射",
        "why": "当前组件库很小，后续要把真实平台库、传感器库、武器库、场景约束纳入 RAG 和校验。",
    },
    {
        "name": "人机协同审查",
        "why": "复杂军事仿真不能只靠模型，需要人工确认约束、参数和战术意图。",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_nested(data: dict[str, Any], path: list[str]) -> Any:
    value: Any = data
    for key in path:
        value = value[key]
    return value


def evaluate_json_check(check: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / check["path"]
    if not path.exists():
        return {**check, "passed": False, "actual": None, "reason": "file missing"}
    data = load_json(path)
    if "event_step" in check:
        events = data.get("events", [])
        event = next((item for item in events if item.get("step") == check["event_step"]), None)
        actual = None if event is None else event.get("data", {}).get(check["event_data_key"])
    elif "key_path" in check:
        actual = get_nested(data, check["key_path"])
    else:
        actual = data.get(check["key"])
    return {**check, "actual": actual, "passed": actual == check["expected"]}


def evaluate_capability(capability: dict[str, Any]) -> dict[str, Any]:
    evidence = []
    for relative in capability["evidence"]:
        path = ROOT / relative
        evidence.append({"path": relative, "exists": path.exists(), "bytes": path.stat().st_size if path.exists() else 0})
    checks = [evaluate_json_check(check) for check in capability.get("json_checks", [])]
    passed = all(item["exists"] for item in evidence) and all(item["passed"] for item in checks)
    return {
        "id": capability["id"],
        "name": capability["name"],
        "passed": passed,
        "meaning": capability["meaning"],
        "evidence": evidence,
        "checks": checks,
    }


def render_markdown(review: dict[str, Any]) -> str:
    lines = [
        "# Step 13 Capability Review",
        "",
        f"Generated at: {review['generated_at']}",
        f"Overall passed: {review['overall_passed']}",
        f"Capabilities passed: {review['passed_count']}/{review['total_count']}",
        "",
        "## 已具备能力",
        "",
    ]
    for item in review["capabilities"]:
        mark = "PASS" if item["passed"] else "FAIL"
        lines.extend(
            [
                f"### {mark} - {item['name']}",
                "",
                item["meaning"],
                "",
                "Evidence:",
            ]
        )
        lines.extend(f"- `{e['path']}` exists={e['exists']} bytes={e['bytes']}" for e in item["evidence"])
        if item["checks"]:
            lines.append("")
            lines.append("Checks:")
            for check in item["checks"]:
                lines.append(f"- `{check['path']}` expected `{check['expected']}`, actual `{check['actual']}`, passed={check['passed']}")
        lines.append("")
    lines.extend(["## 下一阶段能力缺口", ""])
    for item in review["next_capabilities"]:
        lines.extend([f"### {item['name']}", "", item["why"], ""])
    return "\n".join(lines)


def build_review() -> dict[str, Any]:
    capabilities = [evaluate_capability(item) for item in CAPABILITIES]
    passed_count = sum(1 for item in capabilities if item["passed"])
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_count": len(capabilities),
        "passed_count": passed_count,
        "overall_passed": passed_count == len(capabilities),
        "capabilities": capabilities,
        "next_capabilities": NEXT_CAPABILITIES,
    }


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    review = build_review()
    (BUILD / "capability_review.json").write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    (BUILD / "capability_review.md").write_text(render_markdown(review), encoding="utf-8")
    print(f"Capability review: {BUILD / 'capability_review.md'}")
    print(f"Passed: {review['overall_passed']} ({review['passed_count']}/{review['total_count']})")
    return 0 if review["overall_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
