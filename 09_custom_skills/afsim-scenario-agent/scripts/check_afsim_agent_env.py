import json
import os
import subprocess
from pathlib import Path


ROOT = Path("D:/AFsim/Agent")
MISSION_EXE = Path("D:/AFsim/AFSim/afsim-2.9.0-win64/bin/mission.exe")
OLLAMA_EXE = Path("C:/Users/lenovo/AppData/Local/Programs/Ollama/ollama.exe")
OLLAMA_MODELS = ROOT / "ollama" / "models"


def run(command: list[str], cwd: Path | None = None) -> dict:
    try:
        result = subprocess.run(command, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=False)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except FileNotFoundError as exc:
        return {"returncode": 127, "stdout": "", "stderr": str(exc)}


def main() -> int:
    os.environ["OLLAMA_MODELS"] = str(OLLAMA_MODELS)
    checks = {
        "project_root": {"path": str(ROOT), "exists": ROOT.exists()},
        "mission_exe": {"path": str(MISSION_EXE), "exists": MISSION_EXE.exists()},
        "ollama_exe": {"path": str(OLLAMA_EXE), "exists": OLLAMA_EXE.exists()},
        "ollama_models": {"path": str(OLLAMA_MODELS), "exists": OLLAMA_MODELS.exists()},
        "ollama_list": run([str(OLLAMA_EXE), "list"]) if OLLAMA_EXE.exists() else {"returncode": 127, "stdout": "", "stderr": "ollama.exe not found"},
        "git_status": run(["git", "status", "--short"], ROOT) if ROOT.exists() else {"returncode": 127, "stdout": "", "stderr": "project root not found"},
    }
    checks["production_model"] = {
        "name": "qwen2.5:7b",
        "installed": "qwen2.5:7b" in checks["ollama_list"].get("stdout", ""),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    required_ok = (
        checks["project_root"]["exists"]
        and checks["mission_exe"]["exists"]
        and checks["ollama_exe"]["exists"]
        and checks["ollama_models"]["exists"]
        and checks["ollama_list"]["returncode"] == 0
        and checks["production_model"]["installed"]
    )
    return 0 if required_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
