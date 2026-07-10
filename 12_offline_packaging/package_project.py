import argparse
import hashlib
import json
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STEP_ROOT = Path(__file__).resolve().parent
BUILD = STEP_ROOT / "build"
PROJECT_MANIFEST = ROOT / "11_project_integration" / "project_manifest.json"
PROJECT_REPORT = ROOT / "11_project_integration" / "build" / "project_run_report.json"
EXCLUDED_PREFIXES = (
    "ollama/models/",
    "12_offline_packaging/build/",
    ".git/",
)
EXCLUDED_SUFFIXES = (
    ".aer",
    ".evt",
    ".pyc",
    ".log",
)


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=False)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_files() -> list[str]:
    tracked = run(["git", "ls-files"])
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"])
    if tracked.returncode != 0:
        raise RuntimeError(tracked.stderr.strip())
    if untracked.returncode != 0:
        raise RuntimeError(untracked.stderr.strip())
    files = set()
    for raw in (tracked.stdout + "\n" + untracked.stdout).splitlines():
        if not raw.strip():
            continue
        normalized = raw.replace("\\", "/")
        if should_include(normalized) and (ROOT / normalized).is_file():
            files.add(normalized)
    return sorted(files)


def should_include(path: str) -> bool:
    if any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    if any(path.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return False
    return True


def build_package() -> dict[str, Any]:
    BUILD.mkdir(parents=True, exist_ok=True)
    files = tracked_files()
    archive_name = f"AFSIM_Agent_offline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    archive_path = BUILD / archive_name
    checksums = []
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            absolute = ROOT / relative
            archive.write(absolute, arcname=f"AFSIM_Agent/{relative}")
            checksums.append(
                {
                    "path": relative,
                    "bytes": absolute.stat().st_size,
                    "sha256": sha256_file(absolute),
                }
            )
        archive.writestr("AFSIM_Agent/OFFLINE_RESTORE.md", restore_guide())

    package_manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "archive": str(archive_path),
        "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": sha256_file(archive_path),
        "source_commit": run(["git", "rev-parse", "HEAD"]).stdout.strip(),
        "file_count": len(files),
        "excluded": {
            "prefixes": list(EXCLUDED_PREFIXES),
            "suffixes": list(EXCLUDED_SUFFIXES),
            "note": "Ollama model blobs and generated simulation outputs are intentionally excluded.",
        },
        "project_manifest": load_json(PROJECT_MANIFEST) if PROJECT_MANIFEST.exists() else {},
        "latest_project_report": load_json(PROJECT_REPORT) if PROJECT_REPORT.exists() else {},
        "checksums_path": str(BUILD / "package_checksums.json"),
    }
    write_json(BUILD / "package_manifest.json", package_manifest)
    write_json(BUILD / "package_checksums.json", {"files": checksums})
    return package_manifest


def restore_guide() -> str:
    return """# AFSIM Agent Offline Restore Guide

This archive contains the project code, teaching steps, prompts, manifests, and validation reports.

It intentionally does not contain:

- Ollama model blobs under `ollama/models/`
- AFSIM installer or binaries
- Generated `.aer`, `.evt`, `.log`, or Python cache files

Expected local paths after restore:

```text
D:\\AFsim\\Agent
D:\\AFsim\\Agent\\ollama\\models
D:\\AFsim\\AFSim\\afsim-2.9.0-win64\\bin\\mission.exe
```

After copying the project back to `D:\\AFsim\\Agent`, verify:

```powershell
$env:OLLAMA_MODELS='D:\\AFsim\\Agent\\ollama\\models'
cd D:\\AFsim\\Agent\\11_project_integration
python .\\afsim_project.py status
python .\\afsim_project.py run .\\requests\\integrated_eoir_request.txt
python .\\afsim_project.py report
```

Success requires:

```text
draft_provider = ollama
run_exit_code = 0
quality_gates.passed = true
```
"""


def verify_package(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    archive_path = Path(manifest["archive"])
    bad_entries = []
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        for name in names:
            normalized = name.replace("\\", "/")
            if "ollama/models/" in normalized or normalized.endswith(EXCLUDED_SUFFIXES):
                bad_entries.append(normalized)
    result = {
        "archive": str(archive_path),
        "exists": archive_path.exists(),
        "sha256_matches": sha256_file(archive_path) == manifest["archive_sha256"],
        "bad_entries": bad_entries,
        "passed": archive_path.exists() and not bad_entries and sha256_file(archive_path) == manifest["archive_sha256"],
    }
    write_json(BUILD / "package_verify.json", result)
    return result


def command_build(_: argparse.Namespace) -> int:
    manifest = build_package()
    print(f"Package: {manifest['archive']}")
    print(f"Files: {manifest['file_count']}")
    print(f"SHA256: {manifest['archive_sha256']}")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    result = verify_package(Path(args.manifest))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Step 12: build an offline project package.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser_ = subparsers.add_parser("build")
    build_parser_.set_defaults(func=command_build)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("manifest", nargs="?", default=str(BUILD / "package_manifest.json"))
    verify_parser.set_defaults(func=command_verify)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
