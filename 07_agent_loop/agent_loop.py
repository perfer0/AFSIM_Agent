import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.request
from datetime import datetime
from pathlib import Path

import afsim_ai


ROOT = Path(__file__).resolve().parent
KNOWLEDGE = ROOT / "knowledge"
PROMPTS = ROOT / "prompts"
BUILD = ROOT / "build"
EXAMPLES = ROOT / "examples"
DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = os.environ.get("AFSIM_AGENT_MODEL", "qwen2.5:7b")
UNSUPPORTED_SCOPE_TERMS = {
    "radar": "radar",
    "雷达": "radar",
    "communications": "communications",
    "communication": "communications",
    "通信": "communications",
    "weapon": "weapon",
    "missile": "weapon",
    "武器": "weapon",
    "导弹": "weapon",
    "electronic warfare": "electronic_warfare",
    "electronic attack": "electronic_warfare",
    "电子战": "electronic_warfare",
    "电子攻击": "electronic_warfare",
}

SCENARIO_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "platform_type_refs": {
            "type": "array",
            "items": {"type": "string", "enum": ["uav_eoir", "ground_site"]},
            "minItems": 2,
        },
        "actors": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "platform_type_ref": {"type": "string", "enum": ["uav_eoir"]},
                    "side": {"type": "string", "enum": ["blue", "red", "white", "green", "neutral"]},
                    "route": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "properties": {
                                "position": {"type": "string"},
                                "altitude": {"type": "string"},
                                "speed": {"type": "string"},
                                "heading": {"type": "string"},
                            },
                            "required": ["position", "altitude", "speed", "heading"],
                        },
                    },
                    "execute": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "string"},
                                "relative": {"type": "boolean"},
                                "script": {
                                    "type": "string",
                                    "pattern": "^(BeginImaging\\(\\\"eoir\\\", \\\"\\\", -?[0-9]+(?:\\.[0-9]+)?, [0-9]+(?:\\.[0-9]+)?\\);|EndImaging\\(\\);)$",
                                },
                            },
                            "required": ["time", "relative", "script"],
                        },
                    },
                },
                "required": ["name", "platform_type_ref", "side", "route", "execute"],
            },
        },
        "target_set_refs": {
            "type": "array",
            "items": {"type": "string", "enum": ["eoir_short_long_targets"]},
            "minItems": 1,
        },
        "event_pipe": {
            "type": "object",
            "properties": {"file": {"type": "string", "pattern": "^output/[A-Za-z0-9_.-]+\\.aer$"}},
            "required": ["file"],
        },
        "event_output": {
            "type": "object",
            "properties": {
                "file": {"type": "string", "pattern": "^output/[A-Za-z0-9_.-]+\\.evt$"},
                "event_set_ref": {"type": "string", "enum": ["eoir_sensor_events"]},
            },
            "required": ["file", "event_set_ref"],
        },
        "end_time": {
            "type": "object",
            "properties": {
                "value": {"type": "integer", "minimum": 1, "maximum": 120},
                "unit": {"type": "string", "enum": ["sec", "min", "hr"]},
            },
            "required": ["value", "unit"],
        },
    },
    "required": [
        "name", "description", "platform_type_refs", "actors", "target_set_refs",
        "event_pipe", "event_output", "end_time",
    ],
}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def tokenize(text: str) -> set[str]:
    words = set(re.findall(r"[A-Za-z0-9_]+", text.lower()))
    normalized = text.lower()
    synonyms = {
        "eoir": ["eoir", "eo/ir", "光电", "红外"],
        "sensor": ["sensor", "传感器", "探测器"],
        "event": ["event", "事件", "输出"],
        "target": ["target", "目标", "目标区"],
        "uav": ["uav", "无人机"],
        "route": ["route", "waypoint", "航路", "航点"],
        "imaging": ["imaging", "image", "成像", "侦察"],
        "ground": ["ground", "地面", "地面站"],
        "position": ["position", "坐标", "位置"],
    }
    for canonical, variants in synonyms.items():
        if any(variant in normalized for variant in variants):
            words.add(canonical)
    return words


