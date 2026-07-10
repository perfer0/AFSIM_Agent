import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
SKILL_ROOT = ROOT / "09_custom_skills" / "afsim-scenario-agent"
ENV_CHECK = SKILL_ROOT / "scripts" / "check_afsim_agent_env.py"
MCP_TEST = ROOT / "08_mcp_tools" / "mcp_client_test.py"
MCP_SERVER = ROOT / "08_mcp_tools" / "mcp_server.py"
MCP_REQUEST = ROOT / "08_mcp_tools" / "build" / "mcp_request.txt"
MCP_RESULT = ROOT / "08_mcp_tools" / "build" / "mcp_test_result.json"
AGENT_TRACE = ROOT / "07_agent_loop" / "build" / "agent_trace.json"
AGENT_SCENARIO = ROOT / "07_agent_loop" / "examples" / "agent_generated_scenario.json"
OLLAMA_MODELS = ROOT / "ollama" / "models"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run(command: list[str], cwd: Path) -> dict[str, Any]:
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


def extract_mcp_tool_payload(result_path: Path) -> dict[str, Any]:
    result = load_json(result_path)
    text = result["tools_call"]["result"]["content"][0]["text"]
    return json.loads(text)


def audit_outputs(env_check: dict[str, Any], mcp_payload: dict[str, Any]) -> dict[str, Any]:
    trace = load_json(AGENT_TRACE) if AGENT_TRACE.exists() else {"events": []}
    scenario = load_json(AGENT_SCENARIO) if AGENT_SCENARIO.exists() else {}
    events = trace.get("events", [])
    event_map = {event.get("step"): event for event in events}
    run_event = event_map.get("run", {})
    audit = {
        "env_check_returncode": env_check["returncode"],
        "mcp_returncode": mcp_payload.get("mcp", {}).get("returncode"),
        "draft_provider": scenario.get("draft_provider"),
        "run_exit_code": run_event.get("data", {}).get("exit_code"),
        "required_events_present": all(step in event_map for step in ["plan", "scope", "retrieve", "draft", "validate", "generate", "run"]),
        "artifacts_exist": {
            "mcp_server": MCP_SERVER.exists(),
            "mcp_request": MCP_REQUEST.exists(),
            "mcp_result": MCP_RESULT.exists(),
            "agent_trace": AGENT_TRACE.exists(),
            "agent_scenario": AGENT_SCENARIO.exists(),
        },
    }
    audit["passed"] = (
        audit["env_check_returncode"] == 0
        and audit["mcp_returncode"] == 0
        and audit["draft_provider"] in {"ollama", "ollama_repair"}
        and audit["run_exit_code"] == 0
        and audit["required_events_present"]
        and all(audit["artifacts_exist"].values())
    )
    return audit


def render_report(request_text: str, env_check: dict[str, Any], mcp_payload: dict[str, Any], audit: dict[str, Any]) -> str:
    status = "PASSED" if audit["passed"] else "FAILED"
    return f"""# Step 10 Orchestration Report

Generated at: {datetime.now().isoformat(timespec="seconds")}

## Request

{request_text.strip()}

## Orchestration Path

```text
Skill constraints
  -> environment check
  -> MCP client
  -> MCP server tool: afsim_agent_run
  -> Step 07 Agent loop
  -> AFSIM mission.exe
  -> audit report
```

## Audit Status

```text
{status}
```

## Key Evidence

```text
env_check_returncode = {audit["env_check_returncode"]}
mcp_returncode       = {audit["mcp_returncode"]}
draft_provider       = {audit["draft_provider"]}
run_exit_code        = {audit["run_exit_code"]}
events_complete      = {audit["required_events_present"]}
```

## Artifacts

```text
MCP result      {MCP_RESULT}
Agent trace     {AGENT_TRACE}
Scenario JSON   {AGENT_SCENARIO}
```

## MCP Stdout

```text
{mcp_payload.get("mcp", {}).get("stdout", "")}
```
"""


def orchestrate(request_path: Path) -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    request_text = read_text(request_path)
    write_text(BUILD / "orchestration_request.txt", request_text)

    env_check = run([sys.executable, str(ENV_CHECK)], SKILL_ROOT)
    write_json(BUILD / "environment_check.json", env_check)
    if env_check["returncode"] != 0:
        report = render_report(request_text, env_check, {"mcp": {"returncode": None, "stdout": ""}}, {"passed": False, "env_check_returncode": env_check["returncode"], "mcp_returncode": None, "draft_provider": None, "run_exit_code": None, "required_events_present": False})
        write_text(BUILD / "orchestration_report.md", report)
        print("Environment check failed.")
        print(f"Report: {BUILD / 'orchestration_report.md'}")
        return 1

    mcp_run = run([sys.executable, str(MCP_TEST)], ROOT / "08_mcp_tools")
    write_json(BUILD / "mcp_client_run.json", mcp_run)
    if mcp_run["returncode"] != 0:
        print("MCP client test failed.")
        print(mcp_run["stderr"])
        return 1

    mcp_payload = extract_mcp_tool_payload(MCP_RESULT)
    audit = audit_outputs(env_check, mcp_payload)
    write_json(BUILD / "orchestration_audit.json", audit)
    write_text(BUILD / "orchestration_report.md", render_report(request_text, env_check, mcp_payload, audit))
    print(f"Orchestration report: {BUILD / 'orchestration_report.md'}")
    print(f"Audit passed: {audit['passed']}")
    return 0 if audit["passed"] else 1


def main() -> int:
    request_path = Path(sys.argv[1]) if len(sys.argv) > 1 else STEP_ROOT / "requests" / "eoir_orchestration_request.txt"
    return orchestrate(request_path)


if __name__ == "__main__":
    raise SystemExit(main())
