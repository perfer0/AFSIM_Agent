import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
CONFIG_PATH = STEP_ROOT / "engineering_config.json"
CASES_PATH = STEP_ROOT / "benchmark_cases.json"
AGENT = ROOT / "07_agent_loop" / "agent_loop.py"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ollama_request(url: str, path: str, timeout: int = 10) -> dict[str, Any]:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(f"{url.rstrip('/')}{path}", timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def installed_models(endpoint: str) -> list[str]:
    base = endpoint.split("/api/", 1)[0]
    return sorted(item["name"] for item in ollama_request(base, "/api/tags").get("models", []))


def doctor() -> dict[str, Any]:
    config = load_json(CONFIG_PATH)
    models = []
    api_error = None
    try:
        models = installed_models(config["ollama_endpoint"])
    except Exception as exc:
        api_error = str(exc)
    model_storage = Path(config["model_storage"])
    production_model = config["models"]["production_baseline"]
    checks = {
        "ollama_api_reachable": api_error is None,
        "ollama_api_error": api_error,
        "installed_models": models,
        "production_model": production_model,
        "production_model_installed": production_model in models,
        "smoke_model_installed": config["models"]["smoke_test"] in models,
        "model_storage": str(model_storage),
        "model_storage_on_d_drive": model_storage.drive.upper() == "D:",
        "model_storage_exists": model_storage.exists(),
        "model_storage_free_gb": round(shutil.disk_usage(model_storage).free / 1024**3, 2) if model_storage.exists() else None,
        "mission_exe_exists": Path(config["mission_exe"]).exists(),
        "agent_exists": AGENT.exists(),
    }
    checks["passed"] = all(
        checks[key]
        for key in [
            "ollama_api_reachable",
            "production_model_installed",
            "model_storage_on_d_drive",
            "model_storage_exists",
            "mission_exe_exists",
            "agent_exists",
        ]
    )
    return checks


def end_time_minutes(end_time: dict[str, Any]) -> float:
    value = float(end_time.get("value", 0))
    unit = end_time.get("unit")
    return value / 60 if unit == "sec" else value * 60 if unit == "hr" else value


def flatten_route(scenario: dict[str, Any]) -> str:
    return "\n".join(
        str(value)
        for actor in scenario.get("actors", [])
        for point in actor.get("route", [])
        for value in point.values()
    )


def flatten_scripts(scenario: dict[str, Any]) -> str:
    return "\n".join(
        str(action.get("script", ""))
        for actor in scenario.get("actors", [])
        for action in actor.get("execute", [])
    )


def semantic_checks(scenario: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, Any]]:
    route = flatten_route(scenario)
    scripts = flatten_scripts(scenario)
    route_points = sum(len(actor.get("route", [])) for actor in scenario.get("actors", []))
    execute_count = sum(len(actor.get("execute", [])) for actor in scenario.get("actors", []))
    actuals = {
        "required_platform_refs": set(expected.get("required_platform_refs", [])) <= set(scenario.get("platform_type_refs", [])),
        "required_target_refs": set(expected.get("required_target_refs", [])) <= set(scenario.get("target_set_refs", [])),
        "event_set_ref": scenario.get("event_output", {}).get("event_set_ref") == expected.get("event_set_ref"),
        "position_contains": all(value in route for value in expected.get("position_contains", [])),
        "route_contains": all(value in route for value in expected.get("route_contains", [])),
        "script_contains": all(value in scripts for value in expected.get("script_contains", [])),
        "minimum_route_points": route_points >= expected.get("minimum_route_points", 0),
        "minimum_execute_count": execute_count >= expected.get("minimum_execute_count", 0),
        "minimum_begin_imaging_count": scripts.count("BeginImaging") >= expected.get("minimum_begin_imaging_count", 0),
        "minimum_end_imaging_count": scripts.count("EndImaging") >= expected.get("minimum_end_imaging_count", 0),
        "maximum_end_minutes": end_time_minutes(scenario.get("end_time", {})) <= expected.get("maximum_end_minutes", float("inf")),
    }
    relevant = set(expected) | {"required_platform_refs", "required_target_refs", "event_set_ref"}
    return [{"name": key, "passed": value} for key, value in actuals.items() if key in relevant]


def trace_summary(trace: dict[str, Any]) -> dict[str, Any]:
    events = trace.get("events", [])
    return {
        "validation_passed": any(event.get("step") == "validate" and event.get("status") == "ok" for event in events),
        "repair_count": sum(event.get("step") == "repair" and event.get("status") == "ok" for event in events),
        "run_exit_code": next((event.get("data", {}).get("exit_code") for event in reversed(events) if event.get("step") == "run"), None),
        "scope_rejected": any(event.get("step") == "scope" and event.get("status") == "failed" for event in events),
        "failed_events": [event for event in events if event.get("status") == "failed"],
    }