def retrieve_knowledge(request_text: str, top_k: int = 3) -> list[dict]:
    request_terms = tokenize(request_text)
    catalog_path = KNOWLEDGE / "catalog.json"
    catalog = load_json(catalog_path) if catalog_path.exists() else {"documents": []}
    metadata = {item["path"].replace("/", os.sep): item for item in catalog.get("documents", [])}
    hits = []
    for path in KNOWLEDGE.rglob("*.md"):
        text = load_text(path)
        terms = tokenize(text)
        relative = str(path.relative_to(KNOWLEDGE))
        item = metadata.get(relative, {})
        metadata_terms = tokenize(" ".join(item.get("keywords", []) + item.get("components", [])))
        score = len(request_terms & terms) + 3 * len(request_terms & metadata_terms)
        if score:
            hits.append({
                "path": str(path.relative_to(ROOT)),
                "score": score,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "source": item.get("source", "local_project_knowledge"),
                "text": text,
            })
    hits.sort(key=lambda item: (-item["score"], item["path"]))
    return hits[:top_k]


def validate_request_scope(request_text: str) -> list[str]:
    if not request_text.strip():
        return ["request is empty"]
    if len(request_text) > 20000:
        return ["request exceeds the 20000 character limit"]
    lowered = request_text.lower()
    unsupported = sorted({capability for term, capability in UNSUPPORTED_SCOPE_TERMS.items() if term in lowered})
    if unsupported:
        return [
            "unsupported scenario capability: " + ", ".join(unsupported) + "; current validated scope is EOIR reconnaissance only"
        ]
    return []


def format_context(hits: list[dict]) -> str:
    blocks = []
    for hit in hits:
        blocks.append(
            f"## {hit['path']} (score={hit['score']}, sha256={hit['sha256']}, source={hit['source']})\n\n"
            f"{hit['text'].strip()}"
        )
    return "\n\n---\n\n".join(blocks)


def extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def call_ollama(prompt: str, model: str, endpoint: str) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "format": SCENARIO_SCHEMA,
        "keep_alive": "10m",
        "options": {"temperature": 0, "top_p": 0.9, "num_ctx": 8192},
        "prompt": prompt,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    draft = extract_json(body.get("response", ""))
    draft["_generation"] = {
        "model": body.get("model", model),
        "total_duration_ns": body.get("total_duration"),
        "load_duration_ns": body.get("load_duration"),
        "prompt_eval_count": body.get("prompt_eval_count"),
        "eval_count": body.get("eval_count"),
        "eval_duration_ns": body.get("eval_duration"),
    }
    return draft


def rule_fallback() -> dict:
    draft = afsim_ai.local_rule_draft()
    draft["name"] = "eoir_agent_loop_demo"
    draft["description"] = "Generated by the step 07 agent rule fallback."
    draft["event_pipe"]["file"] = "output/eoir_agent_loop_demo.aer"
    draft["event_output"]["file"] = "output/eoir_agent_loop_demo.evt"
    return draft


class AgentTrace:
    def __init__(self) -> None:
        self.events = []

    def add(self, step: str, status: str, detail: str, data: dict | None = None) -> None:
        self.events.append(
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "step": step,
                "status": status,
                "detail": detail,
                "data": data or {},
            }
        )

    def save(self, path: Path) -> None:
        write_json(path, {"events": self.events})


def build_draft_prompt(request_text: str, context: str) -> str:
    return (
        f"{load_text(PROMPTS / 'agent_draft_prompt.md')}\n\n"
        f"## 必须满足的 JSON Schema\n\n{json.dumps(SCENARIO_SCHEMA, ensure_ascii=False)}\n\n"
        f"## 检索到的 AFSIM 知识\n\n{context}\n\n"
        f"## 用户需求\n\n{request_text}\n"
    )


