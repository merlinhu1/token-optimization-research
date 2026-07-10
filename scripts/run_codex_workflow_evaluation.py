#!/usr/bin/env python3
"""Run Codex continuous workflow-sequence evaluations.

The runner evaluates one profile on one active workflow sequence from
``data/workflow-task-sequences.json``. Unlike the early ad-hoc workflow runner,
tasks are fed to the same Codex session one at a time via ``codex exec resume``;
future task prompts are not visible to the model until the previous task verifier
has passed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import extract_codex_usage  # type: ignore
import run_codex_fixture_evaluation as fixture  # type: ignore

DEFAULT_DOCKER_IMAGE = "token-eval-codex:latest"
DEFAULT_SOURCE_CODEX_HOME = Path(os.environ.get("CODEX_HOME", "/opt/data/home/.codex"))
DATE = dt.datetime.now(dt.UTC).date().isoformat()
COMPACT_ARTIFACT_NAMES = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}

PROJECT_META: dict[str, dict[str, str]] = {
    "large-django-django": {
        "project_id": "django-django",
        "dependency_command": "python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e .",
    },
    "large-hashicorp-terraform": {
        "project_id": "hashicorp-terraform",
        "dependency_command": "export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH; go env GOMODCACHE >/dev/null",
    },
    "medium-psf-requests": {
        "project_id": "psf-requests",
        "dependency_command": "python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e . 'pytest<9' pytest-httpbin==2.1.0 'httpbin~=0.10.0' pytest-cov pytest-mock pytest-xdist trustme PySocks",
    },
    "medium-pallets-flask": {
        "project_id": "pallets-flask",
        "dependency_command": "python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e . 'pytest<9' asgiref python-dotenv",
    },
    "large-orchardcms-orchardcore": {
        "project_id": "orchardcms-orchardcore",
        "dependency_command": "DOTNET_ROOT=/opt/data/dotnet; export DOTNET_ROOT PATH=\"$DOTNET_ROOT:$PATH\" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1; dotnet restore test/OrchardCore.Tests/OrchardCore.Tests.csproj >/dev/null",
    },
    "medium-fastify-fastify": {
        "project_id": "fastify-fastify",
        "dependency_command": "npm install --ignore-scripts --no-audit --no-fund",
    },
    "medium-beetbox-beets": {
        "project_id": "beetbox-beets",
        "dependency_command": "uv sync --group test",
    },
}

SUPPORTED_WORKFLOW_TOOL_PROFILES = {
    "retrieval-leanctx": "lean-ctx",
    "retrieval-codegraph": "codegraph",
    "lower-intervention-codegraph": "codegraph",
    "retrieval-serena": "serena",
    "retrieval-graphify": "graphify",
    "retrieval-sigmap": "sigmap",
    "retrieval-jcodemunch-mcp": "jcodemunch-mcp",
    "integrated-token-savior": "token-savior",
    "headroom-default-codex": "headroom",
    "terminal-rtk": "rtk",
    "terminal-snip": "snip",
    "terminal-lowfat": "lowfat",
    "terminal-tokenjuice": "tokenjuice",
    "behavior-caveman": "caveman",
    "artifact-ponytail": "ponytail",
}


def build_profile_meta() -> dict[str, dict[str, Any]]:
    catalog_path = ROOT / "data/evaluation-profiles.json"
    catalog = json.loads(catalog_path.read_text())
    canonical = {profile["id"]: profile for profile in catalog.get("profiles", [])}
    supported = {"baseline-bare-codex": None, **SUPPORTED_WORKFLOW_TOOL_PROFILES}
    profiles: dict[str, dict[str, Any]] = {}
    for profile_id, tool_id in supported.items():
        source = canonical.get(profile_id)
        if source is None:
            raise KeyError(f"workflow profile {profile_id} is missing from {catalog_path}")
        cfg = fixture.TOOL_CONFIGS[str(tool_id)] if tool_id else None
        protocol = source.get("evaluation_protocol") or {}
        profile_type = str(source["profile_type"])
        profiles[profile_id] = {
            "session_role": (
                "baseline"
                if profile_type == "control"
                else "stack_treatment"
                if profile_type == "stack"
                else "individual_tool_treatment"
            ),
            "profile_type": profile_type,
            "component_ids": [str(component["component_id"]) for component in source.get("components", [])],
            "enabled_surfaces": [str(surface) for surface in source.get("enabled_surfaces", [])],
            "disabled_overlaps": [str(surface) for surface in source.get("disabled_overlaps", [])],
            "allowed_terms": sorted({str(tool_id), *[str(term) for term in (cfg or {}).get("allowed_terms", [])]}) if tool_id else [],
            "tool_state": str(protocol.get("tool_state", (cfg or {}).get("default_tool_state", "none"))),
            "tool_use_policy": str(protocol.get("tool_use_policy", "optional" if tool_id else "none")),
            "tool_id": tool_id,
        }
    return profiles


PROFILE_META: dict[str, dict[str, Any]] = build_profile_meta()

DEFAULT_WORKFLOW_MODEL_CONDITION_ID = "codex-openai-gpt-5-6-terra-medium"
DEFAULT_WORKFLOW_MODEL = "gpt-5.6-terra"
DEFAULT_WORKFLOW_REASONING_EFFORT = "medium"

LEAKY_PROMPT_LINE_PATTERNS = [
    re.compile(r"^Issue source:.*$", re.IGNORECASE),
    re.compile(r"^The repository has already been checked out.*$", re.IGNORECASE),
    re.compile(r"^This task follows a SWE-bench-style flow:.*$", re.IGNORECASE),
    re.compile(r".*pinned fixed upstream commit.*", re.IGNORECASE),
    re.compile(r".*seeded with a regression.*", re.IGNORECASE),
    re.compile(r".*removes? the relevant production fix.*", re.IGNORECASE),
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run(
    cmd: list[str],
    *,
    cwd: Path,
    stdout: Path | None = None,
    timeout: int = 900,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if stdout:
        stdout.parent.mkdir(parents=True, exist_ok=True)
        with stdout.open("w") as out:
            return subprocess.run(cmd, cwd=cwd, text=True, stdout=out, stderr=subprocess.STDOUT, timeout=timeout, env=env)
    return subprocess.run(cmd, cwd=cwd, text=True, timeout=timeout, env=env)


def chmod_tree(path: Path) -> None:
    if not path.exists():
        return
    for cur, dirs, files in os.walk(path):
        try:
            os.chmod(cur, 0o700)
        except OSError:
            pass
        for name in dirs:
            try:
                os.chmod(Path(cur) / name, 0o700)
            except OSError:
                pass
        for name in files:
            try:
                os.chmod(Path(cur) / name, 0o600)
            except OSError:
                pass


def sequence_doc() -> dict[str, Any]:
    return json.loads((ROOT / "data/workflow-task-sequences.json").read_text())


def load_sequence(sequence_id: str) -> dict[str, Any]:
    for seq in sequence_doc().get("sequences", []):
        if seq.get("id") == sequence_id:
            return seq
    raise KeyError(f"unknown workflow sequence {sequence_id}")


def active_sequence_ids() -> list[str]:
    return [seq["id"] for seq in sequence_doc().get("sequences", []) if seq.get("status") == "active"]


def safe_profile_key(profile_id: str) -> str:
    return profile_id.replace("_", "-")


BASELINE_POOL_PROTOCOL_VERSION = "baseline-pool-v1"
BASELINE_POOL_FINGERPRINT_LENGTH = 12


def _protocol_file_hash(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"baseline protocol input is missing: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_protocol_descriptor(seq: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    """Return the date-independent contract that makes a baseline reusable.

    This deliberately contains only frozen evaluation inputs: task/verifier bytes,
    fixture snapshot, baseline substrate, runtime binding, and isolation policy.
    Calendar time is execution metadata, never an identity input.
    """
    tasks = []
    for task in sorted(seq.get("tasks", []), key=lambda item: int(item["order"])):
        prompt_path = root / str(task["prompt_path"])
        verifier_path = root / str(task["verifier_command"])
        tasks.append({
            "id": task["id"],
            "order": int(task["order"]),
            "prompt_path": str(task["prompt_path"]),
            "prompt_sha256": _protocol_file_hash(prompt_path),
            "verifier_command": str(task["verifier_command"]),
            "verifier_sha256": _protocol_file_hash(verifier_path),
        })
    baseline = PROFILE_META["baseline-bare-codex"]
    return {
        "version": BASELINE_POOL_PROTOCOL_VERSION,
        "sequence_id": seq["id"],
        "fixture_id": seq["fixture_id"],
        "fixture_scale": seq.get("fixture_scale"),
        "initial_snapshot": seq.get("initial_snapshot", {}),
        "objective": seq.get("objective", "individual_tool_effectiveness"),
        "primary_metric": seq.get("primary_metric", "cumulative provider-billed workflow tokens"),
        "tasks": tasks,
        "baseline_profile": {
            "profile_id": "baseline-bare-codex",
            "profile_type": baseline["profile_type"],
            "enabled_surfaces": baseline["enabled_surfaces"],
            "disabled_overlaps": baseline["disabled_overlaps"],
        },
        "agent": {
            "runtime_id": "codex-cli",
            "provider": "openai",
            "model": DEFAULT_WORKFLOW_MODEL,
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
        },
        "isolation": {
            "prompt_delivery": "sequential-one-task-at-a-time",
            "seed_delivery_mode": "lazy-one-task-at-a-time",
            "future_tasks_visible": False,
            "verifier_assets_model_visible": False,
            "git_baseline_true_root_per_task": True,
        },
    }


def baseline_protocol_fingerprint(seq: dict[str, Any], root: Path = ROOT) -> str:
    descriptor = baseline_protocol_descriptor(seq, root)
    encoded = json.dumps(descriptor, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:BASELINE_POOL_FINGERPRINT_LENGTH]


def artifact_lane_label(project_id: str) -> str:
    return project_id.rsplit("-", 1)[-1]


def artifact_profile_label(profile_id: str) -> str:
    return "baseline" if profile_id == "baseline-bare-codex" else safe_profile_key(profile_id).rsplit("-", 1)[-1]


def canonical_baseline_session_id(project_id: str, replicate_index: int, protocol_fingerprint: str = "legacy", *, run_date: str = DATE) -> str:
    return f"baseline-{artifact_lane_label(project_id)}-{run_date.replace('-', '')}-p-{protocol_fingerprint}-r{replicate_index}"


def canonical_treatment_session_id(project_id: str, profile_id: str, replicate_index: int, protocol_fingerprint: str = "legacy", *, run_date: str = DATE) -> str:
    return f"{artifact_profile_label(profile_id)}-{artifact_lane_label(project_id)}-{run_date.replace('-', '')}-p-{protocol_fingerprint}-r{replicate_index}"


def reviewed_session_reuse_state(session: dict[str, Any] | None, root: Path = ROOT) -> str:
    if session is None:
        return "missing"
    interpretation = session.get("interpretation", {}) if isinstance(session.get("interpretation"), dict) else {}
    execution_accepted = interpretation.get("accepted_for_execution") is True
    completed = session.get("status") == "completed"
    sequence = session.get("task_sequence", {}) if isinstance(session.get("task_sequence"), dict) else {}
    prompt_delivery = sequence.get("prompt_delivery", {}) if isinstance(sequence.get("prompt_delivery"), dict) else {}
    leakage = sequence.get("leakage_controls", {}) if isinstance(sequence.get("leakage_controls"), dict) else {}
    isolated = (
        prompt_delivery.get("future_tasks_visible") is False
        and prompt_delivery.get("future_prompts_materialized_lazily") is True
        and prompt_delivery.get("seed_delivery_mode") == "lazy-one-task-at-a-time"
        and prompt_delivery.get("future_seed_regressions_visible") is False
        and leakage.get("task_directories_model_visible") is False
        and leakage.get("verifier_assets_model_visible") is False
        and leakage.get("verifier_integrity_passed") is True
        and leakage.get("seed_patches_model_visible") is False
        and leakage.get("git_baseline_true_root_per_task") is True
        and leakage.get("fixed_snapshot_objects_model_visible") is False
        and leakage.get("pre_seed_reflog_entries_visible") is False
        and leakage.get("concealment_verification_passed") is True
    )
    quality = session.get("software_quality", {}) if isinstance(session.get("software_quality"), dict) else {}
    quality_score = quality.get("quality_score")
    reviewed_quality = (
        quality.get("quality_review_status") == "reviewed"
        and isinstance(quality_score, int)
        and quality_score >= 4
        and not quality.get("critical_failures")
        and interpretation.get("accepted_for_objective") is True
    )
    artifacts = session.get("artifacts", {}) if isinstance(session.get("artifacts"), dict) else {}
    required = [artifacts.get(key) for key in ("run_record", "final_diff", "evidence_bundle", "manifest")]
    have_artifacts = all(path and (root / path).exists() for path in required)
    execution_ready = execution_accepted and completed and isolated and have_artifacts
    if execution_ready and reviewed_quality:
        return "reusable"
    if execution_ready and quality.get("quality_review_status") == "not-reviewed":
        return "review-pending"
    return "occupied"


def canonical_baseline_group_id(project_id: str, replicate_index: int, protocol_fingerprint: str) -> str:
    return f"{project_id}-canonical-baseline-{protocol_fingerprint}-sequential-workflow-r{replicate_index}"


def treatment_experiment_group_id(project_id: str, treatment_profile_id: str, replicate_index: int, protocol_fingerprint: str = "legacy") -> str:
    return f"{project_id}-{safe_profile_key(treatment_profile_id)}-{protocol_fingerprint}-sequential-workflow-r{replicate_index}"


def find_pool_profile_record(registry: dict[str, Any], seq: dict[str, Any], profile_id: str, replicate_index: int) -> dict[str, Any] | None:
    fingerprint = baseline_protocol_fingerprint(seq)
    matches = [
        session for session in registry.get("sessions", [])
        if session.get("baseline_pool", {}).get("protocol_fingerprint") == fingerprint
        and session.get("replicate_index") == replicate_index
        and session.get("task_sequence", {}).get("sequence_id") == seq["id"]
        and session.get("profile", {}).get("profile_id") == profile_id
    ]
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous {profile_id} pool records for {seq['id']} r{replicate_index}: {[item['session_id'] for item in matches]}")
    return matches[0] if matches else None


def find_canonical_baseline_record(registry: dict[str, Any], seq: dict[str, Any], replicate_index: int) -> dict[str, Any] | None:
    protocol_fingerprint = baseline_protocol_fingerprint(seq)
    matches = []
    for session in registry.get("sessions", []):
        if session.get("baseline_pool", {}).get("protocol_fingerprint") != protocol_fingerprint:
            continue
        if session.get("session_role") != "baseline":
            continue
        if session.get("replicate_index") != replicate_index:
            continue
        if session.get("task_sequence", {}).get("sequence_id") != seq["id"]:
            continue
        if session.get("status") not in (None, "completed"):
            continue
        interpretation = session.get("interpretation", {})
        accepted = interpretation.get("accepted_for_execution")
        if accepted is None:
            accepted = interpretation.get("accepted_for_objective")
        if accepted is True:
            matches.append(session)
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous canonical baseline pool for {seq['id']} r{replicate_index}: {[item['session_id'] for item in matches]}")
    return matches[0] if matches else None


def task_alias(order: int) -> str:
    return f"task-{order:02d}"


def task_dir(project: Path, order: int) -> Path:
    return project / "tasks" / task_alias(order)


def sanitize_task_prompt(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if any(pattern.match(line) for pattern in LEAKY_PROMPT_LINE_PATTERNS):
            continue
        # Hide public lookup keys and upstream-fixed framing in model-facing
        # prompts. The task text still describes the bug and verifier, but not
        # the public issue/commit answer path.
        line = re.sub(r"issue\s+#?\d+", "issue", line, flags=re.IGNORECASE)
        line = re.sub(r"real issue-derived regression", "regression", line, flags=re.IGNORECASE)
        line = re.sub(r"restores? the real upstream behavior", "restores the correct behavior", line, flags=re.IGNORECASE)
        line = re.sub(r"upstream test", "acceptance test", line, flags=re.IGNORECASE)
        lines.append(line)
    text = "\n".join(lines).strip() + "\n"
    return text


def write_sanitized_prompt(src: Path, dest: Path) -> None:
    dest.write_text(sanitize_task_prompt(src.read_text()))


def controller_scratch_dir(run_dir: Path) -> Path:
    return run_dir / "controller-scratch"


def controller_git_dir(run_dir: Path) -> Path:
    return controller_scratch_dir(run_dir) / "reference.git"


def seed_delivery_path(run_dir: Path) -> Path:
    return run_dir / "seed-delivery.json"


def configure_model_git(repo: Path) -> None:
    run(["git", "config", "user.email", "workflow-eval@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Workflow Eval"], cwd=repo)
    info = repo / ".git" / "info" / "exclude"
    with info.open("a") as out:
        out.write("\n.venv/\n__pycache__/\n.pytest_cache/\nnode_modules/\n")


def verify_concealed_stage(repo: Path, fixed_snapshot_oid: str, order: int) -> dict[str, Any]:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    parents = subprocess.check_output(["git", "rev-list", "--parents", "-1", "HEAD"], cwd=repo, text=True).split()
    remotes = subprocess.check_output(["git", "remote"], cwd=repo, text=True).splitlines()
    status = subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True).splitlines()
    reflog_oids = sorted(set(subprocess.check_output(["git", "reflog", "--all", "--format=%H"], cwd=repo, text=True).splitlines()))
    fixed_probe = subprocess.run(
        ["git", "cat-file", "-e", f"{fixed_snapshot_oid}^{{commit}}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    fsck = subprocess.run(
        ["git", "fsck", "--unreachable", "--no-reflogs"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    leaked_admin_paths = [
        str(path.relative_to(repo / ".git"))
        for path in [
            repo / ".git" / "FETCH_HEAD",
            repo / ".git" / "objects" / "info" / "alternates",
            repo / ".git" / "refs" / "replace",
            repo / ".git" / "refs" / "remotes",
        ]
        if path.exists()
    ]
    result = {
        "order": order,
        "head": head,
        "head_is_root": len(parents) == 1,
        "reachable_commit_count": int(subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=repo, text=True).strip()),
        "reflog_oids": reflog_oids,
        "remotes": remotes,
        "working_tree_clean": not status,
        "fixed_snapshot_object_present": fixed_probe.returncode == 0,
        "unreachable_objects": [line for line in fsck.stdout.splitlines() if line.strip()],
        "leaked_git_admin_paths": leaked_admin_paths,
    }
    result["passed"] = (
        result["head_is_root"]
        and result["reachable_commit_count"] == 1
        and result["reflog_oids"] == [head]
        and not result["remotes"]
        and result["working_tree_clean"]
        and not result["fixed_snapshot_object_present"]
        and not result["unreachable_objects"]
        and not result["leaked_git_admin_paths"]
    )
    return result


def conceal_seed(repo: Path, run_dir: Path, order: int, fixed_snapshot_oid: str) -> dict[str, Any]:
    """Replace Git metadata and commit the current broken state as a true root.

    Deleting the fetched repository's object database is required: committing a
    seed on top of the fixed snapshot leaves the exact answer available through
    ``HEAD^`` even after the upstream remote is removed.
    """
    git_dir = repo / ".git"
    if git_dir.exists():
        chmod_tree(git_dir)
        shutil.rmtree(git_dir)
    run(["git", "init", "-q"], cwd=repo, stdout=run_dir / f"seed-task-{order:02d}-git-init.txt")
    configure_model_git(repo)
    run(["git", "add", "-A"], cwd=repo, stdout=run_dir / f"seed-task-{order:02d}-git-add.txt")
    commit = run(
        ["git", "commit", "-q", "-m", f"workflow task {order} broken-start baseline"],
        cwd=repo,
        stdout=run_dir / f"seed-task-{order:02d}-git-commit.txt",
    )
    if commit.returncode != 0:
        raise RuntimeError(f"failed to create concealed root for task {order}")
    verification = verify_concealed_stage(repo, fixed_snapshot_oid, order)
    (run_dir / f"seed-task-{order:02d}-concealment.json").write_text(json.dumps(verification, indent=2) + "\n")
    if not verification["passed"]:
        raise RuntimeError(f"concealed task {order} baseline failed structural verification")
    return verification


def apply_seed_patch(repo: Path, patch: Path, output: Path) -> None:
    # Prefer a normal context apply. It composes cleanly with a prior model repair
    # when the task hunks do not overlap. A forced three-way apply depends on the
    # concealed fixed-snapshot blob, which is intentionally absent from a model
    # stage root and can fail even for non-overlapping hunks.
    with output.open("w") as out:
        proc = subprocess.run(
            ["git", "apply", str(patch)],
            cwd=repo,
            text=True,
            stdout=out,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
        if proc.returncode != 0:
            out.write("\nnormal apply failed; retrying three-way apply\n")
            proc = subprocess.run(
                ["git", "apply", "--3way", str(patch)],
                cwd=repo,
                text=True,
                stdout=out,
                stderr=subprocess.STDOUT,
                timeout=120,
            )
    if proc.returncode != 0:
        raise RuntimeError(f"seed patch failed: {patch}")
    conflicts = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )
    if conflicts.stdout.strip():
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=repo, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        raise RuntimeError(f"seed patch produced merge conflicts: {patch}: {conflicts.stdout.strip()}")


def seed_patch_application_state(repo: Path, patch: Path) -> dict[str, bool]:
    def check(*extra: str) -> bool:
        proc = subprocess.run(
            # State detection must inspect the working tree, not reconstruct a
            # three-way result from patch blob IDs (which makes an absent
            # pending seed appear reverse-applicable).
            ["git", "apply", *extra, "--check", str(patch)],
            cwd=repo,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return proc.returncode == 0

    return {
        "forward_applicable": check(),
        "reverse_applicable": check("--reverse"),
    }


def verify_seed_delivery_stage(seq: dict[str, Any], repo: Path, run_dir: Path, active_order: int, pending_orders: list[int]) -> dict[str, Any]:
    orders = [active_order, *pending_orders]
    states = {
        str(order): seed_patch_application_state(repo, task_dir(run_dir, order) / "seed-regression.patch")
        for order in orders
    }
    active_applied = states[str(active_order)]["reverse_applicable"]
    pending_absent = all(not states[str(order)]["reverse_applicable"] for order in pending_orders)
    pending_forward_applicable = all(states[str(order)]["forward_applicable"] for order in pending_orders)
    leaked_assets = [
        str(path.relative_to(repo))
        for path in repo.rglob("*")
        if path.is_file() and path.name in {"seed-regression.patch", "verify.sh"}
    ]
    return {
        "active_seed_order": active_order,
        "pending_seed_orders": pending_orders,
        "seed_patch_states": states,
        "active_seed_applied": active_applied,
        "pending_seed_regressions_absent": pending_absent,
        "pending_seed_patches_forward_applicable": pending_forward_applicable,
        "model_repo_seed_or_verifier_assets": leaked_assets,
        "passed": active_applied and pending_absent and pending_forward_applicable and not leaked_assets,
    }


def create_project(seq: dict[str, Any], project: Path, run_dir: Path, *, conceal_seed_origin: bool = True) -> None:
    if project.exists():
        chmod_tree(project)
        shutil.rmtree(project)
    project.mkdir(parents=True)
    tasks_dest = run_dir / "tasks"
    tasks_dest.mkdir()

    ordered_tasks = sorted(seq["tasks"], key=lambda item: item["order"])
    alias_manifest: list[dict[str, Any]] = []
    for task in ordered_tasks:
        order = int(task["order"])
        src = ROOT / Path(task["prompt_path"]).parent
        dest = task_dir(run_dir, order)
        shutil.copytree(src, dest)
        write_sanitized_prompt(src / "agent-prompt.txt", dest / "agent-prompt.txt")
        alias_manifest.append({
            "order": order,
            "task_id": task["id"],
            "alias": task_alias(order),
            "model_prompt_path": rel(dest / "agent-prompt.txt"),
            "verifier_command": rel(dest / "verify.sh"),
        })
    (run_dir / "task-alias-manifest.json").write_text(json.dumps(alias_manifest, indent=2) + "\n")

    repo = project / "repo"
    repo.mkdir()
    commit = seq["initial_snapshot"]["commit"]
    upstream = seq["initial_snapshot"]["upstream"]
    run(["git", "init", "-q"], cwd=repo, stdout=run_dir / "setup-git-init.txt")
    run(["git", "remote", "add", "origin", upstream], cwd=repo)
    run(["git", "fetch", "--depth", "1", "origin", commit], cwd=repo, stdout=run_dir / "setup-fetch.txt", timeout=1200)
    fetched = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"], cwd=repo, text=True).strip()
    if fetched != commit:
        raise RuntimeError(f"fetched {fetched}, expected {commit}")
    run(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], cwd=repo)
    run(["git", "reset", "--hard", commit], cwd=repo, stdout=run_dir / "setup-reset.txt")
    run(["git", "clean", "-fdx"], cwd=repo, stdout=run_dir / "setup-clean.txt")
    run(["git", "config", "user.email", "workflow-eval@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Workflow Eval"], cwd=repo)

    # Move the fetched Git object database outside the model mount while the
    # fixed source tree is still checked out. Future seed patches are not applied
    # here; task deltas provide cumulative review evidence without requiring
    # independent task seeds to stack in one synthetic broken tree.
    scratch = controller_scratch_dir(run_dir)
    scratch.mkdir()
    shutil.move(str(repo / ".git"), str(controller_git_dir(run_dir)))

    run(["git", "init", "-q"], cwd=repo)
    configure_model_git(repo)
    # git apply --3way needs the fixed tree in the temporary controller index.
    # conceal_seed deletes this metadata before the model can access the repo.
    run(["git", "add", "-A"], cwd=repo)
    first_order = int(ordered_tasks[0]["order"])
    apply_seed_patch(
        repo,
        task_dir(run_dir, first_order) / "seed-regression.patch",
        run_dir / f"seed-task-{first_order:02d}-apply.txt",
    )
    if conceal_seed_origin:
        concealment = conceal_seed(repo, run_dir, first_order, commit)
    else:
        first_patch = task_dir(run_dir, first_order) / "seed-regression.patch"
        reverse = subprocess.run(["git", "apply", "--reverse", str(first_patch)], cwd=repo, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        if reverse.returncode != 0:
            raise RuntimeError("failed to restore fixed debug baseline")
        run(["git", "add", "-A"], cwd=repo)
        run(["git", "commit", "-q", "-m", "debug fixed snapshot"], cwd=repo)
        apply_seed_patch(repo, first_patch, run_dir / f"seed-task-{first_order:02d}-debug-reapply.txt")
        concealment = {"order": first_order, "passed": False, "debug_unconcealed": True}

    orders = [int(task["order"]) for task in ordered_tasks]
    delivery_verification = verify_seed_delivery_stage(seq, repo, run_dir, first_order, orders[1:])
    stage_passed = bool(concealment.get("passed")) and delivery_verification["passed"]
    state = {
        "mode": "lazy-one-task-at-a-time",
        "future_seed_regressions_visible": False,
        "seed_patches_model_visible": False,
        "active_seed_order": first_order,
        "applied_seed_orders": [first_order],
        "pending_seed_orders": orders[1:],
        "diff_basis": "ordered-task-deltas",
        "fixed_snapshot_oid": commit,
        "transitions": [{"order": first_order, "concealment": concealment, "seed_delivery": delivery_verification}],
    }
    seed_delivery_path(run_dir).write_text(json.dumps(state, indent=2) + "\n")
    prepare_verification = {"passed": stage_passed, **state, "stage_seed_delivery": delivery_verification}
    (run_dir / "prepare-verification.json").write_text(json.dumps(prepare_verification, indent=2) + "\n")
    if conceal_seed_origin and not stage_passed:
        raise RuntimeError("initial lazy seed delivery or concealment verification failed")


def capture_task_delta(repo: Path, run_dir: Path, order: int) -> Path:
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=repo)
    paths = [path for path in untracked.decode().split("\0") if path]
    if paths:
        run(["git", "add", "-N", "--", *paths], cwd=repo)
    path = run_dir / f"task-{order:02d}-agent.diff"
    run(["git", "diff", "--binary", "HEAD", "--"], cwd=repo, stdout=path, timeout=120)
    run(["git", "diff", "--stat", "HEAD", "--"], cwd=repo, stdout=run_dir / f"task-{order:02d}-agent-diffstat.txt", timeout=120)
    return path


def advance_task_seed(seq: dict[str, Any], repo: Path, run_dir: Path, next_order: int) -> dict[str, Any]:
    state = json.loads(seed_delivery_path(run_dir).read_text())
    pending = [int(order) for order in state.get("pending_seed_orders", [])]
    if not pending or next_order != pending[0]:
        raise ValueError(f"seed transition must advance to the next pending order; requested {next_order}, pending={pending}")
    patch = task_dir(run_dir, next_order) / "seed-regression.patch"
    apply_seed_patch(repo, patch, run_dir / f"seed-task-{next_order:02d}-apply.txt")
    concealment = conceal_seed(repo, run_dir, next_order, str(state["fixed_snapshot_oid"]))
    remaining = pending[1:]
    delivery_verification = verify_seed_delivery_stage(seq, repo, run_dir, next_order, remaining)
    if not delivery_verification["passed"]:
        raise RuntimeError(f"lazy seed delivery verification failed for task {next_order}")
    state["active_seed_order"] = next_order
    state["applied_seed_orders"].append(next_order)
    state["pending_seed_orders"] = remaining
    state["transitions"].append({"order": next_order, "concealment": concealment, "seed_delivery": delivery_verification})
    seed_delivery_path(run_dir).write_text(json.dumps(state, indent=2) + "\n")
    return state


def base_record(session_id: str, seq: dict[str, Any], profile_id: str, project: Path, run_dir: Path) -> dict[str, Any]:
    pmeta = PROFILE_META[profile_id]
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    return {
        "schema_version": 1,
        "evaluation_id": session_id,
        "target": {
            "fixture_id": seq["fixture_id"],
            "fixture_scale": seq["fixture_scale"],
            "project_id": project_id,
            "repository_path": rel(project / "repo"),
        },
        "task": {
            "id": seq["id"],
            "prompt_path": rel(run_dir / "task-prompts"),
            "verifier_command": rel(run_dir / "verify-workflow.sh"),
        },
        "profile": {
            "profile_id": profile_id,
            "profile_type": pmeta["profile_type"],
            "component_ids": pmeta["component_ids"],
            "enabled_surfaces": pmeta["enabled_surfaces"],
        },
        "setup": {
            "tool_permissions": {
                "profile_id": profile_id,
                "allowed_token_saving_tools": pmeta["allowed_terms"],
                "allowed_prompt_mentions": pmeta["allowed_terms"],
                "forbidden_tools": [],
            }
        },
        "agent": {
            "runtime_id": "codex-cli",
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "provider": "openai",
            "model": DEFAULT_WORKFLOW_MODEL,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
        },
        "artifacts": {"root": rel(run_dir)},
    }


def profile_prompt_guidance(profile_id: str) -> str:
    pmeta = PROFILE_META[profile_id]
    tool_id = pmeta.get("tool_id")
    if not tool_id:
        return (
            "# Evaluation isolation contract\n\n"
            "You are running inside the `baseline-bare-codex` control lane. "
            "This is a Codex substrate baseline: native shell, file, git, and repository edit operations are allowed. "
            "Do not use external retrieval, compression, memory, MCP, or token-saving tools. "
            "Work only inside the target repository. The controller runs the hidden verifier after you finish; "
            "do not inspect or modify evaluation harness files.\n\n"
            "---\n\n"
        )
    cfg = fixture.TOOL_CONFIGS[str(tool_id)]
    tool_state = str(pmeta.get("tool_state", "cold"))
    use_policy = str(pmeta.get("tool_use_policy", "optional"))
    guidance_key = "optional_guidance" if use_policy == "optional" else "preferred_guidance"
    use_sentence = cfg.get(guidance_key) or cfg.get("preferred_guidance") or "Use the exposed treatment tool only when it helps."
    prompt_instructions = fixture.render_prompt_instructions(cfg)
    prompt_block = f"\n# {cfg['display_name']} lane instructions\n\n{prompt_instructions}\n\n---\n\n" if prompt_instructions else ""
    return (
        "# Evaluation isolation contract\n\n"
        f"You are running inside the `{profile_id}` treatment lane for {cfg['display_name']}. "
        f"Tool-state condition: `{tool_state}`. Tool-use policy: `{use_policy}`. "
        f"{use_sentence} Do not use other retrieval, compression, memory, or token-saving tools. "
        "Work only inside the target repository. The controller runs the hidden verifier after you finish; "
        "do not inspect or modify evaluation harness files.\n\n"
        "---\n\n"
        f"{prompt_block}"
    )


def task_prompt(seq: dict[str, Any], profile_id: str, project: Path, order: int, *, first_task: bool) -> str:
    task = next(item for item in seq["tasks"] if int(item["order"]) == order)
    prompt_path = task_dir(project, order) / "agent-prompt.txt"

    preface: list[str] = []
    if first_task:
        preface.append(profile_prompt_guidance(profile_id))
        preface.extend([
            f"# Sequential workflow session: {seq['id']}",
            "",
            "You are in one persistent repository checkout. Do not reset the repository.",
            "You will receive workflow tasks one at a time. Future tasks are intentionally hidden until the current task verifier passes.",
            "Complete only the current task. Preserve the working tree for later tasks.",
            "Source and agent state persist; the controller may replace local Git metadata between tasks to keep undisclosed regressions and answer objects hidden.",
            "The visible git baseline is the current task's broken-start state; do not assume `git diff` or history reveals the intended fix.",
            "",
        ])
    else:
        preface.extend([
            f"# Continue sequential workflow session: {seq['id']}",
            "",
            "The previous task verifier passed. Continue in the same source checkout and preserve earlier fixes.",
            "The controller injected only the current regression and refreshed the concealed local Git baseline; earlier source fixes and agent/tool state persist.",
            "Complete only the current task. Future tasks and regressions are intentionally hidden until this verifier passes.",
            "",
        ])
    preface.extend([
        f"## Current task {order}: {task_alias(order)}",
        "",
        "The controller runs the hidden verifier after you finish.",
        "",
        prompt_path.read_text(),
    ])
    return "\n".join(preface).rstrip() + "\n"


def write_verifier(seq: dict[str, Any], run_dir: Path, task_root: Path) -> Path:
    verifier = run_dir / "verify-workflow.sh"
    lines = ["#!/usr/bin/env bash", "set -euo pipefail"]
    for task in sorted(seq["tasks"], key=lambda item: item["order"]):
        lines.append(f"bash {json.dumps(str(task_dir(task_root, int(task['order'])) / 'verify.sh'))}")
    verifier.write_text("\n".join(lines) + "\n")
    verifier.chmod(0o755)
    return verifier


def verifier_paths(seq: dict[str, Any], task_root: Path, run_dir: Path) -> list[Path]:
    paths = [
        task_dir(task_root, int(task["order"])) / "verify.sh"
        for task in sorted(seq["tasks"], key=lambda item: item["order"])
    ]
    paths.append(run_dir / "verify-workflow.sh")
    return paths


def snapshot_verifier_hashes(seq: dict[str, Any], task_root: Path, run_dir: Path) -> dict[str, str]:
    return {rel(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in verifier_paths(seq, task_root, run_dir)}


def check_verifier_integrity(expected: dict[str, str]) -> dict[str, Any]:
    missing: list[str] = []
    changed: list[str] = []
    for path_text, expected_digest in expected.items():
        path = Path(path_text)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            missing.append(path_text)
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
            changed.append(path_text)
    return {"passed": not missing and not changed, "missing": missing, "changed": changed, "expected_sha256": expected}


def model_output_directory(run_dir: Path) -> Path:
    output = run_dir / "model-output"
    output.mkdir(parents=True, exist_ok=True)
    return output


def model_mounts_for_record(
    record: dict[str, Any],
    codex_home: Path,
    run_dir: Path,
    *,
    cfg: dict[str, Any] | None,
) -> list[tuple[Path, Path, str]]:
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    fixture.add_mount(mounts, model_output_directory(run_dir), mode="rw")
    return mounts


def verifier_mounts_for_task(
    record: dict[str, Any],
    codex_home: Path,
    run_dir: Path,
    order: int,
) -> list[tuple[Path, Path, str]]:
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True)
    repo = ROOT / record["target"]["repository_path"]
    fixture.add_mount(mounts, task_dir(run_dir, order), target=task_dir(repo.parent, order), mode="ro")
    return mounts


def final_verifier_mounts(
    seq: dict[str, Any],
    record: dict[str, Any],
    codex_home: Path,
    run_dir: Path,
) -> list[tuple[Path, Path, str]]:
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True)
    repo = ROOT / record["target"]["repository_path"]
    for task in sorted(seq["tasks"], key=lambda item: item["order"]):
        order = int(task["order"])
        fixture.add_mount(mounts, task_dir(run_dir, order), target=task_dir(repo.parent, order), mode="ro")
    fixture.add_mount(mounts, run_dir / "verify-workflow.sh", mode="ro")
    return mounts


def validate_run_safety_args(args: argparse.Namespace) -> None:
    bypasses = [
        name
        for name in ("skip_container_preflight", "skip_codex_preflight", "skip_dependency_install", "no_conceal_seed_origin")
        if bool(getattr(args, name, False))
    ]
    if bypasses and not bool(getattr(args, "prepare_only", False)):
        rendered = ", ".join("--" + name.replace("_", "-") for name in bypasses)
        raise ValueError(f"debug bypasses are prepare-only and cannot produce an accepted run: {rendered}")


def docker_setup_deps(seq: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> int:
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True)
    cmd = ["bash", "-lc", PROJECT_META[seq["fixture_id"]]["dependency_command"]]
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=run_dir / "setup-deps-output.txt", timeout=2400, mounts=mounts)
    return proc.returncode


def codex_base_cmd(record: dict[str, Any]) -> list[str]:
    return ["codex", "exec", *fixture.codex_model_args(record), "--json", "--color", "never", "--disable", "hooks", "--ignore-rules"]


def extract_thread_id(events_path: Path) -> str | None:
    for line in events_path.read_text(errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "thread.started" and item.get("thread_id"):
            return str(item["thread_id"])
    return None


def run_codex_task(
    record: dict[str, Any],
    profile_id: str,
    codex_home: Path,
    run_dir: Path,
    docker_image: str,
    prompt_path: Path,
    output_path: Path,
    last_message_path: Path,
    *,
    timeout: int,
    thread_id: str | None,
) -> tuple[int, str | None]:
    cfg = fixture.active_tool_config(record, profile_id)
    repo = ROOT / record["target"]["repository_path"]
    if thread_id is None:
        codex_cmd = [*codex_base_cmd(record), "--sandbox", "danger-full-access", "--cd", str(repo), "--output-last-message", str(last_message_path), "-"]
    else:
        codex_cmd = ["codex", "exec", "resume", *fixture.codex_model_args(record), "--json", "--disable", "hooks", "--ignore-rules", "--output-last-message", str(last_message_path), thread_id, "-"]
    wrapper = (cfg or {}).get("codex_wrapper") if cfg else None
    input_path_for_proc: Path | None = prompt_path
    if wrapper:
        assert cfg is not None
        data_dir = fixture.tool_data_dir(codex_home, cfg)
        wrapper_args = [
            str(part).format(
                repo=repo,
                codex_home=codex_home,
                tool_data_dir=data_dir,
                repo_slug=repo.name.replace("-", "_"),
            )
            for part in wrapper.get("args", [])
        ]
        if codex_cmd and codex_cmd[-1] == "-":
            codex_cmd = [*codex_cmd[:-1], prompt_path.read_text()]
            input_path_for_proc = None
        cmd = [str(wrapper["command"]), *wrapper_args, *codex_cmd[1:]]
    else:
        cmd = codex_cmd
    env = fixture.codex_env(codex_home, containerized=True, cfg=cfg)
    env.update(fixture.tool_env_for_record(record, profile_id, codex_home))
    mounts = model_mounts_for_record(record, codex_home, run_dir, cfg=cfg)
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=output_path, input_path=input_path_for_proc, timeout=timeout, mounts=mounts)
    if thread_id is None and proc.returncode == 0:
        thread_id = extract_thread_id(output_path)
    return proc.returncode, thread_id


def run_one_verifier(seq: dict[str, Any], order: int, record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> dict[str, Any]:
    task = next(item for item in seq["tasks"] if int(item["order"]) == order)
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = verifier_mounts_for_task(record, codex_home, run_dir, order)
    out = run_dir / f"verifier-{task_alias(order)}.txt"
    cmd = ["bash", str(task_dir(repo.parent, order) / "verify.sh")]
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=out, timeout=1800, mounts=mounts)
    return {
        "task_id": task["id"],
        "task_alias": task_alias(order),
        "order": order,
        "verifier_exit_code": proc.returncode,
        "accepted": proc.returncode == 0,
        "verifier_output": rel(out),
    }


def run_final_verifier(seq: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> int:
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = final_verifier_mounts(seq, record, codex_home, run_dir)
    proc = fixture.run_backend(["bash", str(run_dir / "verify-workflow.sh")], backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=run_dir / "final-verifier-output.txt", timeout=3600, mounts=mounts)
    return proc.returncode


def concatenate_events(run_dir: Path, task_count: int) -> None:
    combined = run_dir / "codex-events.jsonl"
    with combined.open("w") as out:
        for order in range(1, task_count + 1):
            path = run_dir / f"task-{order:02d}-codex-events.jsonl"
            if path.exists():
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")


def capture_diff(record: dict[str, Any], run_dir: Path) -> None:
    repo = ROOT / record["target"]["repository_path"]
    run(["git", "status", "--short"], cwd=repo, stdout=run_dir / "git-status.txt", timeout=60)
    task_deltas = sorted(run_dir.glob("task-??-agent.diff"))
    if task_deltas:
        with (run_dir / "changes.diff").open("w") as out:
            out.write("# Ordered workflow task deltas. Each section is relative to that task's concealed stage root.\n")
            for path in task_deltas:
                out.write(f"\n# --- {path.stem} ---\n")
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")
        with (run_dir / "final-diffstat.txt").open("w") as out:
            for path in sorted(run_dir.glob("task-??-agent-diffstat.txt")):
                out.write(f"--- {path.name} ---\n")
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")
        return
    run(["git", "diff", "--stat"], cwd=repo, stdout=run_dir / "final-diffstat.txt", timeout=60)
    run(["git", "diff", "--binary"], cwd=repo, stdout=run_dir / "changes.diff", timeout=120)


def audit(record_path: Path, run_dir: Path) -> int:
    artifacts = [str(record_path), str(run_dir / "codex-events.jsonl"), str(run_dir / "codex-mcp-list.txt"), str(run_dir / "codex-effective-config.toml")]
    artifacts.extend(str(path) for path in sorted((run_dir / "task-prompts").glob("task-*.md")))
    return fixture.run([
        sys.executable,
        str(ROOT / "scripts/audit_tool_isolation.py"),
        "--json-output",
        str(run_dir / "tool-isolation-audit.json"),
        *artifacts,
    ], stdout_path=run_dir / "tool-isolation-audit.txt", timeout=120).returncode


def compact_artifacts(run_dir: Path) -> dict[str, str]:
    return {
        "artifact_contract": "compact-v1-four-files",
        "run_record": rel(run_dir / "run.json"),
        "final_diff": rel(run_dir / "changes.diff"),
        "final_diff_basis": "ordered per-task deltas relative to each concealed stage root",
        "evidence_bundle": rel(run_dir / "evidence.jsonl.gz"),
        "manifest": rel(run_dir / "manifest.sha256"),
    }


def evidence_source_files(run_dir: Path) -> list[Path]:
    """Return text evidence to pack, excluding scratch checkouts/homes."""
    files: list[Path] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(run_dir).parts
        if not rel_parts or rel_parts[0] in {"codex-homes", "controller-scratch"}:
            continue
        if rel_parts[0] == "project":
            continue
        if len(rel_parts) == 1 and rel_parts[0] in COMPACT_ARTIFACT_NAMES:
            continue
        files.append(path)
    return files


def write_evidence_bundle(run_dir: Path) -> Path:
    bundle = run_dir / "evidence.jsonl.gz"
    with gzip.open(bundle, "wt", encoding="utf-8") as out:
        for path in evidence_source_files(run_dir):
            entry = {
                "path": str(path.relative_to(run_dir)),
                "content": path.read_text(errors="replace"),
            }
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return bundle


def write_manifest(run_dir: Path) -> Path:
    manifest = run_dir / "manifest.sha256"
    lines = []
    for name in sorted(COMPACT_ARTIFACT_NAMES - {"manifest.sha256"}):
        path = run_dir / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}\n")
    manifest.write_text("".join(lines))
    return manifest


def remove_noncompact_artifacts(run_dir: Path) -> None:
    for path in list(run_dir.iterdir()):
        if path.is_file() and path.name in COMPACT_ARTIFACT_NAMES:
            continue
        if path.is_dir():
            chmod_tree(path)
            shutil.rmtree(path)
        else:
            path.unlink()


def finalize_failed_attempt(summary: dict[str, Any], record: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    """Compact a pre-model infrastructure failure without publishing a session."""
    if not (run_dir / "changes.diff").exists():
        capture_diff(record, run_dir)
    redact_auth_sync(run_dir)
    remove_ephemeral_homes(run_dir)
    summary["artifacts"] = compact_artifacts(run_dir)
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_evidence_bundle(run_dir)
    remove_noncompact_artifacts(run_dir)
    write_manifest(run_dir)
    return summary


def redact_json_file(path: Path, keys: set[str]) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text())
    for key in keys:
        if key in data:
            data[key] = "[REDACTED]"
    path.write_text(json.dumps(data, indent=2) + "\n")


def redact_auth_sync(run_dir: Path) -> None:
    path = run_dir / "codex-auth-sync.jsonl"
    if path.exists():
        lines = []
        for line in path.read_text().splitlines():
            try:
                item = json.loads(line)
                if "source_home" in item:
                    item["source_home"] = "[REDACTED]"
                lines.append(json.dumps(item))
            except json.JSONDecodeError:
                lines.append(line)
        path.write_text("\n".join(lines) + ("\n" if lines else ""))
    redact_json_file(run_dir / "codex-home-manifest.json", {"source_auth_home"})


def sync_copied_codex_auth_back(codex_home: Path, source_home: Path, run_dir: Path, stage: str) -> None:
    """Persist refreshed copied Codex auth from the ephemeral Docker home.

    Docker runs copy auth into the run-local Codex home instead of mounting the
    controller account home. Codex may refresh that file during preflight or task
    execution, so copy it back and leave only a redacted sync audit event.
    """
    if os.environ.get("WORKFLOW_LANE_DISABLE_AUTH_SYNC") == "1":
        return
    auths = fixture.auth_candidates(source_home)
    if not auths:
        return
    source_auth = auths[0]
    copied_auth = codex_home / source_auth.name
    event = {
        "stage": stage,
        "source_home": str(source_auth.parent),
        "auth_link_name": source_auth.name,
        "synced": False,
    }
    if copied_auth.exists():
        shutil.copy2(copied_auth, source_auth)
        os.chmod(source_auth, 0o600)
        event["synced"] = True
    with (run_dir / "codex-auth-sync.jsonl").open("a") as out:
        out.write(json.dumps(event) + "\n")


def remove_ephemeral_homes(run_dir: Path) -> None:
    for name in ["codex-homes"]:
        path = run_dir / name
        if path.exists():
            chmod_tree(path)
            shutil.rmtree(path)


def workflow_session_record(
    seq: dict[str, Any],
    summary: dict[str, Any],
    run_dir: Path,
    profile_id: str,
    codex_exit_codes: list[int],
    final_verifier_code: int,
    audit_code: int,
    usage: dict[str, Any],
    verifier_results: list[dict[str, Any]],
    *,
    prompt_delivery: dict[str, Any],
    leakage_controls: dict[str, Any],
    comparison_baseline_session_id: str = "",
) -> dict[str, Any]:
    pmeta = PROFILE_META[profile_id]
    tasks_passed = sum(1 for result in verifier_results if result["verifier_exit_code"] == 0)
    total_provider_tokens = usage.get("total_provider_tokens")
    tokens_per_accepted_task = (total_provider_tokens / tasks_passed) if tasks_passed and isinstance(total_provider_tokens, (int, float)) else None
    accepted = bool(summary.get("accepted"))
    return {
        "schema_version": 1,
        "session_id": summary["session_id"],
        "record_type": "workflow_session",
        "evidence_type": "workflow-simulation",
        "study_id": summary["study_id"],
        "experiment_group_id": summary["experiment_group_id"],
        "objective": seq.get("objective", "individual_tool_effectiveness"),
        "evidence_stage": "reproduction",
        "status": "completed" if accepted else "failed",
        "session_role": pmeta["session_role"],
        "replicate_index": summary["replicate_index"],
        "baseline_pool": summary["baseline_pool"],
        "date": DATE,
        "target": {
            "fixture_id": seq["fixture_id"],
            "fixture_scale": seq["fixture_scale"],
            "project_id": PROJECT_META[seq["fixture_id"]]["project_id"],
            "repository_path": summary["repository_path"],
            "initial_snapshot": {
                "commit": seq["initial_snapshot"]["commit"],
                "branch": "detached",
                "fixture_hash": "",
            },
        },
        "task_sequence": {
            "sequence_id": seq["id"],
            "task_ids": [task["id"] for task in sorted(seq["tasks"], key=lambda item: item["order"])],
            "reset_policy": "reset source checkout, profile home, tool state, indexes, caches, generated config, and agent home before the session; preserve source/tool/agent state while re-rooting model-facing Git metadata before each task",
            "prompt_delivery": prompt_delivery,
            "leakage_controls": leakage_controls,
        },
        "profile": {
            "profile_id": profile_id,
            "profile_type": pmeta["profile_type"],
            "enabled_surfaces": pmeta["enabled_surfaces"],
            "disabled_overlaps": pmeta["disabled_overlaps"],
            "component_ids": pmeta["component_ids"],
        },
        "agent": {
            "runtime_id": "codex-cli",
            "model_condition_id": DEFAULT_WORKFLOW_MODEL_CONDITION_ID,
            "name": "Codex CLI",
            "version": summary.get("codex_version", ""),
            "provider": "openai",
            "model": DEFAULT_WORKFLOW_MODEL,
            "reasoning_effort": DEFAULT_WORKFLOW_REASONING_EFFORT,
            "temperature": None,
            "max_turns": None,
            "time_budget_seconds": summary.get("timeout_seconds"),
        },
        "state_policy": sequence_doc().get("state_policy_defaults", {}),
        "cumulative_token_usage": {
            "measurement_source": "codex-jsonl-usage-events",
            "fresh_input_tokens": usage.get("fresh_input_tokens"),
            "cached_input_tokens": usage.get("cached_input_tokens"),
            "cache_write_tokens": usage.get("cache_write_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "reasoning_tokens": usage.get("reasoning_tokens"),
            "total_provider_tokens": usage.get("total_provider_tokens"),
            "estimated_cost_usd": usage.get("estimated_cost_usd"),
            "tokens_per_accepted_task": tokens_per_accepted_task,
            "pricing_basis": "not computed; Codex-reported token volume, not billing-weighted cost",
        },
        "per_task_results": verifier_results,
        "software_quality": {
            "tasks_attempted": len(verifier_results),
            "tasks_passed": tasks_passed,
            "final_verifier_command": rel(run_dir / "verify-workflow.sh"),
            "final_verifier_passed": final_verifier_code == 0,
            "functional_verifier_passed": final_verifier_code == 0 and tasks_passed == len(seq["tasks"]),
            "quality_review_status": "not-reviewed",
            "quality_score": None,
            "critical_failures": [] if final_verifier_code == 0 else ["one or more workflow verifiers failed"],
        },
        "state_observations": {
            "stale_context_incidents": None,
            "overfeeding_incidents": None,
            "repeated_rediscovery_incidents": None,
            "thread_continuity_errors": summary.get("thread_continuity_errors", []),
            "seed_transition_errors": summary.get("seed_transition_errors", []),
            "useful_state_reuse_notes": "Single persistent Codex thread and source/tool/agent state across one lazily seeded task at a time.",
        },
        "operational_reproducibility": {
            "install_logged": True,
            "pre_session_reset_verified": True,
            "raw_artifacts_recoverable": True,
            "state_leakage_outside_session_observed": False,
            "tool_isolation_audit": {
                "command": "python3 scripts/audit_tool_isolation.py --json-output ...",
                "passed": audit_code == 0,
                "forbidden_tool_hits": [],
            },
        },
        "artifacts": compact_artifacts(run_dir),
        "interpretation": {
            "accepted_for_execution": accepted,
            "accepted_for_objective": False,
            "claim_status": "quality-review-pending" if accepted else "execution-failed",
            "comparison_baseline_session_id": comparison_baseline_session_id,
            "exclusion_reason": "software-quality-review-pending" if accepted else f"codex_exit_codes={codex_exit_codes}; final_verifier_exit={final_verifier_code}; audit_exit={audit_code}; thread_continuity_errors={summary.get('thread_continuity_errors', [])}; seed_transition_errors={summary.get('seed_transition_errors', [])}; usage_warnings={usage.get('warnings')}",
            "notes": "Execution gates passed; objective acceptance requires a recorded software-quality review." if accepted else "Sequential workflow session failed one or more execution gates; inspect raw artifacts.",
            "scope_note": "Full active workflow sequence; prompts and regressions delivered one task at a time.",
        },
    }


def update_registry(record: dict[str, Any]) -> None:
    path = ROOT / "data/workflow-sessions.json"
    doc = json.loads(path.read_text())
    sessions = doc.get("sessions", [])
    if any(session.get("session_id") == record["session_id"] for session in sessions):
        raise FileExistsError(
            f"workflow session {record['session_id']} already exists; use a new replicate/session ID and supersedes_session_id"
        )
    sessions.append(record)
    doc["sessions"] = sessions
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(json.dumps(doc, indent=2) + "\n")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def freshish_tokens(record: dict[str, Any]) -> int | float | None:
    usage = record.get("cumulative_token_usage", {})
    fresh = usage.get("fresh_input_tokens")
    output = usage.get("output_tokens")
    if isinstance(fresh, (int, float)) and isinstance(output, (int, float)):
        return fresh + output
    total = usage.get("total_provider_tokens")
    cached = usage.get("cached_input_tokens")
    if isinstance(total, (int, float)) and isinstance(cached, (int, float)):
        return total - cached
    return None


def percent_delta(delta: int | float | None, baseline: int | float | None) -> float | None:
    return (delta / baseline * 100) if delta is not None and baseline else None


def write_comparison_if_ready(seq: dict[str, Any], study_id: str, replicate_index: int, treatment_profile_id: str) -> dict[str, Any] | None:
    registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    protocol_fingerprint = baseline_protocol_fingerprint(seq)
    comparison_key = safe_profile_key(treatment_profile_id)
    group_id = treatment_experiment_group_id(project_id, treatment_profile_id, replicate_index, protocol_fingerprint)
    baseline = find_canonical_baseline_record(registry, seq, replicate_index)
    sessions = [s for s in registry.get("sessions", []) if s.get("experiment_group_id") == group_id]
    treatment = next((s for s in sessions if s.get("profile", {}).get("profile_id") == treatment_profile_id and s.get("baseline_pool", {}).get("protocol_fingerprint") == protocol_fingerprint), None)
    if not baseline or not treatment:
        return None
    if reviewed_session_reuse_state(baseline, ROOT) != "reusable" or reviewed_session_reuse_state(treatment, ROOT) != "reusable":
        return None
    b_tokens = baseline.get("cumulative_token_usage", {}).get("total_provider_tokens")
    t_tokens = treatment.get("cumulative_token_usage", {}).get("total_provider_tokens")
    delta = t_tokens - b_tokens if isinstance(b_tokens, (int, float)) and isinstance(t_tokens, (int, float)) else None
    b_freshish = freshish_tokens(baseline)
    t_freshish = freshish_tokens(treatment)
    freshish_delta = t_freshish - b_freshish if isinstance(b_freshish, (int, float)) and isinstance(t_freshish, (int, float)) else None
    comparison = {
        "schema_version": 3,
        "comparison_id": f"baseline-{artifact_lane_label(project_id)}-{DATE.replace('-', '')}-vs-{artifact_profile_label(treatment_profile_id)}-p-{protocol_fingerprint}-r{replicate_index}",
        "study_id": study_id,
        "experiment_group_id": group_id,
        "comparison_design": "protocol-bound-shared-baseline-v3",
        "baseline_reuse_policy": "one reviewed canonical baseline-bare-codex session per frozen protocol fingerprint and replicate is shared by all treatment comparisons; execution date is metadata, not baseline identity",
        "baseline_protocol_fingerprint": protocol_fingerprint,
        "replicate_count": 1,
        "uncertainty": None,
        "claim_status": "single-run-screening",
        "eligible_for_ranking": False,
        "sequence_id": seq["id"],
        "baseline_session_id": baseline["session_id"],
        "treatment_session_id": treatment["session_id"],
        "baseline_total_provider_tokens": b_tokens,
        "treatment_total_provider_tokens": t_tokens,
        "delta_total_provider_tokens": delta,
        "delta_percent": percent_delta(delta, b_tokens),
        "baseline_freshish_tokens": b_freshish,
        "treatment_freshish_tokens": t_freshish,
        "delta_freshish_tokens": freshish_delta,
        "delta_freshish_percent": percent_delta(freshish_delta, b_freshish),
        "baseline_accepted": baseline.get("interpretation", {}).get("accepted_for_objective"),
        "treatment_accepted": treatment.get("interpretation", {}).get("accepted_for_objective"),
        "quality_gate": {
            "baseline_tasks_passed": baseline.get("software_quality", {}).get("tasks_passed"),
            "treatment_tasks_passed": treatment.get("software_quality", {}).get("tasks_passed"),
            "task_count": len(seq["tasks"]),
        },
        "interpretation": f"Single-run screening observation only; do not rank tools from this comparison. Sequential prompt delivery exposes only the current task. Positive token deltas mean {treatment_profile_id} used more Codex-reported tokens than the reviewed shared baseline; negative means fewer. Freshish tokens are fresh_input_tokens + output_tokens for a cache-adjusted secondary view.",
    }
    out = ROOT / "sources/evaluations/workflow-sessions" / f"{comparison['comparison_id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(f"workflow comparison already exists; refusing overwrite: {out}")
    out.write_text(json.dumps(comparison, indent=2) + "\n")
    return comparison


def run_one(args: argparse.Namespace) -> dict[str, Any]:
    validate_run_safety_args(args)
    seq = load_sequence(args.sequence_id)
    if seq.get("status") != "active" and not args.prepare_only:
        raise ValueError(f"workflow sequence {args.sequence_id} is not active; only prepare-only is allowed")
    if seq["fixture_id"] not in PROJECT_META:
        raise ValueError(f"No runner metadata for fixture {seq['fixture_id']}")
    profile_id = args.profile_id
    if profile_id not in PROFILE_META:
        raise ValueError(f"No runner metadata for profile {profile_id}")
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    protocol_fingerprint = baseline_protocol_fingerprint(seq)
    baseline_pool = {
        "protocol_version": BASELINE_POOL_PROTOCOL_VERSION,
        "protocol_fingerprint": protocol_fingerprint,
        "identity_policy": "frozen-protocol-and-replicate; execution date is metadata only",
    }
    study_id = args.study_id or "phase-2-sequential-workflow-v1"
    comparison_profile_id = args.comparison_profile_id or (profile_id if profile_id != "baseline-bare-codex" else "")
    if profile_id == "baseline-bare-codex":
        session_id = args.session_id or canonical_baseline_session_id(project_id, args.replicate_index, protocol_fingerprint)
        experiment_group_id = args.experiment_group_id or canonical_baseline_group_id(project_id, args.replicate_index, protocol_fingerprint)
    else:
        session_id = args.session_id or canonical_treatment_session_id(project_id, profile_id, args.replicate_index, protocol_fingerprint)
        experiment_group_id = args.experiment_group_id or treatment_experiment_group_id(project_id, profile_id, args.replicate_index, protocol_fingerprint)
    run_dir = ROOT / "sources/evaluations/workflow-sessions" / session_id
    if run_dir.exists():
        raise FileExistsError(
            f"workflow session directory already exists: {run_dir}; use a new replicate/session ID instead of overwriting evidence"
        )
    if profile_id != "baseline-bare-codex" and comparison_profile_id:
        comparison_id = f"baseline-{artifact_lane_label(project_id)}-{DATE.replace('-', '')}-vs-{artifact_profile_label(comparison_profile_id)}-p-{protocol_fingerprint}-r{args.replicate_index}"
        comparison_path = ROOT / "sources/evaluations/workflow-sessions" / f"{comparison_id}.json"
        if comparison_path.exists():
            raise FileExistsError(f"workflow comparison already exists; use a new replicate index: {comparison_path}")
    run_dir.mkdir(parents=True, exist_ok=True)
    project = run_dir / "project"
    prompt_dir = run_dir / "task-prompts"
    prompt_dir.mkdir(exist_ok=True)

    create_project(seq, project, run_dir, conceal_seed_origin=not args.no_conceal_seed_origin)
    verifier = write_verifier(seq, run_dir, project)
    expected_verifier_hashes = snapshot_verifier_hashes(seq, run_dir, run_dir)
    record = base_record(session_id, seq, profile_id, project, run_dir)
    record["task"]["verifier_command"] = rel(verifier)
    record_path = run_dir / "run-record-input.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n")

    protocol = fixture.evaluation_protocol(record, profile_id, PROFILE_META[profile_id]["tool_state"], PROFILE_META[profile_id]["tool_use_policy"])
    protocol["prompt_delivery"] = "sequential-one-task-at-a-time"
    protocol["seed_origin_concealment"] = not args.no_conceal_seed_origin
    (run_dir / "evaluation-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")

    codex_home_root = run_dir / "codex-homes"
    codex_home = fixture.prepare_codex_home(record, profile_id, run_dir, args.source_codex_home, codex_home_root, copy_auth=True)
    cfg = fixture.active_tool_config(record, profile_id)

    if not args.skip_container_preflight:
        container_preflight = fixture.check_container_runtime("docker", args.docker_image, run_dir, False, build_image=False, dockerfile=fixture.DEFAULT_DOCKERFILE, codex_home=codex_home, cfg=cfg)
        if not container_preflight.get("passed"):
            return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "container-preflight", "run_dir": rel(run_dir), "container_preflight": container_preflight}, record, run_dir)
    if not args.skip_codex_preflight:
        preflight = fixture.preflight_codex(record, codex_home, profile_id, run_dir, backend="docker", docker_image=args.docker_image)
        sync_copied_codex_auth_back(codex_home, args.source_codex_home, run_dir, "after-preflight")
        redact_auth_sync(run_dir)
        if not preflight.get("passed"):
            return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "codex-preflight", "run_dir": rel(run_dir), "preflight": preflight}, record, run_dir)
    if not args.skip_dependency_install:
        deps_code = docker_setup_deps(seq, record, codex_home, run_dir, args.docker_image)
        if deps_code != 0:
            return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "setup-deps", "setup_deps_exit_code": deps_code, "run_dir": rel(run_dir)}, record, run_dir)

    warmup_code = fixture.prepare_profile_workspace(
        record,
        profile_id,
        codex_home,
        run_dir,
        protocol,
        backend="docker",
        docker_image=args.docker_image,
    )
    if warmup_code != 0:
        return finalize_failed_attempt({"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "tool-warmup", "tool_warmup_exit_code": warmup_code, "run_dir": rel(run_dir)}, record, run_dir)

    ordered_tasks = sorted(seq["tasks"], key=lambda item: item["order"])

    if args.prepare_only:
        first_task = ordered_tasks[0]
        first_order = int(first_task["order"])
        (prompt_dir / f"task-{first_order:02d}.md").write_text(
            task_prompt(seq, profile_id, run_dir, first_order, first_task=True)
        )
        prepare_verification = json.loads((run_dir / "prepare-verification.json").read_text())
        redact_auth_sync(run_dir)
        remove_ephemeral_homes(run_dir)
        return {
            "session_id": session_id,
            "profile_id": profile_id,
            "sequence_id": seq["id"],
            "prepared": bool(prepare_verification.get("passed")),
            "prepare_verification": prepare_verification,
            "run_dir": rel(run_dir),
        }

    thread_id: str | None = None
    codex_exit_codes: list[int] = []
    verifier_results: list[dict[str, Any]] = []
    thread_continuity_errors: list[dict[str, Any]] = []
    seed_transition_errors: list[dict[str, Any]] = []
    verifier_integrity_checks: list[dict[str, Any]] = []
    model_output_dir = model_output_directory(run_dir)
    for task in ordered_tasks:
        order = int(task["order"])
        if order != int(ordered_tasks[0]["order"]):
            try:
                advance_task_seed(seq, project / "repo", run_dir, order)
            except Exception as exc:
                error = {"order": order, "task_id": task["id"], "message": str(exc)}
                seed_transition_errors.append(error)
                (run_dir / f"seed-task-{order:02d}-transition-error.txt").write_text(str(exc) + "\n")
                break
        prompt_path = prompt_dir / f"task-{order:02d}.md"
        prompt_path.write_text(task_prompt(seq, profile_id, run_dir, order, first_task=order == 1))
        events_path = run_dir / f"task-{order:02d}-codex-events.jsonl"
        last_message_path = model_output_dir / f"task-{order:02d}-codex-last-message.txt"
        code, thread_id = run_codex_task(record, profile_id, codex_home, run_dir, args.docker_image, prompt_path, events_path, last_message_path, timeout=args.timeout_per_task, thread_id=thread_id)
        codex_exit_codes.append(code)
        sync_copied_codex_auth_back(codex_home, args.source_codex_home, run_dir, f"after-task-{order:02d}")
        redact_auth_sync(run_dir)
        capture_task_delta(project / "repo", run_dir, order)
        integrity = {"stage": f"after-task-{order:02d}", **check_verifier_integrity(expected_verifier_hashes)}
        verifier_integrity_checks.append(integrity)
        if not integrity["passed"]:
            break
        if code != 0:
            break
        if thread_id is None:
            message = f"Codex task {order} exited 0 but no thread_id was captured; refusing to continue because workflow continuity is unproven."
            thread_continuity_errors.append({"order": order, "task_id": task["id"], "message": message})
            (run_dir / f"task-{order:02d}-thread-continuity-error.txt").write_text(message + "\n")
            break
        result = run_one_verifier(seq, order, record, codex_home, run_dir, args.docker_image)
        verifier_results.append(result)
        if result["verifier_exit_code"] != 0:
            break

    final_integrity = {"stage": "before-final-verifier", **check_verifier_integrity(expected_verifier_hashes)}
    verifier_integrity_checks.append(final_integrity)
    (run_dir / "verifier-integrity.json").write_text(json.dumps({"checks": verifier_integrity_checks}, indent=2) + "\n")
    verifier_integrity_passed = all(check["passed"] for check in verifier_integrity_checks)
    concatenate_events(run_dir, len(ordered_tasks))
    usage = extract_codex_usage.build_summary(run_dir / "codex-events.jsonl")
    (run_dir / "provider-usage.json").write_text(json.dumps(usage, indent=2) + "\n")
    final_verifier_code = run_final_verifier(seq, record, codex_home, run_dir, args.docker_image) if len(verifier_results) == len(ordered_tasks) and verifier_integrity_passed and not seed_transition_errors else 1
    capture_diff(record, run_dir)
    audit_code = audit(record_path, run_dir)
    accepted = all(code == 0 for code in codex_exit_codes) and not thread_continuity_errors and not seed_transition_errors and len(verifier_results) == len(ordered_tasks) and final_verifier_code == 0 and audit_code == 0 and verifier_integrity_passed and not usage.get("warnings")
    smoke = (run_dir / "docker-smoke-output.txt").read_text(errors="replace") if (run_dir / "docker-smoke-output.txt").exists() else ""
    codex_version = next((line.strip() for line in smoke.splitlines() if "codex" in line.lower() and any(ch.isdigit() for ch in line)), "")
    seed_state = json.loads(seed_delivery_path(run_dir).read_text())
    concealment_verified = all(bool(item.get("concealment", {}).get("passed")) for item in seed_state.get("transitions", []))
    prompt_delivery = {
        "mode": "sequential-one-task-at-a-time",
        "future_tasks_visible": False,
        "future_prompts_materialized_lazily": True,
        "seed_delivery_mode": "lazy-one-task-at-a-time",
        "future_seed_regressions_visible": False,
        "codex_thread_id": thread_id,
        "task_prompt_evidence": rel(run_dir / "evidence.jsonl.gz"),
    }
    leakage_controls = {
        "seed_origin_concealed": not args.no_conceal_seed_origin,
        "seed_patches_model_visible": False,
        "git_baseline_true_root_per_task": concealment_verified,
        "fixed_snapshot_objects_model_visible": False,
        "pre_seed_reflog_entries_visible": False,
        "concealment_verification_passed": concealment_verified,
        "task_directories_model_visible": False,
        "verifier_assets_model_visible": False,
        "model_writable_surface": "target repository plus isolated model-output directory",
        "verifier_integrity_passed": verifier_integrity_passed,
        "verifier_integrity_evidence": f"{rel(run_dir / 'evidence.jsonl.gz')}#verifier-integrity.json",
        "model_prompts_sanitized": True,
        "upstream_remote_removed_from_model_facing_repo": not args.no_conceal_seed_origin,
        "broken_start_committed_as_local_baseline": not args.no_conceal_seed_origin,
        "remaining_limitations": [
            "Task semantics and verifier names may still be searchable if the model intentionally uses external network access.",
            "Full prevention requires fixtures built from pre-fix bases plus hidden verifier tests rather than production-code reverse patches.",
        ],
    }
    summary = {
        "session_id": session_id,
        "study_id": study_id,
        "experiment_group_id": experiment_group_id,
        "replicate_index": args.replicate_index,
        "baseline_pool": baseline_pool,
        "profile_id": profile_id,
        "workflow_sequence_id": seq["id"],
        "fixture_id": seq["fixture_id"],
        "repository_path": rel(project / "repo"),
        "codex_exit_codes": codex_exit_codes,
        "final_verifier_exit_code": final_verifier_code,
        "tool_isolation_audit_exit_code": audit_code,
        "verifier_integrity_passed": verifier_integrity_passed,
        "thread_continuity_errors": thread_continuity_errors,
        "seed_transition_errors": seed_transition_errors,
        "seed_delivery": {
            "mode": seed_state["mode"],
            "future_seed_regressions_visible": seed_state["future_seed_regressions_visible"],
            "applied_seed_orders": seed_state["applied_seed_orders"],
            "pending_seed_orders": seed_state["pending_seed_orders"],
        },
        "accepted": accepted,
        "timeout_seconds": args.timeout_per_task * len(ordered_tasks),
        "codex_version": codex_version,
        "token_usage": {k: usage.get(k) for k in ["fresh_input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens", "total_provider_tokens", "estimated_cost_usd"]},
        "usage_warnings": usage.get("warnings"),
        "per_task_results": verifier_results,
        "prompt_delivery": prompt_delivery,
        "leakage_controls": leakage_controls,
        "artifacts": compact_artifacts(run_dir),
        "run_dir": rel(run_dir),
    }
    comparison_baseline_session_id = ""
    if profile_id != "baseline-bare-codex":
        registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
        baseline_record = find_canonical_baseline_record(registry, seq, args.replicate_index)
        if baseline_record:
            comparison_baseline_session_id = baseline_record["session_id"]
    session_record = workflow_session_record(
        seq,
        summary,
        run_dir,
        profile_id,
        codex_exit_codes,
        final_verifier_code,
        audit_code,
        usage,
        verifier_results,
        prompt_delivery=prompt_delivery,
        leakage_controls=leakage_controls,
        comparison_baseline_session_id=comparison_baseline_session_id,
    )
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2) + "\n")
    remove_ephemeral_homes(run_dir)
    write_evidence_bundle(run_dir)
    remove_noncompact_artifacts(run_dir)
    write_manifest(run_dir)
    update_registry(session_record)
    comparison = write_comparison_if_ready(seq, study_id, args.replicate_index, comparison_profile_id) if comparison_profile_id else None
    if comparison:
        summary["comparison"] = comparison
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Manual rerun guide: docs/evaluations/sequential-workflow-runner.md. "
            "For a shared-baseline+treatment rerun use: "
            "scripts/run_sequential_workflow_pair.sh <sequence-id>."
        ),
    )
    parser.add_argument("--sequence-id")
    parser.add_argument("--profile-id", choices=sorted(PROFILE_META), default="baseline-bare-codex")
    parser.add_argument("--list-sequences", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--timeout-per-task", type=int, default=1800)
    parser.add_argument("--replicate-index", type=int, default=0)
    parser.add_argument("--session-id")
    parser.add_argument("--study-id")
    parser.add_argument("--experiment-group-id")
    parser.add_argument("--comparison-profile-id", choices=sorted(PROFILE_META), help="treatment profile used to group baseline/treatment comparison records")
    parser.add_argument("--docker-image", default=DEFAULT_DOCKER_IMAGE)
    parser.add_argument("--source-codex-home", type=Path, default=DEFAULT_SOURCE_CODEX_HOME)
    parser.add_argument("--skip-container-preflight", action="store_true")
    parser.add_argument("--skip-codex-preflight", action="store_true")
    parser.add_argument("--skip-dependency-install", action="store_true")
    parser.add_argument("--no-conceal-seed-origin", action="store_true", help="debug only: leave seed patch as visible git diff; prepare-only runs only")
    args = parser.parse_args(argv)
    if args.list_sequences:
        print(json.dumps({"active_sequences": active_sequence_ids(), "profiles": sorted(PROFILE_META)}, indent=2))
        return 0
    if not args.sequence_id:
        parser.error("--sequence-id is required unless --list-sequences is used")
    try:
        selected_sequence = load_sequence(args.sequence_id)
    except KeyError:
        parser.error(f"unknown workflow sequence: {args.sequence_id}")
    if selected_sequence.get("status") != "active" and not args.prepare_only:
        parser.error(f"workflow sequence {args.sequence_id} is not active; only --prepare-only is allowed")
    result = run_one(args)
    if args.prepare_only:
        print(json.dumps(result, indent=2))
        return 0 if result.get("prepared") is True else 1
    if result.get("prepared"):
        print(json.dumps(result, indent=2))
        return 0
    return 0 if result.get("accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
