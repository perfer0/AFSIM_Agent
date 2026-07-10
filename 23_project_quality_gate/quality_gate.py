import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_check(name: str, command: list[str], cwd: Path, expected_returncode: int = 0) -> dict[str, Any]:
    started = time.perf_counter()
    result = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=False, timeout=180)
    return {
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "returncode": result.returncode,
        "expected_returncode": expected_returncode,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "passed": result.returncode == expected_returncode,
    }


def validate_json_files() -> dict[str, Any]:
    started = time.perf_counter()
    errors = []
    count = 0
    for path in PROJECT_ROOT.rglob("*.json"):
        if "ollama" in path.parts and "models" in path.parts:
            continue
        count += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
    return {
        "name": "json_parse",
        "files_checked": count,
        "errors": errors,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "passed": not errors,
    }


def core_checks() -> list[dict[str, Any]]:
    python = sys.executable
    checks = [
        run_check("python_compile", [python, "-m", "compileall", "-q", str(PROJECT_ROOT)], PROJECT_ROOT),
        validate_json_files(),
        run_check("step19_tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"], PROJECT_ROOT / "19_engineering_baseline"),
        run_check("step21_tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"], PROJECT_ROOT / "21_event_evidence_analysis"),
        run_check("step22_tests", [python, "-m", "unittest", "discover", "-s", "tests", "-v"], PROJECT_ROOT / "22_reproducible_experiments"),
        run_check(
            "reference_event_evidence",
            [
                python,
                "event_evidence.py",
                "verify",
                str(PROJECT_ROOT / "01_json_to_afsim_main" / "build" / "output" / "eoir_demo_generated.evt"),
                "--profile",
                "profiles/eoir_reference_demo.json",
                "--output",
                "build/reference_verification.json",
                "--markdown",
                "build/reference_verification.md",
            ],
            PROJECT_ROOT / "21_event_evidence_analysis",
        ),
        run_check("reproducible_experiment", [python, "experiment_runner.py", "run"], PROJECT_ROOT / "22_reproducible_experiments"),
    ]
    return checks


def production_checks() -> list[dict[str, Any]]:
    python = sys.executable
    return [
        run_check("production_doctor", [python, "engineering_benchmark.py", "doctor"], PROJECT_ROOT / "19_engineering_baseline"),
        run_check(
            "production_model_benchmark",
            [python, "engineering_benchmark.py", "benchmark", "--models", "qwen2.5:7b"],
            PROJECT_ROOT / "19_engineering_baseline",
        ),
    ]


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# AFSIM Agent Project Quality Gate",
        "",
        f"Generated: {report['generated_at']}",
        f"Mode: `{report['mode']}`",
        f"Passed: `{'PASS' if report['passed'] else 'FAIL'}`",
        "",
        "| Check | Return | Seconds | Result |",
        "|---|---:|---:|---|",
    ]
    for check in report["checks"]:
        lines.append(
            f"| `{check['name']}` | {check.get('returncode', '-')} | "
            f"{check['elapsed_seconds']} | `{'PASS' if check['passed'] else 'FAIL'}` |"
        )
    lines.extend([
        "",
        "Core mode does not require a large language model. Production mode additionally requires the configured 7B model and the complete Agent benchmark.",
        "",
    ])
    return "\n".join(lines)


def command_run(args: argparse.Namespace) -> int:
    checks = core_checks()
    if args.mode == "production":
        checks.extend(production_checks())
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": args.mode,
        "checks": checks,
        "passed": all(check["passed"] for check in checks),
    }
    write_json(BUILD / f"{args.mode}_quality_report.json", report)
    write_text(BUILD / f"{args.mode}_quality_report.md", render_report(report))
    print(f"Quality report: {BUILD / f'{args.mode}_quality_report.md'}")
    print(f"Passed: {report['passed']}")
    return 0 if report["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 23: unified AFSIM Agent quality gate.")
    parser.add_argument("mode", choices=["core", "production"], nargs="?", default="core")
    parser.set_defaults(func=command_run)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
