import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
AGENT_DIR = ROOT / "07_agent_loop"
AGENT_SCRIPT = AGENT_DIR / "agent_loop.py"
OLLAMA_MODELS = ROOT / "ollama" / "models"
DEFAULT_MODEL = os.environ.get("AFSIM_AGENT_MODEL", "qwen2.5:7b")


TOOLS = [
    {
        "name": "afsim_agent_run",
        "description": "Run the local AFSIM Agent loop: retrieve knowledge, draft JSON with Ollama, validate, generate AFSIM files, and run mission.exe.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "request_text": {
                    "type": "string",
                    "description": "Natural language AFSIM scenario requirement.",
                },
                "model": {
                    "type": "string",
                    "description": "Local Ollama model name.",
                    "default": DEFAULT_MODEL,
                },
                "run": {
                    "type": "boolean",
                    "description": "Whether to run mission.exe after generation.",
                    "default": True,
                },
                "fallback_rules": {
                    "type": "boolean",
                    "description": "Whether to allow rule fallback if the local model fails.",
                    "default": False,
                },
            },
            "required": ["request_text"],
        },
    },
    {
        "name": "afsim_agent_status",
        "description": "Read the latest Step 07 Agent artifacts and return a compact status summary.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def read_message() -> dict[str, Any] | None:
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        line = line.decode("utf-8").strip()
        if not line:
            break
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = sys.stdin.buffer.read(length)
    return json.loads(body.decode("utf-8"))


def write_message(message: dict[str, Any]) -> None:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def text_result(text: str, is_error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def latest_status() -> dict[str, Any]:
    trace_path = AGENT_DIR / "build" / "agent_trace.json"
    scenario_path = AGENT_DIR / "examples" / "agent_generated_scenario.json"
    main_path = AGENT_DIR / "build" / "main_generated.txt"
    status: dict[str, Any] = {
        "trace": str(trace_path),
        "scenario_json": str(scenario_path),
        "main_txt": str(main_path),
        "exists": {
            "trace": trace_path.exists(),
            "scenario_json": scenario_path.exists(),
            "main_txt": main_path.exists(),
        },
    }
    if trace_path.exists():
        events = load_json(trace_path).get("events", [])
        status["events"] = [{"step": item.get("step"), "status": item.get("status"), "detail": item.get("detail"), "data": item.get("data", {})} for item in events]
    if scenario_path.exists():
        scenario = load_json(scenario_path)
        status["scenario"] = {
            "name": scenario.get("name"),
            "draft_provider": scenario.get("draft_provider"),
            "end_time": scenario.get("end_time"),
        }
    return status


def call_afsim_agent(arguments: dict[str, Any]) -> dict[str, Any]:
    request_text = arguments["request_text"]
    model = arguments.get("model") or DEFAULT_MODEL
    run = arguments.get("run", True)
    fallback_rules = arguments.get("fallback_rules", False)

    BUILD.mkdir(parents=True, exist_ok=True)
    request_path = BUILD / "mcp_request.txt"
    request_path.write_text(request_text, encoding="utf-8")

    command = [sys.executable, str(AGENT_SCRIPT), "agent", str(request_path), "--model", model]
    if run:
        command.append("--run")
    if fallback_rules:
        command.append("--fallback-rules")

    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(OLLAMA_MODELS)

    result = subprocess.run(
        command,
        cwd=str(AGENT_DIR),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    status = latest_status()
    status["mcp"] = {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "ollama_models": str(OLLAMA_MODELS),
    }
    return status


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")

    if request_id is None:
        return None

    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "afsim-local-agent-mcp", "version": "0.1.0"},
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = message.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            if name == "afsim_agent_run":
                result = text_result(json.dumps(call_afsim_agent(arguments), ensure_ascii=False, indent=2))
            elif name == "afsim_agent_status":
                result = text_result(json.dumps(latest_status(), ensure_ascii=False, indent=2))
            else:
                raise ValueError(f"Unknown tool: {name}")
        else:
            raise ValueError(f"Unsupported method: {method}")
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": str(exc)},
        }


def main() -> int:
    while True:
        message = read_message()
        if message is None:
            return 0
        response = handle_request(message)
        if response is not None:
            write_message(response)


if __name__ == "__main__":
    raise SystemExit(main())
