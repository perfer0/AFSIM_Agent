import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MISSION_EXE = Path("D:/AFsim/AFSim/afsim-2.9.0-win64/bin/mission.exe")
VALID_SIDES = {"blue", "red", "white", "green", "neutral"}
VALID_TIME_UNITS = {"sec", "min", "hr"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_scenario(data: dict) -> list[str]:
    errors = []
    required = [
        "name",
        "platform_type_includes",
        "platforms",
        "event_pipe",
        "event_output",
        "end_time",
    ]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    for include_path in data.get("platform_type_includes", []):
        if not Path(include_path).exists():
            errors.append(f"platform type include does not exist: {include_path}")

    platforms = data.get("platforms", [])
    if not isinstance(platforms, list) or not platforms:
        errors.append("platforms must be a non-empty list")
    for index, platform in enumerate(platforms):
        prefix = f"platforms[{index}]"
        for field in ["name", "type", "side"]:
            if not platform.get(field):
                errors.append(f"{prefix}.{field} is required")
        if platform.get("side") not in VALID_SIDES:
            errors.append(f"{prefix}.side must be one of: {sorted(VALID_SIDES)}")

        has_route = bool(platform.get("route"))
        has_position = bool(platform.get("position"))
        if not has_route and not has_position:
            errors.append(f"{prefix} must define either route or position")

        if has_route:
            route = platform.get("route")
            if not isinstance(route, list) or not route:
                errors.append(f"{prefix}.route must be a non-empty list")
            else:
                for route_index, point in enumerate(route):
                    route_prefix = f"{prefix}.route[{route_index}]"
                    for field in ["position", "altitude", "speed", "heading"]:
                        if not point.get(field):
                            errors.append(f"{route_prefix}.{field} is required")

        for execute_index, execute in enumerate(platform.get("execute", [])):
            execute_prefix = f"{prefix}.execute[{execute_index}]"
            for field in ["time", "script"]:
                if not execute.get(field):
                    errors.append(f"{execute_prefix}.{field} is required")
            if not isinstance(execute.get("relative", False), bool):
                errors.append(f"{execute_prefix}.relative must be true or false")

    end_time = data.get("end_time", {})
    if not isinstance(end_time.get("value"), int):
        errors.append("end_time.value must be an integer")
    if end_time.get("unit") not in VALID_TIME_UNITS:
        errors.append(f"end_time.unit must be one of: {sorted(VALID_TIME_UNITS)}")

    event_pipe = data.get("event_pipe", {})
    if not event_pipe.get("file"):
        errors.append("event_pipe.file is required")

    event_output = data.get("event_output", {})
    if not event_output.get("file"):
        errors.append("event_output.file is required")
    if not isinstance(event_output.get("enabled_events", []), list):
        errors.append("event_output.enabled_events must be a list")

    return errors


def render_platform(platform: dict) -> list[str]:
    lines = [f"platform {platform['name']} {platform['type']}", f"   side {platform['side']}"]

    if platform.get("route"):
        lines.append("")
        lines.append("   route")
        for point in platform["route"]:
            lines.append(
                "      position "
                f"{point['position']} "
                f"altitude {point['altitude']} "
                f"speed {point['speed']} "
                f"heading {point['heading']}"
            )
        lines.append("   end_route")

    if platform.get("position"):
        lines.append(f"   position {platform['position']}")

    for execute in platform.get("execute", []):
        relative = " relative" if execute.get("relative", False) else ""
        lines.append("")
        lines.append(f"   execute at_time {execute['time']}{relative}")
        lines.append(f"      {execute['script']}")
        lines.append("   end_execute")

    lines.append("end_platform")
    return lines


def render_scenario_instances(data: dict) -> str:
    lines = [
        "# Generated platform instances from structured JSON.",
        "# This file contains platform objects, routes, positions, and execute actions.",
        "",
    ]
    for platform in data["platforms"]:
        lines.extend(render_platform(platform))
        lines.append("")
    return "\n".join(lines)


def render_main(data: dict, scenario_filename: str) -> str:
    lines = [
        "# Generated AFSIM main file from structured JSON.",
        "# This file includes platform types and the generated platform instance file.",
        "",
    ]
    for include_path in data["platform_type_includes"]:
        lines.append(f"include {include_path}")

    lines.extend(
        [
            f"include {scenario_filename}",
            "",
            "event_pipe",
            f"   file {data['event_pipe']['file']}",
            "end_event_pipe",
            "",
            "event_output",
            f"   file {data['event_output']['file']}",
        ]
    )
    for event_name in data["event_output"].get("enabled_events", []):
        lines.append(f"   enable {event_name}")

    lines.extend(
        [
            "end_event_output",
            "",
            f"end_time {data['end_time']['value']} {data['end_time']['unit']}",
            "",
        ]
    )
    return "\n".join(lines)


def command_validate(args: argparse.Namespace) -> int:
    data = load_json(Path(args.scenario_json))
    errors = validate_scenario(data)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Validation passed.")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    data = load_json(Path(args.scenario_json))
    errors = validate_scenario(data)
    if errors:
        print("Cannot generate because validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    build_dir = Path(args.build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    scenario_path = build_dir / "scenario_generated.txt"
    main_path = build_dir / "main_generated.txt"

    scenario_path.write_text(render_scenario_instances(data), encoding="utf-8")
    main_path.write_text(render_main(data, scenario_path.name), encoding="utf-8")
    print(f"Generated: {main_path}")
    print(f"Generated: {scenario_path}")
    return 0


def command_run(args: argparse.Namespace) -> int:
    main_path = Path(args.main_txt).resolve()
    if not main_path.exists():
        print(f"AFSIM main file does not exist: {main_path}")
        return 1
    if not MISSION_EXE.exists():
        print(f"mission.exe not found: {MISSION_EXE}")
        return 1

    main_path.parent.joinpath("output").mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [str(MISSION_EXE), str(main_path)],
        cwd=str(main_path.parent),
        text=True,
        capture_output=True,
        check=False,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print(f"mission.exe exit code: {result.returncode}")
    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Step 02: generate AFSIM platform instances from JSON."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("scenario_json")
    validate_parser.set_defaults(func=command_validate)

    generate_parser = subparsers.add_parser("generate")
    generate_parser.add_argument("scenario_json")
    generate_parser.add_argument("--build-dir", default=str(ROOT / "build"))
    generate_parser.set_defaults(func=command_generate)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("main_txt")
    run_parser.set_defaults(func=command_run)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
