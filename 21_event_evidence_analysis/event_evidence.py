import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
HEADER_RE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)\s+([A-Z][A-Z0-9_]+)(?:\s+(.*))?$")
FIELD_PATTERNS = {
    "sensor": re.compile(r"\bSensor:\s+(\S+)"),
    "track_id": re.compile(r"\bTrackId:\s+(\S+)"),
    "detected": re.compile(r"\bDetected:\s+([01])\b"),
    "pd": re.compile(r"\bPd:\s+([0-9.eE+-]+)"),
    "required_pd": re.compile(r"\bRequiredPd:\s+([0-9.eE+-]+)"),
    "range_km": re.compile(r"\bRange:\s+([0-9.eE+-]+)\s+km\b"),
}


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


def parse_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\r\n")
            match = HEADER_RE.match(line)
            if match:
                if current is not None:
                    records.append(enrich_record(current))
                current = {
                    "time_seconds": float(match.group(1)),
                    "event": match.group(2),
                    "body": clean_fragment(match.group(3) or ""),
                }
            elif current is not None and line.strip():
                current["body"] += " " + clean_fragment(line)
    if current is not None:
        records.append(enrich_record(current))
    return records


def clean_fragment(value: str) -> str:
    value = value.strip()
    if value.endswith("\\"):
        value = value[:-1].rstrip()
    return value


def enrich_record(record: dict[str, Any]) -> dict[str, Any]:
    body = record["body"]
    prefix = re.split(r"\b(?:Sensor|Processor|TrackId|Mode|Type):", body, maxsplit=1)[0].strip()
    entities = prefix.split()
    record["observer"] = entities[0] if entities else None
    record["target"] = entities[1] if len(entities) > 1 else None
    for name, pattern in FIELD_PATTERNS.items():
        match = pattern.search(body)
        if not match:
            record[name] = None
        elif name == "detected":
            record[name] = match.group(1) == "1"
        elif name in {"pd", "required_pd", "range_km"}:
            record[name] = float(match.group(1))
        else:
            record[name] = match.group(1)
    record["failure_flags"] = sorted(set(re.findall(r"\b(?:Rcvr|Tgt)_[A-Za-z0-9_]+\b", body)))
    return record


def summarize(path: Path) -> dict[str, Any]:
    records = parse_records(path)
    event_counts = Counter(record["event"] for record in records)
    target_rows: dict[str, dict[str, Any]] = {}
    failure_reasons: Counter[str] = Counter()

    for record in records:
        failure_reasons.update(record["failure_flags"])
        target = record.get("target")
        if not target:
            continue
        row = target_rows.setdefault(
            target,
            {
                "attempts": 0,
                "successful_detections": 0,
                "first_detection_seconds": None,
                "last_detection_seconds": None,
                "tracks_initiated": 0,
                "tracks_dropped": 0,
                "first_track_seconds": None,
                "minimum_range_km": None,
                "maximum_pd": None,
            },
        )
        if record["event"] == "SENSOR_DETECTION_ATTEMPT":
            row["attempts"] += 1
            if record["detected"]:
                row["successful_detections"] += 1
                row["first_detection_seconds"] = row["first_detection_seconds"] or record["time_seconds"]
                row["last_detection_seconds"] = record["time_seconds"]
            if record["range_km"] is not None:
                old = row["minimum_range_km"]
                row["minimum_range_km"] = record["range_km"] if old is None else min(old, record["range_km"])
            if record["pd"] is not None:
                old = row["maximum_pd"]
                row["maximum_pd"] = record["pd"] if old is None else max(old, record["pd"])
        elif record["event"] == "SENSOR_TRACK_INITIATED":
            row["tracks_initiated"] += 1
            row["first_track_seconds"] = row["first_track_seconds"] or record["time_seconds"]
        elif record["event"] == "SENSOR_TRACK_DROPPED":
            row["tracks_dropped"] += 1

    attempts = event_counts["SENSOR_DETECTION_ATTEMPT"]
    successful = sum(row["successful_detections"] for row in target_rows.values())
    attempted_targets = sorted(target for target, row in target_rows.items() if row["attempts"] > 0)
    detected_targets = sorted(target for target, row in target_rows.items() if row["successful_detections"] > 0)
    tracked_targets = sorted(target for target, row in target_rows.items() if row["tracks_initiated"] > 0)
    tracks_initiated = event_counts["SENSOR_TRACK_INITIATED"]
    tracks_dropped = event_counts["SENSOR_TRACK_DROPPED"]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": {
            "path": str(path.resolve()),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        },
        "record_count": len(records),
        "first_event_seconds": records[0]["time_seconds"] if records else None,
        "last_event_seconds": records[-1]["time_seconds"] if records else None,
        "event_counts": dict(sorted(event_counts.items())),
        "metrics": {
            "detection_attempts": attempts,
            "successful_detections": successful,
            "detection_success_rate": round(successful / attempts, 6) if attempts else 0.0,
            "unique_targets_attempted": len(attempted_targets),
            "unique_targets_detected": len(detected_targets),
            "target_detection_coverage": round(len(detected_targets) / len(attempted_targets), 6) if attempted_targets else 0.0,
            "tracks_initiated": tracks_initiated,
            "tracks_dropped": tracks_dropped,
            "open_track_balance": tracks_initiated - tracks_dropped,
            "sensor_turned_on": event_counts["SENSOR_TURNED_ON"],
            "sensor_turned_off": event_counts["SENSOR_TURNED_OFF"],
        },
        "targets": dict(sorted(target_rows.items())),
        "attempted_targets": attempted_targets,
        "detected_targets": detected_targets,
        "tracked_targets": tracked_targets,
        "failure_reasons": dict(sorted(failure_reasons.items())),
    }


