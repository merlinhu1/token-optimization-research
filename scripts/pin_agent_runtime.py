#!/usr/bin/env python3
"""Freeze an agent CLI build so a lane cannot silently run on a different one.

Both agent CLIs are installed as npm symlinks into ``node_modules``. Every lane mounted whatever
build happened to be current, so an auto-update between a baseline and a treatment changed the
measurement apparatus with nothing to show for it. That is what put fourteen Claude Code treatment
comparisons across 2.1.241/2.1.247/2.1.250/2.1.251 -- see
``sources/evaluations/audits/claude-code-runtime-drift-20260902.json``.

This copies the build out of the mutable install into an immutable, content-addressed pin and
records its version and SHA-256 in ``data/evaluation-agent-runtimes.json``. From then on the
runner resolves the pin, verifies the hash before every spending launch, and refuses to run when
it does not match, so drift becomes impossible rather than merely visible.

    python3 scripts/pin_agent_runtime.py --runtime claude-code
    python3 scripts/pin_agent_runtime.py --runtime claude-code --verify-only
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN_ROOT = Path(os.environ.get("TOKEN_EVAL_AGENT_RUNTIME_PIN_ROOT", "/opt/data/tool-candidates/agent-runtimes"))
RUNTIMES_REGISTRY = ROOT / "data/evaluation-agent-runtimes.json"

# Where each runtime's live install lives, and what to copy. A single self-contained executable
# copies as a file; a package whose entrypoint needs its siblings copies as a tree.
SOURCES: dict[str, dict[str, object]] = {
    "claude-code": {
        "executable": Path("/opt/data/.local/bin/claude"),
        "kind": "file",
        "version_command": ["--version"],
    },
    "codex-cli": {
        "executable": Path("/opt/data/.local/bin/codex"),
        "kind": "package",
        "package_root": Path("/opt/data/.local/lib/node_modules/@openai/codex"),
        "entrypoint_relative": Path("bin/codex.js"),
        "version_command": ["--version"],
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    """Hash a package directory as an ordered manifest of its file hashes."""
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(sha256_file(path).encode())
    return digest.hexdigest()


def version_slug(version: str) -> str:
    """Pull the dotted version out of a CLI banner.

    The two CLIs disagree about shape: Claude reports "2.1.258 (Claude Code)" and Codex reports
    "codex-cli 0.147.0", so taking the first token names one pin after its own runtime id.
    """
    for token in version.replace("(", " ").replace(")", " ").split():
        stripped = token.strip("v")
        if stripped and stripped[0].isdigit() and "." in stripped:
            return stripped
    return version.split()[0]


def runtime_version(executable: Path, version_command: list[str]) -> str:
    proc = subprocess.run([str(executable), *version_command], text=True, capture_output=True, timeout=120)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError(f"{executable} did not report a version: {proc.stderr.strip()[:200]}")
    return proc.stdout.strip()


def load_registry() -> dict:
    return json.loads(RUNTIMES_REGISTRY.read_text())


def registry_runtime_entries(registry: dict) -> list[dict]:
    for value in registry.values():
        if isinstance(value, list) and any(isinstance(item, dict) and "runtime_id" in item for item in value):
            return [item for item in value if isinstance(item, dict)]
    return []


def recorded_pin(registry: dict, runtime_id: str) -> dict | None:
    for entry in registry_runtime_entries(registry):
        if entry.get("runtime_id") == runtime_id and isinstance(entry.get("runtime_pin"), dict):
            return entry["runtime_pin"]
    return None


def verify_pin(pin: dict) -> list[str]:
    """Return the reasons a recorded pin is not usable, empty when it verifies."""
    problems: list[str] = []
    entrypoint = Path(str(pin.get("entrypoint", "")))
    if not entrypoint.is_file():
        return [f"pinned entrypoint missing: {entrypoint}"]
    if pin.get("kind") == "package":
        package_root = Path(str(pin.get("package_root", "")))
        if not package_root.is_dir():
            return [f"pinned package root missing: {package_root}"]
        actual = sha256_tree(package_root)
    else:
        actual = sha256_file(entrypoint)
    if actual != pin.get("sha256"):
        problems.append(f"pinned build hash changed: recorded {pin.get('sha256')}, found {actual}")
    return problems


def pin_runtime(runtime_id: str) -> dict:
    source = SOURCES[runtime_id]
    executable = Path(str(source["executable"]))
    if not executable.exists():
        raise FileNotFoundError(f"no installed {runtime_id} to pin at {executable}")
    version = runtime_version(executable, list(source["version_command"]))
    destination = PIN_ROOT / f"{runtime_id}-{version_slug(version)}"
    if source["kind"] == "package":
        package_root = Path(str(source["package_root"]))
        target_root = destination / "package"
        if not target_root.exists():
            shutil.copytree(package_root, target_root, symlinks=True)
        entrypoint = target_root / Path(str(source["entrypoint_relative"]))
        digest = sha256_tree(target_root)
        pin = {"kind": "package", "package_root": str(target_root), "entrypoint": str(entrypoint)}
    else:
        destination.mkdir(parents=True, exist_ok=True)
        entrypoint = destination / executable.name
        if not entrypoint.exists():
            shutil.copy2(executable.resolve(), entrypoint)
            entrypoint.chmod(0o755)
        digest = sha256_file(entrypoint)
        pin = {"kind": "file", "entrypoint": str(entrypoint)}
    pin.update({
        "version": version,
        "sha256": digest,
        "pinned_on": dt.date.today().isoformat(),
        "source_install": str(executable),
        "policy": (
            "Lanes run this pinned build, never the live install. The runner verifies this hash "
            "before every spending launch and refuses to run when it does not match, so an "
            "auto-update cannot change the measurement apparatus mid-study."
        ),
    })
    return pin


def write_pin(runtime_id: str, pin: dict) -> None:
    registry = load_registry()
    updated = False
    for value in registry.values():
        if not isinstance(value, list):
            continue
        for entry in value:
            if isinstance(entry, dict) and entry.get("runtime_id") == runtime_id:
                entry["runtime_pin"] = pin
                updated = True
    if not updated:
        raise KeyError(f"no registry entry with runtime_id {runtime_id}")
    RUNTIMES_REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", action="append", dest="runtimes", choices=sorted(SOURCES),
                        help="runtime to pin; repeat for several, default all")
    parser.add_argument("--verify-only", action="store_true", help="check recorded pins without writing")
    args = parser.parse_args(argv)
    runtimes = args.runtimes or sorted(SOURCES)
    registry = load_registry()
    failures: list[str] = []
    for runtime_id in runtimes:
        if args.verify_only:
            pin = recorded_pin(registry, runtime_id)
            if pin is None:
                failures.append(f"{runtime_id}: no runtime_pin recorded")
                print(f"  {'UNPINNED':<16} {runtime_id}")
                continue
            problems = verify_pin(pin)
            failures.extend(f"{runtime_id}: {p}" for p in problems)
            print(f"  {'ok' if not problems else 'FAILED':<16} {runtime_id:<14} {pin.get('version')}")
            for problem in problems:
                print(f"      {problem}")
            continue
        pin = pin_runtime(runtime_id)
        write_pin(runtime_id, pin)
        registry = load_registry()
        print(f"  pinned {runtime_id:<14} {pin['version']} -> {pin['entrypoint']}")
        print(f"      sha256 {pin['sha256']}")
    if failures:
        print("\n".join(f"  FAIL {item}" for item in failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
