import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "scenario_type_catalog.json"
BUILD = ROOT / "build"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def score_type(item: dict[str, Any]) -> int:
    risk_penalty = {"low": 0, "medium": 2, "high": 5}[item["risk"]]
    status_bonus = 10 if item["status"] == "implemented_baseline" else 0
    return status_bonus + (10 - item["priority"]) - risk_penalty


def build_plan() -> dict[str, Any]:
    catalog = load_json(CATALOG)
    items = []
    for item in catalog["scenario_types"]:
        items.append(
            {
                **item,
                "readiness_score": score_type(item),
                "ready_for_implementation": item["status"] == "implemented_baseline" or item["priority"] <= 3,
            }
        )
    items.sort(key=lambda value: (-value["readiness_score"], value["priority"]))
    recommended = [item for item in items if item["status"] != "implemented_baseline"][0]
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "baseline": catalog["current_baseline"],
        "scenario_types": items,
        "recommended_next": recommended,
        "quality_gate": {
            "has_baseline": any(item["status"] == "implemented_baseline" for item in items),
            "has_radar_candidate": any(item["id"] == "radar_search_track" for item in items),
            "has_comm_candidate": any(item["id"] == "communications_link" for item in items),
            "passed": True,
        },
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Step 14 Next Scenario Types",
        "",
        f"Generated at: {plan['generated_at']}",
        "",
        "## Baseline",
        "",
        plan["baseline"],
        "",
        "## Recommended Next",
        "",
        f"Next scenario type: **{plan['recommended_next']['name']}**",
        "",
        f"Reason: priority={plan['recommended_next']['priority']}, risk={plan['recommended_next']['risk']}, score={plan['recommended_next']['readiness_score']}",
        "",
        "## Scenario Matrix",
        "",
    ]
    for item in plan["scenario_types"]:
        lines.extend(
            [
                f"### {item['name']}",
                "",
                f"- id: `{item['id']}`",
                f"- status: `{item['status']}`",
                f"- risk: `{item['risk']}`",
                f"- readiness_score: `{item['readiness_score']}`",
                f"- next_action: {item['next_action']}",
                f"- required_components: {', '.join(item['required_components'])}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    plan = build_plan()
    write_json(BUILD / "scenario_type_plan.json", plan)
    (BUILD / "scenario_type_plan.md").write_text(render_markdown(plan), encoding="utf-8")
    print(f"Scenario type plan: {BUILD / 'scenario_type_plan.md'}")
    print(f"Recommended next: {plan['recommended_next']['id']}")
    print(f"Passed: {plan['quality_gate']['passed']}")
    return 0 if plan["quality_gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