def verify(summary: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for event, minimum in profile.get("event_minimums", {}).items():
        actual = summary["event_counts"].get(event, 0)
        checks.append({"check": f"event_minimum:{event}", "expected": minimum, "actual": actual, "passed": actual >= minimum})
    for metric, minimum in profile.get("metric_minimums", {}).items():
        actual = summary["metrics"].get(metric)
        checks.append({"check": f"metric_minimum:{metric}", "expected": minimum, "actual": actual, "passed": actual is not None and actual >= minimum})
    for metric, maximum in profile.get("metric_maximums", {}).items():
        actual = summary["metrics"].get(metric)
        checks.append({"check": f"metric_maximum:{metric}", "expected": maximum, "actual": actual, "passed": actual is not None and actual <= maximum})
    detected = set(summary["detected_targets"])
    for target in profile.get("required_detected_targets", []):
        checks.append({"check": f"target_must_be_detected:{target}", "expected": True, "actual": target in detected, "passed": target in detected})
    for target in profile.get("required_undetected_targets", []):
        checks.append({"check": f"target_must_not_be_detected:{target}", "expected": False, "actual": target in detected, "passed": target not in detected})
    return {
        "profile": profile.get("name"),
        "profile_version": profile.get("version"),
        "checks": checks,
        "passed": bool(checks) and all(check["passed"] for check in checks),
    }


def render_markdown(summary: dict[str, Any], verification: dict[str, Any] | None = None) -> str:
    metrics = summary["metrics"]
    lines = [
        "# AFSIM Event Evidence Report",
        "",
        f"Source: `{summary['source']['path']}`",
        f"SHA-256: `{summary['source']['sha256']}`",
        f"Records: `{summary['record_count']}`",
        "",
        "## Mission Metrics",
        "",
        f"- Detection attempts: `{metrics['detection_attempts']}`",
        f"- Successful detections: `{metrics['successful_detections']}`",
        f"- Detection success rate: `{metrics['detection_success_rate']:.2%}`",
        f"- Targets detected: `{metrics['unique_targets_detected']}/{metrics['unique_targets_attempted']}`",
        f"- Tracks initiated/dropped: `{metrics['tracks_initiated']}/{metrics['tracks_dropped']}`",
        f"- Open track balance: `{metrics['open_track_balance']}`",
        "",
        "## Detected Targets",
        "",
    ]
    lines.extend(f"- `{target}`" for target in summary["detected_targets"])
    if verification is not None:
        lines.extend(["", "## Verification", "", f"Passed: `{'PASS' if verification['passed'] else 'FAIL'}`", ""])
        for check in verification["checks"]:
            lines.append(
                f"- `{'PASS' if check['passed'] else 'FAIL'}` {check['check']}: "
                f"expected `{check['expected']}`, actual `{check['actual']}`"
            )
    lines.extend(["", "## Failure Reasons", ""])
    lines.extend(f"- `{name}`: {count}" for name, count in summary["failure_reasons"].items())
    return "\n".join(lines) + "\n"


def command_analyze(args: argparse.Namespace) -> int:
    summary = summarize(Path(args.event_file))
    write_json(Path(args.output), summary)
    if args.markdown:
        write_text(Path(args.markdown), render_markdown(summary))
    print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    summary = summarize(Path(args.event_file))
    verification = verify(summary, load_json(Path(args.profile)))
    report = {"summary": summary, "verification": verification}
    write_json(Path(args.output), report)
    if args.markdown:
        write_text(Path(args.markdown), render_markdown(summary, verification))
    print(f"Event evidence passed: {verification['passed']}")
    print(f"Report: {Path(args.output).resolve()}")
    return 0 if verification["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 21: parse AFSIM .evt output and verify mission evidence.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("event_file")
    analyze_parser.add_argument("--output", default=str(ROOT / "build" / "event_summary.json"))
    analyze_parser.add_argument("--markdown", default=str(ROOT / "build" / "event_summary.md"))
    analyze_parser.set_defaults(func=command_analyze)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("event_file")
    verify_parser.add_argument("--profile", default=str(ROOT / "profiles" / "eoir_engineering_minimum.json"))
    verify_parser.add_argument("--output", default=str(ROOT / "build" / "event_verification.json"))
    verify_parser.add_argument("--markdown", default=str(ROOT / "build" / "event_verification.md"))
    verify_parser.set_defaults(func=command_verify)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
