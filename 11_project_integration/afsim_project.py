import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


STEP_ROOT = Path(__file__).resolve().parent
ROOT = STEP_ROOT.parents[0]
MANIFEST = STEP_ROOT / "project_manifest.json"
BUILD = STEP_ROOT / "build"
ORCHESTRATOR = ROOT / "10_agent_orchestration" / "orchestrator.py"
DEFAULT_REQUEST = STEP_ROOT / "requests" / "integrated_eoir_request.txt"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(command: list[str], cwd: Path, env_extra: dict[str, str] | None = None) -> dict[str, Any]:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(command, cwd=str(cwd), env=env, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def command_status(_: argparse.Namespace) -> int:
    manifest = load_json(MANIFEST)
    model_list = run(
        [manifest["ollama_exe"], "list"],
        ROOT,
        {"OLLAMA_MODELS": manifest["model_storage"]},
    ) if Path(manifest["ollama_exe"]).exists() else {"returncode": 127, "stdout": "", "stderr": "ollama.exe not found"}
    installed_models = [line.split()[0] for line in model_list.get("stdout", "").splitlines()[1:] if line.split()]
    status = {
        "project": manifest["project"],
        "root_exists": Path(manifest["root"]).exists(),
        "mission_exe_exists": Path(manifest["mission_exe"]).exists(),
        "model_storage_exists": Path(manifest["model_storage"]).exists(),
        "ollama_exe_exists": Path(manifest["ollama_exe"]).exists(),
        "installed_models": installed_models,
        "default_model": manifest["default_model"],
        "default_model_installed": manifest["default_model"] in installed_models,
        "smoke_test_model_installed": manifest["smoke_test_model"] in installed_models,
        "layers": [],
    }
    for layer in manifest["layers"]:
        path = ROOT / layer["path"]
        status["layers"].append({**layer, "exists": path.exists()})
    write_json(BUILD / "project_status.json", status)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if (
        status["root_exists"]
        and status["mission_exe_exists"]
        and status["model_storage_exists"]
        and status["ollama_exe_exists"]
        and status["default_model_installed"]
        and all(item["exists"] for item in status["layers"])
    ) else 1


def command_run(args: argparse.Namespace) -> int:
    manifest = load_json(MANIFEST)
    BUILD.mkdir(parents=True, exist_ok=True)
    request_path = Path(args.request).resolve()
    integrated_request = request_path.read_text(encoding="utf-8")
    write_text(BUILD / "integrated_request.txt", integrated_request)

    env_extra = {
        "OLLAMA_MODELS": manifest["model_storage"],
        "AFSIM_AGENT_MODEL": manifest["default_model"],
    }
    orchestration = run([sys.executable, str(ORCHESTRATOR), str(request_path)], ROOT / "10_agent_orchestration", env_extra)
    write_json(BUILD / "orchestration_run.json", orchestration)

    audit_path = ROOT / "10_agent_orchestration" / "build" / "orchestration_audit.json"
    audit = load_json(audit_path) if audit_path.exists() else {"passed": False}
    report = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "project": manifest["project"],
        "request": str(request_path),
        "orchestration_returncode": orchestration["returncode"],
        "audit": audit,
        "quality_gates": {
            "model_storage": manifest["model_storage"],
            "default_model": manifest["default_model"],
            "mission_exe": manifest["mission_exe"],
            "passed": orchestration["returncode"] == 0 and audit.get("passed") is True,
        },
        "next_reading_order": [
            "11_project_integration/README.md",
            "11_project_integration/project_manifest.json",
            "11_project_integration/build/project_run_report.json",
            "10_agent_orchestration/build/orchestration_report.md",
        ],
    }
    write_json(BUILD / "project_run_report.json", report)
    print(f"Project run report: {BUILD / 'project_run_report.json'}")
    print(f"Passed: {report['quality_gates']['passed']}")
    return 0 if report["quality_gates"]["passed"] else 1


def command_report(_: argparse.Namespace) -> int:
    report_path = BUILD / "project_run_report.json"
    if not report_path.exists():
        print(f"Report does not exist: {report_path}")
        return 1
    report = load_json(report_path)
    lines = [
        "# Step 11 Project Integration Report",
        "",
        f"Time: {report['time']}",
        f"Project: {report['project']}",
        f"Passed: {report['quality_gates']['passed']}",
        "",
        "## Gates",
        "",
        f"- orchestration_returncode: {report['orchestration_returncode']}",
        f"- audit.passed: {report['audit'].get('passed')}",
        f"- draft_provider: {report['audit'].get('draft_provider')}",
        f"- run_exit_code: {report['audit'].get('run_exit_code')}",
        "",
        "## Reading Order",
        "",
    ]
    lines.extend(f"- {item}" for item in report["next_reading_order"])
    write_text(BUILD / "project_run_report.md", "\n".join(lines) + "\n")
    print(f"Markdown report: {BUILD / 'project_run_report.md'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 11: project-level integration entry point.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=command_status)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("request", nargs="?", default=str(DEFAULT_REQUEST))
    run_parser.set_defaults(func=command_run)

    report_parser = subparsers.add_parser("report")
    report_parser.set_defaults(func=command_report)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