def build_repair_prompt(request_text: str, context: str, draft: dict, errors: list[str]) -> str:
    return (
        f"{load_text(PROMPTS / 'agent_repair_prompt.md')}\n\n"
        f"## 必须满足的 JSON Schema\n\n{json.dumps(SCENARIO_SCHEMA, ensure_ascii=False)}\n\n"
        f"## 用户需求\n\n{request_text}\n\n"
        f"## 检索到的 AFSIM 知识\n\n{context}\n\n"
        f"## 当前 JSON\n\n{json.dumps(draft, ensure_ascii=False, indent=2)}\n\n"
        f"## 校验错误\n\n{json.dumps(errors, ensure_ascii=False, indent=2)}\n"
    )


def draft_with_agent(request_text: str, context: str, model: str, endpoint: str, fallback_rules: bool, trace: AgentTrace) -> dict:
    try:
        draft = call_ollama(build_draft_prompt(request_text, context), model, endpoint)
        draft["draft_provider"] = "ollama"
        trace.add("draft", "ok", "local model produced schema-constrained scenario JSON", draft.get("_generation", {"model": model}))
        return draft
    except Exception as exc:
        trace.add("draft", "failed", str(exc), {"model": model})
        if not fallback_rules:
            raise
        draft = rule_fallback()
        draft["draft_provider"] = "rules_fallback"
        draft["local_model_error"] = str(exc)
        trace.add("draft", "fallback", "used rule fallback scenario JSON")
        return draft


def repair_until_valid(
    request_text: str,
    context: str,
    draft: dict,
    model: str,
    endpoint: str,
    max_repairs: int,
    fallback_rules: bool,
    trace: AgentTrace,
) -> tuple[dict, list[str]]:
    for attempt in range(max_repairs + 1):
        errors = afsim_ai.validate_scenario(draft)
        if not errors:
            trace.add("validate", "ok", f"scenario JSON passed validation on attempt {attempt}")
            return draft, []
        trace.add("validate", "failed", f"validation failed on attempt {attempt}", {"errors": errors})
        if attempt >= max_repairs:
            break
        try:
            draft = call_ollama(build_repair_prompt(request_text, context, draft, errors), model, endpoint)
            draft["draft_provider"] = "ollama_repair"
            trace.add("repair", "ok", f"local model repaired scenario JSON on attempt {attempt + 1}")
        except Exception as exc:
            trace.add("repair", "failed", str(exc))
            break
    if fallback_rules:
        draft = rule_fallback()
        draft["draft_provider"] = "rules_fallback_after_repair"
        errors = afsim_ai.validate_scenario(draft)
        trace.add("repair", "fallback", "used rule fallback after repair loop", {"errors": errors})
        return draft, errors
    return draft, afsim_ai.validate_scenario(draft)


def generate_outputs(draft: dict, build_dir: Path, trace: AgentTrace) -> tuple[Path, Path]:
    errors = afsim_ai.validate_scenario(draft)
    if errors:
        raise ValueError(f"Cannot generate invalid scenario: {errors}")
    platform_types = afsim_ai.load_platform_types(draft)
    platforms = afsim_ai.expand_platforms(draft, platform_types)
    build_dir.mkdir(parents=True, exist_ok=True)
    scenario_path = build_dir / "scenario_generated.txt"
    main_path = build_dir / "main_generated.txt"
    write_text(scenario_path, afsim_ai.render_scenario_instances(platforms))
    write_text(main_path, afsim_ai.render_main(draft, platform_types, scenario_path.name))
    trace.add("generate", "ok", "generated AFSIM main and scenario files", {"platforms": len(platforms)})
    return main_path, scenario_path


