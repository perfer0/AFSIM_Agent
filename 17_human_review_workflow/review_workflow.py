import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
CHECKLIST = STEP_ROOT / "review_checklist.json"
PROJECT_REPORT = ROOT / "11_project_integration" / "build" / "project_run_report.json"
CAPABILITY_REVIEW = ROOT / "13_capability_review" / "build" / "capability_review.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    checklist = load_json(CHECKLIST)
    project_report = load_json(PROJECT_REPORT)
    capability = load_json(CAPABILITY_REVIEW)
    review = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "checklist": checklist,
        "automatic_evidence": {
            "project_quality_passed": project_report.get("quality_gates", {}).get("passed"),
            "draft_provider": project_report.get("audit", {}).get("draft_provider"),
            "run_exit_code": project_report.get("audit", {}).get("run_exit_code"),
            "capability_overall_passed": capability.get("overall_passed"),
        },
        "human_decision_required": [
            "确认想定军事/业务意图是否符合需求",
            "确认平台、传感器、目标和事件输出是否符合真实建模口径",
            "确认参数是否可以用于更复杂场景扩展",
        ],
    }
    review["passed_for_training_demo"] = (
        review["automatic_evidence"]["project_quality_passed"] is True
        and review["automatic_evidence"]["draft_provider"] in {"ollama", "ollama_repair"}
        and review["automatic_evidence"]["run_exit_code"] == 0
        and review["automatic_evidence"]["capability_overall_passed"] is True
    )
    (BUILD / "human_review_report.json").write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Step 17 Human Review Workflow",
        "",
        f"Generated at: {review['generated_at']}",
        f"Passed for training demo: {review['passed_for_training_demo']}",
        "",
        "## Automatic Evidence",
        "",
    ]
    for key, value in review["automatic_evidence"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Human Decision Required", ""])
    for item in review["human_decision_required"]:
        lines.append(f"- {item}")
    (BUILD / "human_review_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Human review report: {BUILD / 'human_review_report.md'}")
    print(f"Passed: {review['passed_for_training_demo']}")
    return 0 if review["passed_for_training_demo"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