def run_case(model: str, case: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    case_dir = BUILD / "runs" / model.replace(":", "_") / case["id"]
    if case_dir.exists():
        shutil.rmtree(case_dir)
    scenario_path = case_dir / "scenario.json"
    command = [
        sys.executable,
        str(AGENT),
        "agent",
        str(STEP_ROOT / case["request"]),
        "--model",
        model,
        "--endpoint",
        config["ollama_endpoint"],
        "--max-repairs",
        str(config["generation"]["max_repairs"]),
        "--build-dir",
        str(case_dir),
        "--scenario-output",
        str(scenario_path),
        "--run",
    ]
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = config["model_storage"]
    started = time.perf_counter()
    timed_out = False
    try:
        result = subprocess.run(
            command,
            cwd=str(ROOT / "07_agent_loop"),
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=config["generation"]["case_timeout_seconds"],
        )
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        result = subprocess.CompletedProcess(
            command,
            124,
            stdout=(exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode("utf-8", errors="replace"),
            stderr=(exc.stderr or "") if isinstance(exc.stderr, str) else (exc.stderr or b"").decode("utf-8", errors="replace"),
        )
    elapsed = round(time.perf_counter() - started, 3)
    trace = load_json(case_dir / "agent_trace.json") if (case_dir / "agent_trace.json").exists() else {"events": []}
    scenario = load_json(scenario_path) if scenario_path.exists() else {}
    summary = trace_summary(trace)
    checks = semantic_checks(scenario, case["expect"]) if scenario else []
    provider = scenario.get("draft_provider")
    no_fallback = provider is None or provider in {"ollama", "ollama_repair"}
    expected_rejection = case["expect"].get("expected_rejection") is True
    if expected_rejection:
        passed = result.returncode == 1 and summary["scope_rejected"] and not scenario
    else:
        passed = (
            result.returncode == 0
            and summary["validation_passed"]
            and summary["run_exit_code"] == 0
            and provider in {"ollama", "ollama_repair"}
            and no_fallback
            and checks
            and all(item["passed"] for item in checks)
        )
    record = {
        "case_id": case["id"],
        "model": model,
        "elapsed_seconds": elapsed,
        "returncode": result.returncode,
        "timed_out": timed_out,
        "draft_provider": provider,
        "no_rules_fallback": no_fallback,
        "expected_rejection": expected_rejection,
        **summary,
        "semantic_checks": checks,
        "generation": scenario.get("_generation", {}),
        "artifacts": {
            "scenario": str(scenario_path),
            "trace": str(case_dir / "agent_trace.json"),
            "main": str(case_dir / "main_generated.txt"),
        },
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "passed": bool(passed),
    }
    write_json(case_dir / "case_result.json", record)
    return record


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# AFSIM Agent 工程基准报告",
        "",
        f"生成时间：{report['generated_at']}",
        f"评测集：`{report['suite']}`",
        f"工程验收：`{'PASSED' if report['engineering_gate_passed'] else 'FAILED'}`",
        "",
        "| 模型 | 通过/总数 | 通过率 | 平均耗时(秒) | 无规则兜底 |",
        "|---|---:|---:|---:|---|",
    ]
    for model in report["models"]:
        lines.append(
            f"| `{model['model']}` | {model['passed_count']}/{model['case_count']} | "
            f"{model['pass_rate']:.0%} | {model['average_elapsed_seconds']:.2f} | `{model['no_fallback']}` |"
        )
    lines.extend(["", "## 样例结果", ""])
    for model in report["models"]:
        for case in model["cases"]:
            failed = [item["name"] for item in case["semantic_checks"] if not item["passed"]]
            lines.append(
                f"- `{model['model']}` / `{case['case_id']}`: "
                f"`{'PASS' if case['passed'] else 'FAIL'}`, {case['elapsed_seconds']}s, "
                f"validate={case['validation_passed']}, mission={case['run_exit_code']}, "
                f"repair={case['repair_count']}, failed_checks={failed or 'none'}"
            )
    lines.extend([
        "",
        "## 结论边界",
        "",
        "本报告只证明当前组件库覆盖的 EOIR 侦察链路。雷达、通信、武器和电子战必须分别增加组件、知识、评测样例和 AFSIM 实跑证据后才能宣称具备工程能力。",
        "",
    ])
    return "\n".join(lines)


def command_doctor(_: argparse.Namespace) -> int:
    result = doctor()
    write_json(BUILD / "doctor_report.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


def command_benchmark(args: argparse.Namespace) -> int:
    config = load_json(CONFIG_PATH)
    suite = load_json(CASES_PATH)
    requested_models = [item.strip() for item in args.models.split(",") if item.strip()]
    available = installed_models(config["ollama_endpoint"])
    missing = [model for model in requested_models if model not in available]
    if missing:
        print(f"Models not installed: {', '.join(missing)}", file=sys.stderr)
        return 2
    model_reports = []
    for model in requested_models:
        cases = []
        for case in suite["cases"]:
            print(f"Running {model} / {case['id']}...", flush=True)
            cases.append(run_case(model, case, config))
        passed_count = sum(case["passed"] for case in cases)
        model_reports.append({
            "model": model,
            "case_count": len(cases),
            "passed_count": passed_count,
            "pass_rate": passed_count / len(cases),
            "average_elapsed_seconds": round(sum(case["elapsed_seconds"] for case in cases) / len(cases), 3),
            "no_fallback": all(case["no_rules_fallback"] for case in cases),
            "cases": cases,
        })
    production = config["models"]["production_baseline"]
    production_report = next((item for item in model_reports if item["model"] == production), None)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "suite": suite["suite"],
        "scope_note": suite["scope_note"],
        "config": config,
        "models": model_reports,
        "engineering_gate_passed": bool(
            production_report
            and production_report["pass_rate"] >= config["acceptance"]["minimum_case_pass_rate"]
            and production_report["no_fallback"]
        ),
    }
    write_json(BUILD / "benchmark_report.json", report)
    write_text(BUILD / "benchmark_report.md", render_report(report))
    print(f"Report: {BUILD / 'benchmark_report.md'}")
    print(f"Engineering gate passed: {report['engineering_gate_passed']}")
    return 0 if report["engineering_gate_passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 19: engineering-grade local model acceptance benchmark.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.set_defaults(func=command_doctor)
    benchmark_parser = subparsers.add_parser("benchmark")
    default_model = load_json(CONFIG_PATH)["models"]["production_baseline"]
    benchmark_parser.add_argument("--models", default=default_model, help="Comma-separated Ollama model names.")
    benchmark_parser.set_defaults(func=command_benchmark)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