def run_mission(main_path: Path, trace: AgentTrace) -> int:
    main_path = main_path.resolve()
    main_path.parent.joinpath("output").mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(afsim_ai.MISSION_EXE), str(main_path)],
        cwd=str(main_path.parent),
        text=True,
        capture_output=True,
        check=False,
    )
    write_text(main_path.parent / "mission_stdout.log", result.stdout)
    write_text(main_path.parent / "mission_stderr.log", result.stderr)
    trace.add("run", "ok" if result.returncode == 0 else "failed", "mission.exe finished", {"exit_code": result.returncode})
    return result.returncode


def command_agent(args: argparse.Namespace) -> int:
    build_dir = Path(args.build_dir).resolve()
    scenario_output = Path(args.scenario_output).resolve()
    build_dir.mkdir(parents=True, exist_ok=True)
    trace = AgentTrace()
    request_text = load_text(Path(args.request))
    trace.add("plan", "ok", "plan: retrieve knowledge, draft JSON, validate, repair if needed, generate AFSIM, run mission")

    scope_errors = validate_request_scope(request_text)
    if scope_errors:
        trace.add("scope", "failed", "request is outside the validated capability boundary", {"errors": scope_errors})
        trace.save(build_dir / "agent_trace.json")
        print("Request rejected:")
        for error in scope_errors:
            print(f"  - {error}")
        return 1
    trace.add("scope", "ok", "request is inside the validated EOIR capability boundary")

    hits = retrieve_knowledge(request_text, args.top_k)
    context = format_context(hits)
    write_text(build_dir / "retrieval_context.md", context)
    trace.add("retrieve", "ok", "retrieved catalog-ranked local AFSIM knowledge snippets", {"hits": [{"path": h["path"], "score": h["score"], "sha256": h["sha256"], "source": h["source"]} for h in hits]})

    try:
        draft = draft_with_agent(request_text, context, args.model, args.endpoint, args.fallback_rules, trace)
        draft, errors = repair_until_valid(
            request_text,
            context,
            draft,
            args.model,
            args.endpoint,
            args.max_repairs,
            args.fallback_rules,
            trace,
        )
        write_json(scenario_output, draft)
        if errors:
            print("Agent failed to produce a valid scenario:")
            for error in errors:
                print(f"  - {error}")
            trace.save(build_dir / "agent_trace.json")
            return 1
        main_path, _ = generate_outputs(draft, build_dir, trace)
        exit_code = run_mission(main_path, trace) if args.run else 0
        trace.save(build_dir / "agent_trace.json")
        print(f"Agent trace: {build_dir / 'agent_trace.json'}")
        print(f"Retrieval context: {build_dir / 'retrieval_context.md'}")
        print(f"Scenario JSON: {scenario_output}")
        print(f"AFSIM main: {build_dir / 'main_generated.txt'}")
        if args.run:
            print(f"mission.exe exit code: {exit_code}")
        return exit_code
    except Exception as exc:
        trace.add("agent", "failed", str(exc))
        trace.save(build_dir / "agent_trace.json")
        print(f"Agent failed: {exc}")
        return 1


def command_clean(_: argparse.Namespace) -> int:
    for path in [BUILD, EXAMPLES / "agent_generated_scenario.json"]:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    print("Cleaned step 07 generated artifacts.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 07: Agent loop for local AFSIM scenario generation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    agent_parser = subparsers.add_parser("agent")
    agent_parser.add_argument("request")
    agent_parser.add_argument("--model", default=DEFAULT_MODEL)
    agent_parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    agent_parser.add_argument("--top-k", type=int, default=3)
    agent_parser.add_argument("--max-repairs", type=int, default=2)
    agent_parser.add_argument("--fallback-rules", action="store_true")
    agent_parser.add_argument("--run", action="store_true")
    agent_parser.add_argument("--build-dir", default=str(BUILD))
    agent_parser.add_argument("--scenario-output", default=str(EXAMPLES / "agent_generated_scenario.json"))
    agent_parser.set_defaults(func=command_agent)

    clean_parser = subparsers.add_parser("clean")
    clean_parser.set_defaults(func=command_clean)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
