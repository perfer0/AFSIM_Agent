import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
AFSIM_DEMOS = Path("D:/AFsim/AFSim/afsim-2.9.0-win64/demos")

SCENARIO_KEYWORDS = {
    "radar": ["radar", "track", "sensor"],
    "communications": ["comm", "network", "message"],
    "weapon": ["weapon", "engage", "shooter", "launcher", "missile"],
    "electronic_warfare": ["jam", "jamming", "electronic", "esm", "rwr"],
    "multi_platform": ["swarm", "iads", "wargame", "outer_air_battle"],
}


def score_file(path: Path, keywords: list[str]) -> int:
    rel = str(path).lower()
    score = sum(3 for keyword in keywords if keyword in rel)
    if score == 0:
        return 0
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:20000].lower()
    except OSError:
        return score
    for keyword in keywords:
        score += len(re.findall(rf"\b{re.escape(keyword)}\b", text))
    return score


def scan() -> dict[str, Any]:
    files = [path for path in AFSIM_DEMOS.rglob("*") if path.is_file() and path.suffix.lower() in {".txt", ".dat", ".afsim"}]
    results = {}
    for scenario_type, keywords in SCENARIO_KEYWORDS.items():
        hits = []
        for path in files:
            score = score_file(path, keywords)
            if score > 0:
                hits.append(
                    {
                        "path": str(path),
                        "relative_to_demos": str(path.relative_to(AFSIM_DEMOS)),
                        "score": score,
                        "bytes": path.stat().st_size,
                    }
                )
        hits.sort(key=lambda item: (-item["score"], item["relative_to_demos"]))
        results[scenario_type] = hits[:10]
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "demos_root": str(AFSIM_DEMOS),
        "demos_root_exists": AFSIM_DEMOS.exists(),
        "results": results,
        "quality_gate": {
            "radar_hits": len(results["radar"]),
            "communications_hits": len(results["communications"]),
            "weapon_hits": len(results["weapon"]),
            "electronic_warfare_hits": len(results["electronic_warfare"]),
            "passed": all(len(results[key]) > 0 for key in ["radar", "communications", "weapon", "electronic_warfare"]),
        },
    }


def render_backlog(report: dict[str, Any]) -> str:
    lines = [
        "# Step 15 Real AFSIM Extension Backlog",
        "",
        f"Generated at: {report['generated_at']}",
        f"AFSIM demos root: `{report['demos_root']}`",
        f"Passed: {report['quality_gate']['passed']}",
        "",
        "## Extension Order",
        "",
        "1. Radar search/track: use radar demos to build a minimal radar component set.",
        "2. Communications link: extract sender/receiver and message routing examples.",
        "3. Weapon engagement: only after radar track generation is stable.",
        "4. Electronic warfare: only after radar and RF snippets are understood.",
        "",
        "## Demo Evidence",
        "",
    ]
    for scenario_type, hits in report["results"].items():
        lines.extend([f"### {scenario_type}", ""])
        for hit in hits[:5]:
            lines.append(f"- score={hit['score']} `{hit['relative_to_demos']}`")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    report = scan()
    (BUILD / "afsim_demo_scan.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (BUILD / "extension_backlog.md").write_text(render_backlog(report), encoding="utf-8")
    print(f"Demo scan: {BUILD / 'afsim_demo_scan.json'}")
    print(f"Backlog: {BUILD / 'extension_backlog.md'}")
    print(f"Passed: {report['quality_gate']['passed']}")
    return 0 if report["quality_gate"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
