import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
REQUIRED_DOCS = [
    STEP_ROOT / "README.md",
    STEP_ROOT / "PITFALLS.md",
    STEP_ROOT / "ACCEPTANCE.md",
    STEP_ROOT / "EXPERT_ROADMAP.md",
    STEP_ROOT / "EXPERIMENT_TEMPLATE.md",
    STEP_ROOT / "PROJECT_GAP_ANALYSIS.md",
]
CONFIG = ROOT / "19_engineering_baseline" / "engineering_config.json"
BENCHMARK = ROOT / "19_engineering_baseline" / "build" / "benchmark_report.json"
EVENT_EVIDENCE = ROOT / "21_event_evidence_analysis" / "build" / "reference_verification.json"
EXPERIMENT = ROOT / "22_reproducible_experiments" / "build" / "experiment_report.json"
CORE_QUALITY = ROOT / "23_project_quality_gate" / "build" / "core_quality_report.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    config = load_json(CONFIG)
    benchmark = load_json(BENCHMARK) if BENCHMARK.exists() else {}
    event_evidence = load_json(EVENT_EVIDENCE) if EVENT_EVIDENCE.exists() else {}
    experiment = load_json(EXPERIMENT) if EXPERIMENT.exists() else {}
    core_quality = load_json(CORE_QUALITY) if CORE_QUALITY.exists() else {}
    checks = {
        "tutorial_files_exist": all(path.exists() for path in REQUIRED_DOCS),
        "production_model_is_7b": config["models"]["production_baseline"] == "qwen2.5:7b",
        "smoke_model_is_0_5b": config["models"]["smoke_test"] == "qwen2.5:0.5b",
        "fallback_forbidden": config["acceptance"]["forbid_rule_fallback"] is True,
        "benchmark_exists": BENCHMARK.exists(),
        "engineering_gate_passed": benchmark.get("engineering_gate_passed") is True,
        "event_evidence_exists": EVENT_EVIDENCE.exists(),
        "event_evidence_passed": event_evidence.get("verification", {}).get("passed") is True,
        "experiment_exists": EXPERIMENT.exists(),
        "experiment_passed": experiment.get("quality_gate_passed") is True,
        "core_quality_exists": CORE_QUALITY.exists(),
        "core_quality_passed": core_quality.get("passed") is True,
    }
    checks["passed"] = all(checks.values())
    output = STEP_ROOT / "build" / "tutorial_verification.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if checks["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
