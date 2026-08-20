#!/usr/bin/env python3
"""Find upstream commits that can become bounded evaluation tasks, and prove they work.

A Lifecycle task is only worth its provider spend if the seeded state genuinely fails and
the repaired state genuinely passes. This miner does not trust a commit's message or its
diffstat for that: it applies the candidate seed, runs the upstream tests that shipped with
the commit, and requires a real failure; then it restores and requires a real pass. A
candidate that cannot demonstrate both is discarded, so nothing reaches the task registry
on the strength of looking plausible.

Selection favours small, closed problems -- one or two production files with the upstream
tests that cover them -- because task size is what lets a sequence hold many tasks without
any single one dominating cost, and a task with a definite failing test has a definite
stopping condition.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FIXTURES = {
    "beets": {
        "repo": ROOT / "sources/evaluations/fixtures/medium/beetbox-beets/repo",
        "production_globs": ("beets/", "beetsplug/"),
        "production_suffix": ".py",
        "test_prefix": "test/",
        "test_command": ["uv", "run", "--offline", "--frozen", "pytest", "-q", "--tb=no"],
        # Already carried by the existing task family; a composite seed must not collide.
        "reserved": {"beets/dbcore/db.py", "beets/util/functemplate.py", "beetsplug/ftintitle.py"},
    },
    "fastify": {
        "repo": ROOT / "sources/evaluations/fixtures/medium/fastify-fastify/repo",
        "production_globs": ("lib/", "fastify.js"),
        "production_suffix": ".js",
        "test_prefix": "test/",
        # borp runs its whole configured glob regardless of file arguments, so candidate
        # validation drives node's own runner, which does honour a single file. The
        # agent-facing suite command is unaffected.
        "test_command": ["node", "--test"],
        "reserved": {"lib/request.js", "lib/errors.js", "lib/content-type.js", "fastify.js"},
    },
}


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr[:400]}")
    return result.stdout


def commit_files(repo: Path, commit: str) -> list[str]:
    return [line for line in git(repo, "show", "--name-only", "--format=", commit).splitlines() if line]


def classify(spec: dict[str, Any], files: list[str]) -> tuple[list[str], list[str]]:
    production, tests = [], []
    for path in files:
        if path.startswith(spec["test_prefix"]):
            tests.append(path)
        elif path.endswith(spec["production_suffix"]) and any(
            path.startswith(prefix) for prefix in spec["production_globs"]
        ):
            production.append(path)
    return production, tests


def candidate_commits(spec: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    repo = spec["repo"]
    found: list[dict[str, Any]] = []
    for commit in git(repo, "log", "--format=%H", f"-n{limit}", "HEAD").split():
        files = commit_files(repo, commit)
        production, tests = classify(spec, files)
        if not (1 <= len(production) <= 2) or not tests or len(files) > 4:
            continue
        if any(path in spec["reserved"] for path in production):
            continue
        found.append({
            "commit": commit,
            "subject": git(repo, "log", "-1", "--format=%s", commit).strip(),
            "production": production,
            "tests": tests,
        })
    return found


def seed_patch(spec: dict[str, Any], candidate: dict[str, Any]) -> str:
    """Reverse only the production half of the commit, leaving upstream tests intact."""
    return git(
        spec["repo"], "diff", candidate["commit"], f"{candidate['commit']}^", "--", *candidate["production"]
    )


def run_tests(spec: dict[str, Any], targets: list[str], timeout: int) -> tuple[int, str]:
    result = subprocess.run(
        [*spec["test_command"], *targets],
        cwd=spec["repo"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, (result.stdout + result.stderr)[-4000:]


def restore(repo: Path) -> None:
    git(repo, "checkout", "--", ".")


def evaluate(spec: dict[str, Any], candidate: dict[str, Any], timeout: int) -> dict[str, Any]:
    """Require a real failure seeded and a real pass repaired, or reject the candidate."""
    repo = spec["repo"]
    patch = seed_patch(spec, candidate)
    verdict: dict[str, Any] = {**candidate, "accepted": False, "reason": None, "seed_characters": len(patch)}
    if not patch.strip():
        verdict["reason"] = "empty production diff"
        return verdict

    applied = subprocess.run(
        ["git", "-C", str(repo), "apply", "-"], input=patch, capture_output=True, text=True
    )
    if applied.returncode != 0:
        verdict["reason"] = "seed does not apply to the pinned snapshot"
        return verdict

    try:
        seeded_code, seeded_output = run_tests(spec, candidate["tests"], timeout)
        verdict["seeded_exit_code"] = seeded_code
        if seeded_code == 0:
            verdict["reason"] = "seeded state still passes; no regression to repair"
            return verdict
        if "error" in seeded_output.lower() and "collected 0" in seeded_output.lower():
            verdict["reason"] = "seeded state fails to collect rather than fails a behaviour"
            return verdict
    except subprocess.TimeoutExpired:
        verdict["reason"] = "seeded test run timed out"
        return verdict
    finally:
        restore(repo)

    try:
        repaired_code, _ = run_tests(spec, candidate["tests"], timeout)
        verdict["repaired_exit_code"] = repaired_code
        if repaired_code != 0:
            verdict["reason"] = "repaired state does not pass; the upstream test is not a clean oracle"
            return verdict
    except subprocess.TimeoutExpired:
        verdict["reason"] = "repaired test run timed out"
        return verdict
    finally:
        restore(repo)

    verdict["accepted"] = True
    verdict["reason"] = "seeded fails, repaired passes"
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("fixture", choices=sorted(FIXTURES))
    parser.add_argument(
        "--production-glob",
        action="append",
        dest="production_globs",
        help=(
            "restrict candidates to production paths under this prefix; repeat to allow several. "
            "Use it to mine a shared code region: tasks drawn from one region amortise the context "
            "an agent reads, where tasks in independent modules each pull in material no other task "
            "needs and the session's accumulated context never converges."
        ),
    )
    parser.add_argument("--scan", type=int, default=200, help="commits of history to consider")
    parser.add_argument("--max-candidates", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)

    spec = FIXTURES[args.fixture]
    if args.production_globs:
        spec = {**spec, "production_globs": tuple(args.production_globs)}
    repo = spec["repo"]
    if git(repo, "status", "--porcelain").strip():
        raise SystemExit(f"{repo} is dirty; refusing to mine against an unpinned tree")

    results: list[dict[str, Any]] = []
    accepted = 0
    for candidate in candidate_commits(spec, args.scan):
        if accepted >= args.max_candidates:
            break
        verdict = evaluate(spec, candidate, args.timeout)
        results.append(verdict)
        accepted += bool(verdict["accepted"])
        flag = "ACCEPT" if verdict["accepted"] else "reject"
        print(f"{flag} {candidate['commit'][:10]} {candidate['subject'][:58]} :: {verdict['reason']}", flush=True)

    if git(repo, "status", "--porcelain").strip():
        raise SystemExit(f"{repo} left dirty after mining; investigate before trusting these results")

    payload = {"fixture": args.fixture, "accepted": accepted, "candidates": results}
    if args.output:
        args.output.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
