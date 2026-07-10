import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def git_log() -> str:
    result = subprocess.run(["git", "log", "--oneline", "-10"], cwd=str(ROOT), text=True, capture_output=True, check=False)
    return result.stdout.strip()


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    capability = read_json(ROOT / "13_capability_review" / "build" / "capability_review.json")
    project = read_json(ROOT / "11_project_integration" / "build" / "project_run_report.json")
    package = read_json(ROOT / "12_offline_packaging" / "build" / "package_verify.json")
    scan = read_json(ROOT / "15_real_afsim_extension" / "build" / "afsim_demo_scan.json")
    model = read_json(ROOT / "16_model_upgrade" / "build" / "model_status.json")
    review = read_json(ROOT / "17_human_review_workflow" / "build" / "human_review_report.json")
    engineering_path = ROOT / "19_engineering_baseline" / "build" / "benchmark_report.json"
    engineering = read_json(engineering_path) if engineering_path.exists() else {}
    event_evidence_path = ROOT / "21_event_evidence_analysis" / "build" / "reference_verification.json"
    event_evidence = read_json(event_evidence_path) if event_evidence_path.exists() else {}
    experiment_path = ROOT / "22_reproducible_experiments" / "build" / "experiment_report.json"
    experiment = read_json(experiment_path) if experiment_path.exists() else {}
    core_quality_path = ROOT / "23_project_quality_gate" / "build" / "core_quality_report.json"
    core_quality = read_json(core_quality_path) if core_quality_path.exists() else {}
    current_production_model = model["production_model"]
    project_report_model = project.get("quality_gates", {}).get("default_model")
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_report_model": project_report_model,
        "current_production_model": current_production_model,
        "project_report_model_matches": project_report_model == current_production_model,
        "project_quality_passed": project["quality_gates"]["passed"] and project_report_model == current_production_model,
        "capability_passed": capability["overall_passed"],
        "capability_count": capability["passed_count"],
        "offline_package_passed": package["passed"],
        "demo_scan_passed": scan["quality_gate"]["passed"],
        "smoke_model_installed": model["smoke_model_installed"],
        "production_model_installed": model["production_model_installed"],
        "engineering_gate_passed": engineering.get("engineering_gate_passed", False),
        "event_evidence_passed": event_evidence.get("verification", {}).get("passed", False),
        "experiment_passed": experiment.get("quality_gate_passed", False),
        "core_quality_passed": core_quality.get("passed", False),
        "human_review_training_passed": review["passed_for_training_demo"],
        "latest_git_log": git_log(),
    }
    summary["overall_training_project_passed"] = all(
        [
            summary["project_quality_passed"],
            summary["capability_passed"],
            summary["offline_package_passed"],
            summary["demo_scan_passed"],
            summary["production_model_installed"],
            summary["engineering_gate_passed"],
            summary["event_evidence_passed"],
            summary["experiment_passed"],
            summary["core_quality_passed"],
            summary["human_review_training_passed"],
        ]
    )
    (BUILD / "final_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md = f"""# Final AFSIM Agent Project Summary

Generated at: {summary['generated_at']}

Overall training project passed: {summary['overall_training_project_passed']}

## Gates

- project_quality_passed: `{summary['project_quality_passed']}`
- project_report_model: `{summary['project_report_model']}`
- current_production_model: `{summary['current_production_model']}`
- project_report_model_matches: `{summary['project_report_model_matches']}`
- capability_passed: `{summary['capability_passed']}`
- capability_count: `{summary['capability_count']}`
- offline_package_passed: `{summary['offline_package_passed']}`
- demo_scan_passed: `{summary['demo_scan_passed']}`
- smoke_model_installed: `{summary['smoke_model_installed']}`
- production_model_installed: `{summary['production_model_installed']}`
- engineering_gate_passed: `{summary['engineering_gate_passed']}`
- event_evidence_passed: `{summary['event_evidence_passed']}`
- experiment_passed: `{summary['experiment_passed']}`
- core_quality_passed: `{summary['core_quality_passed']}`
- human_review_training_passed: `{summary['human_review_training_passed']}`

## Latest Git Log

```text
{summary['latest_git_log']}
```
"""
    (BUILD / "final_summary.md").write_text(md, encoding="utf-8")
    print(f"Final summary: {BUILD / 'final_summary.md'}")
    print(f"Passed: {summary['overall_training_project_passed']}")
    return 0 if summary["overall_training_project_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
