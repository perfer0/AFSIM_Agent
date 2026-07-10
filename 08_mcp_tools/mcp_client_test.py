import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SERVER = ROOT / "mcp_server.py"
REQUEST = ROOT / "requests" / "eoir_mcp_request.txt"
BUILD = ROOT / "build"


def encode_message(message: dict[str, Any]) -> bytes:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body


def read_message(process: subprocess.Popen) -> dict[str, Any]:
    headers = {}
    while True:
        line = process.stdout.readline()
        if not line:
            raise RuntimeError("MCP server closed stdout")
        decoded = line.decode("utf-8").strip()
        if not decoded:
            break
        key, value = decoded.split(":", 1)
        headers[key.lower()] = value.strip()
    body = process.stdout.read(int(headers["content-length"]))
    return json.loads(body.decode("utf-8"))


def request(process: subprocess.Popen, request_id: int, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    message = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        message["params"] = params
    process.stdin.write(encode_message(message))
    process.stdin.flush()
    return read_message(process)


def notify(process: subprocess.Popen, method: str, params: dict[str, Any] | None = None) -> None:
    message = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        message["params"] = params
    process.stdin.write(encode_message(message))
    process.stdin.flush()


def main() -> int:
    process = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=str(ROOT),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        BUILD.mkdir(parents=True, exist_ok=True)
        results = {}
        results["initialize"] = request(process, 1, "initialize", {"clientInfo": {"name": "step08-test", "version": "0.1.0"}})
        print(json.dumps(results["initialize"], ensure_ascii=False, indent=2))
        notify(process, "notifications/initialized")
        results["tools_list"] = request(process, 2, "tools/list")
        print(json.dumps(results["tools_list"], ensure_ascii=False, indent=2))
        request_text = REQUEST.read_text(encoding="utf-8")
        response = request(
            process,
            3,
            "tools/call",
            {
                "name": "afsim_agent_run",
                "arguments": {
                    "request_text": request_text,
                    "model": os.environ.get("AFSIM_AGENT_MODEL", "qwen2.5:7b"),
                    "run": True,
                    "fallback_rules": False,
                },
            },
        )
        results["tools_call"] = response
        (BUILD / "mcp_test_result.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        if "error" in response:
            return 1
        text = response["result"]["content"][0]["text"]
        payload = json.loads(text)
        returncode = payload["mcp"]["returncode"]
        draft_provider = payload.get("scenario", {}).get("draft_provider")
        exit_code = None
        for event in payload.get("events", []):
            if event.get("step") == "run":
                exit_code = event.get("data", {}).get("exit_code")
        if returncode != 0 or draft_provider != "ollama" or exit_code != 0:
            print(f"Unexpected MCP result: returncode={returncode}, draft_provider={draft_provider}, exit_code={exit_code}", file=sys.stderr)
            return 1
        return 0
    finally:
        process.stdin.close()
        process.terminate()
        process.wait(timeout=10)
        stderr = process.stderr.read().decode("utf-8", errors="replace").strip()
        if stderr:
            print(stderr, file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
