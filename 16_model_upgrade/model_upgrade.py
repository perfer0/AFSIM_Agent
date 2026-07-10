import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
PLAN = STEP_ROOT / "model_upgrade_plan.json"
OLLAMA_EXE = Path("C:/Users/lenovo/AppData/Local/Programs/Ollama/ollama.exe")
OLLAMA_MODELS = ROOT / "ollama" / "models"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run(command: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(OLLAMA_MODELS)
    result = subprocess.run(command, cwd=str(cwd), env=env, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def list_models() -> dict[str, Any]:
    if not OLLAMA_EXE.exists():
        return {"returncode": 127, "stdout": "", "stderr": "ollama.exe not found", "models": []}
    result = run([str(OLLAMA_EXE), "list"])
    models = []
    for line in result["stdout"].splitlines()[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0])
    result["models"] = models
    return result


def command_status(_: argparse.Namespace) -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    plan = load_json(PLAN)
    models = list_models()
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "ollama_models_path": str(OLLAMA_MODELS),
        "ollama_models_exists": OLLAMA_MODELS.exists(),
        "ollama": models,
        "baseline_installed": plan["current_baseline"]["model"] in models.get("models", []),
        "candidates": [
            {
                **candidate,
                "installed": candidate["model"] in models.get("models", []),
            }
            for candidate in plan["candidate_models"]
        ],
    }
    write_json(BUILD / "model_status.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["baseline_installed"] else 1


def command_write_pull_script(_: argparse.Namespace) -> int:
    plan = load_json(PLAN)
    lines = [
        "$env:OLLAMA_MODELS='D:\\AFsim\\Agent\\ollama\\models'",
        "& 'C:\\Users\\lenovo\\AppData\\Local\\Programs\\Ollama\\ollama.exe' list",
        "",
        "# Recommended next model. Uncomment when ready to download several GB.",
    ]
    for candidate in plan["candidate_models"]:
        lines.append(f"# {candidate['pull_command']}")
    lines.append("")
    lines.append("# After pulling, verify with:")
    lines.append("# cd D:\\AFsim\\Agent\\07_agent_loop")
    lines.append("# python .\\agent_loop.py agent .\\requests\\eoir_agent_request.txt --model qwen2.5:7b --run")
    script = "\n".join(lines) + "\n"
    path = BUILD / "pull_candidate_models.ps1"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8")
    print(f"Pull script: {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 16: local model upgrade planning.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=command_status)
    script_parser = subparsers.add_parser("write-pull-script")
    script_parser.set_defaults(func=command_write_pull_script)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
