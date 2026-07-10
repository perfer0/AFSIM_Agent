import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
SPEC_PATH = STEP_ROOT / "experiment_spec.json"
AGENT_DIR = PROJECT_ROOT / "07_agent_loop"
EVIDENCE_DIR = PROJECT_ROOT / "21_event_evidence_analysis"
sys.path.insert(0, str(AGENT_DIR))
sys.path.insert(0, str(EVIDENCE_DIR))

import afsim_ai
import event_evidence


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def build_scenario(altitude_ft: int, seed: int, run_id: str) -> dict[str, Any]:
    scenario = afsim_ai.local_rule_draft()
    scenario["name"] = run_id
    scenario["description"] = "Deterministic EOIR altitude and random-seed experiment."
    scenario["actors"][0]["route"][0]["altitude"] = f"{altitude_ft} ft"
    scenario["event_pipe"]["file"] = f"output/{run_id}.aer"
    scenario["event_output"]["file"] = f"output/{run_id}.evt"
    scenario["random_seed"] = seed
    scenario["draft_provider"] = "deterministic_experiment"
    return scenario


def first_detection_seconds(summary: dict[str, Any]) -> float | None:
    values = [
        row["first_detection_seconds"]
        for row in summary["targets"].values()
        if row["first_detection_seconds"] is not None
    ]
    return min(values) if values else None


def run_one(altitude_ft: int, seed: int) -> dict[str, Any]:
    run_id = f"altitude_{altitude_ft}_seed_{seed}"
    run_dir = BUILD / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    scenario = build_scenario(altitude_ft, seed, run_id)
    errors = afsim_ai.validate_scenario(scenario)
    if errors:
        return {"run_id": run_id, "altitude_ft": altitude_ft, "seed": seed, "validation_errors": errors, "passed": False}

    platform_types = afsim_ai.load_platform_types(scenario)
    platforms = afsim_ai.expand_platforms(scenario, platform_types)
    scenario_txt = run_dir / "scenario_generated.txt"
    main_txt = run_dir / "main_generated.txt"
    scenario_json = run_dir / "scenario.json"
    write_json(scenario_json, scenario)
    write_text(scenario_txt, afsim_ai.render_scenario_instances(platforms))
    write_text(main_txt, afsim_ai.render_main(scenario, platform_types, scenario_txt.name))
    (run_dir / "output").mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [str(afsim_ai.MISSION_EXE), str(main_txt)],
        cwd=str(run_dir),
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )
    write_text(run_dir / "mission_stdout.log", result.stdout)
    write_text(run_dir / "mission_stderr.log", result.stderr)
    event_file = run_dir / scenario["event_output"]["file"]
    summary = event_evidence.summarize(event_file) if result.returncode == 0 and event_file.exists() else None
    if summary:
        write_json(run_dir / "event_summary.json", summary)
    metrics = summary["metrics"] if summary else {}
    record = {
        "run_id": run_id,
        "altitude_ft": altitude_ft,
        "seed": seed,
        "mission_exit_code": result.returncode,
        "event_file_exists": event_file.exists(),
        "successful_detections": metrics.get("successful_detections"),
        "detection_success_rate": metrics.get("detection_success_rate"),
        "unique_targets_detected": metrics.get("unique_targets_detected"),
        "tracks_initiated": metrics.get("tracks_initiated"),
        "first_detection_seconds": first_detection_seconds(summary) if summary else None,
        "hashes": {
            "scenario_json": sha256_file(scenario_json),
            "main_txt": sha256_file(main_txt),
            "event_file": sha256_file(event_file) if event_file.exists() else None,
        },
        "passed": result.returncode == 0 and summary is not None,
    }
    write_json(run_dir / "run_result.json", record)
    return record


def aggregate(records: list[dict[str, Any]], spec: dict[str, Any]) -> list[dict[str, Any]]:
    groups = []
    for altitude in spec["factor"]["values"]:
        rows = [row for row in records if row["altitude_ft"] == altitude and row["passed"]]
        group: dict[str, Any] = {"altitude_ft": altitude, "runs": len(rows)}
        for metric in spec["metrics"]:
            values = [float(row[metric]) for row in rows if row.get(metric) is not None]
            group[metric] = {
                "mean": round(statistics.mean(values), 6) if values else None,
                "sample_stdev": round(statistics.stdev(values), 6) if len(values) > 1 else 0.0 if values else None,
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
            }
        groups.append(group)
    return groups


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# EOIR Altitude Experiment Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Question: {report['spec']['question']}",
        f"Hypothesis: {report['spec']['hypothesis']}",
        f"Quality gate: `{'PASS' if report['quality_gate_passed'] else 'FAIL'}`",
        f"Seed variation observed: `{report['seed_variation_observed']}`",
        "",
        "| Altitude (ft) | Runs | Mean detections | Mean success rate | Mean targets | Mean first detection (s) |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for group in report["aggregates"]:
        lines.append(
            f"| {group['altitude_ft']} | {group['runs']} | "
            f"{group['successful_detections']['mean']} | "
            f"{group['detection_success_rate']['mean']:.2%} | "
            f"{group['unique_targets_detected']['mean']} | "
            f"{group['first_detection_seconds']['mean']} |"
        )
    lines.extend([
        "",
        "## Interpretation Boundary",
        "",
        "This sweep demonstrates a reproducible controlled experiment. Three seeds per altitude are enough for learning the workflow, not enough for a high-confidence operational conclusion. Increase repetitions and justify the statistical method before using results for decisions.",
        "",
        "All three seeds produced identical metrics at each altitude in this run. The likely explanation is that the selected EOIR path is deterministic under these conditions. Setting a seed controls stochastic behavior; it does not guarantee that the chosen model contains randomness.",
        "",
    ])
    return "\n".join(lines)


def command_run(_: argparse.Namespace) -> int:
    spec = load_json(SPEC_PATH)
    records = []
    for altitude in spec["factor"]["values"]:
        for seed in spec["random_seeds"]:
            print(f"Running altitude={altitude} ft, seed={seed}...", flush=True)
            records.append(run_one(altitude, seed))
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "environment": {
            "git_commit": git_commit(),
            "python": platform.python_version(),
            "mission_exe": str(afsim_ai.MISSION_EXE),
            "mission_exe_sha256": sha256_file(afsim_ai.MISSION_EXE),
            "experiment_spec_sha256": sha256_file(SPEC_PATH),
        },
        "spec": spec,
        "run_count": len(records),
        "passed_run_count": sum(record["passed"] for record in records),
        "records": records,
        "aggregates": aggregate(records, spec),
    }
    report["seed_variation_observed"] = any(
        metric["sample_stdev"] not in {None, 0.0}
        for group in report["aggregates"]
        for name, metric in group.items()
        if name not in {"altitude_ft", "runs"}
    )
    report["quality_gate_passed"] = report["run_count"] == 9 and report["passed_run_count"] == report["run_count"]
    write_json(BUILD / "experiment_report.json", report)
    write_text(BUILD / "experiment_report.md", render_report(report))
    print(f"Report: {BUILD / 'experiment_report.md'}")
    print(f"Quality gate passed: {report['quality_gate_passed']}")
    return 0 if report["quality_gate_passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 22: reproducible AFSIM parameter experiment.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(func=command_run)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
