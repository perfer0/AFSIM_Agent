import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COMPONENTS = ROOT / "components"
MISSION_EXE = Path("D:/AFsim/AFSim/afsim-2.9.0-win64/bin/mission.exe")
VALID_SIDES = {"blue", "red", "white", "green", "neutral"}
VALID_TIME_UNITS = {"sec", "min", "hr"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_component(kind: str, component_id: str) -> dict:
    path = COMPONENTS / kind / f"{component_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"component not found: {path}")
    return load_json(path)


def load_platform_types(data: dict) -> dict:
    platform_types = {}
    for component_id in data.get("platform_type_refs", []):
        component = load_component("platform_types", component_id)
        platform_types[component_id] = component
    return platform_types


def validate_scenario(data: dict) -> list[str]:
    errors = []
    for field in ["name", "platform_type_refs", "actors", "target_set_refs", "event_pipe", "event_output", "end_time"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    try:
        platform_types = load_platform_types(data)
    except FileNotFoundError as exc:
        errors.append(str(exc))
        platform_types = {}

    for component_id, component in platform_types.items():
        include_path = component.get("include")
        if not include_path:
            errors.append(f"platform_types/{component_id}.include is required")
        elif not Path(include_path).exists():
            errors.append(f"AFSIM include does not exist: {include_path}")
        if not component.get("afsim_type"):
            errors.append(f"platform_types/{component_id}.afsim_type is required")

    for index, actor in enumerate(data.get("actors", [])):
        prefix = f"actors[{index}]"
        validate_platform_like(actor, platform_types, prefix, errors)

    for target_set_ref in data.get("target_set_refs", []):
        try:
            target_set = load_component("target_sets", target_set_ref)
        except FileNotFoundError as exc:
            errors.append(str(exc))
            continue
        platform_type_ref = target_set.get("platform_type_ref")
        if platform_type_ref not in platform_types:
            errors.append(
                f"target_sets/{target_set_ref}.platform_type_ref must be listed in platform_type_refs"
            )
        if target_set.get("side") not in VALID_SIDES:
            errors.append(f"target_sets/{target_set_ref}.side must be one of: {sorted(VALID_SIDES)}")
        for target_index, target in enumerate(target_set.get("targets", [])):
            if not target.get("name"):
                errors.append(f"target_sets/{target_set_ref}.targets[{target_index}].name is required")
            if not target.get("position"):
                errors.append(f"target_sets/{target_set_ref}.targets[{target_index}].position is required")

    event_output = data.get("event_output", {})
    if not event_output.get("file"):
        errors.append("event_output.file is required")
    event_set_ref = event_output.get("event_set_ref")
    if event_set_ref:
        try:
            event_set = load_component("event_outputs", event_set_ref)
            if not isinstance(event_set.get("enabled_events", []), list):
                errors.append(f"event_outputs/{event_set_ref}.enabled_events must be a list")
        except FileNotFoundError as exc:
            errors.append(str(exc))
    else:
        errors.append("event_output.event_set_ref is required")

    if not data.get("event_pipe", {}).get("file"):
        errors.append("event_pipe.file is required")

    end_time = data.get("end_time", {})
    if not isinstance(end_time.get("value"), int):
        errors.append("end_time.value must be an integer")
    if end_time.get("unit") not in VALID_TIME_UNITS:
        errors.append(f"end_time.unit must be one of: {sorted(VALID_TIME_UNITS)}")

    return errors


def validate_platform_like(item: dict, platform_types: dict, prefix: str, errors: list[str]) -> None:
    for field in ["name", "platform_type_ref", "side"]:
        if not item.get(field):
            errors.append(f"{prefix}.{field} is required")
    if item.get("platform_type_ref") not in platform_types:
        errors.append(f"{prefix}.platform_type_ref must be listed in platform_type_refs")
    if item.get("side") not in VALID_SIDES:
        errors.append(f"{prefix}.side must be one of: {sorted(VALID_SIDES)}")
    if not item.get("route") and not item.get("position"):
        errors.append(f"{prefix} must define either route or position")
    for route_index, point in enumerate(item.get("route", [])):
        for field in ["position", "altitude", "speed", "heading"]:
            if not point.get(field):
                errors.append(f"{prefix}.route[{route_index}].{field} is required")
    for execute_index, execute in enumerate(item.get("execute", [])):
        for field in ["time", "script"]:
            if not execute.get(field):
                errors.append(f"{prefix}.execute[{execute_index}].{field} is required")
        if not isinstance(execute.get("relative", False), bool):
            errors.append(f"{prefix}.execute[{execute_index}].relative must be true or false")


def expand_platforms(data: dict, platform_types: dict) -> list[dict]:
    platforms = []
    for actor in data["actors"]:
        platform_type = platform_types[actor["platform_type_ref"]]
        platforms.append({**actor, "type": platform_type["afsim_type"]})

    for target_set_ref in data["target_set_refs"]:
        target_set = load_component("target_sets", target_set_ref)
        platform_type = platform_types[target_set["platform_type_ref"]]
        for target in target_set["targets"]:
            platforms.append(
                {
                    "name": target["name"],
                    "type": platform_type["afsim_type"],
                    "side": target_set["side"],
                    "position": target["position"],
                }
            )
    return platforms


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


def render_scenario_instances(platforms: list[dict]) -> str:
    lines = [
        "# Generated from scenario JSON plus local component library.",
        "# This file contains expanded AFSIM platform instances.",
        "",
    ]
    for platform in platforms:
        lines.extend(render_platform(platform))
        lines.append("")
    return "\n".join(lines)


def render_main(data: dict, platform_types: dict, scenario_filename: str) -> str:
    event_set = load_component("event_outputs", data["event_output"]["event_set_ref"])
    lines = [
        "# Generated AFSIM main file from structured JSON and component library.",
        "",
    ]
    for component_id in data["platform_type_refs"]:
        lines.append(f"include {platform_types[component_id]['include']}")
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
    for event_name in event_set["enabled_events"]:
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
    platform_types = load_platform_types(data)
    platforms = expand_platforms(data, platform_types)
    build_dir = Path(args.build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    scenario_path = build_dir / "scenario_generated.txt"
    main_path = build_dir / "main_generated.txt"
    scenario_path.write_text(render_scenario_instances(platforms), encoding="utf-8")
    main_path.write_text(render_main(data, platform_types, scenario_path.name), encoding="utf-8")
    print(f"Generated: {main_path}")
    print(f"Generated: {scenario_path}")
    print(f"Expanded platforms: {len(platforms)}")
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
    parser = argparse.ArgumentParser(description="Step 03: generate AFSIM scenario from a local component library.")
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
