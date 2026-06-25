#!/usr/bin/env python3
"""Run planned Codex fixture evaluations and summarize results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_codex_fixture_evaluation.py"


def rel_or_abs(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def run_dir_for(record: dict[str, Any]) -> Path:
    root = record.get("artifacts", {}).get("root") or f"sources/evaluations/runs/{record['evaluation_id']}"
    return rel_or_abs(Path(root))


def existing_summary(record: dict[str, Any]) -> dict[str, Any] | None:
    path = run_dir_for(record) / "runner-summary.json"
    if not path.exists():
        return None
    try:
        return load(path)
    except json.JSONDecodeError:
        return None


def evaluation_protocol(record: dict[str, Any]) -> dict[str, Any]:
    protocol = record.get("evaluation_protocol") or record.get("protocol") or {}
    return protocol if isinstance(protocol, dict) else {}


def profile_id(record: dict[str, Any]) -> str:
    return record.get("profile", {}).get("profile_id") or record.get("setup", {}).get("tool_permissions", {}).get("profile_id") or "unknown"


def is_calibration(record: dict[str, Any]) -> bool:
    return bool(evaluation_protocol(record).get("calibration_only"))


def run_record(
    path: Path,
    timeout: int,
    *,
    execution_backend: str,
    allow_host_eval: bool,
    docker_image: str,
    dockerfile: Path,
    build_docker_image: bool,
    tool_state: str | None,
    tool_use_policy: str | None,
) -> dict[str, Any]:
    start = time.time()
    cmd = [sys.executable, str(RUNNER), str(path), "--timeout", str(timeout), "--execution-backend", execution_backend, "--docker-image", docker_image, "--dockerfile", str(dockerfile)]
    if build_docker_image:
        cmd.append("--build-docker-image")
    if allow_host_eval:
        cmd.append("--allow-host-eval")
    if tool_state:
        cmd.extend(["--tool-state", tool_state])
    if tool_use_policy:
        cmd.extend(["--tool-use-policy", tool_use_policy])
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout + 1800,
    )
    elapsed = time.time() - start
    output = proc.stdout or ""
    parsed: dict[str, Any] | None = None
    # Runner prints a JSON object at the end. Parse the last JSON object conservatively.
    for idx in range(len(output)):
        if output[idx] != "{":
            continue
        try:
            candidate = json.loads(output[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict):
            parsed = candidate
    return {
        "planned_run": str(path.relative_to(ROOT)),
        "exit_code": proc.returncode,
        "elapsed_seconds": round(elapsed, 2),
        "runner_output": output[-4000:],
        "summary": parsed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("planned_runs", nargs="*", type=Path)
    parser.add_argument("--glob", default="sources/evaluations/large-projects/*/runs/planned/*.json")
    parser.add_argument("--output", type=Path, default=ROOT / "sources/evaluations/large-projects/batch-summary.json")
    parser.add_argument("--timeout", type=int, default=2700)
    parser.add_argument("--skip-accepted", action="store_true", default=True)
    parser.add_argument("--no-skip-accepted", dest="skip_accepted", action="store_false")
    parser.add_argument("--execution-backend", choices=["docker", "host"], default="docker")
    parser.add_argument("--allow-host-eval", action="store_true", help="permit non-containerized execution; evidence is not container-grade")
    parser.add_argument("--docker-image", default="token-eval-codex:latest")
    parser.add_argument("--dockerfile", type=Path, default=ROOT / "sources/evaluations/large-projects/container/Dockerfile")
    parser.add_argument("--build-docker-image", action="store_true", help="build --docker-image from --dockerfile before Docker preflight")
    parser.add_argument("--tool-state", choices=["none", "cold", "warm-index"], help="override protocol tool-state for every planned run in this batch")
    parser.add_argument("--tool-use-policy", choices=["none", "preferred", "optional"], help="override treatment guidance policy for every planned run in this batch")
    parser.add_argument("--include-calibration", action="store_true", help="include calibration-only lanes; skipped by default to control cost")
    parser.add_argument("--calibration-limit-per-profile", type=int, default=0, help="when including calibration lanes, cap runs per profile; 0 means no cap")
    args = parser.parse_args(argv)

    planned = [rel_or_abs(p) for p in args.planned_runs]
    if not planned:
        planned = sorted(ROOT.glob(args.glob))

    results: list[dict[str, Any]] = []
    calibration_seen: dict[str, int] = {}
    for path in planned:
        record = load(path)
        pid = profile_id(record)
        if is_calibration(record):
            if not args.include_calibration:
                results.append({
                    "planned_run": str(path.relative_to(ROOT)),
                    "skipped": "calibration-only; pass --include-calibration to run",
                    "profile_id": pid,
                })
                print(f"SKIP calibration {path.relative_to(ROOT)}", flush=True)
                continue
            calibration_seen[pid] = calibration_seen.get(pid, 0) + 1
            if args.calibration_limit_per_profile and calibration_seen[pid] > args.calibration_limit_per_profile:
                results.append({
                    "planned_run": str(path.relative_to(ROOT)),
                    "skipped": f"calibration limit per profile reached ({args.calibration_limit_per_profile})",
                    "profile_id": pid,
                })
                print(f"SKIP calibration-limit {path.relative_to(ROOT)}", flush=True)
                continue
        existing = existing_summary(record)
        if args.skip_accepted and existing and existing.get("accepted") is True:
            results.append({
                "planned_run": str(path.relative_to(ROOT)),
                "skipped": "already accepted",
                "summary": existing,
            })
            print(f"SKIP accepted {path.relative_to(ROOT)}", flush=True)
            continue
        print(f"RUN {path.relative_to(ROOT)}", flush=True)
        result = run_record(
            path,
            args.timeout,
            execution_backend=args.execution_backend,
            allow_host_eval=args.allow_host_eval,
            docker_image=args.docker_image,
            dockerfile=args.dockerfile if args.dockerfile.is_absolute() else ROOT / args.dockerfile,
            build_docker_image=args.build_docker_image,
            tool_state=args.tool_state,
            tool_use_policy=args.tool_use_policy,
        )
        results.append(result)
        print(json.dumps({k: result[k] for k in ("planned_run", "exit_code", "elapsed_seconds")}, indent=2), flush=True)

    accepted = sum(1 for r in results if (r.get("summary") or {}).get("accepted") is True)
    skipped = sum(1 for r in results if r.get("skipped"))
    failed = sum(1 for r in results if not r.get("skipped") and not (r.get("summary") or {}).get("accepted") is True)
    summary = {
        "planned_count": len(planned),
        "result_count": len(results),
        "accepted_count": accepted,
        "skipped_count": skipped,
        "failed_or_incomplete_count": failed,
        "results": results,
    }
    output = rel_or_abs(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("planned_count", "accepted_count", "skipped_count", "failed_or_incomplete_count")}, indent=2))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
